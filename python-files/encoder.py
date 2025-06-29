# mp4_to_sstv.py
import cv2
import os
from pydub import AudioSegment
import subprocess

def extract_frames(video_path, output_dir, max_frames=60):
    cap = cv2.VideoCapture(video_path)
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    while cap.isOpened() and count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        img_path = os.path.join(output_dir, f"frame_{count:04d}.jpg")
        cv2.imwrite(img_path, frame)
        count += 1
    cap.release()

def encode_sstv(img_dir, sstv_audio_path):
    audio = AudioSegment.silent(duration=0)
    for fname in sorted(os.listdir(img_dir)):
        if fname.endswith(".jpg"):
            img_path = os.path.join(img_dir, fname)
            wav_out = img_path + ".wav"
            subprocess.run(["pysstv", img_path, wav_out])  # customize depending on encoder
            audio += AudioSegment.from_wav(wav_out)
    audio.export(sstv_audio_path, format="wav")

extract_frames("video.mp4", "frames")
encode_sstv("frames", "final_sstv.wav")
