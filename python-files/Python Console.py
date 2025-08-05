#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cdr_report_excel_or_csv_jalali_plus5.py

Updates:
- Summary shows per-extension columns: answered, missed, talk_time (sum), avg_talk_time.
  * "missed" is displayed BUT NOT counted into "answered" totals (i.e., not attributed).
- Talk time calculation is more robust:
  * Detects billsec/duration under many aliases
  * Parses numeric strings with spaces
  * Parses HH:MM:SS strings -> seconds
"""

import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import pandas as pd
except ImportError:
    raise SystemExit("Missing package pandas. Install with: pip install pandas openpyxl")

# Jalali libraries (optional but needed for Jalali mode)
JALALI_LIB = None
try:
    from persiantools.jdatetime import JalaliDate, JalaliDateTime
    JALALI_LIB = "persiantools"
except Exception:
    try:
        import jdatetime
        JALALI_LIB = "jdatetime"
    except Exception:
        JALALI_LIB = None

DEFAULT_FILE_PATH = r"C:\cdr\cdr.xlsx"  # change if needed

PERSIAN_DISP_MAP = {
    "پاسخ داده شده": "ANSWERED",
    "پاسخ داده": "ANSWERED",
    "بی پاسخ": "NO ANSWER",
    "بی‌پاسخ": "NO ANSWER",
    "ناموفق": "FAILED",
    "مشغول": "BUSY",
    "لغو": "CANCELLED",
}

FA_TO_EN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

def fa_date_normalize(s: str) -> str:
    s = (s or "").strip().translate(FA_TO_EN_DIGITS)
    s = s.replace("/", "-")
    return s

def _smart_read_csv(path: str) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "cp1256", "windows-1256", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, engine="python")

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {}
    lowered = {str(c).lower().strip(): c for c in df.columns}
    def find(*names):
        for n in names:
            if n in lowered:
                return lowered[n]
        return None
    calldate_col = find("calldate", "call_date", "date", "time", "starttime", "start_time")
    src_col      = find("src", "source", "callerid", "clid", "from")
    dst_col      = find("dst", "destination", "to", "did")
    disp_col     = find("disposition", "status", "result", "callstatus")
    billsec_col  = find("billsec", "bill_sec", "bill seconds", "bill_seconds", "talktime", "talk_time", "talk", "bill", "billable")
    duration_col = find("duration", "dur", "call_duration", "calllength", "length")
    if calldate_col: col_map[calldate_col] = "calldate"
    if src_col:      col_map[src_col]      = "src"
    if dst_col:      col_map[dst_col]      = "dst"
    if disp_col:     col_map[disp_col]     = "disposition"
    if billsec_col:  col_map[billsec_col]  = "billsec"
    if duration_col: col_map[duration_col] = "duration"
    return df.rename(columns=col_map)

def _parse_datetime_series(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return pd.to_datetime(s, unit="d", origin="1899-12-30", errors="coerce")
    dt = pd.to_datetime(s, errors="coerce", infer_datetime_format=True, dayfirst=False)
    if dt.isna().mean() > 0.3:
        dt2 = pd.to_datetime(s, errors="coerce", dayfirst=True)
        if dt2.isna().mean() < dt.isna().mean():
            dt = dt2
    return dt

def parse_hms_to_seconds(text: str):
    # Accept H:M:S, M:S, or S
    if not isinstance(text, str):
        return None
    t = text.strip()
    if not t:
        return None
    # e.g., "01:02:03" or "5:33"
    if ":" in t:
        parts = t.split(":")
        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h, m, s = "0", parts[0], parts[1]
        else:
            return None
        try:
            h = int(re.sub(r"\D", "", h))
            m = int(re.sub(r"\D", "", m))
            s = int(re.sub(r"\D", "", s))
            return h*3600 + m*60 + s
        except Exception:
            return None
    # plain number (possibly with spaces)
    t2 = re.sub(r"[^\d.]", "", t)
    if t2 == "":
        return None
    try:
        return int(float(t2))
    except Exception:
        return None

def _ensure_types(df: pd.DataFrame) -> pd.DataFrame:
    if "calldate" in df.columns:
        df["calldate"] = _parse_datetime_series(df["calldate"])
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    # normalize billsec/duration -> talk_seconds_source (raw)
    raw = None
    if "billsec" in df.columns:
        raw = "billsec"
    elif "duration" in df.columns:
        raw = "duration"
    # try parse seconds from strings including HH:MM:SS
    if raw:
        df["talk_seconds"] = df[raw].apply(lambda x: parse_hms_to_seconds(x) if isinstance(x, str) else (int(x) if pd.notna(x) else 0))
        df["talk_seconds"] = df["talk_seconds"].fillna(0).astype(int)
    else:
        df["talk_seconds"] = 0
    return df

def _norm_disposition(val: str) -> str:
    if not isinstance(val, str):
        return ""
    v = val.strip()
    if v in PERSIAN_DISP_MAP:
        return PERSIAN_DISP_MAP[v]
    vu = v.upper().replace("-", " ").replace("_", " ").replace("  ", " ")
    if "ANSWERED" in vu or vu == "ANSWER":
        return "ANSWERED"
    if "NO ANSWER" in vu or "NOANSWER" in vu or "NOT ANSWERED" in vu:
        return "NO ANSWER"
    if "BUSY" in vu:
        return "BUSY"
    if "FAIL" in vu or "FAILED" in vu:
        return "FAILED"
    if "CANCEL" in vu or "CANCELLED" in vu or "CANCELED" in vu:
        return "CANCELLED"
    if "پاسخ" in v and ("داده" in v or "شد" in v):
        return "ANSWERED"
    if "بی پاسخ" in v or "بی‌پاسخ" in v:
        return "NO ANSWER"
    if "مشغول" in v:
        return "BUSY"
    if "ناموفق" in v:
        return "FAILED"
    if "لغو" in v:
        return "CANCELLED"
    return vu

def jalali_to_gregorian_dt(date_str: str, end_of_day: bool=False):
    date_str = fa_date_normalize(date_str)
    if JALALI_LIB == "persiantools":
        y, m, d = map(int, date_str.split("-"))
        g = JalaliDate(y, m, d).to_gregorian()
        ts = pd.Timestamp(g.year, g.month, g.day)
    elif JALALI_LIB == "jdatetime":
        y, m, d = map(int, date_str.split("-"))
        g = jdatetime.date(y, m, d).togregorian()
        ts = pd.Timestamp(g.year, g.month, g.day)
    else:
        raise RuntimeError("Jalali library not found. Install persiantools or jdatetime.")
    if end_of_day:
        return ts + pd.Timedelta(hours=23, minutes=59, seconds=59)
    return ts

def gregorian_to_jalali_str(dt) -> str:
    if pd.isna(dt):
        return ""
    if JALALI_LIB == "persiantools":
        jdt = JalaliDateTime.fromgregorian(datetime=pd.to_datetime(dt).to_pydatetime())
        return jdt.strftime("%Y-%m-%d %H:%M:%S")
    elif JALALI_LIB == "jdatetime":
        g = pd.to_datetime(dt).to_pydatetime()
        jdt = jdatetime.datetime.fromgregorian(datetime=g)
        return jdt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return pd.to_datetime(dt).strftime("%Y-%m-%d %H:%M:%S")

def format_coverage_strings(max_ts):
    if pd.isna(max_ts):
        return "", ""
    g = pd.to_datetime(max_ts)
    g_str = g.strftime("%Y-%m-%d %H:%M:%S")
    j_str = gregorian_to_jalali_str(g)
    return g_str, j_str

def sec_to_hms_str(sec: int) -> str:
    sec = int(sec or 0)
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

class ExcelCDRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CDR Report (Excel/CSV) — Answered-only totals + Missed column + Talk Time")
        self.df = None
        self.summary_df = None
        self.filtered_df = None
        self.max_ts_filtered = None
        self.missed_overall = 0

        # File
        file_frame = ttk.LabelFrame(root, text="Source File (Excel/CSV)")
        file_frame.pack(fill="x", padx=8, pady=6)
        self.path_var = tk.StringVar(value=DEFAULT_FILE_PATH)
        ttk.Entry(file_frame, textvariable=self.path_var, width=70).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Button(file_frame, text="Browse...", command=self.browse).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Load", command=self.load_file).grid(row=0, column=2, padx=5, pady=5)

        # Filters
        filt = ttk.LabelFrame(root, text="Filters")
        filt.pack(fill="x", padx=8, pady=6)
        self.group_var = tk.StringVar(value="dst")
        self.ext_var = tk.StringVar(value="")
        self.start_var = tk.StringVar(value="")
        self.end_var = tk.StringVar(value="")
        self.date_mode_var = tk.StringVar(value="jalali")
        self.tz_offset_var = tk.StringVar(value="0")

        ttk.Label(filt, text="Group by (src/dst):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(filt, textvariable=self.group_var, width=10).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(filt, text="Filter Extension (optional):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(filt, textvariable=self.ext_var, width=20).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(filt, text="Start Date:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(filt, textvariable=self.start_var, width=20).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(filt, text="End Date:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(filt, textvariable=self.end_var, width=20).grid(row=2, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(filt, text="Date input:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(filt, text="Jalali (YYYY-MM-DD or YYYY/MM/DD)", variable=self.date_mode_var, value="jalali").grid(row=3, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(filt, text="Gregorian (YYYY-MM-DD)", variable=self.date_mode_var, value="gregorian").grid(row=3, column=2, padx=5, pady=5, sticky="w")

        ttk.Label(filt, text="Timezone offset (hours):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(filt, textvariable=self.tz_offset_var, width=6).grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Buttons
        btns = ttk.Frame(root)
        btns.pack(fill="x", padx=8, pady=4)
        ttk.Button(btns, text="Generate Report", command=self.run_report).pack(side="left", padx=4)
        ttk.Button(btns, text="Disposition Breakdown", command=self.show_disposition_breakdown).pack(side="left", padx=4)
        ttk.Button(btns, text="Export Summary", command=self.export_summary).pack(side="left", padx=4)
        ttk.Button(btns, text="Export Detailed", command=self.export_detailed).pack(side="left", padx=4)

        # Counters + Coverage
        counters = ttk.Frame(root)
        counters.pack(fill="x", padx=8, pady=(0, 6))
        self.ans_total_var = tk.StringVar(value="Answered (attributed): -")
        self.miss_total_var  = tk.StringVar(value="Missed (overall, not attributed): -")
        ttk.Label(counters, textvariable=self.ans_total_var).pack(side="left", padx=(0, 30))
        ttk.Label(counters, textvariable=self.miss_total_var).pack(side="left", padx=(0, 30))

        coverage = ttk.Frame(root)
        coverage.pack(fill="x", padx=8, pady=(0, 6))
        self.cov_g_var = tk.StringVar(value="Coverage (Gregorian): -")
        self.cov_j_var = tk.StringVar(value="Coverage (Jalali): -")
        ttk.Label(coverage, textvariable=self.cov_g_var).pack(side="left", padx=(0, 20))
        ttk.Label(coverage, textvariable=self.cov_j_var).pack(side="left", padx=(0, 20))

        # Table
        table_frame = ttk.LabelFrame(root, text="Summary by Extension (Answered totals + Missed column)")
        table_frame.pack(fill="both", expand=True, padx=8, pady=6)
        self.tree = ttk.Treeview(table_frame, columns=("ext", "answered", "missed", "talk_time", "avg_talk_time"), show="headings")
        headers = {
            "ext": "Extension",
            "answered": "Answered",
            "missed": "Missed",
            "talk_time": "Talk time (sum)",
            "avg_talk_time": "Avg talk time"
        }
        for col in ("ext", "answered", "missed", "talk_time", "avg_talk_time"):
            self.tree.heading(col, text=headers[col])
            anchor = "center" if col == "ext" else "e"
            self.tree.column(col, width=160 if col == "ext" else 130, anchor=anchor)
        self.tree.pack(fill="both", expand=True)

        # Status
        status = ttk.Frame(root)
        status.pack(fill="x", padx=8, pady=(0,8))
        self.status_var = tk.StringVar(value="Load a file to begin.")
        ttk.Label(status, textvariable=self.status_var).pack(side="left")

    def browse(self):
        path = filedialog.askopenfilename(
            title="Select CDR Excel/CSV file",
            filetypes=[("Excel/CSV files", "*.xlsx;*.xls;*.csv"), ("All files", "*.*")])
        if path:
            self.path_var.set(path)

    def load_file(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showerror("Error", "Please select a file.")
            return
        if not os.path.exists(path):
            messagebox.showerror("Error", f"File not found:\n{path}")
            return
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".csv":
                df = _smart_read_csv(path)
            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(path, engine="openpyxl")
            else:
                raise ValueError("Unsupported file format: " + ext)

            df = _normalize_columns(df)
            missing = [c for c in ("calldate", "src", "dst", "disposition") if c not in df.columns]
            if missing:
                messagebox.showerror("Columns missing",
                                     "These required columns were not found after normalization:\n"
                                     + ", ".join(missing))
                return

            df = _ensure_types(df)
            if "disposition" in df.columns:
                df["disposition_norm"] = df["disposition"].apply(_norm_disposition)
            else:
                df["disposition_norm"] = ""

            self.df = df
            max_all = pd.to_datetime(df["calldate"]).max() if "calldate" in df.columns else pd.NaT
            g_str, j_str = format_coverage_strings(max_all)
            self.cov_g_var.set(f"Coverage (Gregorian): {g_str or '-'} (all rows)")
            self.cov_j_var.set(f"Coverage (Jalali): {j_str or '-'} (all rows)")
            self.status_var.set(f"Loaded {len(df)} rows from {os.path.basename(path)}.")
        except Exception as e:
            messagebox.showerror("Load failed", str(e))

    def _convert_input_dates(self):
        start = fa_date_normalize(self.start_var.get().strip())
        end = fa_date_normalize(self.end_var.get().strip())
        mode = (self.date_mode_var.get() or "jalali").lower()
        start_ts = end_ts = None
        if start:
            if mode == "jalali":
                if not JALALI_LIB:
                    raise RuntimeError("Jalali library not found. Install persiantools or jdatetime.")
                start_ts = jalali_to_gregorian_dt(start, end_of_day=False)
            else:
                start_ts = pd.to_datetime(start + " 00:00:00")
        if end:
            if mode == "jalali":
                if not JALALI_LIB:
                    raise RuntimeError("Jalali library not found. Install persiantools or jdatetime.")
                end_ts = jalali_to_gregorian_dt(end, end_of_day=True)
            else:
                end_ts = pd.to_datetime(end + " 23:59:59")
        return start_ts, end_ts

    def _apply_tz_offset(self, s: pd.Series, hours: float) -> pd.Series:
        try:
            h = float(hours)
        except Exception:
            h = 0.0
        return s + pd.to_timedelta(h, unit="h")

    def _get_coverage_filtered(self, df: pd.DataFrame):
        if df is None or df.empty or "calldate" not in df.columns:
            return pd.NaT
        return pd.to_datetime(df["calldate"]).max()

    def run_report(self):
        if self.df is None or self.df.empty:
            messagebox.showerror("No data", "Please load a file first.")
            return
        df = self.df.copy()

        # Timezone offset (optional)
        tz_off = (self.tz_offset_var.get() or "0").strip()
        if "calldate" in df.columns and tz_off not in ("", "0", "0.0"):
            df["calldate"] = self._apply_tz_offset(df["calldate"], tz_off)

        # Date filtering
        try:
            start_ts, end_ts = self._convert_input_dates()
        except Exception as e:
            messagebox.showerror("Date error", str(e))
            return
        if start_ts is not None:
            df = df[df["calldate"] >= start_ts]
        if end_ts is not None:
            df = df[df["calldate"] <= end_ts]

        # Grouping target
        group = (self.group_var.get() or "dst").strip().lower()
        if group not in ("src", "dst"):
            group = "dst"

        # Optional extension filter
        ext = self.ext_var.get().strip()
        if ext:
            df = df[df[group].astype(str) == ext]

        # Flags
        disp = df["disposition_norm"].str.upper().fillna("")
        df["is_answered"] = (disp == "ANSWERED").astype(int)
        df["is_missed"] = disp.isin(["NO ANSWER", "BUSY", "FAILED", "CANCELLED"]).astype(int)

        # Answered and missed subsets
        df_ans = df[df["is_answered"] == 1].copy()
        df_miss = df[df["is_missed"] == 1].copy()
        self.missed_overall = int(df_miss.shape[0])

        # Per-extension answered metrics
        summary_ans = df_ans.groupby(group, dropna=False).agg(
            answered=(group, "size"),
            talk_time_sec=("talk_seconds", "sum"),
            avg_talk_time_sec=("talk_seconds", "mean"),
        ).reset_index().rename(columns={group: "ext"})

        # Per-extension missed counts (for display only)
        summary_miss = df_miss.groupby(group, dropna=False).agg(
            missed=(group, "size")
        ).reset_index().rename(columns={group: "ext"})

        # Merge
        summary = pd.merge(summary_ans, summary_miss, on="ext", how="outer").fillna(0)
        # Cast
        if not summary.empty:
            for c in ("answered", "missed"):
                summary[c] = summary[c].astype(int)
            summary["talk_time_sec"] = summary["talk_time_sec"].fillna(0).astype(int)
            summary["avg_talk_time_sec"] = summary["avg_talk_time_sec"].fillna(0).round(1)

        # Sort by answered desc then missed desc
        summary = summary.sort_values(["answered", "missed"], ascending=[False, False])

        self.summary_df = summary
        self.filtered_df = df  # keep full filtered

        # Update table
        for i in self.tree.get_children():
            self.tree.delete(i)
        for _, r in summary.iterrows():
            self.tree.insert(
                "", "end",
                values=(
                    str(r["ext"]),
                    int(r["answered"]),
                    int(r["missed"]),
                    sec_to_hms_str(int(r["talk_time_sec"])),
                    sec_to_hms_str(int(round(r["avg_talk_time_sec"]))),
                )
            )

        ans_total = int(summary["answered"].sum()) if not summary.empty else 0
        self.ans_total_var.set(f"Answered (attributed): {ans_total}")
        self.miss_total_var.set(f"Missed (overall, not attributed): {self.missed_overall}")

        # Coverage on filtered data
        self.max_ts_filtered = self._get_coverage_filtered(df)
        g_str, j_str = format_coverage_strings(self.max_ts_filtered)
        self.cov_g_var.set(f"Coverage (Gregorian): {g_str or '-'} (filtered)")
        self.cov_j_var.set(f"Coverage (Jalali): {j_str or '-'} (filtered)")

        self.status_var.set(f"Report generated. {len(summary)} extensions (answered totals + missed column).")

    def show_disposition_breakdown(self):
        if self.df is None or self.df.empty:
            messagebox.showerror("No data", "Load a file first.")
            return
        disp_counts = self.df["disposition_norm"].value_counts(dropna=False).reset_index()
        disp_counts.columns = ["disposition_norm", "count"]
        lines = [f"{row['disposition_norm']}: {row['count']}" for _, row in disp_counts.iterrows()]
        messagebox.showinfo("Disposition Breakdown", "\n".join(lines) if lines else "No disposition data.")

    def _current_coverage_strings(self):
        max_ts = self.max_ts_filtered
        if pd.isna(max_ts):
            if self.filtered_df is not None and not self.filtered_df.empty:
                max_ts = self._get_coverage_filtered(self.filtered_df)
            elif self.df is not None and not self.df.empty:
                max_ts = self._get_coverage_filtered(self.df)
            else:
                max_ts = pd.NaT
        return format_coverage_strings(max_ts)

    def _build_info_sheet_df(self):
        g_str, j_str = self._current_coverage_strings()
        data = {
            "key": [
                "group_by", "extension_filter", "date_input_mode",
                "start_input", "end_input", "timezone_offset_hours",
                "coverage_gregorian", "coverage_jalali",
                "missed_overall_not_attributed"
            ],
            "value": [
                (self.group_var.get() or ""),
                (self.ext_var.get() or ""),
                (self.date_mode_var.get() or ""),
                (self.start_var.get() or ""),
                (self.end_var.get() or ""),
                (self.tz_offset_var.get() or "0"),
                g_str, j_str,
                str(self.missed_overall)
            ]
        }
        return pd.DataFrame(data)

    def export_summary(self):
        if self.summary_df is None or self.summary_df.empty:
            messagebox.showerror("Export Error", "No summary to export. Generate the report first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], title="Save Summary As")
        if not path:
            return
        try:
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                g_str, j_str = self._current_coverage_strings()

                df_sum = self.summary_df.copy()
                df_sum["talk_time_hms"] = df_sum["talk_time_sec"].apply(sec_to_hms_str)
                df_sum["avg_talk_time_hms"] = df_sum["avg_talk_time_sec"].apply(lambda x: sec_to_hms_str(int(round(x))))
                export_cols = ["ext", "answered", "missed", "talk_time_sec", "talk_time_hms", "avg_talk_time_sec", "avg_talk_time_hms"]
                df_sum[export_cols].to_excel(writer, index=False, sheet_name="Summary", startrow=3)

                ws = writer.sheets["Summary"]
                ws["A1"] = f"Coverage through (Gregorian): {g_str or '-'}"
                ws["A2"] = f"Coverage through (Jalali): {j_str or '-'}"
                ws["E1"] = f"Missed (overall, not attributed): {self.missed_overall}"
                ws.freeze_panes = "A4"

                info_df = self._build_info_sheet_df()
                info_df.to_excel(writer, index=False, sheet_name="Info")
            messagebox.showinfo("Exported", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def export_detailed(self):
        if self.filtered_df is None or self.filtered_df.empty:
            messagebox.showerror("Export Error", "No filtered rows to export. Generate the report first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], title="Save Detailed As")
        if not path:
            return
        try:
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                df = self.filtered_df.copy()
                if "calldate" in df.columns:
                    df["calldate_gregorian"] = pd.to_datetime(df["calldate"]).dt.strftime("%Y-%m-%d %H:%M:%S")
                    df["calldate_jalali"] = df["calldate"].apply(gregorian_to_jalali_str)
                for c in df.select_dtypes(include=["object"]).columns:
                    df[c] = df[c].astype(str)
                df.to_excel(writer, index=False, sheet_name="Detailed", startrow=3)

                g_str, j_str = self._current_coverage_strings()
                ws = writer.sheets["Detailed"]
                ws["A1"] = f"Coverage through (Gregorian): {g_str or '-'}"
                ws["A2"] = f"Coverage through (Jalali): {j_str or '-'}"
                ws["E1"] = f"Missed (overall, not attributed): {self.missed_overall}"
                ws.freeze_panes = "A4"

                info_df = self._build_info_sheet_df()
                info_df.to_excel(writer, index=False, sheet_name="Info")
            messagebox.showinfo("Exported", f"Saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelCDRApp(root)
    root.mainloop()
