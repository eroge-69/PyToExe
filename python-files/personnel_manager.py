import os
import datetime
import pandas as pd
from tkinter import *
from tkinter import messagebox, ttk

DB_FILE = "personnel_db.xlsx"

PERSONNEL_SHEET = "Personnel"
NOTES_SHEET = "Notes"

PERSONNEL_HEADERS = ["Code", "FirstName", "LastName", "Position", "Phone"]
NOTES_HEADERS = ["Code", "Date", "Note"]

def init_db():
    if not os.path.exists(DB_FILE):
        with pd.ExcelWriter(DB_FILE, engine="openpyxl") as writer:
            pd.DataFrame(columns=PERSONNEL_HEADERS).to_excel(writer, sheet_name=PERSONNEL_SHEET, index=False)
            pd.DataFrame(columns=NOTES_HEADERS).to_excel(writer, sheet_name=NOTES_SHEET, index=False)

def load_personnel():
    return pd.read_excel(DB_FILE, sheet_name=PERSONNEL_SHEET)

def load_notes():
    return pd.read_excel(DB_FILE, sheet_name=NOTES_SHEET)

def save_personnel(df):
    with pd.ExcelWriter(DB_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=PERSONNEL_SHEET, index=False)

def save_notes(df):
    with pd.ExcelWriter(DB_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=NOTES_SHEET, index=False)

class App:
    def __init__(self, root):
        self.root = root
        root.title("Personnel Manager")
        root.geometry("600x500")
        tab_control = ttk.Notebook(root)
        self.tab_register = Frame(tab_control)
        self.tab_search = Frame(tab_control)
        self.tab_report = Frame(tab_control)
        tab_control.add(self.tab_register, text="Register Personnel")
        tab_control.add(self.tab_search, text="Search & Notes")
        tab_control.add(self.tab_report, text="Managerial Report")
        tab_control.pack(expand=1, fill="both")

        self.build_register_tab()
        self.build_search_tab()
        self.build_report_tab()

    def build_register_tab(self):
        Label(self.tab_register, text="First Name").grid(row=0, column=0, padx=5, pady=5, sticky=E)
        Label(self.tab_register, text="Last Name").grid(row=1, column=0, padx=5, pady=5, sticky=E)
        Label(self.tab_register, text="Code").grid(row=2, column=0, padx=5, pady=5, sticky=E)
        Label(self.tab_register, text="Position").grid(row=3, column=0, padx=5, pady=5, sticky=E)
        Label(self.tab_register, text="Phone").grid(row=4, column=0, padx=5, pady=5, sticky=E)

        self.entry_fname = Entry(self.tab_register)
        self.entry_lname = Entry(self.tab_register)
        self.entry_code = Entry(self.tab_register)
        self.entry_position = Entry(self.tab_register)
        self.entry_phone = Entry(self.tab_register)

        self.entry_fname.grid(row=0, column=1, padx=5, pady=5)
        self.entry_lname.grid(row=1, column=1, padx=5, pady=5)
        self.entry_code.grid(row=2, column=1, padx=5, pady=5)
        self.entry_position.grid(row=3, column=1, padx=5, pady=5)
        self.entry_phone.grid(row=4, column=1, padx=5, pady=5)

        Button(self.tab_register, text="Save Personnel", command=self.save_personnel_btn).grid(row=5, column=0, columnspan=2, pady=10)

    def save_personnel_btn(self):
        fname = self.entry_fname.get().strip()
        lname = self.entry_lname.get().strip()
        code = self.entry_code.get().strip()
        position = self.entry_position.get().strip()
        phone = self.entry_phone.get().strip()
        if not (fname and lname and code):
            messagebox.showerror("Error", "First Name, Last Name, and Code are required.")
            return
        df = load_personnel()
        if code in df["Code"].astype(str).values:
            messagebox.showerror("Error", "Personnel code already exists.")
            return
        df.loc[len(df)] = [code, fname, lname, position, phone]
        save_personnel(df)
        messagebox.showinfo("Success", "Personnel saved successfully.")
        for e in [self.entry_fname, self.entry_lname, self.entry_code, self.entry_position, self.entry_phone]:
            e.delete(0, END)

    def build_search_tab(self):
        Label(self.tab_search, text="Personnel Code").grid(row=0, column=0, padx=5, pady=5, sticky=E)
        self.search_code_entry = Entry(self.tab_search)
        self.search_code_entry.grid(row=0, column=1, padx=5, pady=5)
        Button(self.tab_search, text="Search", command=self.search_personnel).grid(row=0, column=2, padx=5, pady=5)

        self.info_text = Text(self.tab_search, width=60, height=10, state=DISABLED)
        self.info_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        Label(self.tab_search, text="New Note").grid(row=2, column=0, padx=5, pady=5, sticky=NE)
        self.note_entry = Text(self.tab_search, width=45, height=4)
        self.note_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        Button(self.tab_search, text="Add Note", command=self.add_note).grid(row=3, column=1, pady=10)

    def search_personnel(self):
        code = self.search_code_entry.get().strip()
        df = load_personnel()
        person = df[df["Code"].astype(str) == code]
        self.info_text.configure(state=NORMAL)
        self.info_text.delete("1.0", END)
        if person.empty:
            self.info_text.insert(END, "Personnel not found.")
            self.info_text.configure(state=DISABLED)
            return
        p = person.iloc[0]
        info = f"Code: {p['Code']}\nName: {p['FirstName']} {p['LastName']}\nPosition: {p['Position']}\nPhone: {p['Phone']}\n\nNotes:\n"
        notes_df = load_notes()
        notes = notes_df[notes_df["Code"].astype(str) == code]
        if notes.empty:
            info += "No notes yet."
        else:
            for _, n in notes.iterrows():
                info += f"- {n['Date']}: {n['Note']}\n"
        self.info_text.insert(END, info)
        self.info_text.configure(state=DISABLED)

    def add_note(self):
        code = self.search_code_entry.get().strip()
        note_text = self.note_entry.get("1.0", END).strip()
        if not (code and note_text):
            messagebox.showerror("Error", "Enter personnel code and note.")
            return
        df_notes = load_notes()
        df_notes.loc[len(df_notes)] = [code, datetime.date.today().isoformat(), note_text]
        save_notes(df_notes)
        self.note_entry.delete("1.0", END)
        messagebox.showinfo("Success", "Note added.")
        self.search_personnel()

    def build_report_tab(self):
        Button(self.tab_report, text="Generate Report", command=self.generate_report).pack(pady=20)
        self.report_label = Label(self.tab_report, text="")
        self.report_label.pack()

    def generate_report(self):
        notes_df = load_notes()
        if notes_df.empty:
            messagebox.showinfo("Info", "No notes to report.")
            return
        personnel_df = load_personnel()
        merged = notes_df.merge(personnel_df, on="Code", how="left")
        summary = merged.groupby(["Code", "FirstName", "LastName"]).agg(
            NotesCount=("Note", "count"),
            LastNoteDate=("Date", "max")
        ).reset_index()
        report_file = "managerial_report.xlsx"
        summary.to_excel(report_file, index=False)
        self.report_label.config(text=f"Report saved to {report_file}")
        messagebox.showinfo("Report", f"Report saved to {report_file}")

if __name__ == "__main__":
    init_db()
    root = Tk()
    app = App(root)
    root.mainloop()
