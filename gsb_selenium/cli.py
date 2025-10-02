"""Command-line interface for GSB-Selenium."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click
from loguru import logger

from .core.config import GSBConfig
from .core.aws_config import get_config
from .core.gsb import GoogleSearchBot


@click.group()
@click.version_option(version="1.0.0")
def main():
    """GSB-Selenium: Advanced Google Search Bot using Selenium."""
    pass


@main.command()
@click.option("--searches", "-s", type=int, help="Number of searches to perform")
@click.option("--instance-id", "-i", default="main", help="Instance identifier")
@click.option("--search-terms", "-t", help="Search terms to use")
@click.option("--target-website", "-w", help="Target website to find and click")
@click.option("--headless/--no-headless", default=None, help="Run browser in headless mode")
@click.option("--proxy", "-p", help="Proxy string (username:password@host:port)")
@click.option("--config-file", "-c", help="Path to configuration file")
def run(
    searches: Optional[int],
    instance_id: str,
    search_terms: Optional[str],
    target_website: Optional[str],
    headless: Optional[bool],
    proxy: Optional[str],
    config_file: Optional[str],
):
    """Run a single GSB-Selenium instance."""
    try:
        # Load configuration
        config_kwargs = {}
        
        # Override with CLI arguments
        if search_terms:
            config_kwargs["search_term"] = search_terms
        if target_website:
            config_kwargs["target_website"] = target_website
        if headless is not None:
            config_kwargs["headless"] = headless
        # Note: Proxy is now hardcoded in the configuration, CLI proxy option ignored
        if proxy:
            logger.warning("Proxy option ignored - using hardcoded Oxylabs proxy with randomized session ID")
        
        # Load config (will try AWS Parameter Store first, then .env)
        config = get_config(**config_kwargs)
        
        # Create and run bot
        bot = GoogleSearchBot(config, instance_id)
        bot.run_search_session(searches)
        
        logger.info(f"GSB-Selenium instance '{instance_id}' completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Search session interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running GSB-Selenium: {e}")
        sys.exit(1)


@main.command()
@click.option("--instances", "-n", default=3, help="Number of parallel instances")
@click.option("--searches-per-instance", "-s", default=5, help="Searches per instance")
@click.option("--headless/--no-headless", default=True, help="Run browsers in headless mode")
def run_parallel(instances: int, searches_per_instance: int, headless: bool):
    """Run multiple GSB-Selenium instances in parallel."""
    try:
        import concurrent.futures
        import threading
        
        def run_instance(instance_num: int):
            """Run a single instance."""
            instance_id = f"parallel_{instance_num:03d}"
            config = get_config(headless=headless)
            
            try:
                bot = GoogleSearchBot(config, instance_id)
                bot.run_search_session(searches_per_instance)
                logger.info(f"Instance {instance_id} completed successfully")
                return True
            except Exception as e:
                logger.error(f"Instance {instance_id} failed: {e}")
                return False
        
        logger.info(f"Starting {instances} parallel instances with {searches_per_instance} searches each")
        
        # Run instances in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=instances) as executor:
            futures = [
                executor.submit(run_instance, i) 
                for i in range(instances)
            ]
            
            # Wait for all to complete
            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        successful = sum(results)
        logger.info(f"Parallel execution completed: {successful}/{instances} instances successful")
        
    except KeyboardInterrupt:
        logger.info("Parallel execution interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running parallel instances: {e}")
        sys.exit(1)


@main.command()
def init_config():
    """Initialize configuration file."""
    try:
        env_file = Path(".env")
        
        if env_file.exists():
            logger.warning(".env file already exists")
            if not click.confirm("Overwrite existing .env file?"):
                return
        
        # Create default .env file
        env_content = """# GSB-Selenium Configuration

# Environment Detection
ENVIRONMENT=local
AWS_REGION=us-east-1

# Search Configuration
SEARCH_TERMS=marketing services
SUFFIX=
TARGET_WEBSITE=

# Proxy Configuration (Oxylabs)
PROXY_URL=us-pr.oxylabs.io
PROXY_PORT=7777
PROXY_USERNAME=
PROXY_PASSWORD=

# 2Captcha Configuration (Optional)
CAPTCHA_API_KEY=

# Search Control
SEARCH_RANGE_MIN=5
SEARCH_RANGE_MAX=20
CLICK_PROBABILITY=0.3

# Timing Configuration
MIN_TYPING_DELAY=0.05
MAX_TYPING_DELAY=0.15
MIN_ACTION_DELAY=1.0
MAX_ACTION_DELAY=3.0

