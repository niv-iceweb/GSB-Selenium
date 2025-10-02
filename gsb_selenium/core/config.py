"""Configuration management for GSB-Selenium."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GSBConfig(BaseSettings):
    """Configuration settings for the Google Search Bot."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Search Configuration
    search_term: str = Field(default="marketing services", description="Base search terms")
    suffix: str = Field(default="", description="Domain suffix to append to searches")
    target_website: str = Field(default="", description="Target website to find and click")

    # Proxy Configuration (Hardcoded Oxylabs)
    # Note: Proxy is hardcoded with randomized session ID

    # 2Captcha Configuration (Optional)
    captcha_api_key: Optional[str] = Field(default=None, description="2Captcha API key")

    # Search Control
    search_range_min: int = Field(default=5, description="Minimum number of searches")
    search_range_max: int = Field(default=20, description="Maximum number of searches")
    click_probability: float = Field(default=0.3, description="Probability of clicking target website")

    # Timing Configuration
    min_typing_delay: float = Field(default=0.05, description="Minimum typing delay between characters")
    max_typing_delay: float = Field(default=0.15, description="Maximum typing delay between characters")
    min_action_delay: float = Field(default=1.0, description="Minimum delay between actions")
    max_action_delay: float = Field(default=3.0, description="Maximum delay between actions")
    
    # Anti-Detection Timing (Request Pattern Optimization)
    min_search_interval: float = Field(default=60.0, description="Minimum seconds between searches (1-2 per minute)")
    max_search_interval: float = Field(default=120.0, description="Maximum seconds between searches")
    min_session_delay: float = Field(default=300.0, description="Minimum seconds between search sessions (5 minutes)")
    max_session_delay: float = Field(default=900.0, description="Maximum seconds between search sessions (15 minutes)")
    behavior_variation_factor: float = Field(default=0.3, description="Random variation in timing patterns (0.0-1.0)")

    # MongoDB Configuration
    mongo_uri: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URI")
    mongo_database: str = Field(default="gsb_selenium", description="MongoDB database name")
    use_mongodb: bool = Field(default=False, description="Use MongoDB instead of file-based storage")

    # Paths (fallback for file-based storage)
    search_list_path: Path = Field(default=Path("./data/search_terms.txt"), description="Path to search terms file")
    logs_path: Path = Field(default=Path("./logs"), description="Path to logs directory")
    screenshots_path: Path = Field(default=Path("./data/screenshots"), description="Path to screenshots directory")

    # Browser Options
    headless: bool = Field(default=False, description="Run browser in headless mode")
    window_width: int = Field(default=1920, description="Browser window width")
    window_height: int = Field(default=1080, description="Browser window height")
    
    # Browser Fingerprint Alignment
    proxy_country: Optional[str] = Field(default=None, description="Proxy country code for geo-aligned fingerprinting")
    use_residential_fingerprints: bool = Field(default=True, description="Use residential-appropriate browser settings")
    match_locale_to_proxy: bool = Field(default=True, description="Align browser locale with proxy geography")
    enable_selenium_stealth: bool = Field(default=True, description="Enable selenium-stealth for advanced anti-detection")

    # Advanced Features
    block_resources: bool = Field(default=False, description="Block unnecessary resources for performance")
    take_screenshots: bool = Field(default=True, description="Take screenshots during execution")
    human_like_behavior: bool = Field(default=True, description="Enable human-like behavior patterns")
    use_undetected_chrome: bool = Field(default=True, description="Use undetected-chromedriver for stealth")
    
    # Profile Configuration
    use_profiles: bool = Field(default=True, description="Enable Chrome profile creation")
    cleanup_profiles: bool = Field(default=True, description="Auto-cleanup profiles after use")
    profile_template_dir: Optional[str] = Field(default=None, description="Custom template directory (optional)")

    @property
    def proxy_string(self) -> str:
        """Generate hardcoded Oxylabs proxy string with randomized session ID."""
        import random
        
        # Generate random session ID between 606150694 and 606250693
        sessid = random.randint(606150694, 606250693)
        
        return f"https://customer-nivos_qR24w-cc-us-sessid-{sessid}-sesstime-10:Niv220niv220_@pr.oxylabs.io:7777"

    @property
    def final_search_term(self) -> str:
        """Combine search terms with suffix."""
        if self.suffix:
            return f"{self.search_term} {self.suffix}"
        return self.search_term

    def get_user_agents(self, country_code: Optional[str] = None) -> list[str]:
        """Get top 50 Windows Chrome user agents for rotation."""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        ]