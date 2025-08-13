# Version: 10.1 (bug fixes: edit opens draft, save persists, removed extra divider)

import io
import json
import uuid
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st
# --- Safe rerun helper (Streamlit 1.29+ uses st.rerun) ---
def _rerun():
    try:
        st.rerun()
    except Exception:
        try:
            _rerun()
        except Exception:
            pass


# ------------------------- Page config -------------------------
st.set_page_config(page_title="Provjera korisničkih prava", layout="wide")
st.title("Provjera korisničkih prava")

# Fixed worksheet structure:
DATA_ROW_START = 3              # data start row (A3)
NAME_COL_LETTER = "A"           # Korisnik
INST_COL_LETTER = "B"           # Institucija
RIGHTS_START_COL_LETTER = "D"   # first rights column (D+)

# Fixed exemptions by fill color in column A:
SUPERADMIN_HEX = "#9ACD32"      # superadmin => exempt
DEACTIVATED_HEX = "#D3D3D3"     # deactivated => exempt

# ------------------------- Helpers -------------------------
def col_letters_to_index(letters: str) -> int:
    total = 0
    for ch in letters:
        if not ch.isalpha():
            break
        total = total * 26 + (ord(ch.upper()) - ord('A') + 1)
    return total - 1  # 0-based

def data_pos(letter: str) -> int:
    # position in DataFrame after we insert ExcelRow at position 0
    return 1 + col_letters_to_index(letter.strip().upper())

def cell_ref_to_coords(ref: str):
    letters = ''.join([c for c in ref if c.isalpha()])
    digits = ''.join([c for c in ref if c.isdigit()])
    col = col_letters_to_index(letters)
    row = int(digits) - 1 if digits else 0
    return row, col, letters, digits

