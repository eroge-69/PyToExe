import os
import sys
import shutil
import configparser
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "settings.ini")
DLL_PATH = os.path.join(os.path.dirname(__file__), "bin", "mt_predictor.dll")

def ensure_config():
    cfg = configparser.ConfigParser()
    if not os.path.exists(CONFIG_PATH):
        cfg['MTP'] = {'offline_mode': 'False', 'nt_addon_path': ''}
        with open(CONFIG_PATH, 'w') as f:
            cfg.write(f)
    cfg.read(CONFIG_PATH)
    return cfg

class MTPInstallerApp:
    def __init__(self, root):
        self.root = root
        root.title("MTP Portable Manager (Tkinter)")
        root.geometry("720x520")
        self.cfg = ensure_config()

        # Top frame buttons
        top = tk.Frame(root)
        top.pack(fill='x', padx=10, pady=8)

        tk.Button(top, text="Select MTP DLL", command=self.select_mtp_dll, width=16).pack(side='left', padx=4)
        tk.Button(top, text="Auto-detect NT AddOn Path", command=self.autodetect_nt_folder, width=22).pack(side='left', padx=4)
        tk.Button(top, text="Choose NT AddOn Folder", command=self.select_nt_folder, width=18).pack(side='left', padx=4)
        tk.Button(top, text="Test Launch NinjaTrader", command=self.test_launch_nt, width=18).pack(side='left', padx=4)

        # Offline toggle
        self.offline_var = tk.BooleanVar(value=self.cfg.getboolean('MTP', 'offline_mode', fallback=False))
        tk.Checkbutton(top, text="Offline Mode (simulate)", variable=self.offline_var, command=self.save_config).pack(side='right', padx=6)

        # Middle frame: install/uninstall/export
        mid = tk.Frame(root)
        mid.pack(fill='x', padx=10, pady=6)
        tk.Button(mid, text="Install MTP", command=self.install_mtp, width=18, bg='#4CAF50', fg='white').pack(side='left', padx=6)
        tk.Button(mid, text="Uninstall MTP", command=self.uninstall_mtp, width=18, bg='#f44336', fg='white').pack(side='left', padx=6)
        tk.Button(mid, text="Export Config + DLL to USB/Folder", command=self.export_to_usb, width=28).pack(side='left', padx=6)

        # Status label
        self.status = tk.Label(root, text="Ready", anchor='w', fg='darkgreen')
        self.status.pack(fill='x', padx=12, pady=4)

        # Log window
        log_frame = tk.LabelFrame(root, text="Log")
        log_frame.pack(fill='both', expand=True, padx=12, pady=8)
        self.log = scrolledtext.ScrolledText(log_frame, wrap='word', height=18)
        self.log.pack(fill='both', expand=True)
        self.log.insert('end', "Log started...\n")

        # Init paths
        self.mtp_dll_path = DLL_PATH if os.path.exists(DLL_PATH) else ""
        self.nt_folder_path = self.cfg.get('MTP', 'nt_addon_path', fallback="")

        # show initial status
        if self.mtp_dll_path:
            self.log_message(f"Found bundled DLL at: {self.mtp_dll_path}")
        if self.nt_folder_path:
            self.log_message(f"Loaded saved NT addon path: {self.nt_folder_path}")
        self.update_status("Ready")

    def select_mtp_dll(self):
        path = filedialog.askopenfilename(title="Select MTP DLL", filetypes=[("DLL Files","*.dll"),("All files","*.*")])
        if path:
            self.mtp_dll_path = path
            self.log_message(f"Selected MTP DLL: {path}")
            self.update_status("MTP DLL selected")

    def autodetect_nt_folder(self):
        candidates = []
        if sys.platform.startswith('win'):
            pf = os.environ.get('ProgramFiles', r"C:\Program Files")
            pf_x86 = os.environ.get('ProgramFiles(x86)', r"C:\Program Files (x86)")
            candidates += [
                os.path.join(pf, "NinjaTrader 8", "bin", "Custom", "AddOns"),
                os.path.join(pf_x86, "NinjaTrader 8", "bin", "Custom", "AddOns"),
                os.path.join(os.path.expanduser("~"), "Documents", "NinjaTrader 8", "bin", "Custom", "AddOns"),
            ]
        else:
            # Non-Windows fallback (user must pick folder)
            candidates += [os.path.join(os.path.expanduser("~"), "NinjaTrader 8", "bin", "Custom", "AddOns")]

        found = None
        for p in candidates:
            if os.path.exists(p):
                found = p
                break
        if found:
            self.nt_folder_path = found
            self.cfg.set('MTP', 'nt_addon_path', found)
            with open(CONFIG_PATH, 'w') as f:
                self.cfg.write(f)
            self.log_message(f"Auto-detected NinjaTrader AddOn path: {found}")
            self.update_status("Auto-detected NT path")
        else:
            self.log_message("Auto-detect failed. Please choose folder manually.")
            self.update_status("Auto-detect failed")
            messagebox.showinfo("Not found", "Could not auto-detect NinjaTrader. Please select the folder manually.")

    def select_nt_folder(self):
        p = filedialog.askdirectory(title="Select NinjaTrader AddOn Folder")
        if p:
            self.nt_folder_path = p
            self.cfg.set('MTP', 'nt_addon_path', p)
            with open(CONFIG_PATH, 'w') as f:
                self.cfg.write(f)
            self.log_message(f"Selected NinjaTrader AddOn folder: {p}")
            self.update_status("NT folder selected")

    def install_mtp(self):
        if not self.mtp_dll_path:
            messagebox.showerror("Missing DLL", "No MTP DLL selected or bundled. Please select it first.")
            return
        if not self.nt_folder_path:
            messagebox.showerror("Missing NT Path", "No NinjaTrader AddOn folder selected. Auto-detect or choose folder.")
            return
        try:
            dst = os.path.join(self.nt_folder_path, os.path.basename(self.mtp_dll_path))
            shutil.copy2(self.mtp_dll_path, dst)
            self.log_message(f"Installed MTP DLL to: {dst}")
            self.update_status("Install successful")
            messagebox.showinfo("Installed", "MTP DLL installed successfully.")
        except Exception as e:
            self.log_message(f"Install failed: {e}")
            self.update_status("Install failed")
            messagebox.showerror("Error", f"Install failed:\n{e}")

    def uninstall_mtp(self):
        if not self.nt_folder_path:
            messagebox.showerror("Missing NT Path", "No NinjaTrader AddOn folder selected.")
            return
        tgt = os.path.join(self.nt_folder_path, os.path.basename(self.mtp_dll_path)) if self.mtp_dll_path else None
        if tgt and os.path.exists(tgt):
            try:
                os.remove(tgt)
                self.log_message(f"Removed MTP DLL from: {tgt}")
                self.update_status("Uninstall successful")
                messagebox.showinfo("Removed", "MTP DLL removed from NinjaTrader folder.")
            except Exception as e:
                self.log_message(f"Uninstall failed: {e}")
                self.update_status("Uninstall failed")
                messagebox.showerror("Error", f"Failed to remove DLL:\n{e}")
        else:
            self.log_message("Uninstall skipped: DLL not found in NT folder.")
            messagebox.showinfo("Not found", "MTP DLL not found in target folder.")

    def test_launch_nt(self):
        # Try to find NinjaTrader executable relative to saved addon path or common locations
        exe_candidates = []
        if self.nt_folder_path:
            # go up from ...\bin\Custom\AddOns to ..\NinjaTrader.exe (approx)
            candidate = os.path.abspath(os.path.join(self.nt_folder_path, "..", "..", "NinjaTrader.exe"))
            exe_candidates.append(candidate)
        if sys.platform.startswith('win'):
            candidates = [
                os.path.join(os.environ.get('ProgramFiles','C:\\Program Files'), 'NinjaTrader 8', 'NinjaTrader.exe'),
                os.path.join(os.environ.get('ProgramFiles(x86)','C:\\Program Files (x86)'), 'NinjaTrader 8', 'NinjaTrader.exe'),
            ]
            exe_candidates += candidates
        for exe in exe_candidates:
            if exe and os.path.exists(exe):
                try:
                    subprocess.Popen([exe], shell=False)
                    self.log_message(f"Launched NinjaTrader: {exe}")
                    self.update_status("Launched NinjaTrader")
                    return
                except Exception as e:
                    self.log_message(f"Failed to launch {exe}: {e}")
        self.log_message("Could not find NinjaTrader executable to launch.")
        messagebox.showinfo("Not found", "NinjaTrader executable not found. Please launch manually.")

    def export_to_usb(self):
        # Let user choose destination (USB or folder). We'll copy config and bundled DLL (or selected DLL) there.
        dest = filedialog.askdirectory(title="Select USB Drive or Folder to export to")
        if not dest:
            return
        try:
            # export config
            shutil.copy2(CONFIG_PATH, os.path.join(dest, "settings.ini"))
            # determine dll to export
            dll_src = self.mtp_dll_path if self.mtp_dll_path else DLL_PATH
            if dll_src and os.path.exists(dll_src):
                shutil.copy2(dll_src, os.path.join(dest, os.path.basename(dll_src)))
            # write a small manifest/instructions
            with open(os.path.join(dest, "README_MTP_PORTABLE.txt"), 'w') as f:
                f.write("MTP Portable Export\\nReplace DLL if needed. Run the installer script on target machine.\\n")
            self.log_message(f"Exported config and DLL to: {dest}")
            messagebox.showinfo("Exported", f"Config and DLL exported to:\n{dest}")
        except Exception as e:
            self.log_message(f"Export failed: {e}")
            messagebox.showerror("Export failed", str(e))

    def save_config(self):
        self.cfg.set('MTP', 'offline_mode', str(self.offline_var.get()))
        with open(CONFIG_PATH, 'w') as f:
            self.cfg.write(f)
        self.log_message(f"Offline mode set to: {self.offline_var.get()}")
        self.update_status("Config saved")

    def log_message(self, txt):
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.insert('end', f"[{ts}] {txt}\\n")
        self.log.see('end')

    def update_status(self, text):
        self.status.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    app = MTPInstallerApp(root)
    root.mainloop()
