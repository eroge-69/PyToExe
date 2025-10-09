# ===============================================================
# Smart Inventory Manager Pro - Arabic/English (v3)
# Developed & Designed by ENG. HABIB NASER
# Software & Networks Engineer
# ENG.HABIB  —  2025
# Features added: Total Capital badge, Refresh file, Quick Search,
# Low-stock alert, Export PDF report, Save user settings, Sortable columns,
# Bilingual UI (Arabic then English in parentheses)
# ===============================================================

import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import datetime
import os
import webbrowser
import json

try:
    from matplotlib import pyplot as plt
except Exception:
    plt = None

# optional PDF library
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False

OUTPUT_DIR = Path.cwd() / "smart_inventory_output"
OUTPUT_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = OUTPUT_DIR / "settings.json"

# ----------------- Helpers -----------------
def find_col(df_cols, candidates):
    cols = df_cols.str.lower()
    for c in candidates:
        matches = cols[cols.str.contains(c.lower())]
        if not matches.empty:
            return df_cols[matches.index[0]]
    return None

def safe_to_numeric(s):
    return pd.to_numeric(s, errors='coerce')

def default_file_candidates():
    return [
        Path.cwd() / "المصنف1.xlsx",
        Path("/mnt/data/المصنف1.xlsx"),
        Path.cwd() / "inventory.xlsx",
        Path.cwd() / "data.xlsx",
        Path.cwd() / "المصنف.xlsx"
    ]


# ----------------- Core processing -----------------
def process_file(path, exchange_rate=1.0):
    xls = pd.ExcelFile(path)
    dfs = []
    for sheet in xls.sheet_names:
        tmp = pd.read_excel(xls, sheet_name=sheet)
        tmp['_sheet_name'] = sheet
        dfs.append(tmp)
    df = pd.concat(dfs, ignore_index=True, sort=False)
    df.columns = df.columns.str.strip()
    cols = pd.Series(df.columns.astype(str))

    detected = {}
    detected['barcode'] = find_col(cols, ["barcode", "bar code", "باركود", "رمز"])
    detected['brand'] = find_col(cols, ["brand", "make", "manufacturer", "ماركة", "العلامة"])
    detected['category'] = find_col(cols, ["category", "type", "فئة", "تصنيف", "نوع"])
    detected['wholesale'] = find_col(cols, ["wholesale", "cost", "سعر الجملة", "سعر التكلفة", "سعر_التكلفة", "cost price", "سعرالجملة"])
    detected['retail'] = find_col(cols, ["retail", "price", "السعر", "سعر_البيع", "selling price"])
    detected['quantity'] = find_col(cols, ["qty", "quantity", "عدد", "الكمية", "قطعة", "pcs", "الكمية المتوفرة", "الرصيد"])
    detected['manufacture_date'] = find_col(cols, ["manufacture", "date", "تاريخ", "تاريخ التصنيع", "تاريخ_الانتاج"])
    detected['name'] = find_col(cols, ["name", "item", "product", "اسم", "اسم الصنف", "اسم_الصنف", "المنتج", "اسم المنتج"])

    # convert numeric cols
    for k in ('wholesale','retail','quantity'):
        c = detected.get(k)
        if c is not None and c in df.columns:
            df[c] = safe_to_numeric(df[c])

    # compute per-item capital (cost * qty)
    capital_col = "إجمالي_تكلفة_الصنف"
    if detected.get('wholesale') and detected.get('quantity'):
        df[capital_col] = df[detected['wholesale']].fillna(0) * df[detected['quantity']].fillna(0)
    else:
        # try using retail if wholesale missing
        if detected.get('retail') and detected.get('quantity'):
            df[capital_col] = df[detected['retail']].fillna(0) * df[detected['quantity']].fillna(0)
        else:
            df[capital_col] = 0

    # apply exchange rate (to display in selected currency)
    df['capital_in_currency'] = df[capital_col] * float(exchange_rate)

    # summaries
    grand_total = df['capital_in_currency'].sum()
    total_items = df.shape[0]
    total_pieces = int(df[detected['quantity']].fillna(0).sum()) if detected.get('quantity') else None

    # category aggregation
    category_summary = None
    if detected.get('category'):
        try:
            category_summary = df.groupby(detected['category']).agg(
                total_quantity = (detected['quantity'], lambda x: x.dropna().sum() if detected.get('quantity') else 0),
                total_capital = ('capital_in_currency', 'sum'),
                n_items = (detected.get('name') or detected.get('barcode') or '_sheet_name', 'nunique')
            ).reset_index()
        except Exception:
            category_summary = None

    # duplicates by barcode
    duplicates = None
    if detected.get('barcode'):
        dup_mask = df.duplicated(subset=[detected['barcode']], keep=False)
        duplicates = df[dup_mask].sort_values(by=detected['barcode'])

    # attach metadata
    meta = {
        'file': str(path),
        'sheets': xls.sheet_names,
        'detected': detected,
        'grand_total': grand_total,
        'total_items': total_items,
        'total_pieces': total_pieces,
        'capital_col': capital_col,
        'category_summary': category_summary,
        'duplicates': duplicates
    }

    return {'df': df, 'meta': meta}


