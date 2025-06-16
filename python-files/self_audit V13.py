import os
import subprocess
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog
import getpass
from datetime import datetime
import winreg
import string
import win32wnet
import win32print
import psutil
from win32file import GetDriveType, DRIVE_REMOVABLE

# --- Feature Functions ---

def check_app_access(app_name, possible_paths):
    for path in possible_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen(path, shell=True)
                return "Yes"
            except Exception:
                return "No"
    return "No"

def check_sticky_notes():
    paths = [
        r"C:\Windows\System32\StikyNot.exe",
        r"C:\Program Files\WindowsApps\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\StickyNotes.exe",
        r"C:\Program Files\Microsoft Office\root\Office16\onenote.exe",
    ]
    return check_app_access("Sticky Notes", paths)

def check_snipping_tool():
    paths = [
        r"C:\Windows\System32\SnippingTool.exe",
        r"C:\Windows\System32\SnipAndSketch.exe",
        r"C:\Program Files\WindowsApps\Microsoft.ScreenSketch_8wekyb3d8bbwe\ScreenSketch.exe"
    ]
    return check_app_access("Snipping Tool", paths)

def check_print_screen_feature():
    paths = [
        r"C:\Windows\System32\SnippingTool.exe",
        r"C:\Windows\System32\SnipAndSketch.exe",
        r"C:\Program Files\WindowsApps\Microsoft.ScreenSketch_8wekyb3d8bbwe\ScreenSketch.exe"
    ]
    return "Yes" if any(os.path.exists(path) for path in paths) else "No"

def get_hidden_drives_c_to_g():
    hidden_drives = []
    drive_map = {'C': 4, 'D': 8, 'E': 16, 'F': 32, 'G': 64}
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        )
        value, _ = winreg.QueryValueEx(key, "NoDrives")
        winreg.CloseKey(key)
        for drive, bit in drive_map.items():
            if value & bit:
                hidden_drives.append(drive)
    except FileNotFoundError:
        pass
    return ", ".join(hidden_drives) if hidden_drives else "None"

def get_mapped_network_drives():
    mapped_drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:"
        try:
            remote_name = win32wnet.WNetGetConnection(drive)
            mapped_drives.append(f"{drive} -> {remote_name}")
        except Exception:
            continue
    return ", ".join(mapped_drives) if mapped_drives else "None"

def check_unauthorized_websites():
    sites = ["facebook.com", "youtube.com", "instagram.com"]
    for site in sites:
        try:
            response = subprocess.run(["ping", site, "-n", "1"], capture_output=True, text=True, timeout=5)
            if not any(term in response.stdout.lower() for term in ["timed out", "could not find host", "unreachable"]):
                return "Yes"
        except Exception:
            pass
    return "No"

def list_real_connected_printers():
    try:
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS,
            None,
            2
        )
        virtual_keywords = ["fax", "onenote", "xps", "pdf", "anydesk"]
        real_printers = [printer['pPrinterName'] for printer in printers if not any(vk in printer['pPrinterName'].lower() for vk in virtual_keywords)]
        return ", ".join(real_printers) if real_printers else "None"
    except Exception:
        return "Error retrieving printers"

def check_right_click_access():
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
    test_file = os.path.join(desktop_path, "right_click_test.txt")
    try:
        subprocess.run([
            "powershell", "-Command",
            f"New-Item -Path '{test_file}' -ItemType File -Force"
        ], capture_output=True, text=True)
        return "Yes" if os.path.exists(test_file) else "No"
    except Exception:
        return "No"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def check_paste_access():
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
    temp_source = os.path.join(desktop_path, "temp_paste_source.txt")
    temp_dest = os.path.join(desktop_path, "temp_paste_result.txt")
    try:
        with open(temp_source, "w") as f:
            f.write("Clipboard test.")
        shutil.copy(temp_source, temp_dest)
        return "Yes" if os.path.exists(temp_dest) else "No"
    except Exception:
        return "No"
    finally:
        for f in [temp_source, temp_dest]:
            if os.path.exists(f):
                os.remove(f)

def check_usb_drives():
    usb_drives = []
    for letter in string.ascii_uppercase:
        if letter > 'G':
            break
        drive = f"{letter}:\\"
        try:
            if psutil.disk_usage(drive):
                if GetDriveType(drive) == DRIVE_REMOVABLE:
                    usb_drives.append(drive)
        except Exception:
            continue
    return f"External USB Drives Detected: {', '.join(usb_drives)}" if usb_drives else "No External USB Drives Detected"

