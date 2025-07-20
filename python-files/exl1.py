import customtkinter as ctk
from tkinter import filedialog, ttk
import pandas as pd
import threading
import tkinter as tk

class ExcelSearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.df = None
        self.search_results_df = None

        self.title("🔍 محرك بحث Excel المطور")
        self.geometry("700x480")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)  # السماح لإطار الجدول بالتمدد

        self._setup_widgets()
        self._style_treeview()

    def _setup_widgets(self):
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        top_frame.grid_columnconfigure(2, weight=1)

        load_btn = ctk.CTkButton(top_frame, text="📁 اختيار ملف Excel", command=self.load_file)
        load_btn.grid(row=0, column=0, padx=10, pady=10)

        self.file_label = ctk.CTkLabel(top_frame, text="لم يتم اختيار ملف بعد", text_color="gray")
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="w", columnspan=2)

        columns_frame = ctk.CTkFrame(self)
        columns_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        columns_frame.grid_columnconfigure(2, weight=1)

        columns_label = ctk.CTkLabel(columns_frame, text="🔽 اختر عمود للبحث:")
        columns_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.column_combobox = ttk.Combobox(columns_frame, state="readonly")
        self.column_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.column_combobox["values"] = ["كل الأعمدة"]
        self.column_combobox.current(0)

        self.exact_match_var = tk.BooleanVar(value=True)
        exact_match_check = ctk.CTkCheckBox(columns_frame, text="بحث دقيق (مطابق تماماً)", variable=self.exact_match_var)
        exact_match_check.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(search_frame, placeholder_text="اكتب الكلمة للبحث...")
        self.entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.entry.bind("<Return>", self.start_search_thread)

        search_btn = ctk.CTkButton(search_frame, text="🔍 بحث", width=100, command=self.start_search_thread)
        search_btn.grid(row=0, column=1, padx=5, pady=10)

        show_all_btn = ctk.CTkButton(search_frame, text="📋 عرض الكل", width=100, command=self.show_all_data)
        show_all_btn.grid(row=0, column=2, padx=5, pady=10)

        clear_btn = ctk.CTkButton(search_frame, text="❌ مسح", width=100, fg_color="#D32F2F", hover_color="#B71C1C", command=self.clear_search)
        clear_btn.grid(row=0, column=3, padx=(5, 10), pady=10)

        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        self.tree_frame.grid_propagate(False)
        self.tree_frame.grid_remove()

        tree_scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical")
        tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal")

        self.tree = ttk.Treeview(self.tree_frame, show="headings",
                                 yscrollcommand=tree_scroll_y.set,
                                 xscrollcommand=tree_scroll_x.set)

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(bottom_frame, text="جاهز للبحث ✨")
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.progressbar = ctk.CTkProgressBar(bottom_frame, orientation="horizontal")
        self.progressbar.set(0)

        self.export_btn = ctk.CTkButton(bottom_frame, text="📤 تصدير النتائج", command=self.export_results, state="disabled")
        self.export_btn.grid(row=0, column=1, padx=10, pady=5, sticky="e")

    def _style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")

        bg_color = "#242424"
        text_color = "#DCE4EE"
        header_bg_color = "#2A2D2E"
        selected_color = "#1F6AA5"

        style.configure("Custom.Treeview",
                        background=bg_color,
                        foreground=text_color,
                        fieldbackground=bg_color,
                        borderwidth=0)

        style.map('Custom.Treeview', background=[('selected', selected_color)])

        style.configure("Custom.Treeview.Heading",
                        background=header_bg_color,
                        foreground=text_color,
                        relief="flat",
                        font=('Calibri', 11, 'bold'))

        style.map("Custom.Treeview.Heading",
                  background=[('active', bg_color)])

        self.tree.configure(style="Custom.Treeview")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="اختر ملف Excel",
            filetypes=[("Excel Files", "*.xlsx;*.xls"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            self.df = pd.read_excel(file_path)
            self.file_label.configure(text=f"📄 {file_path.split('/')[-1]}", text_color="white")
            self.status_label.configure(text=f"✅ تم تحميل الملف بنجاح ({len(self.df)} صف، {len(self.df.columns)} عمود)")
            self.clear_search()
            self._fill_combobox()
        except Exception as e:
            self.status_label.configure(text=f"❌ خطأ في تحميل الملف: {e}", text_color="#E53935")
            self.df = None

    def _fill_combobox(self):
        cols = ["كل الأعمدة"]
        if self.df is not None:
            cols.extend(self.df.columns.tolist())
        self.column_combobox["values"] = cols
        self.column_combobox.current(0)

    def start_search_thread(self, event=None):
        if self.df is None:
            self.status_label.configure(text="⚠️ يرجى تحميل ملف أولاً!", text_color="orange")
            return

        keyword = self.entry.get().strip()
        if not keyword:
            self.status_label.configure(text="🟡 أدخل كلمة للبحث.", text_color="yellow")
            return

        selected_col = self.column_combobox.get()
        exact = self.exact_match_var.get()

        self.status_label.configure(text="⏳ جاري البحث...", text_color="cyan")
        self.progressbar.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.progressbar.start()

        search_thread = threading.Thread(target=self._perform_search, args=(keyword, selected_col, exact))
        search_thread.daemon = True
        search_thread.start()

    def _perform_search(self, keyword, column, exact):
        try:
            df = self.df
            if column == "كل الأعمدة":
                if exact:
                    mask = df.apply(lambda row: row.astype(str).eq(keyword).any(), axis=1)
                else:
                    mask = df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)
                results = df[mask]
            else:
                col_series = df[column].astype(str)
                if exact:
                    mask = col_series.eq(keyword)
                else:
                    mask = col_series.str.contains(keyword, case=False, na=False)
                results = df[mask]
        except Exception as e:
            results = pd.DataFrame()
            self.after(0, self.status_label.configure, {"text": f"❌ خطأ في البحث: {e}", "text_color": "#E53935"})

        self.after(0, self._update_ui_with_results, results)

    def show_all_data(self):
        if self.df is None:
            self.status_label.configure(text="⚠️ يرجى تحميل ملف أولاً!", text_color="orange")
            return
        self.after(0, self._update_ui_with_results, self.df)

    def _update_ui_with_results(self, results_df):
        self.clear_table()
        self.search_results_df = results_df

        if not results_df.empty:
            self.tree_frame.grid()
            self.geometry("1000x700")

            self.tree["columns"] = list(results_df.columns)
            self.tree["displaycolumns"] = list(results_df.columns)

            for col in results_df.columns:
                self.tree.heading(col, text=col, anchor="center")
                self.tree.column(col, anchor="w", width=150, minwidth=100)

            for _, row in results_df.iterrows():
                self.tree.insert("", "end", values=list(row))

            self.status_label.configure(text=f"✅ تم العثور على {len(results_df)} نتيجة.", text_color="lightgreen")
            self.export_btn.configure(state="normal")
        else:
            self.tree_frame.grid_remove()
            self.geometry("700x480")
            self.status_label.configure(text="❌ لم يتم العثور على نتائج.", text_color="#E53935")
            self.export_btn.configure(state="disabled")

        self.progressbar.stop()
        self.progressbar.grid_remove()

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_search(self):
        self.entry.delete(0, 'end')
        self.clear_table()
        self.tree_frame.grid_remove()
        self.status_label.configure(text="جاهز للبحث ✨", text_color="gray")
        self.export_btn.configure(state="disabled")
        self.search_results_df = None
        self.geometry("700x480")

    def export_results(self):
        if self.search_results_df is None or self.search_results_df.empty:
            self.status_label.configure(text="⚠️ لا توجد نتائج لتصديرها.", text_color="orange")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")],
            title="حفظ نتائج البحث"
        )

        if not file_path:
            return

        try:
            if file_path.endswith('.csv'):
                self.search_results_df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                self.search_results_df.to_excel(file_path, index=False)
            self.status_label.configure(text=f"💾 تم تصدير النتائج بنجاح إلى: {file_path.split('/')[-1]}", text_color="lightgreen")
        except Exception as e:
            self.status_label.configure(text=f"❌ فشل التصدير: {e}", text_color="#E53935")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ExcelSearchApp()
    app.mainloop()
