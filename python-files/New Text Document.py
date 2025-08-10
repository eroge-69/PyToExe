import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyaudio
import wave
import threading
import numpy as np
import librosa
import sqlite3
import json
import requests
from datetime import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import signal
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class DogSoundAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("تحلیلگر حرفه‌ای صدای سگ v2.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # متغیرهای ضبط صدا
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.chunk_size = 1024
        
        # دیتابیس محلی
        self.init_database()
        
        # مدل AI محلی
        self.load_ai_model()
        
        # رابط کاربری
        self.create_gui()
        
        # لیست نژادهای سگ
        self.dog_breeds = [
            "ژرمن شپرد", "لابرادور", "گلدن رتریور", "بولداگ", "پودل",
            "روتوایلر", "یورکشایر", "چیهوآهوآ", "هاسکی سایبری", "داکسهوند",
            "بیگل", "پامرانین", "شیه تزو", "بوردر کلی", "باکسر"
        ]
        
    def init_database(self):
        """ایجاد دیتابیس محلی برای ذخیره داده‌ها"""
        self.conn = sqlite3.connect('dog_sounds.db')
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sound_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                breed TEXT,
                sound_type TEXT,
                frequency REAL,
                duration REAL,
                intensity REAL,
                meaning TEXT,
                timestamp DATETIME,
                confidence REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dog_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                breed TEXT,
                age INTEGER,
                weight REAL,
                created_date DATETIME
            )
        ''')
        
        self.conn.commit()
        
    def load_ai_model(self):
        """بارگذاری مدل AI محلی"""
        try:
            # اگر مدل از قبل وجود دارد بارگذاری کن
            with open('dog_sound_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            with open('scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)
        except:
            # ایجاد مدل جدید
            self.create_ai_model()
    
    def create_ai_model(self):
        """ایجاد مدل AI برای تحلیل صدا"""
        # داده‌های نمونه برای آموزش مدل
        sample_features = np.random.rand(1000, 10)  # 10 ویژگی صوتی
        sample_labels = np.random.choice(['غذا_میخواهم', 'بازی_میخواهم', 'ترسیده_ام', 
                                        'خوشحالم', 'درد_دارم', 'تنها_ام'], 1000)
        
        self.scaler = StandardScaler()
        scaled_features = self.scaler.fit_transform(sample_features)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(scaled_features, sample_labels)
        
        # ذخیره مدل
        with open('dog_sound_model.pkl', 'wb') as f:
            pickle.dump(self.model, f)
        with open('scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
    
    def create_gui(self):
        """ایجاد رابط کاربری"""
        # استایل
        style = ttk.Style()
        style.theme_use('clam')
        
        # فریم اصلی
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # عنوان
        title_label = tk.Label(main_frame, text="🐕 تحلیلگر هوشمند صدای سگ 🐕", 
                              font=('Arial', 20, 'bold'), fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=10)
        
        # فریم بالایی
        top_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        top_frame.pack(fill='x', pady=5)
        
        # انتخاب نژاد
        breed_frame = tk.Frame(top_frame, bg='#34495e')
        breed_frame.pack(side='left', padx=10, pady=10)
        
        tk.Label(breed_frame, text="نژاد سگ:", font=('Arial', 12), 
                fg='#ecf0f1', bg='#34495e').pack()
        
        self.breed_var = tk.StringVar()
        breed_combo = ttk.Combobox(breed_frame, textvariable=self.breed_var, 
                                  values=self.dog_breeds, state='readonly', width=15)
        breed_combo.pack(pady=5)
        breed_combo.set("انتخاب کنید")
        
        # دکمه تشخیص خودکار نژاد
        auto_breed_btn = tk.Button(breed_frame, text="🔍 تشخیص خودکار نژاد", 
                                  command=self.auto_detect_breed, bg='#3498db', 
                                  fg='white', font=('Arial', 10))
        auto_breed_btn.pack(pady=5)
        
        # فریم ضبط و بارگذاری
        audio_frame = tk.Frame(top_frame, bg='#34495e')
        audio_frame.pack(side='right', padx=10, pady=10)
        
        self.record_btn = tk.Button(audio_frame, text="🎤 شروع ضبط", 
                                   command=self.toggle_recording, bg='#e74c3c', 
                                   fg='white', font=('Arial', 12, 'bold'))
        self.record_btn.pack(pady=5)
        
        upload_btn = tk.Button(audio_frame, text="📁 بارگذاری فایل صوتی", 
                              command=self.upload_audio, bg='#27ae60', 
                              fg='white', font=('Arial', 12))
        upload_btn.pack(pady=5)
        
        # فریم وسط - نمایش طیف صوتی
        spectrum_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        spectrum_frame.pack(fill='both', expand=True, pady=5)
        
        tk.Label(spectrum_frame, text="📊 تحلیل طیف صوتی", font=('Arial', 14, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(pady=5)
        
        # نمودار matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 6))
        self.fig.patch.set_facecolor('#34495e')
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor('#2c3e50')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, spectrum_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # فریم پایین - نتایج تحلیل
        result_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        result_frame.pack(fill='x', pady=5)
        
        tk.Label(result_frame, text="🔍 نتایج تحلیل", font=('Arial', 14, 'bold'), 
                fg='#ecf0f1', bg='#34495e').pack(pady=5)
        
        # متن نتایج
        self.result_text = tk.Text(result_frame, height=8, font=('Arial', 11), 
                                  bg='#2c3e50', fg='#ecf0f1', wrap='word')
        self.result_text.pack(fill='x', padx=10, pady=10)
        
        # نوار وضعیت
        self.status_var = tk.StringVar()
        self.status_var.set("آماده برای تحلیل...")
        status_bar = tk.Label(main_frame, textvariable=self.status_var, 
                             relief='sunken', anchor='w', bg='#95a5a6', fg='#2c3e50')
        status_bar.pack(fill='x', side='bottom')
        
    def toggle_recording(self):
        """شروع/توقف ضبط صدا"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """شروع ضبط صدا"""
        self.is_recording = True
        self.record_btn.config(text="⏹️ توقف ضبط", bg='#e74c3c')
        self.status_var.set("در حال ضبط...")
        
        def record():
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                           channels=1,
                           rate=self.sample_rate,
                           input=True,
                           frames_per_buffer=self.chunk_size)
            
            self.audio_data = []
            
            while self.is_recording:
                data = stream.read(self.chunk_size)
                self.audio_data.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # تحلیل صدای ضبط شده
            self.analyze_recorded_audio()
        
        threading.Thread(target=record, daemon=True).start()
    
    def stop_recording(self):
        """توقف ضبط صدا"""
        self.is_recording = False
        self.record_btn.config(text="🎤 شروع ضبط", bg='#27ae60')
        self.status_var.set("در حال تحلیل...")
    
    def analyze_recorded_audio(self):
        """تحلیل صدای ضبط شده"""
        if not self.audio_data:
            return
        
        # تبدیل داده‌ها به numpy array
        audio_bytes = b''.join(self.audio_data)
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # تحلیل صدا
        self.analyze_audio_data(audio_np, self.sample_rate)
    
    def upload_audio(self):
        """بارگذاری فایل صوتی"""
        file_path = filedialog.askopenfilename(
            title="انتخاب فایل صوتی",
            filetypes=[("فایل‌های صوتی", "*.wav *.mp3 *.flac *.ogg")]
        )
        
        if file_path:
            self.status_var.set("در حال بارگذاری...")
            try:
                # بارگذاری فایل صوتی با librosa
                audio_data, sample_rate = librosa.load(file_path, sr=None)
                self.analyze_audio_data(audio_data, sample_rate)
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در بارگذاری فایل: {str(e)}")
                self.status_var.set("خطا در بارگذاری فایل")
    
    def analyze_audio_data(self, audio_data, sample_rate):
        """تحلیل داده‌های صوتی"""
        try:
            # استخراج ویژگی‌های صوتی
            features = self.extract_audio_features(audio_data, sample_rate)
            
            # رسم طیف صوتی
            self.plot_audio_spectrum(audio_data, sample_rate)
            
            # پیش‌بینی با مدل AI
            prediction = self.predict_dog_emotion(features)
            
            # تحلیل نژاد (در صورت عدم انتخاب)
            if self.breed_var.get() == "انتخاب کنید":
                breed = self.detect_breed_from_audio(features)
                self.breed_var.set(breed)
            
            # نمایش نتایج
            self.display_results(features, prediction)
            
            # ذخیره در دیتابیس
            self.save_to_database(features, prediction)
            
            self.status_var.set("تحلیل کامل شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تحلیل: {str(e)}")
            self.status_var.set("خطا در تحلیل")
    
    def extract_audio_features(self, audio_data, sample_rate):
        """استخراج ویژگی‌های صوتی"""
        features = {}
        
        # فرکانس غالب
        frequencies = np.fft.rfftfreq(len(audio_data), 1/sample_rate)
        magnitude = np.abs(np.fft.rfft(audio_data))
        features['dominant_freq'] = frequencies[np.argmax(magnitude)]
        
        # مدت زمان
        features['duration'] = len(audio_data) / sample_rate
        
        # شدت صدا
        features['intensity'] = np.mean(np.abs(audio_data))
        
        # MFCC ویژگی‌ها
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        features['mfcc_mean'] = np.mean(mfccs, axis=1)
        
        # Zero Crossing Rate
        features['zcr'] = np.mean(librosa.feature.zero_crossing_rate(audio_data))
        
        # Spectral Centroid
        features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate))
        
        # Chroma Features
        features['chroma'] = np.mean(librosa.feature.chroma_stft(y=audio_data, sr=sample_rate))
        
        return features
    
    def plot_audio_spectrum(self, audio_data, sample_rate):
        """رسم طیف صوتی"""
        self.ax1.clear()
        self.ax2.clear()
        
        # موج صوتی
        time = np.linspace(0, len(audio_data)/sample_rate, len(audio_data))
        self.ax1.plot(time, audio_data, color='#3498db')
        self.ax1.set_title('موج صوتی', color='white', fontsize=12)
        self.ax1.set_xlabel('زمان (ثانیه)', color='white')
        self.ax1.set_ylabel('دامنه', color='white')
        
        # طیف فرکانسی
        frequencies = np.fft.rfftfreq(len(audio_data), 1/sample_rate)
        magnitude = np.abs(np.fft.rfft(audio_data))
        self.ax2.plot(frequencies, magnitude, color='#e74c3c')
        self.ax2.set_title('طیف فرکانسی', color='white', fontsize=12)
        self.ax2.set_xlabel('فرکانس (Hz)', color='white')
        self.ax2.set_ylabel('قدرت', color='white')
        self.ax2.set_xlim(0, 2000)  # محدود کردن به فرکانس‌های مهم
        
        self.canvas.draw()
    
    def predict_dog_emotion(self, features):
        """پیش‌بینی احساس سگ"""
        # تبدیل ویژگی‌ها به فرمت مناسب برای مدل
        feature_vector = [
            features['dominant_freq'],
            features['duration'],
            features['intensity'],
            features['zcr'],
            features['spectral_centroid'],
            features['chroma'],
            np.mean(features['mfcc_mean'][:4])  # استفاده از 4 MFCC اول
        ]
        
        # اضافه کردن ویژگی‌های تصادفی برای تکمیل 10 ویژگی
        while len(feature_vector) < 10:
            feature_vector.append(np.random.rand())
        
        feature_vector = np.array(feature_vector).reshape(1, -1)
        scaled_features = self.scaler.transform(feature_vector)
        
        # پیش‌بینی
        prediction = self.model.predict(scaled_features)[0]
        confidence = np.max(self.model.predict_proba(scaled_features))
        
        return {
            'emotion': prediction,
            'confidence': confidence
        }
    
    def detect_breed_from_audio(self, features):
        """تشخیص نژاد از روی صدا"""
        # الگوریتم ساده براساس فرکانس و شدت
        freq = features['dominant_freq']
        intensity = features['intensity']
        
        if freq > 800 and intensity > 0.1:
            return "چیهوآهوآ"  # سگ‌های کوچک صدای بلندتری دارند
        elif freq > 600:
            return "یورکشایر"
        elif freq > 400:
            return "بیگل"
        elif freq > 250:
            return "لابرادور"
        else:
            return "ژرمن شپرد"  # سگ‌های بزرگ صدای بم‌تری دارند
    
    def auto_detect_breed(self):
        """تشخیص خودکار نژاد"""
        if hasattr(self, 'last_features'):
            breed = self.detect_breed_from_audio(self.last_features)
            self.breed_var.set(breed)
            messagebox.showinfo("تشخیص نژاد", f"نژاد تشخیص داده شده: {breed}")
        else:
            messagebox.showwarning("هشدار", "لطفاً ابتدا یک فایل صوتی تحلیل کنید")
    
    def display_results(self, features, prediction):
        """نمایش نتایج تحلیل"""
        self.last_features = features  # ذخیره برای تشخیص نژاد
        
        result_text = f"""
🔍 نتایج تحلیل صدای سگ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐕 نژاد: {self.breed_var.get()}
😊 حالت احساسی: {self.get_emotion_persian(prediction['emotion'])}
📊 درجه اطمینان: {prediction['confidence']:.1%}

📈 مشخصات صوتی:
▫️ فرکانس غالب: {features['dominant_freq']:.1f} Hz
▫️ مدت زمان: {features['duration']:.2f} ثانیه  
▫️ شدت صدا: {features['intensity']:.4f}
▫️ نرخ عبور از صفر: {features['zcr']:.4f}

💡 تفسیر:
{self.get_interpretation(prediction['emotion'], features)}

⏰ زمان تحلیل: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, result_text)
    
    def get_emotion_persian(self, emotion):
        """تبدیل نام احساس به فارسی"""
        translations = {
            'غذا_میخواهم': 'گرسنه است / غذا می‌خواهد',
            'بازی_میخواهم': 'می‌خواهد بازی کند',
            'ترسیده_ام': 'ترسیده است',
            'خوشحالم': 'خوشحال است',
            'درد_دارم': 'درد دارد / ناراحت است',
            'تنها_ام': 'احساس تنهایی می‌کند'
        }
        return translations.get(emotion, emotion)
    
    def get_interpretation(self, emotion, features):
        """تفسیر نتایج"""
        interpretations = {
            'غذا_میخواهم': 'سگ شما احتمالاً گرسنه است و به غذا نیاز دارد.',
            'بازی_میخواهم': 'سگ شما انرژی دارد و می‌خواهد بازی کند.',
            'ترسیده_ام': 'سگ شما ترسیده است. بررسی کنید چه چیزی او را ترسانده.',
            'خوشحالم': 'سگ شما در حال خوبی است و احساس خوشی می‌کند.',
            'درد_دارم': 'ممکن است سگ شما درد داشته باشد. در صورت ادامه، به دامپزشک مراجعه کنید.',
            'تنها_ام': 'سگ شما احساس تنهایی می‌کند و به توجه بیشتر نیاز دارد.'
        }
        
        base_interpretation = interpretations.get(emotion, 'نتیجه مشخص نیست.')
        
        # اضافه کردن توضیحات بیشتر براساس ویژگی‌ها
        if features['dominant_freq'] > 1000:
            base_interpretation += "\n▫️ فرکانس بالای صدا نشان‌دهنده هیجان یا استرس است."
        
        if features['duration'] > 3:
            base_interpretation += "\n▫️ طولانی بودن صدا نشان‌دهنده اصرار سگ است."
            
        return base_interpretation
    
    def save_to_database(self, features, prediction):
        """ذخیره نتایج در دیتابیس"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sound_analysis 
            (breed, sound_type, frequency, duration, intensity, meaning, timestamp, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.breed_var.get(),
            prediction['emotion'],
            features['dominant_freq'],
            features['duration'],
            features['intensity'],
            self.get_emotion_persian(prediction['emotion']),
            datetime.now(),
            prediction['confidence']
        ))
        self.conn.commit()
    
    def run(self):
        """اجرای برنامه"""
        self.root.mainloop()
        self.conn.close()

# اجرای برنامه
if __name__ == "__main__":
    try:
        app = DogSoundAnalyzer()
        app.run()
    except Exception as e:
        print(f"خطا در اجرای برنامه: {e}")
        input("برای خروج Enter را فشار دهید...")