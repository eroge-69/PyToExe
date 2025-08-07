import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog, messagebox
import pygame
import threading
import os
import sys
import tempfile
from PIL import Image, ImageTk

class VideoPlayerWithMusicRemover:
    def __init__(self):
        self.root = Tk()
        self.root.title("مشغل الفيديو مع إزالة الموسيقى - v1.0")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        self.video_path = None
        self.cap = None
        self.is_playing = False
        self.is_paused = False
        self.temp_files = []
        
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except:
            messagebox.showerror("خطأ", "فشل في تهيئة نظام الصوت")
        
        self.setup_ui()
        
    def setup_ui(self):
        title_label = Label(
            self.root, 
            text="مشغل الفيديو مع إزالة الموسيقى",
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=10)
        

        control_frame = Frame(self.root, bg='#34495e')
        control_frame.pack(pady=10, padx=20, fill=X)

        btn_style = {
            'font': ('Arial', 10, 'bold'),
            'bg': '#3498db',
            'fg': 'white',
            'relief': 'flat',
            'padx': 15,
            'pady': 5
        }
        
        Button(control_frame, text="?? اختر فيديو", command=self.select_video, **btn_style).pack(side=LEFT, padx=5)
        Button(control_frame, text="?? تشغيل", command=self.play_video, **btn_style).pack(side=LEFT, padx=5)
        Button(control_frame, text="?? إيقاف مؤقت", command=self.pause_video, **btn_style).pack(side=LEFT, padx=5)
        Button(control_frame, text="?? إيقاف", command=self.stop_video, **btn_style).pack(side=LEFT, padx=5)
        
        settings_frame = Frame(self.root, bg='#34495e')
        settings_frame.pack(pady=10, padx=20, fill=X)
        
        Label(
            settings_frame, 
            text="قوة إزالة الموسيقى:",
            font=('Arial', 10),
            bg='#34495e',
            fg='white'
        ).pack(side=LEFT)
        
        self.music_removal_strength = Scale(
            settings_frame, 
            from_=0, 
            to=100, 
            orient=HORIZONTAL,
            bg='#34495e',
            fg='white',
            highlightbackground='#34495e'
        )
        self.music_removal_strength.set(70)
        self.music_removal_strength.pack(side=LEFT, padx=10)
        

        progress_frame = Frame(self.root, bg='#2c3e50')
        progress_frame.pack(pady=5, padx=20, fill=X)
        
        self.progress_var = StringVar()
        self.progress_var.set("00:00 / 00:00")
        Label(
            progress_frame,
            textvariable=self.progress_var,
            font=('Arial', 10),
            bg='#2c3e50',
            fg='white'
        ).pack()

        video_container = Frame(self.root, bg='black', relief=SUNKEN, bd=2)
        video_container.pack(pady=20, padx=20, expand=True, fill=BOTH)
        
        self.video_frame = Label(
            video_container, 
            bg="black", 
            text="اختر ملف فيديو للبدء",
            fg='white',
            font=('Arial', 14)
        )
        self.video_frame.pack(expand=True, fill=BOTH)
        

        status_frame = Frame(self.root, bg='#34495e')
        status_frame.pack(side=BOTTOM, fill=X)
        
        self.status_var = StringVar()
        self.status_var.set("جاهز")
        Label(
            status_frame,
            textvariable=self.status_var,
            font=('Arial', 9),
            bg='#34495e',
            fg='white'
        ).pack(side=LEFT, padx=10, pady=5)
        
    def select_video(self):
        self.video_path = filedialog.askopenfilename(
            title="اختر ملف فيديو",
            filetypes=[
                ("جميع ملفات الفيديو", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("MP4 files", "*.mp4"),
                ("AVI files", "*.avi"),
                ("MOV files", "*.mov"),
                ("جميع الملفات", "*.*")
            ]
        )
        
        if self.video_path:
            self.status_var.set(f"تم اختيار: {os.path.basename(self.video_path)}")
            
    def remove_music_from_audio(self, audio_data):
        """إزالة الموسيقى من الصوت"""
        try:
            if len(audio_data.shape) > 1 and audio_data.shape[1] >= 2:
                left_channel = audio_data[:, 0]
                right_channel = audio_data[:, 1]
                

                vocal_isolated = left_channel - right_channel
                

                strength = self.music_removal_strength.get() / 100.0
                processed_left = vocal_isolated * strength + left_channel * (1 - strength)
                processed_right = vocal_isolated * strength + right_channel * (1 - strength)
                
                return np.column_stack([processed_left, processed_right])
            else:
                return audio_data
                
        except Exception as e:
            print(f"خطأ في معالجة الصوت: {e}")
            return audio_data
    
    def play_video(self):
        if not self.video_path or not os.path.exists(self.video_path):
            messagebox.showerror("خطأ", "يرجى اختيار ملف فيديو صحيح")
            return
            
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.status_var.set("تشغيل...")
            return
            
        self.stop_video()
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                messagebox.showerror("خطأ", "فشل في فتح ملف الفيديو")
                return
                
            self.is_playing = True
            self.status_var.set("جاري التحميل...")
            
           
            video_thread = threading.Thread(target=self.video_loop)
            video_thread.daemon = True
            video_thread.start()
            
            audio_thread = threading.Thread(target=self.audio_loop)
            audio_thread.daemon = True
            audio_thread.start()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التشغيل: {str(e)}")
            
    def pause_video(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.status_var.set("متوقف مؤقتاً")
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.status_var.set("تشغيل...")
    
    def video_loop(self):
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        frame_delay = int(1000 / fps)
        
        while self.is_playing and self.cap.isOpened():
            if not self.is_paused:
                ret, frame = self.cap.read()
                if not ret:
                    break
                    

                height, width = frame.shape[:2]
                max_width, max_height = 640, 480
                
                if width > max_width or height > max_height:
                    scale = min(max_width/width, max_height/height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
           
                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(img)
                
                self.video_frame.configure(image=img_tk, text="")
                self.video_frame.image = img_tk
                
            self.root.after(frame_delay)
            
    def audio_loop(self):
        try:
     
            import moviepy.editor as mp
            
            video = mp.VideoFileClip(self.video_path)
            
            if video.audio is not None:
             
                temp_audio = tempfile.mktemp(suffix='.wav')
                self.temp_files.append(temp_audio)
                
           
                audio_clip = video.audio
                audio_clip.write_audiofile(temp_audio, verbose=False, logger=None)
                
           
                if self.music_removal_strength.get() > 0:
                    import librosa
                    import soundfile as sf
                    
                  
                    audio_data, sample_rate = librosa.load(temp_audio, sr=None, mono=False)
                    
                    if audio_data.ndim == 1:
                        audio_data = np.expand_dims(audio_data, axis=1)
                    else:
                        audio_data = audio_data.T
                    
            
                    processed_audio = self.remove_music_from_audio(audio_data)
                    
               
                    processed_temp = tempfile.mktemp(suffix='.wav')
                    self.temp_files.append(processed_temp)
                    sf.write(processed_temp, processed_audio, sample_rate)
                    
              
                    pygame.mixer.music.load(processed_temp)
                else:
               
                    pygame.mixer.music.load(temp_audio)
                
                pygame.mixer.music.play()
                self.status_var.set("تشغيل...")
                
                video.close()
                audio_clip.close()
                
        except ImportError:
            messagebox.showerror("خطأ", "مكتبات معالجة الصوت غير متوفرة")
        except Exception as e:
            print(f"خطأ في معالجة الصوت: {e}")
            self.status_var.set("خطأ في الصوت")
    
    def stop_video(self):
        self.is_playing = False
        self.is_paused = False
        
        if self.cap:
            self.cap.release()
            
        try:
            pygame.mixer.music.stop()
        except:
            pass

        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        self.temp_files.clear()
        
 
        self.video_frame.configure(image="", text="اختر ملف فيديو للبدء")
        self.video_frame.image = None
        self.progress_var.set("00:00 / 00:00")
        self.status_var.set("متوقف")
            
    def on_closing(self):
        self.stop_video()
        self.root.destroy()
        
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoPlayerWithMusicRemover()
    app.run()
