"""Proxy usage example for GSB-Selenium with Oxylabs."""

import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gsb_selenium.core.config import GSBConfig
from gsb_selenium.core.gsb import GoogleSearchBot


def main():
    """Run GSB-Selenium with Oxylabs proxy example."""
    print("🌐 GSB-Selenium Proxy Usage Example (Oxylabs)")
    print("=" * 50)
    
    # Proxy is now hardcoded with randomized session ID
    print("ℹ️  Using hardcoded Oxylabs proxy with randomized session ID")
    
    # Create configuration (proxy is automatically configured)
    config = GSBConfig(
        search_term="marketing automation tools",
        target_website="example.com",  # Replace with your target website
        headless=True,  # Use headless mode for proxy testing
        
        # Search settings
        search_range_min=1,
        search_range_max=2,
        click_probability=0.3,
        
        # Stealth settings optimized for proxy use
        use_residential_fingerprints=True,
        match_locale_to_proxy=True,
        enable_selenium_stealth=True,
        human_like_behavior=True,
        take_screenshots=True
    )
    
    print(f"Search term: '{config.final_search_term}'")
    print(f"Target website: '{config.target_website}'")
    print(f"Proxy: {config.proxy_string[:50]}...") # Show first 50 chars of proxy string
    print()
    
    # Create and run bot with proxy
    try:
        bot = GoogleSearchBot(config, "proxy_example")
        print("Starting search session with proxy...")
        bot.run_search_session()
        print("✅ Proxy search session completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Search session interrupted by user")
    except Exception as e:
        print(f"❌ Error running proxy search session: {e}")
        print("   Check your proxy credentials and network connection")


def test_proxy_connection():
    """Test hardcoded proxy connection without running full search."""
    print("\n🔍 Testing hardcoded proxy connection...")
    
    from gsb_selenium.utils.stealth_driver import StealthDriver
    
    config = GSBConfig(
        headless=True,
        take_screenshots=False
    )
    
    stealth_driver = StealthDriver(config, "proxy_test")
    
    try:
        with stealth_driver as driver:
            # Test connection to IP check service
            print("Connecting to IP check service...")
            driver.driver.get("https://ip.oxylabs.io/location")
            
            import time
            time.sleep(3)
            
            page_source = driver.driver.page_source
            if "country" in page_source.lower():
                print("✅ Proxy connection test successful!")
                print("   Your requests are going through the proxy")
            else:
                print("⚠️  Proxy connection test inconclusive")
                
    except Exception as e:
        print(f"❌ Proxy connection test failed: {e}")


if __name__ == "__main__":
    main()
    test_proxy_connection()