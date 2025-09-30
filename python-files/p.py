import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import whisper
import os
from datetime import datetime
import torch

class AudioTranscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Transcriber & Translator")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # Variables
        self.audio_file = tk.StringVar()
        self.source_lang = tk.StringVar(value="Auto Detect")
        self.task = tk.StringVar(value="transcribe")
        self.target_lang = tk.StringVar(value="English")
        self.model_size = tk.StringVar(value="base (74MB, balanced)")
        self.progress_var = tk.DoubleVar()
        self.result_text = ""
        
        # Check GPU availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.gpu_info = f"Using: {torch.cuda.get_device_name(0)}" if self.device == "cuda" else "Using: CPU"
        
        # Language options (Whisper supported languages with full names)
        self.lang_options = [
            "Auto Detect", "English", "Spanish", "French", "German", "Italian", 
            "Portuguese", "Russian", "Chinese", "Japanese", "Korean", "Arabic", 
            "Hindi", "Thai", "Vietnamese", "Turkish", "Polish", "Dutch", 
            "Swedish", "Danish", "Norwegian", "Finnish"
        ]
        
        # Mapping from full name to Whisper language code
        self.lang_to_code = {
            "Auto Detect": None,
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Chinese": "zh",
            "Japanese": "ja",
            "Korean": "ko",
            "Arabic": "ar",
            "Hindi": "hi",
            "Thai": "th",
            "Vietnamese": "vi",
            "Turkish": "tr",
            "Polish": "pl",
            "Dutch": "nl",
            "Swedish": "sv",
            "Danish": "da",
            "Norwegian": "no",
            "Finnish": "fi"
        }
        
        # Model options
        self.model_options = [
            ("tiny (39MB, fastest)", "tiny"),
            ("base (74MB, balanced)", "base"),
            ("small (244MB, good)", "small"),
            ("medium (769MB, very good)", "medium"),
            ("large (1550MB, best)", "large")
        ]
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # File selection
        file_frame = tk.LabelFrame(self.root, text="Audio File", padx=10, pady=10)
        file_frame.pack(padx=10, pady=10, fill="x")
        
        tk.Entry(file_frame, textvariable=self.audio_file, width=50).pack(side="left", padx=5)
        tk.Button(file_frame, text="Browse", command=self.browse_file).pack(side="left", padx=5)
        
        # Model selection
        model_frame = tk.LabelFrame(self.root, text="Whisper Model", padx=10, pady=10)
        model_frame.pack(padx=10, pady=10, fill="x")
        
        tk.Label(model_frame, text="Select model:").pack(side="left", padx=5)
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_size, 
                                  values=[name for name, _ in self.model_options], 
                                  state="readonly", width=20)
        model_combo.pack(side="left", padx=5)
        tk.Label(model_frame, text="(larger = more accurate but slower)").pack(side="left", padx=5)
        
        # Device info
        device_frame = tk.LabelFrame(self.root, text="Processing Device", padx=10, pady=10)
        device_frame.pack(padx=10, pady=10, fill="x")
        
        tk.Label(device_frame, text=self.gpu_info, font=("Arial", 10, "bold")).pack(side="left", padx=5)
        if self.device == "cuda":
            tk.Label(device_frame, text="(GPU acceleration enabled)", fg="green").pack(side="left", padx=5)
        else:
            tk.Label(device_frame, text="(No GPU detected, using CPU)", fg="orange").pack(side="left", padx=5)
        
        # Source language selection
        lang_frame = tk.LabelFrame(self.root, text="Source Language", padx=10, pady=10)
        lang_frame.pack(padx=10, pady=10, fill="x")
        
        tk.Label(lang_frame, text="Select language:").pack(side="left", padx=5)
        ttk.Combobox(lang_frame, textvariable=self.source_lang, values=self.lang_options, 
                     state="readonly", width=15).pack(side="left", padx=5)
        tk.Label(lang_frame, text="(Auto Detect = automatically detect)").pack(side="left", padx=5)
        
        # Task selection
        task_frame = tk.LabelFrame(self.root, text="Task", padx=10, pady=10)
        task_frame.pack(padx=10, pady=10, fill="x")
        
        tk.Label(task_frame, text="Select task:").pack(side="left", padx=5)
        task_combo = ttk.Combobox(task_frame, textvariable=self.task, 
                                  values=["transcribe", "translate"], state="readonly", width=15)
        task_combo.pack(side="left", padx=5)
        task_combo.bind("<<ComboboxSelected>>", self.toggle_target_lang)
        
        # Target language selection (initially hidden)
        self.target_frame = tk.LabelFrame(self.root, text="Target Language", padx=10, pady=10)
        
        tk.Label(self.target_frame, text="Translate to:").pack(side="left", padx=5)
        ttk.Combobox(self.target_frame, textvariable=self.target_lang, 
                     values=self.lang_options[1:], state="readonly", width=15).pack(side="left", padx=5)
        
        # Progress bar
        progress_frame = tk.LabelFrame(self.root, text="Progress", padx=10, pady=10)
        progress_frame.pack(padx=10, pady=10, fill="x")
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(pady=5)
        self.progress_label = tk.Label(progress_frame, text="Ready")
        self.progress_label.pack()
        
        # Action buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(padx=10, pady=10, fill="x")
        
        self.process_button = tk.Button(button_frame, text="Process Audio", 
                                       command=self.process_audio, bg="#4CAF50", fg="white")
        self.process_button.pack(side="left", padx=5)
        
        self.save_button = tk.Button(button_frame, text="Save Result", 
                                    command=self.save_result, state="disabled", bg="#2196F3", fg="white")
        self.save_button.pack(side="left", padx=5)
        
        # Result display
        result_frame = tk.LabelFrame(self.root, text="Result", padx=10, pady=10)
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.result_textbox = tk.Text(result_frame, height=8, wrap="word")
        self.result_textbox.pack(fill="both", expand=True)
        
        # Configure text tags for better readability
        self.result_textbox.tag_configure("header", font=("Arial", 10, "bold"))
        self.result_textbox.tag_configure("content", font=("Arial", 10))
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.m4a *.ogg *.flac"), ("All Files", "*.*")]
        )
        if file_path:
            self.audio_file.set(file_path)
    
    def toggle_target_lang(self, event=None):
        if self.task.get() == "translate":
            self.target_frame.pack(padx=10, pady=10, fill="x", after=self.root.children["!labelframe5"])
        else:
            self.target_frame.pack_forget()
    
    def process_audio(self):
        if not self.audio_file.get():
            messagebox.showwarning("No File", "Please select an audio file first.")
            return
        
        # Disable UI during processing
        self.process_button.config(state="disabled")
        self.save_button.config(state="disabled")
        self.progress_var.set(0)
        self.progress_label.config(text="Processing...")
        
        # Start processing in a separate thread
        threading.Thread(target=self.run_whisper, daemon=True).start()
    
    def run_whisper(self):
        try:
            # Get selected model display name and map to actual model name
            selected_display = self.model_size.get()
            model_name = next((value for name, value in self.model_options if name == selected_display), "base")
            
            # Update progress
            self.progress_var.set(10)
            self.progress_label.config(text=f"Loading {selected_display} model on {self.device.upper()}...")
            
            # Load model with device specification
            model = whisper.load_model(model_name, device=self.device)
            
            # Update progress
            self.progress_var.set(30)
            self.progress_label.config(text="Model loaded. Processing audio...")
            
            # Determine language parameter
            lang = self.lang_to_code.get(self.source_lang.get())
            
            # Process audio with device specification
            result = model.transcribe(
                self.audio_file.get(),
                task=self.task.get(),
                language=lang,
                verbose=False,
                fp16=torch.cuda.is_available()  # Use FP16 for GPU if available
            )
            
            # Update progress
            self.progress_var.set(90)
            self.progress_label.config(text="Processing complete!")
            
            # Format result
            task_name = "Transcription" if self.task.get() == "transcribe" else "Translation"
            source_lang = result.get("language", "unknown")
            
            # Convert language code to full name for display
            source_lang_name = next((name for name, code in self.lang_to_code.items() 
                                    if code == source_lang), source_lang)
            
            target_lang_name = self.target_lang.get() if self.task.get() == "translate" else ""
            
            header = f"{task_name} Result\n"
            header += f"Model: {selected_display}\n"
            header += f"Device: {self.device.upper()}\n"
            header += f"Source Language: {source_lang_name}\n"
            if target_lang_name:
                header += f"Target Language: {target_lang_name}\n"
            header += f"Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += "-" * 50 + "\n\n"
            
            self.result_text = header + result.get("text", "")
            
            # Update UI in main thread
            self.root.after(0, self.update_result_ui)
            
        except Exception as e:
            error_msg = f"Error processing audio: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
    
    def update_result_ui(self):
        # Update progress
        self.progress_var.set(100)
        self.progress_label.config(text="Ready")
        
        # Update result display
        self.result_textbox.delete(1.0, tk.END)
        self.result_textbox.insert(tk.END, self.result_text)
        
        # Enable save button
        self.save_button.config(state="normal")
        self.process_button.config(state="normal")
    
    def show_error(self, message):
        messagebox.showerror("Error", message)
        self.progress_label.config(text="Error occurred")
        self.process_button.config(state="normal")
    
    def save_result(self):
        if not self.result_text:
            messagebox.showwarning("No Result", "No result to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Result",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.result_text)
                messagebox.showinfo("Success", f"Result saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioTranscriberApp(root)
    root.mainloop()