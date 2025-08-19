import subprocess
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog, messagebox
import os
import http.client
import mimetypes
from urllib.parse import urlparse
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
DEFAULT_WEBHOOK = "https://discord.com/api/webhooks/REPLACE_ME"
REMOTE_SCREENSHOT_DIRS = ["/sdcard/Oculus/Screenshots/", "/sdcard/Pictures/Screenshots/"]
REMOTE_VIDEO_DIRS = ["/sdcard/Oculus/VideoShots/", "/sdcard/Movies/VideoShots/"]
LOCAL_SAVE_BASE = os.path.join(os.path.expanduser("~"), "Downloads")
os.makedirs(os.path.join(LOCAL_SAVE_BASE, "screenshots"), exist_ok=True)
os.makedirs(os.path.join(LOCAL_SAVE_BASE, "videos"), exist_ok=True)
monitoring = False

# -----------------------------
# ADB Helpers
# -----------------------------
def adb_devices_connected():
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()
        devices = [line for line in lines[1:] if line.strip() and "device" in line]
        return devices
    except Exception:
        return []

def adb_list_packages():
    try:
        result = subprocess.run(["adb", "shell", "pm", "list", "packages"], capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()
        packages = [line.replace("package:", "").strip() for line in lines]
        return sorted(packages)
    except Exception:
        return []

def run_adb_command(command, output_box):
    try:
        if not command.startswith("adb"):
            command = "adb " + command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += "\n[ERROR]\n" + result.stderr
        output_box.insert(tk.END, f"> {command}\n{output}\n\n")
        output_box.see(tk.END)
    except Exception as e:
        output_box.insert(tk.END, f"Failed to run command: {e}\n")

# -----------------------------
# APK Export
# -----------------------------
def export_apk(package_name, output_box):
    if not package_name:
        messagebox.showwarning("No Package", "Please select a package first.")
        return
    try:
        result = subprocess.run(["adb", "shell", "pm", "path", package_name], capture_output=True, text=True)
        output = result.stdout.strip()
        if not output.startswith("package:"):
            output_box.insert(tk.END, f"❌ Could not find APK for {package_name}\n")
            return
        apk_path = output.replace("package:", "")
        local_file = filedialog.asksaveasfilename(defaultextension=".apk",
                                                 initialfile=f"{package_name}.apk",
                                                 title="Save APK As")
        if not local_file:
            return
        subprocess.run(["adb", "pull", apk_path, local_file])
        output_box.insert(tk.END, f"✅ APK saved: {local_file}\n")
    except Exception as e:
        output_box.insert(tk.END, f"⚠️ Error exporting APK: {e}\n")

# -----------------------------
# OBB Upload
# -----------------------------
def upload_obb_new_flow(output_box):
    filepath = filedialog.askopenfilename(title="Select OBB file", filetypes=[("OBB files", "*.obb"), ("All files", "*.*")])
    if not filepath:
        return
    package_selection_window = tk.Toplevel()
    package_selection_window.title("Select Target Package")
    package_selection_window.configure(bg="#222222")
    frame = ttk.Frame(package_selection_window, padding=15)
    frame.pack(fill="both", expand=True)
    label = ttk.Label(frame, text="Select the package to upload the OBB file to:")
    label.pack(pady=10)
    package_var = tk.StringVar()
    packages = adb_list_packages()
    package_dropdown = ttk.Combobox(frame, textvariable=package_var, font=("Helvetica", 11), values=packages, state="readonly")
    package_dropdown.pack(fill="x", padx=5, pady=5)
    if packages:
        package_dropdown.set(packages[0])
    def start_upload():
        package_name = package_var.get()
        if not package_name:
            messagebox.showwarning("No Package", "Please select a package.")
            return
        obb_dir = f"/sdcard/Android/obb/{package_name}/"
        obb_filename = os.path.basename(filepath)
        def upload_thread():
            run_adb_command(f"adb shell mkdir -p {obb_dir}", output_box)
            run_adb_command(f"adb push \"{filepath}\" {obb_dir}{obb_filename}", output_box)
            messagebox.showinfo("Upload Complete", f"Uploaded {obb_filename} to {obb_dir}")
            package_selection_window.destroy()
        threading.Thread(target=upload_thread, daemon=True).start()
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="Upload", command=start_upload).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Cancel", command=package_selection_window.destroy).pack(side="left", padx=5)
    package_selection_window.grab_set()
    package_selection_window.transient(package_selection_window.master)
    package_selection_window.wait_window()

