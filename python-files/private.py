import os
import time
import subprocess
from pathlib import Path

desktop = Path.home() / "Desktop"
documents = Path.home() / "Documents"
public = Path("C:/Users/Public")
root_c = Path("C:/")

folder_targets = {
    root_c / "VX-TRACE_000": None,
    public / "EXFIL_QUEUE": "EXFIL module armed.\nQueue state: Listening...",
    documents / "GHOSTSYNC": "Ghostsync connection: ESTABLISHED.\nPayload: dormant",
    desktop / "SEED69-INIT": "SEED_69 sequence injected.\nFlag set: volatile."
}

special_readme = (
    "VX-TRACE BOOTMARK v0.7\n"
    "--------------------------\n"
    "Trace ID locked.\n"
    "System flag detected.\n"
    "VXROOT engaged.\n"
    "\n"
    "\n"
    "you fucked up"
)

desktop_files = [
    "vxseed_69a3.sys", "kernel_trace.dump", "inject_trace_000.hex", "ghost-flag.init",
    "MEMDUMP.0", "boot_patch_fail.dmp", "autorun.sys", "INFECTED_README.txt",
    "wake_signal.log", "VX_BOOT_LOCK.tmp", "🛑_no_exit.bat", "cfg_root.inject",
    "⚠️_SYSFAIL.dmp", "bios_flag.bin", "vxmirror.exe", "EXFIL_QUEUE_ACCESS.log"
]

file_content = (
    "VX_TRACE_ID: 69A3-F4X\n"
    "STATUS: LOCKED\n"
    "BOOT HOOK: ACTIVE\n"
    "INFECTION MARKER: DEPLOYED\n"
    "WATCHDOG: OFFLINE\n"
    "DO NOT DELETE."
)

console_lines = [
    "[vx.lab] Malware container injected",
    "[vx.lab] VX-TRACE_000 initializing...",
    "[vx.lab] Boot Hook: ACTIVE",
    "[vx.lab] ghostsync.exe running",
    "[vx.lab] VXROOT exploit chain deployed",
    "[vx.lab] Backdoor injection: SUCCESS",
    "[vx.lab] Trace ID: 69A3-F4X assigned",
    "[vx.lab] Local shell override granted",
    "[vx.lab] Registry lockdown: ENFORCED",
    "[vx.lab] kernel_patch.sys → injected",
    "[vx.lab] Memory exfiltration in progress...",
    "[vx.lab] BIOS ping: PASSED",
    "[vx.lab] Lock sequence: SYNCED",
    "[vx.lab] Root-access secured",
    "[vx.lab] VX-MIRROR backup created",
    "[vx.lab] Infection marker dropped",
    "[vx.lab] System compromise: COMPLETE",
    "[vx.lab] WARNING: Broadcast flagged",
    "[vx.lab] Silent watchdog disabled",
    "[vx.lab] VX_PROXY contacted @ 69.42.0.1",
    "[vx.lab] System under surveillance",
    "[vx.lab] vx.lab // status: PERMANENT"
]

def deploy_folders():
    for path, content in folder_targets.items():
        try:
            path.mkdir(parents=True, exist_ok=True)
            with open(path / "README.txt", "w") as f:
                if path.name == "VX-TRACE_000":
                    f.write(special_readme)
                else:
                    f.write(content)
        except:
            pass

def drop_desktop_files():
    for name in desktop_files:
        try:
            with open(desktop / name, "w") as f:
                f.write(file_content)
        except:
            pass

def run_fake_console():
    for line in console_lines:
        print(line)
        time.sleep(0.5)

def open_special_readme():
    try:
        subprocess.Popen(["notepad", str(root_c / "VX-TRACE_000" / "README.txt")])
    except:
        pass

def countdown_and_exit():
    for i in range(5, 0, -1):
        print(f"[vx.lab] Countdown: {i}")
        time.sleep(1)
    print("[vx.lab] Closing shell...")
    time.sleep(2)
    subprocess.run("taskkill /f /im notepad.exe", shell=True)
    os._exit(0)

if __name__ == "__main__":
    deploy_folders()
    drop_desktop_files()
    run_fake_console()
    open_special_readme()
    time.sleep(2)
    countdown_and_exit()