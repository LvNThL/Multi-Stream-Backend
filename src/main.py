"""
Multi-Stream Operations Main Application
"""

from gui import MultiStreamApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = MultiStreamApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()