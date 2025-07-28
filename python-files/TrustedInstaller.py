import subprocess
import os
import tempfile
import textwrap

# Define your PowerShell code as a raw string
powershell_script = r'''
$moduleName = "NtObjectManager"

if (-not (Get-Module -ListAvailable -Name $moduleName)) {
    try { 
        Install-Module -Name $moduleName -Force -Scope CurrentUser -ErrorAction Stop
    } catch {
        exit 1
    }
}

Import-Module $moduleName -Force
Set-NtTokenPrivilege SeDebugPrivilege
Start-Service TrustedInstaller
$p = Get-NtProcess -Name "TrustedInstaller.exe"
New-Win32Process powershell.exe -CreationFlags NewConsole -ParentProcess $p
'''

def run_powershell_script(script: str):
    # Write the PowerShell code to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.ps1', mode='w', encoding='utf-8') as ps_file:
        ps_file.write(script)
        ps_file_path = ps_file.name

    # Build the PowerShell command
    command = [
        "powershell.exe",
        "-ExecutionPolicy", "Bypass",
        "-NoProfile",
        "-WindowStyle", "Hidden",
        "-File", ps_file_path
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] PowerShell script failed: {e}")
    finally:
        os.remove(ps_file_path)

if __name__ == "__main__":
    run_powershell_script(powershell_script)
