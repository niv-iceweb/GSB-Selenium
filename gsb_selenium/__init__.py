"""GSB-Selenium: Advanced Google Search Bot using Selenium."""

from .core.config import GSBConfig
from .core.gsb import GoogleSearchBot

__version__ = "1.0.0"
__all__ = ["GSBConfig", "GoogleSearchBot"]