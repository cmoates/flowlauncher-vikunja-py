# Vikunja Flow Launcher Plugin (Python)

A Python implementation of the Flow Launcher Vikunja plugin with support for multiple dynamic keywords in a single plugin instance.

## Features

- **Single plugin, multiple keywords** - Use `vk`, `vw`, `vs`, etc., with different configurations
- **Quick task creation** with natural language parsing
- **Syntax support**:
  - Vikunja style: `task text +project *label !priority`
  - Todoist style: `task text #project @label p1`
- **Natural language dates**: `today`, `tomorrow`, `next week`, `monday`, etc.
- **Per-keyword configuration** - Each keyword has its own server, token, project, and parsing mode
- **No compilation needed** - Edit and restart for instant updates


## Installation

1. **Prerequisites**:
   - Python 3.11+
   - Flow Launcher

2. **Setup**:
   ```bash
   # Clone into Flow Launcher plugins directory
   cd %APPDATA%\Roaming\FlowLauncher\Plugins
   git clone <repo-url> flowlauncher-vikunja-py
   cd flowlauncher-vikunja-py
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Restart Flow Launcher**:
   - Type `restart Flow Launcher` in Flow Launcher search
   - Or restart the application

## Configuration

### First Time Setup

The plugin starts with a default `vk` keyword configured. To add your server details:

1. Open Flow Launcher settings
2. Find the Vikunja plugin
3. Click to open settings dialog
4. Configure the `vk` keyword:
   - **Server URL**: Your Vikunja instance URL (e.g., `https://vikunja.example.com`)
   - **API Token**: Your Vikunja API token (create in Vikunja → Settings → API Tokens)
   - **Default Project ID**: Project to use when none specified (default: 1 = Inbox)
   - **Parsing Mode**: Choose `vikunja` or `todoist` syntax

### Adding More Keywords

To add a new keyword (e.g., `vw` for "work", `vs` for "side"):

1. In the settings dialog, click "Add Keyword"
2. Enter the new keyword (e.g., `vw`)
3. Configure its settings:
   - Can use the same or different server
   - Each keyword can have its own project, token, and parsing mode
4. Click "Save"
5. The keyword is immediately available in Flow Launcher

### Keyword Configuration Example

```json
{
  "keywords": {
    "vk": {
      "serverUrl": "https://vikunja.example.com",
      "apiToken": "token123",
      "defaultProjectId": 1,
      "parsingMode": "vikunja"
    },
    "vw": {
      "serverUrl": "https://vikunja.example.com",
      "apiToken": "token123",
      "defaultProjectId": 42,
      "parsingMode": "vikunja"
    },
    "vs": {
      "serverUrl": "https://vikunja.example.com",
      "apiToken": "token456",
      "defaultProjectId": 99,
      "parsingMode": "todoist"
    }
  }
}
```


## Usage

### Using Different Keywords

Each keyword routes to its configured project by default:

```
vk buy milk              → Goes to project 1 (Inbox)
vw fix bug               → Goes to project 42 (Work)
vs write article         → Goes to project 99 (Side projects)
```

### Vikunja Syntax (Default)

```
task title +project *label !priority
```

Examples:
- `vk Buy groceries +shopping *today !2` - Medium priority task with label
- `vw Fix bug tomorrow` - Work task due tomorrow
- `vk Meeting next monday +work` - Work task for next Monday

### Todoist Syntax

Enable for a keyword in settings, then use:

```
task title #project @label p1
```

Examples:
- `vs Write article #blog @writing p1` - High priority blog article
- `vs Review PR tomorrow` - Review PR due tomorrow
- `vs Call client next friday #sales` - Sales task for next Friday

### Date Examples

All keywords support these date formats:
- `today` - Due today
- `tomorrow` - Due tomorrow
- `next week` - Due in 7 days
- `monday` - Due next Monday
- `tuesday`, `wednesday`, etc. - Due next specified weekday
- `2024-12-25` - Due on specific date (ISO format)


## Architecture

### Single Plugin, Multiple Keywords

Instead of maintaining separate plugin copies, all keywords are managed in a single plugin instance:

1. **Flow Launcher sees**: One plugin with multiple action keywords
2. **Settings file**: Contains configurations for all keywords
3. **Per-keyword routing**: Each keyword uses its configured server, token, and project

**Benefits**:
- No duplicate plugin code
- Single update path
- All keywords in one settings dialog
- Future configuration options apply to all keywords

### File Structure

```
flowlauncher-vikunja-py/
├── plugin.json          # Plugin metadata with ActionKeywords array
├── main.py              # Entry point & keyword routing
├── config.py            # Multi-keyword configuration management
├── vikunja_api.py       # Vikunja API client
├── task_parser.py       # Natural language parser (Vikunja + Todoist)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Test the parser
python -c "from task_parser import TaskParser; print(TaskParser().parse('buy milk tomorrow +personal *shopping !2'))"
```

### Adding New Configuration Fields

To add a new field (e.g., `color`, `labels`, etc.) that applies to all keywords:

1. Add the field to the default config in `config.py`'s `_initialize_settings()`
2. Update the settings UI to include the new field
3. Use `config.get("fieldName")` in `main.py` and other modules

All existing keywords automatically get the new field with a default value.

### Live Reload

After making changes:
1. Type `restart Flow Launcher` in Flow Launcher
2. Your changes are immediately applied

No compilation needed!

## Troubleshooting

### Plugin not showing up

1. Check Flow Launcher logs: `%APPDATA%\Roaming\FlowLauncher\Logs\`
2. Ensure `plugin.json` has valid JSON syntax
3. Verify Python 3.11+ is installed and on PATH
4. Run `pip install -r requirements.txt` again

### Keywords not recognized

- Ensure `ActionKeywords` array in `plugin.json` includes your keyword
- After adding keywords in settings, restart Flow Launcher
- Check that `Settings.json` has the keyword in the `keywords` dict

### Settings not saving

- Ensure `%APPDATA%\Roaming\FlowLauncher\Settings\Plugins\Vikunja\` directory exists
- Check file permissions
- Review Flow Launcher logs for errors

### Tasks not creating

- Verify server URL and API token are correct for the keyword used
- Test connection in settings dialog for the specific keyword
- Check Vikunja server logs for API errors
- Ensure API token has required permissions (tasks: create, labels: create/read)

## Requirements

The Vikunja API token needs these permissions:
- `tasks: create` - Create new tasks
- `labels: create, read` - Create and read labels
- `projects: read` - List projects
- `tasks_labels: create` - Assign labels to tasks

## Extending with New Keywords

To add even more keywords dynamically without editing code:

1. Open settings dialog
2. Click "Add Keyword"
3. Enter new keyword and configuration
4. Save
5. Restart Flow Launcher

All keywords share the same parsing logic and API client code, so adding keywords has minimal overhead.

## License

See LICENSE file for details.

## Credits

This plugin was inspired by the original Vikunja Flow Launcher plugin in C#. (https://github.com/AntoineTA/Flow.Launcher.Plugin.Vikunja)

