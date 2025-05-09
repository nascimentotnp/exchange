import logging
from contextvars import ContextVar
from typing import Optional
import uuid
from pathlib import Path
from datetime import datetime

current_user_id: ContextVar[Optional[str]] = ContextVar('current_user_id', default="system")
current_username: ContextVar[Optional[str]] = ContextVar('current_username', default="system")
correlation_id: ContextVar[str] = ContextVar('correlation_id', default=str(uuid.uuid4()))


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id.get()
        record.user_id = current_user_id.get()
        record.username = current_username.get()

        return True


def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    log_format = ('%(asctime)s.%(msecs)03d | %(levelname)-8s | CID:%(correlation_id)s | User:%(username)-15s | %('
                  'message)s')
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = logging.FileHandler(
        filename=log_dir / f"exchange_{datetime.now().strftime('%Y-%m-%d')}.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(ContextFilter())

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ContextFilter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('passlib').setLevel(logging.CRITICAL)
    logging.getLogger('bcrypt').setLevel(logging.CRITICAL)

    return logger


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.addFilter(ContextFilter())
    return logger
