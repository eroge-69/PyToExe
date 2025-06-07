import streamlit as st
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import os
import io
import json
import shutil
import zipfile
from streamlit_drawable_canvas import st_canvas

# === Utility Functions ===
def save_image(data, path):
    with open(path, 'wb') as f:
        f.write(data)

def compress_image(image_rgb, min_kb, max_kb):
    img = Image.fromarray(image_rgb)
    quality = 95
    while quality >= 10:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        size_kb = len(buffer.getvalue()) / 1024
        if min_kb <= size_kb <= max_kb:
            return buffer.getvalue()
        quality -= 5
    return buffer.getvalue()

def remove_white_border(img_bgr, tighter=False):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return img_bgr
    x, y, w, h = cv2.boundingRect(np.vstack(contours))
    pad = 3 if tighter else 5
    return img_bgr[max(y - pad, 0):min(y + h + pad, img_bgr.shape[0]),
                   max(x - pad, 0):min(x + w + pad, img_bgr.shape[1])]

# --- NEW: Get corners of page by detecting largest contour polygon approx 4 corners ---
def get_page_corners(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest_contour = max(contours, key=cv2.contourArea)
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    if len(approx) != 4:
        return None
    pts = approx.reshape(4, 2)
    return order_points(pts)

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]       # top-left
    rect[2] = pts[np.argmax(s)]       # bottom-right
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]    # top-right
    rect[3] = pts[np.argmax(diff)]    # bottom-left
    return rect

def warp_to_reference(target_img, ref_corners, ref_size):
    target_corners = get_page_corners(target_img)
    if target_corners is None:
        # No corners found, return original
        return target_img
    M = cv2.getPerspectiveTransform(target_corners, ref_corners)
    warped = cv2.warpPerspective(target_img, M, ref_size)
    return warped

def read_uploaded_file(uploaded_file):
    if uploaded_file.name.lower().endswith('.pdf'):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        images = []
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
        return images
    elif uploaded_file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
        img = Image.open(uploaded_file).convert("RGB")
        return [cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)]
    else:
        return []

def extract_using_template(images, layout_data, photo_min, photo_max, sign_min, sign_max):
    OUTPUT_DIR = "output"
    PHOTOS_DIR = os.path.join(OUTPUT_DIR, "photos")
    SIGNS_DIR = os.path.join(OUTPUT_DIR, "signatures")
    if os.path.exists(OUTPUT_DIR): shutil.rmtree(OUTPUT_DIR)
    os.makedirs(PHOTOS_DIR), os.makedirs(SIGNS_DIR)

    previews = {"photos": [], "signatures": []}

    # Reference image corners & size from first image (layout page)
    ref_img = images[0]
    ref_corners = np.array([[0,0], [ref_img.shape[1]-1, 0], [ref_img.shape[1]-1, ref_img.shape[0]-1], [0, ref_img.shape[0]-1]], dtype="float32")
    ref_size = (ref_img.shape[1], ref_img.shape[0])

    for page_num, img in enumerate(images):
        if page_num == 0:
            aligned_img = img
        else:
            aligned_img = warp_to_reference(img, ref_corners, ref_size)
        for i, region in enumerate(layout_data):
            x, y, w, h = region['photo']
            photo_bgr = aligned_img[y:y+h, x:x+w]
            photo_bgr = remove_white_border(photo_bgr, tighter=True)
            photo_rgb = cv2.cvtColor(photo_bgr, cv2.COLOR_BGR2RGB)
            photo_data = compress_image(photo_rgb, photo_min, photo_max)
            photo_path = os.path.join(PHOTOS_DIR, f"photo_{page_num+1}_{i+1}.jpg")
            save_image(photo_data, photo_path)
            previews["photos"].append(photo_path)

            x, y, w, h = region['sign']
            sign_bgr = aligned_img[y:y+h, x:x+w]
            sign_bgr = remove_white_border(sign_bgr)
            sign_rgb = cv2.cvtColor(sign_bgr, cv2.COLOR_BGR2RGB)
            sign_data = compress_image(sign_rgb, sign_min, sign_max)
            sign_path = os.path.join(SIGNS_DIR, f"sign_{page_num+1}_{i+1}.jpg")
            save_image(sign_data, sign_path)
            previews["signatures"].append(sign_path)

    return previews

