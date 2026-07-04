import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from docforge.config import settings
from docforge.interfaces.api import register_routes
from docforge.interfaces.chat_routes import router as chat_router
from docforge.interfaces.pdf_routes import router as pdf_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("docforge")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting DocForge application")
    yield
    logger.info("Stopping DocForge application")


app = FastAPI(title="DocForge", version="0.1.0", lifespan=lifespan)
register_routes(app)
app.include_router(pdf_router)
app.include_router(chat_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
