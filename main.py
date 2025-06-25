
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional, Sequence
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

# Load environment variables from .env file
load_dotenv()


class SlackClient:
    def __init__(self, bot_token: str, team_id: str):
        self.bot_headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json",
        }
        self.team_id = team_id

    async def get_channels(self, limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "types": "public_channel",
            "exclude_archived": "true",
            "limit": str(min(limit, 200)),
            "team_id": self.team_id,
        }
        
        if cursor:
            params["cursor"] = cursor
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://slack.com/api/conversations.list?{urlencode(params)}",
                headers=self.bot_headers,
            )
            return response.json()
        
    async def get_conversation_info(self, channel_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            params = {"channel": channel_id}
            
            response = await client.get(
                f"https://slack.com/api/conversations.info?{urlencode(params)}",
                headers=self.bot_headers
            )
            data = response.json()
            
            if data.get("ok") and data.get("channel") and not data["channel"].get("is_archived"):
                return data["channel"]

    async def post_message(self, channel_id: str, text: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers=self.bot_headers,
                json={
                    "channel": channel_id,
                    "text": text,
                },
            )
            return response.json()

    async def post_reply(self, channel_id: str, thread_ts: str, text: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/chat.postMessage",
                headers=self.bot_headers,
                json={
                    "channel": channel_id,
                    "thread_ts": thread_ts,
                    "text": text,
                },
            )
            return response.json()

    async def add_reaction(self, channel_id: str, timestamp: str, reaction: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/reactions.add",
                headers=self.bot_headers,
                json={
                    "channel": channel_id,
                    "timestamp": timestamp,
                    "name": reaction,
                },
            )
            return response.json()

    async def get_channel_history(self, channel_id: str, limit: int = 10) -> Dict[str, Any]:
        params = {
            "channel": channel_id,
            "limit": str(limit),
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://slack.com/api/conversations.history?{urlencode(params)}",
                headers=self.bot_headers,
            )
            return response.json()

    async def get_thread_replies(self, channel_id: str, thread_ts: str) -> Dict[str, Any]:
        params = {
            "channel": channel_id,
            "ts": thread_ts,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://slack.com/api/conversations.replies?{urlencode(params)}",
                headers=self.bot_headers,
            )
            return response.json()

    async def get_users(self, limit: int = 100, cursor: Optional[str] = None) -> Dict[str, Any]:
        params = {
            "limit": str(min(limit, 200)),
            "team_id": self.team_id,
        }
        
        if cursor:
            params["cursor"] = cursor
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://slack.com/api/users.list?{urlencode(params)}",
                headers=self.bot_headers,
            )
            return response.json()

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        params = {
            "user": user_id,
            "include_labels": "true",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://slack.com/api/users.profile.get?{urlencode(params)}",
                headers=self.bot_headers,
            )
            return response.json()


# Tool definitions
TOOLS = [
    Tool(
        name="slack_list_channels",
        description="List public or pre-defined channels in the workspace with pagination",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "number",
                    "description": "Maximum number of channels to return (default 100, max 200)",
                    "default": 100,
                },
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor for next page of results",
                },
            },
        },
    ),
    Tool(
        name="slack_post_message",
        description="Post a new message to a Slack channel",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "The ID of the channel to post to",
                },
                "text": {
                    "type": "string",
                    "description": "The message text to post",
                },
            },
            "required": ["channel_id", "text"],
        },
    ),
    Tool(
        name="slack_reply_to_thread",
        description="Reply to a specific message thread in Slack",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "The ID of the channel containing the thread",
                },
                "thread_ts": {
                    "type": "string",
                    "description": "The timestamp of the parent message in the format '1234567890.123456'. Timestamps in the format without the period can be converted by adding the period such that 6 numbers come after it.",
                },
                "text": {
                    "type": "string",
                    "description": "The reply text",
                },
            },
            "required": ["channel_id", "thread_ts", "text"],
        },
    ),
    Tool(
        name="slack_add_reaction",
        description="Add a reaction emoji to a message",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "The ID of the channel containing the message",
                },
                "timestamp": {
                    "type": "string",
                    "description": "The timestamp of the message to react to",
                },
                "reaction": {
                    "type": "string",
                    "description": "The name of the emoji reaction (without ::)",
                },
            },
            "required": ["channel_id", "timestamp", "reaction"],
        },
    ),
    Tool(
        name="slack_get_channel_history",
        description="Get recent messages from a channel",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "The ID of the channel",
                },
                "limit": {
                    "type": "number",
                    "description": "Number of messages to retrieve (default 10)",
                    "default": 10,
                },
            },
            "required": ["channel_id"],
        },
    ),
    Tool(
        name="slack_get_thread_replies",
        description="Get all replies in a message thread",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "The ID of the channel containing the thread",
                },
                "thread_ts": {
                    "type": "string",
                    "description": "The timestamp of the parent message in the format '1234567890.123456'. Timestamps in the format without the period can be converted by adding the period such that 6 numbers come after it.",
                },
            },
            "required": ["channel_id", "thread_ts"],
        },
    ),
    Tool(
        name="slack_get_users",
        description="Get a list of all users in the workspace with their basic profile information",
        inputSchema={
            "type": "object",
            "properties": {
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor for next page of results",
                },
                "limit": {
                    "type": "number",
                    "description": "Maximum number of users to return (default 100, max 200)",
                    "default": 100,
                },
            },
        },
    ),
    Tool(
        name="slack_get_user_profile",
        description="Get detailed profile information for a specific user",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "The ID of the user",
                },
            },
            "required": ["user_id"],
        },
    ),
    Tool(
        name="get_conversation_info",
        description="Get information about a specific conversation (channel or DM)",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "The ID of the channel or conversation",
                },
            },
            "required": ["channel_id"],
        },
    ),
]


