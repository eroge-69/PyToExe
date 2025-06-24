import tkinter as tk
import ctypes
import platform

# Define the SMS template and firmware update links
steps = {
    "Step 1": {
        "description": "Send SMS",
        "content": """Please be aware we are setting up your Public Wifi network today and your router may restart several times during this.

Sorry for the inconvenience.

-XLN"""
    },
    "Step 2": {
        "description": "Firmware Update to: 0.17.0 2.0.0 v606c.0 Build 250314 Rel.33162n",
        "content": "http://khulme.co.uk:2220/download/Step1_VX230vv1_0.17.0_2.0.0_UP_BOOT_TRANS(250314)_2025-03-24_14.06.31_EU.bin"
    },
    "Step 3": {
        "description": "Firmware Update to: 0.17.0 2.0.0 v606c.0 Build 250421 Rel.33750n_Beta",
        "content": "http://khulme.co.uk:2220/download/Step2_VX230vv1_0.17.0_2.0.0_UP_BOOT_BETA(250421)_1024_2025-04-25_10.24.13.bin"
    },
    "Step 4": {
        "description": "Firmware Update to: 0.17.0 2.0.0 v606c.0 Build 250611 Rel.25141n",
        "content": "http://khulme.co.uk:2220/download/VX230vv1_0.17.0_2.0.0_UP_BOOT_agc3000(250611)_2025-06-11_15.53.13.bin"
    },
    "Step 6": {
        "description": "SSID: Daisy Group Free Wifi",
        "content": "Daisy Group Free Wifi",
        "button_label": "Copy SSID"
    },
    "Final": {
        "description": "Provision Complete SMS",
        "content": "Hi, your Daisy Group Free Wifi order is now complete. If you experience any issues with it please contact us on 0808 178 5200. Regards, XLN"
    }
}

# Function to show a temporary confirmation popup
def show_temp_popup(message):
    popup = tk.Toplevel(root)
    popup.title("Copied")
    popup.geometry("300x80")
    popup.resizable(False, False)
    label = tk.Label(popup, text=message, padx=10, pady=10)
    label.pack(expand=True)
    popup.after(1000, popup.destroy)

# Function to copy content to clipboard
def copy_content(step):
    root.clipboard_clear()
    root.clipboard_append(steps[step]["content"])
    root.update()
    show_temp_popup(f"{step} content copied to clipboard!")

# Hide console window on Windows
if platform.system() == "Windows":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Create the main window
root = tk.Tk()
root.title("Provisioning Link Copier")
root.resizable(False, False)

# Add padding around the content
frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

# Create buttons and labels for each step
for step in steps:
    separator = tk.Label(frame, text="-=-=-=-", fg="gray")
    separator.pack(pady=(10, 0))

    label = tk.Label(frame, text=steps[step]["description"], font=("Arial", 10, "bold"), wraplength=500, justify="left")
    label.pack(pady=(5, 0))

    button_text = steps[step].get("button_label", f"Copy {step} Content")
    btn = tk.Button(frame, text=button_text, command=lambda s=step: copy_content(s), width=50, pady=5)
    btn.pack(pady=(0, 5))

# Final separator
separator = tk.Label(frame, text="-=-=-=-", fg="gray")
separator.pack(pady=(10, 0))

# Run the application
root.mainloop()