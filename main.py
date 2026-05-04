from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from contextlib import asynccontextmanager
from config import settings
from loglib import logger
from database import init_db
from routers.router import router
from services.mqtt_client import mqtt_client
from routers.websocket_router import router as ws_router
from services.websocket_manager import ws_manager
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting up...")

    # Initialize database
    await init_db()
    
    logger.info("Database initialized")

    # Start WebSocket background processor
    await ws_manager.start_background_processor()  
    logger.info("WebSocket background processor started")

    # Start MQTT client
    await mqtt_client.start()
    logger.info("MQTT client started")

    yield


    # Shutdown
    logger.info("Shutting down...")

    await ws_manager.stop_background_processor()  # ← добавить
    logger.info("WebSocket background processor stopped")
    
    # Stop MQTT client
    await mqtt_client.stop()
    logger.info("MQTT client stopped")



# инициализация FastAPI app
app = FastAPI(
    title="MQTT to SQLite FastAPI Service",
    description="Service that receives MQTT messages and stores them in SQLite database",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)
app.include_router(ws_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
