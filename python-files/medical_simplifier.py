import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import torch
import pandas as pd
import pytesseract
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pdf2image import convert_from_path
from PIL import Image, ImageTk
import os
import sys

# ----- Model Setup -----
input_dir = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "model")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

try:
    loaded_model = AutoModelForSequenceClassification.from_pretrained(input_dir).to(device)
    loaded_model.eval()
    loaded_tokenizer = AutoTokenizer.from_pretrained(input_dir)
    loaded_df_label = pd.read_pickle(os.path.join(input_dir, "df_label.pkl"))
except Exception as e:
    messagebox.showerror("Model Load Error", f"Could not load model: {str(e)}")
    sys.exit()

# ----- OCR & Substitution Functions -----

def extract_text_from_pdf(pdf_path):
    try:
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        pages = convert_from_path(pdf_path, dpi=300)
        text_data = [pytesseract.image_to_string(page).strip() for page in pages]
        return "\n".join(text_data)
    except Exception as e:
        return f"Error: {e}"

def replace_medical_terms_with_biobert(text):
    inputs = loaded_tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = loaded_model(**inputs)
    logits = outputs.logits
    predicted_id = torch.argmax(logits, dim=1).item()

    if predicted_id in loaded_df_label["id"].values:
        return str(loaded_df_label.loc[loaded_df_label["id"] == predicted_id, "intent"].values[0])
    return "Unknown Term"

def substitute_long_text_with_keyword(full_text):
    groups = re.split(r'\n?\s*(?:\d+[.)]|•|-)\s*', full_text)
    groups = [g.strip() for g in groups if g.strip()]
    output_lines = ["--- Prediction and Replacement ---"]
    numbered_outputs = []

    for idx, sentence in enumerate(groups, 1):
        if len(sentence.split()) > 3:
            keyword = replace_medical_terms_with_biobert(sentence)
            output_lines.append(f"\n[{idx}] {sentence} → Predicted Substitution: {keyword}")
            numbered_outputs.append(f"{idx}. {keyword}.")

    output_lines.append("\nSubstitute words:")
    output_lines.extend(numbered_outputs)

    with open("modified_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    return "\n".join(output_lines)

# ----- GUI Functions -----

def toggle_mode():
    selected_mode = mode_var.get()
    if selected_mode == "ocr":
        input_label.pack_forget()
        input_text.pack_forget()
        simplify_btn.pack_forget()
        upload_btn.pack(side="left", padx=5)
        output_frame.pack_forget()
    else:
        input_label.pack(anchor="w")
        input_text.pack(pady=5)
        input_text.config(state="normal")
        input_text.delete("1.0", tk.END)
        input_label.config(text="Enter Medical Text:")
        simplify_btn.pack(side="left", padx=5)
        upload_btn.pack_forget()
        output_frame.pack_forget()
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.config(state="disabled")

def simplify_input():
    original = input_text.get("1.0", tk.END).strip()
    if original:
        simplified = substitute_long_text_with_keyword(original)
        output_label.config(text="Simplified Text:")
        output_frame.pack(pady=10, padx=20, fill="x")
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, simplified)
        output_text.config(state="disabled")
    else:
        messagebox.showwarning("Warning", "No text available to simplify")

def load_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        extracted = extract_text_from_pdf(file_path)
        output_frame.pack_forget()
        output_label.config(text="Output:")
        input_frame.pack(pady=10, padx=20, fill="x")
        input_label.pack(anchor="w")
        input_text.pack(pady=5)
        input_text.config(state="normal")
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, extracted)
        input_text.config(state="disabled")
        input_label.config(text="PDF Extracted Text:")
        simplify_btn.pack(side="left", padx=5)
        upload_btn.pack_forget()

# ----- GUI Setup -----

def run_gui():
    root = tk.Tk()
    root.title("Medical Terminology Simplifier")
    root.geometry("800x650")
    root.configure(bg="#eaf6fb")

    canvas = tk.Canvas(root, width=800, height=650)
    canvas.pack(fill="both", expand=True)

    for i in range(0, 650, 2):
        color = "#%02x%02x%02x" % (200 - i//4, 240 - i//6, 255)
        canvas.create_rectangle(0, i, 800, i+2, outline=color, fill=color)

    main_frame = tk.Frame(root, bg="white", bd=2, relief=tk.RIDGE)
    main_frame.place(relx=0.5, rely=0.5, anchor="center", width=700, height=600)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("TButton", font=('Helvetica', 10, 'bold'), padding=6, background="#4a90e2", foreground="white")
    style.map("TButton", background=[("active", "#357ABD")])
    style.configure("TRadiobutton", font=('Helvetica', 10), background="#ffffff")

    header = tk.Label(main_frame, text="🩺 Medical Terminology Simplifier", font=('Helvetica', 16, 'bold'), bg="#ffffff", fg="#2c3e50")
    header.pack(pady=(15, 5))

    mode_frame = tk.Frame(main_frame, bg="#ffffff")
    mode_frame.pack(pady=10)

    global mode_var
    mode_var = tk.StringVar(value="text")
    ttk.Radiobutton(mode_frame, text="Text Simplification Mode", variable=mode_var, value="text", command=toggle_mode).pack(side="left", padx=10)
    ttk.Radiobutton(mode_frame, text="PDF OCR Mode", variable=mode_var, value="ocr", command=toggle_mode).pack(side="left", padx=10)

    global input_frame, input_label, input_text, simplify_btn, upload_btn, output_frame, output_label, output_text

    input_frame = tk.Frame(main_frame, bg="#ffffff")
    input_frame.pack(pady=10, padx=20, fill="x")
    input_label = tk.Label(input_frame, text="Enter Medical Text:", font=('Helvetica', 10, 'bold'), bg="#ffffff")
    input_text = scrolledtext.ScrolledText(input_frame, height=10, width=70, font=('Helvetica', 10), wrap=tk.WORD, bd=2, relief=tk.GROOVE, bg="#f8faff")

    button_frame = tk.Frame(main_frame, bg="#ffffff")
    button_frame.pack(pady=5)
    simplify_btn = ttk.Button(button_frame, text="Simplify Terminology", command=simplify_input)
    upload_btn = ttk.Button(button_frame, text="Upload PDF (OCR)", command=load_pdf)

    output_frame = tk.Frame(main_frame, bg="#ffffff")
    output_label = tk.Label(output_frame, text="Output:", font=('Helvetica', 10, 'bold'), bg="#ffffff")
    output_label.pack(anchor="w")
    output_text = scrolledtext.ScrolledText(output_frame, height=12, width=70, font=('Helvetica', 10), wrap=tk.WORD, bd=2, relief=tk.GROOVE, bg="#f3faff", state="disabled")
    output_text.pack(pady=5)

    footer = tk.Label(main_frame, text="© 2025 Medical Simplifier Tool", font=('Helvetica', 8), bg="#ffffff", fg="#7f8c8d")
    footer.pack(side="bottom", pady=10)

    toggle_mode()
    root.mainloop()

# Run the application
if __name__ == "__main__":
    run_gui()
