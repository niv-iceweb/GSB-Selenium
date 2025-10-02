"""Basic usage example for GSB-Selenium."""

import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gsb_selenium.core.config import GSBConfig
from gsb_selenium.core.gsb import GoogleSearchBot


def main():
    """Run a basic GSB-Selenium example."""
    print("🤖 GSB-Selenium Basic Usage Example")
    print("=" * 50)
    
    # Create configuration
    config = GSBConfig(
        search_term="digital marketing services",
        target_website="example.com",  # Replace with your target website
        headless=False,  # Set to True to run without visible browser
        search_range_min=2,
        search_range_max=3,
        click_probability=0.5,
        take_screenshots=True,
        human_like_behavior=True,
        enable_selenium_stealth=True
    )
    
    print(f"Search term: '{config.final_search_term}'")
    print(f"Target website: '{config.target_website}'")
    print(f"Headless mode: {config.headless}")
    print(f"Screenshots: {config.take_screenshots}")
    print()
    
    # Create and run bot
    try:
        bot = GoogleSearchBot(config, "basic_example")
        print("Starting search session...")
        bot.run_search_session()
        print("✅ Search session completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Search session interrupted by user")
    except Exception as e:
        print(f"❌ Error running search session: {e}")


if __name__ == "__main__":
    main()