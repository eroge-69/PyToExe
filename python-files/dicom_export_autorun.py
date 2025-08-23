#!/usr/bin/env python3
"""
Автоматический экспорт DICOM в PNG.
Использование: python dicom_export_autorun.py
- ищет DICOM в папке, где лежит сам скрипт
- сохраняет PNG (10 центральных срезов каждой серии) в подпапку "out_quick_png"
"""

import os
from pathlib import Path
import numpy as np
from PIL import Image

try:
    import pydicom
except Exception:
    raise SystemExit("Требуется установить pydicom: pip install pydicom pillow numpy")


def find_dicom_files(input_dir: Path):
    files = []
    for root, _, fnames in os.walk(input_dir):
        for f in fnames:
            p = Path(root) / f
            try:
                _ = pydicom.dcmread(str(p), stop_before_pixels=True, force=True)
                files.append(p)
            except Exception:
                pass
    return files


def group_by_series(files):
    by_series = {}
    for f in files:
        try:
            ds = pydicom.dcmread(str(f), stop_before_pixels=True, force=True)
            uid = getattr(ds, "SeriesInstanceUID", "unknown")
            by_series.setdefault(uid, []).append(f)
        except Exception:
            continue
    return by_series


def safe_series_name(ds):
    desc = getattr(ds, "SeriesDescription", "") or ""
    body = getattr(ds, "BodyPartExamined", "") or ""
    seq = getattr(ds, "SeriesNumber", None)
    parts = []
    if seq is not None:
        parts.append(f"{int(seq):03d}")
    if desc:
        parts.append("".join(c if c.isalnum() else "_" for c in desc))
    if body:
        parts.append("".join(c if c.isalnum() else "_" for c in body))
    return "_".join(parts) if parts else "series"


def auto_window(img: np.ndarray) -> np.ndarray:
    lo = np.percentile(img, 1)
    hi = np.percentile(img, 99)
    if hi <= lo:
        lo, hi = np.min(img), np.max(img)
    img = np.clip((img - lo) / (hi - lo + 1e-8), 0, 1)
    return (img * 255).astype(np.uint8)


def export_series(series_files, out_dir: Path, n_center=10):
    # сортируем по InstanceNumber
    def sort_key(p):
        try:
            ds = pydicom.dcmread(str(p), stop_before_pixels=True, force=True)
            return int(getattr(ds, "InstanceNumber", 1e6))
        except Exception:
            return 1e6

    series_files = sorted(series_files, key=sort_key)
    if not series_files:
        return

    try:
        ds0 = pydicom.dcmread(str(series_files[0]), stop_before_pixels=True, force=True)
        sub = safe_series_name(ds0)
    except Exception:
        sub = "series"

    out_path = out_dir / sub
    out_path.mkdir(parents=True, exist_ok=True)

    mid = len(series_files) // 2
    half = n_center // 2
    sel = series_files[max(0, mid - half):min(len(series_files), mid + half)]

    saved = 0
    for i, f in enumerate(sel):
        try:
            ds = pydicom.dcmread(str(f), force=True)
            arr = ds.pixel_array.astype(np.float32)
            slope = float(getattr(ds, "RescaleSlope", 1.0))
            inter = float(getattr(ds, "RescaleIntercept", 0.0))
            arr = arr * slope + inter
            if arr.ndim == 3:
                arr = arr[..., 0]
            arr8 = auto_window(arr)
            Image.fromarray(arr8).save(out_path / f"{i:04d}.png")
            saved += 1
        except Exception as e:
            print(f"[WARN] {f}: {e}")
    print(f"Сохранено {saved} PNG в {out_path}")


def main():
    script_dir = Path(__file__).resolve().parent
    input_dir = script_dir
    out_dir = script_dir / "out_quick_png"
    out_dir.mkdir(exist_ok=True)

    files = find_dicom_files(input_dir)
    if not files:
        print("Не найдено DICOM файлов в папке со скриптом")
        return

    groups = group_by_series(files)
    print(f"Найдено {len(files)} файлов, {len(groups)} серий")

    for uid, flist in groups.items():
        export_series(flist, out_dir)


if __name__ == "__main__":
    main()
