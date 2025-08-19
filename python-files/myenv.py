# Windows only — no third-party packages
# 功能：
# 1) 托盤圖示（右鍵 Exit）
# 2) y > TRIGGER_Y 區域：滾輪上/下 => Ctrl+Win+Left/Right
# 3) 右下角 (y > TRIGGER_Y 且 x > TRIGGER_X) 中鍵 => Win+Tab

import ctypes
import ctypes.wintypes as wt
import threading

# ====== 參數 ======
TRIGGER_Y = 1050
TRIGGER_X = 1320

# 鍵碼
VK_CONTROL = 0x11
VK_LWIN    = 0x5B
VK_TAB     = 0x09
VK_LEFT    = 0x25
VK_RIGHT   = 0x27

# Windows 常數/型別
user32  = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32
gdi32 = ctypes.windll.gdi32

WM_USER = 0x0400
WM_APP  = 0x8000
WM_DESTROY = 0x0002
WM_COMMAND = 0x0111
WM_CONTEXTMENU = 0x007B
WM_CLOSE = 0x0010
NIM_ADD = 0x00000000
NIM_MODIFY = 0x00000001
NIM_DELETE = 0x00000002
NIF_MESSAGE = 0x00000001
NIF_ICON = 0x00000002
NIF_TIP = 0x00000004
WM_MBUTTONDOWN = 0x0207
WM_MOUSEWHEEL = 0x020A

WH_MOUSE_LL = 14
WM_RBUTTONUP = 0x0205

MIIM_ID = 0x00000002
MIIM_STRING = 0x00000040
MIIM_FTYPE = 0x00000100
MFT_STRING = 0x00000000

IDC_ARROW = 32512
IDI_APPLICATION = 32512
LR_SHARED = 0x00008000

# 結構定義
class POINT(ctypes.Structure):
    _fields_ = [("x", wt.LONG), ("y", wt.LONG)]

class MSG(ctypes.Structure):
    _fields_ = [("hwnd", wt.HWND),
                ("message", wt.UINT),
                ("wParam", wt.WPARAM),
                ("lParam", wt.LPARAM),
                ("time", wt.DWORD),
                ("pt", POINT)]

class NOTIFYICONDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wt.DWORD),
        ("hWnd", wt.HWND),
        ("uID", wt.UINT),
        ("uFlags", wt.UINT),
        ("uCallbackMessage", wt.UINT),
        ("hIcon", wt.HICON),
        ("szTip", wt.WCHAR * 128),
        ("dwState", wt.DWORD),
        ("dwStateMask", wt.DWORD),
        ("szInfo", wt.WCHAR * 256),
        ("uTimeoutOrVersion", wt.UINT),
        ("szInfoTitle", wt.WCHAR * 64),
        ("dwInfoFlags", wt.DWORD),
        ("guidItem", wt.GUID),
        ("hBalloonIcon", wt.HICON),
    ]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", POINT),
        ("mouseData", wt.DWORD),
        ("flags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwExtraInfo", wt.ULONG_PTR),
    ]

# Menu item
class MENUITEMINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wt.UINT),
        ("fMask", wt.UINT),
        ("fType", wt.UINT),
        ("fState", wt.UINT),
        ("wID", wt.UINT),
        ("hSubMenu", wt.HMENU),
        ("hbmpChecked", wt.HBITMAP),
        ("hbmpUnchecked", wt.HBITMAP),
        ("dwItemData", wt.ULONG_PTR),
        ("dwTypeData", wt.LPWSTR),
        ("cch", wt.UINT),
        ("hbmpItem", wt.HBITMAP),
    ]

# SendInput
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wt.WORD),
        ("wScan", wt.WORD),
        ("dwFlags", wt.DWORD),
        ("time", wt.DWORD),
        ("dwExtraInfo", wt.ULONG_PTR),
    ]

class INPUT(ctypes.Structure):
    class _I(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT)]
    _anonymous_ = ("i",)
    _fields_ = [("type", wt.DWORD), ("i", _I)]

# ====== 全域狀態 ======
hInstance = kernel32.GetModuleHandleW(None)
WM_TRAYICON = WM_APP + 1
EXIT_CMD_ID = 1001

# 建隱藏視窗（托盤需要視窗接收回呼訊息）
WNDPROC = ctypes.WINFUNCTYPE(wt.LRESULT, wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM)

