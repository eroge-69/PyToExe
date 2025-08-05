from tkinter import *
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import threading
import os
import requests
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import PyPDF2
import re
import docx
from pptx import Presentation

# Try to import transformers for offline model
try:
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Try to import additional document libraries
try:
    import docx

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from pptx import Presentation

    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

try:
    import mammoth

    MAMMOTH_AVAILABLE = True
except ImportError:
    MAMMOTH_AVAILABLE = False


class PDFSummarizerApp:
    def __init__(self):
        self.window = Tk()
        self.window.title("Bel Code - PDF Summarizer")
        self.window.geometry("1200x800")
        self.window.configure(bg='#f0f0f0')

        # Variables
        self.precision_var = StringVar(value="medium")
        self.ai_model_var = StringVar(value="online")
        self.file_paths = []
        self.offline_summarizer = None

        # Initialize offline model if available
        self.init_offline_model()

        self.create_widgets()

    def init_offline_model(self):
        """Initialize offline summarization model"""
        if TRANSFORMERS_AVAILABLE:
            try:
                model_path = os.path.join(os.getcwd(), "models", "bart-large-cnn")
                self.offline_summarizer = pipeline(
                    "summarization",
                    model=model_path,
                    tokenizer=model_path,
                    device=-1  # CPU
                )
            except Exception as e:
                print(f"Failed to load offline model: {e}")
                self.offline_summarizer = None

    def create_widgets(self):
        # Main container with scrollable frame
        main_frame = Frame(self.window, bg='#f0f0f0')
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Left panel for controls
        left_panel = Frame(main_frame, bg='#ffffff', relief=RAISED, bd=2)
        left_panel.pack(side=LEFT, fill=Y, padx=(0, 5))

        # Right panel for text comparison
        right_panel = Frame(main_frame, bg='#ffffff', relief=RAISED, bd=2)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))

        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)

    def create_left_panel(self, parent):
        # Title
        title_label = Label(parent, text="PDF Summarizer", font=("Arial", 16, "bold"), bg='#ffffff')
        title_label.pack(pady=10)

        # Input Files Section
        Label(parent, text="Input Files (PDF, DOCX, TXT, PPTX)", font=("Arial", 12, "bold"), bg='#ffffff').pack(
            pady=(10, 5))

        files_frame = Frame(parent, bg='#ffffff')
        files_frame.pack(pady=5, padx=10, fill=X)

        self.files_listbox = Listbox(files_frame, height=4, width=40)
        self.files_listbox.pack(side=LEFT, fill=BOTH, expand=True)

        files_scroll = Scrollbar(files_frame, orient=VERTICAL)
        files_scroll.pack(side=RIGHT, fill=Y)
        self.files_listbox.config(yscrollcommand=files_scroll.set)
        files_scroll.config(command=self.files_listbox.yview)

        buttons_frame = Frame(parent, bg='#ffffff')
        buttons_frame.pack(pady=5, padx=10, fill=X)

        Button(buttons_frame, text="Add Files", command=self.add_files, bg='#4CAF50', fg='white').pack(side=LEFT,
                                                                                                       padx=2)
        Button(buttons_frame, text="Remove Selected", command=self.remove_file, bg='#f44336', fg='white').pack(
            side=LEFT, padx=2)
        Button(buttons_frame, text="Clear All", command=self.clear_files, bg='#ff9800', fg='white').pack(side=LEFT,
                                                                                                         padx=2)

        # AI Model Selection
        Label(parent, text="AI Model", font=("Arial", 12, "bold"), bg='#ffffff').pack(pady=(20, 5))

        model_frame = Frame(parent, bg='#ffffff')
        model_frame.pack(pady=5, padx=10)

        Radiobutton(model_frame, text="Online AI", variable=self.ai_model_var, value="online",
                    bg='#ffffff', command=self.on_model_change).pack(anchor=W)

        offline_text = "Offline AI" + ("" if TRANSFORMERS_AVAILABLE else " (Not Available)")
        offline_state = NORMAL if TRANSFORMERS_AVAILABLE else DISABLED

        Radiobutton(model_frame, text=offline_text, variable=self.ai_model_var, value="offline",
                    bg='#ffffff', state=offline_state, command=self.on_model_change).pack(anchor=W)

        # Precision Selection
        Label(parent, text="Summary Precision", font=("Arial", 12, "bold"), bg='#ffffff').pack(pady=(20, 5))

        precision_frame = Frame(parent, bg='#ffffff')
        precision_frame.pack(pady=5, padx=10)

        Radiobutton(precision_frame, text="Low (Brief)", variable=self.precision_var, value="low", bg='#ffffff').pack(
            anchor=W)
        Radiobutton(precision_frame, text="Medium (Balanced)", variable=self.precision_var, value="medium",
                    bg='#ffffff').pack(anchor=W)
        Radiobutton(precision_frame, text="High (Detailed)", variable=self.precision_var, value="high",
                    bg='#ffffff').pack(anchor=W)

        # Progress bar
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=10, padx=10, fill=X)

        # Status label
        self.status_label = Label(parent, text="Ready", font=("Arial", 10), bg='#ffffff', fg='#666666')
        self.status_label.pack(pady=5)

        # Summarize button
        self.summarize_btn = Button(parent, text="Summarize Files", command=self.start_summarization,
                                    bg='#2196F3', fg='white', font=("Arial", 12, "bold"), height=2)
        self.summarize_btn.pack(pady=20, padx=10, fill=X)

        # Save button
        self.save_btn = Button(parent, text="Save Summary as PDF", command=self.save_summary,
                               bg='#9C27B0', fg='white', font=("Arial", 12), state=DISABLED)
        self.save_btn.pack(pady=5, padx=10, fill=X)

        # Supported formats info
        formats_label = Label(parent, text="Supported: PDF, DOCX, DOC, PPTX, TXT",
                              font=("Arial", 8), bg='#ffffff', fg='#666666')
        formats_label.pack(pady=2)

    def create_right_panel(self, parent):
        # Title for comparison
        Label(parent, text="Text Comparison", font=("Arial", 14, "bold"), bg='#ffffff').pack(pady=10)

        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Original text tab
        original_frame = Frame(self.notebook, bg='#ffffff')
        self.notebook.add(original_frame, text="Original Text")

        Label(original_frame, text="Original Content", font=("Arial", 12, "bold"), bg='#ffffff').pack(pady=5)
        self.original_text = ScrolledText(original_frame, wrap=WORD, height=25, width=60)
        self.original_text.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Summary tab
        summary_frame = Frame(self.notebook, bg='#ffffff')
        self.notebook.add(summary_frame, text="Summary")

        Label(summary_frame, text="Generated Summary", font=("Arial", 12, "bold"), bg='#ffffff').pack(pady=5)
        self.summary_text = ScrolledText(summary_frame, wrap=WORD, height=25, width=60)
        self.summary_text.pack(fill=BOTH, expand=True, padx=10, pady=5)

    def add_files(self):
        # Define supported file types
        filetypes = [
            ("All Supported", "*.pdf;*.txt;*.docx;*.pptx;*.doc"),
            ("PDF files", "*.pdf"),
            ("Text files", "*.txt"),
            ("Word documents", "*.docx;*.doc"),
            ("PowerPoint presentations", "*.pptx"),
            ("All files", "*.*")
        ]

        file_paths = filedialog.askopenfilenames(
            title="Select document files",
            filetypes=filetypes
        )

        for file_path in file_paths:
            if file_path not in self.file_paths:
                self.file_paths.append(file_path)
                self.files_listbox.insert(END, os.path.basename(file_path))

    def remove_file(self):
        selected = self.files_listbox.curselection()
        if selected:
            index = selected[0]
            self.files_listbox.delete(index)
            del self.file_paths[index]

    def clear_files(self):
        self.files_listbox.delete(0, END)
        self.file_paths.clear()
        self.original_text.delete("1.0", END)
        self.summary_text.delete("1.0", END)

    def on_model_change(self):
        if self.ai_model_var.get() == "offline" and not TRANSFORMERS_AVAILABLE:
            messagebox.showwarning("Warning", "Offline AI model is not available. Please install transformers library.")
            self.ai_model_var.set("online")

    def extract_text_from_file(self, file_path):
        """Extract text from various file formats"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.pdf':
                return self.extract_text_from_pdf(file_path)
            elif file_extension == '.txt':
                return self.extract_text_from_txt(file_path)
            elif file_extension == '.docx':
                return self.extract_text_from_docx(file_path)
            elif file_extension == '.doc':
                return self.extract_text_from_doc(file_path)
            elif file_extension == '.pptx':
                return self.extract_text_from_pptx(file_path)
            else:
                return f"Unsupported file format: {file_extension}"

        except Exception as e:
            return f"Error extracting text from {file_path}: {str(e)}"

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"

    def extract_text_from_txt(self, file_path):
        """Extract text from TXT file"""
        try:
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue

            # If all encodings fail, try with error handling
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()

        except Exception as e:
            return f"Error reading text file: {str(e)}"

    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX file"""
        try:
            if not DOCX_AVAILABLE:
                return "python-docx library not available. Please install: pip install python-docx"

            doc = docx.Document(file_path)
            text = ""

            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "
                    text += "\n"

            return text.strip()

        except Exception as e:
            return f"Error extracting DOCX text: {str(e)}"

    def extract_text_from_doc(self, file_path):
        """Extract text from DOC file using mammoth"""
        try:
            if not MAMMOTH_AVAILABLE:
                return "mammoth library not available. Please install: pip install mammoth"

            with open(file_path, "rb") as docx_file:
                result = mammoth.extract_raw_text(docx_file)
                return result.value

        except Exception as e:
            # Fallback: suggest conversion
            return f"Error extracting DOC text: {str(e)}\nPlease convert .doc to .docx format for better compatibility."

    def extract_text_from_pptx(self, file_path):
        """Extract text from PowerPoint PPTX file"""
        try:
            if not PPTX_AVAILABLE:
                return "python-pptx library not available. Please install: pip install python-pptx"

            presentation = Presentation(file_path)
            text = ""

            for slide_num, slide in enumerate(presentation.slides, 1):
                text += f"\n--- Slide {slide_num} ---\n"

                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"

                    # Extract text from tables in slides
                    if shape.has_table:
                        table = shape.table
                        for row in table.rows:
                            for cell in row.cells:
                                text += cell.text + " "
                            text += "\n"

            return text.strip()

        except Exception as e:
            return f"Error extracting PowerPoint text: {str(e)}"

    def chunk_text(self, text, max_length=1000):
        """Split text into chunks for processing"""
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk + sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def summarize_online(self, text, precision):
        """Summarize text using online API (placeholder)"""
        try:
            # This is a placeholder - you would integrate with actual API like OpenAI, Hugging Face, etc.
            # For demo purposes, we'll create a simple extractive summary

            sentences = re.split(r'[.!?]+', text)

            if precision == "low":
                summary_length = min(2, len(sentences) // 4)
            elif precision == "medium":
                summary_length = min(4, len(sentences) // 2)
            else:  # high
                summary_length = min(6, len(sentences) // 1.5)

            # Simple extractive summary (take first few sentences)
            summary_sentences = sentences[:int(summary_length)]
            summary = ". ".join(summary_sentences) + "."

            return f"[Online AI Summary - {precision.upper()} precision]\n\n{summary}"

        except Exception as e:
            return f"Error in online summarization: {str(e)}"

    def summarize_offline(self, text, precision):
        """Summarize text using offline model"""
        try:
            if not self.offline_summarizer:
                return "Offline model not available"

            # Adjust parameters based on precision
            if precision == "low":
                max_length = 50
                min_length = 20
            elif precision == "medium":
                max_length = 130
                min_length = 50
            else:  # high
                max_length = 200
                min_length = 100

            # Process in chunks if text is too long
            chunks = self.chunk_text(text, max_length=1000)
            summaries = []

            for chunk in chunks:
                if len(chunk.strip()) > 50:  # Only process meaningful chunks
                    summary = self.offline_summarizer(chunk,
                                                      max_length=max_length,
                                                      min_length=min_length,
                                                      do_sample=False)
                    summaries.append(summary[0]['summary_text'])

            final_summary = " ".join(summaries)
            return f"[Offline AI Summary - {precision.upper()} precision]\n\n{final_summary}"

        except Exception as e:
            return f"Error in offline summarization: {str(e)}"

    def process_files(self):
        """Process all selected files"""
        try:
            if not self.file_paths:
                self.status_label.config(text="No files selected")
                return

            self.summarize_btn.config(state=DISABLED)
            self.progress_var.set(0)

            all_text = ""
            all_summaries = []

            total_files = len(self.file_paths)

            for i, file_path in enumerate(self.file_paths):
                self.status_label.config(text=f"Processing {os.path.basename(file_path)}...")
                self.window.update()

                # Extract text based on file type
                text = self.extract_text_from_file(file_path)
                all_text += f"\n\n=== {os.path.basename(file_path)} ===\n\n{text}"

                # Generate summary
                if self.ai_model_var.get() == "online":
                    summary = self.summarize_online(text, self.precision_var.get())
                else:
                    summary = self.summarize_offline(text, self.precision_var.get())

                all_summaries.append(f"\n\n=== Summary of {os.path.basename(file_path)} ===\n\n{summary}")

                # Update progress
                progress = ((i + 1) / total_files) * 100
                self.progress_var.set(progress)
                self.window.update()

            # Update text areas
            self.original_text.delete("1.0", END)
            self.original_text.insert("1.0", all_text)

            self.summary_text.delete("1.0", END)
            self.summary_text.insert("1.0", "\n".join(all_summaries))

            self.status_label.config(text="Summarization completed successfully!")
            self.save_btn.config(state=NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Error occurred during processing")
        finally:
            self.summarize_btn.config(state=NORMAL)
            self.progress_var.set(0)

    def start_summarization(self):
        """Start summarization in a separate thread"""
        if not self.file_paths:
            messagebox.showwarning("Warning", "Please select at least one document file.")
            return

        # Check if any unsupported files
        supported_extensions = ['.pdf', '.txt', '.docx', '.doc', '.pptx']
        unsupported_files = []

        for file_path in self.file_paths:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in supported_extensions:
                unsupported_files.append(os.path.basename(file_path))

        if unsupported_files:
            response = messagebox.askyesno(
                "Unsupported Files",
                f"The following files may not be supported:\n{', '.join(unsupported_files)}\n\nContinue anyway?"
            )
            if not response:
                return

        # Start processing in a separate thread to prevent UI freezing
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()

    def save_summary(self):
        """Save summary as PDF"""
        try:
            summary_content = self.summary_text.get("1.0", END).strip()

            if not summary_content:
                messagebox.showwarning("Warning", "No summary to save.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Summary As"
            )

            if file_path:
                # Create PDF
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []

                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    spaceAfter=30,
                    alignment=1  # Center alignment
                )

                title = Paragraph("PDF Summary Report", title_style)
                story.append(title)
                story.append(Spacer(1, 12))

                # Metadata
                meta_style = styles['Normal']
                meta = Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
                                 f"AI Model: {self.ai_model_var.get().title()}<br/>"
                                 f"Precision: {self.precision_var.get().title()}<br/>"
                                 f"Files processed: {len(self.file_paths)}", meta_style)
                story.append(meta)
                story.append(Spacer(1, 20))

                # Summary content
                summary_paragraphs = summary_content.split('\n\n')
                for para in summary_paragraphs:
                    if para.strip():
                        p = Paragraph(para.replace('\n', '<br/>'), styles['Normal'])
                        story.append(p)
                        story.append(Spacer(1, 12))

                doc.build(story)

                messagebox.showinfo("Success", f"Summary saved successfully to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")

    def run(self):
        self.window.mainloop()


# Check for required dependencies
missing_deps = []

try:
    import PyPDF2
except ImportError:
    missing_deps.append("PyPDF2")

try:
    from reportlab.lib.pagesizes import letter
except ImportError:
    missing_deps.append("reportlab")

# Check for optional dependencies
optional_deps = []
if not DOCX_AVAILABLE:
    optional_deps.append("python-docx")
if not PPTX_AVAILABLE:
    optional_deps.append("python-pptx")
if not MAMMOTH_AVAILABLE:
    optional_deps.append("mammoth")

if missing_deps:
    print("Missing required dependencies. Please install:")
    print("pip install " + " ".join(missing_deps))

if optional_deps:
    print("Optional dependencies for additional file formats:")
    print("pip install " + " ".join(optional_deps))

if not TRANSFORMERS_AVAILABLE:
    print("pip install transformers torch  # For offline AI model")

if not missing_deps:  # Only run if required deps are available
    # Run the application
    if __name__ == "__main__":
        app = PDFSummarizerApp()
        app.run()