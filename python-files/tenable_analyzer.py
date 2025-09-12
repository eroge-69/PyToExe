#!/usr/bin/env python3
"""
tenable_gui_onefile.py
Pick files OR scan a root folder (recursive) and produce ONE combined workbook.
You can now CHOOSE which Excel tabs to export via checkboxes.

Output name: "Full Analysis for Endpoints - <Day YYYY-MM-DD HH-MM-SS>.xlsx"

Tabs you can toggle: Summary, Severity, Top_Hosts (Top 100),
                     Top_CVEs (Top 1000), Top_Plugins (Top 1000), Top_Solutions (Top 1000),
                     Per_Host_Severity, Files, Charts
"""

import sys, os, re, threading, traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ===== Top-N controls =====
TOP_HOSTS_N     = 100
TOP_CVES_N      = 1000
TOP_PLUGINS_N   = 1000
TOP_SOLUTIONS_N = 1000
# ==========================

# --- dependencies ---
MISSING = []
try:
    import pandas as pd
except Exception:
    pd = None; MISSING.append("pandas")
try:
    import numpy as np
except Exception:
    np = None; MISSING.append("numpy")
try:
    import xlsxwriter  # noqa: F401
except Exception:
    xlsxwriter = None; MISSING.append("xlsxwriter")
try:
    import matplotlib.pyplot as plt  # optional PNG charts
except Exception:
    plt = None

# ---------------- helpers ----------------
def find_col(cols: List[str], patterns: List[str]) -> str:
    for c in cols:
        cl = str(c).strip()
        for p in patterns:
            if re.search(p, cl, re.IGNORECASE):
                return c
    return ""

def normalize_severity(val) -> str:
    if pd.isna(val):
        return "Unknown"
    s = str(val).strip().lower()
    mapping = {
        "informational": "Info", "information": "Info", "info": "Info",
        "low": "Low", "medium": "Medium", "med": "Medium",
        "high": "High", "critical": "Critical",
        "none": "Unknown", "error": "Unknown",
    }
    return mapping.get(s, s.title())

def auto_detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    cols = list(df.columns)
    return {
        "host":      find_col(cols, [r"^host(name)?$", r"^dns name$", r"^fqdn$"]),
        "risk":      find_col(cols, [r"^risk$", r"^severity$"]),
        "cvss":      find_col(cols, [r"^cvss.*base", r"^cvss v2\.0 base score$"]),
        "cve":       find_col(cols, [r"^cve(s)?$"]),
        "name":      find_col(cols, [r"^name$", r"^plugin name$"]),
        "port":      find_col(cols, [r"^port$"]),
        "protocol":  find_col(cols, [r"^protocol$"]),
        "solution":  find_col(cols, [r"solution", r"remediation"]),
        "metasploit":find_col(cols, [r"^metasploit$"]),
        "coreimpact":find_col(cols, [r"^core impact$"]),
        "canvas":    find_col(cols, [r"^canvas$"]),
    }

def build_data(df: pd.DataFrame, colmap: Dict[str, str]) -> pd.DataFrame:
    out = pd.DataFrame()
    out["Host"] = df[colmap["host"]] if colmap["host"] else None
    sev = df[colmap["risk"]] if colmap["risk"] else None
    out["Severity"] = sev.map(normalize_severity) if sev is not None else "Unknown"
    if colmap["cvss"]:
        out["CVSSv2"] = pd.to_numeric(df[colmap["cvss"]], errors="coerce")
    else:
        out["CVSSv2"] = np.nan
    for src_key, out_col in [
        ("port", "Port"), ("protocol", "Protocol"), ("name", "Name"),
        ("cve", "CVE"), ("solution", "Solution"),
        ("metasploit", "Metasploit"), ("coreimpact", "Core Impact"),
        ("canvas", "CANVAS"),
    ]:
        out[out_col] = df[colmap[src_key]] if colmap[src_key] else np.nan
    return out

