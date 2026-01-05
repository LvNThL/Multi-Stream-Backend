"""
Platform APIs module for streaming platform integrations.

Provides unified interfaces for Twitch, YouTube, and Kick APIs.
"""

import requests
from typing import Optional
from config import (
    TWITCH_CLIENT_ID, TWITCH_ACCESS_TOKEN, TWITCH_CHANNEL_ID,
    YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID,
    KICK_USERNAME
)


class BasePlatformAPI:
    """Base class for platform API integrations."""

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


class TwitchAPI(BasePlatformAPI):
    """Twitch API integration for stream metrics."""

    BASE_URL = "https://api.twitch.tv/helix"

    def __init__(self):
        self.client_id = TWITCH_CLIENT_ID
        self.access_token = TWITCH_ACCESS_TOKEN
        self.channel_id = TWITCH_CHANNEL_ID

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

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.channel_id = YOUTUBE_CHANNEL_ID

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

    Note: Kick doesn't have an official public API yet.
    This is a placeholder for future implementation.
    """

    def __init__(self):
        self.username = KICK_USERNAME

    def get_viewers(self) -> int:
        """Get viewer count from Kick (unofficial)."""
        if not self.username:
            return 0
        # TODO: Implement when Kick API becomes available
        # Currently would require web scraping or unofficial endpoints
        return 0

    def get_followers(self) -> int:
        """Get follower count from Kick."""
        return 0

    def get_subscribers(self) -> int:
        """Get subscriber count from Kick."""
        return 0

    def get_donations(self) -> float:
        """Get donations from Kick."""
        return 0.0