def log_audit_results(results, log_path):
    now = datetime.now()
    filename = os.path.join(log_path, f"audit_{now.strftime('%Y%m%d_%H%M%S')}.txt")
    with open(filename, "w") as f:
        f.write(f"Audit Log - {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Username: {getpass.getuser()}\n\n")
        for key, value in results.items():
            f.write(f"{key}: {value}\n")

# --- GUI Setup ---
app = tk.Tk()
app.title("Self Audit System")
app_width, app_height = 800, 530
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x = (screen_width // 2) - (app_width // 2)
y = (screen_height // 2) - (app_height // 2)
app.geometry(f"{app_width}x{app_height}+{x}+{y}")
app.resizable(False, False)

left_frame = tk.Frame(app, width=300, padx=10, pady=10)
left_frame.pack(side="left", fill="y")

right_frame = tk.Frame(app, padx=10, pady=10)
right_frame.pack(side="right", fill="both", expand=True)

tk.Label(left_frame, text="System Audit Panel", font=("Arial", 14, "bold")).pack(pady=(0, 10), anchor="center")

username_var = tk.StringVar(value=getpass.getuser())
tk.Label(left_frame, text="Username:").pack(anchor="w")
tk.Entry(left_frame, textvariable=username_var, state="readonly").pack(fill="x")

datetime_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
tk.Label(left_frame, text="Date & Time:").pack(anchor="w", pady=(10, 0))
tk.Entry(left_frame, textvariable=datetime_var, state="readonly").pack(fill="x")

tk.Label(left_frame, text="Zimbra Email Access:").pack(anchor="w", pady=(10, 0))
zimbra_var = tk.StringVar()
tk.Radiobutton(left_frame, text="Yes", variable=zimbra_var, value="Yes").pack(anchor="w")
tk.Radiobutton(left_frame, text="No", variable=zimbra_var, value="No").pack(anchor="w")

status_label = tk.Label(left_frame, text="Status: Ready", fg="gray")
status_label.pack(fill="x", pady=(10, 0))

log_directory = r"Z:\Public\Protective_Transient\Karthikeyan\monitor_logs"
audit_results = {}

def run_audit():
    global audit_results
    if zimbra_var.get() not in ["Yes", "No"]:
        messagebox.showerror("Input Error", "Please select Zimbra Email Access (Yes or No).")
        return

    status_label.config(text="Status: Auditing...", fg="blue")
    app.update()

    audit_results = {
        "Sticky Notes": check_sticky_notes(),
        "Snipping Tool": check_snipping_tool(),
        "Hidden Drives (C-G)": get_hidden_drives_c_to_g(),
        "Mapped Network Drives": get_mapped_network_drives(),
        "Website Access": check_unauthorized_websites(),
        "Printers": list_real_connected_printers(),
        "Right-click on Desktop": check_right_click_access(),
        "Paste on Desktop": check_paste_access(),
        "External USB Access": check_usb_drives(),
        "Printscreen Access": check_print_screen_feature(),
        "Zimbra access to outside email": "Yes" if zimbra_var.get() == "Yes" else "No"
    }

    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    for key, value in audit_results.items():
        result_text.insert(tk.END, f"{key}: {value}\n")
    result_text.config(state="disabled")

    log_audit_results(audit_results, log_directory)
    export_button.config(state="normal")
    status_label.config(text="Status: Audit Complete", fg="green")

def export_results_to_csv():
    if not audit_results:
        messagebox.showerror("No Data", "No audit data available to export.")
        return

    export_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save audit results as CSV"
    )

    if not export_path:
        return

    try:
        with open(export_path, "w", encoding="utf-8") as f:
            f.write("Parameter,Result\n")
            for key, value in audit_results.items():
                f.write(f"{key},{value}\n")
        messagebox.showinfo("Export Successful", f"Audit results exported to:\n{export_path}")
    except Exception as e:
        messagebox.showerror("Export Failed", f"Error: {e}")

# Buttons
audit_button = tk.Button(left_frame, text="Start Audit", bg="#007acc", fg="white", command=run_audit)
audit_button.pack(fill="x", pady=(20, 5))

export_button = tk.Button(left_frame, text="Export Result", bg="#5cb85c", fg="white", state="disabled", command=export_results_to_csv)
export_button.pack(fill="x", pady=5)

tk.Label(right_frame, text="Audit Results", font=("Arial", 14, "bold")).pack(anchor="w")
result_text = tk.Text(right_frame, wrap="word", height=25, state="disabled", bg="#f5f5f5", font=("Courier New", 10))
result_text.pack(fill="both", expand=True, pady=(10, 0))

app.mainloop()

