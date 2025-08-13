import pygame
import sys
import random

# --- Ustawienia Gry ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Kolory (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_ROAD = (50, 150, 50)  # Kolor dróg
BLUE_TRUCK = (0, 0, 200)  # Kolor ciężarówki
RED_CARGO = (200, 0, 0)  # Kolor punktów ładunku
GRAY_CITY = (150, 150, 150)  # Kolor miast
YELLOW_TEXT = (255, 255, 0)  # Kolor tekstu UI

# --- Definicja Miast i Dróg ---
# Miasta: (nazwa, x, y)
CITIES = {
    "Warszawa": (150, 100),
    "Kraków": (150, 450),
    "Gdańsk": (450, 50),
    "Poznań": (450, 300),
    "Wrocław": (450, 550),
    "Łódź": (750, 300),
    "Lublin": (750, 100),
    "Katowice": (750, 550)
}

# Drogi: (miasto1, miasto2, dystans_w_jednostkach_gry)
# Dystans jest przykładowy, w prawdziwej grze byłby liczony z koordynat
ROADS = [
    ("Warszawa", "Gdańsk", 300),
    ("Warszawa", "Poznań", 250),
    ("Warszawa", "Łódź", 150),
    ("Warszawa", "Lublin", 200),
    ("Kraków", "Wrocław", 250),
    ("Kraków", "Katowice", 100),
    ("Kraków", "Łódź", 200),
    ("Gdańsk", "Poznań", 200),
    ("Poznań", "Wrocław", 150),
    ("Wrocław", "Katowice", 150),
    ("Łódź", "Katowice", 180),
    ("Lublin", "Warszawa", 200),  # Dodane, aby zamknąć sieć
]


# --- Klasa Ciężarówki ---
class Truck(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([40, 20])
        self.image.fill(BLUE_TRUCK)
        self.rect = self.image.get_rect()
        self.rect.center = CITIES["Warszawa"]  # Start w Warszawie
        self.speed = 2  # Prędkość ruchu ciężarówki
        self.fuel = 5000  # Paliwo początkowe
        self.max_fuel = 5000
        self.money = 1000  # Pieniądze początkowe
        self.fuel_consumption_rate = 0.5  # Zużycie paliwa na jednostkę ruchu

        self.has_cargo = False
        self.current_cargo = None  # {'from': city, 'to': city, 'reward': amount, 'name': 'ładunek'}

    def update(self, target_pos=None):
        if self.fuel <= 0:
            return  # Nie można się ruszać bez paliwa

        if target_pos:
            # Proste poruszanie się do celu
            dx = target_pos[0] - self.rect.centerx
            dy = target_pos[1] - self.rect.centery
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist > self.speed:
                self.rect.centerx += dx / dist * self.speed
                self.rect.centery += dy / dist * self.speed
                self.fuel -= self.fuel_consumption_rate
            else:
                self.rect.center = target_pos  # Dotarł do celu
                self.fuel -= self.fuel_consumption_rate * (dist / self.speed)  # Reszta paliwa
                return True  # Oznacza dotarcie do celu
        return False

    def pickup_cargo(self, cargo):
        self.has_cargo = True
        self.current_cargo = cargo
        print(f"Pobrano ładunek: {cargo['name']} z {cargo['from']} do {cargo['to']}")

    def deliver_cargo(self):
        if self.has_cargo:
            reward = self.current_cargo['reward']
            self.money += reward
            print(f"Dostarczono ładunek! Zarobiono {reward} zł. Całość: {self.money} zł")
            self.has_cargo = False
            self.current_cargo = None
            return True
        return False

    def refill_fuel(self, amount):
        cost = amount * 1  # 1 zł za jednostkę paliwa
        if self.money >= cost:
            self.fuel = min(self.max_fuel, self.fuel + amount)
            self.money -= cost
            print(f"Zatankowano {amount} jednostek paliwa za {cost} zł. Paliwo: {self.fuel}, Pieniądze: {self.money}")
            return True
        else:
            print("Za mało pieniędzy na paliwo!")
            return False


# --- Funkcje Gry ---
def draw_map(screen):
    # Rysuj drogi
    for c1_name, c2_name, _ in ROADS:
        c1_pos = CITIES[c1_name]
        c2_pos = CITIES[c2_name]
        pygame.draw.line(screen, GREEN_ROAD, c1_pos, c2_pos, 5)

    # Rysuj miasta
    for name, pos in CITIES.items():
        pygame.draw.circle(screen, GRAY_CITY, pos, 20)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(name, True, BLACK)
        text_rect = text_surface.get_rect(center=pos)
        screen.blit(text_surface, text_rect)


def draw_ui(screen, truck, font):
    # Panel UI
    pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - 120, SCREEN_WIDTH, 120))  # Tło panelu

    # Wyświetlanie paliwa
    fuel_text = font.render(f"Paliwo: {int(truck.fuel)} / {truck.max_fuel}", True, YELLOW_TEXT)
    screen.blit(fuel_text, (10, SCREEN_HEIGHT - 110))
    fuel_bar_width = int((truck.fuel / truck.max_fuel) * 200)
    pygame.draw.rect(screen, RED_CARGO, (10, SCREEN_HEIGHT - 80, 200, 15), 1)  # Ramka
    pygame.draw.rect(screen, RED_CARGO, (10, SCREEN_HEIGHT - 80, fuel_bar_width, 15))  # Wypełnienie

    # Wyświetlanie pieniędzy
    money_text = font.render(f"Pieniądze: {int(truck.money)} zł", True, YELLOW_TEXT)
    screen.blit(money_text, (10, SCREEN_HEIGHT - 50))

    # Wyświetlanie statusu ładunku
    cargo_status_text = font.render("Ładunek:", True, YELLOW_TEXT)
    screen.blit(cargo_status_text, (250, SCREEN_HEIGHT - 110))

    if truck.has_cargo:
        cargo_info_text = font.render(
            f"{truck.current_cargo['name']} z {truck.current_cargo['from']} do {truck.current_cargo['to']} ({truck.current_cargo['reward']} zł)",
            True, YELLOW_TEXT)
        screen.blit(cargo_info_text, (250, SCREEN_HEIGHT - 80))
    else:
        no_cargo_text = font.render("Brak ładunku. Podjedź do miasta, by wziąć zlecenie.", True, YELLOW_TEXT)
        screen.blit(no_cargo_text, (250, SCREEN_HEIGHT - 80))

    # Instrukcje
    inst_text = font.render("Kliknij na miasto by jechać. Spacja: Tankuj (500 jedn. paliwa).", True, YELLOW_TEXT)
    screen.blit(inst_text, (SCREEN_WIDTH - inst_text.get_width() - 10, SCREEN_HEIGHT - 110))


