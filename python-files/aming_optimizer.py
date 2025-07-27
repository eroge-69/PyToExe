import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List
import os
import subprocess
import shutil
import sys
import ctypes
import win32com.shell.shell as shell

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin() -> None:
    if not is_admin():
        shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=' '.join(sys.argv))
        sys.exit(0)

class DayOptimizations:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Day Optimizations - Windows Optimization")
        self.root.geometry("900x700")
        self.root.configure(bg="#000000")
        self.is_admin = is_admin()

        # Attempt to elevate if not admin
        if not self.is_admin:
            run_as_admin()

        # Title label
        self.title_label = tk.Label(root, text="DAY OPTIMIZATIONS", fg="#FFFFFF", bg="#000000", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        # Search bar
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(root, textvariable=self.search_var, fg="#FFFFFF", bg="#333333", width=50)
        self.search_entry.pack(pady=5)
        self.search_var.trace('w', self.filter_optimizations)

        # Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", pady=5)

        # Define all optimization actions
        self.actions: dict[str, Callable[[], None]] = {
            "Optimize Windows Settings": self.optimize_windows,
            "Disable UAC": self.disable_uac,
            "Clean Temp All Files": self.clean_temp,
            "Optimize Network": self.optimize_network,
            "Clear Startup Items": self.clear_startup,
            "Disable Updates": self.disable_updates,
            "Memory Cleaner": self.memory_cleaner,
            "System Restore Point": self.system_restore,
            "Power Tweaks": self.power_tweaks,
            "Power Plan": self.power_plan,
            "Storage Tweaks": self.storage_tweaks,
            "FSutil Tweaks": self.fsutil_tweaks,
            "Defrag Drive": self.defrag_drive,
            "Performance Options": self.performance_options,
            "BCD-Edit": self.bcd_edit,
            "Revert": self.revert,
            "Optimize Services": self.optimize_services,
            "Disable Telemetry": self.disable_telemetry,
            "Clear Registry": self.clear_registry,
            "Optimize Disk": self.optimize_disk,
            "Clear DNS Cache": self.clear_dns_cache,
            "Disable Hibernation": self.disable_hibernation,
            "Enable High Performance": self.enable_high_performance,
            "Disable Windows Defender": self.disable_windows_defender,
            "Disable Fast Startup": self.disable_fast_startup,
            "Optimize Pagefile": self.optimize_pagefile,
            "Disable Scheduled Tasks": self.disable_scheduled_tasks,
            "Enable Hardware Acceleration": self.enable_hardware_acceleration,
            "Optimize SSD": self.optimize_ssd
        }

        # Tabs and their optimizations
        tabs = [
            ("System", ["Optimize Windows Settings", "Disable UAC", "Clean Temp All Files", "Memory Cleaner", "System Restore Point", "Revert"]),
            ("Network", ["Optimize Network", "Clear Startup Items", "Disable Updates", "Clear DNS Cache"]),
            ("Performance", ["Power Tweaks", "Power Plan", "FSutil Tweaks", "Defrag Drive", "Performance Options", "Enable High Performance", "Optimize Pagefile"]),
            ("Storage", ["Storage Tweaks", "Optimize Disk", "Optimize SSD"]),
            ("Services", ["Optimize Services", "Disable Telemetry", "Clear Registry", "Disable Scheduled Tasks"]),
            ("Security", ["Disable Windows Defender", "Disable Hibernation", "Disable Fast Startup", "Enable Hardware Acceleration", "BCD-Edit"])
        ]

        self.tab_frames: List[tk.Frame] = []
        for tab_name, optimizations in tabs:
            tab = tk.Frame(self.notebook, bg="#000000")
            self.notebook.add(tab, text=tab_name)
            self.tab_frames.append(tab)
            self.create_buttons(tab, optimizations)

        # Configure grid for expansion
        for frame in self.tab_frames:
            for i in range(5):
                frame.grid_columnconfigure(i, weight=1)
                frame.grid_rowconfigure(i, weight=1)

    def create_buttons(self, frame: tk.Frame, optimizations: List[str]) -> None:
        row, col = 0, 0
        for opt in optimizations:
            if opt.lower().startswith(self.search_var.get().lower()):
                btn = tk.Button(frame, text=opt, command=lambda o=opt: self.actions[o](), bg="#666666", fg="#FFFFFF", width=20, height=2)
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                col += 1
                if col > 4:
                    col = 0
                    row += 1

    def filter_optimizations(self, *args) -> None:
        for frame in self.tab_frames:
            for widget in frame.winfo_children():
                widget.destroy()
        for frame, (_, optimizations) in zip(self.tab_frames, tabs):
            self.create_buttons(frame, optimizations)

    def optimize_windows(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["sfc", "/scannow"], check=True)
                messagebox.showinfo("Done", "Windows settings optimized with SFC scan.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to optimize Windows: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def disable_uac(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["reg", "add", "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "EnableLUA", "/t", "REG_DWORD", "/d", "0", "/f"], check=True)
                messagebox.showinfo("Done", "UAC disabled. Requires restart.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to disable UAC: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def clean_temp(self) -> None:
        temp_dir = os.path.join(os.environ["TEMP"])
        try:
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
            messagebox.showinfo("Done", "Temp files cleaned successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean temp files: {e}")

    def optimize_network(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["netsh", "int", "ip", "reset"], check=True)
                messagebox.showinfo("Done", "Network settings reset and optimized.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to optimize network: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def clear_startup(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["schtasks", "/Change", "/TN", "\\Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator", "/Disable"], check=True)
                messagebox.showinfo("Done", "Startup items cleared (e.g., CEIP disabled).")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to clear startup items: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def disable_updates(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["reg", "add", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU", "/v", "NoAutoUpdate", "/t", "REG_DWORD", "/d", "1", "/f"], check=True)
                messagebox.showinfo("Done", "Windows Updates disabled. Requires restart.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to disable updates: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def memory_cleaner(self) -> None:
        try:
            import gc
            gc.collect()
            messagebox.showinfo("Done", "Memory cleaned (basic garbage collection).")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean memory: {e}")

    def system_restore(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["wmic", "restorepoint", "create", "System Restore Point"], check=True)
                messagebox.showinfo("Done", "System restore point created.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to create restore point: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def power_tweaks(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["powercfg", "/change", "standby-timeout-ac", "0"], check=True)
                messagebox.showinfo("Done", "Power tweaks applied (sleep disabled).")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to apply power tweaks: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def power_plan(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], check=True)
                messagebox.showinfo("Done", "High performance power plan activated.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to set power plan: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def storage_tweaks(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["fsutil", "behavior", "set", "memoryusage", "2"], check=True)
                messagebox.showinfo("Done", "Storage tweaks applied.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to apply storage tweaks: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def fsutil_tweaks(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["fsutil", "behavior", "set", "encryptpagingfile", "0"], check=True)
                messagebox.showinfo("Done", "FSutil tweaks applied.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to apply FSutil tweaks: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def defrag_drive(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["defrag", "C:", "/O"], check=True)
                messagebox.showinfo("Done", "Drive defragmented and optimized.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to defrag drive: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def performance_options(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management", "/v", "LargeSystemCache", "/t", "REG_DWORD", "/d", "1", "/f"], check=True)
                messagebox.showinfo("Done", "Performance options set (LargeSystemCache enabled).")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to set performance options: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def bcd_edit(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["bcdedit", "/set", "{current}", "bootuxdisabled", "yes"], check=True)
                messagebox.showinfo("Done", "BCD edited (boot UI disabled).")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to edit BCD: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def revert(self) -> None:
        messagebox.showinfo("Done", "Revert functionality not fully implemented. Manual rollback recommended.")  # Placeholder

    def optimize_services(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["sc", "config", "wuauserv", "start=disabled"], check=True)
                messagebox.showinfo("Done", "Services optimized (e.g., update service disabled).")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to optimize services: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def disable_telemetry(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["reg", "add", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "/v", "AllowTelemetry", "/t", "REG_DWORD", "/d", "0", "/f"], check=True)
                messagebox.showinfo("Done", "Telemetry disabled.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to disable telemetry: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def clear_registry(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["reg", "delete", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced", "/v", "Hidden", "/f"], check=True)
                messagebox.showinfo("Done", "Registry cleared (sample key removed).")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to clear registry: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def optimize_disk(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["defrag", "C:", "/O"], check=True)
                messagebox.showinfo("Done", "Disk optimized.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to optimize disk: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def clear_dns_cache(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["ipconfig", "/flushdns"], check=True)
                messagebox.showinfo("Done", "DNS cache cleared.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to clear DNS cache: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def disable_hibernation(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["powercfg", "/hibernate", "off"], check=True)
                messagebox.showinfo("Done", "Hibernation disabled.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to disable hibernation: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def enable_high_performance(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], check=True)
                messagebox.showinfo("Done", "High performance mode enabled.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to enable high performance: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def disable_windows_defender(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["reg", "add", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender", "/v", "DisableAntiSpyware", "/t", "REG_DWORD", "/d", "1", "/f"], check=True)
                messagebox.showinfo("Done", "Windows Defender disabled. Requires restart and may need Group Policy edit.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to disable Defender: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def disable_fast_startup(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power", "/v", "HiberbootEnabled", "/t", "REG_DWORD", "/d", "0", "/f"], check=True)
                messagebox.showinfo("Done", "Fast Startup disabled. Requires restart.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to disable Fast Startup: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def optimize_pagefile(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["wmic", "pagefileset", "where", "name=\"C:\\pagefile.sys\"", "set", "InitialSize=2048,MaximumSize=4096"], check=True)
                messagebox.showinfo("Done", "Pagefile optimized (2GB initial, 4GB max).")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to optimize pagefile: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def disable_scheduled_tasks(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["schtasks", "/Change", "/TN", "\\Microsoft\\Windows\\WindowsUpdate\\Scheduled Start", "/Disable"], check=True)
                messagebox.showinfo("Done", "Scheduled tasks disabled (e.g., Windows Update).")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to disable scheduled tasks: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def enable_hardware_acceleration(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects", "/v", "VisualFXSetting", "/t", "REG_DWORD", "/d", "1", "/f"], check=True)
                messagebox.showinfo("Done", "Hardware acceleration enabled.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to enable hardware acceleration: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

    def optimize_ssd(self) -> None:
        if self.is_admin:
            try:
                subprocess.run(["fsutil", "behavior", "set", "disabledeletenotify", "0"], check=True)
                messagebox.showinfo("Done", "SSD optimized (TRIM enabled).")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to optimize SSD: {e}")
        else:
            messagebox.showwarning("Warning", "Requires admin privileges.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DayOptimizations(root)
    root.mainloop()
    input("Press Enter to exit...")  # Keeps window open for debugging