import customtkinter as ctk 
from tkinter import filedialog as fd, messagebox
from PIL import Image, Image as PilImage
import os
import fitz  # PyMuPDF
import pytesseract  # OCR লাইব্রেরি
import webbrowser

# Appearance settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# App setup
app = ctk.CTk()
app.geometry("400x520")
app.title("🖼️ SMART IMAGE TOOL")

# Global variables
selected_files = []
selected_format = ctk.StringVar(value="PNG")
language = ctk.StringVar(value="বাংলা")
resize_unit = ctk.StringVar(value="px")
dpi_value = ctk.IntVar(value=96)
pdf_output_format = ctk.StringVar(value="docx")
image_to_text_path = ctk.StringVar()
pdf_path = ctk.StringVar()
resize_image_path = ctk.StringVar()

# Language dictionary
LANG = {
    "বাংলা": {
        "browse": "📂 ছবি নির্বাচন করুন",
        "convert": "✅ কনভার্ট ও সেভ করুন",
        "format": "ফরম্যাট নির্বাচন করুন",
        "drop_hint": "ছবি এখানে ড্র্যাগ করে দিন অথবা 'ছবি নির্বাচন করুন' চাপুন",
        "success": "সফলভাবে সেভ হয়েছে!",
        "error": "ত্রুটি ঘটেছে!",
        "resize": "✅ রিসাইজ করুন এবং সেভ করুন",
        "select_pdf": "📂 পিডিএফ ফাইল নির্বাচন করুন",
        "convert_pdf": "✅ ওয়ার্ডে রূপান্তর করুন",
        "no_file": "কোনো ফাইল নির্বাচন করা হয়নি।",
        "no_pdf": "কোনো পিডিএফ নির্বাচন করা হয়নি।",
        "no_image": "কোনো ছবি নির্বাচন করা হয়নি।",
        "convert_txt": "✅ টেক্সট বের করুন"
    },
    "English": {
        "browse": "📂 Choose File",
        "convert": "✅ Convert & Save",
        "format": "Select Format",
        "drop_hint": "Drag images here or click 'Choose File'",
        "success": "Successfully saved!",
        "error": "An error occurred!",
        "resize": "✅ Resize & Save",
        "select_pdf": "📂 Select PDF File",
        "convert_pdf": "✅ Convert to Word",
        "no_file": "No file selected.",
        "no_pdf": "No PDF selected.",
        "no_image": "No image selected.",
        "convert_txt": "✅ Extract Text"
    }
}

def get_text(key):
    return LANG[language.get()][key]

# ---------- Frame Hide/Show ----------
def hide_all_frames():
    for f in (main_frame, convert_frame, resize_frame, pdf_frame, image_to_text_frame, word_to_pdf_frame):
        f.pack_forget()

def show_main():
    hide_all_frames()
    main_frame.pack(pady=40)

def show_convert_ui():
    hide_all_frames()
    refresh_ui()
    convert_frame.pack(pady=40)

def show_resize_ui():
    hide_all_frames()
    refresh_ui()
    resize_frame.pack(pady=40)

def show_pdf_to_word_ui():
    hide_all_frames()
    refresh_ui()
    pdf_frame.pack(pady=40)

def show_image_to_text_ui():
    hide_all_frames()
    refresh_ui()
    image_to_text_frame.pack(pady=40)

def show_word_to_pdf_ui():
    hide_all_frames()
    refresh_ui()
    word_to_pdf_frame.pack(pady=40)

# ---------- Language Toggle ----------
def toggle_language():
    language.set("English" if language.get() == "বাংলা" else "বাংলা")
    refresh_ui()

def refresh_ui():
    browse_btn.configure(text=get_text("browse"))
    convert_btn.configure(text=get_text("convert"))
    drop_label.configure(text="\n".join([os.path.basename(f) for f in selected_files]) if selected_files else get_text("drop_hint"))
    format_label.configure(text=get_text("format"))
    resize_btn.configure(text=get_text("resize"))
    pdf_browse_btn.configure(text=get_text("select_pdf"))
    pdf_convert_btn.configure(text=get_text("convert_pdf"))
    image_to_text_browse_btn.configure(text=get_text("browse"))
    image_to_text_convert_btn.configure(text=get_text("convert_txt"))
    word_to_pdf_browse_btn.configure(text="📂 ওয়ার্ড ফাইল নির্বাচন করুন")
    word_to_pdf_convert_btn.configure(text="✅ পিডিএফে রূপান্তর করুন")

