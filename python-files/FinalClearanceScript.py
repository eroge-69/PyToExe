#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
import json
import time
import math
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from typing import Optional


# ---- Log helper ----
def log(msg):
    print(msg, flush=True)

# ---- Tkinter GUI setup ----
def select_input_file():
    """ Open file dialog to select the input excel file """
    file_path = filedialog.askopenfilename(filetypes=(("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")))
    input_file_var.set(file_path)

def select_output_folder():
    """ Open folder dialog to select the output folder """
    folder_path = filedialog.askdirectory()
    output_folder_var.set(folder_path)

def save_default_folder(folder):
    """ Save the selected output folder path to a json file for future use """
    with open("default_output_folder.json", "w") as f:
        json.dump({"output_folder": folder}, f)

def load_default_folder():
    """ Load the default output folder if it exists """
    if Path("default_output_folder.json").exists():
        with open("default_output_folder.json", "r") as f:
            data = json.load(f)
        return data.get("output_folder", "")
    return ""

# ---- File reading and processing functions ----
def _existing_input_path(p_str: str) -> Path:
    p = Path(p_str)
    if p.exists():
        return p
    alt = p.with_suffix(".xlsx")
    if alt.exists():
        log(f"ℹ️ Using .xlsx variant found next to it: {alt}")
        return alt
    return p

def _read_by_column_letters(path: Path) -> pd.DataFrame:
    """ Reads the Excel file and processes it based on column letters. """
    log(f"📄 Reading (no headers): {path}")
    ext = path.suffix.lower()
    read_kwargs = dict(header=None)  # NO header; we will slice by row/col positions
    try:
        if ext in [".xlsx", ".xlsm", ".xltx", ".xltm"]:
            df_raw = pd.read_excel(path, engine="openpyxl", **read_kwargs)
        elif ext == ".xls":
            df_raw = pd.read_excel(path, engine="xlrd", **read_kwargs)
        else:
            df_raw = pd.read_excel(path, **read_kwargs)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to read Excel: {e}")

    df = df_raw.iloc[4:, :]  # data rows only
    needed_idx = [0, 1, 2, 9, 10, 11]
    df = df.iloc[:, needed_idx].copy()
    df.columns = ["Department", "Article", "Product Name", "Was Price", "Current Price", "Markdown %"]

    # Clean text fields
    for c in ["Department", "Article", "Product Name"]:
        df[c] = df[c].astype(str).str.strip()

    # Coerce prices & percent
    def to_price(s):
        if pd.isna(s):
            return math.nan
        txt = re.sub(r"[^\d\.,-]", "", str(s)).replace(",", "")
        try:
            return float(txt)
        except Exception:
            return math.nan

    df["Was Price"] = df["Was Price"].apply(to_price)
    df["Current Price"] = df["Current Price"].apply(to_price)

    def to_pct(s):
        if pd.isna(s):
            return math.nan
        txt = str(s).strip().replace("%", "")
        try:
            return float(txt)
        except Exception:
            return math.nan

    df["Markdown %"] = df["Markdown %"].apply(to_pct)

    # Compute Markdown % when missing & prices present
    need = df["Markdown %"].isna() & df["Was Price"].notna() & df["Current Price"].notna() & (df["Was Price"] > 0)
    df.loc[need, "Markdown %"] = (1 - (df.loc[need, "Current Price"] / df.loc[need, "Was Price"])) * 100.0

    # Clearance filter
    mask = (
        (df["Was Price"].notna() & df["Current Price"].notna() & (df["Current Price"] < df["Was Price"])) |
        (df["Markdown %"].notna() & (df["Markdown %"] > 0))
    )
    df = df[mask].copy()

    df = df[df["Department"].astype(str).str.strip() != ""]
    df = df[df["Article"].astype(str).str.strip() != ""]
    df.sort_values(by=["Department", "Product Name"], inplace=True, ignore_index=True)

    log(f"✅ Loaded {len(df):,} clearance rows.")
    return df

# ---- Image download ----
def _extract_image_url_from_page(html: str, base_url: str) -> Optional[str]:
    """Extracts the image URL from the HTML of the product page."""
    soup = BeautifulSoup(html, "lxml")
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return urljoin(base_url, og["content"])
    gallery = soup.select_one(".hdca-product__gallery-media-container")
    if gallery:
        img_tag = gallery.find("img")
        if img_tag:
            for attr in ["src", "data-src", "data-original", "data-lazy"]:
                if img_tag.get(attr):
                    return urljoin(base_url, img_tag.get(attr))
    return None

