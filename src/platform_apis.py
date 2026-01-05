"""
Platform APIs module for streaming platform integrations.

Provides unified interfaces for Twitch, YouTube, Kick APIs,
with a registry system to easily add new platforms.
"""

import requests
import webbrowser
import urllib.parse
import threading
import http.server
import socketserver
from typing import Optional, Dict, Type, List, Callable
from dataclasses import dataclass
from config import (
    TWITCH_CLIENT_ID, TWITCH_ACCESS_TOKEN, TWITCH_CHANNEL_ID,
    TWITCH_STREAM_KEY, TWITCH_CLIENT_SECRET,
    YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID, YOUTUBE_STREAM_KEY,
    KICK_USERNAME, KICK_STREAM_KEY
)


# OAuth callback port
OAUTH_CALLBACK_PORT = 3000


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for OAuth callbacks."""

    def __init__(self, *args, callback: Callable[[Dict], None] = None, **kwargs):
        self.callback = callback
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # Send response to browser
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if 'code' in params:
            self.wfile.write(b"""
                <html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>Authorization Successful!</h1>
                <p>You can close this window and return to the app.</p>
                </body></html>
            """)
            if self.callback:
                self.callback({'code': params['code'][0]})
        elif 'error' in params:
            self.wfile.write(f"""
                <html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>Authorization Failed</h1>
                <p>Error: {params.get('error_description', ['Unknown error'])[0]}</p>
                </body></html>
            """.encode())
            if self.callback:
                self.callback({'error': params.get('error', ['unknown'])[0]})

    def log_message(self, format, *args):
        """Suppress logging."""
        pass


class TwitchOAuth:
    """Handle Twitch OAuth authentication flow."""

    AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
    TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    SCOPES = [
        "channel:read:subscriptions",
        "channel:read:stream_key",
        "chat:read",
        "chat:edit",
        "user:read:email"
    ]

    def __init__(self, client_id: str, client_secret: str,
                 on_success: Callable[[str], None] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.on_success = on_success
        self.redirect_uri = f"http://localhost:{OAUTH_CALLBACK_PORT}/callback"
        self._server = None
        self._auth_code = None

    def start_auth_flow(self) -> bool:
        """Start the OAuth flow by opening the browser."""
        if not self.client_id or not self.client_secret:
            print("Twitch Client ID and Secret required for OAuth")
            return False

        # Build authorization URL
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.SCOPES)
        }
        auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

        # Start callback server in background
        self._start_callback_server()

        # Open browser
        webbrowser.open(auth_url)
        return True

    def _start_callback_server(self):
        """Start a local server to receive the OAuth callback."""
        def handler(*args, **kwargs):
            return OAuthCallbackHandler(*args, callback=self._handle_callback, **kwargs)

        def run_server():
            with socketserver.TCPServer(("", OAUTH_CALLBACK_PORT), handler) as httpd:
                self._server = httpd
                httpd.handle_request()  # Handle one request then stop

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

    def _handle_callback(self, params: Dict):
        """Handle the OAuth callback."""
        if 'code' in params:
            self._auth_code = params['code']
            token = self._exchange_code_for_token(params['code'])
            if token and self.on_success:
                self.on_success(token)

    def _exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token."""
        try:
            response = requests.post(self.TOKEN_URL, data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except Exception as e:
            print(f"Failed to exchange code for token: {e}")
            return None


class YouTubeOAuth:
    """Handle YouTube/Google OAuth authentication flow."""

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    SCOPES = [
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.force-ssl"  # For live chat
    ]

    def __init__(self, client_id: str, client_secret: str,
                 on_success: Callable[[str], None] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.on_success = on_success
        self.redirect_uri = f"http://localhost:{OAUTH_CALLBACK_PORT}/callback"
        self._server = None

    def start_auth_flow(self) -> bool:
        """Start the OAuth flow by opening the browser."""
        if not self.client_id or not self.client_secret:
            print("YouTube Client ID and Secret required for OAuth")
            return False

        # Build authorization URL
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.SCOPES),
            'access_type': 'offline',
            'prompt': 'consent'
        }
        auth_url = f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

        # Start callback server in background
        self._start_callback_server()

        # Open browser
        webbrowser.open(auth_url)
        return True

    def _start_callback_server(self):
        """Start a local server to receive the OAuth callback."""
        def handler(*args, **kwargs):
            return OAuthCallbackHandler(*args, callback=self._handle_callback, **kwargs)

        def run_server():
            with socketserver.TCPServer(("", OAUTH_CALLBACK_PORT), handler) as httpd:
                self._server = httpd
                httpd.handle_request()

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

    def _handle_callback(self, params: Dict):
        """Handle the OAuth callback."""
        if 'code' in params:
            token = self._exchange_code_for_token(params['code'])
            if token and self.on_success:
                self.on_success(token)

    def _exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token."""
        try:
            response = requests.post(self.TOKEN_URL, data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except Exception as e:
            print(f"Failed to exchange code for token: {e}")
            return None


@dataclass
class StreamConfig:
    """Configuration for a streaming platform's RTMP output."""
    platform_name: str
    rtmp_url: str
    stream_key: str
    enabled: bool = True

    @property
    def full_rtmp_url(self) -> str:
        """Get full RTMP URL with stream key."""
        return f"{self.rtmp_url}/{self.stream_key}"


