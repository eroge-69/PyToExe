
import streamlit as st
import pandas as pd
import io
import csv
from datetime import datetime

st.set_page_config(page_title="Woo CSV Merger", page_icon="🛒", layout="wide")

# ----------------------------
# إعدادات عامة وملفات المساعدة
# ----------------------------
DESIRED_FIELDS = ["Title","Category","Short Description","Long Description","Tags","Price","Image Prompt"]

WOO_EXTRA = {
    "Type": "simple",
    "Published": 1,
    "In stock?": 1,
    "Backorders allowed?": 0,
    "Sold individually?": 0,
    "Allow customer reviews?": 1,
    "Tax status": "none",
    "Downloadable": 1,
    "Virtual": 1,
    "Stock": "",
    "SKU": "",
    "Sale price": "",
    "Regular price": "",
    "Images": "",
    "Parent": "",
    "Visibility in catalog": "visible",
    "Position": 0,
    "Date sale price starts": "",
    "Date sale price ends": "",
    "Tax class": "",
    "Low stock amount": "",
    "Sold individually": 0,
    "Weight (kg)": "",
    "Length (cm)": "",
    "Width (cm)": "",
    "Height (cm)": "",
    "Allow backorders?": "no",
    "Categories": "",
    "Tags": "",
    "Shipping class": "",
    "Download limit": "",
    "Download expiry days": "",
    "Parent SKU": "",
    "Grouped products": "",
    "Upsells": "",
    "Cross-sells": "",
    "External URL": "",
    "Button text": "",
    "Meta: ai_image_prompt": ""
}

COLUMN_ALIASES = {
    "title": "Title",
    "name": "Title",
    "product_name": "Title",
    "category": "Category",
    "categories": "Category",
    "short description": "Short Description",
    "short_description": "Short Description",
    "excerpt": "Short Description",
    "long description": "Long Description",
    "long_description": "Long Description",
    "description": "Long Description",
    "tags": "Tags",
    "keywords": "Tags",
    "price": "Price",
    "regular price": "Price",
    "regular_price": "Price",
    "image prompt": "Image Prompt",
    "image_prompt": "Image Prompt",
    "prompt": "Image Prompt",
}

def normalize_columns(df: pd.DataFrame):
    mapping = {}
    for col in df.columns:
        key = str(col).strip()
        lower = key.lower().strip()
        mapping[col] = COLUMN_ALIASES.get(lower, key)
    return df.rename(columns=mapping)

def auto_sep(sample: bytes):
    # Try to guess delimiter
    text = sample.decode("utf-8", errors="ignore")
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(text[:5000], delimiters=[",",";","|","\t"])
        return dialect.delimiter
    except Exception:
        return ","

def merge_frames(frames):
    if not frames:
        return pd.DataFrame(columns=DESIRED_FIELDS)
    df = pd.concat(frames, ignore_index=True)
    # Keep only desired fields if they exist
    for f in DESIRED_FIELDS:
        if f not in df.columns:
            df[f] = ""
    # Order columns
    df = df[DESIRED_FIELDS + [c for c in df.columns if c not in DESIRED_FIELDS]]
    return df

def to_woo(df, add_extra=True):
    out = df.copy()
    # Map basic Woo fields
    out["Name"] = out["Title"]
    out["Categories"] = out["Category"]
    out["Short description"] = out["Short Description"]
    out["Description"] = out["Long Description"]
    out["Regular price"] = out["Price"]
    out["Tags"] = out["Tags"]
    out["Meta: ai_image_prompt"] = out["Image Prompt"]
    out["Downloadable"] = 1
    out["Virtual"] = 1
    out["Type"] = "simple"
    # Reorder for Woo's common template
    woo_order = ["Name","Type","Published","Is featured?","Visibility in catalog","Short description","Description","SKU","Regular price","Sale price","Categories","Tags","Images","Downloadable","Virtual","Allow customer reviews?","Tax status","Stock"]
    for k, v in WOO_EXTRA.items():
        if k not in out.columns:
            out[k] = v
    # Ensure numeric price formatting
    try:
        out["Regular price"] = pd.to_numeric(out["Regular price"], errors="coerce").fillna("")
    except Exception:
        pass
    preferred = []
    for col in woo_order:
        if col in out.columns:
            preferred.append(col)
    # Then append remaining columns
    rest = [c for c in out.columns if c not in preferred]
    out = out[preferred + rest]
    return out

