import os
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from api.routes.auth import router as auth_router
from api.routes.tasks import router as tasks_router
from core.oauth import initialize_oauth
from config.settings import API_HOST, API_PORT, API_DEBUG

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="SynapseOS API",
        description="SynapseOS autonomous agent API",
        version="0.1.0"
    )

    app.include_router(auth_router)
    app.include_router(tasks_router)

    @app.get("/api/v1/health")
    async def health():
        return JSONResponse({"status": "ok", "service": "SynapseOS API"})

    @app.on_event("startup")
    async def startup_event():
        client_id = os.getenv("OPENAI_CLIENT_ID")
        client_secret = os.getenv("OPENAI_CLIENT_SECRET")
        redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/api/v1/auth/callback")
        jwt_secret = os.getenv("JWT_SECRET", os.getenv("OPENAI_CLIENT_ID", "synapseos-secret"))

        if client_id and client_secret:
            initialize_oauth(client_id, client_secret, redirect_uri, jwt_secret)
            logger.info("OAuth initialized for API server startup")
        else:
            logger.warning("OAuth not configured for API server startup")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT, log_level="info")
