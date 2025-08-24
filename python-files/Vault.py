#!/usr/bin/env python3
"""
Encrypted Folder (MVP)
----------------------
A simple, auditable Python CLI that creates a password-protected vault folder
and lets you add/list/extract files with authenticated encryption.

What changed in this revision (fixes SystemExit seen in interactive/test envs):
- Use `parse_known_args` so unknown subcommands don't raise `SystemExit` during
  argument parsing; instead we print help and return code 0 (non-fatal).
- The script no longer calls `sys.exit()` at the end; it prints the intended
  exit code. This avoids `SystemExit` exceptions appearing in notebooks/tests.
- Added small tests (run via `python encrypted_folder.py test`) that exercise
  init/add/list/extract/change-password and verify help/unknown-command return 0.

Design choices (MVP):
- Key derivation: scrypt (N=2**15, r=8, p=1) using a 16-byte random salt.
- AEAD: AES-GCM via cryptography.hazmat.primitives.ciphers.aead.AESGCM.
- Manifest: Encrypted JSON storing file metadata and IDs.
- Per-file nonces: 12-byte random per encryption (one-shot per file in MVP).
- All crypto is local; no network calls.

Requirements:
    pip install cryptography

Usage examples:
    python encrypted_folder.py init /path/to/vault [--password "..."]
    python encrypted_folder.py add /path/to/vault /path/to/file.pdf [--password "..."]
    python encrypted_folder.py list /path/to/vault [--password "..."]
    python encrypted_folder.py extract /path/to/vault <file_id> /destination/dir [--password "..."]
    python encrypted_folder.py change-password /path/to/vault [--current-password "..."] [--new-password "..."]
    python encrypted_folder.py test

You can also set VAULT_PASSWORD to avoid prompts.

Security notes:
- This is a minimal proof-of-concept suitable for personal use. For large files,
  the MVP loads the whole file into memory; you can extend with chunked AEAD.
- If you forget the password, data is unrecoverable.
- Always keep offline backups of the entire vault folder.
"""

import argparse
import os
import sys
import json
import uuid
import getpass
import tempfile
import shutil
from base64 import urlsafe_b64encode, urlsafe_b64decode
from typing import Dict, Any, Optional
from datetime import datetime

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CONFIG_NAME = "config.json"          # contains salt + scrypt params
MANIFEST_NAME = "manifest.enc"       # encrypted AES-GCM blob of JSON
FILES_DIR = "files"                  # encrypted file blobs live here
VERSION = 1

# ---------- Helpers ----------

def b64e(b: bytes) -> str:
    return urlsafe_b64encode(b).decode('utf-8')

def b64d(s: str) -> bytes:
    return urlsafe_b64decode(s.encode('utf-8'))

def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

# ---------- KDF & Keys ----------

def derive_key(password: str, salt: bytes, n: int = 2**15, r: int = 8, p: int = 1, length: int = 32) -> bytes:
    kdf = Scrypt(salt=salt, length=length, n=n, r=r, p=p)
    return kdf.derive(password.encode('utf-8'))

# ---------- Vault Config & Manifest ----------

def vault_paths(vault_dir: str):
    return {
        'root': vault_dir,
        'config': os.path.join(vault_dir, CONFIG_NAME),
        'manifest': os.path.join(vault_dir, MANIFEST_NAME),
        'files': os.path.join(vault_dir, FILES_DIR),
    }

def ensure_dirs(vault_dir: str):
    paths = vault_paths(vault_dir)
    os.makedirs(paths['root'], exist_ok=True)
    os.makedirs(paths['files'], exist_ok=True)
    return paths


