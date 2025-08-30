import keyboard
import os

# Try to import pyperclip, otherwise use fallback
try:
    import pyperclip
    def copy_to_clipboard(text):
        pyperclip.copy(text)
except ImportError:
    def copy_to_clipboard(text):
        # Windows fallback using built-in "clip"
        os.system(f'echo {text.strip()}| clip')

# Load codes from file
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

# Bind hotkey "K"
keyboard.add_hotkey("k", copy_next_code)

print("Press 'K' to copy the next code to clipboard.")
print(f"Loaded {len(codes)} codes from codes.txt")
keyboard.wait()