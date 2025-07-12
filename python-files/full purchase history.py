import time
import ctypes
import webbrowser
import random

messages = [
    "Steam Admin Verification Complete.",
    "VAC scan in progress...",
    "Suspicious behavior detected: User flagged.",
    "Verifying purchase history integrity...",
    "Internal Valve Protocol: Alert Code 593"
]

def troll_browser():
    links = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=ub82Xb1C8os",
        "https://www.youtube.com/watch?v=DLzxrzFCyOs"
    ]
    webbrowser.open(random.choice(links))

def troll_message():
    msg = random.choice(messages)
    ctypes.windll.user32.MessageBoxW(0, msg, "Steam Validation Program", 1)

for _ in range(3):
    troll_message()
    time.sleep(2)

ctypes.windll.user32.MessageBoxW(0, "Account flagged. Steam will restart in Safe Mode.", "Critical Steam Alert", 0)
troll_browser()
