import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import platform

# ---
# 1. Define your printers and their corresponding drivers
# ---
# A list of dictionaries. Each dictionary contains:
# - name: A descriptive name for the printer.
# - ip: The IP address of the printer.
# - driver_name: The exact name of the printer driver as it appears on your system.
#                You will need to find the correct name for your specific drivers.
#                (e.g., "HP Universal Printing PCL 6", "Generic / Text Only").
#                You can find this by checking your system's printer properties.
PRINTERS = [
    {"DROPPRO01": "Office Printer", "IP": "10.73.65.135", "Xerox": "Xerox Universal Printing PCL 6"},
    {"DROPPRO08": "Shop Floor Printer Post M-16", "IP": "10.73.65.142", "Xerox": "Xerox Universal Printing PCL6"},
    {"DROPPRO10": "Shop Floor Printer Post Q-16", "IP": "10.73.65.144", "Xerox": "Xerox Universal Printing PCL6"},
    {"DROPPRO11": "Shop Floor Printer Post U-16", "IP": "10.73.65.145", "Xerox": "Xerox Universal Printing PCL6"},
    {"DROPPRO12": "Shop Floor Printer Post Y-16", "IP": "10.73.65.146", "Xerox": "Xerox Universal Printing PCL6"},
    {"DROPPRO13": "Shop Floor Printer Post AD", "IP": "10.73.65.147", "Xerox": "Xerox Universal Printing PCL6"},
]

# A list of available printer drivers to populate the dropdown menu.
# This should match the driver names in the PRINTERS list.
DRIVER_LIST = sorted(list(set(p['driver_name'] for p in PRINTERS)))

# ---
# 2. Function to add a printer (OS-specific)
# ---
def add_printer_to_system(printer_name, printer_ip, driver_name, username=None, password=None):
    """
    Connects a network printer using a system-level command.
    This is highly dependent on your operating system.
    """
    # Windows Example (PowerShell command)
    if platform.system() == "Windows":
        try:
            # We first need to check if the driver is already installed.
            # You would need a more robust check in a production environment.
            
            # The command adds a TCP/IP port, then a printer using that port and driver.
            # A more secure way to handle credentials would be to use a dedicated
            # management library or run a pre-configured script.
            command = [
                "powershell.exe",
                "Add-PrinterPort -Name \"{} - Port\" -PrinterHostAddress \"{}\" -ErrorAction SilentlyContinue;".format(printer_ip, printer_ip) +
                "Add-Printer -Name \"{}\" -PortName \"{} - Port\" -DriverName \"{}\"".format(printer_name, printer_ip, driver_name)
            ]
            
            # This is a very simple and potentially insecure way to pass credentials.
            # In a real-world scenario, you would need a more secure method.
            # For Windows, running the script with `runas /user:Administrator ...` is a common approach.
            if username and password:
                messagebox.showwarning("Insecure Credentials", "Passing passwords directly is not secure. This is a demonstration. The script assumes it's run with administrative privileges.")
            
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to add printer '{printer_name}' at {printer_ip}.\nError: {e}")
            return False

    # macOS Example (lpadmin command)
    elif platform.system() == "Darwin":
        try:
            # The `lpadmin` command needs a PPD file for the driver.
            # The example below uses a generic driver, which may or may not work.
            # You would need to locate or provide the specific PPD file for your printer.
            # The `-P` flag points to the PPD file.
            # macOS also uses a security framework for handling passwords for admin tasks.
            
            # This is a placeholder command and needs a valid PPD file path.
            # e.g., `-P "/Library/Printers/PPDs/Contents/Resources/EN.lproj/Generic.ppd"`
            # Replace `Generic.ppd` with your specific driver's PPD file name.
            ppd_path = "/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/PrintCore.framework/Versions/A/Resources/Generic.ppd"
            
            command = [
                "lpadmin", "-p", f"Network_Printer_{printer_ip.replace('.', '_')}", "-E", "-v", f"socket://{printer_ip}",
                "-P", ppd_path
            ]
            
            if username and password:
                 # In macOS, `sudo` would be used, but it's not a secure way to pass passwords
                 # in a script. A user-friendly GUI would use a separate prompt.
                print("Warning: Passing password directly is insecure.")
                command.insert(0, "sudo")
            
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to add printer '{printer_name}' at {printer_ip}.\nError: {e}")
            return False

    else:
        messagebox.showwarning("Warning", "Your OS is not supported by this script.")
        return False

# ---
# 3. Main GUI application class
# ---
class PrinterInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Printer Installer")
        self.root.geometry("600x500")

        self.printer_vars = {}
        self.create_widgets()

    def create_widgets(self):
        # --- Printer Selection Section ---
        printer_select_frame = ttk.LabelFrame(self.root, text="Select Printers to Install")
        printer_select_frame.pack(padx=20, pady=10, fill="both", expand=True)

        for printer in PRINTERS:
            var = tk.IntVar()
            self.printer_vars[printer["ip"]] = var
            checkbox = ttk.Checkbutton(
                printer_select_frame,
                text=f"{printer['name']} ({printer['ip']})",
                variable=var
            )
            checkbox.pack(anchor="w", pady=2, padx=10)
        
        # --- Driver Selection Section ---
        driver_frame = ttk.LabelFrame(self.root, text="Select Driver (Optional, falls back to default from printer list)")
        driver_frame.pack(padx=20, pady=10, fill="x")
        
        driver_label = ttk.Label(driver_frame, text="Printer Driver:")
        driver_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.driver_combobox = ttk.Combobox(driver_frame, values=DRIVER_LIST)
        self.driver_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.driver_combobox.set("Select a driver...")
        
        driver_frame.columnconfigure(1, weight=1)

        # --- Credential Section ---
        credentials_frame = ttk.LabelFrame(self.root, text="Administrator Credentials (if needed)")
        credentials_frame.pack(padx=20, pady=10, fill="x")

        username_label = ttk.Label(credentials_frame, text="Username:")
        username_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.username_entry = ttk.Entry(credentials_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        password_label = ttk.Label(credentials_frame, text="Password:")
        password_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.password_entry = ttk.Entry(credentials_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        credentials_frame.columnconfigure(1, weight=1)

        # Button to trigger the installation
        install_button = ttk.Button(self.root, text="Connect Selected Printers", command=self.install_printers)
        install_button.pack(pady=20)

    def install_printers(self):
        selected_printers = [p for p in PRINTERS if self.printer_vars[p['ip']].get() == 1]
        
        if not selected_printers:
            messagebox.showwarning("No Selection", "Please select at least one printer to connect.")
            return

        username = self.username_entry.get()
        password = self.password_entry.get()
        selected_driver = self.driver_combobox.get()
        
        success_count = 0
        for printer in selected_printers:
            # Use the selected driver from the dropdown if a valid one is chosen.
            # Otherwise, use the driver specified in the PRINTERS list.
            driver_to_use = selected_driver if selected_driver in DRIVER_LIST else printer['driver_name']

            if add_printer_to_system(printer['name'], printer['ip'], driver_to_use, username, password):
                success_count += 1

        if success_count > 0:
            messagebox.showinfo(
                "Installation Complete",
                f"Successfully connected {success_count} out of {len(selected_printers)} printers."
            )
        else:
            messagebox.showerror(
                "Installation Failed",
                "No printers were connected. Check the errors for details."
            )

# ---
# 4. Run the application
# ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PrinterInstallerApp(root)
    root.mainloop()