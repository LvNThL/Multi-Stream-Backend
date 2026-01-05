"""
Chat Manager for multi-platform chat
"""

import asyncio
import requests
from config import BACKEND_URL

class ChatManager:
    def __init__(self):
        self.connections = {}
        self.backend_url = BACKEND_URL

    async def connect_all(self):
        # TODO: Connect to all platforms' chat
        pass

    async def send_message(self, platform, message):
        # Send message to backend
        data = {"platform": platform, "message": message}
        try:
            response = requests.post(f"{self.backend_url}/chat/send", json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send chat message: {e}")
        # TODO: Also send to specific platform

    async def receive_messages(self):
        # TODO: Yield messages from all platforms
        pass

    def get_messages_from_backend(self):
        try:
            response = requests.get(f"{self.backend_url}/chat/messages")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to get chat messages: {e}")
            return []