# Anti-Detection Timing
MIN_SEARCH_INTERVAL=60.0
MAX_SEARCH_INTERVAL=120.0
MIN_SESSION_DELAY=300.0
MAX_SESSION_DELAY=900.0
BEHAVIOR_VARIATION_FACTOR=0.3

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=gsb_selenium
USE_MONGODB=true

# Browser Options
HEADLESS=false
WINDOW_WIDTH=1920
WINDOW_HEIGHT=1080

# Browser Fingerprint Alignment
PROXY_COUNTRY=US
USE_RESIDENTIAL_FINGERPRINTS=true
MATCH_LOCALE_TO_PROXY=true
ENABLE_WEBGL_SPOOFING=true

# Advanced Features
BLOCK_RESOURCES=false
TAKE_SCREENSHOTS=true
HUMAN_LIKE_BEHAVIOR=true
USE_UNDETECTED_CHROME=true
"""
        
        env_file.write_text(env_content)
        logger.info(f"Configuration file created: {env_file.absolute()}")
        logger.info("Please edit the .env file with your settings before running GSB-Selenium")
        
    except Exception as e:
        logger.error(f"Error creating configuration file: {e}")
        sys.exit(1)


@main.command()
def validate_config():
    """Validate configuration settings."""
    try:
        config = get_config()
        
        logger.info("Configuration validation:")
        logger.info(f"  Search term: '{config.search_term}'")
        logger.info(f"  Target website: '{config.target_website}'")
        logger.info(f"  Headless mode: {config.headless}")
        logger.info(f"  Proxy configured: {bool(config.proxy_string)}")
        logger.info(f"  CAPTCHA solver: {bool(config.captcha_api_key)}")
        logger.info(f"  MongoDB enabled: {config.use_mongodb}")
        logger.info(f"  Screenshots enabled: {config.take_screenshots}")
        logger.info(f"  Human-like behavior: {config.human_like_behavior}")
        
        if config.proxy_string:
            logger.info(f"  Proxy: {config.proxy_url}:{config.proxy_port}")
        
        logger.info("✅ Configuration is valid")
        
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        sys.exit(1)


@main.command()
@click.option("--test-type", "-t", 
              type=click.Choice(["proxy", "captcha", "search", "all"]), 
              default="all",
              help="Type of test to run")
def test(test_type: str):
    """Run component tests."""
    try:
        config = get_config()
        
        if test_type in ["proxy", "all"]:
            logger.info("Testing proxy configuration...")
            _test_proxy(config)
        
        if test_type in ["captcha", "all"]:
            logger.info("Testing CAPTCHA solver...")
            _test_captcha(config)
        
        if test_type in ["search", "all"]:
            logger.info("Testing basic search functionality...")
            _test_search(config)
        
        logger.info("✅ All tests completed")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        sys.exit(1)


def _test_proxy(config: GSBConfig):
    """Test hardcoded proxy configuration."""
    try:
        from .utils.stealth_driver import StealthDriver
        
        stealth_driver = StealthDriver(config, "proxy_test")
        with stealth_driver as driver:
            driver.driver.get("https://httpbin.org/ip")
            import time
            time.sleep(3)
            
            page_source = driver.driver.page_source
            if "origin" in page_source:
                logger.info("✅ Proxy test successful")
            else:
                logger.error("❌ Proxy test failed - no IP information found")
    
    except Exception as e:
        logger.error(f"❌ Proxy test failed: {e}")


def _test_captcha(config: GSBConfig):
    """Test CAPTCHA solver."""
    if not config.captcha_api_key:
        logger.warning("No CAPTCHA API key configured, skipping CAPTCHA test")
        return
    
    try:
        from .utils.captcha_solver import CaptchaSolver
        
        solver = CaptchaSolver(config.captcha_api_key)
        balance = solver.get_balance()
        
        if balance is not None:
            logger.info(f"✅ CAPTCHA solver test successful - Balance: ${balance}")
        else:
            logger.error("❌ CAPTCHA solver test failed")
    
    except Exception as e:
        logger.error(f"❌ CAPTCHA solver test failed: {e}")


def _test_search(config: GSBConfig):
    """Test basic search functionality."""
    try:
        # Create a test configuration with minimal settings
        test_config = GSBConfig(
            search_term="test search",
            headless=True,
            take_screenshots=False,
            human_like_behavior=False,
            search_range_min=1,
            search_range_max=1
        )
        
        bot = GoogleSearchBot(test_config, "search_test")
        bot.run_search_session(1)
        
        logger.info("✅ Basic search test successful")
        
    except Exception as e:
        logger.error(f"❌ Search test failed: {e}")


if __name__ == "__main__":
    main()