import tkinter as tk
from tkinter import filedialog, messagebox
from docx import Document
import pyperclip  # Увери се, че си инсталирал: pip install pyperclip

extracted_data = []  # Глобална променлива за съхранение на данните

def extract_data(file_path):
    target_columns = ["код на стоката", "колич.", "ед.цена"]
    document = Document(file_path)
    data = []

    for table in document.tables:
        header = [cell.text.strip().lower() for cell in table.rows[0].cells]
        indexes = [header.index(col) for col in target_columns if col in header]

        if len(indexes) == len(target_columns):
            for row in table.rows[1:]:
                values = [row.cells[i].text.strip() for i in indexes]
                data.append(values)
            break

    return data

def choose_file():
    global extracted_data
    file_path = filedialog.askopenfilename(
        title="Избери .docx файл",
        filetypes=[("Word Files", "*.docx")]
    )
    if file_path:
        try:
            extracted_data = extract_data(file_path)
            if extracted_data:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "Код на стоката | Колич. | Ед.цена\n")
                result_text.insert(tk.END, "-"*40 + "\n")
                for row in extracted_data:
                    result_text.insert(tk.END, " | ".join(row) + "\n")
            else:
                messagebox.showinfo("Резултат", "Не бяха намерени съответстващи данни.")
        except Exception as e:
            messagebox.showerror("Грешка", f"Възникна проблем: {e}")
def copy_to_clipboard():
    if not extracted_data:
        messagebox.showwarning("Внимание", "Няма данни за копиране.")
        return
    processed = []
    for row in extracted_data:
        code, qty, price = row
        price = price.replace("лв.", "").strip()
        processed.append(f"{code}, {qty}, {price}, лв.")  # добавена запетая и интервал преди лв.
    pyperclip.copy("\n".join(processed))
    messagebox.showinfo("Готово", "Данните са копирани в клипборда!")


# Създаване на GUI
root = tk.Tk()
root.title("Извличане на данни от Word фактури")

btn_choose = tk.Button(root, text="Избери документ", command=choose_file)
btn_choose.pack(pady=10)

btn_copy = tk.Button(root, text="Копирай в клипборда (CSV)", command=copy_to_clipboard)
btn_copy.pack(pady=5)

result_text = tk.Text(root, width=60, height=20)
result_text.pack(padx=10, pady=10)

root.mainloop()