def _download_product_image(article: str, session: requests.Session, out_dir: Path, progress_var, total_images, current_image) -> Optional[str]:
    """Downloads the product image."""
    product_url = f"https://www.homedepot.ca/product/{article}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    try:
        r = session.get(product_url, timeout=15, headers=headers)
        if r.status_code != 200:
            return None
        img_url = _extract_image_url_from_page(r.text, base_url=product_url)
        if not img_url:
            return None
        time.sleep(0.2)
        img_r = session.get(img_url, timeout=15, headers=headers, stream=True)
        if img_r.status_code != 200:
            return None
        out_dir.mkdir(parents=True, exist_ok=True)
        img_path = out_dir / f"{_safe_filename(article)}.jpg"
        with open(img_path, "wb") as f:
            for chunk in img_r.iter_content(8192):
                if chunk:
                    f.write(chunk)
        current_image.set(current_image.get() + 1)
        progress_var.set(current_image.get() / total_images * 100)
        return str(img_path)
    except Exception:
        return None

# ---- HTML generation ----
def _format_money(x) -> str:
    """Formats a numeric value as currency."""
    if pd.isna(x): return ""
    return f"${x:,.2f}"

def _format_pct(x) -> str:
    """Formats a percentage."""
    if pd.isna(x): return ""
    return f"{x:.0f}%"

def _safe_filename(s: str) -> str:
    """Sanitizes strings to create safe filenames."""
    return re.sub(r"[^A-Za-z0-9_\-\.]+", "_", s)

def _build_html(df: pd.DataFrame, output_dir: Path, run_label: str) -> str:
    """
    Builds a printable booklet with:
      - 9 cards per page (3x3) when possible
      - No card cut across pages (hard page breaks)
      - Big department header at the start of each department
      - Small department strip on every page of that department
    """
    # ---- Styles tuned for print booklet ----
    css = """
    <style>
      @media print {
        @page { size: A4 portrait; margin: 12mm; }
        .page { break-after: page; }
      }
      * { box-sizing: border-box; }
      body { font-family: Arial, Helvetica, sans-serif; color: #111; margin: 0; padding: 0 0 24px; }
      .header { padding: 16px 24px; border-bottom: 2px solid #f0f0f0; }
      .title { font-size: 28px; font-weight: 700; margin: 0; }
      .subtitle { color: #666; margin-top: 6px; }
      .dept-start { padding: 16px 24px 0; }
      .dept-start h2 { font-size: 22px; margin: 0 0 10px; border-left: 6px solid #ff6600; padding-left: 10px; }
      .deptstrip { font-size: 11px; color: #444; padding: 6px 24px 4px; border-bottom: 1px dashed #e8e8e8; margin-bottom: 8px; display:flex; justify-content:space-between; align-items:center; }
      .deptstrip .left { font-weight: 600; }
      .deptstrip .right { color: #777; }
      .page { padding: 6px 16px 16px; }
      .grid9 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; break-inside: avoid; page-break-inside: avoid; }
      .card { border: 1px solid #eaeaea; border-radius: 10px; padding: 8px; page-break-inside: avoid; break-inside: avoid; }
      .imgwrap { width: 100%; aspect-ratio: 1 / 1; display:flex; align-items:center; justify-content:center; overflow:hidden; border-radius: 8px; background:#fafafa; border:1px solid #f3f3f3; }
      .imgwrap img { max-width:100%; max-height:100%; object-fit:contain; }
      .name { font-weight:700; margin: 6px 0 3px; font-size: 13px; line-height:1.25; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
      .meta { font-size: 11px; color:#555; margin-bottom:6px; }
      .price { font-size: 13px; }
      .was { color:#999; text-decoration:line-through; margin-right:6px; }
      .now { font-weight:700; }
      .badge { display:inline-block; font-size:11px; font-weight:700; padding:2px 6px; border-radius:999px; border:1px solid #ffd4bf; background:#fff5ef; color:#c24a00; margin-left:6px; }
      .footer { text-align:center; color:#888; font-size: 12px; padding: 6px 0 16px; border-top: 1px dashed #eee; }
      .link { color:#ff6600; text-decoration:none; }
      .link:hover { text-decoration: underline; }
    </style>
    """

    def chunk(seq, n):
        """Yield successive n-sized chunks from seq."""
        for i in range(0, len(seq), n):
            yield seq[i:i+n]

    # Build HTML
    parts = []
    parts.append("<!doctype html><html><head><meta charset='utf-8'>")
    parts.append("<meta name='viewport' content='width=device-width, initial-scale=1'>")
    parts.append(css)
    parts.append("</head><body>")

    # Cover / global header
    parts.append(f"""
      <div class="header">
        <h1 class="title">Clearance Catalogue</h1>
        <div class="subtitle">Generated: {run_label}</div>
      </div>
    """)

    # Per-department pages (3x3 per page)
    for dept, g in df.groupby("Department", sort=True):
        g = g.reset_index(drop=True)

        # Big dept header at the start of this department
        parts.append(f"""<section class="dept-start"><h2>{dept}</h2></section>""")

        rows = [row for _, row in g.iterrows()]
        pages = list(chunk(rows, 9))
        total_pages = len(pages)

        for page_idx, page_rows in enumerate(pages, start=1):
            cont = " (cont.)" if page_idx > 1 else ""
            parts.append('<div class="page">')
            # Small dept strip at top of every page
            parts.append(f"""
              <div class="deptstrip">
                <div class="left">{dept}{cont}</div>
                <div class="right">Page {page_idx} of {total_pages}</div>
              </div>
            """)
            parts.append('<div class="grid9">')

            for row in page_rows:
                article = str(row["Article"])
                name    = row["Product Name"]
                was     = _format_money(row["Was Price"])
                now     = _format_money(row["Current Price"])
                pct     = _format_pct(row.get("Markdown %", math.nan))

                img_file = output_dir / "images" / f"{_safe_filename(article)}.jpg"
                has_img  = img_file.exists()

                img_tag = (
                    f"<img src='images/{img_file.name}' alt='{name}'>"
                    if has_img else "<div style='padding:10px;color:#bbb;font-size:12px;'>No image</div>"
                )

                product_url = f"https://www.homedepot.ca/product/{article}"

                parts.append(f"""
                  <div class="card">
                    <div class="imgwrap">{img_tag}</div>
                    <div class="name">{name}</div>
                    <div class="meta">Article: <a class='link' href="{product_url}" target="_blank" rel="noopener">{article}</a></div>
                    <div class="price">
                      <span class="was">{was}</span>
                      <span class="now">{now}</span>
                      {"<span class='badge'>-" + pct + "</span>" if pct else ""}
                    </div>
                  </div>
                """)

            parts.append("</div>")   # .grid9
            parts.append("</div>")   # .page

    parts.append(f"<div class='footer'>End of catalogue • {run_label}</div>")
    parts.append("</body></html>")

    html = "\n".join(parts)
    out_html = output_dir / "clearance_catalogue.html"
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    return str(out_html)

