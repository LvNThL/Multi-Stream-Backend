"""
GUI module using Tkinter

Provides multi-platform streaming controls with per-platform toggles.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from obs_integration import OBSController
from metrics_aggregator import MetricsAggregator
from chat_manager import ChatManager
from platform_apis import PlatformRegistry
from config import WINDOW_TITLE, WINDOW_SIZE, OBS_HOST, OBS_PORT, OBS_PASSWORD


class SettingsDialog:
    """Settings dialog for configuring credentials and preferences."""

    def __init__(self, parent, app: "MultiStreamApp"):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Store entry references
        self.entries: Dict[str, ttk.Entry] = {}

        self._create_widgets()
        self._load_current_values()

        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Create settings form widgets."""
        # Main container with scrollbar
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=20)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # OBS Settings Section
        obs_frame = ttk.LabelFrame(scrollable_frame, text="OBS WebSocket", padding=10)
        obs_frame.pack(fill=tk.X, pady=(0, 15))

        self._create_field(obs_frame, "obs_host", "Host:", "localhost")
        self._create_field(obs_frame, "obs_port", "Port:", "4455")
        self._create_field(obs_frame, "obs_password", "Password:", "", show="*")

        # Twitch Settings Section
        twitch_frame = ttk.LabelFrame(scrollable_frame, text="Twitch", padding=10)
        twitch_frame.pack(fill=tk.X, pady=(0, 15))

        self._create_field(twitch_frame, "twitch_client_id", "Client ID:")
        self._create_field(twitch_frame, "twitch_client_secret", "Client Secret:", show="*")
        self._create_field(twitch_frame, "twitch_access_token", "Access Token:", show="*")
        self._create_field(twitch_frame, "twitch_channel_id", "Channel ID:")
        self._create_field(twitch_frame, "twitch_stream_key", "Stream Key:", show="*")

        # Twitch OAuth button
        twitch_btn_frame = ttk.Frame(twitch_frame)
        twitch_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(twitch_btn_frame, text="🔐 Authenticate with Twitch",
                   command=self._start_twitch_oauth).pack(side=tk.LEFT)
        ttk.Label(twitch_frame, text="Get credentials at: dev.twitch.tv/console",
                  foreground="blue", cursor="hand2").pack(anchor=tk.W, pady=(5, 0))

        # YouTube Settings Section
        youtube_frame = ttk.LabelFrame(scrollable_frame, text="YouTube", padding=10)
        youtube_frame.pack(fill=tk.X, pady=(0, 15))

        self._create_field(youtube_frame, "youtube_client_id", "Client ID:")
        self._create_field(youtube_frame, "youtube_client_secret", "Client Secret:", show="*")
        self._create_field(youtube_frame, "youtube_access_token", "Access Token:", show="*")
        self._create_field(youtube_frame, "youtube_api_key", "API Key:", show="*")
        self._create_field(youtube_frame, "youtube_channel_id", "Channel ID:")
        self._create_field(youtube_frame, "youtube_stream_key", "Stream Key:", show="*")

        # YouTube OAuth button
        youtube_btn_frame = ttk.Frame(youtube_frame)
        youtube_btn_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(youtube_btn_frame, text="🔐 Authenticate with Google",
                   command=self._start_youtube_oauth).pack(side=tk.LEFT)
        ttk.Label(youtube_frame, text="Get credentials at: console.cloud.google.com",
                  foreground="blue", cursor="hand2").pack(anchor=tk.W, pady=(5, 0))

        # Kick Settings Section
        kick_frame = ttk.LabelFrame(scrollable_frame, text="Kick", padding=10)
        kick_frame.pack(fill=tk.X, pady=(0, 15))

        self._create_field(kick_frame, "kick_username", "Username:")
        self._create_field(kick_frame, "kick_stream_key", "Stream Key:", show="*")

        ttk.Label(kick_frame, text="Get stream key from: kick.com/dashboard/settings/stream",
                  foreground="blue", cursor="hand2").pack(anchor=tk.W, pady=(5, 0))

        # Buttons
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Save", command=self._save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)

        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_field(self, parent: ttk.Frame, key: str, label: str,
                      default: str = "", show: str = ""):
        """Create a labeled entry field."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        ttk.Label(frame, text=label, width=15).pack(side=tk.LEFT)
        entry = ttk.Entry(frame, show=show)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.insert(0, default)

        self.entries[key] = entry

    def _load_current_values(self):
        """Load current configuration values into fields."""
        # Load from app's current settings
        settings = self.app.get_current_settings()
        for key, value in settings.items():
            if key in self.entries and value:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, value)

    def _save_settings(self):
        """Save settings and update the application."""
        settings = {key: entry.get() for key, entry in self.entries.items()}
        self.app.apply_settings(settings)
        messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
        self.dialog.destroy()

    def _start_twitch_oauth(self):
        """Start Twitch OAuth authentication flow."""
        from platform_apis import TwitchOAuth

        client_id = self.entries.get("twitch_client_id").get()
        client_secret = self.entries.get("twitch_client_secret").get()

        if not client_id or not client_secret:
            messagebox.showwarning(
                "Missing Credentials",
                "Please enter your Twitch Client ID and Client Secret first."
            )
            return

        def on_token_received(token: str):
            # Update the access token field
            self.dialog.after(0, lambda: self._set_twitch_token(token))

        oauth = TwitchOAuth(client_id, client_secret, on_success=on_token_received)
        if oauth.start_auth_flow():
            messagebox.showinfo(
                "Authentication Started",
                "A browser window will open for Twitch authentication.\n\n"
                "After authorizing, the access token will be filled automatically."
            )

    def _set_twitch_token(self, token: str):
        """Set the Twitch access token in the entry field."""
        if "twitch_access_token" in self.entries:
            self.entries["twitch_access_token"].delete(0, tk.END)
            self.entries["twitch_access_token"].insert(0, token)
            messagebox.showinfo("Success", "Twitch access token received!")

    def _start_youtube_oauth(self):
        """Start YouTube/Google OAuth authentication flow."""
        from platform_apis import YouTubeOAuth

        client_id = self.entries.get("youtube_client_id").get()
        client_secret = self.entries.get("youtube_client_secret").get()

        if not client_id or not client_secret:
            messagebox.showwarning(
                "Missing Credentials",
                "Please enter your YouTube/Google Client ID and Client Secret first.\n\n"
                "Create OAuth credentials at console.cloud.google.com"
            )
            return

        def on_token_received(token: str):
            self.dialog.after(0, lambda: self._set_youtube_token(token))

        oauth = YouTubeOAuth(client_id, client_secret, on_success=on_token_received)
        if oauth.start_auth_flow():
            messagebox.showinfo(
                "Authentication Started",
                "A browser window will open for Google authentication.\n\n"
                "After authorizing, the access token will be filled automatically."
            )

    def _set_youtube_token(self, token: str):
        """Set the YouTube access token in the entry field."""
        if "youtube_access_token" in self.entries:
            self.entries["youtube_access_token"].delete(0, tk.END)
            self.entries["youtube_access_token"].insert(0, token)
            messagebox.showinfo("Success", "YouTube access token received!")


class MultiStreamApp:
    """Main application class for Multi-Stream Operations GUI."""

    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)

        self.obs = OBSController(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        self.metrics = MetricsAggregator()
        self.chat = ChatManager()

        # Track platform toggle states
        self.platform_vars: Dict[str, tk.BooleanVar] = {}
        self.platform_labels: Dict[str, ttk.Label] = {}
        self.is_streaming = False

        self._create_widgets()
        self._check_platform_configs()

    def _create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Controls and Metrics
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # OBS Connection frame
        obs_frame = ttk.LabelFrame(left_panel, text="OBS Connection", padding=10)
        obs_frame.pack(fill=tk.X, pady=(0, 10))

        self.obs_status_label = ttk.Label(obs_frame, text="● Disconnected", foreground="red")
        self.obs_status_label.pack(side=tk.LEFT)

        ttk.Button(obs_frame, text="⚙ Settings", command=self._open_settings).pack(side=tk.RIGHT, padx=(5, 0))
        self.connect_obs_btn = ttk.Button(obs_frame, text="Connect to OBS", command=self._toggle_obs_connection)
        self.connect_obs_btn.pack(side=tk.RIGHT)

        # Platform selection frame
        platform_frame = ttk.LabelFrame(left_panel, text="Streaming Platforms", padding=10)
        platform_frame.pack(fill=tk.X, pady=(0, 10))

        # Create toggles for each registered platform
        for platform_name in PlatformRegistry.list_available():
            self._create_platform_row(platform_frame, platform_name)

        # Stream control buttons
        control_frame = ttk.Frame(left_panel)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.stream_button = ttk.Button(
            control_frame, text="▶ Start Streaming", command=self.toggle_streaming
        )
        self.stream_button.pack(fill=tk.X, ipady=10)

        # Metrics display frame
        self.metrics_frame = ttk.LabelFrame(left_panel, text="Live Metrics", padding=10)
        self.metrics_frame.pack(fill=tk.X, pady=(0, 10))

        # Per-platform metrics
        metrics_grid = ttk.Frame(self.metrics_frame)
        metrics_grid.pack(fill=tk.X)

        # Headers
        ttk.Label(metrics_grid, text="Platform", font=("", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Label(metrics_grid, text="Viewers", font=("", 9, "bold")).grid(row=0, column=1, padx=10)
        ttk.Label(metrics_grid, text="Followers", font=("", 9, "bold")).grid(row=0, column=2, padx=10)

        # Platform rows
        row = 1
        for platform_name in PlatformRegistry.list_available():
            ttk.Label(metrics_grid, text=platform_name.capitalize()).grid(row=row, column=0, sticky=tk.W, padx=5)
            viewers_label = ttk.Label(metrics_grid, text="0")
            viewers_label.grid(row=row, column=1, padx=10)
            followers_label = ttk.Label(metrics_grid, text="0")
            followers_label.grid(row=row, column=2, padx=10)
            self.platform_labels[f"{platform_name}_viewers"] = viewers_label
            self.platform_labels[f"{platform_name}_followers"] = followers_label
            row += 1

        # Totals row
        ttk.Separator(metrics_grid, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky="ew", pady=5)
        row += 1
        ttk.Label(metrics_grid, text="Total", font=("", 9, "bold")).grid(row=row, column=0, sticky=tk.W, padx=5)
        self.total_viewers_label = ttk.Label(metrics_grid, text="0", font=("", 9, "bold"))
        self.total_viewers_label.grid(row=row, column=1, padx=10)
        self.total_followers_label = ttk.Label(metrics_grid, text="0", font=("", 9, "bold"))
        self.total_followers_label.grid(row=row, column=2, padx=10)

        # Refresh button
        ttk.Button(self.metrics_frame, text="🔄 Refresh Metrics", command=self.update_metrics).pack(pady=(10, 0))

        # Right panel - Chat
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Chat display frame
        chat_frame = ttk.LabelFrame(right_panel, text="Unified Chat", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        # Chat text area with scrollbar
        chat_container = ttk.Frame(chat_frame)
        chat_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(chat_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_text = tk.Text(chat_container, height=15, state=tk.DISABLED, yscrollcommand=scrollbar.set)
        self.chat_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.chat_text.yview)

        # Chat input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        self.chat_entry = ttk.Entry(input_frame)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_entry.bind("<Return>", self.send_chat_message)

        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_chat_message)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

    def _create_platform_row(self, parent: ttk.Frame, platform_name: str):
        """Create a row with toggle and status for a platform."""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=2)

        # Toggle checkbox
        var = tk.BooleanVar(value=True)
        self.platform_vars[platform_name] = var

        cb = ttk.Checkbutton(
            row_frame,
            text=platform_name.capitalize(),
            variable=var,
            command=lambda p=platform_name: self._on_platform_toggle(p)
        )
        cb.pack(side=tk.LEFT)

        # Status indicator
        status_label = ttk.Label(row_frame, text="● Not configured", foreground="gray")
        status_label.pack(side=tk.RIGHT)
        self.platform_labels[f"{platform_name}_status"] = status_label

    def _check_platform_configs(self):
        """Check which platforms have valid configurations."""
        for platform in PlatformRegistry.get_all():
            name = platform.PLATFORM_NAME.lower()
            status_label = self.platform_labels.get(f"{name}_status")
            if status_label:
                if platform.is_configured():
                    status_label.config(text="● Ready", foreground="green")
                else:
                    status_label.config(text="● Not configured", foreground="gray")
                    self.platform_vars[name].set(False)

    def _on_platform_toggle(self, platform_name: str):
        """Handle platform toggle checkbox changes."""
        platform = PlatformRegistry.get(platform_name)
        if platform:
            enabled = self.platform_vars[platform_name].get()
            if enabled and not platform.is_configured():
                messagebox.showwarning(
                    "Configuration Required",
                    f"{platform_name.capitalize()} requires configuration.\n\n"
                    f"Please set the stream key in your environment variables."
                )
                self.platform_vars[platform_name].set(False)
                return
            platform.enabled = enabled

    def _toggle_obs_connection(self):
        """Connect or disconnect from OBS."""
        if self.obs.connected:
            self.obs.disconnect()
            self.obs_status_label.config(text="● Disconnected", foreground="red")
            self.connect_obs_btn.config(text="Connect to OBS")
        else:
            if self.obs.connect():
                self.obs_status_label.config(text="● Connected", foreground="green")
                self.connect_obs_btn.config(text="Disconnect")
            else:
                messagebox.showerror(
                    "Connection Failed",
                    "Could not connect to OBS.\n\n"
                    "Make sure OBS is running and WebSocket server is enabled."
                )

    def toggle_streaming(self):
        """Toggle streaming state across enabled platforms."""
        if not self.obs.connected:
            messagebox.showwarning("OBS Not Connected", "Please connect to OBS first.")
            return

        enabled_platforms = [p for p in PlatformRegistry.get_all()
                           if self.platform_vars.get(p.PLATFORM_NAME.lower(), tk.BooleanVar()).get()
                           and p.is_configured()]

        if not enabled_platforms:
            messagebox.showwarning("No Platforms", "No platforms are enabled and configured.")
            return

        if self.is_streaming:
            # Stop streaming
            if self.obs.stop_streaming():
                self.is_streaming = False
                self.stream_button.config(text="▶ Start Streaming")
                self._append_chat("[System] Streaming stopped.")
        else:
            # Start streaming
            platform_names = [p.PLATFORM_NAME.capitalize() for p in enabled_platforms]
            if self.obs.start_streaming():
                self.is_streaming = True
                self.stream_button.config(text="⏹ Stop Streaming")
                self._append_chat(f"[System] Now streaming to: {', '.join(platform_names)}")
                self.metrics.send_metrics_to_backend()

    def update_metrics(self):
        """Refresh metrics display from all platforms."""
        total_viewers = 0
        total_followers = 0

        for platform in PlatformRegistry.get_all():
            name = platform.PLATFORM_NAME.lower()
            viewers = platform.get_viewers()
            followers = platform.get_followers()

            total_viewers += viewers
            total_followers += followers

            # Update per-platform labels
            if f"{name}_viewers" in self.platform_labels:
                self.platform_labels[f"{name}_viewers"].config(text=f"{viewers:,}")
            if f"{name}_followers" in self.platform_labels:
                self.platform_labels[f"{name}_followers"].config(text=f"{followers:,}")

        # Update totals
        self.total_viewers_label.config(text=f"{total_viewers:,}")
        self.total_followers_label.config(text=f"{total_followers:,}")

    def send_chat_message(self, event=None):
        """Send chat message to backend and display locally."""
        message = self.chat_entry.get().strip()
        if message:
            self.chat.send_message_sync("all", message)
            self._append_chat(f"You: {message}")
            self.chat_entry.delete(0, tk.END)

    def _append_chat(self, text: str):
        """Append text to chat display."""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"{text}\n")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def _open_settings(self):
        """Open the settings dialog."""
        SettingsDialog(self.root, self)

    def get_current_settings(self) -> Dict[str, str]:
        """Get current settings for the settings dialog."""
        import config
        return {
            "obs_host": getattr(config, 'OBS_HOST', 'localhost'),
            "obs_port": str(getattr(config, 'OBS_PORT', 4455)),
            "obs_password": getattr(config, 'OBS_PASSWORD', ''),
            "twitch_client_id": getattr(config, 'TWITCH_CLIENT_ID', ''),
            "twitch_client_secret": getattr(config, 'TWITCH_CLIENT_SECRET', ''),
            "twitch_access_token": getattr(config, 'TWITCH_ACCESS_TOKEN', ''),
            "twitch_channel_id": getattr(config, 'TWITCH_CHANNEL_ID', ''),
            "twitch_stream_key": getattr(config, 'TWITCH_STREAM_KEY', ''),
            "youtube_client_id": getattr(config, 'YOUTUBE_CLIENT_ID', ''),
            "youtube_client_secret": getattr(config, 'YOUTUBE_CLIENT_SECRET', ''),
            "youtube_access_token": getattr(config, 'YOUTUBE_ACCESS_TOKEN', ''),
            "youtube_api_key": getattr(config, 'YOUTUBE_API_KEY', ''),
            "youtube_channel_id": getattr(config, 'YOUTUBE_CHANNEL_ID', ''),
            "youtube_stream_key": getattr(config, 'YOUTUBE_STREAM_KEY', ''),
            "kick_username": getattr(config, 'KICK_USERNAME', ''),
            "kick_stream_key": getattr(config, 'KICK_STREAM_KEY', ''),
        }

    def apply_settings(self, settings: Dict[str, str]):
        """Apply new settings to the application."""
        import config
        from config import save_settings

        # Update config module values
        config.OBS_HOST = settings.get("obs_host", "localhost")
        config.OBS_PORT = int(settings.get("obs_port", 4455))
        config.OBS_PASSWORD = settings.get("obs_password", "")

        config.TWITCH_CLIENT_ID = settings.get("twitch_client_id", "")
        config.TWITCH_CLIENT_SECRET = settings.get("twitch_client_secret", "")
        config.TWITCH_ACCESS_TOKEN = settings.get("twitch_access_token", "")
        config.TWITCH_CHANNEL_ID = settings.get("twitch_channel_id", "")
        config.TWITCH_STREAM_KEY = settings.get("twitch_stream_key", "")

        config.YOUTUBE_CLIENT_ID = settings.get("youtube_client_id", "")
        config.YOUTUBE_CLIENT_SECRET = settings.get("youtube_client_secret", "")
        config.YOUTUBE_ACCESS_TOKEN = settings.get("youtube_access_token", "")
        config.YOUTUBE_API_KEY = settings.get("youtube_api_key", "")
        config.YOUTUBE_CHANNEL_ID = settings.get("youtube_channel_id", "")
        config.YOUTUBE_STREAM_KEY = settings.get("youtube_stream_key", "")

        config.KICK_USERNAME = settings.get("kick_username", "")
        config.KICK_STREAM_KEY = settings.get("kick_stream_key", "")

        # Save settings to file for persistence
        save_settings(settings)

        # Recreate OBS controller with new settings
        if self.obs.connected:
            self.obs.disconnect()
            self.obs_status_label.config(text="● Disconnected", foreground="red")
            self.connect_obs_btn.config(text="Connect to OBS")

        self.obs = OBSController(config.OBS_HOST, config.OBS_PORT, config.OBS_PASSWORD)

        # Reinitialize platform APIs to pick up new credentials
        PlatformRegistry._instances.clear()

        # Refresh platform status indicators
        self._check_platform_configs()


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiStreamApp(root)
    root.mainloop()