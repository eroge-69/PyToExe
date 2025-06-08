import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import shutil
import os
import sys
import ctypes
import tempfile
import json
import threading
import zipfile
import requests
import platform

control_reg = r'''...'''
pc_reg = r'''...'''
user_reg = r'''...'''

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if not is_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, ' '.join(sys.argv), None, 1)
    except Exception as e:
        messagebox.showerror('Admin Required', f'Failed to relaunch as admin: {str(e)}')
    sys.exit(0)
apps = {
    "Mozilla Firefox": "Mozilla.Firefox",
    "Google Chrome": "Google.Chrome",
    "Opera GX": "Opera.OperaGX",
    "Apache OpenOffice": "Apache.OpenOffice",
    "VLC Media Player": "VideoLAN.VLC",
    "Adobe Acrobat Reader": "Adobe.Acrobat.Reader.64-bit",
    "WinRAR": "RARLab.WinRAR",
    "LibreOffice": "TheDocumentFoundation.LibreOffice",
    "VC++ Redistributable 2015+": "Microsoft.VCRedist.2015+.x64"
}

browsers = ["Mozilla Firefox", "Google Chrome", "Opera GX"]
text_editors = ["Apache OpenOffice", "LibreOffice"]
media_utils = ["VLC Media Player", "Adobe Acrobat Reader", "WinRAR", "VC++ Redistributable 2015+"]

powershell_path = shutil.which("powershell") or shutil.which("pwsh") or r"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
if not os.path.exists(powershell_path): raise EnvironmentError("PowerShell not found.")

prep_done_flag = os.path.join(tempfile.gettempdir(), "winget_prep_done.json")

current_theme = {"bg": "#001f3f", "fg": "#00FF00", "log_bg": "black", "log_fg": "#00FF00"}
root = tk.Tk()
root.title("Winget GUI Installer")
root.geometry("1000x700")
root.configure(bg=current_theme["bg"])
notebook = ttk.Notebook(root)
frame2 = tk.Frame(notebook, bg=current_theme["bg"])
frame4 = tk.Frame(notebook, bg=current_theme["bg"])
frame5 = tk.Frame(notebook, bg=current_theme["bg"])
notebook.add(frame2, text="Install Apps")
notebook.add(frame4, text="Manufacturer Tools")
notebook.add(frame5, text="Useful")
log_output = scrolledtext.ScrolledText(root, height=10, bg=current_theme["log_bg"], fg=current_theme["log_fg"])
log_output.pack(side="bottom", fill="x")
check_vars = {}
progress_label = tk.Label(root, text="", font=('Arial', 12), bg=current_theme["bg"], fg=current_theme["fg"])
progress_label.pack(side="bottom")
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(side="bottom", fill="x")

per_app_progress = {}  # App name to progress bar

progress_frame = tk.Frame(root, bg=current_theme["bg"])
progress_frame.pack(side="bottom", fill="x")

def add_per_app_progress_bar(app_name):
    label = tk.Label(progress_frame, text=app_name, font=('Arial', 10), bg=current_theme["bg"], fg=current_theme["fg"])
    label.pack()
    var = tk.DoubleVar()
    bar = ttk.Progressbar(progress_frame, variable=var, maximum=100)
    bar.pack(fill="x", padx=10)
    per_app_progress[app_name] = var

def run_command(cmd, on_complete=None):
    def t():
        install_btn.config(state="disabled")
        tools_btn.config(state="disabled")
        progress_label.config(text="Running...")
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)
        for l in p.stdout:
            log_output.insert(tk.END, l)
            log_output.see(tk.END)
        p.wait()
        progress_label.config(text="Done")
        if on_complete: on_complete()
        install_btn.config(state="normal")
        tools_btn.config(state="normal")
    threading.Thread(target=t).start()

def write_reg_files():
    try:
        for name, content in [("control.reg", control_reg), ("pc.reg", pc_reg), ("user.reg", user_reg)]:
            if content.strip() == "..." or "..." in content:
                log_output.insert(tk.END, f"Skipped writing {name}: placeholder content.\n")
                continue
            path = os.path.join(tempfile.gettempdir(), name)
            with open(path, "w") as f:
                f.write(content)
            subprocess.run(["reg", "import", path], shell=True)
    except Exception as e:
        log_output.insert(tk.END, f"Registry import failed: {str(e)}\n")
    for name, content in [("control.reg", control_reg), ("pc.reg", pc_reg), ("user.reg", user_reg)]:
        path = os.path.join(tempfile.gettempdir(), name)
        with open(path, "w") as f: f.write(content)
        subprocess.run(["reg", "import", path], shell=True)

