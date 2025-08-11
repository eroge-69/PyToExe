import os
import threading
import requests
import json
import random
import platform
import shutil
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.lang import Builder
from pydub import AudioSegment
from pydub.silence import detect_leading_silence
from moviepy.editor import *
import imageio
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from PIL import Image as PILImage, ImageDraw, ImageFont

# تهيئة مسارات المكتبات
os.environ["FFMPEG_BINARY"] = "ffmpeg"
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg"

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

# تحميل مفاتيح Pexels API
try:
    with open('pexels.txt', 'r') as f:
        API_KEYS = [line.strip() for line in f.readlines() if line.strip()]
except:
    API_KEYS = []

# إنشاء خلفية افتراضية إذا لم توجد
if not os.path.exists("background.png"):
    try:
        # إنشاء خلفية إسلامية بسيطة
        width, height = 1920, 1080
        bg_color = (5, 20, 40)  # لون أزرق داكن
        
        image = PILImage.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # إضافة زخارف إسلامية بسيطة
        draw.rectangle([(0, height-100), (width, height)], fill=(0, 80, 60))  # شريط سفلي
        
        # إضافة نص زخرفي (اختياري)
        try:
            font = ImageFont.truetype("arial.ttf", 120)
            text = "بسم الله الرحمن الرحيم"
            reshaped_text = reshape(text)
            bidi_text = get_display(reshaped_text)
            w, h = draw.textsize(bidi_text, font=font)
            draw.text(((width-w)/2, (height-h)/2), bidi_text, font=font, fill=(255, 255, 255, 50))
        except:
            pass
        
        image.save("background.png", quality=85, optimize=True)
    except Exception as e:
        print(f"Error creating default background: {e}")

Builder.load_string('''
<MainScreen>:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    
    canvas.before:
        Color:
            rgba: (0.05, 0.1, 0.2, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    
    ScrollView:
        size_hint_y: None
        height: root.height - 50
        do_scroll_x: False
        do_scroll_y: True
        
        GridLayout:
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            padding: 10
            spacing: 15
            
            # شعار التطبيق
            Image:
                source: 'logo.png' if os.path.exists('logo.png') else ''
                size_hint: (1, None)
                height: 100 if os.path.exists('logo.png') else 0
                allow_stretch: True
            
            # اختيار القارئ
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: 50
                spacing: 10
                
                Label:
                    text: 'القارئ:'
                    size_hint_x: 0.3
                    font_size: 18
                    color: (1, 1, 1, 1)
                    halign: 'right'
                    valign: 'middle'
                    text_size: self.size
                
                Spinner:
                    id: qari_spinner
                    text: QURRA[0]
                    values: QURRA
                    size_hint_x: 0.7
                    font_size: 18
                    background_color: (0.2, 0.4, 0.6, 1)
            
            # اختيار السورة
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: 50
                spacing: 10
                
                Label:
                    text: 'السورة:'
                    size_hint_x: 0.3
                    font_size: 18
                    color: (1, 1, 1, 1)
                    halign: 'right'
                    valign: 'middle'
                    text_size: self.size
                
                Spinner:
                    id: sura_spinner
                    text: SURAS[0]['name']
                    values: [s['name'] for s in SURAS]
                    size_hint_x: 0.7
                    font_size: 18
                    background_color: (0.2, 0.4, 0.6, 1)
            
            # آية البداية
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: 50
                spacing: 10
                
                Label:
                    text: 'آية البداية:'
                    size_hint_x: 0.3
                    font_size: 18
                    color: (1, 1, 1, 1)
                    halign: 'right'
                    valign: 'middle'
                    text_size: self.size
                
                TextInput:
                    id: verse_start
                    text: '1'
                    size_hint_x: 0.7
                    font_size: 18
                    input_filter: 'int'
                    multiline: False
                    background_color: (0.2, 0.4, 0.6, 1)
            
            # عدد الآيات
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: 50
                spacing: 10
                
                Label:
                    text: 'عدد الآيات:'
                    size_hint_x: 0.3
                    font_size: 18
                    color: (1, 1, 1, 1)
                    halign: 'right'
                    valign: 'middle'
                    text_size: self.size
                
                TextInput:
                    id: verse_count
                    text: '1'
                    size_hint_x: 0.7
                    font_size: 18
                    input_filter: 'int'
                    multiline: False
                    background_color: (0.2, 0.4, 0.6, 1)
            
            # زر التصدير
            Button:
                id: export_btn
                text: 'إنشاء الفيديو'
                size_hint_y: None
                height: 60
                font_size: 22
                background_color: (0, 0.6, 0.3, 1)
                on_press: root.start_generation()
            
            # شريط التقدم
            ProgressBar:
                id: progress_bar
                size_hint_y: None
                height: 30
                max: 100
                value: root.progress_value
            
            # حالة التوليد
            Label:
                id: status_label
                text: root.status_text
                size_hint_y: None
                height: 40
                font_size: 16
                color: (1, 1, 1, 1)
                halign: 'center'
                valign: 'middle'
                text_size: self.size
    
    # روابط التواصل الاجتماعي
    BoxLayout:
        size_hint_y: None
        height: 50
        spacing: 10
        
        Button:
            text: 'YouTube'
            size_hint_x: 0.25
            background_color: (1, 0, 0, 1)
            on_press: root.open_link('youtube')
        
        Button:
            text: 'Instagram'
            size_hint_x: 0.25
            background_color: (0.8, 0.2, 0.6, 1)
            on_press: root.open_link('instagram')
        
        Button:
            text: 'Twitter'
            size_hint_x: 0.25
            background_color: (0.2, 0.6, 1, 1)
            on_press: root.open_link('twitter')
        
        Button:
            text: 'Facebook'
            size_hint_x: 0.25
            background_color: (0.2, 0.4, 0.8, 1)
            on_press: root.open_link('facebook')
''')

