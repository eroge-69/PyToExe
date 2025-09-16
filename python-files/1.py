import docx
import pymorphy2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Инициализация словаря замен
REPLACEMENTS = {
    "стол": ["стул", "кресло", "табурет"],
    "машина": ["автомобиль", "тачка", "транспорт"],
}

morph = pymorphy2.MorphAnalyzer()

def get_word_form(word, replacement):
    parsed_word = morph.parse(word)[0] if morph.parse(word) else None
    parsed_repl = morph.parse(replacement)[0] if morph.parse(replacement) else None
    if not parsed_word or not parsed_repl:
        return replacement
    form = parsed_repl.inflect(parsed_word.tag.grammemes)
    return form.word if form else replacement

def extract_replacements(doc):
    replacements = []
    for para in doc.paragraphs:
        for run in para.runs:
            words = run.text.split()
            for i, w in enumerate(words):
                base = morph.parse(w.lower())[0].normal_form
                if base in REPLACEMENTS:
                    start = max(0, i-2)
                    end = min(len(words), i+3)
                    context = " ".join(words[start:end])
                    if start > 0:
                        context = "..." + context
                    if end < len(words):
                        context += "..."
                    replacements.append((w, [get_word_form(w, opt) for opt in REPLACEMENTS[base]], context, run, i))
    return replacements

def apply_replacements(replacements, chosen_replacements):
    for orig_word, options, context, run, index in replacements:
        chosen = chosen_replacements.get((run, index), orig_word)
        words = run.text.split()
        words[index] = chosen
        run.text = " ".join(words)

def process_docx(input_file, output_file):
    try:
        doc = docx.Document(input_file)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")
        return

    replacements = extract_replacements(doc)
    if not replacements:
        messagebox.showinfo("Инфо", "Замен не найдено.")
        return

    root = tk.Tk()
    root.title("Выбор замен")
    root.geometry("800x400")

    tree = ttk.Treeview(root, columns=("orig", "context", "choice"), show="headings")
    tree.heading("orig", text="Исходное слово")
    tree.heading("context", text="Контекст")
    tree.heading("choice", text="Замена")
    tree.column("orig", width=150)
    tree.column("context", width=400)
    tree.column("choice", width=200)
    tree.pack(fill=tk.BOTH, expand=True)

    chosen_replacements = {}

    def on_select(event):
        for item in tree.selection():
            idx = int(item)
            orig_word, options, context, run, word_idx = replacements[idx]
            popup = tk.Toplevel(root)
            popup.title("Выбор замены")

            tk.Label(popup, text=f"Слово: {orig_word}\nКонтекст: {context}").pack(pady=10)

            combo = ttk.Combobox(popup, values=[orig_word] + options, state="readonly")
            combo.current(0)
            combo.pack(pady=5)

            def save_choice():
                choice = combo.get()
                chosen_replacements[(run, word_idx)] = choice
                tree.set(item, column="choice", value=choice)
                popup.destroy()

            tk.Button(popup, text="OK", command=save_choice).pack(pady=10)

    tree.bind("<Double-1>", on_select)

    for i, (orig_word, options, context, run, word_idx) in enumerate(replacements):
        tree.insert("", "end", iid=str(i), values=(orig_word, context, orig_word))

    def save_and_close():
        apply_replacements(replacements, chosen_replacements)
        try:
            doc.save(output_file)
            messagebox.showinfo("Готово", f"Файл сохранён как {output_file}")
            root.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def on_closing():
        if messagebox.askokcancel("Выход", "Вы хотите выйти без сохранения?"):
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    tk.Button(root, text="Сохранить", command=save_and_close).pack(pady=10)
    root.mainloop()

def add_custom_replacements():
    def save_replacements():
        word = entry_word.get().strip()
        replacements = entry_replacements.get().strip().split(",")
        if word and replacements:
            REPLACEMENTS[word.lower()] = [r.strip() for r in replacements if r.strip()]
            messagebox.showinfo("Успех", f"Добавлены замены для слова '{word}': {replacements}")
        else:
            messagebox.showwarning("Ошибка", "Введите слово и список замен через запятую.")
        custom_window.destroy()

    custom_window = tk.Toplevel()
    custom_window.title("Добавить замены")
    custom_window.geometry("400x200")

    tk.Label(custom_window, text="Введите слово для замены:").pack(pady=10)
    entry_word = tk.Entry(custom_window, width=40)
    entry_word.pack(pady=5)

    tk.Label(custom_window, text="Введите замены через запятую (например: стул, кресло):").pack(pady=10)
    entry_replacements = tk.Entry(custom_window, width=40)
    entry_replacements.pack(pady=5)

    tk.Button(custom_window, text="Сохранить", command=save_replacements).pack(pady=20)

def main():
    root = tk.Tk()
    root.withdraw()

    # Добавление пользовательских замен перед выбором файла
    add_custom_replacements()
    root.deiconify()

    input_file = filedialog.askopenfilename(
        title="Выберите документ Word",
        filetypes=[("Word файлы", "*.docx")]
    )

    if not input_file:
        messagebox.showwarning("Отмена", "Файл не выбран.")
        return

    output_file = filedialog.asksaveasfilename(
        title="Сохранить документ как",
        defaultextension=".docx",
        filetypes=[("Word файлы", "*.docx")]
    )

    if not output_file:
        messagebox.showwarning("Отмена", "Файл не сохранён.")
        return

    process_docx(input_file, output_file)

if __name__ == "__main__":
    main()