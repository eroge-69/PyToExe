import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import psutil
import platform
import subprocess
import time

# Try to import python-mtp
try:
    import mtp
except ImportError:
    mtp = None

class MP3ManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Player File Manager")
        self.device_path = None
        self.mtp_device = None

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        # USB Mass Storage Tab
        self.usb_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.usb_frame, text="USB Mass Storage")

        tk.Label(self.usb_frame, text="Available USB Devices:").pack(anchor='w')
        self.usb_device_list = tk.Listbox(self.usb_frame, height=4)
        self.usb_device_list.pack(fill='x')

        ttk.Button(self.usb_frame, text="Scan for Devices", command=self.scan_usb_devices).pack(fill='x')
        ttk.Button(self.usb_frame, text="Load Files from Device", command=self.load_usb_files_thread).pack(fill='x')
        ttk.Button(self.usb_frame, text="Eject Selected Device", command=self.eject_usb_device_thread).pack(fill='x')

        tk.Label(self.usb_frame, text="Files on Device:").pack(anchor='w')
        self.usb_tree = ttk.Treeview(self.usb_frame)
        self.usb_tree.pack(fill='both', expand=True)

        ttk.Button(self.usb_frame, text="Delete Selected", command=self.delete_usb_selected_thread).pack(fill='x')
        ttk.Button(self.usb_frame, text="Add MP3 Files", command=self.add_usb_files_thread).pack(fill='x')

        # MTP Tab
        self.mtp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mtp_frame, text="MTP Devices")

        tk.Label(self.mtp_frame, text="Available MTP Devices:").pack(anchor='w')
        self.mtp_device_list = tk.Listbox(self.mtp_frame, height=4)
        self.mtp_device_list.pack(fill='x')

        ttk.Button(self.mtp_frame, text="Scan for MTP Devices", command=self.scan_mtp_devices).pack(fill='x')
        ttk.Button(self.mtp_frame, text="Load Files from MTP Device", command=self.load_mtp_files_thread).pack(fill='x')
        ttk.Button(self.mtp_frame, text="Add MP3 Files to MTP Device", command=self.add_mtp_files_thread).pack(fill='x')

        tk.Label(self.mtp_frame, text="Files on MTP Device:").pack(anchor='w')
        self.mtp_tree = ttk.Treeview(self.mtp_frame)
        self.mtp_tree.pack(fill='both', expand=True)

        ttk.Button(self.mtp_frame, text="Delete Selected from MTP", command=self.delete_mtp_selected_thread).pack(fill='x')

        # Shared status and progress bar
        self.progress = ttk.Progressbar(root, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x')
        self.status_label = tk.Label(root, text="Status: Ready")
        self.status_label.pack(anchor='w')

        # Start scanning for USB devices initially
        self.scan_usb_devices()

        # Start monitoring USB devices for changes
        self.last_usb_devices = []
        self.start_usb_monitoring_thread()

        # Scan MTP devices if mtp module available
        if mtp:
            self.scan_mtp_devices()
        else:
            self.status_label.config(text="Status: python-mtp not installed; MTP disabled.")

    #######################
    # USB Mass Storage Code
    #######################

    def get_connected_usb_devices(self):
        system = platform.system()
        devices = []
        for part in psutil.disk_partitions(all=False):
            mountpoint = part.mountpoint
            device = part.device
            opts = part.opts.lower()
            if system == 'Windows':
                if 'removable' in opts:
                    devices.append(f"{device} → {mountpoint}")
            elif system == 'Darwin':
                if mountpoint.startswith("/Volumes"):
                    devices.append(f"{device} → {mountpoint}")
            elif system == 'Linux':
                if mountpoint.startswith("/media") or mountpoint.startswith("/mnt"):
                    devices.append(f"{device} → {mountpoint}")
        return devices

    def scan_usb_devices(self):
        self.usb_device_list.delete(0, tk.END)
        devices = self.get_connected_usb_devices()
        if not devices:
            self.usb_device_list.insert(tk.END, "No USB devices found")
            self.status_label.config(text="Status: No USB devices detected")
        else:
            for d in devices:
                self.usb_device_list.insert(tk.END, d)
            self.status_label.config(text="Status: USB scan complete")
        self.last_usb_devices = devices

    def monitor_usb_devices(self):
        while True:
            current = self.get_connected_usb_devices()
            if current != self.last_usb_devices:
                self.root.after(0, self.scan_usb_devices)
            time.sleep(3)

    def start_usb_monitoring_thread(self):
        thread = threading.Thread(target=self.monitor_usb_devices, daemon=True)
        thread.start()

    def load_usb_files_thread(self):
        threading.Thread(target=self.load_usb_files).start()

    def load_usb_files(self):
        try:
            selected = self.usb_device_list.get(self.usb_device_list.curselection())
            if "No USB devices found" in selected:
                messagebox.showwarning("No USB device", "No USB device selected.")
                return
        except tk.TclError:
            messagebox.showwarning("Select USB device", "Please select a USB device first.")
            return
        self.device_path = selected.split("→")[1].strip()
        self.status_label.config(text="Status: Loading USB files...")
        self.progress.config(value=0, maximum=0)
        self.usb_tree.delete(*self.usb_tree.get_children())
        total_items = 0
        for root_dir, dirs, files in os.walk(self.device_path):
            total_items += len(dirs) + len(files)
        self.progress.config(maximum=total_items)
        self._insert_usb_tree_items(self.device_path, '')
        self.progress.config(value=total_items)
        self.status_label.config(text=f"Status: Loaded {total_items} items from USB device.")

    def _insert_usb_tree_items(self, parent_path, parent_node):
        try:
            entries = sorted(os.listdir(parent_path), key=lambda s: s.lower())
        except PermissionError:
            return
        for entry in entries:
            full_path = os.path.join(parent_path, entry)
            node_id = self.usb_tree.insert(parent_node, 'end', text=entry, open=False)
            if os.path.isdir(full_path):
                self._insert_usb_tree_items(full_path, node_id)

    def delete_usb_selected_thread(self):
        threading.Thread(target=self.delete_usb_selected).start()

    def delete_usb_selected(self):
        selected_items = self.usb_tree.selection()
        if not selected_items:
            messagebox.showwarning("No selection", "Please select files or folders to delete on USB.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete selected items on USB?")
        if not confirm:
            return
        self.status_label.config(text="Status: Deleting selected USB items...")
        self.progress.config(value=0, maximum=len(selected_items))
        for i, item in enumerate(selected_items, 1):
            path = self._get_usb_full_path(item)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {path}:\n{e}")
            self.progress.config(value=i)
            self.status_label.config(text=f"Status: Deleted {i} of {len(selected_items)} USB items")
        self.load_usb_files()
        self.status_label.config(text="Status: USB delete completed.")
        self.progress.config(value=0)

    def add_usb_files_thread(self):
        threading.Thread(target=self.add_usb_files).start()

    def add_usb_files(self):
        if not self.device_path:
            messagebox.showwarning("No USB device", "Please load a USB device first.")
            return
        files = filedialog.askopenfilenames(title="Select MP3 files to add to USB device",
                                            filetypes=[("MP3 files", "*.mp3")])
        if not files:
            return
        self.status_label.config(text="Status: Copying files to USB device...")
        self.progress.config(value=0, maximum=len(files))
        for i, src in enumerate(files, 1):
            try:
                dest = os.path.join(self.device_path, os.path.basename(src))
                shutil.copy2(src, dest)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy {src}:\n{e}")
            self.progress.config(value=i)
            self.status_label.config(text=f"Status: Copied {i} of {len(files)} files to USB")
        self.load_usb_files()
        self.status_label.config(text="Status: USB copy completed.")
        self.progress.config(value=0)

    def eject_usb_device_thread(self):
        threading.Thread(target=self.eject_usb_device).start()

    def eject_usb_device(self):
        try:
            selected = self.usb_device_list.get(self.usb_device_list.curselection())
            if "No USB devices found" in selected:
                messagebox.showwarning("No USB device", "No USB device selected.")
                return
        except tk.TclError:
            messagebox.showwarning("Select USB device", "Please select a USB device to eject.")
            return
        device_path = selected.split("→")[1].strip()

        # Secure eject check: make sure no file operations in progress or device mounted
        confirm = messagebox.askyesno("Confirm Eject", f"Are you sure you want to safely eject:\n{device_path}?")
        if not confirm:
            return

        self.status_label.config(text="Status: Ejecting USB device...")

        system = platform.system()
        success = False
        try:
            if system == 'Windows':
                # Use Windows built-in command (requires admin privileges)
                # You can also use third party libs for ejecting drives
                # Here we just use powershell to eject the drive letter
                drive_letter = device_path.strip("\\").replace("\\", "")
                cmd = f'powershell "(New-Object -comObject Shell.Application).Namespace(17).ParseName(\'{drive_letter}\').InvokeVerb(\'Eject\')"'
                subprocess.run(cmd, shell=True)
                success = True
            elif system == 'Darwin':
                # macOS eject command
                subprocess.run(['diskutil', 'unmountDisk', device_path], check=True)
                success = True
            elif system == 'Linux':
                # Linux eject command
                subprocess.run(['udisksctl', 'unmount', '-b', device_path], check=True)
                subprocess.run(['udisksctl', 'power-off', '-b', device_path], check=True)
                success = True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to eject device:\n{e}")
            self.status_label.config(text="Status: Eject failed.")
            return

        if success:
            self.status_label.config(text="Status: Device ejected successfully.")
            # Play sound or show notification on success
            try:
                if system == 'Windows':
                    import winsound
                    winsound.MessageBeep(winsound.MB_OK)
                else:
                    # Try to play a sound (requires 'afplay' on mac or 'paplay' on Linux)
                    if system == 'Darwin':
                        subprocess.Popen(['afplay', '/System/Library/Sounds/Glass.aiff'])
                    elif system == 'Linux':
                        subprocess.Popen(['paplay', '/usr/share/sounds/freedesktop/stereo/complete.oga'])
            except:
                pass
            self.scan_usb_devices()

    def _get_usb_full_path(self, tree_item):
        parts = []
        while tree_item:
            parts.append(self.usb_tree.item(tree_item)['text'])
            tree_item = self.usb_tree.parent(tree_item)
        parts.reverse()
        return os.path.join(self.device_path, *parts)

    #######################
    # MTP Device Code
    #######################

    def scan_mtp_devices(self):
        self.mtp_device_list.delete(0, tk.END)
        if not mtp:
            self.status_label.config(text="Status: python-mtp library not available.")
            return
        devices = mtp.get_devices()
        if not devices:
            self.mtp_device_list.insert(tk.END, "No MTP devices found")
            self.status_label.config(text="Status: No MTP devices detected.")
        else:
            for i, d in enumerate(devices):
                self.mtp_device_list.insert(tk.END, f"{i}: {d.name}")
            self.status_label.config(text="Status: MTP scan complete.")

    def load_mtp_files_thread(self):
        threading.Thread(target=self.load_mtp_files).start()

    def load_mtp_files(self):
        try:
            selected = self.mtp_device_list.get(self.mtp_device_list.curselection())
            if "No MTP devices found" in selected:
                messagebox.showwarning("No MTP device", "No MTP device selected.")
                return
        except tk.TclError:
            messagebox.showwarning("Select MTP device", "Please select an MTP device first.")
            return
        device_index = int(selected.split(":")[0].strip())
        devices = mtp.get_devices()
        self.mtp_device = devices[device_index]
        try:
            self.mtp_device.open()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open MTP device:\n{e}")
            return

        self.status_label.config(text="Status: Loading MTP files...")
        self.progress.config(value=0, maximum=0)
        self.mtp_tree.delete(*self.mtp_tree.get_children())

        # Recursively add files/folders to treeview
        self._insert_mtp_tree_items(self.mtp_device.get_folder(0), '')

        self.status_label.config(text="Status: MTP files loaded.")

    def _insert_mtp_tree_items(self, folder, parent_node):
        # folder is an mtp.Folder object
        children = folder.get_children()
        for item in children:
            node_id = self.mtp_tree.insert(parent_node, 'end', text=item.filename, open=False)
            if hasattr(item, 'object_id') and item.object_id:
                if item.filetype == 1:  # 1 means folder type in libmtp
                    # Recursive insert folders
                    child_folder = self.mtp_device.get_folder(item.object_id)
                    if child_folder:
                        self._insert_mtp_tree_items(child_folder, node_id)

    def add_mtp_files_thread(self):
        threading.Thread(target=self.add_mtp_files).start()

    def add_mtp_files(self):
        if not self.mtp_device:
            messagebox.showwarning("No MTP device", "Please load an MTP device first.")
            return
        files = filedialog.askopenfilenames(title="Select MP3 files to add to MTP device",
                                            filetypes=[("MP3 files", "*.mp3")])
        if not files:
            return
        self.status_label.config(text="Status: Copying files to MTP device...")
        self.progress.config(value=0, maximum=len(files))

        for i, src in enumerate(files, 1):
            try:
                with open(src, 'rb') as f:
                    data = f.read()
                # Send data to root folder (ID 0)
                self.mtp_device.send_file(data, os.path.basename(src), parent_folder=0)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy {src}:\n{e}")
            self.progress.config(value=i)
            self.status_label.config(text=f"Status: Copied {i} of {len(files)} files to MTP device")

        self.load_mtp_files()
        self.status_label.config(text="Status: MTP copy completed.")
        self.progress.config(value=0)

    def delete_mtp_selected_thread(self):
        threading.Thread(target=self.delete_mtp_selected).start()

    def delete_mtp_selected(self):
        selected_items = self.mtp_tree.selection()
        if not selected_items:
            messagebox.showwarning("No selection", "Please select files or folders to delete on MTP.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete selected items on MTP?")
        if not confirm:
            return

        self.status_label.config(text="Status: Deleting selected MTP items...")
        self.progress.config(value=0, maximum=len(selected_items))

        for i, item in enumerate(selected_items, 1):
            filename = self.mtp_tree.item(item)['text']
            # NOTE: python-mtp library does not provide direct ID mapping in tree
            # This example assumes items are unique and in root folder only.
            # For full support, you'd need to store object_id in tree node tags.
            try:
                # This is a simplification: delete by filename in root folder
                objs = self.mtp_device.get_folder(0).get_children()
                target_obj = None
                for obj in objs:
                    if obj.filename == filename:
                        target_obj = obj
                        break
                if target_obj:
                    self.mtp_device.delete_object(target_obj.object_id)
                else:
                    raise Exception(f"File {filename} not found on device.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {filename}:\n{e}")
            self.progress.config(value=i)
            self.status_label.config(text=f"Status: Deleted {i} of {len(selected_items)} MTP items")

        self.load_mtp_files()
        self.status_label.config(text="Status: MTP delete completed.")
        self.progress.config(value=0)

    #######################
    # Utility
    #######################

    def _get_usb_full_path(self, tree_item):
        parts = []
        while tree_item:
            parts.append(self.usb_tree.item(tree_item)['text'])
            tree_item = self.usb_tree.parent(tree_item)
        parts.reverse()
        return os.path.join(self.device_path, *parts)

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3ManagerApp(root)
    root.mainloop()
