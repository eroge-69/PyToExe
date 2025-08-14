"""
EGP Purchasing Power Estimator — EXE with Optional GUI (Tkinter if available)
=============================================================================

✅ New fixes (network‑robust):
- Handles **IMF API connection failures** gracefully with layered fallbacks.
- Adds **offline forecast derivation** from World Bank inflation (YoY %) when IMF is unreachable.
- Supports **non‑interactive** mode (no stdin) and **optional GUI** (Tkinter) without crashing.
- Baseline year still **defaults to app launch year** (captured once).
- **Unit tests** extended (existing unchanged) to cover fallback logic.

Data sources at runtime
- World Bank CPI (Egypt) — indicator **FP.CPI.TOTL** (2010=100)
- IMF WEO inflation forecasts — indicator **PCPIPCH** (annual % change)
- Fallback: World Bank **Inflation, consumer prices (annual %)** — indicator **FP.CPI.TOTL.ZG** (historical YoY)

Build to EXE (Windows)
----------------------
1) Install Python 3.11+:
   pip install requests pyinstaller

2) Save as: egp_pp_estimator_app.py

3) Build CLI‑only EXE (works everywhere):
   pyinstaller --onefile egp_pp_estimator_app.py

4) (Optional) Build GUI EXE (requires Tkinter on the target machine):
   pyinstaller --onefile --windowed egp_pp_estimator_app.py

Run modes
---------
GUI (if available):
    egp_pp_estimator_app.py --gui

Headless one‑shot:
    egp_pp_estimator_app.py --target-year 2030 --out results.json

Non‑interactive (no TTY) fallback:
    # stdin is not a TTY → program reads env vars or uses defaults
    set EGP_TARGET_YEAR=2030
    set EGP_BASELINE_YEAR=2025    # optional
    set EGP_OUT=results.json      # optional (.json or .csv)
    set EGP_ALLOW_OFFLINE=1       # allow WB‑only fallback if IMF is unreachable
    set EGP_FALLBACK_STRATEGY=avg3  # options: hold | avg3 | avg5
    egp_pp_estimator_app.exe

Daily Windows Task Scheduler example:
    schtasks /Create /SC DAILY /TN "EGP_PP_Estimate" /TR "\"C:\\path\\to\\egp_pp_estimator_app.exe\" --target-year 2030 --out \"%USERPROFILE%\\Documents\\egp_pp_daily.csv\"" /ST 09:00

Notes
-----
- If IMF fails, the app will **optionally** (env/flag) forecast using World Bank historical YoY inflation:
  • **hold**: repeat the last available YoY forward
  • **avg3** (default): use trailing 3‑year average
  • **avg5**: use trailing 5‑year average
  This fallback is clearly labeled in the output (`imf_refreshed_at` starts with `offline_fallback:`).

"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

# 3rd-party
import requests

# Optional GUI imports (may be unavailable in sandbox/headless)
GUI_AVAILABLE = False
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    GUI_AVAILABLE = True
except Exception:  # pragma: no cover
    GUI_AVAILABLE = False

# --------------------------
# Configuration & Endpoints
# --------------------------
EGYPT_ISO3 = "EGY"
WB_CPI_SERIES = "FP.CPI.TOTL"  # CPI level (2010=100)
WB_CPI_URL = (
    f"https://api.worldbank.org/v2/country/{EGYPT_ISO3}/indicator/{WB_CPI_SERIES}?format=json&per_page=20000"
)
WB_INFL_YOY_SERIES = "FP.CPI.TOTL.ZG"  # Inflation, consumer prices (annual %)
WB_INFL_YOY_URL = (
    f"https://api.worldbank.org/v2/country/{EGYPT_ISO3}/indicator/{WB_INFL_YOY_SERIES}?format=json&per_page=20000"
)
IMF_INDICATOR = "PCPIPCH"  # inflation, average consumer prices, annual % change
IMF_DM_BASE = "https://www.imf.org/-/media/Websites/IMF/Data/Data-Mapper/API/v1"
IMF_API_URL = f"{IMF_DM_BASE}/WEO/{IMF_INDICATOR}/{EGYPT_ISO3}"
HTTP_TIMEOUT = 25
DEFAULT_HEADERS = {
    "User-Agent": "EGP-Estimator/1.0 (+local)",
    "Accept": "application/json, */*",
}

# --------------------------
# HTTP helper with backoff
# --------------------------

def http_get_json(url: str, params: Optional[dict] = None, tries: int = 5, timeout: int = HTTP_TIMEOUT) -> dict:
    last_err = None
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # pragma: no cover (network)
            last_err = e
            time.sleep(0.7 * (i + 1))
    raise RuntimeError(f"Failed GET {url}: {last_err}")


# --------------------------
# Data loading & projection
# --------------------------

def load_worldbank_cpi() -> Dict[int, float]:
    payload = http_get_json(WB_CPI_URL)
    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError("Unexpected World Bank response shape")
    rows = payload[1]
    out: Dict[int, float] = {}
    for row in rows:
        y = row.get("date")
        v = row.get("value")
        try:
            y = int(y)
        except Exception:
            continue
        if v is None:
            continue
        try:
            out[y] = float(v)
        except Exception:
            continue
    if not out:
        raise RuntimeError("No CPI data parsed from World Bank")
    return out


def load_worldbank_inflation_yoy(periods: Optional[Tuple[int, int]] = None) -> Dict[int, float]:
    payload = http_get_json(WB_INFL_YOY_URL)
    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError("Unexpected World Bank inflation response shape")
    rows = payload[1]
    out: Dict[int, float] = {}
    for row in rows:
        y = row.get("date")
        v = row.get("value")
        try:
            y = int(y)
        except Exception:
            continue
        if v is None:
            continue
        try:
            out[y] = float(v)
        except Exception:
            continue
    if periods:
        a, b = periods
        out = {y: v for y, v in out.items() if a <= y <= b}
    if not out:
        raise RuntimeError("No inflation YoY data parsed from World Bank")
    return out


def load_imf_inflation(periods: Optional[Tuple[int, int]] = None) -> Dict[int, float]:
    params = {}
    if periods:
        params["periods"] = f"{periods[0]}-{periods[1]}"
    data = http_get_json(IMF_API_URL, params=params)

    # Expected shape: { "WEO": { "PCPIPCH": { "EGY": {"2025": 23.1, ... } } } }
    series = None
    for top in data.values():
        if isinstance(top, dict):
            node = top.get(IMF_INDICATOR)
            if isinstance(node, dict):
                series = node.get(EGYPT_ISO3)
                break
    if not isinstance(series, dict):
        # fallback if the shape flattens
        series = data.get(EGYPT_ISO3) if isinstance(data.get(EGYPT_ISO3), dict) else None
    if not isinstance(series, dict):
        raise RuntimeError("Unexpected IMF response shape for WEO PCPIPCH")

    out: Dict[int, float] = {}
    for k, v in series.items():
        try:
            y = int(k)
            if v is None:
                continue
            out[y] = float(v)
        except Exception:
            continue
    if periods:
        a, b = periods
        out = {y: v for y, v in out.items() if a <= y <= b}
    if not out:
        raise RuntimeError("No inflation data parsed from IMF")
    return out


def nearest_cpi(cpi_by_year: Dict[int, float], year: int, direction: str = "backward") -> Tuple[int, float]:
    years = sorted(cpi_by_year.keys())
    if year in cpi_by_year:
        return year, cpi_by_year[year]
    if direction == "backward":
        candidates = [y for y in years if y < year]
        if candidates:
            y = max(candidates)
            return y, cpi_by_year[y]
    else:
        candidates = [y for y in years if y > year]
        if candidates:
            y = min(candidates)
            return y, cpi_by_year[y]
    raise ValueError("No CPI data found near requested year")


def _extend_forecasts_from_yoy(
    yoy: Dict[int, float], end_year: int, strategy: str = "avg3"
) -> Dict[int, float]:
    """Extend historical YoY inflation forward to end_year using a simple rule.
    strategy: 'hold' | 'avg3' | 'avg5'
    Returns a new dict with years up to end_year.
    """
    if not yoy:
        raise ValueError("No YoY data to extend")
    years = sorted(yoy)
    last_hist_year = years[-1]

    def trailing_avg(k: int) -> float:
        w = 1 if strategy == "hold" else (3 if strategy == "avg3" else 5)
        sample_years = [y for y in years if y <= k][-w:]
        if not sample_years:
            return yoy[years[-1]]
        vals = [yoy[y] for y in sample_years]
        return sum(vals) / len(vals)

    extended = dict(yoy)
    for y in range(last_hist_year + 1, end_year + 1):
        if strategy == "hold":
            extended[y] = extended[y - 1]
        else:
            extended[y] = trailing_avg(y - 1)
    return extended


def project_cpi(
    cpi_by_year: Dict[int, float],
    infl_by_year: Dict[int, float],
    start_year: int,
    end_year: int,
) -> Tuple[Dict[int, float], List[str]]:
    """Project CPI levels from the last known anchor up to end_year (inclusive)."""
    steps: List[str] = []
    cpi_levels: Dict[int, float] = {}

    # Anchor at or before start_year
    anchor_year, anchor_cpi = nearest_cpi(cpi_by_year, start_year, direction="backward")
    cpi_levels[anchor_year] = anchor_cpi
    steps.append(f"Anchor CPI {anchor_cpi:.2f} at {anchor_year} (nearest to baseline)")

    # Fill actual CPI up to last actual year
    max_actual_year = max(cpi_by_year.keys())
    for y in range(anchor_year + 1, min(end_year, max_actual_year) + 1):
        if y in cpi_by_year:
            cpi_levels[y] = cpi_by_year[y]
            steps.append(f"Actual CPI {cpi_by_year[y]:.2f} used for {y}")

    # Project beyond last actual CPI using provided inflation rates
    last_year_filled = max(cpi_levels.keys())
    last_cpi = cpi_levels[last_year_filled]
    for y in range(max(last_year_filled + 1, start_year + 1), end_year + 1):
        infl_pct = infl_by_year.get(y)
        if infl_pct is None:
            infl_pct = infl_by_year.get(y - 1)
        if infl_pct is None:
            raise ValueError(f"Missing inflation rate for year {y}")
        last_cpi = last_cpi * (1.0 + infl_pct / 100.0)
        cpi_levels[y] = last_cpi
        steps.append(f"Projected CPI for {y} using inflation {infl_pct:.2f}% → {last_cpi:.2f}")

    return cpi_levels, steps


@dataclass
class Estimate:
    baseline_year: int
    target_year: int
    baseline_cpi: float
    target_cpi_estimated: float
    price_level_change_pct: float
    purchasing_power_change_pct: float
    steps: List[str]
    worldbank_refreshed_at: str
    imf_refreshed_at: str


class EstimatorService:
    def __init__(
        self,
        cpi_fetcher: Callable[[], Dict[int, float]] = load_worldbank_cpi,
        infl_fetcher: Callable[[Optional[Tuple[int, int]]], Dict[int, float]] = load_imf_inflation,
        now_func: Callable[[], dt.datetime] = lambda: dt.datetime.now(),
        infl_fallback_fetcher: Callable[[Optional[Tuple[int, int]]], Dict[int, float]] = load_worldbank_inflation_yoy,
        allow_offline: Optional[bool] = None,
        fallback_strategy: Optional[str] = None,
    ):
        self._cpi_fetcher = cpi_fetcher
        self._infl_fetcher = infl_fetcher
        self._infl_fallback_fetcher = infl_fallback_fetcher
        self._now = now_func

        self.cpi_by_year: Dict[int, float] = {}
        self.infl_by_year: Dict[int, float] = {}
        self.worldbank_refreshed_at = ""
        self.imf_refreshed_at = ""
        self._lock = threading.Lock()

        # Baseline default = launch year
        self.launch_year = self._now().year

        # Offline policy
        if allow_offline is None:
            try:
                interactive = sys.stdin.isatty()
            except Exception:
                interactive = False
            env = os.getenv("EGP_ALLOW_OFFLINE", "1" if not interactive else "0")
            self.allow_offline = env.strip() not in ("", "0", "false", "False")
        else:
            self.allow_offline = allow_offline

        self.fallback_strategy = (fallback_strategy or os.getenv("EGP_FALLBACK_STRATEGY", "avg3")).lower()
        if self.fallback_strategy not in {"hold", "avg3", "avg5"}:
            self.fallback_strategy = "avg3"

    def refresh_sources(self):
        with self._lock:
            # CPI (must succeed; if it fails, we let it propagate)
            self.cpi_by_year = self._cpi_fetcher()
            self.worldbank_refreshed_at = self._now().isoformat(timespec="seconds")

            # Inflation: try IMF first, then WB YoY fallback (derive forecasts)
            this_year = self._now().year
            period = (this_year - 10, this_year + 15)
            try:
                self.infl_by_year = self._infl_fetcher(period)
                self.imf_refreshed_at = self._now().isoformat(timespec="seconds")
            except Exception as e:
                if not self.allow_offline:
                    raise
                # Fallback: use WB YoY historical and extend
                yoy = self._infl_fallback_fetcher(period)
                extended = _extend_forecasts_from_yoy(yoy, end_year=period[1], strategy=self.fallback_strategy)
                self.infl_by_year = extended
                self.imf_refreshed_at = f"offline_fallback:{self._now().isoformat(timespec='seconds')}"

    def estimate(self, baseline_year: Optional[int], target_year: int) -> Estimate:
        if not self.cpi_by_year or not self.infl_by_year:
            self.refresh_sources()

        base_year = baseline_year if baseline_year is not None else self.launch_year
        if target_year < base_year:
            raise ValueError("target_year must be >= baseline_year")

        cpi_path, steps = project_cpi(self.cpi_by_year, self.infl_by_year, base_year, target_year)
        base_used_year, base_cpi = nearest_cpi(self.cpi_by_year, base_year, direction="backward")
        target_cpi = cpi_path[target_year]

        ratio = target_cpi / base_cpi
        price_level_change_pct = (ratio - 1.0) * 100.0
        purchasing_power_change_pct = ((1.0 / ratio) - 1.0) * 100.0
        steps.insert(0, f"Baseline requested {base_year}, using CPI from {base_used_year}")

        return Estimate(
            baseline_year=base_year,
            target_year=target_year,
            baseline_cpi=base_cpi,
            target_cpi_estimated=target_cpi,
            price_level_change_pct=price_level_change_pct,
            purchasing_power_change_pct=purchasing_power_change_pct,
            steps=steps,
            worldbank_refreshed_at=self.worldbank_refreshed_at,
            imf_refreshed_at=self.imf_refreshed_at,
        )


# --------------------------
# Optional Tkinter GUI (only if available)
# --------------------------
if GUI_AVAILABLE:
    class App(tk.Tk):  # pragma: no cover
        def __init__(self):
            super().__init__()
            self.title("EGP Purchasing Power Estimator")
            self.geometry("780x560")
            self.resizable(True, True)
            self.estimator = EstimatorService()

            self._build_ui()
            self._set_defaults()

        def _build_ui(self):
            pad = {"padx": 8, "pady": 6}

            frm = ttk.Frame(self)
            frm.pack(fill=tk.BOTH, expand=True)

            row = 0
            ttk.Label(frm, text="Baseline Year (default = launch year)").grid(column=0, row=row, sticky="w", **pad)
            self.baseline_var = tk.StringVar()
            self.baseline_entry = ttk.Entry(frm, textvariable=self.baseline_var, width=16)
            self.baseline_entry.grid(column=1, row=row, sticky="w", **pad)

            row += 1
            ttk.Label(frm, text="Target Future Year").grid(column=0, row=row, sticky="w", **pad)
            self.target_var = tk.StringVar(value=str(dt.datetime.now().year + 5))
            self.target_entry = ttk.Entry(frm, textvariable=self.target_var, width=16)
            self.target_entry.grid(column=1, row=row, sticky="w", **pad)

            row += 1
            self.btn_estimate = ttk.Button(frm, text="Estimate Now", command=self.on_estimate)
            self.btn_estimate.grid(column=0, row=row, **pad)
            self.btn_refresh = ttk.Button(frm, text="Refresh Sources", command=self.on_refresh)
            self.btn_refresh.grid(column=1, row=row, **pad)

            row += 1
            sep = ttk.Separator(frm)
            sep.grid(column=0, row=row, columnspan=3, sticky="ew", pady=(4, 8))

            row += 1
            self.result_box = tk.Text(frm, height=12, wrap="word")
            self.result_box.grid(column=0, row=row, columnspan=3, sticky="nsew", **pad)
            frm.rowconfigure(row, weight=1)
            frm.columnconfigure(2, weight=1)

            row += 1
            self.btn_save_csv = ttk.Button(frm, text="Save Result as CSV", command=self.save_csv)
            self.btn_save_csv.grid(column=0, row=row, **pad)
            self.btn_save_json = ttk.Button(frm, text="Save Result as JSON", command=self.save_json)
            self.btn_save_json.grid(column=1, row=row, **pad)

            row += 1
            self.status_var = tk.StringVar(value="Ready")
            ttk.Label(frm, textvariable=self.status_var).grid(column=0, row=row, columnspan=3, sticky="w", **pad)

        def _set_defaults(self):
            self.baseline_var.set("")  # empty ⇒ default launch year

        def on_refresh(self):
            self.status_var.set("Refreshing sources…")
            self.update_idletasks()
            try:
                self.estimator.refresh_sources()
                self.status_var.set(
                    f"Sources refreshed | WB: {self.estimator.worldbank_refreshed_at} | IMF: {self.estimator.imf_refreshed_at}"
                )
            except Exception as e:
                messagebox.showerror("Refresh failed", str(e))
                self.status_var.set("Refresh failed")

        def on_estimate(self):
            try:
                baseline = self._parse_year(self.baseline_var.get())
                target = self._parse_year(self.target_var.get())
                if target is None:
                    raise ValueError("Target year is required")
                est = self.estimator.estimate(baseline, target)
                self._show_result(est)
                self.status_var.set("Estimate computed")
                self.last_result = est
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.status_var.set("Error")

        def _parse_year(self, s: str) -> Optional[int]:
            s = (s or "").strip()
            if not s:
                return None
            y = int(s)
            if y < 1900 or y > 2100:
                raise ValueError("Year must be between 1900 and 2100")
            return y

        def _show_result(self, est: Estimate):
            doc = {
                "baseline_year": est.baseline_year,
                "target_year": est.target_year,
                "baseline_cpi": round(est.baseline_cpi, 4),
                "target_cpi_estimated": round(est.target_cpi_estimated, 4),
                "price_level_change_pct": round(est.price_level_change_pct, 3),
                "purchasing_power_change_pct": round(est.purchasing_power_change_pct, 3),
                "sources": {
                    "worldbank_cpi": WB_CPI_SERIES,
                    "worldbank_refreshed_at": est.worldbank_refreshed_at,
                    "imf_indicator": IMf_INDICATOR if 'IMf_INDICATOR' in globals() else IMF_INDICATOR,
                    "imf_refreshed_at": est.imf_refreshed_at,
                },
                "explain_steps": est.steps,
            }
            self.result_box.delete("1.0", tk.END)
            self.result_box.insert(tk.END, json.dumps(doc, indent=2))

        def _ensure_last_result(self):
            if not hasattr(self, "last_result") or self.last_result is None:
                raise RuntimeError("No result yet. Click 'Estimate Now' first.")

        def save_csv(self):
            try:
                self._ensure_last_result()
                est = self.last_result
                path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialfile=f"egp_pp_{est.baseline_year}_to_{est.target_year}.csv",
                )
                if not path:
                    return
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow([
                        "baseline_year",
                        "target_year",
                        "baseline_cpi",
                        "target_cpi_estimated",
                        "price_level_change_pct",
                        "purchasing_power_change_pct",
                    ])
                    w.writerow([
                        est.baseline_year,
                        est.target_year,
                        round(est.baseline_cpi, 4),
                        round(est.target_cpi_estimated, 4),
                        round(est.price_level_change_pct, 3),
                        round(est.purchasing_power_change_pct, 3),
                    ])
                messagebox.showinfo("Saved", f"Saved CSV to:\n{path}")
            except Exception as e:
                messagebox.showerror("Save CSV failed", str(e))

        def save_json(self):
            try:
                self._ensure_last_result()
                est = self.last_result
                path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialfile=f"egp_pp_{est.baseline_year}_to_{est.target_year}.json",
                )
                if not path:
                    return
                doc = {
                    "baseline_year": est.baseline_year,
                    "target_year": est.target_year,
                    "baseline_cpi": round(est.baseline_cpi, 4),
                    "target_cpi_estimated": round(est.target_cpi_estimated, 4),
                    "price_level_change_pct": round(est.price_level_change_pct, 3),
                    "purchasing_power_change_pct": round(est.purchasing_power_change_pct, 3),
                    "worldbank_refreshed_at": est.worldbank_refreshed_at,
                    "imf_refreshed_at": est.imf_refreshed_at,
                    "steps": est.steps,
                }
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(doc, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Saved", f"Saved JSON to:\n{path}")
            except Exception as e:
                messagebox.showerror("Save JSON failed", str(e))


# --------------------------
# CLI / TUI helpers
# --------------------------

def _print_result(est: Estimate):
    doc = {
        "baseline_year": est.baseline_year,
        "target_year": est.target_year,
        "baseline_cpi": round(est.baseline_cpi, 4),
        "target_cpi_estimated": round(est.target_cpi_estimated, 4),
        "price_level_change_pct": round(est.price_level_change_pct, 3),
        "purchasing_power_change_pct": round(est.purchasing_power_change_pct, 3),
        "worldbank_refreshed_at": est.worldbank_refreshed_at,
        "imf_refreshed_at": est.imf_refreshed_at,
        "explain_steps": est.steps,
    }
    print(json.dumps(doc, indent=2, ensure_ascii=False))


def _get_env_int(name: str) -> Optional[int]:
    v = os.getenv(name)
    if v is None:
        return None
    v = v.strip()
    if not v:
        return None
    return int(v)


def run_noninteractive(out_path: Optional[str] = None):
    """Fallback when no TTY is available (sandbox/CI). Uses env vars or defaults."""
    svc = EstimatorService()
    baseline = _get_env_int("EGP_BASELINE_YEAR")
    target = _get_env_int("EGP_TARGET_YEAR")
    if target is None:
        target = svc.launch_year + 5  # safe default
    est = svc.estimate(baseline, target)

    path = out_path or os.getenv("EGP_OUT")
    if path:
        if path.lower().endswith(".json"):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "baseline_year": est.baseline_year,
                        "target_year": est.target_year,
                        "baseline_cpi": round(est.baseline_cpi, 4),
                        "target_cpi_estimated": round(est.target_cpi_estimated, 4),
                        "price_level_change_pct": round(est.price_level_change_pct, 3),
                        "purchasing_power_change_pct": round(est.purchasing_power_change_pct, 3),
                        "worldbank_refreshed_at": est.worldbank_refreshed_at,
                        "imf_refreshed_at": est.imf_refreshed_at,
                        "steps": est.steps,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            print(f"Saved JSON: {path}")
        else:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(
                    [
                        "baseline_year",
                        "target_year",
                        "baseline_cpi",
                        "target_cpi_estimated",
                        "price_level_change_pct",
                        "purchasing_power_change_pct",
                        "worldbank_refreshed_at",
                        "imf_refreshed_at",
                    ]
                )
                w.writerow(
                    [
                        est.baseline_year,
                        est.target_year,
                        round(est.baseline_cpi, 4),
                        round(est.target_cpi_estimated, 4),
                        round(est.price_level_change_pct, 3),
                        round(est.purchasing_power_change_pct, 3),
                        est.worldbank_refreshed_at,
                        est.imf_refreshed_at,
                    ]
                )
            print(f"Saved CSV: {path}")
    else:
        _print_result(est)


def run_interactive_cli():
    svc = EstimatorService()
    print("EGP Purchasing Power Estimator (CLI)")
    print("Baseline year (default = launch year): leave empty to use default.")
    try:
        bline = input("Baseline year [Enter=default]: ").strip()
        baseline = int(bline) if bline else None
        target = None
        while target is None:
            t = input("Target future year (e.g., 2030): ").strip()
            if t:
                target = int(t)
            else:
                print("Target year is required.")
    except (OSError, EOFError):  # no TTY / sandbox
        print("No interactive input available. Running in non‑interactive fallback mode…")
        return run_noninteractive()

    try:
        est = svc.estimate(baseline, target)
        _print_result(est)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# --------------------------
# Unit tests (offline, no network)
# --------------------------

def _self_test():  # pragma: no cover
    import unittest

    class Tests(unittest.TestCase):
        def setUp(self):
            # Stub data: CPI actuals through 2022, forecast inflation from 2023
            self.cpi = {2018: 100.0, 2019: 110.0, 2020: 121.0, 2021: 133.1, 2022: 146.41}
            self.infl = {2023: 10.0, 2024: 5.0, 2025: 2.0}

            def cpi_fetch():
                return self.cpi

            def infl_fetch(periods=None):
                return self.infl

            fixed_now = lambda: dt.datetime(2023, 1, 1)
            self.svc = EstimatorService(cpi_fetch, infl_fetch, fixed_now)
            # Preload to avoid network
            self.svc.refresh_sources()

        # Existing tests (unchanged)
        def test_nearest_cpi_backward(self):
            year, val = nearest_cpi(self.cpi, 2020)
            self.assertEqual((year, round(val, 2)), (2020, 121.0))
            year, val = nearest_cpi(self.cpi, 2023)
            self.assertEqual((year, round(val, 2)), (2022, 146.41))

        def test_project_and_estimate(self):
            est = self.svc.estimate(baseline_year=2022, target_year=2025)
            # 2023 projected: 146.41 * 1.10 = 161.051
            # 2024 projected: 161.051 * 1.05 ≈ 169.10355
            # 2025 projected: 169.10355 * 1.02 ≈ 172.48562
            self.assertAlmostEqual(round(est.target_cpi_estimated, 5), 172.48562, places=5)
            ratio = est.target_cpi_estimated / est.baseline_cpi
            self.assertAlmostEqual(round(est.price_level_change_pct, 3), round((ratio - 1) * 100, 3))

        def test_baseline_default_is_launch_year(self):
            # launch year captured from fixed_now() = 2023
            est = self.svc.estimate(baseline_year=None, target_year=2024)
            self.assertEqual(est.baseline_year, 2023)

        def test_invalid_target_before_baseline(self):
            with self.assertRaises(ValueError):
                self.svc.estimate(baseline_year=2024, target_year=2023)

        # New tests
        def test_forecast_fallback_to_previous_year(self):
            # Remove 2025 forecast, it should reuse 2024's rate (5.0)
            infl2 = {2023: 10.0, 2024: 5.0}

            def infl_fetch(periods=None):
                return infl2

            svc2 = EstimatorService(lambda: self.cpi, infl_fetch, lambda: dt.datetime(2023, 1, 1))
            svc2.refresh_sources()
            est = svc2.estimate(baseline_year=2022, target_year=2025)
            # 2023: 146.41*1.10 = 161.051
            # 2024: 161.051*1.05 = 169.10355
            # 2025: 169.10355*1.05 = 177.55873 (fallback uses 5% again)
            self.assertAlmostEqual(round(est.target_cpi_estimated, 5), 177.55873, places=5)

        def test_missing_forecast_raises_error(self):
            # No forecast for 2023 or 2022 ⇒ should raise
            infl3 = {}

            def infl_fetch(periods=None):
                return infl3

            svc3 = EstimatorService(lambda: self.cpi, infl_fetch, lambda: dt.datetime(2022, 12, 31))
            svc3.refresh_sources()
            with self.assertRaises(ValueError):
                svc3.estimate(baseline_year=2022, target_year=2025)

        def test_offline_fallback_with_wb_yoy_hold(self):
            # Simulate IMF failure → raise; provide WB YoY fallback; strategy=hold
            yoy = {2020: 6.0, 2021: 5.0, 2022: 10.0}

            def failing_imf(periods=None):
                raise RuntimeError("IMF down")

            svc = EstimatorService(
                cpi_fetcher=lambda: self.cpi,
                infl_fetcher=failing_imf,
                now_func=lambda: dt.datetime(2022, 12, 31),
                infl_fallback_fetcher=lambda periods=None: yoy,
                allow_offline=True,
                fallback_strategy="hold",
            )
            svc.refresh_sources()
            est = svc.estimate(baseline_year=2022, target_year=2024)
            # 2023 uses 10.0 (last YoY), 2024 holds 10.0
            # 2023: 146.41*1.10=161.051; 2024: *1.10=177.1561
            self.assertAlmostEqual(round(est.target_cpi_estimated, 4), 177.1561, places=4)

        def test_offline_fallback_with_wb_yoy_avg3(self):
            yoy = {2019: 9.0, 2020: 6.0, 2021: 5.0, 2022: 10.0}

            def failing_imf(periods=None):
                raise RuntimeError("IMF down")

            svc = EstimatorService(
                cpi_fetcher=lambda: self.cpi,
                infl_fetcher=failing_imf,
                now_func=lambda: dt.datetime(2022, 12, 31),
                infl_fallback_fetcher=lambda periods=None: yoy,
                allow_offline=True,
                fallback_strategy="avg3",
            )
            svc.refresh_sources()
            est = svc.estimate(baseline_year=2022, target_year=2025)
            # trailing avg3 at 2022 is avg(6,5,10)=7.0 → 2023=7.0
            # 2024 uses avg of (5,10,7)=7.333..., 2025 uses avg of (10,7,7.333..)=8.111...
            c2023 = 146.41 * 1.07
            c2024 = c2023 * (1 + 7.3333333333/100)
            c2025 = c2024 * (1 + 8.1111111111/100)
            self.assertAlmostEqual(est.target_cpi_estimated, c2025, places=4)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    if not res.wasSuccessful():
        sys.exit(1)


# --------------------------
# Main entry
# --------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EGP Purchasing Power Estimator — CLI/GUI")
    parser.add_argument("--gui", action="store_true", help="Launch GUI if Tkinter is available")
    parser.add_argument("--target-year", type=int, help="Target future year (e.g., 2030)")
    parser.add_argument("--baseline-year", type=int, default=None, help="Optional baseline year (default = launch year)")
    parser.add_argument("--out", type=str, default=None, help="Path to CSV or JSON (by extension) to write result")
    parser.add_argument("--self-test", action="store_true", help="Run built-in unit tests (offline)")
    parser.add_argument("--allow-offline", action="store_true", help="Force allow offline fallback (WB YoY)")
    parser.add_argument("--fallback-strategy", choices=["hold", "avg3", "avg5"], help="Offline forecast rule")
    args = parser.parse_args()

    if args.self_test:
        _self_test()
        sys.exit(0)

    # GUI mode requested
    if args.gui:
        if GUI_AVAILABLE:
            app = App()  # type: ignore[name-defined]
            try:
                app.estimator.refresh_sources()
            except Exception:
                pass
            app.mainloop()
            sys.exit(0)
        else:
            print("GUI not available (Tkinter not installed). Falling back to CLI.")

    # Headless one-shot if target provided
    if args.target_year is not None:
        svc = EstimatorService(
            allow_offline=args.allow_offline if args.allow_offline else None,
            fallback_strategy=args.fallback_strategy,
        )
        try:
            est = svc.estimate(args.baseline_year, args.target_year)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

        if args.out:
            path = args.out
            if path.lower().endswith(".json"):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "baseline_year": est.baseline_year,
                            "target_year": est.target_year,
                            "baseline_cpi": round(est.baseline_cpi, 4),
                            "target_cpi_estimated": round(est.target_cpi_estimated, 4),
                            "price_level_change_pct": round(est.price_level_change_pct, 3),
                            "purchasing_power_change_pct": round(est.purchasing_power_change_pct, 3),
                            "worldbank_refreshed_at": est.worldbank_refreshed_at,
                            "imf_refreshed_at": est.imf_refreshed_at,
                            "steps": est.steps,
                        },
                        f,
                        ensure_ascii=False,
                        indent=2,
                    )
                print(f"Saved JSON: {path}")
            else:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(
                        [
                            "baseline_year",
                            "target_year",
                            "baseline_cpi",
                            "target_cpi_estimated",
                            "price_level_change_pct",
                            "purchasing_power_change_pct",
                            "worldbank_refreshed_at",
                            "imf_refreshed_at",
                        ]
                    )
                    w.writerow(
                        [
                            est.baseline_year,
                            est.target_year,
                            round(est.baseline_cpi, 4),
                            round(est.target_cpi_estimated, 4),
                            round(est.price_level_change_pct, 3),
                            round(est.purchasing_power_change_pct, 3),
                            est.worldbank_refreshed_at,
                            est.imf_refreshed_at,
                        ]
                    )
                print(f"Saved CSV: {path}")
        else:
            _print_result(est)
        sys.exit(0)

    # No args → if no TTY, run non‑interactive fallback; otherwise prompt
    try:
        interactive = sys.stdin.isatty()
    except Exception:
        interactive = False

    if interactive:
        run_interactive_cli()
    else:
        run_noninteractive(args.out)
