# -*- coding: utf-8 -*-
"""
Pharmacy Parser — Streamlit — v32
- Fix: إزالة تكرار اسم الصنف تلقائيًا (dedupe).
- يبقي على تعديلات v31: Co-payment -> نسبة التحمل، رأس العمود N، شريط التقدّم، اختيار مجلد الحفظ Topmost، تنظيف الأسماء، دعم ملفات متعددة وإيصالات متعددة داخل PDF واحد، إلخ.
"""

import io, os, re, json, unicodedata, platform, time
import streamlit as st
import pdfplumber, fitz
import pandas as pd
from PIL import Image, ImageDraw
from datetime import datetime
from typing import List, Dict, Any, Tuple

# PDF
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Arabic
import arabic_reshaper
from bidi.algorithm import get_display

# --------- ثابتات ---------
PHARMACY = {"name": "صيدلية مصر", "address": "مدينه السادات - المنوفية", "phone": "01552462008"}
RIGHT_NOTE = "212811126"
LEFT_NOTE  = "8143"

st.set_page_config(page_title="صيدلية مصر — Nice Deer Receipt", layout="wide")

# --------- CSS ----------
st.markdown("""
<style>
.header-card{padding:14px;border-radius:16px;background:linear-gradient(135deg,#0ea5e9,#22d3ee);color:white;}
.header-title{margin:0;text-align:center;font-size:28px;letter-spacing:.5px;font-weight:800;}
.header-sub{margin-top:6px;text-align:center;font-size:16px;font-weight:600;}
.header-note{margin-top:4px;text-align:center;font-size:18px;font-weight:800}
.start-wrap{display:flex;justify-content:center;margin:12px 0;}
.start-wrap .stButton>button {background:#0ea5e9;color:#fff;border:0;
  padding:14px 48px;font-size:22px;font-weight:800;border-radius:12px;box-shadow:0 4px 16px rgba(0,0,0,.18);}
.start-wrap .stButton>button:hover{filter:brightness(1.05);}
</style>
""", unsafe_allow_html=True)

# --------- خطوط عربية ----------
def register_arabic_fonts() -> Tuple[str, str]:
    normal_candidates = [
        "Amiri-Regular.ttf", "Cairo-Regular.ttf", "NotoNaskhArabic-Regular.ttf",
        r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\times.ttf",
        r"C:\Windows\Fonts\DejaVuSans.ttf",
    ]
    bold_candidates = [
        "Amiri-Bold.ttf", "Cairo-Bold.ttf", "NotoNaskhArabic-Bold.ttf",
        r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\tahomabd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\timesbd.ttf",
        r"C:\Windows\Fonts\DejaVuSans-Bold.ttf",
    ]
    normal_name = "ArabicUI"; bold_name = "ArabicUIB"
    ok_normal = ok_bold = False
    for p in normal_candidates:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(normal_name, p))
                ok_normal = True
                break
            except Exception:
                pass
    for p in bold_candidates:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(bold_name, p))
                ok_bold = True
                break
            except Exception:
                pass
    if not ok_normal:
        normal_name = "Helvetica"
    if not ok_bold:
        bold_name = normal_name
    return normal_name, bold_name

AR_FONT_NAME, AR_FONT_BOLD = register_arabic_fonts()

# --------- Regex / Helpers ----------
AR_RE     = re.compile(r"[\u0600-\u06FF]")
FLOAT_ONLY_RX = re.compile(r"^\d+(?:\.\d+)?$")
ANY_NUM_RX    = re.compile(r"\d+(?:[\.,]\d+)?")
QTY_RX    = re.compile(r"\d+(?:\.\d+)?\s*/\s*[A-Za-z\u0621-\u064A\.\-]+")
STOP_RX   = re.compile(r"^(No\.?\s*Of\s*Items|Gross\s*Amount|Net\s*Amount|Approved\s*Items|Beneficiary\s*Dues|Insurance\s*Co\.)", re.I)
SI_RX     = re.compile(r"^\s*Special\s*instructions?\s*:?\s*$", re.I)
PN_RX     = re.compile(r"^\s*Provider\s*Notes?\s*:?\s*$", re.I)
STATUS_WORD_RX = re.compile(r"^(Approved|Deleted|Rejected|Denied|Pending|Returned|Dispensed|Cancelled|Cancel(l)?ed|Excluded)$", re.I)
DIAG_RX   = re.compile(r"^(Type\s*\d+\s*Diabetes|Diabetes\s*Mellitus|Peptic\s+Ulcer|Antihyperlipidemic|Antiarteriosclerotic|With\s+Unspecified\s+Complications|Unspe?cified)\b", re.I)

HDR_RX = {
    "receipt_no":   re.compile(r"(?:Receipt|Reciept)\s*#\s*([0-9]+)", re.I),
    "beneficiary":  re.compile(r"Beneficiary\s*Name\s*:\s*([^\r\n]+)", re.I),
    "dispensed_date": re.compile(r"Dispensed\s*Date\s*:\s*([0-9]{1,2}[/\-][0-9]{1,2}[/\-][0-9]{2,4})", re.I),
    "printed_on":   re.compile(r"Printed\s*On\s*:\s*([0-9]{1,2}[/\-][0-9]{1,2}[/\-][0-9]{2,4})", re.I),
    "gross_amount": re.compile(r"Gross\s*Amount\s*:\s*([0-9.,]+)\s*EGP?", re.I),
    "net_amount":   re.compile(r"(?:Net\s*Amount|Net)\s*:\s*([0-9.,]+)\s*EGP?", re.I),
    "copayment":    re.compile(r"Co[-\s]?payment\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*%", re.I),
}

