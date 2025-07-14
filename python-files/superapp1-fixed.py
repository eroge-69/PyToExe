import os
import sys
import re
import datetime
import textwrap
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext

import pandas as pd
import ttkbootstrap as ttkb
from PIL import Image, ImageTk  # for images

# Optional dependencies
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB = True
except ImportError:
    MATPLOTLIB = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        PageBreak,
        Image as PDFImage,
    )
    REPORTLAB = True
except ImportError:
    REPORTLAB = False

# ===================== CONFIGURATION =====================
ROLES_FILE = "roles_ciberseguridad.xlsx"
CERTS_FILE = "plantilla_certificacion.xlsx"
IMG_DIR = "imagenes"

FONT = ("Segoe UI", 10)
BOLD = ("Segoe UI", 12, "bold")
TINY = ("Segoe UI", 9)
THEMES = ("litera", "darkly", "superhero", "minty")
TAB_ORDER = [
    "Resumen",
    "Descripción",
    "Certificaciones asociadas",
    "Salario",
    "Recursos",
    "Info extra",
    "Imagen",
    "Notas",
    "Guía de uso",
]
URL_RGX = re.compile(r"(https?://\S+)")
NUM_RGX = re.compile(r"(\d{2,6})")

SECS = {
    "Descripción": ["descripción"],
    "Certificaciones asociadas": ["certificaciones"],
    "Salario": ["salario"],
    "Recursos": ["recursos"],
    "Info extra": ["información adicional", "info extra"],
}

# ===================== UTILS =====================

def ensure_file(path: str, title: str) -> str:
    """Ensure an Excel file exists; prompt user if missing."""
    if Path(path).is_file():
        return path
    root = tk.Tk(); root.withdraw()
    messagebox.showinfo("Seleccionar archivo", f"No se encontró {path}. Selecciona el archivo de {title}.")
    file_path = filedialog.askopenfilename(title=f"Selecciona {title}", filetypes=[("Excel", "*.xlsx *.xls")])
    if not file_path:
        messagebox.showerror("Error", f"Debe seleccionarse un archivo de {title}.")
        sys.exit(1)
    return file_path

def load_indexed_book(path: str):
    """Load sheets with optional 'indice' mapping sheet -> name."""
    xls = pd.ExcelFile(path)
    sheets = xls.sheet_names
    if "indice" not in sheets:
        data = {s: pd.read_excel(xls, sheet_name=s, dtype=str) for s in sheets}
        return data, sheets
    idx_df = pd.read_excel(xls, sheet_name="indice", header=None, dtype=str)
    names = [str(v).strip() for v in idx_df.iloc[:, 0].dropna() if str(v).strip()]
    detail_sheets = [s for s in sheets if s != "indice"]
    data: Dict[str, pd.DataFrame] = {}
    for i, name in enumerate(names[: len(detail_sheets)]):
        data[name] = pd.read_excel(xls, sheet_name=detail_sheets[i], dtype=str)
    return data, names[: len(detail_sheets)]

def parse_sheet(df: pd.DataFrame) -> Dict[str, str]:
    """Convert an Excel sheet to a dict of sections -> text."""
    df = df.dropna(axis=1, how="all").fillna("")
    lines = df.apply(lambda r: " ".join(r.astype(str)).strip(), axis=1).tolist()

    out: Dict[str, str] = {k: "" for k in SECS}
    cur: Optional[str] = None
    buf: List[str] = []

    def flush():
        nonlocal buf, cur
        if cur:
            out[cur] = "\n".join(buf).strip()
        buf = []

    for ln in lines:
        if not ln:
            continue
        low = ln.lower().rstrip(":")
        new = next((s for s, keys in SECS.items() if any(k in low for k in keys)), None)
        if new:
            flush(); cur = new
            rest = re.sub(r"(?i)^.*?:", "", ln, 1).strip()
            if rest:
                buf.append(rest)
        else:
            buf.append(ln)
    flush()
    return out

