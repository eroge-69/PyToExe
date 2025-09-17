import os
import shutil
import ctypes
import getpass
import sys

# ============================
# Force run as Administrator
# ============================
def run_as_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
    except:
        return False

    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

# ============================
# Fast delete function
# ============================
def fast_delete(path):
    """Delete all contents inside a folder quickly"""
    if os.path.exists(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
            except:
                pass  # Skip locked/system files

# ============================
# Empty Recycle Bin
# ============================
def empty_recycle_bin():
    """Empty Windows Recycle Bin"""
    SHERB_NOCONFIRMATION = 0x00000001
    SHERB_NOPROGRESSUI = 0x00000002
    SHERB_NOSOUND = 0x00000004
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(
            None, None,
            SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
        )
        print("Recycle Bin emptied ✅")
    except:
        print("Could not empty Recycle Bin (maybe no items).")

# ============================
# Popup Message (using ctypes)
# ============================
def show_popup(message):
    """Show a simple Windows message box."""
    # Define constants for the message box
    MB_OK = 0
    MB_ICONINFORMATION = 0x40
    
    # Call the Windows API function MessageBoxW
    ctypes.windll.user32.MessageBoxW(None, message, "Cleanup Complete", MB_OK | MB_ICONINFORMATION)

# ============================
# Main cleanup
# ============================
def main():
    user = getpass.getuser()
    paths = [
        r"C:\Windows\Temp",
        rf"C:\Users\{user}\AppData\Local\Temp",
        r"C:\Windows\Prefetch",
        rf"C:\Users\{user}\AppData\Local\Microsoft\Windows\Explorer"  # Thumbnails
    ]

    for p in paths:
        fast_delete(p)
        print(f"Cleaned: {p}")

    empty_recycle_bin()

    print("\n🎉 All junk cleaned successfully!")
    show_popup("All junk cleaned successfully!")

# ============================
# Run script
# ============================
if __name__ == "__main__":
    run_as_admin()
    main()