# -----------------------------
# Screenshot Monitor → Discord
# -----------------------------
def adb_shell(cmd):
    result = subprocess.run(["adb", "shell"] + cmd.split(), capture_output=True, text=True)
    return result.stdout.strip()

def adb_pull(remote_path, local_path):
    subprocess.run(["adb", "pull", remote_path, local_path])

def send_to_discord(filepath, webhook_url, output_box):
    try:
        parsed = urlparse(webhook_url)
        conn = http.client.HTTPSConnection(parsed.netloc)
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        filetype = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            file_data = f.read()
        body = []
        body.append(f"--{boundary}")
        body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"')
        body.append(f"Content-Type: {filetype}\r\n")
        body_bytes = "\r\n".join(body).encode() + b"\r\n" + file_data + b"\r\n"
        body_bytes += f"--{boundary}--\r\n".encode()
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body_bytes))}
        conn.request("POST", parsed.path, body_bytes, headers)
        response = conn.getresponse()
        if response.status in (200, 204):
            output_box.insert("end", f"✅ Sent {filename} to Discord\n")
        else:
            output_box.insert("end", f"❌ Failed to send {filename} ({response.status})\n")
    except Exception as e:
        output_box.insert("end", f"⚠️ Discord Error: {e}\n")

def monitor_screenshots(webhook_url, output_box):
    global monitoring
    last_seen_time = 0
    output_box.insert(tk.END, "🚀 Screenshot monitor started...\n")
    while monitoring:
        for remote_dir in REMOTE_SCREENSHOT_DIRS:
            try:
                output = adb_shell(f"ls -t {remote_dir}")
                if not output:
                    continue
                files = output.splitlines()
                for f in files:
                    remote_path = remote_dir + f
                    mtime_str = adb_shell(f"stat -c %Y {remote_path}")
                    if not mtime_str.isdigit():
                        continue
                    mtime = int(mtime_str)
                    if mtime > last_seen_time:
                        last_seen_time = mtime
                        local_path = os.path.join(LOCAL_SAVE_BASE, "screenshots", f"{mtime}_{f}")
                        output_box.insert(tk.END, f"📸 New screenshot: {remote_path}\n")
                        adb_pull(remote_path, local_path)
                        send_to_discord(local_path, webhook_url, output_box)
                        output_box.see(tk.END)
                        break
            except Exception as e:
                output_box.insert(tk.END, f"⚠️ Monitor Error: {e}\n")
        time.sleep(1)
    output_box.insert(tk.END, "🛑 Screenshot monitor stopped.\n")

def toggle_monitor(webhook_entry, output_box, button):
    global monitoring
    if not monitoring:
        webhook_url = webhook_entry.get().strip()
        if not webhook_url.startswith("https://discord.com/api/webhooks/"):
            messagebox.showerror("Invalid Webhook", "Please enter a valid Discord webhook URL.")
            return
        monitoring = True
        button.config(text="Stop Screenshot Monitor")
        threading.Thread(target=monitor_screenshots, args=(webhook_url, output_box), daemon=True).start()
    else:
        monitoring = False
        button.config(text="Start Screenshot Monitor")