def avg_salary(text: str) -> Optional[float]:
    nums = [int(n) for n in NUM_RGX.findall(text)]
    if len(nums) >= 2:
        return sum(nums[:2]) / 2
    return nums[0] if nums else None

def get_img_path(name: str, mode: str):
    for ext in (".png", ".jpg", ".jpeg", ".gif"):
        p = os.path.join(IMG_DIR, f"{mode}_{name.replace(' ', '_')}{ext}")
        if os.path.isfile(p):
            return p
    for ext in (".png", ".jpg", ".jpeg", ".gif"):
        p = os.path.join(IMG_DIR, f"{name.replace(' ', '_')}{ext}")
        if os.path.isfile(p):
            return p
    return None

def safe_img_load(path, maxsize=(260, 260)):
    try:
        img = Image.open(path)
        img.thumbnail(maxsize)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def safe_img_reportlab(path, width=200):
    try:
        return PDFImage(path, width, width)
    except Exception:
        return None

# ===================== MAIN APP =====================
class CyberSuperApp(ttkb.Window):
    """Main window class."""

    def __init__(self):
        super().__init__(themename=THEMES[0])
        self.title("Roles y Certificaciones – SuperApp 2025")
        self.geometry("1280x800")
        self.minsize(1100, 650)

        # Load data
        self.roles_path = ensure_file(ROLES_FILE, "Roles")
        self.certs_path = ensure_file(CERTS_FILE, "Certificaciones")
        self.roles_raw, self.role_names = load_indexed_book(self.roles_path)
        self.certs_data, self.cert_names = load_indexed_book(self.certs_path)

        # Build maps
        self.roles_data: Dict[str, Dict[str, str]] = {}
        self.salary: Dict[str, Optional[float]] = {}
        self.roles_cert_map: Dict[str, List[str]] = {}
        self.certs_role_map: Dict[str, List[str]] = {}
        for name, df in self.roles_raw.items():
            sections = parse_sheet(df)
            self.roles_data[name] = sections
            self.salary[name] = avg_salary(sections["Salario"])
            certs = [c.strip() for c in sections.get("Certificaciones asociadas", "").split("\n") if c.strip()]
            self.roles_cert_map[name] = certs
            for cert in certs:
                self.certs_role_map.setdefault(cert, []).append(name)

        # UI state vars
        self.cur_role = None
        self.cur_cert = None

        # Build interface
        self._build_ui()
        self._populate_lists()
        self._select_initial()

    # -------------------- UI BUILDERS --------------------
    def _build_ui(self):
        top = ttkb.Frame(self, padding=5)
        top.pack(fill=tk.X)

        # Theme toggle
        self.theme_icon = tk.StringVar(value="🌙")
        ttkb.Button(top, textvariable=self.theme_icon, width=3, command=self._toggle_theme).pack(side=tk.LEFT, padx=4)

        # Certification filter
        ttkb.Label(top, text="Filtrar por certificación:").pack(side=tk.LEFT, padx=(8, 2))
        self.filter_var = tk.StringVar()
        filter_entry = ttkb.Entry(top, textvariable=self.filter_var, width=20)
        filter_entry.pack(side=tk.LEFT)
        self.filter_var.trace_add("write", lambda *_: self._apply_filter())

        # Global search
        ttkb.Label(top, text="Buscar:").pack(side=tk.LEFT, padx=(4, 2))
        self.search_var = tk.StringVar()
        search_entry = ttkb.Entry(top, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT)
        self.search_var.trace_add("write", lambda *_: self._global_search())

        # LinkedIn search
        ttkb.Label(top, text="Buscar empleo en LinkedIn:").pack(side=tk.LEFT, padx=(8, 2))
        self.job_var = tk.StringVar()
        job_entry = ttkb.Entry(top, textvariable=self.job_var, width=22)
        job_entry.pack(side=tk.LEFT)
        job_entry.bind("<Return>", self._search_linkedin)
        ttkb.Button(top, text="Buscar empleo", command=self._search_linkedin).pack(side=tk.LEFT, padx=2)

        # Split panes
        main = ttkb.Panedwindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=7, pady=4)

        # Left pane (lists + card)
        left = ttkb.Frame(main, padding=8)
        main.add(left, weight=1)

        ttkb.Label(left, text="Roles", font=BOLD).pack(anchor="w")
        self.roles_list = tk.Listbox(left, font=FONT, height=18, exportselection=False)
        self.roles_list.pack(fill=tk.BOTH, expand=False, pady=3)
        self.roles_list.bind("<<ListboxSelect>>", self._on_role_select)
        self.roles_list.bind("<Motion>", self._on_role_hover)
        self.roles_list.bind("<Leave>", lambda _e: self._clear_card())

        ttkb.Label(left, text="Certificaciones", font=BOLD).pack(anchor="w", pady=(10, 0))
        self.certs_list = tk.Listbox(left, font=FONT, height=10, exportselection=False)
        self.certs_list.pack(fill=tk.BOTH, expand=False, pady=3)
        self.certs_list.bind("<<ListboxSelect>>", self._on_cert_select)

        self.card_frame = ttkb.Frame(left)
        self.card_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 2))

        # Action buttons
        btn_frame = ttkb.Frame(left)
        btn_frame.pack(fill=tk.X, pady=4)
        ttkb.Button(btn_frame, text="Gráfica salarios", command=self._salary_chart).pack(side=tk.LEFT, padx=2)
        ttkb.Button(btn_frame, text="Comparar", command=self._compare_dialog).pack(side=tk.LEFT, padx=2)
        ttkb.Button(btn_frame, text="Ranking", command=self._show_ranking).pack(side=tk.LEFT, padx=2)

        # Right pane (notebook)
        right = ttkb.Frame(main, padding=8)
        main.add(right, weight=4)

        self.nb = ttkb.Notebook(right)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.section_widgets: Dict[str, tk.Text] = {}
        self.img_label: Optional[ttkb.Label] = None

        for tab in TAB_ORDER:
            fr = ttkb.Frame(self.nb)
            self.nb.add(fr, text=tab)
            if tab == "Imagen":
                self.img_label = ttkb.Label(fr)
                self.img_label.pack(pady=6)
            elif tab == "Notas":
                self.notes_text = scrolledtext.ScrolledText(fr, wrap=tk.WORD, font=FONT)
                self.notes_text.pack(fill=tk.BOTH, expand=True, pady=4)
                ttkb.Button(fr, text="Guardar Notas", command=self._save_notes).pack(pady=6)
            elif tab == "Guía de uso":
                guide = scrolledtext.ScrolledText(fr, wrap=tk.WORD, font=FONT, state=tk.DISABLED)
                guide.pack(fill=tk.BOTH, expand=True, pady=4)
                self._set_guide(guide)
            else:
                txt = scrolledtext.ScrolledText(fr, wrap=tk.WORD, font=FONT, state=tk.DISABLED)
                txt.pack(fill=tk.BOTH, expand=True)
                txt.tag_config("bold", font=BOLD)
                self.section_widgets[tab] = txt

        ttkb.Button(right, text="Exportar ficha PDF", command=self._export_pdf).pack(pady=7)

    # -------------------- LISTFILLERS --------------------
    def _populate_lists(self):
        self.roles_list.delete(0, tk.END)
        for r in self.role_names:
            self.roles_list.insert(tk.END, r)
        self.certs_list.delete(0, tk.END)
        for c in self.cert_names:
            self.certs_list.insert(tk.END, c)

    def _select_initial(self):
        if self.role_names:
            self.roles_list.selection_set(0)
            self._load_role()

    # -------------------- THEME --------------------
    def _toggle_theme(self):
        idx = THEMES.index(self.style.theme.name)
        new_theme = THEMES[(idx + 1) % len(THEMES)]
        self.style.theme_use(new_theme)
        self.theme_icon.set("☀️" if new_theme in ("darkly", "superhero") else "🌙")

    # -------------------- FILTER & SEARCH --------------------
    def _apply_filter(self):
        tgt = self.filter_var.get().strip().lower()
        self.roles_list.delete(0, tk.END)
        for r in self.role_names:
            certs = " ".join(self.roles_cert_map.get(r, []))
            if tgt in certs.lower() if tgt else True:
                self.roles_list.insert(tk.END, r)

    def _global_search(self):
        term = self.search_var.get().strip().lower()
        self.roles_list.delete(0, tk.END)
        self.certs_list.delete(0, tk.END)
        if not term:
            self._populate_lists(); return

        for r, secs in self.roles_data.items():
            if term in r.lower() or any(term in v.lower() for v in secs.values()):
                self.roles_list.insert(tk.END, r)
        for c in self.cert_names:
            if term in c.lower():
                self.certs_list.insert(tk.END, c)

    # -------------------- CARD (hover) --------------------
    def _on_role_hover(self, event):
        idx = self.roles_list.nearest(event.y)
        if idx < 0:
            return
        name = self.roles_list.get(idx)
        data = self.roles_data[name]
        resumen = data.get("Descripción", "").split("\n")[0][:120] + "..."
        certs = ", ".join(self.roles_cert_map.get(name, [])) or "Ninguna"
        salary = self.salary.get(name)
        self._show_card(name, resumen, certs, salary)

    def _show_card(self, name: str, resumen: str, certs: str, salary: Optional[float]):
        for w in self.card_frame.winfo_children():
            w.destroy()
        frame = ttkb.Frame(self.card_frame, bootstyle="primary", relief=tk.RIDGE, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)
        ttkb.Label(frame, text=name, font=BOLD).pack(anchor="w")
        ttkb.Label(frame, text="Descripción:", font=TINY).pack(anchor="w")
        ttkb.Label(frame, text=resumen, wraplength=260, font=FONT).pack(anchor="w")
        ttkb.Label(frame, text=f"Certificaciones: {certs}", font=TINY).pack(anchor="w")
        ttkb.Label(frame, text=f"Salario estimado: {salary if salary else 'N/A'}", font=TINY).pack(anchor="w")

        p = get_img_path(name, "rol")
        if p:
            img = safe_img_load(p, (60, 60))
            if img:
                ttkb.Label(frame, image=img).pack(anchor="e")
                frame.img = img  # keep reference

    def _clear_card(self):
        for w in self.card_frame.winfo_children():
            w.destroy()

    # -------------------- LIST SELECTIONS --------------------
    def _on_role_select(self, _):
        sel = self.roles_list.curselection()
        if not sel:
            return
        name = self.roles_list.get(sel[0])
        self.cur_role, self.cur_cert = name, None
        self.certs_list.selection_clear(0, tk.END)
        self._load_role(name)

    def _on_cert_select(self, _):
        sel = self.certs_list.curselection()
        if not sel:
            return
        name = self.certs_list.get(sel[0])
        self.cur_cert, self.cur_role = name, None
        self.roles_list.selection_clear(0, tk.END)
        self._load_cert(name)

    # -------------------- FORMATTER --------------------
    ICON_MAP = {
        "proveedor": "🏢",
        "issuer": "🏢",
        "organización": "🏢",
        "duración": "⏱️",
        "coste": "💶",
        "precio": "💶",
        "fee": "💶",
        "requisitos": "📝",
        "requisitos previos": "📝",
        "contenidos": "📚",
        "temario": "📚",
        "contenido": "📚",
        "objetivo": "🎯",
        "examen": "🧪",
        "nivel": "⭐",
        "idioma": "🌐",
        "modalidad": "💻",
        "formato": "💻",
        "certificación": "🎓",
        "certificado": "🎓",
    }
    COLOR_MAP = {
        "proveedor": "#0d6efd",
        "duración": "#dc3545",
        "coste": "#198754",
        "requisitos": "#fd7e14",
        "contenidos": "#6610f2",
        "objetivo": "#20c997",
        "nivel": "#ffc107",
        "idioma": "#0dcaf0",
        "modalidad": "#6610f2",
        "certificación": "#6f42c1",
    }

    def _format_cert_description_rich(self, desc_long: str, widget: tk.Text):
        """Return display text and configure tags for rich presentation."""
        lines = [line.strip() for line in desc_long.splitlines() if line.strip()]
        rows: List[tuple] = []
        tags: Dict[str, str] = {}
        idx = 1
        for line in lines:
            if ":" in line:
                campo, valor = line.split(":", 1)
                campo_key = campo.strip().lower()
                valor = valor.strip()

                icon = self.ICON_MAP.get(campo_key, "🔹")
                color = self.COLOR_MAP.get(campo_key, "#222")
                tagc = f"campo_{idx}"
                tagv = f"valor_{idx}"
                tags[tagc] = color
                tags[tagv] = "#222222"

                # bullet lists
                if any(sep in valor for sep in [";", "·", "•"]):
                    items = re.split(r";|·|•", valor)
                    items = [it.strip() for it in items if it.strip()]
                    valor_fmt = "\n      " + "\n      ".join([f"• {it}" for it in items])
                else:
                    valor_fmt = f" {valor}"

                row = f"{icon} {campo.strip():<16}: {valor_fmt}"
                rows.append((row, tagc, tagv))
                idx += 1
            else:
                rows.append((f"   {line}", None, None))

        # render in hidden text; we return string + tags so caller can insert
        display = ""
        line_no = 1
        for text, tagc, tagv in rows:
            if tagc and tagv and ":" in text:
                campo, valor = text.split(":", 1)
                display += f"{campo}:"
                start_campo = f"{line_no}.0"
                end_campo = f"{line_no}.{len(campo)+1}"
                widget.tag_add(tagc, start_campo, end_campo)

                display += f"{valor}\n"
                start_val = f"{line_no}.{len(campo)+1}"
                end_val = f"{line_no}.{len(campo)+1+len(valor)}"
                widget.tag_add(tagv, start_val, end_val)
            else:
                display += text + "\n"
            line_no += 1
        return display, tags

    # -------------------- URL helper --------------------
    def _add_urls(self, widget: tk.Text, text: str):
        """Insert text and make headings bold, links clickable."""
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        text = re.sub(r"\n\s*-\s+", "\n• ", text)
        widget.insert(tk.END, text)

        # headings (anything like 'Campo:')
        idx = "1.0"
        while True:
            idx = widget.search(r".+?:", idx, tk.END, regexp=True)
            if not idx:
                break
            lineend = widget.index(f"{idx} lineend")
            widget.tag_add("bold", idx, lineend)
            idx = widget.index(f"{lineend}+1c")

        # links
        for i, match in enumerate(URL_RGX.finditer(text)):
            s, e = match.span()
            tag = f"url{i}"
            widget.tag_add(tag, f"1.0+{s}c", f"1.0+{e}c")
            widget.tag_config(tag, foreground="blue", underline=True)
            link = match.group(1)
            widget.tag_bind(tag, "<Button-1>", lambda _e, l=link: webbrowser.open(l))
        widget.config(state=tk.DISABLED)

    # -------------------- DATA LOADERS --------------------
    def _load_role(self, name: Optional[str] = None):
        if not name:
            sel = self.roles_list.curselection()
            if not sel:
                return
            name = self.roles_list.get(sel[0])

        data = self.roles_data[name]
        resumen = data["Descripción"].split("\n")[0]
        self._add_urls(self.section_widgets["Resumen"], resumen)
        for s in ["Descripción", "Salario", "Recursos", "Info extra"]:
            self._add_urls(self.section_widgets[s], data.get(s, ""))

        certs_txt = "\n".join([f"• {c}" for c in self.roles_cert_map.get(name, [])]) or "Ninguna certificación asociada"
        self._add_urls(self.section_widgets["Certificaciones asociadas"], certs_txt)

        self._show_img(name, "rol")
        self.nb.select(0)

    def _load_cert(self, name: str):
        df = self.certs_data.get(name)
        desc = df.to_string(index=False).split("\n")[0] if df is not None else "Sin datos"
        self._add_urls(self.section_widgets["Resumen"], desc)

        desc_long = df.to_string(index=False) if df is not None else "Sin datos"
        widget = self.section_widgets["Descripción"]
        widget.config(state=tk.NORMAL); widget.delete("1.0", tk.END)
        desc_fmt, tags = self._format_cert_description_rich(desc_long, widget)
        self._add_urls(widget, desc_fmt)
        for tag, color in tags.items():
            widget.tag_config(tag, foreground=color)

        roles = self.certs_role_map.get(name, [])
        txt = "\n".join([f"• {r}" for r in roles]) or "No hay roles principales que requieran esta certificación."
        self._add_urls(self.section_widgets["Certificaciones asociadas"], txt)

        for s in ["Salario", "Recursos", "Info extra"]:
            self.section_widgets[s].config(state=tk.NORMAL)
            self.section_widgets[s].delete("1.0", tk.END)
            self.section_widgets[s].insert(tk.END, "N/A")
            self.section_widgets[s].config(state=tk.DISABLED)

        self._show_img(name, "cert")
        self.nb.select(0)

    # -------------------- IMAGE --------------------
    def _show_img(self, name: str, mode: str):
        p = get_img_path(name, mode)
        if not self.img_label:
            return
        if p:
            img = safe_img_load(p, (360, 360))
            if img:
                self.img_label.config(image=img, text="")
                self.img_label.image = img
            else:
                self.img_label.config(image="", text="(Imagen no soportada)")
        else:
            self.img_label.config(image="", text="(Sin imagen)")

    # -------------------- OTHER ACTIONS --------------------
    def _compare_dialog(self):
        sel_roles = [self.roles_list.get(i) for i in self.roles_list.curselection()]
        sel_certs = [self.certs_list.get(i) for i in self.certs_list.curselection()]
        if (len(sel_roles) + len(sel_certs)) not in (2, 3):
            messagebox.showinfo("Comparar", "Selecciona 2 o 3 roles/certificaciones en total.")
            return
        CompareWindow(self, sel_roles, sel_certs, self.roles_data, self.certs_data, self.salary)

    def _show_ranking(self):
        win = ttkb.Toplevel(self)
        win.title("Tendencias y Ranking")
        ttkb.Label(win, text="Top Roles con más certificaciones asociadas", font=BOLD).pack(pady=4)
        data = sorted(self.roles_cert_map.items(), key=lambda x: len(x[1]), reverse=True)
        txt = "\n".join([f"{name}: {len(certs)} certs" for name, certs in data[:10]])
        ttkb.Label(win, text=txt, font=FONT, bootstyle="success").pack(anchor="w", padx=12)

        ttkb.Label(win, text="Top Certificaciones más requeridas por roles", font=BOLD).pack(pady=4)
        cert_count = {c: len(r) for c, r in self.certs_role_map.items()}
        data = sorted(cert_count.items(), key=lambda x: x[1], reverse=True)
        txt = "\n".join([f"{name}: requerido por {n} roles" for name, n in data[:10]])
        ttkb.Label(win, text=txt, font=FONT, bootstyle="info").pack(anchor="w", padx=12)

    def _search_linkedin(self, _=None):
        query = self.job_var.get().strip()
        if not query:
            messagebox.showinfo("LinkedIn", "Introduce un término de búsqueda."); return
        url_query = query.replace(" ", "%20")
        url = f"https://www.linkedin.com/jobs/search/?keywords={url_query}"
        webbrowser.open(url)

    def _export_pdf(self):
        if not REPORTLAB:
            messagebox.showinfo("Exportar", "ReportLab no está instalado."); return
        name = self.cur_role or self.cur_cert
        mode = "rol" if self.cur_role else "cert"
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = filedialog.asksaveasfilename(initialfile=f"{mode}_{name.split()[0]}_{ts}.pdf", defaultextension=".pdf")
        if not fname:
            return
        doc = SimpleDocTemplate(fname, pagesize=A4)
        styles = getSampleStyleSheet()
        flow = [Paragraph(f"{'Rol' if mode == 'rol' else 'Certificación'}: {name}", styles["Title"]), Spacer(1, 10)]

        p = get_img_path(name, mode)
        if p and (img := safe_img_reportlab(p, width=160)):
            flow.extend([img, Spacer(1, 8)])

        if mode == "rol":
            data = self.roles_data[name]
            for sec in ["Descripción", "Certificaciones asociadas", "Salario", "Recursos", "Info extra"]:
                flow.append(Paragraph(sec, styles["Heading2"]))
                txt = data.get(sec, "").replace("\n", "<br/>").replace("•", "&#9679;")
                flow.append(Paragraph(txt, styles["BodyText"]))
                flow.append(Spacer(1, 6))
        else:
            df = self.certs_data.get(name)
            txt = df.to_string(index=False).replace("\n", "<br/>") if df is not None else "Sin datos"
            flow.append(Paragraph("Detalle de certificación", styles["Heading2"]))
            flow.append(Paragraph(txt, styles["BodyText"]))
        doc.build(flow)
        messagebox.showinfo("PDF creado", os.path.abspath(fname))

    def _save_notes(self):
        content = self.notes_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showinfo("Guardar Notas", "No hay contenido para guardar."); return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"notas_{ts}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Guardar Notas", f"Notas guardadas en: {os.path.abspath(fname)}")

    def _set_guide(self, widget: tk.Text):
        guide_text = textwrap.dedent(
            """
            BIENVENIDO AL VISOR AVANZADO DE ROLES Y CERTIFICACIONES DE CIBERSEGURIDAD

            — Funcionalidades principales:
            • Buscar y filtrar roles/certificaciones, con resultados instantáneos.
            • Exporta cualquier rol/certificación a PDF profesional (incluyendo imagen si existe).
            • Gráfica de salarios (requiere matplotlib instalado).
            • Ranking de tendencias: roles/certs más demandados.
            • Temas de color claro/oscuro y más.
            • LinkedIn search integrado.
            """
        ).strip()
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, guide_text)
        widget.config(state=tk.DISABLED)

    def _salary_chart(self):
        if not MATPLOTLIB:
            messagebox.showinfo("Gráfica", "matplotlib no está instalado."); return
        r_valid = [r for r in self.role_names if self.salary.get(r) is not None]
        if not r_valid:
            messagebox.showinfo("Gráfica", "No hay datos salariales suficientes."); return
        s_vals = [self.salary[r] for r in r_valid]
        plt.figure(figsize=(9, max(6, len(r_valid)*0.32)))
        plt.barh(r_valid, s_vals)
        plt.xlabel("Salario promedio (€)")
        plt.title("Salario promedio por rol de ciberseguridad")
        plt.tight_layout()
        plt.show()

