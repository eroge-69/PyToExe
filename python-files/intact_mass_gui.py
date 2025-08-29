import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os

# ===================== 数据处理辅助函数 =====================

def process_modification(mod_series):
    unique_modifications = set()
    for mod_str in mod_series.dropna():
        individual_mods = mod_str.split(',')
        for mod in individual_mods:
            processed_mod = re.sub(r'^\d+x\s*', '', mod.strip())
            unique_modifications.add(processed_mod)
    return None if not unique_modifications else "/".join(sorted(unique_modifications))

def get_range(series):
    if series.empty or series.isnull().all():
        return None
    return f"{series.min():.2f} - {series.max():.2f}"

def process_intact_mass_data(df_input):
    df_input['Sequence Name'] = df_input['Sequence Name'].astype(object)
    df_filtered = df_input[df_input['Score'] >= 20].copy()
    df_known = df_filtered[df_filtered['Sequence Name'].notnull()].copy()
    df_unknown = df_filtered[df_filtered['Sequence Name'].isnull()].copy()

    # --- 处理高丰度未识别序列 ---
    df_unidentified_high = df_unknown[df_unknown['Fractional Abundance'] >= 0.5].copy()
    df_unidentified_high = df_unidentified_high.sort_values(by=['Fractional Abundance', 'Average Mass'], ascending=[False, True]).reset_index(drop=True)
    df_unidentified_high_out = pd.DataFrame()
    if not df_unidentified_high.empty:
        df_unidentified_high_out = pd.DataFrame({
            'Sequence Name': [f'Unidentified {i+1}' for i in range(len(df_unidentified_high))],
            'Fraction Abundance': df_unidentified_high['Fractional Abundance'],
            'Modification': None,
            'Theoretical Mass (Da)': None,
            'Average Mass': df_unidentified_high['Average Mass'],
            'Apex RT': df_unidentified_high['Apex RT']
        })

    # --- 处理低丰度未识别序列 ---
    df_unidentified_low = df_unknown[df_unknown['Fractional Abundance'] < 0.5].copy()
    df_unidentified_total = pd.DataFrame()
    if not df_unidentified_low.empty:
        df_unidentified_total = pd.DataFrame([{
            'Sequence Name': 'Unidentified (total)',
            'Fraction Abundance': df_unidentified_low['Fractional Abundance'].sum(),
            'Modification': None,
            'Theoretical Mass (Da)': None,
            'Average Mass': get_range(df_unidentified_low['Average Mass']),
            'Apex RT': get_range(df_unidentified_low['Apex RT'])
        }])

    # --- 处理已知序列 ---
    grouped = df_known.groupby('Sequence Name')
    known_records = []
    for name, group in grouped:
        fa_sum = group['Fractional Abundance'].sum()
        merged_mod = process_modification(group['Modification'])
        top_abundance_row = group.loc[group['Fractional Abundance'].idxmax()]
        theoretical_mass = top_abundance_row['Theoretical Mass (Da)']
        avg_mass_range = get_range(group['Average Mass'])
        rt_range = get_range(group['Apex RT'])

        known_records.append({
            'Sequence Name': name,
            'Fraction Abundance': fa_sum,
            'Modification': merged_mod,
            'Theoretical Mass (Da)': theoretical_mass,
            'Average Mass': avg_mass_range,
            'Apex RT': rt_range
        })

    df_known_out = pd.DataFrame(known_records)

    # --- 合并结果 ---
    for df in [df_known_out, df_unidentified_total, df_unidentified_high_out]:
        if 'Theoretical Mass (Da)' in df.columns:
            df['Theoretical Mass (Da)'] = df['Theoretical Mass (Da)'].astype(object)

    final_df = pd.concat([df_known_out, df_unidentified_total, df_unidentified_high_out], ignore_index=True)
    final_df = final_df[['Sequence Name', 'Fraction Abundance', 'Theoretical Mass (Da)', 'Average Mass', 'Apex RT', 'Modification']]
    return final_df

# ===================== GUI 主程序 =====================

class MassAnalyzerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Intact Mass Excel Processor")

        # 文件路径存储
        self.file_paths = []
        self.output_dir = ""

        # 按钮区域
        tk.Button(master, text="选择 Excel 文件", command=self.select_files).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        tk.Button(master, text="选择输出文件夹", command=self.select_output_folder).grid(row=0, column=1, padx=10, pady=5, sticky='w')
        tk.Button(master, text="开始处理", command=self.process_files).grid(row=0, column=2, padx=10, pady=5, sticky='w')

        # 日志窗口
        self.log_box = scrolledtext.ScrolledText(master, height=20, width=100, state='disabled')
        self.log_box.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

    def log(self, message):
        self.log_box.configure(state='normal')
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state='disabled')
        print(message)

    def select_files(self):
        paths = filedialog.askopenfilenames(
            title="选择 Excel 文件",
            filetypes=[("Excel 文件", "*.xlsx *.xls")]
        )
        if paths:
            self.file_paths = paths
            self.log(f"已选择 {len(paths)} 个文件。")

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_dir = folder
            self.log(f"输出目录设置为: {folder}")

    def process_files(self):
        if not self.file_paths:
            messagebox.showwarning("缺少文件", "请先选择要处理的 Excel 文件。")
            return
        if not self.output_dir:
            messagebox.showwarning("缺少目录", "请先选择输出文件夹。")
            return

        for file_path in self.file_paths:
            try:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                self.log(f"\n开始处理: {base_name}")
                df_raw = pd.read_excel(file_path)
                df_result = process_intact_mass_data(df_raw)
                out_path = os.path.join(self.output_dir, f"{base_name}_summary.xlsx")
                df_result.to_excel(out_path, index=False)
                self.log(f"完成: {out_path}")
            except Exception as e:
                self.log(f"❌ 处理失败 {file_path}: {e}")

# ===================== 程序入口 =====================

if __name__ == "__main__":
    root = tk.Tk()
    app = MassAnalyzerApp(root)
    root.mainloop()
