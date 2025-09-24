import win32gui
import win32con
import ctypes
import math
import time
import winsound
from PIL import ImageGrab, Image, ImageDraw, ImageFont, ImageColor
import numpy as np
import sys

# --- Show warning dialog ---
MB_YESNO = 0x04
MB_ICONWARNING = 0x30
IDYES = 6
IDNO = 7
user32 = ctypes.windll.user32
response = user32.MessageBoxW(
    0,
    "WARNING: This program will rapidly and repeatedly manipulate your screen and play sounds.\n\nDo you want to continue?",
    "WARNING",
    MB_YESNO | MB_ICONWARNING
)
if response == IDNO:
    sys.exit(0)

    MB_YESNO = 0x04
MB_ICONWARNING = 0x30
IDYES = 6
IDNO = 7
user32 = ctypes.windll.user32
response = user32.MessageBoxW(
    0,
    "Are you sure you want to continue?\n\nThis program may cause discomfort or trigger seizures in some individuals.",
    "WARNING",
    MB_YESNO | MB_ICONWARNING
)
if response == IDNO:
    sys.exit(0)

gdi32 = ctypes.windll.gdi32
user32.SetProcessDPIAware()
sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
hdc = win32gui.GetDC(0)
dx = dy = 1
angle = 0
size = 1
speed = 5

last_invert = time.time()
start_time = time.time()
noodle_mode = False
hue_mode = False
whirlpool_mode = False
flaming_mode = False
flipped_mode = False
crumple_mode = False
balls_mode = False

noodle_start = None
hue_start = None
whirlpool_start = None
flaming_start = None
flaming_last_text = 0
flaming_text_positions = []
sound_cycle_start = None
sound_index = 0
sounds = ["SystemHand", "SystemExclamation", "SystemAsterisk", "notify"]

crumple_start = None
balls = [
    {"x": 200, "y": 200, "vx": 18, "vy": 13, "hue": 0},
    {"x": 600, "y": 400, "vx": -16, "vy": 15, "hue": 128}
]
trail_img = None

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_int32),
        ("biHeight", ctypes.c_int32),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_int32),
        ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", ctypes.c_uint32 * 3)
    ]

