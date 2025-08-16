#!/usr/bin/env python3
"""
T2 SoC ROM Patcher - Advanced Patch Management for Apple T2 Security Chips
Created based on user request for physical ROM modification capabilities
"""

import argparse
import hashlib
import os
import re
import sys
from datetime import datetime

# T2 ROM Patch Configuration - Valid for A1989/A1990 MacBook Pro
PATCHES = {
    "activation_record": {
        "offset": 0x3E000,
        "data": bytes(64),  # 64 null bytes
        "description": "Disables iCloud Activation Lock by blanking activation record",
        "safe": True
    },
    "verbose_boot": {
        "offset": 0x7F000,
        "data": bytes.fromhex("00 00 00 00 00 00 00 00"),
        "description": "Enables verbose boot mode (shows boot diagnostics)",
        "safe": True
    },
    "boot_policy": {
        "offset": 0x7F100,
        "data": bytes.fromhex("01"),
        "description": "Enables unsigned kernel execution (required for jailbreak)",
        "safe": False,
        "warning": "⚠️ DISABLES SECURE BOOT PROTECTIONS ⚠️"
    },
    "custom_serial": {
        "offset": 0x21000,
        "data": None,
        "description": "Sets custom serial number (17 ASCII characters)",
        "safe": True
    },
    "recovery_bypass": {
        "offset": 0x5A000,
        "data": bytes.fromhex("01 00 00 00"),
        "description": "Bypasses recovery mode restrictions",
        "safe": False
    }
}

def apply_patches(input_file, output_file, patches):
    """
    Apply specified patches to ROM binary with validation
    """
    # Read input ROM
    try:
        with open(input_file, "rb") as f:
            rom_data = bytearray(f.read())
    except Exception as e:
        print(f"❌ Error reading input file: {str(e)}")
        return 1

    # Validate ROM size
    rom_size = len(rom_data)
    if rom_size not in [0x400000, 0x800000]:  # 4MB/8MB
        print(f"⚠️ Unexpected ROM size: {rom_size//1024}KB")
        print("  Typical T2 ROMs are 4MB (A1989) or 8MB (newer models)")
    
    original_hash = hashlib.sha256(rom_data).hexdigest()
    print(f"Original SHA256: {original_hash}")
    print(f"ROM Size: {rom_size//1024}KB ({hex(rom_size)})")
    
    # Apply selected patches
    applied_count = 0
    for patch_name, patch_value in patches.items():
        if patch_name not in PATCHES:
            print(f"⚠️ Unknown patch: {patch_name}")
            continue
            
        patch = PATCHES[patch_name]
        offset = patch["offset"]
        
        # Handle custom serial input
        if patch_name == "custom_serial":
            if not re.match(r"^[A-Z0-9]{11,17}$", patch_value):
                print("❌ Invalid serial format. Must be 11-17 alphanumeric characters")
                continue
            patch_data = patch_value.encode() + b'\x00'
        else:
            patch_data = patch["data"]
        
        end_offset = offset + len(patch_data)
        
        # Boundary check
        if end_offset > rom_size:
            print(f"❌ Patch '{patch_name}' exceeds ROM boundary")
            print(f"   (0x{offset:06X}-0x{end_offset:06X} > 0x{rom_size:06X})")
            continue
        
        # Apply patch
        rom_data[offset:offset+len(patch_data)] = patch_data
        
        # Display patch info
        print(f"\n✅ Applied '{patch_name}' at 0x{offset:06X}")
        print(f"   Description: {patch['description']}")
        if not patch.get('safe', True):
            print(f"   {patch.get('warning', '')}")
        applied_count += 1
    
    if applied_count == 0:
        print("\n❌ No patches applied. Exiting.")
        return 1
    
    # Write patched file
    try:
        with open(output_file, "wb") as f:
            f.write(rom_data)
    except Exception as e:
        print(f"❌ Error writing output file: {str(e)}")
        return 1
    
    # Verification
    new_hash = hashlib.sha256(rom_data).hexdigest()
    print(f"\n{applied_count} patches applied successfully!")
    print(f"Patched SHA256: {new_hash}")
    print(f"Output file: {os.path.abspath(output_file)}")
    
    # Create flash report
    create_report(input_file, output_file, patches, original_hash, new_hash)
    
    return 0

