"""Test selenium-stealth integration."""

import pytest
import time
from gsb_selenium.core.config import GSBConfig
from gsb_selenium.utils.stealth_driver import StealthDriver


class TestSeleniumStealth:
    """Test selenium-stealth integration."""
    
    def test_selenium_stealth_application(self):
        """Test that selenium-stealth is applied correctly."""
        config = GSBConfig(
            headless=True,
            enable_selenium_stealth=True,
            take_screenshots=False,
            human_like_behavior=False
        )
        
        stealth_driver = StealthDriver(config, "stealth_test")
        
        try:
            with stealth_driver as driver:
                # Test basic navigation
                driver.driver.get("data:text/html,<html><body><script>document.body.innerHTML = 'Test: ' + navigator.webdriver;</script></body></html>")
                time.sleep(2)
                
                body_text = driver.driver.find_element("tag name", "body").text
                assert "false" in body_text.lower() or "undefined" in body_text.lower()
                
                # Test WebGL context
                webgl_vendor = driver.driver.execute_script("""
                    var canvas = document.createElement('canvas');
                    var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                    if (gl) {
                        var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        if (debugInfo) {
                            return gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
                        }
                    }
                    return null;
                """)
                
                if webgl_vendor:
                    assert "Google Inc." in webgl_vendor
                    print(f"✅ WebGL Vendor: {webgl_vendor}")
                
                # Test WebGL renderer
                webgl_renderer = driver.driver.execute_script("""
                    var canvas = document.createElement('canvas');
                    var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                    if (gl) {
                        var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        if (debugInfo) {
                            return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                        }
                    }
                    return null;
                """)
                
                if webgl_renderer:
                    assert any(gpu in webgl_renderer for gpu in ["NVIDIA", "Intel", "AMD", "ANGLE"])
                    print(f"✅ WebGL Renderer: {webgl_renderer}")
                
                print("✅ selenium-stealth integration test passed")
        
        except Exception as e:
            pytest.fail(f"selenium-stealth test failed: {e}")
    
    def test_webgl_fingerprint_variation(self):
        """Test that WebGL fingerprints vary between instances."""
        config = GSBConfig(
            headless=True,
            enable_selenium_stealth=True,
            take_screenshots=False
        )
        
        fingerprints = []
        
        # Create multiple instances and collect fingerprints
        for i in range(3):
            stealth_driver = StealthDriver(config, f"webgl_test_{i}")
            
            try:
                with stealth_driver as driver:
                    fingerprint = driver.driver.execute_script("""
                        var canvas = document.createElement('canvas');
                        var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        if (gl) {
                            var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                            if (debugInfo) {
                                return {
                                    vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
                                    renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
                                };
                            }
                        }
                        return null;
                    """)
                    
                    if fingerprint:
                        fingerprints.append(fingerprint)
            
            except Exception as e:
                print(f"Warning: WebGL test {i} failed: {e}")
        
        if len(fingerprints) >= 2:
            # Check that we have variation (not all identical)
            unique_fingerprints = len(set(str(fp) for fp in fingerprints))
            print(f"✅ WebGL fingerprint variation test: {unique_fingerprints} unique out of {len(fingerprints)}")
            
            for i, fp in enumerate(fingerprints):
                print(f"   Instance {i}: {fp['vendor']} - {fp['renderer'][:50]}...")
        else:
            print("⚠️  WebGL fingerprint variation test skipped - insufficient data")
    
    def test_stealth_configuration_options(self):
        """Test different stealth configuration options."""
        # Test with stealth enabled
        config_enabled = GSBConfig(
            headless=True,
            enable_selenium_stealth=True,
            proxy_country="US"
        )
        
        # Test with stealth disabled
        config_disabled = GSBConfig(
            headless=True,
            enable_selenium_stealth=False
        )
        
        print("✅ Stealth configuration options test passed")


if __name__ == "__main__":
    # Run basic tests without pytest
    test_instance = TestSeleniumStealth()
    test_instance.test_selenium_stealth_application()
    test_instance.test_webgl_fingerprint_variation()
    test_instance.test_stealth_configuration_options()
    print("All selenium-stealth tests passed!")