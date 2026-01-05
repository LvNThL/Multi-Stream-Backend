"""
Metrics Aggregator for multi-platform streaming.

Aggregates viewer counts, followers, subscribers, and donations
across all connected streaming platforms.
"""

import requests
from typing import Dict
from platform_apis import TwitchAPI, YouTubeAPI, KickAPI
from config import BACKEND_URL


class MetricsAggregator:
    """Aggregates metrics from multiple streaming platforms."""

    def __init__(self):
        self.twitch = TwitchAPI()
        self.youtube = YouTubeAPI()
        self.kick = KickAPI()
        self.backend_url = BACKEND_URL

    def get_total_viewers(self) -> int:
        """Get combined viewer count across all platforms."""
        return (
            self.twitch.get_viewers() +
            self.youtube.get_viewers() +
            self.kick.get_viewers()
        )

    def get_total_followers(self) -> int:
        """Get combined follower count across all platforms."""
        return (
            self.twitch.get_followers() +
            self.youtube.get_followers() +
            self.kick.get_followers()
        )

    def get_total_subscribers(self) -> int:
        """Get combined subscriber count across all platforms."""
        return (
            self.twitch.get_subscribers() +
            self.youtube.get_subscribers() +
            self.kick.get_subscribers()
        )

    def get_total_donations(self) -> float:
        """Get combined donations across all platforms."""
        return (
            self.twitch.get_donations() +
            self.youtube.get_donations() +
            self.kick.get_donations()
        )

    def get_all_metrics(self) -> Dict:
        """Get all metrics as a dictionary."""
        return {
            "viewers": self.get_total_viewers(),
            "followers": self.get_total_followers(),
            "subscribers": self.get_total_subscribers(),
            "donations": self.get_total_donations()
        }

    def send_metrics_to_backend(self) -> bool:
        """Send current metrics to the backend API.

        Returns:
            True if successful, False otherwise
        """
        metrics = self.get_all_metrics()
        try:
            response = requests.post(
                f"{self.backend_url}/metrics",
                json=metrics,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Failed to send metrics: {e}")
            return False