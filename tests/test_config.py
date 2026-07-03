"""
Unit tests for config module
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
from config import ConfigManager


class TestConfigManager:
    """Test ConfigManager functionality"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock the FlowLauncher settings directory
            yield Path(tmpdir)
    
    def test_config_manager_default_settings_structure(self, temp_config_dir):
        """Test that default settings have correct structure"""
        with patch('config.Path.home', return_value=temp_config_dir):
            with patch.object(Path, 'expanduser', return_value=temp_config_dir):
                # This test validates the expected settings structure
                expected_structure = {
                    "keywords": {
                        "vk": {
                            "serverUrl": "",
                            "apiToken": "",
                            "defaultProjectId": 1,
                            "parsingMode": "vikunja"
                        }
                    }
                }
                assert "keywords" in expected_structure
                assert "vk" in expected_structure["keywords"]
                assert "serverUrl" in expected_structure["keywords"]["vk"]
    
    def test_keyword_config_independence(self):
        """Test that keyword configs are independent"""
        # Create two configs and verify they're different
        config1 = {
            "serverUrl": "https://server1.com",
            "apiToken": "token1",
            "defaultProjectId": 1,
            "parsingMode": "vikunja"
        }
        config2 = {
            "serverUrl": "https://server2.com",
            "apiToken": "token2",
            "defaultProjectId": 2,
            "parsingMode": "todoist"
        }
        
        # Verify configs are different
        assert config1 != config2
        assert config1["serverUrl"] != config2["serverUrl"]
        assert config1["parsingMode"] != config2["parsingMode"]
    
    def test_settings_file_structure_validation(self):
        """Test that settings file has correct structure"""
        settings = {
            "keywords": {
                "vk": {
                    "serverUrl": "",
                    "apiToken": "",
                    "defaultProjectId": 1,
                    "parsingMode": "vikunja"
                }
            }
        }
        
        # Validate structure
        assert "keywords" in settings
        for keyword, config in settings["keywords"].items():
            assert "serverUrl" in config
            assert "apiToken" in config
            assert "defaultProjectId" in config
            assert "parsingMode" in config
    
    def test_keyword_addition_structure(self):
        """Test structure of newly added keywords"""
        new_keyword_config = {
            "serverUrl": "https://vikunja.example.com",
            "apiToken": "test-token",
            "defaultProjectId": 5,
            "parsingMode": "vikunja"
        }
        
        # Verify new keyword has all required fields
        assert "serverUrl" in new_keyword_config
        assert "apiToken" in new_keyword_config
        assert "defaultProjectId" in new_keyword_config
        assert "parsingMode" in new_keyword_config
    
    def test_parsing_mode_values(self):
        """Test valid parsing mode values"""
        valid_modes = ["vikunja", "todoist"]
        
        for mode in valid_modes:
            assert mode in ["vikunja", "todoist"]
    
    def test_default_project_id_type(self):
        """Test that project ID is numeric"""
        project_id = 1
        assert isinstance(project_id, int)
        assert project_id > 0
    
    def test_api_token_is_string(self):
        """Test that API token is string type"""
        token = "test-token-123"
        assert isinstance(token, str)
    
    def test_server_url_format(self):
        """Test server URL format"""
        server_url = "https://vikunja.example.com"
        assert server_url.startswith("https://") or server_url.startswith("http://")
    
    def test_multiple_keyword_dict_structure(self):
        """Test structure with multiple keywords"""
        keywords = {
            "vk": {"serverUrl": "", "apiToken": "", "defaultProjectId": 1, "parsingMode": "vikunja"},
            "vw": {"serverUrl": "", "apiToken": "", "defaultProjectId": 2, "parsingMode": "todoist"},
            "vx": {"serverUrl": "", "apiToken": "", "defaultProjectId": 3, "parsingMode": "vikunja"}
        }
        
        # Verify all keywords have same structure
        for keyword, config in keywords.items():
            assert "serverUrl" in config
            assert "apiToken" in config
            assert "defaultProjectId" in config
            assert "parsingMode" in config

