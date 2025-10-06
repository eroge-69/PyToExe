# Recon_App_V3.py
# Provider-aware reconciliation GUI with multi-PSP separation and copy.

import os, json, traceback, threading
from datetime import datetime
from pathlib import Path
import pandas as pd
from tkinter import Tk, StringVar, IntVar, filedialog, messagebox
from tkinter import ttk

# --- Optional .xls -> .xlsx via Excel ---
try:
    import win32com.client as win32
except Exception:
    win32 = None

def _xls_to_xlsx(xls_path: Path) -> Path | None:
    if win32 is None:
        return None
    xlsx = xls_path.with_suffix(".xlsx")
    xl = win32.Dispatch("Excel.Application"); xl.Visible = False
    wb = xl.Workbooks.Open(str(xls_path.resolve()))
    wb.SaveAs(str(xlsx.resolve()), FileFormat=51)
    wb.Close(False); xl.Quit()
    return xlsx

# --- Robust file reader ---
def read_any(path: str, *, dtype=str, keep_default_na=False) -> pd.DataFrame:
    p = Path(path); s = p.suffix.lower()
    if s in (".csv", ".txt"):
        return pd.read_csv(p, dtype=dtype, keep_default_na=keep_default_na, encoding_errors="replace")
    if s == ".gz" and p.name.lower().endswith(".csv.gz"):
        return pd.read_csv(p, compression="gzip", dtype=dtype, keep_default_na=keep_default_na, encoding_errors="replace")
    if s == ".xls":
        try:
            import xlrd  # noqa
            return pd.read_excel(p, engine="xlrd", dtype=dtype, keep_default_na=keep_default_na)
        except Exception:
            newp = _xls_to_xlsx(p)
            if newp and newp.exists():
                return pd.read_excel(newp, engine="openpyxl", dtype=dtype, keep_default_na=keep_default_na)
            raise ImportError("Legacy .xls requires xlrd>=2.0.1 or Excel conversion.")
    if s in (".xlsx", ".xlsm"):
        return pd.read_excel(p, engine="openpyxl", dtype=dtype, keep_default_na=keep_default_na)
    if s == ".xlsb":
        return pd.read_excel(p, engine="pyxlsb", dtype=dtype, keep_default_na=keep_default_na)
    raise ValueError(f"Unsupported file type: {p.suffix}")

# include engines for PyInstaller
try: import openpyxl
except Exception: pass
try: import xlrd
except Exception: pass
try: import pyxlsb
except Exception: pass

# --- Theme ---
COLORS = {
    "bg_dark":   "#000042",
    "card":      "#0C1267",
    "accent":    "#2336B1",
    "highlight": "#2D47D6",
    "text":      "#FFFFFF",
    "muted":     "#C9D2FF",
}

HISTORY_FILE = "recon_history.json"
RULES_FILE   = "recon_rules.json"

# --- Provider specs ---
PROVIDERS = {
    "CRM":       {"key": ["PSP Transaction ID"], "alt": []},
    "Paymaxis":  {"key": ["Reference ID"], "alt": ["External ID"]},
    "Match2Pay": {"key": ["Payment ID"], "alt": []},
    "ForumPay":  {"key": ["Payment ID"], "alt": []},
}
PROVIDER_SHEETS = {
    "CRM":       ["All transaction", "All-Transactions", "All Transactions"],
    "Paymaxis":  ["Payments"],
    "Match2Pay": ["Crypto transactions", "Crypto Transactions"],
    "ForumPay":  ["TransactionsList", "Transactions List"],
}
FILE_SIGNATURES = {
    "CRM":       ["all transaction", "all-transactions", "all_transactions"],
    "Paymaxis":  ["payments"],
    "Match2Pay": ["crypto transactions", "crypto_transactions"],
    "ForumPay":  ["transactionslist", "transactions list"],
}
PROVIDER_OPTIONS = ["CRM","Paymaxis","Match2Pay","ForumPay"]

# --- Helpers ---
def resource_path(rel_path: str) -> str:
    import sys
    bases = []
    if getattr(sys, "frozen", False):
        bases += [getattr(sys, "_MEIPASS", ""), os.path.dirname(sys.executable)]
    bases.append(os.path.abspath("."))
    for base in bases:
        if base:
            p = os.path.join(base, rel_path)
            if os.path.exists(p): return p
    return rel_path

def load_logo_image(master, filename="logo.png", max_wh=(140, 80)):
    path = resource_path(filename)
    if not os.path.exists(path): return None, None
    try:
        from PIL import Image, ImageTk
        im = Image.open(path).convert("RGBA")
        if max_wh: im.thumbnail(max_wh)
        return ImageTk.PhotoImage(im, master=master), None
    except Exception as e:
        return None, str(e)

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE, "r") as f: return json.load(f)
    except Exception: return []

def save_history(entries):
    try:
        with open(HISTORY_FILE, "w") as f: json.dump(entries, f, indent=2)
    except Exception as e:
        print("Error saving history:", e)

def load_rules():
    if not os.path.exists(RULES_FILE): return {}
    try:
        with open(RULES_FILE, "r") as f: return json.load(f)
    except Exception: return {}

def save_rules(rules: dict):
    try:
        with open(RULES_FILE, "w") as f: json.dump(rules, f, indent=2)
    except Exception as e:
        messagebox.showerror("Rules Save Error", str(e))

def find_first_col(df: pd.DataFrame, candidates) -> str | None:
    if not isinstance(candidates, (list, tuple)): candidates = [candidates]
    for c in candidates:
        if c in df.columns: return c
    lowmap = {str(c).strip().lower(): c for c in df.columns}
    for c in candidates:
        key = str(c).strip().lower()
        if key in lowmap: return lowmap[key]
    for want in candidates:
        w = str(want).strip().lower()
        for real in df.columns:
            if w and w in str(real).strip().lower():
                return real
    return None

def series_from_cols(df: pd.DataFrame, candidates, default="") -> pd.Series:
    col = find_first_col(df, candidates)
    if col is None: return pd.Series([default]*len(df), index=df.index)
    return df[col]

AMOUNT_COLS = {
    "default":   ["Amount","Value","Gross"],
    "Match2Pay": ["Final amount","Amount","Value","Gross"],
}
CURRENCY_COLS = {
    "default":   ["Currency","Curr"],
    "Match2Pay": ["Final currency","Currency","Curr"],
}
DATE_COLS = ["Date","Created On","Txn Date"]
TYPE_COLS = ["Type","Txn Type","Direction","Kind","Debit/Credit","Dr/Cr"]
EMAIL_COLS = ["Email","Client Email","User"]

