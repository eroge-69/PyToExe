import tkinter as tk
from tkinter import messagebox
import random
import string
import uuid
import subprocess

# Function to generate a random seed
def generate_seed():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Function to spoof system identifiers
def spoof_identifiers(seed):
    random.seed(seed)
    spoofed_data = {
        'UUID': str(uuid.uuid4()),
        'SERIAL': ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)),
        'DISK0': ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)),
        'DISK1': ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)),
        'DISK2': ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)),
        'MAC0': ''.join(random.choices(string.hexdigits, k=12)),
        'MAC1': ''.join(random.choices(string.hexdigits, k=12))
    }
    return spoofed_data

# Function to update the GUI with spoofed data
def update_gui(seed):
    spoofed_data = spoof_identifiers(seed)
    for key, value in spoofed_data.items():
        labels[key].config(text=f'{key}: {value}')
        # Persist the changes temporarily
        persist_spoof(key, value)

# Function to persist spoofed data temporarily
def persist_spoof(identifier, value):
    try:
        if identifier == 'UUID':
            subprocess.run(['powershell', '-Command', f'Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Cryptography" -Name "MachineGuid" -Value "{value}" -Force'], check=True)
        elif identifier.startswith('DISK'):
            disk_number = identifier[-1]
            subprocess.run(['powershell', '-Command', f'Set-ItemProperty -Path "HKLM:\SYSTEM\MountedDevices" -Name "\\DosDevices\\{disk_number}:" -Value "{value}" -Force'], check=True)
        elif identifier.startswith('MAC'):
            mac_number = identifier[-1]
            subprocess.run(['powershell', '-Command', f'Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}" -Name "NetworkAddress" -Value "{value}" -Force'], check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to spoof {identifier}: {e}")

# Function to handle the randomize seed button click
def randomize_seed():
    new_seed = generate_seed()
    seed_entry.delete(0, tk.END)
    seed_entry.insert(0, new_seed)
    update_gui(new_seed)

# Function to handle the spoof button click
def spoof_button_click():
    seed = seed_entry.get()
    if not seed:
        messagebox.showerror("Error", "Please enter a seed.")
        return
    update_gui(seed)

# Create the main window
root = tk.Tk()
root.title("Fort Spoofer")
root.configure(bg='sky blue')

# Create and place widgets
seed_label = tk.Label(root, text="Seed:", bg='sky blue', fg='black')
seed_label.pack(pady=5)

seed_entry = tk.Entry(root, width=20)
seed_entry.pack(pady=5)

randomize_button = tk.Button(root, text="Randomize Seed", command=randomize_seed)
randomize_button.pack(pady=5)

spoof_button = tk.Button(root, text="Spoof", command=spoof_button_click)
spoof_button.pack(pady=20)

# Dictionary to hold labels for spoofed data
labels = {}
for identifier in ['UUID', 'SERIAL', 'DISK0', 'DISK1', 'DISK2', 'MAC0', 'MAC1']:
    label = tk.Label(root, text=f'{identifier}: ', bg='sky blue', fg='black')
    label.pack(pady=2)
    labels[identifier] = label

# Run the application
root.mainloop()