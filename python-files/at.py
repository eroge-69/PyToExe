import os
import time
import subprocess
import sys
import shutil
import winreg
import ctypes
import base64
import tempfile

# --- Configuration ---
# User-provided base64 wallpaper data
# This is decoded and saved to a temporary file for use as wallpaper.
WALLPAPER_BASE64 = "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"

# Second base64 image (used in webpage_urls)
WEBPAGE_BASE64_IMAGE = "data:image/jpeg;base64,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án6QFMABsPmlU8OOgRywJNTyFttP4ga5jmcnNLfcQvHq7C1zmncEtPmDC9pC8g4mEYmqB+275mfql2OL7VLihOKISuFTUBKHpRy1c0oj1jZXE4hcComTGokpNKfCzH03EQeYMiOoXseTYjXTY/wDaaD6xdeNhaXIuJnYf/bfdlo/h7eSnpXxtjxJgjUaYMReyyTGkGCtVQ4kw7myXtg91nMXUaXEjqY8lCx2Y/wBI+JKiNeZUqsEAM5rHTsJiIuVa4TFyfwWdcVYZa+CEtGe2+yyvstDhallkMtqQAr/CVSqePTj8uPa8LwAqTOM6bTOmbldxGJJEArA8Q1HCs2oSYLin3sPD4Zb7aGtSdUGoc0LCgzpduEbJcya5ov9VGIbrnqo8/ta9npd5a2BZWVPdRcsiN3waAuvE9OHd9ueIJhGaFWZm/SA7vCfg8bIRmvfAubzqa58LxviKvqxFVw51HfIx9F6pmmM0U31P2WOPqBb5wvGqriTJ9fNLujiGgp0piUpFDkkglCMgMWCnwmtT1QhNaiBNaiBBnQFzHC8dgiMCj4qoHXHK3slPhCetbl7y5rT2CytQWWgyGpNMDpZL5J6X8N9rarshsJ2TqhgIVF91B1LLC4LVeLIuEYA6O6tMnEsPyVXhZFUg/tfVJTdanLKBImLK21adjsh5PRHh+iHmjvDBdBiLnsq5jl3e6O/SZlQMbhA7cD81XYLPKLjZ49CCr3C4um79YLG/j8Zmpw+4HUwkHf4ZCYaWKp3PxDobH0K3tCmw7Ee4UpmCaQmnj78JfPz7GcyTH1IALHT5LV0g6J2JTaGBDdrKdpsrZzye3L5NzV9RTZvQc5hBMhJEWuqjJK7iPMx6rUV3D2VRlWCj1cXe5KTWf8ALps6/wqeOcbootpTeoZP8jfz+5eeEq94zx/iYl17N+Eem/wBVQF4RGQ5qdCZTcnyg1KF1IImhaFrDtRQhIjVUpwT0xdCDCB8XKgPdBkKVVIPooxCxp6c1AqfktaCR3lVrmdE/D1YcChqdh8a5WorVlGZWugNqSN0AvhS/Lqu3oXDOI+GFFzQaK8xY3VTw3j4crfiF/wBl/LY9lKz2pL322mRV5aLqwxLQQe6xnDeNgb2WkZiU8vpz7zf11kc74QpPc59KKT3C+kWJ6whUC6lRpUjh9TgWirUbuGA3IAuZWtxreYQ6FEOuRdafVPXPaTg6ODqOYGug6SSJewm4iZ81bUsvYHBrK7hzI1Ndb1QcJhmQJaEb9GYT9ldGZ6ce57+n4006QvVqOdya0iSeWwt5qqyShjqसुर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"


# Webpage URLs to open sequentially
# Note: The third URL is also a base64 image, which will be decoded and opened locally.
WEBPAGE_URLS = [
    "https://pbs.twimg.com/media/E2ajg41XIAg5tTc.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQirt-Q1ERwBu-d2uVQJu9Tvu7gl51VTHIyDQ&s",
    WEBPAGE_BASE64_IMAGE,
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRirAIu6-8v0XDUjIhf8d4nIZ-VcxtMdqeH_A&s",
    "https://i.pinimg.com/736x/79/66/47/7966477b39befe3e5d49331597dbc12e.jpg"
]