def run_preparation():
    if os.path.exists(prep_done_flag): show_main_interface(); return
    write_reg_files()
    with open(prep_done_flag, "w") as f: json.dump({"prepared": True}, f)
    show_main_interface()

def show_main_interface():
    start_frame.pack_forget(); notebook.pack(expand=1, fill="both")

def run_installation():
    sel = [n for n, v in check_vars.items() if v.get() and n in apps]
    if not sel: messagebox.showinfo("No selection", "Select at least one application."); return
    install_btn.config(state="disabled")
    total = len(sel)
    for idx, name in enumerate(sel):
        add_per_app_progress_bar(name)
        def update(val):
            per_app_progress[name].set(val)
            progress_var.set(((idx + val / 100) / total) * 100)
            root.update_idletasks()
        run_command(f'{powershell_path} -Command "winget install -e --id {apps[name]} --accept-source-agreements"', on_complete=lambda: update(100))

def download_with_progress(url, path, title=""):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, stream=True)
    if r.status_code != 200:
        log_output.insert(tk.END, f"[{title}] HTTP {r.status_code} - download failed.\n")
        return
    total_length = int(r.headers.get("content-length", 0))
    downloaded = 0
    log_output.insert(tk.END, f"[{title}] Starting download to {path}\n")
    if total_length:
        progress_label.config(text=f"Downloading {title}...")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_length:
                percent = downloaded / total_length * 100
                if title in per_app_progress:
                    per_app_progress[title].set(percent)
                progress_var.set(percent)
                root.update_idletasks()
    progress_label.config(text="Download complete.")
    try:
        size = os.path.getsize(path)
        log_output.insert(tk.END, f"[{title}] Downloaded file size: {size} bytes\n")
    except Exception as e:
        log_output.insert(tk.END, f"[{title}] Size check failed: {str(e)}\n")
