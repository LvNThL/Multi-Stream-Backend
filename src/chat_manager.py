"""
Chat Manager for multi-platform chat integration.

Handles sending and receiving chat messages across streaming platforms.
"""

import socket
import threading
import requests
import time
import json
from typing import List, Dict, Optional, Callable
from config import (
    BACKEND_URL, TWITCH_ACCESS_TOKEN, TWITCH_CHANNEL_ID,
    YOUTUBE_ACCESS_TOKEN, YOUTUBE_CHANNEL_ID,
    KICK_USERNAME
)


class TwitchIRC:
    """Twitch IRC client for chat integration."""

    SERVER = "irc.chat.twitch.tv"
    PORT = 6667

    def __init__(self, access_token: str, channel: str,
                 on_message: Callable[[str, str, str], None] = None):
        """Initialize Twitch IRC client.

        Args:
            access_token: OAuth token for authentication
            channel: Channel name to join (without #)
            on_message: Callback for received messages (username, message, channel)
        """
        self.access_token = access_token
        self.channel = channel.lower().lstrip('#')
        self.on_message = on_message
        self._socket: Optional[socket.socket] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.connected = False

    def connect(self) -> bool:
        """Connect to Twitch IRC server."""
        if not self.access_token or not self.channel:
            print("Twitch IRC: Missing access token or channel")
            return False

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.SERVER, self.PORT))
            self._socket.settimeout(1.0)

            # Authenticate
            self._send(f"PASS oauth:{self.access_token}")
            self._send(f"NICK {self.channel}")  # Nick can be anything with OAuth
            self._send(f"JOIN #{self.channel}")

            # Request capabilities for better message parsing
            self._send("CAP REQ :twitch.tv/tags twitch.tv/commands")

            self._running = True
            self.connected = True
            self._thread = threading.Thread(target=self._receive_loop, daemon=True)
            self._thread.start()

            print(f"Twitch IRC: Connected to #{self.channel}")
            return True
        except Exception as e:
            print(f"Twitch IRC: Connection failed - {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from Twitch IRC."""
        self._running = False
        self.connected = False
        if self._socket:
            try:
                self._send(f"PART #{self.channel}")
                self._socket.close()
            except Exception:
                pass
            self._socket = None

    def send_message(self, message: str) -> bool:
        """Send a message to the channel."""
        if not self.connected or not self._socket:
            return False
        try:
            self._send(f"PRIVMSG #{self.channel} :{message}")
            return True
        except Exception as e:
            print(f"Twitch IRC: Failed to send - {e}")
            return False

    def _send(self, message: str):
        """Send raw IRC message."""
        if self._socket:
            self._socket.send(f"{message}\r\n".encode('utf-8'))

    def _receive_loop(self):
        """Background loop to receive messages."""
        buffer = ""
        while self._running and self._socket:
            try:
                data = self._socket.recv(2048).decode('utf-8')
                if not data:
                    continue
                buffer += data
                while "\r\n" in buffer:
                    line, buffer = buffer.split("\r\n", 1)
                    self._handle_message(line)
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    print(f"Twitch IRC: Receive error - {e}")
                break

    def _handle_message(self, line: str):
        """Parse and handle an IRC message."""
        # Respond to PING to stay connected
        if line.startswith("PING"):
            self._send(f"PONG {line[5:]}")
            return

        # Parse PRIVMSG for chat messages
        if "PRIVMSG" in line:
            try:
                # Parse username from :username!username@username.tmi.twitch.tv
                prefix_end = line.index(' ')
                prefix = line[1:prefix_end]
                username = prefix.split('!')[0]

                # Parse message content after :
                msg_start = line.index(':', 1) + 1
                message = line[msg_start:]

                if self.on_message:
                    self.on_message(username, message, self.channel)
            except (ValueError, IndexError):
                pass


class YouTubeLiveChat:
    """YouTube Live Chat API client."""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, access_token: str, channel_id: str,
                 on_message: Callable[[str, str, str], None] = None):
        """Initialize YouTube Live Chat client.

        Args:
            access_token: OAuth token for authentication
            channel_id: YouTube channel ID
            on_message: Callback for received messages (username, message, channel)
        """
        self.access_token = access_token
        self.channel_id = channel_id
        self.on_message = on_message
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._live_chat_id: Optional[str] = None
        self._next_page_token: Optional[str] = None
        self.connected = False

    def connect(self) -> bool:
        """Connect to YouTube Live Chat by finding active broadcast."""
        if not self.access_token or not self.channel_id:
            print("YouTube Chat: Missing access token or channel ID")
            return False

        # Find active live broadcast
        self._live_chat_id = self._get_live_chat_id()
        if not self._live_chat_id:
            print("YouTube Chat: No active live broadcast found")
            return False

        self._running = True
        self.connected = True
        self._thread = threading.Thread(target=self._poll_messages, daemon=True)
        self._thread.start()

        print(f"YouTube Chat: Connected to live chat")
        return True

    def disconnect(self):
        """Disconnect from YouTube Live Chat."""
        self._running = False
        self.connected = False
        self._live_chat_id = None

    def send_message(self, message: str) -> bool:
        """Send a message to YouTube Live Chat."""
        if not self.connected or not self._live_chat_id:
            return False

        try:
            response = requests.post(
                f"{self.BASE_URL}/liveChat/messages",
                params={"part": "snippet"},
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={
                    "snippet": {
                        "liveChatId": self._live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {"messageText": message}
                    }
                },
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"YouTube Chat: Failed to send - {e}")
            return False

    def _get_live_chat_id(self) -> Optional[str]:
        """Get the live chat ID for the active broadcast."""
        try:
            # First, find the active live broadcast
            response = requests.get(
                f"{self.BASE_URL}/liveBroadcasts",
                params={
                    "part": "snippet",
                    "broadcastStatus": "active",
                    "broadcastType": "all"
                },
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            response.raise_for_status()
            items = response.json().get("items", [])

            if items:
                return items[0]["snippet"].get("liveChatId")
            return None
        except Exception as e:
            print(f"YouTube Chat: Failed to get live chat ID - {e}")
            return None

    def _poll_messages(self):
        """Poll for new messages in a background thread."""
        poll_interval = 5  # seconds

        while self._running and self._live_chat_id:
            try:
                params = {
                    "liveChatId": self._live_chat_id,
                    "part": "snippet,authorDetails"
                }
                if self._next_page_token:
                    params["pageToken"] = self._next_page_token

                response = requests.get(
                    f"{self.BASE_URL}/liveChat/messages",
                    params=params,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()

                self._next_page_token = data.get("nextPageToken")
                poll_interval = data.get("pollingIntervalMillis", 5000) / 1000

                for item in data.get("items", []):
                    snippet = item.get("snippet", {})
                    author = item.get("authorDetails", {})

                    if snippet.get("type") == "textMessageEvent":
                        username = author.get("displayName", "Unknown")
                        message = snippet.get("textMessageDetails", {}).get("messageText", "")
                        if self.on_message and message:
                            self.on_message(username, message, self.channel_id)

            except Exception as e:
                print(f"YouTube Chat: Poll error - {e}")

            time.sleep(poll_interval)


class KickChat:
    """Kick chat client using their public API.
    
    Note: Kick uses Pusher WebSockets for real-time chat.
    This implementation polls the public API as a fallback.
    """

    BASE_URL = "https://kick.com/api/v2"

    def __init__(self, username: str,
                 on_message: Callable[[str, str, str], None] = None):
        """Initialize Kick chat client.

        Args:
            username: Kick channel username
            on_message: Callback for received messages (username, message, channel)
        """
        self.username = username.lower()
        self.on_message = on_message
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._chatroom_id: Optional[int] = None
        self._last_message_id: int = 0
        self.connected = False

    def connect(self) -> bool:
        """Connect to Kick chat by getting channel info."""
        if not self.username:
            print("Kick Chat: Missing username")
            return False

        # Get channel info to find chatroom ID
        try:
            response = requests.get(
                f"{self.BASE_URL}/channels/{self.username}",
                timeout=10
            )
            if response.status_code != 200:
                print(f"Kick Chat: Channel not found - {self.username}")
                return False

            data = response.json()
            self._chatroom_id = data.get("chatroom", {}).get("id")

            if not self._chatroom_id:
                print("Kick Chat: Could not find chatroom ID")
                return False

            self._running = True
            self.connected = True
            self._thread = threading.Thread(target=self._poll_messages, daemon=True)
            self._thread.start()

            print(f"Kick Chat: Connected to {self.username}")
            return True
        except Exception as e:
            print(f"Kick Chat: Connection failed - {e}")
            return False

    def disconnect(self):
        """Disconnect from Kick chat."""
        self._running = False
        self.connected = False

    def send_message(self, message: str) -> bool:
        """Send a message to Kick chat.
        
        Note: Sending messages requires authentication which Kick
        doesn't publicly document. This is a placeholder.
        """
        print("Kick Chat: Sending messages not supported (requires auth)")
        return False

    def _poll_messages(self):
        """Poll for new messages."""
        poll_interval = 3  # seconds

        while self._running and self._chatroom_id:
            try:
                response = requests.get(
                    f"{self.BASE_URL}/channels/{self.username}/messages",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    messages = data.get("data", {}).get("messages", [])

                    for msg in messages:
                        msg_id = msg.get("id", 0)
                        if msg_id > self._last_message_id:
                            self._last_message_id = msg_id
                            username = msg.get("sender", {}).get("username", "Unknown")
                            content = msg.get("content", "")
                            if self.on_message and content:
                                self.on_message(username, content, self.username)

            except Exception as e:
                print(f"Kick Chat: Poll error - {e}")

            time.sleep(poll_interval)


class ChatManager:
    """Manages chat connections and messages for multiple platforms."""

    def __init__(self):
        self.connections: Dict[str, object] = {}
        self.backend_url = BACKEND_URL
        self._message_callbacks: List[Callable[[str, str, str, str], None]] = []

    def add_message_callback(self, callback: Callable[[str, str, str, str], None]):
        """Add a callback for incoming messages.

        Args:
            callback: Function(platform, username, message, channel)
        """
        self._message_callbacks.append(callback)

    def _notify_message(self, platform: str, username: str, message: str, channel: str):
        """Notify all callbacks of a new message."""
        for callback in self._message_callbacks:
            try:
                callback(platform, username, message, channel)
            except Exception as e:
                print(f"Chat callback error: {e}")

    def connect_twitch(self, access_token: str = None, channel: str = None) -> bool:
        """Connect to Twitch IRC chat.

        Args:
            access_token: OAuth token (uses config if not provided)
            channel: Channel name (uses config if not provided)

        Returns:
            True if connected successfully
        """
        token = access_token or TWITCH_ACCESS_TOKEN
        chan = channel or TWITCH_CHANNEL_ID

        if not token or not chan:
            print("Twitch chat: Missing credentials")
            return False

        def on_twitch_message(username: str, message: str, channel: str):
            self._notify_message("twitch", username, message, channel)

        irc = TwitchIRC(token, chan, on_message=on_twitch_message)
        if irc.connect():
            self.connections["twitch"] = irc
            return True
        return False

    def connect_youtube(self, access_token: str = None, channel_id: str = None) -> bool:
        """Connect to YouTube Live Chat.

        Args:
            access_token: OAuth token (uses config if not provided)
            channel_id: Channel ID (uses config if not provided)

        Returns:
            True if connected successfully
        """
        token = access_token or YOUTUBE_ACCESS_TOKEN
        chan = channel_id or YOUTUBE_CHANNEL_ID

        if not token or not chan:
            print("YouTube chat: Missing credentials")
            return False

        def on_youtube_message(username: str, message: str, channel: str):
            self._notify_message("youtube", username, message, channel)

        chat = YouTubeLiveChat(token, chan, on_message=on_youtube_message)
        if chat.connect():
            self.connections["youtube"] = chat
            return True
        return False

    def connect_kick(self, username: str = None) -> bool:
        """Connect to Kick chat.

        Args:
            username: Kick username (uses config if not provided)

        Returns:
            True if connected successfully
        """
        user = username or KICK_USERNAME

        if not user:
            print("Kick chat: Missing username")
            return False

        def on_kick_message(username: str, message: str, channel: str):
            self._notify_message("kick", username, message, channel)

        chat = KickChat(user, on_message=on_kick_message)
        if chat.connect():
            self.connections["kick"] = chat
            return True
        return False

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
        platform = platform.lower()
        if platform == "twitch":
            return self.connect_twitch()
        elif platform == "youtube":
            return self.connect_youtube()
        elif platform == "kick":
            return self.connect_kick()
        else:
            print(f"Unknown platform: {platform}")
            return False

    def send_to_platform(self, platform: str, message: str) -> bool:
        """Send a message to a specific platform chat.

        Args:
            platform: Target platform
            message: Message to send

        Returns:
            True if sent successfully
        """
        conn = self.connections.get(platform.lower())
        if not conn:
            return False

        if platform.lower() == "twitch" and isinstance(conn, TwitchIRC):
            return conn.send_message(message)
        elif platform.lower() == "youtube" and isinstance(conn, YouTubeLiveChat):
            return conn.send_message(message)
        elif platform.lower() == "kick" and isinstance(conn, KickChat):
            return conn.send_message(message)

        return False

    def send_to_all(self, message: str) -> Dict[str, bool]:
        """Send a message to all connected platforms.

        Returns:
            Dict mapping platform names to success status
        """
        results = {}
        for platform in self.connections:
            results[platform] = self.send_to_platform(platform, message)
        return results

    def is_connected(self, platform: str) -> bool:
        """Check if connected to a platform's chat."""
        conn = self.connections.get(platform.lower())
        if conn and hasattr(conn, 'connected'):
            return conn.connected
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