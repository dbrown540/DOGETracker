"""
Logger Module
============

This module provides utilities for configuring and using logging throughout the application.

Examples:
    Basic usage:
    
    from src.utils.logger import initialize_logger, get_logger
    
    # Initialize the root logger (typically in main.py or app startup)
    initialize_logger(level='INFO')
    
    # Get a logger in any module and use it
    logger = get_logger(__name__)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    ```
    
    Advanced usage with file logging:
    
    ```python
    from src.utils.logger import initialize_logger, get_logger
    
    # Initialize with file logging enabled
    initialize_logger(
        level='DEBUG',
        log_to_file=True,
        log_dir='app_logs',
        log_file='doge_tracker.log',
        max_file_size_mb=5,
        backup_count=3
    )
    
    # Get a logger for a specific component
    logger = get_logger("scraper.binance")
    logger.info("Starting Binance scraper")
    
    try:
        # Some code that might fail
        result = 1 / 0
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
    
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Literal

import coloredlogs

LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

def initialize_logger(  # pylint: disable=too-many-arguments
    level: LogLevel = 'DEBUG',
    log_to_file: bool = False,
    log_dir: str = 'logs',
    log_file: str = 'app.log',
    max_file_size_mb: int = 10,
    backup_count: int = 3,
    fmt: str = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
) -> None:
    """
    Initializes the root logger with the specified configuration.
    
    This function configures the root logger with colored output to console
    and optionally writes logs to a file with rotation support.
    
    Args:
        level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file in addition to console output
        log_dir: Directory to store log files (created if it doesn't exist)
        log_file: Name of the log file
        max_file_size_mb: Maximum size of each log file in MB before rotation
        backup_count: Number of backup log files to keep
        fmt: Log message format string
        
    Returns:
        None
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Set the log level
    logger.setLevel(getattr(logging, level))
    
    # Install colored logs for console output
    coloredlogs.install(
        level=level,
        logger=logger,
        fmt=fmt
    )
    
    # Add file handler if requested
    if log_to_file:
        try:
            # Create log directory if it doesn't exist
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, log_file)
            
            # Set up rotating file handler
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=max_file_size_mb * 1024 * 1024,  # Convert MB to bytes
                backupCount=backup_count
            )
            file_formatter = logging.Formatter(fmt)
            file_handler.setFormatter(file_formatter)
            
            # Add the handler to the logger
            logger.addHandler(file_handler)
            
            logger.debug("Log file initialized at %s", log_path)
        except OSError as err:
            logger.warning(
                "Ran into an OS error while attempting to create a"
                " new directory: %s. Continuing with stderr logs.", str(err)
            )

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module or component.
    
    Args:
        name: The name for the logger, typically __name__ from the calling module
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)
