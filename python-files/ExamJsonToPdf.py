import json, re, os, threading, requests
from io import BytesIO
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ----------------- HTML helpers -----------------

def clean_html(text):
    """Remove unsupported HTML tags except <img> which we handle separately."""
    if not text:
        return ""
    text = re.sub(r'<\s*span[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</\s*span\s*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*div[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</\s*div\s*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<(?!img\b)[^>]+>', '', text)  # strip any tag that's not <img>
    return text.strip()

def process_text_with_images(
    text, base_dir, base_url, para_style, session, log=None, cancel_event=None
):
    """
    Split text on <img> tags and return a list of ReportLab flowables (Paragraphs + Images).
    para_style: ParagraphStyle to use for any text parts produced here.
    """
    flows = []
    styles = getSampleStyleSheet()
    ital = styles["Italic"]

    img_pattern = re.compile(r'<img[^>]*src="([^"]+)"[^>]*>', re.IGNORECASE)
    last = 0

    def add_log(msg):
        if log:
            log(msg)

    for m in img_pattern.finditer(text or ""):
        if cancel_event and cancel_event.is_set():
            return flows

        before = text[last:m.start()]
        if before.strip():
            flows.append(Paragraph(clean_html(before), para_style))

        src = m.group(1) or ""
        # Expand relative to absolute URL
        if src.startswith("/"):
            full = (base_url.rstrip("/") + src) if base_url else src
        else:
            full = src

        try:
            if full.startswith("http"):
                add_log(f"Downloading image: {full}")
                resp = session.get(full, timeout=8)
                if resp.status_code == 200:
                    flows.append(Image(BytesIO(resp.content), width=300, height=200))
                else:
                    flows.append(Paragraph(f"[Image failed: HTTP {resp.status_code}]", ital))
            else:
                # Local fallback
                fname = os.path.basename(full)
                cand = [
                    os.path.join(base_dir, fname),
                    os.path.join(base_dir, "exam-media", fname),
                    os.path.join(base_dir, "media", fname),
                ]
                path = next((p for p in cand if os.path.exists(p)), None)
                if path:
                    flows.append(Image(path, width=300, height=200))
                else:
                    flows.append(Paragraph(f"[Image not found: {fname}]", ital))
        except Exception as e:
            flows.append(Paragraph(f"[Image error: {str(e)[:120]}]", ital))

        last = m.end()

    after = (text or "")[last:]
    if after.strip():
        flows.append(Paragraph(clean_html(after), para_style))

    return flows

# ----------------- PDF generation (worker-safe) -----------------

def generate_pdf(
    json_path, pdf_path, show_comments, base_url, log, notify_done, cancel_event
):
    try:
        log("Loading JSON…")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        questions = data.get("questions", [])
        if not questions:
            raise ValueError("No 'questions' array found in JSON.")

        def maybe_int(v):
            try:
                return int(str(v))
            except Exception:
                return 10**9

        questions = sorted(
            questions,
            key=lambda q: (maybe_int(q.get("index") or q.get("id")),)
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], spaceAfter=20)
        question_style = ParagraphStyle('QuestionStyle', parent=styles['Heading2'], spaceAfter=10)
        normal_style   = styles['Normal']
        option_style   = ParagraphStyle('OptionStyle', parent=styles['Normal'], leftIndent=20)
        answer_style   = ParagraphStyle('AnswerStyle', parent=styles['Normal'], textColor='green', spaceBefore=5)
        comment_style  = ParagraphStyle('CommentStyle', parent=styles['Italic'], textColor='gray', leftIndent=30)

        elements = []
        provider = data.get('provider', 'Unknown Provider')
        exam_code = data.get('examCode') or data.get('exam') or "Unknown Exam"

        elements.append(Paragraph(f"Provider: {provider} — Exam: {exam_code}", title_style))
        elements.append(Spacer(1, 12))

        base_dir = os.path.dirname(json_path)
        # --- FIX: Add headers here ---
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0 Safari/537.36"
            ),
            "Referer": "https://www.examtopics.com/"
        })

        total = len(questions)
        for idx, q in enumerate(questions, start=1):
            if cancel_event.is_set():
                log("Cancelled.")
                notify_done(cancelled=True)
                return

            log(f"Processing Q{idx}/{total}…")

            q_index  = q.get("index") or q.get("id") or idx
            q_body   = q.get("body") or q.get("question", "")
            q_opts   = q.get("options") or q.get("choices", [])
            q_ans    = q.get("answer", "")
            q_comms  = q.get("comments") or []
            q_expl   = q.get("explanation", "")

            # Question number/title
            elements.append(Paragraph(f"Q{q_index}.", question_style))
            # Body (text + images)
            elements += process_text_with_images(q_body, base_dir, base_url, normal_style, session, log, cancel_event)

            # Options
            for opt in q_opts:
                elements += process_text_with_images(str(opt), base_dir, base_url, option_style, session, log, cancel_event)

            # Answer
            if q_ans:
                elements.append(Paragraph("Answer:", answer_style))
                elements += process_text_with_images(str(q_ans), base_dir, base_url, normal_style, session, log, cancel_event)

            # Explanation
            if q_expl:
                elements.append(Paragraph("Explanation:", comment_style))
                elements += process_text_with_images(str(q_expl), base_dir, base_url, normal_style, session, log, cancel_event)

            # Comments (optional)
            if show_comments and q_comms:
                elements.append(Paragraph("Comments:", styles['Italic']))
                for c in q_comms:
                    if isinstance(c, dict):
                        c_text = f"{c.get('date','')}: {c.get('content','')}"
                    else:
                        c_text = str(c)
                    elements += process_text_with_images(c_text, base_dir, base_url, comment_style, session, log, cancel_event)

            if idx != total:
                elements.append(Spacer(1, 18))
                elements.append(PageBreak())

        log("Building PDF…")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        doc.build(elements)
        log("Done.")
        notify_done(success=True, path=pdf_path)

    except Exception as e:
        notify_done(success=False, error=str(e))

