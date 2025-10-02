#!/usr/bin/env python3
"""
Example script demonstrating Oxylabs proxy integration with GSB-Selenium.

This example shows how to:
1. Configure Oxylabs proxy credentials
2. Test proxy connectivity
3. Run searches through the proxy
4. Use different proxy endpoints for different regions

Based on Oxylabs documentation: https://developers.oxylabs.io/scraping-apis/web-scraping-api/python
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import gsb_selenium
sys.path.insert(0, str(Path(__file__).parent.parent))

from gsb_selenium.core.config import GSBConfig
from gsb_selenium.core.gsb import GoogleSearchBot
from gsb_selenium.utils.proxy_tester import test_oxylabs_proxy_from_config, OxylabsProxyTester
from loguru import logger


def test_oxylabs_proxy_basic():
    """Test basic Oxylabs proxy connectivity."""
    logger.info("Testing basic Oxylabs proxy connectivity...")
    
    # Replace with your actual Oxylabs credentials
    USERNAME = "your_username"
    PASSWORD = "your_password"
    ENDPOINT = "pr.oxylabs.io:7777"  # Residential and Mobile Proxies
    
    if USERNAME == "your_username" or PASSWORD == "your_password":
        logger.error("Please update the USERNAME and PASSWORD variables with your actual Oxylabs credentials")
        return False
    
    # Test proxy connection
    results = OxylabsProxyTester.run_full_proxy_test(USERNAME, PASSWORD, ENDPOINT)
    
    if results["overall_status"] == "success":
        logger.success("✅ Oxylabs proxy test passed!")
        return True
    else:
        logger.error("❌ Oxylabs proxy test failed!")
        return False


def test_different_proxy_endpoints():
    """Test different Oxylabs proxy endpoints."""
    logger.info("Testing different Oxylabs proxy endpoints...")
    
    # Replace with your actual credentials
    USERNAME = "your_username"
    PASSWORD = "your_password"
    
    if USERNAME == "your_username" or PASSWORD == "your_password":
        logger.error("Please update the USERNAME and PASSWORD variables with your actual Oxylabs credentials")
        return
    
    # Different Oxylabs endpoints from the documentation
    endpoints = {
        "Residential and Mobile Proxies": "pr.oxylabs.io:7777",
        "Datacenter Proxies": "dc.oxylabs.io:8001", 
        "ISP Proxies": "isp.oxylabs.io:8001",
        "Self-Service Dedicated Datacenter": "ddc.oxylabs.io:8001",
        # Note: Enterprise Dedicated uses specific IP addresses like "1.2.3.4:60000"
    }
    
    for proxy_type, endpoint in endpoints.items():
        logger.info(f"\nTesting {proxy_type} ({endpoint})...")
        
        # Test just the IP check for each endpoint
        result = OxylabsProxyTester.test_proxy_connection(USERNAME, PASSWORD, endpoint)
        
        if result["status"] == "success":
            logger.success(f"✅ {proxy_type}: {result['message']}")
        else:
            logger.error(f"❌ {proxy_type}: {result['message']}")


def run_search_with_proxy():
    """Run a Google search using Oxylabs proxy."""
    logger.info("Running Google search with Oxylabs proxy...")
    
    # Configure GSB with proxy settings
    config = GSBConfig(
        # Proxy configuration
        use_proxy=True,
        proxy_username="your_username",  # Replace with your username
        proxy_password="your_password",  # Replace with your password
        proxy_endpoint="pr.oxylabs.io:7777",
        proxy_country="US",
        
        # Search configuration
        search_term="python web scraping",
        search_range_min=1,
        search_range_max=1,
        
        # Browser configuration
        headless=True,
        take_screenshots=False,
    )
    
    if config.proxy_username == "your_username" or config.proxy_password == "your_password":
        logger.error("Please update the proxy credentials in the GSBConfig")
        return
    
    # Test proxy configuration first
    logger.info("Testing proxy configuration...")
    test_result = test_oxylabs_proxy_from_config(config)
    
    if test_result["status"] == "error":
        logger.error(f"Proxy test failed: {test_result['message']}")
        return
    
    # Run the search bot
    try:
        bot = GoogleSearchBot(config, instance_id="oxylabs_example")
        logger.info("Starting search session with Oxylabs proxy...")
        bot.run_search_session(num_searches=1)
        logger.success("✅ Search completed successfully with Oxylabs proxy!")
        
    except Exception as e:
        logger.error(f"Search failed: {e}")


def main():
    """Main example function."""
    logger.info("Oxylabs Proxy Integration Example")
    logger.info("=" * 50)
    
    # Example 1: Test basic proxy connectivity
    logger.info("\n1. Testing basic proxy connectivity...")
    if not test_oxylabs_proxy_basic():
        logger.warning("Skipping remaining examples due to proxy test failure")
        return
    
    # Example 2: Test different endpoints (optional)
    logger.info("\n2. Testing different proxy endpoints...")
    # Uncomment the next line if you want to test multiple endpoints
    # test_different_proxy_endpoints()
    
    # Example 3: Run actual search with proxy
    logger.info("\n3. Running search with proxy...")
    # Uncomment the next line if you want to run a full search
    # run_search_with_proxy()
    
    logger.success("\n🎉 Oxylabs proxy integration examples completed!")
    
    logger.info("\n" + "=" * 50)
    logger.info("Next Steps:")
    logger.info("1. Update your .env file with Oxylabs credentials")
    logger.info("2. Test proxy: poetry run gsb test-proxy")
    logger.info("3. Run searches: poetry run gsb run")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()