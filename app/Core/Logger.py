import logging
from logging.handlers import RotatingFileHandler


def setupLogger():
    logging.basicConfig(
        handlers=[RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=3)],
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


logger = logging.getLogger(__name__)
