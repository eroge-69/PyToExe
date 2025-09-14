# save as quick_setup.py
import os
import sys
import subprocess
import ctypes
import tempfile
import tkinter as tk
from tkinter import messagebox, scrolledtext

# -----------------------
# admin check
# -----------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# -----------------------
# Program list (name -> winget id)
# update/add as you like; IDs from winget repo examples
# -----------------------
PROGRAMS = {
    "Google Chrome": "Google.Chrome",
    "Mozilla Firefox": "Mozilla.Firefox",
    "Visual Studio Code": "Microsoft.VisualStudioCode",
    "7-Zip": "7zip.7zip",
    "VLC": "VideoLAN.VLC",
    "Git for Windows": "Git.Git",
    "Python 3.11": "Python.Python.3.11",
    # add more here
}

# -----------------------
# Build winget command for a given id
# -----------------------
def winget_install_cmd(pkg_id):
    # --accept-package-agreements and --accept-source-agreements may help automation
    return ["winget", "install", "--id", pkg_id, "-e", "--accept-package-agreements", "--accept-source-agreements", "--scope", "machine"]

# -----------------------
# Run installer sequence, stream output to a window
# -----------------------
def install_selected(selected_ids, output_widget):
    if not selected_ids:
        messagebox.showinfo("Bilgi", "Önce en az bir uygulama seçin.")
        return
    for pid in selected_ids:
        cmd = winget_install_cmd(pid)
        output_widget.insert(tk.END, f"\n--- Installing {pid} ---\n")
        output_widget.see(tk.END)
        try:
            # run and stream output
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in p.stdout:
                output_widget.insert(tk.END, line)
                output_widget.see(tk.END)
            p.wait()
            output_widget.insert(tk.END, f"Finished {pid} (return {p.returncode})\n")
        except FileNotFoundError:
            output_widget.insert(tk.END, "winget bulunamadı. Lütfen Windows Package Manager (winget) yüklü olduğundan emin olun.\n")
            break
        except Exception as e:
            output_widget.insert(tk.END, f"Hata: {e}\n")
    messagebox.showinfo("Bitti", "Seçilen kurulumlar tamamlandı (veya hata verdi).")

# -----------------------
# PowerShell telemetry disable script generator
# -----------------------
def make_telemetry_ps1():
    ps = r'''
# Telemetry disable script (requires admin). Use at your own risk.
# This script attempts:
# 1) Set AllowTelemetry (DataCollection) to 0 (where possible)
# 2) Disable Connected User Experiences and Telemetry service (DiagTrack / dmwappushsvc)
# 3) Disable some scheduled tasks known to collect telemetry
# 4) Stop services immediately

# Note: Some edits require Windows Enterprise/Server for full effect. User consent and MS policies may override.
Set-StrictMode -Version Latest

# 1) Registry - DataCollection
Try {
    New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows" -ErrorAction SilentlyContinue | Out-Null
    New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -ErrorAction SilentlyContinue | Out-Null
    New-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -PropertyType DWord -Force | Out-Null
    Write-Output "Set AllowTelemetry = 0"
} Catch {
    Write-Output "Registry write failed: $_"
}

# 2) Disable telemetry services
$services = @("DiagTrack","dmwappushsvc","WdiServiceHost","WdiSystemHost")
foreach($s in $services){
    Try {
        if (Get-Service -Name $s -ErrorAction SilentlyContinue) {
            Set-Service -Name $s -StartupType Disabled -ErrorAction SilentlyContinue
            Stop-Service -Name $s -Force -ErrorAction SilentlyContinue
            Write-Output "Disabled/Stopped service $s"
        }
    } Catch {
        Write-Output "Service change failed for $s: $_"
    }
}

# 3) Disable Microsoft Compatibility Appraiser task (common)
$tasks = @(
    "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
    "\Microsoft\Windows\Application Experience\ProgramDataUpdater",
    "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator"
)
foreach($t in $tasks){
    Try {
        $td = Get-ScheduledTask -TaskPath (Split-Path $t -Parent) -ErrorAction SilentlyContinue | Where-Object { $_.TaskName -eq (Split-Path $t -Leaf) }
        if ($td) {
            Disable-ScheduledTask -TaskName (Split-Path $t -Leaf) -TaskPath (Split-Path $t -Parent) -ErrorAction SilentlyContinue
            Write-Output "Disabled scheduled task $t"
        } else {
            Write-Output "Task not found: $t"
        }
    } Catch {
        Write-Output "Task disable failed for $t: $_"
    }
}

# 4) Force group policy refresh (best-effort)
Try {
    gpupdate /force | Out-Null
    Write-Output "Requested gpupdate /force"
} Catch {
    Write-Output "gpupdate failed or not available"
}

Write-Output "Telemetry-disable script finished. Some settings may require reboot to take effect."
'''
    return ps

