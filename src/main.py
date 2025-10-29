from src.config import config
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=config.server.host,
        port=config.server.port,
        reload=not config.server.production,
    )
