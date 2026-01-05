"""
Tests for Multi-Stream Operations application.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestConfig:
    """Tests for configuration module."""

    def test_backend_url_exists(self):
        from config import BACKEND_URL
        assert BACKEND_URL is not None
        assert BACKEND_URL.startswith("http")

    def test_window_settings(self):
        from config import WINDOW_TITLE, WINDOW_SIZE
        assert WINDOW_TITLE == "Multi-Stream Operations"
        assert "x" in WINDOW_SIZE


class TestPlatformAPIs:
    """Tests for platform API integrations."""

    def test_twitch_api_init(self):
        from platform_apis import TwitchAPI
        api = TwitchAPI()
        assert hasattr(api, 'get_viewers')
        assert hasattr(api, 'get_followers')

    def test_youtube_api_init(self):
        from platform_apis import YouTubeAPI
        api = YouTubeAPI()
        assert hasattr(api, 'get_viewers')
        assert hasattr(api, 'get_followers')

    def test_kick_api_init(self):
        from platform_apis import KickAPI
        api = KickAPI()
        assert hasattr(api, 'get_viewers')


class TestMetricsAggregator:
    """Tests for metrics aggregation."""

    def test_aggregator_init(self):
        from metrics_aggregator import MetricsAggregator
        aggregator = MetricsAggregator()
        assert aggregator.backend_url is not None

    def test_get_all_metrics(self):
        from metrics_aggregator import MetricsAggregator
        aggregator = MetricsAggregator()
        metrics = aggregator.get_all_metrics()
        assert "viewers" in metrics
        assert "followers" in metrics
        assert "subscribers" in metrics
        assert "donations" in metrics
        assert "platforms" in metrics


class TestPlatformRegistry:
    """Tests for platform registry system."""

    def test_registry_lists_platforms(self):
        from platform_apis import PlatformRegistry
        platforms = PlatformRegistry.list_available()
        assert "twitch" in platforms
        assert "youtube" in platforms
        assert "kick" in platforms

    def test_registry_get_platform(self):
        from platform_apis import PlatformRegistry
        twitch = PlatformRegistry.get("twitch")
        assert twitch is not None
        assert twitch.PLATFORM_NAME == "twitch"


class TestChatManager:
    """Tests for chat management."""

    def test_chat_manager_init(self):
        from chat_manager import ChatManager
        manager = ChatManager()
        assert hasattr(manager, 'send_message_sync')
        assert hasattr(manager, 'get_messages')