"""
Chat Manager for multi-platform chat integration.

Handles sending and receiving chat messages across streaming platforms.
"""

import socket
import threading
import requests
from typing import List, Dict, Optional, Callable
from config import BACKEND_URL, TWITCH_ACCESS_TOKEN, TWITCH_CHANNEL_ID


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
            # YouTube chat will be implemented in task 6
            print("YouTube chat: Not yet implemented")
            return False
        elif platform == "kick":
            # Kick chat will be implemented in task 7
            print("Kick chat: Not yet implemented")
            return False
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