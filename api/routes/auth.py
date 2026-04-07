"""
FastAPI OAuth 2.0 Endpoints for SynapseOS

Handles:
- Authorization flow initiation
- Callback handling
- Token management
- User authentication
- Session management
"""

from typing import Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

from core.oauth import oauth_client, jwt_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


# Pydantic Models
class AuthRequest(BaseModel):
    """Request body for manual auth initiation"""
    user_id: Optional[str] = None
    redirect_to: Optional[str] = None


class TokenResponse(BaseModel):
    """Response with JWT session token"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    expires_in: int = 3600


class UserInfoResponse(BaseModel):
    """User information response"""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    scope: list = []


class LogoutRequest(BaseModel):
    """Logout request"""
    user_id: str


# Dependency for getting current user from token
async def get_current_user(
    authorization: str = None
) -> Dict[str, Any]:
    """
    Get current user from JWT token in Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        User payload from token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    token = parts[1]
    payload = jwt_manager.verify_session_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload


@router.get("/authorize")
async def authorize(
    user_id: Optional[str] = Query(None),
    redirect_to: Optional[str] = Query(None)
):
    """
    Initiate OAuth authorization flow.
    
    Args:
        user_id: Optional user identifier for tracking
        redirect_to: URL to redirect to after authentication
        
    Returns:
        Redirect to OAuth provider's authorization URL
    """
    if not oauth_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth client not initialized"
        )
    
    auth_url, state = oauth_client.get_authorization_url(user_id)
    
    # Store redirect_to in state session if provided
    if redirect_to and state in oauth_client.sessions:
        oauth_client.sessions[state]["redirect_to"] = redirect_to
    
    logger.info(f"Authorization initiated for user: {user_id}, state: {state}")
    return RedirectResponse(url=auth_url, status_code=status.HTTP_302_FOUND)


@router.get("/callback")
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
):
    """
    OAuth callback endpoint.
    
    Handles the redirect from OAuth provider after user authorization.
    
    Args:
        code: Authorization code from OAuth provider
        state: State token for security
        error: Error code if authorization failed
        error_description: Error description
        
    Returns:
        JSON response with session token or error
    """
    if not oauth_client or not jwt_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth client not initialized"
        )
    
    # Handle errors from OAuth provider
    if error:
        logger.error(f"OAuth error: {error} - {error_description}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error_description}"
        )
    
    try:
        # Exchange code for token
        token_data = await oauth_client.exchange_code_for_token(code, state)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code"
            )
        
        # Get user info
        user_id = oauth_client.sessions.get(state, {}).get("user_id", "user_" + code[:8])
        user_info = await oauth_client.get_user_info(user_id)
        
        # Create session JWT token
        session_token = jwt_manager.create_session_token(user_id)
        
        # Prepare response
        response_data = {
            "access_token": session_token,
            "token_type": "bearer",
            "user_id": user_id,
            "expires_in": 3600,
            "oauth_token_expires_at": token_data.get("expires_at"),
            "user_email": user_info.get("email") if user_info else None,
        }
        
        logger.info(f"OAuth callback successful for user: {user_id}")
        return JSONResponse(content=response_data)
    
    except ValueError as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/token/refresh")
async def refresh_token(
    user_id: str = Query(...),
    current_user: Dict = Depends(get_current_user)
):
    """
    Refresh access token.
    
    Args:
        user_id: User identifier
        current_user: Current user from JWT token (dependency)
        
    Returns:
        New session token
    """
    if not jwt_manager:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT manager not initialized"
        )
    
    # Verify user can only refresh their own token
    if current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot refresh token for other users"
        )
    
    # Refresh OAuth token
    oauth_token = await oauth_client.refresh_token(user_id)
    if not oauth_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to refresh OAuth token"
        )
    
    # Create new session JWT
    new_session_token = jwt_manager.create_session_token(user_id)
    
    logger.info(f"Token refreshed for user: {user_id}")
    return TokenResponse(
        access_token=new_session_token,
        user_id=user_id
    )


@router.get("/user/info")
async def get_user_info(
    current_user: Dict = Depends(get_current_user)
) -> UserInfoResponse:
    """
    Get current user information.
    
    Args:
        current_user: Current user from JWT token (dependency)
        
    Returns:
        User information
    """
    if not oauth_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth client not initialized"
        )
    
    user_id = current_user.get("user_id")
    user_info = await oauth_client.get_user_info(user_id)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User information not found"
        )
    
    logger.info(f"Retrieved user info for: {user_id}")
    return UserInfoResponse(
        user_id=user_id,
        email=user_info.get("email"),
        name=user_info.get("name"),
        picture=user_info.get("picture"),
        scope=user_info.get("scope", [])
    )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: Dict = Depends(get_current_user)
) -> JSONResponse:
    """
    Logout user and revoke OAuth token.
    
    Args:
        request: Logout request with user_id
        current_user: Current user from JWT token (dependency)
        
    Returns:
        Success message
    """
    if not oauth_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth client not initialized"
        )
    
    user_id = request.user_id
    
    # Verify user can only logout themselves
    if current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot logout other users"
        )
    
    # Revoke OAuth token
    success = await oauth_client.revoke_token(user_id)
    
    if not success:
        logger.warning(f"Token revocation may have failed for user: {user_id}")
    
    logger.info(f"User logged out: {user_id}")
    return JSONResponse(
        content={"message": "Successfully logged out", "user_id": user_id}
    )


@router.get("/login/status")
async def login_status(
    current_user: Optional[Dict] = None
):
    """
    Check if user is logged in.
    
    Args:
        current_user: Current user from JWT token (dependency, optional)
        
    Returns:
        Login status
    """
    if current_user:
        return JSONResponse(
            content={
                "logged_in": True,
                "user_id": current_user.get("user_id"),
                "expires_at": current_user.get("exp")
            }
        )
    else:
        return JSONResponse(
            content={"logged_in": False},
            status_code=status.HTTP_401_UNAUTHORIZED
        )


@router.get("/authorize/state/{state}")
async def get_authorization_state(state: str):
    """
    Get authorization state information (for debugging).
    
    Args:
        state: State token
        
    Returns:
        State information or 404
    """
    if not oauth_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth client not initialized"
        )
    
    if state not in oauth_client.sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )
    
    session_info = oauth_client.sessions[state]
    return JSONResponse(
        content={
            "state": state,
            "user_id": session_info.get("user_id"),
            "created_at": session_info.get("created_at"),
            "expires_at": session_info.get("expires_at"),
        }
    )


# Health check endpoint
@router.get("/health")
async def auth_health():
    """OAuth service health check."""
    return JSONResponse(
        content={
            "status": "ok",
            "oauth_initialized": oauth_client is not None,
            "jwt_initialized": jwt_manager is not None,
        }
    )
