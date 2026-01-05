"""
Configuration module for Multi-Stream Operations
"""

import os

# Backend API settings
BACKEND_URL = os.getenv("BACKEND_URL", "https://your-render-app.onrender.com")  # Update with actual Render URL

# OBS WebSocket settings
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = os.getenv("OBS_PASSWORD", "")

# Platform API keys (set via environment variables)
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID", "")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET", "")
TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN", "")
TWITCH_CHANNEL_ID = os.getenv("TWITCH_CHANNEL_ID", "")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")

# Kick settings (if API available)
KICK_USERNAME = os.getenv("KICK_USERNAME", "")
KICK_PASSWORD = os.getenv("KICK_PASSWORD", "")

# GUI settings
WINDOW_TITLE = "Multi-Stream Operations"
WINDOW_SIZE = "800x600"