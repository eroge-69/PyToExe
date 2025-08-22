import os
import time
import csv
import streamlit as st
import pydicom
import numpy as np
import cv2
from datetime import datetime
from collections import defaultdict
from pathlib import Path
import hashlib
import pickle
import tkinter as tk
from tkinter import filedialog

# =========================
# Utilities
# =========================
def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def bytescale_to_uint8(img):
    img = img.astype(np.float32)
    img_min, img_max = np.min(img), np.max(img)
    if img_max == img_min:
        return np.zeros_like(img, dtype=np.uint8)
    img = (img - img_min) / (img_max - img_min) * 255.0
    return img.astype(np.uint8)

def open_folder_dialog(initial=None):
    """Native folder picker. Returns '' if cancelled or Tk fails."""
    if not hasattr(tk, 'Tk'):
        st.warning("Tkinter is not available. Please paste the folder path manually.")
        return st.session_state.get("root_dicom_widget", "") or ""
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askdirectory(
            initialdir=initial or os.path.expanduser("~"),
            mustexist=True,
            parent=root
        )
        root.destroy()
        return path or ""
    except Exception as e:
        st.warning(f"Folder picker failed ({e}). Paste the path manually.")
        return st.session_state.get("root_dicom_widget", "") or ""

def sanitize_path(path: str) -> str:
    """Sanitize and validate a path, ensuring it exists and is a directory."""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")
        if not path_obj.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        return str(path_obj)
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")

# =========================
# Grouping logic (patients/studies)
# =========================
def scan_studies(root_dir):
    """Scan and group DICOM files by (PatientID, StudyInstanceUID)."""
    dir_hash = hashlib.md5(root_dir.encode()).hexdigest()
    if st.session_state.get("last_dir_hash") == dir_hash:
        return st.session_state.get("cached_groups", [])

    groups = {}
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if not fn.lower().endswith(".dcm"):
                continue
            fpath = os.path.join(dirpath, fn)
            try:
                d = pydicom.dcmread(fpath, stop_before_pixels=True, force=True)
                pid = getattr(d, "PatientID", "Unknown")
                study = getattr(d, "StudyInstanceUID", f"NO_STUDYUID::{os.path.abspath(dirpath)}")
                series = getattr(d, "SeriesInstanceUID", None)
                key = (pid, study)
                if key not in groups:
                    groups[key] = {"patient_id": pid, "study_uid": study, "series_uids": set(), "files": []}
                if series:
                    groups[key]["series_uids"].add(series)
                groups[key]["files"].append(fpath)
            except Exception:
                pass

    keys_sorted = sorted(groups.keys(), key=lambda k: (str(k[0]), str(k[1])))
    result = [groups[k] for k in keys_sorted]
    st.session_state["cached_groups"] = result
    st.session_state["last_dir_hash"] = dir_hash
    return result

def load_slices_for_group(group):
    """Load the axial series for a study group. Pick largest series by file count."""
    by_series = defaultdict(list)
    for f in group["files"]:
        try:
            d = pydicom.dcmread(f)
            sid = getattr(d, "SeriesInstanceUID", "NO_SERIES")
            by_series[sid].append(d)
        except Exception:
            pass

    if not by_series:
        st.error("No valid DICOM slices found in this study.")
        return []

    series_id, series_slices = max(by_series.items(), key=lambda kv: len(kv[1]))
    series_slices.sort(key=lambda d: int(getattr(d, "InstanceNumber", 0)))
    return series_slices

def dicom_to_uint8(dicom_slice):
    arr = dicom_slice.pixel_array.astype(np.float32)
    slope = safe_float(getattr(dicom_slice, "RescaleSlope", 1.0), 1.0)
    intercept = safe_float(getattr(dicom_slice, "RescaleIntercept", 0.0), 0.0)
    return bytescale_to_uint8(arr * slope + intercept)

# =========================
# Preprocessing (optional)
# =========================
def preprocess_remove_flesh(image_uint8, threshold=100, kernel_size=5):
    _, binary = cv2.threshold(image_uint8, threshold, 255, cv2.THRESH_BINARY)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    return cv2.bitwise_and(image_uint8, image_uint8, mask=closed)

# =========================
# Saving utilities
# =========================
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_filename(patient_id, study_uid, slice_index):
    """Generate a unique filename using patient_id, shortened study_uid, and slice_index."""
    study_uid_short = hashlib.md5(study_uid.encode()).hexdigest()[:8]
    return f"{patient_id}_{study_uid_short}_{slice_index:03d}.png"

