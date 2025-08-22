# loader.py — load the decoded DLL and call hack_security(0x2008)
import time


import ctypes
import os
import sys

dll_name = "decoded_BOMB.dll"
dll_path = r"C:\ReversingCTF\decoded_BOMB.dll"


if not os.path.exists(dll_path):
    print(f"ERROR: {dll_name} not found in {os.getcwd()}")
    sys.exit(1)

# Use WinDLL (the DLL seems to be built with stdcall exports) — this worked for you earlier
try:
    mydll = ctypes.WinDLL(dll_path)
except OSError as e:
    print("Load error:", e)
    sys.exit(1)
time.sleep(20)   # pause for 10 seconds
# Get the export
try:
    hack = mydll.hack_security
except AttributeError:
    print("Export 'hack_security' not found")
    sys.exit(1)
time.sleep(20)   # pause for 10 seconds
# Set argtypes/restype
hack.argtypes = (ctypes.c_uint32,)   # one 32-bit integer parameter
hack.restype  = ctypes.c_void_p      # returns nothing meaningful for us

print("[+] Calling hack_security(0x2008) ...")
# Call with the magic value 0x2008 (the binary checks for this)
hack(0x2008)

print("[+] hack_security returned (if the DLL didn't call ExitProcess).")
