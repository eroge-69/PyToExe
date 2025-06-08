import os
import sys
from panda3d.core import loadPrcFileData

# Принудительная установка графического драйвера
loadPrcFileData("", "load-display pandagl")  # Основной драйвер
loadPrcFileData("", "aux-display pandadx9")  # Резервный для Windows
loadPrcFileData("", "aux-display pandavulkan")  # Резервный Vulkan
loadPrcFileData("", "window-type offscreen")  # На случай проблем с окном

# Для режима EXE - исправление путей
if getattr(sys, 'frozen', False):
    if hasattr(sys, '_MEIPASS'):
        # Режим OneFile
        os.environ['PATH'] = sys._MEIPASS + os.pathsep + os.environ['PATH']
        resource_dir = sys._MEIPASS
    else:
        # Режим OneDirectory
        resource_dir = os.path.dirname(sys.executable)
    
    # Указываем пути к ресурсам
    loadPrcFileData("", f"model-path {resource_dir}")
    loadPrcFileData("", f"icon-path {resource_dir}")

try:
    # Проверка инициализации графики
    from panda3d.core import GraphicsPipeSelection
    pipe = GraphicsPipeSelection.get_global_ptr()
    if pipe.get_num_pipe_types() == 0:
        print("ERROR: No graphics pipes available!")
    else:
        print(f"Available graphics pipes: {pipe.get_pipe_type_names()}")
except Exception as e:
    print(f"Graphics check failed: {e}")


# Теперь можно импортировать Ursina/Panda3D

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import ctypes

# Увеличиваем дальность отрисовки
app = Ursina(z_far=5000, z_near=0.1)  # Значительно увеличенная дальность
window.icon = 'textures/ursina.ico'
window.fullscreen = True
window.borderless = False
window.title = "Game Window"
window.anti_aliasing = True  # Включаем сглаживание

# ========== НАСТРОЙКИ ========== #
TERRAIN_SCALE = 300
TEXTURE_SCALE_FACTOR = 1.4
WALL_HEIGHT = 20
SPEED_LEVELS = {
    '1': 2, '2': 4, '3': 6,
    '4': 8, '5': 12, '6': 16, '7': 20
}

MAP_TEXTURES = {
    '32R': '32R.png',
    '32GR': '32GR.png',
    '32L': '32L.png',
    '32SR': '32SR.png',
    '32SL': '32SL.png',
    '32PR': '32PR.png',
    '32PL': '32PL.png',
    '32LIGHTL': '32LIGHTL.png',
    '32LIGHTR': '32LIGHTR.png'
}
# =============================== #

def center_window():
    """Центрирует окно на экране (работает только в оконном режиме)"""
    if not window.fullscreen:
        # Получаем размеры экрана
        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        
        # Используем window.size вместо width/height
        win_width, win_height = window.size
        x = (screen_width - win_width) // 2
        y = (screen_height - win_height) // 2
        window.position = (x, y)

class Game:
    def __init__(self):
        self.current_map = '32GR'
        self.menu_open = False
        
        # Создаем элементы интерфейса
        self.speed_label = Text(
            text=f"Speed: 4 (8 m/s)",
            position=(-0.8, 0.45),
            scale=1.5
        )
        self.map_label = Text(
            text=f"Map: {self.current_map}",
            position=(-0.8, 0.5),
            scale=1.5
        )
        self.fullscreen_info = Text(
            text="",
            position=(-0.8, 0.4),
            scale=1.0,
            color=color.yellow
        )
        
        # Создаем список для кнопок
        self.map_buttons = []
        
        # Создаем игрока с уменьшенным FOV
        self.player = FirstPersonController(
            position=(0, 10, 0),
            gravity=0.5,
            mouse_sensitivity=(40, 40),
            fov=60  # Уменьшаем FOV для уменьшения перспективных искажений
        )
        
        self.current_speed = 4
        self.player.speed = SPEED_LEVELS['4']
        
        # Создаем игровые объекты
        self.floor = Entity(
            model='plane',
            scale=(TERRAIN_SCALE, 1, TERRAIN_SCALE),
            collider='box'
        )
        
        # Создаем кнопки выбора карты
        self.create_map_buttons()
        
        # Загружаем текстуру
        self.load_map_texture(self.current_map)
        
        self.create_boundary_walls()

    def create_map_buttons(self):
        y_pos = 0.35
        for i, map_name in enumerate(MAP_TEXTURES.keys()):
            btn = Button(
                text=map_name,
                position=(-0.8, y_pos - i*0.05),
                scale=(0.15, 0.04),
                color=color.dark_gray,
                visible=False,
                on_click=Func(self.load_map_texture, map_name)
            )
            self.map_buttons.append(btn)

    def load_map_texture(self, map_name):
        self.current_map = map_name
        try:
            texture = load_texture(MAP_TEXTURES[map_name])
            # Включаем mipmapping и анизотропную фильтрацию
            texture.filtering = 'mipmap'
            texture.anisotropy = 8
        except:
            texture = load_texture('white_cube')
            texture.filtering = 'mipmap'
            print(f"Error loading texture: {map_name}")
        
        self.floor.texture = texture
        self.floor.texture_scale = (
            TERRAIN_SCALE/100/TEXTURE_SCALE_FACTOR,
            TERRAIN_SCALE/100/TEXTURE_SCALE_FACTOR
        )
        self.map_label.text = f"Map: {map_name}"
        self.toggle_map_menu(False)

    def toggle_map_menu(self, show=None):
        if show is None:
            show = not self.menu_open
            
        self.menu_open = show
        
        for btn in self.map_buttons:
            btn.visible = show
            btn.enabled = show
            
        mouse.locked = not show
        self.player.enabled = not show
        
        if show:
            mouse.visible = True
        else:
            invoke(self.hide_cursor, delay=0.1)
    
    def hide_cursor(self):
        if not self.menu_open:
            mouse.visible = False

    def create_boundary_walls(self):
        """Оптимизированное создание стен"""
        wall_thickness = 10
        area_size = TERRAIN_SCALE/2
        
        # Создаем единый объект для всех стен
        walls = Entity(
            model='cube',
            collider='box',
            scale=(TERRAIN_SCALE + wall_thickness, WALL_HEIGHT, TERRAIN_SCALE + wall_thickness),
            position=(0, WALL_HEIGHT/2, 0),
            color=color.rgba(100, 100, 255, 50),  # Полупрозрачный для отладки
            texture='white_cube'
        )

    def update_speed(self, level):
        if level in SPEED_LEVELS:
            speed_value = SPEED_LEVELS[level]
            self.player.speed = speed_value
            self.speed_label.text = f"Speed: {level} ({speed_value} m/s)"

def toggle_fullscreen():
    window.fullscreen = not window.fullscreen
    
    if window.fullscreen:
        game.fullscreen_info.text = "Fullscreen: True"
        window.borderless = True
    else:
        game.fullscreen_info.text = "Fullscreen: False"
        window.borderless = False
        window.size = (1280, 720)
        center_window()  # Центрируем после изменения размера
    
    invoke(setattr, game.fullscreen_info, 'text', "", delay=2)

def input(key):
    if key == 'escape':
        application.quit()
    
    if key in '1234567':
        game.update_speed(key)
    
    if key == 'f11':
        toggle_fullscreen()
    
    if key == 'm':
        game.toggle_map_menu()

game = Game()
AmbientLight(color=color.rgba(1, 1, 1, 0.8))
DirectionalLight(position=(0, 50, 0), shadows=False)

# Скрываем курсор при запуске
mouse.visible = False

# Центрируем окно после его создания
center_window()

app.run()