# ----------------- GUI -----------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Exam JSON → PDF")
        self.geometry("720x480")
        self.resizable(False, False)

        self.json_path = tk.StringVar()
        self.pdf_path  = tk.StringVar()
        self.base_url  = tk.StringVar(value="http://192.168.1.6:3000/api/examtopics")
        self.include_comments = tk.BooleanVar(value=False)

        self.cancel_event = threading.Event()
        self.worker = None

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, **pad)

        title = ttk.Label(frm, text="Exam JSON to PDF Converter", font=("Segoe UI", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(6, 12))

        ttk.Label(frm, text="1) Exam JSON file:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.json_path, width=70).grid(row=2, column=0, columnspan=2, sticky="we")
        ttk.Button(frm, text="Browse…", command=self.pick_json).grid(row=2, column=2, sticky="e")

        ttk.Label(frm, text="2) Output PDF path:").grid(row=3, column=0, sticky="w", pady=(8,0))
        ttk.Entry(frm, textvariable=self.pdf_path, width=70).grid(row=4, column=0, columnspan=2, sticky="we")
        ttk.Button(frm, text="Save as…", command=self.pick_pdf).grid(row=4, column=2, sticky="e")

        ttk.Label(frm, text="Base URL for images (used for /relative src):").grid(row=5, column=0, sticky="w", pady=(8,0))
        ttk.Entry(frm, textvariable=self.base_url, width=70).grid(row=6, column=0, columnspan=2, sticky="we")

        ttk.Checkbutton(frm, text="Include comments", variable=self.include_comments).grid(row=6, column=2, sticky="e")

        # Buttons
        self.btn_run = ttk.Button(frm, text="Generate PDF", command=self.start_worker)
        self.btn_run.grid(row=7, column=0, sticky="w", pady=(10, 4))

        self.btn_cancel = ttk.Button(frm, text="Cancel", command=self.cancel_worker, state="disabled")
        self.btn_cancel.grid(row=7, column=1, sticky="w", pady=(10, 4))

        # Progress + log
        self.bar = ttk.Progressbar(frm, mode="indeterminate")
        self.bar.grid(row=8, column=0, columnspan=3, sticky="we", pady=(6,2))

        self.logbox = tk.Text(frm, height=11, state="disabled")
        self.logbox.grid(row=9, column=0, columnspan=3, sticky="nsew", pady=(6, 8))

        frm.rowconfigure(9, weight=1)
        frm.columnconfigure(0, weight=1)

    def pick_json(self):
        path = filedialog.askopenfilename(title="Select Exam JSON", filetypes=[("JSON files", "*.json")])
        if path:
            self.json_path.set(path)

    def pick_pdf(self):
        path = filedialog.asksaveasfilename(title="Save PDF As", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            self.pdf_path.set(path)

    # ---- Logging helpers ----
    def log(self, msg):
        self.logbox.configure(state="normal")
        self.logbox.insert("end", msg + "\n")
        self.logbox.see("end")
        self.logbox.configure(state="disabled")
        self.update_idletasks()

    # ---- Worker control ----
    def start_worker(self):
        if not self.json_path.get():
            messagebox.showwarning("Missing input", "Please select an exam JSON file.")
            return
        if not self.pdf_path.get():
            messagebox.showwarning("Missing output", "Please choose where to save the PDF.")
            return

        self.cancel_event.clear()
        self.btn_run.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.bar.start(10)
        self.log("Starting…")

        def notify_done(success=None, path=None, error=None, cancelled=False):
            # re-enter UI thread
            def _finish():
                self.bar.stop()
                self.btn_run.configure(state="normal")
                self.btn_cancel.configure(state="disabled")
                if cancelled:
                    self.log("Cancelled by user.")
                elif success:
                    self.log(f"PDF created: {path}")
                    messagebox.showinfo("Success", f"PDF created successfully:\n{path}")
                else:
                    self.log(f"Error: {error}")
                    messagebox.showerror("Error", f"Failed to create PDF:\n{error}")
            self.after(0, _finish)

        def ui_log(msg):
            self.after(0, lambda: self.log(msg))

        # Thread target
        def run():
            generate_pdf(
                self.json_path.get(),
                self.pdf_path.get(),
                self.include_comments.get(),
                self.base_url.get().strip(),
                ui_log,
                notify_done,
                self.cancel_event
            )

        self.worker = threading.Thread(target=run, daemon=True)
        self.worker.start()

    def cancel_worker(self):
        if self.worker and self.worker.is_alive():
            self.cancel_event.set()
            self.log("Cancelling…")

if __name__ == "__main__":
    App().mainloop()
