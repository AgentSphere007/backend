from fastapi import FastAPI
from src.router import router
from src.config import config

app = FastAPI(
    docs_url="/docs" if not config.server.production else None,
    redoc_url="/redoc" if not config.server.production else None,
    debug=not config.server.production,
    title="AI Git",
    openapi_url="/openapi.json" if not config.server.production else None,
    swagger_ui_init_oauth=None,
    swagger_ui_oauth2_redirect_url=None,
)

app.include_router(router)
