import wx
import pandas as pd
import string
import os
from datetime import datetime

# Helper to convert Excel column letter to zero‐based index
def col_to_idx(col):
    col = col.upper().strip()
    idx = 0
    for c in col:
        if c in string.ascii_uppercase:
            idx = idx * 26 + (ord(c) - ord('A') + 1)
    return idx - 1

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Rat Performance Analyzer", size=(700,500))
        panel = wx.Panel(self)

        # --- File picker ---
        hfile = wx.BoxSizer(wx.HORIZONTAL)
        hfile.Add(wx.StaticText(panel, label="Files:"), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 8)
        self.file_txt = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hfile.Add(self.file_txt, 1, wx.EXPAND|wx.RIGHT, 8)
        pick_btn = wx.Button(panel, label="Browse…")
        pick_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        hfile.Add(pick_btn, 0)
        
        # --- Column inputs ---
        grid = wx.FlexGridSizer(2,4,10,10)
        # Pre-define column-letter text controls
        self.c_animal = wx.TextCtrl(panel, value="J")
        self.c_correct = wx.TextCtrl(panel, value="AP")
        self.c_trial = wx.TextCtrl(panel, value="AQ")
        self.c_dist = wx.TextCtrl(panel, value="AR")

        grid.AddMany([
            (wx.StaticText(panel, label="Animal ID col:"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.c_animal, 1, wx.EXPAND),
            (wx.StaticText(panel, label="NumCorrect col:"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.c_correct, 1, wx.EXPAND),
            (wx.StaticText(panel, label="Trial# col:"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.c_trial, 1, wx.EXPAND),
            (wx.StaticText(panel, label="DistanceGP col:"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.c_dist, 1, wx.EXPAND),
        ])

        # --- Range manager ---
        rng_box = wx.StaticBox(panel, label="Distance Ranges")
        rng_sizer = wx.StaticBoxSizer(rng_box, wx.VERTICAL)
        inner = wx.BoxSizer(wx.HORIZONTAL)
        self.range_min = wx.TextCtrl(panel, value="1", size=(50,-1))
        self.range_max = wx.TextCtrl(panel, value="4", size=(50,-1))
        add_btn = wx.Button(panel, label="Add")
        add_btn.Bind(wx.EVT_BUTTON, self.on_add_range)
        inner.Add(wx.StaticText(panel,label="Min:"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,5)
        inner.Add(self.range_min,0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,10)
        inner.Add(wx.StaticText(panel,label="Max:"),0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,5)
        inner.Add(self.range_max,0,wx.ALIGN_CENTER_VERTICAL|wx.RIGHT,10)
        inner.Add(add_btn,0)
        rng_sizer.Add(inner,0,wx.ALL,8)

        self.range_list = wx.ListBox(panel)
        for mn,mx in [(1,4),(5,8),(9,13)]:
            self.range_list.Append(f"{mn}-{mx}")
        rng_sizer.Add(self.range_list,1,wx.EXPAND|wx.ALL,8)
        del_btn = wx.Button(panel, label="Delete Selected")
        del_btn.Bind(wx.EVT_BUTTON, self.on_del_range)
        rng_sizer.Add(del_btn,0,wx.ALIGN_CENTER|wx.ALL,5)

        # --- Analyze and Save ---
        hrun = wx.BoxSizer(wx.HORIZONTAL)
        run_btn = wx.Button(panel, label="Analyze")
        run_btn.Bind(wx.EVT_BUTTON, self.on_analyze)
        hrun.Add(run_btn,0,wx.RIGHT,10)
        self.save_txt = wx.TextCtrl(panel, style=wx.TE_READONLY)
        hrun.Add(self.save_txt,1,wx.EXPAND|wx.RIGHT,8)
        save_btn = wx.Button(panel, label="Save As…")
        save_btn.Bind(wx.EVT_BUTTON, self.on_save_as)
        hrun.Add(save_btn,0)

        # Checkbox to append to existing Excel file
        self.append_chk = wx.CheckBox(panel, label="Append to existing file")
        hrun.Add(self.append_chk, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)

        # --- Layout ---
        vs = wx.BoxSizer(wx.VERTICAL)
        vs.Add(hfile,0,wx.EXPAND|wx.ALL,10)
        vs.Add(grid,0,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
        vs.Add(rng_sizer,1,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
        vs.Add(hrun,0,wx.EXPAND|wx.ALL,10)
        panel.SetSizer(vs)

        self.files = []
        self.out_path = None

    def on_browse(self, evt):
        dlg = wx.FileDialog(self, "Select data files", wildcard="CSV or Excel (*.csv;*.xlsx)|*.csv;*.xlsx",
                            style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE)
        if dlg.ShowModal()==wx.ID_OK:
            self.files = dlg.GetPaths()
            self.file_txt.SetValue("; ".join(self.files))
        dlg.Destroy()

    def on_add_range(self, evt):
        try:
            mn = float(self.range_min.GetValue())
            mx = float(self.range_max.GetValue())
        except ValueError:
            wx.MessageBox("Ranges must be numeric","Error",wx.ICON_ERROR)
            return
        if mn>mx:
            wx.MessageBox("Min ≤ Max","Error",wx.ICON_ERROR)
            return
        self.range_list.Append(f"{mn:g}-{mx:g}")

    def on_del_range(self, evt):
        sel = self.range_list.GetSelection()
        if sel!=wx.NOT_FOUND:
            self.range_list.Delete(sel)

    def on_save_as(self, evt):
        dlg = wx.FileDialog(self, "Save summary as…", wildcard="Excel (*.xlsx)|*.xlsx|CSV (*.csv)|*.csv",
                            style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal()==wx.ID_OK:
            self.out_path = dlg.GetPath()
            self.save_txt.SetValue(self.out_path)
        dlg.Destroy()

    def on_analyze(self, evt):
        if not self.files:
            wx.MessageBox("Please select at least one file.","Error",wx.ICON_ERROR)
            return
        # parse column indices
        a_idx = col_to_idx(self.c_animal.GetValue())
        c_idx = col_to_idx(self.c_correct.GetValue())
        t_idx = col_to_idx(self.c_trial.GetValue())
        d_idx = col_to_idx(self.c_dist.GetValue())
        # parse ranges
        ranges = []
        for i in range(self.range_list.GetCount()):
            mn,mx = map(float,self.range_list.GetString(i).split('-'))
            ranges.append((mn,mx))
        # aggregate
        records = {}  # animal -> list of dicts {trial, dist, correct, file, row}
        for fp in self.files:
            ext = os.path.splitext(fp)[1].lower()
            if ext=='.csv':
                df = pd.read_csv(fp, header=0, dtype=str)
            else:
                df = pd.read_excel(fp, sheet_name=0, dtype=str)
            for idx,row in df.iterrows():
                aid = row.iat[a_idx]
                trial = row.iat[t_idx]
                if pd.isna(aid) or pd.isna(trial):
                    continue
                key = (aid, trial)
                # first occurrence only
                if aid not in records:
                    records[aid] = {}
                if trial in records[aid]:
                    continue
                try:
                    dist = float(row.iat[d_idx])
                    corr = int(float(row.iat[c_idx]))
                except:
                    continue
                # compute excel‐like row number for diagnostics
                excel_row = idx + 2
                records[aid][trial] = {
                    'dist': dist,
                    'corr': corr,
                    'coord': (f"{self.c_correct.GetValue().upper()}{excel_row}",
                              f"{self.c_dist.GetValue().upper()}{excel_row}")
                }

        # build summary
        out_rows = []
        for aid, trials in records.items():
            row = {'Animal ID': aid}
            for mn,mx in ranges:
                # filter trials by distance
                sel = [v for v in trials.values() if mn <= v['dist'] <= mx]
                count = len(sel)
                total = sum(v['corr'] for v in sel)
                pct = (total/count*100) if count>0 else 0.0
                # diagnostic string
                coords = ";".join(f"[{v['coord'][0]},{v['coord'][1]}]" for v in sel)
                diag = f"{total},{count},{coords}"
                row[f"%C {mn:g}-{mx:g}"] = pct
                row[f"Diag {mn:g}-{mx:g}"] = diag
            out_rows.append(row)

        out_df = pd.DataFrame(out_rows).sort_values("Animal ID")

        if self.out_path:
            ext = os.path.splitext(self.out_path)[1].lower()
            append = hasattr(self, 'append_chk') and self.append_chk.GetValue()
            # Append to existing Excel workbook if requested
            if append and ext == '.xlsx' and os.path.exists(self.out_path):
                try:
                    # Generate timestamp-based sheet name
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    with pd.ExcelWriter(self.out_path, engine='openpyxl', mode='a') as writer:
                        out_df.to_excel(writer, sheet_name=ts, index=False)
                    wx.MessageBox(f"Summary appended as new sheet '{ts}' to:\n{self.out_path}", "Done", wx.ICON_INFORMATION)
                except Exception as e:
                    wx.MessageBox(f"Error appending sheet:\n{e}", "Error", wx.ICON_ERROR)
            else:
                try:
                    if ext == '.csv':
                        out_df.to_csv(self.out_path, index=False)
                    else:
                        out_df.to_excel(self.out_path, index=False)
                    wx.MessageBox(f"Summary saved to:\n{self.out_path}", "Done", wx.ICON_INFORMATION)
                except Exception as e:
                    wx.MessageBox(f"Error saving file:\n{e}", "Error", wx.ICON_ERROR)
        else:
            wx.MessageBox("Please choose a Save As… location first.","Info",wx.ICON_INFORMATION)


if __name__ == "__main__":
    app = wx.App(False)
    frm = MainFrame()
    frm.Show()
    app.MainLoop()