# --- Recon core ---
def run_recon_logic(primary_path, psp_inputs, *, primary_provider="CRM",
                    output_path=None, rules=None, write_output=True, use_cache=True):
    import re
    rules = rules or {}

    if not hasattr(run_recon_logic, "_CACHE"):
        run_recon_logic._CACHE = {}
    _C = run_recon_logic._CACHE

    def _read_any_cached(path: str):
        mtime = os.path.getmtime(path); hit = _C.get(path)
        if use_cache and hit and hit["mtime"] == mtime: return hit["df"].copy()
        df = read_any(path, dtype=str, keep_default_na=False); df.columns = [str(c).strip() for c in df.columns]
        _C[path] = {"mtime": mtime, "df": df.copy()}
        return df.copy()

    def _pick_sheet_name(all_sheets, provider, sheets_dict):
        wanted = [s.lower() for s in PROVIDER_SHEETS.get(provider, [])]
        for w in wanted:
            for real in all_sheets:
                if w in real.lower(): return real
        if len(all_sheets) == 1: return all_sheets[0]
        spec = PROVIDERS.get(provider, {"key": [], "alt": []})
        cand_headers = [h.strip().lower() for h in (spec.get("key", []) + spec.get("alt", [])) if h]
        def has_any(df):
            cols = [str(c).strip().lower() for c in df.columns]
            for t in cand_headers:
                for c in cols:
                    if t and t in c: return True
            return False
        for name in all_sheets:
            try:
                if has_any(sheets_dict[name]): return name
            except Exception: pass
        return all_sheets[0] if all_sheets else None

    def validate_file(provider: str, path: str):
        base = os.path.basename(path).lower(); sigs = FILE_SIGNATURES.get(provider, [])
        if not sigs: return
        if not any(sig in base for sig in sigs):
            wanted = ", ".join(sigs)
            raise ValueError(f"File '{os.path.basename(path)}' does not look like {provider}. Expected one of: {wanted}")

    def _read_excel_provider(path, provider):
        validate_file(provider, path)
        try:
            sheets = pd.read_excel(path, sheet_name=None, dtype=str, keep_default_na=False, engine="openpyxl")
        except Exception:
            return read_any(path, dtype=str, keep_default_na=False)
        all_names = list(sheets.keys()); pick = _pick_sheet_name(all_names, provider, sheets)
        if not pick:
            expected = ", ".join(PROVIDER_SHEETS.get(provider, [])) or "(no hint)"
            raise ValueError(f"Workbook '{os.path.basename(path)}' lacks an expected sheet for {provider}. Looking for: {expected}")
        return sheets[pick]

    def norm_id(x):
        s = str(x or "").strip()
        if not s or s.lower() in ("nan","none","null"): return ""
        s = s.replace(" ", "").replace("_","").replace("-","")
        if re.fullmatch(r"\d+\.0", s): s = s[:-2]
        return s.upper()

    def pick_first(df, cols, provider=None):
        col = find_first_col(df, cols)
        if col is not None: return col
        for real in df.columns:
            name = str(real).strip().lower()
            if provider == "CRM":
                if ("psp" in name) and ("id" in name): return real
            if provider == "Paymaxis":
                if ("reference" in name and "id" in name) or ("external" in name and "id" in name): return real
            if provider in ("Match2Pay","ForumPay"):
                if ("payment" in name and "id" in name) or ("transaction" in name and "id" in name): return real
        return None

    def extract_keys(df, provider):
        spec = PROVIDERS.get(provider, {"key": [], "alt": []})
        kcol = pick_first(df, spec["key"], provider) if spec["key"] else None
        acol = pick_first(df, spec.get("alt", []), provider) if spec.get("alt") else None
        key  = df[kcol].map(norm_id) if kcol else pd.Series([""]*len(df), index=df.index)
        alt  = df[acol].map(norm_id) if acol else pd.Series([""]*len(df), index=df.index)
        return key, alt, kcol, acol

    # read primary
    prim_ext = os.path.splitext(primary_path)[1].lower()
    if prim_ext in (".xlsx", ".xlsm"): prim_df = _read_excel_provider(primary_path, primary_provider)
    else: validate_file(primary_provider, primary_path); prim_df = _read_any_cached(primary_path)

    prim_key, prim_alt, prim_kcol, prim_acol = extract_keys(prim_df, primary_provider)
    use_primary_alt = (primary_provider == "Paymaxis")
    if prim_kcol is None and not use_primary_alt and prim_acol is None:
        prim_key = pd.Series([""] * len(prim_df), index=prim_df.index)
        prim_alt = pd.Series([""] * len(prim_df), index=prim_df.index)

    amt_cols_prim = AMOUNT_COLS.get(primary_provider, AMOUNT_COLS["default"])
    cur_cols_prim = CURRENCY_COLS.get(primary_provider, CURRENCY_COLS["default"])
    prim = primary_provider
    crm_raw = pd.DataFrame({
        f"{prim}_Email":   series_from_cols(prim_df, EMAIL_COLS),
        f"{prim}_Amount":  pd.to_numeric(series_from_cols(prim_df, amt_cols_prim), errors="coerce"),
        f"{prim}_Currency":series_from_cols(prim_df, cur_cols_prim),
        f"{prim}_Date":    pd.to_datetime(series_from_cols(prim_df, DATE_COLS), errors="coerce"),
        f"{prim}_Type":    series_from_cols(prim_df, TYPE_COLS),
    })
    primary_key_series = (prim_alt if use_primary_alt else prim_key)
    crm_raw["Match_Key"] = primary_key_series.map(norm_id)

    grp = (crm_raw.groupby("Match_Key", dropna=False)
           .agg({f"{prim}_Email":"first", f"{prim}_Amount":"sum", f"{prim}_Currency":"first",
                 f"{prim}_Date":"first",  f"{prim}_Type":"first"}).reset_index())
    cnt = crm_raw.groupby("Match_Key", dropna=False).size().reset_index(name="CRM_TX_Count")
    crm_grouped = grp.merge(cnt, on="Match_Key", how="left")
    crm_grouped = crm_grouped.rename(columns={"Match_Key":"Primary_Ref"})
    crm_grouped[f"{prim}_Date"] = crm_grouped[f"{prim}_Date"].dt.date.astype(str)
    crm_grouped[f"{prim}_Direction"] = crm_grouped[f"{prim}_Amount"].apply(
        lambda a: "Deposit" if pd.notna(a) and a>0 else ("Withdrawal" if pd.notna(a) and a<0 else "")
    )
    primary_id_col_used = (prim_acol if use_primary_alt else prim_kcol) or "ID"
    primary_id_label = f"{primary_provider} {primary_id_col_used}"

    # PSPs by provider
    psp_order = [it["provider"] for it in psp_inputs]
    psp_grouped_by_prov = {}
    psp_keycol_used = {}
    for item in psp_inputs:
        prov, path = item["provider"], item["path"]
        ext = os.path.splitext(path)[1].lower()
        if ext in (".xlsx",".xlsm"): df = _read_excel_provider(path, prov)
        else: validate_file(prov, path); df = _read_any_cached(path)
        k, a, kc, ac = extract_keys(df, prov)
        psp_keycol_used[prov] = kc or ac or "ID"

        amt_cols_psp = AMOUNT_COLS.get(prov, AMOUNT_COLS["default"])
        cur_cols_psp = CURRENCY_COLS.get(prov, CURRENCY_COLS["default"])
        tmp = pd.DataFrame({
            "PSP_Key": k,
            f"{prov}_Email":    series_from_cols(df, EMAIL_COLS),
            f"{prov}_Amount":   pd.to_numeric(series_from_cols(df, amt_cols_psp), errors="coerce"),
            f"{prov}_Currency": series_from_cols(df, cur_cols_psp),
            f"{prov}_Date":     pd.to_datetime(series_from_cols(df, DATE_COLS), errors="coerce").dt.date.astype(str),
            f"{prov}_Type":     series_from_cols(df, TYPE_COLS),
        })
        g = (tmp.groupby("PSP_Key", dropna=False)
               .agg({f"{prov}_Email":"first", f"{prov}_Amount":"sum",
                     f"{prov}_Currency":"first", f"{prov}_Date":"first", f"{prov}_Type":"first"}).reset_index())
        cnt = tmp.groupby("PSP_Key", dropna=False).size().reset_index(name=f"{prov}_TX_Count")
        psp_grouped_by_prov[prov] = g.merge(cnt, on="PSP_Key", how="left").set_index("PSP_Key")

    # choose match provider per key (first provider that has it)
    matched_provider_for_key = {}
    for key in crm_grouped["Primary_Ref"].astype(str):
        for prov in psp_order:
            if key in psp_grouped_by_prov.get(prov, pd.DataFrame()).index:
                matched_provider_for_key[key] = prov
                break

    def _num(x):
        try: return round(float(x), 2)
        except Exception: return None

    # build recon rows
    records = []
    for _, r in crm_grouped.iterrows():
        key = str(r["Primary_Ref"])
        prov = matched_provider_for_key.get(key, None)
        if prov:
            prow = psp_grouped_by_prov[prov].loc[key]

            amt_ok = (_num(r[f"{prim}_Amount"]) is not None and
                      _num(prow.get(f"{prov}_Amount", "")) is not None and
                      _num(r[f"{prim}_Amount"]) == _num(prow.get(f"{prov}_Amount", "")))
            cur_ok = (str(r[f"{prim}_Currency"]).strip().upper() ==
                      str(prow.get(f"{prov}_Currency","")).strip().upper())
            if amt_ok and cur_ok:
                status, note = "OK", ""
            else:
                miss = []
                if not amt_ok: miss.append("amount")
                if not cur_ok: miss.append("currency")
                status, note = "Investigate", f"Mismatch: {', '.join(miss)}"

            rec = {
                "Status": status, "Match Method":"ID",
                f"{primary_id_label}": key,
                f"{prov} {psp_keycol_used[prov]}": key,

                "CRM_Ref": key, "PSP_Ref": key,

                f"{prim}_Email": r[f"{prim}_Email"],
                f"{prim}_Amount": r[f"{prim}_Amount"],
                f"{prim}_Currency": r[f"{prim}_Currency"],
                f"{prim}_Date": r[f"{prim}_Date"],
                f"{prim}_Type": r[f"{prim}_Type"],
                f"{prim}_Direction": r[f"{prim}_Direction"],

                f"{prov}_Email": prow.get(f"{prov}_Email",""),
                f"{prov}_Amount": prow.get(f"{prov}_Amount",""),
                f"{prov}_Currency": prow.get(f"{prov}_Currency",""),
                f"{prov}_Date": prow.get(f"{prov}_Date",""),
                f"{prov}_Type": prow.get(f"{prov}_Type",""),
                f"{prov}_Direction": ("Deposit" if _num(prow.get(f"{prov}_Amount",0)) and _num(prow.get(f"{prov}_Amount",0))>0
                                      else ("Withdrawal" if _num(prow.get(f"{prov}_Amount",0)) and _num(prow.get(f"{prov}_Amount",0))<0 else "")),
                f"{prov}_TX_Count": prow.get(f"{prov}_TX_Count", 1),
                "Rule Note": note, "Pending": False,
            }
            records.append(rec)
        else:
            # not found in any PSP
            rec = {
                "Status": f"Missing from {primary_provider if not psp_order else psp_order[0]}",
                "Match Method":"No Match",
                f"{primary_id_label}": key,
                "CRM_Ref": key, "PSP_Ref":"",

                f"{prim}_Email": r.get(f"{prim}_Email",""),
                f"{prim}_Amount": r.get(f"{prim}_Amount",""),
                f"{prim}_Currency": r.get(f"{prim}_Currency",""),
                f"{prim}_Date": r.get(f"{prim}_Date",""),
                f"{prim}_Type": r.get(f"{prim}_Type",""),
                f"{prim}_Direction": r.get(f"{prim}_Direction",""),
                "Rule Note":"", "Pending": False,
            }
            records.append(rec)

    # PSP-only rows → Missing from Primary
    all_primary_keys = set(crm_grouped["Primary_Ref"].astype(str))
    for prov, gdf in psp_grouped_by_prov.items():
        for key in gdf.index.astype(str):
            if key and key not in all_primary_keys:
                prow = gdf.loc[key]
                rec = {
                    "Status": f"Missing from {primary_provider}", "Match Method":"No Match",
                    f"{primary_id_label}": "", f"{prov} {psp_keycol_used[prov]}": key,
                    "CRM_Ref":"", "PSP_Ref": key,

                    f"{prov}_Email": prow.get(f"{prov}_Email",""),
                    f"{prov}_Amount": prow.get(f"{prov}_Amount",""),
                    f"{prov}_Currency": prow.get(f"{prov}_Currency",""),
                    f"{prov}_Date": prow.get(f"{prov}_Date",""),
                    f"{prov}_Type": prow.get(f"{prov}_Type",""),
                    f"{prov}_Direction": ("Deposit" if _num(prow.get(f"{prov}_Amount",0)) and _num(prow.get(f"{prov}_Amount",0))>0
                                          else ("Withdrawal" if _num(prow.get(f"{prov}_Amount",0)) and _num(prow.get(f"{prov}_Amount",0))<0 else "")),
                    f"{prov}_TX_Count": prow.get(f"{prov}_TX_Count", 1),
                    "Rule Note":"", "Pending": False,
                }
                records.append(rec)

    recon = pd.DataFrame(records)

    # manual rules
    for r in (rules.get("set_status", []) or []):
        scope = (r.get("scope") or "").strip(); ident = str(r.get("id",""))
        if scope == "crm_ref":
            mask = recon["CRM_Ref"].astype(str) == ident
        elif scope == "psp_ref":
            mask = recon["PSP_Ref"].astype(str) == ident
        else:
            continue
        recon.loc[mask,"Status"] = r.get("status","OK (Manual)")
        recon.loc[mask,"Match Method"] = "Manual"
        recon.loc[mask,"Rule Note"] = r.get("note","Solved offline")
        recon.loc[mask,"Pending"] = False

    # display: only columns for the matched PSP on each row
    def row_visible_cols(row):
        cols = ["Status","Match Method", f"{primary_id_label}"]
        # find which PSP matched this row
        matched = None
        for prov in psp_order:
            lab = f"{prov} {psp_keycol_used.get(prov,'ID')}"
            if lab in row.index and pd.notna(row.get(lab, "")) and str(row.get(lab,"")).strip() != "":
                matched = prov; cols.append(lab); break
        # primary detail cols
        cols += [c for c in row.index if c.startswith(f"{prim}_")]
        # matched PSP detail cols only
        if matched:
            cols += [c for c in row.index if c.startswith(f"{matched}_")]
        return [c for c in cols if c in row.index]

    if len(recon):
        recon_display = recon.apply(lambda r: r[row_visible_cols(r)], axis=1)
    else:
        recon_display = recon.copy()
        
        # --- enforce correct first columns and auto-fix if swapped ---
        if isinstance(recon_display, pd.DataFrame) and not recon_display.empty:
    # if Status contains only method-like tokens, swap the two cols
            if "Match Method" in recon_display.columns and "Status" in recon_display.columns:
                method_like = {"ID", "No Match", "Manual", "Manual (OK)", "Manual OK"}
        vals = set(str(x) for x in recon_display["Status"].dropna().unique())
        if vals and vals.issubset(method_like):
            recon_display[["Status", "Match Method"]] = recon_display[["Match Method", "Status"]].to_numpy()

    first = [c for c in ["Status", "Match Method"] if c in recon_display.columns]
    rest  = [c for c in recon_display.columns if c not in first]
    recon_display = recon_display[first + rest]


    # Summary
    total_primary_rows = (~recon["Status"].astype(str).str.startswith("Missing from "+primary_provider)).sum()
    ok = (recon["Status"].isin(["OK","OK (Manual)"])).sum()
    investigate_cnt = recon["Status"].astype(str).str.startswith("Investigate").sum()

    # per-provider "Missing from {PSP}" tabs:
    # include only primary rows that were NOT matched to any PSP AND show only primary + that PSP’s id header.
    missing_tabs = {}
    unmatched_keys = {str(r["Primary_Ref"]) for _, r in crm_grouped.iterrows()} - set(matched_provider_for_key.keys())
    for prov in psp_order:
        rows = []
        for _, r in crm_grouped.iterrows():
            key = str(r["Primary_Ref"])
            if key not in unmatched_keys: continue  # already reconciled somewhere
            rec = {
                "Status": f"Missing from {prov}",
                "Match Method": "No Match",
                f"{primary_id_label}": key,
                f"{prim}_Email": r.get(f"{prim}_Email",""),
                f"{prim}_Amount": r.get(f"{prim}_Amount",""),
                f"{prim}_Currency": r.get(f"{prim}_Currency",""),
                f"{prim}_Date": r.get(f"{prim}_Date",""),
                f"{prim}_Type": r.get(f"{prim}_Type",""),
                f"{prim}_Direction": r.get(f"{prim}_Direction",""),
            }
            rows.append(rec)
        missing_tabs[f"Missing from {prov}"] = pd.DataFrame(rows)

    # Results pack
    providers_in_run = {primary_provider} | set(psp_order)
    summary_rows = [["Total primary rows", total_primary_rows], ["OK", ok], ["Investigate", investigate_cnt]]
    for prov in sorted(providers_in_run):
        label = f"Missing from {prov}"
        if label in missing_tabs:
            count_val = len(missing_tabs[label])
        else:
            count_val = recon["Status"].astype(str).eq(label).sum()
        summary_rows.append([label, count_val])

    results = {
        "Meta": {"primary_id_label": primary_id_label, "psp_id_label": f"{psp_order[0]} {psp_keycol_used.get(psp_order[0],'ID')}" if psp_order else "PSP ID"},
        "Summary": pd.DataFrame(summary_rows, columns=["Metric","Value"]),
        "Recon View": recon_display.reset_index(drop=True),
        "Investigate": recon_display[recon["Status"].astype(str).str.startswith("Investigate")].reset_index(drop=True),
        "OK (Split)": pd.DataFrame([]),
        "Split Details": pd.DataFrame([]),
        "Pending": recon_display[recon.get("Pending", False)==True].reset_index(drop=True),
    }
    results.update(missing_tabs)

    # write xlsx
    def _excel_safe_sheet(name, used):
        bad = '[]:*?/\\'
        safe = ''.join('_' if ch in bad else ch for ch in name).strip() or "Sheet"
        safe = safe[:31]; base = safe; i = 1
        while safe in used:
            suf = f" ({i})"; safe = (base[:31-len(suf)] + suf) if len(base)+len(suf) > 31 else base + suf; i += 1
        used.add(safe); return safe

    if write_output:
        if not output_path:
            output_path = os.path.join(os.getcwd(), f"Recon_{datetime.now():%Y%m%d_%H%M%S}.xlsx")
        used = set()
        with pd.ExcelWriter(output_path) as w:
            for name,df in results.items():
                if name == "Meta": continue
                df.to_excel(w, sheet_name=_excel_safe_sheet(name, used), index=False)
    else:
        output_path = output_path or ""
    return output_path, results

