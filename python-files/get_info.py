import os
import subprocess
import sys
from datetime import datetime

def run_cmd(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        return result.decode(errors='ignore').strip()
    except Exception:
        return "Not found or not retrievable."

def get_windows_info():
    info = []
    output = run_cmd('systeminfo')
    if output != "Not found or not retrievable.":
        for line in output.splitlines():
            if line.startswith("OS Name") or line.startswith("OS Version") or line.startswith("System Type"):
                info.append(line)
    return info if info else ["Windows Info: Not found"]

def get_serial_number():
    serial = run_cmd('wmic bios get serialnumber')
    lines = [l.strip() for l in serial.splitlines() if l.strip() and "SerialNumber" not in l]
    return lines[0] if lines else "UnknownServiceTag"

def get_serial_number_line():
    serial = run_cmd('wmic bios get serialnumber')
    lines = [l.strip() for l in serial.splitlines() if l.strip() and "SerialNumber" not in l]
    return ["Serial Number: " + lines[0]] if lines else ["Serial Number: Not found"]

def get_windows_product_key():
    try:
        import winreg
        reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, reg_path)
        value, _ = winreg.QueryValueEx(key, "DigitalProductId")
        winreg.CloseKey(key)
        key_str = decode_product_key(value)
        if key_str:
            return ["Windows Product Key: " + key_str]
    except Exception:
        pass
    return ["Windows Product Key: Not found or not retrievable."]

def decode_product_key(digitalProductId):
    keyOffset = 52
    isWin8 = (digitalProductId[66] // 6) & 1
    key = ""
    digits = "BCDFGHJKMPQRTVWXY2346789"
    if isWin8:
        return "OEM Key not decodable"
    else:
        hexPid = list(digitalProductId[keyOffset:keyOffset+15])
        decoded = []
        for i in range(25):
            curr = 0
            for j in range(14, -1, -1):
                curr = curr * 256
                curr += hexPid[j]
                hexPid[j] = curr // 24
                curr = curr % 24
            decoded.append(digits[curr])
        key = "".join([decoded[i] for i in range(24, -1, -1)])
        for i in range(5, 25, 6):
            key = key[:i] + "-" + key[i:]
        return key

def get_office_partial_keys():
    result = []
    wmic_cmd = 'wmic path SoftwareLicensingProduct where "Name like \'Office%%\' and PartialProductKey is not null" get Name,PartialProductKey /format:list'
    output = run_cmd(wmic_cmd)
    products = [l for l in output.split('\n\n') if l.strip()]
    if not products:
        return ["Office Product Key: Not found or not retrievable."]
    for product in products:
        lines = [line for line in product.strip().splitlines() if line]
        name, key = "", ""
        for line in lines:
            if line.startswith("Name="):
                name = line.split("=", 1)[1]
            elif line.startswith("PartialProductKey="):
                key = line.split("=", 1)[1]
        if name and key:
            result.append(f" - {name}: {key}")
    return result if result else ["Office Product Key: Not found or not retrievable."]

def main():
    output = []
    output.append("="*45)
    output.append("        SYSTEM INFORMATION REPORT")
    output.append("="*45 + "\n")

    output.append("[Windows Information]")
    output.extend(get_windows_info())
    output.append("")

    output.append("[BIOS Serial Number / Service Tag]")
    serial_number = get_serial_number()
    output.extend(["Serial Number: " + serial_number])
    output.append("")

    output.append("[Windows Product Key]")
    output.extend(get_windows_product_key())
    output.append("")

    output.append("[Office Partial Product Key(s)]")
    output.extend(get_office_partial_keys())
    output.append("")

    output.append("="*45)
    output.append(f"Report generated on: {datetime.now()}")
    output.append("="*45)

    # Clean up serial for use as filename
    safe_serial = ''.join(c for c in serial_number if c.isalnum())
    if not safe_serial:
        safe_serial = "UnknownServiceTag"
    filename = f"{safe_serial}.txt"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    outpath = os.path.join(script_dir, filename)
    with open(outpath, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print(f"Done! Check {filename} in this folder.")

if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script is for Windows only.")
        sys.exit(1)
    main()