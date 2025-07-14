#!/usr/bin/env python3
import sys
import fitz  # PyMuPDF

def remove_grey_watermark(page, grey_rgb=(0.890196, 0.890196, 0.890196)):
    """
    Strips out any filled shapes drawn with the exact grey_rgb color
    (the watermark) by removing from the setrgbcolor ("rg") call
    through the following fill ("f" or "F") operator.
    """
    raw = page.read_contents().splitlines()
    out_lines = []
    skip = False

    # Build the grey color command, e.g. b"0.890196 0.890196 0.890196 rg"
    grey_cmd = ("%.6f %.6f %.6f rg" % grey_rgb).encode()

    for line in raw:
        if not skip and grey_cmd in line and line.strip().endswith(b"rg"):
            skip = True
            continue
        if skip:
            # Stop skipping once we encounter the fill operator
            if line.strip().endswith(b"f") or line.strip().endswith(b"F"):
                skip = False
            continue
        out_lines.append(line)

    # Write back if any removal took place
    if out_lines and len(page.get_contents()) > 0:
        xref = page.get_contents()[0]
        page.parent.update_stream(xref, b"\n".join(out_lines))

def replace_header_text(page, old_text="Demo Frilo", new_text="Frilo", fontname="helv", fontsize=11):
    """
    1) Search for all instances of old_text
    2) Cover it with a white rectangle
    3) Insert new_text at the same location
    """
    text_instances = page.search_for(old_text)
    for inst in text_instances:
        # cover original text
        page.draw_rect(inst, color=None, fill=(1,1,1), overlay=True)
        # insert new text at the top-left of the original bbox
        page.insert_text(
            inst.tl,
            new_text,
            fontname=fontname,
            fontsize=fontsize,
            color=(0,0,0)
        )

def clean_pdf(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    for page in doc:
        remove_grey_watermark(page)
        replace_header_text(page)
    # Fast incremental save
    doc.ez_save(output_pdf)
    print(f"✔ Cleaned PDF saved as: {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_pdf_watermark_and_header.py <input.pdf> <output.pdf>")
        sys.exit(1)
    clean_pdf(sys.argv[1], sys.argv[2])
