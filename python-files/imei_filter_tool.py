
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_registered_imeis(input_text):
    imeis = []
    blocks = input_text.split("IMEI\n")
    for block in blocks[1:]:
        lines = block.strip().splitlines()
        imei = lines[0].strip()
        try:
            durum_index = lines.index("Durum")
            durum_value = lines[durum_index + 1].strip()
            if "KAYITLI" in durum_value:
                imeis.append(imei)
        except ValueError:
            continue  # Skip block if "Durum" not found
    return imeis

def select_file():
    file_path = filedialog.askopenfilename(title="اختر ملف نتائج IMEI", filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()

    filtered_imeis = extract_registered_imeis(data)
    if not filtered_imeis:
        messagebox.showinfo("النتيجة", "لم يتم العثور على أي IMEI بحالة 'KAYITLI'")
        return

    output_path = Path(file_path).with_name("kayitli_imeis.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        for imei in filtered_imeis:
            f.write(imei + "\n")

    messagebox.showinfo("تم", f"تم حفظ {len(filtered_imeis)} IMEI في: {output_path}")

root = tk.Tk()
root.title("فلترة IMEI")
root.geometry("300x150")

btn = tk.Button(root, text="اختيار ملف نتائج IMEI", command=select_file, font=("Arial", 12))
btn.pack(expand=True)

root.mainloop()
