import time
import webbrowser
import random

def rickroll_programi():
    print("🎮 Python Öğrenme Simülatörüne Hoş Geldiniz!")
    time.sleep(2)
    print("\nBu program Python programlama becerilerinizi test edecek...")
    time.sleep(2)
    
    # Sahte bir "yükleniyor" efekti
    print("\nSistem hazırlanıyor:", end="")
    for i in range(5):
        print("█", end="", flush=True)
        time.sleep(0.5)
    print(" Tamamlandı!")
    
    time.sleep(1)
    print("\n🔍 İlk test: Matematiksel işlemler")
    time.sleep(1)
    
    # Basit matematik sorusu
    sayi1 = random.randint(1, 10)
    sayi2 = random.randint(1, 10)
    
    cevap = input(f"\n{sayi1} × {sayi2} = ? ")
    
    try:
        if int(cevap) == sayi1 * sayi2:
            print("✅ Doğru! Çok iyi gidiyorsun!")
        else:
            print("❌ Yanlış, ama önemli değil...")
    except:
        print("⚠️ Geçersiz giriş, devam ediyoruz...")
    
    time.sleep(2)
    print("\n🎯 İkinci test: String işlemleri")
    time.sleep(1)
    
    kelime = "PYTHON"
    print(f"\n'{kelime}' kelimesinin tersten yazılışı nedir?")
    
    # Kullanıcı cevap versin diye bekleyelim
    input("Cevabınızı yazıp ENTER'a basın: ")
    
    print("🤔 Değerlendiriliyor...")
    time.sleep(3)
    
    # Sürpriz hazırlığı
    print("\n" + "="*50)
    print("🎉 TEBRİKLER! Tüm testleri geçtiniz!")
    print("Ödülünüzü açıyorum...")
    print("="*50)
    
    time.sleep(3)
    
    # Geri sayım
    for i in range(5, 0, -1):
        print(f"⏰ {i}...")
        time.sleep(1)
    
    # RICKROLL!
    print("\n🎵 SÜRPRİZ! 🎵")
    print("Rick Astley - Never Gonna Give You Up")
    print("Bu bir RICKROLL! 😄")
    
    # Rickroll videosunu aç
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    time.sleep(2)
    print("\n" + "🎭" * 25)
    print("Never gonna give you up, never gonna let you down...")
    print("🎭" * 25)

# Programı çalıştır
if __name__ == "__main__":
    rickroll_programi()