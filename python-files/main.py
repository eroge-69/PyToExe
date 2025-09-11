import kivy
import pygame 
import sys
import openai

openai.api_key = "shx"


def generate_script(prompt, max_tokens=128000):
    response = openai.ChatCompletion.create(
        model="GPT-5",
        messages=[{"role": "system", "content": "You are a professional screenwriter."},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.8,
    )
    return response['choices'][0]['message']['content']

prompt = "Write a detailed movie script for a 110-minute movie about a detective in a futuristic city."
script = generate_script(prompt)
print(script)
from diffusers import StableDiffusionPipeline
import torch

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16
)
pipe = pipe.to("cuda")

def generate_scene_image(prompt, filename):
    image = pipe(prompt).images[0]
    image.save(filename)

prompts = [
    "futuristic cityscape at night, cinematic lighting, photorealistic",
    "detective character walking in rainy street, film noir style",
    # ... ادامه برای صحنه‌های دیگر
]

for i, prompt in enumerate(prompts):
    generate_scene_image(prompt, f"scene_{i+1}.png")
from pyttsx3.api import pyttsx3

pyttsx3 = pyttsx3(model_name="pyttsx3_models/en/ljspeech/tacotron2-DDC", gpu=True)

def generate_voice(text, filename):
    tts.tts_to_file(text=text, file_path=filename)

dialogue = "Hello detective, we have a new case for you."
generate_voice(dialogue, "dialogue_1.wav")
import moviepy.editor as mpe

image_files = ["scene_1.png", "scene_2.png"]
audio_file = "dialogue_1.wav"

clips = [mpe.ImageClip(m).set_duration(5) for m in image_files]
video = mpe.concatenate_videoclips(clips, method="compose")

audio = mpe.AudioFileClip(audio_file)
video = video.set_audio(audio)

video.write_videofile("movie.mp4", fps=24)
# این کد باید داخل محیط Blender اجرا شود
import bpy

# بارگذاری فایل صحنه
bpy36.ops.wm.open_mainfile(filepath="/path/to/scene.blend")

# تنظیمات رندر
bpy.context.scene.render.filepath = "/tmp/rendered_frame.png"
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = True

bpy.ops.render.render(write_still=True)
import json
import os

class MovieProject:
    def __init__(self, project_path):
        self.project_path = project_path
        self.data = {
            "title": "",
            "genre": "",
            "script": "",
            "characters": [],
            "scenes": [],
            "dialogues": [],
            "poster": None,
            "trailer": None,
            "videos": []
        }

    def save(self):
        os.makedirs(self.project_path, exist_ok=True)
        with open(os.path.join(self.project_path, "project.json"), "w") as f:
            json.dump(self.data, f, indent=4)

    def load(self):
        with open(os.path.join(self.project_path, "project.json"), "r") as f:
            self.data = json.load(f)
def add_character(project, name, photo_path):
    project.data['characters'].append({
        "name": name,
        "photo":
...     })

# جایگزین کن با کلید API خودت
openai.api_key = "shx"

class Actor:
    def __init__(self, name):
        self.name = name

class Dialogue:
    def __init__(self, actor, text):
        self.actor = actor
        self.text = text

class Scene:
    def __init__(self, number, description):
        self.number = number
        self.description = description
        self.actors = []
        self.dialogues = []

    def add_actor(self, actor):
        if actor not in self.actors:
            self.actors.append(actor)

    def add_dialogue(self, dialogue):
        self.dialogues.append(dialogue)

    def show_scene(self):
        print(f"Scene {self.number}: {self.description}")
        print("Actors in scene:")
        for a in self.actors:
            print(f"- {a.name}")
        print("Dialogues:")
        for d in self.dialogues:
            print(f"{d.actor.name}: {d.text}")
        print()

