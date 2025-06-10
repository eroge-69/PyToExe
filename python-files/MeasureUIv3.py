#!/usr/bin/env python
# coding: utf-8

# In[14]:


# Measure GUI Program v3.0
# last updated : 8/apr/2025
# logging work
# Generate logs as per Study Selection.
# P: Integrate the PowerShell with log files
# 3/18: Need to work on PS is processing , either display console or flag that it is processing.
# need to add text area + os code
 
import json
import tkinter as tk
from tkinter import ttk
import datetime
import subprocess
import os
from pathlib import Path
import re
 
# Set all paths:
json_file_path = Path("D:\\Measure Team - PS Scripts\\Measure-Automation\\measure_gui\\CFG\\masterconfig.json")
AH_script = Path("D:\\Measure Team - PS Scripts\\Measure-Automation\\measure_gui\\Study\\AH\\AH_script.ps1")  
ULH_script = Path("D:\\Measure Team - PS Scripts\\Measure-Automation\\measure_gui\\Study\\ULH\\ULH_script.ps1")  
log_dir = Path("D:\\Measure Team - PS Scripts\\Measure-Automation\\measure_gui\\logs")
 
# Loading JSON file
try:
    with open(json_file_path, "r") as file:
        json_data = json.load(file)
except Exception as e:
    print(f"Failed to load JSON file: {e}")
    json_data = {"Study": {}}
 
# Logging messages based on selected study:
def log_event(message):
    study = study_var.get() or "default"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_filename = log_dir / f"{study}_{timestamp}.log"
    log_dir.mkdir(exist_ok=True)
    with open(log_filename, "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")
    print(f"Logged event: {message}")
 
# Validate & parsing date format into MMDDYYYY format and actual date - mainly for SeqStartdate
def validate_date(date_str):
    if not re.match(r'^\d{8}$', date_str):  
        return False
    try:
        month = int(date_str[0:2])
        day = int(date_str[2:4])
        year = int(date_str[4:8])
        datetime.datetime(year, month, day)
        return True
    except ValueError:
        return False
 
# Update TextArea
def update_text():
    study = study_var.get()
    if not study or study not in json_data["Study"]:
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
    update_lbl_ps_path()
 
def save_json():
    study = study_var.get()
    if not study:
        lbl_save_status.config(text="No Study selected", fg="red")
        return
    study_run = study_run_var.get().strip()
    sequence_start = sequence_start_var.get().strip()
    if not study_run or not sequence_start:
        lbl_save_status.config(text="StudyRun and SequenceStartDate cannot be blank", fg="red")
        return
    if not validate_date(sequence_start):
        lbl_save_status.config(text="Invalid date format (use MMDDYYYY)", fg="red")
        return
    json_data["Study"][study] = {
        "StudyRun": study_run,
        "SequenceStartDate": sequence_start,
        "NewRateFiles": new_rate_files_var.get(),
        "NewPlans": new_plans_var.get()
    }
    try:
        with open(json_file_path, "w") as file:
            json.dump(json_data, file, indent=4)
        lbl_save_status.config(text="Saved JSON Successfully", fg="green")
        log_event("JSON file updated successfully.")
    except Exception as e:
        lbl_save_status.config(text=f"Error saving JSON: {e}", fg="red")
        log_event(f"Error saving JSON file: {e}")
 
def get_ps_script_path():
    study = study_var.get()
    if study == "AH":
        return AH_script
    elif study == "ULH":
        return ULH_script
    return AH_script
 
def update_lbl_ps_path():
    ps_path = get_ps_script_path()
    lbl_ps_path.config(text=f"PS script: {ps_path}")
 
def run_powershell():
    log_event("UI: Run PowerShell button clicked.")
    ps_script_path = get_ps_script_path()
    ps_console_area.delete(1.0, tk.END)
    ps_console_area.insert(tk.END, f"Starting PowerShell script: {ps_script_path}\n")
    if not ps_script_path.exists():
        log_event(f"PowerShell script not found at: {ps_script_path}")
        lbl_save_status.config(text=f"Script not found: {ps_script_path}", fg="red")
        ps_console_area.insert(tk.END, f"Error: Script not found at {ps_script_path}\n")
        return
    try:
        ps_console_area.insert(tk.END, "Executing...\n")
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script_path)], 
                              capture_output=True, text=True)
        ps_console_area.insert(tk.END, f"Output:\n{result.stdout}\n")
        log_event(f"PowerShell Output: {result.stdout}")
        if result.stderr:
            ps_console_area.insert(tk.END, f"Errors:\n{result.stderr}\n")
            log_event(f"PowerShell Error: {result.stderr}")
            lbl_save_status.config(text="PowerShell executed with errors", fg="orange")
        else:
            ps_console_area.insert(tk.END, "Execution completed successfully\n")
            lbl_save_status.config(text="PowerShell executed successfully", fg="green")
    except Exception as e:
        ps_console_area.insert(tk.END, f"Exception occurred: {str(e)}\n")
        log_event(f"Error running PowerShell script: {e}")
        lbl_save_status.config(text=f"Error running script: {e}", fg="red")
 
