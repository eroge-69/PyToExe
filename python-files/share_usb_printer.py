import win32print
import win32con
import win32net
import subprocess
import time

def enable_network_discovery_and_sharing():
    """Enable network discovery and file/printer sharing on Windows."""
    try:
        # Enable Network Discovery and File/Printer Sharing using netsh
        subprocess.run('netsh advfirewall firewall set rule group="Network Discovery" new enable=Yes', shell=True, check=True)
        subprocess.run('netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=Yes', shell=True, check=True)
        print("Network discovery and file/printer sharing enabled.")
    except subprocess.CalledProcessError as e:
        print(f"Error enabling network settings: {e}")
        return False
    return True

def set_network_private():
    """Set the current network to private."""
    try:
        # Set network profile to private using PowerShell
        subprocess.run('powershell -Command "Set-NetConnectionProfile -NetworkCategory Private"', shell=True, check=True)
        print("Network set to private.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting network to private: {e}")
        return False
    return True

def share_printer(printer_name, share_name):
    """Share the specified printer on the network."""
    try:
        # Open printer handle
        printer_handle = win32print.OpenPrinter(printer_name)
        
        # Get current printer info
        printer_info = win32print.GetPrinter(printer_handle, 2)
        
        # Set sharing attributes
        printer_info['Attributes'] |= win32print.PRINTER_ATTRIBUTE_SHARED
        printer_info['ShareName'] = share_name
        
        # Update printer settings
        win32print.SetPrinter(printer_handle, 2, printer_info, 0)
        win32print.ClosePrinter(printer_handle)
        print(f"Printer '{printer_name}' shared as '{share_name}'.")
        return True
    except Exception as e:
        print(f"Error sharing printer: {e}")
        return False

def get_printer_name():
    """Get the name of the default printer."""
    try:
        printer_name = win32print.GetDefaultPrinter()
        return printer_name
    except Exception as e:
        print(f"Error getting default printer: {e}")
        return None

def main():
    # Step 1: Ensure network is set to private
    if not set_network_private():
        print("Failed to set network to private. Exiting.")
        return
    
    # Step 2: Enable network discovery and sharing
    if not enable_network_discovery_and_sharing():
        print("Failed to enable network discovery and sharing. Exiting.")
        return
    
    # Step 3: Get the default printer
    printer_name = get_printer_name()
    if not printer_name:
        print("No default printer found. Please ensure a printer is installed and set as default.")
        return
    
    # Step 4: Share the printer
    share_name = "SharedUSBPrinter"  # You can change this to any name
    if share_printer(printer_name, share_name):
        print(f"Printer successfully shared on the network. Other devices can connect using: \\\\{win32net.NetWkstaGetInfo(None, 100)['wksname']}\\{share_name}")
    else:
        print("Failed to share the printer.")

if __name__ == "__main__":
    main()