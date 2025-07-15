import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Stok Barang")
        self.root.geometry("1200x600")

        self.dataframe = pd.DataFrame()
        self.selected_item = None
        self.riwayat_data = []
        self.riwayat_data_keluar = []

        self.show_main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_window()

        label = tk.Label(self.root, text="Menu Utama", font=("Arial", 20))
        label.pack(pady=20)

        lihat_button = tk.Button(self.root, text="Lihat Data", width=20, command=self.show_lihat_data)
        lihat_button.pack(pady=10)

        tambah_button = tk.Button(self.root, text="Tambah Data", width=20, command=self.tambah_data)
        tambah_button.pack(pady=10)
        
        keluar_button = tk.Button(self.root, text="Barang Keluar", width=20, command=self.barang_keluar)
        keluar_button.pack(pady=10)


    def load_excel_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if file_path:
            self.dataframe = pd.read_excel(file_path)
            self.dataframe['Stok Awal'] = 100
            self.dataframe['Barang Masuk'] = 0
            self.dataframe['Barang Keluar'] = 0
            self.dataframe['Stok Akhir'] = (
                self.dataframe['Stok Awal'] + self.dataframe['Barang Masuk'] - self.dataframe['Barang Keluar']
            )
            self.dataframe['Status'] = "ADA"
            self.show_lihat_data_table()

    def show_lihat_data(self):
        self.clear_window()

        label = tk.Label(self.root, text="Halaman Lihat Data", font=("Arial", 16))
        label.pack(pady=10)

        if self.dataframe.empty:
            pilih_button = tk.Button(self.root, text="Pilih File Excel", command=self.load_excel_file)
            pilih_button.pack(pady=5)
        else:
            self.show_lihat_data_table()

    def tambah_data(self):
        if self.dataframe.empty:
            messagebox.showwarning("Peringatan", "Silakan muat file data terlebih dahulu.")
            return

        self.clear_window()

        label = tk.Label(self.root, text="Tambah Barang Masuk", font=("Arial", 16))
        label.pack(pady=10)

        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Tanggal:").grid(row=0, column=0, padx=5, pady=5)
        self.tanggal_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(form_frame, textvariable=self.tanggal_var, state='readonly').grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Kode Barang:").grid(row=1, column=0, padx=5, pady=5)
        self.kode_barang_var = tk.StringVar()
        self.kode_barang_combo = ttk.Combobox(form_frame, textvariable=self.kode_barang_var)
        self.kode_barang_combo['values'] = self.dataframe['Kode Barang'].tolist()
        self.kode_barang_combo.grid(row=1, column=1, padx=5, pady=5)
        self.kode_barang_combo.bind("<<ComboboxSelected>>", self.update_nama_barang)

        tk.Label(form_frame, text="Nama Barang:").grid(row=2, column=0, padx=5, pady=5)
        self.nama_barang_var = tk.StringVar()
        self.nama_barang_entry = tk.Entry(form_frame, textvariable=self.nama_barang_var, state='readonly')
        self.nama_barang_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Keterangan:").grid(row=3, column=0, padx=5, pady=5)
        self.keterangan_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.keterangan_var).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Jumlah Masuk:").grid(row=4, column=0, padx=5, pady=5)
        self.jumlah_masuk_var = tk.IntVar(value=0)
        tk.Entry(form_frame, textvariable=self.jumlah_masuk_var).grid(row=4, column=1, padx=5, pady=5)

        simpan_button = tk.Button(self.root, text="Simpan Data", command=self.simpan_data)
        simpan_button.pack(pady=5)

        back_button = tk.Button(self.root, text="Kembali ke Menu", command=self.show_main_menu)
        back_button.pack(pady=5)

        riwayat_label = tk.Label(self.root, text="Riwayat Barang Masuk", font=("Arial", 14))
        riwayat_label.pack(pady=10)

        self.riwayat_tree = ttk.Treeview(self.root, columns=("Tanggal", "Kode Barang", "Nama Barang", "Keterangan", "Jumlah"), show="headings")
        for col in ("Tanggal", "Kode Barang", "Nama Barang", "Keterangan", "Jumlah"):
            self.riwayat_tree.heading(col, text=col)
            self.riwayat_tree.column(col, width=120)
        self.riwayat_tree.pack(pady=10, fill='both', expand=True)

        self.update_riwayat_tree()

    def update_nama_barang(self, event):
        kode = self.kode_barang_var.get()
        row = self.dataframe[self.dataframe['Kode Barang'] == kode]
        if not row.empty:
            nama_barang = row.iloc[0]['Nama Barang']
            self.nama_barang_var.set(nama_barang)

    def simpan_data(self):
        kode = self.kode_barang_var.get()
        jumlah_masuk = self.jumlah_masuk_var.get()

        if kode == "" or jumlah_masuk <= 0:
            messagebox.showerror("Error", "Pastikan kode barang dan jumlah masuk diisi dengan benar.")
            return

        idx = self.dataframe.index[self.dataframe['Kode Barang'] == kode].tolist()[0]
        self.dataframe.at[idx, 'Barang Masuk'] += jumlah_masuk
        self.dataframe.at[idx, 'Stok Akhir'] = (
            self.dataframe.at[idx, 'Stok Awal'] + self.dataframe.at[idx, 'Barang Masuk'] - self.dataframe.at[idx, 'Barang Keluar']
        )

        riwayat_entry = (
            self.tanggal_var.get(),
            kode,
            self.nama_barang_var.get(),
            self.keterangan_var.get(),
            jumlah_masuk
        )
        self.riwayat_data.append(riwayat_entry)
        self.update_riwayat_tree()

        messagebox.showinfo("Sukses", "Data barang masuk berhasil disimpan.")

    def update_riwayat_tree(self):
        if hasattr(self, 'riwayat_tree'):
            for item in self.riwayat_tree.get_children():
                self.riwayat_tree.delete(item)
            for row in self.riwayat_data:
                self.riwayat_tree.insert("", tk.END, values=row)

    def show_lihat_data_table(self):
        self.clear_window()

        label = tk.Label(self.root, text="Data Barang", font=("Arial", 16))
        label.pack(pady=10)

        columns = (
            "Kode Barang", "Nama Barang", "Satuan", "Stok Awal",
            "Barang Masuk", "Barang Keluar", "Stok Akhir", "Status"
        )

        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        for idx, row in self.dataframe.iterrows():
            self.tree.insert("", tk.END, iid=idx, values=tuple(row))

        self.tree.pack(pady=10, fill='both', expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Status:").grid(row=0, column=0, padx=5)
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(form_frame, textvariable=self.status_var, values=["ADA", "KOSONG"])
        self.status_combo.grid(row=0, column=1, padx=5)

        update_button = tk.Button(form_frame, text="Update Status", command=self.update_status)
        update_button.grid(row=0, column=2, padx=5)

        reset_button = tk.Button(self.root, text="Reset Data", command=self.reset_data)
        reset_button.pack(pady=5)

        exit_button = tk.Button(self.root, text="Kembali ke Menu", command=self.show_main_menu)
        exit_button.pack(pady=10)

    def on_row_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_item = int(selected[0])
            current_status = self.dataframe.at[self.selected_item, 'Status']
            self.status_var.set(current_status)

    def update_status(self):
        if self.selected_item is not None:
            new_status = self.status_var.get()
            self.dataframe.at[self.selected_item, 'Status'] = new_status
            row = list(self.dataframe.iloc[self.selected_item])
            self.tree.item(self.selected_item, values=row)

    def reset_data(self):
        confirm = messagebox.askyesno("Konfirmasi", "Apakah yakin ingin reset data?")
        if confirm:
            self.dataframe = pd.DataFrame()
            self.riwayat_data = []
            self.show_lihat_data()
            
    def barang_keluar(self):
        if self.dataframe.empty:
            messagebox.showwarning("Peringatan", "Silakan muat file data terlebih dahulu.")
            return

        self.clear_window()

        label = tk.Label(self.root, text="Barang Keluar", font=("Arial", 16))
        label.pack(pady=10)

        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Tanggal:").grid(row=0, column=0, padx=5, pady=5)
        self.tanggal_keluar_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(form_frame, textvariable=self.tanggal_keluar_var, state='readonly').grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Kode Barang:").grid(row=1, column=0, padx=5, pady=5)
        self.kode_barang_keluar_var = tk.StringVar()
        self.kode_barang_keluar_combo = ttk.Combobox(form_frame, textvariable=self.kode_barang_keluar_var)
        self.kode_barang_keluar_combo['values'] = self.dataframe['Kode Barang'].tolist()
        self.kode_barang_keluar_combo.grid(row=1, column=1, padx=5, pady=5)
        self.kode_barang_keluar_combo.bind("<<ComboboxSelected>>", self.update_nama_barang_keluar)

        tk.Label(form_frame, text="Nama Barang:").grid(row=2, column=0, padx=5, pady=5)
        self.nama_barang_keluar_var = tk.StringVar()
        self.nama_barang_keluar_entry = tk.Entry(form_frame, textvariable=self.nama_barang_keluar_var, state='readonly')
        self.nama_barang_keluar_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Keterangan:").grid(row=3, column=0, padx=5, pady=5)
        self.keterangan_keluar_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.keterangan_keluar_var).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Jumlah Keluar:").grid(row=4, column=0, padx=5, pady=5)
        self.jumlah_keluar_var = tk.IntVar(value=0)
        tk.Entry(form_frame, textvariable=self.jumlah_keluar_var).grid(row=4, column=1, padx=5, pady=5)

        simpan_button = tk.Button(self.root, text="Simpan Data Keluar", command=self.simpan_data_keluar)
        simpan_button.pack(pady=5)

        back_button = tk.Button(self.root, text="Kembali ke Menu", command=self.show_main_menu)
        back_button.pack(pady=5)

        riwayat_label = tk.Label(self.root, text="Riwayat Barang Keluar", font=("Arial", 14))
        riwayat_label.pack(pady=10)

        self.riwayat_keluar_tree = ttk.Treeview(
            self.root, columns=("Tanggal", "Kode Barang", "Nama Barang", "Keterangan", "Jumlah"), show="headings")
        for col in ("Tanggal", "Kode Barang", "Nama Barang", "Keterangan", "Jumlah"):
            self.riwayat_keluar_tree.heading(col, text=col)
            self.riwayat_keluar_tree.column(col, width=120)
        self.riwayat_keluar_tree.pack(pady=10, fill='both', expand=True)

        self.update_riwayat_keluar_tree()
        
    def update_nama_barang_keluar(self, event):
        kode = self.kode_barang_keluar_var.get()
        row = self.dataframe[self.dataframe['Kode Barang'] == kode]
        if not row.empty:
            nama_barang = row.iloc[0]['Nama Barang']
            self.nama_barang_keluar_var.set(nama_barang)
            
    def simpan_data_keluar(self):
        kode = self.kode_barang_keluar_var.get()
        jumlah_keluar = self.jumlah_keluar_var.get()

        if kode == "" or jumlah_keluar <= 0:
            messagebox.showerror("Error", "Pastikan kode barang dan jumlah keluar diisi dengan benar.")
            return

        idx = self.dataframe.index[self.dataframe['Kode Barang'] == kode].tolist()[0]
        if jumlah_keluar > self.dataframe.at[idx, 'Stok Akhir']:
            messagebox.showerror("Error", "Stok tidak mencukupi.")
            return

        self.dataframe.at[idx, 'Barang Keluar'] += jumlah_keluar
        self.dataframe.at[idx, 'Stok Akhir'] = (
            self.dataframe.at[idx, 'Stok Awal'] + self.dataframe.at[idx, 'Barang Masuk'] - self.dataframe.at[idx, 'Barang Keluar']
        )

        riwayat_entry = (
            self.tanggal_keluar_var.get(),
            kode,
            self.nama_barang_keluar_var.get(),
            self.keterangan_keluar_var.get(),
            jumlah_keluar
        )
        self.riwayat_data_keluar.append(riwayat_entry)
        self.update_riwayat_keluar_tree()

        messagebox.showinfo("Sukses", "Data barang keluar berhasil disimpan.")
        
    def update_riwayat_keluar_tree(self):
        if hasattr(self, 'riwayat_keluar_tree'):
            for item in self.riwayat_keluar_tree.get_children():
                self.riwayat_keluar_tree.delete(item)
            for row in self.riwayat_data_keluar:
                self.riwayat_keluar_tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleApp(root)
    root.mainloop()
