import logging
import sys
from typing import Optional

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("embedding_service")
    
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler("embedding_service.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.setLevel(logging.INFO)
    
    return logger

def get_logger() -> logging.Logger:
    return logging.getLogger("embedding_service")