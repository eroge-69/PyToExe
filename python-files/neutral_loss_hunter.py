# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 22:00:21 2025

@author: mthom
"""

#!/usr/bin/env python3
from __future__ import annotations
"""
Neutral‑Loss Hunter — LC–MS/MS mzML scanner (CLI + optional GUI, with tests & demo)

This version improves the default behavior:
- If **no arguments** are provided, the program now **launches the GUI** (tkinter). If tkinter
  is unavailable (headless environment), it **falls back to demo mode** with a clear message.
- Demo mode is still available with `--demo`.
- CLI and self‑test behaviors remain unchanged.

What it does
------------
Given an mzML file, a target neutral‑loss mass (in Da), and a tolerance (ppm), this tool:
  1) Scans every MS2 spectrum and checks **all fragment–fragment pairs** within that scan.
  2) Flags scans where any pair’s m/z difference ≈ target neutral loss (within ppm).
  3) Collects the parent (precursor) m/z for those scans and builds a **combined XIC**
     over the entire run by summing MS1 intensities within ±ppm for all matched precursors.
  4) Writes a detailed **CSV/Excel table** of hits: parent m/z, RT, and the fragment pair(s)
     that produce the neutral loss, plus **plots** when libraries are available.

Install
-------
Required:
    pip install pymzml numpy pandas
Optional (for plots):
    pip install matplotlib plotly openpyxl

Usage
-----
GUI (now the default when run with no args):
    python neutral_loss_hunter.py
    # → opens the GUI (falls back to demo if tkinter is unavailable)

Explicit GUI:
    python neutral_loss_hunter.py --gui

CLI (headless):
    python neutral_loss_hunter.py \
        --mzml "/path/to/run.mzML" \
        --neutral-loss 129.0426 \
        --ppm 10 \
        --min-ms2-int 200 \
        --ms2-topN 200 \
        --outdir "/path/to/output_dir" \
        --overlay-count 8

Self‑test (no mzML needed):
    python neutral_loss_hunter.py --self-test

Demo (synthetic data → files & plots without mzML):
    python neutral_loss_hunter.py --demo --outdir ./demo_out

Outputs
-------
<basename>_NL<neutral_loss>ppm<ppm>_hits.csv
<basename>_NL<neutral_loss>ppm<ppm>_hits.xlsx (if openpyxl available)
<basename>_NL<neutral_loss>ppm<ppm>_xic.csv
Optional plots (if libs available):
  PNG: <basename>_NL<neutral_loss>ppm<ppm>_xic.png
  PNG: <basename>_NL<neutral_loss>ppm<ppm>_xic_overlay.png
  HTML: <basename>_NL<neutral_loss>ppm<ppm>_xic.html

Notes
-----
• Matplotlib/Plotly are optional; if missing, plotting simply no‑ops and the program
  still writes tables/CSVs.
