import pygame
import sys
import time

# Emojiler
EMOJIS = {
    "çoban": "🧔",
    "koyun": "🐑",
    "kurt": "🐺",
    "lahana": "🥬"
}

# Renkler
WHITE = (255, 255, 255)
BLUE = (100, 149, 237)
BLACK = (0, 0, 0)

# Pygame başlat
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Çoban, Koyun, Kurt, Lahana")
font = pygame.font.SysFont("segoeuisymbol", 60)
small_font = pygame.font.SysFont("arial", 24)

clock = pygame.time.Clock()

# Başlangıç durumu
sol = ["koyun", "kurt", "lahana"]
sag = []
boat_side = "sol"
coban = "çoban"
yaninda = None
gecis_yapiliyor = False

def yazdir_yanit(text):
    label = small_font.render(text, True, BLACK)
    screen.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT - 40))

def ciz():
    screen.fill(BLUE)

    # Sol ve sağ kıyı
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH//2 - 50, HEIGHT))
    pygame.draw.rect(screen, WHITE, (WIDTH//2 + 50, 0, WIDTH//2 - 50, HEIGHT))

    # Sandal
    boat_x = 250 if boat_side == "sol" else 500
    pygame.draw.rect(screen, (139,69,19), (boat_x, 250, 100, 60))

    # Sandaldaki çoban
    coban_label = font.render(EMOJIS[coban], True, BLACK)
    screen.blit(coban_label, (boat_x + 10, 250))

    # Sandaldaki nesne
    if yaninda:
        emoji = font.render(EMOJIS[yaninda], True, BLACK)
        screen.blit(emoji, (boat_x + 50, 250))

    # Sol kıyıdaki nesneler
    for i, nesne in enumerate(sol):
        emoji = font.render(EMOJIS[nesne], True, BLACK)
        screen.blit(emoji, (50, 50 + i * 80))

    # Sağ kıyıdaki nesneler
    for i, nesne in enumerate(sag):
        emoji = font.render(EMOJIS[nesne], True, BLACK)
        screen.blit(emoji, (WIDTH - 100, 50 + i * 80))

def kontrol_et():
    # Çoban karşıdaysa diğer tarafı kontrol et
    diger = sol if boat_side == "sag" else sag
    if "koyun" in diger and "kurt" in diger:
        return "🐺 Kurt koyunu yedi! Kaybettin."
    if "koyun" in diger and "lahana" in diger:
        return "🐑 Koyun lahanayı yedi! Kaybettin."
    return None

def kazanma_kontrol():
    return len(sag) == 3

def gecir(nesne):
    global yaninda, boat_side, gecis_yapiliyor
    gecis_yapiliyor = True

    # Nesneyi al
    if nesne and nesne in (sol if boat_side == "sol" else sag):
        (sol if boat_side == "sol" else sag).remove(nesne)
        yaninda = nesne
    else:
        yaninda = None

    for _ in range(60):  # küçük animasyon efekti
        ciz()
        pygame.display.flip()
        clock.tick(60)

    # Taraf değiştir
    boat_side = "sag" if boat_side == "sol" else "sol"

    # Nesneyi bırak
    if yaninda:
        (sol if boat_side == "sol" else sag).append(yaninda)
        yaninda = None

    gecis_yapiliyor = False

def buton_yap(text, x, y, w, h):
    pygame.draw.rect(screen, (200, 200, 200), (x, y, w, h))
    label = small_font.render(text, True, BLACK)
    screen.blit(label, (x + w//2 - label.get_width()//2, y + h//2 - 10))
    return pygame.Rect(x, y, w, h)

def oyun():
    global yaninda
    while True:
        ciz()

        # Butonlar
        btns = []
        if not gecis_yapiliyor and boat_side == "sol":
            for i, n in enumerate(["koyun", "kurt", "lahana", "hiçbir şey"]):
                btn = buton_yap(n, 50, HEIGHT - 150 + i*35, 120, 30)
                btns.append((btn, n))
        elif not gecis_yapiliyor and boat_side == "sag":
            for i, n in enumerate(["koyun", "kurt", "lahana", "hiçbir şey"]):
                btn = buton_yap(n, WIDTH - 170, HEIGHT - 150 + i*35, 120, 30)
                btns.append((btn, n))

        mesaj = kontrol_et()
        if mesaj:
            yazdir_yanit(mesaj)
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()

        if kazanma_kontrol():
            yazdir_yanit("🎉 Tebrikler! Hepsini karşıya geçirdin.")
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and not gecis_yapiliyor:
                for btn, isim in btns:
                    if btn.collidepoint(event.pos):
                        if isim == "hiçbir şey":
                            gecir(None)
                        else:
                            gecir(isim)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    oyun()
