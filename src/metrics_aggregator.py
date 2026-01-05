"""
Metrics Aggregator
"""

import requests
from platform_apis import TwitchAPI, YouTubeAPI, KickAPI
from config import BACKEND_URL

class MetricsAggregator:
    def __init__(self):
        self.twitch = TwitchAPI()
        self.youtube = YouTubeAPI()
        self.kick = KickAPI()
        self.backend_url = BACKEND_URL

    def get_total_viewers(self):
        return self.twitch.get_viewers() + self.youtube.get_viewers() + self.kick.get_viewers()

    def get_total_followers(self):
        return self.twitch.get_followers() + self.youtube.get_followers() + self.kick.get_followers()

    def get_total_subscribers(self):
        return self.twitch.get_subscribers() + self.youtube.get_subscribers() + self.kick.get_subscribers()

    def get_total_donations(self):
        return self.twitch.get_donations() + self.youtube.get_donations() + self.kick.get_donations()

    def send_metrics_to_backend(self):
        metrics = {
            "viewers": self.get_total_viewers(),
            "followers": self.get_total_followers(),
            "subscribers": self.get_total_subscribers(),
            "donations": self.get_total_donations()
        }
        try:
            response = requests.post(f"{self.backend_url}/metrics", json=metrics)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to send metrics: {e}")