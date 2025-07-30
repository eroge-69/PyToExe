import tkinter as tk

def buton():
 etiket.delete(0, tk.END) 
 etiket.insert(0, "1")
  

def qbuton():
 etiket.delete(0, tk.END) 
 etiket.insert(0, "2")

def abuton():
 etiket.delete(0, tk.END) 
 etiket.insert(0, "3")
def pbuton():
 etiket.delete(0, tk.END) 
 etiket.insert(0, "4")
pencere = tk.Tk()
pencere.geometry("300x400")
pencere.title("Boş Alan")

# Kullanıcının yazacağı giriş kutusu
etiket = tk.Entry(pencere, font=("Arial", 16))
etiket.pack(pady=10)

buton = tk.Button(pencere, text= "1", command=buton)
buton.pack(pady=10)

qbuton = tk.Button(pencere, text= "2", command=qbuton)
qbuton.pack(pady=10)

abuton = tk.Button(pencere, text= "3", command=abuton)
abuton.pack(pady=10)
pbuton = tk.Button(pencere, text= "4", command=pbuton)
pbuton.pack(pady=10)
pencere.mainloop()
