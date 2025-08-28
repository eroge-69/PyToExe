# insta_autoscroll.py
#
# Description:
# This script automates watching Instagram Reels in a web browser. It launches
# the browser, navigates to Reels, and then enters a loop to automatically
# scroll at the precise end of each video.
#
# Author: Gemini
# Version: 5.0 (Final Production Version)
#
# Dependencies:
# pip install pyautogui keyboard pillow yt-dlp pyperclip

import time
import keyboard
import pyautogui
import yt_dlp
import pyperclip

# --- Configuration ---

# Key to press to stop the automation.
STOP_KEY = 'q'

# --- 1. Instagram Launch and Navigation (Browser Version) ---

def launch_and_navigate():
    """
    Launches a web browser, navigates to Instagram Reels, and performs setup clicks.
    """
    print("Step 1: Launching Browser and navigating to Instagram Reels...")
    try:
        # === USER-PROVIDED COORDINATES ===
        # Ensure these are correct for your screen and browser window size.
        browser_name = "brave" # or "chrome", "firefox", etc.
        reels_tab_coords = (157, 762)
        unmute_coords = (1932, 268)
        focus_window_coords = (2358, 878) # This is also used later for refocusing

        # Launch the browser
        pyautogui.press('win')
        time.sleep(1)
        pyautogui.write(browser_name, interval=0.1)
        time.sleep(1.5)
        pyautogui.press('enter')
        print(f"{browser_name.capitalize()} launched. Waiting 8 seconds for it to open...")
        time.sleep(6)

        # Navigate to Instagram
        pyautogui.write('instagram.com', interval=0.1)
        pyautogui.press('enter')
        print("Navigating to Instagram.com. Waiting 8 seconds for the page to load...")
        time.sleep(6)

        # Perform the initial setup clicks
        print("Clicking on the Reels tab...")
        pyautogui.click(reels_tab_coords)
        time.sleep(4)

        print("Clicking to unmute the video...")
        pyautogui.click(unmute_coords)
        time.sleep(0.5)

        print("Performing final click to focus the window...")
        pyautogui.click(focus_window_coords)

        print("Initial navigation complete.")
        return True
    except Exception as e:
        print(f"An error occurred during launch/navigation: {e}")
        return False

# --- 2. Current Reel URL Extraction ---

def get_current_reel_url():
    """
    Extracts the URL by clicking the address bar and copying its content.
    """
    print("Step 2: Extracting current reel URL from address bar...")
    try:
        # === USER-PROVIDED COORDINATES ===
        url_bar_coords = (1567, 112)
        focus_window_coords = (2358, 878) # Same coordinate as in launch function

        pyperclip.copy('') # Clear the clipboard

        # Click the URL bar to select the address
        pyautogui.click(url_bar_coords)
        time.sleep(0.1) # Short pause to ensure click registers

        # Copy the URL to the clipboard
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1) # Short pause to ensure copy completes

        # IMPORTANT: Click back on the window to focus it for the spacebar press later
        pyautogui.click(focus_window_coords)

        url = pyperclip.paste()

        if url and "instagram.com/reel" in url:
            print(f"Successfully extracted URL: {url}")
            return url
        else:
            print(f"Failed to copy a valid reel URL from address bar. Clipboard: '{url}'")
            return None
    except Exception as e:
        print(f"An error occurred while trying to get the current reel URL: {e}")
        return None

# --- 3. Reel Duration Fetching ---

def get_reel_duration(url):
    """
    Fetches the duration of an Instagram reel using yt_dlp.
    """
    print("Step 3: Fetching reel duration...")
    if not url:
        print("Cannot fetch duration, URL is missing.")
        return None
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'force_generic_extractor': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration")
            print(f"Duration found: {duration:.2f} seconds")
            return duration
    except Exception as e:
        print(f"Error fetching reel duration: {e}")
        return None

# --- 4 & 5. Main Automation Loop ---

def run_autoscroller():
    """Main function to run the auto-scroller loop."""
    print("\n--- Instagram Reels Auto-Scroller ---")

    if not launch_and_navigate():
        print("Launch and navigate failed. Please open and set up Instagram Reels manually.")

    print(f"\nAutomation will start in 5 seconds. Press '{STOP_KEY}' to stop.")
    time.sleep(5)

    while True:
        if keyboard.is_pressed(STOP_KEY):
            print("\nStop key pressed. Exiting script.")
            break

        extraction_start_time = time.monotonic()
        current_url = get_current_reel_url()
        duration = get_reel_duration(current_url)
        extraction_end_time = time.monotonic()
        extraction_time = extraction_end_time - extraction_start_time
        print(f"Time to extract URL and duration: {extraction_time:.2f} seconds")

        reel_duration = duration if duration is not None else 15
        adjusted_wait_time = reel_duration - extraction_time
        
        # Final timing adjustment: No +1 second buffer is added.
        final_wait_time = max(0, adjusted_wait_time)

        print(f"Step 4: Watching reel... (Adjusted wait: {final_wait_time:.2f} seconds)")
        time.sleep(final_wait_time)

        print("Step 5: Scrolling to the next reel...")
        pyautogui.press('space')
        print("-----------------------------------------")
        time.sleep(3)

# --- Script Execution ---

if __name__ == "__main__":
    # Directly run the autoscroller function when the script is executed.
    run_autoscroller()