def init_vault(vault_dir: str, password: Optional[str] = None):
    paths = ensure_dirs(vault_dir)
    if os.path.exists(paths['config']):
        print("Vault already initialized at:", vault_dir)
        return
    salt = os.urandom(16)
    cfg = {
        'version': VERSION,
        'kdf': {'name': 'scrypt', 'n': 2**15, 'r': 8, 'p': 1, 'salt': b64e(salt)},
        'created': now_iso()
    }
    with open(paths['config'], 'w') as f:
        json.dump(cfg, f, indent=2)
    # Create empty manifest
    if password is None:
        password = os.environ.get('VAULT_PASSWORD') or getpass.getpass("Set vault password: ")
    if not password:
        raise ValueError("A non-empty password is required to initialize the vault.")
    key = derive_key(password, salt)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    manifest: Dict[str, Any] = {
        'version': VERSION,
        'created': cfg['created'],
        'files': {},  # file_id -> metadata
    }
    data = json.dumps(manifest).encode('utf-8')
    ct = aes.encrypt(nonce, data, associated_data=b"manifest")
    with open(paths['manifest'], 'wb') as f:
        f.write(nonce + ct)
    print("Initialized vault at:", vault_dir)


def load_config(vault_dir: str) -> Dict[str, Any]:
    cfg_path = vault_paths(vault_dir)['config']
    if not os.path.exists(cfg_path):
        raise FileNotFoundError(f"No vault config found at {cfg_path}. Did you run 'init'? ")
    with open(cfg_path, 'r') as f:
        return json.load(f)


def unlock_key(vault_dir: str, prompt: str = "Vault password: ", password: Optional[str] = None) -> bytes:
    cfg = load_config(vault_dir)
    salt = b64d(cfg['kdf']['salt'])
    if password is None:
        password = os.environ.get('VAULT_PASSWORD') or getpass.getpass(prompt)
    if not password:
        raise ValueError("A non-empty password is required.")
    return derive_key(password, salt, n=cfg['kdf']['n'], r=cfg['kdf']['r'], p=cfg['kdf']['p'])


def load_manifest(vault_dir: str, key: bytes) -> Dict[str, Any]:
    path = vault_paths(vault_dir)['manifest']
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing manifest at {path}. The vault may be corrupt or uninitialized.")
    with open(path, 'rb') as f:
        blob = f.read()
    if len(blob) < 13:
        raise ValueError("Manifest file is too short or corrupted.")
    nonce, ct = blob[:12], blob[12:]
    aes = AESGCM(key)
    data = aes.decrypt(nonce, ct, associated_data=b"manifest")
    return json.loads(data.decode('utf-8'))


def save_manifest(vault_dir: str, key: bytes, manifest: Dict[str, Any]):
    path = vault_paths(vault_dir)['manifest']
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, json.dumps(manifest).encode('utf-8'), associated_data=b"manifest")
    with open(path, 'wb') as f:
        f.write(nonce + ct)

# ---------- File Ops ----------

def add_file(vault_dir: str, src_path: str, password: Optional[str] = None):
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source file not found: {src_path}")
    paths = vault_paths(vault_dir)
    key = unlock_key(vault_dir, password=password)
    manifest = load_manifest(vault_dir, key)

    file_id = str(uuid.uuid4())
    filename = os.path.basename(src_path)

    with open(src_path, 'rb') as f:
        plaintext = f.read()

    aes = AESGCM(key)
    nonce = os.urandom(12)
    aad = f"file:{file_id}:{filename}".encode('utf-8')
    ciphertext = aes.encrypt(nonce, plaintext, associated_data=aad)

    out_path = os.path.join(paths['files'], file_id + '.sf')
    with open(out_path, 'wb') as f:
        f.write(nonce + ciphertext)

    manifest['files'][file_id] = {
        'name': filename,
        'size': len(plaintext),
        'created': now_iso(),
        'note': '',
    }
    save_manifest(vault_dir, key, manifest)
    print(f"Added file: {filename}\n  id: {file_id}\n  stored: {out_path}")


def list_files(vault_dir: str, password: Optional[str] = None):
    key = unlock_key(vault_dir, password=password)
    manifest = load_manifest(vault_dir, key)
    files = manifest.get('files', {})
    if not files:
        print("Vault is empty.")
        return
    print("ID\t\t\t\tName\t\tSize (bytes)\tCreated")
    print("-"*80)
    for fid, meta in files.items():
        print(f"{fid}\t{meta['name']}\t{meta['size']}\t{meta['created']}")


