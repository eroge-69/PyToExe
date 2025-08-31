import time
import numpy as np
import imageio
import pygame
from PIL import ImageGrab, Image
from moviepy.editor import VideoFileClip, AudioFileClip
import cv2
import os

def create_video(frames, output_file):
    fps = 25
    writer = imageio.get_writer(output_file, fps=fps)
    for frame in frames:
        writer.append_data(frame)
    writer.close()

def main():
    pygame.mixer.init()
    
    pygame.mixer.music.load('start.mp3')
    pygame.mixer.music.play()
    time.sleep(1)

    im = ImageGrab.grab()
    original_image = np.array(im)
    mirrored_image = np.array(im.transpose(Image.FLIP_LEFT_RIGHT))
    flipped_image = np.array(im.transpose(Image.FLIP_TOP_BOTTOM))

    frames = []
    for _ in range(30):
        frames.append(original_image)
        frames.append(mirrored_image)

    for _ in range(75):
        frames.append(original_image)
        frames.append(flipped_image)

    create_video(frames, 'output.mp4')

    pygame.mixer.music.stop()

    video_clip = VideoFileClip('output.mp4')
    audio_clip = AudioFileClip('sound.mp3')
    final_video = video_clip.set_audio(audio_clip)

    final_video.write_videofile('final_output.mp4', codec='libx264', audio_codec='aac')

    final_video.preview()

    cv2.namedWindow('Video', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cap = cv2.VideoCapture('final_output.mp4')

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Video', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    os.system('python part2.py')

if __name__ == "__main__":
    main()
