import pyautogui
import time
import sys

def move_mouse_afk(interval_seconds=10, move_pixels=1):
    """
    Fareyi belirli aralıklarla milimlik olarak hareket ettirir.
    AFK kalmayı önler.

    Args:
        interval_seconds (int): Fare hareketleri arasındaki bekleme süresi (saniye).
        move_pixels (int): Farenin her seferinde hareket edeceği piksel miktarı.
    """
    print(f"Fareyi her {interval_seconds} saniyede bir {move_pixels} piksel hareket ettireceğim.")
    print("Programı durdurmak için 'Ctrl + C' tuşlarına basın.")

    try:
        while True:
            # Farenin mevcut konumunu al
            current_x, current_y = pyautogui.position()

            # Fareyi mevcut konumdan belirtilen piksel kadar sağa hareket ettir
            pyautogui.moveTo(current_x + move_pixels, current_y, duration=0.25)
            # Kısa bir bekleme
            time.sleep(0.5)
            # Fareyi başlangıç konumuna geri getir (veya sola hareket ettir)
            pyautogui.moveTo(current_x, current_y, duration=0.25)

            # Belirtilen aralık kadar bekle
            time.sleep(interval_seconds - 1) # Yukarıdaki hareketler 1 saniye kadar sürdüğü için düşüyoruz

    except KeyboardInterrupt:
        print("\nProgram sonlandırılıyor...")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Parametreleri isteğe göre değiştirebilirsin
    # Örneğin: her 5 saniyede bir 2 piksel hareket ettir
    move_mouse_afk(interval_seconds=5, move_pixels=2)