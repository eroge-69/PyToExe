import ctypes
from ctypes import wintypes

# Fehlende Typen ergänzen
wintypes.HCURSOR = wintypes.HANDLE
wintypes.HICON = wintypes.HANDLE

# Konstanten
WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_VISIBLE = 0x10000000
CW_USEDEFAULT = 0x80000000
WHITE_BRUSH = 0
WM_DESTROY = 0x0002
WM_PAINT = 0x000F
WM_COMMAND = 0x0111

IDI_APPLICATION = 32512
IDC_ARROW = 32512

# Fenster-Control-Klassen
WC_EDIT = "Edit"
WC_BUTTON = "Button"
WC_STATIC = "Static"

# IDs
ID_BUTTON_SUCHEN = 1001
ID_EDIT_EINGABE = 1002

# DLLs laden
user32 = ctypes.WinDLL('user32', use_last_error=True)
gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
shell32 = ctypes.WinDLL('shell32', use_last_error=True)

# Typ-Definitionen
user32.DefWindowProcW.restype = ctypes.c_longlong
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.CreateWindowExW.restype = wintypes.HWND

# Structures
class POINT(ctypes.Structure):
    _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]

class MSG(ctypes.Structure):
    _fields_ = [
        ('hwnd', wintypes.HWND),
        ('message', wintypes.UINT),
        ('wParam', wintypes.WPARAM),
        ('lParam', wintypes.LPARAM),
        ('time', wintypes.DWORD),
        ('pt', POINT),
    ]

class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ('style', wintypes.UINT),
        ('lpfnWndProc', ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)),
        ('cbClsExtra', ctypes.c_int),
        ('cbWndExtra', ctypes.c_int),
        ('hInstance', wintypes.HINSTANCE),
        ('hIcon', wintypes.HICON),
        ('hCursor', wintypes.HCURSOR),
        ('hbrBackground', wintypes.HBRUSH),
        ('lpszMenuName', wintypes.LPCWSTR),
        ('lpszClassName', wintypes.LPCWSTR),
    ]

class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ('hdc', wintypes.HDC),
        ('fErase', wintypes.BOOL),
        ('rcPaint', wintypes.RECT),
        ('fRestore', wintypes.BOOL),
        ('fIncUpdate', wintypes.BOOL),
        ('rgbReserved', ctypes.c_byte * 32),
    ]

# Handles
edit_handle = None
button_handle = None

def open_link_from_input(hwnd):
    """Holt Eingabe, prüft und öffnet URL im Browser."""
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(edit_handle, buffer, 256)
    eingabe = buffer.value.strip()

    if not eingabe.isdigit():
        user32.MessageBoxW(hwnd, "Bitte eine gültige Zahl eingeben.", "Fehler", 0)
        return

    base_url = "https://www.gesetze-im-internet.de/bgb/__"
    full_url = base_url + eingabe + ".html"

    shell32.ShellExecuteW(None, "open", full_url, None, None, 1)

@ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
def wnd_proc(hwnd, msg, wparam, lparam):
    if msg == WM_PAINT:
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
        user32.EndPaint(hwnd, ctypes.byref(ps))
        return 0

    elif msg == WM_COMMAND:
        control_id = wparam & 0xFFFF
        notification_code = (wparam >> 16) & 0xFFFF

        # Wenn Button oder Enter gedrückt
        if control_id in (ID_BUTTON_SUCHEN, ID_EDIT_EINGABE) and notification_code in (0, 1):
            open_link_from_input(hwnd)
            return 0

    elif msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0

    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

def main():
    global edit_handle, button_handle

    hInstance = kernel32.GetModuleHandleW(None)
    className = "GesetzSuchFenster"

    wndclass = WNDCLASS()
    wndclass.lpfnWndProc = wnd_proc
    wndclass.hInstance = hInstance
    wndclass.lpszClassName = className
    wndclass.hbrBackground = gdi32.GetStockObject(WHITE_BRUSH)
    wndclass.hCursor = user32.LoadCursorW(None, IDC_ARROW)
    wndclass.hIcon = user32.LoadIconW(None, IDI_APPLICATION)

    if not user32.RegisterClassW(ctypes.byref(wndclass)):
        raise ctypes.WinError(ctypes.get_last_error())

    hwnd = user32.CreateWindowExW(
        0,
        className,
        "§-Suche im BGB (WinAPI, kein tkinter)",
        WS_OVERLAPPEDWINDOW | WS_VISIBLE,
        200, 200, 600, 180,
        None, None, hInstance, None
    )

    # Optional: Label (statisch)
    user32.CreateWindowExW(
        0,
        WC_STATIC,
        "Gib eine Paragraphenzahl ein:",
        0x50000000 | WS_VISIBLE,  # WS_CHILD | WS_VISIBLE
        20, 20, 250, 20,
        hwnd,
        None,
        hInstance,
        None
    )

    # Eingabefeld
    edit_handle = user32.CreateWindowExW(
        0,
        WC_EDIT,
        "",
        0x50010000 | WS_VISIBLE,  # WS_CHILD | WS_VISIBLE | WS_BORDER
        20, 50, 300, 25,
        hwnd,
        ctypes.c_void_p(ID_EDIT_EINGABE),
        hInstance,
        None
    )

    # Button
    button_handle = user32.CreateWindowExW(
        0,
        WC_BUTTON,
        "Suchen",
        0x50010000 | WS_VISIBLE,  # WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON
        340, 50, 100, 25,
        hwnd,
        ctypes.c_void_p(ID_BUTTON_SUCHEN),
        hInstance,
        None
    )

    # Nachrichtenschleife
    msg = MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

if __name__ == '__main__':
    main()
