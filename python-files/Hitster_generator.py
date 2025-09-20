import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap
from fpdf import FPDF
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

RAINBOW_COLORS = [
    (148, 0, 211),
    (0, 0, 255),
    (0, 255, 0),
    (255, 255, 0),
    (255, 0, 0),
]

DEFAULT_COLOR = (128, 128, 128)

def interpolate_colors(color1, color2, factor: float):
    return tuple(
        int(color1[i] + (color2[i] - color1[i]) * factor)
        for i in range(3)
    )

def get_rainbow_color(t: float):
    n = len(RAINBOW_COLORS) - 1
    scaled_pos = t * n
    idx = int(np.floor(scaled_pos))
    factor = scaled_pos - idx
    if idx >= n:
        return RAINBOW_COLORS[-1]
    return interpolate_colors(RAINBOW_COLORS[idx], RAINBOW_COLORS[idx+1], factor)

def generate_qr_code(url, size=200):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img

def create_text_image(artist, year, title, background_color, size=(200, 200)):
    width, height = size
    img = Image.new('RGB', size, background_color)
    draw = ImageDraw.Draw(img)
    try:
        font_artist = ImageFont.truetype("arial.ttf", 14)
        font_title = ImageFont.truetype("arial.ttf", 14)
        font_year = ImageFont.truetype("arialbd.ttf", 40)
    except IOError:
        font_artist = ImageFont.load_default()
        font_title = ImageFont.load_default()
        font_year = ImageFont.load_default()

    def draw_multiline_text_centered(text, y, font):
        lines = []
        for line in text.split('\n'):
            wrapped = textwrap.wrap(line, width=20)
            lines.extend(wrapped)
        total_height = sum([(font.getbbox(line)[3] - font.getbbox(line)[1]) for line in lines]) + (len(lines)-1)*3
        current_y = y - total_height // 2
        for line in lines:
            bbox = font.getbbox(line)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((width - w) / 2, current_y), line, font=font, fill=(0,0,0))
            current_y += h + 3

    draw_multiline_text_centered(artist, height//4, font_artist)
    year_text = str(int(year)) if year is not None and not pd.isna(year) else ''
    bbox = font_year.getbbox(year_text)
    year_w, year_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - year_w) / 2, (height - year_h) // 2), year_text, font=font_year, fill=(0, 0, 0))
    draw_multiline_text_centered(title, (height*3)//4, font_title)
    return img

class PDFWithCutMarks(FPDF):
    def __init__(self, width, height, rows, cols):
        super().__init__(unit='pt', format=[width, height])
        self.page_width = width
        self.page_height = height
        self.rows = rows
        self.cols = cols
        self.card_size = min(width / cols, height / rows)

    def draw_cut_marks(self):
        mark_length = 10
        thickness = 0.3
        self.set_line_width(thickness)
        for c in range(1, self.cols):
            x = c * self.card_size
            self.line(x, 0, x, mark_length)
            self.line(x, self.page_height - mark_length, x, self.page_height)
        for r in range(1, self.rows):
            y = r * self.card_size
            self.line(0, y, mark_length, y)
            self.line(self.page_width - mark_length, y, self.page_width, y)

def generate_cards(df, output_folder, country, page_width, page_height, rows, cols, progress_callback=None):
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    valid_years = df['Year'].dropna()
    if valid_years.empty:
        min_year = None
        max_year = None
    else:
        min_year = int(valid_years.min())
        max_year = int(valid_years.max())
    year_range = (max_year - min_year) if min_year and max_year and max_year != min_year else 1

    pdf = PDFWithCutMarks(page_width, page_height, rows, cols)

    cards_per_page = rows * cols
    card_size = pdf.card_size
    total = len(df)
    processed = 0

    for idx in range(0, total, cards_per_page):
        pdf.add_page()
        pdf.draw_cut_marks()
        subset = df.iloc[idx:idx + cards_per_page]
        for i, (_, row) in enumerate(subset.iterrows()):
            year_val = row['Year']
            if pd.isna(year_val):
                bg_color = DEFAULT_COLOR
            else:
                t = (int(year_val) - min_year) / year_range
                bg_color = get_rainbow_color(t)
            qr_img = generate_qr_code(row['Hitster_Link'], size=int(card_size))
            qr_path = os.path.join(output_folder, f'qr_{idx+i+1}.png')
            qr_img.save(qr_path)
            col = i % cols
            row_pos = i // cols
            x = col * card_size
            y = row_pos * card_size
            pdf.image(qr_path, x, y, card_size, card_size)
            os.remove(qr_path)

            processed += 1
            if progress_callback:
                progress_callback(processed, total)

        pdf.add_page()
        pdf.draw_cut_marks()
        subset = df.iloc[idx:idx + cards_per_page]
        for i, (_, row) in enumerate(subset[::-1].iterrows()):
            year_val = row['Year']
            if pd.isna(year_val):
                bg_color = DEFAULT_COLOR
            else:
                t = (int(year_val) - min_year) / year_range
                bg_color = get_rainbow_color(t)
            text_img = create_text_image(row['Artist'], row['Year'], row['Title'], bg_color, size=(int(card_size), int(card_size)))
            text_path = os.path.join(output_folder, f'text_{idx+i+1}.png')
            text_img.save(text_path)
            col = (cols - 1) - (i % cols)
            row_pos = (rows - 1) - (i // cols)
            x = col * card_size
            y = row_pos * card_size
            pdf.image(text_path, x, y, card_size, card_size)
            os.remove(text_path)

            processed += 1
            if progress_callback:
                progress_callback(processed, total)

    pdf_output = os.path.join(output_folder, f'hitster_cards_{country}.pdf')
    pdf.output(pdf_output)
    print(f'PDF sikeresen mentve ide: {pdf_output}')

class HitsterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Hitster Kártya Generátor")
        self.geometry("400x250")

        self.create_widgets()

        self.df = None
        self.load_data()

    def load_data(self):
        excel_path = filedialog.askopenfilename(title="Válassza ki az excel fájlt", filetypes=(("Excel files", "*.xlsx;*.xls"),))
        if not excel_path:
            messagebox.showerror("Hiba", "Nem választott ki excel fájlt!")
            self.quit()
            return
        self.df = pd.read_excel(excel_path)
        countries = self.df['Country'].dropna().unique().tolist()
        self.country_combobox['values'] = countries
        if countries:
            self.country_combobox.current(0)

    def create_widgets(self):
        lbl_country = ttk.Label(self, text="Válassz országot:")
        lbl_country.pack(pady=(10, 0))
        self.country_combobox = ttk.Combobox(self, state="readonly")
        self.country_combobox.pack(pady=(0, 10))

        lbl_size = ttk.Label(self, text="Válassz papírméretet:")
        lbl_size.pack()

        self.paper_size_var = tk.StringVar(value="A4")

        rb_a4 = ttk.Radiobutton(self, text="A4 (3x4)", variable=self.paper_size_var, value="A4")
        rb_a4.pack()

        rb_a3 = ttk.Radiobutton(self, text="A3 (5x7)", variable=self.paper_size_var, value="A3")
        rb_a3.pack()

        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

        self.btn_generate = ttk.Button(self, text="Generálás", command=self.start_generation)
        self.btn_generate.pack()

    def start_generation(self):
        if self.df is None or self.df.empty:
            messagebox.showerror("Hiba", "Az adat nincs betöltve!")
            return
        country = self.country_combobox.get()
        if not country:
            messagebox.showerror("Hiba", "Válassz országot!")
            return

        paper_size = self.paper_size_var.get()
        if paper_size == "A4":
            PAGE_WIDTH = 595
            PAGE_HEIGHT = 842
            ROWS = 4
            COLS = 3
        else:
            PAGE_WIDTH = 842
            PAGE_HEIGHT = 1191
            ROWS = 7
            COLS = 5

        output_folder = filedialog.askdirectory(title="Válassza ki a mentési mappát")
        if not output_folder:
            messagebox.showerror("Hiba", "Nem választott ki mappát!")
            return

        self.progress['value'] = 0
        self.btn_generate.config(state=tk.DISABLED)

        def progress_callback(completed, total):
            percent = (completed / total) * 100
            self.progress['value'] = percent
            self.update_idletasks()

        def generation_thread():
            try:
                df_country = self.df[self.df['Country'] == country].copy()
                if df_country.empty:
                    messagebox.showinfo("Info", "Nincs adat a kiválasztott országhoz.")
                else:
                    generate_cards(df_country, output_folder, country, PAGE_WIDTH, PAGE_HEIGHT, ROWS, COLS, progress_callback)
                    messagebox.showinfo("Siker", "A PDF generálás befejeződött!")
            except Exception as e:
                messagebox.showerror("Hiba", f"Hiba történt: {e}")
            finally:
                self.btn_generate.config(state=tk.NORMAL)
                self.progress['value'] = 0

        threading.Thread(target=generation_thread, daemon=True).start()

if __name__ == '__main__':
    app = HitsterApp()
    app.mainloop()
