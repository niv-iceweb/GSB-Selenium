# Oxylabs Proxy Integration for GSB-Selenium

This document describes the Oxylabs proxy integration implemented in GSB-Selenium, based on the official Oxylabs documentation.

## Overview

The integration provides seamless authentication with Oxylabs proxy services using `selenium-wire` for handling authenticated proxies. This enables the GSB-Selenium bot to operate through Oxylabs residential, datacenter, ISP, and mobile proxies.

## Features

- ✅ **Selenium-Wire Integration**: Uses `selenium-wire` for proxy authentication
- ✅ **Multiple Proxy Types**: Supports all Oxylabs proxy types
- ✅ **Proxy Testing**: Built-in proxy connectivity and functionality testing
- ✅ **CLI Commands**: Easy-to-use command-line tools for testing
- ✅ **Configuration Management**: Environment-based configuration
- ✅ **Example Scripts**: Complete examples for getting started

## Installation

The required dependencies are automatically included:

```bash
poetry install
```

Key dependencies added:
- `selenium-wire ^5.1.0` - For proxy authentication
- `webdriver-manager ^4.0.1` - Already included, used for driver management

### SSL Certificate Setup (Important!)

To avoid "Your connection to this site is not secure" warnings when using proxies, install the selenium-wire certificate:

```bash
# Automatic installation (recommended)
poetry run gsb install-certificate

# Or manual installation
poetry run python -m seleniumwire extractcert
# Then follow the prompts to install ca.crt in your system
```

This step is required only once per system and fixes SSL certificate warnings that appear when using selenium-wire with proxies.

## Configuration

### Environment Variables

Add these variables to your `.env` file:

```bash
# Oxylabs Proxy Configuration
USE_PROXY=true
PROXY_USERNAME=your_oxylabs_username
PROXY_PASSWORD=your_oxylabs_password
PROXY_ENDPOINT=pr.oxylabs.io:7777
PROXY_COUNTRY=US
```

### Supported Endpoints

Based on Oxylabs documentation:

| Proxy Type | Endpoint | Description |
|------------|----------|-------------|
| Residential and Mobile | `pr.oxylabs.io:7777` | Residential IPs |
| Datacenter | `dc.oxylabs.io:8001` | Datacenter IPs |
| ISP | `isp.oxylabs.io:8001` | ISP IPs |
| Self-Service Dedicated | `ddc.oxylabs.io:8001` | Dedicated datacenter |
| Enterprise Dedicated | `1.2.3.4:60000` | Specific IP address |

### Country-Specific Endpoints

For geo-targeted requests, use country-specific endpoints:

```bash
# US residential proxy
PROXY_ENDPOINT=us-pr.oxylabs.io:10000

# UK residential proxy  
PROXY_ENDPOINT=uk-pr.oxylabs.io:10000

# Canada residential proxy
PROXY_ENDPOINT=ca-pr.oxylabs.io:10000
```

## Usage

### 1. Test Proxy Connection

Test your proxy configuration before running searches:

```bash
# Test using credentials from .env file
poetry run gsb test-proxy

# Test with specific credentials
poetry run gsb test-proxy --username your_username --password your_password --endpoint pr.oxylabs.io:7777
```

The test performs:
- IP address verification via `ip.oxylabs.io`
- Google search functionality test
- Comprehensive connectivity check

### 2. Run Searches with Proxy

Once your proxy is configured and tested:

```bash
# Run with proxy enabled
poetry run gsb run
```

### 3. Programmatic Usage

```python
from gsb_selenium.core.config import GSBConfig
from gsb_selenium.core.gsb import GoogleSearchBot

# Configure with proxy
config = GSBConfig(
    use_proxy=True,
    proxy_username="your_username",
    proxy_password="your_password", 
    proxy_endpoint="pr.oxylabs.io:7777",
    proxy_country="US",
    search_term="your search term"
)

# Create and run bot
bot = GoogleSearchBot(config)
bot.run_search_session()
```

## Implementation Details

### Proxy Authentication Flow

1. **Configuration**: Proxy credentials loaded from environment or config
2. **Selenium-Wire Options**: Credentials formatted for `selenium-wire`
3. **Driver Creation**: Chrome driver created with proxy authentication
4. **Request Routing**: All traffic routed through authenticated proxy
5. **Stealth Integration**: Proxy combined with existing stealth features

### Code Architecture

```
gsb_selenium/
├── core/
│   ├── config.py              # Proxy configuration management
│   └── gsb.py                 # Main bot with proxy integration
├── utils/
│   ├── stealth.py            # Selenium-wire driver creation
│   └── proxy_tester.py       # Proxy testing utilities
├── cli.py                    # CLI commands including test-proxy
└── examples/
    └── oxylabs_proxy_example.py  # Complete usage examples
```

### Key Methods

- `GSBConfig.get_selenium_wire_proxy_options()` - Generate selenium-wire proxy config
- `StealthManager.setup_stealth_driver()` - Create authenticated proxy driver
- `OxylabsProxyTester.run_full_proxy_test()` - Comprehensive proxy testing
- `test_oxylabs_proxy_from_config()` - Test proxy from GSB config

## Testing

### Automated Tests

```bash
# Test proxy connectivity
poetry run gsb test-proxy

# Test browser functionality
poetry run gsb test-browser

# Run with verbose logging
poetry run gsb test-proxy --verbose
```

### Manual Verification

1. Check IP address: Navigate to `https://ip.oxylabs.io/`
2. Verify geolocation: Check if IP matches expected country
3. Test Google access: Ensure Google searches work properly
4. Monitor logs: Check for proxy-related errors

## Troubleshooting

### Common Issues

**Authentication Failed**
```
Error: Proxy test failed: 407 Proxy Authentication Required
```
- Verify username and password are correct
- Check if account has sufficient credits
- Ensure endpoint is correct for your subscription

**Connection Timeout**
```
Error: Proxy test failed: Connection timeout
```
- Check network connectivity
- Verify endpoint URL and port
- Try different proxy endpoint

**IP Not Changing**
```
Warning: IP address same as direct connection
```
- Verify `USE_PROXY=true` in configuration
- Check proxy credentials are loaded
- Ensure selenium-wire is installed

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger("seleniumwire").setLevel(logging.DEBUG)
```

## Example Output

Successful proxy test:
```
✅ Proxy Connection: Proxy connection successful. IP: 192.168.1.100
✅ Google Search: Google search successful. Found 10 results for 'test search'
🎉 All proxy tests passed! Your Oxylabs proxy is working correctly.
```

## Security Notes

- Store credentials in `.env` file, not in code
- Use environment variables in production
- Rotate credentials regularly
- Monitor proxy usage and costs
- Keep selenium-wire updated for security patches

## Support

For issues related to:
- **Oxylabs Proxy Service**: Contact Oxylabs support
- **GSB-Selenium Integration**: Check project documentation
- **Selenium-Wire**: Refer to selenium-wire documentation

## References

- [Oxylabs Python Integration Guide](https://developers.oxylabs.io/scraping-apis/web-scraping-api/python)
- [Selenium-Wire Documentation](https://github.com/wkeeling/selenium-wire)
- [GSB-Selenium Documentation](./README.md)