# -----------------------------
# Media Management
# -----------------------------
def save_all_media(output_box, media_type):
    if media_type == "screenshots":
        remote_dirs = REMOTE_SCREENSHOT_DIRS
        media_folder = "screenshots"
    elif media_type == "videos":
        remote_dirs = REMOTE_VIDEO_DIRS
        media_folder = "videos"
    else:
        return

    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    base_folder_name = f"Quest_{media_folder.capitalize()}"
    save_folder = os.path.join(downloads_path, base_folder_name)
    counter = 1
    while os.path.exists(save_folder):
        save_folder = os.path.join(downloads_path, f"{base_folder_name}_{counter}")
        counter += 1
    try:
        os.makedirs(save_folder, exist_ok=True)
        output_box.insert(tk.END, f"📁 Creating folder and saving all {media_type} to: {save_folder}...\n")
        for remote_dir in remote_dirs:
            output = adb_shell(f"ls {remote_dir}")
            if not output:
                continue
            files = output.splitlines()
            for f in files:
                remote_path = os.path.join(remote_dir, f)
                local_path = os.path.join(save_folder, f)
                adb_pull(remote_path, local_path)
                output_box.insert(tk.END, f"📸 Pulled {remote_path} → {local_path}\n")
        output_box.see(tk.END)
        output_box.insert(tk.END, f"✅ All {media_type} saved.\n")
    except Exception as e:
        output_box.insert(tk.END, f"⚠️ Error saving {media_type}: {e}\n")

def clear_all_media(output_box):
    if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete ALL screenshots and videos from your headset? This cannot be undone."):
        output_box.insert(tk.END, "Action cancelled.\n")
        return
    output_box.insert(tk.END, "🗑️ Deleting all screenshots and videos from headset...\n")
    def clear_thread():
        try:
            for dir in REMOTE_SCREENSHOT_DIRS + REMOTE_VIDEO_DIRS:
                run_adb_command(f"adb shell rm -r {dir}", output_box)
            output_box.insert(tk.END, "✅ All screenshots and videos deleted from headset.\n")
        except Exception as e:
            output_box.insert(tk.END, f"⚠️ Error deleting media: {e}\n")
    threading.Thread(target=clear_thread, daemon=True).start()

# -----------------------------
# Manual ADB Command Window
# -----------------------------
def execute_custom_adb_command(command_entry, output_box_popup, main_output_box):
    command = command_entry.get().strip()
    if not command:
        return
    if not command.startswith("adb"):
        full_command = f"adb {command}"
    else:
        full_command = command
    output_box_popup.delete("1.0", tk.END)
    output_box_popup.insert(tk.END, f"> {full_command}\n")
    def run_thread():
        try:
            result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += "\n[ERROR]\n" + result.stderr
            output_box_popup.insert(tk.END, f"{output}\n\n")
            output_box_popup.see(tk.END)
            main_output_box.insert(tk.END, f"✅ Manual command executed: {full_command}\n")
            main_output_box.see(tk.END)
        except Exception as e:
            output_box_popup.insert(tk.END, f"Failed to run command: {e}\n")
            main_output_box.insert(tk.END, f"⚠️ Failed to run manual command: {e}\n")
    threading.Thread(target=run_thread, daemon=True).start()
    command_entry.delete(0, tk.END)