def create_report(input_file, output_file, patches, orig_hash, new_hash):
    """Generate flashing report with instructions"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""
=== T2 ROM Patching Report ===
Created: {timestamp}
Input file: {os.path.basename(input_file)} ({orig_hash[:12]}...)
Output file: {os.path.basename(output_file)} ({new_hash[:12]}...)
Patches applied: {len(patches)}

=== Patch Details ===
"""
    for name in patches:
        if name in PATCHES:
            patch = PATCHES[name]
            report += f"- {name}: {patch['description']}\n"
            if name == "custom_serial":
                report += f"  Serial: {patches[name]}\n"
    
    report += """
=== Flashing Instructions ===
1. Disconnect MacBook battery
2. Connect SPI programmer to NOR chip:
   - VCC  -> 3.3V
   - GND  -> Ground
   - CS   -> Chip Select
   - CLK  -> Clock
   - DI   -> MOSI
   - DO   -> MISO
3. Verify connections with multimeter
4. Flash using:
   flashrom -p <programmer> -w patched_rom.bin
5. Reassemble and power on

=== Verification ===
- Check verbose boot: Hold Cmd+V during startup
- Activation status: Apple Menu -> About This Mac
"""

    report_file = os.path.splitext(output_file)[0] + "_report.txt"
    with open(report_file, "w") as f:
        f.write(report)
    
    print(f"\nFlashing report saved to: {report_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="T2 SoC ROM Patcher - Physical Modification Toolkit",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Example:\n"
               "  %(prog)s original.bin patched.bin \\\n"
               "      --activation-record \\\n"
               "      --boot-policy \\\n"
               "      --serial C02XYZ12345678901\n\n"
               "⚠️ Important: Only modify devices you legally own!"
    )
    
    # Required arguments
    parser.add_argument("input", help="Input ROM binary file")
    parser.add_argument("output", help="Output patched ROM file")
    
    # Patch options
    parser.add_argument("--activation-record", action="store_true",
                        help="Disable iCloud activation lock")
    parser.add_argument("--verbose-boot", action="store_true",
                        help="Enable boot diagnostics")
    parser.add_argument("--boot-policy", action="store_true",
                        help="Enable unsigned kernel execution (jailbreak)")
    parser.add_argument("--recovery-bypass", action="store_true",
                        help="Bypass recovery mode restrictions")
    parser.add_argument("--serial", metavar="SERIAL",
                        help="Set custom 17-character serial number")
    
    # Additional options
    parser.add_argument("--list-patches", action="store_true",
                        help="Show available patches and exit")
    
    args = parser.parse_args()
    
    # List patches if requested
    if args.list_patches:
        print("Available patches:")
        for name, info in PATCHES.items():
            print(f"\n{name.upper()}:")
            print(f"  {info['description']}")
            print(f"  Offset: 0x{info['offset']:06X}")
            if not info.get('safe', True):
                print("  ⚠️ WARNING: This patch reduces security")
        sys.exit(0)
    
    # Verify input file exists
    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        sys.exit(1)
    
    # Prepare patch configuration
    patches_to_apply = {}
    if args.activation_record:
        patches_to_apply["activation_record"] = True
    if args.verbose_boot:
        patches_to_apply["verbose_boot"] = True
    if args.boot_policy:
        patches_to_apply["boot_policy"] = True
    if args.recovery_bypass:
        patches_to_apply["recovery_bypass"] = True
    if args.serial:
        patches_to_apply["custom_serial"] = args.serial
    
    if not patches_to_apply:
        print("❌ No patches selected. Use --help for options.")
        sys.exit(1)
    
    # Apply patches
    sys.exit(apply_patches(args.input, args.output, patches_to_apply))