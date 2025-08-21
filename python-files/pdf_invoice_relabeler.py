
"""
PDF Invoice Relabeler — replace "Documento Cortesia" with "Fattura/Invoice"
----------------------------------------------------------------------------
A tiny desktop app (Windows/Mac/Linux) that lets you pick a PDF and outputs
a modified copy alongside it (filename ends with "_modified.pdf").

How it works
- Uses PyMuPDF (fitz) to *search* for the exact text "Documento Cortesia".
- Draws a white rectangle to cover the original text.
- Writes "Fattura/Invoice" centered in the same box (bold Helvetica).
- Repeats for all pages/occurrences found.

Install once:
    pip install pymupdf

Run:
    python pdf_invoice_relabeler.py

Or run headless (CLI):
    python pdf_invoice_relabeler.py "input.pdf"

Notes:
- This edits only the visible label. It does not change embedded metadata.
- If your PDFs use a different casing or extra spaces, you can add those terms
  to SEARCH_TERMS below.
"""

import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

try:
    import fitz  # PyMuPDF
except Exception as e:
    fitz = None

# Terms to replace (exact match). Add variations if needed.
SEARCH_TERMS = [
    "Documento Cortesia",
]

REPLACEMENT_TEXT = "Fattura/Invoice"

# Style for the replacement text
FONT_NAME = "helv"         # 'helv' is Helvetica in PyMuPDF standard fonts
FONT_SIZE = 12             # Adjust if your PDF uses bigger/smaller label
TEXT_COLOR = (0, 0, 0)     # black RGB
PADDING_SCALE = 0.10       # expand the white cover box by 10% for safety


def replace_on_page(page, terms=SEARCH_TERMS, replacement=REPLACEMENT_TEXT):
    """
    Replace all occurrences of any term in `terms` on a given page.
    Returns the number of replacements performed.
    """
    total_replacements = 0

    for term in terms:
        # search_for returns a list of rects where the term is found
        rects = page.search_for(term, quads=False)
        for r in rects:
            # Expand rect slightly so we fully cover original glyphs
            pad_x = (r.x1 - r.x0) * PADDING_SCALE
            pad_y = (r.y1 - r.y0) * PADDING_SCALE
            cover = fitz.Rect(r.x0 - pad_x, r.y0 - pad_y, r.x1 + pad_x, r.y1 + pad_y)

            # 1) Draw white rectangle to cover original text
            page.draw_rect(cover, fill=(1, 1, 1), color=None, width=0)

            # 2) Draw replacement text centered within the original rect
            # Use text alignment: we can compute center and use page.insert_textbox
            text_rect = r  # original rectangle for alignment
            page.insert_textbox(
                text_rect,
                replacement,
                fontname=FONT_NAME,
                fontsize=FONT_SIZE,
                color=TEXT_COLOR,
                align=1,  # 0=left,1=center,2=right,3=justify
            )

            total_replacements += 1

    return total_replacements


def process_pdf(input_path: Path) -> Path:
    """
    Open the PDF, replace terms on all pages, write an output PDF
    with suffix '_modified.pdf'. Returns the output path.
    """
    if fitz is None:
        raise RuntimeError(
            "PyMuPDF (fitz) is not installed. Install it with: pip install pymupdf"
        )

    doc = fitz.open(input_path.as_posix())
    total = 0
    for page in doc:
        total += replace_on_page(page)

    output_path = input_path.with_name(input_path.stem + "_modified.pdf")
    doc.save(output_path.as_posix())
    doc.close()

    if total == 0:
        # Still saved a copy, but inform user no labels were found
        print(f"WARNING: No occurrences found. Saved copy as '{output_path.name}'.")
    else:
        print(f"Replaced {total} occurrence(s). Saved '{output_path.name}'.")

    return output_path


def run_cli(args):
    if len(args) >= 2:
        in_file = Path(args[1])
        if not in_file.exists():
            print(f"Input file not found: {in_file}")
            sys.exit(1)
        out = process_pdf(in_file)
        print(f"Done: {out}")
        return True
    return False


def run_gui():
    root = tk.Tk()
    root.title("PDF Invoice Relabeler — 'Documento Cortesia' → 'Fattura/Invoice'")
    root.geometry("520x220")
    root.resizable(False, False)

    def choose_and_process():
        in_path = filedialog.askopenfilename(
            title="Choose a PDF",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not in_path:
            return
        try:
            out_path = process_pdf(Path(in_path))
            messagebox.showinfo("Done", f"Saved:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    frm = tk.Frame(root, padx=20, pady=20)
    frm.pack(expand=True, fill=tk.BOTH)

    lbl = tk.Label(
        frm,
        text=(
            "This app replaces the label 'Documento Cortesia' with 'Fattura/Invoice'\n"
            "in the same position on the page.\n\n"
            "Click the button below, pick a PDF, and the modified copy will be\n"
            "saved next to it with the suffix '_modified.pdf'."
        ),
        justify="left",
    )
    lbl.pack(anchor="w")

    btn = tk.Button(frm, text="Choose PDF and Convert", command=choose_and_process)
    btn.pack(pady=16, anchor="center")

    foot = tk.Label(frm, text="Tip: If nothing changes, the exact phrase wasn't found.", fg="#555")
    foot.pack(anchor="w")

    root.mainloop()


if __name__ == "__main__":
    # If a path is passed, do CLI mode; otherwise open the GUI.
    if not run_cli(sys.argv):
        run_gui()
