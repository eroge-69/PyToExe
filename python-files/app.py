import streamlit as st
import pandas as pd
from openpyxl import Workbook, load_workbook
from pathlib import Path
import tempfile
import os
import io

# ============================
# === CONSTANT MAPPINGS ======
# ============================
# "tc_name" must match the element's UpdateChart name in PPT.
# "sheet" is the Excel worksheet name (we write to "Sheet1").
# "address" can be A1 ranges or named ranges. "transposed" per your original mappings.
MAPPINGS = [
    {"tc_name": "Process_Eff",   "sheet": "Sheet1", "address": "A2:Z12",    "transposed": True},
    {"tc_name": "Process_Cost","sheet": "Sheet1", "address": "A16:Z26",    "transposed": True},
    {"tc_name": "FPA_Eff",       "sheet": "Sheet1", "address": "A30:Z35",   "transposed": True},
    {"tc_name": "FPA_Cost",       "sheet": "Sheet1", "address": "A39:Z44",   "transposed": True},
    {"tc_name": "RTR_Eff",       "sheet": "Sheet1", "address": "A160:Z164",   "transposed": True},
    {"tc_name": "RTR_Cost",       "sheet": "Sheet1", "address": "A168:Z172", "transposed": True},
    {"tc_name": "ITC-NC_Eff",       "sheet": "Sheet1", "address": "A106:Z111",  "transposed": True},
    {"tc_name": "ITC-NC_Cost",       "sheet": "Sheet1", "address": "A115:Z120",  "transposed": True},
    {"tc_name": "ITC-C_Eff",       "sheet": "Sheet1", "address": "A86:Z92",  "transposed": True},
    {"tc_name": "ITC-C_Cost",       "sheet": "Sheet1", "address": "A96:Z102",  "transposed": True},
    {"tc_name": "PTP_Eff",       "sheet": "Sheet1", "address": "A142:Z147",  "transposed": True},
    {"tc_name": "PTP_Cost",       "sheet": "Sheet1", "address": "A151:Z156","transposed": True},
    {"tc_name": "Tax_Eff",       "sheet": "Sheet1", "address": "A176:Z180",  "transposed": True},
    {"tc_name": "Tax_Cost",       "sheet": "Sheet1", "address": "A184:Z188",  "transposed": True},
    {"tc_name": "Treasury_Eff",       "sheet": "Sheet1", "address": "A192:Z198",  "transposed": True},
    {"tc_name": "Treasury_Cost",       "sheet": "Sheet1", "address": "A202:Z208",  "transposed": True},
    {"tc_name": "Payroll_Eff",       "sheet": "Sheet1", "address": "A124:Z129",  "transposed": True},
    {"tc_name": "Payroll_Cost",       "sheet": "Sheet1", "address": "A133:Z138","transposed": True},
    {"tc_name": "IR_Eff",       "sheet": "Sheet1", "address": "A64:Z71",  "transposed": True},
    {"tc_name": "IR_Cost",       "sheet": "Sheet1", "address": "A75:Z82",  "transposed": True},
    {"tc_name": "Audit_Eff",       "sheet": "Sheet1", "address": "A48:Z52",  "transposed": True},
    {"tc_name": "Audit_Cost",       "sheet": "Sheet1", "address": "A56:Z60",  "transposed": True},
]

# ============================
# === HELPERS (DATA) =========
# ============================

def adjusted_weighted_avg(group: pd.DataFrame, score_col: str, weight_col: str):
    q_group = group.groupby('Question Number')
    values = []
    for _, q_rows in q_group:
        avg_score = q_rows[score_col].mean()
        weight = q_rows[weight_col].iloc[0]
        if pd.notna(avg_score) and pd.notna(weight):
            values.append((avg_score, weight))
    if not values:
        return None
    total_weight = sum(w for _, w in values)
    if total_weight == 0:
        return None
    weighted_sum = sum(score * weight for score, weight in values)
    return round(weighted_sum / total_weight, 4)


