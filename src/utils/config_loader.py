import yaml
from typing import Dict, Any
from src.utils.constants import DEFAULT_CONFIG
from src.utils.logger import get_logger

logger = get_logger()

def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return {**DEFAULT_CONFIG, **config}
    except Exception as e:
        logger.warning(f"Failed to load config from {config_path}: {str(e)}")
        logger.info("Using default configuration")
        return DEFAULT_CONFIG