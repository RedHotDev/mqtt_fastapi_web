import json
import asyncio
import logging
from typing import Optional
import paho.mqtt.client as mqtt
from datetime import datetime
from config import settings
from schemas.schemas import SensorDataCreate
from services.sensor_service import create_sensor_data
from database import SessionLocal

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
        self.message_handler: Optional[Callable] = None

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
        try:
            payload = msg.payload.decode('utf-8')
            logger.info(f"Received message on topic {msg.topic}: {payload}")

            # Process message asynchronously
            self.process_message(payload)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    
    def process_message(self, payload: str):
        """Process incoming MQTT message and save to database"""
        try:
            data = json.loads(payload)

            # Validate required fields
            required_fields = ['datastamp', 'device', 'temp', 'humidity']
            if not all(field in data for field in required_fields):
                logger.error(
                    f"Missing required fields. Required: {required_fields}, Received: {data.keys()}")
                return

            # Convert datastamp string to datetime if needed
            if isinstance(data['datastamp'], str):
                data['datastamp'] = datetime.fromisoformat(
                    data['datastamp'].replace('Z', '+00:00'))

            # Create sensor data object
            sensor_data = SensorDataCreate(**data)

            # Save to database
            db = SessionLocal()
            create_sensor_data(db, sensor_data)
            logger.info(
                f"Saved sensor data: device={sensor_data.device}, temp={sensor_data.temp}, humidity={sensor_data.humidity}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e}")
        except Exception as e:
            logger.error(f"Error saving to database: {e}")

    # async def reconnect(self):
    #     """Reconnect to MQTT broker"""
    #     while not self.connected:
    #         try:
    #             logger.info("Reconnecting to MQTT broker...")
    #             self.client.connect(settings.broker_host,
    #                                 settings.broker_port, 60)
    #             self.client.loop_start()
    #             await asyncio.sleep(5)
    #         except Exception as e:
    #             logger.error(f"Reconnection failed: {e}")
    #             await asyncio.sleep(10)

    def start(self):
        """Start MQTT client"""
        try:
          

            # Connect to MQTT broker
            self.client.connect(settings.broker_host, settings.broker_port, 60)
           
            self.client.loop_start()

            

        except Exception as e:
            logger.error(f"Failed to start MQTT client: {e}")
            raise

    def stop(self):
        """Stop MQTT client"""
       

        # Stop MQTT client
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT client stopped")



# Global MQTT client instance
mqtt_client = MQTTClient()
