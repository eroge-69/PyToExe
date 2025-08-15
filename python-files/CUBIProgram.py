#!/usr/bin/env python3
# Cubiscan Cleaner — single-file version (GUI + logic) for py-to-exe sites
# Outputs one CSV per SKU with rows RU → PK → PA and columns:
# Site Id, Primary, Length, Width, Height, Weight, Pack Type, Qty, Package

import os, re, math, sys, csv, traceback, threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---- Rules & defaults ----
EXPECTED_COLS = ["Site Id","Primary","Length","Width","Height","Weight","Pack Type","Qty","Package"]
DEFAULTS = {"PK_LEN": 37.5, "PK_WID": 20.3, "PK_HT": 6.7, "RU_WT": 0.24, "PK_QTY": 6}
PALLET = {"L": 120.0, "W": 100.0, "H": 140.0, "VOL": 1.68}
AIM_PREFIX = re.compile(r"^\][A-Za-z0-9]+")

def clean_sku(val: Any) -> str:
    s = "" if val is None else str(val).strip()
    return AIM_PREFIX.sub("", s).strip()

def try_float(x) -> Optional[float]:
    if x is None: return None
    try:
        if isinstance(x, str):
            s = re.sub(r"[^0-9.\-]", "", x)
            if s in ("", ".", "-", "-.", ".-"): return None
            return float(s)
        return float(x)
    except Exception:
        return None

def first_non_empty(seq) -> Optional[str]:
    for v in seq:
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    return None

# ---- CSV helpers (pure standard library) ----
def read_csv_flexible(path: Path) -> Tuple[List[str], List[List[str]]]:
    """Read a CSV with unknown delimiter/quoting; return (header, rows)."""
    data = path.read_bytes()
    sample = data[:4096].decode("utf-8", errors="ignore")
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except Exception:
        class Simple(csv.Dialect):
            delimiter = ","
            quotechar = '"'
            escapechar = None
            doublequote = True
            lineterminator = "\n"
            quoting = csv.QUOTE_MINIMAL
        dialect = Simple
    text = data.decode("utf-8", errors="ignore").splitlines()
    reader = csv.reader(text, dialect)
    rows = list(reader)
    if not rows:
        return [], []
    header = [c.strip() for c in rows[0]]
    return header, rows[1:]

