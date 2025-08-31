import tkinter as tk
from tkinter import filedialog, messagebox
import os
import webbrowser
import json

DATA_FILE = "data.json"  # ovde se cuvaju svi predmeti i fajlovi

class UTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UTS")
        self.root.configure(bg="green")
        self.root.geometry("600x400")

        self.data = self.load_data()

        # Pocetni ekran
        self.label = tk.Label(root, text="UTS", font=("Arial", 48, "bold"), fg="white", bg="green")
        self.label.pack(expand=True)

        self.btn_next = tk.Button(
            root, text="Fajlovi", command=self.open_subjects_window,
            bg="white", fg="green", font=("Arial", 14, "bold")
        )
        self.btn_next.pack(pady=20)

    # Ucitavanje sacuvanih podataka
    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    # Cuvanje podataka
    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def open_subjects_window(self):
        self.subject_window = tk.Toplevel(self.root)
        self.subject_window.title("Predmeti")
        self.subject_window.geometry("600x400")
        self.subject_window.configure(bg="green")

        tk.Label(
            self.subject_window, text="Unesi predmet i pritisni Enter",
            bg="green", fg="white", font=("Arial", 14)
        ).pack(pady=10)

        self.entry_subject = tk.Entry(self.subject_window, font=("Arial", 14))
        self.entry_subject.pack(pady=5)
        self.entry_subject.bind("<Return>", self.add_subject)

        self.listbox = tk.Listbox(self.subject_window, font=("Arial", 14), bg="white", fg="green")
        self.listbox.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.listbox.bind("<Double-Button-1>", self.open_files_window)

        # Ucitaj postojeca imena predmeta
        for subject in self.data.keys():
            self.listbox.insert(tk.END, subject)

    def add_subject(self, event=None):
        subject = self.entry_subject.get().strip()
        if subject and subject not in self.data:
            self.listbox.insert(tk.END, subject)
            self.data[subject] = []
            self.save_data()
            self.entry_subject.delete(0, tk.END)

    def open_files_window(self, event=None):
        selected = self.listbox.curselection()
        if not selected:
            return
        subject = self.listbox.get(selected)

        self.files_window = tk.Toplevel(self.root)
        self.files_window.title(f"Fajlovi za {subject}")
        self.files_window.geometry("600x400")
        self.files_window.configure(bg="green")

        self.current_subject = subject
        self.files = self.data.get(subject, [])

        self.listbox_files = tk.Listbox(self.files_window, font=("Arial", 12), bg="white", fg="green")
        self.listbox_files.pack(fill="both", expand=True, padx=20, pady=20)

        # Ucitaj fajlove
        for fp in self.files:
            self.listbox_files.insert(tk.END, os.path.basename(fp))

        btn_frame = tk.Frame(self.files_window, bg="green")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="Dodaj fajlove", command=self.add_files,
            bg="white", fg="green", font=("Arial", 12, "bold")
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame, text="Otvori fajl", command=self.open_file,
            bg="white", fg="green", font=("Arial", 12, "bold")
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            btn_frame, text="Izbrisi fajl", command=self.delete_file,
            bg="white", fg="green", font=("Arial", 12, "bold")
        ).grid(row=0, column=2, padx=10)

    def add_files(self):
        filepaths = filedialog.askopenfilenames(title="Izaberi fajlove")
        for fp in filepaths:
            if fp not in self.files:
                self.files.append(fp)
                self.listbox_files.insert(tk.END, os.path.basename(fp))
        self.data[self.current_subject] = self.files
        self.save_data()

    def open_file(self):
        selected = self.listbox_files.curselection()
        if not selected:
            messagebox.showwarning("Upozorenje", "Nijedan fajl nije izabran")
            return
        filepath = self.files[selected[0]]
        try:
            webbrowser.open(filepath)
        except Exception as e:
            messagebox.showerror("Greška", str(e))

    def delete_file(self):
        selected = self.listbox_files.curselection()
        if not selected:
            return
        index = selected[0]
        self.listbox_files.delete(index)
        self.files.pop(index)
        self.data[self.current_subject] = self.files
        self.save_data()


if __name__ == "__main__":
    root = tk.Tk()
    app = UTSApp(root)
    root.mainloop()
