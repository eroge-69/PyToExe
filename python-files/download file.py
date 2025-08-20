#!/usr/bin/env python3
import argparse, os, sys, getpass, json, time, pathlib, secrets
from typing import List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import constant_time
from cryptography.hazmat.backends import default_backend

MAGIC = b"SAFEENC1"  # file format tag
EXT = ".enc"
DEFAULT_EXTS = {".txt",".md",".docx",".xlsx",".pptx",".pdf",".jpg",".jpeg",".png",".csv",".json"}

def derive_key(password: bytes, salt: bytes) -> bytes:
    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1, backend=default_backend())
    return kdf.derive(password)

def encrypt_file(path: pathlib.Path, password: bytes, keep_original: bool, dry_run: bool=False) -> None:
    data = path.read_bytes()
    salt = secrets.token_bytes(16)
    key = derive_key(password, salt)
    aes = AESGCM(key)
    nonce = secrets.token_bytes(12)
    # store some metadata for convenience (original name, mtime)
    meta = {
        "orig_name": path.name,
        "mtime": int(path.stat().st_mtime),
        "size": len(data),
        "alg": "AES-256-GCM",
        "kdf": "scrypt(n=32768,r=8,p=1,salt=hex)"
    }
    aad = json.dumps(meta, separators=(",",":")).encode("utf-8")
    ct = aes.encrypt(nonce, data, aad)
    out = path.with_suffix(path.suffix + EXT)
    blob = MAGIC + salt + nonce + len(aad).to_bytes(4,"big") + aad + ct
    if dry_run:
        print(f"[DRY-RUN] would write {out} ({len(blob)} bytes) and keep_original={keep_original}")
        return
    out.write_bytes(blob)
    # sync file permissions and times
    try: os.chmod(out, path.stat().st_mode)
    except Exception: pass
    if not keep_original:
        # extra safety: overwrite with zeros of same length before unlink (optional, best-effort)
        try:
            with open(path, "r+b", buffering=0) as f:
                f.write(b"\x00" * len(data))
                f.flush()
                os.fsync(f.fileno())
        except Exception:
            pass
        path.unlink(missing_ok=False)

def should_encrypt(path: pathlib.Path, allowed_exts: set) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    if path.suffix.lower() not in allowed_exts:
        return False
    if path.name.endswith(EXT):  # already encrypted
        return False
    return True

def walk_paths(root: pathlib.Path, allowed_exts: set, recursive: bool) -> List[pathlib.Path]:
    files = []
    if recursive:
        for p in root.rglob("*"):
            if should_encrypt(p, allowed_exts):
                files.append(p)
    else:
        for p in root.iterdir():
            if should_encrypt(p, allowed_exts):
                files.append(p)
    return files

def main():
    ap = argparse.ArgumentParser(description="Encrypt files in a chosen folder (opt-in, local, safe).")
    ap.add_argument("folder", type=pathlib.Path, help="Folder to encrypt")
    ap.add_argument("--ext", action="append", default=[], help="File extension to include (e.g., --ext .pdf). Can repeat.")
    ap.add_argument("--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument("--keep-originals", action="store_true", help="Keep originals (default).")
    ap.add_argument("--delete-originals", action="store_true", help="Delete originals after encrypting (requires --confirm-delete).")
    ap.add_argument("--confirm-delete", action="store_true", help="Required with --delete-originals to avoid mistakes.")
    ap.add_argument("--dry-run", action="store_true", help="Show what would happen without writing anything.")
    args = ap.parse_args()

    if not args.folder.exists() or not args.folder.is_dir():
        print("Folder does not exist or is not a directory.", file=sys.stderr)
        sys.exit(2)

    allow = set(e.lower() for e in (args.ext or DEFAULT_EXTS))
    delete = args.delete_originals
    keep = True
    if delete:
        if not args.confirm_delete:
            print("Refusing to delete originals without --confirm-delete.", file=sys.stderr)
            sys.exit(3)
        keep = False
    else:
        keep = True  # default safest behavior

    password1 = getpass.getpass("Enter encryption password: ").encode("utf-8")
    password2 = getpass.getpass("Re-enter password: ").encode("utf-8")
    if not constant_time.bytes_eq(password1, password2):
        print("Passwords do not match.", file=sys.stderr)
        sys.exit(4)

    files = walk_paths(args.folder, allow, args.recursive)
    if not files:
        print("No matching files found.")
        return

    start = time.time()
    for p in files:
        try:
            encrypt_file(p, password1, keep_original=keep, dry_run=args.dry_run)
            print(f"Encrypted: {p}")
        except Exception as e:
            print(f"Failed: {p} -> {e}", file=sys.stderr)
    dur = time.time() - start
    print(f"Done. {len(files)} file(s) processed in {dur:.2f}s.")
    if not args.dry_run:
        readme = args.folder / "HOW_TO_DECRYPT.txt"
        if not readme.exists():
            readme.write_text(
"""How to decrypt your files (legitimate local encryption utility)
1) Run the companion script: decrypt_folder.py
2) Provide the same password you used for encryption.
3) Encrypted files use the .enc suffix alongside the original (unless you chose to delete originals).
4) No data leaves this machine; there is no remote server or payment involved.

If you forget your password, the data cannot be recovered. Store it safely."""
            )

if __name__ == "__main__":
    main()
