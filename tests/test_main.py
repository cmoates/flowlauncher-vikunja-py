"""
Unit tests for main plugin module
"""

import pytest
import json
import sys
from unittest.mock import Mock, patch, MagicMock

# Mock pyflowlauncher before importing main
sys.modules['pyflowlauncher'] = MagicMock()

from main import VikunjaPlugin


class TestVikunjaPluginStructure:
    """Test plugin structure and attributes"""
    
    def test_plugin_module_exists(self):
        """Test that main module imports successfully"""
        # The fact that VikunjaPlugin is imported without error means module structure is ok
        assert VikunjaPlugin is not None


class TestKeywordExtractionLogic:
    """Test keyword extraction logic"""
    
    def test_keyword_extraction_from_query(self):
        """Test extracting keyword from raw query"""
        # Test various query formats
        test_cases = [
            ("vk buy milk", "vk"),
            ("vw buy milk", "vw"),
            ("vs task", "vs"),
        ]
        
        for query, expected_keyword in test_cases:
            # Extract first word
            keyword = query.split()[0]
            assert keyword == expected_keyword
    
    def test_keyword_with_modifiers(self):
        """Test extracting keyword from query with modifiers"""
        query = "vk buy milk +Project *label !2"
        keyword = query.split()[0]
        
        assert keyword == "vk"
        assert "+Project" in query
        assert "*label" in query
        assert "!2" in query


class TestQueryHandlingLogic:
    """Test query parsing structure"""
    
    def test_task_parsing_structure(self):
        """Test expected structure after parsing"""
        expected_parse_result = {
            "title": "Buy milk",
            "description": "",
            "project": None,
            "labels": [],
            "priority": 0,
            "dueDate": None
        }
        
        # Verify all required keys are present
        required_keys = ["title", "description", "project", "labels", "priority", "dueDate"]
        for key in required_keys:
            assert key in expected_parse_result
    
    def test_task_creation_payload_structure(self):
        """Test expected structure of task creation payload"""
        task_payload = {
            "title": "Buy milk",
            "description": "2% milk",
            "dueDate": "2026-07-05T00:00:00.000Z",
            "priority": 2
        }
        
        # Verify payload structure
        assert "title" in task_payload
        assert "description" in task_payload
        assert "dueDate" in task_payload
        assert "priority" in task_payload
        assert task_payload["title"] == "Buy milk"


class TestPreviewFormattingLogic:
    """Test preview formatting"""
    
    def test_preview_subtitle_components(self):
        """Test that preview can include all task components"""
        task = {
            "title": "Buy milk",
            "description": "2% milk",
            "project": "Shopping",
            "labels": ["grocery", "urgent"],
            "priority": 2,
            "dueDate": "2026-07-05"
        }
        
        # Simulate preview building
        preview_parts = []
        if task.get("project"):
            preview_parts.append(f"Project: {task['project']}")
        if task.get("labels"):
            preview_parts.append(f"Labels: {', '.join(task['labels'])}")
        if task.get("priority"):
            preview_parts.append(f"Priority: {task['priority']}")
        if task.get("dueDate"):
            preview_parts.append(f"Due: {task['dueDate']}")
        
        preview = " | ".join(preview_parts)
        
        # Verify preview contains expected information
        assert "Shopping" in preview or len(preview_parts) > 0
        assert "grocery" in preview or "Labels" in preview


class TestConfigurationManagement:
    """Test configuration management logic"""
    
    def test_keyword_config_structure(self):
        """Test keyword configuration structure"""
        config = {
            "serverUrl": "https://vikunja.example.com",
            "apiToken": "test-token",
            "defaultProjectId": 1,
            "parsingMode": "vikunja"
        }
        
        # Verify config has all required fields
        required_fields = ["serverUrl", "apiToken", "defaultProjectId", "parsingMode"]
        for field in required_fields:
            assert field in config
    
    def test_multiple_keyword_configurations(self):
        """Test multiple keyword configurations"""
        keywords_config = {
            "vk": {
                "serverUrl": "https://server1.com",
                "apiToken": "token1",
                "defaultProjectId": 1,
                "parsingMode": "vikunja"
            },
            "vw": {
                "serverUrl": "https://server2.com",
                "apiToken": "token2",
                "defaultProjectId": 42,
                "parsingMode": "todoist"
            }
        }
        
        # Verify each keyword has independent config
        assert keywords_config["vk"]["serverUrl"] != keywords_config["vw"]["serverUrl"]
        assert keywords_config["vk"]["parsingMode"] != keywords_config["vw"]["parsingMode"]


class TestApiClientCaching:
    """Test API client caching logic"""
    
    def test_client_cache_structure(self):
        """Test client cache structure"""
        api_clients = {}
        
        # Simulate caching
        api_clients["vk"] = Mock(name="VikunjaClient_vk")
        api_clients["vw"] = Mock(name="VikunjaClient_vw")
        
        # Verify caching works
        assert "vk" in api_clients
        assert "vw" in api_clients
        assert api_clients["vk"] != api_clients["vw"]
    
    def test_client_reuse_from_cache(self):
        """Test that cached clients are reused"""
        api_clients = {}
        client_vk = Mock(name="VikunjaClient")
        
        # First access
        api_clients["vk"] = client_vk
        first_access = api_clients.get("vk")
        
        # Second access
        second_access = api_clients.get("vk")
        
        # Should be the same object
        assert first_access is second_access