def open_adb_command_window(parent_window, main_output_box):
    window = tk.Toplevel(parent_window)
    window.title("ADB Command Line")
    window.geometry("600x600")
    window.configure(bg="#222222")
    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure("TFrame", background="#222222")
    style.configure("TLabel", background="#222222", foreground="#FFFFFF", font=("Helvetica", 11))
    style.configure("TButton", background="#444444", foreground="#FFFFFF", font=("Helvetica", 11), borderwidth=0)
    style.map("TButton", background=[("active", "#555555")])
    style.configure("TEntry", fieldbackground="#2e2e2e", foreground="#FFFFFF", font=("Consolas", 11), borderwidth=1, relief="solid")
    frame = ttk.Frame(window, padding=15)
    frame.pack(fill="both", expand=True)
    input_frame = ttk.Frame(frame)
    input_frame.pack(fill="x", pady=(0, 10))
    label = ttk.Label(input_frame, text="Enter Command:")
    label.pack(side="left")
    command_entry = ttk.Entry(input_frame)
    command_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
    command_entry.bind("<Return>", lambda event: execute_custom_adb_command(command_entry, output_box, main_output_box))
    run_btn = ttk.Button(input_frame, text="Run", command=lambda: execute_custom_adb_command(command_entry, output_box, main_output_box))
    run_btn.pack(side="left")
    examples_frame = ttk.LabelFrame(frame, text="Example Commands", padding=10)
    examples_frame.pack(fill="x", pady=5)
    def set_command(cmd):
        command_entry.delete(0, tk.END)
        command_entry.insert(0, cmd)
    btn_row1 = ttk.Frame(examples_frame)
    btn_row1.pack(fill="x", pady=(0, 5))
    ttk.Button(btn_row1, text="adb devices", command=lambda: set_command("devices")).pack(side="left", padx=2, fill="x", expand=True)
    ttk.Button(btn_row1, text="adb reboot", command=lambda: set_command("reboot")).pack(side="left", padx=2, fill="x", expand=True)
    btn_row2 = ttk.Frame(examples_frame)
    btn_row2.pack(fill="x")
    ttk.Button(btn_row2, text="adb shell ls /sdcard/", command=lambda: set_command("shell ls /sdcard/")).pack(side="left", padx=2, fill="x", expand=True)
    ttk.Button(btn_row2, text="adb logcat", command=lambda: set_command("logcat")).pack(side="left", padx=2, fill="x", expand=True)
    output_frame = ttk.LabelFrame(frame, text="Command Output", padding=10)
    output_frame.pack(fill="both", expand=True, pady=10)
    output_box = scrolledtext.ScrolledText(output_frame, bg="#2e2e2e", fg="#FFFFFF", font=("Consolas", 11), wrap="word", relief="flat", padx=10, pady=10)
    output_box.pack(fill="both", expand=True)
    window.transient(parent_window)
    window.grab_set()
    window.focus_set()
    window.wait_window()

# -----------------------------
# Performance Tools
# -----------------------------
def toggle_fps_display(action, output_box):
    if action == "on":
        cmd = "shell setprop debug.oculus.showVidPerfPanel true"
        message = "✅ FPS Display ON. You may need to restart the game."
    elif action == "off":
        cmd = "shell setprop debug.oculus.showVidPerfPanel false"
        message = "❌ FPS Display OFF."
    else:
        return
    threading.Thread(target=run_adb_command, args=(cmd, output_box), daemon=True).start()
    output_box.insert(tk.END, f"{message}\n\n")

def toggle_passthrough_mode(action, output_box):
    if action == "on":
        cmd = "shell am start -n com.oculus.vrshell/.MainActivity -e passthrough_mode true"
        message = "✅ Passthrough mode ON."
    elif action == "off":
        cmd = "shell am start -n com.oculus.vrshell/.MainActivity -e passthrough_mode false"
        message = "❌ Passthrough mode OFF."
    else:
        return
    threading.Thread(target=run_adb_command, args=(cmd, output_box), daemon=True).start()
    output_box.insert(tk.END, f"{message}\n\n")

def check_battery_status(output_box):
    output_box.insert(tk.END, "🔋 Checking battery status...\n")
    def battery_thread():
        try:
            result = subprocess.run(["adb", "shell", "dumpsys", "battery"], capture_output=True, text=True)
            lines = result.stdout.strip().splitlines()
            status_line = next((line for line in lines if "status:" in line), None)
            level_line = next((line for line in lines if "level:" in line), None)
            status = "Unknown"
            if status_line:
                status_val = status_line.split(":")[1].strip()
                status_map = {"2": "Charging", "3": "Discharging", "4": "Not Charging", "5": "Full"}
                status = status_map.get(status_val, status_val)
            level = "Unknown"
            if level_line:
                level = level_line.split(":")[1].strip() + "%"
            output_box.insert(tk.END, f"Status: {status}\nLevel: {level}\n\n")
            output_box.see(tk.END)
        except Exception as e:
            output_box.insert(tk.END, f"⚠️ Error getting battery status: {e}\n")
    threading.Thread(target=battery_thread, daemon=True).start()