def hex_to_rgb(hexstr: str):
    hexstr = hexstr.strip().lstrip("#")
    if len(hexstr) == 8:  # ARGB -> drop alpha
        hexstr = hexstr[2:]
    return tuple(int(hexstr[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)

def apply_tint(rgb, tint: float):
    r, g, b = rgb
    def _t(c):
        if tint < 0:
            return max(0, min(255, int(round(c * (1.0 + tint)))))
        else:
            return max(0, min(255, int(round(c + (255 - c) * tint))))
    return (_t(r), _t(g), _t(b))

INDEXED_COLORS = {
    0: "#000000", 1: "#000000", 2: "#FFFFFF", 3: "#FF0000", 4: "#00FF00",
    5: "#0000FF", 6: "#FFFF00", 7: "#FF00FF", 8: "#00FFFF", 9: "#800000",
    10: "#008000", 11: "#000080", 12: "#808000", 13: "#800080", 14: "#008080",
    15: "#C0C0C0", 16: "#808080", 64: None,
}

def resolve_color(attr: dict, theme_colors: dict):
    if not attr:
        return None
    if 'rgb' in attr:
        try:
            rgb = hex_to_rgb(attr['rgb'])
            return rgb_to_hex(rgb)
        except Exception:
            return None
    if 'theme' in attr:
        try:
            t_idx = int(attr['theme'])
            base_hex = theme_colors.get(t_idx)
            if base_hex is None:
                return None
            base_rgb = hex_to_rgb(base_hex)
            tint = float(attr.get('tint', 0))
            tinted = apply_tint(base_rgb, tint)
            return rgb_to_hex(tinted)
        except Exception:
            return None
    if 'indexed' in attr:
        try:
            i = int(attr['indexed'])
            return INDEXED_COLORS.get(i)
        except Exception:
            return None
    return None

def robust_read_xlsx(file_bytes: bytes) -> Tuple[pd.DataFrame, Dict[int, str]]:
    """
    Robustly parse the first worksheet of an XLSX:
    - Returns a DataFrame with the first row as header
    - Returns a mapping {excel_row_number: hex_color or ""} for column A fills
    """
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        # workbook -> first sheet target
        wb_xml = ET.fromstring(z.read("xl/workbook.xml"))
        ns_wb = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
                 'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
        first_sheet = wb_xml.find('.//main:sheets/main:sheet', ns_wb)
        rid = first_sheet.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        rels_xml = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        ns_rel = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
        target = None
        for rel in rels_xml.findall('.//rel:Relationship', ns_rel):
            if rel.attrib.get('Id') == rid:
                target = rel.attrib.get('Target')
                break
        sheet_path = "xl/" + target if not target.startswith('xl/') else target

        # theme colors
        theme_colors = {}
        try:
            theme_root = ET.fromstring(z.read("xl/theme/theme1.xml"))
            a = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
            scheme = theme_root.find(f'.//{a}clrScheme')
            order = ['lt1','dk1','lt2','dk2','accent1','accent2','accent3','accent4','accent5','accent6','hlink','folHlink']
            base_colors = []
            if scheme is not None:
                for key in order:
                    el = scheme.find(f'{a}{key}')
                    hexval = None
                    if el is not None:
                        srgb = el.find(f'{a}srgbClr')
                        sys = el.find(f'{a}sysClr')
                        if srgb is not None and 'val' in srgb.attrib:
                            hexval = "#" + srgb.attrib['val'].upper()
                        elif sys is not None and 'lastClr' in sys.attrib:
                            hexval = "#" + sys.attrib['lastClr'].upper()
                    base_colors.append(hexval or "#000000")
            theme_colors = {i: base_colors[i] for i in range(len(base_colors))}
        except KeyError:
            theme_colors = {}

        # styles (fills)
        styles_root = ET.fromstring(z.read("xl/styles.xml"))
        ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
        fills = styles_root.find(f'{ns}fills')
        fills_info = []
        if fills is not None:
            for fill in fills.findall(f'{ns}fill'):
                pattern = fill.find(f'{ns}patternFill')
                info = {"patternType": None, "fgColor": None, "bgColor": None}
                if pattern is not None:
                    fg = pattern.find(f'{ns}fgColor')
                    bg = pattern.find(f'{ns}bgColor')
                    if fg is not None:
                        info["fgColor"] = fg.attrib
                    if bg is not None:
                        info["bgColor"] = bg.attrib
                fills_info.append(info)

        cellXfs = styles_root.find(f'{ns}cellXfs')
        xf_fill_ids = []
        if cellXfs is not None:
            for xf in cellXfs.findall(f'{ns}xf'):
                fillId = int(xf.attrib.get('fillId', '0'))
                xf_fill_ids.append(fillId)

        # shared strings
        shared_strings = []
        try:
            sst_root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sst_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                texts = []
                for t in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                    texts.append(t.text or "")
                shared_strings.append("".join(texts))
        except KeyError:
            shared_strings = []

        # sheet values and shading for column A
        sheet_root = ET.fromstring(z.read(sheet_path))

        # determine width
        max_col_idx = 0
        for c in sheet_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            r_attr = c.attrib.get('r', 'A1')
            _, col_idx, _, _ = cell_ref_to_coords(r_attr)
            if col_idx > max_col_idx:
                max_col_idx = col_idx
        max_cols = max_col_idx + 1

        rows_list = []
        excel_row_numbers = []
        shade_map: Dict[int, Optional[str]] = {}

        for row in sheet_root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            rnum = int(row.attrib.get('r', '1'))
            row_values = [None] * max_cols
            for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                r_attr = c.attrib.get('r', 'A1')
                _, col_idx, col_letters, _ = cell_ref_to_coords(r_attr)

                # cell value
                t = c.attrib.get('t')
                v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                is_el = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is')
                value = None
                if t == 's' and v is not None and v.text is not None:
                    try:
                        idx = int(v.text)
                        value = shared_strings[idx] if 0 <= idx < len(shared_strings) else ""
                    except ValueError:
                        value = ""
                elif t == 'inlineStr' and is_el is not None:
                    tnode = is_el.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    value = tnode.text if tnode is not None else ""
                elif v is not None and v.text is not None:
                    value = v.text
                else:
                    value = None

                row_values[col_idx] = value

                # capture Column A fill color
                if col_letters == 'A':
                    s_attr = c.attrib.get('s')
                    color_hex = None
                    if s_attr is not None and s_attr.isdigit():
                        xf_idx = int(s_attr)
                        if xf_idx < len(xf_fill_ids):
                            fill_id = xf_fill_ids[xf_idx]
                            if fill_id is not None and fill_id < len(fills_info):
                                finfo = fills_info[fill_id]
                                color_hex = (resolve_color(finfo.get("fgColor"), theme_colors) or
                                             resolve_color(finfo.get("bgColor"), theme_colors))
                    shade_map[rnum] = color_hex

            rows_list.append(row_values)
            excel_row_numbers.append(rnum)

    df = pd.DataFrame(rows_list)
    header = [str(c).strip() if c is not None else "" for c in df.iloc[0].tolist()]
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = [str(c).strip() for c in header]

    excel_row_series = pd.Series(excel_row_numbers[1:len(df)+1], name="ExcelRow")
    df.insert(0, "ExcelRow", excel_row_series.values)

    return df, shade_map

def normalize(s: str) -> str:
    return " ".join(str(s).split()).casefold()

def is_x(val) -> bool:
    if pd.isna(val):
        return False
    s = str(val).strip().casefold()
    return s in {"x", "1"}

# ------------------------- Upload & parse -------------------------
uploaded = st.file_uploader("Učitaj Excel (.xlsx)", type=["xlsx"])
if uploaded is None:
    st.info("Učitaj Excel datoteku kako bi započeo analizu.")
    st.stop()

# Parse workbook
try:
    df, shade_map = robust_read_xlsx(uploaded.read())
except Exception as e:
    st.error(f"Neuspješno čitanje .xlsx: {e}")
    st.stop()

# Positions and rights headers
NAME_POS = data_pos(NAME_COL_LETTER)
INST_POS = data_pos(INST_COL_LETTER)
RIGHTS_START_POS = data_pos(RIGHTS_START_COL_LETTER)
rights_cols_raw = list(df.columns[RIGHTS_START_POS:])

# Filter out non-right labels per spec
EXCLUDE_LABELS = [
    "Poziv na dostavu projektnih prijedloga (PDP)",
    "Financijski instrumenti (FI)",
    "Odabir",
    "Priprema podataka za ugovor",
    "Ugovaranje",
    "Plan nabave (PN)",
    "Početni plan dostavljanja ZPP-ova i ZNS-ova",
    "Zahtjev za plaćanjem predujma (ZPP)",
    "Zahtjev za nadoknadom sredstava (ZNS)",
    "Provjera na licu mjesta (PLM)",
    "Plaćanja i povrati (PIP)",
    "Ispravak statusa projekta (ISP)",
    "Izvješće nakon provedbe (INP)",
]
EXCLUDE_SET = {normalize(x) for x in EXCLUDE_LABELS}
rights_cols = [c for c in rights_cols_raw if normalize(c) not in EXCLUDE_SET]

# Filter data rows
df_data = df[df["ExcelRow"] >= DATA_ROW_START].copy()

# Status/exempt via Column A color
def status_from_color(c_hex: Optional[str]) -> str:
    if not c_hex:
        return "normal"
    u = c_hex.upper()
    if u == SUPERADMIN_HEX:
        return "superadmin (izuzeće)"
    if u == DEACTIVATED_HEX:
        return "deaktiviran (izuzeće)"
    return "druga boja"

df_data["A_FillColor"] = df_data["ExcelRow"].map(shade_map).fillna("")
df_data["Status"] = df_data["A_FillColor"].map(status_from_color)
df_data["Exempt"] = df_data["Status"].str.contains("izuzeće")

# ------------------------- Sidebar: Group creator (stacked layout) -------------------------
st.sidebar.header("Kreator grupa (vizualni)")

# Session state init with stable IDs
if "saved_groups" not in st.session_state:
    st.session_state.saved_groups: List[Dict] = []  # [{id, name, rights}]
if "drafts" not in st.session_state:
    st.session_state.drafts: List[Dict] = []       # [{id, name, rights}]

# Top: Add new group (draft)
if st.sidebar.button("➕ Dodaj novu grupu"):
    st.session_state.drafts.append({"id": uuid.uuid4().hex, "name": f"Grupa_{len(st.session_state.saved_groups) + len(st.session_state.drafts) + 1}", "rights": []})

# Next: Export saved groups
export_payload = [
    {"name": g["name"], "rights": [r for r in g["rights"] if r in rights_cols]}
    for g in st.session_state.saved_groups
]
export_json = json.dumps(export_payload, ensure_ascii=False, indent=2)
st.sidebar.download_button("⬇️ Izvezi grupe", data=export_json.encode("utf-8"), file_name="grupe.json", mime="application/json")

# Single import (drag & drop) placed just under "Izvezi grupe"
st.sidebar.caption("Uvezi grupe (JSON) – povuci i ispusti datoteku ovdje:")
cfg_up = st.sidebar.file_uploader("Uvezi grupe (JSON)", type=["json"], label_visibility="collapsed", key="import_groups_top")
if cfg_up is not None:
    try:
        cfg = json.loads(cfg_up.read())
        if isinstance(cfg, list):
            new_saved = []
            for g in cfg:
                nm = g.get("name","grupa")
                rts = [r for r in g.get("rights",[]) if isinstance(r, str)]
                rts = [r for r in rts if r in rights_cols]  # ensure valid rights
                if rts:
                    new_saved.append({"id": uuid.uuid4().hex, "name": nm, "rights": rts})
            st.session_state.saved_groups = new_saved
            st.success(f"Uvezeno grupa: {len(new_saved)}")
        else:
            st.error("Očekivan je JSON niz (lista grupa).")
    except Exception as e:
        st.error(f"Neuspješno učitavanje: {e}")


st.sidebar.subheader("Spremljene grupe")
if not st.session_state.saved_groups:
    st.sidebar.caption("Nema spremljenih grupa.")
else:
    # Clean saved groups from any now-excluded rights
    for sg in st.session_state.saved_groups:
        sg["rights"] = [r for r in sg["rights"] if r in rights_cols]
    for j, sg in enumerate(st.session_state.saved_groups):
        with st.sidebar.expander(f"{sg['name']}", expanded=False):
            st.caption(f"Prava ({len(sg['rights'])}):")
            for r in sg["rights"]:
                st.write(f"- {r}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✏️ Uredi", key=f"edit_saved_{sg['id']}" if 'id' in sg else f"edit_saved_{j}"):
                    # push to drafts for editing
                    st.session_state.drafts.append({"id": uuid.uuid4().hex, "name": sg["name"], "rights": sg["rights"].copy()})
                    st.info(f"Grupa '{sg['name']}' dodana u nacrte za uređivanje.")
                    _rerun()
            with c2:
                if st.button("🗑️ Obriši", key=f"delete_saved_{sg['id']}" if 'id' in sg else f"delete_saved_{j}"):
                    st.session_state.saved_groups.pop(j)
                    _rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Uređivanje nacrta")

# Render drafts (each with stable widget keys)
remove_ids = []
for draft in st.session_state.drafts:
    did = draft["id"]
    name_key = f"name_{did}"
    rights_key = f"rights_{did}"

    # Initialize defaults BEFORE widget creation
    if name_key not in st.session_state:
        st.session_state[name_key] = draft["name"]
    if rights_key not in st.session_state:
        st.session_state[rights_key] = [r for r in draft["rights"] if r in rights_cols]

    with st.sidebar.expander(f"Nacrt: {st.session_state[name_key]}", expanded=True):
        # Widgets use only keys; no 'value'/'default'
        st.text_input("Naziv grupe", key=name_key)
        st.multiselect("Prava u grupi (ALL-of)", options=rights_cols, key=rights_key)

        # Sync back to draft object from session_state (not from widget return)
        draft["name"] = st.session_state[name_key]
        draft["rights"] = [r for r in st.session_state[rights_key] if r in rights_cols]

        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            if st.button("💾 Spremi grupu", key=f"save_{did}"):
                if not draft["rights"]:
                    st.warning("Grupa mora sadržavati barem jedno pravo.")
                else:
                    # If a saved group with same name exists, overwrite its rights
                    names = [sg["name"] for sg in st.session_state.saved_groups]
                    if draft["name"] in names:
                        pos = names.index(draft["name"])
                        st.session_state.saved_groups[pos]["rights"] = draft["rights"].copy()
                    else:
                        st.session_state.saved_groups.append({"id": uuid.uuid4().hex, "name": draft["name"], "rights": draft["rights"].copy()})
                    remove_ids.append(did)
                    # Clean widget state for removed draft
                    st.session_state.pop(name_key, None)
                    st.session_state.pop(rights_key, None)
                    st.success(f"Spremljeno: {draft['name']}")
                    _rerun()
        with c2:
            if st.button("🧹 Očisti nacrt", key=f"clear_{did}"):
                st.session_state[rights_key] = []
        with c3:
            if st.button("❌ Ukloni nacrt", key=f"del_{did}"):
                remove_ids.append(did)
                st.session_state.pop(name_key, None)
                st.session_state.pop(rights_key, None)

# Remove drafts flagged for deletion
if remove_ids:
    st.session_state.drafts = [d for d in st.session_state.drafts if d["id"] not in remove_ids]
    _rerun()

# Import (drag & drop) INSIDE "Kreator grupa (vizualni)"
st.sidebar.markdown("---")
st.sidebar.markdown("---")
# Bottom: Import (drag & drop)# ------------------------- Evaluate rules (ONLY saved groups) -------------------------
def has_all(row, cols: List[str]) -> bool:
    return bool(cols) and all((str(row.get(c, "")).strip().casefold() in {"x","1"}) for c in cols)

violations_records = []
exempt_records = []

valid_groups = [g for g in st.session_state.saved_groups if g.get("rights")]
for _, row in df_data.iterrows():
    name = row.iloc[NAME_POS]
    inst = row.iloc[INST_POS]
    exempt = bool(row["Exempt"])
    for g in valid_groups:
        if has_all(row, g["rights"]):
            rec = {"Institucija": inst, "Korisnik": name, "Grupa": g.get("name","grupa")}
            if exempt:
                exempt_records.append(rec)
            else:
                violations_records.append(rec)

df_viol_detail = pd.DataFrame(violations_records)
df_exempt_detail = pd.DataFrame(exempt_records)

# Aggregate multiple violations per user into a single row (comma-separated groups)
def _aggregate_groups(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=["Institucija","Korisnik","Grupa"])
    agg = (df.groupby(["Institucija","Korisnik"], as_index=False)
             .agg({"Grupa": lambda s: ", ".join(dict.fromkeys([str(v) for v in list(s)])) }))
    return agg

df_viol = _aggregate_groups(df_viol_detail)
df_exempt = _aggregate_groups(df_exempt_detail)

# ------------------------- Reports -------------------------
st.subheader("Rezultati")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Ukupan broj kršenja", int(len(df_viol_detail)))
with col2:
    st.metric("Izuzeti (zadovoljavaju neku spremljenu grupu)", int(len(df_exempt_detail)))
with col3:
    st.metric("Broj spremljenih grupa", int(len(valid_groups)))

st.markdown("**Popis kršenja (Korisnik ima SVA prava iz spremljene grupe i nije izuzet):**")
if not valid_groups:
    st.info("Nema spremljenih grupa. Spremi barem jednu grupu u lijevom izborniku.")
elif df_viol.empty:
    st.info("Nema kršenja prema spremljenim grupama.")
else:
    try:
        st.dataframe(df_viol.sort_values(["Institucija","Grupa","Korisnik"]).reset_index(drop=True), use_container_width=True, hide_index=True)
    except TypeError:
        st.dataframe(df_viol.sort_values(["Institucija","Grupa","Korisnik"]).reset_index(drop=True), use_container_width=True)

st.markdown("**Sažetak po instituciji i grupi:**")
if not valid_groups or df_viol_detail.empty:
    st.info("—")
else:
    # Agregacija: zbroj svih kršenja po instituciji (preko svih grupa)
    summary = df_viol_detail.groupby(["Institucija"]).size().reset_index(name="Broj kršenja")
    try:
        st.dataframe(summary.sort_values(["Institucija"]).reset_index(drop=True), use_container_width=True, hide_index=True)
    except TypeError:
        st.dataframe(summary.sort_values(["Institucija"]).reset_index(drop=True), use_container_width=True)

with st.expander("Imaju prava koja zadovoljavaju spremljenu grupu, ali su izuzeti (superadmin/deaktivirani)"):
    if not valid_groups or df_exempt.empty:
        st.info("—")
    else:
        try:
            st.dataframe(df_exempt.sort_values(["Institucija","Grupa","Korisnik"]).reset_index(drop=True), use_container_width=True, hide_index=True)
        except TypeError:
            st.dataframe(df_exempt.sort_values(["Institucija","Grupa","Korisnik"]).reset_index(drop=True), use_container_width=True)

# ------------------------- Downloads -------------------------
st.markdown("---")
st.subheader("Izvoz")

st.download_button("Preuzmi CSV - kršenja", data=df_viol.to_csv(index=False).encode("utf-8-sig"),
                   file_name="krsenja.csv", mime="text/csv")
st.download_button("Preuzmi CSV - izuzeti", data=df_exempt.to_csv(index=False).encode("utf-8-sig"),
                   file_name="izuzeti.csv", mime="text/csv")

def to_excel_bytes(dfs: Dict[str, pd.DataFrame]) -> bytes:
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for name, d in dfs.items():
            (d if not d.empty else pd.DataFrame()).to_excel(writer, index=False, sheet_name=name[:31] or "Sheet1")
    return output.getvalue()

xls_bytes = to_excel_bytes({"Krsenja": df_viol, "Izuzeti": df_exempt})
st.download_button("Preuzmi XLSX (oba lista)", data=xls_bytes, file_name="izvjestaj_prava.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
