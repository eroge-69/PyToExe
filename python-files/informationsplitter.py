import tkinter as tk
from tkinter import ttk

def process_and_copy():
    # 1. Girdi metnini al
    raw_text = txt_input.get("1.0", tk.END)
    
    # 2. Dönüşümleri uygula
    transformed = (
        raw_text
        .replace("(", "")
        .replace(")", "")
        .replace("*", "-")
        .replace("ç", ".")
    )
    
    # 3. Boşluklara göre alt satıra ayır
    lines = transformed.split()
    result = "\n".join(lines)
    
    # 4. Sonucu ekrana yaz ve panoya kopyala
    txt_output.config(state="normal")
    txt_output.delete("1.0", tk.END)
    txt_output.insert(tk.END, result)
    txt_output.config(state="disabled")
    
    root.clipboard_clear()
    root.clipboard_append(result)
    lbl_status.config(text="İşlem tamamlandı! Panoya kopyalandı.", foreground="green")

# Ana pencere
root = tk.Tk()
root.title("Metin Dönüştürücü")
root.geometry("500x400")

# Girdi etiketi ve metin kutusu
ttk.Label(root, text="Girdi Metni:").pack(anchor="w", padx=10, pady=(10, 0))
txt_input = tk.Text(root, height=8, wrap="word")
txt_input.pack(fill="both", expand=True, padx=10)

# Düğme
btn_process = ttk.Button(root, text="Dönüştür ve Kopyala", command=process_and_copy)
btn_process.pack(pady=10)

# Çıktı etiketi ve metin kutusu (salt okunur)
ttk.Label(root, text="Çıktı:").pack(anchor="w", padx=10)
txt_output = tk.Text(root, height=8, wrap="word", state="disabled")
txt_output.pack(fill="both", expand=True, padx=10)

# Durum çubuğu
lbl_status = ttk.Label(root, text="")
lbl_status.pack(pady=(5, 10))

root.mainloop()
