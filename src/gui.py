"""
GUI module using Tkinter

Provides multi-platform streaming controls with per-platform toggles.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict
from obs_integration import OBSController
from metrics_aggregator import MetricsAggregator
from chat_manager import ChatManager
from platform_apis import PlatformRegistry
from config import WINDOW_TITLE, WINDOW_SIZE, OBS_HOST, OBS_PORT, OBS_PASSWORD


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


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiStreamApp(root)
    root.mainloop()