def save_png(image_uint8, out_dir, filename):
    """Save image to out_dir, appending timestamp if filename exists."""
    ensure_dir(out_dir)
    out_path = os.path.join(out_dir, filename)
    if os.path.exists(out_path):
        base, ext = os.path.splitext(filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{base}_{timestamp}{ext}"
        out_path = os.path.join(out_dir, filename)
    cv2.imwrite(out_path, image_uint8)
    return filename

def append_label_csv(csv_path, rows):
    """Append rows to a single labels.csv."""
    fieldnames = ["timestamp", "patient_id", "study_uid", "series_uid", "slice_index", "label", "filename"]
    try:
        ensure_dir(os.path.dirname(csv_path))
        file_exists = os.path.exists(csv_path)
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for r in rows:
                writer.writerow(r)
    except PermissionError:
        st.error("Permission denied when writing to labels.csv. Check output folder permissions.")
    except Exception as e:
        st.error(f"Failed to write to labels.csv: {e}")

def load_processed_keys(output_dir):
    """Load processed_keys from a file if it exists."""
    processed_file = os.path.join(output_dir, "processed_keys.pkl")
    if os.path.exists(processed_file):
        try:
            with open(processed_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.warning(f"Failed to load processed keys: {e}")
    return set()

def save_processed_keys(output_dir, processed_keys):
    """Save processed_keys to a file."""
    processed_file = os.path.join(output_dir, "processed_keys.pkl")
    try:
        with open(processed_file, "wb") as f:
            pickle.dump(processed_keys, f)
    except Exception as e:
        st.error(f"Failed to save processed keys: {e}")

# =========================
# Streamlit App
# =========================
st.set_page_config(page_title="CBCT Mid-Palatal Suture Labeler", layout="wide")
st.title("CBCT Mid‑Palatal Suture Labeler")

# Session init
for k, v in {
    "root_dicom": "",
    "output_dir": "",
    "root_dicom_widget": "",
    "output_dir_widget": "",
    "groups": [],
    "cur_idx": 0,
    "processed_keys": set(),
    "slice_range": (0, 0),
    "selected_index": 0,
    "last_dir_hash": "",
    "cached_groups": [],
    "action_history": []
}.items():
    st.session_state.setdefault(k, v)

# Load processed_keys if output_dir is set
if st.session_state.output_dir and os.path.isdir(st.session_state.output_dir):
    st.session_state.processed_keys = load_processed_keys(st.session_state.output_dir)

# Browse callbacks
def _browse_root():
    chosen = open_folder_dialog(st.session_state.get("root_dicom", ""))
    if chosen and chosen != st.session_state.root_dicom:
        try:
            st.session_state.root_dicom = sanitize_path(chosen)
            st.session_state.root_dicom_widget = chosen
            st.session_state.groups = scan_studies(st.session_state.root_dicom)
            st.session_state.cur_idx = 0
            st.session_state.processed_keys = load_processed_keys(st.session_state.output_dir)
            st.rerun()
        except ValueError as e:
            st.error(f"Invalid DICOM folder path: {e}")

def _browse_out():
    chosen = open_folder_dialog(st.session_state.get("output_dir", ""))
    if chosen and chosen != st.session_state.output_dir:
        try:
            st.session_state.output_dir = sanitize_path(chosen)
            st.session_state.output_dir_widget = chosen
            st.session_state.processed_keys = load_processed_keys(st.session_state.output_dir)
            st.rerun()
        except ValueError as e:
            st.error(f"Invalid output folder path: {e}")

with st.sidebar:
    st.header("Folders")
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.text_input("Root DICOM Folder (can be one big folder)", key="root_dicom_widget",
                      value=st.session_state.root_dicom_widget)
    with col_b:
        st.button("Browse", key="browse_root_button", on_click=_browse_root)

    col_c, col_d = st.columns([3, 1])
    with col_c:
        st.text_input("Output Folder (labeled images + CSV)", key="output_dir_widget",
                      value=st.session_state.output_dir_widget)
    with col_d:
        st.button("Browse", key="browse_output_button", on_click=_browse_out)

    # Sync widget → state
    if st.session_state.root_dicom != st.session_state.root_dicom_widget:
        try:
            st.session_state.root_dicom = sanitize_path(st.session_state.root_dicom_widget)
            st.session_state.groups = scan_studies(st.session_state.root_dicom)
            st.session_state.cur_idx = 0
            st.session_state.processed_keys = load_processed_keys(st.session_state.output_dir)
        except ValueError as e:
            st.error(f"Invalid DICOM folder path: {e}")
    if st.session_state.output_dir != st.session_state.output_dir_widget:
        try:
            st.session_state.output_dir = sanitize_path(st.session_state.output_dir_widget)
            st.session_state.processed_keys = load_processed_keys(st.session_state.output_dir)
        except ValueError as e:
            st.error(f"Invalid output folder path: {e}")

    st.divider()
    st.header("Options")
    st.session_state.apply_flesh = st.checkbox("Remove soft tissue (preprocessing)", value=False,
                                               key="apply_flesh_checkbox")
    st.session_state.flesh_thresh = st.slider(
        "Threshold (soft tissue removal)", 50, 180, 100, 1, disabled=not st.session_state.apply_flesh,
        key="flesh_thresh_slider"
    )
    st.session_state.kernel_size = st.slider(
        "Kernel size (soft tissue removal)", 3, 15, 5, 2, disabled=not st.session_state.apply_flesh,
        key="kernel_size_slider"
    )
    st.session_state.play_speed = st.slider(
        "Playback speed (sec/frame)", 0.05, 0.6, 0.15, 0.05, key="play_speed_slider"
    )

# Guard folders
if not os.path.isdir(st.session_state.root_dicom):
    st.warning("Select a valid Root DICOM folder in the left panel.")
    st.stop()

groups = st.session_state.groups or scan_studies(st.session_state.root_dicom)
st.session_state.groups = groups

if not groups:
    st.error("No DICOM studies found in the selected folder.")
    st.stop()

# Current group
cur_idx = max(0, min(st.session_state.cur_idx, len(groups) - 1))
group = groups[cur_idx]
group_key = (group["patient_id"], group["study_uid"])

# Remaining counter
processed_count = len(st.session_state.processed_keys)
is_current_processed = group_key in st.session_state.processed_keys
remaining = len(groups) - processed_count - (0 if is_current_processed else 1)

# Load series for current group
slices = load_slices_for_group(group)
if not slices:
    st.stop()

# Metadata
s0 = slices[0]
raw_thickness = safe_float(getattr(s0, "SliceThickness", 0.0))
slice_thickness = raw_thickness if 0.1 < raw_thickness < 10 else 0.4
if raw_thickness <= 0.1 or raw_thickness >= 10:
    st.warning(f"Invalid slice thickness ({raw_thickness} mm). Using default: 0.4 mm.")
px = getattr(s0, "PixelSpacing", [0.0, 0.0])
resolution = f"{px[0]} mm × {px[1]} mm" if len(px) == 2 and all(p > 0 for p in px) else "Unknown"
if resolution == "Unknown":
    st.warning("Invalid pixel spacing in DICOM metadata.")
depth_mm = round(slice_thickness * len(slices), 2)
patient_id = group["patient_id"]
study_uid = group["study_uid"]
series_uid = getattr(s0, "SeriesInstanceUID", "Unknown")

# Header row: current and remaining
top1, top2, top3 = st.columns([3, 3, 2])
with top1:
    st.write(f"Patient ID: `{patient_id}`")
with top2:
    st.write(f"Study UID: `{study_uid}`")
with top3:
    st.write(f"Current: {cur_idx + 1}/{len(groups)} | Remaining: {remaining}")

# Study metadata
mcol1, mcol2, mcol3, mcol4 = st.columns(4)
with mcol1:
    st.write(f"Slice thickness: `{slice_thickness} mm` (extracted from DICOM 'SliceThickness' tag)")
with mcol2:
    st.write(f"Pixel spacing: `{resolution}`")
with mcol3:
    st.write(f"Slices in series: `{len(slices)}`")
with mcol4:
    st.write(f"Total depth: `{depth_mm} mm`")

# Decoupled sliders
st.subheader("Slice controls")
ctl1, ctl2, ctl3 = st.columns([2, 2, 1])
with ctl1:
    default_end = min(10, len(slices) - 1)
    st.session_state.slice_range = st.slider(
        "Range to play / save", 0, len(slices) - 1,
        st.session_state.slice_range if st.session_state.slice_range != (0, 0) else (0, default_end),
        key="slice_range_slider"
    )
with ctl2:
    st.session_state.selected_index = st.slider(
        "Inspect individual slice", 0, len(slices) - 1,
        st.session_state.selected_index, key="selected_index_slider"
    )
with ctl3:
    if st.button("Sync to range start", key="sync_range_start_button"):
        st.session_state.selected_index = st.session_state.slice_range[0]

def prepare_for_display(dcm_slice):
    img = dicom_to_uint8(dcm_slice)
    if st.session_state.apply_flesh:
        img = preprocess_remove_flesh(img, st.session_state.flesh_thresh, st.session_state.kernel_size)
    return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

left, right = st.columns(2, gap="large")
with left:
    st.subheader("Manual slice view")
    img_left = prepare_for_display(slices[st.session_state.selected_index])
    st.image(img_left, caption=f"Slice {st.session_state.selected_index}", channels="RGB", use_container_width=True)

with right:
    st.subheader("Playback")
    play = st.button("Play range", key="play_range_button")
    video_box = st.empty()
    if play:
        start, end = st.session_state.slice_range
        for i in range(start, end + 1, 2):
            frame = prepare_for_display(slices[i])
            video_box.image(frame, caption=f"Slice {i}", channels="RGB", use_container_width=True)
            time.sleep(st.session_state.play_speed * 2)

# Label and save
st.subheader("Label and save")
lab1, lab2, lab3 = st.columns([1, 1, 2])
with lab1:
    label = st.selectbox("Label", ["A", "B", "C", "D", "E", "Other"], key="label_selectbox")
with lab2:
    save_single = st.button("Save single slice", key="save_single_button")
with lab3:
    save_range = st.button("Save range", key="save_range_button")

if not os.path.isdir(st.session_state.output_dir):
    st.warning("Select a valid output folder in the left panel to enable saving.")
else:
    try:
        test_file = os.path.join(st.session_state.output_dir, ".test_write")
        with open(test_file, "w") as f:
            f.write("")
        os.remove(test_file)
    except Exception as e:
        st.error(f"Output directory is not writable: {e}")
        st.stop()

    timestamp = datetime.utcnow().isoformat()
    labels_csv = os.path.join(st.session_state.output_dir, "labels.csv")

    # Create label folders directly in output_dir
    all_labels = ["A", "B", "C", "D", "E", "Other"]
    for lbl in all_labels:
        ensure_dir(os.path.join(st.session_state.output_dir, lbl))

    if save_single:
        idx = st.session_state.selected_index
        img = prepare_for_display(slices[idx])
        sub_dir = os.path.join(st.session_state.output_dir, label)
        fname = generate_filename(patient_id, study_uid, idx)
        fname = save_png(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), sub_dir, fname)
        append_label_csv(labels_csv, [{
            "timestamp": timestamp,
            "patient_id": patient_id,
            "study_uid": study_uid,
            "series_uid": series_uid,
            "slice_index": idx,
            "label": label,
            "filename": os.path.join(label, fname)
        }])
        st.success(f"Saved slice {idx} → {os.path.join(label, fname)}")

    if save_range:
        start, end = st.session_state.slice_range
        progress = st.progress(0)
        rows, count = [], 0
        sub_dir = os.path.join(st.session_state.output_dir, label)
        for i in range(start, end + 1):
            img = prepare_for_display(slices[i])
            fname = generate_filename(patient_id, study_uid, i)
            fname = save_png(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY), sub_dir, fname)
            rows.append({
                "timestamp": timestamp,
                "patient_id": patient_id,
                "study_uid": study_uid,
                "series_uid": series_uid,
                "slice_index": i,
                "label": label,
                "filename": os.path.join(label, fname)
            })
            count += 1
            progress.progress((i - start + 1) / (end - start + 1))
        append_label_csv(labels_csv, rows)
        st.success(f"Saved {count} slices ({start}–{end}) to {label} folder")

