#!/usr/bin/env python3
"""
Device Fingerprinting Tool
Generates a unique device fingerprint for licensing purposes.
"""

import uuid
import platform
import subprocess
import hashlib
import json
import sys

def get_mac_address():
    """Get the MAC address of the primary network interface."""
    try:
        mac = uuid.getnode()
        return f"{mac:012x}"
    except:
        return "unknown"

def get_cpu_info():
    """Get CPU information."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'ProcessorId', '/format:list'],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'ProcessorId=' in line:
                    return line.split('=')[1].strip()
        elif platform.system() == "Linux":
            # Try to get CPU serial from /proc/cpuinfo
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'Serial' in line:
                        return line.split(':')[1].strip()
            # Fallback to CPU model
            result = subprocess.run(
                ['lscpu'], capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'Model name:' in line:
                    return line.split(':')[1].strip()
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ['system_profiler', 'SPHardwareDataType'],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'Serial Number' in line:
                    return line.split(':')[1].strip()
    except:
        pass
    return "unknown"

def get_motherboard_serial():
    """Get motherboard serial number."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'baseboard', 'get', 'serialnumber', '/format:list'],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'SerialNumber=' in line:
                    return line.split('=')[1].strip()
        elif platform.system() == "Linux":
            result = subprocess.run(
                ['dmidecode', '-s', 'baseboard-serial-number'],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip()
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ['system_profiler', 'SPHardwareDataType'],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'Hardware UUID:' in line:
                    return line.split(':')[1].strip()
    except:
        pass
    return "unknown"

def get_disk_serial():
    """Get primary disk serial number."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'diskdrive', 'get', 'serialnumber', '/format:list'],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'SerialNumber=' in line and line.split('=')[1].strip():
                    return line.split('=')[1].strip()
        elif platform.system() == "Linux":
            # Try to get serial from /dev/sda
            result = subprocess.run(
                ['lsblk', '-d', '-o', 'name,serial'],
                capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] != '':
                        return parts[1]
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ['diskutil', 'info', 'disk0'],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'Device / Media UUID:' in line:
                    return line.split(':')[1].strip()
    except:
        pass
    return "unknown"

def get_system_info():
    """Get basic system information."""
    return {
        'platform': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'hostname': platform.node()
    }

def get_timestamp():
    """Get current timestamp in a cross-platform way."""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['date', '/t'], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        else:
            result = subprocess.run(['date'], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
    except:
        # Fallback to Python's datetime if system command fails
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_device_fingerprint():
    """Generate a unique device fingerprint."""
    # print("🔍 Generating device fingerprint...")
    # print("=" * 50)
    
    # Collect device information
    mac_addr = get_mac_address()
    cpu_info = get_cpu_info()
    motherboard_serial = get_motherboard_serial()
    disk_serial = get_disk_serial()
    system_info = get_system_info()
    
    # print(f"📱 MAC Address: {mac_addr}")
    # print(f"🖥️  CPU Info: {cpu_info}")
    # print(f"🔧 Motherboard Serial: {motherboard_serial}")
    # print(f"💾 Disk Serial: {disk_serial}")
    # print(f"🖥️  System: {system_info['platform']} {system_info['machine']}")
    # print(f"🏠 Hostname: {system_info['hostname']}")
    
    # Create combined fingerprint
    fingerprint_data = f"{mac_addr}-{cpu_info}-{motherboard_serial}-{disk_serial}-{system_info['platform']}"
    
    # Generate hash for shorter, consistent ID
    device_id = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    # print("=" * 50)
    # print(f"🆔 Device ID: {device_id}")
    
    # Create detailed result
    result = {
        'device_id': device_id,
        'fingerprint_raw': fingerprint_data,
        'details': {
            'mac_address': mac_addr,
            'cpu_info': cpu_info,
            'motherboard_serial': motherboard_serial,
            'disk_serial': disk_serial,
            'system_info': system_info
        },
        'timestamp': get_timestamp()
    }
    
    return result

def main():
    """Main function to generate and save device fingerprint."""
    try:
        # print("🚀 AutoClick Tool - Device Fingerprint Generator")
        # print("=" * 50)
        
        # Generate fingerprint
        result = generate_device_fingerprint()
        

        
        # Save as JSON for programmatic use
        with open('device_fingerprint.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        # print("=" * 50)
        # print("✅ Device fingerprint saved to: device_fingerprint.json")

        # print("📧 Send the device_fingerprint.json file to get your license!")
        # print("ID thiết bị của bạn là:", result['device_id'])
        # print("Hãy gửi ID này cho người bán để nhận bản quyền.")
        # print("Nếu bạn cần hỗ trợ thêm, hãy liên hệ với người bán.")

        # Show Tkinter UI with copyable device ID
        import tkinter as tk
        from tkinter import messagebox
        def copy_to_clipboard():
            root.clipboard_clear()
            root.clipboard_append(result['device_id'])
            messagebox.showinfo("Đã sao chép", "ID thiết bị đã được sao chép vào clipboard!")
        root = tk.Tk()
        root.title("Device ID")
        root.geometry("420x180")
        root.resizable(False, False)
        tk.Label(root, text="ID thiết bị của bạn là:", font=("Arial", 12, "bold")).pack(pady=(18, 5))
        entry = tk.Entry(root, font=("Courier", 14), width=32, justify='center')
        entry.insert(0, result['device_id'])
        entry.config(state='readonly')
        entry.pack(pady=(0, 5))
        copy_btn = tk.Button(root, text="📋 Sao chép ID", command=copy_to_clipboard, font=("Arial", 11))
        copy_btn.pack(pady=(0, 10))
        tk.Label(root, text="Hãy gửi ID này cho người bán để nhận bản quyền.\nNếu bạn cần hỗ trợ thêm, hãy liên hệ với người bán.", font=("Arial", 10), wraplength=400, justify='center').pack(pady=(0, 10))
        root.mainloop()
    except Exception as e:
        print(f"❌ Error generating fingerprint: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
