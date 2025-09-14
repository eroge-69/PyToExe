import pyautogui
import time

# Ayarlar
WAIT_MENU = 0.5       # Sağ tık menüsünün açılması için bekleme
WAIT_DELETE = 0.5     # Delete menüsünün tıklanması için bekleme
WAIT_CONFIRM = 0.5    # Delete onayının tıklanması için bekleme
WAIT_SCROLL = 1       # Scroll sonrası sayfanın yüklenmesi için bekleme
SCROLL_AMOUNT = -300  # Her scroll adımı (negatif = aşağı kaydır)

# Delete menü ve onay koordinatları (Slack penceresine göre ayarla)
DELETE_MENU_POS = (520, 320)   # Sağ tık menüsündeki Delete seçeneği
CONFIRM_POS = (800, 500)       # Delete onay butonu

# Mesajın tahmini X koordinatı (tüm mesajlar aynı X üzerinde varsayılır)
MESSAGE_X = 500

# Tahmini Y koordinat aralığı (görünür mesajlar için)
START_Y = 300
END_Y = 700
STEP_Y = 100  # Mesajlar arası tahmini dikey mesafe

def delete_visible_messages():
    y_positions = list(range(START_Y, END_Y+1, STEP_Y))
    for y in y_positions:
        # 1️⃣ Mesajın üzerine sağ tık
        pyautogui.moveTo(MESSAGE_X, y, duration=0.2)
        pyautogui.click(button='right')
        time.sleep(WAIT_MENU)

        # 2️⃣ Delete menüsünü tıkla
        pyautogui.moveTo(DELETE_MENU_POS[0], DELETE_MENU_POS[1], duration=0.2)
        pyautogui.click()
        time.sleep(WAIT_DELETE)

        # 3️⃣ Onay Delete tıkla
        pyautogui.moveTo(CONFIRM_POS[0], CONFIRM_POS[1], duration=0.2)
        pyautogui.click()
        time.sleep(WAIT_CONFIRM)

        print(f"Deleted message at Y={y}")

def scroll_down():
    pyautogui.scroll(SCROLL_AMOUNT)
    time.sleep(WAIT_SCROLL)

# Ana döngü: Kanalın tüm mesajları boyunca
while True:
    delete_visible_messages()
    scroll_down()
