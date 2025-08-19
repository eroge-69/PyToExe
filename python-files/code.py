#!/usr/bin/env python3
"""
bom_inventory_compare.py  (updated with price columns)

Compare a BOM and an Inventory and produce a 3rd Excel "comparison" sheet.

- Inputs: 2 files (CSV or Excel): Inventory and BOM.
- Output: Excel file with the "comparison" sheet.

Column expectations (case-insensitive; extra spaces ignored; basic synonyms supported):

Inventory (excel1):
    "Item name", "part Desc"/"description", "notes", "QTY."/ "qty"/"quantity", "location",
    "suppliers"/"supplier", "Manufacturer", "Price (usd)", "Price (euro)", "Price (dkk)", "Supplier Number"

BOM (excel2):
    "Title"/"Component", "Quantity"/"Qty", "Maturity State", "Supplier Number", "Supplier",
    "Make Or Buy", "long Lead", "Bookmark", "Collaborative Space", "description"

Output columns ("comparison"):
    Component name (BOM)
    Supplier number
    Supplier or manufacturer (from both)
    Buy or make (from BOM)
    QTY in stock (from inventory)
    QTY required (from BOM)
    Should buy?
    How many to buy
    Price USD (inventory)
    Price EUR (inventory)
    Price DKK (inventory)
    Description (from both)

Matching logic (lightly "smart" / fuzzy):
- Prefer exact Supplier Number match; otherwise fall back to best Title match by normalized string similarity.
- Merge Supplier/Manufacturer names, collapsing near-duplicates.
- Merge BOM+Inventory descriptions, removing repeated/near-duplicate fragments.
- QTY in stock sums all inventory rows matching Supplier Number (preferred) or best title match if Supplier Number missing.
- Should buy? = "Y" if stock < required, else "N".
- How many to buy = max(required - stock, 0).

Usage:
    python bom_inventory_compare.py --inventory path/to/inventory.xlsx --bom path/to/bom.csv --out comparison.xlsx

Requires: pandas, openpyxl (for writing xlsx)
"""

import argparse
import os
import re
import unicodedata
from typing import List, Tuple, Optional

import pandas as pd
from difflib import SequenceMatcher


# -------- Utilities --------

