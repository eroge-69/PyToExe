import tkinter as tk
from tkinter import ttk
from deep_translator import GoogleTranslator

# Mapping of full language names to codes
LANGUAGE_MAP = {
    "English": "en", "Spanish": "es", "French": "fr",
    "German": "de", "Hindi": "hi", "Bengali": "bn",
    "Italian": "it", "Portuguese": "pt", "Chinese": "zh-CN",
    "Japanese": "ja", "Russian": "ru", "Korean": "ko",
    "Arabic": "ar", "Dutch": "nl", "Turkish": "tr"
}


# Function to translate text
def translate_text():
    input_text = text_entry.get("1.0", tk.END).strip()
    target_lang_full = lang_combobox.get()

    if not input_text or input_text == "SINAN":
        output_text_box.delete("1.0", tk.END)
        output_text_box.insert("1.0", "SINAN")
        output_text_box.tag_add("center", "1.0", "end")
        return

    target_lang_code = LANGUAGE_MAP.get(target_lang_full)

    try:
        translated = GoogleTranslator(source='auto', target=target_lang_code).translate(input_text)
        output_text_box.delete("1.0", tk.END)
        output_text_box.insert("1.0", translated)
        output_text_box.tag_add("center", "1.0", "end")
    except Exception as e:
        output_text_box.delete("1.0", tk.END)
        output_text_box.insert("1.0", f"Error: {str(e)}")
        output_text_box.tag_add("center", "1.0", "end")


# Function to add watermark in the center
def add_watermark(event=None):
    if not text_entry.get("1.0", tk.END).strip():
        text_entry.insert("1.0", "SINAN")
        text_entry.tag_add("center", "1.0", "end")
        text_entry.config(fg="gray")


# Function to remove watermark when user starts typing
def remove_watermark(event=None):
    if text_entry.get("1.0", tk.END).strip() == "SINAN":
        text_entry.delete("1.0", tk.END)
        text_entry.config(fg="black")


# Create main window
root = tk.Tk()
root.title("Translator App")
root.geometry("600x500")
root.configure(bg="#d4e6f1")  # **Soft Blue Background**

# Heading label with color
heading_label = tk.Label(root, text="Language Translator", font=("Arial", 18, "bold"), bg="#5dade2", fg="white")
heading_label.pack(pady=10, fill=tk.X)

# Text Entry Box (Bigger & Watermark Centered)
text_entry = tk.Text(root, height=8, width=60, bg="#fef9e7", fg="gray", font=("Times New Roman", 14, "italic"))
text_entry.insert("1.0", "SINAN")
text_entry.tag_configure("center", justify="center")
text_entry.tag_add("center", "1.0", "end")
text_entry.pack(pady=5)
text_entry.bind("<FocusIn>", remove_watermark)
text_entry.bind("<FocusOut>", add_watermark)

# Language Dropdown Menu
lang_combobox = ttk.Combobox(root, values=list(LANGUAGE_MAP.keys()), width=20, font=("Arial", 12))
lang_combobox.pack()
lang_combobox.set("English")  # Default language is English

# Styled Translate Button
translate_button = tk.Button(root, text="Translate", font=("Arial", 14, "bold"), bg="#58d68d", fg="white",
                             command=translate_text)
translate_button.pack(pady=10)

# Output Box (Bigger & Watermark Centered)
output_text_box = tk.Text(root, height=8, width=60, bg="#f2f3f4", fg="gray", font=("Courier", 14, "bold"))
output_text_box.insert("1.0", "SINAN")
output_text_box.tag_configure("center", justify="center")
output_text_box.tag_add("center", "1.0", "end")
output_text_box.pack(pady=5)

# Run the GUI application
root.mainloop()
