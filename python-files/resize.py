import time
import threading
try:
    import win32gui
    import win32con
    import win32api
except Exception as e:
    print("Missing pywin32. Install with: pip install pywin32")
    raise
try:
    import pyautogui
except Exception as e:
    print("Missing pyautogui. Install with: pip install pyautogui")
    raise

pyautogui.FAILSAFE = True
CLICK_OFF_X = 799
CLICK_OFF_Y = 618
SCAN_INTERVAL = 20
CLICK_DELAY = 0.2
START_X_OFFSET = 300
STEP_X = 1
STEP_Y = 1
tracked = {}
tracked_lock = threading.Lock()
stop_event = threading.Event()

def enum_roblox_windows():
    result = []
    def _cb(hwnd, lparam):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title == "Roblox":
                result.append(hwnd)
    win32gui.EnumWindows(_cb, None)
    return result

def move_and_register(all_hwnds):
    with tracked_lock:
        current_count = len(tracked)
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        xPos = screen_w - START_X_OFFSET - current_count * STEP_X
        yPos = 0 + current_count * STEP_Y
        for hwnd in all_hwnds:
            if hwnd in tracked:
                tracked[hwnd]['last_seen'] = time.time()
                continue
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            except Exception:
                continue
            w = right - left
            h = bottom - top
            if xPos + w > screen_w:
                xPos = screen_w - w
            if yPos + h > screen_h:
                yPos = screen_h - h
            try:
                win32gui.MoveWindow(hwnd, int(xPos), int(yPos), int(w), int(h), True)
            except Exception:
                pass
            tracked[hwnd] = {'x': int(xPos), 'y': int(yPos), 'w': int(w), 'h': int(h), 'last_seen': time.time()}
            xPos -= STEP_X
            yPos += STEP_Y
        existing = set(all_hwnds)
        for hwnd in list(tracked.keys()):
            if hwnd not in existing:
                del tracked[hwnd]

def scanner_loop():
    while not stop_event.is_set():
        hwnds = enum_roblox_windows()
        if hwnds:
            move_and_register(hwnds)
        for _ in range(int(SCAN_INTERVAL)):
            if stop_event.is_set():
                break
            time.sleep(1)

def clicker_loop():
    while not stop_event.is_set():
        with tracked_lock:
            has = bool(tracked)
        if not has:
            time.sleep(1)
            continue
        with tracked_lock:
            hwnds = list(tracked.keys())
        for hwnd in hwnds:
            if stop_event.is_set():
                break
            try:
                if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                    with tracked_lock:
                        if hwnd in tracked:
                            del tracked[hwnd]
                    continue
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                except Exception:
                    pass
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except Exception:
                    try:
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    except Exception:
                        pass
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                click_x = int(left + CLICK_OFF_X)
                click_y = int(top + CLICK_OFF_Y)
                screen_w = win32api.GetSystemMetrics(0)
                screen_h = win32api.GetSystemMetrics(1)
                if 0 <= click_x <= screen_w and 0 <= click_y <= screen_h:
                    pyautogui.click(x=click_x, y=click_y)
                time.sleep(CLICK_DELAY)
            except Exception:
                with tracked_lock:
                    if hwnd in tracked:
                        del tracked[hwnd]
                continue

def main():
    try:
        try:
            import keyboard
            keyboard.add_hotkey('f6', lambda: stop_event.set())
            print("Press F6 to stop (keyboard module detected). Ctrl+C also stops.")
        except Exception:
            print("Press Ctrl+C to stop. Install 'keyboard' to enable F6 to stop: pip install keyboard")
        initial = enum_roblox_windows()
        if not initial:
            print("No Roblox windows found. Waiting for at least one...")
            while not stop_event.is_set():
                time.sleep(2)
                hw = enum_roblox_windows()
                if hw:
                    move_and_register(hw)
                    break
        else:
            move_and_register(initial)
        scanner = threading.Thread(target=scanner_loop, daemon=True)
        clicker = threading.Thread(target=clicker_loop, daemon=True)
        scanner.start()
        clicker.start()
        print("Started scanning and clicking. Press F6 or Ctrl+C to stop.")
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        stop_event.set()
        print("Stopping... Please wait a moment.")

if __name__ == "__main__":
    main()