def process_metric(df_in: pd.DataFrame, metric_type: str) -> pd.DataFrame:
    if metric_type == "Effectiveness":
        client_col    = next((c for c in df_in.columns if 'Overall' in c and 'Process' in c and 'Effectiveness' in c), None)
        benchmark_col = next((c for c in df_in.columns if c.strip() == 'Median_Process score_Eff'), None)
        bu_suffix     = " - Process - Eff"
        filter_key    = "effectiveness"
    else:
        client_col    = next((c for c in df_in.columns if 'Overall' in c and 'Process' in c and 'Cost' in c), None)
        benchmark_col = next((c for c in df_in.columns if c.strip() == 'Median_Process score_Cost'), None)
        bu_suffix     = " - Process - Cost"
        filter_key    = "cost"

    if not client_col or not benchmark_col:
        raise KeyError(f"Missing columns for {metric_type}")

    filtered_df = df_in[df_in['Dimension'].astype(str).str.lower().str.contains(filter_key)].copy()
    filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()]

    bu_cols = [
        c for c in filtered_df.columns
        if (bu_suffix in c) and ('SubProcess' not in c) and (c not in (client_col, benchmark_col)) and (not c.startswith('Overall - '))
    ]

    cols_to_use = ['Process', client_col, benchmark_col] + bu_cols
    score_df = filtered_df[cols_to_use].copy().groupby('Process', as_index=False).mean(numeric_only=True)

    bu_renames = {c: c.replace(bu_suffix, "").strip() for c in bu_cols}
    score_df.rename(columns={client_col: 'Client', benchmark_col: 'Benchmark', **bu_renames}, inplace=True)
    return score_df[['Process', 'Client', 'Benchmark'] + list(bu_renames.values())]


