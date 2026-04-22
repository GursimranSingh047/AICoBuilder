import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configure loguru for structured, leveled logging."""
    logger.remove()  # Remove default handler

    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Console
    logger.add(sys.stdout, format=fmt, level="DEBUG" if settings.DEBUG else "INFO", colorize=True)

    # File – rotates daily, retained 7 days
    logger.add(
        "logs/projectpilot_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="7 days",
        format=fmt,
        level="INFO",
        enqueue=True,  # thread-safe
    )

    logger.info(f"Logging initialised | debug={settings.DEBUG}")
