from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# Простые настройки игры
class Game:
    def __init__(self):
        self.state = 'menu'
        self.level = 1
        self.score = 0
        self.player_health = 100
        self.shrek_health = 3
        self.poop_count = 10
        self.game_over = False
        
game = Game()

# Простое меню
def show_menu():
    # Очищаем сцену
    for e in scene.entities:
        if e not in [camera, ]:
            destroy(e)
    
    # Фон
    bg = Entity(model='quad', scale=(2,2), color=color.dark_gray, parent=camera.ui)
    
    # Текст
    Text("SHREK GAME", y=0.3, scale=2, parent=camera.ui)
    
    # Кнопки
    Button("ИГРАТЬ", y=0.1, scale=(0.3,0.1), color=color.green, 
           on_click=lambda: start_game(), parent=camera.ui)
    Button("ВЫХОД", y=-0.1, scale=(0.3,0.1), color=color.red,
           on_click=lambda: quit(), parent=camera.ui)

def start_game():
    game.state = 'playing'
    load_level()

# Игровые объекты
player = None
shrek = None
ground = None

def load_level():
    # Очистка
    for e in scene.entities:
        if e not in [camera, ]:
            destroy(e)
    
    # Игрок
    global player
    player = FirstPersonController()
    player.y = 2
    
    # Пол
    global ground
    ground = Entity(model='plane', scale=20, color=color.green, collider='box')
    
    # Шрек
    global shrek
    shrek = Entity(model='cube', color=color.green, scale=(1,2,1), 
                   position=(5,1,0), collider='box')
    
    # UI
    Text(f"Уровень: {game.level}", position=(-0.8,0.4), scale=1.5)
    Text(f"Здоровье: {game.player_health}", position=(-0.8,0.35), scale=1.5)
    Text(f"Какашки: {game.poop_count}", position=(-0.8,0.3), scale=1.5)

def update():
    if game.state != 'playing' or game.game_over:
        return
    
    # Движение Шрека
    if shrek and player:
        dir_to_player = (player.position - shrek.position).normalized()
        shrek.position += dir_to_player * 2 * time.dt
        
        # Атака Шрека
        if distance(shrek.position, player.position) < 2:
            game.player_health -= 1 * time.dt * 10
            if game.player_health <= 0:
                game_over()

def input(key):
    if key == 'left mouse down' and game.state == 'playing':
        throw_poop()
    elif key == 'escape':
        show_menu()

def throw_poop():
    if game.poop_count > 0:
        poop = Entity(model='sphere', color=color.brown, scale=0.3,
                     position=player.position + (0,1,0), collider='sphere')
        
        # Бросок
        direction = camera.forward
        poop.animate_position(poop.position + direction * 10, duration=1)
        
        game.poop_count -= 1
        
        # Проверка попадания
        def check_hit():
            if poop.intersects(shrek).hit:
                game.shrek_health -= 0.5
                game.score += 10
                if game.shrek_health <= 0:
                    next_level()
            destroy(poop)
        
        invoke(check_hit, delay=1.1)

def next_level():
    game.level += 1
    game.shrek_health = 3 + game.level
    game.poop_count = 10
    load_level()

def game_over():
    game.game_over = True
    Text("GAME OVER", scale=2, background=True)
    invoke(show_menu, delay=2)

# Запуск
show_menu()

print("Управление:")
print("ЛКМ - бросок")
print("ESC - меню")

app.run()