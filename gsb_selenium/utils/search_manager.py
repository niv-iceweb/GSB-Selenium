"""Search term management for GSB-Selenium."""

import random
from typing import List, Optional
from pathlib import Path
from loguru import logger


class SearchTermManager:
    """Manages search term rotation and selection."""
    
    def __init__(self, config):
        """Initialize the search term manager."""
        self.config = config
        self.search_terms: List[str] = []
        self.current_index = 0
        self._load_search_terms()
    
    def _load_search_terms(self):
        """Load search terms from various sources."""
        # Start with base search term from config
        base_terms = [self.config.search_term]
        
        # Try to load from file if it exists
        if self.config.search_list_path.exists():
            try:
                with open(self.config.search_list_path, 'r', encoding='utf-8') as f:
                    file_terms = [line.strip() for line in f if line.strip()]
                    base_terms.extend(file_terms)
                logger.info(f"Loaded {len(file_terms)} search terms from file")
            except Exception as e:
                logger.warning(f"Could not load search terms from file: {e}")
        
        # Create variations of base terms
        self.search_terms = self._create_variations(base_terms)
        logger.info(f"Total search terms available: {len(self.search_terms)}")
    
    def _create_variations(self, base_terms: List[str]) -> List[str]:
        """Create variations of base search terms."""
        variations = []
        
        # Common search modifiers
        modifiers = [
            "", "best", "top", "professional", "local", "affordable", 
            "expert", "quality", "reliable", "trusted", "experienced"
        ]
        
        # Common search suffixes
        suffixes = [
            "", "services", "company", "business", "solutions", 
            "providers", "experts", "professionals", "near me"
        ]
        
        for term in base_terms:
            # Add original term
            variations.append(term)
            
            # Add variations with modifiers and suffixes
            for modifier in modifiers[:3]:  # Limit to avoid too many variations
                for suffix in suffixes[:3]:
                    if modifier and suffix:
                        variation = f"{modifier} {term} {suffix}".strip()
                    elif modifier:
                        variation = f"{modifier} {term}".strip()
                    elif suffix:
                        variation = f"{term} {suffix}".strip()
                    else:
                        continue
                    
                    if variation not in variations:
                        variations.append(variation)
        
        return variations
    
    def get_next_search_term(self) -> str:
        """Get the next search term in rotation."""
        if not self.search_terms:
            return self.config.search_term
        
        # Use random selection for more natural behavior
        term = random.choice(self.search_terms)
        
        # Add suffix if configured
        if self.config.suffix:
            term = f"{term} {self.config.suffix}"
        
        logger.debug(f"Selected search term: '{term}'")
        return term
    
    def get_random_search_term(self) -> str:
        """Get a random search term."""
        return self.get_next_search_term()


def create_search_manager(config) -> SearchTermManager:
    """Factory function to create search manager."""
    return SearchTermManager(config)


def should_click_target(config) -> bool:
    """Determine if target website should be clicked based on probability."""
    return random.random() < config.click_probability