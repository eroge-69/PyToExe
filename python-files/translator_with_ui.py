import json
import pyaudio
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from vosk import Model, KaldiRecognizer, SetLogLevel
from transformers import MarianMTModel, MarianTokenizer
import os
import queue
import time

class RealTimeVoiceTranslatorGUI:
    def __init__(self, root):
        # Add paragraph tracking
        self.chinese_paragraph_start = None
        self.english_paragraph_start = None
        self.current_chinese_content = ""
        self.current_english_content = ""
        self.root = root
        self.root.title("Real-time Chinese Voice Translator - 实时中文语音翻译器")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Real-time translation parameters
        self.last_partial_text = ""
        self.last_translation_time = 0
        self.translation_interval = 0.8  # Translate every 0.8 seconds
        self.min_chars_for_translation = 2  # Minimum characters before translating
        self.partial_translation_active = True
        
        # Initialize models
        self.setup_models()
        
        # Audio setup
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.current_sentence = ""
        
        # GUI setup
        self.setup_gui()
        
        # Start audio processing thread
        self.audio_thread = None
        
    def setup_models(self):
        """Load translation and VOSK models"""
        SetLogLevel(0)
        
        # Load translation model[2]
        model_dir = "./models/opus-mt-zh-en"
        if not os.path.exists(model_dir):
            print(f"❌ Translation model not found at {model_dir}")
            exit(1)
            
        print("Loading translation model...")
        self.tokenizer = MarianTokenizer.from_pretrained(model_dir, local_files_only=True)
        self.translation_model = MarianMTModel.from_pretrained(model_dir, local_files_only=True)
        
        # Load VOSK model
        vosk_model_path = "./vosk-model-cn"
        if not os.path.exists(vosk_model_path):
            print(f"❌ VOSK model not found at {vosk_model_path}")
            exit(1)
            
        print("Loading VOSK model...")
        self.vosk_model = Model(vosk_model_path)
        self.recognizer = KaldiRecognizer(self.vosk_model, 16000)
        
        print("✅ All models loaded successfully!")
    
    def setup_gui(self):
        """Create the enhanced GUI layout with real-time controls"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="实时中文语音翻译器 | Real-time Chinese Voice Translator", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Chinese text
        left_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        chinese_header = tk.Label(left_frame, text="🎤 中文识别 (Chinese Recognition)", 
                                 font=('Arial', 14, 'bold'), bg='#3498db', fg='white', pady=10)
        chinese_header.pack(fill='x')
        
        # Chinese text display with real-time indicator
        self.chinese_text = scrolledtext.ScrolledText(left_frame, font=('SimHei', 12), 
                                                     wrap=tk.WORD, bg='#f8f9fa', 
                                                     fg='#2c3e50', padx=10, pady=10)
        self.chinese_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Right panel - English text
        right_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        english_header = tk.Label(right_frame, text="🌐 英文翻译 (English Translation)", 
                                 font=('Arial', 14, 'bold'), bg='#27ae60', fg='white', pady=10)
        english_header.pack(fill='x')
        
        # English text display
        self.english_text = scrolledtext.ScrolledText(right_frame, font=('Arial', 12), 
                                                     wrap=tk.WORD, bg='#f8f9fa', 
                                                     fg='#2c3e50', padx=10, pady=10)
        self.english_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Enhanced control panel with real-time settings
        control_frame = tk.Frame(self.root, bg='#34495e', height=120)
        control_frame.pack(fill='x')
        control_frame.pack_propagate(False)
        
        # Status and real-time settings
        top_control = tk.Frame(control_frame, bg='#34495e')
        top_control.pack(fill='x', padx=20, pady=(10, 5))
        
        self.status_label = tk.Label(top_control, text="准备就绪 | Ready", 
                                    font=('Arial', 12), fg='white', bg='#34495e')
        self.status_label.pack(side='left')
        
        # Real-time translation controls
        realtime_frame = tk.Frame(top_control, bg='#34495e')
        realtime_frame.pack(side='right')
        
        tk.Label(realtime_frame, text="翻译间隔 | Translation Interval (s):", 
                 font=('Arial', 10), fg='white', bg='#34495e').pack(side='left')
        
        self.interval_var = tk.DoubleVar(value=self.translation_interval)
        interval_scale = tk.Scale(realtime_frame, from_=0.3, to=2.0, resolution=0.1,
                                 orient='horizontal', variable=self.interval_var,
                                 command=self.update_translation_interval,
                                 bg='#34495e', fg='white', length=150)
        interval_scale.pack(side='left', padx=10)
        
        # Bottom control buttons
        bottom_control = tk.Frame(control_frame, bg='#34495e')
        bottom_control.pack(fill='x', padx=20, pady=(5, 10))
        
        # Toggle partial translation
        self.partial_var = tk.BooleanVar(value=True)
        partial_check = tk.Checkbutton(bottom_control, text="实时部分翻译 | Real-time Partial Translation", 
                                      variable=self.partial_var, command=self.toggle_partial_translation,
                                      font=('Arial', 10), fg='white', bg='#34495e', 
                                      selectcolor='#34495e', activebackground='#34495e')
        partial_check.pack(side='left')
        
        # Buttons
        button_frame = tk.Frame(bottom_control, bg='#34495e')
        button_frame.pack(side='right')
        
        self.start_button = tk.Button(button_frame, text="🎤 开始监听 | Start Listening", 
                                     font=('Arial', 11, 'bold'), bg='#27ae60', fg='white',
                                     command=self.toggle_listening, padx=20, pady=5)
        self.start_button.pack(side='left', padx=5)
        
        clear_button = tk.Button(button_frame, text="🗑️ 清空 | Clear", 
                               font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                               command=self.clear_text, padx=20, pady=5)
        clear_button.pack(side='left', padx=5)
    
    def update_translation_interval(self, value):
        """Update translation interval from slider"""
        self.translation_interval = float(value)
        self.update_status(f"翻译间隔已更新 | Translation interval updated: {value}s")
    
    def toggle_partial_translation(self):
        """Toggle partial translation feature"""
        self.partial_translation_active = self.partial_var.get()
        status = "启用" if self.partial_translation_active else "禁用"
        status_en = "enabled" if self.partial_translation_active else "disabled"
        self.update_status(f"实时翻译已{status} | Real-time translation {status_en}")
    
    def translate_sentence(self, input_text):
        """Optimized translation function"""
        try:
            tokens = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
            # Use faster generation parameters for real-time performance
            translated_ids = self.translation_model.generate(
                **tokens, 
                max_length=100,
                num_beams=1,  # Greedy decoding for speed
                do_sample=False,
                early_stopping=True
            )
            translated_text = self.tokenizer.decode(translated_ids[0], skip_special_tokens=True)
            return translated_text
        except Exception as e:
            return f"Translation error: {str(e)}"
    
    def should_translate_partial(self, partial_text, current_time):
        """Determine if partial text should be translated"""
        return (
            self.partial_translation_active and
            len(partial_text) >= self.min_chars_for_translation and
            current_time - self.last_translation_time >= self.translation_interval and
            partial_text != self.last_partial_text and
            len(partial_text.strip()) > 0
        )
    
    def audio_processing_thread(self):
        """Enhanced audio processing with frequent real-time translations"""
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=16000,
                       input=True,
                       frames_per_buffer=4096)
        
        stream.start_stream()
        
        try:
            while self.is_listening:
                data = stream.read(4096, exception_on_overflow=False)
                current_time = time.time()
                
                if self.recognizer.AcceptWaveform(data):
                    # Complete phrase recognized - immediate final translation
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        # Add final Chinese text
                        self.root.after(0, self.add_chinese_text, text, True)
                        
                        # Translate final sentence
                        translation = self.translate_sentence(text)
                        self.root.after(0, self.add_english_text, translation, True)
                        
                        self.root.after(0, self.update_status, "句子完成 | Sentence completed")
                        
                        # Reset partial text tracking
                        self.last_partial_text = ""
                        self.last_translation_time = current_time
                
                else:
                    # Partial result - real-time processing
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    
                    if partial_text:
                        # Always show partial Chinese text
                        self.root.after(0, self.add_chinese_text, partial_text, False)
                        
                        # Check if we should translate partial text
                        if self.should_translate_partial(partial_text, current_time):
                            # Translate partial text in real-time
                            partial_translation = self.translate_sentence(partial_text)
                            self.root.after(0, self.add_english_text, partial_translation, False)
                            
                            # Update tracking variables
                            self.last_partial_text = partial_text
                            self.last_translation_time = current_time
                            
                            self.root.after(0, self.update_status, 
                                          f"实时翻译 | Real-time translating: {partial_text[:15]}...")
                        else:
                            self.root.after(0, self.update_status, 
                                          f"正在识别 | Recognizing: {partial_text[:15]}...")
                    else:
                        self.root.after(0, self.update_status, "正在监听 | Listening...")
        
        except Exception as e:
            self.root.after(0, self.update_status, f"错误 | Error: {str(e)}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    def add_chinese_text(self, text, is_final=False):
        """Update Chinese text continuously in same paragraph"""
        self.chinese_text.config(state='normal')
        
        if is_final:
            # Final text - clean up and finalize paragraph
            if self.chinese_paragraph_start:
                self.chinese_text.delete(self.chinese_paragraph_start, 'end')
            else:
                self.chinese_paragraph_start = self.chinese_text.index('end-1c')
            
            # Add final text with space for continuation
            self.chinese_text.insert('end', f"{text} ")
            self.current_chinese_content = text
            
            # Keep paragraph start for potential continuation
            # Don't reset paragraph_start to allow continuation
            
        else:
            # Partial text - update within same paragraph
            if self.chinese_paragraph_start:
                self.chinese_text.delete(self.chinese_paragraph_start, 'end')
            else:
                self.chinese_paragraph_start = self.chinese_text.index('end-1c')
            
            # Add partial text with cursor indicator
            display_text = f"{text}█"  # Use block cursor to show active typing
            self.chinese_text.insert('end', display_text)
            self.current_chinese_content = text
        
        self.chinese_text.see('end')
        self.chinese_text.config(state='disabled')
    
    def add_english_text(self, text, is_final=False):
        """Update English translation continuously in same paragraph"""
        self.english_text.config(state='normal')
        
        if is_final:
            # Final translation - clean up and finalize
            if self.english_paragraph_start:
                self.english_text.delete(self.english_paragraph_start, 'end')
            else:
                self.english_paragraph_start = self.english_text.index('end-1c')
            
            # Add final translation with space for continuation
            self.english_text.insert('end', f"{text} ")
            self.current_english_content = text
            
        else:
            # Partial translation - update within same paragraph
            if self.english_paragraph_start:
                self.english_text.delete(self.english_paragraph_start, 'end')
            else:
                self.english_paragraph_start = self.english_text.index('end-1c')
            
            # Add partial translation with cursor indicator
            display_text = f"{text}█"
            self.english_text.insert('end', display_text)
            self.current_english_content = text
        
        self.english_text.see('end')
        self.english_text.config(state='disabled')


    def start_new_paragraph(self):
        """Start a new paragraph for both text areas"""
        # Add line breaks to start fresh paragraphs
        self.chinese_text.config(state='normal')
        self.chinese_text.insert('end', '\n\n')
        self.chinese_text.config(state='disabled')
        
        self.english_text.config(state='normal')
        self.english_text.insert('end', '\n\n')
        self.english_text.config(state='disabled')
        
        # Reset paragraph tracking
        self.chinese_paragraph_start = None
        self.english_paragraph_start = None
        self.current_chinese_content = ""
        self.current_english_content = ""
        
        self.update_status("新段落开始 | New paragraph started")    

    
    def update_status(self, status):
        """Update status label"""
        self.status_label.config(text=status)
    
    def toggle_listening(self):
        """Start/stop voice recognition"""
        if not self.is_listening:
            # Start listening
            self.is_listening = True
            self.start_button.config(text="🛑 停止监听 | Stop Listening", bg='#e74c3c')
            self.update_status("开始监听 | Starting to listen...")
            
            # Reset tracking variables
            self.last_partial_text = ""
            self.last_translation_time = 0
            
            # Start audio thread
            self.audio_thread = threading.Thread(target=self.audio_processing_thread)
            self.audio_thread.daemon = True
            self.audio_thread.start()
        else:
            # Stop listening
            self.is_listening = False
            self.start_button.config(text="🎤 开始监听 | Start Listening", bg='#27ae60')
            self.update_status("已停止 | Stopped")
    
    def clear_text(self):
        """Clear all text displays"""
        self.chinese_text.config(state='normal')
        self.chinese_text.delete('1.0', 'end')
        self.chinese_text.config(state='disabled')
        
        self.english_text.config(state='normal')
        self.english_text.delete('1.0', 'end')
        self.english_text.config(state='disabled')
        
        # Reset paragraph tracking
        self.chinese_paragraph_start = None
        self.english_paragraph_start = None
        self.current_chinese_content = ""
        self.current_english_content = ""
        
        # Reset other tracking variables
        self.last_partial_text = ""
        self.last_translation_time = 0
        
        self.update_status("文本已清空 | Text cleared")


def main():
    root = tk.Tk()
    app = RealTimeVoiceTranslatorGUI(root)
    
    # Handle window closing
    def on_closing():
        app.is_listening = False
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