class MainScreen(BoxLayout):
    progress_value = NumericProperty(0)
    status_text = StringProperty("جاهز للبدء")
    is_generating = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        })
        
    def open_link(self, platform):
        links = {
            "youtube": "https://www.youtube.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.twitter.com",
            "facebook": "https://www.facebook.com"
        }
        import webbrowser
        webbrowser.open(links[platform])
    
    def start_generation(self):
        if self.is_generating:
            return
            
        try:
            qari = self.ids.qari_spinner.text
            sura_name = self.ids.sura_spinner.text
            sura_index = next((s["number"] for s in SURAS if s["name"] == sura_name), 0)
            start_verse = int(self.ids.verse_start.text)
            verse_count = min(10, max(1, int(self.ids.verse_count.text)))
        except Exception as e:
            self.show_error("خطأ", "الرجاء اختيار مدخلات صحيحة")
            return
        
        if start_verse < 1:
            self.show_error("خطأ", "رقم الآية يجب أن يكون 1 على الأقل")
            return
        
        self.is_generating = True
        self.ids.export_btn.disabled = True
        self.ids.export_btn.text = "جارٍ التوليد..."
        self.status_text = "جارٍ بدء عملية التوليد"
        self.progress_value = 0
        
        threading.Thread(
            target=self.build_video, 
            args=(qari, sura_index, start_verse, verse_count),
            daemon=True
        ).start()
    
    def show_error(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size=18))
        btn = Button(text='حسناً', size_hint_y=None, height=40)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def show_success(self, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, font_size=18))
        btn = Button(text='حسناً', size_hint_y=None, height=40)
        popup = Popup(title='تم بنجاح', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        content.add_widget(btn)
        popup.open()
    
    def clear_outputs(self):
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
            response = self.session.get(
                f"http://api.quran.com/api/v3/chapters/{sura}/verses/{verse}?language=ar",
                timeout=15
            )
            data = response.json()
            
            if 'verse' in data and 'text_uthmani' in data['verse']:
                arabic_text = data['verse']['text_uthmani']
                
                try:
                    reshaped = reshape(arabic_text)
                    bidi_text = get_display(reshaped)
                    fixed_text = ' '.join(bidi_text.split())
                    return fixed_text
                except Exception as e:
                    print(f"Error processing Arabic text: {e}")
                    return arabic_text
                
            return "نص الآية غير متوفر"
        except Exception as e:
            print(f"Error fetching verse: {e}")
            return "نص الآية غير متوفر"
    
    def get_translation(self, sura, verse):
        try:
            try:
                response = self.session.get(
                    f"https://api.quran.com/api/v4/verses/by_key/{sura}:{verse}/translations/131",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'translations' in data and len(data['translations']) > 0:
                        translation = data['translations'][0]['text']
                        return translation.replace('<i>', '').replace('</i>', '')
            except:
                pass
            
            response = self.session.get(
                f"http://api.alquran.cloud/v1/ayah/{sura}:{verse}/en.asad",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'text' in data['data']:
                    return data['data']['text']
                    
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching translation: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        return "Translation unavailable"
    
    def download_background_video(self):
        if not API_KEYS:
            return None
        
        api_key = random.choice(API_KEYS)
        headers = {"Authorization": api_key}
        
        queries = [
            "nature landscape", "mountain river", "desert sunset", 
            "forest stream", "ocean waves", "islamic architecture",
            "mountain sunset", "green valley", "starry night"
        ]
        query = random.choice(queries)
        
        try:
            response = self.session.get(
                f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=landscape&size=large",
                headers=headers,
                timeout=20
            )
            video_data = response.json()
            if video_data.get("videos"):
                video_files = video_data["videos"][0]["video_files"]
                hd_videos = [vf for vf in video_files if vf.get('height', 0) >= 720]
                
                if hd_videos:
                    best_quality = max(hd_videos, key=lambda x: x.get('width', 0) * x.get('height', 0))
                    video_url = best_quality['link']
                else:
                    video_url = video_files[0]['link']
                
                local_path = f"temp/backgrounds/{video_url.split('/')[-1].split('?')[0]}"
                with open(local_path, 'wb') as f:
                    video_response = self.session.get(video_url, stream=True)
                    for chunk in video_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return local_path
        except Exception as e:
            print(f"Error downloading background: {e}")
        return None
    
    def create_text_clip(self, text, fontsize, color, font, size, position, duration):
        try:
            if not isinstance(text, str):
                text = str(text)
            
            if any('\u0600' <= char <= '\u06FF' for char in text):
                try:
                    reshaped = reshape(text)
                    bidi_text = get_display(reshaped)
                    text = ' '.join(bidi_text.split())
                except Exception as e:
                    print(f"Arabic text processing error: {e}")
            
            arabic_fontsize = 35 if any('\u0600' <= char <= '\u06FF' for char in text) else fontsize
            
            return TextClip(
                text,
                fontsize=arabic_fontsize,
                color=color,
                font=font,
                size=size,
                method='pango',
                align='center',
                stroke_color='black',
                stroke_width=1,
                kerning=2,
                print_cmd=False
            ).set_position(position).set_duration(duration)
            
        except Exception as e:
            print(f"Error creating text clip: {e}")
            return TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font=font,
                size=size,
                method='label',
                align='center',
                print_cmd=False
            ).set_position(position).set_duration(duration)
    
    def enhance_video_quality(self, clip):
        try:
            return clip.fx(vfx.sharpen, factor=0.5)
        except:
            return clip
    
    def update_progress(self, value, text):
        self.progress_value = value
        self.status_text = text
    
    def build_video(self, qari, sura, start_verse, verse_count):
        Clock.schedule_once(lambda dt: self.clear_outputs())
        
        clips = []
        total_verses = verse_count
        current_progress = 0
        
        for i in range(verse_count):
            verse_num = start_verse + i
            
            Clock.schedule_once(
                lambda dt, v=verse_num: self.update_progress(
                    current_progress, 
                    f"جارٍ معالجة الآية {v}"
                )
            )
            
            audio_url = f"http://everyayah.com/data/{qari}/{sura:03d}{verse_num:03d}.mp3"
            audio_path = f"outputs/audio/{sura}_{verse_num}.mp3"
            
            try:
                with open(audio_path, 'wb') as f:
                    response = self.session.get(audio_url, timeout=20)
                    if response.status_code == 200:
                        f.write(response.content)
                    else:
                        raise Exception(f"HTTP Error: {response.status_code}")
                
                audio = AudioSegment.from_file(audio_path, format="mp3")
                trimmed_audio = self.trim_silence(audio)
                trimmed_audio.export(audio_path, format="mp3")
            except Exception as e:
                print(f"Error processing audio: {e}")
                Clock.schedule_once(
                    lambda dt: self.show_error("خطأ", f"فشل تحميل الصوت للآية {verse_num}")
                )
                self.finish_generation(False)
                return
            
            arabic_text = self.get_verse_text(sura, verse_num)
            english_text = self.get_translation(sura, verse_num)
            
            bg_path = self.download_background_video()
            if not bg_path:
                bg_path = "background.png"
            
            try:
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                
                if bg_path.endswith('.mp4') or bg_path.endswith('.mov'):
                    try:
                        bg_clip = VideoFileClip(bg_path).subclip(0, duration)
                    except:
                        bg_clip = ImageClip("background.png").set_duration(duration)
                    
                    bg_clip = bg_clip.resize((930, 820))
                else:
                    bg_clip = ImageClip(bg_path).set_duration(duration)
                    bg_clip = bg_clip.resize((930, 820))
                
                txt_clip_arabic = self.create_text_clip(
                    text=arabic_text,
                    fontsize=35,
                    color='white',
                    font="font.ttf",
                    size=(800, 150),
                    position=('center', 100),
                    duration=duration
                )
                
                txt_clip_english = self.create_text_clip(
                    text=english_text,
                    fontsize=20,
                    color='gold',
                    font="Arial",
                    size=(800, 100),
                    position=('center', 300),
                    duration=duration
                )
                
                final_clip = CompositeVideoClip([bg_clip, txt_clip_arabic, txt_clip_english])
                final_clip = final_clip.set_audio(audio_clip)
                
                final_clip = self.enhance_video_quality(final_clip)
                
                temp_video = f"outputs/video/verse_{sura}_{verse_num}.mp4"
                final_clip.write_videofile(
                    temp_video, 
                    codec='libx264', 
                    audio_codec='aac',
                    fps=24,
                    threads=4,
                    bitrate="8000k",
                    preset='slow',
                    logger=None
                )
                clips.append(VideoFileClip(temp_video))
                
                current_progress = int((i + 1) * 100 / total_verses)
                Clock.schedule_once(
                    lambda dt: self.update_progress(
                        current_progress, 
                        f"تم معالجة الآية {verse_num} من {verse_count}"
                    )
                )
                
            except Exception as e:
                print(f"Error creating video clip: {e}")
                Clock.schedule_once(
                    lambda dt: self.show_error("خطأ", f"فشل إنشاء الفيديو للآية {verse_num}")
                )
                self.finish_generation(False)
                return
        
        if clips:
            try:
                Clock.schedule_once(lambda dt: self.update_progress(95, "جارٍ دمج مقاطع الفيديو"))
                
                final_video = concatenate_videoclips(clips)
                output_path = "final_video.mp4"
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    fps=24,
                    threads=4,
                    bitrate="10000k",
                    preset='medium'
                )
                
                Clock.schedule_once(
                    lambda dt: self.show_success(f"تم إنشاء الفيديو بنجاح!\nتم حفظه في: {output_path}")
                )
                
            except Exception as e:
                print(f"Error concatenating videos: {e}")
                Clock.schedule_once(
                    lambda dt: self.show_error("خطأ", "فشل دمج مقاطع الفيديو")
                )
        
        self.finish_generation(True)
    
    def finish_generation(self, success):
        self.is_generating = False
        Clock.schedule_once(lambda dt: setattr(self.ids.export_btn, 'disabled', False))
        self.ids.export_btn.text = "إنشاء الفيديو"
        
        if success:
            self.progress_value = 100
            self.status_text = "تم الانتهاء بنجاح"
        else:
            self.status_text = "حدث خطأ أثناء التوليد"


class QuranVideoApp(App):
    def build(self):
        if platform.system() != 'android':
            Window.size = (360, 640)
        
        self.title = "مولد الفيديوهات القرآنية"
        return MainScreen()


if __name__ == "__main__":
    QuranVideoApp().run()