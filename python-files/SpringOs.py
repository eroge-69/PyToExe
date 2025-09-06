import tkinter as tk

def windows_benzeri_pencere_olustur():
    # Ana pencereyi oluştur
    pencere = tk.Tk()
    pencere.title("Spring OS")
    pencere.geometry("1024x768")
    
    # Pencerenin boyutunu kullanıcı tarafından değiştirilemez yap
    pencere.resizable(False, False)
    
    # Görev çubuğu için alt kısımda bir çerçeve oluştur
    gorev_cubugu = tk.Frame(pencere, bg="#1E1E1E", height=40)
    gorev_cubugu.pack(side="bottom", fill="x")
    
    # Masaüstü için ana çerçeveyi oluştur
    masaustu = tk.Frame(pencere, bg="#2c2c2c")
    masaustu.pack(expand=True, fill="both")
    
    # Başlat butonu (örnek)
    baslat_butonu = tk.Button(gorev_cubugu, text="Başlat", bg="#1e1e1e", fg="white", bd=0, relief="flat", font=("Arial", 10))
    baslat_butonu.pack(side="left", padx=5)
    
    # Uygulamayı çalıştır
    pencere.mainloop()

# Kodu başlat
if __name__ == "__main__":
    windows_benzeri_pencere_olustur()
