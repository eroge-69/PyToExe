import tkinter as tk

def gonder():
    kullanici = girdi.get()  # Kullanıcının yazdığı metin
    girdi.delete(0, tk.END)  # Girdi kutusunu temizle
    
    if kullanici.lower() == "çık":
        cevap = "SecAI: Görüşürüz!"
        pencere.destroy()  # Pencereyi kapat
    elif "nasılsın" in kullanici.lower():
        cevap = "SecAI: Ben iyiyim, sen nasılsın?"
    elif "adın ne" in kullanici.lower():
        cevap = "SecAI: Ben SecAI'yim. Senin adın ne?"
    elif "selamun aleykum" in kullanici.lower():
        cevap = "SecAI: Aleykum selam"
    elif "seni kim yaptı" in kullanici.lower():
       cevap = "SecAI: Beni Seckin yaptı."   
    elif "s.a" in kullanici.lower():
        cevap = "SecAI: a.s"
    elif "kendini tanıt" in kullanici.lower():
        cevap = "SecAI: ben basit bir Aİ konuşma botuyum."
    elif "reis" in kullanici.lower():
        cevap = "SecAI: efendim reis."
    elif "malmısın" in kullanici.lower():
        cevap = "SecAI: Ben malsam sen nesin?."   
    elif "selam" in kullanici.lower():
        cevap = "SecAI: Selam!"
    
    else:
        cevap = "SecAI: Ben basit bir Aİ'yim belirli sorulara cevap verebilirim."
 
    sohbet.config(state="normal")
    sohbet.insert(tk.END, f"Sen: {kullanici}\n{cevap}\n\n")
    sohbet.config(state="disabled")
    sohbet.see(tk.END)

# Pencere oluştur
pencere = tk.Tk()
pencere.title("SecAI v0.1")
ikon = tk.PhotoImage(file="secai.png")
pencere.iconphoto(False, ikon)

# Sohbet alanı
sohbet = tk.Text(pencere, height=20, width=50, state="disabled")
sohbet.pack()

# Kullanıcı girdi kutusu
girdi = tk.Entry(pencere, width=50)
girdi.pack()

# Gönder butonu
buton = tk.Button(pencere, text="Gönder", command=gonder)
buton.pack()

pencere.mainloop()
