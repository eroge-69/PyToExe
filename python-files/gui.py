import requests
import os
import cv2
from ffpyplayer.player import MediaPlayer
import ctypes
import keyboard

def set_max_volume():
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(1.0, None)
        print("[INFO] Volume set to 100%")
    except Exception as e:
        print(f"[WARNING] Could not set volume: {e}")

def download_video(url, save_path):
    if os.path.exists(save_path):
        return
    print("[INFO] Downloading video...")
    with requests.get(url, stream=True) as r:
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print("[INFO] Download complete.")

def hide_taskbar():
    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        user32.ShowWindow(hwnd, 0)  # 0 = SW_HIDE

def show_taskbar():
    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        user32.ShowWindow(hwnd, 5)  # 5 = SW_SHOW

def block_windows_key():
    keyboard.block_key('left windows')
    keyboard.block_key('right windows')

def unblock_windows_key():
    keyboard.unblock_key('left windows')
    keyboard.unblock_key('right windows')

def play_video_fullscreen_loop(path):
    while True:
        cap = cv2.VideoCapture(path)
        player = MediaPlayer(path)

        cv2.namedWindow("Video", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while True:
            grabbed, frame = cap.read()
            audio_frame, val = player.get_frame()

            if not grabbed or val == 'eof':
                break

            if frame is not None:
                cv2.imshow("Video", frame)

            key = cv2.waitKey(20)
            if key == 27 or key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return  # Exit the loop and end the program

        cap.release()
        player.close_player()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    VIDEO_URL = (
        "https://cdn.discordapp.com/attachments/1368713329824104548/"
        "1382086580650639420/ssstik.io_1749585416888.mp4?"
        "ex=6849dfee&is=68488e6e&hm=b268870ed460f02dfcd29ad963db826e201b854f06dde63740178794fd5bea92"
    )
    VIDEO_PATH = "video_with_audio.mp4"

    download_video(VIDEO_URL, VIDEO_PATH)
    set_max_volume()

    hide_taskbar()
    try:
        block_windows_key()
        play_video_fullscreen_loop(VIDEO_PATH)
    finally:
        unblock_windows_key()
        show_taskbar()
