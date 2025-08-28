import requests
import json
import base64
import argparse
import os
import sys 
import zipfile
import shutil
import tempfile
from colorama import Fore, init
from Crypto.Cipher import ChaCha20
import datetime

MASTER_KEY = [0xb3, 0xcb, 0x2e, 0x04, 0x87, 0x94, 0xd6, 0x73, 0x08, 0x23, 0xc4, 0x93, 0x7a, 0xbd, 0x18, 0xad, 0x6b, 0xe6, 0xdc, 0xb3, 0x91, 0x43, 0x0d, 0x28, 0xf9, 0x40, 0x9d, 0x48, 0x37, 0xb9, 0x38, 0xfb]
DECRYPT_FILES_COUNT = 0
SKIPPED_FILES_COUNT = 0
DB_PATH = "grant_cache.json"
CONFIG_PATH = "config.json"

def load_config():
    """Load configuration from config.json"""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"server_key": "", "last_used": "", "auto_load": True}

def save_config(config):
    """Save configuration to config.json"""
    try:
        config["last_used"] = datetime.datetime.now().isoformat()
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"{Fore.LIGHTYELLOW_EX}[!] Could not save config: {e}")

def get_server_key(provided_key=None):
    """Get server key from parameter, config, or user input"""
    if provided_key:
        # Save the provided key to config
        config = load_config()
        config["server_key"] = provided_key
        save_config(config)
        return provided_key
    
    # Try to load from config
    config = load_config()
    if config.get("server_key") and config.get("auto_load", True):
        print(f"{Fore.LIGHTGREEN_EX}[+] Using saved server key from config")
        return config["server_key"]
    
    return None

