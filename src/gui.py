"""
GUI module using Tkinter
"""

import tkinter as tk
from tkinter import ttk
import asyncio
from obs_integration import OBSController
from metrics_aggregator import MetricsAggregator
from chat_manager import ChatManager
from config import *

class MultiStreamApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)

        self.obs = OBSController(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        self.metrics = MetricsAggregator()
        self.chat = ChatManager()

        self.create_widgets()

    def create_widgets(self):
        # Start/Stop Streaming button
        self.stream_button = ttk.Button(self.root, text="Start Streaming", command=self.toggle_streaming)
        self.stream_button.pack(pady=10)

        # Metrics display
        self.metrics_frame = ttk.Frame(self.root)
        self.metrics_frame.pack(pady=10)

        self.viewers_label = ttk.Label(self.metrics_frame, text="Total Viewers: 0")
        self.viewers_label.pack()

        self.followers_label = ttk.Label(self.metrics_frame, text="Total Followers: 0")
        self.followers_label.pack()

        self.subscribers_label = ttk.Label(self.metrics_frame, text="Total Subscribers: 0")
        self.subscribers_label.pack()

        self.donations_label = ttk.Label(self.metrics_frame, text="Total Donations: 0.0")
        self.donations_label.pack()

        # Chat area (placeholder)
        self.chat_text = tk.Text(self.root, height=10)
        self.chat_text.pack(pady=10)

        self.chat_entry = ttk.Entry(self.root)
        self.chat_entry.pack(fill=tk.X, padx=10)
        # Refresh Metrics button
        self.refresh_button = ttk.Button(self.root, text="Refresh Metrics", command=self.update_metrics)
        self.refresh_button.pack(pady=5)

        # Chat area (placeholder)
        self.chat_text = tk.Text(self.root, height=10)
        self.chat_text.pack(pady=10)

        self.chat_entry = ttk.Entry(self.root)
        self.chat_entry.pack(fill=tk.X, padx=10)
        self.chat_entry.bind("<Return>", self.send_chat_message)

        # Send button for chat
        self.send_button = ttk.Button(self.root, text="Send", command=self.send_chat_message)
        self.send_button.pack(pady=5)

    def toggle_streaming(self):
        # TODO: Implement toggle
        # For now, just send metrics when clicked
        self.metrics.send_metrics_to_backend()
        self.update_metrics()

    def update_metrics(self):
        self.viewers_label.config(text=f"Total Viewers: {self.metrics.get_total_viewers()}")
        self.followers_label.config(text=f"Total Followers: {self.metrics.get_total_followers()}")
        self.subscribers_label.config(text=f"Total Subscribers: {self.metrics.get_total_subscribers()}")
        self.donations_label.config(text=f"Total Donations: {self.metrics.get_total_donations()}")

    def send_chat_message(self, event=None):
        message = self.chat_entry.get()
        if message:
            # Send to all platforms via backend
            asyncio.run(self.chat.send_message("all", message))
            self.chat_text.insert(tk.END, f"You: {message}\n")
            self.chat_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiStreamApp(root)
    root.mainloop()