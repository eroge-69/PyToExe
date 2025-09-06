import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import json
import re
from threading import Thread

# ----------------------------
# Improved Mapping ESX -> QBox with Regex for safer replacements
# ----------------------------
script_mapping = {
    r'ESX\.GetPlayerFromId\s*\((.*?)\)': r"QBox.Functions.GetPlayer(\1)",
    r'ESX\.GetPlayerFromIdentifier\s*\((.*?)\)': r"QBox.Functions.GetPlayerByCitizenId(\1)",
    r'ESX\.GetPlayers\s*\(\)': r"QBox.Functions.GetPlayers()",
    r'ESX\.RegisterServerCallback\s*\((.*?),\s*(.*?)\)': r"QBox.Functions.CreateCallback(\1, \2)",
    r'ESX\.RegisterUsableItem\s*\((.*?),\s*(.*?)\)': r"QBox.Functions.CreateUseableItem(\1, \2)",
    r'xPlayer\.getMoney\s*\(\)': r"Player.Functions.GetMoney('cash')",
    r'xPlayer\.addMoney\s*\((.*?)\)': r"Player.Functions.AddMoney('cash', \1)",
    r'xPlayer\.removeMoney\s*\((.*?)\)': r"Player.Functions.RemoveMoney('cash', \1)",
    r'xPlayer\.addInventoryItem\s*\((.*?),\s*(.*?)\)': r"Player.Functions.AddItem(\1, \2)",
    r'xPlayer\.getInventoryItem\s*\((.*?)\)': r"Player.Functions.GetItemByName(\1)",
    r"xPlayer\.getAccount\s*\('bank'\)\.money": r"Player.Functions.GetMoney('bank')",
    r"xPlayer\.addAccountMoney\s*\('bank',\s*(.*?)\)": r"Player.Functions.AddMoney('bank', \1)",
    r"xPlayer\.removeAccountMoney\s*\('bank',\s*(.*?)\)": r"Player.Functions.RemoveMoney('bank', \1)",
    r"TriggerEvent\s*\('esx:getSharedObject',\s*function\s*\(obj\)\s*ESX\s*=\s*obj\s*end\s*\)": r"local QBox = exports['qbx_core']:GetCoreObject()",
    r"AddEventHandler\s*\('esx:getSharedObject',\s*function\s*\(cb\)\s*cb\s*\(ESX\)\s*end\s*\)": r"local QBox = exports['qbx_core']:GetCoreObject()",
    # Add more from common conversions
    r'ESX\.Trace\s*\((.*?)\)': r"QBox.Debug(\1)",
    r'xPlayer\.showNotification\s*\((.*?)\)': r"QBox.Functions.Notify(\1, 'info')"
}

# ----------------------------
# GUI Setup with Progress Bar
# ----------------------------
root = tk.Tk()
root.title("Improved ESX → QBox Full Safe Migrator")
root.geometry("560x420")

tk.Label(root, text="Select your ESX server folder:").pack(pady=10)
server_path_var = tk.StringVar()
entry = tk.Entry(root, textvariable=server_path_var, width=60)
entry.pack(pady=5)

def browse_folder():
    folder = filedialog.askdirectory()
    server_path_var.set(folder)

tk.Button(root, text="Browse", command=browse_folder).pack(pady=5)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, fill=tk.X, padx=20)

status_label = tk.Label(root, text="")
status_label.pack(pady=5)