def build_master_and_analyst(input_xlsx: Path, master_template_xlsx: Path, work_dir: Path):
    """Returns paths: master_out, analyst_out and a plaintext log."""
    logs = []
    logs.append("➡️ Step 1/2: Building Master & Analyst from Tableau input…")

    df = pd.read_excel(input_xlsx, sheet_name="Sheet1")
    df.columns = df.columns.str.strip()

    required_cols = [
        'Process', 'Sub process', 'Business Unit',
        'Actual selection', 'Effectiveness Weightage', 'Cost Weightage', 'Question Number'
    ]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column in input: {col}")

    # Trim
    df['Process'] = df['Process'].astype(str).str.strip()
    df['Sub process'] = df['Sub process'].astype(str).str.strip()

    # BU list
    bu_series = df['Business Unit'].astype(str).str.strip()
    invalid_bu_tokens = {'', 'blank', 'null', 'na', 'n/a'}
    bu_list = sorted(
        bu_series[
            bu_series.str.lower().isin(invalid_bu_tokens) == False
        ].replace(['nan', 'NaN', 'None'], pd.NA).dropna().unique()
    )

    # per-BU
    for bu in bu_list:
        bu_df = df[df['Business Unit'].astype(str).str.strip().str.lower() == bu.lower()]
        proc_eff = bu_df.groupby('Process').apply(lambda g: adjusted_weighted_avg(g, 'Actual selection', 'Effectiveness Weightage')).to_dict()
        proc_cost = bu_df.groupby('Process').apply(lambda g: adjusted_weighted_avg(g, 'Actual selection', 'Cost Weightage')).to_dict()
        sub_eff = bu_df.groupby(['Process', 'Sub process']).apply(lambda g: adjusted_weighted_avg(g, 'Actual selection', 'Effectiveness Weightage')).to_dict()
        sub_cost = bu_df.groupby(['Process', 'Sub process']).apply(lambda g: adjusted_weighted_avg(g, 'Actual selection', 'Cost Weightage')).to_dict()

        df[f"{bu} - Process - Eff"]  = df['Process'].map(proc_eff)
        df[f"{bu} - Process - Cost"] = df['Process'].map(proc_cost)
        df[f"{bu} - SubProcess - Eff"]  = df.set_index(['Process', 'Sub process']).index.map(sub_eff)
        df[f"{bu} - SubProcess - Cost"] = df.set_index(['Process', 'Sub process']).index.map(sub_cost)

    # overall
    overall_df = df.copy()
    overall_proc_eff = overall_df.groupby('Process').apply(lambda g: adjusted_weighted_avg(g, 'Actual selection', 'Effectiveness Weightage')).to_dict()
    overall_proc_cost = overall_df.groupby('Process').apply(lambda g: adjusted_weighted_avg(g, 'Actual selection', 'Cost Weightage')).to_dict()
    overall_sub_eff  = overall_df.groupby(['Process', 'Sub process']).apply(lambda g: adjusted_weighted_avg(g, 'Actual selection', 'Effectiveness Weightage')).to_dict()
    overall_sub_cost = overall_df.groupby(['Process', 'Sub process']).apply(lambda g: adjusted_weighted_avg(g, 'Actual selection', 'Cost Weightage')).to_dict()

    df["Overall - Process - Effectiveness"]   = df['Process'].map(overall_proc_eff)
    df["Overall - Process - Cost"]            = df['Process'].map(overall_proc_cost)
    df["Overall - SubProcess - Effectiveness"] = df.set_index(['Process', 'Sub process']).index.map(overall_sub_eff)
    df["Overall - SubProcess - Cost"]          = df.set_index(['Process', 'Sub process']).index.map(overall_sub_cost)

    # Validate Name_Mapping exists and all Changed Name values are present in input
    mapping_df = pd.read_excel(master_template_xlsx, sheet_name="Name_Mapping", usecols="B:C", header=1)
    mapping_df.columns = mapping_df.columns.str.strip()
    mapping_df = mapping_df.dropna(subset=["Changed Name"])  # expects a column literally called "Changed Name"

    used_names = set(df['Process'].dropna().astype(str).str.strip()).union(
                 set(df['Sub process'].dropna().astype(str).str.strip()))
    missing_changed_names = [
        name for name in mapping_df["Changed Name"].astype(str).str.strip()
        if name not in used_names
    ]
    if missing_changed_names:
        raise ValueError("These 'Changed Name' values were NOT found in the Alteryx input file: " + str(missing_changed_names))

    # Clean out literal strings
    df['Process'].replace(['nan', 'NaN', 'None'], pd.NA, inplace=True)
    df['Sub process'].replace(['nan', 'NaN', 'None'], pd.NA, inplace=True)
    df = df[df['Process'].notna() & df['Sub process'].notna()]

    # Subprocess configs
    sub_eff_col   = 'Overall - SubProcess - Effectiveness'
    sub_eff_bench = 'Median_subProcess score_Eff'
    sub_cost_col  = 'Overall - SubProcess - Cost'
    sub_cost_bench= 'Median_subProcess score_Cost'

    sub_eff_bu_cols = [c for c in df.columns if (' - SubProcess - Eff' in c) and (c not in (sub_eff_col, sub_eff_bench)) and (not c.startswith('Overall - '))]
    sub_cost_bu_cols = [c for c in df.columns if (' - SubProcess - Cost' in c) and (c not in (sub_cost_col, sub_cost_bench)) and (not c.startswith('Overall - '))]

    sub_eff_bu_renames  = {c: c.replace(" - SubProcess - Eff", "").strip()  for c in sub_eff_bu_cols}
    sub_cost_bu_renames = {c: c.replace(" - SubProcess - Cost", "").strip() for c in sub_cost_bu_cols}

    # Process-level
    eff_df  = process_metric(df, "Effectiveness")
    cost_df = process_metric(df, "Cost")

    # Subprocess-level aggregates
    sub_eff_df = df.groupby(['Process', 'Sub process'], as_index=False).agg(
        {sub_eff_col: 'mean', sub_eff_bench: 'mean', **{col: 'mean' for col in sub_eff_bu_cols}}
    )
    sub_cost_df = df.groupby(['Process', 'Sub process'], as_index=False).agg(
        {sub_cost_col: 'mean', sub_cost_bench: 'mean', **{col: 'mean' for col in sub_cost_bu_cols}}
    )

    # Prepare outputs
    master_out = work_dir / "MasterExcel2.xlsx"  # same name as original script
    analyst_out = work_dir / "MasterExcel_Analyst.xlsx"

    # Open/clear Sheet1 (use uploaded master as template to preserve Name_Mapping sheet)
    try:
        wb = load_workbook(master_template_xlsx)
        if "Sheet1" in wb.sheetnames:
            ws = wb["Sheet1"]
            ws.delete_rows(1, ws.max_row)
        else:
            ws = wb.create_sheet("Sheet1")
    except FileNotFoundError:
        wb = Workbook()
        ws = wb.active
        ws.title = "Sheet1"

    def write_header(ws, row_ptr, text):
        ws.cell(row=row_ptr, column=1).value = f"---- {text} ----"
        return row_ptr + 1

    # Write Process Effectiveness
    row_ptr = write_header(ws, 1, "Process Effectiveness Scores")
    for col_index, col_name in enumerate(eff_df.columns, start=1):
        ws.cell(row=row_ptr, column=col_index).value = col_name
    row_ptr += 1
    for row in eff_df.itertuples(index=False):
        for col_index, value in enumerate(row, start=1):
            ws.cell(row=row_ptr, column=col_index).value = round(value, 4) if isinstance(value, (float, int)) else value
        row_ptr += 1
    row_ptr += 2

    # Write Process Cost
    row_ptr = write_header(ws, row_ptr, "Process Cost Scores")
    for col_index, col_name in enumerate(cost_df.columns, start=1):
        ws.cell(row=row_ptr, column=col_index).value = col_name
    row_ptr += 1
    for row in cost_df.itertuples(index=False):
        for col_index, value in enumerate(row, start=1):
            ws.cell(row=row_ptr, column=col_index).value = round(value, 4) if isinstance(value, (float, int)) else value
        row_ptr += 1
    row_ptr += 2

    # Write SubProcess Effectiveness/Cost per Process
    for process_name in df['Process'].dropna().unique():
        sub_eff_process  = sub_eff_df[sub_eff_df['Process'] == process_name]
        sub_cost_process = sub_cost_df[sub_cost_df['Process'] == process_name]

        if not sub_eff_process.empty:
            row_ptr = write_header(ws, row_ptr, f"SubProcess Effectiveness for: {process_name}")
            final_eff_cols = ['Sub process', 'Client', 'Benchmark'] + list(sub_eff_bu_renames.values())
            for col_index, col_name in enumerate(final_eff_cols, start=1):
                ws.cell(row=row_ptr, column=col_index).value = col_name
            row_ptr += 1
            for _, row in sub_eff_process.iterrows():
                ws.cell(row=row_ptr, column=1).value = row['Sub process']
                ws.cell(row=row_ptr, column=2).value = round(row[sub_eff_col], 4) if pd.notna(row[sub_eff_col]) else None
                ws.cell(row=row_ptr, column=3).value = round(row[sub_eff_bench], 4) if pd.notna(row[sub_eff_bench]) else None
                for i, col in enumerate(sub_eff_bu_cols, start=4):
                    val = row[col]
                    if pd.notna(val):
                        ws.cell(row=row_ptr, column=i).value = round(val, 4)
                row_ptr += 1
            row_ptr += 2

        if not sub_cost_process.empty:
            row_ptr = write_header(ws, row_ptr, f"SubProcess Cost for: {process_name}")
            final_cost_cols = ['Sub process', 'Client', 'Benchmark'] + list(sub_cost_bu_renames.values())
            for col_index, col_name in enumerate(final_cost_cols, start=1):
                ws.cell(row=row_ptr, column=col_index).value = col_name
            row_ptr += 1
            for _, row in sub_cost_process.iterrows():
                ws.cell(row=row_ptr, column=1).value = row['Sub process']
                ws.cell(row=row_ptr, column=2).value = round(row[sub_cost_col], 4) if pd.notna(row[sub_cost_col]) else None
                ws.cell(row=row_ptr, column=3).value = round(row[sub_cost_bench], 4) if pd.notna(row[sub_cost_bench]) else None
                for i, col in enumerate(sub_cost_bu_cols, start=4):
                    val = row[col]
                    if pd.notna(val):
                        ws.cell(row=row_ptr, column=i).value = round(val, 4)
                row_ptr += 1
            row_ptr += 2

    # Save the master file to work_dir
    wb.save(master_out)

    # Create Analyst copy as values only
    master_wb = load_workbook(master_out, data_only=True)
    master_ws = master_wb.active

    analyst_wb = Workbook()
    analyst_ws = analyst_wb.active
    analyst_ws.title = master_ws.title

    for r_idx, row in enumerate(master_ws.iter_rows(values_only=True), start=1):
        for c_idx, value in enumerate(row, start=1):
            analyst_ws.cell(row=r_idx, column=c_idx, value=value)

    analyst_wb.save(analyst_out)

    logs.append("✅ Master and Analyst files generated successfully. Analyst is values-only (no think-cell links).")

    return master_out, analyst_out, "\n".join(logs)