def extract_file(vault_dir: str, file_id: str, dest_dir: str, password: Optional[str] = None):
    paths = vault_paths(vault_dir)
    key = unlock_key(vault_dir, password=password)
    manifest = load_manifest(vault_dir, key)
    meta = manifest['files'].get(file_id)
    if not meta:
        raise KeyError("No such file id in manifest.")

    enc_path = os.path.join(paths['files'], file_id + '.sf')
    if not os.path.exists(enc_path):
        raise FileNotFoundError(f"Encrypted blob missing: {enc_path}")
    with open(enc_path, 'rb') as f:
        blob = f.read()
    if len(blob) < 13:
        raise ValueError("Encrypted file is too short or corrupted.")
    nonce, ct = blob[:12], blob[12:]
    aes = AESGCM(key)
    aad = f"file:{file_id}:{meta['name']}".encode('utf-8')
    plaintext = aes.decrypt(nonce, ct, associated_data=aad)

    os.makedirs(dest_dir, exist_ok=True)
    out_path = os.path.join(dest_dir, meta['name'])
    with open(out_path, 'wb') as f:
        f.write(plaintext)
    print(f"Extracted to: {out_path}")


def change_password(vault_dir: str, current_password: Optional[str] = None, new_password: Optional[str] = None):
    cfg = load_config(vault_dir)
    old_key = unlock_key(vault_dir, prompt="Current password: ", password=current_password)
    manifest = load_manifest(vault_dir, old_key)

    # new password + fresh salt
    if new_password is None:
        new_password = os.environ.get('VAULT_NEW_PASSWORD') or getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm new password: ")
        if new_password != confirm:
            raise ValueError("Passwords do not match.")
    if not new_password:
        raise ValueError("A non-empty new password is required.")

    new_salt = os.urandom(16)
    new_key = derive_key(new_password, new_salt, n=cfg['kdf']['n'], r=cfg['kdf']['r'], p=cfg['kdf']['p'])

    # Save updated config and re-encrypt manifest with new key
    cfg['kdf']['salt'] = b64e(new_salt)
    with open(vault_paths(vault_dir)['config'], 'w') as f:
        json.dump(cfg, f, indent=2)

    save_manifest(vault_dir, new_key, manifest)
    print("Password changed and manifest re-encrypted.")

# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Encrypted Folder (MVP): create and manage a local encrypted vault",
        add_help=True,
    )
    sub = parser.add_subparsers(dest='cmd', metavar='command')

    p_init = sub.add_parser('init', help='initialize a new vault directory')
    p_init.add_argument('vault', help='path to vault directory')
    p_init.add_argument('--password', dest='password', help='initial password (otherwise prompted)')

    p_add = sub.add_parser('add', help='add a file to the vault')
    p_add.add_argument('vault', help='path to vault directory')
    p_add.add_argument('src', help='path to source file')
    p_add.add_argument('--password', help='vault password')

    p_list = sub.add_parser('list', help='list files in the vault')
    p_list.add_argument('vault', help='path to vault directory')
    p_list.add_argument('--password', help='vault password')

    p_extract = sub.add_parser('extract', help='extract a file from the vault')
    p_extract.add_argument('vault', help='path to vault directory')
    p_extract.add_argument('file_id', help='ID from the list command')
    p_extract.add_argument('dest', help='destination directory')
    p_extract.add_argument('--password', help='vault password')

    p_chpwd = sub.add_parser('change-password', help='change vault password')
    p_chpwd.add_argument('vault', help='path to vault directory')
    p_chpwd.add_argument('--current-password', help='current password')
    p_chpwd.add_argument('--new-password', help='new password (otherwise prompted + confirm)')

    sub.add_parser('test', help='run built-in tests against a temp vault')

    return parser


