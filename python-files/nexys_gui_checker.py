import tkinter as tk
from tkinter import ttk
import subprocess
import threading

# Function to run system commands and return cleaned output
def run_command(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, encoding='utf-8', stderr=subprocess.DEVNULL)
        lines = result.strip().split('\n')
        # Skip header line
        if len(lines) > 1:
            return '\n'.join(line.strip() for line in lines[1:] if line.strip())
        return result.strip()
    except Exception as e:
        return f"Error: {e}"

# Function to get all serials
def get_serials():
    serial_data = {
        "Disk Drive": run_command("wmic diskdrive get model, serialnumber"),
        "CPU": run_command("wmic cpu get serialnumber"),
        "BIOS": run_command("wmic bios get serialnumber"),
        "Motherboard": run_command("wmic baseboard get serialnumber"),
        "smBIOS UUID": run_command("wmic path win32_computersystemproduct get uuid"),
        "MAC Address": run_command("getmac"),
    }
    return serial_data

# GUI Setup
def build_gui():
    root = tk.Tk()
    root.title("Nexys v1 Serial Checker")
    root.configure(bg="#121212")
    root.geometry("600x500")
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#121212", foreground="#ffffff", font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#00FFC6")
    style.configure("TButton", background="#1F1F1F", foreground="#ffffff", borderwidth=0)
    style.map("TButton", background=[("active", "#333333")])

    header = ttk.Label(root, text="Nexys v1 Serial Checker", style="Header.TLabel")
    header.pack(pady=15)

    output_text = tk.Text(root, wrap="word", bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff",
                          font=("Consolas", 10), borderwidth=0, relief="flat")
    output_text.pack(padx=20, pady=10, fill="both", expand=True)

    def display_serials():
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, "Loading...\n")

        def fetch_and_display():
            serials = get_serials()
            output_text.delete(1.0, tk.END)
            for key, value in serials.items():
                output_text.insert(tk.END, f"{key}:\n{value}\n\n")

        threading.Thread(target=fetch_and_display, daemon=True).start()

    refresh_btn = ttk.Button(root, text="Refresh", command=display_serials)
    refresh_btn.pack(pady=10)

    # Start by loading serials
    display_serials()

    root.mainloop()

build_gui()
