"""Timing utilities for human-like behavior."""

import asyncio
import random
import time
from typing import Tuple


def human_sleep(min_seconds: float, max_seconds: float) -> None:
    """Sleep for a random duration between min and max seconds."""
    duration = random.uniform(min_seconds, max_seconds)
    time.sleep(duration)


def typing_delay() -> None:
    """Add a small random delay between keystrokes."""
    time.sleep(random.uniform(0.05, 0.15))


def action_delay(min_delay: float = 1.0, max_delay: float = 3.0) -> None:
    """Add a delay between major actions."""
    human_sleep(min_delay, max_delay)


def get_random_scroll_amount() -> Tuple[int, int]:
    """Get random scroll amounts for natural scrolling behavior."""
    x_scroll = random.randint(-10, 50)
    y_scroll = random.randint(100, 500)
    return x_scroll, y_scroll


def gradual_type(element, text: str, typing_speed: Tuple[float, float] = (0.05, 0.15)) -> None:
    """Type text gradually with human-like timing using Selenium."""
    from loguru import logger
    
    logger.debug(f"gradual_type called with typing_speed: {typing_speed}")
    
    # Clear the element first
    element.clear()
    
    for char in text:
        element.send_keys(char)
        try:
            delay = random.uniform(*typing_speed)
        except TypeError as e:
            logger.error(f"Error unpacking typing_speed {typing_speed}: {e}")
            raise
        time.sleep(delay)


class TimingPattern:
    """Manages timing patterns for different activities."""
    
    def __init__(self):
        """Initialize timing patterns."""
        self.patterns = {
            "search": (1.0, 3.0),
            "navigation": (2.0, 4.0),
            "click": (0.5, 1.5),
            "typing": (0.05, 0.15),
            "page_load": (3.0, 7.0),
            "captcha_solve": (15.0, 30.0),
        }
    
    def wait_for(self, activity: str) -> None:
        """Wait for an appropriate time for the given activity."""
        if activity in self.patterns:
            min_time, max_time = self.patterns[activity]
            human_sleep(min_time, max_time)
        else:
            human_sleep(1.0, 2.0)  # Default
    
    def get_pattern(self, activity: str) -> Tuple[float, float]:
        """Get timing pattern for an activity."""
        return self.patterns.get(activity, (1.0, 2.0))


class PerformanceTimer:
    """Timer for measuring operation performance."""
    
    def __init__(self):
        """Initialize the performance timer."""
        self.start_time: float = 0.0
        self.end_time: float = 0.0
    
    def start(self) -> None:
        """Start timing."""
        self.start_time = time.perf_counter()
    
    def stop(self) -> float:
        """Stop timing and return duration."""
        self.end_time = time.perf_counter()
        return self.end_time - self.start_time
    
    @property
    def duration(self) -> float:
        """Get the duration of the last measurement."""
        return self.end_time - self.start_time