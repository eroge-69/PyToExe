import winreg
import sys
import glob
import xmltodict

if len(sys.argv) != 2:
    print(f"[-] usage: {sys.argv[0]} [path]", file = sys.stderr)
    sys.exit(1)

lib_root = sys.argv[1]
if lib_root == "[gui]":
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    print("[.] please select the directory of the target library to continue")
    print("[.] the directory should have at least one .nicnt file in it")

    lib_root = filedialog.askdirectory(mustexist = True, title = "Select the directory of the target library")
    if lib_root == "":
        print(f"[-] cancelled")
        sys.exit()

try:
    lib_nicnt = glob.glob(f"{lib_root}/*.nicnt")[0]
except:
    print(f"[-] error: no NICNT files found in {lib_root}", file = sys.stderr)
    sys.exit(1)

nicnt = open(lib_nicnt, "rb").read()

# read the version, UTF-16, ends with NULL, at most 16 bytes
version = nicnt[0x42:0x42 + 16][::2]
version = version[:version.index(0x00)].decode()

if version.count(".") == 1:
    version += ".0"

# read the manifest block; starts at 0x100, and ends with NULL
manifest = xmltodict.parse(nicnt[0x100:nicnt.index(0x00, 0x100)].decode())
product = manifest["ProductHints"]["Product"]

regkey = product["RegKey"]

print()
print("[.] Library information:")
print(f"[.]    Name: {product["Name"]}")
print(f"[.]    Company: {product["Company"]}")
print(f"[.]    Registry key: {regkey}")
print(f"[.]    Version: {version}")
print()

key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, fr"SOFTWARE\Native Instruments\{regkey}")
winreg.SetValueEx(key, "ContentDir", 0, winreg.REG_SZ, lib_root.replace("/", "\\"))
winreg.SetValueEx(key, "ContentVersion", 0, winreg.REG_SZ, version)
winreg.SetValueEx(key, "HU", 0, winreg.REG_SZ, product["ProductSpecific"]["HU"])
winreg.SetValueEx(key, "JDX", 0, winreg.REG_SZ, product["ProductSpecific"]["JDX"])
winreg.SetValueEx(key, "Visibility", 0, winreg.REG_DWORD, 3)

winreg.CloseKey(key)

print("[+] Library added!")
