import asyncio
from fastapi import WebSocket
from typing import Set, Dict, Any
import json
from loglib import logger


class ConnectionManager:
    """Управляет WebSocket подключениями и рассылкой сообщений"""

    def __init__(self):
        # Множество активных подключений
        self.active_connections: Set[WebSocket] = set()
        # Очередь сообщений для фоновой рассылки
        self.message_queue: asyncio.Queue = asyncio.Queue()
        # Задача-воркер для рассылки
        self.broadcast_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket):
        """Принять новое WebSocket соединение"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(
            f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Закрыть соединение"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(
            f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict | str):
        """Отправить сообщение ВСЕМ подключённым клиентам"""
        if not self.active_connections:
            return

        # Если передали словарь - превращаем в JSON строку
        if isinstance(message, dict):
            message = json.dumps(message, default=str)

        # Отправляем всем параллельно
        tasks = []
        for connection in self.active_connections.copy():
            try:
                tasks.append(connection.send_text(message))
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                self.disconnect(connection)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def add_to_queue(self, data: dict):
        """Добавить данные в очередь для фоновой отправки"""
        await self.message_queue.put(data)

    async def process_queue(self):
        """Фоновая задача: забирает из очереди и отправляет клиентам"""
        while True:
            try:
                data = await self.message_queue.get()
                await self.broadcast(data)
                self.message_queue.task_done()
            except asyncio.CancelledError:
                logger.info("WebSocket queue processor cancelled")
                break
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(0.1)

    async def start_background_processor(self):
        """Запустить фоновый обработчик очереди"""
        if not self.broadcast_task or self.broadcast_task.done():
            self.broadcast_task = asyncio.create_task(self.process_queue())
            logger.info("WebSocket background processor started")

    async def stop_background_processor(self):
        """Остановить фоновый обработчик"""
        if self.broadcast_task and not self.broadcast_task.done():
            self.broadcast_task.cancel()
            try:
                await self.broadcast_task
            except asyncio.CancelledError:
                pass
            logger.info("WebSocket background processor stopped")


# Глобальный экземпляр менеджера
ws_manager = ConnectionManager()
