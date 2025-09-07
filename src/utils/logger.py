"""
Système de logging pour RTPA Studio
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

# Configuration globale des logs
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Configure et retourne un logger"""
    logger_name = name or 'RTPA_Studio'
    logger = logging.getLogger(logger_name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier rotatif
    file_handler = RotatingFileHandler(
        LOG_DIR / 'rtpa_studio.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Retourne un logger configuré"""
    return setup_logger(name)