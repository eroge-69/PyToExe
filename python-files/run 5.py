import vlc
import time
import win32gui
import win32con

# Your video file paths
video_path_1 = r"C:\_Career\1.mp4"
video_path_2 = r"C:\_Career\2.mp4"

# Number of times to spam each video
spam_count = 1000  # Total windows = spam_count * 2

players = []

def loop_player(player):
    """Loop the video when it ends."""
    def on_end(event):
        player.stop()
        player.play()
    event_manager = player.event_manager()
    event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, on_end)

def resize_vlc_window(player, width=120, height=80, x=20, y=20):
    time.sleep(1)
    hwnd = player.get_hwnd()
    if hwnd:
        win32gui.SetWindowPos(hwnd, None, x, y, width, height, win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW)
    else:
        print("Window handle not found.")


for _ in range(spam_count):
    # First video
    instance1 = vlc.Instance('--aspect-ratio=4:3', '--video-filter=sepia')
    player1 = instance1.media_player_new()
    media1 = instance1.media_new(video_path_1)
    player1.set_media(media1)
    loop_player(player1)
    player1.play()
    resize_vlc_window(player1)
    players.append(player1)

    # Second video
    instance2 = vlc.Instance('--aspect-ratio=4:3')
    player2 = instance2.media_player_new()
    media2 = instance2.media_new(video_path_2)
    player2.set_media(media2)
    loop_player(player2)
    player2.play()
    resize_vlc_window(player2, x=800, y=100)  # Different position for 2nd video
    players.append(player2)

    time.sleep(0.5)  # Delay to avoid overload

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping playback...")
    for p in players:
        p.stop()