# -----------------------------
# Device Monitor
# -----------------------------
def device_monitor(status_label, devices_box):
    connected_prev = []
    while True:
        devices = adb_devices_connected()
        if devices != connected_prev:
            if devices:
                status_label.config(text="✅ Device Connected", foreground="#4CAF50")
                devices_box.delete(0, tk.END)
                for d in devices:
                    devices_box.insert(tk.END, d)
            else:
                status_label.config(text="❌ No Device", foreground="#F44336")
                devices_box.delete(0, tk.END)
            connected_prev = devices
        time.sleep(3)

# -----------------------------
# Tkinter GUI
# -----------------------------
def start_gui():
    root = tk.Tk()
    root.title("Quest ADB Tool")
    root.geometry("1000x750")
    HEADING_FONT = ("Helvetica", 14, "bold")
    UI_FONT = ("Helvetica", 11)
    MONO_FONT = ("Consolas", 11)
    BG_COLOR = "#222222"
    FG_COLOR = "#FFFFFF"
    FRAME_BG = "#2e2e2e"
    BUTTON_BG = "#444444"
    BUTTON_FG = "#FFFFFF"
    ACCENT_COLOR = "#1E88E5"
    STATUS_DANGER = "#F44336"
    STATUS_SUCCESS = "#4CAF50"
    root.configure(bg=BG_COLOR)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabelFrame", background=BG_COLOR, foreground=FG_COLOR, font=("Helvetica", 12, "bold"), bordercolor="#333333", borderwidth=2)
    style.configure("TLabelFrame.Label", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=UI_FONT)
    style.configure("TEntry", fieldbackground=FRAME_BG, foreground=FG_COLOR, font=UI_FONT, borderwidth=1, relief="solid")
    style.configure("TCombobox", fieldbackground=FRAME_BG, foreground=FG_COLOR, font=UI_FONT)
    style.map("TCombobox", fieldbackground=[('readonly', FRAME_BG)])
    style.configure("TButton", background=BUTTON_BG, foreground=BUTTON_FG, font=UI_FONT, borderwidth=0)
    style.map("TButton", background=[("active", "#555555")], relief=[("pressed", "sunken")])
    style.configure("Accent.TButton", background=ACCENT_COLOR, foreground=FG_COLOR)
    style.map("Accent.TButton", background=[("active", "#29B6F6")])
    style.configure("Status.TLabel", font=HEADING_FONT)
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(fill="x", pady=(0, 15))
    status_label = ttk.Label(status_frame, text="❌ No Device", style="Status.TLabel", foreground=STATUS_DANGER)
    status_label.pack(side="left", padx=(0, 10))
    devices_box = tk.Listbox(status_frame, height=1, bg=FRAME_BG, fg=FG_COLOR, font=MONO_FONT, selectbackground="#444444", relief="flat")
    devices_box.pack(side="left", fill="x", expand=True)
    controls_frame = ttk.Frame(main_frame)
    controls_frame.pack(fill="x", pady=(0, 15))
    pkg_frame = ttk.LabelFrame(controls_frame, text="Package & File Management", padding=15)
    pkg_frame.pack(fill="x", pady=(0, 10))
    pkg_controls_row = ttk.Frame(pkg_frame)
    pkg_controls_row.pack(fill="x")
    package_var = tk.StringVar()
    package_dropdown = ttk.Combobox(pkg_controls_row, textvariable=package_var, font=UI_FONT, state="readonly")
    package_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 10))
    ttk.Button(pkg_controls_row, text="Refresh", command=lambda: package_dropdown.config(values=adb_list_packages())).pack(side="left", padx=5)
    ttk.Button(pkg_controls_row, text="Export APK", command=lambda: threading.Thread(target=export_apk, args=(package_var.get(), output_box), daemon=True).start()).pack(side="left", padx=5)
    ttk.Button(pkg_controls_row, text="Upload OBB", command=lambda: upload_obb_new_flow(output_box)).pack(side="left", padx=5)
    ttk.Button(pkg_controls_row, text="Run ADB Command", command=lambda: open_adb_command_window(root, output_box)).pack(side="left", padx=5)
    media_frame = ttk.LabelFrame(controls_frame, text="Media Management", padding=15)
    media_frame.pack(fill="x", pady=(0, 10))
    media_buttons_row = ttk.Frame(media_frame)
    media_buttons_row.pack(fill="x")
    ttk.Button(media_buttons_row, text="Save All Screenshots", command=lambda: threading.Thread(target=save_all_media, args=(output_box, "screenshots"), daemon=True).start()).pack(side="left", padx=5)
    ttk.Button(media_buttons_row, text="Save All Videos", command=lambda: threading.Thread(target=save_all_media, args=(output_box, "videos"), daemon=True).start()).pack(side="left", padx=5)
    ttk.Button(media_buttons_row, text="Clear All Screenshots/Videos", command=lambda: clear_all_media(output_box)).pack(side="left", padx=5)
    perf_frame = ttk.LabelFrame(controls_frame, text="Performance & Device Tools", padding=15)
    perf_frame.pack(fill="x", pady=(0, 10))
    perf_buttons_row = ttk.Frame(perf_frame)
    perf_buttons_row.pack(fill="x")
    ttk.Button(perf_buttons_row, text="FPS Display ON", command=lambda: toggle_fps_display("on", output_box)).pack(side="left", padx=5)
    ttk.Button(perf_buttons_row, text="FPS Display OFF", command=lambda: toggle_fps_display("off", output_box)).pack(side="left", padx=5)
    ttk.Button(perf_buttons_row, text="Passthrough ON", command=lambda: toggle_passthrough_mode("on", output_box)).pack(side="left", padx=5)
    ttk.Button(perf_buttons_row, text="Passthrough OFF", command=lambda: toggle_passthrough_mode("off", output_box)).pack(side="left", padx=5)
    ttk.Button(perf_buttons_row, text="Check Battery Status", command=lambda: threading.Thread(target=check_battery_status, args=(output_box,), daemon=True).start()).pack(side="left", padx=5)
    webhook_frame = ttk.LabelFrame(controls_frame, text="Discord Screenshot Monitor", padding=15)
    webhook_frame.pack(fill="x")
    webhook_controls_row = ttk.Frame(webhook_frame)
    webhook_controls_row.pack(fill="x")
    webhook_entry = ttk.Entry(webhook_controls_row, font=UI_FONT)
    webhook_entry.insert(0, DEFAULT_WEBHOOK)
    webhook_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    monitor_btn = ttk.Button(webhook_controls_row, text="Start Screenshot Monitor", style="Accent.TButton", command=lambda: toggle_monitor(webhook_entry, output_box, monitor_btn))
    monitor_btn.pack(side="left")
    output_frame = ttk.LabelFrame(main_frame, text="ADB Output Log", padding=15)
    output_frame.pack(fill="both", expand=True, pady=(15, 0))
    output_box = scrolledtext.ScrolledText(output_frame, bg=FRAME_BG, fg=FG_COLOR, font=MONO_FONT, wrap="word", relief="flat", padx=10, pady=10)
    output_box.pack(fill="both", expand=True)
    threading.Thread(target=device_monitor, args=(status_label, devices_box), daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    start_gui()


