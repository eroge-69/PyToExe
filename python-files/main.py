from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

window.fps_counter.enabled = False  # Отключить текст с FPS
window.exit_button.enabled = False  # Отключить крестик закрытия
window.entity_counter.enabled = False    # Отключить счетчик сущностей
window.collider_counter.enabled = False    # Отключить счетчик колайдеров

# =============================================
# ПАРАМЕТРЫ ИГРЫ И НАСТРОЙКИ
# =============================================
room_size = 20          # Размер комнаты
wall_thickness = 1      # Толщина стен
wall_height = 3         # Высота стен
door_width = 3          # Ширина дверного проема
monster_speed = 1.2      # Скорость бабушки
player_speed = 5        # Скорость игрока

# =============================================
# ПОЛЬЗОВАТЕЛЬСКИЙ ИНТЕРФЕЙС
# =============================================
# Текстовые сообщения
message_text = Text(
    text='', 
    origin=(0, 0), 
    scale=1.5, 
    y=0.4,
    enabled=False
)

# =============================================
# ЭЛЕМЕНТЫ МЕНЮ
# =============================================
# Главное меню
menu_panel = Panel(
    scale = 2,
    color = color.dark_gray,
    model = 'quad',
    enabled = True
)

# Меню паузы
pause_panel = Panel(
    scale = 2,
    model = 'quad',
    enabled = False
)

# Меню завершения игры
game_over_panel = Panel(
    scale = 2,
    color = color.dark_gray,
    model = 'quad',
    enabled = False
)

# =============================================
# КНОПКИ
# =============================================
# Кнопка начала игры
start_button = Button(
    text = 'Начать игру',
    parent = menu_panel,
    y=-0.1,
    color=color.blue,
    scale = (0.3, 0.05),
    enabled = True
)

# Кнопка выхода из игры
exit_start_button = Button(
    text='Выйти',
    parent = menu_panel,
    y = -0.18,
    color=color.red,
    scale = (0.3, 0.05),
    enabled = True
)

# Кнопка выхода из игры во время паузы
exit_pause_button = Button(
    text='Выйти',
    parent = pause_panel,
    y = -0.18,
    color=color.red,
    scale = (0.3, 0.05),
    enabled = False
)

# Кнопка выхода из игры по её завершению
exit_over_button = Button(
    text='Выйти',
    parent = game_over_panel,
    y = -0.18,
    color=color.red,
    scale = (0.3, 0.05),
    enabled = False
)

# Кнопка продолжения игры
continue_button = Button(
    text = 'Продолжить игру',
    parent = pause_panel,
    y=-0.1,
    color=color.blue,
    scale = (0.3, 0.05),
    enabled = False
)

# =============================================
# ЭЛЕМЕНТЫ ТЕКСТА
# =============================================
# Текст главного меню
menu_text = Text(
    text='MONSTER\n\nДобро пожаловать в игру!',
    origin=(0,0),
    scale=3,
    background=True,
    background_color=color.black66,
    enabled=True,
    y=0.3
)

# Текст меню паузы
pause_text = Text(
    text='ПАУЗА',
    origin=(0,0),
    scale=2,
    background=True,
    background_color=color.black66,
    enabled=False,
    y=0
)

# Текст окончания игры
game_over_text = Text(
    text='',
    origin=(0,0),
    scale=2,
    background=True,
    background_color=color.black66,
    enabled=False,
    y=0
)

# =============================================
# ИГРОВЫЕ ОБЪЕКТЫ
# =============================================
# Создание игрового пространства
def create_environment():
    """Создает окружение: пол, стены, крышу"""
    # Пол
    Entity(
        model='plane',
        scale=room_size,
        texture='grass',
        collider='box'
    )

    # Передняя стена с дверью
    wall_left = Entity(
        model='cube',
        scale=((room_size - door_width)/2, wall_height, wall_thickness),
        position=(-(door_width + (room_size - door_width)/2)/2, wall_height/2, room_size/2),
        texture='brick',
        collider='box'
    )

    wall_right = Entity(
        model='cube',
        scale=((room_size - door_width)/2, wall_height, wall_thickness),
        position=((door_width + (room_size - door_width)/2)/2, wall_height/2, room_size/2),
        texture='brick',
        collider='box'
    )

    # Остальные стены
    walls = [
        Entity(model='cube', scale=(room_size, wall_height, wall_thickness), position=(0, wall_height/2, -room_size/2), texture='brick', collider='box'),  # Задняя
        Entity(model='cube', scale=(wall_thickness, wall_height, room_size), position=(-room_size/2, wall_height/2, 0), texture='brick', collider='box'),   # Левая
        Entity(model='cube', scale=(wall_thickness, wall_height, room_size), position=(room_size/2, wall_height/2, 0), texture='brick', collider='box')     # Правая
    ]

    # Крыша с прозрачностью
    #Entity(
        #model='cube',
        #scale=(room_size, wall_thickness, room_size),
        #position=(0, wall_height + wall_thickness/2, 0),
        #color=color.rgba(150, 150, 255, 100),
        #double_sided=True,
        #collider='box'
    #)

