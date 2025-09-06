import tkinter as tk from tkinter import filedialog, messagebox from docx import Document import os

class DocxReplacerApp: def init(self, root): self.root = root self.root.title("DOCX Replacer") self.template_path = None self.save_location = None

# Select template button
    tk.Button(root, text="Select Template", command=self.load_template).pack(pady=5)

    # File name
    tk.Label(root, text="File Name:").pack()
    self.file_name_entry = tk.Entry(root, width=40)
    self.file_name_entry.pack(pady=5)

    # ID
    tk.Label(root, text="ID:").pack()
    self.id_entry = tk.Entry(root, width=40)
    self.id_entry.pack(pady=5)

    # Name
    tk.Label(root, text="Name:").pack()
    self.name_entry = tk.Entry(root, width=40)
    self.name_entry.pack(pady=5)

    # Age
    tk.Label(root, text="Age:").pack()
    self.age_entry = tk.Entry(root, width=40)
    self.age_entry.pack(pady=5)

    # Select location button
    tk.Button(root, text="Select Save Location", command=self.select_location).pack(pady=5)

    # Save button
    tk.Button(root, text="Save", command=self.save_docx).pack(pady=10)

def load_template(self):
    self.template_path = filedialog.askopenfilename(
        title="Select Template DOCX",
        filetypes=[("Word Documents", "*.docx")]
    )
    if self.template_path:
        messagebox.showinfo("Template Loaded", f"Template loaded: {os.path.basename(self.template_path)}")

def select_location(self):
    self.save_location = filedialog.askdirectory(title="Select Save Location")
    if self.save_location:
        messagebox.showinfo("Save Location Selected", f"Save location: {self.save_location}")

def save_docx(self):
    if not self.template_path:
        messagebox.showerror("Error", "Please select a template.")
        return
    if not self.save_location:
        messagebox.showerror("Error", "Please select a save location.")
        return
    if not self.file_name_entry.get():
        messagebox.showerror("Error", "Please enter a file name.")
        return

    # Load template
    doc = Document(self.template_path)

    # Replace placeholders in table
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text = cell.text
                if "id-if6h" in text:
                    cell.text = text.replace("id-if6h", self.id_entry.get())
                if "name-iguh" in text:
                    cell.text = text.replace("name-iguh", self.name_entry.get())
                if "age-ycuf" in text:
                    cell.text = text.replace("age-ycuf", self.age_entry.get())

    # Save new file
    save_path = os.path.join(self.save_location, f"{self.file_name_entry.get()}.docx")
    doc.save(save_path)
    messagebox.showinfo("Success", f"File saved: {save_path}")

if name == "main": root = tk.Tk() app = DocxReplacerApp(root) root.mainloop()

