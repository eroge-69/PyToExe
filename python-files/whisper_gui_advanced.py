import os
import whisper
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import timedelta
import threading
import time

def format_timestamp(seconds):
    td = timedelta(seconds=seconds)
    return str(td)[:-3].replace('.', ',')

class WhisperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Multilingual Translator/Transcriber")
        self.root.geometry("800x600")
        self.folder_path = ""
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Task Mode:").grid(row=0, column=0)
        self.task_mode = ttk.Combobox(frame, values=["transcribe", "translate"], state="readonly")
        self.task_mode.set("translate")
        self.task_mode.grid(row=0, column=1, padx=10)

        tk.Label(frame, text="Model:").grid(row=0, column=2)
        self.model_var = ttk.Combobox(frame, values=["tiny", "base", "small", "medium", "large"], state="readonly")
        self.model_var.set("base")
        self.model_var.grid(row=0, column=3, padx=10)

        tk.Label(frame, text="Source Language:").grid(row=1, column=0)
        self.source_lang = ttk.Combobox(frame, values=["ja", "en", "hi", "es", "fr", "de", "auto"], state="readonly")
        self.source_lang.set("ja")
        self.source_lang.grid(row=1, column=1, padx=10)

        tk.Label(frame, text="Target Language:").grid(row=1, column=2)
        self.target_lang = ttk.Combobox(frame, values=["en", "hi", "ja", "es", "fr", "de"], state="readonly")
        self.target_lang.set("en")
        self.target_lang.grid(row=1, column=3, padx=10)

        self.merge_output = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Merge all outputs into one file", variable=self.merge_output).pack()

        tk.Button(self.root, text="Select Audio Folder", command=self.select_folder, bg="#2196F3", fg="white").pack(pady=5)

        self.progress = ttk.Progressbar(self.root, length=600, mode="determinate")
        self.progress.pack(pady=5)

        self.log_box = tk.Text(self.root, height=20, width=100)
        self.log_box.pack(pady=10)

    def log(self, message):
        self.log_box.insert(tk.END, f"{message}\n")
        self.log_box.see(tk.END)
        self.root.update()

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.log_box.delete(1.0, tk.END)
            threading.Thread(target=self.process_folder, daemon=True).start()

    def process_folder(self):
        model = whisper.load_model(self.model_var.get())
        files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('.mp3', '.wav', '.m4a'))]
        total = len(files)
        if not files:
            messagebox.showinfo("No Files", "No audio files found.")
            return

        output_dir = os.path.join(self.folder_path, "output_translations")
        os.makedirs(output_dir, exist_ok=True)

        merged_text = ""
        for i, file in enumerate(files, 1):
            self.progress['value'] = (i / total) * 100
            self.log(f"Processing ({i}/{total}): {file}")
            file_path = os.path.join(self.folder_path, file)
            result = model.transcribe(file_path, task=self.task_mode.get(), language=None if self.source_lang.get() == "auto" else self.source_lang.get())

            base_name = os.path.splitext(file)[0]
            out_text = result["text"]

            txt_file = os.path.join(output_dir, f"{base_name}_output.txt")
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(out_text)

            srt_file = os.path.join(output_dir, f"{base_name}.srt")
            with open(srt_file, "w", encoding="utf-8") as f:
                for idx, seg in enumerate(result["segments"], 1):
                    f.write(f"{idx}\n{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n{seg['text'].strip()}\n\n")

            merged_text += f"\n\n=== {file} ===\n{out_text}" if self.merge_output.get() else ""

            self.log(f"✅ Done: {file}")
        if self.merge_output.get():
            with open(os.path.join(output_dir, "merged_output.txt"), "w", encoding="utf-8") as f:
                f.write(merged_text)

        self.progress['value'] = 100
        messagebox.showinfo("Completed", f"Processed {total} files. Output in: {output_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()
