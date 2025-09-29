# -*- coding: utf-8 -*-
"""
Product CSV Importer — EN (Minimal Fields)
-----------------------------------------
Streamlit GUI to **import product data from CSV** (no auto-generation) and export a
**WooCommerce-ready CSV**. UI and columns are fully in English.

SUPPORTED FIELDS (per product row):
- Title
- Category
- Short Description
- Long Description
- Tags (comma-separated)
- Price
- Image Prompt (kept for your workflow; not exported to WooCommerce but available in UI/exportable as a separate CSV if needed)

Run:
  pip install streamlit pandas
  python -m streamlit run app.py

Notes:
- Input CSV must have exactly the columns above (case-sensitive). You can download a template from the sidebar.
- Exported WooCommerce CSV contains the minimal required columns + sensible defaults for downloadable/virtual products.
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st
import pandas as pd

APP_NAME = "Product CSV Importer — EN (Minimal Fields)"

# ============================
# Woo mapping (minimal columns)
# ============================

def to_woocommerce_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Map our minimal fields to WooCommerce import CSV columns."""
    return {
        # Core
        "Name": row.get("Title", "Untitled"),
        "Type": "simple",
        "Published": 1,
        "Is featured?": 0,
        "Visibility in catalog": "visible",

        # Content
        "Short description": row.get("Short Description", ""),
        "Description": row.get("Long Description", ""),

        # Pricing
        "Regular price": row.get("Price", ""),
        "Sale price": "",

        # Tax / Inventory / Shipping (left neutral)
        "Tax status": "none",
        "In stock?": 1,
        "Stock": "",
        "Backorders allowed?": 0,
        "Sold individually?": 0,
        "Shipping class": "",

        # Categorization
        "Categories": row.get("Category", ""),
        "Tags": row.get("Tags", ""),

        # Media / Downloads (left empty for now)
        "Images": "",
        "Downloadable": 1,
        "Virtual": 1,
        "Download 1 name": row.get("Title", "File"),
        "Download 1 URL": "",

        # SEO (optional; not part of minimal set)
        "Meta: _yoast_wpseo_title": "",
        "Meta: _yoast_wpseo_metadesc": "",

        # Slug/SKU omitted (Woo will generate if missing)
        "SKU": "",
        "Slug": "",

        # Misc
        "Position": 0,
    }

INPUT_COLUMNS = [
    "Title",
    "Category",
    "Short Description",
    "Long Description",
    "Tags",
    "Price",
    "Image Prompt",
]


def template_df() -> pd.DataFrame:
    return pd.DataFrame([{c: "" for c in INPUT_COLUMNS}])

# ============================
# UI
# ============================
st.set_page_config(page_title=APP_NAME, page_icon="📄", layout="wide")

st.title("📄 Product CSV Importer — Minimal Fields (EN)")
st.caption("Import product rows from CSV (Title, Category, Short/Long Description, Tags, Price, Image Prompt). Review/edit and export a WooCommerce-ready CSV.")

with st.sidebar:
    st.header("Template & Help")
    if st.button("⬇️ Download Empty Template"):
        st.download_button(
            label="Download template.csv",
            data=template_df().to_csv(index=False).encode("utf-8-sig"),
            file_name="products_template_en.csv",
            mime="text/csv",
        )
    st.markdown("""
**Input CSV columns (exact names):**
- Title
- Category
- Short Description
- Long Description
- Tags (comma-separated)
- Price
- Image Prompt (kept for your workflow)
""")

if "items" not in st.session_state:
    st.session_state["items"] = []  # each is a dict with the 7 minimal fields

uploaded_csv = st.file_uploader("Upload CSV file(s)", type=["csv"], accept_multiple_files=True)

if uploaded_csv:
    for f in uploaded_csv:
        try:
            df = pd.read_csv(f, encoding="utf-8")
        except Exception:
            f.seek(0)
            df = pd.read_csv(f, encoding="utf-8-sig")
        missing = [c for c in INPUT_COLUMNS if c not in df.columns]
        if missing:
            st.error(f"Missing columns in {f.name}: {', '.join(missing)}")
        else:
            st.session_state["items"].extend(df.fillna("").to_dict(orient="records"))
            st.success(f"Imported {len(df)} rows from {f.name}")

# Render & edit
if st.session_state["items"]:
    st.markdown("### Imported Items")
    for idx, it in enumerate(st.session_state["items"]):
        with st.expander(f"✦ {it.get('Title','(Untitled)')}"):
            c1, c2 = st.columns(2)
            with c1:
                it["Title"] = st.text_input("Title", value=it.get("Title",""), key=f"title_{idx}")
                it["Category"] = st.text_input("Category", value=it.get("Category",""), key=f"cat_{idx}")
                it["Price"] = st.text_input("Price", value=str(it.get("Price","")), key=f"price_{idx}")
            with c2:
                it["Tags"] = st.text_input("Tags (comma-separated)", value=it.get("Tags",""), key=f"tags_{idx}")
                it["Image Prompt"] = st.text_area("Image Prompt", value=it.get("Image Prompt",""), height=100, key=f"ip_{idx}")
            it["Short Description"] = st.text_area("Short Description", value=it.get("Short Description",""), height=120, key=f"sd_{idx}")
            it["Long Description"] = st.text_area("Long Description", value=it.get("Long Description",""), height=220, key=f"ld_{idx}")

    st.markdown("---")
    # Build Woo rows for preview/export
    woo_rows = [to_woocommerce_row(it) for it in st.session_state["items"]]
    df_out = pd.DataFrame(woo_rows)

    st.markdown("### Preview & Export (WooCommerce CSV)")
    st.data_editor(df_out, use_container_width=True, num_rows="dynamic", key="preview_editor")

    if st.button("⬇️ Download WooCommerce CSV"):
        csv_bytes = df_out.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="Download WooCommerce CSV",
            data=csv_bytes,
            file_name=f"woocommerce_products_{int(time.time())}.csv",
            mime="text/csv",
        )

    # Optional: Export the minimal fields back out (including Image Prompt)
    st.markdown("#### (Optional) Download Back the Minimal Fields CSV")
    df_min = pd.DataFrame(st.session_state["items"])  # retains Image Prompt
    st.download_button(
        label="Download Minimal Fields CSV",
        data=df_min.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"products_minimal_{int(time.time())}.csv",
        mime="text/csv",
    )

    # Save/Restore session
    st.markdown("#### Session Save / Restore")
    sess = {"items": st.session_state["items"], "ts": datetime.utcnow().isoformat()}
    st.download_button("💾 Download Session (.json)", data=json.dumps(sess, ensure_ascii=False).encode("utf-8"), file_name="products_session.json", mime="application/json")
    up_sess = st.file_uploader("Restore Session (.json)", type=["json"], key="sess_upl")
    if up_sess is not None:
        try:
            content = json.loads(up_sess.read().decode("utf-8"))
            if "items" in content:
                st.session_state["items"] = content["items"]
                st.success("Session restored.")
        except Exception:
            st.error("Failed to read the session file.")
else:
    st.info("Upload your CSV to start. Use the template from the sidebar to match the exact columns.")
