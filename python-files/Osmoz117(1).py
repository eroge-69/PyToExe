#!/usr/bin/env python
# coding: utf-8

# In[1]:


# ============================================
# Osmoz 1.16 — Import Amazon (.xlsx/.csv/.tsv/.txt) + Étiquettes PDF (A4, 8/page)
# Flux: [Charger données] -> cocher/décocher -> [Générer le PDF]
# Regroupement: produits similaires (clé: product-name -> sku -> asin), affichage "[N] Nom produit"
# Statuts: total lignes/valides, nb commandes (uniques), nb items, commandes par pays
# PDF: A4, 8 étiquettes par page (2 x 4), logo optionnel
# Labels PDF: adresse seule (PAS de nom produit, PAS de n° de commande), adresse en gras + taille augmentée
# Déduplication PDF: 1 étiquette par commande (order-id) pour les produits sélectionnés
# RESET: remet l'interface à zéro pour un nouvel import
# ============================================

import sys, subprocess, importlib, io, os, re, math, traceback, csv
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# ---------- Install deps if missing ----------
def _pip_install(pkg):
    import importlib.util
    if importlib.util.find_spec(pkg) is None:
        print(f"Installation de {pkg}…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for p in ["pandas", "ipywidgets", "openpyxl", "chardet", "reportlab", "pillow"]:
    _pip_install(p)

import pandas as pd, chardet
from ipywidgets import (
    VBox, HBox, HTML, Button, FileUpload, Output, Layout, Checkbox, ToggleButtons
)
from IPython.display import display, FileLink, clear_output
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image

# ========== UI container (allow rebuild on RESET) ==========
app_box = VBox()

# ---------- Journal ----------
log = Output()
def log_print(*args, **kw):
    with log:
        print(*args, **kw)

# ---------- Utils bytes / text ----------
def to_bytes(obj) -> bytes:
    if obj is None:
        return b""
    if isinstance(obj, (bytes, bytearray)):
        return bytes(obj)
    try:
        if isinstance(obj, memoryview):
            return obj.tobytes()
    except NameError:
        pass
    try:
        return bytes(obj)
    except Exception:
        return b""

def smart_decode(b: bytes) -> Tuple[str, str]:
    if not b:
        return "", "utf-8"
    try:
        return b.decode("utf-8"), "utf-8"
    except Exception:
        enc = chardet.detect(b).get("encoding") or "utf-8"
        try:
            return b.decode(enc, errors="replace"), enc
        except Exception:
            return b.decode("latin-1", errors="replace"), "latin-1"

# ---------- Parsing helpers ----------
AMZ_COLS_BASE = [
    "order-id","order-item-id","purchase-date","payments-date","reporting-date","promise-date","days-past-promise",
    "buyer-email","buyer-name","payment-method-details","buyer-phone-number","sku","number-of-items","product-name",
    "quantity-purchased","quantity-shipped","quantity-to-ship","ship-service-level","recipient-name",
    "ship-address-1","ship-address-2","ship-address-3","ship-city","ship-state","ship-postal-code","ship-country",
    "customized-url","customized-page","is-business-order","purchase-order-number","price-designation",
    "buyer-company-name","is-iba","buyer-citizen-name","buyer-citizen-id","is-ispu-order","is-pickup-point-order",
    "pickup-point-type","order-invoice-type","invoice-business-legal-name","invoice-business-address",
    "invoice-business-tax-id","invoice-business-tax-office","verge-of-cancellation","verge-of-lateShipment"
]

def normalize_text_table(txt: str) -> str:
    # Normalise fins de ligne
    txt = txt.replace("\r\n", "\n").replace("\r", "\n")
    # Si pas de saut avant un nouvel order-id, en insérer un
    # Pattern order-id Amazon: 3-7-7 chiffres
    txt = re.sub(r'(?<!\n)(\d{3}-\d{7}-\d{7}\t)', r'\n\1', txt)
    # Supprimer NULs ou caractères de contrôle hors tab et newline
    txt = re.sub(r'[^\S\n\t]+', lambda m: m.group(0), txt)  # conserver spaces
    txt = txt.replace('\x00','')
    return txt

def parse_tabular_from_text(txt: str) -> pd.DataFrame:
    lines = txt.split("\n")
    # Trouver la ligne d'en-tête la plus complète
    header_idx = None
    for i, line in enumerate(lines[:5]):
        if line.strip().startswith("order-id"):
            header_idx = i
            break
    if header_idx is None:
        # Parfois l'entête est concaténée après un bout de ligne
        for i, line in enumerate(lines[:20]):
            if "order-id\torder-item-id" in line:
                header_idx = i
                # insérer un saut avant l'entête si collée
                parts = line.split("order-id\torder-item-id", 1)
                if parts[0].strip():
                    lines[i] = parts[0]
                    lines.insert(i+1, "order-id\torder-item-id" + parts[1])
                break
    if header_idx is None:
        raise ValueError("Entête introuvable (order-id ...).")

    header = lines[header_idx].split("\t")
    # Harmoniser sur le set attendu si proche
    if len(header) < len(AMZ_COLS_BASE):
        # Si ça ressemble à l'entête Amazon, utiliser notre liste standard
        if header[0] == "order-id" and header[1] == "order-item-id":
            header = AMZ_COLS_BASE[:]
    cols = header
    data_lines = []
    for j in range(header_idx+1, len(lines)):
        line = lines[j]
        if not line.strip():
            continue
        if line.startswith("order-id\t"):
            # entête dupliquée -> skip
            continue
        # couper proprement en tab
        row = line.split("\t")
        # Si des blocs ont été concaténés sur une même ligne, ne garder que le premier bloc complet
        if len(row) > len(cols):
            row = row[:len(cols)]
        elif len(row) < len(cols):
            row += [""] * (len(cols)-len(row))
        data_lines.append(row)

    df = pd.DataFrame(data_lines, columns=cols)
    return df

def read_table_flex(file_bytes: bytes, filename: str) -> Tuple[pd.DataFrame, Dict]:
    file_bytes = to_bytes(file_bytes)
    ext = (os.path.splitext(filename)[1] or '').lower()
    meta = {'encoding': None, 'sep': None, 'skipped': 0, 'raw_lines': 0, 'header_row': 0, 'parser':'mixed'}

    if ext in [".xlsx", ".xlsm", ".xls"]:
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        meta['parser'] = 'excel'
        # normaliser colonnes
        df.columns = [str(c).strip() for c in df.columns]
        return df, meta

    # Text-like
    txt, enc = smart_decode(file_bytes)
    meta['encoding'] = enc
    txt = normalize_text_table(txt)
    meta['raw_lines'] = txt.count("\n") + 1
    try:
        df = parse_tabular_from_text(txt)
        meta['parser'] = 'txt'
    except Exception as e:
        # fallback csv/tsv
        sniffer = csv.Sniffer()
        dialect = None
        try:
            dialect = sniffer.sniff(txt[:10000], delimiters="\t,;")
        except Exception:
            class D: delimiter = "\t"
            dialect = D()
        reader = csv.reader(io.StringIO(txt), delimiter=getattr(dialect,'delimiter',"\t"))
        rows = list(reader)
        if not rows:
            raise
        cols = rows[0]
        rows = rows[1:]
        norm = []
        for r in rows:
            if len(r) > len(cols):
                r = r[:len(cols)]
            elif len(r) < len(cols):
                r += [""]*(len(cols)-len(r))
            norm.append(r)
        df = pd.DataFrame(norm, columns=cols)
        meta['parser'] = 'csv'
    # Nettoyage colonnes
    df.columns = [str(c).strip() for c in df.columns]
    return df, meta

# ---------- Domain cleaning / mapping ----------
ColMap = Dict[str, str]

def build_cols_map(df: pd.DataFrame) -> ColMap:
    cols_lower = {c.lower(): c for c in df.columns}
    def pick(*names):
        for n in names:
            if n in cols_lower:
                return cols_lower[n]
        return None
    m = {
        'order_id': pick('order-id','order id'),
        'order_item_id': pick('order-item-id','order item id'),
        'product_name': pick('product-name','product name','title'),
        'sku': pick('sku'),
        'asin': pick('asin'),
        'qty': pick('quantity-purchased','qty','quantity'),
        'recipient': pick('recipient-name','recipient','name'),
        'addr1': pick('ship-address-1','address-1'),
        'addr2': pick('ship-address-2','address-2'),
        'addr3': pick('ship-address-3','address-3'),
        'city': pick('ship-city','city'),
        'state': pick('ship-state','state'),
        'postal': pick('ship-postal-code','postal code'),
        'country': pick('ship-country','country'),
        'phone': pick('buyer-phone-number','phone'),
    }
    return m

def clean_str(x: str) -> str:
    return (str(x).replace("\r"," ").replace("\n"," ").strip()) if pd.notna(x) else ""

def product_key(row, m: ColMap) -> str:
    p = clean_str(row.get(m.get('product_name'), ""))
    s = clean_str(row.get(m.get('sku'), ""))
    a = clean_str(row.get(m.get('asin'), ""))
    base = p or s or a or f"Produit {clean_str(row.get(m.get('order_item_id'),''))}"
    return " | ".join([b for b in [p, s, a] if b]) if base else base

def format_address(row, m: ColMap) -> List[str]:
    # Construit les lignes d'adresse (sans téléphone) pour impression, en wrap 25 chars
    parts = [
        clean_str(row.get(m.get('recipient'), "")),
        clean_str(row.get(m.get('addr1'), "")),
        clean_str(row.get(m.get('addr2'), "")),
        clean_str(row.get(m.get('addr3'), "")),
        " ".join([w for w in [clean_str(row.get(m.get('postal'), "")), clean_str(row.get(m.get('city'), ""))] if w]),
        clean_str(row.get(m.get('state'), "")),
        clean_str(row.get(m.get('country'), "")),
    ]
    # enlever vides et doublons successifs
    parts = [p for p in parts if p]
    # wrap à 25 chars par ligne (respect des mots)
    wrapped = []
    for p in parts:
        wrapped.extend(wrap_text(p, width=25))
    # supprimer lignes entièrement vides
    return [l for l in wrapped if l.strip()]

def wrap_text(text: str, width: int = 25) -> List[str]:
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def unique_orders(df: pd.DataFrame, m: ColMap) -> pd.DataFrame:
    # 1 ligne par order-id (garder la première occurrence)
    oid_col = m.get('order_id')
    if not oid_col:
        return df.drop_duplicates()
    # garder colonnes d'adresse
    keep_cols = list({c for c in [
        oid_col, m.get('recipient'), m.get('addr1'), m.get('addr2'), m.get('addr3'),
        m.get('city'), m.get('state'), m.get('postal'), m.get('country')
    ] if c})
    # Trier pour cohérence (par date si dispo sinon par order-id)
    df2 = df.copy()
    if 'purchase-date' in df2.columns:
        df2 = df2.sort_values('purchase-date')
    dfu = df2.drop_duplicates(subset=[oid_col], keep='first')
    return dfu[keep_cols]

# ---------- PDF ----------
@dataclass
class PdfLayout:
    margin_left: float = 15 * mm
    margin_top: float = 15 * mm
    cols: int = 2
    rows: int = 4
    col_gap: float = 8 * mm
    row_gap: float = 6 * mm
    cell_w: float = (A4[0] - 2*15*mm - 8*mm) / 2
    cell_h: float = (A4[1] - 2*15*mm - 6*mm*3) / 4

def generate_labels_pdf(df_orders: pd.DataFrame, m: ColMap, out_path="etiquettes.pdf", logo_bytes: Optional[bytes]=None) -> Tuple[str, int]:
    c = canvas.Canvas(out_path, pagesize=A4)
    layout = PdfLayout()
    logo = None
    if logo_bytes:
        try:
            logo = ImageReader(io.BytesIO(logo_bytes))
        except Exception:
            logo = None

    n = 0
    for idx, row in df_orders.iterrows():
        page_idx = n // (layout.cols * layout.rows)
        pos_in_page = n % (layout.cols * layout.rows)
        col = pos_in_page % layout.cols
        rw = pos_in_page // layout.cols
        x = layout.margin_left + col * (layout.cell_w + layout.col_gap)
        y = A4[1] - layout.margin_top - (rw+1)*layout.cell_h - rw*layout.row_gap

        # Cadre optionnel (léger repère)
        # c.rect(x, y, layout.cell_w, layout.cell_h, stroke=0, fill=0)

        # Logo (si présent)
        if logo:
            try:
                lw = 18*mm
                lh = 18*mm
                c.drawImage(logo, x + layout.cell_w - lw, y + layout.cell_h - lh, width=lw, height=lh, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        # Adresse — gras et plus grand, pas de produit, pas d'order-id
        addr_lines = format_address(row, m)
        # Taille de base plus grande
        font_name = "Helvetica-Bold"
        font_size = 12  # plus grand que standard
        c.setFont(font_name, font_size)
        # Interligne
        leading = font_size + 2

        # Dessin des lignes (du haut vers le bas)
        text_obj = c.beginText()
        text_obj.setTextOrigin(x + 8, y + layout.cell_h - 24)  # petites marges internes
        text_obj.setLeading(leading)
        for ln in addr_lines:
            text_obj.textLine(ln)
        c.drawText(text_obj)

        n += 1
        if n % (layout.cols*layout.rows) == 0:
            c.showPage()

    if n % (layout.cols*layout.rows) != 0:
        c.showPage()
    c.save()
    return out_path, n

# ---------- Grouping and checkboxes ----------
def build_group_key(row, m: ColMap) -> str:
    # clé pour regrouper produits similaires
    parts = []
    p = clean_str(row.get(m.get('product_name'), "")) or ""
    s = clean_str(row.get(m.get('sku'), "")) or ""
    a = clean_str(row.get(m.get('asin'), "")) or ""
    if p: parts.append(p)
    if s: parts.append(s)
    if a: parts.append(a)
    if not parts:
        parts = [f"Produit {clean_str(row.get(m.get('order_item_id'),''))}"]
    return " | ".join(parts)

def summarize_groups(df: pd.DataFrame, m: ColMap) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['_group','count'])
    tmp = df.copy()
    tmp['_group'] = tmp.apply(lambda r: build_group_key(r, m), axis=1)
    # Compter commandes uniques par groupe (pas items)
    oid = m.get('order_id')
    if oid and oid in tmp.columns:
        grp = tmp.groupby('_group')[oid].nunique().reset_index().rename(columns={oid:'count'})
    else:
        grp = tmp.groupby('_group').size().reset_index(name='count')
    grp = grp.sort_values(['count','_group'], ascending=[False, True])
    return grp

# ---------- Global state ----------
df_raw_global: Optional[pd.DataFrame] = None
cols_map_global: Optional[ColMap] = None
logo_bytes_global: Optional[bytes] = None
checkboxes: List[Checkbox] = []
groups_box = VBox()
groups_bar = HBox(layout=Layout(gap="8px"))
stats_html = HTML()
export_out = Output()

def render_stats(df_raw: pd.DataFrame, df_orders_unique: pd.DataFrame, m: ColMap, groups_df: pd.DataFrame):
    total_lines = len(df_raw)
    total_valid = len(df_raw.dropna(how='all'))
    oid = m.get('order_id')
    nb_cmd = df_raw[oid].nunique() if oid and oid in df_raw.columns else total_valid
    nb_items = len(df_raw)
    # pays
    country_col = m.get('country')
    country_counts = {}
    if country_col and country_col in df_orders_unique.columns:
        country_counts = df_orders_unique[country_col].value_counts().to_dict()
    countries_str = ", ".join(f"{k}:{v}" for k,v in country_counts.items()) if country_counts else "—"
    stats_html.value = f"""
    <div style="font-family:system-ui,Segoe UI,Roboto,Arial;line-height:1.35">
      <div style="margin:2px 0"><b>Lignes (brutes):</b> {total_lines}</div>
      <div style="margin:2px 0"><b>Items:</b> {nb_items}</div>
      <div style="margin:2px 0"><b>Commandes uniques:</b> {nb_cmd}</div>
      <div style="margin:2px 0"><b>Commandes (sélection) pour PDF:</b> {len(df_orders_unique)}</div>
      <div style="margin:2px 0"><b>Par pays:</b> {countries_str}</div>
    </div>
    """

def refresh_groups_ui(df: pd.DataFrame, m: ColMap):
    global checkboxes
    checkboxes = []
    grp = summarize_groups(df, m)
    if grp.empty:
        groups_box.children = [HTML("<i>Aucun produit détecté.</i>")]
        return
    items = []
    for _, r in grp.iterrows():
        label = f"[{int(r['count'])}] {r['_group']}"
        cb = Checkbox(value=True, description=label, indent=False, layout=Layout(width="100%"))
        items.append(cb)
        checkboxes.append(cb)
    groups_box.children = items

def apply_selection(df: pd.DataFrame, m: ColMap) -> pd.DataFrame:
    if not checkboxes:
        return df
    # déterminer groupes cochés
    enabled = set()
    for cb in checkboxes:
        if cb.value:
            # enlever "[N] " du début
            label = cb.description
            gname = re.sub(r'^\[\d+\]\s*', '', label)
            enabled.add(gname)
    tmp = df.copy()
    tmp['_group'] = tmp.apply(lambda r: build_group_key(r, m), axis=1)
    tmp = tmp[tmp['_group'].isin(enabled)]
    # réduire à 1 par commande
    df_orders = unique_orders(tmp, m)
    return df_orders

# ---------- Widgets factory (to allow full RESET) ----------
def make_widgets():
    title = HTML("""<div style="font-family:Inter,system-ui,Segoe UI,Roboto,Arial">
        <div style="font-size:22px;font-weight:700;color:#0b3954">Osmoz <span style="color:#1273de">1.17</span></div>
        <div style="color:#444">Import Amazon + Étiquettes PDF</div>
    </div>""")
    hint = HTML("""<div style="background:#f6f9fe;border:1px solid #d6e4ff;border-radius:8px;padding:8px 10px;font-size:12.5px;color:#1f3b57">
        1) Déposez l’export Amazon (.txt/.csv/.tsv/.xlsx). 2) Cliquez <b>Charger les données</b>.
        3) Cochez les produits (groupés). 4) Cliquez <b>Générer le PDF</b>.
    </div>""")
    uploader = FileUpload(accept=".txt,.csv,.tsv,.xlsx", multiple=False, description="Fichier Amazon", layout=Layout(width="60%"))
    uploader_logo = FileUpload(accept=".png,.jpg,.jpeg", multiple=False, description="Logo (option)", layout=Layout(width="38%"))
    btn_load = Button(description="Charger les données", button_style="primary", layout=Layout(width="50%"))
    btn_pdf = Button(description="Générer le PDF", layout=Layout(width="48%"))
    btn_reset = Button(description="RESET", button_style="danger", layout=Layout(width="48%"))
    return title, hint, uploader, uploader_logo, btn_load, btn_pdf, btn_reset

# ---------- Upload helpers ----------
def get_first_upload(fu: FileUpload) -> Optional[Tuple[bytes, str]]:
    v = fu.value
    if not v:
        return None
    # ipywidgets 8.x: tuple/list d'UploadedFile
    if isinstance(v, (tuple, list)):
        up = v[0]
        content = getattr(up, "content", None)
        name = getattr(up, "name", None)
        # compat dict-like
        if content is None and isinstance(up, dict):
            content = up.get('content')
            name = up.get('name') or up.get('metadata', {}).get('name')
        return (to_bytes(content), name or "upload.bin")
    # ipywidgets 7.x: dict
    if isinstance(v, dict):
        up = next(iter(v.values()))
        content = up.get('content')
        name = up.get('metadata', {}).get('name') or up.get('name') or "upload.bin"
        return (to_bytes(content), name)
    return None

def load_logo_from_uploader(uploader_logo: FileUpload) -> Optional[bytes]:
    up = get_first_upload(uploader_logo)
    if not up:
        return None
    content, _ = up
    return to_bytes(content) if content is not None else None

# ---------- Actions ----------
def build_interface():
    global df_raw_global, cols_map_global, logo_bytes_global
    global groups_box, groups_bar, stats_html, export_out

    # reset state
    df_raw_global = None
    cols_map_global = None
    logo_bytes_global = None

    title, hint, uploader, uploader_logo, btn_load, btn_pdf, btn_reset = make_widgets()
    stats_html = HTML()
    groups_box = VBox()
    groups_bar = HBox(layout=Layout(gap="8px"))
    export_out = Output()

    # top bar actions
    groups_bar.children = [
        btn_pdf,
        btn_reset,
    ]

    # callbacks
    def action_load_clicked(_):
        nonlocal uploader, uploader_logo
        try:
            up = get_first_upload(uploader)
            if not up:
                with log: print("Aucun fichier importé.")
                return
            (file_bytes, filename) = up
            with log: print(f"Chargement: {filename}")
            df, meta = read_table_flex(file_bytes, filename)
            # Mapping colonnes
            m = build_cols_map(df)
            # Filtrer lignes vides order-id
            oid = m.get('order_id')
            if oid and oid in df.columns:
                df = df[df[oid].astype(str).str.match(r'^\d{3}-\d{7}-\d{7}$', na=False)]
            # Nettoyage basique adresses (espaces multiples)
            for k in ['recipient','addr1','addr2','addr3','city','state','postal','country','product_name','sku']:
                col = m.get(k)
                if col and col in df.columns:
                    df[col] = df[col].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()

            # Sauvegarde globales
            logo = load_logo_from_uploader(uploader_logo)
            global df_raw_global, cols_map_global, logo_bytes_global
            df_raw_global = df.reset_index(drop=True)
            cols_map_global = m
            logo_bytes_global = logo

            # Rafraîchir UI
            refresh_groups_ui(df_raw_global, cols_map_global)
            # Par défaut, si tout coché, évaluer sélection -> commandes uniques
            df_sel = apply_selection(df_raw_global, cols_map_global)
            render_stats(df_raw_global, df_sel, cols_map_global, None)
            with log:
                print("Import terminé. Groupes produits générés.")
        except Exception as e:
            with log:
                print("Erreur chargement:", e)
                traceback.print_exc()

    def action_pdf_clicked(_):
        try:
            if df_raw_global is None or cols_map_global is None:
                with log: print("Importez d’abord un fichier, puis cliquez sur Charger les données.")
                return
            df_sel_orders = apply_selection(df_raw_global, cols_map_global)
            if df_sel_orders.empty:
                with log: print("Aucun résultat: vérifiez les cases cochées.")
                return
            out_path, n = generate_labels_pdf(df_sel_orders, cols_map_global, out_path="etiquettes.pdf", logo_bytes=logo_bytes_global)
            with export_out:
                clear_output(wait=True)
                display(HTML(f"<div style='margin:6px 0 8px 0;'>PDF généré: <b>{out_path}</b> — {n} étiquette(s).</div>"))
                try:
                    display(FileLink(out_path))
                except Exception:
                    pass
            with log:
                print("PDF généré avec succès.")
            # Mettre à jour stats (nombre de commandes pour la sélection)
            render_stats(df_raw_global, df_sel_orders, cols_map_global, None)
        except Exception as e:
            with log:
                print("Erreur génération PDF:", e)
                traceback.print_exc()

    def action_reset_clicked(_):
        # Réinitialiser totalement l'interface et l'état
        global df_raw_global, cols_map_global, logo_bytes_global
        df_raw_global = None
        cols_map_global = None
        logo_bytes_global = None
        with export_out:
            clear_output(wait=True)
        with log:
            clear_output(wait=True)
            print("Interface réinitialisée.")
        # reconstruire complètement l'UI
        build_interface()

    btn_load.on_click(action_load_clicked)
    btn_pdf.on_click(action_pdf_clicked)
    btn_reset.on_click(action_reset_clicked)

    # ---------- Layout ----------
    left_col = VBox([
        HTML("<h4 style='margin:10px 0 6px 0;'>Import</h4>"),
        HBox([uploader, uploader_logo], layout=Layout(gap="8px")),
        HBox([btn_load], layout=Layout(margin="8px 0", gap="8px")),
        HTML("<h4 style='margin:10px 0 6px 0;'>Statistiques</h4>"),
        stats_html,
        HTML("<h4 style='margin:12px 0 6px 0;'>Résultat</h4>"),
        export_out,
    ], layout=Layout(width="46%"))

    right_col = VBox([
        HTML("<h4 style='margin:10px 0 6px 0;'>Sélection des produits</h4>"),
        groups_bar,
        HTML("<div style='max-height:360px;overflow:auto;border:1px solid #eee;border-radius:6px;padding:6px;background:#fff'>"),
        groups_box,
        HTML("</div>"),
        HTML("<h4 style='margin:12px 0 6px 0;'>Journal</h4>"),
        log
    ], layout=Layout(width="52%"))

    app_box.children = [
        title,
        hint,
        HBox([left_col, right_col], layout=Layout(justify_content="space-between", gap="16px"))
    ]

# build and display UI
build_interface()
display(app_box)
with log:
    print("Interface prête. 1) Déposez l’export. 2) Cliquez “Charger les données”. 3) Cochez les produits. 4) Cliquez “Générer le PDF”.")


# In[ ]:




