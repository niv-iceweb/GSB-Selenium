"""Core Google Search Bot implementation using Selenium."""

import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .config import GSBConfig
from ..utils.captcha_solver import CaptchaSolver
from ..utils.logger import (
    setup_logger,
    log_search_start,
    log_search_completion,
    log_target_found,
    log_captcha_detection,
    log_proxy_info,
    log_error,
    start_run,
    end_run,
)
from ..utils.stealth_driver import StealthDriver
from ..utils.mongo_search_manager import create_search_manager
from ..utils.timing import TimingPattern, PerformanceTimer, human_sleep


class GoogleSearchBot:
    """Advanced Google Search Bot using Selenium."""

    def __init__(self, config: GSBConfig, instance_id: str = "main"):
        """Initialize the Google Search Bot."""
        self.config = config
        self.instance_id = instance_id
        self.timing = TimingPattern()
        self.search_manager = create_search_manager(config)
        self.stealth_driver = StealthDriver(config, instance_id)
        
        # Initialize 2Captcha solver if API key is provided
        self.captcha_solver = None
        if config.captcha_api_key:
            try:
                self.captcha_solver = CaptchaSolver(config.captcha_api_key)
                logger.info("2Captcha solver initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize 2Captcha solver: {e}")
        else:
            logger.info("No 2Captcha API key provided - captcha solving disabled")
        
        # Initialize logging
        setup_logger(config, instance_id)
        logger.info(f"GSB-Selenium instance {instance_id} initialized")
        
        # Log proxy info (always configured since hardcoded)
        log_proxy_info(config.proxy_string, instance_id)

    def run_search_session(self, num_searches: Optional[int] = None) -> None:
        """Run a complete search session."""
        if num_searches is None:
            num_searches = random.randint(
                self.config.search_range_min, self.config.search_range_max
            )

        logger.info(f"Starting search session with {num_searches} searches")

        for search_num in range(num_searches):
            # Start run tracking for each individual search
            search_term = self.search_manager.get_next_search_term()
            run_id = start_run(search_term, self.config.target_website)
            
            timer = PerformanceTimer()
            timer.start()
            
            success = False
            target_clicked = False
            captcha_solved = False

            try:
                log_search_start(search_term, self.instance_id)
                
                # Create stealth driver for this search
                with self.stealth_driver as driver:
                    self.driver = driver.driver
                    
                    # Perform the search
                    success = self._perform_search(search_term)
                    
                    if success:
                        # Check for CAPTCHA
                        if self._detect_captcha():
                            captcha_solved = self._solve_captcha()
                            if not captcha_solved:
                                success = False
                        
                        # Look for target website if search was successful
                        if success and self.config.target_website:
                            target_clicked = self._find_and_click_target()
                
                duration = timer.stop()
                log_search_completion(search_term, self.instance_id, duration, success)
                
                # End run tracking
                end_run(run_id, success, duration)
                
                if target_clicked:
                    log_target_found(self.config.target_website, self.instance_id, clicked=True)
                
            except Exception as e:
                duration = timer.stop()
                log_error(f"Search failed", self.instance_id, e)
                end_run(run_id, False, duration)
            
            # Wait between searches (anti-detection timing)
            if search_num < num_searches - 1:  # Don't wait after the last search
                wait_time = random.uniform(
                    self.config.min_search_interval,
                    self.config.max_search_interval
                )
                logger.info(f"Waiting {wait_time:.1f}s before next search...")
                human_sleep(wait_time, wait_time)

    def _perform_search(self, search_term: str) -> bool:
        """Perform a Google search."""
        try:
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
            print(self.driver.execute_script("return navigator.userAgent;"))
            # Navigate to Google
            logger.info("Navigating to Google")
            self.driver.get("https://antcpt.com/score_detector/")

            # sleep for 10 seconds
            time.sleep(1000)
            
            # Wait for page load
            self.timing.wait_for("page_load")
            
            # Take screenshot if enabled
            if self.config.take_screenshots:
                self.stealth_driver.take_screenshot(f"google_homepage_{self.instance_id}_{int(time.time())}.png")
            
            # Find search box
            search_box = self._find_search_box()
            if not search_box:
                logger.error("Could not find Google search box")
                return False
            
            # Type search term with human-like behavior
            logger.info(f"Typing search term: '{search_term}'")
            self.stealth_driver.human_type(search_box, search_term)
            
            # Wait before submitting
            self.timing.wait_for("typing")
            
            # Submit search
            search_box.submit()
            
            # Wait for results to load
            self.timing.wait_for("page_load")
            
            # Verify we're on results page
            if not self._verify_search_results():
                logger.error("Search results page not loaded properly")
                return False
            
            # Take screenshot of results
            if self.config.take_screenshots:
                self.stealth_driver.take_screenshot(f"search_results_{self.instance_id}_{int(time.time())}.png")
            
            # Random scroll to simulate reading results
            if self.config.human_like_behavior:
                self._simulate_human_browsing()
            
            logger.info("Search completed successfully")
            return True
            
        except Exception as e:
            log_error("Error performing search", self.instance_id, e)
            return False

    def _find_search_box(self):
        """Find the Google search input box."""
        search_selectors = [
            "input[name='q']",
            "input[title='Search']",
            "textarea[name='q']",
            "#searchboxinput",
            ".gLFyf"
        ]
        
        for selector in search_selectors:
            element = self.stealth_driver.safe_find_element(By.CSS_SELECTOR, selector)
            if element and element.is_displayed():
                return element
        
        return None

    def _verify_search_results(self) -> bool:
        """Verify that search results page loaded."""
        try:
            # Wait for search results to appear
            wait = WebDriverWait(self.driver, 10)
            
            # Look for common search result indicators
            result_selectors = [
                "#search",
                ".g",
                "#rso",
                ".srg"
            ]
            
            for selector in result_selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.debug(f"Search results verified using selector: {selector}")
                    return True
                except TimeoutException:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying search results: {e}")
            return False

    def _simulate_human_browsing(self):
        """Simulate human-like browsing behavior."""
        try:
            # Random scrolling
            scroll_actions = random.randint(2, 5)
            for _ in range(scroll_actions):
                self.stealth_driver.random_scroll("down")
                human_sleep(0.5, 2.0)
            
            # Sometimes scroll back up
            if random.random() < 0.3:
                self.stealth_driver.random_scroll("up")
                human_sleep(0.5, 1.0)
            
        except Exception as e:
            logger.debug(f"Error in human browsing simulation: {e}")

    def _detect_captcha(self) -> bool:
        """Detect if CAPTCHA is present."""
        try:
            if self.captcha_solver:
                return self.captcha_solver.detect_recaptcha_v2(self.driver)
            
            # Basic CAPTCHA detection without solver
            captcha_selectors = [
                "div.g-recaptcha",
                "iframe[src*='recaptcha']",
                ".recaptcha-checkbox",
                "#recaptcha"
            ]
            
            for selector in captcha_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    log_captcha_detection("reCAPTCHA v2", self.instance_id)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {e}")
            return False

    def _solve_captcha(self) -> bool:
        """Solve detected CAPTCHA."""
        try:
            if not self.captcha_solver:
                logger.warning("CAPTCHA detected but no solver available")
                return False
            
            logger.info("Attempting to solve CAPTCHA...")
            proxy_string = self.config.proxy_string  # Always available since hardcoded
            
            success = self.captcha_solver.solve_recaptcha_v2(self.driver, proxy_string)
            
            if success:
                logger.info("CAPTCHA solved successfully")
                self.timing.wait_for("captcha_solve")
                return True
            else:
                logger.error("Failed to solve CAPTCHA")
                return False
                
        except Exception as e:
            log_error("Error solving CAPTCHA", self.instance_id, e)
            return False

    def _find_and_click_target(self) -> bool:
        """Find and click the target website in search results."""
        try:
            if not self.config.target_website:
                return False
            
            # Should we click the target based on probability?
            from ..utils.search_manager import should_click_target
            if not should_click_target(self.config):
                logger.info(f"Skipping target click based on probability ({self.config.click_probability})")
                return False
            
            logger.info(f"Looking for target website: {self.config.target_website}")
            
            # Find search result links
            result_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
            
            for link in result_links:
                try:
                    href = link.get_attribute("href")
                    if href and self.config.target_website.lower() in href.lower():
                        logger.info(f"Found target website link: {href}")
                        
                        # Scroll to element and click
                        self.stealth_driver.human_click(link)
                        
                        # Wait for page to load
                        self.timing.wait_for("page_load")
                        
                        # Take screenshot of target website
                        if self.config.take_screenshots:
                            self.stealth_driver.take_screenshot(f"target_website_{self.instance_id}_{int(time.time())}.png")
                        
                        # Simulate some browsing on target site
                        if self.config.human_like_behavior:
                            human_sleep(3.0, 8.0)  # Stay on site for a bit
                            self._simulate_human_browsing()
                        
                        return True
                        
                except Exception as e:
                    logger.debug(f"Error checking link: {e}")
                    continue
            
            logger.info(f"Target website '{self.config.target_website}' not found in results")
            return False
            
        except Exception as e:
            log_error("Error finding target website", self.instance_id, e)
            return False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Cleanup is handled by StealthDriver context manager
        pass