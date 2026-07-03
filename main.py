"""
Flow Launcher plugin for Vikunja with multi-keyword support

Each keyword can have its own complete configuration including:
- Server URL
- API Token
- Default Project ID
- Parsing Mode (Vikunja or Todoist syntax)
- Future extensibility (color, labels, etc.)
"""

from pyflowlauncher import FlowLauncher
from config import ConfigManager
from task_parser import TaskParser
from vikunja_api import VikunjaClient


class VikunjaPlugin(FlowLauncher):
    """Flow Launcher plugin for Vikunja task creation with multi-keyword support"""

    def __init__(self):
        """Initialize the plugin"""
        super().__init__()
        self.config_manager = ConfigManager()
        self.task_parser = TaskParser()
        self.api_clients = {}  # Cache API clients per keyword

    def query(self, query_str: str):
        """
        Handle search query from Flow Launcher
        
        Args:
            query_str: The search query (keyword already stripped by Flow Launcher)
            
        Returns:
            List of result dictionaries for Flow Launcher
        """
        try:
            # Extract the keyword from the raw RPC request
            keyword = self._extract_keyword_from_rpc()
            
            # Get configuration for this keyword
            config = self.config_manager.get_keyword_config(keyword)
            if not config:
                return self._error_result(f"Keyword '{keyword}' not configured")
            
            # Validate configuration
            if not config.get("serverUrl") or not config.get("apiToken"):
                return self._error_result(f"Keyword '{keyword}' is not fully configured. Set server URL and API token.")
            
            # If no query, show help
            if not query_str.strip():
                return [{
                    "Title": f"Create task in Vikunja (project {config['defaultProjectId']})",
                    "SubTitle": "Type a task description to add to Vikunja",
                    "IcoPath": "Images/app.png"
                }]
            
            # Parse the task
            parsing_mode = config.get("parsingMode", "vikunja")
            parsed_task = self.task_parser.parse(query_str, parsing_mode)
            
            # Use default project if not specified
            if not parsed_task.get("project"):
                parsed_task["project"] = config["defaultProjectId"]
            
            # Build preview
            preview = self._build_preview(parsed_task, config)
            
            return [{
                "Title": f"Create: {parsed_task['title']}",
                "SubTitle": preview,
                "IcoPath": "Images/app.png",
                "JsonRPCAction": {
                    "method": "create_task",
                    "parameters": [keyword, parsed_task]
                }
            }]
        
        except Exception as e:
            return self._error_result(f"Error: {str(e)}")

    def create_task(self, keyword: str, parsed_task: dict):
        """
        Create a task in Vikunja
        
        Args:
            keyword: The keyword that triggered this action
            parsed_task: The parsed task dictionary
        """
        try:
            config = self.config_manager.get_keyword_config(keyword)
            if not config:
                self._show_error(f"Keyword '{keyword}' not found in configuration")
                return
            
            # Get or create API client for this keyword
            if keyword not in self.api_clients:
                self.api_clients[keyword] = VikunjaClient(
                    config["serverUrl"],
                    config["apiToken"]
                )
            
            client = self.api_clients[keyword]
            
            # Determine project ID
            project_id = parsed_task.get("project")
            if isinstance(project_id, str):
                # User specified project name, look it up
                found_id = client.find_project_by_name_async(project_id)
                if not found_id:
                    self._show_error(f"Project '{project_id}' not found")
                    return
                project_id = found_id
            else:
                # Use numeric project ID
                project_id = int(project_id or config["defaultProjectId"])
            
            # Create the task
            success = client.create_task(parsed_task, project_id)
            if success:
                self._show_message(f"✓ Task created: {parsed_task['title']}")
            else:
                self._show_error("Failed to create task")
        
        except Exception as e:
            self._show_error(f"Error creating task: {str(e)}")

    def _extract_keyword_from_rpc(self) -> str:
        """
        Extract the keyword from the raw RPC request
        
        Flow Launcher strips the keyword before passing to query(), but we can
        access the original input via rpc_request to determine which keyword was used.
        
        Returns:
            The keyword that triggered this query (e.g., 'vk', 'vw')
        """
        try:
            # Access raw query from RPC context
            raw_query = self.rpc_request.get("rawQuery", {})
            full_input = raw_query.get("RawQuery", "")
            
            # Extract first word as keyword
            if full_input:
                keyword = full_input.split()[0].lower()
                # Validate it's a known keyword
                all_keywords = self.config_manager.get_all_keywords()
                if keyword in all_keywords:
                    return keyword
        except Exception:
            pass
        
        # Fallback to first configured keyword
        all_keywords = self.config_manager.get_all_keywords()
        if all_keywords:
            return next(iter(all_keywords.keys()))
        
        return "vk"

    def _build_preview(self, task: dict, config: dict) -> str:
        """
        Build preview subtitle for task result
        
        Args:
            task: Parsed task dictionary
            config: Configuration for this keyword
            
        Returns:
            Preview string
        """
        parts = []
        
        project = task.get("project") or config.get("defaultProjectId", 1)
        parts.append(f"Project: {project}")
        
        if task.get("labels"):
            parts.append(f"Labels: {', '.join(task['labels'])}")
        
        if task.get("priority"):
            parts.append(f"Priority: {task['priority']}")
        
        if task.get("dueDate"):
            parts.append(f"Due: {task['dueDate']}")
        
        return " | ".join(parts)

    def _error_result(self, message: str):
        """Create an error result"""
        return [{
            "Title": "Error",
            "SubTitle": message,
            "IcoPath": "Images/warning.png"
        }]

    def _show_message(self, message: str):
        """Show a message (Flow Launcher will handle this)"""
        print(message)

    def _show_error(self, message: str):
        """Show an error message"""
        print(f"Error: {message}")


if __name__ == "__main__":
    VikunjaPlugin()