# ----------------------------
# Script Conversion with Safety and Progress
# ----------------------------
def convert_scripts_thread():
    server_path = server_path_var.get()
    if not server_path:
        messagebox.showerror("Error", "Please select a server folder!")
        return

    src_resources = os.path.join(server_path, "resources")
    if not os.path.exists(src_resources):
        messagebox.showerror("Error", "Cannot find 'resources' folder in server path!")
        return

    backup_resources = os.path.join(server_path, "backup_resources")
    if os.path.exists(backup_resources):
        if not messagebox.askyesno("Backup Exists", "Backup already exists. Overwrite?"):
            return
        shutil.rmtree(backup_resources)
    shutil.copytree(src_resources, backup_resources)

    log_file = os.path.join(server_path, "script_conversion_log.txt")
    success_count = 0
    fail_count = 0

    # Count total Lua files for progress
    total_files = sum(1 for root_dir, _, files in os.walk(src_resources) for file in files if file.endswith(".lua"))
    processed = 0

    with open(log_file, "w", encoding="utf-8") as log:
        for root_dir, dirs, files in os.walk(src_resources):
            for file in files:
                if file.endswith(".lua"):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        original_content = content
                        for pattern, replacement in script_mapping.items():
                            content = re.sub(pattern, replacement, content)
                        if content != original_content:
                            with open(file_path, "w", encoding="utf-8") as f:
                                f.write(content)
                        log.write(f"SUCCESS: {file_path}\n")
                        success_count += 1
                    except Exception as e:
                        log.write(f"FAILED: {file_path} - {e}\n")
                        fail_count += 1
                    processed += 1
                    progress_var.set((processed / total_files) * 100)
                    root.update_idletasks()

    status_label.config(text=f"Conversion complete! Successful: {success_count}, Failed: {fail_count}")
    messagebox.showinfo(
        "Done",
        f"All resources processed!\nSuccessful: {success_count}\nFailed: {fail_count}\nSee 'script_conversion_log.txt' for details"
    )

def convert_scripts():
    status_label.config(text="Converting scripts...")
    progress_var.set(0)
    Thread(target=convert_scripts_thread).start()

# ----------------------------
# Improved Database Conversion with Better SQL Mapping
# ----------------------------
def convert_database():
    server_path = server_path_var.get()
    if not server_path:
        messagebox.showerror("Error", "Please select a server folder!")
        return

    sql_file = os.path.join(server_path, "esx.sql")
    if not os.path.exists(sql_file):
        messagebox.showerror("Error", "Cannot find 'esx.sql' in server folder!")
        return

    backup_sql = os.path.join(server_path, "backup_esx.sql")
    if os.path.exists(backup_sql):
        if not messagebox.askyesno("Backup Exists", "Backup SQL already exists. Overwrite?"):
            return
    shutil.copy2(sql_file, backup_sql)

    qbox_sql_file = os.path.join(server_path, "qbox_migration.sql")
    sql_content = """
-- ================= Improved QBox Full Migration =================
-- Note: This is an approximate migration. For complex servers, use official tools like https://github.com/qbcore-framework/esx-to-qbcore
-- Assumes standard ESX Legacy and QBX schemas. Adjust as needed.
-- Generate citizenid if not present.

-- Players (mapping money, job, etc.)
INSERT INTO players (citizenid, license, money, job, gang, position, inventory)
SELECT LOWER(HEX(RANDOM_BYTES(8))) AS citizenid,  -- Generate unique citizenid
       REPLACE(identifier, 'steam:', 'license:') AS license,
       JSON_OBJECT('cash', JSON_EXTRACT(accounts, '$.money'), 
                   'bank', JSON_EXTRACT(accounts, '$.bank'), 
                   'crypto', JSON_EXTRACT(accounts, '$.black_money')) AS money,
       JSON_OBJECT('name', job, 
                   'grade', JSON_OBJECT('level', job_grade, 
                                        'name', (SELECT name FROM job_grades WHERE job_name = job AND grade = job_grade LIMIT 1))) AS job,
       JSON_OBJECT('name', 'none', 'grade', JSON_OBJECT('level', 0)) AS gang,
       position,
       inventory  -- Assumes compatible JSON format; may need conversion
FROM users;

-- Vehicles (all types in one table typically)
INSERT INTO player_vehicles (license, citizenid, vehicle, plate, garage, state, mods)
SELECT REPLACE(u.identifier, 'steam:', 'license:') AS license,
       p.citizenid,  -- Join with players to get citizenid
       ov.vehicle,
       ov.plate,
       ov.garage,
       CASE WHEN ov.stored = 1 THEN 1 ELSE 0 END AS state,
       '{}' AS mods  -- Empty JSON; adjust if ESX has mods
FROM owned_vehicles ov
JOIN users u ON ov.owner = u.identifier
JOIN players