import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import geopandas as gpd
from shapely import wkt
import re

REQUIRED_COLUMNS = ["Nama Usaha", "Geometry", "Nama Pemilik", "SLS", "Sektor"]

class CSVEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor CSV/Excel UMKM")
        self.df = pd.DataFrame(columns=REQUIRED_COLUMNS)

        tree_frame = tk.Frame(root)
        tree_frame.pack(padx=10, pady=10, fill='both', expand=True)

        # Scrollbar
        vsb = tk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        DISPLAY_COLUMNS = ["No"] + REQUIRED_COLUMNS
        self.tree = ttk.Treeview(tree_frame, columns=DISPLAY_COLUMNS, show='headings', height=15, yscrollcommand=vsb.set)
        vsb.config(command=self.tree.yview)

        for col in DISPLAY_COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=50 if col == "No" else 240, anchor="w")

        self.tree.pack(fill='both', expand=True)

        # Tombol fungsi
        button_frame = tk.Frame(root)
        button_frame.pack()

        # Filter dan pencarian
        filter_frame = tk.Frame(root)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Cari Nama:").grid(row=0, column=0)
        self.search_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.search_var, width=30).grid(row=0, column=1)

        tk.Label(filter_frame, text="RW (SLS):").grid(row=0, column=2)
        self.rw_filter = ttk.Combobox(filter_frame, state="readonly")
        self.rw_filter.grid(row=0, column=3)

        tk.Label(filter_frame, text="Sektor:").grid(row=0, column=4)
        self.sektor_filter = ttk.Combobox(filter_frame, state="readonly", width=100)
        self.sektor_filter.grid(row=0, column=5)

        tk.Button(filter_frame, text="Terapkan Filter", command=self.apply_filters).grid(row=0, column=6, padx=5)
        tk.Button(filter_frame, text="Reset Filter", command=self.reset_filters).grid(row=0, column=7, padx=5)

        tk.Button(button_frame, text="Buka File", command=self.load_file).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Simpan File", command=self.save_file).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Hapus Baris", command=self.delete_row).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Tambah Baris Baru", command=self.add_row_window).grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Append File Lain", command=self.append_file).grid(row=0, column=4, padx=5)
        tk.Button(button_frame, text="Export GeoJSON", command=self.export_geojson).grid(row=0, column=5, padx=5)

    def apply_filters(self):
        keyword = self.search_var.get().strip().lower()
        rw = self.rw_filter.get()
        sektor = self.sektor_filter.get()

        df_filtered = self.df.copy()

        # Filter berdasarkan kata kunci di Nama Usaha atau Nama Pemilik
        if keyword:
            df_filtered = df_filtered[
                df_filtered["Nama Usaha"].str.lower().str.contains(keyword) |
                df_filtered["Nama Pemilik"].str.lower().str.contains(keyword)
            ]

            # Filter berdasarkan SLS
        if rw and rw != "Semua":
            df_filtered = df_filtered[df_filtered["SLS"] == rw]

            # Filter berdasarkan Sektor
        if sektor and sektor != "Semua":
            df_filtered = df_filtered[df_filtered["Sektor"] == sektor]

        self.refresh_treeview(df_filtered)

    def reset_filters(self):
        self.search_var.set("")
        self.rw_filter.set("Semua")
        self.sektor_filter.set("Semua")
        self.refresh_treeview()

    def refresh_treeview(self, df=None):
        self.tree.delete(*self.tree.get_children())
        if df is None:
            df = self.df

        for idx, (_, row) in enumerate(df.iterrows(), start=1):
            self.tree.insert("", "end", values=[idx] + list(row))

        # Update opsi filter jika diminta refresh semua
        if df is self.df:
            self.update_filter_options()

    def update_filter_options(self):
        sls_values = self.df["SLS"].dropna().unique().tolist()

        def extract_rw_rt(sls):
            sls = str(sls)
            # Cari RW dan RT menggunakan regex (misal: "RT 002 RW 001")
            rt_match = re.search(r'RT[-\s]?(\d+)', sls, re.IGNORECASE)
            rw_match = re.search(r'RW[-\s]?(\d+)', sls, re.IGNORECASE)

            rt = int(rt_match.group(1)) if rt_match else float('inf')
            rw = int(rw_match.group(1)) if rw_match else float('inf')

            return (rw, rt)

        # Urutkan berdasarkan RW lalu RT
        sls_values_sorted = sorted(sls_values, key=extract_rw_rt)

        sektor_values = sorted(self.df["Sektor"].dropna().unique().tolist())

        self.rw_filter["values"] = ["Semua"] + sls_values_sorted
        self.sektor_filter["values"] = ["Semua"] + sektor_values
        self.rw_filter.set("Semua")
        self.sektor_filter.set("Semua")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV or Excel", "*.csv *.xlsx")])
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

                if not all(col in df.columns for col in REQUIRED_COLUMNS):
                    messagebox.showerror("Error", f"File harus memiliki kolom: {REQUIRED_COLUMNS}")
                    return

                self.df = df[REQUIRED_COLUMNS].copy()
                self.refresh_treeview()
                self.update_filter_options()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")])
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df.to_csv(file_path, index=False)
                else:
                    self.df.to_excel(file_path, index=False)
                messagebox.showinfo("Sukses", "File berhasil disimpan.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_row(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Baris", "Silakan pilih baris yang akan dihapus.")
            return
        indexes = [self.tree.index(row) for row in selected]
        self.df.drop(self.df.index[indexes], inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        self.refresh_treeview()

    def add_row_window(self):
        win = tk.Toplevel(self.root)
        win.title("Tambah Baris Baru")
        entries = {}

        for i, col in enumerate(REQUIRED_COLUMNS):
            tk.Label(win, text=col).grid(row=i, column=0, sticky='w')
            entry = tk.Entry(win, width=40)
            entry.grid(row=i, column=1)
            entries[col] = entry

        def add():
            new_row = {col: entries[col].get() for col in REQUIRED_COLUMNS}
            if any(v == "" for v in new_row.values()):
                messagebox.showwarning("Input Tidak Lengkap", "Semua kolom harus diisi.")
                return
            self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
            self.refresh_treeview()
            win.destroy()

        tk.Button(win, text="Tambah", command=add).grid(row=len(REQUIRED_COLUMNS), columnspan=2, pady=10)

    def append_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")])
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    df_new = pd.read_csv(file_path)
                else:
                    df_new = pd.read_excel(file_path)

                if not all(col in df_new.columns for col in REQUIRED_COLUMNS):
                    messagebox.showerror("Error", f"File harus memiliki kolom: {REQUIRED_COLUMNS}")
                    return

                self.df = pd.concat([self.df, df_new[REQUIRED_COLUMNS]], ignore_index=True)
                self.refresh_treeview()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_geojson(self):
        self.df['Geometry'] = self.df['Geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(self.df).set_geometry('Geometry', crs="EPSG:4326")
        try:
            with open('umkmpoint.geojson', 'w') as f:
                f.write("var point = ")
                f.write(gdf.to_json())
            messagebox.showinfo("Sukses", "GeoJSON berhasil disimpan sebagai umkmpoint.geojson.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def parse_point_wkt(self, wkt):
        # Contoh format: POINT(106.827153 -6.175110)
        match = re.match(r'POINT\(\s*([\d\.\-]+)\s+([\d\.\-]+)\s*\)', wkt.strip())
        if match:
            lon, lat = float(match.group(1)), float(match.group(2))
            return [lon, lat]
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVEditor(root)
    root.mainloop()
