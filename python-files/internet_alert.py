Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import os
... import time
... import tkinter as tk
... from tkinter import messagebox
... 
... def check_internet(host="8.8.8.8"):
...     response = os.system(f"ping -n 1 {host} >nul 2>&1")
...     return response == 0
... 
... def alert_message():
...     root = tk.Tk()
...     root.withdraw()
...     messagebox.showwarning("Internet Alert", "⚠️ Internet connection lost!")
...     root.destroy()
... 
... if __name__ == "__main__":
...     print("🔍 Internet Monitor Started... (Close window to stop)")
...     while True:
...         if not check_internet():
...             alert_message()
...             time.sleep(10)
...         else:
...             time.sleep(5)
