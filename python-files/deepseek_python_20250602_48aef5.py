import os
import threading
import requests
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
from moviepy.editor import *
import imageio
import json
import random

# تهيئة مسارات المكتبات
os.environ["FFMPEG_BINARY"] = "ffmpeg"
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"
os.environ["IMAGEMAGICK_BINARY"] = "magick"

# إنشاء مجلدات العمل
os.makedirs("outputs/audio", exist_ok=True)
os.makedirs("outputs/video", exist_ok=True)
os.makedirs("temp/backgrounds", exist_ok=True)

# قائمة القراء
QURRA = [
    "Abdul_Basit_Murattal", "Abdullah_Basfar", "Abdurrahmaan_As-Sudais", 
    "Ahmed_ibn_Ali_al-Ajamy", "Alafasy", "Ali_Hudhaify", "Hani_Rifai",
    "Husary", "Minshawy_Murattal", "Muhammad_Jibreel"
]

# قائمة السور
SURAS = [{"name": f"سورة {name}", "number": num} for num, name in enumerate([
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال",
    "التوبة", "يونس", "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء",
    "الكهف", "مريم", "طه", "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان", "الشعراء",
    "النمل", "القصص", "العنكبوت", "الروم", "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر",
    "يس", "الصافات", "ص", "الزمر", "غافر", "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية",
    "الأحقاف", "محمد", "الفتح", "الحجرات", "ق", "الذاريات", "الطور", "النجم", "القمر",
    "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة", "الصف", "الجمعة",
    "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
    "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات",
    "عبس", "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج", "الطارق", "الأعلى",
    "الغاشية", "الفجر", "البلد", "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق",
    "القدر", "البينة", "الزلزلة", "العاديات", "القارعة", "التكاثر", "العصر", "الهمزة",
    "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون", "النصر", "المسد", "الإخلاص", "الفلق", "الناس"
], 1)]

class QuranVideoGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("مولد الفيديوهات القرآنية")
        self.root.geometry("930x820")
        self.root.resizable(False, False)
        
        # تحميل الصور
        self.bg_image = ImageTk.PhotoImage(Image.open("background.png").resize((930, 820)))
        self.export_btn = ImageTk.PhotoImage(Image.open("export_button.png").resize((300, 70)))
        self.export_btn_hover = ImageTk.PhotoImage(Image.open("export_button_hover.png").resize((300, 70)))
        
        # إنشاء Canvas
        self.canvas = Canvas(root, width=930, height=820)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        
        # إضافة الأيقونات
        self.social_icons = {
            "youtube": {"normal": "youtube_icon.png", "hover": "youtube_icon_hover.png"},
            "instagram": {"normal": "instagram_icon.png", "hover": "instagram_icon_hover.png"},
            "twitter": {"normal": "twitter_icon.png", "hover": "twitter_icon_hover.png"},
            "facebook": {"normal": "facebook_icon.png", "hover": "facebook_icon_hover.png"}
        }
        self.add_social_icons()
        
        # إضافة عناصر الواجهة
        self.add_widgets()
        
        # شريط التقدم
        self.progress = ttk.Progressbar(root, orient=HORIZONTAL, length=600, mode='determinate')
        self.canvas.create_window(465, 750, window=self.progress)
        
        # تحميل مفاتيح Pexels API
        with open('pexels.txt', 'r') as f:
            self.api_keys = [line.strip() for line in f.readlines() if line.strip()]
    
    def add_social_icons(self):
        positions = [(50, 30), (130, 30), (210, 30), (290, 30)]
        for idx, (platform, images) in enumerate(self.social_icons.items()):
            normal_img = ImageTk.PhotoImage(Image.open(images["normal"]).resize((60, 60)))
            hover_img = ImageTk.PhotoImage(Image.open(images["hover"]).resize((60, 60)))
            
            icon = self.canvas.create_image(positions[idx][0], positions[idx][1], image=normal_img, anchor="nw")
            
            # تأثير Hover
            self.canvas.tag_bind(icon, "<Enter>", lambda e, icon=icon, img=hover_img: 
                                self.canvas.itemconfig(icon, image=img))
            self.canvas.tag_bind(icon, "<Leave>", lambda e, icon=icon, img=normal_img: 
                                self.canvas.itemconfig(icon, image=img))
            
            # فتح الرابط عند الضغط
            self.canvas.tag_bind(icon, "<Button-1>", 
                               lambda e, p=platform: self.open_link(p))
    
    def open_link(self, platform):
        links = {
            "youtube": "https://www.youtube.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.twitter.com",
            "facebook": "https://www.facebook.com"
        }
        import webbrowser
        webbrowser.open(links[platform])
    
    def add_widgets(self):
        # اختيار القارئ
        self.canvas.create_text(200, 120, text="القارئ:", font=("Arial", 14), fill="white")
        self.qari_var = StringVar()
        self.qari_cb = ttk.Combobox(self.root, textvariable=self.qari_var, width=30)
        self.qari_cb['values'] = QURRA
        self.qari_cb.current(0)
        self.canvas.create_window(350, 120, window=self.qari_cb)
        
        # اختيار السورة
        self.canvas.create_text(200, 170, text="السورة:", font=("Arial", 14), fill="white")
        self.sura_var = StringVar()
        self.sura_cb = ttk.Combobox(self.root, textvariable=self.sura_var, width=30)
        self.sura_cb['values'] = [s["name"] for s in SURAS]
        self.sura_cb.current(0)
        self.canvas.create_window(350, 170, window=self.sura_cb)
        
        # آية البداية
        self.canvas.create_text(200, 220, text="آية البداية:", font=("Arial", 14), fill="white")
        self.verse_var = IntVar(value=1)
        self.verse_spin = Spinbox(self.root, from_=1, to=286, textvariable=self.verse_var, width=5)
        self.canvas.create_window(350, 220, window=self.verse_spin)
        
        # عدد الآيات
        self.canvas.create_text(200, 270, text="عدد الآيات (1-10):", font=("Arial", 14), fill="white")
        self.count_var = IntVar(value=1)
        self.count_spin = Spinbox(self.root, from_=1, to=10, textvariable=self.count_var, width=5)
        self.canvas.create_window(350, 270, window=self.count_spin)
        
        # زر التصدير
        self.export_btn_id = self.canvas.create_image(315, 350, image=self.export_btn, anchor="nw")
        self.canvas.tag_bind(self.export_btn_id, "<Enter>", lambda e: 
                            self.canvas.itemconfig(self.export_btn_id, image=self.export_btn_hover))
        self.canvas.tag_bind(self.export_btn_id, "<Leave>", lambda e: 
                            self.canvas.itemconfig(self.export_btn_id, image=self.export_btn))
        self.canvas.tag_bind(self.export_btn_id, "<Button-1>", lambda e: self.start_generation())
    
    def start_generation(self):
        # التحقق من المدخلات
        try:
            qari = self.qari_var.get()
            sura_index = self.sura_cb.current() + 1
            start_verse = self.verse_var.get()
            verse_count = min(10, max(1, self.count_var.get()))
        except:
            messagebox.showerror("خطأ", "الرجاء اختيار مدخلات صحيحة")
            return
        
        # بدء العملية في خيط منفصل
        threading.Thread(target=self.build_video, 
                        args=(qari, sura_index, start_verse, verse_count),
                        daemon=True).start()
    
    def clear_outputs(self):
        import shutil
        folders = ["outputs/audio", "outputs/video", "temp/backgrounds"]
        for folder in folders:
            shutil.rmtree(folder, ignore_errors=True)
            os.makedirs(folder, exist_ok=True)
    
    def trim_silence(self, audio):
        start_trim = detect_leading_silence(audio)
        end_trim = detect_leading_silence(audio.reverse())
        duration = len(audio)
        trimmed = audio[start_trim:duration-end_trim]
        return trimmed
    
    def get_verse_text(self, sura, verse):
        try:
            response = requests.get(f"http://api.quran.com/api/v3/chapters/{sura}/verses/{verse}?language=ar")
            data = response.json()
            return data["verse"]["text_uthmani"]
        except:
            return "نص الآية غير متوفر"
    
    def get_translation(self, sura, verse):
        try:
            response = requests.get(f"http://api.quran.com/api/v3/chapters/{sura}/verses/{verse}/translations/131")
            data = response.json()
            return data["translations"][0]["text"] if data["translations"] else "Translation unavailable"
        except:
            return "Translation unavailable"
    
    def download_background_video(self):
        if not self.api_keys:
            return None
        
        api_key = random.choice(self.api_keys)
        headers = {"Authorization": api_key}
        query = random.choice(["nature", "abstract", "religious", "calm"])
        
        try:
            response = requests.get(
                f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait",
                headers=headers
            )
            video_data = response.json()
            if video_data.get("videos"):
                video_file = video_data["videos"][0]["video_files"][0]["link"]
                local_path = f"temp/backgrounds/{video_file.split('/')[-1]}"
                with open(local_path, 'wb') as f:
                    f.write(requests.get(video_file).content)
                return local_path
        except:
            pass
        return None
    
    def build_video(self, qari, sura, start_verse, verse_count):
        self.progress['value'] = 0
        self.clear_outputs()
        
        clips = []
        total_verses = verse_count
        current_progress = 0
        
        for i in range(verse_count):
            verse_num = start_verse + i
            
            # تحميل الصوت
            audio_url = f"http://everyayah.com/data/{qari}/{sura:03d}{verse_num:03d}.mp3"
            audio_path = f"outputs/audio/{sura}_{verse_num}.mp3"
            
            try:
                with open(audio_path, 'wb') as f:
                    f.write(requests.get(audio_url).content)
                
                # معالجة الصوت
                audio = AudioSegment.from_file(audio_path, format="mp3")
                trimmed_audio = self.trim_silence(audio)
                trimmed_audio.export(audio_path, format="mp3")
            except:
                messagebox.showerror("خطأ", "فشل تحميل الصوت")
                return
            
            # جلب النصوص
            arabic_text = self.get_verse_text(sura, verse_num)
            english_text = self.get_translation(sura, verse_num)
            
            # تحميل خلفية الفيديو
            bg_path = self.download_background_video()
            if not bg_path:
                bg_path = "background.png"  # استخدام الخلفية الافتراضية
            
            # إنشاء الفيديو
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            if bg_path.endswith('.mp4'):
                bg_clip = VideoFileClip(bg_path).subclip(0, duration)
            else:
                bg_clip = ImageClip(bg_path).set_duration(duration)
            
            # إضافة النصوص
            txt_clip_arabic = TextClip(
                arabic_text, 
                fontsize=50, 
                color='white', 
                font="font.ttf",
                size=(800, 200),
                method='caption',
                align='center'
            ).set_position(('center', 100)).set_duration(duration)
            
            txt_clip_english = TextClip(
                english_text, 
                fontsize=30, 
                color='gold', 
                font="Arial",
                size=(800, 150),
                method='caption',
                align='center'
            ).set_position(('center', 350)).set_duration(duration)
            
            # دمج العناصر
            final_clip = CompositeVideoClip([bg_clip, txt_clip_arabic, txt_clip_english])
            final_clip = final_clip.set_audio(audio_clip)
            
            # حفظ الفيديو المؤقت
            temp_video = f"outputs/video/verse_{sura}_{verse_num}.mp4"
            final_clip.write_videofile(
                temp_video, 
                codec='libx264', 
                audio_codec='aac',
                fps=24,
                logger=None
            )
            clips.append(VideoFileClip(temp_video))
            
            # تحديث شريط التقدم
            current_progress += 100 / total_verses
            self.progress['value'] = current_progress
        
        # دمج المقاطع
        if clips:
            final_video = concatenate_videoclips(clips)
            final_video.write_videofile(
                "final_video.mp4",
                codec='libx264',
                audio_codec='aac',
                fps=24
            )
            messagebox.showinfo("تم", "تم إنشاء الفيديو بنجاح!")
        self.progress['value'] = 0

# تشغيل التطبيق
if __name__ == "__main__":
    root = Tk()
    app = QuranVideoGenerator(root)
    root.mainloop()