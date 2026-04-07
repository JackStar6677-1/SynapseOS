"""
OAuth 2.0 Authentication Module for SynapseOS with Codex/OpenAI Integration

Implements OAuth 2.0 authorization code flow for:
- OpenAI Codex / GPT API access
- User authentication
- Secure token management
- Session management
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import hashlib
import base64

import aiohttp
import jwt
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class OAuth2Config:
    """OAuth 2.0 Configuration for OpenAI"""
    
    # OpenAI OAuth endpoints
    AUTHORIZE_URL = "https://openai.com/api/auth/oauth2/authorize"
    TOKEN_URL = "https://openai.com/api/auth/oauth2/token"
    USERINFO_URL = "https://openai.com/api/auth/oauth2/userinfo"
    REVOKE_URL = "https://openai.com/api/auth/oauth2/revoke"
    
    # Scopes required by SynapseOS
    SCOPES = [
        "openai.api",                    # API access
        "openai.codex",                  # Codex models
        "openai.models",                 # Model listing
        "user_profile",                  # User information
    ]
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """Initialize OAuth configuration."""
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = redirect_uri
        self.SCOPES_STR = " ".join(self.SCOPES)


class CodeChallenge:
    """PKCE (Proof Key for Public Clients) Challenge Generation"""
    
    @staticmethod
    def generate() -> tuple[str, str]:
        """
        Generate code_verifier and code_challenge for PKCE.
        
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        # Generate 128 character random string
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(96)).decode('utf-8')
        code_verifier = code_verifier.replace('=', '')
        
        # Create challenge
        challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8')
        code_challenge = code_challenge.replace('=', '')
        
        return code_verifier, code_challenge