• PPM tolerance is used for both neutral‑loss matching and XIC extraction.
• Efficient pair‑finding uses a two‑pointer sweep on sorted fragment m/z.
"""

import argparse
import os
import sys
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any, Callable

import numpy as np
import pandas as pd

# Optional plotting backends -------------------------------------------------
try:  # matplotlib (PNG plots)
    import matplotlib.pyplot as plt  # type: ignore
    _HAS_MPL = True
except Exception:
    _HAS_MPL = False

try:  # plotly (interactive HTML)
    import plotly.graph_objs as go  # type: ignore
    from plotly.offline import plot as plotly_plot  # type: ignore
    _HAS_PLOTLY = True
except Exception:
    _HAS_PLOTLY = False

# Optional Excel writer
try:
    import openpyxl  # noqa: F401
    _HAS_OPENPYXL = True
except Exception:
    _HAS_OPENPYXL = False

# mzML reader (required for real data; not required for --demo/--self-test)
try:
    import pymzml  # type: ignore
    _HAS_PYMZML = True
except Exception:
    _HAS_PYMZML = False

# -----------------------------
# Helpers
# -----------------------------

def ppm_tol_delta(value_da: float, ppm: float) -> float:
    """Return absolute delta in Da for given ppm tolerance around value_da."""
    return float(value_da) * (ppm * 1e-6)


def within_ppm(measured: float, target: float, ppm: float) -> bool:
    if target <= 0:
        return False
    return abs(float(measured) - float(target)) <= ppm_tol_delta(target, ppm)


def safe_rt_minutes(spec: Any) -> Optional[float]:
    """Extract retention time in minutes if available; otherwise None."""
    try:
        if 'scan start time' in spec:
            return float(spec['scan start time'])
    except Exception:
        pass
    try:
        if 'retention time' in spec:
            rt = float(spec['retention time'])
            return rt/60.0 if rt > 100 else rt
    except Exception:
        pass
    return None


def safe_precursor_mz(spec: Any) -> Optional[float]:
    """Best‑effort extraction of the selected precursor m/z for an MS2 spectrum."""
    try:
        if hasattr(spec, 'selected_precursors') and spec.selected_precursors:
            cand = spec.selected_precursors[0]
            for k in ('mz', 'selected ion m/z', 'ion m/z', 'm/z'):
                if k in cand and cand[k] is not None:
                    return float(cand[k])
    except Exception:
        pass
    try:
        for k in ('precursor m/z', 'ms2 precursor m/z'):
            if k in spec:
                return float(spec[k])
    except Exception:
        pass
    return None


@dataclass
class NLPair:
    mz1: float
    mz2: float
    diff: float
    ppm_err: float
    i1: float
    i2: float


@dataclass
class NLHit:
    scan_id: str
    rt_min: Optional[float]
    precursor_mz: Optional[float]
    pairs: List[NLPair]


# -----------------------------
# Core logic
# -----------------------------

def find_neutral_loss_pairs(peaks: np.ndarray, neutral_loss: float, ppm: float) -> List[NLPair]:
    """Given peaks as Nx2 array [[mz,intensity],...], return all pairs within ppm of the neutral loss.
    Uses a two‑pointer sweep on sorted m/z to achieve ~O(n) behavior per spectrum.
    """
    if peaks.size == 0:
        return []
    order = np.argsort(peaks[:, 0])
    mz = peaks[order, 0]
    it = peaks[order, 1]

    tol = ppm_tol_delta(neutral_loss, ppm)
    n = len(mz)
    out: List[NLPair] = []

    j_start = 1
    for i in range(n - 1):
        j = max(j_start, i + 1)
        while j < n and (mz[j] - mz[i]) < (neutral_loss - tol):
            j += 1
        k = j
        while k < n and (mz[k] - mz[i]) <= (neutral_loss + tol):
            diff = mz[k] - mz[i]
            ppm_err = (abs(diff - neutral_loss) / neutral_loss) * 1e6
            out.append(NLPair(mz1=float(mz[i]), mz2=float(mz[k]), diff=float(diff), ppm_err=float(ppm_err), i1=float(it[i]), i2=float(it[k])))
            k += 1
        j_start = j
    return out


def scan_ms2_for_hits(reader: Any,
                       neutral_loss: float,
                       ppm: float,
                       min_ms2_int: float,
                       ms2_topN: int) -> Tuple[List[NLHit], List[float]]:
    """First pass: traverse spectra, collect NL hits and matched precursor m/z values."""
    hits: List[NLHit] = []
    matched_precursors: List[float] = []

    for spec in reader:
        try:
            ms_level = getattr(spec, 'ms_level', None)
        except Exception:
            ms_level = None
        if ms_level != 2:
            continue

        # MS2 peaks
        try:
            peaks = np.asarray(spec.peaks('centroided'))  # Nx2: m/z, intensity
        except Exception:
            pk = getattr(spec, 'peaks', None)
            peaks = np.asarray(pk()) if callable(pk) else np.empty((0, 2))

        if peaks.size == 0:
            continue

        # Intensity filter + topN throttle
        peaks = peaks[peaks[:, 1] >= float(min_ms2_int)]
        if peaks.size == 0:
            continue
        if ms2_topN > 0 and len(peaks) > ms2_topN:
            idx = np.argsort(peaks[:, 1])[::-1][:ms2_topN]
            peaks = peaks[idx]

        pairs = find_neutral_loss_pairs(peaks, neutral_loss, ppm)
        if pairs:
            rt_min = safe_rt_minutes(spec)
            prec_mz = safe_precursor_mz(spec)
            scan_id = getattr(spec, 'ID', None) or getattr(spec, 'id', None) or ''
            hits.append(NLHit(scan_id=scan_id, rt_min=rt_min, precursor_mz=prec_mz, pairs=pairs))
            if prec_mz is not None:
                matched_precursors.append(float(prec_mz))

    return hits, matched_precursors


def build_combined_xic(reader: Any,
                       target_mzs: List[float],
                       ppm: float) -> Tuple[np.ndarray, np.ndarray, Dict[float, np.ndarray]]:
    """Second pass: from MS1 spectra, build summed XIC across target_mzs and per‑target overlays.

    Returns (rt_minutes, combined_intensity, overlay_dict)
        overlay_dict maps target_mz -> intensity vector aligned with rt_minutes.
    """
    if not target_mzs:
        return np.array([]), np.array([]), {}

    targets = np.array(sorted(set(float(x) for x in target_mzs)))
    low = targets * (1.0 - ppm * 1e-6)
    high = targets * (1.0 + ppm * 1e-6)

    rts: List[float] = []
    combined: List[float] = []
    overlay: Dict[float, List[float]] = {t: [] for t in targets}

    for spec in reader:
        try:
            ms_level = getattr(spec, 'ms_level', None)
        except Exception:
            ms_level = None
        if ms_level != 1:
            continue

        rt_min = safe_rt_minutes(spec)
        if rt_min is None:
            continue

        try:
            peaks = np.asarray(spec.peaks('centroided'))
        except Exception:
            pk = getattr(spec, 'peaks', None)
            peaks = np.asarray(pk()) if callable(pk) else np.empty((0, 2))

        if peaks.size == 0:
            rts.append(rt_min)
            combined.append(0.0)
            for t in targets:
                overlay[t].append(0.0)
            continue

        mz = peaks[:, 0]
        it = peaks[:, 1]
        if not np.all(mz[:-1] <= mz[1:]):
            order = np.argsort(mz)
            mz = mz[order]
            it = it[order]

        total = 0.0
        for idx, t in enumerate(targets):
            lo = np.searchsorted(mz, low[idx], side='left')
            hi = np.searchsorted(mz, high[idx], side='right')
            val = float(it[lo:hi].sum()) if hi > lo else 0.0
            total += val
            overlay[t].append(val)

        rts.append(rt_min)
        combined.append(total)

    rt_arr = np.array(rts)
    comb_arr = np.array(combined)
    overlay_arr = {t: np.array(v) for t, v in overlay.items()}

    order = np.argsort(rt_arr)
    rt_arr = rt_arr[order]
    comb_arr = comb_arr[order]
    overlay_arr = {t: v[order] for t, v in overlay_arr.items()}
    return rt_arr, comb_arr, overlay_arr


# -----------------------------
# Plotting (optional backends)
# -----------------------------

def plot_xic_png(rt_min: np.ndarray, intensity: np.ndarray, hits: List[NLHit], out_png: str, title: str):
    if not _HAS_MPL:
        return  # silently skip if matplotlib is unavailable
    import matplotlib.pyplot as plt  # local import keeps module optional
    plt.figure(figsize=(12, 5))
    plt.plot(rt_min, intensity, linewidth=2)
    plt.xlabel('Retention time (min)')
    plt.ylabel('Summed intensity')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    hit_rts = [h.rt_min for h in hits if h.rt_min is not None]
    if hit_rts:
        ymin, ymax = plt.ylim()
        for x in hit_rts:
            plt.vlines(x, ymin, ymax, alpha=0.08)
        plt.ylim(ymin, ymax)
    plt.tight_layout()
    plt.savefig(out_png, dpi=180)
    plt.close()


def plot_overlay_png(rt_min: np.ndarray, overlay: Dict[float, np.ndarray], out_png: str, title: str, overlay_count: int = 8):
    if not _HAS_MPL:
        return  # silently skip if matplotlib is unavailable
    import matplotlib.pyplot as plt  # local import keeps module optional
    if not overlay:
        return
    items = sorted(overlay.items(), key=lambda kv: float(np.nanmax(kv[1]) if kv[1].size else 0.0), reverse=True)
    to_plot = items[:overlay_count]
    plt.figure(figsize=(12, 6))
    for t, y in to_plot:
        plt.plot(rt_min, y, linewidth=1.3, label=f"{t:.4f} m/z")
    plt.xlabel('Retention time (min)')
    plt.ylabel('Intensity')
    plt.title(title + ' — Top precursors overlay')
    plt.legend(frameon=False, ncol=2)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png, dpi=180)
    plt.close()


def plot_xic_html(rt_min: np.ndarray, intensity: np.ndarray, hits: List[NLHit], out_html: str, title: str):
    if not _HAS_PLOTLY:
        return  # silently skip if plotly is unavailable
    import plotly.graph_objs as go  # local import keeps module optional
    from plotly.offline import plot as plotly_plot  # type: ignore
    traces = [go.Scatter(x=rt_min, y=intensity, mode='lines', name='Combined XIC')]
    shapes = []
    hit_rts = [h.rt_min for h in hits if h.rt_min is not None]
    y_max = float(np.nanmax(intensity)) if intensity.size else 1.0
    for x in hit_rts:
        shapes.append(dict(type='line', x0=x, x1=x, y0=0, y1=y_max, line=dict(width=1, dash='dot'), opacity=0.2))
    layout = go.Layout(title=title, xaxis=dict(title='Retention time (min)'))
    fig = go.Figure(data=traces, layout=layout)
    if shapes:
        fig.update_layout(shapes=shapes)
    plotly_plot(fig, filename=out_html, auto_open=False)


# -----------------------------
# I/O helpers
# -----------------------------

def write_hits_table(hits: List[NLHit], out_csv: str, out_xlsx: Optional[str] = None):
    rows = []
    for h in hits:
        for p in h.pairs:
            rows.append({
                'scan_id': h.scan_id,
                'rt_min': h.rt_min,
                'rt_sec': (h.rt_min * 60.0) if h.rt_min is not None else None,
                'precursor_mz': h.precursor_mz,
                'frag_mz_1': p.mz1,
                'frag_mz_2': p.mz2,
                'diff_Da': p.diff,
                'ppm_err': p.ppm_err,
                'frag_int_1': p.i1,
                'frag_int_2': p.i2,
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        df.sort_values(['rt_min', 'precursor_mz', 'ppm_err'], inplace=True, na_position='last')
    df.to_csv(out_csv, index=False)

    if out_xlsx and _HAS_OPENPYXL:
        try:
            with pd.ExcelWriter(out_xlsx, engine='openpyxl') as xw:
                df.to_excel(xw, index=False, sheet_name='hits')
        except Exception:
            pass


def write_xic_csv(rt_min: np.ndarray, intensity: np.ndarray, out_csv: str):
    df = pd.DataFrame({'rt_min': rt_min, 'intensity': intensity})
    df.to_csv(out_csv, index=False)


# -----------------------------
# Minimal fakes for tests/demo (no mzML required)
# -----------------------------
class _Spec:
    def __init__(self, ms_level: int, peaks: np.ndarray, rt_min: Optional[float] = None, precursor_mz: Optional[float] = None, scan_id: str = ''):
        self.ms_level = ms_level
        self._peaks = peaks
        self._rt_min = rt_min
        self._scan_id = scan_id
        self.selected_precursors = [{'mz': precursor_mz}] if (precursor_mz is not None and ms_level == 2) else []
    def peaks(self, mode: str = 'centroided'):
        return self._peaks
    @property
    def ID(self):
        return self._scan_id
    def __contains__(self, key: str) -> bool:
        return key == 'scan start time' and (self._rt_min is not None)
    def __getitem__(self, key: str) -> float:
        if key == 'scan start time' and (self._rt_min is not None):
            return float(self._rt_min)
        raise KeyError(key)


class _Reader(list):
    pass


def _make_demo_readers(nl: float, ppm: float) -> Tuple[_Reader, _Reader]:
    """Create synthetic MS2 (for hits) and MS1 (for XIC) readers."""
    # MS2: three scans with fragment pairs around target NL
    ms2 = _Reader()
    rng = np.random.default_rng(0)
    for i, rt in enumerate([1.0, 2.0, 3.5]):
        frags = np.array([
            [150.0000, 1000],
            [150.0000 + nl,  800],   # exact NL pair
            [200.1234, 500],
            [300.5678, 400],
        ], dtype=float)
        jitter = (rng.normal(0, 0.3, size=frags.shape[0]) * 1e-6) * frags[:, 0]
        frags[:, 0] += jitter
        ms2.append(_Spec(ms_level=2, peaks=frags, rt_min=rt, precursor_mz=400.1234 + i, scan_id=f'scan{i+1}'))

    # MS1: simple chromatogram with two precursor windows having small bumps
    ms1 = _Reader()
    times = np.linspace(0.0, 5.0, 101)
    targets = [400.1234, 401.1234, 402.1234]
    for t in times:
        peaks = []
        for m in targets:
            peaks.append([m * (1 + 0.5e-6), 5.0 + 100.0 * math.exp(-((t-2.0)**2)/(2*0.1**2))])  # Gaussian at 2.0 min
        ms1.append(_Spec(ms_level=1, peaks=np.array(peaks), rt_min=t))
    return ms2, ms1


# -----------------------------
# Mode selection helpers
# -----------------------------

def _should_auto_demo(args: argparse.Namespace, argv_len: Optional[int] = None) -> bool:
    """Return True when we should auto‑fallback to demo mode.
    Conditions:
      • GUI not requested/available and required args missing, and
      • Tkinter unavailable (headless), and
      • Either no CLI args at all (argv_len==1), or we're likely in an IDE/interactive env.
    """
    if args.demo or args.self_test:
        return False
    if args.mzml and args.neutral_loss:
        return False
    if argv_len is None:
        argv_len = len(sys.argv)
    interactive = bool(os.environ.get('SPYDER', '')) or ('ipykernel' in sys.modules) or (os.environ.get('PYCHARM_HOSTED') == '1')
    try:
        import tkinter  # noqa: F401
        tk_available = True
    except Exception:
        tk_available = False
    return (argv_len == 1 or interactive) and (not tk_available)


def _should_auto_gui(args: argparse.Namespace, argv_len: Optional[int] = None) -> bool:
    """Return True when we should auto‑launch the GUI.
    Conditions:
      • No required args (mzml or neutral‑loss missing), and
      • Tkinter available, and
      • Either no CLI args at all (argv_len==1) or likely interactive.
    """
    if args.gui or args.demo or args.self_test:
        return False
    if args.mzml and args.neutral_loss:
        return False
    if argv_len is None:
        argv_len = len(sys.argv)
    interactive = bool(os.environ.get('SPYDER', '')) or ('ipykernel' in sys.modules) or (os.environ.get('PYCHARM_HOSTED') == '1')
    try:
        import tkinter  # noqa: F401
        tk_available = True
    except Exception:
        tk_available = False
    return (argv_len == 1 or interactive) and tk_available


# -----------------------------
# Processing entry point (reusable by CLI & GUI)
# -----------------------------

def process_mzml(mzml: str, neutral_loss: float, ppm: float, outdir: str,
                  min_ms2_int: float = 200.0, ms2_topN: int = 200, overlay_count: int = 8,
                  progress: Optional[Callable[[str], None]] = None) -> Dict[str, str]:
    """Run the full pipeline on a real mzML file. Returns dict of output paths.
    `progress` if provided will be called with status strings for GUI logging.
    """
    def log(msg: str):
        if progress:
            progress(msg)
        else:
            print(msg)

    if not _HAS_PYMZML:
        raise RuntimeError('pymzml is required for reading mzML. Install with: pip install pymzml')
    if not os.path.isfile(mzml):
        raise FileNotFoundError(f"mzML not found: {mzml}")

    os.makedirs(outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(mzml))[0]
    tag = f"NL{neutral_loss:.4f}ppm{int(ppm)}"
    out_hits_csv = os.path.join(outdir, f"{base}_{tag}_hits.csv")
    out_hits_xlsx = os.path.join(outdir, f"{base}_{tag}_hits.xlsx")
    out_xic_csv = os.path.join(outdir, f"{base}_{tag}_xic.csv")
    out_png = os.path.join(outdir, f"{base}_{tag}_xic.png")
    out_overlay_png = os.path.join(outdir, f"{base}_{tag}_xic_overlay.png")
    out_html = os.path.join(outdir, f"{base}_{tag}_xic.html")

    log('Scanning MS2 for neutral‑loss hits...')
    reader1 = pymzml.run.Reader(mzml)  # type: ignore
    hits, precursors = scan_ms2_for_hits(reader1, float(neutral_loss), float(ppm), float(min_ms2_int), int(ms2_topN))

    if not hits:
        log('No neutral‑loss hits found in MS2.')
        write_hits_table([], out_hits_csv, out_hits_xlsx)
        write_xic_csv(np.array([]), np.array([]), out_xic_csv)
        return {
            'hits_csv': out_hits_csv,
            'hits_xlsx': out_hits_xlsx,
            'xic_csv': out_xic_csv,
        }

    log(f'Building XIC across {len(set([p for p in precursors if p is not None]))} matched precursors...')
    reader2 = pymzml.run.Reader(mzml)  # type: ignore
    rt_min, comb, overlay = build_combined_xic(reader2, [p for p in precursors if p is not None], float(ppm))

    log('Writing tables and plots...')
    write_hits_table(hits, out_hits_csv, out_hits_xlsx)
    if rt_min.size and comb.size:
        write_xic_csv(rt_min, comb, out_xic_csv)
        title = f"Combined XIC for NL {neutral_loss:.4f}±{ppm} ppm (n={len(set(precursors))} precursors)"
        plot_xic_png(rt_min, comb, hits, out_png, title)
        plot_overlay_png(rt_min, overlay, out_overlay_png, title, overlay_count=int(overlay_count))
        plot_xic_html(rt_min, comb, hits, out_html, title)

    return {
        'hits_csv': out_hits_csv,
        'hits_xlsx': out_hits_xlsx,
        'xic_csv': out_xic_csv,
        'xic_png': out_png if os.path.exists(out_png) else '',
        'overlay_png': out_overlay_png if os.path.exists(out_overlay_png) else '',
        'xic_html': out_html if os.path.exists(out_html) else '',
    }


# -----------------------------
# GUI (tkinter)
# -----------------------------

def _launch_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title('Neutral‑Loss Hunter')
    root.geometry('700x440')

    def row(parent, r, label):
        tk.Label(parent, text=label).grid(row=r, column=0, sticky='e', padx=8, pady=6)
        e = tk.Entry(parent, width=60)
        e.grid(row=r, column=1, sticky='we', padx=8, pady=6)
        return e

    frm = tk.Frame(root)
    frm.pack(fill='both', expand=True, padx=10, pady=10)
    frm.grid_columnconfigure(1, weight=1)

    e_mzml = row(frm, 0, 'mzML file:')
    btn_browse_mzml = tk.Button(frm, text='Browse…', command=lambda: e_mzml.delete(0, 'end') or e_mzml.insert(0, filedialog.askopenfilename(title='Select mzML', filetypes=[('mzML files', '*.mzML'), ('All files', '*.*')]) or ''))
    btn_browse_mzml.grid(row=0, column=2, padx=6)

    e_out = row(frm, 1, 'Output folder:')
    btn_browse_out = tk.Button(frm, text='Browse…', command=lambda: e_out.delete(0, 'end') or e_out.insert(0, filedialog.askdirectory(title='Select output folder') or ''))
    btn_browse_out.grid(row=1, column=2, padx=6)

    e_nl = row(frm, 2, 'Neutral loss (Da):')
    e_ppm = row(frm, 3, 'Tolerance (ppm):')
    e_minint = row(frm, 4, 'Min MS2 intensity:')
    e_topn = row(frm, 5, 'MS2 top N:')
    e_overlay = row(frm, 6, 'Overlay count:')

    # defaults
    e_ppm.insert(0, '10')
    e_minint.insert(0, '200')
    e_topn.insert(0, '200')
    e_overlay.insert(0, '8')

    log = tk.Text(frm, height=10)
    log.grid(row=7, column=0, columnspan=3, sticky='nsew', padx=8, pady=8)
    frm.grid_rowconfigure(7, weight=1)

    def append(msg: str):
        log.insert('end', msg + '\n')
        log.see('end')
        root.update_idletasks()

    def run():
        try:
            mzml = e_mzml.get().strip()
            outdir = e_out.get().strip() or (os.path.dirname(mzml) if mzml else os.getcwd())
            nl = float(e_nl.get().strip())
            ppm = float(e_ppm.get().strip())
            minint = float(e_minint.get().strip())
            topn = int(e_topn.get().strip())
            overlay = int(e_overlay.get().strip())
        except Exception as ex:
            messagebox.showerror('Invalid input', f'Please check your parameters.\n\n{ex}')
            return

        if not mzml:
            messagebox.showerror('Missing mzML', 'Please choose an mzML file.')
            return
        try:
            outputs = process_mzml(mzml, nl, ppm, outdir, minint, topn, overlay, progress=append)
            append('Done!')
            messagebox.showinfo('Finished', 'Processing complete. Outputs written to:\n' + outdir)
        except Exception as ex:
            append(f'ERROR: {ex}')
            messagebox.showerror('Error', str(ex))

    btn_run = tk.Button(frm, text='Run', command=run)
    btn_run.grid(row=8, column=2, sticky='e', padx=8, pady=6)

    root.mainloop()


# -----------------------------
# Demo runner
# -----------------------------

def _run_demo_mode(args: argparse.Namespace) -> None:
    outdir = args.outdir or os.getcwd()
    os.makedirs(outdir, exist_ok=True)
    base = 'demo'
    tag = f"NL{args.neutral_loss or 18.0106:.4f}ppm{int(args.ppm)}"
    out_hits_csv = os.path.join(outdir, f"{base}_{tag}_hits.csv")
    out_hits_xlsx = os.path.join(outdir, f"{base}_{tag}_hits.xlsx")
    out_xic_csv = os.path.join(outdir, f"{base}_{tag}_xic.csv")
    out_png = os.path.join(outdir, f"{base}_{tag}_xic.png")
    out_overlay_png = os.path.join(outdir, f"{base}_{tag}_xic_overlay.png")
    out_html = os.path.join(outdir, f"{base}_{tag}_xic.html")

    nl = args.neutral_loss or 18.010565
    ms2_reader, ms1_reader = _make_demo_readers(nl, args.ppm)
    hits, precs = scan_ms2_for_hits(ms2_reader, nl, args.ppm, args.min_ms2_int, args.ms2_topN)
    write_hits_table(hits, out_hits_csv, out_hits_xlsx)
    rt_min, comb, overlay = build_combined_xic(ms1_reader, [p for p in precs if p is not None], args.ppm)
    write_xic_csv(rt_min, comb, out_xic_csv)
    title = f"Combined XIC for NL {nl:.4f}±{args.ppm} ppm (demo)"
    if rt_min.size and comb.size:
        plot_xic_png(rt_min, comb, hits, out_png, title)
        plot_overlay_png(rt_min, overlay, out_overlay_png, title, overlay_count=args.overlay_count)
        plot_xic_html(rt_min, comb, hits, out_html, title)
    print('Demo outputs written to:', outdir)


# -----------------------------
# Main
# -----------------------------

def main():
    ap = argparse.ArgumentParser(description='Find fragment–fragment neutral‑loss events in MS2 and build a combined XIC over matching precursors (CLI or GUI).')
    ap.add_argument('--mzml', type=str, help='Path to input mzML file')
    ap.add_argument('--neutral-loss', type=float, help='Target neutral‑loss mass in Da (e.g., 129.0426)')
    ap.add_argument('--ppm', type=float, default=10.0, help='Tolerance in ppm (default: 10)')
    ap.add_argument('--min-ms2-int', type=float, default=200.0, help='Minimum MS2 fragment intensity to consider (default: 200)')
    ap.add_argument('--ms2-topN', type=int, default=200, help='Limit MS2 fragments to top‑N by intensity per scan (default: 200; 0 = all)')
    ap.add_argument('--outdir', type=str, default=None, help='Output directory (default: alongside mzML)')
    ap.add_argument('--overlay-count', type=int, default=8, help='How many individual precursor XICs to overlay (by max intensity)')
    ap.add_argument('--self-test', action='store_true', help='Run unit tests (no mzML required)')
    ap.add_argument('--demo', action='store_true', help='Generate outputs from synthetic data (no mzML required)')
    ap.add_argument('--gui', action='store_true', help='Launch the graphical interface')
    args = ap.parse_args()

    # Unit tests
    if args.self_test:
        _run_tests()
        print('All self‑tests passed.')
        return

    # GUI explicitly requested
    if args.gui:
        _launch_gui()
        return

    # Auto‑GUI if no args and tkinter is available
    if _should_auto_gui(args):
        _launch_gui()
        return

    # Auto‑demo fallback if running with no args in IDE/sandbox and GUI is unavailable
    if _should_auto_demo(args):
        print('No --mzml/--neutral-loss provided; tkinter unavailable — auto‑running demo mode. To process real data, pass --gui (on a desktop) or both flags.')
        _run_demo_mode(args)
        return

    # Explicit demo mode
    if args.demo:
        _run_demo_mode(args)
        return

    # Regular mzML workflow (CLI arguments REQUIRED)
    if not args.mzml or not args.neutral_loss:
        print('\nERROR: --mzml and --neutral-loss are required.\n')
        print('Example:')
        print('  python neutral_loss_hunter.py \
  --mzml "C:/data/run.mzML" \
  --neutral-loss 129.0426 \
  --ppm 10 \
  --min-ms2-int 200 \
  --ms2-topN 200 \
  --outdir "C:/data/out"')
        sys.exit(64)

    if not _HAS_PYMZML:
        print('ERROR: pymzml is required for reading mzML. Install with: pip install pymzml')
        sys.exit(1)

    mzml = args.mzml
    neutral_loss = float(args.neutral_loss)
    ppm = float(args.ppm)
    min_ms2_int = float(args.min_ms2_int)
    ms2_topN = int(args.ms2_topN)
    outdir = args.outdir or os.path.dirname(os.path.abspath(mzml))
    overlay_count = int(args.overlay_count)

    outputs = process_mzml(mzml, neutral_loss, ppm, outdir, min_ms2_int, ms2_topN, overlay_count)

    print('\nDone!')
    for k, v in outputs.items():
        if v:
            print(f"{k}: {v}")


# -----------------------------
# Tests
# -----------------------------

def _run_tests():
    # ppm math
    assert abs(ppm_tol_delta(100.0, 10.0) - 0.001) < 1e-12
    assert within_ppm(100.0010, 100.0, 10.0)
    assert not within_ppm(100.0021, 100.0, 10.0)
    assert not within_ppm(100.0, -5.0, 10.0)  # negative target guard

    # pair finding — exact, boundary, and outside
    nl = 18.010565
    mzs = np.array([
        [100.0000, 1000.0],
        [118.010565, 900.0],    # exact NL
        [150.0000, 500.0],
        [168.0100, 400.0],      # slightly off
        [200.0000, 800.0],
        [218.010565*(1+5e-6), 600.0],  # +5 ppm from exact diff with 200.0000
    ])
    pairs = find_neutral_loss_pairs(mzs, nl, ppm=5.0)
    # We expect two hits: (100 -> 118.010565) and (200 -> 218.010565*(1+5e-6)) at boundary
    assert len(pairs) == 2, f"Unexpected pair count: {len(pairs)}"
    assert any(abs(p.mz1 - 100.0) < 1e-6 and abs(p.mz2 - 118.010565) < 1e-6 for p in pairs)
    assert any(abs(p.mz1 - 200.0) < 1e-6 for p in pairs)

    # empty peaks returns no pairs
    assert find_neutral_loss_pairs(np.empty((0, 2)), nl, 10.0) == []

    # build_combined_xic with synthetic MS1
    ms2_reader, ms1_reader = _make_demo_readers(nl, 10.0)
    hits, precs = scan_ms2_for_hits(ms2_reader, nl, 10.0, min_ms2_int=0, ms2_topN=0)
    rt, comb, overlay = build_combined_xic(ms1_reader, precs, 10.0)
    assert rt.size == comb.size and rt.size > 0
    assert len(overlay) > 0
    t_peak = float(rt[np.argmax(comb)])
    assert 1.7 <= t_peak <= 2.3, f"Unexpected peak RT {t_peak}"

    # plotting functions should no‑op safely when backends are missing
    try:
        plot_xic_png(rt, comb, [], os.path.join(os.getcwd(), 'tmp.png'), 'tmp')
        plot_overlay_png(rt, overlay, os.path.join(os.getcwd(), 'tmp2.png'), 'tmp', overlay_count=2)
        plot_xic_html(rt, comb, [], os.path.join(os.getcwd(), 'tmp.html'), 'tmp')
    except Exception as e:
        raise AssertionError(f"Plotting functions should not raise even without backends: {e}")

    # auto‑selection tests (no mzML needed)
    class _Args:  # lightweight stand‑in for argparse.Namespace
        def __init__(self, mzml=None, nl=None, demo=False, self_test=False, gui=False):
            self.mzml = mzml
            self.neutral_loss = nl
            self.demo = demo
            self.self_test = self_test
            self.gui = gui
            self.ppm = 10.0
            self.min_ms2_int = 0.0
            self.ms2_topN = 0
            self.outdir = None
            self.overlay_count = 2
    # Depending on tkinter availability, either auto‑GUI or auto‑demo triggers when no args
    try:
        import tkinter  # noqa: F401
        tk_avail = True
    except Exception:
        tk_avail = False
    if tk_avail:
        assert _should_auto_gui(_Args(), argv_len=1) is True
        assert _should_auto_demo(_Args(), argv_len=1) is False
    else:
        assert _should_auto_demo(_Args(), argv_len=1) is True
    # Provided both required → neither auto GUI nor auto demo
    assert _should_auto_gui(_Args('file.mzML', 100.0), argv_len=3) is False
    assert _should_auto_demo(_Args('file.mzML', 100.0), argv_len=3) is False
    # Explicit demo flag → no auto decision needed (handled elsewhere)
    assert _should_auto_gui(_Args(demo=True), argv_len=3) is False
    assert _should_auto_demo(_Args(demo=True), argv_len=3) is False
    # GUI flag prevents auto‑demo
    assert _should_auto_demo(_Args(gui=True), argv_len=1) is False


if __name__ == '__main__':
    main()
