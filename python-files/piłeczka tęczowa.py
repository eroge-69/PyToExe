import tkinter as tk
import colorsys
import time
import pygame 
import os     
import math 
import sys # WAŻNE: Dodany do obsługi ścieżek PyInstallera

# --- Ustawienia fizyczne ---
GRAWITACJA = 0.5                      
WSPOLCZYNNIK_TARCIA_ODBICIOWEGO = 0.8 
CZAS_CYKLU = 20                       
SKALA_SZYBKOSCI = 0.15                
MAX_PREDKOSC = 40                     
PROG_PREDKOSCI_ODBITEJ = 2.0 

# --- Ustawienia Repulsji ---
PROMIEN_REPOLSUJACY = 100 
SILA_ODPYCHANIA = 50      

# --- Ustawienia obiektu ---
ROZMIAR_KOLKA = 60
SZEROKOSC_OBIEKTU = ROZMIAR_KOLKA
WYSOKOSC_OBIEKTU = ROZMIAR_KOLKA

# --- Zmienne globalne stanu ---
x = 50.0 
y = 50.0 
vx = 5.0 
vy = 0.0 

przeciaganie = False
przesuniecie_x = 0 
przesuniecie_y = 0 

kolor_hue = 0.0
kolo = None
canvas = None

ostatni_x_myszy = 0.0
ostatni_y_myszy = 0.0
czas_miedzy_probkami = 0.05 
czy_okno_gotowe = False
dzwiek_odbicia = None
root = None 


# ----------------------------------------------------------------------
# KLUCZOWA ZMIANA: Obsługa Dźwięku ze wsparciem dla PyInstallera
# ----------------------------------------------------------------------

def zaladuj_dzwiek():
    global dzwiek_odbicia
    
    # 1. Określenie ścieżki bazowej (WAŻNE DLA PLIKÓW .EXE)
    if getattr(sys, 'frozen', False):
        # Uruchomione jako .exe, użyj ścieżki tymczasowej PyInstallera
        base_path = sys._MEIPASS
    else:
        # Uruchomione jako zwykły skrypt Pythona
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 2. Sprawdzenie plików
    plik_mp3 = os.path.join(base_path, "sound.mp3")
    plik_wav = os.path.join(base_path, "sound.wav")
    
    nazwa_pliku = None
    if os.path.exists(plik_mp3):
        nazwa_pliku = plik_mp3
    elif os.path.exists(plik_wav):
        nazwa_pliku = plik_wav
    else:
        # print("Nie znaleziono pliku dźwiękowego w żadnym formacie.")
        return False
        
    # 3. Ładowanie Pygame
    try:
        pygame.mixer.init()
        dzwiek_odbicia = pygame.mixer.Sound(nazwa_pliku)
        return True
    except pygame.error:
        # print(f"Błąd ładowania dźwięku Pygame: {e}")
        return False

def odtworz_dzwiek():
    if dzwiek_odbicia:
        dzwiek_odbicia.play()

# ----------------------------------------------------------------------

# --- Funkcje sterujące ---

def generuj_kolor_hex():
    global kolor_hue
    r, g, b = colorsys.hsv_to_rgb(kolor_hue, 1.0, 1.0)
    r_int = int(r * 255)
    g_int = int(g * 255)
    b_int = int(b * 255)
    kolor_hue = (kolor_hue + 0.005) % 1.0
    return f"#{r_int:02x}{g_int:02x}{b_int:02x}"

def rozpocznij_przeciaganie(event):
    global przeciaganie, przesuniecie_x, przesuniecie_y, vx, vy
    global ostatni_x_myszy, ostatni_y_myszy
    
    vx = 0.0
    vy = 0.0
    przeciaganie = True
    
    ostatni_x_myszy = event.x_root
    ostatni_y_myszy = event.y_root
    
    przesuniecie_x = event.x_root - root.winfo_x()
    przesuniecie_y = event.y_root - root.winfo_y()

def przeciagaj_okienko(event):
    global ostatni_x_myszy, ostatni_y_myszy, przesuniecie_x, przesuniecie_y

    if przeciaganie:
        nowy_x = event.x_root - przesuniecie_x
        nowy_y = event.y_root - przesuniecie_y
        
        root.geometry(f"{SZEROKOSC_OBIEKTU}x{WYSOKOSC_OBIEKTU}+{nowy_x}+{nowy_y}")
        
        global x, y
        x = nowy_x
        y = nowy_y
        
        ostatni_x_myszy = event.x_root 
        ostatni_y_myszy = event.y_root


