import pdfplumber
import difflib
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import sys
import os

def resource_path(relative_path):
    """Zwraca prawidłową ścieżkę do zasobów w trybie .exe lub .py."""
    try:
        # PyInstaller tworzy folder tymczasowy i przechowuje ścieżkę w _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PDFComparerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Porównywanie plików PDF")
        self.root.geometry("800x600")

        # Ścieżki do plików
        self.pdf_a_path = None
        self.pdf_b_path = None

        # Tworzenie GUI
        self.create_widgets()

    def create_widgets(self):
        # Ramka na wybór plików
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        # Przycisk i etykieta dla pliku A
        self.label_a = tk.Label(self.frame, text="Plik PDF A: Nie wybrano")
        self.label_a.pack()
        self.btn_select_a = tk.Button(self.frame, text="Wybierz plik A", command=self.select_pdf_a)
        self.btn_select_a.pack(pady=5)

        # Przycisk i etykieta dla pliku B
        self.label_b = tk.Label(self.frame, text="Plik PDF B: Nie wybrano")
        self.label_b.pack()
        self.btn_select_b = tk.Button(self.frame, text="Wybierz plik B", command=self.select_pdf_b)
        self.btn_select_b.pack(pady=5)

        # Przycisk do porównania
        self.btn_compare = tk.Button(self.frame, text="Porównaj pliki", command=self.compare_pdfs)
        self.btn_compare.pack(pady=10)

        # Pole tekstowe na wyniki
        self.result_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, height=20, font=("Arial", 10))
        self.result_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def select_pdf_a(self):
        self.pdf_a_path = filedialog.askopenfilename(filetypes=[("Pliki PDF", "*.pdf")])
        if self.pdf_a_path:
            self.label_a.config(text=f"Plik PDF A: {self.pdf_a_path}")

    def select_pdf_b(self):
        self.pdf_b_path = filedialog.askopenfilename(filetypes=[("Pliki PDF", "*.pdf")])
        if self.pdf_b_path:
            self.label_b.config(text=f"Plik PDF B: {self.pdf_b_path}")

    def extract_text_from_pdf(self, pdf_path):
        """Wyodrębnia tekst z pliku PDF i normalizuje go."""
        text = ""
        try:
            # Używamy resource_path do obsługi ścieżek w .exe
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            text = re.sub(r'\s+', ' ', text.strip())
            return text.splitlines()
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas przetwarzania {pdf_path}: {e}")
            return []

    def compare_pdfs(self):
        """Porównuje dwa pliki PDF i wyświetla różnice."""
        if not self.pdf_a_path or not self.pdf_b_path:
            messagebox.showwarning("Ostrzeżenie", "Proszę wybrać oba pliki PDF!")
            return

        # Wyczyść poprzednie wyniki
        self.result_text.delete(1.0, tk.END)

        # Wyodrębnij tekst
        text_a = self.extract_text_from_pdf(self.pdf_a_path)
        text_b = self.extract_text_from_pdf(self.pdf_b_path)

        if not text_a or not text_b:
            messagebox.showerror("Błąd", "Nie udało się wyodrębnić tekstu z jednego lub obu plików!")
            return

        # Porównanie tekstu
        differ = difflib.Differ()
        diff = list(differ.compare(text_a, text_b))

        # Przetwarzanie różnic
        only_in_a = []
        only_in_b = []
        common = []

        for line in diff:
            if line.startswith('- '):
                only_in_a.append(line[2:].strip())
            elif line.startswith('+ '):
                only_in_b.append(line[2:].strip())
            elif line.startswith('  '):
                common.append(line[2:].strip())

        # Wyświetlanie wyników
        self.result_text.insert(tk.END, "=== Różnice między dokumentami ===\n\n")
        
        if only_in_a:
            self.result_text.insert(tk.END, "Tekst obecny tylko w dokumencie A:\n")
            for line in only_in_a:
                self.result_text.insert(tk.END, f"- {line}\n")
        
        if only_in_b:
            self.result_text.insert(tk.END, "\nTekst dodany w dokumencie B:\n")
            for line in only_in_b:
                self.result_text.insert(tk.END, f"+ {line}\n")
        
        if common:
            self.result_text.insert(tk.END, "\nTekst wspólny dla obu dokumentów:\n")
            for line in common:
                self.result_text.insert(tk.END, f"  {line}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFComparerApp(root)
    root.mainloop()