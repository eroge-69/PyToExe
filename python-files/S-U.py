import subprocess
import os
import sys

# ==============================================================================
# Dependency Installation
# ==============================================================================
def install_dependencies():
    """
    Installs required Python packages using pip.
    """
    print("Checking for required Python packages...")
    required_packages = ['requests', 'schedule']
    installed_packages = {pkg.split('==')[0] for pkg in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode().split('\n')}

    for package in required_packages:
        if package not in installed_packages:
            try:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"{package} installed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {package}: {e}")
                sys.exit(1)

# Run dependency check first
install_dependencies()

# Now it's safe to import the modules
import requests
import time
import schedule
import json


# ==============================================================================
# Configuration
# ==============================================================================

# GitHub API URL for Sunshine releases
GITHUB_RELEASES_API = "https://api.github.com/repos/LizardByte/Sunshine/releases"
# The name of the installer file to download
INSTALLER_FILENAME = "Sunshine-Windows-AMD64-installer.exe"
# File to store the currently installed version number
VERSION_FILE = "sunshine_version.txt"
# Directory to save the downloaded installer
DOWNLOAD_DIR = "C:\\Temp"

# ViGEmBus
VIGEMBUS_GITHUB_RELEASES_API = "https://api.github.com/repos/nefarius/ViGEmBus/releases"
VIGEMBUS_INSTALLER_FILENAME = "ViGEmBus_1.22.0_x64_x86_arm64.exe"
VIGEMBUS_VERSION_FILE = "vigembus_version.txt"


# ==============================================================================
# Functions
# ==============================================================================

def get_latest_prerelease_version():
    """
    Fetches the latest pre-release version from the GitHub API.

    Returns:
        str: The tag name (version) of the latest pre-release, or None if not found.
    """
    try:
        response = requests.get(GITHUB_RELEASES_API)
        response.raise_for_status()
        releases = response.json()
        for release in releases:
            # Check for pre-release status and the correct installer asset
            if release['prerelease'] and any(asset['name'] == INSTALLER_FILENAME for asset in release['assets']):
                print(f"Found latest pre-release: {release['tag_name']}")
                return release['tag_name']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching releases from GitHub: {e}")
        return None

def get_latest_vigembus_version():
    """
    Fetches the latest stable ViGEmBus version from the GitHub API.

    Returns:
        str: The tag name (version) of the latest release, or None if not found.
    """
    try:
        response = requests.get(VIGEMBUS_GITHUB_RELEASES_API)
        response.raise_for_status()
        releases = response.json()
        for release in releases:
            if not release['prerelease'] and any(asset['name'] == VIGEMBUS_INSTALLER_FILENAME for asset in release['assets']):
                print(f"Found latest ViGEmBus version: {release['tag_name']}")
                return release['tag_name']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ViGEmBus releases from GitHub: {e}")
        return None

def get_local_version(file_path):
    """
    Reads the locally stored version number from a given file.

    Returns:
        str: The version number as a string, or None if the file doesn't exist.
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                version = f.read().strip()
                print(f"Local version found for {file_path}: {version}")
                return version
        print(f"Local version file not found for {file_path}.")
        return None
    except IOError as e:
        print(f"Error reading local version file {file_path}: {e}")
        return None

def update_local_version(file_path, version):
    """
    Writes the new version number to the local file.

    Args:
        file_path (str): The path to the version file.
        version (str): The new version string to write.
    """
    try:
        with open(file_path, "w") as f:
            f.write(version)
        print(f"Updated local version to: {version} in {file_path}")
    except IOError as e:
        print(f"Error writing to local version file {file_path}: {e}")

def download_and_install(tag_name, installer_filename):
    """
    Downloads the specified installer and runs it in silent mode.

    Args:
        tag_name (str): The tag name (version) of the release to download.
        installer_filename (str): The filename of the installer.
    
    Note: This function requires the script to be run with administrator privileges on Windows.
    """
    repo_name = "Sunshine" if "Sunshine" in installer_filename else "ViGEmBus"
    download_url = f"https://github.com/LizardByte/{repo_name}/releases/download/{tag_name}/{installer_filename}"
    installer_path = os.path.join(DOWNLOAD_DIR, installer_filename)

    print(f"Downloading installer from: {download_url}")
    try:
        # Create download directory if it doesn't exist
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        # Download the file
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(installer_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("Download complete.")

        print(f"Starting silent installation of {installer_path}...")
        # Execute the installer silently with the /S flag (common for Inno Setup)
        subprocess.run([installer_path, "/S"], check=True)
        print("Installation complete.")

        # Update the local version file
        if "Sunshine" in installer_filename:
            update_local_version(VERSION_FILE, tag_name)
        elif "ViGEmBus" in installer_filename:
            update_local_version(VIGEMBUS_VERSION_FILE, tag_name)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the installer: {e}")
    except subprocess.CalledProcessError as e:
        # Catch the specific elevation error
        if e.returncode == 740:
            print("\n--------------------------------------------------------------")
            print("INSTALLATION FAILED: The requested operation requires elevation.")
            print("Please re-run this script as an administrator.")
            print("--------------------------------------------------------------\n")
        else:
            print(f"Error running the installer: {e}")
    except IOError as e:
        print(f"Error handling file I/O: {e}")
    finally:
        # Clean up the downloaded file
        if os.path.exists(installer_path):
            try:
                os.remove(installer_path)
                print("Cleaned up temporary installer file.")
            except OSError as e:
                print(f"Error cleaning up installer file: {e}")

def check_for_update_job():
    """
    The main job that checks for updates and triggers the install process.
    """
    print("Checking for ViGEmBus dependencies...")
    latest_vigembus_version = get_latest_vigembus_version()
    local_vigembus_version = get_local_version(VIGEMBUS_VERSION_FILE)
    
    if latest_vigembus_version and latest_vigembus_version != local_vigembus_version:
        print(f"New ViGEmBus version available: {latest_vigembus_version}. Current version: {local_vigembus_version}. Starting update...")
        download_and_install(latest_vigembus_version, VIGEMBUS_INSTALLER_FILENAME)
    else:
        print("ViGEmBus is already up to date. No action needed.")

    print("Checking for Sunshine updates...")
    latest_version = get_latest_prerelease_version()
    local_version = get_local_version(VERSION_FILE)

    if latest_version and latest_version != local_version:
        print(f"New version available: {latest_version}. Current version: {local_version}. Starting update...")
        download_and_install(latest_version, INSTALLER_FILENAME)
    else:
        print("Sunshine is already up to date. No action needed.")

# ==============================================================================
# Main execution block
# ==============================================================================

if __name__ == "__main__":
    print("Sunshine Auto-Updater started.")
    print("This script will check for updates daily.")

    # Run the check immediately on startup
    check_for_update_job()

    # Schedule the job to run daily
    schedule.every().day.do(check_for_update_job)

    # Keep the script running to allow the scheduler to work
    while True:
        schedule.run_pending()
        time.sleep(1)