async def nango_credentials(connection_id: str, integration_id: str) -> Dict[str, Any]:
    """Get credentials from Nango"""
    base_url = os.environ.get("NANGO_BASE_URL")
    secret_key = os.environ.get("NANGO_SECRET_KEY")
    
    url = f"{base_url}/connection/{connection_id}"
    params = {
        "provider_config_key": integration_id,
        "refresh_token": "true",
    }
    headers = {"Authorization": f"Bearer {secret_key}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, headers=headers,params=params,
        )
        response.raise_for_status()
        return response.json()




async def main():
    """Main function to run the Slack MCP server."""

    print(f"Starting Slack MCP Server v1.0.0 (MCP )...", file=sys.stderr)
    
    server = Server("Slack MCP Server")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        print("Received ListToolsRequest", file=sys.stderr)
        return TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        print(f"Received CallToolRequest: {name}", file=sys.stderr)
        credentials = await nango_credentials(
            connection_id=os.getenv("NANGO_CONNECTION_ID"),
            integration_id=os.getenv("NANGO_INTEGRATION_ID"),
        )
        bot_token = credentials.get("credentials", {}).get("access_token")
        team_id = credentials.get("connection_config", {}).get("team.id")
            
        slack_client = SlackClient(bot_token=bot_token, team_id=team_id)
        
        try:
            if name == "slack_list_channels":
                limit = arguments.get("limit", 100)
                cursor = arguments.get("cursor")
                response = await slack_client.get_channels(limit, cursor)
                return [TextContent(type="text", text=json.dumps(response))]

            elif name == "get_conversation_info":
                channel_id = arguments.get("channel_id")
                if not channel_id:
                    raise ValueError("Missing required argument: channel_id")
                response = await slack_client.get_conversation_info(channel_id)
                if response:
                    return [TextContent(type="text", text=json.dumps(response))]
                else:
                    return [TextContent(type="text", text=json.dumps({"error": "Channel not found or is archived"}))]

            elif name == "slack_post_message":
                channel_id = arguments.get("channel_id")
                text = arguments.get("text")
                if not channel_id or not text:
                    raise ValueError("Missing required arguments: channel_id and text")
                response = await slack_client.post_message(channel_id, text)
                return [TextContent(type="text", text=json.dumps(response))]

            elif name == "slack_reply_to_thread":
                channel_id = arguments.get("channel_id")
                thread_ts = arguments.get("thread_ts")
                text = arguments.get("text")
                if not channel_id or not thread_ts or not text:
                    raise ValueError("Missing required arguments: channel_id, thread_ts, and text")
                response = await slack_client.post_reply(channel_id, thread_ts, text)
                return [TextContent(type="text", text=json.dumps(response))]

            elif name == "slack_add_reaction":
                channel_id = arguments.get("channel_id")
                timestamp = arguments.get("timestamp")
                reaction = arguments.get("reaction")
                if not channel_id or not timestamp or not reaction:
                    raise ValueError("Missing required arguments: channel_id, timestamp, and reaction")
                response = await slack_client.add_reaction(channel_id, timestamp, reaction)
                return [TextContent(type="text", text=json.dumps(response))]

            elif name == "slack_get_channel_history":
                channel_id = arguments.get("channel_id")
                if not channel_id:
                    raise ValueError("Missing required argument: channel_id")
                limit = arguments.get("limit", 10)
                response = await slack_client.get_channel_history(channel_id, limit)
                return [TextContent(type="text", text=json.dumps(response))]

            elif name == "slack_get_thread_replies":
                channel_id = arguments.get("channel_id")
                thread_ts = arguments.get("thread_ts")
                if not channel_id or not thread_ts:
                    raise ValueError("Missing required arguments: channel_id and thread_ts")
                response = await slack_client.get_thread_replies(channel_id, thread_ts)
                return [TextContent(type="text", text=json.dumps(response))]

            elif name == "slack_get_users":
                limit = arguments.get("limit", 100)
                cursor = arguments.get("cursor")
                response = await slack_client.get_users(limit, cursor)
                return [TextContent(type="text", text=json.dumps(response))]

            elif name == "slack_get_user_profile":
                user_id = arguments.get("user_id")
                if not user_id:
                    raise ValueError("Missing required argument: user_id")
                response = await slack_client.get_user_profile(user_id)
                return [TextContent(type="text", text=json.dumps(response))]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as error:
            print(f"Error executing tool: {error}", file=sys.stderr)
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(error)})
            )]

    async with stdio_server() as (read_stream, write_stream):
        print("Connecting server to transport...", file=sys.stderr)
        await server.run(read_stream, write_stream, server.create_initialization_options())


def run():
    """Run the main function in an asyncio event loop."""
    try:
        asyncio.run(main())
    except Exception as error:
        print(f"Fatal error in main(): {error}", file=sys.stderr)
        sys.exit(1)