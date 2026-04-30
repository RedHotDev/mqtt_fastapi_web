import logging
from logging.handlers import RotatingFileHandler

# Создание логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Форматирование
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Файловый обработчик с ротацией
file_handler = RotatingFileHandler(
    'log.log',
    maxBytes=10485760,  # 10 MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

# Консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Добавление обработчиков
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Использование
logger.debug("Отладка")
logger.info("Информация")
logger.warning("Предупреждение")
logger.error("Ошибка")
