"""Logging utilities for GSB-Selenium."""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from loguru import logger


def setup_logger(config, instance_id: str = "main"):
    """Set up structured logging for the GSB instance."""
    # Remove default handler
    logger.remove()
    
    # Ensure logs directory exists
    logs_dir = Path(config.logs_path)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Main log file
    logger.add(
        logs_dir / f"gsb_{instance_id}.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    # Error log file
    logger.add(
        logs_dir / f"gsb_errors_{instance_id}.log",
        rotation="1 day",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR"
    )
    
    # Success log file
    logger.add(
        logs_dir / f"gsb_success_{instance_id}.log",
        rotation="1 day",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        filter=lambda record: "SUCCESS" in record["message"] or record["level"].name == "SUCCESS"
    )


def log_search_start(search_term: str, instance_id: str):
    """Log the start of a search."""
    logger.info(f"[{instance_id}] Starting search for: '{search_term}'")


def log_search_completion(search_term: str, instance_id: str, duration: float, success: bool):
    """Log search completion."""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"[{instance_id}] Search '{search_term}' completed in {duration:.2f}s - {status}")


def log_target_found(target_website: str, instance_id: str, clicked: bool = False):
    """Log when target website is found."""
    action = "clicked" if clicked else "found"
    logger.info(f"[{instance_id}] Target website '{target_website}' {action}")


def log_captcha_detection(captcha_type: str, instance_id: str):
    """Log CAPTCHA detection."""
    logger.warning(f"[{instance_id}] CAPTCHA detected: {captcha_type}")


def log_proxy_info(proxy_string: str, instance_id: str):
    """Log proxy information."""
    # Mask credentials in log
    masked_proxy = proxy_string.replace("://", "://***:***@") if "@" in proxy_string else proxy_string
    logger.info(f"[{instance_id}] Using proxy: {masked_proxy}")


def log_error(error_msg: str, instance_id: str, exception: Optional[Exception] = None):
    """Log error with optional exception details."""
    if exception:
        logger.error(f"[{instance_id}] {error_msg}: {str(exception)}")
    else:
        logger.error(f"[{instance_id}] {error_msg}")


def start_run(search_term: str, target_website: str) -> str:
    """Start a run and return run ID."""
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"Starting run {run_id} - Search: '{search_term}', Target: '{target_website}'")
    return run_id


def end_run(run_id: str, success: bool, duration: float):
    """End a run."""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Run {run_id} completed in {duration:.2f}s - {status}")