def run_manufacturer_tools():
    tools_btn.config(state="disabled")
    for name in selected: add_per_app_progress_bar(name)
    def done(): tools_btn.config(state="normal")
    pending = len(selected)
    def mark_done():
        nonlocal pending
        pending -= 1
        if pending <= 0: done()

    if check_vars.get("MSI Center") and check_vars["MSI Center"].get():
        def msi():
            url = "https://download.msi.com/uti_exe/desktop/MSI-Center.zip"
            z = os.path.join(tempfile.gettempdir(), "MSI-Center.zip")
            ex = os.path.join(tempfile.gettempdir(), "msi_center")
            try:
                download_with_progress(url, z, "MSI Center")
                with zipfile.ZipFile(z, 'r') as ref: ref.extractall(ex)
                for root_dir, _, files in os.walk(ex):
                    for file in files:
                        if file.lower().endswith(('.exe', '.msi')):
                            path = os.path.join(root_dir, file)
                            run_command(cmd, on_complete=mark_done); return
                log_output.insert(tk.END, "No installer found in MSI Center ZIP.\n"); mark_done()
            except Exception as e:
                log_output.insert(tk.END, f"MSI Center install failed: {str(e)}\n"); mark_done()
        threading.Thread(target=msi).start()

    if check_vars.get("Dell SupportAssist") and check_vars["Dell SupportAssist"].get():
        script = r'''$workdir = "C:\\Temp\\"; If (!(Test-Path -Path $workdir)){ New-Item -Path $workdir -ItemType directory }; $source = "https://downloads.dell.com/serviceability/catalog/SupportAssistInstaller.exe"; $destination = "$workdir\\SupportAssistInstaller.exe"; Invoke-WebRequest $source -OutFile $destination; Start-Process -FilePath "$destination" -ArgumentList "/S"'''
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w", encoding="utf-8") as temp_script:
            temp_script.write(script)
            run_command(f'{powershell_path} -ExecutionPolicy Bypass -File "{temp_script.name}"', on_complete=mark_done)

    if check_vars.get("NVIDIA App") and check_vars["NVIDIA App"].get():
        def nvidia():
            url = "https://us.download.nvidia.com/nvapp/client/11.0.4.148/NVIDIA_app_v11.0.4.148.exe"
            exe = os.path.join(tempfile.gettempdir(), "NVIDIA_app.exe")
            download_with_progress(url, exe, "NVIDIA App")
            run_command(f'"{exe}" /S', on_complete=mark_done)
        threading.Thread(target=nvidia).start()

    if check_vars.get("HP Support Tool") and check_vars["HP Support Tool"].get():
        def hp():
            url = "https://ftp.hp.com/pub/softpaq/sp160001-160500/sp160047.exe"
            exe = os.path.join(tempfile.gettempdir(), "hp_support_tool.exe")
            download_with_progress(url, exe, "HP Support Tool")
            run_command(f'"{exe}" /s', on_complete=mark_done)
        threading.Thread(target=hp).start()

    if check_vars.get("ASUS Armory Crate") and check_vars["ASUS Armory Crate"].get():
        run_command(f'{powershell_path} -Command "winget install -e --id Asus.ArmouryCrate --accept-source-agreements"', on_complete=mark_done)
        run_command(f'{powershell_path} -Command "winget install -e --id Asus.ArmouryCrate --accept-source-agreements"', on_complete=mark_done)
        return

    if check_vars.get("Gigabyte Control Center") and check_vars["Gigabyte Control Center"].get():
        def gigabyte():
            url = "https://download.gigabyte.com/FileList/Utility/GCC_25.05.05.01.zip"
            z = os.path.join(tempfile.gettempdir(), "GigabyteControlCenter.zip")
            ex = os.path.join(tempfile.gettempdir(), "gigabyte_control_center")
            try:
                download_with_progress(url, z, "Gigabyte Control Center")
                with zipfile.ZipFile(z, "r") as ref:
                    ref.extractall(ex)
                for root_dir, _, files in os.walk(ex):
                    for file in files:
                        if file.lower().endswith((".exe", ".msi")):
                            path = os.path.join(root_dir, file)
                            run_command(cmd, on_complete=mark_done)
                            return
                log_output.insert(tk.END, "No installer found in Gigabyte Control Center ZIP.\n")
                mark_done()
            except Exception as e:
                log_output.insert(tk.END, f"Gigabyte Control Center install failed: {str(e)}\n")
                mark_done()
        threading.Thread(target=gigabyte).start()

    if check_vars.get("AMD Adrenalin") and check_vars["AMD Adrenalin"].get():
        def amd():
            url = "https://drivers.amd.com/drivers/installer/25.10/whql/amd-software-adrenalin-edition-25.6.1-minimalsetup-250602_web.exe"
            exe_path = os.path.join(tempfile.gettempdir(), "amd_adrenalin.exe")
            try:
                download_with_progress(url, exe_path, "AMD Adrenalin")
                run_command(f'"{exe_path}" /S', on_complete=mark_done)
            except Exception as e:
                log_output.insert(tk.END, f"AMD Adrenalin install failed: {str(e)}\n")
                mark_done()
        threading.Thread(target=amd).start()


def add_group_label(frame, text):
    tk.Label(frame, text=text, font=('Arial', 16, 'bold'), bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor='w', pady=(10, 0))

for group, names in [("Browsers", browsers), ("Text Editors", text_editors), ("Other Utilities", media_utils)]:
    add_group_label(frame2, group)
    for name in names:
        var = tk.BooleanVar()
        tk.Checkbutton(frame2, text=name, variable=var, font=('Arial', 14), bg=current_theme["bg"], fg=current_theme["fg"], selectcolor='red').pack(anchor='w')
        check_vars[name] = var

install_btn = tk.Button(frame2, text="Install Selected Apps", command=run_installation, font=('Arial', 14), bg='blue', fg='white')
install_btn.pack(pady=20)

add_group_label(frame4, "Laptop Tools")
var = tk.BooleanVar()
tk.Checkbutton(frame4, text="Dell SupportAssist", variable=var, font=('Arial', 14), bg=current_theme["bg"], fg=current_theme["fg"], selectcolor="red").pack(anchor="w")
check_vars["Dell SupportAssist"] = var
var = tk.BooleanVar()
tk.Checkbutton(frame4, text="HP Support Tool", variable=var, font=('Arial', 14), bg=current_theme["bg"], fg=current_theme["fg"], selectcolor="red").pack(anchor="w")
check_vars["HP Support Tool"] = var

