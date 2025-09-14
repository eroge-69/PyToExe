import os
import ctypes
import winreg


import urllib.request
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Requesting administrator privileges...")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, __file__, None, 1)
    sys.exit()
    
# Download image
image_url = "https://images3.alphacoders.com/134/1340734.png"  # Replace with your image URL
image_path = os.path.join(os.environ["USERPROFILE"], "1340734.png")
urllib.request.urlretrieve(image_url, image_path)

# Set wallpaper
ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)

# Edit registry to block wallpaper changes
key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop"
try:
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
    winreg.SetValueEx(key, "NoChangingWallPaper", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)
except Exception as e:
    print(f"Registry edit failed: {e}")

print("Wallpaper set and changes blocked.")