# ----------------- File saving -----------------
def save_results(proc_result, currency_label="USD"):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_xlsx = OUTPUT_DIR / f"نتائج_الجرد_{ts}.xlsx"
    df = proc_result['df']
    with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="raw_data", index=False)
        # write summary sheet
        summary = {
            'grand_total': proc_result['meta']['grand_total'],
            'total_items': proc_result['meta']['total_items'],
            'total_pieces': proc_result['meta']['total_pieces'],
            'currency': currency_label
        }
        pd.DataFrame([summary]).to_excel(writer, sheet_name="summary", index=False)
        if proc_result['meta'].get('category_summary') is not None:
            proc_result['meta']['category_summary'].to_excel(writer, sheet_name="by_category", index=False)
        if proc_result['meta'].get('duplicates') is not None and not proc_result['meta']['duplicates'].empty:
            proc_result['meta']['duplicates'].to_excel(writer, sheet_name="duplicates", index=False)
        # append signature/footer sheet
        footer = pd.DataFrame([{
            'report_generated_by': 'ENG.HABIB (ENG. HABIB NASER)',
            'note': 'Report generated by ENG.HABIB — 2025'
        }])
        footer.to_excel(writer, sheet_name="report_footer", index=False)
    # also quick CSV
    out_csv = OUTPUT_DIR / f"quick_export_{ts}.csv"
    useful = []
    det = proc_result['meta']['detected']
    if det.get('name'): useful.append(det['name'])
    if det.get('barcode'): useful.append(det['barcode'])
    if det.get('category'): useful.append(det['category'])
    if det.get('wholesale'): useful.append(det['wholesale'])
    if det.get('quantity'): useful.append(det['quantity'])
    useful.append('capital_in_currency')
    # ensure columns exist
    available = [c for c in useful if c in proc_result['df'].columns]
    proc_result['df'][available].to_csv(out_csv, index=False, encoding='utf-8-sig')
    return out_xlsx, out_csv