# ============================
# === HELPERS (THINK-CELL) ===
# ============================

def update_thinkcell_ppt(master_xlsx: Path, ppt_template: Path, output_ppt: Path):
    """Automate think-cell UpdateChart via Excel COM Add-in."""
    if os.name != 'nt':
        raise SystemExit("Step (2) requires Windows.")

    try:
        import pythoncom
        import win32com.client as win32
    except Exception as e:
        raise SystemExit(
            "Requires Windows with Office + think-cell + pywin32.\nInstall: pip install pywin32\n\nDetails: " + str(e)
        )

    if not master_xlsx.exists():
        raise FileNotFoundError(f"Excel not found: {master_xlsx}")
    if not ppt_template.exists():
        raise FileNotFoundError(f"PPT not found: {ppt_template}")

    xl = wb_xl = pp = pres = None
    results = []
    updated = 0

    try:
        pythoncom.CoInitialize()

        xl = win32.DispatchEx("Excel.Application")
        xl.Visible = False
        xl.DisplayAlerts = False

        pp = win32.DispatchEx("PowerPoint.Application")
        pp.Visible = True
        try:
            pp.WindowState = 2  # minimized
        except Exception:
            pass

        wb_xl = xl.Workbooks.Open(str(master_xlsx.resolve()))
        pres = pp.Presentations.Open(FileName=str(ppt_template.resolve()), WithWindow=False)

        try:
            tc = xl.COMAddIns("thinkcell.addin").Object
        except Exception:
            tc = None
        if tc is None:
            raise RuntimeError("Could not access think-cell via Excel COM Add-Ins. Enable it in Excel > Options > Add-ins > COM Add-ins.")

        for m in MAPPINGS:
            name = m["tc_name"]; sheet = m["sheet"]; addr = m["address"]; trans = bool(m["transposed"])
            try:
                ws = wb_xl.Worksheets(sheet)
            except Exception as e:
                results.append((name, f"❌ Worksheet '{sheet}' not found: {e}"))
                continue
            try:
                rng = ws.Range(addr)
            except Exception:
                try:
                    rng = wb_xl.Range(addr)
                except Exception as e2:
                    results.append((name, f"❌ Range '{addr}' not found on '{sheet}' (or as named range): {e2}"))
                    continue

            try:
                tc.UpdateChart(pres, name, rng, trans)
                results.append((name, f"✅ Updated from {sheet}!{addr}, transposed={trans}"))
                updated += 1
            except Exception as e:
                results.append((name, f"❌ UpdateChart failed: {e}"))

        pres.SaveAs(str(output_ppt.resolve()))

        return updated, len(MAPPINGS), results, output_ppt

    finally:
        try:
            if pres is not None:
                pres.Close()
        except Exception:
            pass
        try:
            if wb_xl is not None:
                wb_xl.Close(SaveChanges=False)
        except Exception:
            pass
        try:
            if pp is not None:
                pp.Quit()
        except Exception:
            pass
        try:
            if xl is not None:
                xl.Quit()
        except Exception:
            pass
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except Exception:
            pass


