#!/usr/bin/env python3
# mac_changer.py
# Requires Windows. Uses PowerShell via subprocess to edit registry and restart adapter.
# Run as Administrator.

import subprocess
import sys
import os
import random
import re

def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_powershell(ps_cmd):
    # Run a PowerShell command and return (returncode, stdout, stderr)
    proc = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

def list_adapters():
    ps = "Get-NetAdapter | Select-Object -Property Name,InterfaceDescription,MacAddress,InterfaceGuid | ConvertTo-Json"
    rc, out, err = run_powershell(ps)
    if rc != 0:
        print("خطا در گرفتن اطلاعات کارت‌ها: ", err)
        return []
    import json
    try:
        data = json.loads(out)
    except Exception:
        # If only one adapter, PowerShell returns object not list
        try:
            data = [json.loads(out)]
        except Exception as e:
            print("خطا در خواندن خروجی PowerShell:", e)
            return []
    # normalize single object
    if isinstance(data, dict):
        data = [data]
    adapters = []
    for d in data:
        adapters.append({
            "Name": d.get("Name"),
            "Desc": d.get("InterfaceDescription"),
            "MAC": d.get("MacAddress"),
            "Guid": d.get("InterfaceGuid")
        })
    return adapters

def fmt_mac(mac):
    # Remove separators and uppercase
    return re.sub(r'[^0-9A-Fa-f]', '', mac).upper()

def random_mac():
    # Generate a locally-administered unicast MAC:
    # set second least significant bit of first octet to 1 (locally administered),
    # and least significant bit to 0 (unicast).
    first = random.randrange(0x00, 0x100)
    # set locally administered bit (bit1) and clear multicast bit (bit0)
    first = (first & 0b11111110) | 0b00000010
    octets = [first] + [random.randrange(0x00, 0x100) for _ in range(5)]
    return ''.join(f"{b:02X}" for b in octets)

def set_network_address_by_guid(interface_guid, new_mac_no_sep, adapter_name_for_restart):
    # PowerShell script:
    ps = rf'''
$guid = "{interface_guid}"
$val = "{new_mac_no_sep}"
$base = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{{4d36e972-e325-11ce-bfc1-08002be10318}}"
Get-ChildItem $base | ForEach-Object {{
    $p = $_.PsPath
    try {{
        $item = Get-ItemProperty -Path $p -ErrorAction Stop
        if ($item.NetCfgInstanceId -eq $guid) {{
            if ($val -eq "") {{
                # remove value
                if (Get-ItemProperty -Path $p -Name "NetworkAddress" -ErrorAction SilentlyContinue) {{
                    Remove-ItemProperty -Path $p -Name "NetworkAddress" -ErrorAction SilentlyContinue
                }}
            }} else {{
                Set-ItemProperty -Path $p -Name "NetworkAddress" -Value $val -Type String
            }}
            Write-Output "OK"
            exit 0
        }}
    }} catch {{ }}
}}
Write-Error "Adapter registry entry not found"
exit 1
'''
    rc, out, err = run_powershell(ps)
    return rc, out, err

def restart_adapter(adapter_name):
    # disable then enable
    ps = rf'''
$nm = "{adapter_name}"
try {{
    Disable-NetAdapter -Name $nm -Confirm:$false -ErrorAction Stop
    Start-Sleep -Seconds 1
    Enable-NetAdapter -Name $nm -Confirm:$false -ErrorAction Stop
    Write-Output "RESTARTED"
    exit 0
}} catch {{
    Write-Error $_.Exception.Message
    exit 1
}}
'''
    return run_powershell(ps)

def main():
    if os.name != 'nt':
        print("این برنامه فقط روی ویندوز اجرا می‌شود.")
        return

    if not is_admin():
        print("لطفاً برنامه را با دسترسی Administrator اجرا کن (Run as administrator).")
        return

    adapters = list_adapters()
    if not adapters:
        print("هیچ کارت شبکه‌ای پیدا نشد یا دسترسی به PowerShell ممکن نیست.")
        return

    print("کارت‌های شبکهٔ پیدا شده:")
    for i, a in enumerate(adapters, 1):
        print(f"{i}. Name: {a['Name']}\n   Desc: {a['Desc']}\n   MAC: {a['MAC']}\n   Guid: {a['Guid']}\n")

    # انتخاب کاربر
    sel = input("شماره کارت برای تغییر MAC را وارد کن (یا نام کارت را بچسبان): ").strip()
    chosen = None
    if sel.isdigit():
        idx = int(sel) - 1
        if 0 <= idx < len(adapters):
            chosen = adapters[idx]
    else:
        for a in adapters:
            if a['Name'].lower() == sel.lower():
                chosen = a
                break

    if not chosen:
        print("انتخاب نامعتبر.")
        return

    print(f"انتخاب شد: {chosen['Name']} ({chosen['MAC']})")

    mode = input("می‌خوای MAC جدید بصورت (r) تصادفی باشه یا (m) وارد کنی؟ [r/m]: ").strip().lower()
    if mode == 'r' or mode == '':
        new_mac = random_mac()
        print("MAC تصادفی ساخته شد:", ':'.join(new_mac[i:i+2] for i in range(0,12,2)))
    else:
        mac_in = input("MAC را وارد کن (مجاز: 12 هگزادسیمال یا با : یا -): ").strip()
        new_mac = fmt_mac(mac_in)
        if len(new_mac) != 12 or not re.fullmatch(r'[0-9A-F]{12}', new_mac):
            print("MAC نامعتبر. باید 12 رقم هگزادسیمال باشد.")
            return

    # Apply change (write NetworkAddress in registry under matching subkey)
    print("در حال نوشتن به رجیستری...")
    rc, out, err = set_network_address_by_guid(chosen['Guid'], new_mac, chosen['Name'])
    if rc != 0:
        print("خطا در نوشتن رجیستری:", err or out)
        print("ممکن است درایور/آداپتر امکان تغییر MAC را نداشته باشد یا GUID پیدا نشده باشد.")
        return
    print("مقدار NetworkAddress نوشته شد. ریستارت آداپتر...")

    rc2, out2, err2 = restart_adapter(chosen['Name'])
    if rc2 == 0:
        print("آداپتر غیرفعال/فعال شد.")
        print("MAC فعلی (ممکن است نیاز به چند ثانیه یا ری‌استارت داشته باشد):")
        # show new MAC
        rc3, out3, err3 = run_powershell(f"Get-NetAdapter -Name \"{chosen['Name']}\" | Select-Object -Property Name,MacAddress | ConvertTo-Json")
        if rc3 == 0:
            try:
                import json
                data = json.loads(out3)
                if isinstance(data, dict):
                    print(f"{data.get('Name')}: {data.get('MacAddress')}")
                else:
                    print(out3)
            except Exception:
                print(out3)
        else:
            print("نتوانستیم MAC را پس از ریستارت بخوانیم.")
    else:
        print("خطا در ریستارت کردن آداپتر:", err2 or out2)
        print("ممکن است نیاز به ری‌استارت سیستم باشد.")

    print("پایان.")

if __name__ == "__main__":
    main()
