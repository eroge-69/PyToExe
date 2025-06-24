import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pdfplumber
from transformers import pipeline
import threading

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Summarize text
def summarize_text(text, max_chunk=1000):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    return "\n".join(summaries)

# Function triggered by "Summarize" button
def run_summarization():
    file_path = file_path_var.get()
    if not file_path:
        messagebox.showwarning("Warning", "Please select a PDF file first!")
        return

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, "Extracting and summarizing. Please wait...\n")

    def worker():
        try:
            text = extract_text_from_pdf(file_path)
            if not text.strip():
                output_text.delete(1.0, tk.END)
                output_text.insert(tk.END, "⚠️ No text found in the PDF.")
                return
            summary = summarize_text(text)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, summary)
        except Exception as e:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, f"Error: {e}")

    threading.Thread(target=worker).start()

# Function to browse PDF files
def browse_file():
    file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file:
        file_path_var.set(file)

# Create main window
root = tk.Tk()
root.title("PDF Summarizer AI")
root.geometry("700x500")

file_path_var = tk.StringVar()

# File selection frame
frame = tk.Frame(root)
frame.pack(pady=10, padx=10, fill=tk.X)

tk.Label(frame, text="Select PDF file:").pack(side=tk.LEFT)
file_entry = tk.Entry(frame, textvariable=file_path_var, width=60)
file_entry.pack(side=tk.LEFT, padx=5)
browse_btn = tk.Button(frame, text="Browse", command=browse_file)
browse_btn.pack(side=tk.LEFT)

# Summarize button
summarize_btn = tk.Button(root, text="Summarize PDF", command=run_summarization)
summarize_btn.pack(pady=10)

# Output text box
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
output_text.pack(padx=10, pady=10)

root.mainloop()