class BasePlatformAPI:
    """Base class for platform API integrations.
    
    To add a new platform:
    1. Create a subclass of BasePlatformAPI
    2. Implement the required methods
    3. Register it with PlatformRegistry.register()
    """
    
    PLATFORM_NAME: str = "unknown"
    RTMP_URL: str = ""

    def __init__(self):
        self.enabled = True
        self._stream_key = ""

    def get_viewers(self) -> int:
        """Get current viewer count."""
        return 0

    def get_followers(self) -> int:
        """Get follower/subscriber count."""
        return 0

    def get_subscribers(self) -> int:
        """Get paid subscriber count."""
        return 0

    def get_donations(self) -> float:
        """Get total donations amount."""
        return 0.0

    def get_stream_config(self) -> Optional[StreamConfig]:
        """Get stream configuration for this platform."""
        if not self._stream_key:
            return None
        return StreamConfig(
            platform_name=self.PLATFORM_NAME,
            rtmp_url=self.RTMP_URL,
            stream_key=self._stream_key,
            enabled=self.enabled
        )

    def is_configured(self) -> bool:
        """Check if platform has required credentials configured."""
        return bool(self._stream_key)


class PlatformRegistry:
    """Registry for managing streaming platforms.
    
    Allows dynamic registration of new platforms for extensibility.
    """
    
    _platforms: Dict[str, Type[BasePlatformAPI]] = {}
    _instances: Dict[str, BasePlatformAPI] = {}

    @classmethod
    def register(cls, platform_class: Type[BasePlatformAPI]) -> None:
        """Register a new platform API class."""
        name = platform_class.PLATFORM_NAME.lower()
        cls._platforms[name] = platform_class

    @classmethod
    def get(cls, name: str) -> Optional[BasePlatformAPI]:
        """Get or create a platform instance by name."""
        name = name.lower()
        if name not in cls._instances and name in cls._platforms:
            cls._instances[name] = cls._platforms[name]()
        return cls._instances.get(name)

    @classmethod
    def get_all(cls) -> List[BasePlatformAPI]:
        """Get all registered platform instances."""
        for name in cls._platforms:
            if name not in cls._instances:
                cls._instances[name] = cls._platforms[name]()
        return list(cls._instances.values())

    @classmethod
    def get_configured(cls) -> List[BasePlatformAPI]:
        """Get all platforms that have credentials configured."""
        return [p for p in cls.get_all() if p.is_configured()]

    @classmethod
    def get_enabled(cls) -> List[BasePlatformAPI]:
        """Get all platforms that are enabled for streaming."""
        return [p for p in cls.get_configured() if p.enabled]

    @classmethod
    def get_stream_configs(cls) -> List[StreamConfig]:
        """Get stream configs for all enabled platforms."""
        configs = []
        for platform in cls.get_enabled():
            config = platform.get_stream_config()
            if config:
                configs.append(config)
        return configs

    @classmethod
    def list_available(cls) -> List[str]:
        """List all registered platform names."""
        return list(cls._platforms.keys())


