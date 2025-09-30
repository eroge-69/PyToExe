import os
import sys
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class USBWriteProtectGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Write Protection Manager")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Check admin privileges on startup
        if not self.is_admin():
            messagebox.showerror(
                "Administrator Required",
                "This application requires administrator privileges!\n\n"
                "Windows: Run as Administrator\n"
                "Linux/Mac: Use sudo"
            )
            self.root.destroy()
            sys.exit(1)

        self.setup_ui()
        self.refresh_drives()

    def is_admin(self):
        """Check if the script is running with administrator privileges."""
        try:
            if platform.system() == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False

    def setup_ui(self):
        """Setup the user interface."""
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="USB Write Protection Manager",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)

        # System info
        info_frame = tk.Frame(self.root, bg="#ecf0f1", height=40)
        info_frame.pack(fill=tk.X)
        info_frame.pack_propagate(False)

        system_label = tk.Label(
            info_frame,
            text=f"Operating System: {platform.system()}",
            font=("Arial", 10),
            bg="#ecf0f1"
        )
        system_label.pack(pady=10)

        # Drive list frame
        list_frame = tk.Frame(self.root, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        list_label = tk.Label(
            list_frame,
            text="Removable USB Drives:",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        list_label.pack(anchor=tk.W, pady=(0, 10))

        # Treeview for drives
        columns = ("drive", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.tree.heading("drive", text="Drive")
        self.tree.heading("status", text="Status")
        self.tree.column("drive", width=200)
        self.tree.column("status", width=400)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Button frame
        button_frame = tk.Frame(self.root, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Refresh button
        refresh_btn = tk.Button(
            button_frame,
            text="🔄 Refresh List",
            font=("Arial", 11),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.refresh_drives
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Enable protection button
        enable_btn = tk.Button(
            button_frame,
            text="🔒 Enable Write Protection",
            font=("Arial", 11),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.enable_protection
        )
        enable_btn.pack(side=tk.LEFT, padx=5)

        # Disable protection button
        disable_btn = tk.Button(
            button_frame,
            text="🔓 Disable Write Protection",
            font=("Arial", 11),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.disable_protection
        )
        disable_btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 9),
            bg="#34495e",
            fg="white",
            anchor=tk.W,
            padx=10
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def list_removable_drives(self):
        """List all removable USB drives."""
        drives = []
        system = platform.system()

        if system == "Windows":
            import string
            import ctypes

            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                if drive_type == 2:
                    drives.append(letter)
        elif system == "Linux":
            try:
                result = subprocess.run(['lsblk', '-ndo', 'NAME,RM,TYPE'],
                                      capture_output=True, text=True, check=True)
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] == '1' and parts[2] == 'disk':
                        drives.append(f"/dev/{parts[0]}")
            except:
                pass
        elif system == "Darwin":
            try:
                result = subprocess.run(['diskutil', 'list'],
                                      capture_output=True, text=True, check=True)
                for line in result.stdout.split('\n'):
                    if 'external' in line.lower():
                        parts = line.split()
                        for part in parts:
                            if part.startswith('/dev/disk'):
                                drives.append(part)
            except:
                pass

        return drives

    def refresh_drives(self):
        """Refresh the list of USB drives."""
        self.status_var.set("Scanning for USB drives...")
        self.tree.delete(*self.tree.get_children())

        drives = self.list_removable_drives()

        if not drives:
            self.tree.insert("", tk.END, values=("No USB drives found", "-"))
            self.status_var.set("No USB drives detected")
        else:
            for drive in drives:
                self.tree.insert("", tk.END, values=(drive, "Connected"))
            self.status_var.set(f"Found {len(drives)} USB drive(s)")

    def enable_protection(self):
        """Enable write protection for all USB drives."""
        system = platform.system()

        result = messagebox.askyesno(
            "Confirm Action",
            "Enable write protection for ALL USB drives?\n\n"
            "You will need to unplug and replug the drives for changes to take effect."
        )

        if not result:
            return

        self.status_var.set("Enabling write protection...")

        def task():
            success = False
            if system == "Windows":
                success = self.enable_write_protection_windows()
            elif system == "Linux":
                drives = self.list_removable_drives()
                success = all(self.enable_write_protection_linux(d) for d in drives)
            else:
                messagebox.showerror("Error", "Unsupported operating system")
                return

            if success:
                messagebox.showinfo(
                    "Success",
                    "Write protection enabled!\n\n"
                    "Please unplug and replug USB drives for changes to take effect."
                )
                self.status_var.set("Write protection enabled")
            else:
                messagebox.showerror("Error", "Failed to enable write protection")
                self.status_var.set("Operation failed")

        threading.Thread(target=task, daemon=True).start()

    def disable_protection(self):
        """Disable write protection for all USB drives."""
        system = platform.system()

        result = messagebox.askyesno(
            "Confirm Action",
            "Disable write protection for ALL USB drives?\n\n"
            "You will need to unplug and replug the drives for changes to take effect."
        )

        if not result:
            return

        self.status_var.set("Disabling write protection...")

        def task():
            success = False
            if system == "Windows":
                success = self.disable_write_protection_windows()
            elif system == "Linux":
                drives = self.list_removable_drives()
                success = all(self.disable_write_protection_linux(d) for d in drives)
            else:
                messagebox.showerror("Error", "Unsupported operating system")
                return

            if success:
                messagebox.showinfo(
                    "Success",
                    "Write protection disabled!\n\n"
                    "Please unplug and replug USB drives for changes to take effect."
                )
                self.status_var.set("Write protection disabled")
            else:
                messagebox.showerror("Error", "Failed to disable write protection")
                self.status_var.set("Operation failed")

        threading.Thread(target=task, daemon=True).start()

    def enable_write_protection_windows(self):
        """Enable write protection for USB drives on Windows."""
        try:
            import winreg

            key_path = r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"

            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                                   winreg.KEY_SET_VALUE)
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)

            winreg.SetValueEx(key, "WriteProtect", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def disable_write_protection_windows(self):
        """Disable write protection for USB drives on Windows."""
        try:
            import winreg

            key_path = r"SYSTEM\CurrentControlSet\Control\StorageDevicePolicies"

            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                                   winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "WriteProtect", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def enable_write_protection_linux(self, device):
        """Enable write protection for a USB drive on Linux."""
        try:
            subprocess.run(['blockdev', '--setro', device], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def disable_write_protection_linux(self, device):
        """Disable write protection for a USB drive on Linux."""
        try:
            subprocess.run(['blockdev', '--setrw', device], check=True)
            return True
        except subprocess.CalledProcessError:
            return False


def main():
    root = tk.Tk()
    app = USBWriteProtectGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()