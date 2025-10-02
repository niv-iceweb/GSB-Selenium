"""Chrome Profile Manager for GSB-Selenium."""

import json
import os
import platform
import random
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict

from loguru import logger


class ChromeProfileManager:
    """Manages Chrome profiles for GSB-Selenium with cross-platform support."""
    
    def __init__(self, config, instance_id: str = "main"):
        """Initialize the Chrome profile manager.
        
        Args:
            config: GSB configuration object
            instance_id: Unique identifier for this instance
        """
        self.config = config
        self.instance_id = instance_id
        self.user_data_dir = self._get_chrome_user_data_dir()
        self.template_dir = self._get_template_dir()
        self.current_profile = None
        
        logger.info(f"ChromeProfileManager initialized for instance {instance_id}")
        logger.info(f"Chrome user data directory: {self.user_data_dir}")
        
    def _get_chrome_user_data_dir(self) -> Path:
        """Get Chrome user data directory for current OS."""
        system = platform.system()
        home = Path.home()
        
        if system == "Darwin":  # macOS
            return home / "Library" / "Application Support" / "Google" / "Chrome"
        elif system == "Linux":
            return home / ".config" / "google-chrome"
        elif system == "Windows":
            localappdata = os.environ.get('LOCALAPPDATA')
            if localappdata:
                return Path(localappdata) / "Google" / "Chrome" / "User Data"
            else:
                # Fallback for Windows
                return home / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        else:
            # Fallback for unknown systems
            logger.warning(f"Unknown system {system}, using fallback directory")
            return home / ".chrome-profile"
    
    def _get_template_dir(self) -> Path:
        """Get template directory path."""
        if self.config.profile_template_dir:
            return Path(self.config.profile_template_dir)
        else:
            # Use built-in template directory
            return Path(__file__).parent / "templates"
    
    def create_random_profile(self) -> str:
        """Create a randomized Chrome profile and return profile name.
        
        Returns:
            str: Profile name (e.g., "Profile12345")
        """
        if not self.config.use_profiles:
            logger.info("Profile creation disabled in config")
            return None
            
        # Generate random profile name with high entropy to avoid conflicts
        profile_name = f"Profile{random.randint(100000, 999999)}"
        
        try:
            # Ensure user data directory exists
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy template files to user data directory
            self._copy_template_files()
            
            # Create profile directory
            profile_path = self.user_data_dir / profile_name
            profile_path.mkdir(parents=True, exist_ok=True)
            
            # Create profile structure
            self._setup_profile_structure(profile_path, profile_name)
            
            # Copy and randomize history if template exists
            self._setup_profile_history(profile_path)
            
            self.current_profile = profile_name
            logger.info(f"Created Chrome profile: {profile_name}")

            # only continue after verifying profile is created
            if not profile_path.exists():
                logger.error(f"Profile directory not found: {profile_name}")
                return None

            logger.info(f"Profile created: {profile_name}")

            
            return profile_name
            
        except Exception as e:
            logger.error(f"Failed to create Chrome profile: {e}")
            return None
    
    def _copy_template_files(self):
        """Copy template files to Chrome user data directory."""
        try:
            # Copy Local State if it exists
            local_state_template = self.template_dir / "Local State"
            if local_state_template.exists():
                local_state_dest = self.user_data_dir / "Local State"
                shutil.copy2(local_state_template, local_state_dest)
                logger.debug("Copied Local State template")
            
            # Copy First Run if it exists
            first_run_template = self.template_dir / "First Run"
            if first_run_template.exists():
                first_run_dest = self.user_data_dir / "First Run"
                shutil.copy2(first_run_template, first_run_dest)
                logger.debug("Copied First Run template")
                
        except Exception as e:
            logger.warning(f"Failed to copy template files: {e}")
    
    def _setup_profile_structure(self, profile_path: Path, profile_name: str):
        """Create profile directory structure and essential files.
        
        Args:
            profile_path: Path to the profile directory
            profile_name: Name of the profile
        """
        try:
            # Create First Run marker
            first_run_path = profile_path / "First Run"
            first_run_path.touch()
            
            # Create Preferences file
            preferences = {
                "profile": {
                    "name": profile_name,
                    "avatar_index": 0,
                    "gaia_picture_file_name": "default",
                    "managed_user_id": "",
                    "user_type": -1
                },
                "browser": {
                    "show_home_button": True,
                    "check_default_browser": False
                },
                "translate": {
                    "enabled": False
                },
                "distribution": {
                    "import_bookmarks": False,
                    "import_history": False,
                    "import_home_page": False,
                    "import_search_engine": False,
                    "make_chrome_default_for_user": False,
                    "show_welcome_page": False
                },
                "sync": {
                    "remaining_rollback_tries": 0,
                    "suppress_start": False
                },
                "signin": {
                    "chrome_device_id": "0"
                },
                "media": {
                    "router": {
                        "enabled": True
                    }
                }
            }
            
            preferences_path = profile_path / "Preferences"
            with open(preferences_path, 'w') as f:
                json.dump(preferences, f)
                
            logger.debug(f"Created profile structure for {profile_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup profile structure: {e}")
            raise
    
    def _setup_profile_history(self, profile_path: Path):
        """Setup and randomize profile history.
        
        Args:
            profile_path: Path to the profile directory
        """
        try:
            history_path = profile_path / "History"
            
            # Check for template History file
            history_template = self.template_dir / "History"
            if history_template.exists():
                # Copy template history
                shutil.copy2(history_template, history_path)
                logger.debug("Copied History template")
                
                # Randomize history entries
                self._randomize_history(history_path)
            else:
                # Create empty history file
                history_path.touch()
                logger.debug("Created empty History file")
                
        except Exception as e:
            logger.warning(f"Failed to setup profile history: {e}")
    
    def _randomize_history(self, history_path: Path):
        """Randomize browser history entries to create unique fingerprint.
        
        Args:
            history_path: Path to the History database file
        """
        try:
            # Use the same SQL script as the original GSB implementation
            sql_script = """
            UPDATE urls
            SET 
                url = shuffled_table.url, 
                title = shuffled_table.title
            FROM (
                SELECT row_number() OVER (ORDER BY RANDOM()) as rownum, url, title
                FROM urls
            ) as shuffled_table
            WHERE urls.rowid = shuffled_table.rownum;
            """
            
            self._run_sql_script(str(history_path), sql_script)
            logger.debug("Randomized browser history")
            
        except Exception as e:
            logger.warning(f"Failed to randomize history: {e}")
    
    def _run_sql_script(self, db_path: str, sql_script: str):
        """Run SQL script on SQLite database.
        
        Args:
            db_path: Path to the SQLite database
            sql_script: SQL script to execute
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.executescript(sql_script)
            conn.commit()
            conn.close()
            logger.debug(f"Executed SQL script on {db_path}")
            
        except Exception as e:
            logger.error(f"Failed to execute SQL script: {e}")
            raise
    
    def get_profile_arguments(self, profile_name: str) -> Dict[str, str]:
        """Get Chrome arguments for using the profile.
        
        Args:
            profile_name: Name of the profile to use
            
        Returns:
            Dict containing Chrome arguments
        """
        if not profile_name:
            return {}
            
        return {
            "user_data_dir": str(self.user_data_dir),
            "profile_directory": profile_name
        }
    
    def cleanup_profile(self, profile_name: str = None):
        """Remove profile directory after use.
        
        Args:
            profile_name: Name of profile to cleanup (defaults to current profile)
        """
        if not self.config.cleanup_profiles:
            logger.info("Profile cleanup disabled in config")
            return
            
        target_profile = profile_name or self.current_profile
        if not target_profile:
            logger.warning("No profile to cleanup")
            return
            
        try:
            profile_path = self.user_data_dir / target_profile
            if profile_path.exists():
                shutil.rmtree(profile_path)
                logger.info(f"Cleaned up profile: {target_profile}")
            else:
                logger.warning(f"Profile directory not found: {target_profile}")
                
            if target_profile == self.current_profile:
                self.current_profile = None
                
        except Exception as e:
            logger.error(f"Failed to cleanup profile {target_profile}: {e}")
    
    def cleanup_all_profiles(self):
        """Cleanup all profiles created by this manager."""
        if not self.config.cleanup_profiles:
            return
            
        try:
            # Look for profiles matching our naming pattern
            for item in self.user_data_dir.iterdir():
                if item.is_dir() and item.name.startswith("Profile") and item.name[7:].isdigit():
                    if len(item.name) == 13:  # "Profile" + 6 digits
                        shutil.rmtree(item)
                        logger.debug(f"Cleaned up profile: {item.name}")
                        
        except Exception as e:
            logger.error(f"Failed to cleanup all profiles: {e}")
    
    def __del__(self):
        """Cleanup current profile on destruction."""
        if hasattr(self, 'current_profile') and self.current_profile:
            self.cleanup_profile()