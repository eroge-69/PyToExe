import tkinter as tk
from tkinter import simpledialog
import json
import os
import re


klasor = os.path.dirname(os.path.abspath(__file__))
dosya = os.path.join(klasor, "bilgi.json")

if not os.path.exists(dosya):
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)


with open(dosya, "r", encoding="utf-8") as f:
    bilgiler = json.load(f)
def sohbet_gonder(event=None):
    soru = giris.get().lower().strip()
    if soru:
        sohbet.insert(tk.END, "Sen: " + soru + "\n")
        
 
        if re.fullmatch(r"[\d\s\+\-\*/\(\)]+", soru):
            try:
                cevap = str(eval(soru))
            except:
                cevap = "İşlem hatalı."
        elif soru in bilgiler:
            cevap = bilgiler[soru]
        else:
            cevap = simpledialog.askstring("Botx", f"'{soru}' sorusuna nasıl cevap vermeliyim?")
            if cevap:
                bilgiler[soru] = cevap
                with open(dosya, "w", encoding="utf-8") as f:
                    json.dump(bilgiler, f, ensure_ascii=False, indent=4)
            else:
                cevap = "Anlayamadım."
        
        sohbet.insert(tk.END, "Botx: " + cevap + "\n\n")
        sohbet.see(tk.END)
        giris.delete(0, tk.END)

pencere = tk.Tk()
pencere.title("Botx")
pencere.geometry("500x600")


sohbet = tk.Text(pencere, wrap="word")
sohbet.pack(expand=True, fill="both")
scrollbar = tk.Scrollbar(pencere)
scrollbar.pack(side="right", fill="y")
sohbet.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=sohbet.yview)


giris = tk.Entry(pencere)
giris.pack(fill="x", padx=5, pady=5)
giris.bind("<Return>", sohbet_gonder)


buton = tk.Button(pencere, text="Gönder", command=sohbet_gonder)
buton.pack(pady=5)
sohbet.insert(tk.END, "Botx: Merhaba.\n\n")

pencere.mainloop()
