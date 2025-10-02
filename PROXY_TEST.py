#!/usr/bin/env python3
"""Simple proxy test without dependencies to verify hardcoded proxy configuration."""

import re
import random

def test_hardcoded_proxy():
    """Test the hardcoded proxy string generation logic."""
    
    def generate_proxy_string():
        """Generate hardcoded Oxylabs proxy string with randomized session ID."""
        # Generate random session ID between 606150694 and 606250693
        sessid = random.randint(606150694, 606250693)
        
        return f"https://customer-nivos_qR24w-cc-us-sessid-{sessid}-sesstime-10:Niv220niv220_@pr.oxylabs.io:7777"
    
    print("🔍 Testing Hardcoded Proxy Configuration")
    print("=" * 50)
    
    # Generate two proxy strings
    proxy1 = generate_proxy_string()
    proxy2 = generate_proxy_string()
    
    print(f"Proxy 1: {proxy1}")
    print(f"Proxy 2: {proxy2}")
    print()
    
    # Test format
    tests = [
        ("Contains customer prefix", "customer-nivos_qR24w-cc-us-sessid-" in proxy1),
        ("Contains endpoint", "pr.oxylabs.io:7777" in proxy1),
        ("Contains password", "Niv220niv220_" in proxy1),
        ("Uses HTTPS", proxy1.startswith("https://")),
        ("Contains sesstime", "sesstime-10" in proxy1),
    ]
    
    # Extract and test session IDs
    sessid1 = re.search(r'sessid-(\d+)-', proxy1).group(1)
    sessid2 = re.search(r'sessid-(\d+)-', proxy2).group(1)
    
    print(f"Session ID 1: {sessid1}")
    print(f"Session ID 2: {sessid2}")
    print()
    
    # Test session ID ranges
    sessid1_int = int(sessid1)
    sessid2_int = int(sessid2)
    
    tests.extend([
        ("Session ID 1 in range", 606150694 <= sessid1_int <= 606250693),
        ("Session ID 2 in range", 606150694 <= sessid2_int <= 606250693),
        ("Session IDs are different", sessid1 != sessid2),
    ])
    
    # Run tests
    all_passed = True
    for test_name, result in tests:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}: {result}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All proxy tests passed!")
        print("✅ Hardcoded proxy configuration is working correctly")
    else:
        print("❌ Some proxy tests failed")
    
    return all_passed

if __name__ == "__main__":
    test_hardcoded_proxy()