# ============================
# === STREAMLIT UI ===========
# ============================

st.set_page_config(page_title="Tableau → Master/Analyst → think-cell", layout="centered")
st.title("End‑to‑end: Build Master/Analyst & Update think‑cell PPT")

st.markdown(
    """
**Inputs** (all required):
1. **Master Excel (template)** – must contain a `Name_Mapping` sheet with columns **B:C** and header on **row 2**.
2. **Input for Tableau (xlsx)** – raw Alteryx/Tableau export (expects a `Sheet1`).
3. **PPT template** – a `.pptx/.pptm` file with think‑cell elements named to match **tc_name** in the mappings.

The logic for building the Master/Analyst and updating think‑cell is unchanged from your script.
    """
)

with st.expander("View hard‑coded think‑cell mappings"):
    st.json(MAPPINGS)

col1, col2 = st.columns(2)
with col1:
    master_up = st.file_uploader("Upload **Master Excel (template)**", type=["xlsx", "xlsm"], accept_multiple_files=False)
    input_up  = st.file_uploader("Upload **Input for Tableau**", type=["xlsx"], accept_multiple_files=False)
with col2:
    ppt_up    = st.file_uploader("Upload **PPT template**", type=["pptx", "pptm"], accept_multiple_files=False)
    run_tc    = st.checkbox("Run Step (2) – update think‑cell charts", value=True)

