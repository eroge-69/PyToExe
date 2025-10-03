# hand_sleep_headless.pyw  (run with pythonw.exe for no console window)
import os
import time
import platform
import ctypes
import cv2
import mediapipe as mp

# ===================== Config =====================
# "s0_sleep" = turn display off (Modern Standby will idle after)
# "hibernate" = full hibernate (resume session on power on)
MODE = "s0_sleep"          # change to "hibernate" if you prefer
CAM_INDEX = 0              # webcam index
FRAME_WIDTH = 640          # lower = less CPU
FRAME_HEIGHT = 480
FPS_LIMIT = 24             # cap processing rate
DEBOUNCE_SEC = 1.2         # avoid repeated triggers
MODEL_COMPLEXITY = 0       # 0 = fastest, 1 = default
MIN_DET_CONF = 0.6
MIN_TRK_CONF = 0.6

# ===================== Power actions =====================
def _turn_off_display_windows():
    """Turn off monitor (the practical 'sleep' on S0 devices)."""
    if platform.system() != "Windows":
        return False, "Not Windows"
    HWND_BROADCAST  = 0xFFFF
    WM_SYSCOMMAND   = 0x0112
    SC_MONITORPOWER = 0xF170
    SMTO_ABORTIFHUNG = 0x0002
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    try:
        # Use SendMessageTimeout so we don't hang on weird shells
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2,
            SMTO_ABORTIFHUNG, 2000, ctypes.byref(ctypes.c_ulong())
        )
        return True, "Display off"
    except Exception as e:
        return False, f"SendMessageTimeoutW failed: {e!r}"

def _hibernate_windows():
    """Force hibernate. Best-effort enable first."""
    if platform.system() != "Windows":
        return False, "Not Windows"
    try:
        os.system("powercfg -hibernate on")
    except Exception:
        pass
    rc = os.system("shutdown /h")
    return (rc == 0), f"shutdown /h rc={rc}"

def do_sleep_action():
    if MODE.lower() == "hibernate":
        return _hibernate_windows()
    return _turn_off_display_windows()

# ===================== Gesture logic =====================
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

            frame = cv2.flip(frame, 1)

            # Downscale if camera didn’t honor requested size
            h, w = frame.shape[:2]
            if w > FRAME_WIDTH:
                frame = cv2.resize(frame, (FRAME_WIDTH, int(FRAME_WIDTH * h / w)), interpolation=cv2.INTER_AREA)
                h, w = frame.shape[:2]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = hands.process(rgb)

            if res.multi_hand_landmarks:
                # only first hand (we limited to 1 anyway)
                hl = res.multi_hand_landmarks[0]
                pts = [(int(p.x * w), int(p.y * h)) for p in hl.landmark]

                if _middle_only_up(pts) and (time.time() - last_trigger) > DEBOUNCE_SEC:
                    last_trigger = time.time()

                    # Clean up resources before power action
                    cap.release()
                    hands.close()
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

if __name__ == "__main__":
    main()
