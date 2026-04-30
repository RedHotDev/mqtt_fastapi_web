from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from config import settings
from loglib import logger
from database import init_db
from routers.router import router
from services.mqtt_client import mqtt_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting up...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Start MQTT client
    await mqtt_client.start()
    logger.info("MQTT client started")

    yield

    # Shutdown
    logger.info("Shutting down...")

    # Stop MQTT client
    # await mqtt_client.stop()
    # logger.info("MQTT client stopped")



# инициализация FastAPI app
app = FastAPI(
    title="MQTT to SQLite FastAPI Service",
    description="Service that receives MQTT messages and stores them in SQLite database",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
