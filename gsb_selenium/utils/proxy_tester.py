"""Proxy testing utilities for Oxylabs integration."""

import re
from typing import Optional

from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger


class OxylabsProxyTester:
    """Test Oxylabs proxy connectivity and functionality."""

    @staticmethod
    def test_proxy_connection(username: str, password: str, endpoint: str) -> dict:
        """
        Test proxy connection using the Oxylabs documentation approach.
        
        Args:
            username: Oxylabs proxy username
            password: Oxylabs proxy password
            endpoint: Proxy endpoint (e.g., "pr.oxylabs.io:7777")
            
        Returns:
            dict: Test results with IP address and status
        """
        wire_options = {
            "proxy": {
                "http": f"http://{username}:{password}@{endpoint}",
                "https": f"https://{username}:{password}@{endpoint}",
            }
        }

        driver = None
        try:
            # Setup Chrome options
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Create service with webdriver-manager
            service = Service(ChromeDriverManager().install())
            
            # Create driver with proxy
            driver = webdriver.Chrome(
                service=service,
                options=options,
                seleniumwire_options=wire_options
            )
            
            logger.info("Testing proxy connection to ip.oxylabs.io...")
            
            # Navigate to Oxylabs IP checker
            driver.get("https://ip.oxylabs.io/")
            
            # Extract IP address from page
            ip_match = re.search(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", driver.page_source)
            
            if ip_match:
                proxy_ip = ip_match.group()
                logger.success(f"Proxy test successful! Your IP is: {proxy_ip}")
                return {
                    "status": "success",
                    "ip": proxy_ip,
                    "message": f"Proxy connection successful. IP: {proxy_ip}"
                }
            else:
                logger.error("Could not extract IP address from response")
                return {
                    "status": "error",
                    "ip": None,
                    "message": "Could not extract IP address from proxy response"
                }
                
        except Exception as e:
            error_msg = f"Proxy test failed: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "ip": None,
                "message": error_msg
            }
            
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing driver: {e}")

    @staticmethod
    def test_google_search_with_proxy(username: str, password: str, endpoint: str, 
                                    search_term: str = "test search") -> dict:
        """
        Test Google search functionality with proxy.
        
        Args:
            username: Oxylabs proxy username
            password: Oxylabs proxy password  
            endpoint: Proxy endpoint
            search_term: Search term to test with
            
        Returns:
            dict: Test results
        """
        wire_options = {
            "proxy": {
                "http": f"http://{username}:{password}@{endpoint}",
                "https": f"https://{username}:{password}@{endpoint}",
            }
        }

        driver = None
        try:
            # Setup Chrome options
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Create service with webdriver-manager
            service = Service(ChromeDriverManager().install())
            
            # Create driver with proxy
            driver = webdriver.Chrome(
                service=service,
                options=options,
                seleniumwire_options=wire_options
            )
            
            logger.info(f"Testing Google search with proxy: '{search_term}'")
            
            # Navigate to Google
            driver.get("https://www.google.com")
            
            # Find search box and perform search
            search_box = driver.find_element("name", "q")
            search_box.send_keys(search_term)
            search_box.submit()
            
            # Wait for results and check if we got them
            driver.implicitly_wait(10)
            results = driver.find_elements("css selector", "#search .g")
            
            if results:
                logger.success(f"Google search test successful! Found {len(results)} results")
                return {
                    "status": "success",
                    "results_count": len(results),
                    "message": f"Google search successful. Found {len(results)} results for '{search_term}'"
                }
            else:
                logger.warning("Google search completed but no results found")
                return {
                    "status": "warning", 
                    "results_count": 0,
                    "message": "Google search completed but no results found"
                }
                
        except Exception as e:
            error_msg = f"Google search test failed: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "results_count": 0,
                "message": error_msg
            }
            
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing driver: {e}")

    @classmethod
    def run_full_proxy_test(cls, username: str, password: str, endpoint: str) -> dict:
        """
        Run comprehensive proxy testing suite.
        
        Args:
            username: Oxylabs proxy username
            password: Oxylabs proxy password
            endpoint: Proxy endpoint
            
        Returns:
            dict: Complete test results
        """
        logger.info("Starting comprehensive Oxylabs proxy test...")
        
        results = {
            "proxy_connection": cls.test_proxy_connection(username, password, endpoint),
            "google_search": cls.test_google_search_with_proxy(username, password, endpoint)
        }
        
        # Overall status
        if all(test["status"] == "success" for test in results.values()):
            results["overall_status"] = "success"
            logger.success("All proxy tests passed!")
        elif any(test["status"] == "success" for test in results.values()):
            results["overall_status"] = "partial"
            logger.warning("Some proxy tests passed, some failed")
        else:
            results["overall_status"] = "failed"
            logger.error("All proxy tests failed")
        
        return results


def test_oxylabs_proxy_from_config(config) -> dict:
    """
    Test Oxylabs proxy using GSB configuration.
    
    Args:
        config: GSBConfig instance
        
    Returns:
        dict: Test results
    """
    if not config.use_proxy or not config.proxy_username or not config.proxy_password:
        return {
            "status": "error",
            "message": "Proxy not configured. Please set use_proxy=True and provide proxy credentials."
        }
    
    return OxylabsProxyTester.run_full_proxy_test(
        config.proxy_username,
        config.proxy_password, 
        config.proxy_endpoint
    )