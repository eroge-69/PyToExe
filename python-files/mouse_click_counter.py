#!/usr/bin/env python3
"""Mouse Click Counter
Runs quietly in the system tray and counts mouse clicks per day.
Save as mouse_click_counter.py, install required packages and (optionally) build to .exe with PyInstaller.
"""

import os
import json
import datetime
import threading
import sys

from pynput import mouse          # pip install pynput
import pystray                    # pip install pystray
from PIL import Image, ImageDraw  # pip install pillow

DATA_FILE = "clicks.json"


def load_counts():
    """Load click history from file, or return empty dict."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_counts(counts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)


def today_key():
    return datetime.date.today().isoformat()


class ClickCounter:
    def __init__(self):
        self.counts = load_counts()
        self._ensure_today_key()
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

    def _ensure_today_key(self):
        if today_key() not in self.counts:
            self.counts[today_key()] = 0
            save_counts(self.counts)

    def on_click(self, x, y, button, pressed):
        if pressed:
            self._ensure_today_key()
            self.counts[today_key()] += 1
            save_counts(self.counts)

    def get_today(self):
        self._ensure_today_key()
        return self.counts[today_key()]


def create_icon_image(size=64, color=(0, 0, 0)):
    """Return a simple dot image for the tray icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = size // 3
    draw.ellipse(
        (size // 2 - r, size // 2 - r, size // 2 + r, size // 2 + r),
        fill=color,
    )
    return img


def run_tray(counter: ClickCounter):
    icon = pystray.Icon(
        "Mouse Click Counter",
        icon=create_icon_image(),
        title="Mouse Click Counter",
        menu=pystray.Menu(
            pystray.MenuItem(
                lambda: f"Dnešné kliky: {counter.get_today()}",
                lambda: None,
                enabled=False,
            ),
            pystray.MenuItem(
                "Zobraziť notifikáciu",
                lambda: icon.notify(f"Dnes si klikol {counter.get_today()}× 🙂"),
            ),
            pystray.MenuItem("Ukončiť", lambda: icon.stop()),
        ),
    )
    icon.run()  # Blocks until the user chooses "Ukončiť"
    counter.listener.stop()
    sys.exit(0)


def midnight_reset(counter: ClickCounter):
    """Resets today's counter at local midnight in a background thread."""
    while True:
        now = datetime.datetime.now()
        tomorrow = (now + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        secs = (tomorrow - now).total_seconds()
        threading.Event().wait(secs)
        counter.counts[today_key()] = 0
        save_counts(counter.counts)


if __name__ == "__main__":
    counter = ClickCounter()
    threading.Thread(target=midnight_reset, args=(counter,), daemon=True).start()
    run_tray(counter)
