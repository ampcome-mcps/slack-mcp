# Slack MPC Integration

This project implements a Slack Multi-Party Chat (MPC) integration using the MCP (Multi-Party Chat Protocol) framework. It allows for seamless integration with Slack's API to manage channels, messages, and user interactions in a multi-party chat environment.

## Features

- Slack channel management
- Real-time message handling
- User authentication and authorization
- Environment-based configuration
- Async HTTP client integration

## Prerequisites

- Python 3.8+
- Slack Bot Token
- Slack Team ID

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

## Configuration

Copy the example environment file and configure your settings:
```bash
cp .env.example .env
```

Edit the `.env` file with your Slack credentials:
- `SLACK_BOT_TOKEN`: Your Slack bot token
- `SLACK_TEAM_ID`: Your Slack team ID
- Other required environment variables

## Running the Application

To run the application:
```bash
python main.py
```

## Project Structure

- `main.py`: Main application file containing the Slack client implementation and MPC server
- `.env`: Environment configuration file
- `.env.example`: Template for environment variables
- `pyproject.toml`: Project configuration
- `.gitignore`: Git ignore rules

## Development

The project uses MCP framework for handling multi-party chat interactions and httpx for making asynchronous HTTP requests to the Slack API.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.