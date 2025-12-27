import logging
from typing import Any

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def safe_get(d: dict, key: str, default: Any = None):
    return d[key] if key in d else default
