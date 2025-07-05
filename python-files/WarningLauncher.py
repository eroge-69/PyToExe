
import os
import time
import ctypes
import pygame
import cv2

# Set filenames
AUDIO_FILE = "warning.mp3"
VIDEO_FILE = "splash.mp4"

def play_audio():
    pygame.mixer.init()
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play()

def play_video():
    cap = cv2.VideoCapture(VIDEO_FILE)
    cv2.namedWindow("warning", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("warning", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("warning", frame)
        if cv2.waitKey(30) & 0xFF == 27:  # ESC won't close
            pass

    cap.release()
    cv2.destroyAllWindows()

def sleep_pc():
    ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)

if __name__ == "__main__":
    if not os.path.exists(AUDIO_FILE) or not os.path.exists(VIDEO_FILE):
        print("Missing warning.mp3 or splash.mp4 in the same folder.")
        time.sleep(3)
        exit()

    play_audio()
    time.sleep(4)
    play_video()
    time.sleep(10)
    sleep_pc()
