import os
import sys

try:
    import keyboard
except ImportError:
    print("❌ Missing dependency: keyboard. Please install it before building.")
    sys.exit(1)

# Clipboard handling: try pyperclip, else fallback to Windows 'clip' command
try:
    import pyperclip
    def copy_to_clipboard(text: str):
        pyperclip.copy(text)
except ImportError:
    def copy_to_clipboard(text: str):
        os.system(f'echo {text.strip()}| clip')

# Load codes from codes.txt
if not os.path.exists("codes.txt"):
    print("❌ No codes.txt found in the same folder as the program.")
    sys.exit(1)

with open("codes.txt", "r", encoding="utf-8") as f:
    codes = [line.strip() for line in f if line.strip()]

index = 0

def copy_next_code():
    global index
    if index < len(codes):
        code = codes[index]
        copy_to_clipboard(code)
        print(f"[{index+1}/{len(codes)}] Copied: {code}")
        index += 1
    else:
        print("✅ All codes used. Restart program to reuse.")
        keyboard.unhook_all_hotkeys()

# Bind hotkey
keyboard.add_hotkey("k", copy_next_code)

print("📋 Code Copier is running.")
print("Press 'K' to copy the next code to clipboard.")
print(f"Loaded {len(codes)} codes from codes.txt")

keyboard.wait()  # keep program alive