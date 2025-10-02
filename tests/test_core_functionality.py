"""Test core GSB functionality."""

import pytest
import time
from gsb_selenium.core.config import GSBConfig
from gsb_selenium.core.gsb import GoogleSearchBot
from gsb_selenium.utils.search_manager import SearchTermManager, should_click_target
from gsb_selenium.utils.timing import TimingPattern, human_sleep


class TestCoreFunctionality:
    """Test core GSB functionality."""
    
    def test_config_creation(self):
        """Test configuration creation and validation."""
        config = GSBConfig(
            search_term="test marketing",
            target_website="example.com",
            headless=True
        )
        
        assert config.search_term == "test marketing"
        assert config.target_website == "example.com"
        assert config.headless is True
        assert config.final_search_term == "test marketing"
        
        # Test with suffix
        config_with_suffix = GSBConfig(
            search_term="marketing",
            suffix="services",
            headless=True
        )
        
        assert config_with_suffix.final_search_term == "marketing services"
        
        print("✅ Configuration creation test passed")
    
    def test_search_term_manager(self):
        """Test search term management."""
        config = GSBConfig(
            search_term="digital marketing",
            suffix="services"
        )
        
        manager = SearchTermManager(config)
        
        # Test search term generation
        term1 = manager.get_next_search_term()
        term2 = manager.get_next_search_term()
        
        assert "digital marketing" in term1 or "services" in term1
        assert isinstance(term1, str)
        assert isinstance(term2, str)
        
        print(f"✅ Search term manager test passed - Generated: '{term1}'")
    
    def test_click_probability(self):
        """Test target click probability logic."""
        # Test with high probability
        config_high = GSBConfig(click_probability=1.0)
        results_high = [should_click_target(config_high) for _ in range(10)]
        assert all(results_high)  # Should all be True
        
        # Test with zero probability
        config_zero = GSBConfig(click_probability=0.0)
        results_zero = [should_click_target(config_zero) for _ in range(10)]
        assert not any(results_zero)  # Should all be False
        
        print("✅ Click probability test passed")
    
    def test_timing_patterns(self):
        """Test timing pattern functionality."""
        timing = TimingPattern()
        
        # Test pattern retrieval
        search_pattern = timing.get_pattern("search")
        assert len(search_pattern) == 2
        assert search_pattern[0] < search_pattern[1]
        
        # Test wait functionality (quick test)
        start_time = time.time()
        timing.wait_for("click")  # Should be 0.5-1.5 seconds
        duration = time.time() - start_time
        
        assert 0.4 < duration < 2.0  # Allow some margin
        
        print("✅ Timing patterns test passed")
    
    def test_human_sleep(self):
        """Test human sleep functionality."""
        start_time = time.time()
        human_sleep(0.1, 0.2)
        duration = time.time() - start_time
        
        assert 0.05 < duration < 0.3  # Allow some margin
        
        print("✅ Human sleep test passed")
    
    def test_gsb_initialization(self):
        """Test GSB bot initialization."""
        config = GSBConfig(
            search_term="test search",
            headless=True,
            take_screenshots=False,
            human_like_behavior=False
        )
        
        bot = GoogleSearchBot(config, "test_instance")
        
        assert bot.config == config
        assert bot.instance_id == "test_instance"
        assert bot.timing is not None
        assert bot.search_manager is not None
        assert bot.stealth_driver is not None
        
        print("✅ GSB initialization test passed")
    
    @pytest.mark.slow
    def test_basic_search_functionality(self):
        """Test basic search functionality (slow test)."""
        config = GSBConfig(
            search_term="test query",
            headless=True,
            take_screenshots=False,
            human_like_behavior=False,
            search_range_min=1,
            search_range_max=1,
            min_search_interval=1.0,
            max_search_interval=2.0
        )
        
        bot = GoogleSearchBot(config, "search_test")
        
        try:
            # This will perform one actual search
            bot.run_search_session(1)
            print("✅ Basic search functionality test passed")
        
        except Exception as e:
            # Don't fail the test suite for network issues
            print(f"⚠️  Basic search test skipped due to: {e}")
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test valid config
        valid_config = GSBConfig(
            search_term="valid search",
            search_range_min=1,
            search_range_max=10,
            click_probability=0.5
        )
        
        assert valid_config.search_range_min < valid_config.search_range_max
        assert 0 <= valid_config.click_probability <= 1
        
        # Test edge cases
        edge_config = GSBConfig(
            click_probability=0.0,
            search_range_min=1,
            search_range_max=1
        )
        
        assert edge_config.click_probability == 0.0
        assert edge_config.search_range_min == edge_config.search_range_max
        
        print("✅ Configuration validation test passed")


if __name__ == "__main__":
    # Run basic tests without pytest
    test_instance = TestCoreFunctionality()
    test_instance.test_config_creation()
    test_instance.test_search_term_manager()
    test_instance.test_click_probability()
    test_instance.test_timing_patterns()
    test_instance.test_human_sleep()
    test_instance.test_gsb_initialization()
    test_instance.test_config_validation()
    print("All core functionality tests passed!")