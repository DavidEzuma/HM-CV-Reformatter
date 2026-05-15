"""Launcher: starts uvicorn silently, opens browser, adds system tray icon."""

import sys
import threading
import time
import webbrowser
from pathlib import Path

import pystray
from PIL import Image, ImageDraw
import uvicorn

PORT = 8000
URL = f"http://localhost:{PORT}"


def _make_icon():
    img = Image.new("RGB", (64, 64), color="#003087")
    draw = ImageDraw.Draw(img)
    draw.text((14, 20), "HM", fill="white")
    return img


def _run_server():
    uvicorn.run("app:app", host="127.0.0.1", port=PORT, log_level="error")


def _open_browser():
    time.sleep(1.5)  # wait for server to start
    webbrowser.open(URL)


def main():
    # Start server in background thread
    t = threading.Thread(target=_run_server, daemon=True)
    t.start()

    # Open browser
    threading.Thread(target=_open_browser, daemon=True).start()

    # Tray icon
    def quit_app(icon, item):
        icon.stop()
        sys.exit(0)

    def open_app(icon, item):
        webbrowser.open(URL)

    icon = pystray.Icon(
        "HM CV Reformatter",
        _make_icon(),
        "HM CV Reformatter",
        menu=pystray.Menu(
            pystray.MenuItem("Open App", open_app, default=True),
            pystray.MenuItem("Quit", quit_app),
        ),
    )
    icon.run()


if __name__ == "__main__":
    main()