def generate_cargo(exclude_city=None):
    cities_list = list(CITIES.keys())
    if exclude_city and exclude_city in cities_list:
        cities_list.remove(exclude_city)  # Nie generuj ładunku do/z tego samego miasta

    from_city = random.choice(cities_list)

    remaining_cities = [c for c in cities_list if c != from_city]
    if not remaining_cities:  # W przypadku bardzo małej mapy, unikaj błędu
        return None
    to_city = random.choice(remaining_cities)

    cargo_names = ["Drewno", "Elektronika", "Żywność", "Maszyny", "Leki", "Paliwo"]
    cargo_name = random.choice(cargo_names)

    # Prosta kalkulacja nagrody na podstawie dystansu (do poprawy)
    reward = random.randint(50, 300)

    return {'name': cargo_name, 'from': from_city, 'to': to_city, 'reward': reward}


# --- Inicjalizacja Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Euro Truck Simulator 2D")
clock = pygame.time.Clock()
font_ui = pygame.font.Font(None, 30)  # Czcionka dla UI

# --- Grupy Sprite'ów ---
all_sprites = pygame.sprite.Group()
truck = Truck()
all_sprites.add(truck)

# Zmienna do przechowywania celu ruchu ciężarówki
current_target_city_name = None
current_target_pos = None

# Początkowy ładunek
current_generated_cargo = generate_cargo(exclude_city="Warszawa")

# --- Główna Pętla Gry ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Sprawdź, czy kliknięto w miasto
            for city_name, city_pos in CITIES.items():
                city_rect = pygame.Rect(city_pos[0] - 20, city_pos[1] - 20, 40, 40)  # Przybliżony obszar miasta
                if city_rect.collidepoint(mouse_pos):
                    current_target_city_name = city_name
                    current_target_pos = city_pos
                    print(f"Cel ustawiony na: {city_name}")
                    break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Tankowanie 500 jednostek paliwa
                truck.refill_fuel(500)

    # --- Aktualizacja Stanu Gry ---
    if current_target_pos:
        arrived = truck.update(current_target_pos)
        if arrived:
            current_target_pos = None  # Reset celu
            current_target_city_name = None
            print("Dotarłeś do celu!")

            # Sprawdzenie interakcji z miastem
            for city_name, city_pos in CITIES.items():
                if (truck.rect.centerx - city_pos[0]) ** 2 + (truck.rect.centery - city_pos[1]) ** 2 < 30 ** 2:
                    # Jesteś w mieście
                    if not truck.has_cargo and current_generated_cargo and city_name == current_generated_cargo['from']:
                        # Możliwość pobrania ładunku
                        truck.pickup_cargo(current_generated_cargo)
                        current_generated_cargo = None  # Usuń zlecenie po pobraniu
                    elif truck.has_cargo and city_name == truck.current_cargo['to']:
                        # Możliwość dostarczenia ładunku
                        if truck.deliver_cargo():
                            # Po dostarczeniu generuj nowe zlecenie
                            current_generated_cargo = generate_cargo(exclude_city=city_name)
                            print(
                                f"Nowe zlecenie dostępne: {current_generated_cargo['name']} z {current_generated_cargo['from']} do {current_generated_cargo['to']}")
                    break  # Przetworzono interakcję z miastem, wyjdź

    # --- Rysowanie ---
    screen.fill(WHITE)  # Jasne tło

    draw_map(screen)  # Rysuj mapę z miastami i drogami

    # Rysuj dostępne zlecenie, jeśli istnieje i nie ma ładunku w ciężarówce
    if not truck.has_cargo and current_generated_cargo:
        cargo_from_pos = CITIES[current_generated_cargo['from']]
        pygame.draw.circle(screen, RED_CARGO, cargo_from_pos, 15, 2)  # Ramka dla miasta z ładunkiem
        cargo_text = font_ui.render(
            f"Zlecenie: {current_generated_cargo['name']} z {current_generated_cargo['from']} do {current_generated_cargo['to']}",
            True, RED_CARGO)
        screen.blit(cargo_text, (SCREEN_WIDTH - cargo_text.get_width() - 10, 10))

    all_sprites.draw(screen)  # Rysuj ciężarówkę

    draw_ui(screen, truck, font_ui)  # Rysuj interfejs użytkownika

    # Odśwież ekran
    pygame.display.flip()

    # Kontroluj FPS
    clock.tick(FPS)

# --- Zakończenie Pygame ---
pygame.quit()
sys.exit()