"""
Items Persistence - Manages saving and loading of item configurations
Provides configuration persistence with validation and error handling.
"""

import json
import os
from typing import Dict, Any
from ..logging_module.error_handler import (
    safe_file_operation,
    safe_operation
)
from ..logging_module.logger import get_logger

logger = get_logger(__name__)


DEFAULT_CONFIG = {
    "player_weapon": "Rusted Sword",
    "enemy_weapon": "Rusted Sword",
    "player_weapons": ["Rusted Sword"],
    "enemy_weapons": ["Rusted Sword"],
}


@safe_file_operation("load items config", DEFAULT_CONFIG.copy(), "WARNING")
def load_items_config(path: str) -> Dict[str, Any]:
    """Load items configuration from file with validation."""
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.warning(f"Invalid items config format: {path}")
                    return DEFAULT_CONFIG.copy()
                
                # Merge with defaults to tolerate missing keys and types
                merged = DEFAULT_CONFIG.copy()
                for k, v in data.items():
                    if k in ("player_weapon", "enemy_weapon") and isinstance(v, str):
                        merged[k] = v
                    if k in ("player_weapons", "enemy_weapons") and isinstance(v, list):
                        # Keep only strings
                        merged[k] = [str(x) for x in v]
                
                logger.debug(f"Loaded items config from: {path}")
                return merged
    except Exception as e:
        logger.warning(f"Failed to load items config from {path}: {str(e)}")
    
    logger.info(f"Using default items config (file not found or invalid: {path})")
    return DEFAULT_CONFIG.copy()


@safe_file_operation("save items config", None, "WARNING")
def save_items_config(path: str, config: Dict[str, Any]) -> None:
    """Save items configuration to file with atomic write."""
    try:
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Write atomically
        tmp_path = f"{path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        os.replace(tmp_path, path)
        
        logger.debug(f"Saved items config to: {path}")
    except Exception as e:
        logger.warning(f"Failed to save items config to {path}: {str(e)}")
        # Swallow errors to avoid crashing on shutdown

