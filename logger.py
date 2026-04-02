# logger.py - Centralized, rotating logger for the speed limit project
import logging
from logging.handlers import RotatingFileHandler
import os
from config import LOG_LEVEL, LOG_FILE, LOG_MAX_MB, LOG_BACKUP_COUNT

# Ensure log directory exists (automotive-ready)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def get_logger(name="speed_limit"):
    logger = logging.getLogger(name)
    # Prevent duplicate handlers if imported multiple times
    if not logger.handlers:
        logger.setLevel(LOG_LEVEL.upper())
        
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_MB * 1024 * 1024,
            backupCount=LOG_BACKUP_COUNT
        )
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console output kept for development (you can comment out later)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger