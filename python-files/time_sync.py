
import subprocess

def sync_time():
    try:
        print("Syncing time with time.windows.com...")
        subprocess.run("w32tm /resync", shell=True, check=True)
        print("Time sync successful.")
    except subprocess.CalledProcessError:
        print("Failed to sync time. Try running as administrator.")

if __name__ == "__main__":
    sync_time()
