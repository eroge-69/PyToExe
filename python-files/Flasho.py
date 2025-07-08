#!/usr/bin/env python3

import os
import subprocess
import sys

def confirm(prompt):
    answer = input(f"{prompt} (y/n): ").lower()
    return answer in ['y', 'yes']

def write_iso_to_device(iso_path, device):
    if not os.path.isfile(iso_path):
        print("Error: ISO file not found.")
        return

    if not os.path.exists(device):
        print("Error: Device not found.")
        return

    print(f"WARNING: This will completely erase all data on {device}")
    if not confirm("Are you sure you want to continue?"):
        print("Aborted.")
        return

    try:
        print("Writing ISO to device... This may take a while.")
        subprocess.run(["sudo", "dd", f"if={iso_path}", f"of={device}", "bs=4M", "status=progress", "oflag=sync"], check=True)
        print("✅ ISO written successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to write ISO.")

def list_devices():
    print("\nAvailable storage devices:")
    subprocess.run(["lsblk", "-d", "-o", "NAME,SIZE,MODEL"], check=True)

def main():
    print("=== ISO Writer ===")
    list_devices()
    iso_path = input("\nEnter the full path to the ISO file: ").strip()
    device = input("Enter the device path (e.g., /dev/sdb): ").strip()
    write_iso_to_device(iso_path, device)

if __name__ == "__main__":
    main()