def zip_output(zip_name="extracted.zip"):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for folder in ["output/photos", "output/signatures"]:
            for root, _, files in os.walk(folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    zipf.write(full_path, os.path.relpath(full_path, "output"))
    return zip_name

# === Streamlit UI ===
st.set_page_config(page_title="📐 Manual Photo & Signature Mapping", layout="wide")
st.title("📷 Manual Layout-Based Photo & Signature Extractor")

uploaded = st.file_uploader("📄 Upload PDF or Image", type=["pdf", "jpg", "jpeg", "png"])

st.subheader("📷 Photo Compression Settings")
c1, c2 = st.columns(2)
photo_min = c1.number_input("Min KB (Photo)", value=40, min_value=10)
photo_max = c2.number_input("Max KB (Photo)", value=60, min_value=photo_min+1)

st.subheader("✍️ Signature Compression Settings")
c3, c4 = st.columns(2)
sign_min = c3.number_input("Min KB (Signature)", value=15, min_value=5)
sign_max = c4.number_input("Max KB (Signature)", value=40, min_value=sign_min+1)

if uploaded:
    images = read_uploaded_file(uploaded)
    first_page = cv2.cvtColor(images[0], cv2.COLOR_BGR2RGB)

    display_h, display_w = first_page.shape[0]//2, first_page.shape[1]//2

    # Mode toggle to switch between drawing new rects or editing existing
    st.subheader("🛠 Mode Selection")
    mode = st.radio("Select Mode", ["Draw Rectangles", "Edit Rectangles"])

    st.subheader("📐 Step 1: Draw all PHOTO boxes manually")

    canvas_photo = st_canvas(
        fill_color="rgba(0, 255, 0, 0.3)",
        stroke_width=2,
        stroke_color="green",
        background_image=Image.fromarray(first_page),
        update_streamlit=True,
        height=display_h,
        width=display_w,
        drawing_mode="rect" if mode == "Draw Rectangles" else "transform",
        key="canvas_photo",
    )

    st.subheader("📐 Step 2: Draw all SIGNATURE boxes manually in same order")

    canvas_sign = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=2,
        stroke_color="red",
        background_image=Image.fromarray(first_page),
        update_streamlit=True,
        height=display_h,
        width=display_w,
        drawing_mode="rect" if mode == "Draw Rectangles" else "transform",
        key="canvas_sign",
    )

    if "saved_layout" not in st.session_state:
        st.session_state.saved_layout = []

    if canvas_photo.json_data and canvas_sign.json_data and st.button("💾 Save Layout"):
        photo_boxes = canvas_photo.json_data["objects"]
        sign_boxes = canvas_sign.json_data["objects"]
        if len(photo_boxes) != len(sign_boxes):
            st.warning("⚠️ Number of photo and signature boxes must match.")
        else:
            def get_coords(b):
                # Convert coordinates from half-size canvas to full image scale
                return (int(b["left"]*2), int(b["top"]*2), int(b["width"]*2), int(b["height"]*2))
            layout = []
            for p, s in zip(photo_boxes, sign_boxes):
                layout.append({"photo": get_coords(p), "sign": get_coords(s)})
            st.session_state.saved_layout = layout
            st.success(f"✅ Layout saved with {len(layout)} blocks")

    # Load / Save Layout buttons
    c_load, c_save = st.columns(2)
    with c_save:
        if st.button("💾 Save Layout to File"):
            with open("layout_template.json", "w") as f:
                json.dump(st.session_state.saved_layout, f)
            st.success("✅ Layout saved to 'layout_template.json'")

    with c_load:
        if st.button("📂 Load Saved Layout"):
            if os.path.exists("layout_template.json"):
                with open("layout_template.json", "r") as f:
                    st.session_state.saved_layout = json.load(f)
                st.success(f"✅ Layout loaded with {len(st.session_state.saved_layout)} blocks")
            else:
                st.error("❌ No saved layout file found.")

    # Show saved layout count
    if st.session_state.saved_layout:
        st.info(f"🗂 Saved layout blocks: {len(st.session_state.saved_layout)}")

    if st.session_state.saved_layout and st.button("🚀 Extract from All Pages Using Saved Layout"):
        with st.spinner("Processing pages..."):
            results = extract_using_template(images, st.session_state.saved_layout, photo_min, photo_max, sign_min, sign_max)
            zip_path = zip_output()

        st.success("✅ Extraction complete!")
        st.markdown(f"**🧍 Photos extracted:** {len(results['photos'])}")
        st.markdown(f"**✍️ Signatures extracted:** {len(results['signatures'])}")

        st.download_button("📦 Download ZIP", open(zip_path, "rb"), file_name="photos_signatures.zip")

        with st.expander("🧍 Preview Photos"):
            for i, p in enumerate(results["photos"], 1):
                st.image(p, width=150, caption=f"Photo {i}", clamp=True)

        with st.expander("✍️ Preview Signatures"):
            for i, s in enumerate(results["signatures"], 1):
                st.image(s, width=150, caption=f"Signature {i}", clamp=True)
else:
    st.info("📄 Please upload a PDF or Image file to start.")