def generate_scene_and_dialogue(scene_number, genre="درام"):
    prompt = f"""
    تو یک نویسنده فیلم هستی که باید یک صحنه فیلم {genre} بسازی.
    صحنه شماره {scene_number} رو با یک توضیح کوتاه بنویس.
    سپس دو شخصیت معرفی کن و یک دیالوگ بین آنها بنویس که جذاب و طبیعی باشه.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2000,
        temperature=0.8,
        n=1,
        stop=None
    )

    text = response.choices[0].text.strip()
    return text

def parse_scene(text):
    # این تابع ساده سعی می‌کنه خروجی رو تقسیم کنه به صحنه، بازیگران و دیالوگ
    lines = text.split('\n')
    description = ""
    actors = []
    dialogues = []

    for line in lines:
        line = line.strip()
        if line.lower().startswith("صحنه"):
            description = line
        elif ":" in line:
            parts = line.split(":", 1)
            actor_name = parts[0].strip()
            dialogue_text = parts[1].strip()
            if actor_name not in actors:
                actors.append(actor_name)
            dialogues.append((actor_name, dialogue_text))
        else:
            # ممکنه اسم بازیگر یا توضیح باشه
            pass

    return description, actors, dialogues

# ساخت صحنه با هوش مصنوعی و نمایش آن
scene_text = generate_scene_and_dialogue(1, genre="درام")
description, actor_names, dialogue_list = parse_scene(scene_text)

scene = Scene(1, description)
actors = {name: Actor(name) for name in actor_names}
for actor in actors.values():
    scene.add_actor(actor)

for actor_name, dialogue_text in dialogue_list:
    scene.add_dialogue(Dialogue(actors[actor_name], dialogue_text))

scene.show_scene()
class Actor:
    def __init__(self, name, image_path=None, voice_path=None):
        self.name = name
        self.image_path = image_path  # مسیر فایل عکس (مثلاً jpg, png)
        self.voice_path = voice_path  # مسیر فایل صدا (مثلاً wav, mp3)

    def __repr__(self):
        return f"Actor(name={self.name}, image={self.image_path}, voice={self.voice_path})"
actor1 = Actor("androew", image_path="media/ali.jpg", voice_path="media/ali_voice.mp3")
import json

actors = [
    {
        "name": actor1.name,
        "image_path": actor1.image_path,
        "voice_path": actor1.voice_path
    }
]

with open("project_actors.json", "w", encoding="utf-8") as f:
    json.dump(actors, f, ensure_ascii=False, indent=4)
with open("project_actors.json", "r", encoding="utf-8") as f:
    data = json.load(f)

actors_loaded = []
for item in data:
    actors_loaded.append(Actor(item["name"], item["image_path"], item["voice_path"]))

for actor in actors_loaded:
    print(actor)
from playsound import playsound

playsound(actor1.voice_path)
with open("project_actors.json", "r", encoding="utf-8") as f:
    data = json.load(f)

actors_loaded = []
for item in data:
    actors_loaded.append(Actor(item["name"], item["image_path"], item["voice_path"]))

for actor in actors_loaded:
    print(actor)

from playsound import playsound

playsound(actor1.voice_path)
import openai
import os
from datetime import datetime

# کلید API خودت رو اینجا بگذار
openai.api_key = "shx"

# ساخت پوشه برای ذخیره فیلم‌ها
output_folder = "weekly_movies"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def generate_movie(genre, min_duration_minutes=60):
    # ساخت نام فیلم
    prompt_title = f"یک اسم جذاب و خلاقانه برای فیلم ژانر {genre} که حداقل {min_duration_minutes//60} ساعت طول دارد بنویس."
    title_resp = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_title,
        max_tokens=2000,
        temperature=0.9
    )
    title = title_resp.choices[0].text.strip()

    # ساخت خلاصه داستان
    prompt_summary = f"یک خلاصه داستان جذاب و هیجان‌انگیز برای فیلم سینمایی ژانر {genre} به طول حداقل ۱ دقیقه فیلم (حدود {min_duration_minutes} دقیقه) بنویس."
    summary_resp = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_summary,
        max_tokens=1500,
        temperature=0.8
    )
    summary = summary_resp.choices[0].text.strip()

    # ساخت پوستر با DALL·E
    poster_prompt = f"پوستر فیلم سینمایی ژانر {genre} با موضوع: {summary}"
    poster_response = openai.Image.create(
        prompt=poster_prompt,
        n=1,
        size="512x512"
    )
    poster_url = poster_response['data'][0]['url']

    # (اینجا می‌تونی کد دانلود تصویر از URL رو اضافه کنی اگر می‌خوای ذخیره کنی)
    
    # ساخت تریلر متنی ساده (می‌تونیم خلاصه‌ای از خلاصه داستان باشه)
    trailer_text = f"تریلر فیلم {title}:\n{summary[:200]}..."

    return {
        "title": title,
        "summary": summary,
        "poster_url": poster_url,
        "trailer_text": trailer_text
    }

def generate_weekly_movies(genres, num_movies=5, min_duration=60):
    movies = []
    for i in range(num_movies):
        genre = genres[i % len(genres)]
        movie = generate_movie(genre, min_duration)
        movies.append(movie)
    return movies

# ژانرهای مورد علاقه
genres = ["درام", "کمدی", "ترسناک", "علمی تخیلی", "اکشن"]

# تولید ۵ فیلم هفتگی
weekly_movies = generate_weekly_movies(genres, num_movies=5, min_duration=90)

# نمایش نتایج
for idx, movie in enumerate(weekly_movies, 1):
    print(f"\nفیلم {idx}: {movie['title']}")
    print(f"ژانر: {genres[(idx-1) % len(genres)]}")
    print(f"خلاصه: {movie['summary']}")
    print(f"پوستر: {movie['poster_url']}")
    print(f"تریلر متنی: {movie['trailer_text']}")
import cv2
import numpy as np
import os

# فرض می‌کنیم چند تصویر پوستر یا صحنه داریم در پوشه "images"
image_folder = 'images'
output_video = 'movie_output.avi'

images = [img for img in os.listdir(image_folder) if img.endswith(('.png', '.jpg', '.jpeg'))]
images.sort()

frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

video = cv2.VideoWriter(output_video, cv2module.VideoWriter_fourcc(*'XVID'), 1, (width, height))

for image in images:
    frame = cv2.imread(os.path.join(image_folder, image))
    video.write(frame)

video.release()
print(f"ویدیو ساخته شد: {output_video}")
import openai

openai.api_key = "shx"

def analyze_screenplay_description(description_text):
    prompt = f"""
    شما یک دستیار هوش مصنوعی هستید که باید از توضیحات زیر بفهمید کاربر چه نوع فیلمی می‌خواهد بسازد.
    متن زیر فیلمنامه یا ایده فیلم است:
    \"\"\"
    {description_text}
    \"\"\"

    لطفاً موارد زیر را استخراج و شرح دهید:
    1. ژانر فیلم
    2. تم اصلی
    3. شخصیت‌های کلیدی
    4. مکان‌ها
    5. سبک و لحن فیلم (مثلاً درام، کمدی، ترسناک و ...)
    6. خلاصه داستان کوتاه
    7. نکات مهم دیگر که به ساخت فیلم کمک می‌کند

    پاسخ را در قالب یک JSON مرتب و خوانا بده.
    """

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return response.choices[0].text.strip()

# مثال استفاده
user_description = """
فیلمی در ژانر علمی تخیلی که در آینده دور اتفاق می‌افتد و درباره یک دانشمند است که تلاش می‌کند انسان‌ها را از نابودی نجات دهد. داستان پر از صحنه‌های هیجان‌انگیز و کشمکش‌های روانی است.
"""

result = analyze_screenplay_description(user_description)
print(result)
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

# 1. تولید صدای دیالوگ با احساس (gTTS ساده)
text = "سلام! حالت چطوره؟ من خیلی خوشحالم که می‌بینمت."
tts = gTTS(text, lang='fa')  # زبان فارسی
tts.save("output_voice.mp3")

# 2. فرض کنیم یک ویدئو از صورت داریم (مثلاً 'input_face.mp4')
# باید ابتدا Wav2Lip را اجرا کنید با دستور زیر در ترمینال:
# python inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face input_face.mp4 --audio output_voice.mp3

# 3. نمایش ویدئوی نهایی
video = VideoFileClip("results/result_voice.mp4")
video.preview()
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import pygame
import time

# بارگذاری ویدئو
video = VideoFileClip("film.mp4")

# بارگذاری موسیقی متن
background_music = AudioFileClip("music.mp3").volumex(0.5)

# بارگذاری صدای افکت (مثلاً نور)
light_sound = AudioFileClip("light_effect.mp3").set_start(5)  # در ثانیه 5

# ترکیب موسیقی متن و افکت
final_audio = CompositeAudioClip([background_music, light_sound])
video = video.set_audio(final_audio)

# ذخیره‌سازی ویدئو جدید با صداگذاری و موسیقی متن
video.write_videofile("output_film.mp4", codec='libx264', audio_codec='aac')

# --- نورپردازی نمایشی با pygame (نمادین) ---
# فرض: وقتی نور باید تغییر کند، صدا هم تغییر می‌کند.

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("نورپردازی نمایشی")

def lighting_effect(color, duration):
    screen.fill(color)
    pygame.display.update()
    time.sleep(duration)

# اجرای افکت‌های نور در لحظات خاص
lighting_schedule = [
    (2, (255, 0, 0)),   # نور قرمز در ثانیه 2
    (4, (0, 255, 0)),   # نور سبز در ثانیه 4
    (6, (0, 0, 255)),   # نور آبی در ثانیه 6
]

start_time = time.time()
i = 0

running = True
while running and i < len(lighting_schedule):
    current_time = time.time() - start_time
    scheduled_time, color = lighting_schedule[i]
    if current_time >= scheduled_time:
        lighting_effect(color, 1)
        i += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
import cv2
import face_recognition
import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx

def scene_detect(video_path, threshold=30):
    """تشخیص صحنه‌ها بر اساس تفاوت فریم‌ها"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    scene_times = [0]
    prev_frame = None
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2module.COLOR_BGR2GRAY)
        if prev_frame is not None:
            diff = cv2module.absdiff(gray, prev_frame)
            score = np.sum(diff) / diff.size
            if score > threshold:
                scene_time = frame_count / fps
                scene_times.append(scene_time)
        prev_frame = gray
        frame_count += 1

    cap.release()
    return scene_times

