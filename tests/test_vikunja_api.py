"""
Unit tests for vikunja_api module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from vikunja_api import VikunjaClient


class TestVikunjaClientInitialization:
    """Test VikunjaClient initialization"""
    
    def test_initialization_sets_headers(self):
        """Test that initialization sets correct headers"""
        client = VikunjaClient("https://vikunja.example.com", "test-token")
        
        assert client.session.headers.get("Authorization") == "Bearer test-token"
        assert client.session.headers.get("Content-Type") == "application/json"
    
    def test_initialization_constructs_base_url(self):
        """Test that base_url is correctly constructed"""
        client = VikunjaClient("https://vikunja.example.com", "test-token")
        
        assert client.base_url.endswith("api/v1/")
        assert "https://vikunja.example.com" in client.base_url
    
    def test_initialization_strips_trailing_slash(self):
        """Test that trailing slash is handled correctly"""
        client1 = VikunjaClient("https://vikunja.example.com", "token")
        client2 = VikunjaClient("https://vikunja.example.com/", "token")
        
        assert client1.base_url == client2.base_url


class TestVikunjaClientTaskCreation:
    """Test task creation functionality"""
    
    @pytest.fixture
    def client(self):
        """Create VikunjaClient with mocked session"""
        return VikunjaClient("https://vikunja.example.com", "test-token")
    
    def test_create_task_minimal_payload(self, client):
        """Test creating task with minimal fields"""
        task = {
            "title": "Buy milk",
            "description": "",
            "dueDate": None,
            "priority": 0
        }
        
        with patch.object(client.session, 'put') as mock_put:
            mock_response = Mock()
            mock_response.json.return_value = {"id": 123}
            mock_response.status_code = 200
            mock_put.return_value = mock_response
            
            result = client.create_task(task, default_project_id=1)
        
        assert result is True
        mock_put.assert_called_once()
    
    def test_create_task_includes_title_and_description(self, client):
        """Test that title and description are included in payload"""
        task = {
            "title": "Buy milk",
            "description": "2% milk, 1 liter",
            "dueDate": None,
            "priority": 0
        }
        
        with patch.object(client.session, 'put') as mock_put:
            mock_response = Mock()
            mock_response.json.return_value = {"id": 123}
            mock_put.return_value = mock_response
            
            client.create_task(task, default_project_id=1)
        
        # Check the payload sent
        call_args = mock_put.call_args
        payload = call_args.kwargs['json']
        
        assert payload["title"] == "Buy milk"
        assert payload["description"] == "2% milk, 1 liter"
    
    def test_create_task_includes_due_date_and_priority(self, client):
        """Test that dueDate and priority are included in payload"""
        task = {
            "title": "Buy milk",
            "description": "",
            "dueDate": "2026-07-05T00:00:00.000Z",
            "priority": 3
        }
        
        with patch.object(client.session, 'put') as mock_put:
            mock_response = Mock()
            mock_response.json.return_value = {"id": 123}
            mock_put.return_value = mock_response
            
            client.create_task(task, default_project_id=1)
        
        call_args = mock_put.call_args
        payload = call_args.kwargs['json']
        
        assert payload["dueDate"] == "2026-07-05T00:00:00.000Z"
        assert payload["priority"] == 3
    
    def test_create_task_removes_none_values(self, client):
        """Test that None values are removed from payload"""
        task = {
            "title": "Buy milk",
            "description": None,
            "dueDate": None,
            "priority": 0
        }
        
        with patch.object(client.session, 'put') as mock_put:
            mock_response = Mock()
            mock_response.json.return_value = {"id": 123}
            mock_put.return_value = mock_response
            
            client.create_task(task, default_project_id=1)
        
        call_args = mock_put.call_args
        payload = call_args.kwargs['json']
        
        assert "description" not in payload or payload["description"] != ""
    
    def test_create_task_uses_default_project_id(self, client):
        """Test that default_project_id is used when no project specified"""
        task = {
            "title": "Buy milk",
            "description": "",
            "project": None
        }
        
        with patch.object(client.session, 'put') as mock_put:
            mock_response = Mock()
            mock_response.json.return_value = {"id": 123}
            mock_put.return_value = mock_response
            
            client.create_task(task, default_project_id=42)
        
        call_args = mock_put.call_args
        url = call_args[0][0]
        
        assert "projects/42/tasks" in url
    
    def test_create_task_failure_returns_false(self, client):
        """Test that creation failure returns False"""
        task = {
            "title": "Buy milk",
            "description": "",
            "dueDate": None,
            "priority": 0
        }
        
        with patch.object(client.session, 'put') as mock_put:
            mock_put.side_effect = Exception("Connection error")
            
            result = client.create_task(task, default_project_id=1)
        
        assert result is False
    
    def test_create_task_adds_labels_if_present(self, client):
        """Test that labels are added after task creation"""
        task = {
            "title": "Buy milk",
            "description": "",
            "dueDate": None,
            "priority": 0,
            "labels": ["grocery", "urgent"]
        }
        
        with patch.object(client.session, 'put') as mock_put, \
             patch.object(client, '_add_labels_to_task') as mock_add_labels:
            
            mock_response = Mock()
            mock_response.json.return_value = {"id": 123}
            mock_put.return_value = mock_response
            
            client.create_task(task, default_project_id=1)
        
        mock_add_labels.assert_called_once_with(123, ["grocery", "urgent"])


class TestVikunjaClientProjectLookup:
    """Test project lookup functionality"""
    
    @pytest.fixture
    def client(self):
        """Create VikunjaClient with mocked session"""
        return VikunjaClient("https://vikunja.example.com", "test-token")
    
    def test_find_project_by_name_exact_match(self, client):
        """Test finding project with exact name match"""
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = [
                {"id": 1, "title": "Shopping"},
                {"id": 2, "title": "Work"}
            ]
            mock_get.return_value = mock_response
            
            project_id = client._find_project_by_name("Shopping")
        
        assert project_id == 1
    
    def test_find_project_by_name_case_insensitive(self, client):
        """Test that project lookup is case-insensitive"""
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = [
                {"id": 1, "title": "Shopping"}
            ]
            mock_get.return_value = mock_response
            
            project_id = client._find_project_by_name("shopping")
        
        assert project_id == 1
    
    def test_find_project_by_name_not_found(self, client):
        """Test that None is returned when project not found"""
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = [
                {"id": 1, "title": "Shopping"}
            ]
            mock_get.return_value = mock_response
            
            project_id = client._find_project_by_name("Nonexistent")
        
        assert project_id is None
    
    def test_find_project_by_name_error_handling(self, client):
        """Test that None is returned on error"""
        with patch.object(client.session, 'get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            project_id = client._find_project_by_name("Shopping")
        
        assert project_id is None


class TestVikunjaClientLabels:
    """Test label functionality"""
    
    @pytest.fixture
    def client(self):
        """Create VikunjaClient with mocked session"""
        return VikunjaClient("https://vikunja.example.com", "test-token")
    
    def test_find_or_create_label_existing(self, client):
        """Test finding existing label"""
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = [
                {"id": 1, "title": "grocery"}
            ]
            mock_get.return_value = mock_response
            
            label_id = client._find_or_create_label("grocery")
        
        assert label_id == 1
    
    def test_find_or_create_label_creates_new(self, client):
        """Test creating label when not found"""
        with patch.object(client.session, 'get') as mock_get, \
             patch.object(client.session, 'put') as mock_put:
            
            mock_get.return_value.json.return_value = []
            mock_put.return_value.json.return_value = {"id": 99, "title": "newlabel"}
            
            label_id = client._find_or_create_label("newlabel")
        
        assert label_id == 99
        mock_put.assert_called_once()
    
    def test_find_or_create_label_sets_color(self, client):
        """Test that created label includes blue color"""
        with patch.object(client.session, 'get') as mock_get, \
             patch.object(client.session, 'put') as mock_put:
            
            mock_get.return_value.json.return_value = []
            mock_put.return_value.json.return_value = {"id": 99}
            
            client._find_or_create_label("newlabel")
        
        call_args = mock_put.call_args
        payload = call_args.kwargs['json']
        
        assert payload["hexColor"] == "#1973ff"
    
    def test_add_labels_to_task(self, client):
        """Test adding multiple labels to task"""
        with patch.object(client.session, 'put') as mock_put, \
             patch.object(client, '_find_or_create_label') as mock_find:
            
            mock_find.side_effect = [1, 2]
            mock_put.return_value.status_code = 200
            
            result = client._add_labels_to_task(123, ["grocery", "urgent"])
        
        assert result is True
        assert mock_put.call_count == 2
    
    def test_add_labels_to_task_error_handling(self, client):
        """Test error handling in label addition"""
        with patch.object(client.session, 'put') as mock_put, \
             patch.object(client, '_find_or_create_label') as mock_find:
            
            mock_find.side_effect = Exception("Label error")
            
            result = client._add_labels_to_task(123, ["grocery"])
        
        assert result is False


class TestVikunjaClientConnection:
    """Test connection testing"""
    
    def test_test_connection_success(self):
        """Test successful connection"""
        client = VikunjaClient("https://vikunja.example.com", "test-token")
        
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = client.test_connection()
        
        assert result is True
    
    def test_test_connection_failure(self):
        """Test failed connection"""
        client = VikunjaClient("https://vikunja.example.com", "test-token")
        
        with patch.object(client.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            
            result = client.test_connection()
        
        assert result is False
    
    def test_test_connection_exception(self):
        """Test connection with exception"""
        client = VikunjaClient("https://vikunja.example.com", "test-token")
        
        with patch.object(client.session, 'get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = client.test_connection()
        
        assert result is False
