"""
Platform APIs module
"""

import requests
from config import *

class TwitchAPI:
    def __init__(self):
        self.client_id = TWITCH_CLIENT_ID
        self.access_token = TWITCH_ACCESS_TOKEN
        self.channel_id = TWITCH_CHANNEL_ID

    def get_viewers(self):
        # TODO: Implement API call
        return 0

    def get_followers(self):
        # TODO: Implement
        return 0

    def get_subscribers(self):
        # TODO: Implement
        return 0

    def get_donations(self):
        # TODO: Implement
        return 0.0

class YouTubeAPI:
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.channel_id = YOUTUBE_CHANNEL_ID

    def get_viewers(self):
        # TODO: Implement
        return 0

    # Similar methods for followers, subs, donations

class KickAPI:
    def __init__(self):
        self.username = KICK_USERNAME
        # Kick might not have official API, use scraping or unofficial
        pass

    def get_viewers(self):
        # TODO: Implement
        return 0

    # Similar methods