# Messages for Notepad instances
NOTEPAD_MESSAGES = [
    "do not forget to study",
    "remember you have an exam after 2 months",
    "do not forget to study",
    "do not forget to study",
    "do not forget to study",
    "do not forget to study",
    "do not forget to study",
    "do not forget to study",
    "do not forget to study",
    "do not forget to study"
]

NOTEPAD_INTERVAL = 9  # seconds between each Notepad launch
BROWSER_INTERVAL = 5  # seconds between each browser launch
# --- End Configuration ---

# Windows API constants for wallpaper management
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

def decode_base64_to_file(base64_string, filename_prefix):
    """
    Decodes a base64 string (potentially from a data URL) and saves it to a temporary file.
    Returns the path to the saved file or None on error.
    """
    try:
        # Extract the base64 part if it's a data URL (e.g., "data:image/jpeg;base64,...")
        if base64_string.startswith("data:image/"):
            header, encoded = base64_string.split(",", 1)
            # Infer file extension from the data URL header
            if "image/jpeg" in header:
                ext = ".jpg"
            elif "image/png" in header:
                ext = ".png"
            else:
                ext = ".tmp"  # Fallback extension
            full_filename = filename_prefix + ext
        else:
            encoded = base64_string
            # Assume JPG if no data URL header (common for plain base64 images)
            full_filename = filename_prefix + ".jpg"

        decoded_data = base64.b64decode(encoded)
        file_path = os.path.join(tempfile.gettempdir(), full_filename) # Use temp directory
        with open(file_path, "wb") as f:
            f.write(decoded_data)
        return file_path
    except Exception as e:
        print(f"Error decoding base64 to file '{filename_prefix}': {e}")
        return None

def set_wallpaper(image_path):
    """
    Sets the Windows desktop wallpaper using the SystemParametersInfoW API.
    `image_path` must be an absolute path to a supported image file (.bmp, .jpg, .gif, .png).
    """
    if not os.path.exists(image_path):
        print(f"Wallpaper image file not found: {image_path}")
        return

    try:
        # SystemParametersInfoW expects a wide string (UTF-16) for the path
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0, # uParam is 0 for SPI_SETDESKWALLPAPER
            image_path,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE # Flags to update settings and notify other apps
        )
        print(f"✅ Desktop wallpaper successfully set to: {image_path}")
    except Exception as e:
        print(f"❌ Error setting wallpaper: {e}")

def create_notepad_message_file(message, file_id):
    """
    Creates a temporary text file with the given message content.
    Returns the path to the created file or None on error.
    """
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"notepad_message_{file_id}.txt")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(message)
        return file_path
    except Exception as e:
        print(f"❌ Error creating Notepad message file '{file_path}': {e}")
        return None

def launch_notepad(message_file_path):
    """
    Launches a Notepad instance, opening the specified message file.
    """
    if not message_file_path:
        return
    try:
        # subprocess.Popen is non-blocking, allowing the script to continue immediately
        subprocess.Popen(["notepad.exe", message_file_path])
        print(f"  📝 Launched Notepad with: '{os.path.basename(message_file_path)}'")
    except Exception as e:
        print(f"❌ Error launching Notepad with '{message_file_path}': {e}")

def get_browser_path():
    """
    Detects and returns the executable path for Microsoft Edge or Google Chrome.
    Prioritizes Edge if both are found. Returns None if neither is found.
    """
    # Common installation paths for Edge
    edge_paths = [
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft", "Edge", "Application", "msedge.exe")
    ]
    # Common installation paths for Chrome
    chrome_paths = [
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe")
    ]

    for path in edge_paths:
        if os.path.exists(path):
            return path
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    return None

def launch_browser_url(browser_path, url):
    """
    Launches the specified browser with the given URL.
    If the URL is a data URL (base64 image), it decodes it to a temporary file
    and opens the local file in the browser.
    """
    if not browser_path:
        print("No compatible browser found to open URLs.")
        return

    # Handle data URLs by decoding them to a local file and opening that file
    if url.startswith("data:image/"):
        temp_image_path = decode_base64_to_file(url, f"webpage_img_{time.time()}")
        if temp_image_path:
            url_to_open = f"file:///{temp_image_path}" # Use file:// protocol for local files
        else:
            print(f"Could not decode data URL for browser: {url[:50]}...")
            return
    else:
        url_to_open = url

    try:
        subprocess.Popen([browser_path, url_to_open])
        print(f"  🌐 Launched browser ({os.path.basename(browser_path)}) with: '{url_to_open}'")
    except Exception as e:
        print(f"❌ Error launching browser with '{url_to_open}': {e}")

