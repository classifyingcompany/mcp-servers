from typing import Any, List
import httpx
from mcp.server.fastmcp import FastMCP
import os

# Initialize FastMCP server
mcp = FastMCP("slack")

# Get Slack token from environment
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_API_BASE = "https://slack.com/api"

async def make_slack_request(endpoint: str, method: str = "GET", data: dict = None) -> dict[str, Any] | None:
    """Make a request to Slack API with proper error handling."""
    if not SLACK_TOKEN:
        return {"error": "SLACK_BOT_TOKEN environment variable not set"}
    
    headers = {
        "Authorization": f"Bearer {SLACK_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{SLACK_API_BASE}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=data or {})
            else:
                response = await client.post(url, headers=headers, json=data or {})
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@mcp.tool()
async def list_channels() -> str:
    """List all channels in the Slack workspace."""
    try:
        data = await make_slack_request("conversations.list", "GET", {"types": "public_channel,private_channel"})
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not data.get("ok"):
            return f"Slack API error: {data.get('error', 'Unknown error')}"
        
        channels = data.get("channels", [])
        if not channels:
            return "No channels found."
        
        channel_list = []
        for channel in channels:
            channel_info = f"""
Name: #{channel['name']}
ID: {channel['id']}
Purpose: {channel.get('purpose', {}).get('value', 'No purpose set')}
Members: {channel.get('num_members', 'Unknown')}
Private: {channel.get('is_private', False)}
"""
            channel_list.append(channel_info)
        
        return "\n---\n".join(channel_list)
    
    except Exception as e:
        return f"Error listing channels: {str(e)}"

@mcp.tool()
async def get_channel_history(channel_id: str, limit: int = 10) -> str:
    """Get recent messages from a Slack channel.
    
    Args:
        channel_id: The ID of the channel
        limit: Number of messages to retrieve (default: 10)
    """
    try:
        data = await make_slack_request("conversations.history", "GET", {
            "channel": channel_id,
            "limit": limit
        })
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not data.get("ok"):
            return f"Slack API error: {data.get('error', 'Unknown error')}"
        
        messages = data.get("messages", [])
        if not messages:
            return "No messages found in channel."
        
        message_list = []
        for msg in messages:
            user_id = msg.get("user", "Unknown")
            text = msg.get("text", "")
            timestamp = msg.get("ts", "")
            
            # Get user info
            user_data = await make_slack_request("users.info", "GET", {"user": user_id})
            username = user_data.get("user", {}).get("name", user_id) if user_data.get("ok") else user_id
            
            message_list.append(f"""
User: {username}
Time: {timestamp}
Message: {text}
""")
        
        return f"Recent messages in channel:\n" + "\n---\n".join(message_list)
    
    except Exception as e:
        return f"Error getting channel history: {str(e)}"

@mcp.tool()
async def send_message(channel: str, text: str) -> str:
    """Send a message to a Slack channel.
    
    Args:
        channel: Channel ID or name (e.g., '#general' or 'C1234567890')
        text: Message text to send
    """
    try:
        data = await make_slack_request("chat.postMessage", "POST", {
            "channel": channel,
            "text": text
        })
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not data.get("ok"):
            return f"Slack API error: {data.get('error', 'Unknown error')}"
        
        return f"Message sent successfully to {channel}. Message timestamp: {data.get('ts')}"
    
    except Exception as e:
        return f"Error sending message: {str(e)}"

@mcp.tool()
async def search_messages(query: str, count: int = 20) -> str:
    """Search for messages in Slack.
    
    Args:
        query: Search query
        count: Number of results to return (default: 20)
    """
    try:
        data = await make_slack_request("search.messages", "GET", {
            "query": query,
            "count": count
        })
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not data.get("ok"):
            return f"Slack API error: {data.get('error', 'Unknown error')}"
        
        messages = data.get("messages", {}).get("matches", [])
        if not messages:
            return f"No messages found for query: {query}"
        
        search_results = []
        for msg in messages:
            username = msg.get("username", "Unknown")
            text = msg.get("text", "")
            channel_name = msg.get("channel", {}).get("name", "Unknown")
            timestamp = msg.get("ts", "")
            
            search_results.append(f"""
User: {username}
Channel: #{channel_name}
Time: {timestamp}
Message: {text}
""")
        
        return f"Found {len(messages)} messages:\n" + "\n---\n".join(search_results)
    
    except Exception as e:
        return f"Error searching messages: {str(e)}"

@mcp.tool()
async def get_user_info(user_id: str) -> str:
    """Get information about a Slack user.
    
    Args:
        user_id: The user ID to get info for
    """
    try:
        data = await make_slack_request("users.info", "GET", {"user": user_id})
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not data.get("ok"):
            return f"Slack API error: {data.get('error', 'Unknown error')}"
        
        user = data.get("user", {})
        profile = user.get("profile", {})
        
        return f"""
Name: {user.get('name', 'Unknown')}
Real Name: {profile.get('real_name', 'Unknown')}
Display Name: {profile.get('display_name', 'Unknown')}
Email: {profile.get('email', 'Not available')}
Status: {profile.get('status_text', 'No status')}
Timezone: {user.get('tz', 'Unknown')}
Is Admin: {user.get('is_admin', False)}
Is Bot: {user.get('is_bot', False)}
"""
    
    except Exception as e:
        return f"Error getting user info: {str(e)}"

@mcp.tool()
async def list_users() -> str:
    """List all users in the Slack workspace."""
    try:
        data = await make_slack_request("users.list", "GET")
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not data.get("ok"):
            return f"Slack API error: {data.get('error', 'Unknown error')}"
        
        members = data.get("members", [])
        if not members:
            return "No users found."
        
        user_list = []
        for user in members:
            if not user.get("deleted", False) and not user.get("is_bot", False):
                profile = user.get("profile", {})
                user_info = f"""
Name: {user.get('name', 'Unknown')}
Real Name: {profile.get('real_name', 'Unknown')}
ID: {user.get('id', 'Unknown')}
Status: {profile.get('status_text', 'No status')}
"""
                user_list.append(user_info)
        
        return "\n---\n".join(user_list)
    
    except Exception as e:
        return f"Error listing users: {str(e)}"

def main():
    """Initialize and run the Slack MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()