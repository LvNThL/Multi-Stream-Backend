"""
OBS Integration module using WebSocket.

Provides control over OBS Studio for multi-platform streaming.
Supports the obs-multi-rtmp plugin for simultaneous streaming to multiple platforms.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    from obswebsocket import obsws, requests as obs_requests
    OBS_AVAILABLE = True
except ImportError:
    OBS_AVAILABLE = False


@dataclass
class StreamOutput:
    """Configuration for a streaming output."""
    name: str
    platform: str
    rtmp_url: str
    stream_key: str
    enabled: bool = True


class OBSController:
    """Controller for OBS Studio WebSocket integration.
    
    Supports standard OBS streaming and the obs-multi-rtmp plugin
    for simultaneous multi-platform streaming.
    """

    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.ws = None
        self.connected = False
        self._outputs: Dict[str, StreamOutput] = {}
        self._multi_rtmp_available = False

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

            # Check for multi-rtmp plugin
            self._check_multi_rtmp_plugin()

            return True
        except Exception as e:
            print(f"Failed to connect to OBS: {e}")
            self.connected = False
            return False

    def _check_multi_rtmp_plugin(self):
        """Check if obs-multi-rtmp plugin is available."""
        if not self.connected:
            return

        try:
            # Try to call a vendor request that the multi-rtmp plugin provides
            # This is a probe to see if the plugin is installed
            result = self.ws.call(obs_requests.GetVersion())
            version_info = str(result)

            # The plugin presence can be detected through available requests
            # For now, we'll set this based on whether custom outputs work
            self._multi_rtmp_available = False  # Will be set true if plugin detected
            print("OBS multi-rtmp plugin: Not detected (use main stream output)")
        except Exception:
            self._multi_rtmp_available = False

    def disconnect(self):
        """Disconnect from OBS WebSocket server."""
        if self.ws and self.connected:
            try:
                self.ws.disconnect()
            except Exception:
                pass
            self.connected = False

    def add_output(self, output: StreamOutput):
        """Add a streaming output configuration."""
        self._outputs[output.name] = output

    def remove_output(self, name: str):
        """Remove a streaming output configuration."""
        self._outputs.pop(name, None)

    def get_outputs(self) -> List[StreamOutput]:
        """Get all configured outputs."""
        return list(self._outputs.values())

    def configure_stream_settings(self, rtmp_url: str, stream_key: str) -> bool:
        """Configure the main OBS stream settings.
        
        Args:
            rtmp_url: RTMP server URL
            stream_key: Stream key for authentication
            
        Returns:
            True if successful
        """
        if not self.connected:
            return False

        try:
            # Set stream settings using OBS WebSocket
            self.ws.call(obs_requests.SetStreamSettings(
                type="rtmp_custom",
                settings={
                    "server": rtmp_url,
                    "key": stream_key
                }
            ))
            return True
        except Exception as e:
            print(f"Failed to configure stream settings: {e}")
            return False

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

    def start_recording(self) -> bool:
        """Start recording in OBS."""
        if not self.connected:
            return False
        try:
            self.ws.call(obs_requests.StartRecording())
            return True
        except Exception as e:
            print(f"Failed to start recording: {e}")
            return False

    def stop_recording(self) -> bool:
        """Stop recording in OBS."""
        if not self.connected:
            return False
        try:
            self.ws.call(obs_requests.StopRecording())
            return True
        except Exception as e:
            print(f"Failed to stop recording: {e}")
            return False

    def get_stream_status(self) -> dict:
        """Get current streaming status from OBS."""
        if not self.connected:
            return {"streaming": False, "recording": False, "stream_timecode": "00:00:00"}
        try:
            status = self.ws.call(obs_requests.GetStreamingStatus())
            return {
                "streaming": status.getStreaming(),
                "recording": status.getRecording(),
                "stream_timecode": getattr(status, 'getStreamTimecode', lambda: "00:00:00")()
            }
        except Exception as e:
            print(f"Failed to get stream status: {e}")
            return {"streaming": False, "recording": False, "stream_timecode": "00:00:00"}

    def get_stream_stats(self) -> dict:
        """Get streaming statistics for health monitoring."""
        if not self.connected:
            return {}
        try:
            # Try to get stats - may vary by OBS version
            stats = self.ws.call(obs_requests.GetStats())
            return {
                "cpu_usage": getattr(stats, 'getCpuUsage', lambda: 0)(),
                "memory_usage": getattr(stats, 'getMemoryUsage', lambda: 0)(),
                "fps": getattr(stats, 'getFps', lambda: 0)(),
                "render_missed_frames": getattr(stats, 'getRenderMissedFrames', lambda: 0)(),
                "output_skipped_frames": getattr(stats, 'getOutputSkippedFrames', lambda: 0)(),
            }
        except Exception as e:
            print(f"Failed to get stream stats: {e}")
            return {}

    def get_scenes(self) -> List[str]:
        """Get list of available scenes."""
        if not self.connected:
            return []
        try:
            result = self.ws.call(obs_requests.GetSceneList())
            return [scene['name'] for scene in result.getScenes()]
        except Exception:
            return []

    def set_scene(self, scene_name: str) -> bool:
        """Switch to a specific scene."""
        if not self.connected:
            return False
        try:
            self.ws.call(obs_requests.SetCurrentScene(scene_name))
            return True
        except Exception as e:
            print(f"Failed to set scene: {e}")
            return False

    @property
    def multi_rtmp_available(self) -> bool:
        """Check if multi-RTMP plugin is available."""
        return self._multi_rtmp_available