# GSB-Selenium: Advanced Google Search Bot

🤖 **Intelligent Google Search Automation** powered by Selenium with advanced stealth features

GSB-Selenium is a sophisticated Google Search Bot that replicates human browsing behavior for search marketing and website promotion. Built from the ground up with Selenium and selenium-wire, it features advanced anti-detection capabilities, built-in CAPTCHA bypass, proxy support, and human-like interactions migrated from the original Pydoll implementation.

## 🌟 Key Features

- **🛡️ Advanced Anti-Detection**: Uses human-like interaction engine with stealth features
- **🔓 Built-in CAPTCHA Bypass**: Handles reCAPTCHA v2/v3, Turnstile, and other CAPTCHAs automatically
- **🎯 2Captcha Integration**: Automatic reCAPTCHA v2 solving using 2captcha service
- **🌐 Proxy Support**: Full support for Oxylabs and other proxy providers via selenium-wire
- **⚡ Async Performance**: High-performance concurrent execution
- **📊 Smart Timing**: Time-based search frequency with realistic patterns
- **🎯 Target Website Detection**: Automatically finds and clicks on specified websites
- **📸 Screenshot Capture**: Visual verification and debugging
- **📈 Comprehensive Logging**: Structured logging with performance metrics
- **🔧 Flexible Configuration**: Environment-based configuration with CLI overrides
- **☁️ AWS Integration**: AWS Parameter Store configuration support

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd GSB-Selenium
```

2. **Install dependencies using Poetry:**
```bash
pip install poetry
poetry install
```

3. **Create configuration file:**
```bash
poetry run gsb init-config
```

4. **Edit the `.env` file with your settings:**
```bash
# Search Configuration
SEARCH_TERMS=marketing services
SUFFIX=guru.com
TARGET_WEBSITE=www.guru.com

# Proxy Configuration (Optional)
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
PROXY_ENDPOINT=us-pr.oxylabs.io

# 2Captcha Configuration (Optional - for reCAPTCHA v2 solving)
CAPTCHA_API_KEY=your_2captcha_api_key

# Advanced Settings
HEADLESS=false
TAKE_SCREENSHOTS=true
```

### Basic Usage

**Run a single bot instance:**
```bash
poetry run gsb run
```

**Run with custom parameters:**
```bash
poetry run gsb run --searches 10 --headless --target-website "example.com"
```

**Run multiple instances in parallel:**
```bash
poetry run gsb run-parallel --instances 3 --searches-per-instance 5
```

## 📋 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SEARCH_TERMS` | Base search terms | `marketing services` |
| `SUFFIX` | Domain suffix to append | `` |
| `TARGET_WEBSITE` | Website to find and click | `` |
| `PROXY_USERNAME` | Proxy username | `` |
| `PROXY_PASSWORD` | Proxy password | `` |
| `PROXY_ENDPOINT` | Proxy server endpoint | `us-pr.oxylabs.io` |
| `SEARCH_RANGE_MIN` | Minimum searches per session | `5` |
| `SEARCH_RANGE_MAX` | Maximum searches per session | `20` |
| `CLICK_PROBABILITY` | Chance of clicking target (0-1) | `0.3` |
| `HEADLESS` | Run without visible browser | `false` |
| `TAKE_SCREENSHOTS` | Capture screenshots | `true` |

## 🏗️ Architecture

### Core Components

- **`GoogleSearchBot`**: Main bot orchestrator using Selenium
- **`GSBConfig`**: Configuration management with Pydantic
- **`SearchTermManager`**: Intelligent search term rotation
- **`TimingPattern`**: Human-like timing and delays
- **`StealthDriver`**: Enhanced Selenium WebDriver with anti-detection
- **Comprehensive Logging**: Structured logging with multiple outputs

### Key Differences from Pydoll Version

| Feature | Pydoll Version | Selenium Version |
|---------|----------------|------------------|
| **Browser Engine** | Chrome DevTools Protocol | Selenium WebDriver |
| **Proxy Support** | Native CDP | selenium-wire |
| **Stealth Features** | Built-in | Custom implementation |
| **Driver Management** | No external drivers | WebDriver Manager |
| **Anti-Detection** | Native | undetected-chromedriver + custom |
| **Performance** | Faster CDP | More stable WebDriver |

## 🛡️ Anti-Detection Features

### Human-Like Behavior

- **Realistic Typing**: Character-by-character input with random delays
- **Natural Mouse Movement**: Hover actions before clicks with PyAutoGUI
- **Scroll Patterns**: Random scrolling behavior
- **Timing Variance**: Randomized delays between actions

### Advanced Evasion

- **User Agent Rotation**: Multiple realistic browser signatures
- **Viewport Randomization**: Varied window sizes
- **WebGL Spoofing**: Fingerprint randomization
- **Request Interception**: Controlled network behavior via selenium-wire
- **Chrome Profile Management**: Random profile generation

### CAPTCHA Handling

Built-in CAPTCHA bypass supports:
- reCAPTCHA v2 (via 2captcha integration)
- reCAPTCHA v3
- Cloudflare Turnstile
- hCaptcha
- Custom CAPTCHA implementations

## 🔍 Proxy Integration

### Oxylabs Integration with selenium-wire

```python
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

USERNAME = "your_username"
PASSWORD = "your_password"
ENDPOINT = "pr.oxylabs.io:7777"

def chrome_proxy(user: str, password: str, endpoint: str) -> dict:
    wire_options = {
        "proxy": {
            "http": f"http://{user}:{password}@{endpoint}",
            "https": f"https://{user}:{password}@{endpoint}",
        }
    }
    return wire_options

# Create driver with proxy
manage_driver = Service(executable_path=ChromeDriverManager().install())
options = webdriver.ChromeOptions()
proxies = chrome_proxy(USERNAME, PASSWORD, ENDPOINT)
driver = webdriver.Chrome(
    service=manage_driver, 
    options=options, 
    seleniumwire_options=proxies
)
```

## 🔧 Advanced Usage

### Custom Search Patterns

```python
from gsb_selenium import GoogleSearchBot, GSBConfig

# Create custom configuration
config = GSBConfig(
    search_terms="custom marketing",
    target_website="example.com",
    headless=True,
    search_range_min=3,
    search_range_max=8
)

# Run bot with custom config
bot = GoogleSearchBot(config, "custom_instance")
await bot.run_search_session()
```

## 📊 Monitoring and Logging

### Log Files

- **`logs/gsb_main.log`**: General application logs
- **`logs/gsb_errors_main.log`**: Error-specific logs
- **`logs/gsb_success_main.log`**: Successful search completions

### Screenshot Capture

Screenshots are automatically saved to `data/screenshots/` with timestamps for:
- Search results pages
- Target website visits
- CAPTCHA detection events
- Verification page visits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
poetry install --with dev

# Run type checking
poetry run mypy gsb_selenium/

# Format code
poetry run black gsb_selenium/
poetry run isort gsb_selenium/

# Run tests
poetry run pytest
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Selenium](https://selenium-python.readthedocs.io/) for the excellent browser automation framework
- [selenium-wire](https://github.com/wkeeling/selenium-wire) for proxy integration
- Original GSB-Pydoll implementation for the core logic and inspiration
- The Python community for the amazing async ecosystem

---

**⚠️ Disclaimer**: This tool is for educational and legitimate business purposes only. Users are responsible for complying with website terms of service and applicable laws. Use responsibly and ethically.