import ctypes
import winreg
import os
from PIL import Image
from tkinter import messagebox
import tkinter as tk


def show_message():
    # Create and hide the main tkinter window
    root = tk.Tk()
    root.withdraw()

    # Show message box
    messagebox.showinfo("petőfi sándor aktiválva", "nayrel made you pink :P")


def create_pink_wallpaper():
    #
    width = 1920
    height = 1080
    pink_color = (255, 192, 203)  #

    # d
    image = Image.new('RGB', (width, height), pink_color)

    # r
    wallpaper_path = os.path.join(os.path.expanduser('~'), 'pink_wallpaper.png')
    image.save(wallpaper_path)
    return wallpaper_path


def set_pink_theme():
    try:
        # C
        wallpaper_path = create_pink_wallpaper()

        # r
        SPI_SETDESKWALLPAPER = 0x0014
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper_path, 3)

        # )
        registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"

        # Enable color personalization
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "ColorPrevalence", 0, winreg.REG_DWORD, 1)

        #
        accent_registry_path = r"SOFTWARE\Microsoft\Windows\DWM"
        pink_color_value = 0xFF1493  # Deep Pink in hex
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, accent_registry_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "AccentColor", 0, winreg.REG_DWORD, pink_color_value)


        show_message()

        print("Successfully set pink theme and wallpaper!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":

    set_pink_theme()