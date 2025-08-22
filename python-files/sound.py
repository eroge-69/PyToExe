import soundcard as sc
import numpy as np
import pygame
import random
import ctypes

# ------------------ Config ------------------
SAMPLERATE = 44100
CHUNK = 1024
OPACITY_TRANSPARENT = 0.90  # 0.0..1.0 when transparent is ON
# -------------------------------------------

pygame.init()
screen = pygame.display.set_mode((1300, 600), pygame.RESIZABLE)   #for starting screen size
pygame.display.set_caption("Rohan's Music Visualizer")

# ---- Helpers for always-on-top & transparency (Windows) ----
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
LWA_ALPHA = 0x2

# Try SDL2 Window API if available (Pygame 2.0+)
try:
    from pygame._sdl2.video import Window
    _window_obj = Window.from_display_module()
except Exception:
    _window_obj = None


def _get_hwnd():
    info = pygame.display.get_wm_info()
    return info.get("window")


def set_topmost(top=True):
    try:
        hwnd = _get_hwnd()
        if hwnd:
            ctypes.windll.user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST if top else HWND_NOTOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE,
            )
    except Exception:
        pass


def set_opacity(alpha: float):
    """Set whole-window opacity. Uses SDL2 Window if available, otherwise Win32 layered window."""
    a = max(0.0, min(1.0, float(alpha)))
    # First try SDL2 Window API (cleaner)
    if _window_obj is not None:
        try:
            _window_obj.opacity = a
            return
        except Exception:
            pass
    # Fallback: Win32 layered window
    try:
        hwnd = _get_hwnd()
        if hwnd:
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
            ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(a * 255), LWA_ALPHA)
    except Exception:
        pass

# Make window always on top by default
set_topmost(True)
# Start fully opaque
set_opacity(1.0)

# Audio capture (loopback from default speaker)
mic = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)

with mic.recorder(samplerate=SAMPLERATE, channels=2, blocksize=CHUNK) as recorder:
    running = True
    hue = random.randint(0, 360)
    flash_timer = 0
    transparent = False
    fullscreen = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:  # toggle fullscreen
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                    # Reacquire SDL2 window object after mode change
                    try:
                        from pygame._sdl2.video import Window
                        _window_obj = Window.from_display_module()
                    except Exception:
                        _window_obj = None
                    # Re-apply topmost & current opacity after mode switch
                    set_topmost(True)
                    set_opacity(OPACITY_TRANSPARENT if transparent else 1.0)
                elif event.key == pygame.K_t:  # toggle transparency
                    transparent = not transparent
                    set_opacity(OPACITY_TRANSPARENT if transparent else 1.0)

        # Record audio
        data = recorder.record(numframes=CHUNK)
        volume = np.linalg.norm(data)

        # Music detected
        if volume > 5:
            brightness = min(1.0, volume * 0.05)
            if volume > 30:  # Beat punch
                brightness = 1.0
            if volume > 60:  # Flash mode
                flash_timer = 3

            # Random hue jumps when louder; small jitter otherwise
            if volume > 10: #good for now try 15 if not working good
                hue = random.randint(0, 360)
            else:
                hue = (hue + random.choice([1, 2, 3, -1, -2])) % 360
        else:
            # No music → gentle random drift
            brightness = 0.5
            hue = (hue + random.choice([1, -1])) % 360

        # Flash handling
        if flash_timer > 0:
            color = (255, 255, 255)
            flash_timer -= 1
        else:
            base_color = pygame.Color(0)
            base_color.hsva = (hue, 100, brightness * 100)
            color = (base_color.r, base_color.g, base_color.b)

        screen.fill(color)
        pygame.display.flip()

pygame.quit()
