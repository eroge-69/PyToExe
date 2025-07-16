import tkinter as tk
from tkinter import messagebox, filedialog

def sort_text(input_text):
    lines = input_text.strip().splitlines()
    lines = [line.strip() for line in lines if line.strip()]

    parsed = []
    for line in lines:
        parts = line.split(maxsplit=2)
        kol1 = parts[0] if len(parts) > 0 else ""
        kol2_raw = parts[1] if len(parts) > 1 else ""
        kol2 = kol2_raw.replace(",", ".")
        kol3 = parts[2].strip().lower() if len(parts) > 2 else ""

        try:
            angka = float(kol2)
            is_float = '.' in kol2
        except ValueError:
            angka = float('-inf')
            is_float = False

        if kol3 == "":
            kol3_sort = "zza" if is_float else "zzz"
        else:
            kol3_sort = kol3

        parsed.append((kol3_sort, -angka, line))

    parsed.sort()
    return "\n".join([x[2] for x in parsed])

def create_app():
    def sort_and_display():
        input_data = text_input.get("1.0", tk.END)
        if not input_data.strip():
            messagebox.showwarning("Peringatan", "Masukkan data terlebih dahulu.")
            return
        result = sort_text(input_data)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, result)

    def save_result():
        result = text_output.get("1.0", tk.END).strip()
        if not result:
            messagebox.showwarning("Peringatan", "Tidak ada hasil untuk disimpan.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result)
            messagebox.showinfo("Berhasil", f"Hasil disimpan ke:\n{file_path}")

    root = tk.Tk()
    root.title("Sorter Kolom")

    tk.Label(root, text="Masukkan Data:").pack()
    text_input = tk.Text(root, height=12, width=60)
    text_input.pack()

    tk.Button(root, text="Urutkan", command=sort_and_display).pack(pady=5)

    tk.Label(root, text="Hasil:").pack()
    text_output = tk.Text(root, height=12, width=60)
    text_output.pack()

    tk.Button(root, text="Simpan Hasil ke File", command=save_result).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_app()
