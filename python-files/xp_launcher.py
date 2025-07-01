import os
import struct
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import shutil
import json

QEMU_EXE = "qemu-system-i386.exe"
HDD_IMG = "winxp.qcow2"
XP_ISO = "WinXP.iso"
UPLOAD_IMG = "upload_fat32.img"
TEMPLATE_DRIVE = "blank_drive.img"  # Template blank drive file
DRIVES_CONFIG = "mounted_drives.json"  # Config file to save drive list
RAM_DEFAULT = "512"
ram_amount = RAM_DEFAULT

PARTITION_START_SECTOR = 2048
SECTOR_SIZE = 512
SECTORS_PER_CLUSTER = 8
RESERVED_SECTORS = 32
NUM_FATS = 2
ROOT_CLUSTER = 2
DEBUG_DIR = "debug_dump"

# Track multiple mounted drives - moved to global scope
mounted_drives = []

def save_drives_config():
    """Save the current mounted drives list to a config file"""
    try:
        config = {
            "mounted_drives": mounted_drives,
            "ram_amount": ram_amount
        }
        with open(DRIVES_CONFIG, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Saved drives config: {mounted_drives}")
    except Exception as e:
        print(f"Error saving drives config: {e}")

def load_drives_config():
    """Load the mounted drives list from config file"""
    global mounted_drives, ram_amount
    try:
        if os.path.exists(DRIVES_CONFIG):
            with open(DRIVES_CONFIG, 'r') as f:
                config = json.load(f)
            
            # Load drives list, filtering out non-existent files
            saved_drives = config.get("mounted_drives", [])
            mounted_drives = []
            for drive in saved_drives:
                if os.path.exists(drive):
                    mounted_drives.append(drive)
                else:
                    print(f"Warning: Previously mounted drive not found: {drive}")
            
            # Load RAM setting
            saved_ram = config.get("ram_amount", RAM_DEFAULT)
            if str(saved_ram).isdigit():
                ram_amount = str(saved_ram)
            
            print(f"Loaded drives config: {mounted_drives}")
            if mounted_drives:
                print(f"Restored {len(mounted_drives)} mounted drives")
    except Exception as e:
        print(f"Error loading drives config: {e}")
        mounted_drives = []

def create_template_drive_if_needed():
    """Create a template blank drive if it doesn't exist"""
    if os.path.exists(TEMPLATE_DRIVE):
        return True
    
    print(f"Creating template drive: {TEMPLATE_DRIVE}")
    try:
        # Use qemu-img to create a properly formatted FAT32 drive
        qemu_img_exe = QEMU_EXE.replace("qemu-system-i386", "qemu-img")
        
        # Create a raw image
        result = subprocess.run([
            qemu_img_exe, "create", "-f", "raw", TEMPLATE_DRIVE, "64M"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to create template with qemu-img: {result.stderr}")
            return create_manual_template()
        
        # Format it with a proper FAT32 structure using the original function
        # but only if qemu-img creation succeeded
        return format_template_drive()
        
    except Exception as e:
        print(f"Error creating template drive: {e}")
        return create_manual_template()

def create_manual_template():
    """Fallback method to create template manually"""
    try:
        return create_blank_fat32_image(TEMPLATE_DRIVE, 64)
    except Exception as e:
        print(f"Failed to create manual template: {e}")
        return False

def format_template_drive():
    """Format the template drive with a minimal FAT32 structure"""
    try:
        size_mb = 64
        total_sectors, clusters, fat_sectors, fs_sectors = calc_sizes(size_mb)
        
        with open(TEMPLATE_DRIVE, 'r+b') as f:
            # Create a minimal working FAT32 structure
            img = bytearray(total_sectors * SECTOR_SIZE)
            
            # Simple MBR
            mbr = bytearray(SECTOR_SIZE)
            part_entry = bytearray([0x80, 1, 1, 0, 0x0C, 254, 255, 255])
            part_entry += struct.pack('<I', PARTITION_START_SECTOR)
            part_entry += struct.pack('<I', fs_sectors)
            mbr[0x1BE:0x1BE+16] = part_entry
            mbr[510:512] = b'\x55\xAA'
            img[:SECTOR_SIZE] = mbr
            
            # Simple boot sector
            bs = bytearray(SECTOR_SIZE)
            bs[0:3] = b'\xEB\x58\x90'
            bs[3:11] = b'MSDOS5.0'
            struct.pack_into('<H', bs, 11, SECTOR_SIZE)
            bs[13] = SECTORS_PER_CLUSTER
            struct.pack_into('<H', bs, 14, RESERVED_SECTORS)
            bs[16] = NUM_FATS
            bs[21] = 0xF8
            struct.pack_into('<I', bs, 32, fs_sectors)
            struct.pack_into('<I', bs, 36, fat_sectors)
            struct.pack_into('<I', bs, 44, ROOT_CLUSTER)
            bs[510:512] = b'\x55\xAA'
            
            start = PARTITION_START_SECTOR * SECTOR_SIZE
            img[start:start + SECTOR_SIZE] = bs
            
            # Simple FAT
            fat = bytearray(fat_sectors * SECTOR_SIZE)
            fat[0:4] = b'\xF8\xFF\xFF\x0F'
            fat[4:8] = b'\xFF\xFF\xFF\xFF'
            fat[8:12] = b'\xFF\xFF\xFF\x0F'
            
            fat_offset = start + RESERVED_SECTORS * SECTOR_SIZE
            for i in range(NUM_FATS):
                img[fat_offset + i * fat_sectors * SECTOR_SIZE:fat_offset + (i+1)*fat_sectors * SECTOR_SIZE] = fat
            
            f.write(img)
        
        print(f"Template drive created successfully: {TEMPLATE_DRIVE}")
        return True
        
    except Exception as e:
        print(f"Error formatting template drive: {e}")
        return False

def calc_sizes(size_mb):
    cluster_size = SECTOR_SIZE * SECTORS_PER_CLUSTER
    
    # Calculate total sectors available for the filesystem
    requested_bytes = size_mb * 1024 * 1024
    
    # Start with an estimate and iterate to find the right size
    # We need to account for: MBR + reserved sectors + FATs + data clusters
    
    # Estimate data clusters needed
    estimated_data_bytes = requested_bytes * 0.95  # Leave some overhead
    estimated_clusters = max(65525, int(estimated_data_bytes // cluster_size))
    
    # Calculate FAT size for this cluster count
    fat_entries = estimated_clusters + 2  # +2 for reserved entries  
    fat_size_bytes = fat_entries * 4
    fat_sectors = (fat_size_bytes + SECTOR_SIZE - 1) // SECTOR_SIZE
    
    # Calculate total sectors needed
    filesystem_overhead = RESERVED_SECTORS + (NUM_FATS * fat_sectors)
    data_sectors = estimated_clusters * SECTORS_PER_CLUSTER
    total_fs_sectors = filesystem_overhead + data_sectors
    total_sectors = PARTITION_START_SECTOR + total_fs_sectors
    
    # Verify we're not exceeding the requested size too much
    actual_size_mb = (total_sectors * SECTOR_SIZE) // (1024 * 1024)
    if actual_size_mb > size_mb * 1.5:  # If we're way over, reduce clusters
        max_data_bytes = (size_mb * 1024 * 1024) - (PARTITION_START_SECTOR * SECTOR_SIZE) - (filesystem_overhead * SECTOR_SIZE)
        estimated_clusters = max(65525, int(max_data_bytes // cluster_size))
        
        # Recalculate with reduced clusters
        fat_entries = estimated_clusters + 2
        fat_size_bytes = fat_entries * 4  
        fat_sectors = (fat_size_bytes + SECTOR_SIZE - 1) // SECTOR_SIZE
        data_sectors = estimated_clusters * SECTORS_PER_CLUSTER
        total_fs_sectors = RESERVED_SECTORS + (NUM_FATS * fat_sectors) + data_sectors
        total_sectors = PARTITION_START_SECTOR + total_fs_sectors
    
    return total_sectors, estimated_clusters, fat_sectors, total_fs_sectors

def create_fat32_image(filename, outfile):
    with open(filename, 'rb') as f:
        filedata = f.read()
    filesize = len(filedata)
    
    # Calculate minimum size needed (file size + some overhead for FAT32)
    min_size_mb = max(32, (filesize // (1024 * 1024)) + 10)
    total_sectors, clusters, fat_sectors, fs_sectors = calc_sizes(min_size_mb)
    img = bytearray(total_sectors * SECTOR_SIZE)

    # MBR
    mbr = bytearray(SECTOR_SIZE)
    part_entry = bytearray([
        0x80, 1, 1, 0, 0x0C, 254, 255, 255
    ]) + struct.pack('<I', PARTITION_START_SECTOR) + struct.pack('<I', total_sectors - PARTITION_START_SECTOR)
    mbr[0x1BE:0x1BE+16] = part_entry
    mbr[510:512] = b'\x55\xAA'
    img[:SECTOR_SIZE] = mbr

    # Boot sector
    bs = bytearray(SECTOR_SIZE)
    bs[0:3] = b'\xEB\x58\x90'
    bs[3:11] = b'MSDOS5.0'
    struct.pack_into('<H', bs, 11, SECTOR_SIZE)
    bs[13] = SECTORS_PER_CLUSTER
    struct.pack_into('<H', bs, 14, RESERVED_SECTORS)
    bs[16] = NUM_FATS
    bs[21] = 0xF8
    struct.pack_into('<H', bs, 24, 63)
    struct.pack_into('<H', bs, 26, 255)
    struct.pack_into('<I', bs, 32, fs_sectors)
    struct.pack_into('<I', bs, 36, fat_sectors)
    struct.pack_into('<I', bs, 44, ROOT_CLUSTER)
    bs[510:512] = b'\x55\xAA'

    start = PARTITION_START_SECTOR * SECTOR_SIZE
    img[start:start + SECTOR_SIZE] = bs
    img[start + 6 * SECTOR_SIZE:start + 7 * SECTOR_SIZE] = bs  # backup boot

    # FSINFO
    fsinfo = bytearray(SECTOR_SIZE)
    fsinfo[0:4] = b'RRaA'
    fsinfo[484:488] = b'rrAa'
    struct.pack_into('<I', fsinfo, 488, clusters - 2)  # Free clusters (total - root - file)
    struct.pack_into('<I', fsinfo, 492, 4)  # Next free cluster
    fsinfo[510:512] = b'\x55\xAA'
    img[start + SECTOR_SIZE:start + 2 * SECTOR_SIZE] = fsinfo

    # FAT
    fat = bytearray(fat_sectors * SECTOR_SIZE)
    fat[0:4] = b'\xF8\xFF\xFF\x0F'
    struct.pack_into('<I', fat, 4, 0xFFFFFFFF)
    struct.pack_into('<I', fat, 8, 0x0FFFFFFF)  # Root directory (end of chain)
    struct.pack_into('<I', fat, 12, 0x0FFFFFFF)  # File cluster (end of chain)
    
    # Mark remaining clusters as free
    for i in range(4, clusters + 2):
        struct.pack_into('<I', fat, i * 4, 0x00000000)
    
    fat_offset = start + RESERVED_SECTORS * SECTOR_SIZE
    for i in range(NUM_FATS):
        img[fat_offset + i * fat_sectors * SECTOR_SIZE : fat_offset + (i+1)*fat_sectors * SECTOR_SIZE] = fat

    # Root dir entry
    entry = bytearray(32)
    name, ext = os.path.splitext(os.path.basename(filename))
    name = ''.join(c for c in name[:8].upper() if c.isalnum()).ljust(8)
    ext = ''.join(c for c in ext[1:4].upper() if c.isalnum()).ljust(3)
    entry[0:8] = name.encode('ascii')
    entry[8:11] = ext.encode('ascii')
    entry[11] = 0x20
    struct.pack_into('<H', entry, 26, 3)  # Start cluster = 3
    struct.pack_into('<I', entry, 28, filesize)
    root_start = fat_offset + NUM_FATS * fat_sectors * SECTOR_SIZE
    img[root_start:root_start + 32] = entry

    # File data in cluster 3
    data_start = root_start + SECTORS_PER_CLUSTER * SECTOR_SIZE
    img[data_start:data_start + filesize] = filedata

    with open(outfile, 'wb') as f:
        f.write(img)
    print(f"Disk image '{outfile}' created.")

def create_blank_fat32_image_from_template(outfile):
    """Create a blank FAT32 drive by copying the template"""
    try:
        # Ensure template exists
        if not create_template_drive_if_needed():
            raise Exception("Could not create or find template drive")
        
        # Copy the template
        shutil.copy2(TEMPLATE_DRIVE, outfile)
        
        print(f"Successfully created blank drive '{outfile}' from template")
        return True
        
    except Exception as e:
        print(f"Error creating blank drive from template: {str(e)}")
        # Fallback to original method
        print("Falling back to original creation method...")
        return create_blank_fat32_image(outfile, 64)

def create_blank_fat32_image(outfile, size_mb):
    try:
        # Validate input
        if size_mb < 32:
            raise ValueError("FAT32 requires at least 32MB")
        
        # Calculate actual size needed for the requested MB
        total_sectors, clusters, fat_sectors, fs_sectors = calc_sizes(size_mb)
        
        print(f"Creating {size_mb}MB drive with {clusters} clusters, {fat_sectors} FAT sectors")
        
        # Create the image
        img = bytearray(total_sectors * SECTOR_SIZE)

        # Create MBR (Master Boot Record)
        mbr = bytearray(SECTOR_SIZE)
        # Bootable flag (0x80), CHS start (1,1,0), partition type (0x0C = FAT32 LBA)
        part_entry = bytearray([
            0x80, 1, 1, 0, 0x0C, 254, 255, 255
        ])
        # Add partition start sector and size
        part_entry += struct.pack('<I', PARTITION_START_SECTOR)
        part_entry += struct.pack('<I', fs_sectors)
        
        # Place partition entry in MBR
        mbr[0x1BE:0x1BE+16] = part_entry
        mbr[510:512] = b'\x55\xAA'  # Boot signature
        img[:SECTOR_SIZE] = mbr

        # Create Boot Sector
        bs = bytearray(SECTOR_SIZE)
        bs[0:3] = b'\xEB\x58\x90'  # Jump instruction
        bs[3:11] = b'MSDOS5.0'     # OEM name
        
        # BIOS Parameter Block (BPB)
        struct.pack_into('<H', bs, 11, SECTOR_SIZE)        # Bytes per sector
        bs[13] = SECTORS_PER_CLUSTER                       # Sectors per cluster
        struct.pack_into('<H', bs, 14, RESERVED_SECTORS)   # Reserved sectors
        bs[16] = NUM_FATS                                  # Number of FATs
        struct.pack_into('<H', bs, 17, 0)                  # Root entries (0 for FAT32)
        struct.pack_into('<H', bs, 19, 0)                  # Total sectors (0 for FAT32)
        bs[21] = 0xF8                                      # Media descriptor
        struct.pack_into('<H', bs, 22, 0)                  # FAT size (0 for FAT32)
        struct.pack_into('<H', bs, 24, 63)                 # Sectors per track
        struct.pack_into('<H', bs, 26, 255)                # Number of heads
        struct.pack_into('<I', bs, 28, PARTITION_START_SECTOR)  # Hidden sectors
        struct.pack_into('<I', bs, 32, fs_sectors)         # Total sectors (FAT32)
        
        # FAT32 Extended BPB
        struct.pack_into('<I', bs, 36, fat_sectors)        # FAT size
        struct.pack_into('<H', bs, 40, 0)                  # Extended flags
        struct.pack_into('<H', bs, 42, 0)                  # Filesystem version
        struct.pack_into('<I', bs, 44, ROOT_CLUSTER)       # Root cluster
        struct.pack_into('<H', bs, 48, 1)                  # FSInfo sector
        struct.pack_into('<H', bs, 50, 6)                  # Backup boot sector
        
        # Add boot signature
        bs[510:512] = b'\x55\xAA'

        # Write boot sector and backup
        start = PARTITION_START_SECTOR * SECTOR_SIZE
        img[start:start + SECTOR_SIZE] = bs
        img[start + 6 * SECTOR_SIZE:start + 7 * SECTOR_SIZE] = bs  # backup boot

        # Create FSINFO sector
        fsinfo = bytearray(SECTOR_SIZE)
        fsinfo[0:4] = b'RRaA'      # Lead signature
        fsinfo[484:488] = b'rrAa'  # Structure signature
        # Only root directory cluster (2) is used, so free clusters = total_clusters - 1
        struct.pack_into('<I', fsinfo, 488, clusters - 1)  # Free cluster count (total - root cluster)
        struct.pack_into('<I', fsinfo, 492, 3)             # Next free cluster (first available after root)
        fsinfo[508:512] = b'\x00\x00\x55\xAA'             # Trail signature
        img[start + SECTOR_SIZE:start + 2 * SECTOR_SIZE] = fsinfo

        # Create FAT
        fat = bytearray(fat_sectors * SECTOR_SIZE)
        # Initialize reserved FAT entries
        fat[0:4] = b'\xF8\xFF\xFF\x0F'        # Media descriptor + end of chain
        struct.pack_into('<I', fat, 4, 0xFFFFFFFF)    # Reserved cluster 1
        struct.pack_into('<I', fat, 8, 0x0FFFFFFF)    # Root directory cluster (end of chain)
        
        # All other clusters should remain 0x00000000 (free) - they're already zeroed in bytearray
        
        # Mark remaining clusters as free (already 0x00000000 in bytearray)
        
        # Write both FAT copies
        fat_offset = start + RESERVED_SECTORS * SECTOR_SIZE
        for i in range(NUM_FATS):
            fat_start = fat_offset + i * fat_sectors * SECTOR_SIZE
            fat_end = fat_start + fat_sectors * SECTOR_SIZE
            img[fat_start:fat_end] = fat

        # Root directory is already initialized (empty) at cluster 2
        
        # Write the image file
        with open(outfile, 'wb') as f:
            f.write(img)
        
        usable_mb = (clusters * SECTORS_PER_CLUSTER * SECTOR_SIZE) // (1024*1024)
        print(f"Successfully created {size_mb}MB FAT32 drive '{outfile}' with {clusters} clusters ({usable_mb}MB usable)")
        return True
        
    except Exception as e:
        print(f"Error creating FAT32 image: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def build_base_args():
    return [
        "-m", ram_amount,
        "-hda", HDD_IMG,
        "-vga", "std",
        "-device", "AC97",
        "-net", "user",
        "-net", "nic"
    ]

def launch_xp():
    if not os.path.exists(QEMU_EXE):
        messagebox.showerror("Error", f"QEMU not found: {QEMU_EXE}")
        return

    if not os.path.exists(HDD_IMG):
        qemu_img_exe = QEMU_EXE.replace("qemu-system-i386", "qemu-img")
        subprocess.run([qemu_img_exe, "create", "-f", "qcow2", HDD_IMG, "10G"])

    # Build base arguments
    args = [QEMU_EXE, "-m", ram_amount, "-hda", HDD_IMG, "-vga", "std", 
            "-device", "AC97", "-net", "user", "-net", "nic"]

    # Add mounted drives (starting from IDE index 1)
    valid_drives = []
    for i, drive_path in enumerate(mounted_drives):
        if os.path.exists(drive_path):  # Check if drive file exists
            drive_index = i + 1  # IDE index=0 is taken by winxp.qcow2
            args += ["-drive", f"file={drive_path},format=raw,if=ide,index={drive_index},media=disk"]
            valid_drives.append(drive_path)
        else:
            print(f"Warning: Drive file not found: {drive_path}")

    # Update mounted drives list to only include valid drives
    if len(valid_drives) != len(mounted_drives):
        mounted_drives[:] = valid_drives
        save_drives_config()

    args += ["-boot", "c"]

    subprocess.Popen(args)
    root.destroy()

def setup_xp():
    if not os.path.exists(XP_ISO):
        messagebox.showerror("Missing ISO", f"'{XP_ISO}' not found.")
        return
    if not os.path.exists(HDD_IMG):
        qemu_img_exe = QEMU_EXE.replace("qemu-system-i386", "qemu-img")
        subprocess.run([qemu_img_exe, "create", "-f", "qcow2", HDD_IMG, "10G"])
    
    args = [QEMU_EXE] + build_base_args() + ["-boot", "d", "-cdrom", XP_ISO]
    subprocess.Popen(args)
    root.destroy()

def setup_drive():
    def refresh_drive_list():
        for widget in drive_list_frame.winfo_children():
            widget.destroy()
        for idx, drive in enumerate(mounted_drives):
            drive_name = os.path.basename(drive)
            exists_text = "" if os.path.exists(drive) else " (MISSING)"
            tk.Label(drive_list_frame, text=f"{chr(69+idx)}: {drive_name}{exists_text}").grid(row=idx, column=0, sticky="w")
            tk.Button(drive_list_frame, text="Remove", command=lambda i=idx: remove_drive(i)).grid(row=idx, column=1, padx=5)

    def add_drive():
        file = filedialog.askopenfilename(title="Select file to mount as drive")
        if not file:
            return
        mounted_drives.append(file)
        save_drives_config()  # Save immediately
        refresh_drive_list()

    def remove_drive(index):
        if 0 <= index < len(mounted_drives):
            mounted_drives.pop(index)
            save_drives_config()  # Save immediately
            refresh_drive_list()

    win = tk.Toplevel(root)
    win.title("Drive Manager")
    win.geometry("500x300")

    tk.Label(win, text="Mounted Drives (Persistent):", font=("Arial", 12, "bold")).pack(pady=5)
    
    drive_list_frame = tk.Frame(win)
    drive_list_frame.pack(pady=10, fill="both", expand=True)

    button_frame = tk.Frame(win)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Add Drive", command=add_drive).pack(side="left", padx=5)
    tk.Button(button_frame, text="Add Blank Drive", command=lambda: add_blank_drive(refresh_drive_list)).pack(side="left", padx=5)
    tk.Button(button_frame, text="Close", command=win.destroy).pack(side="left", padx=5)
    
    refresh_drive_list()

def add_blank_drive(callback_refresh=None):
    def confirm():
        try:
            outfile = f"blank_drive_{len(mounted_drives)+1}.img"
            
            # Use the template-based method
            success = create_blank_fat32_image_from_template(outfile)
            if success:
                mounted_drives.append(outfile)
                save_drives_config()  # Save immediately
                messagebox.showinfo("Drive Added", f"Created and mounted new blank drive: {outfile}")
                if callback_refresh:
                    callback_refresh()
                win.destroy()
            else:
                messagebox.showerror("Error", "Failed to create drive - check console for details")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create drive: {str(e)}")

    win = tk.Toplevel(root)
    win.title("Add Blank Drive")
    win.geometry("300x120")
    
    tk.Label(win, text="Create a new 64MB blank FAT32 drive").pack(pady=10)
    
    button_frame = tk.Frame(win)
    button_frame.pack(pady=15)
    tk.Button(button_frame, text="Create", command=confirm).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=win.destroy).pack(side="left", padx=5)

def mount_iso():
    file = filedialog.askopenfilename(title="Select ISO to mount", filetypes=[("ISO files", "*.iso")])
    if not file: 
        return
    if not os.path.exists(HDD_IMG):
        qemu_img_exe = QEMU_EXE.replace("qemu-system-i386", "qemu-img")
        subprocess.run([qemu_img_exe, "create", "-f", "qcow2", HDD_IMG, "10G"])
    
    args = [
        QEMU_EXE,
        "-m", ram_amount,
        "-hda", HDD_IMG,
        "-vga", "std",
        "-device", "AC97",
        "-net", "user",
        "-net", "nic"
    ]
    
    # Add mounted drives (starting from IDE index 1)
    for i, drive_path in enumerate(mounted_drives):
        if os.path.exists(drive_path):
            drive_index = i + 1
            args += ["-drive", f"file={drive_path},format=raw,if=ide,index={drive_index},media=disk"]
    
    args += ["-cdrom", file, "-boot", "d"]
    
    subprocess.Popen(args)
    root.destroy()

def open_options():
    global ram_amount
    
    def apply():
        global ram_amount
        val = entry.get().strip()
        if val.isdigit() and int(val) > 0:
            ram_amount = val
            save_drives_config()  # Save RAM setting too
            messagebox.showinfo("Options", f"RAM set to {ram_amount}MB")
            win.destroy()
        else:
            messagebox.showerror("Error", "Enter a valid RAM amount in MB")
    
    win = tk.Toplevel(root)
    win.title("Options")
    win.geometry("200x120")
    
    tk.Label(win, text="RAM (MB):").pack(pady=5)
    entry = tk.Entry(win)
    entry.insert(0, ram_amount)
    entry.pack(pady=5)
    
    button_frame = tk.Frame(win)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Apply", command=apply).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=win.destroy).pack(side="left", padx=5)

def on_closing():
    """Handle application closing - save config before exit"""
    save_drives_config()
    root.destroy()

# Initialize template and load config on startup
create_template_drive_if_needed()
load_drives_config()

# Main GUI
root = tk.Tk()
root.title("Windows XP Launcher")
root.geometry("320x240")
root.protocol("WM_DELETE_WINDOW", on_closing)  # Save config on close

tk.Label(root, text="Windows XP Launcher", font=("Arial", 14)).pack(pady=10)

# Show loaded drives info
if mounted_drives:
    tk.Label(root, text=f"({len(mounted_drives)} drives loaded)", font=("Arial", 8), fg="gray").pack()

frm = tk.Frame(root)
frm.pack()

tk.Button(frm, text="Launch XP", width=15, command=launch_xp).grid(row=0, column=0, padx=10, pady=5)
tk.Button(frm, text="Setup XP", width=15, command=setup_xp).grid(row=0, column=1, padx=5)
tk.Button(frm, text="Setup Drives", width=15, command=setup_drive).grid(row=1, column=0, padx=10, pady=5)
tk.Button(frm, text="Mount Disk (.iso)", width=15, command=mount_iso).grid(row=1, column=1, padx=10, pady=5)
tk.Button(frm, text="Options", width=15, command=open_options).grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()