while True:
    current_time = time.time()
    elapsed = current_time - start_time

    # --- BALLS MODE ---
    if balls_mode:
        if trail_img is None:
            trail_img = Image.new("RGBA", (sw, sh), (0, 0, 0, 255))
        arr = np.array(trail_img)
        arr[..., :3] = (arr[..., :3] * 0.85).astype(np.uint8)
        trail_img = Image.fromarray(arr, "RGBA")
        draw = ImageDraw.Draw(trail_img, "RGBA")
        for ball in balls:
            color = tuple(int(c*255) for c in ImageColor.getrgb(f"hsv({ball['hue']},100%,100%)")) + (255,)
            draw.ellipse(
                [ball["x"]-30, ball["y"]-30, ball["x"]+30, ball["y"]+30],
                fill=color
            )
            ball["x"] += ball["vx"]
            ball["y"] += ball["vy"]
            ball["hue"] = (ball["hue"] + 4) % 256
            if ball["x"] < 30 or ball["x"] > sw-30:
                ball["vx"] *= -1
                ball["x"] = max(30, min(sw-30, ball["x"]))
            if ball["y"] < 30 or ball["y"] > sh-30:
                ball["vy"] *= -1
                ball["y"] = max(30, min(sh-30, ball["y"]))
        img_bgrx = trail_img.convert("RGBA")
        img_bytes = img_bgrx.tobytes("raw", "BGRA")
        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = sw
        bmi.bmiHeader.biHeight = -sh
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = win32con.BI_RGB
        bmi.bmiHeader.biSizeImage = 0
        bmi.bmiHeader.biXPelsPerMeter = 0
        bmi.bmiHeader.biYPelsPerMeter = 0
        bmi.bmiHeader.biClrUsed = 0
        bmi.bmiHeader.biClrImportant = 0
        gdi32.SetDIBitsToDevice(
            hdc, 0, 0, sw, sh, 0, 0, 0, sh,
            img_bytes,
            ctypes.byref(bmi),
            win32con.DIB_RGB_COLORS
        )
        time.sleep(0.01)
        continue

    # --- CRUMPLE MODE ---
    if crumple_mode:
        if crumple_start is None:
            crumple_start = current_time
        if current_time - crumple_start < 10:
            img = ImageGrab.grab(bbox=(0, 0, sw, sh)).convert("RGB")
            arr = np.array(img)
            block = 80
            for _ in range(80):
                x1 = np.random.randint(0, sw - block)
                y1 = np.random.randint(0, sh - block)
                x2 = np.random.randint(0, sw - block)
                y2 = np.random.randint(0, sh - block)
                temp = arr[y1:y1+block, x1:x1+block].copy()
                arr[y1:y1+block, x1:x1+block] = arr[y2:y2+block, x2:x2+block]
                arr[y2:y2+block, x2:x2+block] = temp
            img = Image.fromarray(arr)
            img_bgrx = img.convert("RGBA")
            img_bytes = img_bgrx.tobytes("raw", "BGRA")
            bmi = BITMAPINFO()
            bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bmi.bmiHeader.biWidth = sw
            bmi.bmiHeader.biHeight = -sh
            bmi.bmiHeader.biPlanes = 1
            bmi.bmiHeader.biBitCount = 32
            bmi.bmiHeader.biCompression = win32con.BI_RGB
            bmi.bmiHeader.biSizeImage = 0
            bmi.bmiHeader.biXPelsPerMeter = 0
            bmi.bmiHeader.biYPelsPerMeter = 0
            bmi.bmiHeader.biClrUsed = 0
            bmi.bmiHeader.biClrImportant = 0
            gdi32.SetDIBitsToDevice(
                hdc, 0, 0, sw, sh, 0, 0, 0, sh,
                img_bytes,
                ctypes.byref(bmi),
                win32con.DIB_RGB_COLORS
            )
            # Continue error sounds
            if sound_cycle_start is None:
                sound_cycle_start = current_time
            if current_time - sound_cycle_start >= 0.3:
                winsound.PlaySound(sounds[sound_index], winsound.SND_ALIAS | winsound.SND_ASYNC)
                sound_index = (sound_index + 1) % len(sounds)
                sound_cycle_start = current_time
            time.sleep(0.01)
            continue
        else:
            crumple_mode = False
            balls_mode = True
            trail_img = None
            continue

    # --- FLAMING MODE ---
    if elapsed >= 30 and not crumple_mode and not balls_mode:
        flaming_mode = False
        crumple_mode = True
        crumple_start = None
        continue

    if elapsed >= 25 and not flaming_mode:
        flaming_mode = True
        flaming_start = start_time + 30 - 5  # fudge so elapsed in flaming_mode is correct

    if flaming_mode:
        flaming_elapsed = elapsed - 25
        img = ImageGrab.grab(bbox=(0, 0, sw, sh)).convert("RGB")
        arr = np.array(img.convert("HSV"))
        arr[..., 0] = (arr[..., 0].astype(int) + int(flaming_elapsed * 40)) % 256

        # After 10s, overlay random hue-shifted squares
        if 10 <= flaming_elapsed < 25:
            block_size = 80
            num_blocks = 16
            for _ in range(num_blocks):
                x0 = np.random.randint(0, sw - block_size)
                y0 = np.random.randint(0, sh - block_size)
                hue_shift = np.random.randint(0, 256)
                arr[y0:y0+block_size, x0:x0+block_size, 0] = (
                    arr[y0:y0+block_size, x0:x0+block_size, 0].astype(int) + hue_shift
                ) % 256

        img = Image.fromarray(arr, "HSV").convert("RGB")

        # After 15s, apply a gradual hall/tunnel effect (radial zoom blur)
        if 15 <= flaming_elapsed < 30:
            arr = np.array(img)
            y, x = np.indices((sh, sw))
            cx, cy = sw // 2, sh // 2
            hall_elapsed = flaming_elapsed - 15
            max_zoom = 0.08
            zoom = min(max_zoom, max_zoom * (hall_elapsed / 5.0))
            max_iter = 4
            for i in range(1, max_iter + 1):
                factor = 1 + zoom * i
                xs = np.clip(((x - cx) / factor + cx).astype(np.int32), 0, sw - 1)
                ys = np.clip(((y - cy) / factor + cy).astype(np.int32), 0, sh - 1)
                arr = ((arr.astype(np.float32) + arr[ys, xs].astype(np.float32)) / 2).astype(np.uint8)
            img = Image.fromarray(arr)

        # After 25s, only hue and text remain, and screen flips, play error sounds repeatedly
        if flaming_elapsed >= 25:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            if not flipped_mode:
                flipped_mode = True
                sound_cycle_start = current_time
                sound_index = 0
            # Play error sounds in a loop every 0.3s
            if sound_cycle_start is None:
                sound_cycle_start = current_time
            if current_time - sound_cycle_start >= 0.3:
                winsound.PlaySound(sounds[sound_index], winsound.SND_ALIAS | winsound.SND_ASYNC)
                sound_index = (sound_index + 1) % len(sounds)
                sound_cycle_start = current_time
        else:
            flipped_mode = False
            sound_cycle_start = None
            sound_index = 0

        # Draw random "FlamingTime.exe" text every 0.10s, keep all previous texts visible for 10s
        if current_time - flaming_last_text > 0.10:
            x = np.random.randint(0, sw - 300)
            y = np.random.randint(0, sh - 60)
            flaming_text_positions.append((x, y, current_time))
            flaming_last_text = current_time

        flaming_text_positions = [
            (x, y, t) for (x, y, t) in flaming_text_positions if current_time - t < 10
        ]

        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        for x, y, t in flaming_text_positions:
            draw.text((x, y), "FlamingTime.exe", (255, 50, 0), font=font)

        img_bgrx = img.convert("RGBA")
        img_bytes = img_bgrx.tobytes("raw", "BGRA")

        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = sw
        bmi.bmiHeader.biHeight = -sh
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = win32con.BI_RGB
        bmi.bmiHeader.biSizeImage = 0
        bmi.bmiHeader.biXPelsPerMeter = 0
        bmi.bmiHeader.biYPelsPerMeter = 0
        bmi.bmiHeader.biClrUsed = 0
        bmi.bmiHeader.biClrImportant = 0

        gdi32.SetDIBitsToDevice(
            hdc, 0, 0, sw, sh, 0, 0, 0, sh,
            img_bytes,
            ctypes.byref(bmi),
            win32con.DIB_RGB_COLORS
        )
        time.sleep(0.01)
        continue

    # --- WHIRLPOOL MODE ---
    if elapsed >= 20:
        whirlpool_mode = True
    if whirlpool_mode and elapsed < 30:
        img = ImageGrab.grab(bbox=(0, 0, sw, sh)).convert("RGB")
        arr = np.array(img)
        y, x = np.indices((sh, sw))
        cx, cy = sw // 2, sh // 2
        dx_ = x - cx
        dy_ = y - cy
        r = np.sqrt(dx_**2 + dy_**2)
        theta = np.arctan2(dy_, dx_)

        whirl_elapsed = elapsed - 20
        max_swirl = 32
        swirl_strength = min(max_swirl, max_swirl * (whirl_elapsed / 3.0))
        swirl = theta + swirl_strength * np.exp(-r / 180) * (r / (sw // 2))**2.5

        xs = (cx + r * np.cos(swirl)).astype(np.int32)
        ys = (cy + r * np.sin(swirl)).astype(np.int32)
        mask = (xs >= 0) & (xs < sw) & (ys >= 0) & (ys < sh)
        result = np.zeros_like(arr)
        result[mask] = arr[ys[mask], xs[mask]]
        img = Image.fromarray(result)
        img_bgrx = img.convert("RGBA")
        img_bytes = img_bgrx.tobytes("raw", "BGRA")

        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = sw
        bmi.bmiHeader.biHeight = -sh
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = win32con.BI_RGB
        bmi.bmiHeader.biSizeImage = 0
        bmi.bmiHeader.biXPelsPerMeter = 0
        bmi.bmiHeader.biYPelsPerMeter = 0
        bmi.bmiHeader.biClrUsed = 0
        bmi.bmiHeader.biClrImportant = 0

        gdi32.SetDIBitsToDevice(
            hdc, 0, 0, sw, sh, 0, 0, 0, sh,
            img_bytes,
            ctypes.byref(bmi),
            win32con.DIB_RGB_COLORS
        )
        time.sleep(0.01)
        continue

    # --- HUE MODE ---
    if elapsed >= 10:
        hue_mode = True
    if hue_mode and elapsed < 20:
        img = ImageGrab.grab(bbox=(0, 0, sw, sh)).convert("RGB")
        arr = np.array(img.convert("HSV"))
        arr[..., 0] = (arr[..., 0].astype(int) + int((elapsed - 10) * 40)) % 256
        img = Image.fromarray(arr, "HSV").convert("RGB")
        img_bgrx = img.convert("RGBA")
        img_bytes = img_bgrx.tobytes("raw", "BGRA")

        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = sw
        bmi.bmiHeader.biHeight = -sh  # negative for top-down
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = win32con.BI_RGB
        bmi.bmiHeader.biSizeImage = 0
        bmi.bmiHeader.biXPelsPerMeter = 0
        bmi.bmiHeader.biYPelsPerMeter = 0
        bmi.bmiHeader.biClrUsed = 0
        bmi.bmiHeader.biClrImportant = 0

        gdi32.SetDIBitsToDevice(
            hdc, 0, 0, sw, sh, 0, 0, 0, sh,
            img_bytes,
            ctypes.byref(bmi),
            win32con.DIB_RGB_COLORS
        )
        time.sleep(0.01)
        continue

    # --- NOODLE MODE ---
    if elapsed >= 5:
        noodle_mode = True
    if noodle_mode and elapsed < 10:
        for y in range(0, sh, 4):
            offset = int(60 * math.sin(angle * 3 + y / 12.0))
            win32gui.BitBlt(hdc, 0, y, sw, 4, hdc, offset, y, win32con.SRCCOPY)
        angle += 0.25
        if current_time - last_invert >= 1:
            win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, win32con.NOTSRCCOPY)
            last_invert = current_time
        time.sleep(0.01)
        continue

    # --- DEFAULT MOVING MODE ---
    win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, dx, dy, win32con.SRCCOPY)
    dx = int(math.sin(angle) * 20)
    dy = int(math.cos(angle) * 20)
    angle += speed / 10
    if angle > math.pi:
        angle -= math.pi * 2
    if current_time - last_invert >= 1:
        win32gui.BitBlt(hdc, 0, 0, sw, sh, hdc, 0, 0, win32con.NOTSRCCOPY)
        last_invert = current_time

    time.sleep(0.01)