class OAuth2Client:
    """OAuth 2.0 Client for OpenAI Codex Authentication"""
    
    def __init__(self, config: OAuth2Config, memory_system=None):
        """
        Initialize OAuth client.
        
        Args:
            config: OAuth2Config instance
            memory_system: Optional MemorySystem for persistent storage
        """
        self.config = config
        self.memory = memory_system
        self.sessions = {}
        self._load_tokens()
    
    def _extract_account_id(self, access_token: str) -> str:
        """Extract account ID from JWT access token"""
        try:
            # Decode JWT without verification for account ID extraction
            payload = jwt.decode(access_token, options={"verify_signature": False})
            return payload.get("https://api.openai.com/auth", {}).get("chatgpt_account_id", "")
        except Exception as e:
            logger.warning(f"Failed to extract account ID from token: {e}")
            return ""
    
    def _load_tokens(self):
        """Load tokens from memory system and imported files"""
        self.tokens = {}
        
        if not self.memory:
            # Try to load from imported file
            self._load_imported_tokens()
            return
        
        # Try to load from memory
        try:
            token_data = self.memory.retrieve("oauth_tokens")
            if token_data:
                self.tokens.update(token_data)
                logger.info(f"Loaded {len(token_data)} OAuth tokens from memory")
        except Exception as e:
            logger.error(f"Failed to load OAuth tokens from memory: {e}")
        
        # Also try to load imported tokens
        self._load_imported_tokens()
    
    def _load_imported_tokens(self):
        """Load tokens from imported oauth_openai.json file"""
        try:
            import json
            from pathlib import Path
            
            token_file = Path("data") / "memory" / "oauth_openai.json"
            if token_file.exists():
                with open(token_file, 'r') as f:
                    imported_tokens = json.load(f)
                
                # Convert to the expected format and use "default" as user_id
                user_id = "default"  # Use "default" to match openai_client.py
                self.tokens[user_id] = {
                    "access_token": imported_tokens["access_token"],
                    "refresh_token": imported_tokens["refresh_token"],
                    "expires_at": imported_tokens["expires_at"],
                    "expires": imported_tokens["expires_at"],  # For compatibility
                    "accountId": imported_tokens["account_id"],
                    "scope": imported_tokens.get("scope", ""),
                    "obtained_at": "imported_from_openclaw",  # Mark as imported
                }
                
                logger.info(f"Loaded imported OAuth tokens for user: {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to load imported OAuth tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to memory system"""
        if not self.memory:
            return
        
        try:
            self.memory.store("oauth_tokens", self.tokens, "auth")
            logger.info(f"Saved {len(self.tokens)} OAuth tokens to memory")
        except Exception as e:
            logger.error(f"Failed to save OAuth tokens: {e}")
    
    def get_authorization_url(self, user_id: str = None) -> tuple[str, str]:
        """
        Generate authorization URL for user to authenticate.
        
        Args:
            user_id: Optional user identifier for session tracking
            
        Returns:
            Tuple of (auth_url, state_token)
        """
        state = secrets.token_urlsafe(32)
        code_verifier, code_challenge = CodeChallenge.generate()
        
        # Store state and verifier for later validation
        if user_id:
            self.sessions[state] = {
                "user_id": user_id,
                "code_verifier": code_verifier,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat()
            }
        
        params = {
            "client_id": self.config.CLIENT_ID,
            "redirect_uri": self.config.REDIRECT_URI,
            "response_type": "code",
            "scope": self.config.SCOPES_STR,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        auth_url = f"{self.config.AUTHORIZE_URL}?{query_string}"
        
        logger.info(f"Generated auth URL for state: {state}")
        return auth_url, state
    
    async def exchange_code_for_token(
        self, 
        code: str, 
        state: str
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth provider
            state: State token for validation
            
        Returns:
            Token dictionary or None if exchange failed
        """
        if state not in self.sessions:
            logger.error(f"Invalid state token: {state}")
            raise ValueError("Invalid state token")
        
        session = self.sessions[state]
        code_verifier = session["code_verifier"]
        
        # Check expiration
        if datetime.fromisoformat(session["expires_at"]) < datetime.now():
            logger.error(f"State token expired: {state}")
            del self.sessions[state]
            raise ValueError("State token expired")
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.config.CLIENT_ID,
            "client_secret": self.config.CLIENT_SECRET,
            "redirect_uri": self.config.REDIRECT_URI,
            "code_verifier": code_verifier,
        }
        
        try:
            async with aiohttp.ClientSession() as session_http:
                async with session_http.post(
                    self.config.TOKEN_URL,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        token_data = await resp.json()
                        
                        # Store token in OpenClaw-like format
                        user_id = session.get("user_id", code)
                        expires_timestamp = int((
                            datetime.now() + 
                            timedelta(seconds=token_data.get("expires_in", 3600))
                        ).timestamp() * 1000)  # milliseconds
                        
                        self.tokens[user_id] = {
                            "type": "oauth",
                            "provider": "openai-codex",
                            "access": token_data.get("access_token"),
                            "refresh": token_data.get("refresh_token"),
                            "expires": expires_timestamp,
                            "accountId": self._extract_account_id(token_data.get("access_token")),
                            "scope": token_data.get("scope"),
                            "obtained_at": datetime.now().isoformat(),
                        }
                        
                        # Save to storage
                        self._save_tokens()
                        
                        # Clean up session
                        del self.sessions[state]
                        
                        logger.info(f"Successfully obtained token for {user_id}")
                        return self.tokens[user_id]
                    else:
                        error_data = await resp.json()
                        logger.error(f"Token exchange failed: {error_data}")
                        raise ValueError(f"Token exchange failed: {error_data}")
        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error during token exchange: {e}")
            raise
    
    async def refresh_token(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Refresh expired access token using refresh token.
        
        Args:
            user_id: User identifier
            
        Returns:
            Updated token dictionary or None
        """
        if user_id not in self.tokens:
            logger.error(f"No token found for user: {user_id}")
            return None
        
        token_data = self.tokens[user_id]
        refresh_token = token_data.get("refresh_token")
        
        if not refresh_token:
            logger.error(f"No refresh token for user: {user_id}")
            return None
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.config.CLIENT_ID,
            "client_secret": self.config.CLIENT_SECRET,
        }
        
        try:
            async with aiohttp.ClientSession() as session_http:
                async with session_http.post(
                    self.config.TOKEN_URL,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        new_token_data = await resp.json()
                        
                        # Update token in OpenClaw-like format
                        expires_timestamp = int((
                            datetime.now() + 
                            timedelta(seconds=new_token_data.get("expires_in", 3600))
                        ).timestamp() * 1000)
                        
                        self.tokens[user_id].update({
                            "access": new_token_data.get("access_token"),
                            "refresh": new_token_data.get("refresh_token", refresh_token),
                            "expires": expires_timestamp,
                            "obtained_at": datetime.now().isoformat(),
                        })
                        
                        self._save_tokens()
                        logger.info(f"Token refreshed for user: {user_id}")
                        return self.tokens[user_id]
                    else:
                        logger.error(f"Token refresh failed with status {resp.status}")
                        return None
        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error during token refresh: {e}")
            return None
    
    async def get_valid_token(self, user_id: str) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            user_id: User identifier
            
        Returns:
            Valid access token or None
        """
        if user_id not in self.tokens:
            logger.error(f"No token found for user: {user_id}")
            return None
        
        token_data = self.tokens[user_id]
        access_token = token_data.get("access_token") or token_data.get("access")
        
        # For imported tokens, try to use them directly first
        if token_data.get("obtained_at") and "imported" in str(token_data.get("obtained_at", "")):
            logger.info(f"Using imported token for user: {user_id}")
            return access_token
        
        expires_timestamp = token_data.get("expires", 0)
        expires_at = datetime.fromtimestamp(expires_timestamp / 1000)
        
        # If token is still valid (more than 10 minutes left), use it
        if datetime.now() + timedelta(minutes=10) < expires_at:
            return access_token
        
        # Try to refresh if expiring soon
        if datetime.now() + timedelta(minutes=5) >= expires_at:
            logger.info(f"Token expiring soon, attempting refresh for user: {user_id}")
            refreshed = await self.refresh_token(user_id)
            if refreshed:
                return refreshed.get("access_token") or refreshed.get("access")
            else:
                logger.warning(f"Token refresh failed, but trying to use current token anyway")
                # Fall back to current token even if refresh failed
                return access_token
        
        return access_token
    
    async def revoke_token(self, user_id: str) -> bool:
        """
        Revoke user's token (logout).
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        if user_id not in self.tokens:
            logger.warning(f"No token to revoke for user: {user_id}")
            return True
        
        token_data = self.tokens[user_id]
        access_token = token_data.get("access")
        
        data = {
            "client_id": self.config.CLIENT_ID,
            "client_secret": self.config.CLIENT_SECRET,
            "token": access_token,
        }
        
        try:
            async with aiohttp.ClientSession() as session_http:
                async with session_http.post(
                    self.config.REVOKE_URL,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        del self.tokens[user_id]
                        self._save_tokens()
                        logger.info(f"Token revoked for user: {user_id}")
                        return True
                    else:
                        logger.error(f"Token revocation failed with status {resp.status}")
                        return False
        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error during token revocation: {e}")
            return False
    
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get authenticated user information.
        
        Args:
            user_id: User identifier
            
        Returns:
            User information dictionary or None
        """
        access_token = await self.get_valid_token(user_id)
        if not access_token:
            return None
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        
        try:
            async with aiohttp.ClientSession() as session_http:
                async with session_http.get(
                    self.config.USERINFO_URL,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        user_info = await resp.json()
                        logger.info(f"Retrieved user info for: {user_id}")
                        return user_info
                    else:
                        logger.error(f"Failed to get user info: {resp.status}")
                        return None
        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error getting user info: {e}")
            return None


class JWTTokenManager:
    """JWT Token Management for local session management"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        Initialize JWT token manager.
        
        Args:
            secret_key: Secret key for signing
            algorithm: JWT algorithm (default: HS256)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_session_token(
        self, 
        user_id: str,
        expires_in: int = 3600
    ) -> str:
        """
        Create JWT session token.
        
        Args:
            user_id: User identifier
            expires_in: Token expiration in seconds
            
        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "exp": datetime.now() + timedelta(seconds=expires_in),
            "iat": datetime.now(),
            "type": "session",
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Created session token for user: {user_id}")
        return token
    
    def verify_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT session token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.debug(f"Verified session token for user: {payload.get('user_id')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Session token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid session token: {e}")
            return None
    
    def create_api_key_token(
        self,
        user_id: str,
        scope: list = None,
        expires_in: int = 86400 * 30  # 30 days
    ) -> str:
        """
        Create JWT API key token.
        
        Args:
            user_id: User identifier
            scope: API scopes
            expires_in: Token expiration in seconds
            
        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "exp": datetime.now() + timedelta(seconds=expires_in),
            "iat": datetime.now(),
            "type": "api_key",
            "scope": scope or ["read"],
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.debug(f"Created API key token for user: {user_id}")
        return token


# Initialize global oauth client (will be set in main.py)
oauth_client: Optional[OAuth2Client] = None
jwt_manager: Optional[JWTTokenManager] = None


def initialize_oauth(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    jwt_secret: str
) -> tuple[OAuth2Client, JWTTokenManager]:
    """
    Initialize OAuth and JWT managers.
    
    Args:
        client_id: OAuth client ID
        client_secret: OAuth client secret
        redirect_uri: OAuth redirect URI
        jwt_secret: Secret key for JWT
        
    Returns:
        Tuple of (OAuth2Client, JWTTokenManager)
    """
    global oauth_client, jwt_manager
    
    config = OAuth2Config(client_id, client_secret, redirect_uri)
    oauth_client = OAuth2Client(config)
    jwt_manager = JWTTokenManager(jwt_secret)
    
    logger.info("OAuth and JWT managers initialized")
    return oauth_client, jwt_manager
