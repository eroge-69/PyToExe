from __future__ import annotations

import math
import unicodedata
from pathlib import Path
from typing import Optional, Union
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk


def strip_accents(text: str) -> str:
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn").lower()


def parse_grade(value: Union[str, float, int, None]) -> float:
    if pd.isna(value):
        return math.nan
    value_str = str(value).strip().replace(",", ".")
    if value_str in {"", "-", "—"}:
        return math.nan
    try:
        val = float(value_str)
    except ValueError:
        return math.nan
    if val > 10:
        val = val / 10.0
    return max(0.0, min(val, 10.0))


def compute_final_grade(df: pd.DataFrame) -> float:
    passed = df[df["Grade"] >= 5]
    passed["PROD_GRADE_ECTS"] = passed["Grade"] * passed["ECTS"]
    if passed.empty:
        return math.nan

    weighted_sum = passed["PROD_GRADE_ECTS"].sum()
    ects_sum = passed["ECTS"].sum()

    return weighted_sum / ects_sum


def dataframe_from_excel(path: str | Path) -> pd.DataFrame:
    df_raw = pd.read_excel(path)
    df_filtered = df_raw[df_raw["Η Καρτέλα μου"] != "Κωδ. μαθήματος"].copy()

    ects_col = (
        df_filtered["Unnamed: 11"].astype(str).str.replace(",", ".")
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0.0)
        .astype(float)
    )

    df = pd.DataFrame(
        {
            "Course": df_filtered["Unnamed: 1"].astype(str).str.strip(),
            "Grade": df_filtered["Unnamed: 2"].apply(parse_grade),
            "DM": pd.to_numeric(df_filtered["Unnamed: 10"], errors="coerce")
            .fillna(0)
            .astype(int),
            "ECTS": ects_col,
        }
    )
    return df.drop_duplicates(subset="Course", keep="first").reset_index(drop=True)


def save_dataframe_to_excel(df: pd.DataFrame, path: str | Path) -> None:
    df_out = df.copy()
    df_out.rename(columns={"Course": "Μάθημα", "ECTS": "ΔΜ", "Grade": "Βαθμός"}, inplace=True)
    df_out.to_excel(path, index=False)

class GradeDialog(simpledialog.Dialog):

    def __init__(self, parent: tk.Tk, title: str, init_grade: str = ""):
        self.init_grade = init_grade
        self.result: Optional[float] = None
        super().__init__(parent, title=title)

    def body(self, frame):
        ttk.Label(frame, text="Βαθμός (0–10):").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.e_grade = ttk.Entry(frame, width=10)
        self.e_grade.grid(row=0, column=1, sticky=tk.W, pady=6)
        self.e_grade.insert(0, self.init_grade)
        return self.e_grade

    def validate(self):
        grade_txt = self.e_grade.get().strip()
        grade_val = parse_grade(grade_txt)
        if math.isnan(grade_val):
            messagebox.showerror("Λάθος", "Δώσε έγκυρο βαθμό 0–10 ή άφησε κενό.")
            return False
        self.result = grade_val
        return True


