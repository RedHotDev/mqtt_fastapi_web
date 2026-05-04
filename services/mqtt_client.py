import json
import asyncio
import logging
from typing import Optional
import paho.mqtt.client as mqtt
from datetime import datetime
from config import settings
from schemas.schemas import SensorDataCreate
from services.sensor_service import create_sensor_data
from database import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION1,
            client_id=settings.client_id,
            protocol=mqtt.MQTTv311
        )

        # Set username/password if provided
        if settings.mqtt_username and settings.mqtt_password:
            self.client.username_pw_set(
                settings.mqtt_username, settings.mqtt_password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.connected = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.message_queue: Optional[asyncio.Queue] = None
        self.queue_task: Optional[asyncio.Task] = None

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            logger.info(
                f"Connected to MQTT broker at {settings.broker_host}:{settings.broker_port}")
            self.connected = True
            client.subscribe(settings.topic)
            logger.info(f"Subscribed to topic: {settings.topic}")
        else:
            logger.error(
                f"Failed to connect to MQTT broker. Reason code: {reason_code}")
            self.connected = False

    def on_disconnect(self, client, userdata, flags, reason_code, properties=None):
        logger.warning(
            f"Disconnected from MQTT broker. Reason code: {reason_code}")
        self.connected = False

        # Auto-reconnect
        if reason_code != 0:
            logger.info("Attempting to reconnect...")
            # Schedule reconnect in the main event loop
            if self.loop and self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self.reconnect(), self.loop)

    def on_message(self, client, userdata, msg):
        """Вызывается в потоке MQTT"""
        try:
            payload = msg.payload.decode('utf-8')
            logger.info(f"Received: {payload}")

            # Безопасно добавляем в очередь из другого потока
            if self.message_queue:
                self.message_queue.put_nowait(payload)
        except Exception as e:
            logger.error(f"Error: {e}")

    
    async def process_queue(self):
        while True:
            try:
                # Читаем из очереди
                payload = await self.message_queue.get()
                # отправляем на запись в БД
                await self.process_message(payload)
                self.message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в очереди: {e}")
                await asyncio.sleep(0.1)

    async def process_message(self, payload: str):
        """Асинхронная обработка сообщения"""
        async with AsyncSessionLocal() as db:
            try:
                data = json.loads(payload)
                
                # Преобразование данных
                if isinstance(data.get('datastamp'), str):
                    data['datastamp'] = datetime.fromisoformat(
                        data['datastamp'].replace('Z', '+00:00'))
                
                data['device'] = int(data['device'])
                data['temp'] = float(data['temp'])
                data['humidity'] = float(data['humidity'])
                
                sensor_data = SensorDataCreate(**data)
                
                # Асинхронное сохранение в БД
                result = await create_sensor_data(db, sensor_data)
                
                logger.info(f"Saved: device={result.device}, temp={result.temp}, humidity={result.humidity}")
                
            except Exception as e:
                logger.error(f"Process error: {e}", exc_info=True)

    async def reconnect(self):
        """Переподключение"""
        while not self.connected:
            try:
                logger.info("Reconnecting...")
                self.client.connect(settings.broker_host, settings.broker_port, 60)
                self.client.loop_start()
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Reconnect failed: {e}")
                await asyncio.sleep(10)


    async def start(self):
        """Запуск MQTT клиента"""
        self.loop = asyncio.get_running_loop()
        self.message_queue = asyncio.Queue(maxsize=1000)
        self.queue_task = asyncio.create_task(self.process_queue())
        
        self.client.connect(settings.broker_host, settings.broker_port, 60)
        self.client.loop_start()
        
        # Ждем подключения
        for _ in range(50):  # 5 секунд таймаут
            if self.connected:
                break
            await asyncio.sleep(0.1)
        
        logger.info(f"MQTT client started. Connected: {self.connected}")

    async def stop(self):
        """Остановка"""
        if self.queue_task:
            self.queue_task.cancel()
        
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("MQTT client stopped")



# Global MQTT client instance
mqtt_client = MQTTClient()