# GUI Setup
root = tk.Tk()
root.title("Measure UIv2.0")
root.geometry("580x550")
 
# Header 
header_lbl = tk.Label(root, text="Experience Study Processing", font=("Tahoma", 12, "bold"))
header_lbl.grid(row=0, column=0, columnspan=2, pady=5, sticky='w', padx=5)
 
# Select Study Label and Dropdown
lbl_select_study = tk.Label(root, text="Select Study:")
lbl_select_study.grid(row=1, column=0, sticky='e', padx=5, pady=5)
study_var = tk.StringVar()
study_dropdown = ttk.Combobox(root, textvariable=study_var, values=list(json_data["Study"].keys()), state="readonly")
study_dropdown.grid(row=1, column=1, padx=(5, 10), pady=5)
study_dropdown.bind("<<ComboboxSelected>>", lambda e: update_text())
 
# # lbl for
# json_output_lbl = tk.Label(root, text="Output from Json file")
# json_output_lbl.grid(row=2, column=0, columnspan=2, pady=(10, 0))
 
# Study Details Text area - centered
text_area = tk.Text(root, width=50, height=5)
text_area.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
 
# Input Fields
study_run_var = tk.StringVar()
lbl_study_run = tk.Label(root, text="StudyRun:")
lbl_study_run.grid(row=3, column=0, sticky='e', padx=5)
study_run_entry = tk.Entry(root, textvariable=study_run_var, width=23,validate="key", 
                           validatecommand=(root.register(lambda P: bool(re.match(r'^[a-zA-Z0-9]{0,6}$', P))), '%P'))
study_run_entry.grid(row=3, column=1)
 
##SequenceStart_date: 
sequence_start_var = tk.StringVar()
lbl_seq_start = tk.Label(root, text="SequenceStartDate:")
lbl_seq_start.grid(row=4, column=0, sticky='e', padx=5)
sequence_start_entry = tk.Entry(root, textvariable=sequence_start_var, width=23, validate="key",
                                validatecommand=(root.register(lambda P: bool(re.match(r'^\d{0,8}$', P))), '%P'))
sequence_start_entry.grid(row=4, column=1)
 
##New_rate_files: 
new_rate_files_var = tk.StringVar(value="False")
lbl_newrfiles = tk.Label(root, text="New Rate Files:")
lbl_newrfiles.grid(row=5, column=0, sticky='e', padx=5)
new_rate_files_combobox = ttk.Combobox(root, textvariable=new_rate_files_var, values=["True", "False"], state="readonly")
new_rate_files_combobox.grid(row=5, column=1)
 
##New_plans:
new_plans_var = tk.StringVar(value="False")
lbl_new_plans = tk.Label(root, text="New Plans:")
lbl_new_plans.grid(row=6, column=0, sticky='e', padx=5)
new_plans_combobox = ttk.Combobox(root, textvariable=new_plans_var, values=["True", "False"], state="readonly")
new_plans_combobox.grid(row=6, column=1)
 
## Button 
save_button = tk.Button(root, text="Save JSON",width=20, command=save_json)
save_button.grid(row=7, column=0, columnspan=2, pady=10)
 
lbl_save_status = tk.Label(root, text="", fg="black")
lbl_save_status.grid(row=8, column=0, columnspan=2)
 
run_ps_button = tk.Button(root, text="Run PowerShell Script",width=20, command=run_powershell)
run_ps_button.grid(row=9, column=0, columnspan=2, pady=10)
 
# PowerShell Console 
ps_console_area = tk.Text(root, width=60, height=6)
ps_console_area.grid(row=10, column=0, columnspan=2, padx=10, pady=10)
 
lbl_ps_path = tk.Label(root, text=f"PS Script:   {AH_script}")
lbl_ps_path.grid(row=11, column=0, columnspan=2, pady=5)
 
root.mainloop()


# In[ ]:





# In[ ]:




