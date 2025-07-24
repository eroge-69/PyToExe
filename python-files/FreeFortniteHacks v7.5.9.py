import cv2
import numpy as np
import os
import time
import subprocess
import ctypes
import pyautogui

def play_bad_apple_in_cmd(video_path, output_width=80, target_fps=30):
    ASCII_CHARS = "@%#*+=-:. "
    
    frame_delay = 1.0 / target_fps

    subprocess.run(['cmd', '/c', 'mode', 'con:', 'cols={}'.format(output_width + 10), 'lines=50'], 
                   shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    try:

        time.sleep(0.5)
        pyautogui.press('f11')
    except Exception as e:
        print(f"Couldn't enter fullscreen automatically: {e}")
        print("Please press F11 to enter fullscreen mode manually")
    
    intro_messages = [
        "Hi.",
        "Is it okay if I taste your foreskin?",
        "Anyways, Enjoy Bad Apple in ASCII!\n"
    ]
    for msg in intro_messages:
        print(msg, end='', flush=True)
        time.sleep(2 if msg.startswith("Hi.") else 1)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("ERROR: Something Went Wrong!")
        return
    
    ascii_map = [ASCII_CHARS[min(i // 32, len(ASCII_CHARS) - 1)] for i in range(256)]
    
    try:
        prev_time = time.time()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            new_height = int((height / width) * output_width * 0.55)
            resized = cv2.resize(gray, (output_width, new_height))
            
            ascii_frame = []
            for row in resized:
                ascii_row = [ascii_map[pixel] for pixel in row]
                ascii_frame.append("".join(ascii_row))
            ascii_frame = "\n".join(ascii_frame)
            
            os.system('cls')
            print(ascii_frame, end='')
            
            elapsed = time.time() - prev_time
            sleep_time = max(0, frame_delay - elapsed)
            time.sleep(sleep_time)
            prev_time = time.time()
    
    except KeyboardInterrupt:
        print("\nWhy Did U Stop :( ")
    
    finally:
        cap.release()

if __name__ == "__main__":
    video_path = r"C:\Users\raul4\Downloads\New folder (22)\【東方】Bad Apple!! ＰＶ【影絵】 (144p).mp4"
    play_bad_apple_in_cmd(video_path, target_fps=30)