# Создаем окружение
create_environment()

# =============================================
# ПЕРСОНАЖИ
# =============================================
# Игрок
player = FirstPersonController(
    speed=player_speed,
    gravity=0.3,
    collider='box',
    position=(0, 1, 0),
    cursor=Entity(model = 'sphere', color=color.dark_gray, scale=.1)
)

# Монстер
class Monster(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            scale=(1, 2.5, 1),
            position=(random.uniform(-room_size/2+1, room_size/2-1), 1, random.uniform(-room_size/2+1, room_size/2-1)),
            texture='monster.png',
            collider='box'
        )
        self.speed = monster_speed
        self.chasing = False
        self.gravity = 0.3
        self.y_velocity = 0

    def update(self):
        if app.paused:
            return

        # Взгляд монстра на игрока по оси Y
        self.look_at_2d(player.position, 'y')

        # Гравитация
        self.y_velocity -= self.gravity * time.dt
        self.y += self.y_velocity

        # Проверка столкновения с полом (Y=0)
        if self.y < 1:
            self.y = 1
            self.y_velocity = 0
            
        dist = distance_xz(self.position, player.position)
        if dist < 10:
            self.chasing = True
            
        if self.chasing:
            direction = (player.position - self.position).normalized()
            # Двигаем только по XZ, чтобы не "утопить" монстра
            direction.y = 0
            self.position += direction * time.dt * self.speed
            
            if dist < 1.5:
                show_game_over("Монстер поймал тебя!")

monster = Monster()

# Предметы для сбора
items = []
item_positions = [(-5,0.5,-5), (5,0.5,5), (-5,0.5,5), (5,0.5,-5)]
for pos in item_positions:
    item = Entity(
        model='sphere', 
        color=color.gold, 
        scale=0.5, 
        position=pos, 
        collider='box',
        texture='item_texture.png'
    )
    items.append(item)

collected = 0

# Выходная дверь
exit_door = Entity(
    model='cube',
    texture = 'door.jpeg',
    scale=(door_width, 4, 0.2),
    position=(0, 1, room_size/2 + 0.1),
    collider='box'
)

# =============================================
# ОБНОВЛЕНИЕ ИГРЫ
# =============================================
def update():
    global collected
    if app.paused:
        return
    
    # Сбор предметов
    for item in items:
        if item.enabled and distance(player, item) < 1.5:
            item.enabled = False
            collected +=1
            show_message(f"Предметов: {collected}/{len(items)}", 2)

    # Победа при выходе
    if collected == len(items) and distance(player, exit_door) < 2:
        show_game_over("ПОБЕДА! Ты сбежал!")

# =============================================
# ФУНКЦИИ ИНТЕРФЕЙСА
# =============================================
def exit_game():
    application.quit()

exit_start_button.on_click = exit_game
exit_pause_button.on_click = exit_game
exit_over_button.on_click = exit_game

def show_message(text, duration=3):
    """Отображает сообщение на экране"""
    message_text.text = text
    message_text.enabled = True
    invoke(disable_message, delay=duration)

def disable_message():
    """Скрывает сообщение"""
    message_text.enabled = False

def show_menu():
    """Показывает главное меню"""
    menu_panel.enabled = True
    menu_text.enabled = True
    pause_text.enabled = False
    game_over_text.enabled = False
    player.enabled = False
    monster.enabled = False
    app.paused = True

def hide_menu():
    """Скрывает меню и начинает игру"""
    menu_panel.enabled = False
    start_button.enabled = False
    exit_start_button.enabled = False
    menu_text.enabled = False
    player.enabled = True
    monster.enabled = True
    app.paused = False

start_button.on_click = hide_menu

def show_pause():
    """Ставит игру на паузу"""
    pause_panel.enabled = True
    continue_button.enabled = True
    exit_pause_button.enabled = True
    pause_text.enabled = True
    player.enabled = False
    monster.enabled = False
    app.paused = True

def hide_pause():
    """Снимает с паузы"""
    pause_panel.enabled = False
    continue_button.enabled = False
    exit_pause_button.enabled = False
    pause_text.enabled = False
    player.enabled = True
    monster.enabled = True
    app.paused = False

continue_button.on_click = hide_pause

def show_game_over(text):
    """Показывает экран завершения игры"""
    game_over_panel.enabled = True
    exit_over_button.enabled = True
    game_over_text.text = text
    game_over_text.enabled = True
    player.enabled = False
    monster.enabled = False
    app.paused = True

# =============================================
# ОБРАБОТКА ВВОДА
# =============================================
def input(key):
    # Пауза
    if key == 'escape':
        show_pause()

# =============================================
# ЗАПУСК ИГРЫ
# =============================================
Sky()

show_menu()
app.run()
