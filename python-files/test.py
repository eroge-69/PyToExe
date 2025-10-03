# hand_sleep_headless.py  (build with PyInstaller --windowed)
import os
import time
import platform
import ctypes
import sys
from typing import Tuple

# ===================== Config =====================
# "s0_sleep" = turn display off (Modern Standby will idle after)
# "hibernate" = full hibernate (resume session on power on)
MODE = os.getenv("HS_MODE", "s0_sleep")  # "s0_sleep" or "hibernate"
CAM_INDEX = int(os.getenv("HS_CAM_INDEX", "0"))
FRAME_WIDTH = int(os.getenv("HS_WIDTH", "640"))     # lower = less CPU
FRAME_HEIGHT = int(os.getenv("HS_HEIGHT", "480"))
FPS_LIMIT = int(os.getenv("HS_FPS", "24"))          # cap processing rate
DEBOUNCE_SEC = float(os.getenv("HS_DEBOUNCE", "1.2"))
MODEL_COMPLEXITY = int(os.getenv("HS_MODEL_COMPLEXITY", "0"))  # 0 = fastest, 1 = default
MIN_DET_CONF = float(os.getenv("HS_MIN_DET", "0.6"))
MIN_TRK_CONF = float(os.getenv("HS_MIN_TRK", "0.6"))
USE_SINGLE_INSTANCE = os.getenv("HS_SINGLE_INSTANCE", "1") == "1"
MUTEX_NAME = "Global\\hand_sleep_headless_mutex"

# ===================== Single-instance (Windows only, safe no-op elsewhere) =====================
class SingleInstance:
    """Prevents multiple concurrent instances on Windows (no-op on other OS)."""
    def __init__(self, name: str):
        self.handle = None
        self._ok = True
        if platform.system() == "Windows":
            self.handle = ctypes.windll.kernel32.CreateMutexW(None, ctypes.c_bool(True), name)
            last_err = ctypes.windll.kernel32.GetLastError()
            # ERROR_ALREADY_EXISTS = 183
            if last_err == 183:
                self._ok = False

    @property
    def ok(self) -> bool:
        return self._ok

    def close(self):
        if self.handle:
            ctypes.windll.kernel32.ReleaseMutex(self.handle)
            ctypes.windll.kernel32.CloseHandle(self.handle)
            self.handle = None

# ===================== Power actions =====================
def _turn_off_display_windows() -> Tuple[bool, str]:
    """Turn off monitor (the practical 'sleep' on S0 devices)."""
    if platform.system() != "Windows":
        return False, "Not Windows"
    HWND_BROADCAST  = 0xFFFF
    WM_SYSCOMMAND   = 0x0112
    SC_MONITORPOWER = 0xF170
    SMTO_ABORTIFHUNG = 0x0002
    try:
        # Use SendMessageTimeout so we don't hang on weird shells
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2,
            SMTO_ABORTIFHUNG, 2000, ctypes.byref(ctypes.c_ulong())
        )
        return True, "Display off"
    except Exception as e:
        return False, f"SendMessageTimeoutW failed: {e!r}"

def _hibernate_windows() -> Tuple[bool, str]:
    """Force hibernate. Best-effort enable first."""
    if platform.system() != "Windows":
        return False, "Not Windows"
    try:
        os.system("powercfg -hibernate on")
    except Exception:
        pass
    rc = os.system("shutdown /h")
    return (rc == 0), f"shutdown /h rc={rc}"

def do_sleep_action() -> Tuple[bool, str]:
    if MODE.lower() == "hibernate":
        return _hibernate_windows()
    return _turn_off_display_windows()

# ===================== Gesture helpers =====================
def _finger_up(lm, tip, pip):
    # y increases downward; 'up' means tip y < pip y
    return lm[tip][1] < lm[pip][1]

def _middle_only_up(lm):
    idx   = _finger_up(lm, 8, 6)
    mid   = _finger_up(lm, 12, 10)
    ring  = _finger_up(lm, 16, 14)
    pinky = _finger_up(lm, 20, 18)
    return mid and not idx and not ring and not pinky

# ===================== Main loop (headless) =====================
def main():
    # Optional single-instance guard (Windows)
    instance = None
    if USE_SINGLE_INSTANCE:
        instance = SingleInstance(MUTEX_NAME)
        if not instance.ok:
            # Another instance is running; exit quietly
            return

    try:
        # Lazy imports (friendlier to EXE packagers)
        import cv2
        import mediapipe as mp

        cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
        # Best-effort lower resource usage
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, FPS_LIMIT)

        if not cap.isOpened():
            return  # silent fail (no popups)

        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=MODEL_COMPLEXITY,
            min_detection_confidence=MIN_DET_CONF,
            min_tracking_confidence=MIN_TRK_CONF,
        )

        last_trigger = 0.0
        frame_interval = 1.0 / max(1, FPS_LIMIT)

        try:
            while True:
                start = time.time()
                ok, frame = cap.read()
                if not ok:
                    break

                # Mirror
                frame = cv2.flip(frame, 1)

                # Downscale if camera didn’t honor requested size
                h, w = frame.shape[:2]
                if w > FRAME_WIDTH:
                    new_h = int(FRAME_WIDTH * h / w)
                    if new_h < 1:
                        new_h = 1
                    frame = cv2.resize(frame, (FRAME_WIDTH, new_h), interpolation=cv2.INTER_AREA)
                    h, w = frame.shape[:2]

                # Process
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = hands.process(rgb)

                if res.multi_hand_landmarks:
                    hl = res.multi_hand_landmarks[0]
                    pts = [(int(p.x * w), int(p.y * h)) for p in hl.landmark]

                    if _middle_only_up(pts) and (time.time() - last_trigger) > DEBOUNCE_SEC:
                        last_trigger = time.time()

                        # Clean up resources before power action
                        try:
                            cap.release()
                        except Exception:
                            pass
                        try:
                            hands.close()
                        except Exception:
                            pass

                        # small delay so camera driver fully releases
                        time.sleep(0.15)

                        # Do the action (display off or hibernate)
                        do_sleep_action()
                        # Exit after one successful trigger
                        return

                # simple frame pacing
                elapsed = time.time() - start
                if elapsed < frame_interval:
                    time.sleep(frame_interval - elapsed)
        finally:
            try:
                cap.release()
            except Exception:
                pass
            try:
                hands.close()
            except Exception:
                pass
    finally:
        if instance is not None:
            instance.close()

if __name__ == "__main__":
    # On Windows, PyInstaller + --windowed will hide console automatically.
    # This file produces a clean, GUI-less background process.
    main()