# ---------- Image Converter ----------
def browse_files():
    files = fd.askopenfilenames(title="ছবি নির্বাচন করুন", 
                                filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp")])
    if files:
        selected_files.clear()
        selected_files.extend(files)
        refresh_ui()

def convert_images():
    if not selected_files:
        messagebox.showwarning("Oops", get_text("no_file"))
        return

    out_format = selected_format.get().lower()
    ext = "." + out_format

    save_dir = fd.askdirectory(title="Save Converted Files")
    if not save_dir:
        return

    for file in selected_files:
        try:
            img = Image.open(file)
            if out_format == "pdf" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            base = os.path.splitext(os.path.basename(file))[0]
            save_path = os.path.join(save_dir, base + ext)
            img.save(save_path)
        except Exception as e:
            messagebox.showerror(get_text("error"), str(e))
            return
    messagebox.showinfo("✅", get_text("success"))

# ---------- Image Resizer ----------
def browse_resize_file():
    file = fd.askopenfilename(title="ছবি নির্বাচন করুন", 
                                filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp")])
    if file:
        resize_image_path.set(file)
        resize_label.configure(text=os.path.basename(file))

        try:
            img = Image.open(file)
            width, height = img.size
            dpi = img.info.get("dpi", (dpi_value.get(), dpi_value.get()))
            size_bytes = os.path.getsize(file)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            info_text = f"📏 {width} x {height} px | 🧩 {dpi[0]} DPI | 💾 {size_mb} MB"
            info_label.configure(text=info_text)
        except Exception as e:
            info_label.configure(text=str(e))

def resize_and_save():
    file = resize_image_path.get()
    if not file:
        messagebox.showwarning("Oops", get_text("no_image"))
        return
    try:
        img = Image.open(file)
        w = int(width_entry.get())
        h = int(height_entry.get())
        dpi = dpi_value.get()

        if resize_unit.get() == "mm":
            w = int((w / 25.4) * dpi)
            h = int((h / 25.4) * dpi)
        elif resize_unit.get() == "inch":
            w = int(w * dpi)
            h = int(h * dpi)

        resized = img.resize((w, h), Image.Resampling.LANCZOS)
        save_path = fd.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")])
        if save_path:
            resized.save(save_path, dpi=(dpi, dpi))
            messagebox.showinfo("✅", get_text("success"))
    except Exception as e:
        messagebox.showerror(get_text("error"), str(e))

# ---------- PDF to Word ----------
def browse_pdf():
    file = fd.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file:
        pdf_path.set(file)
        pdf_file_label.configure(text=os.path.basename(file))

def convert_pdf_to_word():
    file = pdf_path.get()
    if not file:
        messagebox.showwarning("Oops", get_text("no_pdf"))
        return
    try:
        doc = fitz.open(file)
        text = "\n".join(page.get_text() for page in doc)
        ext = ".docx" if pdf_output_format.get() == "docx" else ".doc"
        save_path = fd.asksaveasfilename(defaultextension=ext, filetypes=[("Word Files", "*.doc *.docx")])
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("✅", get_text("success"))
    except Exception as e:
        messagebox.showerror(get_text("error"), str(e))

# ---------- Word to PDF ----------
def browse_word():
    file = fd.askopenfilename(filetypes=[("Word Files", "*.doc *.docx")])
    if file:
        word_file_path.set(file)
        word_file_label.configure(text=os.path.basename(file))

def convert_word_to_pdf():
    import comtypes.client
    file = word_file_path.get()
    if not file:
        messagebox.showwarning("Oops", "No Word file selected.")
        return
    try:
        word = comtypes.client.CreateObject('Word.Application')
        word.Visible = False
        doc = word.Documents.Open(file)
        save_path = fd.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if save_path:
            doc.SaveAs(save_path, FileFormat=17)
            doc.Close()
            word.Quit()
            messagebox.showinfo("✅", "Successfully converted to PDF!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------- Image to Text (OCR) ----------
def browse_image_to_text_file():
    file = fd.askopenfilename(
        title="ছবি নির্বাচন করুন",
        filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp")]
    )
    if file:
        image_to_text_path.set(file)
        image_to_text_label.configure(text=os.path.basename(file))
        image_text_result.configure(state="normal")
        image_text_result.delete("1.0", "end")
        image_text_result.configure(state="disabled")

def convert_image_to_text():
    file = image_to_text_path.get()
    if not file:
        messagebox.showwarning("Oops", get_text("no_image"))
        return
    try:
        img = PilImage.open(file)
        text = pytesseract.image_to_string(img, lang='eng+ben')  # English and Bengali support
        image_text_result.configure(state="normal")
        image_text_result.delete("1.0", "end")
        image_text_result.insert("1.0", text)
        image_text_result.configure(state="disabled")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# === FRAMES ===
main_frame = ctk.CTkFrame(app)
convert_frame = ctk.CTkFrame(app)
resize_frame = ctk.CTkFrame(app)
pdf_frame = ctk.CTkFrame(app)
image_to_text_frame = ctk.CTkFrame(app)
word_to_pdf_frame = ctk.CTkFrame(app)

# === MAIN FRAME ===
ctk.CTkLabel(main_frame, text="📂 SMART IMAGE TOOL", font=("Helvetica", 24, "bold")).pack(pady=10)

ctk.CTkButton(
    main_frame, 
    text="🖼️ ইমেজ কনভার্টার", 
    command=show_convert_ui,
    fg_color="#0078D7",
    hover_color="#005A9E",
    font=("Helvetica", 16, "bold")
).pack(pady=10)

ctk.CTkButton(
    main_frame, 
    text="📏 ইমেজ রিসাইজার", 
    command=show_resize_ui,
    fg_color="#28A745",
    hover_color="#1E7E34",
    font=("Helvetica", 16, "bold")
).pack(pady=10)

ctk.CTkButton(
    main_frame, 
    text="📄 পিডিএফ টু ওয়ার্ড", 
    command=show_pdf_to_word_ui,
    fg_color="#FFC107",
    hover_color="#D39E00",
    font=("Helvetica", 16, "bold")
).pack(pady=10)


ctk.CTkButton(
    main_frame, 
    text="📑 ওয়ার্ড টু পিডিএফ", 
    command=show_word_to_pdf_ui,
    fg_color="#6F42C1",
    hover_color="#4E2A8E",
    font=("Helvetica", 16, "bold")
).pack(pady=10)


ctk.CTkButton(
    main_frame, 
    text="📝 ইমেজ টু টেক্সট", 
    command=show_image_to_text_ui,
    fg_color="#17A2B8",
    hover_color="#0B6775",
    font=("Helvetica", 16, "bold")
).pack(pady=10)

# === CONVERTER UI ===
ctk.CTkLabel(convert_frame, text="🖼️ Smart Image Converter", font=("Helvetica", 20, "bold")).pack(pady=10)

browse_btn = ctk.CTkButton(
    convert_frame, text=get_text("browse"), command=browse_files,
    fg_color="#0078D7",
    hover_color="#005A9E",
    font=("Helvetica", 14, "bold")
)
browse_btn.pack(pady=10)

drop_label = ctk.CTkLabel(convert_frame, text=get_text("drop_hint"))
drop_label.pack()

format_label = ctk.CTkLabel(convert_frame, text=get_text("format"))
format_label.pack()

format_menu = ctk.CTkOptionMenu(convert_frame, variable=selected_format, values=["PNG", "JPG", "WEBP", "PDF"])
format_menu.pack()

convert_btn = ctk.CTkButton(
    convert_frame, text=get_text("convert"), command=convert_images,
    fg_color="#28A745",
    hover_color="#1E7E34",
    font=("Helvetica", 14, "bold")
)
convert_btn.pack(pady=10)

ctk.CTkButton(
    convert_frame, text="🏠 হোম", command=show_main,
    fg_color="#6C757D",
    hover_color="#5A6268",
    font=("Helvetica", 14, "bold")
).pack(pady=10)

# === RESIZE UI ===
ctk.CTkLabel(resize_frame, text="📐 Image Resizer", font=("Helvetica", 20, "bold")).pack(pady=10)

resize_label = ctk.CTkLabel(resize_frame, text="No image selected")
resize_label.pack()

ctk.CTkButton(
    resize_frame, text="📂 Browse Image", command=browse_resize_file,
    fg_color="#0078D7",
    hover_color="#005A9E",
    font=("Helvetica", 14, "bold")
).pack(pady=10)

info_label = ctk.CTkLabel(resize_frame, text="")
info_label.pack()

entry_row = ctk.CTkFrame(resize_frame)
entry_row.pack(pady=5)

width_entry = ctk.CTkEntry(entry_row, placeholder_text="Width", width=100)
width_entry.pack(side="left", padx=5)

height_entry = ctk.CTkEntry(entry_row, placeholder_text="Height", width=100)
height_entry.pack(side="left", padx=5)

unit_menu = ctk.CTkOptionMenu(entry_row, variable=resize_unit, values=["px", "mm", "inch"])
unit_menu.pack(side="left", padx=5)

ctk.CTkLabel(resize_frame, text="DPI:").pack()

dpi_entry = ctk.CTkEntry(resize_frame, textvariable=dpi_value, width=100)
dpi_entry.pack(pady=5)

resize_btn = ctk.CTkButton(
    resize_frame, text=get_text("resize"), command=resize_and_save,
    fg_color="#28A745",
    hover_color="#1E7E34",
    font=("Helvetica", 14, "bold")
)
resize_btn.pack(pady=10)

ctk.CTkButton(
    resize_frame, text="🏠 হোম", command=show_main,
    fg_color="#6C757D",
    hover_color="#5A6268",
    font=("Helvetica", 14, "bold")
).pack(pady=10)

# === PDF to Word Frame ===
ctk.CTkLabel(pdf_frame, text="📄 PDF to Word", font=("Helvetica", 20, "bold")).pack(pady=10)

pdf_file_label = ctk.CTkLabel(pdf_frame, text="No file selected")
pdf_file_label.pack()

pdf_browse_btn = ctk.CTkButton(
    pdf_frame, text=get_text("select_pdf"), command=browse_pdf,
    fg_color="#0078D7",
    hover_color="#005A9E",
    font=("Helvetica", 14, "bold")
)
pdf_browse_btn.pack(pady=10)

pdf_format_menu = ctk.CTkOptionMenu(pdf_frame, variable=pdf_output_format, values=["doc", "docx"])
pdf_format_menu.pack(pady=5)

pdf_convert_btn = ctk.CTkButton(
    pdf_frame, text=get_text("convert_pdf"), command=convert_pdf_to_word,
    fg_color="#28A745",
    hover_color="#1E7E34",
    font=("Helvetica", 14, "bold")
)
pdf_convert_btn.pack(pady=10)

ctk.CTkButton(
    pdf_frame, text="🏠 হোম", command=show_main,
    fg_color="#6C757D",
    hover_color="#5A6268",
    font=("Helvetica", 14, "bold")
).pack(pady=10)

# === Image to Text Frame ===
ctk.CTkLabel(image_to_text_frame, text="📝 Image to Text", font=("Helvetica", 20, "bold")).pack(pady=10)

image_to_text_label = ctk.CTkLabel(image_to_text_frame, text="No image selected")
image_to_text_label.pack(pady=5)

image_to_text_browse_btn = ctk.CTkButton(
    image_to_text_frame, text=get_text("browse"), command=browse_image_to_text_file,
    fg_color="#0078D7",
    hover_color="#005A9E",
    font=("Helvetica", 14, "bold")
)
image_to_text_browse_btn.pack(pady=10)

image_to_text_convert_btn = ctk.CTkButton(
    image_to_text_frame, text=get_text("convert_txt"), command=convert_image_to_text,
    fg_color="#28A745",
    hover_color="#1E7E34",
    font=("Helvetica", 14, "bold")
)
image_to_text_convert_btn.pack(pady=10)

image_text_result = ctk.CTkTextbox(image_to_text_frame, height=150, width=350, state="disabled")
image_text_result.pack(pady=10)

ctk.CTkButton(
    image_to_text_frame, text="🏠 হোম", command=show_main,
    fg_color="#6C757D",
    hover_color="#5A6268",
    font=("Helvetica", 14, "bold")
).pack(pady=10)

# === Word to PDF Frame ===
word_file_path = ctk.StringVar()
ctk.CTkLabel(word_to_pdf_frame, text="📑 Word to PDF", font=("Helvetica", 20, "bold")).pack(pady=10)

word_file_label = ctk.CTkLabel(word_to_pdf_frame, text="No file selected")
word_file_label.pack(pady=5)

word_to_pdf_browse_btn = ctk.CTkButton(
    word_to_pdf_frame, text="📂 ওয়ার্ড ফাইল নির্বাচন করুন", command=browse_word,
    fg_color="#0078D7",
    hover_color="#005A9E",
    font=("Helvetica", 14, "bold")
)
word_to_pdf_browse_btn.pack(pady=10)

word_to_pdf_convert_btn = ctk.CTkButton(
    word_to_pdf_frame, text="✅ পিডিএফে রূপান্তর করুন", command=convert_word_to_pdf,
    fg_color="#28A745",
    hover_color="#1E7E34",
    font=("Helvetica", 14, "bold")
)
word_to_pdf_convert_btn.pack(pady=10)

ctk.CTkButton(
    word_to_pdf_frame, text="🏠 হোম", command=show_main,
    fg_color="#6C757D",
    hover_color="#5A6268",
    font=("Helvetica", 14, "bold")
).pack(pady=10)


# ---------- Facebook link ----------
def open_facebook(event):
    webbrowser.open_new("https://facebook.com/24jahangir")



# Facebook Link
fb_label = ctk.CTkLabel(main_frame, text="facebook.com/24jahangir", font=("Helvetica", 12, "underline"), text_color="blue", cursor="hand2")
fb_label.pack(side="bottom", pady=(10, 10))
fb_label.bind("<Button-1>", open_facebook)


# Developer info - bottom of the app
dev_label = ctk.CTkLabel(
    app,
    text="Developed by: MD.Jahangir Alam\nSD Globalization, Netrokona",
    font=("Helvetica", 10),
    text_color="#666666"
)
dev_label.pack(side="bottom", pady=(8, 2))

# Show main frame initially
show_main()

app.mainloop()