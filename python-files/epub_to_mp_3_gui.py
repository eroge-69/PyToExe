import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ebooklib import epub
from bs4 import BeautifulSoup
import requests
import threading

API_KEY = "sk_b1716194e91d8fd8e17062cf12bb2bde96712ae61e0aca7c"
VOICE_ID = "FQ8VmAXUrzoLcSCwRJC2"

HEADERS = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

def extract_chapters(epub_path):
    book = epub.read_epub(epub_path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text().strip()
            if len(text) > 100:
                chapters.append(text)
    return chapters

def text_to_speech(text, filename, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    else:
        raise Exception(f"Error from ElevenLabs: {response.status_code}, {response.text}")

def convert_epub_to_mp3(epub_path, output_dir, status_label, progress):
    try:
        status_label.config(text="Extracting chapters...")
        chapters = extract_chapters(epub_path)
        total = len(chapters)
        for i, chapter in enumerate(chapters):
            status_label.config(text=f"Converting chapter {i+1}/{total}...")
            filename = os.path.join(output_dir, f"chapter_{i+1}.mp3")
            text_to_speech(chapter[:4999], filename, VOICE_ID)
            progress["value"] = ((i + 1) / total) * 100
        status_label.config(text="Conversion complete!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Failed")

def launch_gui():
    root = tk.Tk()
    root.title("EPUB to MP3 Converter - ElevenLabs")
    root.geometry("500x300")

    epub_path = tk.StringVar()
    output_path = tk.StringVar()

    def browse_epub():
        path = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")])
        epub_path.set(path)

    def browse_output():
        path = filedialog.askdirectory()
        output_path.set(path)

    def start_conversion():
        if not epub_path.get() or not output_path.get():
            messagebox.showwarning("Missing Info", "Please select both an EPUB file and output folder.")
            return
        threading.Thread(target=convert_epub_to_mp3, args=(epub_path.get(), output_path.get(), status_label, progress), daemon=True).start()

    tk.Label(root, text="Select EPUB File:").pack(pady=5)
    tk.Entry(root, textvariable=epub_path, width=50).pack()
    tk.Button(root, text="Browse", command=browse_epub).pack(pady=5)

    tk.Label(root, text="Select Output Folder:").pack(pady=5)
    tk.Entry(root, textvariable=output_path, width=50).pack()
    tk.Button(root, text="Browse", command=browse_output).pack(pady=5)

    tk.Button(root, text="Start Conversion", command=start_conversion).pack(pady=10)

    status_label = tk.Label(root, text="Idle", fg="blue")
    status_label.pack(pady=5)

    progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
