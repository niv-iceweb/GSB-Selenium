"""AWS Parameter Store configuration management for GSB-Selenium."""

import os
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pathlib import Path

from .config import GSBConfig


class ParameterStoreClient:
    """AWS Parameter Store client with error handling and caching."""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self._client = None
        self._cache: Dict[str, str] = {}
    
    @property
    def client(self):
        """Lazy initialization of SSM client."""
        if self._client is None:
            try:
                self._client = boto3.client('ssm', region_name=self.region)
                # Test connection
                self._client.describe_parameters(MaxResults=1)
            except (NoCredentialsError, ClientError) as e:
                print(f"Warning: AWS credentials not available or invalid: {e}")
                self._client = None
        return self._client
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get parameter from Parameter Store with caching."""
        if name in self._cache:
            return self._cache[name]
        
        if not self.client:
            return default
        
        try:
            response = self.client.get_parameter(Name=name)
            value = response['Parameter']['Value']
            self._cache[name] = value
            return value
        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                print(f"Parameter {name} not found in Parameter Store, using default: {default}")
            else:
                print(f"Error getting parameter {name}: {e}")
            return default
    
    def get_parameters_by_path(self, path: str) -> Dict[str, str]:
        """Get all parameters under a given path."""
        if not self.client:
            return {}
        
        try:
            parameters = {}
            paginator = self.client.get_paginator('get_parameters_by_path')
            
            for page in paginator.paginate(Path=path, Recursive=True):
                for param in page['Parameters']:
                    # Remove the path prefix and convert to snake_case-like format
                    key = param['Name'].replace(path, '').lstrip('/')
                    key = key.replace('-', '_').lower()
                    parameters[key] = param['Value']
                    self._cache[param['Name']] = param['Value']
            
            return parameters
        except ClientError as e:
            print(f"Error getting parameters by path {path}: {e}")
            return {}


class AWSGSBConfig(GSBConfig):
    """GSB Configuration with AWS Parameter Store integration."""
    
    def __init__(self, **kwargs):
        # Detect environment
        environment = os.getenv('ENVIRONMENT', 'local')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Try to load from AWS Parameter Store first, fall back to .env
        aws_config = self._load_from_aws(environment, aws_region)
        
        if aws_config:
            # Successfully loaded from AWS Parameter Store
            print(f"✅ Using AWS Parameter Store configuration for {environment}")
            # Merge AWS config with any provided kwargs (kwargs take precedence)
            merged_config = {**aws_config, **kwargs}
            super().__init__(**merged_config)
        else:
            # Fall back to .env file logic
            print(f"⚠️  AWS Parameter Store not available, using .env file for {environment}")
            super().__init__(**kwargs)
    
    def _load_from_aws(self, environment: str, aws_region: str) -> Dict[str, Any]:
        """Load configuration from AWS Parameter Store."""
        client = ParameterStoreClient(aws_region)
        
        # Parameter Store path structure (using gsb-selenium instead of gsb-pydoll)
        base_path = f"/gsb-pydoll/{environment}"
        
        print(f"Loading configuration from AWS Parameter Store: {base_path}")
        
        # Get all parameters under the base path
        aws_params = client.get_parameters_by_path(base_path)
        
        if not aws_params:
            # No parameters found - could be empty path or access issues
            return {}
        
        # Map Parameter Store keys to config field names
        config_mapping = {
            # Search Configuration
            'search_term': aws_params.get('search_term'),
            'suffix': aws_params.get('suffix'),
            'target_website': aws_params.get('target_website'),
            
            # Proxy Configuration (removed - now hardcoded)
            
            # 2Captcha Configuration
            'captcha_api_key': aws_params.get('captcha_api_key'),
            
            # Search Control
            'search_range_min': self._safe_int(aws_params.get('search_range_min')),
            'search_range_max': self._safe_int(aws_params.get('search_range_max')),
            'click_probability': self._safe_float(aws_params.get('click_probability')),
            
            # Timing Configuration
            'min_typing_delay': self._safe_float(aws_params.get('min_typing_delay')),
            'max_typing_delay': self._safe_float(aws_params.get('max_typing_delay')),
            'min_action_delay': self._safe_float(aws_params.get('min_action_delay')),
            'max_action_delay': self._safe_float(aws_params.get('max_action_delay')),
            
            # Anti-Detection Timing
            'min_search_interval': self._safe_float(aws_params.get('min_search_interval')),
            'max_search_interval': self._safe_float(aws_params.get('max_search_interval')),
            'min_session_delay': self._safe_float(aws_params.get('min_session_delay')),
            'max_session_delay': self._safe_float(aws_params.get('max_session_delay')),
            'behavior_variation_factor': self._safe_float(aws_params.get('behavior_variation_factor')),
            
            # MongoDB Configuration (production-specific)
            'mongo_uri': aws_params.get('mongo_uri'),
            'mongo_database': aws_params.get('mongo_database'),
            'use_mongodb': self._safe_bool(aws_params.get('use_mongodb')),
            
            # Browser Options
            'window_width': self._safe_int(aws_params.get('window_width')),
            'window_height': self._safe_int(aws_params.get('window_height')),
            
            # Browser Fingerprint Alignment
            'proxy_country': aws_params.get('proxy_country'),
            'use_residential_fingerprints': self._safe_bool(aws_params.get('use_residential_fingerprints')),
            'match_locale_to_proxy': self._safe_bool(aws_params.get('match_locale_to_proxy')),
            'enable_selenium_stealth': self._safe_bool(aws_params.get('enable_selenium_stealth')),
            'enable_webgl_spoofing': self._safe_bool(aws_params.get('enable_webgl_spoofing')),
            
            # Advanced Features
            'block_resources': self._safe_bool(aws_params.get('block_resources')),
            'take_screenshots': self._safe_bool(aws_params.get('take_screenshots')),
            'human_like_behavior': self._safe_bool(aws_params.get('human_like_behavior')),
            'use_undetected_chrome': self._safe_bool(aws_params.get('use_undetected_chrome')),
        }
        
        # Filter out None values
        return {k: v for k, v in config_mapping.items() if v is not None}
    
    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        """Safely convert string to int."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value: Optional[str]) -> Optional[float]:
        """Safely convert string to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_bool(self, value: Optional[str]) -> Optional[bool]:
        """Safely convert string to bool."""
        if value is None:
            return None
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)


def get_config(**kwargs) -> GSBConfig:
    """Factory function to get appropriate config with AWS Parameter Store integration."""
    # Always try AWS integration first, will fall back to .env if AWS is not available
    return AWSGSBConfig(**kwargs)