# --------- تنظيف اسم الصنف + إزالة التكرار ----------
REMOVALS = [
    "(New)","5mg5mg","(SPORITAXIME)","EVA PHARMA","(Or.)","25mg/100mg","25mg300mg","(Delayed Re.)",
    "(imported)","Containing Powder For Solution","Iv-Infu","-ADCO","(3strips)","(Sugr Freevit.C)","(Epico)",
    "120mg5mg","Oral Fast Dissolving","(60ml)","25mg100mg","Scored F.C.","200mg/5ml","1000µ/1ml","Dual Release",
    "ORODISPERSIBLE","Inhalation","ENTERIC COATED","LOCAL","100u/Ml 3mlx","MAX E.C.","(250mg200mg)","15mg/1.5ml",
    "100u/Ml 10ml","(Delay Re.)","Orodispersible","Sublingual","30mg/2ml Im/Iv","(Sugar-Free)","100u/Ml 3mlx",
    "Enteric C.","27.5µ 120dose","(Pain Reliev.)","Scor.F.C.","(Organop.)","Scored F.C.","(Glyceryl Trinitrate)",
    "50mcg/Ml 3ml","30mg/2ml","Baby Nappy","(Ex.New)","100u/Ml3ml","300iu/Ml 1.5mlx","100u/Ml3ml","(Mylan)"
]
def _build_clean_patterns() -> List[re.Pattern]:
    pats: List[re.Pattern] = []
    for token in REMOVALS:
        bare = token.strip().strip("()").strip()
        if not bare: continue
        esc_bare = re.escape(bare); esc_tok = re.escape(token.strip())
        pats.append(re.compile(rf"\s*\(\s*{esc_bare}\s*\)\s*", re.I))
        pats.append(re.compile(rf"\s*{esc_tok}\s*", re.I))
        flexible = re.sub(r"\s+", r"\\s+", esc_bare)
        pats.append(re.compile(rf"(?i)(?<!\w){flexible}(?!\w)"))
    pats.append(re.compile(r"\(\s*\)"))
    return pats
_CLEAN_PATS = _build_clean_patterns()

def clean_item_name(s: str) -> str:
    if not s: return s
    for rx in _CLEAN_PATS: s = rx.sub(" ", s)
    s = re.sub(r"\s{2,}", " ", s)
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\s*/\s*", "/", s)
    return s.strip(" -/")

