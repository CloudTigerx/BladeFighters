import logging
from typing import Optional, Dict


_configured: bool = False
_loggers: Dict[str, logging.Logger] = {}


def configure_logging(level: str = "INFO", file_path: Optional[str] = None) -> None:
    """
    Configure basic logging for the application. Idempotent.

    Args:
        level: Logging level name (e.g., "DEBUG", "INFO").
        file_path: Optional file path to also write logs to.
    """
    global _configured
    if _configured:
        return

    # Map level string to logging constant with fallback
    level_value = getattr(logging, str(level).upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level_value)

    # Avoid duplicate handlers
    if not root_logger.handlers:
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

        if file_path:
            try:
                file_handler = logging.FileHandler(file_path)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            except Exception:
                # Fail silently; console logging still works
                pass

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a module-level cached logger by name. Ensures no duplicate handlers.
    """
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    _loggers[name] = logger
    return logger

