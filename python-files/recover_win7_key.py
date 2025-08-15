import winreg as wreg
import os

def decode_key(digital_product_id):
    key_offset = 52
    digits = "BCDFGHJKMPQRTVWXY2346789"
    decoded_chars = []
    pid = list(digital_product_id)
    for i in range(25):
        current = 0
        for j in range(14, -1, -1):
            current = current * 256 ^ pid[j + key_offset]
            pid[j + key_offset] = current // 24
            current %= 24
        decoded_chars.insert(0, digits[current])
    for i in range(5, len(decoded_chars), 6):
        decoded_chars.insert(i, "-")
    return "".join(decoded_chars)

hive_path = r"C:\Windows.old\Windows\System32\config\SOFTWARE"
if not os.path.exists(hive_path):
    print("SOFTWARE hive not found!")
    os.system("pause")
    exit()

try:
    wreg.LoadKey(wreg.HKEY_LOCAL_MACHINE, "OLD_SOFTWARE", hive_path)
    key = wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE, r"OLD_SOFTWARE\Microsoft\Windows NT\CurrentVersion")
    digital_product_id, _ = wreg.QueryValueEx(key, "DigitalProductId")
    print("Recovered Windows 7 Product Key:\n")
    print(decode_key(digital_product_id))
finally:
    try:
        wreg.UnloadKey(wreg.HKEY_LOCAL_MACHINE, "OLD_SOFTWARE")
    except:
        pass

os.system("pause")