# Measure GUI Program v3.0
# last updated : 24/03/2025
# logging work
# Generate logs as per Study Selection.
# P: Integrate the PowerShell with log files
# JSON getting saved as blank
# 3/18: Need to work on PS is processing , either display console or flag that it is processing.

import json
import tkinter as tk
from tkinter import ttk
import datetime
import subprocess
import os

# Load JSON file
json_file_path = "masterconfig.json"
ps_script_path = "PS_fibonacci.ps1"  

try:
    with open(json_file_path, "r") as file:
        json_data = json.load(file)
except Exception as e:
    print(f"Failed to load JSON file: {e}")
    json_data = {"Study": {}}
        
# Study based logging
def log_event(message):
    study = study_var.get()
    if not study:
        study = "default"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_filename = f"logs/{study}_{timestamp}.log"
    os.makedirs("logs", exist_ok=True)
    with open(log_filename, "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")
    print(f"Logged event: {message}")

def update_text():
    study = study_var.get()
    if not study or study not in json_data["Study"]:
        print(f"Invalid Study selection: {study}")
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "Invalid Selection")
        return
    
    details = json_data["Study"][study]
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, f"StudyRun: {details['StudyRun']}\n")
    text_area.insert(tk.END, f"SequenceStartDate: {details['SequenceStartDate']}\n")
    text_area.insert(tk.END, f"NewRateFiles: {details.get('NewRateFiles', 'N/A')}\n")
    text_area.insert(tk.END, f"NewPlans: {details.get('NewPlans', 'N/A')}\n")
    
    log_event(f"Study selected: {study}")

def save_json():
    study = study_var.get()
    if not study:
        print("No Study selected to save.")
        return
    
    if not study_run_var.get().strip() or not sequence_start_var.get().strip():
        save_status_label.config(text="StudyRun and SequenceStartDate cannot be blank", fg="red")
        return
    
    json_data["Study"][study] = {
        "StudyRun": study_run_var.get(),
        "SequenceStartDate": sequence_start_var.get(),
        "NewRateFiles": new_rate_files_var.get(),
        "NewPlans": new_plans_var.get()
    }
    
    try:
        with open(json_file_path, "w") as file:
            json.dump(json_data, file, indent=4)
        save_status_label.config(text="Save JSON Successfully", fg="green")
        log_event("JSON file updated successfully.")
    except Exception as e:
        save_status_label.config(text="Error saving JSON", fg="red")
        log_event(f"Error saving JSON file: {e}")

def run_powershell():
    log_event("UI: Run PowerShell button clicked.")
    try:
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script_path], 
                                capture_output=True, text=True)
        log_event(f"PowerShell Output: {result.stdout}")
        if result.stderr:
            log_event(f"PowerShell Error: {result.stderr}")
    except Exception as e:
        log_event(f"Error running PowerShell script: {e}")
    
root = tk.Tk()
root.title("Measure UIv2.0")
root.geometry("500x550")

# Select Study Label
select_study_label = tk.Label(root, text="Select Study:")
select_study_label.grid(row=0, column=0, sticky='e', padx=5, pady=5)

# Dropdown
study_var = tk.StringVar()
study_dropdown = ttk.Combobox(root, textvariable=study_var, values=list(json_data["Study"].keys()), state="readonly")
study_dropdown.grid(row=0, column=1, padx=10, pady=10)
study_dropdown.bind("<<ComboboxSelected>>", lambda e: update_text())

# Text area
text_area = tk.Text(root, width=50, height=10)
text_area.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Labels and Inputs
study_run_var = tk.StringVar()
study_run_label = tk.Label(root, text="StudyRun:")
study_run_label.grid(row=2, column=0, sticky='e', padx=5)
study_run_entry = tk.Entry(root, textvariable=study_run_var)
study_run_entry.grid(row=2, column=1)

sequence_start_var = tk.StringVar()
sequence_start_label = tk.Label(root, text="SequenceStartDate:")
sequence_start_label.grid(row=3, column=0, sticky='e', padx=5)
sequence_start_entry = tk.Entry(root, textvariable=sequence_start_var)
sequence_start_entry.grid(row=3, column=1)

new_rate_files_var = tk.StringVar()
new_rate_files_label = tk.Label(root, text="New Rate Files:")
new_rate_files_label.grid(row=4, column=0, sticky='e', padx=5)
new_rate_files_combobox = ttk.Combobox(root, textvariable=new_rate_files_var, values=["True", "False"], state="readonly")
new_rate_files_combobox.grid(row=4, column=1)

new_plans_var = tk.StringVar()
new_plans_label = tk.Label(root, text="New Plans:")
new_plans_label.grid(row=5, column=0, sticky='e', padx=5)
new_plans_combobox = ttk.Combobox(root, textvariable=new_plans_var, values=["True", "False"], state="readonly")
new_plans_combobox.grid(row=5, column=1)

# Buttons
save_button = tk.Button(root, text="Save JSON", command=save_json)
save_button.grid(row=6, column=0, columnspan=2, pady=10)

# Save Status Label
save_status_label = tk.Label(root, text="", fg="black")
save_status_label.grid(row=7, column=0, columnspan=2)

run_ps_button = tk.Button(root, text="Run PowerShell Script", command=run_powershell)
run_ps_button.grid(row=8, column=0, columnspan=2, pady=10)

root.mainloop()
