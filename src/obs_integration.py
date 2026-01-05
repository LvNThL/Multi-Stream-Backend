"""
OBS Integration module using WebSocket.

Provides control over OBS Studio for multi-platform streaming.
"""

try:
    from obswebsocket import obsws, requests as obs_requests
    OBS_AVAILABLE = True
except ImportError:
    OBS_AVAILABLE = False


class OBSController:
    """Controller for OBS Studio WebSocket integration."""

    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.ws = None
        self.connected = False

    def connect(self) -> bool:
        """Connect to OBS WebSocket server."""
        if not OBS_AVAILABLE:
            print("OBS WebSocket library not available")
            return False

        try:
            self.ws = obsws(self.host, self.port, self.password)
            self.ws.connect()
            self.connected = True
            print("Connected to OBS")
            return True
        except Exception as e:
            print(f"Failed to connect to OBS: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from OBS WebSocket server."""
        if self.ws and self.connected:
            try:
                self.ws.disconnect()
            except Exception:
                pass
            self.connected = False

    def start_streaming(self) -> bool:
        """Start streaming in OBS."""
        if not self.connected:
            return False
        try:
            self.ws.call(obs_requests.StartStreaming())
            return True
        except Exception as e:
            print(f"Failed to start streaming: {e}")
            return False

    def stop_streaming(self) -> bool:
        """Stop streaming in OBS."""
        if not self.connected:
            return False
        try:
            self.ws.call(obs_requests.StopStreaming())
            return True
        except Exception as e:
            print(f"Failed to stop streaming: {e}")
            return False

    def get_stream_status(self) -> dict:
        """Get current streaming status from OBS."""
        if not self.connected:
            return {"streaming": False, "recording": False}
        try:
            status = self.ws.call(obs_requests.GetStreamingStatus())
            return {
                "streaming": status.getStreaming(),
                "recording": status.getRecording()
            }
        except Exception as e:
            print(f"Failed to get stream status: {e}")
            return {"streaming": False, "recording": False}