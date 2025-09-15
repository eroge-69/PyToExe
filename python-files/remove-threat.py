#!/usr/bin/env python3
"""
PoC remove-threat active-response script for Wazuh.
Behavior:
 - Accepts arguments passed by Wazuh active-response:
    1) action (e.g. 'remove')
    2) file_path (path to suspect file)
    3) agent_id (optional)
 - Validations:
    - Only allow file_path under configured allowed base directories.
    - Do NOT follow symlinks outside allowed dirs.
 - Action:
    - Move the file to a quarantine directory (creates it if needed).
    - Write an entry to a log file.
    - Return exit code 0 on success, non-zero on error.
"""

import os
import sys
import shutil
import hashlib
import time
import logging

# === CONFIGURE HERE ===
# Directories that are allowed to be processed (base directories)
ALLOWED_BASEDIRS = [
    # Windows example:
    r"C:\Users\Public\Downloads",
    r"C:\Users\Public",
    # Linux example:
    "/tmp",
    "/home",
]

# Quarantine directories per OS (ensure agent can write here)
QUARANTINE_DIRS = [
    os.path.join(os.path.dirname(__file__), "..", "quarantine"),  # relative to agent active-response dir
    "/var/ossec/quarantine",  # linux alt
    r"C:\Program Files (x86)\ossec-agent\quarantine"  # windows alt
]

# Log file path (will try options)
LOG_FILES = [
    os.path.join(os.path.dirname(__file__), "..", "remove-threat.log"),
    "/var/ossec/logs/remove-threat.log",
    r"C:\Program Files (x86)\ossec-agent\remove-threat.log"
]

# Maximum file size to move (bytes). Prevents trying to move huge files accidentally.
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

# ======================

def resolve_quarantine_dir():
    for d in QUARANTINE_DIRS:
        if not d:
            continue
        # Ensure path is normalized
        d = os.path.abspath(os.path.expanduser(d))
        try:
            os.makedirs(d, exist_ok=True)
            # Try writing a tiny temp file to check permissions
            test_path = os.path.join(d, ".quarantine_test")
            with open(test_path, "w") as f:
                f.write("ok")
            os.remove(test_path)
            return d
        except Exception:
            continue
    raise RuntimeError("No writable quarantine directory available. Check configuration and permissions.")

def resolve_log_file():
    for p in LOG_FILES:
        if not p:
            continue
        p = os.path.abspath(os.path.expanduser(p))
        d = os.path.dirname(p)
        try:
            os.makedirs(d, exist_ok=True)
            # Setup logger to this file later
            return p
        except Exception:
            continue
    # fallback to current dir
    return os.path.join(os.getcwd(), "remove-threat.log")

def setup_logger(log_path):
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    # also log to stderr for immediate visibility
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

def is_under_allowed_bases(path):
    # Resolve realpath (no symlink escape)
    try:
        real_path = os.path.realpath(path)
    except Exception:
        return False
    for base in ALLOWED_BASEDIRS:
        base_real = os.path.realpath(base)
        # normalize trailing sep
        if not base_real.endswith(os.sep):
            base_real = base_real + os.sep
        if real_path.startswith(base_real) or real_path == base_real.rstrip(os.sep):
            return True
    return False

def sha256_of_file(path, block_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()

def safe_move_to_quarantine(src_path, quarantine_dir):
    # Build destination with timestamp and hash to avoid name collisions
    fname = os.path.basename(src_path)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    try:
        filehash = sha256_of_file(src_path)
    except Exception:
        filehash = "unknownhash"
    dest_fname = f"{timestamp}_{filehash[:12]}_{fname}"
    dest_path = os.path.join(quarantine_dir, dest_fname)
    shutil.move(src_path, dest_path)
    return dest_path, filehash

def main(argv):
    if len(argv) < 2:
        print("Usage: remove-threat.py <action> <file_path> [agent_id]")
        return 2

    action = argv[0].lower()
    file_path = argv[1]
    agent_id = argv[2] if len(argv) >= 3 else "unknown"

    log_path = resolve_log_file()
    setup_logger(log_path)
    logging.info("remove-threat called: action=%s file=%s agent=%s", action, file_path, agent_id)

    if action not in ("remove", "quarantine"):
        logging.error("Unsupported action: %s", action)
        return 3

    # Normalize path
    file_path = os.path.abspath(os.path.expanduser(file_path))

    if not os.path.exists(file_path):
        logging.error("Target file does not exist: %s", file_path)
        return 4

    # Prevent directories being passed accidentally
    if os.path.isdir(file_path):
        logging.error("Target is a directory; refusing to process: %s", file_path)
        return 5

    # Size check
    try:
        size = os.path.getsize(file_path)
        if size > MAX_FILE_SIZE:
            logging.error("File too large (%d bytes); refusing to move", size)
            return 6
    except Exception as e:
        logging.warning("Could not determine file size: %s", e)

    # Validate allowed base directories
    if not is_under_allowed_bases(file_path):
        logging.error("File path not under allowed base directories. Refusing to process: %s", file_path)
        return 7

    # Resolve quarantine dir
    try:
        quarantine_dir = resolve_quarantine_dir()
    except Exception as e:
        logging.exception("Failed to prepare quarantine directory: %s", e)
        return 8

    # Move file to quarantine
    try:
        dest_path, fhash = safe_move_to_quarantine(file_path, quarantine_dir)
        logging.info("File moved to quarantine: %s (sha256=%s)", dest_path, fhash)
        # Optionally: keep a short record file for forensics
        record = {
            "original_path": file_path,
            "quarantine_path": dest_path,
            "sha256": fhash,
            "agent_id": agent_id,
            "action": action,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        record_path = os.path.join(quarantine_dir, f"record_{time.strftime('%Y%m%d%H%M%S')}_{fhash[:8]}.json")
        try:
            import json
            with open(record_path, "w") as rf:
                json.dump(record, rf)
        except Exception:
            logging.warning("Failed to write record file forensics.")
        return 0
    except Exception as e:
        logging.exception("Failed to move file to quarantine: %s", e)
        return 9

if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
