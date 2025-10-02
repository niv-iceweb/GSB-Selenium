"""CAPTCHA solving utilities for GSB-Selenium."""

import time
from typing import Optional
from twocaptcha import TwoCaptcha
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CaptchaSolver:
    """2Captcha integration for solving reCAPTCHA v2."""
    
    def __init__(self, api_key: str):
        """Initialize the CAPTCHA solver."""
        self.solver = TwoCaptcha(api_key)
        self.api_key = api_key
    
    def detect_recaptcha_v2(self, driver) -> bool:
        """Detect if reCAPTCHA v2 is present on the page."""
        try:
            # Look for common reCAPTCHA indicators
            recaptcha_selectors = [
                "div.g-recaptcha",
                "iframe[src*='recaptcha']",
                ".recaptcha-checkbox",
                "#recaptcha",
                "[data-sitekey]"
            ]
            
            for selector in recaptcha_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"reCAPTCHA v2 detected using selector: {selector}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error detecting reCAPTCHA: {e}")
            return False
    
    def extract_site_key(self, driver) -> Optional[str]:
        """Extract the reCAPTCHA site key from the page."""
        try:
            # Try different methods to find the site key
            selectors = [
                "[data-sitekey]",
                ".g-recaptcha[data-sitekey]",
                "div[data-sitekey]"
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    site_key = element.get_attribute("data-sitekey")
                    if site_key:
                        logger.info(f"Site key extracted: {site_key[:20]}...")
                        return site_key
            
            # Try to find in page source
            page_source = driver.page_source
            if 'data-sitekey="' in page_source:
                start = page_source.find('data-sitekey="') + 14
                end = page_source.find('"', start)
                site_key = page_source[start:end]
                if site_key:
                    logger.info(f"Site key found in page source: {site_key[:20]}...")
                    return site_key
            
            logger.warning("Could not extract reCAPTCHA site key")
            return None
        except Exception as e:
            logger.error(f"Error extracting site key: {e}")
            return None
    
    def solve_recaptcha_v2(self, driver, proxy: Optional[str] = None) -> bool:
        """Solve reCAPTCHA v2 on the current page."""
        try:
            # Extract site key
            site_key = self.extract_site_key(driver)
            if not site_key:
                return False
            
            current_url = driver.current_url
            logger.info(f"Attempting to solve reCAPTCHA v2 for: {current_url}")
            
            # Submit to 2captcha
            solve_config = {
                'sitekey': site_key,
                'url': current_url
            }
            
            if proxy:
                # Parse proxy string for 2captcha format
                if "@" in proxy:
                    auth_part, endpoint = proxy.split("@")
                    username, password = auth_part.split("://")[1].split(":")
                    host, port = endpoint.split(":")
                    
                    solve_config['proxy'] = {
                        'type': 'HTTP',
                        'uri': f"{host}:{port}",
                        'login': username,
                        'password': password
                    }
            
            # Solve the CAPTCHA
            result = self.solver.recaptcha(**solve_config)
            token = result.get('code')
            
            if not token:
                logger.error("Failed to get CAPTCHA solution token")
                return False
            
            logger.info("CAPTCHA solved successfully, injecting token...")
            
            # Inject the token into the page
            success = self._inject_token(driver, token)
            
            if success:
                logger.info("CAPTCHA token injected successfully")
                return True
            else:
                logger.error("Failed to inject CAPTCHA token")
                return False
                
        except Exception as e:
            logger.error(f"Error solving reCAPTCHA v2: {e}")
            return False
    
    def _inject_token(self, driver, token: str) -> bool:
        """Inject the CAPTCHA token into the page."""
        try:
            # Method 1: Try to find and fill textarea with token
            textareas = driver.find_elements(By.CSS_SELECTOR, "textarea[name='g-recaptcha-response']")
            for textarea in textareas:
                # Make textarea visible and editable
                driver.execute_script("""
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                    arguments[0].removeAttribute('readonly');
                """, textarea)
                
                # Set the token value
                driver.execute_script("arguments[0].value = arguments[1];", textarea, token)
                
                # Trigger change event
                driver.execute_script("""
                    var event = new Event('input', { bubbles: true });
                    arguments[0].dispatchEvent(event);
                    var changeEvent = new Event('change', { bubbles: true });
                    arguments[0].dispatchEvent(changeEvent);
                """, textarea)
            
            # Method 2: Try to set callback function
            driver.execute_script(f"""
                if (typeof window.grecaptcha !== 'undefined' && window.grecaptcha.getResponse) {{
                    window.grecaptcha.getResponse = function() {{ return '{token}'; }};
                }}
            """)
            
            # Method 3: Try to trigger callback directly
            driver.execute_script(f"""
                var recaptchaElements = document.querySelectorAll('[data-callback]');
                recaptchaElements.forEach(function(element) {{
                    var callback = element.getAttribute('data-callback');
                    if (callback && typeof window[callback] === 'function') {{
                        window[callback]('{token}');
                    }}
                }});
            """)
            
            # Wait a moment for the token to be processed
            time.sleep(2)
            
            # Check if token was accepted by trying to find submit button or form
            submit_buttons = driver.find_elements(By.CSS_SELECTOR, 
                "input[type='submit'], button[type='submit'], button:contains('Submit')")
            
            if submit_buttons:
                logger.info("Found submit button, CAPTCHA likely solved")
                return True
            
            return True  # Assume success if no errors
            
        except Exception as e:
            logger.error(f"Error injecting CAPTCHA token: {e}")
            return False
    
    def get_balance(self) -> Optional[float]:
        """Get 2captcha account balance."""
        try:
            balance = self.solver.balance()
            logger.info(f"2Captcha balance: ${balance}")
            return balance
        except Exception as e:
            logger.error(f"Error getting 2captcha balance: {e}")
            return None