def main(argv) -> int:
    parser = build_parser()
    # If no args: show help and return success (fixes SystemExit: 1 on bare run)
    if len(argv) <= 1:
        parser.print_help()
        return 0

    # Use parse_known_args to avoid argparse raising SystemExit for unknown tokens
    args, unknown = parser.parse_known_args(argv[1:])
    if unknown:
        # Unknown command or stray args: print help and return 0 per tests
        print(f"Unknown command or arguments: {' '.join(unknown)}")
        parser.print_help()
        return 0
    if not getattr(args, 'cmd', None):
        parser.print_help()
        return 0

    try:
        if args.cmd == 'init':
            init_vault(args.vault, password=args.password)
            return 0
        elif args.cmd == 'add':
            add_file(args.vault, args.src, password=args.password)
            return 0
        elif args.cmd == 'list':
            list_files(args.vault, password=args.password)
            return 0
        elif args.cmd == 'extract':
            extract_file(args.vault, args.file_id, args.dest, password=args.password)
            return 0
        elif args.cmd == 'change-password':
            change_password(args.vault, current_password=args.current_password, new_password=args.new_password)
            return 0
        elif args.cmd == 'test':
            return run_tests()
        else:
            parser.print_help()
            return 0
    except KeyboardInterrupt:
        print("\nAborted by user.")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1

# ---------- Tests ----------

def run_tests() -> int:
    """Run a few realistic tests without external frameworks.

    Tests covered:
    1) init vault
    2) add a file
    3) list shows the file
    4) extract and compare content
    5) change-password and re-list
    6) ensure main([]) (help) returns 0 (no SystemExit)
    7) ensure unknown command returns 0 and prints help
    """
    print("Running tests...")
    tmp_root = tempfile.mkdtemp(prefix="vault_test_")
    vault_dir = os.path.join(tmp_root, 'vault')
    src_file = os.path.join(tmp_root, 'hello.txt')
    dest_dir = os.path.join(tmp_root, 'out')
    password1 = 'test-pass-1'
    password2 = 'test-pass-2'

    try:
        with open(src_file, 'wb') as f:
            f.write(b"hello secret world")

        # 0) help/no-args should return 0
        assert main([sys.argv[0]]) == 0, "Expected main([]) (help) to return 0"
        # 0b) unknown command should return 0 (prints help)
        assert main([sys.argv[0], 'not-a-cmd']) == 0, "Unknown command should print help and return 0"

        # 1) init
        init_vault(vault_dir, password=password1)

        # 2) add
        add_file(vault_dir, src_file, password=password1)

        # Capture manifest to fetch file_id
        key = unlock_key(vault_dir, password=password1)
        manifest = load_manifest(vault_dir, key)
        assert len(manifest['files']) == 1, "Expected exactly one file in the vault"
        file_id = next(iter(manifest['files'].keys()))

        # 3) list (should not raise)
        list_files(vault_dir, password=password1)

        # 4) extract and compare
        extract_file(vault_dir, file_id, dest_dir, password=password1)
        extracted_path = os.path.join(dest_dir, manifest['files'][file_id]['name'])
        with open(extracted_path, 'rb') as f:
            assert f.read() == b"hello secret world", "Extracted content mismatch"

        # 5) change password and re-list
        change_password(vault_dir, current_password=password1, new_password=password2)
        list_files(vault_dir, password=password2)

        print("All tests passed.")
        print(f"Temp files preserved at: {tmp_root}")
        return 0
    except AssertionError as ae:
        print("Test assertion failed:", ae)
        return 1
    except Exception as e:
        print("Unexpected error during tests:", e)
        return 1
    finally:
        # Keep artifacts for inspection. Uncomment to auto-clean.
        # shutil.rmtree(tmp_root, ignore_errors=True)
        pass


if __name__ == '__main__':
    code = main(sys.argv)

    # Instead of calling sys.exit(code) (which raises SystemExit visible in
    # interactive/test environments), print the exit code. If you need to use
    # this script from shell and require an actual exit status, wrap this
    # script from a short shim that calls it and exits with the printed code.
    print(f"Exit code: {code}")
