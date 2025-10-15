"""Verify GSB-Selenium installation and basic functionality."""

import sys
from pathlib import Path

def main():
    """Verify the GSB-Selenium installation."""
    print("🔍 GSB-Selenium Installation Verification")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check if we can import the modules
    try:
        from gsb_selenium.core.config import GSBConfig
        print("✅ Core config module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import core config: {e}")
        return False
    
    try:
        from gsb_selenium.utils.timing import TimingPattern, human_sleep
        print("✅ Timing utilities imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import timing utilities: {e}")
        return False
    
    try:
        from gsb_selenium.utils.webgl_spoofer import WebGLSpoofer
        print("✅ WebGL spoofer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WebGL spoofer: {e}")
        return False
    
    # Test basic configuration
    try:
        config = GSBConfig(
            search_term="test search",
            target_website="example.com",
            headless=True
        )
        print("✅ Configuration creation successful")
        print(f"   Search term: '{config.search_term}'")
        print(f"   Final search term: '{config.final_search_term}'")
        print(f"   Target website: '{config.target_website}'")
    except Exception as e:
        print(f"❌ Configuration creation failed: {e}")
        return False
    
    # Test timing functionality
    try:
        timing = TimingPattern()
        pattern = timing.get_pattern("search")
        print(f"✅ Timing pattern test successful: {pattern}")
    except Exception as e:
        print(f"❌ Timing pattern test failed: {e}")
        return False
    
    # Test WebGL spoofing
    try:
        spoofer = WebGLSpoofer()
        profile = spoofer.get_profile_info()
        print(f"✅ WebGL spoofing test successful")
        print(f"   Vendor: {profile['vendor']}")
        print(f"   Extensions: {profile['extensions_count']}")
    except Exception as e:
        print(f"❌ WebGL spoofing test failed: {e}")
        return False
    
    
    print("\n" + "=" * 50)
    print("🎉 All basic tests passed! GSB-Selenium is ready to use.")
    print("\nNext steps:")
    print("1. Update the .env file with your proxy credentials (if using)")
    print("2. Add your 2Captcha API key (if using)")
    print("3. Run: python3 examples/basic_usage.py")
    print("4. Or use the CLI: python3 -m gsb_selenium.cli run --help")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)