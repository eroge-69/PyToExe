import pyautogui
import time
import keyboard

button_image = "buton.png"   # Aranacak butonun ekran görüntüsü
click_count = 1              # Her butona kaç kere tıklasın
click_interval = 0.3         # Tıklamalar arası bekleme süresi (sn)

print("⏳ 3 saniye içinde sayfayı hazırla...")
time.sleep(3)

print("🔍 Program başladı. Sol Shift = dur/başlat, ESC = çıkış")

running = True  # Başlangıçta açık

while True:
    # ESC → çıkış
    if keyboard.is_pressed("esc"):
        print("🛑 Program kullanıcı tarafından kapatıldı.")
        break

    # Shift → toggle başlat/durdur
    if keyboard.is_pressed("shift"):
        running = not running
        state = "devam ediyor" if running else "durdu"
        print(f"⏸ Toggle: Click işlemi {state}.")
        time.sleep(0.5)  # tuş tekrarı önlemek için bekleme

    if not running:
        time.sleep(0.2)
        continue

    matches = list(pyautogui.locateAllOnScreen(button_image, confidence=0.8))

    if not matches:
        print("❌ Buton bulunamadı, sayfayı biraz kaydır...")
        time.sleep(1)
        continue

    for match in matches:
        center = pyautogui.center(match)
        for c in range(click_count):
            pyautogui.click(center)
            print(f"✅ Butona tıklandı: {center} ({c+1}. click)")
            time.sleep(click_interval)
