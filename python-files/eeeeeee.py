import os
import ctypes
from PIL import Image
import win32ui
import win32gui
import win32con

def extract_icons_from_dll(dll_path, save_dir="extracted_icons"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Load DLL/EXE file
    large, small = win32gui.ExtractIconEx(dll_path, -1)
    icon_count = len(large) + len(small)
    print(f"Found {icon_count} icons in {dll_path}")

    # Extract each icon
    idx = 0
    for hicon in large + small:
        # Get icon info
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, 64, 64)
        hdc = hdc.CreateCompatibleDC()

        hdc.SelectObject(hbmp)
        win32gui.DrawIconEx(hdc.GetSafeHdc(), 0, 0, hicon, 64, 64, 0, None, win32con.DI_NORMAL)

        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)

        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        save_path = os.path.join(save_dir, f"icon_{idx}.png")
        img.save(save_path)
        print(f"Saved {save_path}")

        # Cleanup
        win32gui.DestroyIcon(hicon)
        idx += 1


if __name__ == "__main__":
    dll_file = r"C:\Windows\System32\shell32.dll"  # Example DLL
    extract_icons_from_dll(dll_file)