# ---- Main function that combines everything ----
def build_catalogue(input_file, output_folder):
    run_label = datetime.now().strftime("%Y-%m-%d %H:%M")
    out_dir = Path(output_folder) / datetime.now().strftime("%Y-%m-%d")
    img_dir = out_dir / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Path check
    p = _existing_input_path(input_file)
    log(f"🔧 Using path: {p}")
    if not p.exists():
        raise FileNotFoundError(f"❌ File not found: {p}")

    # 2) Load data by column letters (A,B,C,J,K,L), data from row 5
    df = _read_by_column_letters(p)

    # 3) Images (optional first run)
    log("🖼️ Fetching product images...")
    session = requests.Session()
    total = len(df["Article"].unique())
    current_image = tk.IntVar(value=0)
    progress_var = tk.DoubleVar(value=0)

    for i, article in enumerate(df["Article"].unique(), start=1):
        _download_product_image(article, session, img_dir, progress_var, total, current_image)

    # 4) Save CSV
    csv_path = out_dir / "clearance_items.csv"
    df.to_csv(csv_path, index=False)
    log(f"💾 Saved data: {csv_path}")

    # 5) Build HTML
    html_path = _build_html(df, out_dir, run_label)
    log(f"📘 Booklet: {html_path}")

    log("\n✅ Done! Open the HTML and Print → Save as PDF for a weekly booklet.")
    log(f"🗂️ Images saved to: {img_dir}")

# ---- Tkinter UI (main entry point) ----
def run_gui():
    """ Run the Tkinter GUI """
    global input_file_var, output_folder_var
    root = tk.Tk()
    root.title("Clearance Catalogue Builder")

    # Load last output folder from file (if exists)
    default_output_folder = load_default_folder()

    input_file_var = tk.StringVar()
    output_folder_var = tk.StringVar(value=default_output_folder)

    # Input file selection
    tk.Label(root, text="Select Input Excel File").pack(pady=5)
    tk.Entry(root, textvariable=input_file_var, width=40).pack(padx=10)
    tk.Button(root, text="Browse", command=select_input_file).pack(pady=5)

    # Output folder selection
    tk.Label(root, text="Select Output Folder").pack(pady=5)
    tk.Entry(root, textvariable=output_folder_var, width=40).pack(padx=10)
    tk.Button(root, text="Browse", command=select_output_folder).pack(pady=5)

    # Progress bar
    progress_var = tk.DoubleVar(value=0)
    progress_bar = ttk.Progressbar(root, length=300, variable=progress_var, maximum=100)
    progress_bar.pack(pady=10)

    # Start Button
    def start_process():
        """ Start processing the catalogue building process """
        input_file = input_file_var.get()
        output_folder = output_folder_var.get()

        # Check fields
        if not input_file or not output_folder:
            messagebox.showerror("Input Error", "Please select both input file and output folder.")
            return

        # Save default output folder
        save_default_folder(output_folder)

        # Start the catalogue generation
        build_catalogue(input_file, output_folder)

        messagebox.showinfo("Process Completed", "Clearance Catalogue has been generated successfully!")

    tk.Button(root, text="Generate Catalogue", command=start_process).pack(pady=10)

    # Start the Tkinter loop
    root.mainloop()

# --- Run the GUI ---
if __name__ == "__main__":
    run_gui()


# In[ ]:





# In[ ]:




