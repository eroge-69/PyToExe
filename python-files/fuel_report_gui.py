
import fitz
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def extract_fuel_data(pdf_path):
    doc = fitz.open(pdf_path)
    result = {}
    current_name = ""

    for page in doc:
        text = page.get_text()
        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            if line.startswith("Э/к"):
                parts = line.split()
                if len(parts) >= 3:
                    current_name = " ".join(parts[2:])
                    if current_name not in result:
                        result[current_name] = []
                continue

            tokens = line.split()
            if len(tokens) >= 7 and tokens[0].count('-') == 1:
                try:
                    date = tokens[0]
                    liters = float(tokens[5].replace(",", "."))
                    if current_name:
                        result[current_name].append((date, liters))
                except:
                    continue

    return result

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Выберите PDF-файл",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not file_path:
        return

    try:
        data = extract_fuel_data(file_path)
        if not data:
            messagebox.showinfo("Результат", "Не удалось найти данные в файле.")
            return

        report_lines = ["Отчёт по заправкам:\n"]
        for name, entries in data.items():
            report_lines.append(f"Фамилия: {name}")
            report_lines.append("Дата       | Объем (л)")
            report_lines.append("-----------+-----------")
            for date, liters in entries:
                report_lines.append(f"{date}   | {liters:.2f}")
            report_lines.append("")

        report_text = "\n".join(report_lines)
        out_path = os.path.splitext(file_path)[0] + "_отчёт.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        messagebox.showinfo("Готово", f"Отчёт сохранён:
{out_path}")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    main()
