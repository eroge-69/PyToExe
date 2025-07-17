import os
import subprocess
import sys
import re

# ANSI color codes
CYAN = "\033[96m"
GREEN = "\033[92m"
ORANGE = "\033[38;5;214m"
RED = "\033[91m"
RESET = "\033[0m"

ascii_art = f"""
{GREEN}         ▒▓▓                                        ░▒░        ▀
      ▄▓▒▀                                             ▐▓▄
    ▄▓▓        ░      ▄▄     ░░░ ░░     ▓▒▄░  ░▒▓▄        ▓▄
  ▄▒▓       ▒▀        ░░░░░░░░░░░░░              ░▓▓▄       ▓▄
▄▒▓      ▄▓         ░░░░░░░░░░░░░░░░ ░              ▀▓▓       ▒░
▒░     ▄▓      ░   ▄░░░░░░░░░░░░░░░░        ░          ▓▓      ░
      ▒░    ▄▓▀      ░░░░░░░░░░░░░░░  ░           ▐     ▐▒▄
                          ▄▄▄▄▄░▄▄▄░░      ▀   ▒          ▒▒
                         ▒▒▓▓▓▓▓▒▓▓▒▒              ▄        ░
     ▐▓         ░         ▒▒▓▓▓▒▒▒▒░                ▓    ░░
     ▓▓     ▐            ▐░ ░▒▒░  ▄███                    ▒
     ▓░                 ▄██▄▄ ▄▄███████                ░  ░░
    ░  ▐▒              █████████████████               ▐▒
          ▓           ▐█████████████▌▀▀▀▄          ▄ ░  ▐
                     ▄██████████████████▄█
          ▄         ▀██████████████████████        ░
    ░  ▐░ ▐        ▐████████████████████████           ▐▒
     ░  ░          ████████▀████████████████           ▐{RESET}
"""

print(ascii_art)

print(
    "OPTIC is a tool for standalone Android-based VR headsets that lets you\n"
    "Tweak performance, visuals, input, and battery\n"
    "created with love by crabamongspies\n"
)

# adb.exe path (same folder)
ADB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adb.exe")

def adb_shell(command):
    full_cmd = f'"{ADB_PATH}" shell "{command}"'
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Failed command:\n  {command}\n  Error: {result.stderr.strip()}")
        return False
    else:
        print(f"[OK] {result.stdout.strip()}")
        return True

def device_check():
    result = subprocess.run(f'"{ADB_PATH}" get-state', shell=True, capture_output=True, text=True)
    if "device" not in result.stdout:
        print("[ERROR] No device detected. Connect your Quest and enable ADB.")
        sys.exit(1)
    else:
        print("[OK] Device detected.")

def strip_ansi_codes(s):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', s)

def prompt_choice(prompt, options):
    print(prompt)
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")
    while True:
        choice = input("Enter number (or press Enter to skip): ").strip()
        if choice == "":
            return "Skip"
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(options):
                # Return plain text stripped of color codes
                return strip_ansi_codes(options[idx-1])
        print("Invalid choice, please try again.")

def apply_settings(texture_choice, refresh_choice):
    if texture_choice != "Skip":
        sizes = {
            "LOW (768x768)": "768",
            "MEDIUM (1280x1280)": "1280",
            "HIGH (2560x2560)": "2560"
        }
        size = sizes.get(texture_choice)
        if size:
            if not adb_shell(f"setprop debug.oculus.textureWidth {size}"):
                return
            if not adb_shell(f"setprop debug.oculus.textureHeight {size}"):
                return
        else:
            print("[WARNING] Unknown texture size selected.")

    if refresh_choice != "Skip":
        rates = ["60", "72", "90", "120"]
        rate = refresh_choice.split()[0]  # e.g. "60 Hz" -> "60"
        if rate in rates:
            if not adb_shell(f"setprop debug.oculus.refreshRate {rate}"):
                return
        else:
            print("[WARNING] Unknown refresh rate selected.")

    print("\nSettings applied! Please reboot your headset for changes to take effect.")

def main():
    device_check()

    texture_options = [
        f"{GREEN}LOW (768x768){RESET}",
        f"{ORANGE}MEDIUM (1280x1280){RESET}",
        f"{RED}HIGH (2560x2560){RESET}"
    ]

    refresh_options = ["60 Hz", "72 Hz", "90 Hz", "120 Hz"]

    texture_choice = prompt_choice("Select Texture Resolution:", texture_options)
    refresh_choice = prompt_choice("Select Refresh Rate:", refresh_options)

    apply_settings(texture_choice, refresh_choice)

if __name__ == "__main__":
    main()