def add_to_startup():
    """
    Adds the current Python script to Windows startup using the Registry's Run key.
    Configures it to run silently in the background using `pythonw.exe`.
    """
    app_name = "StudyAutomationProgram"
    # Use 'pythonw.exe' for silent execution without a console window.
    # We construct the path by replacing 'python.exe' in the current executable path.
    python_exe = sys.executable.replace("python.exe", "pythonw.exe")
    if not os.path.exists(python_exe):
        print(f"⚠️ Warning: 'pythonw.exe' not found at '{python_exe}'. The script might run with a console window.")
        python_exe = sys.executable # Fallback to 'python.exe' if 'pythonw.exe' is missing

    # Get the absolute path of the current script to ensure it's found
    script_path = os.path.abspath(sys.argv[0])
    # The command to add to startup. Enclose paths in quotes to handle spaces.
    run_command = f'"{python_exe}" "{script_path}"'

    try:
        # Open the Run key under HKEY_CURRENT_USER
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        # Set the value with the application name and command
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, run_command)
        winreg.CloseKey(key)
        print(f"🚀 Program '{app_name}' successfully configured to run at Windows startup.")
        print(f"   Startup command: {run_command}")
    except Exception as e:
        print(f"❌ Error adding program to startup: {e}")

def main():
    """
    Main function to orchestrate wallpaper, Notepad, and browser automation.
    Runs in a perpetual loop until system shutdown.
    """
    print("--- Starting Windows Study Automation Program ---")

    # --- Initial Setup ---
    # 1. Set Wallpaper
    wallpaper_file_path = decode_base64_to_file(WALLPAPER_BASE64, "desktop_wallpaper")
    if wallpaper_file_path:
        set_wallpaper(wallpaper_file_path)
    else:
        print("Skipping wallpaper update as base64 data could not be decoded.")

    # 2. Add to Startup (this only needs to be done once)
    add_to_startup()

    # Pre-create Notepad message files to avoid doing it repeatedly in the loop
    notepad_message_files = []
    for i, msg in enumerate(NOTEPAD_MESSAGES):
        temp_file = create_notepad_message_file(msg, i + 1)
        if temp_file:
            notepad_message_files.append(temp_file)
    if not notepad_message_files:
        print("No Notepad message files could be created. Notepad automation will be skipped.")

    # Detect browser path once
    browser_path = get_browser_path()
    if not browser_path:
        print("⚠️ Warning: Neither Microsoft Edge nor Google Chrome was found. Browser automation will be skipped.")

    # --- Main Infinite Automation Loop ---
    cycle_count = 0
    try:
        while True: # Perpetual loop, terminates only on system shutdown
            cycle_count += 1
            print(f"\n--- Starting Automation Cycle {cycle_count} ---")

            # Notepad Automation Sequence
            if notepad_message_files:
                print("Initiating Notepad automation sequence...")
                for i, msg_file in enumerate(notepad_message_files):
                    launch_notepad(msg_file)
                    # Pause *between* Notepad launches, not after the very last one if it's followed by browser.
                    if i < len(notepad_message_files) - 1:
                        time.sleep(NOTEPAD_INTERVAL)
                time.sleep(NOTEPAD_INTERVAL) # Pause after the last notepad before browsers

            # Browser Automation Sequence
            if browser_path:
                print("Initiating Browser automation sequence...")
                for i, url in enumerate(WEBPAGE_URLS):
                    launch_browser_url(browser_path, url)
                    # Pause *between* browser launches
                    if i < len(WEBPAGE_URLS) - 1:
                        time.sleep(BROWSER_INTERVAL)

            print(f"--- Automation Cycle {cycle_count} completed. Restarting Notepad sequence... ---")
            # The loop continues, immediately starting the next Notepad sequence
            # as per the requirement for a perpetual loop until system shutdown.
    except KeyboardInterrupt:
        print("\nProgram interrupted by user (Ctrl+C). Exiting.")
    except Exception as e:
        print(f"\nAn unexpected error occurred in the main loop: {e}")
        print("The program will attempt to continue or exit gracefully.")

if __name__ == "__main__":
    main()