add_group_label(frame4, "Mainboard Utilities")
var = tk.BooleanVar()
tk.Checkbutton(frame4, text="ASUS Armory Crate", variable=var, font=('Arial', 14), bg=current_theme["bg"], fg=current_theme["fg"], selectcolor="red").pack(anchor="w")
check_vars["ASUS Armory Crate"] = var
var = tk.BooleanVar()
tk.Checkbutton(frame4, text="Gigabyte Control Center", variable=var, font=('Arial', 14), bg=current_theme["bg"], fg=current_theme["fg"], selectcolor="red").pack(anchor="w")
check_vars["Gigabyte Control Center"] = var
var = tk.BooleanVar()
tk.Checkbutton(frame4, text="MSI Center", variable=var, font=('Arial', 14), bg=current_theme["bg"], fg=current_theme["fg"], selectcolor="red").pack(anchor="w")
check_vars["MSI Center"] = var

add_group_label(frame4, "Graphics Drivers")
var = tk.BooleanVar()
tk.Checkbutton(frame4, text="NVIDIA App", variable=var, font=('Arial', 14), bg=current_theme["bg"], fg=current_theme["fg"], selectcolor="red").pack(anchor="w")
check_vars["NVIDIA App"] = var
var = tk.BooleanVar()
tk.Checkbutton(frame4, text="AMD Adrenalin", variable=var, font=('Arial', 14), bg=current_theme["bg"], fg=current_theme["fg"], selectcolor="red").pack(anchor="w")
check_vars["AMD Adrenalin"] = var
tools_btn = tk.Button(frame4, text="Install Tools", command=run_manufacturer_tools, font=('Arial', 14), bg='blue', fg='white')
tools_btn.pack(pady=20)

hp_label = tk.Label(frame5, text="TOOLS", font=('Arial', 16), bg=current_theme["bg"], fg=current_theme["fg"])
hp_label.pack(pady=10)

def download_OCCT():
    add_per_app_progress_bar("OCCT")
    exe = os.path.join(tempfile.gettempdir(), "OCCT_Setup.exe")
    def run_occt():
        download_with_progress("https://dl.ocbase.com/per/stable/OCCT.exe", exe, "OCCT")
        try:
            subprocess.Popen([exe])
        except Exception as e:
            log_output.insert(tk.END, f"Failed to launch OCCT: {str(e)}\n")
    threading.Thread(target=run_occt).start()

tk.Button(frame5, text="OCCT", command=download_OCCT, font=('Arial', 14), bg='RED', fg='BLACK').pack(pady=10)

def download_furmark():
    add_per_app_progress_bar("Furmark")
    exe = os.path.join(tempfile.gettempdir(), "Furmark_Setup.exe")
    def run_furmark_download():
        download_with_progress("https://gpumagick.com/downloads/files/2025/fm2/FurMark_2.8.2.0_Win64_Setup.exe", exe, "Furmark")
        try:
            subprocess.Popen([exe])
        except Exception as e:
            log_output.insert(tk.END, f"Failed to launch Furmark: {str(e)}\n")
    threading.Thread(target=run_furmark_download).start()

tk.Button(frame5, text="Furmark", command=download_furmark, font=('Arial', 14), bg='orange', fg='black').pack(pady=10)

sys_info = platform.platform()
tk.Label(frame5, text=f"System: {sys_info}", font=('Arial', 12), bg=current_theme["bg"], fg=current_theme["fg"]).pack(pady=10)

start_frame = tk.Frame(root, bg=current_theme["bg"])
start_label = tk.Label(start_frame, text="Prepare system or skip to GUI", font=('Arial', 18), bg=current_theme["bg"], fg=current_theme["fg"])
start_label.pack(pady=40)
start_button = tk.Button(start_frame, text="Prepare", command=run_preparation, font=('Arial', 20), bg='green', fg='white')
start_button.pack(pady=10)
skip_button = tk.Button(start_frame, text="Skip", command=show_main_interface, font=('Arial', 20), bg='gray', fg='white')
skip_button.pack(pady=10)
start_frame.pack(expand=True, fill='both')
if os.path.exists(prep_done_flag):
    start_label.config(text="Preparation already done. You can prepare again or skip.")
else:
    skip_button.pack_forget()

messagebox.showinfo("DEBUG", "GUI started successfully")
root.mainloop()