def write_csv(path: Path, rows: List[Dict[str, Any]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=EXPECTED_COLS)
        w.writeheader()
        for r in rows:
            # cast/format
            out = {
                "Site Id": r.get("Site Id",""),
                "Primary": r.get("Primary",""),
                "Length": f"{float(r.get('Length',0)):.2f}" if isinstance(r.get("Length"), (int,float)) or str(r.get("Length")).strip() != "" else "",
                "Width":  f"{float(r.get('Width',0)):.2f}"  if isinstance(r.get("Width"),  (int,float)) or str(r.get("Width")).strip()  != "" else "",
                "Height": f"{float(r.get('Height',0)):.2f}" if isinstance(r.get("Height"), (int,float)) or str(r.get("Height")).strip() != "" else "",
                "Weight": f"{float(r.get('Weight',0)):.2f}" if isinstance(r.get("Weight"), (int,float)) or str(r.get("Weight")).strip() != "" else "",
                "Pack Type": r.get("Pack Type",""),
                "Qty": int(r.get("Qty",0)),
                "Package": r.get("Package",""),
            }
            w.writerow(out)

# ---- Column mapping per file ----
def find_col_idx(header: List[str], keywords: List[str]) -> Optional[int]:
    hlow = [h.lower() for h in header]
    for kw in keywords:
        for i, h in enumerate(hlow):
            if kw in h:
                return i
    return None

def parse_source_rows(csv_path: Path) -> List[Dict[str, Any]]:
    header, rows = read_csv_flexible(csv_path)
    if not header or not rows:
        return []
    # Site Id column
    site_idx = find_col_idx(header, ["site id","site","facility","warehouse"])
    site_default = first_non_empty([r[site_idx] if site_idx is not None and site_idx < len(r) else "" for r in rows])

    # Primary is ALWAYS the second column, per rule (even if named something else)
    primary_idx = 1 if len(header) >= 2 else find_col_idx(header, ["prtnum","primary","item number","itemnumber","itmnum","sku number","sku","item"])
    # Other columns: we’ll try to map flexibly
    len_idx  = find_col_idx(header, ["length","len","l (cm)","l_cm","l"])
    wid_idx  = find_col_idx(header, ["width","wid","w (cm)","w_cm","w"])
    hgt_idx  = find_col_idx(header, ["height","ht","h (cm)","h_cm","h"])
    wgt_idx  = find_col_idx(header, ["weight","wt","gross weight","kg"])
    qty_idx  = find_col_idx(header, ["qty","quantity","pk qty","pack qty","inner qty","units per","units"])
    ptype_idx= find_col_idx(header, ["pack type","packtype","type"])
    pkg_idx  = find_col_idx(header, ["package","pkg","uom","level","packaging"])

    out = []
    for r in rows:
        site = (r[site_idx] if site_idx is not None and site_idx < len(r) else "") or (site_default or "")
        primary_raw = r[primary_idx] if (primary_idx is not None and primary_idx < len(r)) else ""
        primary = clean_sku(primary_raw)
        if not primary:
            continue
        L = try_float(r[len_idx])  if (len_idx  is not None and len_idx  < len(r)) else None
        W = try_float(r[wid_idx])  if (wid_idx  is not None and wid_idx  < len(r)) else None
        H = try_float(r[hgt_idx])  if (hgt_idx  is not None and hgt_idx  < len(r)) else None
        WT= try_float(r[wgt_idx])  if (wgt_idx  is not None and wgt_idx  < len(r)) else None
        Q = try_float(r[qty_idx])  if (qty_idx  is not None and qty_idx  < len(r)) else None
        psrc = (r[ptype_idx].strip().upper() if (ptype_idx is not None and ptype_idx < len(r) and r[ptype_idx] is not None) else "")
        pkg  = (r[pkg_idx].strip()        if (pkg_idx   is not None and pkg_idx   < len(r) and r[pkg_idx]   is not None) else "")
        out.append({
            "Site Id": site, "Primary": primary,
            "Length": L, "Width": W, "Height": H, "Weight": WT, "Qty": Q,
            "Pack Type SRC": psrc, "Package SRC": pkg, "_src_file": str(csv_path)
        })
    return out

# ---- Derive RU → PK → PA for a SKU ----
def derive_rows_for_sku(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not records: return []
    pk_candidates = [r for r in records if r.get("Pack Type SRC") in ("PK","OP")]
    ru_candidates = [r for r in records if r.get("Pack Type SRC") == "RU"]
    pk = pk_candidates[-1] if pk_candidates else records[-1]  # latest wins
    ru_src = ru_candidates[-1] if ru_candidates else None

    site = pk.get("Site Id","")
    L = pk.get("Length");  L = L if (L and L>0) else DEFAULTS["PK_LEN"]
    W = pk.get("Width");   W = W if (W and W>0) else DEFAULTS["PK_WID"]
    H = pk.get("Height");  H = H if (H and H>0) else DEFAULTS["PK_HT"]
    qty = pk.get("Qty");   qty = int(qty) if (qty and qty>0) else int(DEFAULTS["PK_QTY"])
    WT = pk.get("Weight"); WT = WT if (WT and WT>0) else DEFAULTS["RU_WT"]*qty

    # Package cascade: if source PK was OP => "Pack", else keep PK's package (or default to "Pack")
    ptype_src = pk.get("Pack Type SRC","")
    package_all = "Pack" if ptype_src == "OP" else (pk.get("Package SRC") if pk.get("Package SRC") else "Pack")

    # RU: prefer source RU values if present, else cube-root scaling
    if ru_src:
        ruL = ru_src.get("Length")
        ruW = ru_src.get("Width")
        ruH = ru_src.get("Height")
        ruWT= ru_src.get("Weight")
    else:
        ruL=ruW=ruH=ruWT=None

    vol_scale = (1.0/qty) ** (1.0/3.0)
    if not ruL or ruL<=0:  ruL  = L*vol_scale
    if not ruW or ruW<=0:  ruW  = W*vol_scale
    if not ruH or ruH<=0:  ruH  = H*vol_scale
    if not ruWT or ruWT<=0: ruWT = WT/qty if qty else DEFAULTS["RU_WT"]

    pk_cbm = (L*W*H)/1_000_000.0
    packs_per_pallet = max(math.floor(PALLET["VOL"]/pk_cbm), 1)
    pa_qty = packs_per_pallet * qty
    pa_wt = ruWT * pa_qty

    # round to 2dp; Qty int
    ru = {"Site Id": site, "Primary": pk["Primary"],
          "Length": round(ruL,2), "Width": round(ruW,2), "Height": round(ruH,2),
          "Weight": round(ruWT,2), "Pack Type": "RU", "Qty": 1, "Package": package_all}
    pkrow = {"Site Id": site, "Primary": pk["Primary"],
             "Length": round(L,2), "Width": round(W,2), "Height": round(H,2),
             "Weight": round(WT,2), "Pack Type": "PK", "Qty": int(qty), "Package": package_all}
    pa = {"Site Id": site, "Primary": pk["Primary"],
          "Length": PALLET["L"], "Width": PALLET["W"], "Height": PALLET["H"],
          "Weight": round(pa_wt,2), "Pack Type": "PA", "Qty": int(pa_qty), "Package": package_all}
    return [ru, pkrow, pa]

# ---- Processing entry points ----
def process_folder(input_dir: Path, output_dir: Path, consolidated_csv: Optional[Path]=None, report_csv: Optional[Path]=None) -> Tuple[int,int]:
    src_files = sorted([p for p in input_dir.rglob("*.csv")])
    if not src_files: return (0,0)
    raw_by_sku: Dict[str, List[Dict[str, Any]]] = {}
    for p in src_files:
        try:
            for rec in parse_source_rows(p):
                sku = rec.get("Primary","")
                if sku:
                    raw_by_sku.setdefault(sku, []).append(rec)
        except Exception:
            # ignore unreadable file but continue
            continue

    out_count = 0
    consolidated: List[Dict[str, Any]] = []
    report: List[Dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    for sku, recs in raw_by_sku.items():
        rows = derive_rows_for_sku(recs)
        if not rows: continue
        write_csv(output_dir / f"{sku}.csv", rows)
        consolidated.extend(rows)
        # small report
        pk = [r for r in recs if r.get("Pack Type SRC") in ("PK","OP")]
        report.append({"Primary": sku,
                       "PK Source": (pk[-1]["_src_file"] if pk else recs[-1].get("_src_file","")),
                       "PK Qty": rows[1]["Qty"],
                       "Package": rows[0]["Package"]})
        out_count += 1

    if consolidated_csv:
        write_csv(consolidated_csv, consolidated)
    if report_csv:
        # write a simple CSV
        with report_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["Primary","PK Source","PK Qty","Package"])
            w.writeheader()
            for r in sorted(report, key=lambda x: x["Primary"]):
                w.writerow(r)

    return (len(raw_by_sku), out_count)

# ---- Tkinter GUI ----
def launch_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    root = tk.Tk()
    root.title("Cubiscan Cleaner (RU → PK → PA)")
    root.geometry("680x260")
    pad = {"padx":10, "pady":6}

    in_var = tk.StringVar()
    out_var = tk.StringVar()
    cons_var = tk.StringVar()
    rep_var = tk.StringVar()
    status_var = tk.StringVar(value="Ready.")

    def browse_dir(var):
        d = filedialog.askdirectory()
        if d: var.set(d)

    def browse_file_save(var):
        f = filedialog.asksaveasfilename(defaultextension=".csv",
                                         filetypes=[("CSV files","*.csv"),("All files","*.*")])
        if f: var.set(f)

    def run():
        inp, out = in_var.get().strip(), out_var.get().strip()
        cons, rep = cons_var.get().strip(), rep_var.get().strip()
        if not inp or not out:
            messagebox.showwarning("Cubiscan Cleaner", "Select input and output folders.")
            return
        status_var.set("Processing…")
        btn.config(state=tk.DISABLED)

        def job():
            try:
                src = Path(inp); dst = Path(out)
                cons_p = Path(cons) if cons else None
                rep_p = Path(rep) if rep else None
                skus, written = process_folder(src, dst, cons_p, rep_p)
                status_var.set(f"Done. SKUs found: {skus} | Files written: {written}")
                messagebox.showinfo("Cubiscan Cleaner", f"Complete.\nSKUs: {skus}\nFiles written: {written}")
            except Exception as e:
                status_var.set("Error.")
                messagebox.showerror("Cubiscan Cleaner", f"{e}\n\n{traceback.format_exc()}")
            finally:
                btn.config(state=tk.NORMAL)

        threading.Thread(target=job, daemon=True).start()

    # Layout
    ttk.Label(root, text="Input folder (raw CSVs):").grid(row=0, column=0, sticky="w", **pad)
    ttk.Entry(root, textvariable=in_var, width=60).grid(row=0, column=1, **pad)
    ttk.Button(root, text="Browse", command=lambda: browse_dir(in_var)).grid(row=0, column=2, **pad)

    ttk.Label(root, text="Output folder (per-SKU CSVs):").grid(row=1, column=0, sticky="w", **pad)
    ttk.Entry(root, textvariable=out_var, width=60).grid(row=1, column=1, **pad)
    ttk.Button(root, text="Browse", command=lambda: browse_dir(out_var)).grid(row=1, column=2, **pad)

    ttk.Label(root, text="(Optional) Consolidated CSV:").grid(row=2, column=0, sticky="w", **pad)
    ttk.Entry(root, textvariable=cons_var, width=60).grid(row=2, column=1, **pad)
    ttk.Button(root, text="Choose", command=lambda: browse_file_save(cons_var)).grid(row=2, column=2, **pad)

    ttk.Label(root, text="(Optional) Report CSV:").grid(row=3, column=0, sticky="w", **pad)
    ttk.Entry(root, textvariable=rep_var, width=60).grid(row=3, column=1, **pad)
    ttk.Button(root, text="Choose", command=lambda: browse_file_save(rep_var)).grid(row=3, column=2, **pad)

    btn = ttk.Button(root, text="Run", command=run)
    btn.grid(row=4, column=0, columnspan=3, pady=12)

    ttk.Label(root, textvariable=status_var, foreground="gray").grid(row=5, column=0, columnspan=3, sticky="w", **pad)

    root.resizable(False, False)
    root.mainloop()

# ---- CLI support ----
def main():
    if len(sys.argv) >= 3:
        inp = Path(sys.argv[1]); out = Path(sys.argv[2])
        cons = Path(sys.argv[3]) if len(sys.argv) >= 4 and sys.argv[3] != "-" else None
        rep  = Path(sys.argv[4]) if len(sys.argv) >= 5 and sys.argv[4] != "-" else None
        skus, written = process_folder(inp, out, cons, rep)
        print(f"Done. SKUs: {skus}, files written: {written}")
    else:
        launch_gui()

if __name__ == "__main__":
    main()
