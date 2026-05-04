from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.websocket_manager import ws_manager
from loglib import logger

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/sensors/live")
async def websocket_sensors_live(websocket: WebSocket):
    """
    WebSocket эндпоинт для получения данных датчиков в реальном времени.
    
    Клиент подключается к: ws://localhost:8000/ws/sensors/live
    И получает JSON сообщения каждый раз, когда приходит новый MQTT пакет.
    
    Формат сообщения:
    {
        "type": "new_sensor_data",
        "data": {
            "id": 123,
            "device": 1,
            "temp": 22.5,
            "humidity": 60,
            "datastamp": "2024-01-15T10:30:00",
            "created_at": "2024-01-15T10:30:01"
        }
    }
    """
    await ws_manager.connect(websocket)
    try:
        # Отправляем приветственное сообщение
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to sensor data stream",
            "clients_connected": len(ws_manager.active_connections)
        })

        # Держим соединение открытым, слушаем возможные команды от клиента
        while True:
            # Можно принимать команды от клиента (например: ping, subscribe to device)
            data = await websocket.receive_text()
            logger.debug(f"Received from WebSocket client: {data}")

            # Отвечаем на ping
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