def run_telemetry_disable(output_widget):
    ps_content = make_telemetry_ps1()
    tmp = os.path.join(tempfile.gettempdir(), "disable_telemetry.ps1")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(ps_content)
    output_widget.insert(tk.END, f"\n--- Running telemetry disable script: {tmp} ---\n")
    output_widget.see(tk.END)
    try:
        # Run PowerShell script with bypass executionpolicy
        proc = subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", tmp],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            output_widget.insert(tk.END, line)
            output_widget.see(tk.END)
        proc.wait()
        output_widget.insert(tk.END, f"Telemetry script finished (return {proc.returncode})\n")
    except Exception as e:
        output_widget.insert(tk.END, f"Hata çalıştırma sırasında: {e}\n")

# -----------------------
# GUI
# -----------------------
def build_gui():
    root = tk.Tk()
    root.title("Quick Windows Setup - Tek Tık Kurulum")
    root.geometry("780x560")

    top = tk.Frame(root)
    top.pack(fill=tk.X, padx=8, pady=6)

    label = tk.Label(top, text="İnşa edilmesi: Uygulamaları seç ve 'Install' tuşuna bas.", font=("Segoe UI", 10))
    label.pack(side=tk.LEFT)

    # checkboxes
    cb_frame = tk.LabelFrame(root, text="Programlar (winget ID kullanarak)", padx=8, pady=8)
    cb_frame.pack(fill=tk.X, padx=8, pady=6)

    vars_map = {}
    for name, pid in PROGRAMS.items():
        v = tk.IntVar(value=0)
        cb = tk.Checkbutton(cb_frame, text=f"{name}  ({pid})", variable=v, anchor="w", justify="left")
        cb.pack(fill=tk.X, anchor="w")
        vars_map[pid] = v

    btn_frame = tk.Frame(root)
    btn_frame.pack(fill=tk.X, padx=8, pady=6)

    output = scrolledtext.ScrolledText(root, height=18)
    output.pack(fill=tk.BOTH, padx=8, pady=6, expand=True)

    def on_install():
        selected = [pid for pid, v in vars_map.items() if v.get() == 1]
        install_selected(selected, output)

    def on_disable_telemetry():
        if messagebox.askyesno("Uyarı", "Telemetry/diagnostics ayarlarını değiştirmek istiyor musunuz? (Yönetici gerekli)"):
            run_telemetry_disable(output)

    install_btn = tk.Button(btn_frame, text="Install selected apps", command=on_install)
    install_btn.pack(side=tk.LEFT, padx=6)

    tele_btn = tk.Button(btn_frame, text="Disable telemetry (PowerShell)", command=on_disable_telemetry)
    tele_btn.pack(side=tk.LEFT, padx=6)

    quit_btn = tk.Button(btn_frame, text="Çıkış", command=root.quit)
    quit_btn.pack(side=tk.RIGHT, padx=6)

    return root

# -----------------------
# Main
# -----------------------
def main():
    if os.name != 'nt':
        print("Bu araç sadece Windows üzerinde çalışır.")
        sys.exit(1)
    if not is_admin():
        messagebox.showwarning("Yönetici gerekiyor", "Bu uygulama yönetici (admin) olarak çalıştırılmalıdır. Lütfen sağ tıklayıp 'Run as administrator' ile tekrar başlatın.")
        # optionally re-launch as admin
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        except Exception:
            pass
        sys.exit(0)

    root = build_gui()
    root.mainloop()

if __name__ == "__main__":
    main()
