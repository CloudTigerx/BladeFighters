"""
Standardized error handling utilities for the BladeFighters game.

This module provides consistent error handling patterns across all modules,
ensuring proper logging, graceful degradation, and user-friendly error messages.
"""

import logging
import traceback
from typing import Any, Callable, Optional, TypeVar, Union
from functools import wraps
from .logger import get_logger
import json

T = TypeVar('T')

# Custom exception classes for different error types
class BladeFightersError(Exception):
    """Base exception class for BladeFighters-specific errors."""
    pass


class ConfigurationError(BladeFightersError):
    """Raised when configuration operations fail."""
    pass


class AssetError(BladeFightersError):
    """Raised when asset loading or processing fails."""
    pass


class GameStateError(BladeFightersError):
    """Raised when game state operations fail."""
    pass


class InputError(BladeFightersError):
    """Raised when input processing fails."""
    pass


class AudioError(BladeFightersError):
    """Raised when audio operations fail."""
    pass


def safe_operation(
    operation_name: str,
    default_return: Any = None,
    log_level: str = "ERROR",
    reraise: bool = False,
    module_name: Optional[str] = None
) -> Callable:
    """
    Decorator for safe operations with standardized error handling.
    
    Args:
        operation_name: Human-readable name of the operation
        default_return: Value to return if operation fails
        log_level: Logging level for errors ("ERROR", "WARNING", "INFO")
        reraise: Whether to re-raise the exception after logging
        module_name: Optional module name for logging context
    
    Returns:
        Decorated function that handles exceptions gracefully
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Any]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, Any]:
            logger = get_logger(module_name or func.__module__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error with context
                log_message = f"Operation '{operation_name}' failed: {str(e)}"
                
                if log_level.upper() == "ERROR":
                    logger.error(log_message, exc_info=True)
                elif log_level.upper() == "WARNING":
                    logger.warning(log_message)
                else:
                    logger.info(log_message)
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def safe_file_operation(
    operation_name: str,
    file_path: str,
    default_return: Any = None,
    module_name: Optional[str] = None
) -> Callable:
    """
    Decorator specifically for file operations with detailed error context.
    
    Args:
        operation_name: Human-readable name of the file operation
        file_path: Path to the file being operated on
        default_return: Value to return if operation fails
        module_name: Optional module name for logging context
    
    Returns:
        Decorated function that handles file operation exceptions
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Any]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, Any]:
            logger = get_logger(module_name or func.__module__)
            
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                logger.error(f"File not found for '{operation_name}': {file_path}")
                return default_return
            except PermissionError as e:
                logger.error(f"Permission denied for '{operation_name}': {file_path}")
                return default_return
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in '{operation_name}': {file_path} - {str(e)}")
                return default_return
            except Exception as e:
                logger.error(f"Unexpected error in '{operation_name}' for {file_path}: {str(e)}", exc_info=True)
                return default_return
        
        return wrapper
    return decorator


def safe_value_conversion(
    value: Any,
    target_type: type,
    default_value: Any,
    operation_name: str = "value conversion",
    module_name: Optional[str] = None
) -> Any:
    """
    Safely convert a value to a target type with fallback.
    
    Args:
        value: Value to convert
        target_type: Target type (int, float, bool, str)
        default_value: Default value if conversion fails
        operation_name: Name of the operation for logging
        module_name: Optional module name for logging context
    
    Returns:
        Converted value or default_value if conversion fails
    """
    logger = get_logger(module_name or __name__)
    
    try:
        if target_type == bool:
            return bool(value)
        elif target_type == int:
            return int(float(value))  # Handle string floats
        elif target_type == float:
            return float(value)
        elif target_type == str:
            return str(value).strip()
        else:
            return target_type(value)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to convert value '{value}' to {target_type.__name__} in {operation_name}: {str(e)}")
        return default_value


def safe_range_clamp(
    value: Any,
    min_val: Union[int, float],
    max_val: Union[int, float],
    default_value: Union[int, float],
    operation_name: str = "range clamping",
    module_name: Optional[str] = None
) -> Union[int, float]:
    """
    Safely clamp a value to a range with fallback.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        default_value: Default value if clamping fails
        operation_name: Name of the operation for logging
        module_name: Optional module name for logging context
    
    Returns:
        Clamped value or default_value if operation fails
    """
    logger = get_logger(module_name or __name__)
    
    try:
        numeric_value = float(value)
        return max(min_val, min(max_val, numeric_value))
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to clamp value '{value}' to range [{min_val}, {max_val}] in {operation_name}: {str(e)}")
        return default_value


def log_and_continue(
    error_message: str,
    default_return: Any = None,
    log_level: str = "WARNING",
    module_name: Optional[str] = None
) -> Callable:
    """
    Decorator that logs errors and continues execution.
    
    Args:
        error_message: Template message for the error
        default_return: Value to return if operation fails
        log_level: Logging level for errors
        module_name: Optional module name for logging context
    
    Returns:
        Decorated function that logs errors and continues
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Any]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, Any]:
            logger = get_logger(module_name or func.__module__)
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                message = f"{error_message}: {str(e)}"
                
                if log_level.upper() == "ERROR":
                    logger.error(message)
                elif log_level.upper() == "WARNING":
                    logger.warning(message)
                else:
                    logger.info(message)
                
                return default_return
        
        return wrapper
    return decorator


 