# Navigation: mark done and next patient
nav1, nav2, nav3 = st.columns([1, 1, 2])
with nav1:
    if st.button("Mark patient done", key="mark_done_button"):
        st.session_state.processed_keys.add(group_key)
        st.session_state.setdefault("action_history", []).append(("mark_done", group_key))
        save_processed_keys(st.session_state.output_dir, st.session_state.processed_keys)
        st.success("Patient marked as done.")
with nav2:
    if st.button("Next patient", key="next_patient_button"):
        st.session_state.cur_idx = min(len(groups) - 1, st.session_state.cur_idx + 1)
        st.session_state.slice_range = (0, 0)
        st.session_state.selected_index = 0
        st.rerun()
with nav3:
    if st.button("Undo last action", key="undo_action_button"):
        if st.session_state.action_history:
            action, key = st.session_state.action_history.pop()
            if action == "mark_done" and key in st.session_state.processed_keys:
                st.session_state.processed_keys.remove(key)
                save_processed_keys(st.session_state.output_dir, st.session_state.processed_keys)
                st.success("Undo: Patient unmarked.")
    st.info(
        f"Remaining patients after this: {len(groups) - len(st.session_state.processed_keys) - (0 if group_key in st.session_state.processed_keys else 1)}")

# Footer status
if os.path.isdir(st.session_state.output_dir):
    saved_pngs = sum(
        1 for root, dirs, files in os.walk(st.session_state.output_dir) for f in files if f.lower().endswith(".png"))
    st.caption(
        f"Output root: {st.session_state.output_dir} | Labels CSV: {labels_csv} | Total saved PNGs: {saved_pngs}")