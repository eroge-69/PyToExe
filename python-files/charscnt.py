import tkinter as tk
from tkinter import messagebox

def count_characters(text):
    total_chars = len(text)
    cyrillic_count = sum(1 for ch in text if '�' <= ch <= '�' or ch in '����������')
    latin_count = sum(1 for ch in text if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z'))
    digits_count = sum(1 for ch in text if ch.isdigit())
    spaces_count = sum(1 for ch in text if ch.isspace())
    
    return {
        "������ �������": total_chars,
        "��������": cyrillic_count,
        "��������": latin_count,
        "�����": digits_count,
        "������": spaces_count
    }

def on_count():
    text = text_input.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("�����", "���� �����, ������ ����� � ����.")
        return
    
    counts = count_characters(text)
    result_text = "\n".join(f"{k}: {v}" for k, v in counts.items())
    result_label.config(text=result_text)

root = tk.Tk()
root.title("ϳ�������� �������")

tk.Label(root, text="������ ��� ������� ����� �����:").pack(pady=5)

text_input = tk.Text(root, width=60, height=15)
text_input.pack(padx=10)

count_button = tk.Button(root, text="���������� �������", command=on_count)
count_button.pack(pady=10)

result_label = tk.Label(root, text="", justify=tk.LEFT, font=("Arial", 12))
result_label.pack(padx=10, pady=10)

root.mainloop()
