#!/usr/bin/env python3
# premium_terminal.py
# Simple terminal UI with rainbow title + menu + dot animation -> "Successfully."

import sys
import time

try:
    # colorama provides Windows ANSI support
    from colorama import init as color_init, Fore, Style
    color_init()
except Exception:
    # fallback: define minimal color names as empty strings (no color)
    class _C:
        RESET_ALL = ""
    Fore = Style = _C()

# small set of alternating colors for a rainbow-like effect
RAINBOW = [
    getattr(Fore, name) for name in (
        "RED", "YELLOW", "MAGENTA", "CYAN", "GREEN", "WHITE"
    ) if hasattr(Fore, name)
] or ["", ""]


def rainbow_text(text: str) -> str:
    out = []
    color_count = len(RAINBOW)
    for i, ch in enumerate(text):
        color = RAINBOW[i % color_count]
        out.append(f"{color}{ch}{Style.RESET_ALL}")
    return "".join(out)


def clear_screen():
    if sys.platform.startswith("win"):
        _ = sys.stdout.write("\033[2J\033[H")
    else:
        sys.stdout.write("\033c")
    sys.stdout.flush()


def print_header():
    title = "PREMIUM TOOLS"
    # Draw a simple ASCII box with rainbow title centered
    width = 60
    print("=" * width)
    centered = title.center(width)
    print(rainbow_text(centered))
    print("=" * width)
    print()


def show_menu():
    print("Select an option:")
    print("  1) Start Premium Tool")
    print("  2) About")
    print("  3) Exit")
    print()
    # prompt
    choice = input("Enter choice (1-3): ").strip()
    return choice


def dots_animation(base_msg="Processing"):
    # show ., .., ...
    sys.stdout.write(base_msg)
    sys.stdout.flush()
    for i in range(1, 4):
        time.sleep(0.6)  # delay between steps (adjustable)
        sys.stdout.write("." * i)
        sys.stdout.flush()
        # backspace the extra dots for the next iteration
        if i < 3:
            sys.stdout.write("\b" * i)
            sys.stdout.write(" " * i)
            sys.stdout.write("\b" * i)
            sys.stdout.flush()
    sys.stdout.write("\n")


def about_box():
    print()
    print("- About Premium Tools -")
    print("This is a demo terminal UI. It simulates a small tool selection.")
    print("Made with Python. Convert to .exe with PyInstaller if needed.")
    print()


def main():
    clear_screen()
    print_header()

    while True:
        choice = show_menu()

        if choice == "1":
            print()
            dots_animation("Working")
            # Success message (green if available)
            success = (getattr(Fore, "GREEN", "") + "Successfully." + getattr(Style, "RESET_ALL", ""))
            print(success)
            print()
            input("Press Enter to return to menu...")
            clear_screen()
            print_header()
        elif choice == "2":
            about_box()
            input("Press Enter to return to menu...")
            clear_screen()
            print_header()
        elif choice == "3":
            print()
            print("Goodbye.")
            time.sleep(0.5)
            break
        else:
            print()
            print("Invalid choice. Please enter 1, 2 or 3.")
            time.sleep(0.6)
            # redraw header/menu loop continues


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
