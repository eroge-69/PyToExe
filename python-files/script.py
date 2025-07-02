import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess

stop_flag = False

def is_device_connected():
    try:
        output = subprocess.check_output("adb devices", shell=True, text=True)
        return "device" in output.splitlines()[1] if len(output.splitlines()) > 1 else False
    except:
        return False

def get_device_info():
    try:
        if not is_device_connected():
            return {"Error": "📵 No device connected!"}
        output = subprocess.check_output("adb shell getprop", shell=True, text=True)
        info = {}
        for line in output.splitlines():
            if "[ro.product.model]" in line:
                info["Model"] = line.split(":")[1].strip().strip("[]")
            elif "[ro.build.version.release]" in line:
                info["Android Version"] = line.split(":")[1].strip().strip("[]")
            elif "[ro.product.manufacturer]" in line:
                info["Manufacturer"] = line.split(":")[1].strip().strip("[]")
            elif "[ro.build.version.sdk]" in line:
                info["SDK"] = line.split(":")[1].strip().strip("[]")
        return info
    except:
        return {"Error": "❌ ADB failed to fetch device info."}

def get_installed_apps():
    try:
        if not is_device_connected():
            return []
        output = subprocess.check_output("adb shell pm list packages", shell=True, text=True)
        return [line.strip() for line in output.splitlines()]
    except:
        return []

def get_running_apps():
    try:
        if not is_device_connected():
            return []
        output = subprocess.check_output("adb shell dumpsys activity recents", shell=True, text=True)
        return [line.strip() for line in output.splitlines() if "Recent #" in line]
    except:
        return []

def uninstall_app(pkg_name):
    try:
        subprocess.call(f"adb shell pm uninstall --user 0 {pkg_name}", shell=True)
    except:
        pass

def detect_ads_apps(apps):
    ad_keywords = ["ad", "ads", "revenue", "track", "boost", "cleaner", "push", "pop", "promo"]
    return [pkg for pkg in apps if any(k in pkg.lower() for k in ad_keywords)]

def show_device_info():
    text_area.delete(1.0, tk.END)
    info = get_device_info()
    text_area.insert(tk.END, "📱 Device Info:\n\n")
    for key, value in info.items():
        text_area.insert(tk.END, f"{key}: {value}\n")

def scan_ad_apps():
    global stop_flag
    stop_flag = False
    if not is_device_connected():
        messagebox.showwarning("No Device", "📵 Please connect a device with ADB enabled.")
        return
    try:
        apps = get_installed_apps()
        ads = detect_ads_apps(apps)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "🧪 Ad-related Apps:\n\n")
        for a in ads:
            if stop_flag:
                text_area.insert(tk.END, "\n⛔ Scan stopped by user.\n")
                return
            text_area.insert(tk.END, a + "\n")
        if not ads:
            text_area.insert(tk.END, "✅ No obvious ad-related apps found.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def remove_ad_apps():
    if not is_device_connected():
        messagebox.showwarning("No Device", "📵 Please connect a device first.")
        return
    try:
        apps = get_installed_apps()
        ads = detect_ads_apps(apps)
        for a in ads:
            pkg = a.split(":")[-1].strip()
            if pkg in ["com.whatsapp", "com.facebook.katana", "com.phonepe"]:
                continue
            if messagebox.askyesno("Uninstall?", f"Remove {pkg}?"):
                uninstall_app(pkg)
        messagebox.showinfo("Done", "🧹 Ad-related apps removed.")
        scan_ad_apps()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def list_installed():
    if not is_device_connected():
        messagebox.showwarning("No Device", "📵 Connect a device first.")
        return
    try:
        apps = get_installed_apps()
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "📦 Installed Apps:\n\n")
        for a in apps:
            text_area.insert(tk.END, a + "\n")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_running():
    if not is_device_connected():
        messagebox.showwarning("No Device", "📵 Connect a device first.")
        return
    try:
        apps = get_running_apps()
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "🔄 Running Apps:\n\n")
        for a in apps:
            text_area.insert(tk.END, a + "\n")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def auto_block_ads():
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, "🛡 Auto Ad Blocker Guide:\n\n")
    text_area.insert(tk.END, "👉 Use this Private DNS (Android 9+):\n")
    text_area.insert(tk.END, "🔹 dns.adguard-dns.com\n\n")
    text_area.insert(tk.END, "📱 Steps:\n")
    text_area.insert(tk.END, "1. Settings > Network