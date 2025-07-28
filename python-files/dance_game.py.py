
import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import filedialog
import threading
import pygame
from moviepy.editor import VideoFileClip
import numpy as np

# Initialize pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Load sound
pygame.mixer.init()
pygame.mixer.music.load("assets/sounds/success.wav")

# Global score
score = 0

def extract_keypoints(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)
    if results.pose_landmarks:
        return [(lm.x, lm.y) for lm in results.pose_landmarks.landmark]
    return []

def calculate_similarity(kp1, kp2):
    if len(kp1) != len(kp2):
        return 0
    kp1 = np.array(kp1)
    kp2 = np.array(kp2)
    dist = np.linalg.norm(kp1 - kp2)
    return max(0, 100 - dist * 500)

def webcam_thread(reference_keypoints_list):
    global score
    cap = cv2.VideoCapture(0)
    frame_index = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        keypoints = extract_keypoints(frame)
        if frame_index < len(reference_keypoints_list):
            ref_kp = reference_keypoints_list[frame_index]
            similarity = calculate_similarity(keypoints, ref_kp)
            if similarity > 80:
                score += 10
                pygame.mixer.music.play()
        else:
            break

        mp_drawing.draw_landmarks(frame, pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).pose_landmarks, mp_pose.POSE_CONNECTIONS)
        cv2.imshow('Webcam', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_index += 1

    cap.release()
    cv2.destroyAllWindows()

def extract_reference_keypoints(video_path):
    cap = cv2.VideoCapture(video_path)
    keypoints_list = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        keypoints = extract_keypoints(frame)
        keypoints_list.append(keypoints)

    cap.release()
    return keypoints_list

def play_video(video_path):
    clip = VideoFileClip(video_path)
    clip.preview()
... 
... def start_game(video_path):
...     ref_keypoints = extract_reference_keypoints(video_path)
... 
...     # Start video thread
...     video_thread = threading.Thread(target=play_video, args=(video_path,))
...     video_thread.start()
... 
...     # Start webcam thread
...     cam_thread = threading.Thread(target=webcam_thread, args=(ref_keypoints,))
...     cam_thread.start()
... 
... def launch_gui():
...     def on_start():
...         filepath = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
...         if filepath:
...             start_game(filepath)
... 
...     root = tk.Tk()
...     root.title("Just Dance Lite")
... 
...     start_button = tk.Button(root, text="Choose MP4 and Start", command=on_start, height=2, width=25, bg="green", fg="white")
...     start_button.pack(pady=20)
... 
...     score_label = tk.Label(root, text="Dance Score: 0", font=("Helvetica", 16))
...     score_label.pack(pady=10)
... 
...     def update_score():
...         score_label.config(text=f"Dance Score: {score}")
...         root.after(1000, update_score)
... 
...     update_score()
... 
...     root.mainloop()
... 
... if __name__ == "__main__":
...     launch_gui()
