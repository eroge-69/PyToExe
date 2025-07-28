
import tkinter as tk
import threading
import time
import requests

XMR_ADDRESS = "47B7ZrErJQ4M8FE7hbRjifRz81MJbb2kGjdtgkycUXxeEBKRAwvYMywVdwnzzFmufHh9798xStyyibRUyTncGtLmJVVKxW3"
BNB_ADDRESS = "0xc0dadd16960b54326487e5d663513e4f4bbfc9af"
THRESHOLD = 0.004  # XMR الحد الأدنى للتحويل

def get_xmr_balance():
    try:
        url = f"https://api.moneroocean.stream/miner/{XMR_ADDRESS}/stats"
        r = requests.get(url, timeout=10)
        data = r.json()
        return data['amtDue'] / 1e12
    except Exception as e:
        return f"Error: {e}"

def request_conversion():
    try:
        shift_req = {
            "pair": "xmr_bnbbep20",
            "depositAddress": XMR_ADDRESS,
            "settleAddress": BNB_ADDRESS
        }
        res = requests.post("https://sideshift.ai/api/v2/shift", json=shift_req, timeout=15)
        data = res.json()
        if "depositAddress" in data:
            return "✅ التحويل بدأ بنجاح."
        else:
            return f"❌ فشل التحويل: {data}"
    except Exception as e:
        return f"❌ خطأ في التحويل: {e}"

def monitor_and_convert():
    while True:
        status = get_xmr_balance()
        if isinstance(status, float):
            balance_label["text"] = f"الرصيد الحالي: {status:.6f} XMR"
            if status >= THRESHOLD:
                result = request_conversion()
                log_label["text"] = result
        else:
            log_label["text"] = status
        time.sleep(300)  # كل 5 دقائق

def start_monitoring():
    t = threading.Thread(target=monitor_and_convert)
    t.daemon = True
    t.start()

# واجهة المستخدم
window = tk.Tk()
window.title("XMR ➜ BNB Auto Converter")
window.geometry("400x200")
window.configure(bg="#1e1e1e")

balance_label = tk.Label(window, text="جاري فحص الرصيد...", fg="white", bg="#1e1e1e", font=("Arial", 12))
balance_label.pack(pady=10)

log_label = tk.Label(window, text="في انتظار بدء التحويل...", fg="lightgreen", bg="#1e1e1e", wraplength=350)
log_label.pack(pady=10)

start_button = tk.Button(window, text="ابدأ المراقبة والتحويل", command=start_monitoring, bg="#00cc66", fg="white", font=("Arial", 11, "bold"))
start_button.pack(pady=10)

window.mainloop()
