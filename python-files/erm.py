
def get_foreground_window():
    import win32gui
    hwnd = win32gui.GetForegroundWindow()
    return hwnd

def show_message_box(title="Title", message="Message"):
    import win32gui
    import win32con
    hwnd = get_foreground_window()
    win32gui.MessageBox(hwnd, message, title, win32con.MB_OK)


def move_window(hwnd, x, y, w, h):
    import win32gui
    import win32con
    win32gui.MoveWindow(hwnd, x, y, w, h, True)


def get_window_rect(hwnd):
    import win32gui
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    return left, top, width, height
