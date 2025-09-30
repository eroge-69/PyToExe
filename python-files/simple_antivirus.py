#!/usr/bin/env python3
"""
simple_antivirus.py

A lightweight, educational "antivirus-like" scanner in Python.
NOT a replacement for real antivirus software.

Features:
- Scans a directory recursively
- Flags files by suspicious extension
- Calculates MD5 hashes and compares against a small local blacklist
- Optional: invokes Windows Defender quick scan (if running on Windows and Defender is available)
- Writes a simple log file with findings

Usage:
    python simple_antivirus.py --path "C:\Users\Public" --log findings.log

"""

import os
import sys
import hashlib
import argparse
import platform
import subprocess
from datetime import datetime

# === Default configuration ===
DEFAULT_PATH = r"C:\Users\Public" if platform.system() == "Windows" else os.path.expanduser("~")
SUSPICIOUS_EXTENSIONS = {".exe", ".bat", ".vbs", ".js", ".scr", ".ps1"}
# Example known-bad MD5 hashes (EICAR test file + dummy example)
KNOWN_BAD_HASHES = {
    "44d88612fea8a8f36de82e1278abb02f",  # EICAR test file
    "098f6bcd4621d373cade4e832627b4f6"   # "test"
}


def calculate_md5(file_path):
    """Calculate MD5 hash of a file safely and efficiently"""
    try:
        with open(file_path, "rb") as f:
            hasher = hashlib.md5()
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, FileNotFoundError):
        return None
    except Exception:
        return None


def run_windows_defender_quick_scan():
    """Attempt to run a Windows Defender quick scan via PowerShell (only on Windows)."""
    if platform.system() != "Windows":
        return False, "Not running on Windows."
    try:
        # Use PowerShell command to run a quick scan. This requires Defender to be present and permissions.
        cmd = ["powershell", "-NoProfile", "-Command", "Start-MpScan -ScanType QuickScan"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        if proc.returncode == 0:
            return True, out or "Windows Defender quick scan completed."
        else:
            return False, err or f"Exit code {proc.returncode}"
    except FileNotFoundError:
        return False, "PowerShell not found."
    except subprocess.TimeoutExpired:
        return False, "Defender scan timed out."
    except Exception as e:
        return False, str(e)


def scan_directory(path, log_file=None):
    findings = []
    scanned_count = 0
    start_time = datetime.utcnow().isoformat() + "Z"

    for root, _, files in os.walk(path):
        for file in files:
            scanned_count += 1
            file_path = os.path.join(root, file)

            # 1. Check extension
            _, ext = os.path.splitext(file)
            if ext.lower() in SUSPICIOUS_EXTENSIONS:
                msg = f"Suspicious extension: {file_path}"
                findings.append(("suspicious_ext", file_path, msg))

            # 2. Check hash
            md5_hash = calculate_md5(file_path)
            if md5_hash and md5_hash.lower() in KNOWN_BAD_HASHES:
                msg = f"Known-bad hash detected: {md5_hash}"
                findings.append(("malicious_hash", file_path, msg))

    end_time = datetime.utcnow().isoformat() + "Z"

    # Write results to log if requested
    if log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"Scan started: {start_time}\n")
                lf.write(f"Scanned path: {path}\n")
                lf.write(f"Total files scanned: {scanned_count}\n")
                for tag, fpath, message in findings:
                    lf.write(f"[{tag}] {fpath} -- {message}\n")
                lf.write(f"Scan finished: {end_time}\n")
                lf.write("-" * 60 + "\n")
        except Exception as e:
            print(f"Unable to write log file: {e}", file=sys.stderr)

    return {
        "start_time": start_time,
        "end_time": end_time,
        "scanned_count": scanned_count,
        "findings": findings
    }


def main():
    parser = argparse.ArgumentParser(description="Simple Antivirus-like scanner (educational demo).")
    parser.add_argument("--path", "-p", default=DEFAULT_PATH, help="Directory path to scan")
    parser.add_argument("--log", "-l", default=None, help="Optional log file to append results to")
    parser.add_argument("--no-defender", action="store_true", help="Do not attempt to run Windows Defender scan")
    args = parser.parse_args()

    path = args.path

    if not os.path.exists(path):
        print(f"Path does not exist: {path}", file=sys.stderr)
        sys.exit(2)

    print("=== Simple Antivirus Scan ===")
    print(f"Scan path: {path}")
    print(f"Time (UTC): {datetime.utcnow().isoformat()}Z")
    if platform.system() == "Windows" and not args.no_defender:
        print("\n[+] Attempting to run Windows Defender quick scan (if available)...")
        ok, msg = run_windows_defender_quick_scan()
        print("[Defender] " + (msg or "No output"))
        print()

    result = scan_directory(path, log_file=args.log)

    print(f"Scanned files: {result['scanned_count']}")
    if result["findings"]:
        print("\nFindings:")
        for tag, fpath, message in result["findings"]:
            print(f"- [{tag}] {fpath} -- {message}")
    else:
        print("\nNo findings detected.")

    print("\nScan complete.")

if __name__ == "__main__":
    main()
