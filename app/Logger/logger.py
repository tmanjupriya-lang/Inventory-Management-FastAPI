import logging
from logging.handlers import RotatingFileHandler

# Create logger
logger = logging.getLogger("inventory_app")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
)

# File Handler → rotates log file when size exceeds 1MB
file_handler = RotatingFileHandler(
    "app.log", maxBytes=1_000_000, backupCount=3
)
file_handler.setFormatter(formatter)

# Stream Handler → shows logs in console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Add handlers
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
