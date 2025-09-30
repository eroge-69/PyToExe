#!/usr/bin/env python3
"""
Test script for application opening functionality
"""

import os
import subprocess

def find_chrome_path():
    """Find Chrome executable path on Windows."""
    # Common Chrome installation paths on Windows
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"),
        os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\chrome.exe"),
        "chrome.exe"  # Try default PATH
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return path
    return None

def test_open_chrome():
    """Test opening Chrome"""
    print("Testing Chrome opening...")
    chrome_path = find_chrome_path()
    if chrome_path:
        try:
            subprocess.Popen([chrome_path])
            print("✓ Chrome opened successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to open Chrome: {e}")
            return False
    else:
        print("✗ Chrome not found")
        return False

def test_open_notepad():
    """Test opening Notepad"""
    print("Testing Notepad opening...")
    try:
        subprocess.Popen(["notepad.exe"])
        print("✓ Notepad opened successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to open Notepad: {e}")
        return False

if __name__ == "__main__":
    test_open_chrome()
    test_open_notepad()
    print("\nApplication opening tests completed.")