"""
Metrics Aggregator for multi-platform streaming.

Aggregates viewer counts, followers, subscribers, and donations
across all connected streaming platforms using the PlatformRegistry.
"""

import requests
from typing import Dict, List
from platform_apis import PlatformRegistry, BasePlatformAPI
from config import BACKEND_URL


class MetricsAggregator:
    """Aggregates metrics from multiple streaming platforms.
    
    Uses PlatformRegistry to automatically include all registered platforms,
    making it easy to add new platforms without modifying this code.
    """

    def __init__(self):
        self.backend_url = BACKEND_URL

    def _get_platforms(self) -> List[BasePlatformAPI]:
        """Get all registered platforms."""
        return PlatformRegistry.get_all()

    def get_total_viewers(self) -> int:
        """Get combined viewer count across all platforms."""
        return sum(p.get_viewers() for p in self._get_platforms())

    def get_total_followers(self) -> int:
        """Get combined follower count across all platforms."""
        return sum(p.get_followers() for p in self._get_platforms())

    def get_total_subscribers(self) -> int:
        """Get combined subscriber count across all platforms."""
        return sum(p.get_subscribers() for p in self._get_platforms())

    def get_total_donations(self) -> float:
        """Get combined donations across all platforms."""
        return sum(p.get_donations() for p in self._get_platforms())

    def get_platform_metrics(self, platform_name: str) -> Dict:
        """Get metrics for a specific platform."""
        platform = PlatformRegistry.get(platform_name)
        if not platform:
            return {}
        return {
            "platform": platform_name,
            "viewers": platform.get_viewers(),
            "followers": platform.get_followers(),
            "subscribers": platform.get_subscribers(),
            "donations": platform.get_donations()
        }

    def get_all_metrics(self) -> Dict:
        """Get all metrics as a dictionary."""
        return {
            "viewers": self.get_total_viewers(),
            "followers": self.get_total_followers(),
            "subscribers": self.get_total_subscribers(),
            "donations": self.get_total_donations(),
            "platforms": {
                p.PLATFORM_NAME: {
                    "viewers": p.get_viewers(),
                    "followers": p.get_followers(),
                    "configured": p.is_configured()
                }
                for p in self._get_platforms()
            }
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