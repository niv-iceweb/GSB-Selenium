"""MongoDB-based search term management for GSB-Selenium."""

import random
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from loguru import logger

from .search_manager import SearchTermManager


class MongoSearchManager(SearchTermManager):
    """MongoDB-based search term manager."""
    
    def __init__(self, config):
        """Initialize the MongoDB search term manager."""
        self.config = config
        self.client = None
        self.db = None
        self.collection = None
        self.search_terms: List[str] = []
        self.current_index = 0
        
        if config.use_mongodb:
            self._connect_to_mongodb()
        
        self._load_search_terms()
    
    def _connect_to_mongodb(self):
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.config.mongo_uri)
            self.db = self.client[self.config.mongo_database]
            self.collection = self.db.search_terms
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.config.mongo_database}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
    
    def _load_search_terms(self):
        """Load search terms from MongoDB or fallback to parent method."""
        if self.client is None:
            # Fallback to file-based loading
            super()._load_search_terms()
            return
        
        try:
            # Load search terms from MongoDB
            documents = list(self.collection.find({"active": True}))
            
            if documents:
                mongo_terms = [doc["term"] for doc in documents if "term" in doc]
                self.search_terms = self._create_variations(mongo_terms)
                logger.info(f"Loaded {len(mongo_terms)} search terms from MongoDB")
            else:
                # No terms in MongoDB, use default
                logger.info("No search terms found in MongoDB, using default")
                super()._load_search_terms()
                # Store default terms in MongoDB for future use
                self._store_default_terms()
                
        except Exception as e:
            logger.error(f"Error loading search terms from MongoDB: {e}")
            # Fallback to file-based loading
            super()._load_search_terms()
    
    def _store_default_terms(self):
        """Store default search terms in MongoDB."""
        if self.client is None:
            return
        
        try:
            default_terms = [self.config.search_term]
            
            # Add some common variations
            variations = [
                f"{self.config.search_term} services",
                f"best {self.config.search_term}",
                f"professional {self.config.search_term}",
                f"{self.config.search_term} company"
            ]
            
            default_terms.extend(variations)
            
            # Insert terms if they don't exist
            for term in default_terms:
                existing = self.collection.find_one({"term": term})
                if not existing:
                    self.collection.insert_one({
                        "term": term,
                        "active": True,
                        "category": "default",
                        "created_at": logger.bind().opt(record=True).info("")
                    })
            
            logger.info(f"Stored {len(default_terms)} default terms in MongoDB")
            
        except Exception as e:
            logger.error(f"Error storing default terms in MongoDB: {e}")
    
    def add_search_term(self, term: str, category: str = "custom") -> bool:
        """Add a new search term to MongoDB."""
        if self.client is None:
            return False
        
        try:
            # Check if term already exists
            existing = self.collection.find_one({"term": term})
            if existing:
                logger.info(f"Search term already exists: {term}")
                return True
            
            # Insert new term
            self.collection.insert_one({
                "term": term,
                "active": True,
                "category": category,
                "usage_count": 0,
                "created_at": logger.bind().opt(record=True).info("")
            })
            
            # Reload search terms
            self._load_search_terms()
            logger.info(f"Added new search term: {term}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding search term: {e}")
            return False
    
    def update_term_usage(self, term: str):
        """Update usage count for a search term."""
        if self.client is None:
            return
        
        try:
            self.collection.update_one(
                {"term": term},
                {"$inc": {"usage_count": 1}}
            )
        except Exception as e:
            logger.error(f"Error updating term usage: {e}")
    
    def get_next_search_term(self) -> str:
        """Get the next search term and update usage."""
        term = super().get_next_search_term()
        
        # Update usage count in MongoDB
        base_term = term.replace(f" {self.config.suffix}", "").strip()
        self.update_term_usage(base_term)
        
        return term
    
    def get_term_statistics(self) -> Dict[str, Any]:
        """Get statistics about search terms."""
        if self.client is None:
            return {}
        
        try:
            total_terms = self.collection.count_documents({"active": True})
            most_used = list(self.collection.find({"active": True})
                           .sort("usage_count", -1).limit(5))
            
            return {
                "total_active_terms": total_terms,
                "most_used_terms": [
                    {"term": doc["term"], "usage_count": doc.get("usage_count", 0)}
                    for doc in most_used
                ],
                "total_loaded_variations": len(self.search_terms)
            }
        except Exception as e:
            logger.error(f"Error getting term statistics: {e}")
            return {}
    
    def close_connection(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


def create_search_manager(config):
    """Factory function to create appropriate search manager."""
    if config.use_mongodb:
        return MongoSearchManager(config)
    else:
        return SearchTermManager(config)