"""
Configuration management for Vikunja plugin with multitenant support
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """Manages multitenant plugin configuration"""

    def __init__(self):
        """Initialize config manager with Flow Launcher settings directory"""
        # Flow Launcher stores plugin settings in:
        # %APPDATA%\Roaming\FlowLauncher\Settings\Plugins\<PluginName>\
        # For Python plugins, it uses the ExecuteFileName without extension as the key
        self.plugin_name = "Vikunja-Python"
        self.settings_dir = Path.home() / "AppData" / "Roaming" / "FlowLauncher" / "Settings" / "Plugins" / self.plugin_name
        self.settings_file = self.settings_dir / "Settings.json"
        
        # Get the current plugin ID from environment or plugin.json
        self.plugin_id = os.environ.get("PLUGIN_ID", self._get_default_plugin_id())
        
        # Ensure directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize settings
        self.settings = self._load_settings()

    def _get_default_plugin_id(self) -> str:
        """Get plugin ID from plugin.json or use a default"""
        try:
            plugin_json_path = Path(__file__).parent / "plugin.json"
            if plugin_json_path.exists():
                with open(plugin_json_path) as f:
                    data = json.load(f)
                    return data.get("ID", "default")
        except Exception:
            pass
        return "default"

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
        """Create new settings structure"""
        return {
            "configurations": {}
        }

    def get_current_config(self) -> Optional[Dict[str, Any]]:
        """
        Get configuration for the current plugin instance
        
        If no config exists for this ID, inherits from another instance.
        """
        configs = self.settings.get("configurations", {})
        
        # If this plugin ID already has config, return it
        if self.plugin_id in configs:
            return configs[self.plugin_id]
        
        # New instance - try to inherit from another instance if available
        if configs:
            # Copy first available config (likely to be correct)
            existing_config = next(iter(configs.values()))
            config = dict(existing_config)
            configs[self.plugin_id] = config
            self._save_settings()
            return config
        
        # No existing config - return empty/default
        return None

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration for current plugin instance
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            configs = self.settings.get("configurations", {})
            configs[self.plugin_id] = config
            self.settings["configurations"] = configs
            self._save_settings()
            return True
        except Exception as e:
            print(f"Error saving config: {e}", file=__import__("sys").stderr)
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

    def get_all_instances(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured plugin instances"""
        return self.settings.get("configurations", {})
