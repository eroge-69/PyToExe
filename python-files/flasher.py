import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial.tools.list_ports
import threading
import esptool
import os
import time

BIN_DIR = 'bin'  # Directory where the binary files are located

class ESPFlasherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 Multi-Device Flasher")
        self.root.geometry("750x600")

        self.device_widgets = {}  # Store widgets for each device

        self.create_widgets()
        self.refresh_bins()

        threading.Thread(target=self.dynamic_port_update, daemon=True).start()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Ports list
        ports_frame = ttk.LabelFrame(main_frame, text="Detected ESP32 Devices (Select to Flash)", padding="10")
        ports_frame.pack(fill=tk.BOTH, pady=10, expand=True)

        self.ports_listbox = tk.Listbox(ports_frame, height=5, selectmode=tk.MULTIPLE)
        self.ports_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Binary selection
        file_frame = ttk.LabelFrame(main_frame, text="Select Binary Files", padding="10")
        file_frame.pack(fill=tk.BOTH, pady=10)

        self.create_file_selection(file_frame, "Main Binary File:", "bin_combo", "Browse Main Binary")
        self.create_file_selection(file_frame, "Bootloader File:", "bootloader_combo", "Browse Bootloader")
        self.create_file_selection(file_frame, "Partition File:", "partition_combo", "Browse Partition")

        # Action buttons
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=10)

        self.flash_button = ttk.Button(action_frame, text="Flash Selected ESP32 Devices", command=self.flash_selected_devices)
        self.flash_button.pack(side=tk.LEFT, expand=True, padx=5)

        # Status area
        status_frame = ttk.LabelFrame(main_frame, text="Flashing Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.status_container = ttk.Frame(status_frame)
        self.status_container.pack(fill=tk.BOTH, expand=True)

        # Scrollable status area
        self.canvas = tk.Canvas(self.status_container)
        self.scrollbar = ttk.Scrollbar(self.status_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def create_file_selection(self, parent_frame, label_text, attr_name, button_text):
        row = ttk.Frame(parent_frame)
        row.pack(fill=tk.X, pady=5)

        label = ttk.Label(row, text=label_text)
        label.pack(side=tk.LEFT, padx=5)

        combobox = ttk.Combobox(row, values=[], state="readonly", width=30)
        combobox.pack(side=tk.LEFT, expand=True)

        browse_button = ttk.Button(row, text=button_text, command=lambda: self.browse_file(attr_name))
        browse_button.pack(side=tk.RIGHT, padx=5)

        setattr(self, attr_name, combobox)

    def browse_file(self, target_combo_attr):
        file_path = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin")])
        if file_path:
            combo = getattr(self, target_combo_attr)
            combo['values'] = [file_path]
            combo.set(file_path)

    def refresh_bins(self):
        if not os.path.exists(BIN_DIR):
            os.makedirs(BIN_DIR)
        files = os.listdir(BIN_DIR)

        self.set_combo_values(self.bin_combo, [os.path.join(BIN_DIR, f) for f in files if f.endswith('.bin') and 'bootloader' not in f.lower() and 'partition' not in f.lower()])
        self.set_combo_values(self.bootloader_combo, [os.path.join(BIN_DIR, f) for f in files if 'bootloader' in f.lower() and f.endswith('.bin')])
        self.set_combo_values(self.partition_combo, [os.path.join(BIN_DIR, f) for f in files if 'partition' in f.lower() and f.endswith('.bin')])

    def set_combo_values(self, combo, values):
        current_selection = combo.get()
        combo['values'] = values
        if current_selection in values:
            combo.set(current_selection)
        elif values:
            combo.current(0)
        else:
            combo.set('')

    def dynamic_port_update(self):
        previous_ports = []
        while True:
            ports = serial.tools.list_ports.comports()
            port_list = [f"{p.device} - {p.description}" for p in ports]
            if port_list != previous_ports:
                self.root.after(0, lambda: self.update_ports_list(port_list))
                previous_ports = port_list
            time.sleep(1)

    def update_ports_list(self, port_list):
        self.ports_listbox.delete(0, tk.END)
        for port in port_list:
            self.ports_listbox.insert(tk.END, port)

    def flash_selected_devices(self):
        selected_bin = self.bin_combo.get()
        selected_bootloader_bin = self.bootloader_combo.get()
        selected_partition_bin = self.partition_combo.get()

        if not all([selected_bin, selected_bootloader_bin, selected_partition_bin]):
            messagebox.showerror("Error", "All binary files must be selected.")
            return

        selection = self.ports_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No devices selected.")
            return

        ports = [self.ports_listbox.get(i).split(" - ")[0] for i in selection]

        self.flash_button.config(state=tk.DISABLED)
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.device_widgets.clear()

        for port in ports:
            frame = ttk.Frame(self.scrollable_frame, padding=5)
            frame.pack(fill=tk.X, pady=2)

            label = ttk.Label(frame, text=f"{port} - Waiting...")
            label.pack(side=tk.LEFT, padx=5)

            progress = ttk.Progressbar(frame, mode="indeterminate", length=200)
            progress.pack(side=tk.RIGHT, padx=5)

            self.device_widgets[port] = {"label": label, "progress": progress}

            threading.Thread(
                target=self.run_esptool,
                args=(port, selected_bin, selected_bootloader_bin, selected_partition_bin),
                daemon=True
            ).start()

    def run_esptool(self, port, app_bin_file, bootloader_file, partitions_file):
        try:
            self.update_device_status(port, "Flashing...", start_progress=True)
            time.sleep(1)

            esptool_args = [
                '--chip', 'esp32',
                '--port', port,
                '--baud', '460800',
                '--before', 'default_reset',
                '--after', 'hard_reset',
                'write_flash', '-z',
                '0x1000', os.path.abspath(bootloader_file),
                '0x8000', os.path.abspath(partitions_file),
                '0x10000', os.path.abspath(app_bin_file)
            ]

            esptool.main(esptool_args)
            self.update_device_status(port, "✅ Flash completed successfully!", stop_progress=True)

        except Exception as e:
            self.update_device_status(port, f"❌ Error: {str(e)}", stop_progress=True)

        finally:
            if all(not p["progress"]["mode"] == "indeterminate" for p in self.device_widgets.values()):
                self.flash_button.config(state=tk.NORMAL)

    def update_device_status(self, port, message, start_progress=False, stop_progress=False):
        if port in self.device_widgets:
            self.device_widgets[port]["label"].config(text=f"{port} - {message}")
            if start_progress:
                self.device_widgets[port]["progress"].start()
            if stop_progress:
                self.device_widgets[port]["progress"].stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ESPFlasherApp(root)
    root.mainloop()