# ===================== COMPARE WINDOW =====================
class CompareWindow(ttkb.Toplevel):
    def __init__(self, master: CyberSuperApp, sel_roles, sel_certs, roles_data, certs_data, salary):
        super().__init__(master)
        self.title("Comparador avanzado")
        self.geometry("950x700")
        nb = ttkb.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

        # helper to add URLs
        self._add_urls = master._add_urls
        self._format_cert_description_rich = master._format_cert_description_rich

        for r in sel_roles:
            fr = ttkb.Frame(nb)
            nb.add(fr, text=f"Rol: {r}")
            self._populate_role_frame(fr, r, roles_data, salary, master)
        for c in sel_certs:
            fr = ttkb.Frame(nb)
            nb.add(fr, text=f"Cert: {c}")
            self._populate_cert_frame(fr, c, certs_data, master)

        ttkb.Button(
            self,
            text="Exportar comparativa a PDF",
            command=lambda: self._export_pdf(sel_roles, sel_certs, roles_data, certs_data),
        ).pack(pady=12)

    def _populate_role_frame(self, fr, r, roles_data, salary, master):
        img_path = get_img_path(r, "rol")
        if img_path and (img := safe_img_load(img_path, (120, 120))):
            lbl = ttkb.Label(fr, image=img); lbl.image = img; lbl.pack(pady=5)
        for s in ["Descripción", "Certificaciones asociadas", "Salario", "Recursos", "Info extra"]:
            ttkb.Label(fr, text=s, font=BOLD).pack(anchor="w", padx=6, pady=(8, 0))
            txt = scrolledtext.ScrolledText(fr, height=5, wrap=tk.WORD, font=FONT)
            txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))
            if s == "Salario" and salary.get(r):
                self._add_urls(txt, str(salary[r]))
            else:
                self._add_urls(txt, roles_data[r].get(s, ""))
            txt.config(state=tk.DISABLED)

    def _populate_cert_frame(self, fr, c, certs_data, master):
        img_path = get_img_path(c, "cert")
        if img_path and (img := safe_img_load(img_path, (120, 120))):
            lbl = ttkb.Label(fr, image=img); lbl.image = img; lbl.pack(pady=5)
        df = certs_data.get(c)
        desc = df.to_string(index=False) if df is not None else "Sin datos"
        txt = scrolledtext.ScrolledText(fr, height=12, wrap=tk.WORD, font=FONT)
        txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 4))
        self._add_urls(txt, desc)
        txt.config(state=tk.DISABLED)

    def _export_pdf(self, sel_roles, sel_certs, roles_data, certs_data):
        if not REPORTLAB:
            messagebox.showinfo("Exportar", "ReportLab no está instalado."); return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = filedialog.asksaveasfilename(initialfile=f"Comparativa_{ts}.pdf", defaultextension=".pdf")
        if not fname:
            return
        doc = SimpleDocTemplate(fname, pagesize=A4)
        styles = getSampleStyleSheet()
        flow = []
        for r in sel_roles:
            flow.append(Paragraph(f"Rol: {r}", styles["Heading1"]))
            img_path = get_img_path(r, "rol")
            if img_path and (img := safe_img_reportlab(img_path, width=120)):
                flow.extend([img, Spacer(1, 6)])
            for s in ["Descripción", "Certificaciones asociadas", "Salario", "Recursos", "Info extra"]:
                flow.append(Paragraph(s, styles["Heading2"]))
                txt = roles_data[r].get(s, "").replace("\n", "<br/>").replace("•", "&#9679;")
                flow.append(Paragraph(txt, styles["BodyText"]))
                flow.append(Spacer(1, 8))
            flow.append(PageBreak())
        for c in sel_certs:
            flow.append(Paragraph(f"Certificación: {c}", styles["Heading1"]))
            img_path = get_img_path(c, "cert")
            if img_path and (img := safe_img_reportlab(img_path, width=120)):
                flow.extend([img, Spacer(1, 6)])
            df = certs_data.get(c)
            txt = df.to_string(index=False).replace("\n", "<br/>") if df is not None else "Sin datos"
            flow.append(Paragraph("Detalle de certificación", styles["Heading2"]))
            flow.append(Paragraph(txt, styles["BodyText"]))
            flow.append(PageBreak())
        doc.build(flow)
        messagebox.showinfo("Comparativa PDF", os.path.abspath(fname))

# ===================== MAIN =====================

def main():
    app = CyberSuperApp()
    app.mainloop()

if __name__ == "__main__":
    main()
