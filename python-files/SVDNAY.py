import ctypes
import math
import time
import random
import os

# Load Windows API
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
shell32 = ctypes.windll.shell32

# Screen info
hDC = user32.GetDC(0)
width = user32.GetSystemMetrics(0)
height = user32.GetSystemMetrics(1)

# Offscreen buffer
hMemDC = gdi32.CreateCompatibleDC(hDC)
hBitmap = gdi32.CreateCompatibleBitmap(hDC, width, height)
gdi32.SelectObject(hMemDC, hBitmap)

# Emoticon list
texts = [
    "(๑>◡<๑)",
    "｡ﾟ(ﾟ´ω`ﾟ)ﾟ｡",
    "(´⊙ω⊙`)",
    "ʕ•̫͡•ʕ•̫͡•ʔ•̫͡•ʔ",
    ":;(∩´﹏`∩);:",
    "ヾ(＠⌒ー⌒＠)ノ",
]

# Japanese styled text
jp_texts = [
    "ごめんなさい",   # Sorry
    "やめられない", # Can't stop
    "混沌",         # Chaos
    "笑笑笑",       # LOL
    "すごい！！"     # Amazing!!
]

def wave_effect(duration=20):
    t = 0
    start = time.time()
    while time.time() - start < duration:
        gdi32.BitBlt(hMemDC, 0, 0, width, height, hDC, 0, 0, 0x00CC0020)
        for y in range(0, height, 2):
            offset = int(20 * math.sin((y / 50.0) + t))
            gdi32.BitBlt(hDC, offset, y, width, 2, hMemDC, 0, y, 0x00CC0020)
        t += 0.2
        time.sleep(0.02)

def text_spam(duration=20):
    start = time.time()
    hFont = gdi32.CreateFontW(40, 20, 0, 0, 700, False, False, False,
                              1, 0, 0, 0, 0, "Arial")
    gdi32.SelectObject(hDC, hFont)
    while time.time() - start < duration:
        tx = random.choice(texts)
        x = random.randint(0, width - 200)
        y = random.randint(0, height - 50)
        gdi32.TextOutW(hDC, x, y, tx, len(tx))
        time.sleep(0.05)

def shredder(duration=20):
    start = time.time()
    while time.time() - start < duration:
        slice_height = random.randint(5, 30)
        y = random.randint(0, height - slice_height)
        dx = random.randint(-100, 100)
        gdi32.BitBlt(hDC, dx, y, width, slice_height, hDC, 0, y, 0x00CC0020)
        time.sleep(0.01)

def chaos(duration=50):
    start = time.time()
    hFont = gdi32.CreateFontW(30, 15, 0, 0, 700, False, False, False,
                              1, 0, 0, 0, 0, "MS Gothic")
    gdi32.SelectObject(hDC, hFont)

    while time.time() - start < duration:
        mode = random.randint(1, 4)

        if mode == 1:  # Random Japanese text waves
            tx = random.choice(jp_texts) + " " + random.choice(texts)
            x = random.randint(0, width - 200)
            y = random.randint(0, height - 50)
            gdi32.TextOutW(hDC, x, y, tx, len(tx))

        elif mode == 2:  # Shred effect
            slice_height = random.randint(10, 50)
            y = random.randint(0, height - slice_height)
            dx = random.randint(-200, 200)
            gdi32.BitBlt(hDC, dx, y, width, slice_height, hDC, 0, y, 0x00CC0020)

        elif mode == 3:  # Fake icons glitches
            size = random.randint(32, 128)
            x = random.randint(0, width - size)
            y = random.randint(0, height - size)
            gdi32.PatBlt(hDC, x, y, size, size, 0x00A000C9)  # weird rect fill

        elif mode == 4:  # Open random apps (SAFE apps)
            apps = ["notepad.exe", "calc.exe", "mspaint.exe"]
            os.system(random.choice(apps))

        time.sleep(0.05)

def cleanup():
    user32.ReleaseDC(0, hDC)
    gdi32.DeleteDC(hMemDC)
    gdi32.DeleteObject(hBitmap)

# === EXECUTION ORDER ===
try:
    wave_effect(20)
    text_spam(20)
    shredder(20)
    chaos(50)
finally:
    cleanup()