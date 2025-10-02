"""Test stealth features and anti-detection capabilities."""

import pytest
import time
from gsb_selenium.core.config import GSBConfig
from gsb_selenium.utils.stealth_driver import StealthDriver
from gsb_selenium.utils.webgl_spoofer import WebGLSpoofer


class TestStealthFeatures:
    """Test stealth and anti-detection features."""
    
    def test_webgl_spoofing(self):
        """Test WebGL fingerprint spoofing."""
        spoofer = WebGLSpoofer()
        
        # Test profile selection
        profile_info = spoofer.get_profile_info()
        assert "vendor" in profile_info
        assert "renderer" in profile_info
        assert "extensions_count" in profile_info
        
        # Test script generation
        script = spoofer.get_webgl_script()
        assert "WebGLRenderingContext.prototype.getParameter" in script
        assert profile_info["vendor"] in script
        assert profile_info["renderer"] in script
        
        print(f"✅ WebGL spoofing test passed - Vendor: {profile_info['vendor']}")
    
    
    def test_stealth_driver_creation(self):
        """Test stealth driver creation and basic functionality."""
        config = GSBConfig(
            headless=True,
            enable_selenium_stealth=True,
            use_undetected_chrome=False,  # Use regular Selenium for testing
            take_screenshots=False,
            human_like_behavior=False
        )
        
        stealth_driver = StealthDriver(config, "stealth_test")
        
        try:
            with stealth_driver as driver:
                # Test basic navigation
                driver.driver.get("https://httpbin.org/user-agent")
                time.sleep(2)
                
                page_source = driver.driver.page_source
                assert "user-agent" in page_source.lower()
                
                # Test stealth features are applied
                webdriver_value = driver.driver.execute_script("return navigator.webdriver;")
                assert webdriver_value is False or webdriver_value is None
                
                print("✅ Stealth driver creation test passed")
        
        except Exception as e:
            pytest.fail(f"Stealth driver test failed: {e}")
    
    def test_human_like_interactions(self):
        """Test human-like interaction methods."""
        config = GSBConfig(
            headless=True,
            human_like_behavior=True,
            take_screenshots=False
        )
        
        stealth_driver = StealthDriver(config, "human_test")
        
        try:
            with stealth_driver as driver:
                driver.driver.get("https://www.google.com")
                time.sleep(2)
                
                # Test human-like scrolling
                stealth_driver.random_scroll("down", 200)
                time.sleep(1)
                
                stealth_driver.random_scroll("up", 100)
                time.sleep(1)
                
                print("✅ Human-like interactions test passed")
        
        except Exception as e:
            pytest.fail(f"Human-like interactions test failed: {e}")
    
    def test_user_agent_rotation(self):
        """Test user agent rotation functionality."""
        config = GSBConfig(
            use_residential_fingerprints=True,
            proxy_country="US"
        )
        
        # Test US user agents
        us_agents = config.get_user_agents("US")
        assert len(us_agents) > 0
        assert all("Mozilla" in ua for ua in us_agents)
        
        # Test GB user agents
        gb_agents = config.get_user_agents("GB")
        assert len(gb_agents) > 0
        
        # Test fallback
        basic_agents = config.get_user_agents("UNKNOWN")
        assert len(basic_agents) > 0
        
        print("✅ User agent rotation test passed")
    
    def test_webdriver_detection_evasion(self):
        """Test webdriver detection evasion techniques."""
        config = GSBConfig(
            headless=True,
            enable_selenium_stealth=True,
            take_screenshots=False
        )
        
        stealth_driver = StealthDriver(config, "evasion_test")
        
        try:
            with stealth_driver as driver:
                driver.driver.get("data:text/html,<html><body><script>document.body.innerHTML = navigator.webdriver;</script></body></html>")
                time.sleep(1)
                
                body_text = driver.driver.find_element("tag name", "body").text
                assert body_text in ["false", ""]  # Should be false or empty
                
                # Test other navigator properties
                plugins_length = driver.driver.execute_script("return navigator.plugins.length;")
                assert plugins_length > 0  # Should have fake plugins
                
                languages = driver.driver.execute_script("return navigator.languages;")
                assert len(languages) > 0
                
                print("✅ Webdriver detection evasion test passed")
        
        except Exception as e:
            pytest.fail(f"Webdriver detection evasion test failed: {e}")


if __name__ == "__main__":
    # Run basic tests without pytest
    test_instance = TestStealthFeatures()
    test_instance.test_webgl_spoofing()
    test_instance.test_chrome_profile_generation()
    test_instance.test_stealth_driver_creation()
    test_instance.test_human_like_interactions()
    test_instance.test_user_agent_rotation()
    test_instance.test_webdriver_detection_evasion()
    print("All stealth tests passed!")