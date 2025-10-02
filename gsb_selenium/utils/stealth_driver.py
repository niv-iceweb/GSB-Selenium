import random
from pathlib import Path
from typing import Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import seleniumwire.undetected_chromedriver as wire_webdriver
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from selenium_stealth import stealth
from loguru import logger

from .timing import human_sleep, typing_delay
from .profile_manager import ChromeProfileManager


class StealthDriver:
    """Enhanced Selenium WebDriver with advanced stealth features."""
    
    def __init__(self, config, instance_id: str = "main"):
        """Initialize the stealth driver."""
        self.config = config
        self.instance_id = instance_id
        self.driver = None
        self.user_agent = UserAgent()
        self.profile_manager = ChromeProfileManager(config, instance_id)
        self.current_profile = None
        
    def create_driver(self) -> webdriver.Chrome:
        """Create and configure the Chrome driver with stealth features."""
        
        # Create Chrome profile if enabled
        if self.config.use_profiles:
            self.current_profile = self.profile_manager.create_random_profile()
        
        # Configure Chrome options
        options = self._create_chrome_options()
        
        # Configure proxy (always available since hardcoded)
        seleniumwire_options = self._create_proxy_options()
        
        # Use selenium-wire for proxy support (always used since proxy is hardcoded)
        # service = Service(ChromeDriverManager().install())
        self.driver = wire_webdriver.Chrome(
            options=options,
            seleniumwire_options=seleniumwire_options
        )
        
        # Apply selenium-stealth for comprehensive anti-detection
        # self._apply_selenium_stealth()
        
        # Set window size with randomization
        # self._set_random_window_size()
        
        logger.info(f"StealthDriver created for instance {self.instance_id}")
        return self.driver
    
    def _create_chrome_options(self) -> ChromeOptions:
        """Create Chrome options with stealth features."""
        options = wire_webdriver.ChromeOptions()
        
        # Headless mode
        if self.config.headless:
            options.add_argument("--headless=new")
        
        # User agent
        if self.config.use_residential_fingerprints:
            user_agents = self.config.get_user_agents(self.config.proxy_country)
            selected_ua = random.choice(user_agents)
            options.add_argument(f"--user-agent={selected_ua}")
        
        # Profile configuration
        if self.current_profile:
            profile_args = self.profile_manager.get_profile_arguments(self.current_profile)
            # log profile args
            logger.info(f"Profile args: {profile_args}")
            if profile_args:
                options.add_argument(f"--user-data-dir={profile_args['user_data_dir']}")
                options.add_argument(f"--profile-directory={profile_args['profile_directory']}")
                logger.info(f"Using Chrome profile: {self.current_profile}")
        
        return options
    
    def _create_proxy_options(self) -> Dict[str, Any]:
        """Create selenium-wire proxy options with hardcoded Oxylabs proxy."""
        proxy_string = self.config.proxy_string
        
        return {
            "proxy": {
                "http": proxy_string,
                "https": proxy_string,
            }
        }
    
    def _apply_selenium_stealth(self):
        """Apply selenium-stealth for comprehensive anti-detection."""
        if not self.driver:
            return
        
        # Get country-specific settings for better fingerprint alignment
        proxy_country = self.config.proxy_country or "US"
        
        # Define WebGL profiles for different countries/regions
        webgl_profiles = {
            "US": {
                "vendor": "Google Inc. (NVIDIA)",
                "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11-27.21.14.5671)"
            },
            "GB": {
                "vendor": "Google Inc. (Intel)",
                "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"
            },
            "DE": {
                "vendor": "Google Inc. (AMD)",
                "renderer": "ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.13025.1000)"
            }
        }
        
        # Select WebGL profile based on proxy country
        import random
        webgl_profile = webgl_profiles.get(proxy_country, webgl_profiles["US"])
        
        # Randomize between available profiles for variety
        all_profiles = list(webgl_profiles.values())
        webgl_profile = random.choice(all_profiles)
        
        # Apply selenium-stealth with comprehensive settings
        try:
            stealth(
                self.driver,
                languages=["en-US", "en"] if proxy_country == "US" else ["en-GB", "en"] if proxy_country == "GB" else ["de-DE", "de", "en"],
                vendor="Google Inc.",
                platform="Win32" if proxy_country == "US" else "MacIntel" if random.random() > 0.7 else "Win32",
                webgl_vendor=webgl_profile["vendor"],
                renderer=webgl_profile["renderer"],
                fix_hairline=True,
                run_on_insecure_origins=True,
            )
            
            logger.info(f"selenium-stealth applied successfully")
            logger.info(f"WebGL Vendor: {webgl_profile['vendor']}")
            logger.info(f"WebGL Renderer: {webgl_profile['renderer'][:50]}...")
            
        except Exception as e:
            logger.warning(f"Failed to apply selenium-stealth: {e}")
            # Fallback to basic stealth features
            self._apply_basic_stealth_fallback()
    
    def _apply_basic_stealth_fallback(self):
        """Apply basic stealth features as fallback if selenium-stealth fails."""
        try:
            # Hide webdriver property
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                    configurable: true
                });
            """)
            
            # Override permissions
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'permissions', {
                    get: () => ({
                        query: () => Promise.resolve({ state: 'granted' })
                    })
                });
            """)
            
            # Override plugins
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            logger.info("Basic stealth fallback applied")
            
        except Exception as e:
            logger.error(f"Failed to apply basic stealth fallback: {e}")
    def _set_random_window_size(self):
        """Set random window size for fingerprint variation."""
        if not self.driver:
            return
        
        # Random window sizes that look natural
        sizes = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
            (1280, 720), (1600, 900), (1024, 768), (1280, 800)
        ]
        
        if self.config.use_residential_fingerprints:
            width, height = random.choice(sizes)
        else:
            width, height = self.config.window_width, self.config.window_height
        
        self.driver.set_window_size(width, height)
        logger.debug(f"Window size set to {width}x{height}")
    
    def human_click(self, element, offset_range: int = 5):
        """Perform human-like click with random offset."""
        if not self.driver:
            return
        
        # Scroll element into view
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        human_sleep(0.3, 0.7)
        
        # Move to element with human-like behavior
        actions = ActionChains(self.driver)
        
        # Add random offset to make click more human-like
        x_offset = random.randint(-offset_range, offset_range)
        y_offset = random.randint(-offset_range, offset_range)
        
        actions.move_to_element_with_offset(element, x_offset, y_offset)
        human_sleep(0.1, 0.3)  # Pause before click
        actions.click()
        actions.perform()
        
        human_sleep(0.2, 0.5)  # Pause after click
    
    def human_type(self, element, text: str, clear_first: bool = True):
        """Type text with human-like behavior."""
        if not self.driver:
            return
        
        # Focus on element
        element.click()
        human_sleep(0.1, 0.3)
        
        if clear_first:
            element.clear()
            human_sleep(0.1, 0.2)
        
        # Type character by character with random delays
        for char in text:
            element.send_keys(char)
            typing_delay()
    
    def random_scroll(self, direction: str = "down", pixels: Optional[int] = None):
        """Perform random scrolling to simulate human behavior."""
        if not self.driver:
            return
        
        if pixels is None:
            pixels = random.randint(100, 500)
        
        if direction.lower() == "down":
            self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        elif direction.lower() == "up":
            self.driver.execute_script(f"window.scrollBy(0, -{pixels});")
        
        human_sleep(0.5, 1.5)
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element with timeout."""
        if not self.driver:
            return None
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
    
    def safe_find_element(self, by: By, value: str):
        """Safely find element without throwing exception."""
        if not self.driver:
            return None
        
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            return None
    
    def take_screenshot(self, filename: str):
        """Take screenshot if enabled."""
        if not self.driver or not self.config.take_screenshots:
            return
        
        screenshots_dir = Path(self.config.screenshots_path)
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = screenshots_dir / filename
        self.driver.save_screenshot(str(filepath))
        logger.debug(f"Screenshot saved: {filepath}")
    
    def quit(self):
        """Quit the driver and cleanup."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info(f"StealthDriver quit for instance {self.instance_id}")
        
        # Cleanup Chrome profile
        if self.current_profile:
            self.profile_manager.cleanup_profile(self.current_profile)
            self.current_profile = None
    
    def __enter__(self):
        """Context manager entry."""
        self.create_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()


