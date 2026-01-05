"""
Chat Manager for multi-platform chat integration.

Handles sending and receiving chat messages across streaming platforms.
"""

import requests
from typing import List, Dict, Optional
from config import BACKEND_URL


class ChatManager:
    """Manages chat connections and messages for multiple platforms."""

    def __init__(self):
        self.connections: Dict[str, object] = {}
        self.backend_url = BACKEND_URL

    def send_message_sync(self, platform: str, message: str) -> bool:
        """Send a chat message synchronously.

        Args:
            platform: Target platform ('all', 'twitch', 'youtube', 'kick')
            message: Message content to send

        Returns:
            True if successful, False otherwise
        """
        data = {"platform": platform, "message": message}
        try:
            response = requests.post(
                f"{self.backend_url}/chat/send",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Failed to send chat message: {e}")
            return False

    def get_messages(self, limit: int = 50) -> List[Dict]:
        """Fetch recent chat messages from backend.

        Args:
            limit: Maximum number of messages to retrieve

        Returns:
            List of message dictionaries
        """
        try:
            response = requests.get(
                f"{self.backend_url}/chat/messages",
                params={"limit": limit},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to get chat messages: {e}")
            return []

    def connect_platform(self, platform: str) -> bool:
        """Connect to a specific platform's chat.

        Args:
            platform: Platform to connect ('twitch', 'youtube', 'kick')

        Returns:
            True if successful, False otherwise
        """
        # TODO: Implement platform-specific chat connections
        # - Twitch: IRC via twitchio
        # - YouTube: YouTube Live Streaming API
        # - Kick: WebSocket or unofficial API
        print(f"Chat connection to {platform} not yet implemented")
        return False

    def disconnect_all(self):
        """Disconnect from all platform chats."""
        for platform, connection in self.connections.items():
            try:
                if hasattr(connection, 'close'):
                    connection.close()
            except Exception as e:
                print(f"Error disconnecting from {platform}: {e}")
        self.connections.clear()