# --- Drag & Drop ---
def enable_dnd(widget, var, filetypes, fallback_browse=None):
    def drop(event):
        path = event.data.strip("{}"); ext = os.path.splitext(path)[1].lower()
        allowed = [ft[1].replace("*", "") for ft in filetypes]
        if not any(ext.endswith(a.lower()) for a in allowed):
            messagebox.showerror("Invalid File", f"{path} is not a supported type."); return
        var.set(path); widget.configure(text=os.path.basename(path))
    try:
        import tkinterdnd2 as _  # noqa
        widget.drop_target_register("DND_Files"); widget.dnd_bind("<<Drop>>", drop)
        widget.configure(text=widget.cget("text").replace(" (no DnD)", ""))
    except Exception:
        if fallback_browse: widget.bind("<Button-1>", lambda _e: fallback_browse())

# --- Styles ---
def apply_styles(root):
    style = ttk.Style(root)
    try: style.theme_use("clam")
    except Exception: pass
    style.configure("App.TFrame", background=COLORS["bg_dark"])
    style.configure("Card.TFrame", background=COLORS["bg_dark"])
    style.configure("Header.TLabel", background=COLORS["bg_dark"], foreground=COLORS["highlight"], font=("Segoe UI", 32, "bold"))
    style.configure("Field.TLabel", background=COLORS["bg_dark"], foreground=COLORS["text"], font=("Segoe UI", 14))
    style.configure("Drop.TLabel", background=COLORS["card"], foreground=COLORS["text"], font=("Segoe UI", 14), padding=20, relief="ridge")
    style.configure("Menu.TButton", background=COLORS["highlight"], foreground=COLORS["text"], font=("Segoe UI", 14, "bold"), padding=(20, 10))
    style.map("Menu.TButton", background=[("active", COLORS["accent"])])
    style.configure("Primary.TButton", background=COLORS["accent"], foreground=COLORS["text"], font=("Segoe UI", 12), padding=(14, 8))
    style.map("Primary.TButton", background=[("active", COLORS["highlight"])])

