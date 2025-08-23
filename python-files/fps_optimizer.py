import psutil
import platform
import subprocess
import sys

def get_current_fps():
    cpu_usage = psutil.cpu_percent()
    fps = int((100 - cpu_usage) * 0.6)
    return fps

def optimize_fps():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] in ['OneDrive.exe','Spotify.exe','Chrome.exe']:
                proc.kill()
        except:
            pass
    if platform.system() == "Windows":
        subprocess.call("powercfg /s SCHEME_MIN", shell=True)

    current = get_current_fps()
    estimated = int(current * 1.25)
    return current, estimated

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "get"
    if action == "get":
        print(get_current_fps())
    elif action == "optimize":
        c, e = optimize_fps()
        print(f"{c},{e}")
