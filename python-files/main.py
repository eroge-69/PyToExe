import customtkinter as ctk
from tkinter import filedialog, messagebox
from docx import Document
import json
import os

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class WordReplacerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("📄 DOCX Контракт-Редактор PRO")
        self.geometry(f"{int(self.winfo_screenwidth() * 0.85)}x{int(self.winfo_screenheight() * 0.85)}")
        self.file_path = None
        self.fields = {}
        self.create_ui()

    def create_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)

        self.btn_open = ctk.CTkButton(self.sidebar, text="📂 Открыть DOCX", command=self.load_file)
        self.btn_open.pack(pady=10)

        self.btn_save = ctk.CTkButton(self.sidebar, text="💾 Сохранить DOCX", command=self.replace_doc)
        self.btn_save.pack(pady=10)

        self.btn_clear = ctk.CTkButton(self.sidebar, text="🧹 Очистить поля", command=self.clear_fields)
        self.btn_clear.pack(pady=10)

        self.btn_template_save = ctk.CTkButton(self.sidebar, text="📁 Сохранить шаблон", command=self.save_template)
        self.btn_template_save.pack(pady=10)

        self.btn_template_load = ctk.CTkButton(self.sidebar, text="📁 Загрузить шаблон", command=self.load_template)
        self.btn_template_load.pack(pady=10)

        self.btn_theme = ctk.CTkButton(self.sidebar, text="🎨 Сменить тему", command=self.toggle_theme)
        self.btn_theme.pack(pady=10)

        self.main_area = ctk.CTkScrollableFrame(self, width=1000, height=800)
        self.main_area.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.theme = "light"

        sections = {
            "Общие": ["Название фирмы", "Номер контракта"],
            "SELLER": ["SELLER название", "SELLER адрес", "SELLER банк", "SELLER SWIFT", "SELLER счет"],
            "BUYER": ["BUYER название", "BUYER адрес", "BUYER банк", "BUYER SWIFT", "BUYER счет"],
            "Товар": ["Наименование товара", "VIN", "HS код", "Стоимость единицы", "Общая стоимость"]
        }

        for section, labels in sections.items():
            ctk.CTkLabel(self.main_area, text=f"📌 {section}", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=10)
            for label in labels:
                ctk.CTkLabel(self.main_area, text=label).pack(anchor="w", pady=(2, 0))
                entry = ctk.CTkEntry(self.main_area, width=700)
                entry.pack(pady=2)
                self.fields[label] = entry

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        ctk.set_appearance_mode(self.theme)

    def clear_fields(self):
        for field in self.fields.values():
            field.delete(0, ctk.END)

    def load_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
        if self.file_path:
            messagebox.showinfo("Файл загружен", f"Файл:\n{os.path.basename(self.file_path)}")

    def deep_replace_text(self, element, replacements):
        for p in element:
            full_text = "".join(run.text for run in p.runs)
            for old, new in replacements.items():
                if old in full_text:
                    full_text = full_text.replace(old, new)
            if p.runs:
                p.runs[0].text = full_text
                for run in p.runs[1:]:
                    run.text = ""

    def replace_doc(self):
        if not self.file_path:
            messagebox.showwarning("Ошибка", "Сначала загрузите DOCX файл.")
            return

        doc = Document(self.file_path)
        replacements = {
            "YG20250703Y01-1": self.fields["Номер контракта"].get(),
            "Ningbo Yonggang Logistics Co., LTD.": self.fields["SELLER название"].get(),
            "Beilun, Ningbo No.1, Building 1, No. 17 Haifa Road, BaIfeng": self.fields["SELLER адрес"].get(),
            "BANK OF COMMUNICATIONS": self.fields["SELLER банк"].get(),
            "COMMCNSHNBO": self.fields["SELLER SWIFT"].get(),
            "332006282143000006795": self.fields["SELLER счет"].get(),
            "Gou Grupp KG": self.fields["BUYER название"].get(),
            "ОсОО Гоу Групп Кей Джи": self.fields["BUYER название"].get(),
            "K. Akiev st. 95, office 18": self.fields["BUYER адрес"].get(),
            "К.Акиева 95,оф 18": self.fields["BUYER адрес"].get(),
            "ОАО «Айыл Банк»": self.fields["BUYER банк"].get(),
            "OJSC \\\" Аyil bank\\\"": self.fields["BUYER банк"].get(),
            "AIYLKG22": self.fields["BUYER SWIFT"].get(),
            "1350140020096039": self.fields["BUYER счет"].get(),
            "VOYAH FREE 2024 210KM 4WD Ultra-Long Range Intelligent Driving Edition": self.fields["Наименование товара"].get(),
            "VIN:LDP95H962PE310334": "VIN:" + self.fields["VIN"].get(),
            "8703 23 908 9": self.fields["HS код"].get(),
            "21 400,00 USD": self.fields["Общая стоимость"].get(),
            "21 400 USD": self.fields["Общая стоимость"].get(),
            "21 400.": self.fields["Общая стоимость"].get().replace(",", "."),
            "20 000,00 USD": self.fields["Стоимость единицы"].get(),
            "Двадцать одна тысяча четыреста.": "",
            "Twenty one thousand four hundred.": "",
        }

        self.deep_replace_text(doc.paragraphs, replacements)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    self.deep_replace_text(cell.paragraphs, replacements)

        save_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")])
        if save_path:
            doc.save(save_path)
            messagebox.showinfo("Готово", f"Файл сохранён:\n{save_path}")

    def save_template(self):
        data = {label: entry.get() for label, entry in self.fields.items()}
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранено", "Шаблон сохранён.")

    def load_template(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for label, value in data.items():
                if label in self.fields:
                    self.fields[label].delete(0, ctk.END)
                    self.fields[label].insert(0, value)
            messagebox.showinfo("Загружено", "Шаблон успешно загружен.")

if __name__ == "__main__":
    app = WordReplacerApp()
    app.mainloop()