def _norm(s: Optional[str]) -> str:
    """Normalize strings for fuzzy matching (lowercase, remove accents, punctuation, extra spaces)."""
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    if not isinstance(s, str):
        s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^\w]+", " ", s)     # replace punctuation with space
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _similar(a: str, b: str) -> float:
    """Similarity ratio between two normalized strings (0..1)."""
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _coalesce_columns(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Return the first existing column (case/space-insensitive) from candidates. Rename it to the first name."""
    mapping = { _norm(col): col for col in df.columns }
    for cand in candidates:
        key = _norm(cand)
        if key in mapping:
            actual = mapping[key]
            if actual != cand and cand not in df.columns:
                df.rename(columns={actual: cand}, inplace=True)
            return cand
    return None


def _read_table(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    elif ext in [".csv", ".tsv"]:
        sep = "," if ext == ".csv" else "\t"
        return pd.read_csv(path, sep=sep)
    else:
        # Fallback to CSV
        return pd.read_csv(path)


def _safe_int(x) -> int:
    try:
        if pd.isna(x):
            return 0
        if isinstance(x, str):
            m = re.search(r"-?\d+", x.replace(",", ""))
            if m:
                return int(m.group(0))
            return 0
        return int(round(float(x)))
    except Exception:
        return 0


def _safe_money(x) -> Optional[float]:
    """Parse money like '$12.50', '12,50 DKK', '€9.99', '1,234.56' -> float. Return None if not parseable."""
    try:
        if x is None or (isinstance(x, float) and pd.isna(x)):
            return None
        if isinstance(x, str):
            s = x.strip().replace("\u00A0", " ")  # non-breaking space
            # remove currency words/symbols
            s = s.lower().replace("dkk", "").replace("eur", "").replace("usd", "")
            s = s.replace("$", "").replace("€", "").replace("kr", "")
            s = s.strip()
            # handle formats:
            # 1) european comma decimals: 123,45
            if re.fullmatch(r"-?\d+,\d{1,2}", s):
                s = s.replace(",", ".")
                return float(s)
            # 2) thousand sep commas: 1,234.56
            s = s.replace(",", "")
            return float(s)
        return float(x)
    except Exception:
        return None


def _merge_near_duplicates(values: List[str], sim_threshold: float = 0.88) -> str:
    """Merge strings, collapsing near-duplicates by similarity threshold."""
    cleaned = [v for v in (v.strip() for v in values if isinstance(v, str)) if v]
    kept: List[str] = []
    for v in cleaned:
        if not any(_similar(v, k) >= sim_threshold for k in kept):
            kept.append(v)
    return " / ".join(kept) if kept else ""


def _merge_descriptions(descs: List[str]) -> str:
    """
    Merge descriptions, removing repeated parts by sentence/phrase similarity.
    Uses a moderate similarity threshold to collapse overlaps.
    """
    parts: List[str] = []
    for d in descs:
        if not isinstance(d, str):
            continue
        for p in re.split(r"[.;\n]| - | \u2022 ", d):
            p = p.strip(" -•\u2022\t\r ")
            if p:
                parts.append(p)
    merged: List[str] = []
    for p in parts:
        if not any(_similar(p, q) >= 0.9 for q in merged):
            merged.append(p)
    return "; ".join(merged[:20])  # cap to avoid runaway size


# -------- Core logic --------

def prepare_inventory(df_inv: pd.DataFrame) -> pd.DataFrame:
    # Standardize columns
    name_col = _coalesce_columns(df_inv, ["Item name", "item", "title", "component"])
    desc_col = _coalesce_columns(df_inv, ["part Desc", "description", "desc"])
    notes_col = _coalesce_columns(df_inv, ["notes", "note"])
    qty_col  = _coalesce_columns(df_inv, ["QTY.", "qty", "quantity", "stock", "on hand"])
    _ = _coalesce_columns(df_inv, ["location", "bin", "shelf"])  # not used downstream but ok to normalize
    supp_col = _coalesce_columns(df_inv, ["suppliers", "supplier"])
    manu_col = _coalesce_columns(df_inv, ["Manufacturer", "maker", "brand"])
    suppnum_col = _coalesce_columns(df_inv, ["Supplier Number", "supplier no", "supplier id", "part number", "pn"])

    price_usd_col = _coalesce_columns(df_inv, ["Price (usd)", "price usd", "usd price", "unit price usd", "usd"])
    price_eur_col = _coalesce_columns(df_inv, ["Price (euro)", "price (eur)", "price eur", "eur price", "euro price", "eur"])
    price_dkk_col = _coalesce_columns(df_inv, ["Price (dkk)", "price dkk", "dkk price", "kr price", "dkk"])

    # Normalized/fallback fields
    df_inv["__norm_title"] = df_inv[name_col].apply(_norm) if name_col else ""
    df_inv["__qty"] = df_inv[qty_col].apply(_safe_int) if qty_col else 0

    df_inv["__supplier"] = df_inv[supp_col] if supp_col else ""
    df_inv["__manufacturer"] = df_inv[manu_col] if manu_col else ""
    df_inv["__desc"] = df_inv[desc_col] if desc_col else ""
    df_inv["__notes"] = df_inv[notes_col] if notes_col else ""
    df_inv["__supplier_number"] = df_inv[suppnum_col] if suppnum_col else ""
    df_inv["__title"] = df_inv[name_col] if name_col else ""

    # Prices as floats (None if missing)
    df_inv["__price_usd"] = df_inv[price_usd_col].apply(_safe_money) if price_usd_col else None
    df_inv["__price_eur"] = df_inv[price_eur_col].apply(_safe_money) if price_eur_col else None
    df_inv["__price_dkk"] = df_inv[price_dkk_col].apply(_safe_money) if price_dkk_col else None

    return df_inv


def prepare_bom(df_bom: pd.DataFrame) -> pd.DataFrame:
    title_col = _coalesce_columns(df_bom, ["Title", "Component", "Item name", "item"])
    qty_col   = _coalesce_columns(df_bom, ["Quantity", "qty", "required"])
    _ = _coalesce_columns(df_bom, ["Maturity State", "maturity"])
    suppnum_col = _coalesce_columns(df_bom, ["Supplier Number", "supplier no", "supplier id", "part number", "pn"])
    supp_col  = _coalesce_columns(df_bom, ["Supplier", "suppliers"])
    mob_col   = _coalesce_columns(df_bom, ["Make Or Buy", "make or buy", "buy or make", "mob"])
    _ = _coalesce_columns(df_bom, ["long Lead", "long lead", "lead"])
    _ = _coalesce_columns(df_bom, ["Bookmark"])
    _ = _coalesce_columns(df_bom, ["Collaborative Space"])
    desc_col  = _coalesce_columns(df_bom, ["description", "part Desc", "desc"])

    df_bom["__norm_title"] = df_bom[title_col].apply(_norm) if title_col else ""
    df_bom["__qty_req"] = df_bom[qty_col].apply(_safe_int) if qty_col else 0
    df_bom["__supplier_number"] = df_bom[suppnum_col] if suppnum_col else ""
    df_bom["__supplier"] = df_bom[supp_col] if supp_col else ""
    df_bom["__mob"] = df_bom[mob_col] if mob_col else ""
    df_bom["__title"] = df_bom[title_col] if title_col else ""
    df_bom["__desc"] = df_bom[desc_col] if desc_col else ""

    return df_bom


def find_inventory_match(row_bom: pd.Series, df_inv: pd.DataFrame) -> Tuple[int, Optional[pd.Series]]:
    """
    Return (stock_qty, best_inventory_row_or_None) for a BOM row.
    Prefer exact Supplier Number match; fall back to best title similarity if needed.
    """
    suppnum = str(row_bom["__supplier_number"]).strip()
    if suppnum and suppnum != "nan":
        subset = df_inv[df_inv["__supplier_number"].astype(str).str.strip() == suppnum]
        if len(subset) > 0:
            stock = int(subset["__qty"].sum())
            best_row = subset.sort_values("__qty", ascending=False).iloc[0]
            return stock, best_row

    # Fallback: best fuzzy title match
    if row_bom["__norm_title"]:
        df_tmp = df_inv.copy()
        df_tmp["__sim"] = df_tmp["__norm_title"].apply(lambda x: SequenceMatcher(None, x, row_bom["__norm_title"]).ratio())
        best = df_tmp.sort_values("__sim", ascending=False).head(1)
        if len(best) and best["__sim"].iloc[0] >= 0.75:
            best_row = best.iloc[0]
            stock = int(best_row["__qty"])
            return stock, best_row

    return 0, None


def build_comparison(df_bom: pd.DataFrame, df_inv: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, r in df_bom.iterrows():
        stock, inv_row = find_inventory_match(r, df_inv)

        # Supplier/manufacturer merge
        suppliers = [str(r["__supplier"])]
        if inv_row is not None:
            suppliers += [str(inv_row.get("__supplier", "")), str(inv_row.get("__manufacturer", ""))]
        merged_supplier = _merge_near_duplicates(suppliers, sim_threshold=0.88)

        # Description merge
        descs = [str(r["__desc"])]
        if inv_row is not None:
            descs += [str(inv_row.get("__desc", "")), str(inv_row.get("__notes", ""))]
        merged_desc = _merge_descriptions(descs)

        required = _safe_int(r["__qty_req"])
        should_buy = "Y" if stock < required else "N"
        buy_qty = max(required - stock, 0) if should_buy == "Y" else 0

        # Prices: from inventory if a match exists; no currency conversion
        price_usd = inv_row.get("__price_usd", None) if inv_row is not None else None
        price_eur = inv_row.get("__price_eur", None) if inv_row is not None else None
        price_dkk = inv_row.get("__price_dkk", None) if inv_row is not None else None

        records.append({
            "Component name (BOM)": r["__title"],
            "Supplier number": str(r["__supplier_number"]).strip() if str(r["__supplier_number"]) != "nan" else "",
            "Supplier or manufacturer (from both)": merged_supplier,
            "Buy or make (from BOM)": r["__mob"],
            "QTY in stock (from inventory)": stock,
            "QTY required (from BOM)": required,
            "Should buy?": should_buy,
            "How many to buy": buy_qty if should_buy == "Y" else 0,
            "Price USD (inventory)": price_usd if price_usd is not None else "",
            "Price EUR (inventory)": price_eur if price_eur is not None else "",
            "Price DKK (inventory)": price_dkk if price_dkk is not None else "",
            "Description (from both)": merged_desc
        })
    return pd.DataFrame.from_records(records)


def main():
    ap = argparse.ArgumentParser(description="Compare BOM and Inventory and export a comparison Excel.")
    ap.add_argument("--inventory", "-i", required=True, help="Path to Inventory file (CSV or Excel)")
    ap.add_argument("--bom", "-b", required=True, help="Path to BOM file (CSV or Excel)")
    ap.add_argument("--out", "-o", required=True, help="Path to output Excel file")
    args = ap.parse_args()

    df_inv = _read_table(args.inventory)
    df_bom = _read_table(args.bom)

    df_inv = prepare_inventory(df_inv)
    df_bom = prepare_bom(df_bom)

    comparison = build_comparison(df_bom, df_inv)

    # Ensure column order
    cols = [
        "Component name (BOM)",
        "Supplier number",
        "Supplier or manufacturer (from both)",
        "Buy or make (from BOM)",
        "QTY in stock (from inventory)",
        "QTY required (from BOM)",
        "Should buy?",
        "How many to buy",
        "Price USD (inventory)",
        "Price EUR (inventory)",
        "Price DKK (inventory)",
        "Description (from both)",
    ]
    comparison = comparison[cols]

    # Write Excel
    with pd.ExcelWriter(args.out, engine="openpyxl") as writer:
        comparison.to_excel(writer, index=False, sheet_name="comparison")

    print(f"✅ Wrote comparison to: {args.out}")


if __name__ == "__main__":
    main()
