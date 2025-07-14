import sys
import subprocess

# 📦 Tự động cài thư viện nếu chưa có
def auto_install(lib):
    try:
        __import__(lib)
    except ImportError:
        print(f"🧩 Đang cài thư viện: {lib} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# 🧰 Danh sách thư viện mở rộng (tùy chọn nếu bạn nâng cấp sau)
for lib in ["colorama", "psutil", "requests"]:
    auto_install(lib)

# ⬇️ Sau đây là toàn bộ mã GUI GenRouter Mini
import os
import subprocess
import random
import time
import json
import tkinter as tk
from tkinter import messagebox, simpledialog

PROFILE_FILE = "wifi_profiles.json"

mac_prefixes = {
    "Viettel": "00:1A:11",
    "VNPT": "00:1C:DF",
    "FPT": "00:25:9C",
    "Huawei": "00:9A:CD",
    "TP-Link": "C0:25:E9"
}

def generate_mac(prefix):
    suffix = [format(random.randint(0, 255), '02X') for _ in range(3)]
    return prefix + ":" + ":".join(suffix)

def change_mac(adapter_name, new_mac):
    reg_path = f'HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}'
    mac_plain = new_mac.replace(":", "")
    for i in range(0, 50):
        key = f'{reg_path}\\{str(i).zfill(4)}'
        try:
            subprocess.run(['reg', 'add', key, '/v', 'NetworkAddress', '/d', mac_plain, '/f'],
                           stdout=subprocess.DEVNULL)
        except:
            continue
    subprocess.run(['netsh', 'interface', 'set', 'interface', adapter_name, 'admin=disable'])
    time.sleep(2)
    subprocess.run(['netsh', 'interface', 'set', 'interface', adapter_name, 'admin=enable'])

def start_hotspot(ssid, password):
    os.system(f'netsh wlan set hostednetwork mode=allow ssid="{ssid}" key="{password}"')
    os.system('netsh wlan start hostednetwork')

def check_hotspot_status():
    result = subprocess.run(['netsh', 'wlan', 'show', 'hostednetwork'], capture_output=True, text=True)
    return "Status" in result.stdout and "Started" in result.stdout

def get_current_mac(adapter_name):
    result = subprocess.run(['getmac', '/v', '/fo', 'list'], capture_output=True, text=True)
    for i, line in enumerate(result.stdout.splitlines()):
        if adapter_name.lower() in line.lower():
            mac_line = result.stdout.splitlines()[i + 1]
            return mac_line.split(":")[1].strip()
    return None

def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return []
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def save_profiles(profiles):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

class GenRouterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GenRouter Mini – Quản lý Profile & MAC")
        self.profiles = load_profiles()

        tk.Label(root, text="📡 Tên adapter Wi-Fi:").pack()
        self.adapter_entry = tk.Entry(root)
        self.adapter_entry.insert(0, "Wi-Fi")
        self.adapter_entry.pack(pady=4)

        tk.Label(root, text="📁 Danh sách Profile:").pack()
        self.listbox = tk.Listbox(root, width=40)
        self.listbox.pack(pady=4)
        self.refresh_profiles()

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=6)

        tk.Button(btn_frame, text="Phát Wi-Fi", command=self.launch_profile).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text="Tạo Profile", command=self.add_profile).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text="Đổi Tên", command=self.rename_profile).grid(row=0, column=2, padx=4)
        tk.Button(btn_frame, text="Xóa", command=self.delete_profile).grid(row=0, column=3, padx=4)

    def refresh_profiles(self):
        self.listbox.delete(0, tk.END)
        for p in self.profiles:
            self.listbox.insert(tk.END, f"{p['ssid']} ({p['brand']})")

    def add_profile(self):
        ssid = simpledialog.askstring("SSID", "Nhập tên Wi-Fi:")
        password = simpledialog.askstring("Mật khẩu", "Nhập mật khẩu:")
        brand = simpledialog.askstring("Hãng MAC", "Chọn hãng (Viettel/VNPT/FPT/Huawei/TP-Link):")
        if not ssid or not password or brand not in mac_prefixes:
            messagebox.showerror("Lỗi", "Thông tin không hợp lệ.")
            return
        mac = generate_mac(mac_prefixes[brand])
        self.profiles.append({"ssid": ssid, "password": password, "mac": mac, "brand": brand})
        save_profiles(self.profiles)
        self.refresh_profiles()
        messagebox.showinfo("✅ Thành công", f"Đã tạo profile: {ssid} với MAC: {mac}")

    def rename_profile(self):
        idx = self.listbox.curselection()
        if not idx: return
        new_name = simpledialog.askstring("Đổi tên", "Nhập tên mới:")
        if new_name:
            self.profiles[idx[0]]["ssid"] = new_name
            save_profiles(self.profiles)
            self.refresh_profiles()

    def delete_profile(self):
        idx = self.listbox.curselection()
        if not idx: return
        confirm = messagebox.askyesno("Xóa", "Bạn chắc chắn muốn xóa profile này?")
        if confirm:
            self.profiles.pop(idx[0])
            save_profiles(self.profiles)
            self.refresh_profiles()

    def launch_profile(self):
        idx = self.listbox.curselection()
        if not idx: return
        profile = self.profiles[idx[0]]
        adapter = self.adapter_entry.get()
        change_mac(adapter, profile['mac'])
        start_hotspot(profile['ssid'], profile['password'])
        time.sleep(1)

        status = check_hotspot_status()
        current_mac = get_current_mac(adapter)
        if not status:
            messagebox.showwarning("Hotspot", "⚠️ Hotspot chưa được khởi động!")
        elif current_mac.lower() != profile['mac'].lower():
            messagebox.showwarning("Cảnh báo MAC", f"⚠️ MAC hiện tại ({current_mac}) KHÔNG khớp với profile ({profile['mac']})!")
        else:
            messagebox.showinfo("Thành công", f"✅ Hotspot đang hoạt động!\nMAC hiện tại: {current_mac}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GenRouterApp(root)
    root.mainloop()