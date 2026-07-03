"""
Vikunja API client for task management
"""

import requests
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin


class VikunjaClient:
    """HTTP client for Vikunja API"""

    def __init__(self, server_url: str, api_token: str):
        """
        Initialize Vikunja API client
        
        Args:
            server_url: Base URL of Vikunja instance (e.g., https://vikunja.example.com)
            api_token: API token for authentication
        """
        self.server_url = server_url.rstrip('/')
        self.api_token = api_token
        self.base_url = urljoin(self.server_url + '/', 'api/v1/')
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        })

    def create_task(self, task: Dict[str, Any], default_project_id: int = 1) -> bool:
        """
        Create a task in Vikunja
        
        Args:
            task: Task dictionary with keys like 'title', 'description', 'dueDate', 'priority', 'labels'
            default_project_id: Default project ID if none specified in task
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine project ID
            project_id = default_project_id
            
            if task.get('project'):
                # Try to find project by name
                project_id = self._find_project_by_name(task['project'])
                if not project_id:
                    project_id = default_project_id

            # Build task payload
            payload = {
                'title': task.get('title', ''),
                'description': task.get('description', ''),
                'dueDate': task.get('dueDate'),
                'priority': task.get('priority', 0)
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}

            # Create task
            url = urljoin(self.base_url, f'projects/{project_id}/tasks')
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            
            created_task = response.json()
            task_id = created_task.get('id')
            
            # Add labels if any
            if task.get('labels') and task_id:
                self._add_labels_to_task(task_id, task['labels'])
            
            return True
        except Exception as e:
            print(f"Error creating task: {e}")
            return False

    def _find_project_by_name(self, project_name: str) -> Optional[int]:
        """
        Find project ID by name
        
        Args:
            project_name: Name of the project
            
        Returns:
            Project ID if found, None otherwise
        """
        try:
            url = urljoin(self.base_url, 'projects')
            response = self.session.get(url)
            response.raise_for_status()
            
            projects = response.json()
            for project in projects:
                if project.get('title', '').lower() == project_name.lower():
                    return project.get('id')
        except Exception as e:
            print(f"Error finding project: {e}")
        
        return None

    def _add_labels_to_task(self, task_id: int, label_names: List[str]) -> bool:
        """
        Add labels to a task, creating them if they don't exist
        
        Args:
            task_id: ID of the task
            label_names: List of label names to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for label_name in label_names:
                label_id = self._find_or_create_label(label_name)
                if label_id:
                    # Assign label to task
                    url = urljoin(self.base_url, f'tasks/{task_id}/labels')
                    payload = {'labelId': label_id}
                    response = self.session.put(url, json=payload)
                    response.raise_for_status()
            
            return True
        except Exception as e:
            print(f"Error adding labels: {e}")
            return False

    def _find_or_create_label(self, label_name: str) -> Optional[int]:
        """
        Find label by name, creating it if it doesn't exist
        
        Args:
            label_name: Name of the label
            
        Returns:
            Label ID if successful, None otherwise
        """
        try:
            # Try to find existing label
            url = urljoin(self.base_url, 'labels')
            response = self.session.get(url)
            response.raise_for_status()
            
            labels = response.json()
            for label in labels:
                if label.get('title', '').lower() == label_name.lower():
                    return label.get('id')
            
            # Create new label if not found
            payload = {
                'title': label_name,
                'hexColor': '#1973ff'  # Default blue
            }
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            
            created_label = response.json()
            return created_label.get('id')
        except Exception as e:
            print(f"Error finding/creating label: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test connection to Vikunja server
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            url = urljoin(self.base_url, 'user')
            response = self.session.get(url)
            return response.status_code == 200
        except Exception:
            return False