# ----------------- GUI -----------------
class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Inventory Manager - جرد المخزون")
        self.geometry("1200x720")
        self.proc_result = None
        self.file_path = None
        self.currency_label = tk.StringVar(value="USD")
        self.exchange_rate = tk.DoubleVar(value=1.0)
        self.filter_brand = tk.StringVar(value="")
        self.filter_category = tk.StringVar(value="")
        self.search_text = tk.StringVar(value="")
        self.low_stock_threshold = tk.IntVar(value=5)

        # load settings
        self.load_settings()

        # style
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', background='#2b6ea3', foreground='white', padding=6)
        style.configure('TLabel', background='#f5f7fa', foreground='#222222')
        style.configure('TEntry', padding=4)
        self.configure(background='#f5f7fa')

        # top frame with logo and controls
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=6)

        # total capital badge (big, bold, colored)
        self.capital_display = tk.Label(self, text="رأس المال الكلي / Total Capital: 0.00", font=('Helvetica', 18, 'bold'), fg='#0b5394', bg='#f5f7fa')
        self.capital_display.pack(fill='x', padx=8, pady=6)

        # logo at right top
        logo = ttk.Label(top, text="ENG.HABIB", font=('Helvetica', 12, 'bold'))
        logo.pack(side='right', padx=8)

        ttk.Button(top, text="اختيار ملف Excel / Select Excel File", command=self.choose_file).pack(side='left', padx=4)
        ttk.Button(top, text="تحميل ومعالجة / Load & Process", command=self.load_and_process).pack(side='left', padx=4)
        ttk.Button(top, text="تحديث الملف الحالي / Refresh Current File", command=self.refresh_current_file).pack(side='left', padx=4)
        ttk.Button(top, text="حفظ النتائج / Save Results", command=self.save_results).pack(side='left', padx=4)
        ttk.Button(top, text="تقرير PDF / Export PDF Report", command=self.export_pdf_report).pack(side='left', padx=4)
        ttk.Button(top, text="فتح مجلد النتائج / Open Results Folder", command=self.open_output_dir).pack(side='left', padx=4)

        # small welcome banner
        banner = ttk.Label(self, text="Smart Inventory Manager — Designed & Developed by ENG.HABIB (ENG. HABIB NASER)", anchor='center')
        banner.pack(fill='x', padx=8)

        # currency controls
        curfrm = ttk.Frame(self)
        curfrm.pack(fill='x', padx=8, pady=6)
        ttk.Label(curfrm, text="العملة / Currency:").pack(side='left')
        ttk.Entry(curfrm, width=8, textvariable=self.currency_label).pack(side='left', padx=4)
        ttk.Label(curfrm, text="سعر الصرف (ضرب) / Exchange rate:").pack(side='left', padx=6)
        ttk.Entry(curfrm, width=10, textvariable=self.exchange_rate).pack(side='left', padx=4)
        ttk.Label(curfrm, text="(مثال: 1 للـUSD، 3000 للـSYP مقابل 1 USD)").pack(side='left', padx=6)

        # filters + quick search
        filt = ttk.Frame(self)
        filt.pack(fill='x', padx=8, pady=6)
        ttk.Label(filt, text="تصفية ماركة/اسم / Filter Brand/Name:").pack(side='left')
        ttk.Entry(filt, width=20, textvariable=self.filter_brand).pack(side='left', padx=4)
        ttk.Label(filt, text="تصفية فئة / Filter Category:").pack(side='left', padx=6)
        ttk.Entry(filt, width=20, textvariable=self.filter_category).pack(side='left', padx=4)
        ttk.Button(filt, text="تطبيق التصفية / Apply Filters", command=self.apply_filters).pack(side='left', padx=8)

        ttk.Label(filt, text="بحث سريع (اسم أو باركود) / Quick Search (Name or Barcode):").pack(side='left', padx=10)
        search_entry = ttk.Entry(filt, width=25, textvariable=self.search_text)
        search_entry.pack(side='left')
        search_entry.bind('<Return>', lambda e: self.apply_search())
        ttk.Button(filt, text="بحث / Search", command=self.apply_search).pack(side='left', padx=6)

        # low stock controls
        lowfrm = ttk.Frame(self)
        lowfrm.pack(fill='x', padx=8, pady=4)
        ttk.Label(lowfrm, text="تنبيه الأصناف منخفضة الكمية (<) / Low Stock Threshold:").pack(side='left')
        ttk.Entry(lowfrm, width=6, textvariable=self.low_stock_threshold).pack(side='left', padx=4)
        ttk.Button(lowfrm, text="تحقق الآن / Check Low Stock", command=self.check_low_stock).pack(side='left', padx=8)

        # treeview for data
        self.tree = ttk.Treeview(self, show='headings')
        self.tree.pack(fill='both', expand=True, padx=8, pady=8)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb.pack(side='right', fill='y')
        self.hsb.pack(side='bottom', fill='x')

        # summary panel
        self.summary = tk.Text(self, height=6)
        self.summary.pack(fill='x', padx=8, pady=6)

        # bind closing event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # try to autoload default file or last opened file from settings
        if self.settings.get('last_file'):
            p = Path(self.settings['last_file'])
            if p.exists():
                self.file_path = str(p)
                self.summary.delete('1.0', tk.END)
                self.summary.insert(tk.END, f"Found last file: {p.name} — Loading...")
                self.after(500, self.load_and_process)

        else:
            for p in default_file_candidates():
                if p.exists():
                    self.file_path = str(p)
                    self.summary.delete('1.0', tk.END)
                    self.summary.insert(tk.END, f"Found default file: {p.name} — Loading...")
                    self.after(500, self.load_and_process)
                    break

        # show splash screen at start
        self.after(100, self.show_splash)

    # ---------------- Settings ----------------
    def load_settings(self):
        self.settings = {}
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                # load into variables
                self.currency_label.set(self.settings.get('currency', 'USD'))
                self.exchange_rate.set(self.settings.get('exchange_rate', 1.0))
                self.low_stock_threshold.set(self.settings.get('low_stock_threshold', 5))
            except Exception:
                self.settings = {}
        else:
            self.settings = {}

    def save_settings(self):
        self.settings['last_file'] = self.file_path
        self.settings['currency'] = self.currency_label.get()
        try:
            self.settings['exchange_rate'] = float(self.exchange_rate.get())
        except Exception:
            self.settings['exchange_rate'] = 1.0
        self.settings['low_stock_threshold'] = int(self.low_stock_threshold.get())
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)

    # ---------------- UI helpers ----------------
    def show_splash(self):
        splash = tk.Toplevel(self)
        splash.title("Smart Inventory Manager")
        splash.geometry("420x180+400+200")
        splash.overrideredirect(True)
        splash.configure(background="#013a63")
        lbl = tk.Label(splash, text="Smart Inventory Manager", font=('Helvetica', 16, 'bold'), fg='white', bg='#013a63')
        lbl.pack(pady=12)
        lbl2 = tk.Label(splash, text="Designed & Developed by ENG.HABIB", font=('Helvetica', 11), fg='white', bg='#013a63')
        lbl2.pack(pady=6)
        lbl3 = tk.Label(splash, text="ENG. HABIB NASER — Software & Networks Engineer", font=('Helvetica', 9), fg='white', bg='#013a63')
        lbl3.pack(pady=6)
        lbl4 = tk.Label(splash, text="Proudly Made in Syria 🇸🇾", font=('Helvetica', 8), fg='white', bg='#013a63')
        lbl4.pack(side='bottom', pady=8)
        self.after(1200, splash.destroy)

    def choose_file(self):
        p = filedialog.askopenfilename(filetypes=[("Excel files","*.xlsx;*.xls"),("All files","*.*")])
        if p:
            self.file_path = p
            messagebox.showinfo("تم اختيار الملف / File selected", f"الملف: {p}")
            self.save_settings()

    def refresh_current_file(self):
        if not self.file_path:
            messagebox.showwarning("لم يتم اختيار ملف / No file selected", "اختر ملف Excel أولاً / Select an Excel file first.")
            return
        self.load_and_process()

    def load_and_process(self):
        if not self.file_path:
            messagebox.showwarning("لم يتم اختيار ملف / No file selected", "اختر ملف Excel أولاً / Select an Excel file first.")
            return
        try:
            ex = float(self.exchange_rate.get())
        except Exception:
            ex = 1.0
        res = process_file(self.file_path, exchange_rate=ex)
        self.proc_result = res
        self.display_df(res['df'])
        # update summary
        meta = res['meta']
        lines = []
        lines.append(f"المسار / Path: {meta['file']}")
        lines.append(f"عدد السجلات / Records: {meta['total_items']}")
        lines.append(f"إجمالي القطع / Total pieces: {meta['total_pieces']}")
        lines.append(f"رأس المال الكلي ({self.currency_label.get()}) / Total Capital: {meta['grand_total']:.2f}")
        lines.append(f"الأعمدة المكتشفة / Detected columns: {meta['detected']}")
        self.summary.delete('1.0', tk.END)
        self.summary.insert(tk.END, "\\n".join(lines))
        # update capital badge
        self.update_capital_display(meta['grand_total'])
        # save last file
        self.save_settings()

    def display_df(self, df):
        # clear tree
        for c in self.tree.get_children():
            self.tree.delete(c)
        cols = list(df.columns.astype(str))
        self.tree["columns"] = cols
        for col in cols:
            # make headings clickable for sorting
            self.tree.heading(col, text=col, command=lambda _c=col: self.sort_by_column(_c, False))
            self.tree.column(col, width=140, anchor='w')
        # insert first 2000 rows only to keep UI responsive
        for _, row in df.head(2000).iterrows():
            vals = [str(row.get(c,"")) for c in cols]
            self.tree.insert("", "end", values=vals)

    def apply_filters(self):
        if self.proc_result is None:
            messagebox.showinfo("لا توجد بيانات / No data", "قم بتحميل ملف ومعالجته أولاً / Load and process a file first.")
            return
        df = self.proc_result['df']
        det = self.proc_result['meta']['detected']
        brand_f = self.filter_brand.get().strip()
        cat_f = self.filter_category.get().strip()
        df2 = df
        if brand_f and det.get('brand'):
            df2 = df2[df2[det['brand']].astype(str).str.contains(brand_f, case=False, na=False)]
        if cat_f and det.get('category'):
            df2 = df2[df2[det['category']].astype(str).str.contains(cat_f, case=False, na=False)]
        self.display_df(df2)
        # update summary with filtered totals
        total = df2['capital_in_currency'].sum()
        pieces = int(df2[det['quantity']].fillna(0).sum()) if det.get('quantity') else None
        self.summary.delete('1.0', tk.END)
        self.summary.insert(tk.END, f"بعد التصفية / After filters: إجمالي رأس المال = {total:.2f} {self.currency_label.get()} | إجمالي قطع = {pieces}")
        self.update_capital_display(total)

    def apply_search(self):
        if self.proc_result is None:
            messagebox.showinfo("لا توجد بيانات / No data", "قم بتحميل ملف ومعالجته أولاً / Load and process a file first.")
            return
        q = self.search_text.get().strip()
        if not q:
            # if empty, just redisplay full df
            self.display_df(self.proc_result['df'])
            self.summary.delete('1.0', tk.END)
            return
        df = self.proc_result['df']
        det = self.proc_result['meta']['detected']
        mask = pd.Series([False]*len(df))
        if det.get('name'):
            mask = mask | df[det['name']].astype(str).str.contains(q, case=False, na=False)
        if det.get('barcode'):
            mask = mask | df[det['barcode']].astype(str).str.contains(q, case=False, na=False)
        df2 = df[mask]
        self.display_df(df2)
        total = df2['capital_in_currency'].sum()
        pieces = int(df2[det['quantity']].fillna(0).sum()) if det.get('quantity') else None
        self.summary.delete('1.0', tk.END)
        self.summary.insert(tk.END, f"نتائج البحث / Search results: {len(df2)} سجلات | إجمالي رأس المال = {total:.2f} {self.currency_label.get()} | إجمالي قطع = {pieces}")
        self.update_capital_display(total)

    def check_low_stock(self):
        if self.proc_result is None:
            messagebox.showinfo("لا توجد بيانات / No data", "قم بتحميل ملف ومعالجته أولاً / Load and process a file first.")
            return
        threshold = int(self.low_stock_threshold.get())
        det = self.proc_result['meta']['detected']
        if not det.get('quantity'):
            messagebox.showinfo("عمود الكمية غير موجود / Quantity column missing", "لا يمكن التحقق من الكميات لأن عمود الكمية غير مكتشف في الملف / Quantity column not detected in file.")
            return
        df = self.proc_result['df']
        low = df[df[det['quantity']].fillna(0) < threshold]
        if low.empty:
            messagebox.showinfo("لا توجد أصناف منخفضة / No low-stock items", f"لا توجد أصناف أقل من {threshold} / No items below {threshold}.")
            return
        # show a simple list in a Toplevel
        win = tk.Toplevel(self)
        win.title(f"أصناف منخفضة الكمية / Low Stock (<{threshold})")
        txt = tk.Text(win, width=120, height=20)
        txt.pack(fill='both', expand=True)
        columns = det.get('name') or det.get('barcode') or 'index'
        for _, r in low.iterrows():
            name = str(r.get(det.get('name'), ''))
            barcode = str(r.get(det.get('barcode'), ''))
            qty = r.get(det['quantity'], 0)
            txt.insert(tk.END, f"{name} | {barcode} | {qty}\n")
        txt.config(state='disabled')

    def save_results(self):
        if self.proc_result is None:
            messagebox.showinfo("لا توجد نتائج / No results", "قم بتحميل ملف أولاً / Load a file first.")
            return
        out_xlsx, out_csv = save_results(self.proc_result, currency_label=self.currency_label.get())
        messagebox.showinfo("تم الحفظ / Saved", f"تم حفظ النتائج:\n{out_xlsx}\n{out_csv}")

    def show_chart(self, cat=None, save_path=None):
        if plt is None:
            messagebox.showwarning("Matplotlib مفقود / Matplotlib missing", "لتفعيل الرسم البياني ثبت مكتبة matplotlib / Install matplotlib to enable charts.")
            return
        if self.proc_result is None:
            messagebox.showinfo("لا توجد بيانات / No data", "حمل ملفًا أولاً / Load a file first.")
            return
        if cat is None:
            cat = self.proc_result['meta'].get('category_summary')
        if cat is None:
            messagebox.showinfo("لا توجد فئات / No categories", "لا يوجد عمود فئة في الملف لرسم مخططات الفئات / No category column to plot.")
            return
        plt.figure(figsize=(8,5))
        plt.bar(cat.iloc[:,0].astype(str), cat['total_capital'])
        plt.xticks(rotation=45, ha='right')
        plt.ylabel(f"رأس المال ({self.currency_label.get()})")
        plt.title("رأس المال حسب الفئة")
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
            return
        plt.show()

    def export_pdf_report(self):
        if self.proc_result is None:
            messagebox.showinfo("لا توجد بيانات / No data", "قم بتحميل ملف ومعالجته أولاً / Load and process a file first.")
            return
        if not REPORTLAB_OK:
            # fallback: try to save a simple text-based PDF using matplotlib (image) or just warn
            if plt is None:
                messagebox.showwarning("مكتبة PDF مفقودة / PDF library missing", "لتصدير PDF ضروري تثبيت reportlab أو matplotlib. حالياً لا يمكن إنشاء PDF.")
                return
        # build PDF
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_pdf = OUTPUT_DIR / f"تقرير_جرد_{ts}.pdf"
        # create chart image temporary
        chart_img = OUTPUT_DIR / f"_chart_{ts}.png"
        cat = self.proc_result['meta'].get('category_summary')
        if cat is not None and plt is not None:
            try:
                self.show_chart(cat=cat, save_path=str(chart_img))
            except Exception:
                chart_img = None
        else:
            chart_img = None

        if REPORTLAB_OK:
            doc = SimpleDocTemplate(str(out_pdf), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            story.append(Paragraph("تقرير الجرد / Inventory Report", styles['Title']))
            story.append(Spacer(1,12))
            meta = self.proc_result['meta']
            story.append(Paragraph(f"المسار / Path: {meta['file']}", styles['Normal']))
            story.append(Paragraph(f"إجمالي رأس المال ({self.currency_label.get()}) / Total Capital: {meta['grand_total']:.2f}", styles['Normal']))
            story.append(Paragraph(f"عدد السجلات / Records: {meta['total_items']}", styles['Normal']))
            story.append(Paragraph(f"إجمالي القطع / Total pieces: {meta['total_pieces']}", styles['Normal']))
            story.append(Spacer(1,12))
            if chart_img and chart_img.exists():
                story.append(Image(str(chart_img), width=450, height=250))
                story.append(Spacer(1,12))
            doc.build(story)
            messagebox.showinfo("تقرير PDF جاهز / PDF ready", f"تم إنشاء التقرير:\n{out_pdf}")
        else:
            # fallback: save a simple text file and notify user
            txt_path = OUTPUT_DIR / f"تقرير_جرد_نص_{ts}.txt"
            meta = self.proc_result['meta']
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"تقرير الجرد / Inventory Report\n")
                f.write(f"المسار / Path: {meta['file']}\n")
                f.write(f"إجمالي رأس المال ({self.currency_label.get()}): {meta['grand_total']:.2f}\n")
                f.write(f"عدد السجلات / Records: {meta['total_items']}\n")
                f.write(f"إجمالي القطع / Total pieces: {meta['total_pieces']}\n")
            messagebox.showinfo("تقرير بديل تم إنشاؤه / Fallback report created", f"تم إنشاء تقرير نصي بديل:\n{txt_path}\nلتصدير PDF ثبت مكتبة reportlab.")

    def open_output_dir(self):
        try:
            os.startfile(OUTPUT_DIR)
        except Exception:
            webbrowser.open(str(OUTPUT_DIR))

    def show_about(self):
        txt = ("Smart Inventory Manager — Arabic/English Edition\n\n"
               "Developed & Designed by ENG. HABIB NASER\n"
               "Software & Networks Engineer\n"
               "ENG.HABIB — 2025\n\n"
               "Email: (add your email) — Optional\n"
               "Thank you for using the tool.")
        messagebox.showinfo("حول البرنامج / About", txt)

    def on_closing(self):
        # save settings on close
        self.save_settings()
        # bilingual closing popup
        msg = ("💬 Thank you for using Smart Inventory Manager\n\n"
               "👨‍💻 تم تطوير وتصميم البرنامج بواسطة المهندس حبيب ناصر (ENG. HABIB NASER)\n\n"
               "© 2025 All Rights Reserved")
        messagebox.showinfo("Goodbye / وداعاً", msg)
        self.destroy()

    def update_capital_display(self, value):
        try:
            v = float(value)
        except Exception:
            v = 0.0
        self.capital_display.config(text=f"رأس المال الكلي / Total Capital: {v:,.2f} {self.currency_label.get()}")

    def sort_by_column(self, col, reverse):
        # get all values
        try:
            l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        except Exception:
            return
        # try numeric sort
        try:
            l.sort(key=lambda t: float(t[0].replace(',','')) if t[0] not in (None, '') else 0.0, reverse=reverse)
        except Exception:
            l.sort(key=lambda t: t[0], reverse=reverse)
        # rearrange
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        # reverse sort next time
        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

def write_requirements():
    reqs = ["pandas","openpyxl","xlrd","numpy","matplotlib","reportlab"]
    with open(OUTPUT_DIR / "requirements.txt","w", encoding="utf-8") as f:
        f.write("\\n".join(reqs))
    print("requirements.txt created in", OUTPUT_DIR)


# ----------------- Main -----------------
if __name__ == '__main__':
    write_requirements()
    app = InventoryApp()
    app.mainloop()

# PyInstaller example (for Windows):
# pyinstaller --onefile --add-data "المصنف1.xlsx;." smart_inventory_manager_ar_v3.py
