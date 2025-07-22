import pyautogui
import time

# Kullanıcıya bilgi ver ve Discord'a geçiş için süre tanı
print("Script 10 saniye içinde başlayacak. Lütfen bu sürede Discord'a geçiş yapın ve mesaj yazma kutusuna tıklayarak seçili hale getirin.")

# Scriptin başlaması için 10 saniye bekle
# Bu, Discord uygulamasına geçip mesaj kutusuna odaklanmanız için size zaman tanır.
time.sleep(10)

# "oe" yazısını 30 kez gönder
for i in range(30):
    pyautogui.write("oe")  # "oe" yazısını klavye ile yazar
    pyautogui.press("enter")  # Enter tuşuna basarak mesajı gönderir
    time.sleep(0.1)  # Her mesaj arasında 0.1 saniye (100 milisaniye) bekleme
                     # Bu, Discord'un "çok hızlı yazıyorsun" uyarılarını önlemeye yardımcı olur.

print("İşlem tamamlandı. 'oe' 30 kez gönderildi.")