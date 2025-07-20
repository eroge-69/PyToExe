import os
import sys
import subprocess
import psutil

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if process_name.lower() in proc.info['name'].lower():
            return True
    return False


def open_file_with_default_app(filepath):

    # Check if the file actually exists
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        return

    try:
        if sys.platform == "win32":
            os.startfile(os.path.realpath(filepath))
    except Exception as e:
        print(f"Failed to open '{filepath}'. Reason: {e}")


def open_chrome_profile(profile_directory):
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    user_data_dir = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data")

    if not os.path.exists(chrome_path):
        print("Error: Google Chrome not found at the specified path.")
        return

    command = [
        chrome_path,
        f"--profile-directory={profile_directory}",
        f"--user-data-dir={user_data_dir}"
    ]

    try:
        subprocess.Popen(command)
        print(f"Successfully opened Chrome with profile: {profile_directory}")
    except Exception as e:
        print(f"An error occurred: {e}")


ue_project_path = r"D:\UnrealProjects\Production\OpenWorldRPG\OpenWorldRPG.uproject"
image_path = r"D:\Game Assets\OpenWorldRPG_GameAsset\Mesh\Environment\Buildings\All Building Props.png"
yt_music_path = r"C:\Users\RAKIB RAHAMAN\AppData\Local\youtube_music_desktop_app\youtube-music-desktop-app.exe"

ue_process_name = "unrealeditor.exe"
yt_music_process_name = "youtube-music-desktop-app.exe"
image_process_name = "photos.exe"
chrome_process_name = "chrome.exe"

# --- Main execution ---
if __name__ == "__main__":

    if not is_process_running(ue_process_name):
        open_file_with_default_app(ue_project_path)
    
    open_file_with_default_app(image_path)
    
    if not is_process_running(yt_music_process_name):
        open_file_with_default_app(yt_music_path)
    
    if not is_process_running(chrome_process_name):
        open_chrome_profile("Profile 6")

    print("\nScript finished.")