import pyautogui
import time

# Ustawienia
wiadomosc = "Wiadomość"
start = 1
ilosc_powtorzen = 10
opoznienie = 1.5  # czas między wysyłaniem kolejnych wiadomości (w sekundach)

# Czas na przełączenie się do okna czatu
print("Masz 5 sekund, aby przełączyć się do okna czatu...")
time.sleep(5)

# Pętla wysyłająca wiadomości
for i in range(start, start + ilosc_powtorzen):
    tekst = f"{wiadomosc} {i}"
    pyautogui.typewrite(tekst)
    pyautogui.press("enter")
    time.sleep(opoznienie)

print("Wysyłanie zakończone.")