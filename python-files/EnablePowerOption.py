import os
import subprocess

# GUID for "High performance" power plan (Windows default)
HIGH_PERFORMANCE_GUID = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"

def set_power_plan():
    try:
        subprocess.run(["powercfg", "/setactive", HIGH_PERFORMANCE_GUID], check=True)
        print("High Performance power plan enabled.")
    except subprocess.CalledProcessError as e:
        print("Failed to change power plan:", e)

if name == "main":
    set_power_plan()