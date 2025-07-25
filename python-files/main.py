import os
import ctypes
import win32gui
import win32con
import vlc
import time

VIDEO_FILE = "wallpaper.mp4"

def get_workerw():
    progman = win32gui.FindWindow("Progman", None)
    win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
    
    def enum_windows_callback(hwnd, lparam):
        p = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
        if p != 0:
            lparam.append(win32gui.FindWindowEx(0, hwnd, "WorkerW", None))
        return True

    workerws = []
    win32gui.EnumWindows(enum_windows_callback, workerws)
    return workerws[0] if workerws else None

def set_video_wallpaper(video_path):
    hwnd = get_workerw()
    if hwnd:
        os.environ["VLC_PLUGIN_PATH"] = r"C:\Program Files\VideoLAN\VLC\plugins"  # Update as needed
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(video_path)
        player.set_media(media)
        player.set_hwnd(hwnd)
        player.play()
        time.sleep(1)  # Let the video load
        while True:
            if player.get_state() == vlc.State.Ended:
                player.stop()
                player.play()
            time.sleep(1)

if __name__ == "__main__":
    set_video_wallpaper(VIDEO_FILE)
