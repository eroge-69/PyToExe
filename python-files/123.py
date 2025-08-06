import webbrowser
import time
import os
import tkinter as tk

url = "https://files.catbox.moe/xkls70.mp4"  # غير الرابط حسب رغبتك

# 1. فتح صفحة وحدة
webbrowser.open(url)

# 2. انتظر 4 ثواني
time.sleep(4)

# 3. فتح 10 صفحات
for _ in range(10):
    webbrowser.open(url)

# 4. انتظر 6 ثواني
time.sleep(6)

# 5. نافذة وهمية (كأنها تهكير)
root = tk.Tk()
root.title("Hacked")
root.configure(bg="black")
root.attributes('-fullscreen', True)

# نص التهكير
label = tk.Label(root, text="""
[!] SYSTEM BREACH DETECTED
[!] Encrypting files...
[!] Sending data to remote server...
[!] Tracking your IP: 192.168.1.5
[!] BIOS access granted...
[!] Shuttin
