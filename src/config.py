"""
Configuration module for Multi-Stream Operations

All sensitive values are loaded from environment variables or settings file.
Settings are stored in user's app data directory for persistence.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

# App data directory for settings persistence
APP_NAME = "MultiStreamOperations"
if os.name == 'nt':  # Windows
    APP_DATA_DIR = Path(os.getenv('APPDATA', '')) / APP_NAME
else:  # macOS/Linux
    APP_DATA_DIR = Path.home() / '.config' / APP_NAME

SETTINGS_FILE = APP_DATA_DIR / 'settings.json'


def load_settings() -> Dict[str, Any]:
    """Load settings from the settings file."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_settings(settings: Dict[str, Any]) -> bool:
    """Save settings to the settings file.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except IOError as e:
        print(f"Failed to save settings: {e}")
        return False


def get_setting(key: str, default: str = "") -> str:
    """Get a setting value, checking settings file first, then env vars."""
    settings = load_settings()
    # Settings file takes priority, then environment variable, then default
    return settings.get(key, os.getenv(key.upper(), default))


# Backend API settings
BACKEND_URL = get_setting("backend_url", "https://multi-stream-backend.onrender.com")

# OBS WebSocket settings
OBS_HOST = get_setting("obs_host", "localhost")
OBS_PORT = int(get_setting("obs_port", "4455"))
OBS_PASSWORD = get_setting("obs_password", "")

# =============================================================================
# TWITCH CONFIGURATION
# Get credentials from: https://dev.twitch.tv/console/apps
# =============================================================================
TWITCH_CLIENT_ID = get_setting("twitch_client_id", "")
TWITCH_CLIENT_SECRET = get_setting("twitch_client_secret", "")
TWITCH_ACCESS_TOKEN = get_setting("twitch_access_token", "")
TWITCH_CHANNEL_ID = get_setting("twitch_channel_id", "")
TWITCH_STREAM_KEY = get_setting("twitch_stream_key", "")

# =============================================================================
# YOUTUBE CONFIGURATION
# Get credentials from: https://console.cloud.google.com/
# Stream key from: YouTube Studio > Go Live > Stream Settings
# =============================================================================
YOUTUBE_API_KEY = get_setting("youtube_api_key", "")
YOUTUBE_CHANNEL_ID = get_setting("youtube_channel_id", "")
YOUTUBE_STREAM_KEY = get_setting("youtube_stream_key", "")

# =============================================================================
# KICK CONFIGURATION
# Stream key from: Kick Dashboard > Settings > Stream Key
# =============================================================================
KICK_USERNAME = get_setting("kick_username", "")
KICK_STREAM_KEY = get_setting("kick_stream_key", "")

# =============================================================================
# GUI SETTINGS
# =============================================================================
WINDOW_TITLE = "Multi-Stream Operations"
WINDOW_SIZE = "1000x700"