import os
import sys
import uuid
import pyautogui
import pydirectinput
import pyperclip
import time
import random

# --- HWID Lock System ---

ALLOWED_HWIDS = [
    "HWID_HERE_1",
    "HWID_HERE_2",
    "HWID_HERE_3",
    "HWID_HERE_4",
    "HWID_HERE_5",
    "HWID_HERE_6",
    "HWID_HERE_7",
    "HWID_HERE_8",
    "HWID_HERE_9",
    "HWID_HERE_10",
    "HWID_HERE_11",
    "HWID_HERE_12",
    "HWID_HERE_13",
    "HWID_HERE_14",
    "HWID_HERE_15",
    "HWID_HERE_16",
    "HWID_HERE_17",
    "HWID_HERE_18",
    "HWID_HERE_19",
    "HWID_HERE_20"
]

def get_hwid():
    return hex(uuid.getnode()).upper()[2:]

def check_hwid():
    hwid = get_hwid()
    if hwid not in ALLOWED_HWIDS:
        print("❌ Unauthorized machine! Contact seller for access.")
        print(f"Your HWID: {hwid}")
        sys.exit(1)
    else:
        print(f"✅ HWID verified: {hwid}\n")

# Run check before anything else
check_hwid()

# Set pydirectinput to minimize delays for mouse movements
pydirectinput.PAUSE = 0

# Clear console for a clean startup
os.system('cls' if os.name == 'nt' else 'clear')

# Display new compact ASCII art banner and instructions
print("""
╔════════════════════════════════════╗
║         Z14D Auto-Joiner           ║
╚════════════════════════════════════╝
      ______
  .-        -.
 /            \\
|
| )(_o/  \\o_)( |
|/     /\\     \\|
(_     ^^     _)
 \\__|IIIIII|__/
  | \\IIIIII/ |
  \\          /
   `--------`

Welcome to the Z14D Auto-Joiner!
--------------------------------
How to Use:
1. Copy a JobId or Teleport Script to your clipboard.
2. The script will auto-detect it, paste it into the text box, and click Join.
3. Press Ctrl+C to stop the script at any time.
--------------------------------
""")

# Function to get coordinates from user
def get_coordinates(prompt):
    print(f"→ {prompt}")
    input("   (Move mouse to position and press Enter): ")
    return pyautogui.position()

# Get coordinates for text box, joiner, and defocus spot
print("Setting up coordinates...")
text_box_pos = get_coordinates("Position for text box")
joiner_pos = get_coordinates("Position for joiner")
defocus_pos = get_coordinates("Position for defocus click (e.g., in the 3D world to remove focus from text box)")

# Display coordinates
print("\nCoordinates set:")
print(f"  Text box: {text_box_pos}")
print(f"  Joiner: {joiner_pos}")
print(f"  Defocus: {defocus_pos}")
print("\nMonitoring clipboard for new content... Press Ctrl+C to stop.\n")

# Clear clipboard at start to ignore previous content
pyperclip.copy("")
previous_clipboard = ""

try:
    while True:
        # Get current clipboard content
        current_clipboard = pyperclip.paste().strip()

        # Check if clipboard has new, non-empty content
        if current_clipboard != previous_clipboard and current_clipboard != "":
            print(f"[{time.strftime('%H:%M:%S')}] New clipboard content detected. Automating join...")

            # Teleport to text box, click twice to focus
            pydirectinput.moveTo(text_box_pos.x, text_box_pos.y)
            pydirectinput.click()
            time.sleep(random.uniform(0.02, 0.05))
            pydirectinput.click()
            time.sleep(random.uniform(0.02, 0.05))

            # Paste with Ctrl+V using direct input
            pydirectinput.keyDown('ctrl')
            time.sleep(random.uniform(0.02, 0.05))
            pydirectinput.press('v')
            time.sleep(random.uniform(0.02, 0.05))
            pydirectinput.keyUp('ctrl')
            time.sleep(random.uniform(0.02, 0.05))

            # Force defocus with double-click in the defocus spot
            pydirectinput.moveTo(defocus_pos.x, defocus_pos.y)
            pydirectinput.click()
            time.sleep(random.uniform(0.02, 0.05))
            pydirectinput.click()
            time.sleep(random.uniform(0.02, 0.05))

            # Teleport to joiner, single click to activate
            pydirectinput.moveTo(joiner_pos.x, joiner_pos.y)
            pydirectinput.click()

            # Update previous clipboard to avoid repeating
            previous_clipboard = current_clipboard

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nScript stopped.")
