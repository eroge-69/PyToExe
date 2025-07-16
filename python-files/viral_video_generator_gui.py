
import os
import random
import requests
import pyttsx3
from moviepy.editor import *
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog

# ================== CONFIG ===================
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_DURATION = 15
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-Bold.ttf"
FONT_FILE = "Montserrat-Bold.ttf"
# ============================================

# === Download font if not exists ===
def ensure_font():
    if not os.path.exists(FONT_FILE):
        r = requests.get(FONT_URL)
        with open(FONT_FILE, "wb") as f:
            f.write(r.content)

# === Fetch trending topic from Inshorts ===
def get_trending_topic():
    try:
        url = "https://inshortsapi.vercel.app/news?category=all"
        res = requests.get(url).json()
        article = random.choice(res["data"])
        return f"{article['title']}. {article['content']}"
    except:
        return "AI is taking over the world. Here’s what you should know."

# === Generate script using free chatbot API ===
def generate_script(topic):
    try:
        url = f"https://api.affiliateplus.xyz/api/chatbot?message=make a viral video script about {topic}&botname=ViralBot&ownername=You"
        return requests.get(url).json()["message"]
    except:
        return "Here's a fun and informative short video about how AI is taking over creative media!"

# === Generate hashtags using simple keywords ===
def generate_hashtags(script):
    keywords = [word.strip("#.,!") for word in script.split() if len(word) > 4]
    top_words = list(set(random.sample(keywords, min(8, len(keywords)))))
    hashtags = ["#" + word.lower() for word in top_words]
    return " ".join(hashtags)

# === Voice-over generator ===
def generate_voice(text, filename):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    voice = random.choice(voices)
    engine.setProperty('voice', voice.id)
    engine.setProperty('rate', 145)
    engine.save_to_file(text, filename)
    engine.runAndWait()

# === Subtitle frame generator ===
def create_subtitle_frame(text, duration, font_path):
    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 65)
    y = VIDEO_HEIGHT // 2
    draw.text((80, y), text, font=font, fill=(255, 255, 255))
    img_path = f"frame_{random.randint(1000,9999)}.jpg"
    img.save(img_path)
    return ImageClip(img_path).set_duration(duration)

# === Download background music ===
def download_music():
    url = "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Kevin_MacLeod/Film_Noir/Kevin_MacLeod_-_Cool_Vibes.mp3"
    music_path = "bg_music.mp3"
    if not os.path.exists(music_path):
        r = requests.get(url)
        with open(music_path, "wb") as f:
            f.write(r.content)
    return music_path

# === UI and Execution ===
def run_generator():
    ensure_font()
    topic = topic_var.get().strip() or get_trending_topic()
    script_text = generate_script(topic)
    hashtags = generate_hashtags(script_text)

    generate_voice(script_text, "voice.mp3")
    narration = AudioFileClip("voice.mp3").set_duration(VIDEO_DURATION)
    music = AudioFileClip(download_music()).volumex(0.2).set_duration(VIDEO_DURATION)
    final_audio = CompositeAudioClip([narration, music])

    clips = []

    # Scene: Intro text
    if use_subtitles.get():
        lines = script_text.split('.')[:3]
        for line in lines:
            clip = create_subtitle_frame(line.strip(), 4, FONT_FILE)
            clips.append(clip.crossfadein(1))

    # Final still with hashtags
    final_img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), color=(20, 20, 20))
    draw = ImageDraw.Draw(final_img)
    font = ImageFont.truetype(FONT_FILE, 60)
    draw.text((60, VIDEO_HEIGHT // 2), "Follow for More!\n" + hashtags, fill="white", font=font)
    final_img.save("final.jpg")
    final_clip = ImageClip("final.jpg").set_duration(4)

    clips.append(final_clip)
    final_video = concatenate_videoclips(clips).set_audio(final_audio)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_video = f"viral_video_{timestamp}.mp4"
    final_video.write_videofile(output_video, fps=24)
    messagebox.showinfo("Done!", f"Video saved as: {output_video}")

# === GUI ===
root = tk.Tk()
root.title("AI Viral Video Generator")
root.geometry("400x300")

tk.Label(root, text="Enter Topic (or leave blank for trending):").pack(pady=10)
topic_var = tk.StringVar()
tk.Entry(root, textvariable=topic_var, width=50).pack()

use_subtitles = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Include Subtitles & Transitions", variable=use_subtitles).pack(pady=10)

tk.Button(root, text="Generate Video", command=run_generator).pack(pady=20)
tk.Label(root, text="Built with ❤️ by AI").pack(pady=10)

root.mainloop()
