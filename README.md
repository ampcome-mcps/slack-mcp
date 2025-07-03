# Slack MCP Server

A Model Context Protocol (MCP) server that provides seamless integration with Slack's API. This server enables AI assistants like Claude to interact with Slack workspaces, manage channels, send messages, and perform various Slack operations.

## Features

- **Channel Management**: List public channels and get channel information
- **Message Operations**: Post messages, reply to threads, and get message history
- **User Management**: List users and get detailed user profiles
- **Reactions**: Add emoji reactions to messages
- **Thread Support**: Get thread replies and post threaded responses
- **Pagination**: Support for paginated results across all list operations
- **Authentication**: Secure OAuth-based authentication via Nango

## Prerequisites

- Python 3.13+
- Slack Bot Token with appropriate permissions
- Slack Team ID
- Nango integration for credential management (optional)

## Installation

1. **Clone the repository** (or create the project structure):
```bash
mkdir slack-mcp-server
cd slack-mcp-server
```

2. **Create a virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -e .
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
NANGO_BASE_URL=https://api.nango.dev
NANGO_SECRET_KEY=your-nango-secret-key
NANGO_CONNECTION_ID=your-connection-id
NANGO_INTEGRATION_ID=slack
```

### Slack App Setup

1. **Create a Slack App** at [api.slack.com](https://api.slack.com/apps)
2. **Add Bot Token Scopes**:
   - `channels:read` - View basic information about public channels
   - `channels:history` - View messages in public channels
   - `chat:write` - Send messages as the bot
   - `reactions:write` - Add emoji reactions
   - `users:read` - View people in the workspace
   - `users:read.email` - View email addresses (if needed)
3. **Install the app** to your workspace
4. **Copy the Bot User OAuth Token** to your `.env` file

### Claude Desktop Configuration

Add this configuration to your Claude Desktop config file:

**Location**: 
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "slack": {
      "command": "uvx",
      "args": ["git+https://github.com/ampcome-mcps/slack-mcp.git"],
      "env": {
        "NANGO_BASE_URL": "NANGO BASE URL",
        "NANGO_SECRET_KEY":"ENTER YOUR NANAGO SECRET KEY",
        "NANGO_CONNECTION_ID":"ENTER NANGO CONNECTION ID",
        "NANGO_INTEGRATION_ID":"ENTER NANGO INTEGRATION ID"
      }
    }
  }
}
```

## Available Tools

The MCP server provides the following tools for Claude:

### Channel Operations
- `slack_list_channels` - List public channels with pagination
- `get_conversation_info` - Get detailed information about a specific channel

### Message Operations  
- `slack_post_message` - Post a new message to a channel
- `slack_reply_to_thread` - Reply to a specific message thread
- `slack_get_channel_history` - Get recent messages from a channel
- `slack_get_thread_replies` - Get all replies in a message thread

### User Operations
- `slack_get_users` - List all users in the workspace
- `slack_get_user_profile` - Get detailed profile information for a user

### Interaction Operations
- `slack_add_reaction` - Add emoji reactions to messages

## Usage Examples

Once configured with Claude, you can use natural language commands like:

- "List all the channels in our Slack workspace"
- "Post a message to the #general channel saying 'Hello team!'"
- "Get the recent messages from the #development channel"
- "Reply to that thread with 'Thanks for the update'"
- "Add a thumbs up reaction to that message"
- "Show me the user profile for John Doe"

## Running the Server Standalone

For testing or development purposes, you can run the server directly:

```bash
python main.py
```

The server will start and listen for MCP protocol messages via stdin/stdout.

## Project Structure

```
slack-mcp-server/
├── main.py              # Main MCP server implementation
├── pyproject.toml       # Project configuration and dependencies  
├── .env                 # Environment variables (create from template)
├── .env.example         # Environment variables template
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## Development

### Key Components

- **SlackClient**: Handles all Slack API interactions using httpx
- **MCP Server**: Implements the Model Context Protocol for tool exposure
- **Tool Definitions**: Structured schemas for all available Slack operations
- **Error Handling**: Comprehensive error handling and logging

### Adding New Tools

To add new Slack API functionality:

1. Add the method to the `SlackClient` class
2. Define the tool schema in the `TOOLS` list
3. Add the tool handler in the `call_tool` function

### Dependencies

- `httpx` - Async HTTP client for Slack API calls
- `mcp` - Model Context Protocol framework
- `python-dotenv` - Environment variable management

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify your `SLACK_BOT_TOKEN` is correct and has necessary scopes
2. **Channel Not Found**: Ensure the bot has access to the channel and it's not archived
3. **Permission Denied**: Check that your Slack app has the required OAuth scopes
4. **Rate Limiting**: The server handles Slack's rate limits automatically

### Debugging

The server logs debug information to stderr. Check the Claude Desktop logs or run the server directly to see detailed error messages.

## Security Notes

- Store sensitive tokens in environment variables, never in code
- Use `.gitignore` to prevent committing `.env` files
- Regularly rotate your Slack bot tokens
- Follow the principle of least privilege for OAuth scopes

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues related to:
- **Slack API**: Check the [Slack API documentation](https://api.slack.com/)
- **MCP Protocol**: See the [MCP specification](https://spec.modelcontextprotocol.io/)
- **This server**: Open an issue in the project repository