def apply_ai_glow_effect(frame):
    """جلوه درخشش روی چهره با استفاده از face_recognition"""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition-module.face_locations(rgb_frame)
    for (top, right, bottom, left) in face_locations:
        face = frame[top:bottom, left:right]
        glow = cv2.GaussianBlur(face, (21, 21), 30)
        frame[top:bottom, left:right] = cv2.addWeighted(face, 0.5, glow, 0.5, 0)
    return frame

def render_effect_clip(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2module.CAP_PROP_FPS)
    width  = int(cap.get(cv2module.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2module.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = apply_ai_glow_effect(frame)
        out.write(frame)

    cap.release()
    out.release()

def auto_edit_and_add_effects(input_video, output_video):
    scene_times = scene_detect(input_video)
    clip = VideoFileClip(input_video)
    clips = []

    for i in range(len(scene_times)-1):
        subclip = clip.subclip(scene_times[i], scene_times[i+1])
        # افزودن افکت سرعت یا روشنایی به صورت نمادین
        subclip = subclip.fx(vfx.colorx, 1.2)
        clips.append(subclip)

    final_clip = concatenate_videoclips(clips)
    temp_path = "temp_ai_effect.mp4"
    final_clip.write_videofile(temp_path)

    # افزودن جلوه درخشش هوشمند روی چهره‌ها
    render_effect_clip(temp_path, output_video)

# استفاده
input_video = "film.mp4"
output_video = "final_ai_edited_film.mp4"
auto_edit_and_add_effects(input_video, output_video)
import bpy
import json
import time

# --- Load Script ---
with open('/path/to/scene_script.json') as f:
    scene_data = json.load(f)

# --- Load or create actors ---
actors = {}
for name in scene_data["actors"]:
    if name not in bpy.data.objects:
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        obj = bpy.context.object
        obj.name = name
    actors[name] = bpy-cuda.data.objects[name]

# --- Execute Actions ---
for action in scene_data["script"]:
    actor = actors[action["actor"]]
    
    if action["action"] == "move":
        loc = action["to"]
        duration = action.get("duration", 1)
        frame_start = bpy.context.scene.frame_current
        frame_end = frame_start + int(duration * 24)
        actor.keyframe_insert(data_path="location", frame=frame_start)
        actor.location = loc
        actor.keyframe_insert(data_path="location", frame=frame_end)
        bpy.context.scene.frame_set(frame_end)
    
    elif action["action"] == "speak":
        print(f"{action['actor']} says: {action['text']}")
        # برای دیالوگ‌ها می‌تونی از سیستم صوتی یا متنی Blender استفاده کنی
    
    elif action["action"] == "emotion":
        print(f"{action['actor']} becomes {action['state']}")
        # می‌تونی morph target یا shape key تغییر بدی

# ذخیره یا اجرای رندر نهایی
# bpy.ops.render.render(animation=True)
 