def zakoncz_przeciaganie(event):
    global przeciaganie, vx, vy
    global ostatni_x_myszy, ostatni_y_myszy, czas_miedzy_probkami

    przeciaganie = False

    koncowy_x_myszy = event.x_root
    koncowy_y_myszy = event.y_root
    
    zmiana_x = koncowy_x_myszy - ostatni_x_myszy
    zmiana_y = koncowy_y_myszy - ostatni_y_myszy

    vx = (zmiana_x / czas_miedzy_probkami) * SKALA_SZYBKOSCI
    vy = (zmiana_y / czas_miedzy_probkami) * SKALA_SZYBKOSCI
        
    vx = max(min(vx, MAX_PREDKOSC), -MAX_PREDKOSC)
    vy = max(min(vy, MAX_PREDKOSC), -MAX_PREDKOSC)


def animacja():
    global x, y, vx, vy
    
    szerokosc_ekranu = root.winfo_screenwidth()
    wysokosc_ekranu = root.winfo_screenheight()

    # 1. AKTUALIZACJA KOLORU
    nowy_kolor = generuj_kolor_hex()
    canvas.itemconfig(kolo, fill=nowy_kolor) 
    
    # 2. REPULSJA
    if not przeciaganie and czy_okno_gotowe: 
        try: 
            pozycja_kursora_x = root.winfo_pointerx()
            pozycja_kursora_y = root.winfo_pointery()
        except:
            pozycja_kursora_x = x 
            pozycja_kursora_y = y 

        srodek_x = x + SZEROKOSC_OBIEKTU / 2
        srodek_y = y + WYSOKOSC_OBIEKTU / 2

        dx = srodek_x - pozycja_kursora_x
        dy = srodek_y - pozycja_kursora_y

        dystans = math.sqrt(dx**2 + dy**2) 

        if dystans < PROMIEN_REPOLSUJACY and dystans > 0:
            wspolczynnik_sily = SILA_ODPYCHANIA / (dystans**2) 
            
            sila_x = (dx / dystans) * wspolczynnik_sily
            sila_y = (dy / dystans) * wspolczynnik_sily
            
            vx += sila_x
            vy += sila_y
            
    # --- 3. FIZYKA I ODBICIE OD KRAWĘDZI EKRANU ---
    
    if not przeciaganie:
        
        # Przesunięcie
        vy += GRAWITACJA
        x += vx
        y += vy
        
        odbicie_x = False
        odbicie_y = False
        
        # Poziom (Lewo/Prawo)
        if x < 0 or x + SZEROKOSC_OBIEKTU > szerokosc_ekranu:
            if x < 0: x = 0
            else: x = szerokosc_ekranu - SZEROKOSC_OBIEKTU
            vx *= -WSPOLCZYNNIK_TARCIA_ODBICIOWEGO
            odbicie_x = True 
        
        # Pion (Góra/Dół)
        if y < 0 or y + WYSOKOSC_OBIEKTU > wysokosc_ekranu:
            if y < 0: 
                y = 0
            else: 
                y = wysokosc_ekranu - WYSOKOSC_OBIEKTU
                
            if abs(vy) > PROG_PREDKOSCI_ODBITEJ:
                vy *= -WSPOLCZYNNIK_TARCIA_ODBICIOWEGO
                odbicie_y = True 
            else:
                vy = 0.0
            
            if abs(vx) > 0.01: 
                vx *= 0.98
            else: 
                vx = 0.0
                
        if odbicie_x or odbicie_y:
            odtworz_dzwiek()

        # PRZESUNIĘCIE OKIENKA
        root.geometry(f"{SZEROKOSC_OBIEKTU}x{WYSOKOSC_OBIEKTU}+{int(x)}+{int(y)}")

    root.after(CZAS_CYKLU, animacja)


# --- Główna część programu ---
root = tk.Tk()
root.title("Antygrawitacyjne Kółko") 

# 0. INICJALIZACJA DŹWIĘKU
zaladuj_dzwiek()

def aktywuj_repulsje():
    global czy_okno_gotowe
    czy_okno_gotowe = True

# 1. Ustawienia dla Okienka w Kształcie Kółka
root.wm_attributes('-transparentcolor', '#000000') 
root.overrideredirect(True)
root.attributes('-topmost', True) 

# 2. Rysowanie Kółka 
canvas = tk.Canvas(root, width=ROZMIAR_KOLKA, height=ROZMIAR_KOLKA, 
                   highlightthickness=0, bg='#000000') 
canvas.pack()

kolo = canvas.create_oval(0, 0, ROZMIAR_KOLKA, ROZMIAR_KOLKA, fill="red", outline="") 

# 3. Przywiązanie zdarzeń myszy 
canvas.bind('<Button-1>', rozpocznij_przeciaganie)
canvas.bind('<B1-Motion>', przeciagaj_okienko)
canvas.bind('<ButtonRelease-1>', zakoncz_przeciaganie)

# 4. Uruchomienie pętli
root.after_idle(aktywuj_repulsje) 

animacja()
root.mainloop()

try:
    pygame.quit()
except:
    pass