out_ppt_name = st.text_input("Output PPT filename", value="Deck_UPDATED.pptx")

run_btn = st.button("Run pipeline", type="primary", use_container_width=True)

if run_btn:
    if not (master_up and input_up and ppt_up):
        st.error("Please upload all three files.")
        st.stop()

    with tempfile.TemporaryDirectory() as tdir:
        tdir = Path(tdir)

        # Persist uploads
        master_path = tdir / (master_up.name or "MasterTemplate.xlsx")
        input_path  = tdir / (input_up.name or "InputForTableau.xlsx")
        ppt_path    = tdir / (ppt_up.name or "Template.pptx")

        master_path.write_bytes(master_up.read())
        input_path.write_bytes(input_up.read())
        ppt_path.write_bytes(ppt_up.read())

        # Step 1: Build Master & Analyst
        with st.status("Building Master & Analyst from Tableau input…", expanded=True) as status:
            try:
                master_out, analyst_out, step1_log = build_master_and_analyst(input_path, master_path, tdir)
                status.update(label="Master & Analyst created", state="complete")
                st.code(step1_log)
            except Exception as e:
                status.update(label="Failed building Master/Analyst", state="error")
                st.exception(e)
                st.stop()

        # Download buttons for Excel outputs
        with open(master_out, "rb") as f:
            st.download_button("Download Master Excel", f, file_name=master_out.name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with open(analyst_out, "rb") as f:
            st.download_button("Download Analyst Excel (values‑only)", f, file_name=analyst_out.name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Step 2: Update think‑cell
        if run_tc:
            with st.status("Updating think‑cell charts in PowerPoint…", expanded=True) as status:
                try:
                    updated, total, results, out_ppt_path = update_thinkcell_ppt(master_out, ppt_path, tdir / out_ppt_name)
                    status.update(label=f"think‑cell updated: {updated}/{total}", state="complete")
                    for name, msg in results:
                        st.write(f"- **{name}**: {msg}")

                    # Download button for PPT
                    with open(out_ppt_path, "rb") as f:
                        st.download_button("Download updated PPT", f, file_name=Path(out_ppt_name).name, mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")

                    st.info("`UpdateChart` replaces each chart's datasheet and breaks any live Excel link for that element.")
                except SystemExit as e:
                    status.update(label="Environment requirement", state="error")
                    st.error(str(e))
                except Exception as e:
                    status.update(label="Failed updating think‑cell", state="error")
                    st.exception(e)
        else:
            st.warning("Step (2) skipped. Enable the checkbox to update think‑cell charts.")

st.caption("Requires Windows, Microsoft Office (Excel + PowerPoint), think‑cell installed & enabled, and Python packages: pandas, openpyxl, pywin32.")
