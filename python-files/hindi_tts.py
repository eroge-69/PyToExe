import tkinter as tk
from tkinter import filedialog, messagebox
import pyttsx3
import librosa
import numpy as np
import json
import os

class HindiTTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hindi TTS with Voice Profile")
        self.root.geometry("600x400")
        
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        
        # Voice profile storage
        self.voice_profile = {"pitch": 150, "rate": 150}  # Default values
        self.profile_file = "voice_profile.json"
        
        # Load existing voice profile if available
        self.load_voice_profile()
        
        # GUI Elements
        self.label = tk.Label(root, text="हिंदी टेक्स्ट दर्ज करें:", font=("Arial", 14))
        self.label.pack(pady=10)
        
        self.text_area = tk.Text(root, height=10, width=50, font=("Arial", 12))
        self.text_area.pack(pady=10)
        
        self.upload_button = tk.Button(root, text="ऑडियो फाइल अपलोड करें", command=self.upload_audio, font=("Arial", 12))
        self.upload_button.pack(pady=5)
        
        self.convert_button = tk.Button(root, text="ऑडियो में कन्वर्ट करें", command=self.convert_to_speech, font=("Arial", 12))
        self.convert_button.pack(pady=5)
        
        self.save_audio_button = tk.Button(root, text="ऑडियो फाइल सेव करें", command=self.save_audio, font=("Arial", 12))
        self.save_audio_button.pack(pady=5)
        
        self.save_profile_button = tk.Button(root, text="वॉइस प्रोफाइल सेव करें", command=self.save_voice_profile, font=("Arial", 12))
        self.save_profile_button.pack(pady=5)
        
        self.output_file = "output.wav"
        
    def upload_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav *.mp3")])
        if file_path:
            try:
                # Analyze audio file
                y, sr = librosa.load(file_path)
                pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
                pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 150
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                
                # Store in voice profile
                self.voice_profile["pitch"] = pitch
                self.voice_profile["rate"] = int(tempo)
                
                messagebox.showinfo("सफलता", f"ऑडियो विश्लेषण पूरा! पिच: {pitch:.2f}, रेट: {int(tempo)}")
            except Exception as e:
                messagebox.showerror("त्रुटि", f"ऑडियो विश्लेषण में त्रुटि: {str(e)}")
    
    def save_voice_profile(self):
        try:
            with open(self.profile_file, 'w') as f:
                json.dump(self.voice_profile, f)
            messagebox.showinfo("सफलता", "वॉइस प्रोफाइल सेव हो गया!")
        except Exception as e:
            messagebox.showerror("त्रुटि", f"वॉइस प्रोफाइल सेव करने में त्रुटि: {str(e)}")
    
    def load_voice_profile(self):
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, 'r') as f:
                    self.voice_profile = json.load(f)
            except Exception as e:
                messagebox.showwarning("चेतावनी", f"वॉइस प्रोफाइल लोड करने में त्रुटि: {str(e)}")
    
    def convert_to_speech(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("चेतावनी", "कृपया कुछ टेक्स्ट दर्ज करें!")
            return
        
        try:
            # Configure TTS engine
            self.engine.setProperty('voice', 'hindi')
            self.engine.setProperty('rate', self.voice_profile["rate"])
            # pyttsx3 doesn't directly support pitch; using rate as proxy
            self.engine.say(text)
            self.engine.runAndWait()
            messagebox.showinfo("सफलता", "टेक्स्ट को ऑडियो में कन्वर्ट कर दिया गया!")
        except Exception as e:
            messagebox.showerror("त्रुटि", f"कन्वर्जन में त्रुटि: {str(e)}")
    
    def save_audio(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("चेतावनी", "कृपया कुछ टेक्स्ट दर्ज करें!")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if file_path:
            try:
                self.engine.setProperty('voice', 'hindi')
                self.engine.setProperty('rate', self.voice_profile["rate"])
                self.engine.save_to_file(text, file_path)
                self.engine.runAndWait()
                messagebox.showinfo("सफलता", f"ऑडियो फाइल {file_path} के रूप में सेव की गई!")
            except Exception as e:
                messagebox.showerror("त्रुटि", f"ऑडियो सेव करने में त्रुटि: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HindiTTSApp(root)
    root.mainloop()