class CourseDialog(simpledialog.Dialog):

    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        init_course: str = "",
        init_dm: str = "",
        init_ects: str = "",
        init_grade: str = "",
        disable_course: bool = False,
    ):
        self.init_course = init_course
        self.init_dm = init_dm
        self.init_ects = init_ects
        self.init_grade = init_grade
        self.disable_course = disable_course
        self.result = None
        super().__init__(parent, title=title)

    def body(self, frame):
        ttk.Label(frame, text="Μάθημα:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.e_course = ttk.Entry(frame, width=50)
        self.e_course.grid(row=0, column=1, pady=4)
        self.e_course.insert(0, self.init_course)
        if self.disable_course:
            self.e_course.configure(state="disabled")

        ttk.Label(frame, text="ΔΜ:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.e_dm = ttk.Entry(frame, width=10)
        self.e_dm.grid(row=1, column=1, sticky=tk.W, pady=4)
        self.e_dm.insert(0, self.init_dm)

        ttk.Label(frame, text="ECTS:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.e_ects = ttk.Entry(frame, width=10)
        self.e_ects.grid(row=2, column=1, sticky=tk.W, pady=4)
        self.e_ects.insert(0, self.init_ects)

        ttk.Label(frame, text="Βαθμός (0–10):").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.e_grade = ttk.Entry(frame, width=10)
        self.e_grade.grid(row=3, column=1, sticky=tk.W, pady=4)
        self.e_grade.insert(0, self.init_grade)
        return self.e_course

    def validate(self):
        course = self.e_course.get().strip()
        dm_txt = self.e_dm.get().strip()
        ects_txt = self.e_ects.get().strip()
        grade_txt = self.e_grade.get().strip()

        if not course:
            messagebox.showerror("Λάθος", "Ο τίτλος μαθήματος είναι κενός.")
            return False

        try:
            dm_val = int(dm_txt)
            if dm_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Λάθος", "ΔΜ πρέπει να είναι μη αρνητικός ακέραιος.")
            return False
        
        try:
            ects_val = float(ects_txt)
            if ects_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Λάθος", "ECTS πρέπει να είναι μη αρνητικός ακέραιος.")
            return False

        grade_val = parse_grade(grade_txt)
        if not (math.isnan(grade_val) or 0 <= grade_val <= 10):
            messagebox.showerror("Λάθος", "Βαθμός πρέπει να είναι 0–10 ή κενός.")
            return False

        self.result = (course, dm_val, ects_val, grade_val)
        return True


class GradeManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Διαχειριστής Καρτέλας Μαθημάτων")
        self.geometry("900x600")
        self.minsize(760, 520)
        self.configure(padx=10, pady=10)

        self.df: Optional[pd.DataFrame] = None
        self.file_path: Optional[str | Path] = None

        self.create_widgets()
        self.after(100, self.open_excel_dialog)

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure(
            "Grade.Treeview.Heading",
            background="#376592",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure("Grade.Treeview", rowheight=22)

        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=(8, 8))

        self.search_button = ttk.Button(top, text="Αναζήτηση", command=self.search_course)
        self.search_button.pack(side=tk.RIGHT)

        self.search_bar = ttk.Entry(top, font=("Segoe UI", 11))
        self.search_bar.bind("<Return>", self.search_course)
        self.search_bar.bind("<Control-a>", self._select_all)
        self.search_bar.bind("<Control-A>", self._select_all)
        self.search_bar.bind("<Control-BackSpace>", self._ctrl_backspace)
        self.search_bar.pack(side=tk.RIGHT, padx=(0, 8))

        self.search_label = ttk.Label(top, text="Αναζήτηση Μαθήματος:", font=("Segoe UI", 11, "bold"))
        self.search_label.pack(side=tk.RIGHT, padx=(0, 20))
        
        columns = ("Course", "DM", "ECTS", "Grade")
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Grade.Treeview",
        )
        self.tree.heading("Course", text="Μάθημα")
        self.tree.heading("DM", text="ΔΜ")
        self.tree.heading("ECTS", text="ECTS")
        self.tree.heading("Grade", text="Βαθμός")

        self.tree.column("Course", width=460, anchor=tk.W)
        self.tree.column("DM", width=60, anchor=tk.CENTER)
        self.tree.column("ECTS", width=60, anchor=tk.CENTER)
        self.tree.column("Grade", width=80, anchor=tk.CENTER)

        self.tree.tag_configure("odd", background="#D3D3D3")
        self.tree.tag_configure("even", background="#FFFFFF")

        self.tree.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, pady=(8, 0))

        self.avg_label = ttk.Label(bottom, text="Σταθμισμένος Μ.Ο.: —", font=("Segoe UI", 11, "bold"))
        self.avg_label.pack(side=tk.LEFT, padx=(0, 20))

        btn_specs = (
            ("📂 Άνοιγμα…", self.open_excel_dialog),
            ("➕ Προσθήκη", self.add_course_dialog),
            ("✏️  Αλλαγή Βαθμού", self.edit_selected_dialog),
            ("🗑️  Διαγραφή", self.delete_selected),
            ("💾 Αποθήκευση", self.save_changes),
            ("💾 Αποθήκευση ως…", self.save_as_dialog),
        )
        for text, cmd in reversed(btn_specs):
            ttk.Button(bottom, text=text, command=cmd).pack(side=tk.RIGHT, padx=4)

    def _select_all(self, event):
        event.widget.select_range(0, tk.END)
        event.widget.icursor(tk.END)
        return "break"

    def _ctrl_backspace(self, event):
        entry: tk.Entry = event.widget
        cursor = entry.index(tk.INSERT)
        if cursor == 0:
            return "break"
        text = entry.get()
        i = cursor
        while i > 0 and text[i - 1] == " ":
            i -= 1
        while i > 0 and text[i - 1] != " ":
            i -= 1
        entry.delete(i, cursor)
        return "break"

    def open_excel_dialog(self):
        path = filedialog.askopenfilename(
            title="Επιλογή Excel καρτέλας",
            initialdir=".",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*")),
        )
        if path:
            self.load_file(path)

    def load_file(self, path: str | Path):
        try:
            self.df = dataframe_from_excel(path)
        except Exception as err:
            messagebox.showerror("Σφάλμα", f"Αποτυχία φόρτωσης Excel:\n{err}")
            return
        self.file_path = path
        self.refresh_tree()
        self.update_average()
        self.title(f"Καρτέλα: {Path(path).name} – Διαχειριστής Μαθημάτων")

    def save_changes(self):
        if self.df is None:
            messagebox.showinfo("Δεν υπάρχει δεδομένα", "Δεν υπάρχουν δεδομένα για αποθήκευση.")
            return
        if self.file_path is None:
            self.save_as_dialog()
            return
        try:
            save_dataframe_to_excel(self.df, self.file_path)
            messagebox.showinfo("Επιτυχία", f"Αποθηκεύτηκε: {self.file_path}")
        except Exception as err:
            messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατή η αποθήκευση:\n{err}")

    def save_as_dialog(self):
        if self.df is None:
            messagebox.showinfo("Δεν υπάρχει δεδομένα", "Δεν υπάρχουν δεδομένα για αποθήκευση.")
            return
        initial_dir = str(Path(self.file_path).parent) if self.file_path else "."
        path = filedialog.asksaveasfilename(
            title="Αποθήκευση καρτέλας ως…",
            defaultextension=".xlsx",
            initialdir=initial_dir,
            filetypes=(("Excel", "*.xlsx"),),
        )
        if not path:
            return
        try:
            save_dataframe_to_excel(self.df, path)
            self.file_path = path
            self.title(f"Καρτέλα: {Path(path).name} – Διαχειριστής Μαθημάτων")
            messagebox.showinfo("Επιτυχία", f"Αποθηκεύτηκε: {path}")
        except Exception as err:
            messagebox.showerror("Σφάλμα", f"Δεν ήταν δυνατή η αποθήκευση:\n{err}")

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        if self.df is None:
            return

        for idx, row in self.df.iterrows():
            grade_disp = "0.0" if math.isnan(row["Grade"]) else f"{row['Grade']:.1f}"
            tag = "odd" if idx % 2 else "even"
            self.tree.insert(
                "",
                tk.END,
                iid=str(idx),
                values=(row["Course"], row["DM"], row["ECTS"], grade_disp),
                tags=(tag,)
            )

    def update_average(self):
        if self.df is None or self.df.empty:
            self.avg_label.config(text="Σταθμισμένος Μ.Ο.: —")
            return
        avg = compute_final_grade(self.df)
        self.avg_label.config(text=f"Σταθμισμένος Μ.Ο.: {'—' if math.isnan(avg) else f'{avg:.2f}'}")

    def get_selected_index(self) -> Optional[int]:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Καμία επιλογή", "Παρακαλώ επιλέξτε ένα μάθημα.")
            return None
        return int(sel[0])

    def add_course_dialog(self):
        dlg = CourseDialog(self, title="Προσθήκη Μαθήματος")
        if dlg.result:
            course, dm_val, ects_val, grade_val = dlg.result
            if course in self.df["Course"].values:
                messagebox.showerror("Υπάρχει ήδη", "Το μάθημα υπάρχει ήδη στη λίστα.")
                return
            self.df.loc[len(self.df)] = {"Course": course, "DM": dm_val, "ECTS": ects_val, "Grade": grade_val}
            self.refresh_tree()
            self.update_average()

    def edit_selected_dialog(self):
        idx = self.get_selected_index()
        if idx is None:
            return
        curr_grade = self.df.at[idx, "Grade"]
        init_grade = "" if math.isnan(curr_grade) else f"{curr_grade:.1f}"

        dlg = GradeDialog(self, title="Αλλαγή Βαθμού", init_grade=init_grade)
        if dlg.result is not None:
            self.df.at[idx, "Grade"] = dlg.result
            self.refresh_tree()
            self.update_average()

    def delete_selected(self):
        idx = self.get_selected_index()
        if idx is None:
            return
        if messagebox.askyesno("Διαγραφή", "Να διαγραφεί το επιλεγμένο μάθημα;"):
            self.df.drop(index=idx, inplace=True)
            self.df.reset_index(drop=True, inplace=True)
            self.refresh_tree()
            self.update_average()

    def search_course(self, *_):
        if self.df is None:
            return

        query_raw = self.search_bar.get()
        query = strip_accents(query_raw)

        self.tree.selection_remove(self.tree.selection())

        if not query:
            return
        
        for idx, course in enumerate(self.df["Course"]):
            if query in strip_accents(course):
                iid = str(idx)
                self.tree.selection_set(iid)
                self.tree.focus(iid)
                self.tree.see(iid)
                return
            
        messagebox.showerror("Δεν Υπάρχει", "Δεν υπάρχει αυτό το μάθημα στην λίστα.")
            

def main():
    app = GradeManagerApp()
    app.mainloop()

if __name__ == "__main__":
    main()