st.markdown("## 🛒 أداة دمج ملفات CSV للمنتجات الرقمية — WooCommerce")
st.caption("ارفع عدة ملفات CSV تحتوي على أعمدة: Title, Category, Short Description, Long Description, Tags, Price, Image Prompt. سنقوم بدمجها، إزالة التكرارات اختياريًا، وتجهيز ملف واحد للاستيراد في WooCommerce.")

# Sidebar options
with st.sidebar:
    st.header("الإعدادات")
    encoding = st.selectbox("ترميز الملفات", ["utf-8-sig","utf-8","cp1256","cp1252","iso-8859-1"], index=0)
    sep_choice = st.selectbox("محدد الأعمدة", ["Auto", ",",";","|","Tab (\\t)"], index=0)
    dedupe = st.checkbox("إزالة التكرارات (حسب Title + Category)", value=True)
    keep_last = st.checkbox("عند التكرار احتفظ بآخر صف (حسب عمود تاريخ إن وجد)", value=True)
    add_woo = st.checkbox("تجهيز أعمدة WooCommerce الإضافية", value=True)
    st.markdown("---")
    st.markdown("**نصائح:** إذا كان الملف لا يفتح بشكل صحيح، جرّب تغيير الترميز أو محدد الأعمدة.")

uploaded = st.file_uploader("ارفع ملفات CSV", type=["csv"], accept_multiple_files=True, help="يمكنك سحب وإفلات عدة ملفات مرة واحدة.")

frames = []
errors = []

if uploaded:
    for f in uploaded:
        try:
            raw = f.read()
            # detect sep
            if sep_choice == "Auto":
                sep = auto_sep(raw)
            else:
                sep = {"Tab (\\t)": "\t"}.get(sep_choice, sep_choice)
            df = pd.read_csv(io.BytesIO(raw), encoding=encoding, sep=sep)
            df = normalize_columns(df)
            frames.append(df)
        except Exception as e:
            errors.append(f"فشل قراءة الملف {f.name}: {e}")

    if errors:
        st.error("\\n".join(errors))

    if frames:

        st.subheader("معاينة وتحرير كل ملف")
        for i, (f, df) in enumerate(zip(uploaded, frames)):
            with st.expander(f"📄 {f.name}"):
                st.write(f"عدد الصفوف: **{len(df)}** | الأعمدة: {list(df.columns)}")
                st.dataframe(df.head(200), use_container_width=True)

        merged = merge_frames(frames)

        st.markdown("---")
        st.subheader("🧾 تحرير البيانات المدمجة قبل التصدير")
        st.caption("يمكنك تعديل القيم مباشرة داخل الجدول، إضافة/حذف صفوف، أو تصحيح الأسعار والأوصاف.")
        edited = st.data_editor(
            merged,
            use_container_width=True,
            num_rows="dynamic",
            key="editor_merged"
        )

        # dedupe
        if dedupe:
            subset_cols = [c for c in ["Title","Category"] if c in edited.columns]
            if subset_cols:
                if keep_last:
                    # Try to find a date column
                    date_cols = [c for c in edited.columns if "modified" in c.lower() or "update" in c.lower() or "date" in c.lower()]
                    if date_cols:
                        col = date_cols[0]
                        edited["_sort_dt"] = pd.to_datetime(edited[col], errors="coerce")
                        edited = edited.sort_values("_sort_dt").drop(columns=["_sort_dt"])
                edited = edited.drop_duplicates(subset=subset_cols, keep="last" if keep_last else "first")

        # Prepare Woo sheet
        final_df = to_woo(edited, add_extra=add_woo) if add_woo else edited

        st.markdown("---")
        st.subheader("النتيجة الجاهزة للتنزيل")
        st.write(f"عدد المنتجات بعد التحرير: **{len(final_df)}**")
        buf = io.StringIO()
        final_df.to_csv(buf, index=False)
        st.download_button("⬇️ تنزيل CSV المدمج", data=buf.getvalue().encode("utf-8-sig"), file_name=f"woo_merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")

        st.markdown("### إعادة ترتيب/إخفاء الأعمدة (اختياري)")
        cols = list(final_df.columns)
        selected = st.multiselect("اختر الأعمدة التي تريد إبقاءها في ملف التصدير", cols, default=cols)
        if selected:
            buf2 = io.StringIO()
            final_df[selected].to_csv(buf2, index=False)
            st.download_button("⬇️ تنزيل CSV مع الأعمدة المحددة", data=buf2.getvalue().encode("utf-8-sig"), file_name=f"woo_merged_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")

else:
    st.info("ابدأ برفع ملف أو أكثر بصيغة CSV.")