def severity_tables(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    order = ["Critical", "High", "Medium", "Low", "Info", "Unknown"]
    counts = df["Severity"].value_counts().reindex(order).fillna(0).astype(int)
    total = int(counts.sum()) if counts.sum() else 0
    sev_df = pd.DataFrame({"Severity": counts.index, "Findings": counts.values})
    sev_df["Percent"] = (sev_df["Findings"] / total * 100).round(2) if total else 0
    per_host_sev = (
        df.pivot_table(index="Host", columns="Severity", values="Name",
                       aggfunc="count", fill_value=0)
        .reindex(columns=order, fill_value=0)
    )
    per_host_sev["Total"] = per_host_sev.sum(axis=1)
    per_host_sev = per_host_sev.sort_values(["Critical","High","Total"], ascending=False)
    return sev_df, per_host_sev

def top_hosts_tables(df: pd.DataFrame):
    per_host = df.groupby("Host").size().rename("Total Findings").sort_values(ascending=False)
    per_host_ch = df[df["Severity"].isin(["Critical","High"])].groupby("Host").size().rename("Critical/High Findings")
    top_hosts = (pd.concat([per_host, per_host_ch], axis=1)
                 .fillna(0).astype(int)
                 .sort_values(["Critical/High Findings","Total Findings"], ascending=False)
                 .head(TOP_HOSTS_N))
    return top_hosts, per_host_ch

def extract_cves(series: pd.Series) -> pd.Series:
    vals: List[str] = []
    for item in series.dropna().astype(str):
        parts = [p.strip() for p in item.replace(";", ",").split(",") if p.strip()]
        vals.extend(parts)
    return pd.Series(vals, dtype=str)

def top_cves_table(df: pd.DataFrame) -> pd.DataFrame:
    if "CVE" not in df.columns: return pd.DataFrame(columns=["CVE","Affected Hosts","Findings"])
    exp = df.copy()
    exp["CVE"] = exp["CVE"].fillna("")
    exp = exp.assign(CVE=exp["CVE"].str.replace(";", ",").str.split(",")).explode("CVE")
    exp["CVE"] = exp["CVE"].str.strip()
    exp = exp[exp["CVE"] != ""]
    if exp.empty: return pd.DataFrame(columns=["CVE","Affected Hosts","Findings"])
    host_count = exp.groupby("CVE")["Host"].nunique().rename("Affected Hosts")
    findings = exp.groupby("CVE").size().rename("Findings")
    return (pd.concat([host_count, findings], axis=1)
            .sort_values(["Affected Hosts","Findings"], ascending=False)
            .head(TOP_CVES_N).reset_index())

def top_plugins_table(df: pd.DataFrame) -> pd.DataFrame:
    by_plugin = df.groupby("Name")["Host"].nunique().sort_values(ascending=False).rename("Affected Hosts").to_frame()
    sev_mode = df.groupby("Name")["Severity"].agg(lambda s: s.mode().iat[0] if len(s.mode()) else "Unknown").rename("Typical Severity")
    return by_plugin.join(sev_mode, how="left").reset_index().head(TOP_PLUGINS_N)

def top_solutions_table(df: pd.DataFrame) -> pd.DataFrame:
    sol = df.copy(); sol["Solution"] = sol["Solution"].fillna("").str.strip()
    sol = sol[sol["Solution"] != ""]
    if sol.empty: return pd.DataFrame(columns=["Solution","Affected Hosts"])
    return (sol.groupby("Solution")["Host"].nunique().sort_values(ascending=False)
            .rename("Affected Hosts").reset_index().head(TOP_SOLUTIONS_N))

def write_excel_report(out_path: Path,
                       summary_df, sev_df, top_hosts, top_cves, top_plugins, top_solutions, per_host_sev,
                       files_table: pd.DataFrame,
                       include: Dict[str, bool]):
    """
    include: dict of tab->bool, keys:
      'Summary','Severity','Top_Hosts','Top_CVEs','Top_Plugins','Top_Solutions','Per_Host_Severity','Files','Charts'
    """
    with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
        # --- data sheets (conditional) ---
        if include.get("Summary", True):
            summary_df.to_excel(writer, index=False, sheet_name="Summary")
        if include.get("Severity", True):
            sev_df.to_excel(writer, index=False, sheet_name="Severity")
        if include.get("Top_Hosts", True):
            top_hosts.to_excel(writer, sheet_name="Top_Hosts")
        if include.get("Top_CVEs", True):
            top_cves.to_excel(writer, index=False, sheet_name="Top_CVEs")
        if include.get("Top_Plugins", True):
            top_plugins.to_excel(writer, index=False, sheet_name="Top_Plugins")
        if include.get("Top_Solutions", True):
            top_solutions.to_excel(writer, index=False, sheet_name="Top_Solutions")
        if include.get("Per_Host_Severity", True):
            per_host_sev.to_excel(writer, sheet_name="Per_Host_Severity")
        if include.get("Files", True):
            (files_table if files_table is not None else pd.DataFrame(columns=["File"])
             ).to_excel(writer, index=False, sheet_name="Files")

        # quick formatting / autofit only for included sheets
        def _autofit(name: str, df_sheet):
            if name in writer.sheets and df_sheet is not None:
                ws = writer.sheets[name]
                ws.set_zoom(110)
                cols = list(df_sheet.columns) if hasattr(df_sheet, "columns") else ["File"]
                for i, col in enumerate(cols):
                    try:
                        width = max(10, min(60, int(df_sheet[col].astype(str).str.len().mean() + 4)))
                    except Exception:
                        width = 24
                    ws.set_column(i, i, width)

        if include.get("Summary", True):           _autofit("Summary", summary_df)
        if include.get("Severity", True):          _autofit("Severity", sev_df)
        if include.get("Top_Hosts", True):         _autofit("Top_Hosts", top_hosts)
        if include.get("Top_CVEs", True):          _autofit("Top_CVEs", top_cves)
        if include.get("Top_Plugins", True):       _autofit("Top_Plugins", top_plugins)
        if include.get("Top_Solutions", True):     _autofit("Top_Solutions", top_solutions)
        if include.get("Per_Host_Severity", True): _autofit("Per_Host_Severity", per_host_sev)
        if include.get("Files", True):             _autofit("Files", files_table if files_table is not None else pd.DataFrame())

        # --- Charts tab (conditional) ---
        if include.get("Charts", True):
            wb = writer.book
            ws_ch = wb.add_worksheet("Charts")

            # Severity chart (needs Severity sheet + data)
            if include.get("Severity", True) and not sev_df.empty:
                sev_rows = len(sev_df)
                ch = wb.add_chart({'type': 'column'})
                ch.set_title({'name': 'Findings by Severity'})
                ch.set_x_axis({'name': 'Severity'})
                ch.set_y_axis({'name': 'Findings'})
                ch.add_series({
                    'name':       'Findings',
                    'categories': f"=Severity!$A$2:$A${sev_rows+1}",
                    'values':     f"=Severity!$B$2:$B${sev_rows+1}",
                })
                ws_ch.insert_chart('A1', ch, {'x_scale': 1.25, 'y_scale': 1.25})

            # Top Hosts chart (needs Top_Hosts + data)
            if include.get("Top_Hosts", True) and not top_hosts.empty:
                host_rows = len(top_hosts)
                ch = wb.add_chart({'type': 'bar'})
                ch.set_title({'name': f'Top Hosts by Critical/High (Top {TOP_HOSTS_N})'})
                ch.set_x_axis({'name': 'Critical/High Findings'})
                ch.set_y_axis({'name': 'Host'})
                ch.add_series({
                    'name':       'Critical/High Findings',
                    'categories': f"=Top_Hosts!$A$2:$A${host_rows+1}",
                    'values':     f"=Top_Hosts!$C$2:$C${host_rows+1}",
                })
                ws_ch.insert_chart('A18', ch, {'x_scale': 1.25, 'y_scale': 1.25})

            # Top CVEs chart (needs Top_CVEs + data)
            if include.get("Top_CVEs", True) and not top_cves.empty:
                cve_rows = len(top_cves)
                ch = wb.add_chart({'type': 'column'})
                ch.set_title({'name': f'Top CVEs by Affected Hosts (Top {min(cve_rows, TOP_CVES_N)})'})
                ch.set_x_axis({'name': 'CVE'})
                ch.set_y_axis({'name': 'Affected Hosts'})
                ch.add_series({
                    'name':       'Affected Hosts',
                    'categories': f"=Top_CVEs!$A$2:$A${cve_rows+1}",
                    'values':     f"=Top_CVEs!$B$2:$B${cve_rows+1}",
                })
                ws_ch.insert_chart('J1', ch, {'x_scale': 1.25, 'y_scale': 1.25})

def maybe_make_charts(out_dir: Path, sev_df, top_hosts, top_cves, df):
    if plt is None:
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    # Severity
    if not sev_df.empty:
        fig = plt.figure(figsize=(7,5)); ax = fig.gca()
        ax.bar(sev_df["Severity"], sev_df["Findings"]); ax.set_title("Findings by Severity")
        ax.set_xlabel("Severity"); ax.set_ylabel("Findings"); fig.tight_layout()
        fig.savefig(out_dir / "severity.png", dpi=150); plt.close(fig)
    # Hosts (Top 100)
    if "Critical/High Findings" in top_hosts.columns and not top_hosts.empty:
        fig = plt.figure(figsize=(14,9)); ax = fig.gca()
        th = top_hosts.head(TOP_HOSTS_N).reset_index()
        ax.bar(th["Host"], th["Critical/High Findings"])
        ax.set_title(f"Top Hosts by Critical/High Findings (Top {TOP_HOSTS_N})")
        ax.set_xlabel("Host"); ax.set_ylabel("Critical/High Findings")
        import matplotlib.pyplot as _plt
        _plt.setp(ax.get_xticklabels(), rotation=90, ha="right", fontsize=7)
        fig.tight_layout(); fig.savefig(out_dir / "top_hosts_ch.png", dpi=150); _plt.close(fig)
    # CVEs (Top 1000)
    if not top_cves.empty:
        fig = plt.figure(figsize=(18,10)); ax = fig.gca()
        tcv = top_cves.head(TOP_CVES_N)
        ax.bar(tcv["CVE"], tcv["Affected Hosts"])
        ax.set_title(f"Top CVEs by Affected Hosts (Top {TOP_CVES_N})")
        ax.set_xlabel("CVE"); ax.set_ylabel("Affected Hosts")
        import matplotlib.pyplot as _plt
        _plt.setp(ax.get_xticklabels(), rotation=90, ha="right", fontsize=6)
        fig.tight_layout(); fig.savefig(out_dir / "top_cves.png", dpi=150); _plt.close(fig)

# --------- file discovery ----------
def collect_excels_under(root_dir: Path, folder_regex: str | None) -> List[Path]:
    """Recursively find .xlsx under root_dir; optional parent-folder regex filter; skip '~$' temp files."""
    if not root_dir.exists():
        return []
    pattern = re.compile(folder_regex, re.IGNORECASE) if folder_regex else None
    results: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        parent = Path(dirpath).name
        for fn in filenames:
            if not fn.lower().endswith(".xlsx"):  continue
            if fn.startswith("~$"):               continue
            p = Path(dirpath) / fn
            if pattern and not pattern.search(parent):
                continue
            results.append(p)
    return results

# ---------------- GUI ----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tenable Analyzer (files or root folder → single output)")
        self.geometry("980x560"); self.minsize(920, 520)

        self.input_paths: List[str] = []
        self.root_dir = tk.StringVar()
        self.folder_filter = tk.StringVar()
        # Tab export toggles
        self.exp_summary = tk.BooleanVar(value=True)
        self.exp_severity = tk.BooleanVar(value=True)
        self.exp_top_hosts = tk.BooleanVar(value=True)
        self.exp_top_cves = tk.BooleanVar(value=True)
        self.exp_top_plugins = tk.BooleanVar(value=True)
        self.exp_top_solutions = tk.BooleanVar(value=True)
        self.exp_per_host = tk.BooleanVar(value=True)
        self.exp_files = tk.BooleanVar(value=True)
        self.exp_charts = tk.BooleanVar(value=True)
        # PNG charts toggle
        self.save_png = tk.BooleanVar(value=False)

        pad = {"padx":10, "pady":6}
        frm = ttk.Frame(self); frm.pack(fill="both", expand=True, **pad)

        # --- Mode A: pick files ---
        ttk.Label(frm, text="Pick file(s) (.xlsx):").grid(row=0, column=0, sticky="w")
        self.ent_files = ttk.Entry(frm, width=60)
        self.ent_files.grid(row=0, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse Files…", command=self.browse_inputs).grid(row=0, column=2, sticky="e")
        self.lbl_count = ttk.Label(frm, text="No files selected.")
        self.lbl_count.grid(row=1, column=1, sticky="w", **pad)

        # --- Mode B: scan root folder ---
        ttk.Label(frm, text="Or scan ROOT folder:").grid(row=2, column=0, sticky="w")
        self.ent_root = ttk.Entry(frm, textvariable=self.root_dir, width=60)
        self.ent_root.grid(row=2, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse Folder…", command=self.browse_root).grid(row=2, column=2, sticky="e")

        ttk.Label(frm, text="Folder filter (regex, optional):").grid(row=3, column=0, sticky="w")
        self.ent_filter = ttk.Entry(frm, textvariable=self.folder_filter, width=60)
        self.ent_filter.grid(row=3, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Scan Now", command=self.scan_root).grid(row=3, column=2, sticky="e")

        self.lbl_scan = ttk.Label(frm, text="No folder scanned yet.")
        self.lbl_scan.grid(row=4, column=1, sticky="w", **pad)

        # --- Export tab checkboxes ---
        grp = ttk.LabelFrame(frm, text="Tabs to export")
        grp.grid(row=5, column=0, columnspan=3, sticky="we", padx=10, pady=10)
        # left column
        ttk.Checkbutton(grp, text="Summary", variable=self.exp_summary).grid(row=0, column=0, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(grp, text="Severity", variable=self.exp_severity).grid(row=1, column=0, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(grp, text=f"Top Hosts (Top {TOP_HOSTS_N})", variable=self.exp_top_hosts).grid(row=2, column=0, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(grp, text=f"Top CVEs (Top {TOP_CVES_N})", variable=self.exp_top_cves).grid(row=3, column=0, sticky="w", padx=8, pady=4)
        # right column
        ttk.Checkbutton(grp, text=f"Top Plugins (Top {TOP_PLUGINS_N})", variable=self.exp_top_plugins).grid(row=0, column=1, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(grp, text=f"Top Solutions (Top {TOP_SOLUTIONS_N})", variable=self.exp_top_solutions).grid(row=1, column=1, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(grp, text="Per-Host Severity", variable=self.exp_per_host).grid(row=2, column=1, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(grp, text="Files", variable=self.exp_files).grid(row=3, column=1, sticky="w", padx=8, pady=4)
        # charts & png
        ttk.Checkbutton(grp, text="Charts tab", variable=self.exp_charts).grid(row=0, column=2, sticky="w", padx=8, pady=4)
        ttk.Checkbutton(grp, text="Also save PNG charts", variable=self.save_png).grid(row=1, column=2, sticky="w", padx=8, pady=4)

        # quick buttons
        ttk.Button(grp, text="Select All Tabs", command=self._select_all_tabs).grid(row=2, column=2, sticky="w", padx=8, pady=4)
        ttk.Button(grp, text="Clear All Tabs", command=self._clear_all_tabs).grid(row=3, column=2, sticky="w", padx=8, pady=4)

        # Run
        self.btn_run = ttk.Button(frm, text="Run Analysis", command=self.run_clicked)
        self.btn_run.grid(row=6, column=1, sticky="e", **pad)

        # Status
        self.status = tk.StringVar(value="Ready.")
        ttk.Label(frm, textvariable=self.status).grid(row=7, column=0, columnspan=3, sticky="w", **pad)

        frm.columnconfigure(1, weight=1)

        if MISSING:
            messagebox.showwarning(
                "Missing packages",
                "Install required packages:\n\n"
                f"python -m pip install {' '.join(MISSING)}\n\n"
                "PNG charts are optional (matplotlib)."
            )

    # ---------- UI helpers ----------
    def _select_all_tabs(self):
        for v in [self.exp_summary, self.exp_severity, self.exp_top_hosts, self.exp_top_cves,
                  self.exp_top_plugins, self.exp_top_solutions, self.exp_per_host, self.exp_files, self.exp_charts]:
            v.set(True)

    def _clear_all_tabs(self):
        for v in [self.exp_summary, self.exp_severity, self.exp_top_hosts, self.exp_top_cves,
                  self.exp_top_plugins, self.exp_top_solutions, self.exp_per_host, self.exp_files, self.exp_charts]:
            v.set(False)

    # ---------- UI actions ----------
    def browse_inputs(self):
        paths = filedialog.askopenfilenames(title="Select one or more Tenable Excel exports",
                                            filetypes=[("Excel files","*.xlsx")])
        if paths:
            self.input_paths = list(paths)
            first = Path(self.input_paths[0]).name
            extra = f" (+{len(self.input_paths)-1} more)" if len(self.input_paths) > 1 else ""
            self.ent_files.delete(0, tk.END)
            self.ent_files.insert(0, first + extra)
            self.lbl_count.config(text=f"{len(self.input_paths)} file(s) selected.")

    def browse_root(self):
        folder = filedialog.askdirectory(title="Select root folder to scan")
        if folder:
            self.root_dir.set(folder)
            self.lbl_scan.config(text="Ready to scan… (click Scan Now)")

    def scan_root(self):
        root = self.root_dir.get().strip()
        filt = self.folder_filter.get().strip() or None
        if not root:
            messagebox.showwarning("Select folder", "Please choose a root folder first.")
            return
        root_p = Path(root)
        found = collect_excels_under(root_p, filt)
        self.input_paths = [str(p) for p in found]
        self.ent_files.delete(0, tk.END)
        self.ent_files.insert(0, (root_p.name + f" [{len(self.input_paths)} file(s)]"))
        self.lbl_count.config(text=f"{len(self.input_paths)} file(s) (from folder scan)")
        if filt:
            self.lbl_scan.config(text=f"Scanned with filter /{filt}/ — {len(self.input_paths)} file(s) found.")
        else:
            self.lbl_scan.config(text=f"Scanned — {len(self.input_paths)} file(s) found.")

    def run_clicked(self):
        if pd is None or np is None or xlsxwriter is None:
            messagebox.showerror("Dependencies missing",
                                 "Install required packages first:\npython -m pip install pandas numpy xlsxwriter matplotlib")
            return
        if not self.input_paths:
            messagebox.showwarning("No input", "Select files or scan a root folder to collect .xlsx.")
            return
        self.status.set("Running…")
        self.btn_run.config(state="disabled")
        threading.Thread(target=self._do_run, daemon=True).start()

    # ---------- core run ----------
    def _do_run(self):
        try:
            # Build combined dataset
            frames = []
            files_ok = []
            for p in self.input_paths:
                in_p = Path(p)
                if not in_p.exists():
                    continue
                try:
                    xls = pd.ExcelFile(in_p)
                    df = xls.parse(xls.sheet_names[0])
                except Exception:
                    continue  # skip unreadable
                df.columns = [str(c).strip() for c in df.columns]
                colmap = auto_detect_columns(df)
                data = build_data(df, colmap)
                data["__SourceFile"] = in_p.name
                data["__SourceFolder"] = in_p.parent.name
                frames.append(data)
                files_ok.append(str(in_p))

            if not frames:
                raise FileNotFoundError("No readable Excel files.")

            data = pd.concat(frames, ignore_index=True)

            # Tables on combined data
            sev_df, per_host_sev = severity_tables(data)
            top_hosts, per_host_ch = top_hosts_tables(data)
            top_cves = top_cves_table(data)
            top_plugins = top_plugins_table(data)
            top_solutions = top_solutions_table(data)

            # Summary (combined)
            total_findings = int(len(data))
            unique_hosts = int(data["Host"].nunique(dropna=True))
            distinct_cves = int(extract_cves(data["CVE"]).nunique()) if "CVE" in data.columns else 0
            exploitable = 0
            for c in ["Metasploit","Core Impact","CANVAS"]:
                if c in data.columns:
                    exploitable += int(data[c].astype(str).str.lower().isin(["yes","true","1"]).sum())
            critical = int((data["Severity"]=="Critical").sum())
            high = int((data["Severity"]=="High").sum())
            summary_rows = [
                ("Total findings (rows)", total_findings),
                ("Unique hosts", unique_hosts),
                ("Distinct CVEs", distinct_cves),
                ("Findings with exploit available", exploitable),
                ("% Critical+High", round(100.0*(critical+high)/total_findings, 2) if total_findings else 0.0),
                ("Hosts with ≥500 Critical/High findings", int((per_host_ch >= 500).sum())),
            ]
            summary_df = pd.DataFrame(summary_rows, columns=["Metric","Value"])

            # Files table (with folder & filename & full path)
            files_table = pd.DataFrame(
                [{"Folder": Path(f).parent.name, "File": Path(f).name, "FullPath": f} for f in files_ok]
            )

            # Output name: Full Analysis for Endpoints - Day YYYY-MM-DD HH-MM-SS.xlsx
            ts = datetime.now().strftime("%a %Y-%m-%d %H-%M-%S")
            out_name = f"Full Analysis for Endpoints - {ts}.xlsx"
            base_dir = Path(self.root_dir.get()) if self.root_dir.get().strip() else Path(files_ok[0]).parent
            out_path = base_dir / out_name

            # Build "include" map from checkboxes
            include = {
                "Summary":           self.exp_summary.get(),
                "Severity":          self.exp_severity.get(),
                "Top_Hosts":         self.exp_top_hosts.get(),
                "Top_CVEs":          self.exp_top_cves.get(),
                "Top_Plugins":       self.exp_top_plugins.get(),
                "Top_Solutions":     self.exp_top_solutions.get(),
                "Per_Host_Severity": self.exp_per_host.get(),
                "Files":             self.exp_files.get(),
                "Charts":            self.exp_charts.get(),
            }

            # Save (fallback if locked)
            try:
                write_excel_report(out_path,
                                   summary_df, sev_df, top_hosts, top_cves, top_plugins, top_solutions, per_host_sev,
                                   files_table,
                                   include)
                final_path = out_path
                note = ""
            except PermissionError:
                alt = out_path.with_name(f"{out_path.stem}_{datetime.now():%Y%m%d_%H%M%S}{out_path.suffix}")
                write_excel_report(alt,
                                   summary_df, sev_df, top_hosts, top_cves, top_plugins, top_solutions, per_host_sev,
                                   files_table,
                                   include)
                final_path = alt
                note = ("\n\n(Original file name was locked by Excel/OneDrive. "
                        f"Saved as: {alt})")

            # Optional PNG charts (combined) — independent of tab inclusion
            if self.save_png.get():
                if plt is None:
                    raise RuntimeError("matplotlib not installed; cannot save PNG charts.")
                charts_dir = final_path.parent / "charts"
                maybe_make_charts(charts_dir, sev_df, top_hosts, top_cves, data)
                note += f"\nCharts folder: {charts_dir}"

            self._on_done(True, f"Report saved: {final_path}{note}")

        except Exception as e:
            err = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self._on_done(False, err)

    def _on_done(self, ok: bool, msg: str):
        def _upd():
            self.btn_run.config(state="normal")
            self.status.set("Done." if ok else "Failed.")
            (messagebox.showinfo if ok else messagebox.showerror)("Result", msg)
        self.after(0, _upd)

# ---------------- main ----------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