class Grants:
    def __init__(self, server_key=None):
        self.server_key = server_key

    def _decode_jwt(self, jwt_token):
        parts = jwt_token.split('.')
        if len(parts) != 3:
            raise ValueError(f"{Fore.LIGHTRED_EX}[!] Invalid JWT format")

        payload_b64 = parts[1] + '=' * (-len(parts[1]) % 4)
        payload_json = base64.urlsafe_b64decode(payload_b64.encode()).decode()
        return json.loads(payload_json)

    def _load_cache(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r") as f:
                    content = f.read().strip()
                    if not content:
                        return {} 
                    return json.loads(content)
            except json.JSONDecodeError:
                print(f"{Fore.LIGHTRED_EX}[!] grant_cache.json is empty or corrupted. Using empty cache.")
                return {}
        return {}

    def _save_cache(self, cache):
        with open(DB_PATH, "w") as f:
            json.dump(cache, f, indent=2)

    def _update_cache_with_key(self, key, cache):
        url = f"https://keymaster.fivem.net/api/validate/{key}"
        resp = requests.get(url)

        if resp.status_code != 200:
            print(f"{Fore.LIGHTRED_EX}[!] Error with key: {key} (Status code: {resp.status_code})")
            return []

        data = resp.json()
        grants_token = data.get("grants_token")
        if not grants_token:
            return []

        payload = self._decode_jwt(grants_token)
        grants = payload.get("grants", {})

        new_ids = []
        for rid, val in grants.items():
            if rid not in cache:
                cache[rid] = val
                new_ids.append(rid)

        return new_ids

    def get_all(self):
        cache = self._load_cache()
        new_ids = self._update_cache_with_key(self.server_key, cache)

        if new_ids:
            self._save_cache(cache)
            print(f"{Fore.LIGHTGREEN_EX}[+] Retrieved {len(new_ids)} new IDs.{Fore.RESET}")
        else:
            print(f"{Fore.LIGHTYELLOW_EX}[-] No new IDs found or invalid key.{Fore.RESET}")

    def get_hash(self, resource_id, server_key=None):
        resource_id = str(resource_id)
        cache = self._load_cache()

        # Si ya tenemos la key en cache, devolverla inmediatamente
        if resource_id in cache:
            print(f"{Fore.LIGHTGREEN_EX}[+] Using cached key for resource {resource_id}")
            return cache[resource_id]

        # Solo hacer la consulta a keymaster si no tenemos la key
        key_to_use = server_key or self.server_key
        if not key_to_use:
            return None

        print(f"{Fore.LIGHTCYAN_EX}[+] Fetching key from keymaster for resource {resource_id}")
        self._update_cache_with_key(key_to_use, cache)

        if resource_id in cache:
            self._save_cache(cache)
            return cache[resource_id]

        return None

class Escrow:
    def __init__(self, fx_base, fx_file, server_key):
        self.fx_base = fx_base
        self.fx_file = fx_file
        self.server_key = server_key
        self.resource_key = None

    def is_valid(self):
        fxapContent = None
        with open(self.fx_file, "rb") as f:
            fxapContent = f.read()

        return fxapContent[:4] == b'FXAP'

    def get_resource_id(self):
        if not self.is_valid():
            return

        file = None
        with open(self.fx_base, "rb") as f:
            file = f.read()
        
        iv = file[0x4a:0x4a + 0xc]
        cipher = ChaCha20.new(key=bytes(MASTER_KEY), nonce=iv)
        decrypted = cipher.decrypt(file[0x56:])
        resource_id = int.from_bytes(decrypted[0x4a:0x4a + 4], byteorder="big")

        return resource_id

    def get_key(self):
        resource_id = self.get_resource_id()

        grants = Grants(server_key=self.server_key)
        key = grants.get_hash(resource_id)
        
        if key is None and self.server_key is None:
            print(f"{Fore.LIGHTRED_EX}[!] Key doesn't have the resource{Fore.RESET}")
            sys.exit(1)

        if key is None:
            key = grants.get_hash(resource_id, server_key=self.server_key)

        if key is not None:
            pass
        else:
            print(f"{Fore.LIGHTRED_EX}[!]  Key doesn't have the resource{Fore.RESET}")
            sys.exit(1)

        self.resource_key = key

    def save_decrypted(self, decrypted, base_input_dir, resource_name=None):
        import os

        rel_path = os.path.relpath(self.fx_file, base_input_dir)
        output_dir = os.path.join("./out", resource_name)
        output_path = os.path.join(output_dir, rel_path)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        content = decrypted
        if self.fx_file.endswith("fxmanifest.lua"):
            text = decrypted.decode("utf-8", errors="ignore")
            lines = text.splitlines()

            filtered_lines = [line for line in lines if line.strip() != "dependency '/assetpacks'"]
            header = ["-- Decrypted by https://discord.gg/77PWuTRGJ5" for _ in range(5)]
            new_lines = header + filtered_lines

            content = "\n".join(new_lines).encode("utf-8")

        with open(output_path, "wb") as f:
            f.write(content)

        fxap_path = os.path.join(output_dir, ".fxap")
        if os.path.isfile(fxap_path):
            try:
                os.remove(fxap_path)
            except:
                pass

    def decrypt(self):
        global DECRYPT_FILES_COUNT
        global SKIPPED_FILES_COUNT

        if not self.is_valid():
            # print(f"{Fore.LIGHTRED_EX}[!] Skipping file: {self.fx_file}")
            SKIPPED_FILES_COUNT += 1
            return False

        self.get_key()

        file = None
        with open(self.fx_file, "rb") as f:
            file = f.read()

        iv = file[0x4a:0x4a + 0xc]
        encrypted = file[0x56:]

        cipher = ChaCha20.new(key=bytes(MASTER_KEY), nonce=iv)
        first_round = cipher.decrypt(encrypted)
        real_iv = first_round[:0x5c][-16:][-12:]
        
        header = first_round[:0x5c]
        content = first_round[0x5c:]

        cipher = ChaCha20.new(key=bytes.fromhex(self.resource_key), nonce=real_iv)
        decrypted = cipher.decrypt(content)

        # print(f"{Fore.GREEN}[+] Decrypted: {self.fx_file}")
        DECRYPT_FILES_COUNT += 1

        return decrypted


def extract_archive(archive_path, extract_to):
    """Extract ZIP and other archive formats"""
    try:
        file_ext = os.path.splitext(archive_path)[1].lower()
        
        if file_ext == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return True
        else:
            # For RAR and others, try external tools
            import subprocess
            commands_to_try = [
                ['7z', 'x', f'"{archive_path}"', f'-o"{extract_to}"', '-y'],
                ['winrar', 'x', '-y', archive_path, f'{extract_to}\\'],
                ['unrar', 'x', '-y', archive_path, extract_to]
            ]
            
            for cmd in commands_to_try:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
            
            return False
            
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[!] Error extracting {archive_path}: {e}")
        return False

def process_archive(archive_path, server_key):
    """Process a compressed file: extract, search for .fxap, decrypt"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix='fxap_extract_')
        print(f"{Fore.LIGHTCYAN_EX}[+] Extracting archive: {archive_path}")
        
        if not extract_archive(archive_path, temp_dir):
            print(f"{Fore.LIGHTRED_EX}[!] Failed to extract: {archive_path}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        
        # Search for folders with .fxap more thoroughly
        found_resources = []
        
        print(f"{Fore.LIGHTCYAN_EX}[+] Searching for .fxap files in extracted content...")
        
        for root, dirs, files in os.walk(temp_dir):
            if ".fxap" in files:
                found_resources.append(root)
                print(f"{Fore.LIGHTGREEN_EX}[+] Found .fxap in: {root}")
            
            # Also search in subdirectories that might contain resources
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if os.path.exists(os.path.join(dir_path, ".fxap")):
                    found_resources.append(dir_path)
                    print(f"{Fore.LIGHTGREEN_EX}[+] Found .fxap in subdirectory: {dir_path}")
        
        # Show what was found in the archive
        print(f"{Fore.LIGHTCYAN_EX}[+] Archive contents:")
        for root, dirs, files in os.walk(temp_dir):
            level = root.replace(temp_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:10]:  # Show only first 10 files per folder
                print(f"{subindent}{file}")
            if len(files) > 10:
                print(f"{subindent}... and {len(files) - 10} more files")
        
        if not found_resources:
            print(f"{Fore.LIGHTYELLOW_EX}[-] No .fxap files found in: {archive_path}")
            print(f"{Fore.LIGHTYELLOW_EX}[?] This might not be a FiveM resource archive")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False
        
        # Process each found resource
        success_count = 0
        for resource_dir in found_resources:
            resource_name = os.path.basename(resource_dir)
            print(f"{Fore.LIGHTCYAN_EX}[+] Processing resource: {resource_name}")
            
            fxap_path = os.path.join(resource_dir, ".fxap")
            
            if not os.path.exists(fxap_path):
                print(f"{Fore.LIGHTRED_EX}[!] .fxap file not found at expected path: {fxap_path}")
                continue
                
            files_processed = 0
            for root, dirs, files in os.walk(resource_dir):
                for file in files:
                    if file == ".fxap":
                        continue  # Skip the .fxap file itself
                        
                    file_path = os.path.join(root, file)
                    try:
                        escrow_parser = Escrow(fxap_path, file_path, server_key)
                        des = escrow_parser.decrypt()

                        if des:
                            escrow_parser.save_decrypted(des, resource_dir, resource_name)
                            files_processed += 1
                        else:
                            # If couldn't decrypt, copy the original file
                            with open(file_path, "rb") as f:
                                original_data = f.read()
                            escrow_parser.save_decrypted(original_data, resource_dir, resource_name)
                    except Exception as e:
                        print(f"{Fore.LIGHTYELLOW_EX}[!] Error processing file {file}: {e}")
                        continue
            
            if files_processed > 0:
                success_count += 1
                print(f"{Fore.LIGHTGREEN_EX}[+] Successfully processed {files_processed} files from resource: {resource_name}")
            else:
                print(f"{Fore.LIGHTYELLOW_EX}[-] No files processed from resource: {resource_name}")
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        if success_count > 0:
            print(f"{Fore.LIGHTGREEN_EX}[+] Successfully processed {success_count} resources from archive")
            return True
        else:
            print(f"{Fore.LIGHTYELLOW_EX}[-] No resources were successfully processed from archive")
            return False
        
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[!] Error processing archive {archive_path}: {e}")
        return False

def get_all_keys(server_key):
    g = Grants(server_key)
    g.get_all()

def banner():
    os.system("cls || clear")
    os.system(f'title Escrow MLO Decrypt')
    print(f"""{Fore.LIGHTCYAN_EX}                                            
 _____                          _____         _           
|   __|___ ___ ___ ___ _ _ _   |   __|_ _ ___| |_ ___ ___ 
|   __|_ -|  _|  _| . | | | |  |   __| | |  _| '_| -_|  _|
|_____|___|___|_| |___|_____|  |__|  |___|___|_,_|___|_|  
                                                          
    """)


def main():
    banner()
    parser = argparse.ArgumentParser(
        description="FXAP Decryptor v2 - Now supports ZIP/RAR files! Auto-saves your server key.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-f', '--file', help='Path to the encrypted .sv file to decrypt')
    parser.add_argument('-d', '--dir', help='Path to a directory to decrypt all stream files recursively')
    parser.add_argument('-z', '--zip', help='Path to a ZIP/RAR file to extract and decrypt')
    parser.add_argument('-k', '--server_key', help='Server key used to retrieve new grants (will be saved for future use)')
    parser.add_argument('-s', '--only_keys', action='store_true', help='Only fetch and list all known resource IDs for a given server key')
    parser.add_argument('-r', '--recursive', help='Path to a directory to decrypt all RESOURCES')
    parser.add_argument('--reset-key', action='store_true', help='Reset saved server key')

    args = parser.parse_args()

    # Handle key reset
    if args.reset_key:
        config = load_config()
        config["server_key"] = ""
        save_config(config)
        print(f"{Fore.LIGHTGREEN_EX}[+] Server key reset. You'll need to provide it again next time.")
        return

    # Get server key (from parameter or saved config)
    server_key = get_server_key(args.server_key)
    
    if not server_key and not args.only_keys:
        print(f"{Fore.LIGHTYELLOW_EX}[!] No server key found. Please provide one with -k parameter")
        print(f"{Fore.LIGHTCYAN_EX}[i] Example: python escrow.py -z yourfile.zip -k your_server_key")
        return

    if server_key and args.only_keys:
        get_all_keys(server_key)
        return

    if args.file:
        escrow_parser = Escrow(args.fxap, args.file, server_key)
        des = escrow_parser.decrypt()
        escrow_parser.save_decrypted(des, args.file)
    elif args.zip:
        # NEW FUNCTIONALITY: ZIP/RAR file handling
        if not os.path.isfile(args.zip):
            print(f"{Fore.LIGHTRED_EX}[!] Archive file not found: {args.zip}")
            return
        
        archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
        file_ext = os.path.splitext(args.zip)[1].lower()
        
        if file_ext not in archive_extensions:
            print(f"{Fore.LIGHTYELLOW_EX}[-] Warning: {args.zip} might not be a supported archive format")
        
        success = process_archive(args.zip, server_key)
        if success:
            print(f"{Fore.LIGHTGREEN_EX}[+] Archive processed successfully: {args.zip}")
        else:
            print(f"{Fore.LIGHTRED_EX}[!] Failed to process archive: {args.zip}")
    elif args.dir:
        # IMPROVED: Detect if it's a file or directory
        if os.path.isfile(args.dir):
            # If it's a file, treat it as compressed archive
            archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
            file_ext = os.path.splitext(args.dir)[1].lower()
            
            if file_ext in archive_extensions:
                print(f"{Fore.LIGHTCYAN_EX}[+] Detected archive file, processing: {args.dir}")
                success = process_archive(args.dir, server_key)
                if not success:
                    print(f"{Fore.LIGHTRED_EX}[!] Failed to process archive: {args.dir}")
            else:
                print(f"{Fore.LIGHTRED_EX}[!] File provided but not a supported archive: {args.dir}")
        elif os.path.isdir(args.dir):
            # Normal directory processing
            fxap_path = os.path.join(args.dir, ".fxap")
            resource_name = os.path.basename(os.path.normpath(args.dir))

            for root, dirs, files in os.walk(args.dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    escrow_parser = Escrow(fxap_path, file_path, server_key)
                    des = escrow_parser.decrypt()

                    if des:
                        escrow_parser.save_decrypted(des, args.dir, resource_name)
                    else:
                        with open(file_path, "rb") as f:
                            original_data  = f.read()

                        escrow_parser.save_decrypted(original_data, args.dir, resource_name)

            print(f"{Fore.LIGHTGREEN_EX}[+] Decrypted Asset: {resource_name}")
            print(f"{Fore.LIGHTGREEN_EX}[+] Total files decrypted: {DECRYPT_FILES_COUNT}")
            print(f"{Fore.LIGHTYELLOW_EX}[+] Total files skipped: {SKIPPED_FILES_COUNT}")
        else:
            print(f"{Fore.LIGHTRED_EX}[!] Path not found: {args.dir}")

    else:
        parser.error(
            "You must provide either:\n"
            "  -f/--file to decrypt a single file\n"
            "  -d/--dir to decrypt all files in a directory (or archive file)\n"
            "  -z/--zip to decrypt a ZIP/RAR archive\n"
            "  -k/--server_key with -s/--only_keys to fetch all known decrypt keys.\n\n"
            "Examples:\n"
            "  python escrow.py -d path/to/folder -k your_key\n"
            "  python escrow.py -d path/to/archive.zip -k your_key\n"
            "  python escrow.py -z path/to/archive.rar -k your_key"
        )

    print(Fore.RESET)

if __name__ == "__main__":
    main() 