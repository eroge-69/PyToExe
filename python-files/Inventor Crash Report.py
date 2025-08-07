import ctypes
import sys

def main():
    meme_message = "Autodesk Inventor yeeted itself into the void."
    title = "Autodesk Crash LOL"

    # MessageBox: 0 = OK button only, 16 = Error icon
    ctypes.windll.user32.MessageBoxW(0, meme_message, title, 0x10)

    # Optional: simulate error report sending delay
    import time
    time.sleep(2)

    # Exit with success code (or use 1 if you want to simulate failure)
    sys.exit(0)

if __name__ == "__main__":
    main()
