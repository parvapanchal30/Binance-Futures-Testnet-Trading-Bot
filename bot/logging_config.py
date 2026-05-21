import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging(log_file: str | None = None, level: int = logging.INFO):
    if log_file is None:
        log_file = os.path.join(os.getcwd(), "trading_bot.log")

    logger = logging.getLogger("trading_bot")
    logger.setLevel(level)

    if not logger.handlers:
        fmt = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        )
        handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    return logger


__all__ = ["setup_logging"]
