import os
import re
import torch
import subprocess
from PIL import Image, ImageTk
from pathlib import Path
from transformers import BlipProcessor, BlipForConditionalGeneration
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Load BLIP model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# Keyword cleaning function
def seo_keywords(text, max_keywords=10):
    words = re.findall(r'\b\w+\b', text.lower())
    unique_words = list(dict.fromkeys(words))
    return ", ".join(unique_words[:max_keywords])

# Generate IPTC tags
def generate_iptc_tags(image_path, fast_mode=False, use_gpu=False):
    device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
    model.to(device)
    raw_image = Image.open(image_path).convert('RGB')
    inputs = processor(raw_image, return_tensors="pt").to(device)
    out = model.generate(**inputs, max_length=60 if fast_mode else 155)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return {
        "title": caption[:60],
        "description": caption[:155],
        "keywords": seo_keywords(caption)
    }

# Save image with title in filename
def save_tagged_image_with_title(image_path, title, output_dir):
    image = Image.open(image_path)
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    title_slug = title.strip().replace(" ", "_")
    safe_title = "".join(c for c in title_slug if c.isalnum() or c in ('_', '-'))
    filename = f"{safe_title}_tagged.jpg"
    output_path = output_dir / filename
    image.save(output_path)
    return safe_title

# Save tags to text file
def save_tags_text(safe_title, tags, output_dir):
    text_path = output_dir / f"{safe_title}_tags.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        for key, value in tags.items():
            f.write(f"{key}: {value}\n")

# Main App Class
class IPTCTaggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IPTC Tag Generator - Futuristic UI")
        self.root.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.output_dir = Path("./output")
        self.output_dir.mkdir(exist_ok=True)

        self.fast_mode = ctk.BooleanVar()
        self.use_gpu = ctk.BooleanVar()
        self.export_as_text = ctk.BooleanVar()

        self.image_paths = []
        self.image_tags = {}
        self.selected_image_path = None

        self.build_ui()

    def build_ui(self):
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        title_label = ctk.CTkLabel(self.frame, text="AI IPTC Tagger", font=("Orbitron", 24))
        title_label.pack(pady=10)

        switches = ctk.CTkFrame(self.frame)
        switches.pack(pady=5)
        ctk.CTkCheckBox(switches, text="Fast Mode", variable=self.fast_mode).pack(side="left", padx=10)
        ctk.CTkCheckBox(switches, text="Use GPU", variable=self.use_gpu).pack(side="left", padx=10)
        ctk.CTkCheckBox(switches, text="Export Tags as Text", variable=self.export_as_text).pack(side="left", padx=10)

        folder_buttons = ctk.CTkFrame(self.frame)
        folder_buttons.pack(pady=5)
        ctk.CTkButton(folder_buttons, text="Set Output Folder", command=self.set_output_folder).pack(side="left", padx=10)
        ctk.CTkButton(folder_buttons, text="Open Output Folder", command=self.open_output_folder).pack(side="left", padx=10)

        ctk.CTkButton(self.frame, text="Upload Images", command=self.upload_pictures).pack(pady=5)
        ctk.CTkButton(self.frame, text="Generate Tags", command=self.process_images).pack(pady=5)

        self.progress_label = ctk.CTkLabel(self.frame, text="Status: Waiting")
        self.progress_label.pack(pady=2)
        self.progress_bar = ctk.CTkProgressBar(self.frame, width=600)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=5)

        self.result_box = ctk.CTkTextbox(self.frame, height=200)
        self.result_box.pack(pady=10, fill="x", padx=20)

        tag_editor = ctk.CTkFrame(self.frame)
        tag_editor.pack(pady=10)

        self.title_entry = ctk.CTkEntry(tag_editor, width=700, placeholder_text="Title")
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)
        self.desc_entry = ctk.CTkEntry(tag_editor, width=700, placeholder_text="Description")
        self.desc_entry.grid(row=1, column=1, padx=10, pady=5)
        self.key_entry = ctk.CTkEntry(tag_editor, width=700, placeholder_text="Keywords")
        self.key_entry.grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkButton(self.frame, text="Save Edits", command=self.save_edits).pack(pady=10)

    def upload_pictures(self):
        filetypes = [("Image Files", "*.jpg *.jpeg *.png")]
        self.image_paths = filedialog.askopenfilenames(filetypes=filetypes)
        self.image_tags.clear()
        self.result_box.delete("1.0", "end")

        for img_path in self.image_paths:
            status_line = f"[UNPROCESSED] {os.path.basename(img_path)}\n"
            self.result_box.insert("end", status_line)

    def process_images(self):
        if not self.image_paths:
            messagebox.showwarning("No Images", "Upload images first")
            return

        self.progress_bar.set(0)
        total = len(self.image_paths)

        for i, img_path in enumerate(self.image_paths):
            tags = generate_iptc_tags(
                img_path,
                self.fast_mode.get(),
                self.use_gpu.get()
            )
            self.image_tags[img_path] = tags

            safe_title = save_tagged_image_with_title(img_path, tags["title"], self.output_dir)
            if self.export_as_text.get():
                save_tags_text(safe_title, tags, self.output_dir)

            percent = (i + 1) / total
            self.progress_bar.set(percent)
            self.progress_label.configure(text=f"Processing... {int(percent * 100)}%")

        self.result_box.delete("1.0", "end")
        for img_path in self.image_paths:
            status_line = f"[TAGGED] {os.path.basename(img_path)}\n"
            self.result_box.insert("end", status_line)

        self.progress_label.configure(text="✅ Done")
        messagebox.showinfo("Completed", f"All images processed and saved in {self.output_dir}/")

    def save_edits(self):
        if not self.selected_image_path:
            messagebox.showwarning("No Selection", "Select an image from the list")
            return

        edited_tags = {
            "title": self.title_entry.get().strip()[:60],
            "description": self.desc_entry.get().strip()[:155],
            "keywords": self.key_entry.get().strip()
        }
        safe_title = save_tagged_image_with_title(self.selected_image_path, edited_tags["title"], self.output_dir)
        save_tags_text(safe_title, edited_tags, self.output_dir)
        self.image_tags[self.selected_image_path] = edited_tags
        messagebox.showinfo("Saved", f"Tags saved for {os.path.basename(self.selected_image_path)}")

    def set_output_folder(self):
        selected = filedialog.askdirectory(title="Choose Output Folder")
        if selected:
            self.output_dir = Path(selected)
            self.output_dir.mkdir(exist_ok=True)
            messagebox.showinfo("Folder Set", f"Output folder set to:\n{self.output_dir}")

    def open_output_folder(self):
        if self.output_dir.exists():
            subprocess.Popen(f'explorer "{self.output_dir.resolve()}"')
        else:
            messagebox.showerror("Not Found", "Output directory does not exist.")

if __name__ == "__main__":
    root = ctk.CTk()
    app = IPTCTaggerApp(root)
    root.mainloop()