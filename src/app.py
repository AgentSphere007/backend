from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db import DB
from src.router import router
from src.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    await DB.create_all()
    yield
    await DB.dispose()


app = FastAPI(
    docs_url="/docs" if not config.server.production else None,
    redoc_url="/redoc" if not config.server.production else None,
    debug=not config.server.production,
    title="AI Git",
    openapi_url="/openapi.json" if not config.server.production else None,
    swagger_ui_init_oauth=None,
    swagger_ui_oauth2_redirect_url=None,
    lifespan=lifespan,
    log_config=None,
    access_log=False,
)

if config.server.production:
    allowed_origins = config.server.cors_url
else:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
