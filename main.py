#!/usr/bin/env python3
"""
Flow Launcher Vikunja Plugin - Main Entry Point
Supports multitenant configuration for multiple plugin instances
"""

import sys
import json
from pathlib import Path

try:
    from flowlauncher import FlowLauncher
except ImportError:
    # Fallback for testing without flowlauncher package
    class FlowLauncher:
        def __call__(self):
            pass

from config import ConfigManager
from vikunja_api import VikunjaClient
from task_parser import TaskParser


class VikunjaPlugin(FlowLauncher):
    """Flow Launcher plugin for Vikunja task creation"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.task_parser = TaskParser()
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Vikunja API client with current plugin config"""
        config = self.config_manager.get_current_config()
        if config and config.get('serverUrl') and config.get('apiToken'):
            self.client = VikunjaClient(
                server_url=config['serverUrl'],
                api_token=config['apiToken']
            )

    def query(self, query_str: str):
        """
        Handle query input from Flow Launcher
        
        Args:
            query_str: User's search input
            
        Returns:
            List of result dictionaries for Flow Launcher display
        """
        results = []
        config = self.config_manager.get_current_config()

        # Empty query - show syntax help
        if not query_str.strip():
            parsing_mode = config.get('parsingMode', 'vikunja') if config else 'vikunja'
            if parsing_mode == 'todoist':
                syntax_help = "Enter a task with optional due date and tags (#project, p1-p5, @label)"
            else:
                syntax_help = "Enter a task with optional due date and tags (+project, !1-5, *label)"
            
            results.append({
                "Title": "Vikunja Quick Add",
                "SubTitle": syntax_help,
                "IcoPath": "Images/app.png"
            })
            return results

        # Validate configuration
        if not config or not config.get('serverUrl') or not config.get('apiToken'):
            results.append({
                "Title": "⚠️ Configuration Required",
                "SubTitle": "Please configure server URL and API token in settings",
                "IcoPath": "Images/app.png"
            })
            return results

        try:
            # Parse the task
            parsing_mode = config.get('parsingMode', 'vikunja')
            parsed_task = self.task_parser.parse(query_str, mode=parsing_mode)

            # Build preview subtitle
            subtitle = self._build_preview(parsed_task, config)

            results.append({
                "Title": f"Create task: {parsed_task['title']}",
                "SubTitle": subtitle,
                "IcoPath": "Images/app.png",
                "JsonRPCAction": {
                    "method": "create_task",
                    "parameters": [parsed_task]
                }
            })
        except Exception as e:
            results.append({
                "Title": "Error parsing task",
                "SubTitle": str(e),
                "IcoPath": "Images/app.png"
            })

        return results

    def create_task(self, parsed_task: dict):
        """
        Create a task in Vikunja
        
        Args:
            parsed_task: Dictionary with task details (title, description, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        self._init_client()
        if not self.client:
            self.show_message("Error", "Vikunja not configured")
            return False

        try:
            config = self.config_manager.get_current_config()
            default_project_id = config.get('defaultProjectId', 1) if config else 1
            
            success = self.client.create_task(parsed_task, default_project_id)
            
            if success:
                self.show_message("Task Created", f"Successfully created: {parsed_task['title']}")
            else:
                self.show_message("Error", "Failed to create task. Check logs for details.")
            
            return success
        except Exception as e:
            self.show_message("Error", f"Exception: {str(e)}")
            return False

    def _build_preview(self, task: dict, config: dict) -> str:
        """Build preview subtitle for task result"""
        parts = [f"Title:'{task['title']}'"]
        
        if task.get('labels'):
            parts.append(f"Labels:[{','.join(task['labels'])}]")
        
        if task.get('project'):
            parts.append(f"Project:{task['project']}")
        elif config.get('defaultProjectId'):
            parts.append("Project:Default")
        
        if task.get('dueDate'):
            parts.append(f"Due:{task['dueDate']}")
        
        if task.get('priority'):
            priority_names = {1: "Low", 2: "Medium", 3: "High", 4: "Urgent", 5: "DO NOW"}
            priority_name = priority_names.get(task['priority'], str(task['priority']))
            parts.append(f"Priority:{priority_name}")
        
        return " | ".join(parts)


if __name__ == "__main__":
    VikunjaPlugin()
