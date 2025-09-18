#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
import sys
import zipfile
import argparse
from pathlib import Path

from PIL import Image, ImageOps

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

def natural_key(s: str):
    # מיון "טבעי" כדי ש-1,2,10 ימוקמו נכון
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def load_images_from_zip(zip_path: Path):
    images = []
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = [n for n in zf.namelist() if not n.endswith('/')]

        # סינון רק לקבצי תמונה, מיון טבעי לפי שם מלא בתוך ה-ZIP
        img_names = [n for n in names if Path(n).suffix.lower() in SUPPORTED_EXTS]
        if not img_names:
            raise ValueError("לא נמצאו תמונות נתמכות ב-ZIP. סיומות נתמכות: " + ", ".join(sorted(SUPPORTED_EXTS)))

        img_names.sort(key=natural_key)

        for name in img_names:
            with zf.open(name, 'r') as f:
                data = f.read()
            bio = io.BytesIO(data)
            im = Image.open(bio)
            # תיקון סיבוב לפי EXIF אם קיים
            try:
                im = ImageOps.exif_transpose(im)
            except Exception:
                pass

            # המרה ל-RGB (למניעת בעיות אלפא/P/MODE)
            if im.mode in ("RGBA", "LA"):
                # מילוי רקע לבן לפיקסלים שקופים
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            elif im.mode != "RGB":
                im = im.convert("RGB")

            images.append(im)

    return images

def save_images_to_pdf(images, out_path: Path, fit_to_page=None, page_size=None, margin=0):
    """
    images: רשימת אובייקטי PIL Image במצב RGB.
    fit_to_page: None/ 'fit' / 'shrink'  (אופציונלי – אם תרצה בהמשך להקטין/להתאים)
    page_size: (width,height) בפיקסלים, אם רוצים לכפות גודל דף אחיד (ברירת מחדל: גודל מקורי של כל תמונה)
    margin: מרווח לבן בפיקסלים סביב התמונה אם page_size נקבע.
    """
    if not images:
        raise ValueError("אין תמונות לשמירה.")

    if page_size:
        W, H = page_size
        normed = []
        for im in images:
            canvas = Image.new("RGB", (W, H), (255, 255, 255))
            w, h = im.size
            # התאמה לתוך העמוד עם שמירת יחס
            scale = min((W - 2*margin) / w, (H - 2*margin) / h)
            nw, nh = max(1, int(w*scale)), max(1, int(h*scale))
            im_resized = im.resize((nw, nh), Image.LANCZOS)
            # מיקום במרכז
            x = (W - nw) // 2
            y = (H - nh) // 2
            canvas.paste(im_resized, (x, y))
            normed.append(canvas)
        images = normed

    # שמירה: התמונה הראשונה כבסיס, היתר ב-append_images
    first, rest = images[0], images[1:]
    first.save(out_path, "PDF", save_all=True, append_images=rest)

def detect_default_output(zip_path: Path) -> Path:
    return zip_path.with_suffix(".pdf")

def parse_args(argv):
    ap = argparse.ArgumentParser(
        description="המרת ZIP עם תמונות לקובץ PDF אחד.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    ap.add_argument("zipfile", nargs="?", help="נתיב ל-ZIP עם תמונות")
    ap.add_argument("-o", "--output", help="שם קובץ ה-PDF ליצירה (אם לא יינתן, ייגזר משם ה-ZIP)")
    ap.add_argument("--a4", action="store_true", help="לכפות עמודי A4 (פיקסלים בקירוב ל-300DPI: 2480x3508) עם התאמה אוטומטית")
    ap.add_argument("--margin", type=int, default=40, help="מרווח לבן בפיקסלים סביב התמונה (רלוונטי רק עם --a4)")
    ap.add_argument("--gui", action="store_true", help="פתיחת חלון בחירה במקום CLI")
    return ap.parse_args(argv)

def run_cli(zip_path: Path, output_path: Path, use_a4: bool, margin: int):
    images = load_images_from_zip(zip_path)
    if use_a4:
        # A4 ב~300 DPI: 2480×3508 פיקסלים
        save_images_to_pdf(images, output_path, page_size=(2480, 3508), margin=margin)
    else:
        save_images_to_pdf(images, output_path)
    return output_path

def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.withdraw()

    zip_path = filedialog.askopenfilename(
        title="בחר קובץ ZIP עם תמונות",
        filetypes=[("ZIP files", "*.zip")]
    )
    if not zip_path:
        return

    default_out = detect_default_output(Path(zip_path))
    out_path = filedialog.asksaveasfilename(
        title="בחר היכן לשמור PDF",
        defaultextension=".pdf",
        initialfile=default_out.name,
        filetypes=[("PDF", "*.pdf")]
    )
    if not out_path:
        return

    use_a4 = messagebox.askyesno("גודל עמוד", "להשתמש בפורמט A4 לכל העמודים?")
    margin = 40
    if use_a4:
        # אופציונלי: בקשת מרווח. כדי לא לסבך, נשאיר 40 ברירת מחדל.
        pass

    try:
        out = run_cli(Path(zip_path), Path(out_path), use_a4, margin)
        messagebox.showinfo("המרה הושלמה", f"נוצר: {out}")
    except Exception as e:
        messagebox.showerror("שגיאה", str(e))

def main():
    args = parse_args(sys.argv[1:])
    if args.gui:
        return run_gui()

    if not args.zipfile:
        print("שימוש: zip_to_pdf.py <path/to/file.zip> [-o out.pdf] [--a4] [--margin 40]")
        print("או: zip_to_pdf.py --gui  (ממשק חלון)")
        sys.exit(1)

    zip_path = Path(args.zipfile)
    if not zip_path.exists():
        print(f"שגיאה: הקובץ לא נמצא: {zip_path}")
        sys.exit(1)

    out_path = Path(args.output) if args.output else detect_default_output(zip_path)

    try:
        out = run_cli(zip_path, out_path, use_a4=args.a4, margin=args.margin)
        print(f"הסתיים בהצלחה: {out}")
    except Exception as e:
        print("נכשלה ההמרה:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