def dedupe_repeated_name(s: str) -> str:
    """يحذف تكرار الاسم لو كان النص كله مكرر مرتين أو لو ذيل الاسم مكرر."""
    if not s: return s
    s = re.sub(r"\s+", " ", s).strip()

    # النص كله مكرر مرتين
    m = re.match(r"^(?P<p>.+?)\s+\1$", s, flags=re.IGNORECASE)
    if m:
        return m.group("p").strip()

    # نصف أول = نصف ثانٍ
    toks = s.split()
    n = len(toks)
    if n >= 4 and n % 2 == 0 and toks[: n // 2] == toks[n // 2 :]:
        return " ".join(toks[: n // 2])

    # ذيل مكرر
    for k in range(n // 2, 2, -1):
        if toks[-k:] == toks[-2 * k : -k]:
            return " ".join(toks[:-k]).strip()

    return s

# --------- عربي (Excel/PDF) ----------
def _remove_bidi_and_zw(s: str) -> str:
    return re.sub(r"[\u200c\u200d\u200e\u200f\u061c\u202a-\u202e\u2066-\u2069\u0640]", "", s or "")

def _normalize_ar_logical(raw: str) -> str:
    if not raw: return ""
    txt = raw.replace('"', ' ').replace("'", " ")
    txt = re.sub(r"\s+", " ", txt).strip(" :-/")
    if "/" in txt:
        left, right = txt.split("/", 1)
        if left.strip().isdigit(): txt = right.strip()
    m = re.match(r"^\d{6,}\s+(.+)$", txt)
    if m: txt = m.group(1).strip()
    txt = _remove_bidi_and_zw(txt)
    txt = unicodedata.normalize("NFKC", txt)
    toks = txt.split()
    ar_toks = [t for t in toks if AR_RE.search(t)]
    if ar_toks:
        rev_ratio = sum(1 for t in ar_toks if (t==t[::-1])) / max(1, len(ar_toks))
        if rev_ratio >= 0.4:
            toks = [t[::-1] if AR_RE.search(t) else t for t in toks]
    txt = " ".join(toks)
    return re.sub(r"\s+", " ", txt).strip()

def ar_visual_for_pdf(s: str) -> str:
    try: return get_display(arabic_reshaper.reshape(_remove_bidi_and_zw(s or "")))
    except Exception: return s or ""

def ar_visual_for_excel(s: str) -> str:
    try: return get_display(arabic_reshaper.reshape(s or ""))
    except Exception: return s or ""

def parse_date_iso(s: str) -> str:
    s = (s or "").strip()
    for fmt in ("%d/%m/%Y","%d-%m-%Y","%Y/%m/%d","%Y-%m-%d","%d/%m/%y","%d-%m-%y"):
        try: return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except: pass
    s2 = re.sub(r"[^0-9/\-]","", s)
    for fmt in ("%d/%m/%Y","%d-%m-%Y","%Y/%m/%d","%Y-%m-%d"):
        try: return datetime.strptime(s2, fmt).strftime("%Y-%m-%d")
        except: pass
    return datetime.now().strftime("%Y-%m-%d")

def detect_company(text: str) -> str:
    t = " ".join([ln.strip() for ln in (text or "").splitlines()[:8]])
    tl = t.lower()
    if "misr health care" in tl: return "Misr Health Care"
    if re.search(r"\bAMC\b", t):  return "Al Ahly Medical Company - AMC"
    if re.search(r"\bBM\b", t):   return "Banque Misr"
    if re.search(r"\bInaya\b", t, re.I): return "Inaya Misr"
    if re.search(r"\bMedSure\b", t, re.I): return "MedSure"
    return ""

def parse_header(text: str) -> Dict[str,str]:
    d = {k:"" for k in ("receipt_no","patient_id","patient_name_excel","patient_name_pdf","date","total_gross","company","copayment")}
    d["company"] = detect_company(text or "")
    m = HDR_RX["receipt_no"].search(text or ""); d["receipt_no"]=m.group(1) if m else ""
    b = HDR_RX["beneficiary"].search(text or "")
    if b:
        raw = b.group(1).strip()
        if "/" in raw:
            left, right = raw.split("/",1); pid = re.sub(r"\D","", left); name = right
        else:
            mm = re.match(r"^(\d{6,})\s+(.+)$", raw); pid, name = (mm.group(1), mm.group(2)) if mm else ("", raw)
        d["patient_id"] = pid
        logical = _normalize_ar_logical(name)
        d["patient_name_excel"] = ar_visual_for_excel(logical)
        d["patient_name_pdf"]   = ar_visual_for_pdf(logical)
    dt = HDR_RX["dispensed_date"].search(text or "") or HDR_RX["printed_on"].search(text or "")
    d["date"] = parse_date_iso(dt.group(1)) if dt else datetime.now().strftime("%Y-%m-%d")
    g = HDR_RX["gross_amount"].search(text or ""); n = HDR_RX["net_amount"].search(text or "")
    d["total_gross"] = (g.group(1) if g else (n.group(1) if n else "")).strip()
    cp = HDR_RX["copayment"].search(text or "")
    if cp:
        v = cp.group(1)
        try: d["copayment"] = f"{int(round(float(v)))}%"
        except: d["copayment"] = v.strip()+"%"
    return d

# --------- جدول ----------
def _group_lines(words: List[Dict]) -> List[List[Dict]]:
    lines: List[List[Dict]] = []
    for w in words:
        if not lines or abs(lines[-1][0]["top"] - w["top"]) > 2.2:
            lines.append([w])
        else:
            lines[-1].append(w)
    for i in range(len(lines)):
        lines[i] = sorted(lines[i], key=lambda w: w["x0"])
    return lines

def detect_table_region_by_text(page: pdfplumber.page.Page) -> Tuple[float,float]:
    top_y = 0.0; bottom_y = page.height
    words = page.extract_words(use_text_flow=True, x_tolerance=1, y_tolerance=3)
    lines = []
    for w in sorted(words, key=lambda x: (x["top"], x["x0"])):
        if not lines or abs(lines[-1][0]["top"] - w["top"]) > 2.2:
            lines.append([w])
        else:
            lines[-1].append(w)
    for ln in lines:
        text = " ".join([w["text"].lower().strip(":") for w in ln])
        if ("qty" in text and "name" in text and "unit" in text):
            top_y = min(w["top"] for w in ln) + 6.0; break
    for ln in lines:
        joined = " ".join(w["text"] for w in ln)
        if STOP_RX.match(joined):
            bottom_y = min(w["top"] for w in ln) - 2.0; break
    return max(0.0, top_y), min(page.height, bottom_y)

def detect_row_bands_by_lines(page: pdfplumber.page.Page, region: Tuple[float,float]) -> List[Tuple[float,float]]:
    y_top, y_bottom = region
    try: lines = page.objects.get("lines", [])
    except: lines = []
    good = []; min_width = page.width * 0.55
    for ln in lines:
        x0,x1,y0,y1 = ln.get("x0",0), ln.get("x1",0), ln.get("y0",0), ln.get("y1",0)
        if abs(y1 - y0) <= 0.7 and (x1 - x0) >= min_width and y_top <= y0 <= y_bottom:
            good.append(y0)
    if len(good) < 2: return []
    good = sorted(good); merged = []; tol = 2.0
    for y in good:
        if not merged or abs(merged[-1] - y) > tol: merged.append(y)
    bands = []
    for i in range(len(merged)-1):
        y0,y1 = merged[i], merged[i+1]
        if (y1 - y0) >= 8.0: bands.append((y0, y1))
    return bands

def is_dose_fragment(token: str) -> bool:
    t = token.strip().lower()
    return ("mg" in t or "tab" in t or "caps" in t or "cap." in t or "susp" in t
            or "/" in t or "-" in t or "f.c.tab" in t or "scor.tab" in t)

def assign_to_columns(words: List[Dict],
                      bounds: Dict[str,Tuple[float,float]],
                      name_span: Tuple[float,float]) -> Dict[str,str]:
    cols = {k: "" for k in ("qty","icd","name","unit","status")}
    centers = {k: (v[0]+v[1])/2.0 for k,v in bounds.items()}
    qty_r, name_right_cap = name_span
    unit_l = bounds["unit"][0]
    status_l = bounds["status"][0]

    def smart_add(dst: str, token: str) -> str:
        token = token.strip()
        if not token: return dst
        if not dst: return token
        if AR_RE.search(dst[-1]) and AR_RE.search(token[0]) and len(token) <= 2:
            return dst + token
        return (dst + " " + token).strip()

    def add_status(token: str):
        t = token.strip()
        if STATUS_WORD_RX.match(t): return smart_add(cols["status"], t)
        if FLOAT_ONLY_RX.match(t) or ANY_NUM_RX.search(t) or t.upper()=="EGP": return cols["status"]
        if re.match(r"^[A-Za-z]+\.?$", t): return smart_add(cols["status"], t)
        return cols["status"]

    for w in words:
        cx = (w["x0"] + w["x1"]) / 2.0
        text = w["text"].strip()
        placed = False
        for col,(l,r) in bounds.items():
            if l <= cx <= r:
                if col == "name":
                    if FLOAT_ONLY_RX.match(text) and cx >= unit_l - 2 and not is_dose_fragment(text):
                        cols["unit"] = smart_add(cols["unit"], text)
                    else:
                        cols["name"] = smart_add(cols["name"], text)
                elif col == "status":
                    cols["status"] = add_status(text)
                else:
                    cols[col] = smart_add(cols[col], text)
                placed = True; break
        if placed: continue

        if qty_r <= cx <= name_right_cap:
            if FLOAT_ONLY_RX.match(text) and not is_dose_fragment(text):
                cols["unit"] = smart_add(cols["unit"], text)
            else:
                cols["name"] = smart_add(cols["name"], text)
            continue

        if unit_l <= cx < status_l:
            continue

        nearest = min(centers.items(), key=lambda kv: abs(cx - kv[1]))[0]
        if nearest == "status":
            cols["status"] = add_status(text)
        elif nearest == "name" and FLOAT_ONLY_RX.match(text) and not is_dose_fragment(text) and cx > unit_l - 2:
            cols["unit"] = smart_add(cols["unit"], text)
        else:
            cols[nearest] = smart_add(cols[nearest], text)
    return cols

def _ingest_cols(cur: Dict[str,Any], cols: Dict[str,str], allow_fallback: bool):
    qcell = (cols.get("qty") or "").strip()
    if qcell:
        if QTY_RX.fullmatch(qcell.replace(" ", "")):
            cur["qty"] = qcell.replace(" ", ""); cur["qty_parts"] = []
        else:
            cur["qty_parts"] = cur.get("qty_parts", []); cur["qty_parts"].append(qcell)
    nm  = (cols.get("name") or "").strip()
    icd = (cols.get("icd")  or "").strip()
    if allow_fallback and icd and not DIAG_RX.match(icd):
        nm = (icd + (" " + nm if nm else "")).strip()
    if nm and not (SI_RX.match(nm) or PN_RX.match(nm)):
        cur["name_parts"] = cur.get("name_parts", []); cur["name_parts"].append(nm)
    if cols.get("unit"):
        m = re.search(r"\d+(?:\.\d+)?", cols["unit"])
        if m: cur["unit"] = m.group(0)
    if cols.get("status"):
        cur["status"] = cols["status"].strip()

def _merge_pre_into_cur(cur: Dict[str,Any], pre: Dict[str,Any]):
    if pre.get("name_parts"): cur["name_parts"] = cur.get("name_parts", []) + pre["name_parts"]
    if pre.get("unit") and not cur.get("unit"): cur["unit"] = pre["unit"]
    if pre.get("status") and not cur.get("status"): cur["status"] = pre["status"]

def _finish_cur(cur: Dict[str,Any], dispensed_date: str) -> Dict[str,Any] | None:
    qty = cur.get("qty") or ("".join(cur.get("qty_parts",[])).replace(" ", ""))
    name = " ".join([s for s in cur.get("name_parts",[]) if s]).strip()
    unit = (cur.get("unit","") or "").strip()
    status = (cur.get("status","") or "").strip()
    if qty and name and unit and status and QTY_RX.fullmatch(qty):
        return {"qty":qty, "name":name, "unit":unit, "status":status, "dispensed_date":dispensed_date}
    return None

def parse_items_by_bands(page, col_bounds, row_bands, dispensed_date, allow_fallback=True):
    words = page.extract_words(use_text_flow=True, x_tolerance=1, y_tolerance=3)
    buckets = [[] for _ in row_bands]
    for w in words:
        cy = (w["top"] + w["bottom"]) / 2.0
        for i,(y0,y1) in enumerate(row_bands):
            if y0 <= cy <= y1: buckets[i].append(w); break
    items = []
    qty_r = col_bounds["qty"][1]
    name_right_cap = min(col_bounds["name"][1], col_bounds["unit"][0] - 10.0)
    for row_words in buckets:
        if not row_words: continue
        if SI_RX.match(" ".join(ww["text"] for ww in row_words)) or PN_RX.match(" ".join(ww["text"] for ww in row_words)):
            continue
        pre = {"name_parts":[], "unit":"", "status":""}
        cur = {"qty":"", "qty_parts":[], "name_parts":[], "unit":"", "status":""}
        seen_qty = False
        for ln in _group_lines(row_words):
            cols = assign_to_columns(ln, col_bounds, (qty_r, name_right_cap))
            qcell = (cols.get("qty") or "").replace(" ", "")
            if not seen_qty and not (qcell and QTY_RX.fullmatch(qcell)):
                _ingest_cols(pre, cols, allow_fallback);  continue
            if qcell and QTY_RX.fullmatch(qcell) and not seen_qty:
                seen_qty = True; _merge_pre_into_cur(cur, pre)
            if qcell and QTY_RX.fullmatch(qcell) and cur.get("qty"):
                maybe = _finish_cur(cur, dispensed_date)
                if maybe: items.append(maybe)
                cur = {"qty":"", "qty_parts":[], "name_parts":[], "unit":"", "status":""}
            _ingest_cols(cur, cols, allow_fallback)
        maybe = _finish_cur(cur, dispensed_date)
        if maybe: items.append(maybe)
    return items

def parse_items_by_signals(page, col_bounds, dispensed_date, region, allow_fallback=True):
    y_top, y_bottom = region
    words_all = page.extract_words(use_text_flow=True, x_tolerance=1, y_tolerance=3)
    words = [w for w in words_all if y_top <= ((w["top"]+w["bottom"])/2.0) <= y_bottom]
    lines = _group_lines(sorted(words, key=lambda x: (x["top"], x["x0"])))
    items = []
    pre = {"name_parts":[], "unit":"", "status":""}
    cur = {"qty":"", "qty_parts":[], "name_parts":[], "unit":"", "status":""}
    started = False
    qty_r = col_bounds["qty"][1]
    name_right_cap = min(col_bounds["name"][1], col_bounds["unit"][0] - 10.0)
    for ln in lines:
        raw = " ".join([w["text"] for w in ln]).strip()
        if STOP_RX.match(raw):
            maybe = _finish_cur(cur, dispensed_date)
            if maybe: items.append(maybe); break
        if SI_RX.match(raw) or PN_RX.match(raw):
            maybe = _finish_cur(cur, dispensed_date)
            if maybe: items.append(maybe)
            pre = {"name_parts":[], "unit":"", "status":""}
            cur = {"qty":"", "qty_parts":[], "name_parts":[], "unit":"", "status":""}
            started = False; continue
        cols = assign_to_columns(ln, col_bounds, (qty_r, name_right_cap))
        qcell = (cols.get("qty") or "").replace(" ", "")
        if not started:
            if qcell and QTY_RX.fullmatch(qcell):
                started = True; _merge_pre_into_cur(cur, pre); _ingest_cols(cur, cols, allow_fallback)
            else:
                _ingest_cols(pre, cols, allow_fallback); continue
        else:
            if qcell and QTY_RX.fullmatch(qcell) and cur.get("qty"):
                maybe = _finish_cur(cur, dispensed_date)
                if maybe: items.append(maybe)
                cur = {"qty":"", "qty_parts":[], "name_parts":[], "unit":"", "status":""}
                pre = {"name_parts":[], "unit":"", "status":""}
        _ingest_cols(cur, cols, allow_fallback)
    maybe = _finish_cur(cur, dispensed_date)
    if maybe: items.append(maybe)
    return items

# --------- Preview helper ----------
def draw_preview(pdf_bytes: bytes, col_b: Dict[str,Tuple[float,float]], row_bands: List[Tuple[float,float]]):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    p = doc[0]; pix = p.get_pixmap(dpi=160)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    draw = ImageDraw.Draw(img)
    scale_x = img.width / p.rect.width; scale_y = img.height / p.rect.height
    colors = [(255,0,0),(0,255,0),(0,0,255),(255,128,0),(180,0,180)]
    for idx,(k,(l,r)) in enumerate(col_b.items()):
        if k=="icd": continue
        color = colors[idx % len(colors)]
        L = int(l*scale_x); R = int(r*scale_x)
        draw.line([(L,0),(L,img.height)], fill=color, width=2)
        draw.line([(R,0),(R,img.height)], fill=color, width=2)
        draw.text((L+4, 8+16*idx), f"{k}", fill=color)
    for y0,y1 in row_bands:
        Y0 = int(y0*scale_y); Y1 = int(y1*scale_y)
        draw.line([(0,Y0),(img.width,Y0)], fill=(255,200,0), width=2)
        draw.line([(0,Y1),(img.width,Y1)], fill=(255,200,0), width=2)
    st.image(img, caption="Columns/Row bands", use_container_width=True)

# --------- Header UI ----------
st.markdown(
    f"""
    <div class="header-card">
      <h1 class="header-title">💊 {PHARMACY["name"]}</h1>
      <div class="header-sub">العنوان: {PHARMACY["address"]} — الهاتف: {PHARMACY["phone"]}</div>
      <div class="header-note">Nice Deer Receipt</div>
    </div>
    """, unsafe_allow_html=True
)

show_bounds  = st.checkbox("Numbering", value=False)
show_preview = st.checkbox("first page vision", value=False)

defaults = {"qty_l":27.0, "qty_r":78.0,"name_l":200.0, "name_r":327.0,"unit_l":329.0, "unit_r":372.0,"sts_l":526.0, "sts_r":579.0,"TopY":150.0, "BottomY":700.0, "RowH":28.0, "RowCount":12}
for k,v in defaults.items(): st.session_state.setdefault(k, v)
if show_bounds:
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.session_state["qty_l"]  = st.number_input("Qty Left",  value=st.session_state["qty_l"],  step=1.0)
        st.session_state["qty_r"]  = st.number_input("Qty Right", value=st.session_state["qty_r"], step=1.0)
    with c2:
        st.session_state["name_l"] = st.number_input("Name Left", value=st.session_state["name_l"], step=1.0)
        st.session_state["name_r"] = st.number_input("Name Right",value=st.session_state["name_r"], step=1.0)
    with c3:
        st.session_state["unit_l"] = st.number_input("Unit Left", value=st.session_state["unit_l"], step=1.0)
        st.session_state["unit_r"] = st.number_input("Unit Right",value=st.session_state["unit_r"], step=1.0)
    with c4:
        st.session_state["sts_l"]  = st.number_input("Status Left",value=st.session_state["sts_l"], step=1.0)
        st.session_state["sts_r"]  = st.number_input("Status Right",value=st.session_state["sts_r"], step=1.0)
    l,r = st.columns(2)
    with l:
        st.subheader("Manual Grid (optional)")
        st.session_state["TopY"]     = st.number_input("Top Y",    value=st.session_state["TopY"], step=1.0)
        st.session_state["BottomY"]  = st.number_input("Bottom Y", value=st.session_state["BottomY"], step=1.0)
        st.session_state["RowH"]     = st.number_input("Row Height", value=st.session_state["RowH"], step=0.5)
        st.session_state["RowCount"] = st.number_input("Row Count",  value=st.session_state["RowCount"], step=1)
    with r:
        rows_json_text = st.text_area("Manual JSON: [[y_top, y_bottom], ...]", height=120, key="rows_json_text")
else:
    rows_json_text = ""

# --------- رفع الملفات + عرض عدد الصفحات ----------
col_u1, col_u2 = st.columns([2,1])
with col_u1:
    uploaded = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
with col_u2:
    if uploaded:
        info = []
        for uf in uploaded:
            try:
                with pdfplumber.open(io.BytesIO(uf.getvalue())) as pdf:
                    info.append({"File": uf.name, "Pages": len(pdf.pages)})
            except Exception:
                info.append({"File": uf.name, "Pages": "Unknown"})
        st.markdown("**Uploaded files**")
        st.dataframe(pd.DataFrame(info), use_container_width=True, hide_index=True)

# --------- اختيار مجلد الحفظ (Topmost) ----------
def choose_output_dir(default_path: str) -> str:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        root.lift(); root.focus_force(); root.update()
        dirname = filedialog.askdirectory(
            initialdir=st.session_state.get("last_output_dir", default_path),
            parent=root,
            title="Select folder to save all 80mm receipts"
        )
        root.destroy()
        if dirname:
            st.session_state["last_output_dir"] = dirname
            return dirname
    except Exception:
        pass
    return st.session_state.get("last_output_dir", default_path)

# --------- Utilities ----------
def split_qty(q: str) -> Tuple[str,str]:
    if not q: return "", ""
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*([A-Za-z\u0621-\u064A\.\-]+)\s*$", q)
    if m: return m.group(1), m.group(2)
    m2n = re.search(r"([0-9]+(?:\.[0-9]+)?)", q)
    m2t = re.search(r"/\s*([A-Za-z\u0621-\u064A\.\-]+)", q)
    return (m2n.group(1) if m2n else q, m2t.group(1) if m2t else "")

# --------- زر Start ----------
st.markdown('<div class="start-wrap">', unsafe_allow_html=True)
process = st.button("Start", key="start_btn")
st.markdown('</div>', unsafe_allow_html=True)

# --------- المعالجة ----------
if process and uploaded:
    receipts_rows: List[Dict[str,Any]] = []
    items_rows: List[Dict[str,Any]] = []

    total_pages = 0
    for uf in uploaded:
        try:
            with pdfplumber.open(io.BytesIO(uf.getvalue())) as pdf:
                total_pages += len(pdf.pages)
        except Exception:
            pass
    total_pages = max(total_pages, 1)
    done_pages = 0
    prog = st.progress(0.0)
    status_box = st.empty()

    for uf in uploaded:
        fb = uf.getvalue()
        receipts_in_file: List[Dict[str,Any]] = []
        current: Dict[str,Any] = None

        with pdfplumber.open(io.BytesIO(fb)) as pdf:
            name_r_eff_default = min(float(st.session_state["name_r"]), float(st.session_state["unit_l"]) - 10.0)
            col_bounds_default = {
                "qty":   (float(st.session_state["qty_l"]), float(st.session_state["qty_r"])),
                "name":  (float(st.session_state["name_l"]), float(name_r_eff_default)),
                "unit":  (float(st.session_state["unit_l"]), float(st.session_state["unit_r"])),
                "status":(float(st.session_state["sts_l"]),  float(st.session_state["sts_r"])),
                "icd":   (0.0, float(st.session_state["name_l"]) - 1.0),
            }
            pages_count = len(pdf.pages)

            for pi, p in enumerate(pdf.pages, start=1):
                try:
                    with p.within_bbox((0, 0, p.width, p.height*0.42)) as top_region:
                        top_text = top_region.extract_text() or ""
                except Exception:
                    top_text = ""
                page_text = p.extract_text() or ""
                header_text = top_text or page_text
                hdr = parse_header(header_text)

                new_no = hdr.get("receipt_no","")
                if new_no and (current is None or new_no != current.get("invoice_no","")):
                    if current is not None:
                        receipts_in_file.append(current)
                    current = {
                        "invoice_no": new_no,
                        "date": hdr.get("date",""),
                        "patient_id": hdr.get("patient_id",""),
                        "patient_name_excel": hdr.get("patient_name_excel",""),
                        "patient_name_pdf": hdr.get("patient_name_pdf",""),
                        "total_gross": hdr.get("total_gross",""),
                        "company": hdr.get("company",""),
                        "copayment": hdr.get("copayment",""),
                        "items": []
                    }
                else:
                    if current is None:
                        current = {"invoice_no":"", "date":"", "patient_id":"", "patient_name_excel":"", "patient_name_pdf":"", "total_gross":"", "company":"", "copayment":"", "items":[]}
                    for k in ("date","patient_id","patient_name_excel","patient_name_pdf","total_gross","company","copayment"):
                        if not current.get(k) and hdr.get(k):
                            current[k] = hdr[k]
                    if not current.get("invoice_no") and new_no:
                        current["invoice_no"] = new_no

                region = detect_table_region_by_text(p)
                if show_bounds and st.session_state.get("rows_json_text","").strip():
                    bands = [tuple(map(float,b)) for b in json.loads(st.session_state["rows_json_text"])]
                elif show_bounds:
                    top, bottom, rh, rc = st.session_state["TopY"], st.session_state["BottomY"], st.session_state["RowH"], int(st.session_state["RowCount"])
                    bands=[]; y=top
                    for _ in range(rc):
                        y2 = min(bottom, y+rh); bands.append((y,y2)); y=y2
                else:
                    bands = detect_row_bands_by_lines(p, region)

                if bands:
                    parsed = parse_items_by_bands(p, col_bounds_default, bands, current["date"] or hdr["date"], allow_fallback=False)
                else:
                    parsed = parse_items_by_signals(p, col_bounds_default, current["date"] or hdr["date"], region, allow_fallback=False)

                parsed = [it for it in parsed if it.get("status","").strip().lower() not in ("deleted","excluded")]
                for it in parsed:
                    nm = dedupe_repeated_name(clean_item_name(it.get("name","")))
                    it["name"] = nm
                current["items"].extend(parsed)

                done_pages += 1
                prog.progress(min(done_pages/total_pages, 1.0))
                status_box.info(f"Processing: {uf.name} — page {pi}/{pages_count}  |  {done_pages}/{total_pages} pages")

                if show_preview and done_pages == 1:
                    try:
                        region0 = detect_table_region_by_text(p)
                        bands0 = detect_row_bands_by_lines(p, region0) or []
                        draw_preview(fb, col_bounds_default, bands0 if bands0 else [(region0[0], region0[1])])
                    except Exception:
                        pass

        if current is not None:
            receipts_in_file.append(current)

        # تجميع الصفوف لهذه الملفات (قد تحتوي أكثر من إيصال)
        for rec in receipts_in_file:
            inv = rec["invoice_no"] or f"{datetime.now().strftime('%Y%m%d')}-{os.path.splitext(uf.name)[0]}"
            receipts_rows.append({
                "invoice_no": inv,
                "date": rec.get("date","") or datetime.now().strftime("%Y-%m-%d"),
                "patient_id": rec.get("patient_id",""),
                "patient_name": rec.get("patient_name_excel",""),
                "total_gross": rec.get("total_gross",""),
                "source_file": f"{uf.name}",
                "_patient_name_pdf": rec.get("patient_name_pdf",""),
                "company": rec.get("company",""),
                "copayment": rec.get("copayment",""),
            })
            for it in rec.get("items",[]):
                qv, qt = split_qty(it.get("qty",""))
                items_rows.append({
                    "invoice_no": inv,
                    "name": it.get("name",""),
                    "Type": qt,
                    "qty": qv,
                    "unit": it.get("unit",""),
                    "status": it.get("status",""),
                    "dispensed_date": it.get("dispensed_date",""),
                    "gross_amount": rec.get("total_gross",""),
                })

    prog.progress(1.0); status_box.success("All files processed successfully.")
    st.success(f"Extracted {len(receipts_rows)} receipts and {len(items_rows)} items after filtering.")
    st.session_state["receipts"] = receipts_rows
    st.session_state["items"]    = items_rows

# --------- العرض والتصدير ----------
show_tables = st.checkbox("Extraction details", value=False)
if st.session_state.get("receipts"):
    df_r = pd.DataFrame(st.session_state["receipts"])
    df_i = pd.DataFrame(st.session_state["items"])
    if show_tables:
        st.subheader("Receipts")
        show_r = df_r.drop(columns=["_patient_name_pdf"]) if "_patient_name_pdf" in df_r.columns else df_r
        st.dataframe(show_r, use_container_width=True)
        st.subheader("Items")
        st.dataframe(df_i[["invoice_no","name","Type","qty","unit","status","dispensed_date","gross_amount"]],
                     use_container_width=True)

    # Excel
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as xw:
        (df_r.drop(columns=["_patient_name_pdf"]) if "_patient_name_pdf" in df_r.columns else df_r)\
            .to_excel(xw, index=False, sheet_name="Receipts")
        out_i = df_i.copy()
        out_i["name"] = out_i["name"].map(lambda x: dedupe_repeated_name(clean_item_name(x)))
        out_i[["invoice_no","name","Type","qty","unit","status","dispensed_date","gross_amount"]].to_excel(
            xw, index=False, sheet_name="Items")
    bio.seek(0)
    st.download_button("Excel", data=bio,
                       file_name=f"receipts_items_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # PDF Receipt
    if st.button("PDF Receipt"):
        default_dir = os.path.expanduser("~\\Desktop") if platform.system().lower().startswith("win") else os.path.expanduser("~/")
        output_dir = choose_output_dir(default_dir)
        os.makedirs(output_dir, exist_ok=True)

        WIDTH = 80*mm
        LEFT   = 4*mm
        RIGHT  = WIDTH - 4*mm
        LINE_H = 4.8*mm
        FONT_SZ = 8
        FONT_SZ_NAME = 9   # +1

        COLS = [("N",6*mm), ("Name",34*mm), ("Type",10*mm), ("Qty",10*mm), ("Unit",12*mm)]

        def wrap_text(text, max_w, canv, font, size):
            words = (text or "").split(); lines=[]; cur=""
            for w in words:
                t = (cur + " " + w).strip()
                if canv.stringWidth(t, font, size) <= max_w: cur = t
                else:
                    if cur: lines.append(cur); cur = w
            if cur: lines.append(cur)
            return lines

        def make_pdf_receipt(out_path, header, items):
            c_dummy = canvas.Canvas(io.BytesIO(), pagesize=(WIDTH, 200*mm))
            name_w = COLS[1][1]-2
            extra_rows = 0
            for it in items:
                nm = dedupe_repeated_name(clean_item_name(it['name']))
                nm = ar_visual_for_pdf(nm) if AR_RE.search(nm) else nm
                nm_lines = wrap_text(nm, name_w, c_dummy, AR_FONT_NAME, FONT_SZ_NAME)
                extra_rows += max(0, len(nm_lines)-1)

            base_lines = 13  # + سطر "نسبة التحمل"
            total_lines = base_lines + len(items) + extra_rows
            height = max(124*mm, total_lines*LINE_H + 20*mm)

            c = canvas.Canvas(out_path, pagesize=(WIDTH, height))
            W,H = WIDTH, height
            y = H - 8*mm

            # Header
            c.setFont(AR_FONT_BOLD, 16)
            c.drawCentredString(W/2, y, ar_visual_for_pdf(PHARMACY["name"])); y -= LINE_H
            c.setFont(AR_FONT_NAME, 8)
            c.drawCentredString(W/2, y, ar_visual_for_pdf(PHARMACY["address"])); y -= LINE_H
            c.drawCentredString(W/2, y, ar_visual_for_pdf(f"هاتف: {PHARMACY['phone']}")); y -= LINE_H*0.8
            c.setFont(AR_FONT_NAME, 8)
            c.drawRightString(RIGHT, y, ar_visual_for_pdf(RIGHT_NOTE))
            c.drawString(LEFT,  y, ar_visual_for_pdf(LEFT_NOTE)); y -= LINE_H*0.8
            company_line = header.get("company","")
            if company_line:
                c.setFont(AR_FONT_NAME, 9)
                c.drawCentredString(W/2, y, ar_visual_for_pdf(f"الشركة: {company_line}")); y -= LINE_H*0.6
            c.line(LEFT, y, RIGHT, y); y -= LINE_H*0.6

            # رقم + تاريخ + نسبة التحمل
            c.setFont(AR_FONT_NAME, 8)
            box_h = LINE_H*3.4
            top = y; bottom = y - box_h
            c.rect(LEFT, bottom, RIGHT-LEFT, box_h, stroke=1, fill=0)
            c.line((LEFT+RIGHT)/2, top, (LEFT+RIGHT)/2, bottom)
            c.drawRightString(RIGHT-2*mm, top - LINE_H*1.2, ar_visual_for_pdf(f"رقم: {header['invoice_no']}"))
            c.drawString(LEFT+2*mm,  top - LINE_H*1.2, ar_visual_for_pdf(f"التاريخ: {header['date']}"))
            cp = header.get("copayment","")
            if cp:
                c.drawRightString(RIGHT-2*mm, top - LINE_H*2.4, ar_visual_for_pdf(f"نسبة التحمل : {cp}"))
            y = bottom - LINE_H*0.6

            # Table header
            row_h = LINE_H
            c.rect(LEFT, y-row_h, (RIGHT-LEFT), row_h, stroke=1, fill=0)
            x = LEFT
            for title, w in COLS:
                c.line(x, y-row_h, x, y)
                c.drawCentredString(x + w/2, y - row_h*0.75, ar_visual_for_pdf(title))
                x += w
            c.line(x, y-row_h, x, y)
            y -= row_h

            # Rows
            idx = 1
            for it in items:
                nm = dedupe_repeated_name(clean_item_name(it['name']))
                nm = ar_visual_for_pdf(nm) if AR_RE.search(nm) else nm
                nm_lines = wrap_text(nm, COLS[1][1]-2, c, AR_FONT_NAME, FONT_SZ_NAME)
                cell_h = row_h * max(1, len(nm_lines))
                c.rect(LEFT, y - cell_h, (RIGHT-LEFT), cell_h, stroke=1, fill=0)
                x = LEFT
                c.line(x, y - cell_h, x, y); c.setFont(AR_FONT_NAME, FONT_SZ); c.drawCentredString(x + COLS[0][1]/2, y - row_h*0.75, str(idx)); x += COLS[0][1]
                c.line(x, y - cell_h, x, y)
                yy = y - row_h*0.75
                c.setFont(AR_FONT_NAME, FONT_SZ_NAME)
                for ln in nm_lines:
                    c.drawString(x + 2, yy, ln); yy -= row_h
                x += COLS[1][1]
                c.setFont(AR_FONT_NAME, FONT_SZ)
                c.line(x, y - cell_h, x, y); c.drawCentredString(x + COLS[2][1]/2, y - row_h*0.75, it.get('Type','')); x += COLS[2][1]
                c.line(x, y - cell_h, x, y); c.drawCentredString(x + COLS[3][1]/2, y - row_h*0.75, it.get('qty','')); x += COLS[3][1]
                c.line(x, y - cell_h, x, y); c.drawCentredString(x + COLS[4][1]/2, y - row_h*0.75, it.get('unit','')); x += COLS[4][1]
                c.line(x, y - cell_h, x, y)
                y -= cell_h; idx += 1

            y -= LINE_H*0.3
            c.line(LEFT, y, RIGHT, y); y -= LINE_H
            c.setFont(AR_FONT_NAME, 9)
            c.drawRightString(RIGHT, y, ar_visual_for_pdf(f"Total: {header.get('total_gross','')} EGP"))
            c.showPage(); c.save()

        saved = 0
        for r in st.session_state["receipts"]:
            try:
                items_for_invoice = [it for it in st.session_state["items"] if it["invoice_no"]==r["invoice_no"]]
                comp = (r.get("company","") or "Company").replace(" ","_")
                make_pdf_receipt(os.path.join(output_dir, f"{comp}_{r['date']}_{r['invoice_no']}_receipt.pdf"),
                                 r, items_for_invoice)
                saved += 1
            except Exception as e:
                st.error(f"Failed to save {r['invoice_no']}: {e}")
        st.success(f"Saved {saved} receipts (80mm) to: {output_dir}")