def create_window(class_name="MyHiddenWindow"):
    # 註冊視窗類別
    WNDCLASS = ctypes.WINFUNCTYPE(None)  # dummy, we use the WNDCLASSEXW via winapi helpers
    class WNDCLASSEX(ctypes.Structure):
        _fields_ = [
            ("cbSize", wt.UINT),
            ("style", wt.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", wt.INT),
            ("cbWndExtra", wt.INT),
            ("hInstance", wt.HINSTANCE),
            ("hIcon", wt.HICON),
            ("hCursor", wt.HCURSOR),
            ("hbrBackground", wt.HBRUSH),
            ("lpszMenuName", wt.LPCWSTR),
            ("lpszClassName", wt.LPCWSTR),
            ("hIconSm", wt.HICON),
        ]

    def py_wnd_proc(hWnd, msg, wParam, lParam):
        if msg == WM_COMMAND:
            if wParam == EXIT_CMD_ID:
                user32.PostMessageW(hWnd, WM_CLOSE, 0, 0)
        elif msg == WM_TRAYICON:
            # 右鍵放開 => 顯示選單
            if lParam == WM_RBUTTONUP:
                show_tray_menu(hWnd)
        elif msg == WM_CLOSE:
            remove_tray_icon(hWnd)
            user32.DestroyWindow(hWnd)
        elif msg == WM_DESTROY:
            user32.PostQuitMessage(0)
        return user32.DefWindowProcW(hWnd, msg, wParam, lParam)

    wnd_proc = WNDPROC(py_wnd_proc)

    # 準備 WNDCLASSEX
    wc = WNDCLASSEX()
    wc.cbSize = ctypes.sizeof(WNDCLASSEX)
    wc.style = 0
    wc.lpfnWndProc = wnd_proc
    wc.cbClsExtra = 0
    wc.cbWndExtra = 0
    wc.hInstance = hInstance
    wc.hIcon = user32.LoadIconW(None, IDI_APPLICATION)
    wc.hCursor = user32.LoadCursorW(None, IDC_ARROW)
    wc.hbrBackground = 0
    wc.lpszMenuName = None
    wc.lpszClassName = class_name
    wc.hIconSm = user32.LoadIconW(None, IDI_APPLICATION)

    atom = user32.RegisterClassExW(ctypes.byref(wc))
    if not atom:
        raise ctypes.WinError()

    hwnd = user32.CreateWindowExW(
        0, class_name, "Hidden", 0, 0, 0, 0, 0, None, None, hInstance, None
    )
    if not hwnd:
        raise ctypes.WinError()
    return hwnd, wnd_proc  # keep wnd_proc referenced

def add_tray_icon(hWnd, tooltip="Tray Helper"):
    nid = NOTIFYICONDATA()
    nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
    nid.hWnd = hWnd
    nid.uID = 1
    nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
    nid.uCallbackMessage = WM_TRAYICON
    nid.hIcon = user32.LoadIconW(None, IDI_APPLICATION)
    ctypes.memmove(nid.szTip, tooltip, len(tooltip)*2)
    if not shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid)):
        raise ctypes.WinError()

def remove_tray_icon(hWnd):
    nid = NOTIFYICONDATA()
    nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
    nid.hWnd = hWnd
    nid.uID = 1
    shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))

def show_tray_menu(hWnd):
    hMenu = user32.CreatePopupMenu()
    # 加入 Exit 項
    mii = MENUITEMINFO()
    mii.cbSize = ctypes.sizeof(MENUITEMINFO)
    mii.fMask = MIIM_ID | MIIM_STRING | MIIM_FTYPE
    mii.fType = MFT_STRING
    mii.wID = EXIT_CMD_ID
    text = "Exit"
    mii.dwTypeData = wt.LPWSTR(text)
    mii.cch = len(text)
    user32.InsertMenuItemW(hMenu, 0, True, ctypes.byref(mii))

    # 在滑鼠位置彈出
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    user32.SetForegroundWindow(hWnd)
    user32.TrackPopupMenu(hMenu, 0, pt.x, pt.y, 0, hWnd, None)
    user32.DestroyMenu(hMenu)

# ====== SendInput: 模擬按鍵 ======
def press_combo(mods, key):
    inputs = []
    def keydown(vk):
        ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=0, time=0, dwExtraInfo=0)
        inp = INPUT(type=INPUT_KEYBOARD, ki=ki)
        inputs.append(inp)
    def keyup(vk):
        ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)
        inp = INPUT(type=INPUT_KEYBOARD, ki=ki)
        inputs.append(inp)

    # mods down
    for m in mods:
        keydown(m)
    # key down/up
    keydown(key)
    keyup(key)
    # mods up (reverse)
    for m in reversed(mods):
        keyup(m)

    arr = (INPUT * len(inputs))(*inputs)
    user32.SendInput(len(inputs), ctypes.byref(arr), ctypes.sizeof(INPUT))

# ====== 滑鼠全域 hook ======
LowLevelMouseProc = ctypes.WINFUNCTYPE(wt.LRESULT, wt.INT, wt.WPARAM, wt.LPARAM)
mouse_hook_handle = None

def HIWORD(dword):
    return (dword >> 16) & 0xFFFF

def signed_short(val):
    return val - 0x10000 if val & 0x8000 else val

@LowLevelMouseProc
def mouse_proc(nCode, wParam, lParam):
    if nCode == 0:  # HC_ACTION
        ms = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        x, y = ms.pt.x, ms.pt.y

        if wParam == WM_MOUSEWHEEL and y > TRIGGER_Y:
            delta = signed_short(HIWORD(ms.mouseData))
            if delta > 0:
                # 上滾：Ctrl + Win + Left
                press_combo([VK_CONTROL, VK_LWIN], VK_LEFT)
            elif delta < 0:
                # 下滾：Ctrl + Win + Right
                press_combo([VK_CONTROL, VK_LWIN], VK_RIGHT)

        elif wParam == WM_MBUTTONDOWN and y > TRIGGER_Y and x > TRIGGER_X:
            # 中鍵：Win + Tab
            press_combo([VK_LWIN], VK_TAB)

    # 傳給下一個 hook
    return user32.CallNextHookEx(mouse_hook_handle, nCode, wParam, lParam)

def start_mouse_hook():
    global mouse_hook_handle
    mouse_hook_handle = user32.SetWindowsHookExW(
        WH_MOUSE_LL, mouse_proc, kernel32.GetModuleHandleW(None), 0
    )
    if not mouse_hook_handle:
        raise ctypes.WinError()

    # 獨立訊息迴圈以保持 hook 存活
    msg = MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

# ====== 主執行：建立托盤 + 啟動 hook ======
def main():
    hwnd, _wndproc_keep = create_window()
    add_tray_icon(hwnd, "Tray Helper (no third-party)")

    # 滑鼠 hook 放在子執行緒，主執行緒跑視窗訊息
    t = threading.Thread(target=start_mouse_hook, daemon=True)
    t.start()

    # 主視窗訊息迴圈
    msg = MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

if __name__ == "__main__":
    main()
