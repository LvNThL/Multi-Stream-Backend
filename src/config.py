"""
Configuration module for Multi-Stream Operations

All sensitive values are loaded from environment variables.
Create a .env file or set system environment variables before running.
"""

import os

# Backend API settings
BACKEND_URL = os.getenv("BACKEND_URL", "https://multi-stream-backend.onrender.com")

# OBS WebSocket settings
OBS_HOST = os.getenv("OBS_HOST", "localhost")
OBS_PORT = int(os.getenv("OBS_PORT", "4455"))
OBS_PASSWORD = os.getenv("OBS_PASSWORD", "")

# =============================================================================
# TWITCH CONFIGURATION
# Get credentials from: https://dev.twitch.tv/console/apps
# =============================================================================
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID", "")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET", "")
TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN", "")
TWITCH_CHANNEL_ID = os.getenv("TWITCH_CHANNEL_ID", "")
TWITCH_STREAM_KEY = os.getenv("TWITCH_STREAM_KEY", "")

# =============================================================================
# YOUTUBE CONFIGURATION
# Get credentials from: https://console.cloud.google.com/
# Stream key from: YouTube Studio > Go Live > Stream Settings
# =============================================================================
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")
YOUTUBE_STREAM_KEY = os.getenv("YOUTUBE_STREAM_KEY", "")

# =============================================================================
# KICK CONFIGURATION
# Stream key from: Kick Dashboard > Settings > Stream Key
# =============================================================================
KICK_USERNAME = os.getenv("KICK_USERNAME", "")
KICK_STREAM_KEY = os.getenv("KICK_STREAM_KEY", "")

# =============================================================================
# GUI SETTINGS
# =============================================================================
WINDOW_TITLE = "Multi-Stream Operations"
WINDOW_SIZE = "1000x700"