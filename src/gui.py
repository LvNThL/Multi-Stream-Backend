"""
GUI module using Tkinter
"""

import tkinter as tk
from tkinter import ttk
from obs_integration import OBSController
from metrics_aggregator import MetricsAggregator
from chat_manager import ChatManager
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

        self._create_widgets()

    def _create_widgets(self):
        """Create and arrange all GUI widgets."""
        # Stream control button
        self.stream_button = ttk.Button(
            self.root, text="Start Streaming", command=self.toggle_streaming
        )
        self.stream_button.pack(pady=10)

        # Metrics display frame
        self.metrics_frame = ttk.LabelFrame(self.root, text="Metrics", padding=10)
        self.metrics_frame.pack(pady=10, padx=10, fill=tk.X)

        self.viewers_label = ttk.Label(self.metrics_frame, text="Total Viewers: 0")
        self.viewers_label.pack(anchor=tk.W)

        self.followers_label = ttk.Label(self.metrics_frame, text="Total Followers: 0")
        self.followers_label.pack(anchor=tk.W)

        self.subscribers_label = ttk.Label(self.metrics_frame, text="Total Subscribers: 0")
        self.subscribers_label.pack(anchor=tk.W)

        self.donations_label = ttk.Label(self.metrics_frame, text="Total Donations: $0.00")
        self.donations_label.pack(anchor=tk.W)

        # Refresh metrics button
        self.refresh_button = ttk.Button(
            self.root, text="Refresh Metrics", command=self.update_metrics
        )
        self.refresh_button.pack(pady=5)

        # Chat display frame
        chat_frame = ttk.LabelFrame(self.root, text="Chat", padding=10)
        chat_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.chat_text = tk.Text(chat_frame, height=10, state=tk.DISABLED)
        self.chat_text.pack(fill=tk.BOTH, expand=True)

        # Chat input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))

        self.chat_entry = ttk.Entry(input_frame)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.chat_entry.bind("<Return>", self.send_chat_message)

        self.send_button = ttk.Button(
            input_frame, text="Send", command=self.send_chat_message
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

    def toggle_streaming(self):
        """Toggle streaming state and update metrics."""
        # TODO: Implement actual OBS streaming toggle
        self.metrics.send_metrics_to_backend()
        self.update_metrics()

    def update_metrics(self):
        """Refresh metrics display from aggregator."""
        viewers = self.metrics.get_total_viewers()
        followers = self.metrics.get_total_followers()
        subscribers = self.metrics.get_total_subscribers()
        donations = self.metrics.get_total_donations()

        self.viewers_label.config(text=f"Total Viewers: {viewers:,}")
        self.followers_label.config(text=f"Total Followers: {followers:,}")
        self.subscribers_label.config(text=f"Total Subscribers: {subscribers:,}")
        self.donations_label.config(text=f"Total Donations: ${donations:,.2f}")

    def send_chat_message(self, event=None):
        """Send chat message to backend and display locally."""
        message = self.chat_entry.get().strip()
        if message:
            self.chat.send_message_sync("all", message)
            self._append_chat(f"You: {message}")
            self.chat_entry.delete(0, tk.END)

    def _append_chat(self, text):
        """Append text to chat display."""
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, f"{text}\n")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiStreamApp(root)
    root.mainloop()