class TwitchAPI(BasePlatformAPI):
    """Twitch API integration for stream metrics."""

    PLATFORM_NAME = "twitch"
    RTMP_URL = "rtmp://live.twitch.tv/app"
    BASE_URL = "https://api.twitch.tv/helix"

    def __init__(self):
        super().__init__()
        self.client_id = TWITCH_CLIENT_ID
        self.access_token = TWITCH_ACCESS_TOKEN
        self.channel_id = TWITCH_CHANNEL_ID
        self._stream_key = TWITCH_STREAM_KEY

    def _get_headers(self) -> dict:
        """Get authorization headers for Twitch API."""
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_viewers(self) -> int:
        """Get current live viewer count from Twitch."""
        if not self.access_token or not self.channel_id:
            return 0
        try:
            response = requests.get(
                f"{self.BASE_URL}/streams",
                headers=self._get_headers(),
                params={"user_id": self.channel_id},
                timeout=10
            )
            response.raise_for_status()
            data = response.json().get("data", [])
            return data[0].get("viewer_count", 0) if data else 0
        except Exception as e:
            print(f"Twitch API error: {e}")
            return 0

    def get_followers(self) -> int:
        """Get follower count from Twitch."""
        if not self.access_token or not self.channel_id:
            return 0
        try:
            response = requests.get(
                f"{self.BASE_URL}/channels/followers",
                headers=self._get_headers(),
                params={"broadcaster_id": self.channel_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("total", 0)
        except Exception as e:
            print(f"Twitch API error: {e}")
            return 0

    def get_subscribers(self) -> int:
        """Get subscriber count from Twitch."""
        if not self.access_token or not self.channel_id:
            return 0
        try:
            response = requests.get(
                f"{self.BASE_URL}/subscriptions",
                headers=self._get_headers(),
                params={"broadcaster_id": self.channel_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("total", 0)
        except Exception as e:
            print(f"Twitch API error: {e}")
            return 0

    def get_donations(self) -> float:
        """Get donations (requires third-party integration)."""
        # Twitch doesn't have native donation API
        # Would need StreamElements, Streamlabs, etc.
        return 0.0


class YouTubeAPI(BasePlatformAPI):
    """YouTube API integration for stream metrics."""

    PLATFORM_NAME = "youtube"
    RTMP_URL = "rtmp://a.rtmp.youtube.com/live2"
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        super().__init__()
        self.api_key = YOUTUBE_API_KEY
        self.channel_id = YOUTUBE_CHANNEL_ID
        self._stream_key = YOUTUBE_STREAM_KEY

    def get_viewers(self) -> int:
        """Get current live viewer count from YouTube."""
        if not self.api_key or not self.channel_id:
            return 0
        try:
            # First get live broadcast ID
            response = requests.get(
                f"{self.BASE_URL}/search",
                params={
                    "key": self.api_key,
                    "channelId": self.channel_id,
                    "eventType": "live",
                    "type": "video",
                    "part": "id"
                },
                timeout=10
            )
            response.raise_for_status()
            items = response.json().get("items", [])
            if not items:
                return 0

            video_id = items[0]["id"]["videoId"]
            # Get live stream details
            response = requests.get(
                f"{self.BASE_URL}/videos",
                params={
                    "key": self.api_key,
                    "id": video_id,
                    "part": "liveStreamingDetails"
                },
                timeout=10
            )
            response.raise_for_status()
            items = response.json().get("items", [])
            if items:
                details = items[0].get("liveStreamingDetails", {})
                return int(details.get("concurrentViewers", 0))
            return 0
        except Exception as e:
            print(f"YouTube API error: {e}")
            return 0

    def get_followers(self) -> int:
        """Get subscriber count from YouTube."""
        if not self.api_key or not self.channel_id:
            return 0
        try:
            response = requests.get(
                f"{self.BASE_URL}/channels",
                params={
                    "key": self.api_key,
                    "id": self.channel_id,
                    "part": "statistics"
                },
                timeout=10
            )
            response.raise_for_status()
            items = response.json().get("items", [])
            if items:
                stats = items[0].get("statistics", {})
                return int(stats.get("subscriberCount", 0))
            return 0
        except Exception as e:
            print(f"YouTube API error: {e}")
            return 0

    def get_subscribers(self) -> int:
        """YouTube members (requires OAuth, not public API)."""
        return 0

    def get_donations(self) -> float:
        """Super Chat totals (requires OAuth)."""
        return 0.0


class KickAPI(BasePlatformAPI):
    """Kick API integration for stream metrics.

    Note: Kick uses a different ingest URL format.
    Stream key format: kick_ingest_url?kick_stream_key
    """

    PLATFORM_NAME = "kick"
    RTMP_URL = "rtmps://fa723fc1b171.global-contribute.live-video.net/app"

    def __init__(self):
        super().__init__()
        self.username = KICK_USERNAME
        self._stream_key = KICK_STREAM_KEY

    def get_viewers(self) -> int:
        """Get viewer count from Kick.
        
        Note: Kick has limited API access. This uses their
        public channel endpoint when available.
        """
        if not self.username:
            return 0
        try:
            # Kick's public API endpoint (may change)
            response = requests.get(
                f"https://kick.com/api/v2/channels/{self.username}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                livestream = data.get("livestream")
                if livestream:
                    return livestream.get("viewer_count", 0)
            return 0
        except Exception as e:
            print(f"Kick API error: {e}")
            return 0

    def get_followers(self) -> int:
        """Get follower count from Kick."""
        if not self.username:
            return 0
        try:
            response = requests.get(
                f"https://kick.com/api/v2/channels/{self.username}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("followers_count", 0)
            return 0
        except Exception as e:
            print(f"Kick API error: {e}")
            return 0

    def get_subscribers(self) -> int:
        """Get subscriber count from Kick."""
        # Requires authenticated API access
        return 0

    def get_donations(self) -> float:
        """Get donations from Kick."""
        # Requires authenticated API access
        return 0.0


# Register all built-in platforms
PlatformRegistry.register(TwitchAPI)
PlatformRegistry.register(YouTubeAPI)
PlatformRegistry.register(KickAPI)