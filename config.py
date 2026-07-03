"""
Configuration management for Vikunja plugin with multi-keyword support
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """Manages multi-keyword plugin configuration"""

    def __init__(self):
        """Initialize config manager with Flow Launcher settings directory"""
        # Flow Launcher stores plugin settings in:
        # %APPDATA%\Roaming\FlowLauncher\Settings\Plugins\<PluginName>\
        self.plugin_name = "Vikunja"
        appdata_path = Path.home() / "AppData" / "Roaming" / "FlowLauncher"
        plugins_dir = appdata_path / "Settings" / "Plugins"
        self.settings_dir = plugins_dir / self.plugin_name
        self.settings_file = self.settings_dir / "Settings.json"

        # Ensure directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)

        # Load or initialize settings
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from disk or create default structure"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._initialize_settings()
        else:
            return self._initialize_settings()

    def _initialize_settings(self) -> Dict[str, Any]:
        """Create new settings structure with default 'vk' keyword"""
        return {
            "keywords": {
                "vk": {
                    "serverUrl": "",
                    "apiToken": "",
                    "defaultProjectId": 1,
                    "parsingMode": "vikunja"
                }
            }
        }

    def get_keyword_config(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific keyword

        Args:
            keyword: The keyword (e.g., 'vk', 'vw', 'vs')

        Returns:
            Configuration dictionary or None if keyword not found
        """
        keywords = self.settings.get("keywords", {})
        return keywords.get(keyword)

    def save_keyword_config(self, keyword: str, config: Dict[str, Any]) -> bool:
        """
        Save configuration for a specific keyword

        Args:
            keyword: The keyword to save config for
            config: Configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            keywords = self.settings.get("keywords", {})
            keywords[keyword] = config
            self.settings["keywords"] = keywords
            self._save_settings()
            return True
        except Exception as e:
            print(f"Error saving keyword config: {e}", file=__import__("sys").stderr)
            return False

    def add_keyword(self, keyword: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a new keyword with configuration

        Args:
            keyword: The keyword to add
            config: Configuration for this keyword (uses default if not provided)

        Returns:
            True if successful, False if keyword already exists
        """
        keywords = self.settings.get("keywords", {})
        if keyword in keywords:
            return False

        if config is None:
            config = {
                "serverUrl": "",
                "apiToken": "",
                "defaultProjectId": 1,
                "parsingMode": "vikunja"
            }

        return self.save_keyword_config(keyword, config)

    def remove_keyword(self, keyword: str) -> bool:
        """
        Remove a keyword

        Args:
            keyword: The keyword to remove

        Returns:
            True if successful, False if keyword not found or is last one
        """
        keywords = self.settings.get("keywords", {})
        if keyword not in keywords:
            return False

        # Don't allow removing the last keyword
        if len(keywords) <= 1:
            return False

        try:
            del keywords[keyword]
            self.settings["keywords"] = keywords
            self._save_settings()
            return True
        except Exception as e:
            print(f"Error removing keyword: {e}", file=__import__("sys").stderr)
            return False

    def _save_settings(self) -> bool:
        """Write settings to disk"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing settings: {e}", file=__import__("sys").stderr)
            return False

    def get_all_keywords(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured keywords and their configurations"""
        return self.settings.get("keywords", {})
