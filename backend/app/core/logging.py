import logging
import sys

from app.core.config import settings

logger = logging.getLogger("somahub")


def setup_logging():
    """Configure application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_format = (
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        if settings.APP_ENV == "development"
        else '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    )

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logger.info("Logging configured for %s environment.", settings.APP_ENV)
