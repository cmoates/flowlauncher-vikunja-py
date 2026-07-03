# Vikunja Flow Launcher Plugin (Python)

A Python implementation of the Flow Launcher Vikunja plugin with native support for multitenant configuration.

## Features

- **Quick task creation** with natural language parsing
- **Multitenant support** - Run multiple instances with different keywords and configurations
- **Syntax support**:
  - Vikunja style: `task text +project *label !priority`
  - Todoist style: `task text #project @label p1`
- **Natural language dates**: `today`, `tomorrow`, `next week`, `monday`, etc.
- **Configuration inheritance** - New instances automatically inherit settings from existing ones
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

### First Instance

Type `vk` in Flow Launcher to open the settings dialog:
- **Server URL**: Your Vikunja instance URL (e.g., `https://vikunja.example.com`)
- **API Token**: Your Vikunja API token (create in Vikunja → Settings → API Tokens)
- **Default Project ID**: Project to use when none specified (default: 1 = Inbox)
- **Parsing Mode**: Choose `vikunja` or `todoist` syntax

### Multiple Instances

To create a second instance:

1. Copy `plugin.json` and generate a new unique UUID:
   ```bash
   python -c "import uuid; print(str(uuid.uuid4()))"
   ```

2. Update `plugin.json`:
   ```json
   {
     "ID": "<new-uuid>",
     "ActionKeywords": ["vk2"],
     "Name": "Vikunja (Work)",
     ...
   }
   ```

3. Restart Flow Launcher - the new instance will automatically:
   - Get its own settings folder
   - Inherit settings from the first instance
   - Allow independent configuration if needed

## Usage

### Vikunja Syntax (Default)

```
task title +project *label !priority
```

Examples:
- `Buy groceries +personal *shopping !2` - Medium priority task
- `Fix bug tomorrow` - Task due tomorrow
- `Meeting next monday +work` - Work task for next Monday

### Todoist Syntax

Enable in settings, then use:

```
task title #project @label p1
```

Examples:
- `Buy groceries #personal @shopping p2`
- `Fix bug tomorrow`
- `Meeting next monday #work`

### Date Examples

- `today` - Due today
- `tomorrow` - Due tomorrow
- `next week` - Due in 7 days
- `monday` - Due next Monday
- `2024-12-25` - Due on specific date

## Architecture

### Multitenant Design

Settings are stored in a single `Settings.json` file with a per-instance configuration structure:

```json
{
  "configurations": {
    "plugin-id-1": {
      "serverUrl": "https://vikunja1.example.com",
      "apiToken": "token1",
      ...
    },
    "plugin-id-2": {
      "serverUrl": "https://vikunja2.example.com",
      "apiToken": "token2",
      ...
    }
  }
}
```

**Benefits**:
- No configuration conflicts between instances
- New instances inherit settings automatically
- Single settings file for all instances
- Easy migration from C# version

### File Structure

```
flowlauncher-vikunja-py/
├── plugin.json          # Plugin metadata
├── main.py             # Entry point & main plugin class
├── config.py           # Configuration management (multitenant)
├── vikunja_api.py      # Vikunja API client
├── task_parser.py      # Natural language parser
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Test the parser
python -c "from task_parser import TaskParser; print(TaskParser().parse('buy milk tomorrow +personal *shopping !2'))"
```

### Live Reload

After making changes:
1. Type `restart Flow Launcher` in Flow Launcher
2. Your changes are immediately applied

No compilation needed!

## Migration from C# Version

The settings format is compatible with the C# plugin:
- Automatically migrates old flat settings to multitenant format
- Old C# instances can coexist with new Python instances
- Settings are shared between both versions

## Troubleshooting

### Plugin not showing up

1. Check Flow Launcher logs: `%APPDATA%\Roaming\FlowLauncher\Logs\`
2. Ensure `plugin.json` has valid JSON syntax
3. Verify Python 3.11+ is installed and on PATH
4. Run `pip install -r requirements.txt` again

### Settings not saving

- Ensure `%APPDATA%\Roaming\FlowLauncher\Settings\Plugins\Vikunja\` directory exists
- Check file permissions
- Review Flow Launcher logs for errors

### Tasks not creating

- Verify server URL and API token are correct
- Test connection in settings dialog
- Check Vikunja server logs for API errors
- Ensure API token has required permissions (tasks: create, labels: create/read)

## Requirements

The Vikunja API token needs these permissions:
- `tasks: create` - Create new tasks
- `labels: create, read` - Create and read labels
- `projects: read` - List projects
- `tasks_labels: create` - Assign labels to tasks

## License

Same as original C# plugin

## Credits

- Original C# plugin by AntoineTA
- Python rewrite with native multitenant support