# --- App / UI ---
class ReconApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Tradin Recon"); self.geometry("1200x800"); self.configure(bg=COLORS["bg_dark"])
        self.container = ttk.Frame(self, style="App.TFrame"); self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1); self.container.grid_columnconfigure(0, weight=1)
        self.shared = {
            "primary_provider": StringVar(value="CRM"),
            "crm_path": StringVar(value=""),
            "psp_vars": [], "psp_provider_vars": [],
            "psp_count": IntVar(value=1),
            "results": {}, "history": load_history()
        }
        self.frames = {}
        for F in (WelcomePage, SetupPage, RulesPage, ResultsPage, HistoryPage):
            frame = F(parent=self.container, controller=self); self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(WelcomePage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        if hasattr(frame, "refresh"): frame.refresh()
        frame.tkraise()

def header_block(parent, title_text):
    block = ttk.Frame(parent, style="Card.TFrame")
    logo, _ = load_logo_image(parent.winfo_toplevel())
    if logo:
        logo_lbl = ttk.Label(block, image=logo, background=COLORS["bg_dark"])
        logo_lbl.image = logo; logo_lbl.pack(pady=(0, 10))
    ttk.Label(block, text=title_text, style="Header.TLabel").pack()
    return block

class WelcomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Card.TFrame")
        inner = ttk.Frame(self, style="Card.TFrame", padding=40); inner.place(relx=0.5, rely=0.5, anchor="center")
        header = header_block(inner, "TradIn Recon"); header.pack(pady=(0, 30))
        ttk.Button(inner, text="🚀 Start Reconciliation", style="Menu.TButton",
                   command=lambda: controller.show_frame(SetupPage)).pack(pady=8)
        ttk.Button(inner, text="📜 History", style="Menu.TButton",
                   command=lambda: controller.show_frame(HistoryPage)).pack(pady=8)

class SetupPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Card.TFrame"); self.controller = controller
        inner = ttk.Frame(self, style="Card.TFrame", padding=30); inner.place(relx=0.5, rely=0.5, anchor="center")
        header = header_block(inner, "Setup Reconciliation"); header.pack(pady=(0, 20))

        ttk.Label(inner, text="Primary provider:", style="Field.TLabel").pack(pady=(2, 2))
        self.primary_combo = ttk.Combobox(inner, state="readonly", width=18, values=PROVIDER_OPTIONS,
                                          textvariable=controller.shared["primary_provider"]); self.primary_combo.pack()

        self._primary_lbl = ttk.Label(inner, text="Drop Primary File Here", style="Drop.TLabel",
                                      anchor="center", width=44); self._primary_lbl.pack(fill="x", pady=(6, 6))
        def browse_primary():
            p = filedialog.askopenfilename(filetypes=[("Excel/CSV", "*.xlsx;*.xls;*.xlsb;*.csv")])
            if p: controller.shared["crm_path"].set(p); self._primary_lbl.configure(text=os.path.basename(p))
        enable_dnd(self._primary_lbl, controller.shared["crm_path"], [("Excel/CSV", "*.xlsx;*.xls;*.xlsb;*.csv")], fallback_browse=browse_primary)
        ttk.Button(inner, text="Browse Primary", style="Primary.TButton", command=browse_primary).pack(pady=(0, 12))

        ttk.Label(inner, text="How many PSPs?", style="Field.TLabel").pack(pady=(8, 4))
        self.count_combo = ttk.Combobox(inner, textvariable=controller.shared["psp_count"],
                                        values=[1,2,3,4,5,6], state="readonly", width=6); self.count_combo.pack()
        self.count_combo.bind("<<ComboboxSelected>>", lambda _e: self._build_psp_grid())

        self.psp_grid_holder = ttk.Frame(inner, style="Card.TFrame"); self.psp_grid_holder.pack(pady=16, fill="x")
        self._build_psp_grid()

        ttk.Button(inner, text="Next → Run", style="Menu.TButton",
                   command=lambda: controller.show_frame(RulesPage)).pack(pady=(8, 0))
        ttk.Button(inner, text="🏠 Home", style="Menu.TButton",
                   command=lambda: controller.show_frame(WelcomePage)).pack(pady=(8, 0))

    def _build_psp_grid(self):
        for w in self.psp_grid_holder.winfo_children(): w.destroy()
        count = self.controller.shared["psp_count"].get()
        self.controller.shared["psp_vars"] = []; self.controller.shared["psp_provider_vars"] = []
        cols = min(3, count)
        for c in range(cols): self.psp_grid_holder.grid_columnconfigure(c, weight=1)

        for i in range(count):
            file_var = StringVar(value=""); prov_var = StringVar(value="Paymaxis")
            self.controller.shared["psp_vars"].append(file_var)
            self.controller.shared["psp_provider_vars"].append(prov_var)

            block = ttk.Frame(self.psp_grid_holder, style="Card.TFrame", padding=8)
            r, c = divmod(i, cols); block.grid(row=r, column=c, padx=12, pady=12, sticky="n")

            ttk.Label(block, text=f"PSP {i+1} provider:", style="Field.TLabel").pack()
            cb = ttk.Combobox(block, state="readonly", width=18, values=PROVIDER_OPTIONS, textvariable=prov_var); cb.pack(pady=(0,6))

            lbl = ttk.Label(block, text=f"Drop PSP {i+1} File Here", style="Drop.TLabel", anchor="center", width=30); lbl.pack(pady=(0, 6))
            def make_browse(v=file_var, label=lbl):
                def _browse():
                    p = filedialog.askopenfilename(filetypes=[("Excel/CSV", "*.xlsx;*.xls;*.xlsb;*.csv")])
                    if p: v.set(p); label.configure(text=os.path.basename(p))
                return _browse
            enable_dnd(lbl, file_var, [("Excel/CSV","*.xlsx;*.xls;*.xlsb;*.csv")], fallback_browse=make_browse())
            ttk.Button(block, text=f"Browse PSP {i+1}", style="Primary.TButton", command=make_browse()).pack()

class RulesPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Card.TFrame"); self.controller = controller
        inner = ttk.Frame(self, style="Card.TFrame", padding=30); inner.place(relx=0.5, rely=0.5, anchor="center")
        header = header_block(inner, "Run"); header.pack(pady=(0, 20))
        ttk.Button(inner, text="▶ Run Reconciliation", style="Primary.TButton", command=self._run).pack(pady=(6, 12))
        ttk.Button(inner, text="← Back", style="Menu.TButton", command=lambda: controller.show_frame(SetupPage)).pack()
        ttk.Button(inner, text="🏠 Home", style="Menu.TButton", command=lambda: controller.show_frame(WelcomePage)).pack(pady=(8, 0))

    def _run(self):
        c = self.controller; d = c.shared
        try:
            primary_file = d["crm_path"].get()
            if not primary_file or not os.path.exists(primary_file):
                messagebox.showerror("Missing File", "Provide a valid primary file."); return

            expected = d["psp_count"].get()
            files = [v.get() for v in d["psp_vars"] if v.get()]
            if len(files) != expected:
                messagebox.showerror("Missing Files", f"You selected {expected} PSP(s), but provided {len(files)}."); return

            primary_provider = d["primary_provider"].get()
            psp_inputs = []
            for i, v in enumerate(d["psp_vars"]):
                path = v.get(); prov = d["psp_provider_vars"][i].get()
                psp_inputs.append({"name": f"PSP{i+1}", "provider": prov, "path": path})

            rules = load_rules()
            out_path, results = run_recon_logic(primary_file, psp_inputs,
                                                primary_provider=primary_provider,
                                                rules=rules, write_output=True, use_cache=True)
            d["results"] = {"summary": results, "out_path": out_path}
            entry = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "path": out_path}
            d["history"].append(entry); save_history(d["history"])
            c.show_frame(ResultsPage)
        except Exception as e:
            messagebox.showerror("Error", f"{e}\n\n{traceback.format_exc()}")

class ResultsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Card.TFrame"); self.controller = controller
        self._data_by_tab = {}; self._colfiltered_by_tab = {}; self._filtered_by_tab = {}
        self._sort_state = {}; self._col_filter_state = {}; self._col_filter_widgets = {}
        self._last_cell = None

        inner = ttk.Frame(self, style="Card.TFrame", padding=24); inner.pack(fill="both", expand=True)
        header = header_block(inner, "Results"); header.pack(pady=(0, 10))

        fb = ttk.Frame(inner, style="Card.TFrame"); fb.pack(fill="x", pady=(0, 8))
        ttk.Label(fb, text="Column:", style="Field.TLabel").pack(side="left", padx=(0, 6))
        self.col_combo = ttk.Combobox(fb, state="readonly", width=28, values=["(All Columns)"])
        self.col_combo.pack(side="left", padx=(0, 10)); self.col_combo.set("(All Columns)")
        ttk.Label(fb, text="Operator:", style="Field.TLabel").pack(side="left", padx=(0, 6))
        self.op_combo = ttk.Combobox(fb, state="readonly", width=16,
                                     values=["contains","equals","starts with","ends with",">",">=","=","<=","<","!="])
        self.op_combo.pack(side="left", padx=(0, 10)); self.op_combo.set("contains")
        ttk.Label(fb, text="Value:", style="Field.TLabel").pack(side="left", padx=(0, 6))
        self.val_entry = ttk.Entry(fb, width=28); self.val_entry.pack(side="left", padx=(0, 10))
        ttk.Button(fb, text="Apply Filter", style="Primary.TButton", command=self._apply_filter).pack(side="left", padx=(0, 6))
        ttk.Button(fb, text="Clear", style="Primary.TButton", command=self._clear_filter).pack(side="left", padx=(0, 6))
        ttk.Button(fb, text="Clear Col Filters", style="Primary.TButton", command=self._clear_col_filters).pack(side="left", padx=(0, 6))
        ttk.Button(fb, text="Export Filtered", style="Primary.TButton", command=self._export_active).pack(side="left", padx=(0, 6))
        self.count_lbl = ttk.Label(fb, text="", style="Field.TLabel"); self.count_lbl.pack(side="right")

        self.colfilters_holder = ttk.Frame(inner, style="Card.TFrame"); self.colfilters_holder.pack(fill="x", pady=(0, 8))

        self.notebook = ttk.Notebook(inner); self.notebook.pack(fill="both", expand=True, pady=6)
        self.tabs, self.trees = {}, {}
        base_tabs = ["Summary","Recon View","Investigate","OK (Split)","Split Details","Pending"]
        for name in base_tabs:
            frame = ttk.Frame(self.notebook, style="Card.TFrame"); self.notebook.add(frame, text=name)
            self.tabs[name] = frame
            tree = ttk.Treeview(frame, show="headings")
            vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.grid(row=0, column=0, sticky="nsew"); vsb.grid(row=0, column=1, sticky="ns"); hsb.grid(row=1, column=0, sticky="ew")
            frame.grid_rowconfigure(0, weight=1); frame.grid_columnconfigure(0, weight=1)
            self.trees[name] = tree
            tree.bind("<Button-1>", self._remember_click)
            tree.bind("<Button-3>", self._popup_menu)
        self.bind_all("<Control-c>", self._copy_selection)

        btn_frame = ttk.Frame(inner, style="Card.TFrame"); btn_frame.pack(pady=8, fill="x")
        ttk.Button(btn_frame, text="← Back", style="Menu.TButton", command=lambda: controller.show_frame(RulesPage)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🏠 Home", style="Menu.TButton", command=lambda: controller.show_frame(WelcomePage)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Export PowerPoint", style="Primary.TButton", command=self._export_powerpoint).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Reload sources", style="Primary.TButton", command=self._rerun_with_rules).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Mark Pending CRM", style="Primary.TButton", command=self._mark_pending_crm).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Mark Pending PSP", style="Primary.TButton", command=self._mark_pending_psp).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Mark Solved (OK)", style="Primary.TButton", command=self._mark_ok_manual).pack(side="right", padx=5)

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.menu = None

    # copy helpers
    def _remember_click(self, event):
        tree = event.widget
        col_id = tree.identify_column(event.x)
        item_id = tree.identify_row(event.y)
        if not item_id or not col_id: self._last_cell = None; return
        try:
            col_index = int(col_id.replace("#","")) - 1
            col_name = tree["columns"][col_index]
            self._last_cell = (tree, item_id, col_name)
        except Exception:
            self._last_cell = None

    def _copy_selection(self, event=None):
        tree = self.trees.get(self._active_tab_name())
        if not tree: return
        text = ""
        if self._last_cell and self._last_cell[0] is tree:
            _, item_id, col_name = self._last_cell
            try:
                text = str(tree.set(item_id, col_name))
            except Exception:
                text = ""
        if not text:
            sel = tree.selection()
            if sel:
                vals = tree.item(sel[0], "values")
                text = "\t".join(str(v) for v in vals)
        if text:
            try:
                self.clipboard_clear(); self.clipboard_append(text)
            except Exception:
                pass

    def _popup_menu(self, event):
        tree = event.widget; self._remember_click(event)
        if self.menu:
            try: self.menu.unpost()
            except Exception: pass
        self.menu = ttk.Menu(tree, tearoff=0)
        self.menu.add_command(label="Copy cell", command=lambda: self._copy_selection())
        self.menu.add_command(label="Copy row", command=lambda: (self._clear_last_cell(), self._copy_selection()))
        try: self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _clear_last_cell(self):
        self._last_cell = None

    def _ensure_missing_tabs(self, data_dict):
        desired_missing = {k for k in data_dict.keys() if k.startswith("Missing from ")}
        for name, frame in list(self.tabs.items()):
            if name.startswith("Missing from ") and name not in desired_missing:
                try: self.notebook.forget(frame)
                except Exception: pass
                self.tabs.pop(name, None); self.trees.pop(name, None)
        existing = {self.notebook.tab(t, "text") for t in self.notebook.tabs()}
        for k in sorted(desired_missing):
            if k in self.tabs or k in existing: continue
            frame = ttk.Frame(self.notebook, style="Card.TFrame"); self.notebook.add(frame, text=k)
            self.tabs[k] = frame
            tree = ttk.Treeview(frame, show="headings")
            vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.grid(row=0, column=0, sticky="nsew"); vsb.grid(row=0, column=1, sticky="ns"); hsb.grid(row=1, column=0, sticky="ew")
            frame.grid_rowconfigure(0, weight=1); frame.grid_columnconfigure(0, weight=1)
            self.trees[k] = tree
            tree.bind("<Button-1>", self._remember_click)
            tree.bind("<Button-3>", self._popup_menu)

    def refresh(self):
        r = self.controller.shared.get("results", {})
        if not r: return
        data_dict = r.get("summary", {})
        if not isinstance(data_dict, dict): data_dict = {"Summary": data_dict}

        self.meta = data_dict.get("Meta", {"primary_id_label":"Primary ID", "psp_id_label":"PSP ID"})
        self._ensure_missing_tabs(data_dict)

        desired = ["Summary","Recon View","Investigate","OK (Split)","Split Details","Pending"] + \
                  [k for k in data_dict.keys() if k.startswith("Missing from ")]
        self._data_by_tab.clear(); self._colfiltered_by_tab.clear(); self._filtered_by_tab.clear(); self._col_filter_state.clear()
        for name in desired:
            if name == "Meta": continue
            df = data_dict.get(name); df = df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()
            self._data_by_tab[name] = df; self._colfiltered_by_tab[name] = df.copy(); self._filtered_by_tab[name] = df.copy()
            self._col_filter_state[name] = {col: "(All)" for col in df.columns}
            self._render_table(name, df)

        self._sync_filter_controls(); self._rebuild_column_filters(); self._update_count_label()

    def _render_table(self, name, df):
        tree = self.trees.get(name)
        if not tree: return
        tree.delete(*tree.get_children())

        cols = list(df.columns) if isinstance(df, pd.DataFrame) and not df.empty else []

    # >>> Ensure "Status" is the first column
        if "Status" in cols:
            cols = ["Status"] + [c for c in cols if c != "Status"]
    # <<<

        tree["columns"] = cols
        for col in cols:
            tree.heading(col, text=col, command=lambda c=col, n=name: self._sort_by(n, c))
            tree.column(col, width=180, stretch=True)

        if cols:
            for row in df.fillna("").astype(str).values.tolist():
                tree.insert("", "end", values=row)

        if name == self._active_tab_name():
            self._sync_filter_controls()


    def _active_tab_name(self):
        tab_id = self.notebook.select()
        for name, frame in self.tabs.items():
            if str(frame) == tab_id: return name
        return "Recon View"

    def _get_base_df(self, name=None):
        if name is None: name = self._active_tab_name()
        return self._data_by_tab.get(name, pd.DataFrame())

    def _get_active_df(self, filtered=True):
        name = self._active_tab_name()
        return (name, self._filtered_by_tab.get(name, pd.DataFrame())) if filtered else (name, self._colfiltered_by_tab.get(name, pd.DataFrame()))

    def _apply_filter(self):
        name, base = self._get_active_df(filtered=False)
        if base.empty: return
        col = self.col_combo.get(); op = self.op_combo.get(); val = self.val_entry.get()
        df = base.copy()
        try:
            if col == "(All Columns)":
                if val.strip():
                    mask = df.apply(lambda r: r.astype(str).str.contains(val, case=False, na=False).any(), axis=1)
                    df = df[mask]
            else:
                s = df[col]; is_num = pd.api.types.is_numeric_dtype(s)
                if op in [">", ">=", "=", "<=", "<", "!="] and not is_num:
                    s_num = pd.to_numeric(s, errors="coerce"); v_num = pd.to_numeric(pd.Series([val]), errors="coerce").iloc[0]
                    if pd.isna(v_num):
                        if op == "=": df = df[s.astype(str) == str(val)]
                        elif op == "!=": df = df[s.astype(str) != str(val)]
                    else:
                        if op == ">":   df = df[s_num >  v_num]
                        if op == ">=":  df = df[s_num >= v_num]
                        if op == "=":   df = df[s_num == v_num]
                        if op == "<=":  df = df[s_num <= v_num]
                        if op == "<":   df = df[s_num <  v_num]
                        if op == "!=":  df = df[s_num != v_num]
                else:
                    if op == "contains": df = df[s.astype(str).str.contains(val, case=False, na=False)]
                    elif op in ("equals","="): df = df[s == (pd.to_numeric(val, errors="ignore") if is_num else val)]
                    elif op == "starts with": df = df[s.astype(str).str.startswith(val, na=False)]
                    elif op == "ends with":   df = df[s.astype(str).str.endswith(val, na=False)]
                    elif op in [">", ">=", "<=", "<"]:
                        v = pd.to_numeric(val, errors="coerce")
                        if pd.isna(v): df = df.iloc[0:0]
                        else:
                            if op == ">":  df = df[s >  v]
                            if op == ">=": df = df[s >= v]
                            if op == "<=": df = df[s <= v]
                            if op == "<":  df = df[s <  v]
                    elif op == "!=": df = df[s != (pd.to_numeric(val, errors="ignore") if is_num else val)]
        except Exception:
            df = base.copy()
        self._filtered_by_tab[name] = df; self._render_table(name, df); self._update_count_label()

    def _clear_filter(self):
        name, _ = self._get_active_df(filtered=False)
        self.col_combo.set("(All Columns)"); self.op_combo.set("contains"); self.val_entry.delete(0, "end")
        self._filtered_by_tab[name] = self._colfiltered_by_tab.get(name, pd.DataFrame()).copy()
        self._render_table(name, self._filtered_by_tab[name]); self._update_count_label()

    def _export_active(self):
        name, df = self._get_active_df(filtered=True)
        if df.empty: messagebox.showinfo("Export", "Nothing to export."); return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")],
                                            initialfile=f"{name.replace(' ','_')}_filtered.xlsx")
        if not path: return
        try:
            with pd.ExcelWriter(path) as w: df.to_excel(w, sheet_name=name[:31], index=False)
            messagebox.showinfo("Export", f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _clear_col_filters(self):
        name = self._active_tab_name(); base = self._get_base_df(name)
        self._col_filter_state[name] = {col: "(All)" for col in base.columns}
        self._colfiltered_by_tab[name] = base.copy()
        self._rebuild_column_filters(); self._clear_filter()

    def _rebuild_column_filters(self):
        for w in self.colfilters_holder.winfo_children(): w.destroy()
        tab = self._active_tab_name(); base = self._get_base_df(tab)
        if base.empty: return
        self._col_filter_widgets = getattr(self, "_col_filter_widgets", {})
        self._col_filter_widgets[tab] = {}; cols = list(base.columns); max_unique = 200
        def choices_for(series: pd.Series):
            vals = series.astype(str).fillna("").replace({"nan": ""})
            uniq = sorted([v for v in vals.unique().tolist() if v != ""])
            if len(uniq) > max_unique: uniq = uniq[:max_unique]
            return ["(All)", "(Blanks)", "(Non-blanks)"] + uniq
        pairs_per_row = 4; r = c = 0
        for col in cols:
            ttk.Label(self.colfilters_holder, text=col, style="Field.TLabel").grid(row=r, column=c*2, sticky="w", padx=4, pady=2)
            cb = ttk.Combobox(self.colfilters_holder, state="readonly", width=24, values=choices_for(base[col]))
            sel = self._col_filter_state.get(tab, {}).get(col, "(All)")
            if sel not in cb["values"]: sel = "(All)"
            cb.set(sel); cb.grid(row=r, column=c*2+1, sticky="w", padx=4, pady=2)
            cb.bind("<<ComboboxSelected>>", lambda _e, t=tab, column=col: self._on_col_dropdown_change(t, column))
            self._col_filter_widgets[tab][col] = cb; c += 1
            if c >= pairs_per_row: c = 0; r += 1

    def _on_col_dropdown_change(self, tab, column):
        sel = self._col_filter_widgets[tab][column].get()
        self._col_filter_state.setdefault(tab, {})[column] = sel
        self._apply_column_filters_for_tab(tab)

    def _apply_column_filters_for_tab(self, tab):
        base = self._get_base_df(tab)
        if base.empty: return
        state = self._col_filter_state.get(tab, {}); df = base.copy()
        for col, sel in state.items():
            if sel in (None, "(All)"): continue
            s = df[col].astype(str)
            blanks_mask = (s.isna()) | (s == "") | (s.str.lower() == "nan")
            if sel == "(Blanks)": df = df[blanks_mask]
            elif sel == "(Non-blanks)": df = df[~blanks_mask]
            else: df = df[s == sel]
        self._colfiltered_by_tab[tab] = df
        if tab == self._active_tab_name(): self._apply_filter()
        else:
            self._filtered_by_tab[tab] = df; self._render_table(tab, df); self._update_count_label()

    def _sort_by(self, tab_name, col):
        df = self._filtered_by_tab.get(tab_name, pd.DataFrame()).copy()
        if df.empty or col not in df.columns: return
        key = (tab_name, col); asc = not self._sort_state.get(key, True); self._sort_state[key] = asc
        try: df = df.sort_values(by=col, ascending=asc, kind="mergesort")
        except Exception: df = df.sort_values(by=col.astype(str), ascending=asc, kind="mergesort")
        self._filtered_by_tab[tab_name] = df; self._render_table(tab_name, df); self._update_count_label()

    def _sync_filter_controls(self):
        name = self._active_tab_name(); base = self._get_base_df(name)
        cols = ["(All Columns)"] + (list(base.columns) if not base.empty else [])
        self.col_combo["values"] = cols
        if self.col_combo.get() not in cols: self.col_combo.set("(All Columns)")

    def _update_count_label(self):
        name = self._active_tab_name()
        base = self._colfiltered_by_tab.get(name, pd.DataFrame()); cur = self._filtered_by_tab.get(name, pd.DataFrame())
        total = len(base.index) if not base.empty else 0; shown = len(cur.index) if not cur.empty else 0
        self.count_lbl.config(text=f"{name}: {shown} / {total} rows")

    def _get_selected_row(self):
        tree = self.trees.get(self._active_tab_name())
        if not tree: return None
        sel = tree.selection()
        if not sel:
            messagebox.showinfo("Select Row", "Select a row first."); return None
        vals = tree.item(sel[0], "values") or (); cols = list(tree["columns"])
        prim_label = self.controller.shared.get("results",{}).get("summary",{}).get("Meta",{}).get("primary_id_label","Primary ID")
        def v(name):
            try: idx = cols.index(name)
            except ValueError: return ""
            return vals[idx] if idx < len(vals) else ""
        return {"CRM_Ref": v(prim_label), "PSP_Ref": ""}

    def _mark_ok_manual(self):
        row = self._get_selected_row()
        if not row: return
        rules = load_rules(); rules.setdefault("set_status", [])
        if row["CRM_Ref"]:
            rules["set_status"].append({"scope":"crm_ref","id":str(row["CRM_Ref"]),"status":"OK (Manual)","note":"Solved offline"})
        else:
            messagebox.showinfo("Mark Solved", "Row has no primary ID."); return
        save_rules(rules); self._rerun_with_rules()

    def _mark_pending_psp(self):
        messagebox.showinfo("Pending PSP", "Use rules JSON if needed.")

    def _mark_pending_crm(self):
        messagebox.showinfo("Pending CRM", "Use rules JSON if needed.")

    def _rerun_with_rules(self):
        d = self.controller.shared; rules = load_rules()
        primary_file = d["crm_path"].get()
        if not primary_file:
            messagebox.showerror("Reload", "Missing primary file path."); return
        primary_provider = d["primary_provider"].get()
        psp_inputs = []
        for i, v in enumerate(d["psp_vars"]):
            if not v.get(): continue
            psp_inputs.append({"name": f"PSP{i+1}", "provider": d["psp_provider_vars"][i].get(), "path": v.get()})
        def _work():
            try:
                out_path, res = run_recon_logic(primary_file, psp_inputs, primary_provider=primary_provider,
                                                rules=rules, write_output=False, use_cache=True)
                d["results"] = {"summary": res, "out_path": d.get("results",{}).get("out_path","")}
                self.after(0, self.refresh)
            except Exception as e:
                self.after(0, messagebox.showerror, "Reload failed", str(e))
        threading.Thread(target=_work, daemon=True).start()

    def _export_powerpoint(self):
        messagebox.showinfo("Info", "PowerPoint export unchanged in this build.")

    def _on_tab_changed(self, _e):
        self._sync_filter_controls(); self._rebuild_column_filters(); self._update_count_label()

class HistoryPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="Card.TFrame"); self.controller = controller
        inner = ttk.Frame(self, style="Card.TFrame", padding=24); inner.place(relx=0.5, rely=0.5, anchor="center")
        header = header_block(inner, "History"); header.pack(pady=(0, 16))

        self.tree = ttk.Treeview(inner, columns=("date", "path"), show="headings", height=12)
        self.tree.heading("date", text="Date"); self.tree.heading("path", text="Saved File")
        self.tree.column("date", width=180); self.tree.column("path", width=600); self.tree.pack(pady=10)

        btn_frame = ttk.Frame(inner, style="Card.TFrame"); btn_frame.pack(pady=6)
        self.export_btn = ttk.Button(btn_frame, text="Export Again", style="Primary.TButton",
                                     command=self._export_again, state="disabled"); self.export_btn.pack(side="left", padx=5)
        self.delete_btn = ttk.Button(btn_frame, text="Delete", style="Primary.TButton",
                                     command=self._delete_entry, state="disabled"); self.delete_btn.pack(side="left", padx=5)
        ttk.Button(inner, text="🏠 Home", style="Menu.TButton", command=lambda: controller.show_frame(WelcomePage)).pack(pady=10)

        self.tree.bind("<<TreeviewSelect>>", self._on_select); self.refresh()

    def refresh(self):
        d = self.controller.shared
        self.tree.delete(*self.tree.get_children())
        for i, entry in enumerate(d["history"]):
            self.tree.insert("", "end", iid=str(i), values=(entry["date"], entry["path"]))
        self.export_btn.config(state="disabled"); self.delete_btn.config(state="disabled")

    def _on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.export_btn.config(state="normal"); self.delete_btn.config(state="normal")
        else:
            self.export_btn.config(state="disabled"); self.delete_btn.config(state="disabled")

    def _export_again(self):
        selected = self.tree.selection()
        if not selected: return
        idx = int(selected[0]); entry = self.controller.shared["history"][idx]
        try:
            df_dict = pd.read_excel(entry["path"], sheet_name=None, engine="openpyxl")
            out_path = os.path.join(os.getcwd(), f"Recon_ReExport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            with pd.ExcelWriter(out_path) as writer:
                for name, df in df_dict.items(): df.to_excel(writer, sheet_name=name[:31], index=False)
            messagebox.showinfo("Exported", f"Exported again: {out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export again: {e}")

    def _delete_entry(self):
        selected = self.tree.selection()
        if not selected: return
        idx = int(selected[0]); del self.controller.shared["history"][idx]
        save_history(self.controller.shared["history"]); self.refresh()

# --- Main ---
if __name__ == "__main__":
    app = ReconApp(); apply_styles(app); app.mainloop()
