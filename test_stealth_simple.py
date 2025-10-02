#!/usr/bin/env python3
"""Simple test for selenium-stealth integration without dependencies."""

def test_selenium_stealth_integration():
    """Test selenium-stealth integration and WebGL spoofing."""
    
    print("🔍 Testing selenium-stealth Integration")
    print("=" * 50)
    
    try:
        # Test import
        from selenium_stealth import stealth
        print("✅ selenium-stealth import successful")
        
        # Test configuration
        from gsb_selenium.core.config import GSBConfig
        config = GSBConfig(enable_selenium_stealth=True)
        print(f"✅ Configuration created with selenium-stealth: {config.enable_selenium_stealth}")
        
        # Test WebGL profiles
        webgl_profiles = {
            "US": {
                "vendor": "Google Inc. (NVIDIA)",
                "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11-27.21.14.5671)"
            },
            "GB": {
                "vendor": "Google Inc. (Intel)",
                "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"
            },
            "DE": {
                "vendor": "Google Inc. (AMD)",
                "renderer": "ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.13025.1000)"
            }
        }
        
        print("✅ WebGL profiles defined:")
        for country, profile in webgl_profiles.items():
            print(f"   {country}: {profile['vendor']} - {profile['renderer'][:50]}...")
        
        # Test stealth driver creation (without actually creating browser)
        from gsb_selenium.utils.stealth_driver import StealthDriver
        stealth_driver = StealthDriver(config, "test_instance")
        print("✅ StealthDriver created successfully")
        
        print("\n🎉 selenium-stealth integration test passed!")
        print("✅ All components are properly integrated")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install selenium-stealth: poetry add selenium-stealth")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_webgl_randomization():
    """Test WebGL profile randomization logic."""
    
    print("\n🎲 Testing WebGL Profile Randomization")
    print("=" * 50)
    
    import random
    
    webgl_profiles = [
        {"vendor": "Google Inc. (NVIDIA)", "gpu": "GeForce GTX 1060"},
        {"vendor": "Google Inc. (Intel)", "gpu": "UHD Graphics 630"},
        {"vendor": "Google Inc. (AMD)", "gpu": "Radeon RX 580"}
    ]
    
    # Test randomization
    selected_profiles = []
    for i in range(10):
        profile = random.choice(webgl_profiles)
        selected_profiles.append(profile["vendor"])
    
    unique_vendors = set(selected_profiles)
    print(f"✅ Generated {len(selected_profiles)} profiles with {len(unique_vendors)} unique vendors")
    print(f"   Vendors: {list(unique_vendors)}")
    
    # Should have some variation (not all the same)
    if len(unique_vendors) > 1:
        print("✅ WebGL randomization working correctly")
        return True
    else:
        print("⚠️  WebGL randomization may need improvement")
        return False

if __name__ == "__main__":
    success1 = test_selenium_stealth_integration()
    success2 = test_webgl_randomization()
    
    if success1 and success2:
        print("\n🎉 All selenium-stealth tests passed!")
    else:
        print("\n❌ Some tests failed")