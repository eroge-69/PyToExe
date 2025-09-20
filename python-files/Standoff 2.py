from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.uix.button import Button, Label
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from random import randint

class Player(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, 50)
        # Исходная позиция игрока
        self.pos = (Window.width // 2 -25, 150)
        with self.canvas:
            Color(0, 0, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.speed = 10
        self.move_dir = 0

    def move(self):
        if self.move_dir != 0:
            new_x = self.x + self.speed * self.move_dir
            new_x = max(0, min(Window.width - self.width, new_x))
            self.pos = (new_x, self.y)
            self.rect.pos = self.pos

class Bullet(Widget):
    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.size = (10, 20)
        self.pos = (x, y)
        with self.canvas:
            Color(1, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.speed = 15

    def update(self):
        self.y += self.speed
        self.rect.pos = (self.x, self.y)
        return self.top <= Window.height

class Enemy(Widget):
    def __init__(self, x, y, **kwargs):
        super().__init__(**kwargs)
        self.size = (40, 40)
        self.pos = (x, y)
        with self.canvas:
            Color(0, 1, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.speed = randint(2, 5)

    def update(self):
        self.y -= self.speed
        self.rect.pos = (self.x, self.y)
        return self.top >= 0

class PauseMenu(Widget):
    def __init__(self, resume_callback, menu_callback, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self.bg_rect = Rectangle(pos=self.pos, size=Window.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.btn_resume = Button(text="Продолжить", size_hint=(None, None), size=(200, 100),
                                 pos=(Window.width // 2 - 100, Window.height // 2 + 30))
        self.btn_resume.bind(on_press=lambda x: resume_callback())
        self.add_widget(self.btn_resume)

        self.btn_menu = Button(text="Выйти в меню", size_hint=(None, None), size=(200, 100),
                               pos=(Window.width // 2 - 100, Window.height // 2 - 100))
        self.btn_menu.bind(on_press=lambda x: menu_callback())
        self.add_widget(self.btn_menu)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class ShooterGame(Widget):
    def __init__(self, menu_callback, **kwargs):
        super().__init__(**kwargs)
        self.menu_callback = menu_callback
        self.paused = False

        with self.canvas.before:
            Color(0.4, 0.7, 1, 1)  # Светло-голубой фон
            self.bg_rect = Rectangle(pos=self.pos, size=Window.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.player = Player()
        self.add_widget(self.player)

        self.bullets = []
        self.enemies = []
        self.score = 0
        self.lives = 3
        self.game_over = False

        self.sound_shoot = SoundLoader.load('shoot.wav')
        self.sound_explosion = SoundLoader.load('explosion.wav')
        self.sound_hit = SoundLoader.load('hit.wav')

        self.ammo = 30
        self.reloading = False
        self.shooting_event = None

        self.btn_menu = Button(text='Меню', size_hint=(None, None), size=(180, 70), pos=(10, Window.height - 80))
        self.btn_menu.bind(on_press=self.go_to_menu)
        self.add_widget(self.btn_menu)

        self.btn_pause = Button(text='Пауза', size_hint=(None, None), size=(150, 60), pos=(10, Window.height - 150))
        self.btn_pause.bind(on_press=self.pause_game)
        self.add_widget(self.btn_pause)

        self.score_label = Label(text="Очки: 0", pos=(10, Window.height - 210), size_hint=(None, None), size=(200, 40), color=(1,1,1,1))
        self.add_widget(self.score_label)

        self.ammo_label = Label(text=f"Патроны: {self.ammo}", pos=(10, Window.height - 260), size_hint=(None, None), size=(200, 40), color=(1,1,1,1))
        self.add_widget(self.ammo_label)

        self.lives_label = Label(text="Жизни: 3", pos=(Window.width - 180, Window.height - 40), size_hint=(None, None), size=(140, 40), color=(1,1,1,1))
        self.add_widget(self.lives_label)

        self.btn_left = Button(text='←', size_hint=(None, None), size=(100, 100), pos=(10, 10))
        self.btn_left.bind(on_press=self.start_move_left)
        self.btn_left.bind(on_release=self.stop_move)
        self.add_widget(self.btn_left)

        self.btn_right = Button(text='→', size_hint=(None, None), size=(100, 100), pos=(120, 10))
        self.btn_right.bind(on_press=self.start_move_right)
        self.btn_right.bind(on_release=self.stop_move)
        self.add_widget(self.btn_right)

        self.btn_shoot = Button(text='Стрелять', size_hint=(None, None), size=(100, 100), pos=(Window.width - 110, 10))
        self.btn_shoot.bind(on_press=self.start_shooting)
        self.btn_shoot.bind(on_release=self.stop_shooting)
        self.add_widget(self.btn_shoot)

        self.spawn_event = Clock.schedule_interval(self.spawn_enemy, 1.5)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def pause_game(self, *args):
        if self.game_over or self.paused:
            return
        self.paused = True
        if self.shooting_event:
            self.shooting_event.cancel()
            self.shooting_event = None
        self.spawn_event.cancel()
        self.pause_menu = PauseMenu(resume_callback=self.resume_game, menu_callback=self.go_to_menu)
        self.add_widget(self.pause_menu)

    def resume_game(self):
        if not self.paused:
            return
        self.paused = False
        self.remove_widget(self.pause_menu)
        self.spawn_event = Clock.schedule_interval(self.spawn_enemy, 1.5)

    def go_to_menu(self, *args):
        if not self.paused:
            if self.shooting_event:
                self.shooting_event.cancel()
                self.shooting_event = None
            self.spawn_event.cancel()
        self.menu_callback()

    def start_move_left(self, *args):
        if not self.game_over and not self.paused:
            self.player.move_dir = -1

    def start_move_right(self, *args):
        if not self.game_over and not self.paused:
            self.player.move_dir = 1

    def stop_move(self, *args):
        self.player.move_dir = 0

    def start_shooting(self, *args):
        if not self.shooting_event:
            self.shoot()
            self.shooting_event = Clock.schedule_interval(lambda dt: self.shoot(), 0.2)

    def stop_shooting(self, *args):
        if self.shooting_event:
            self.shooting_event.cancel()
            self.shooting_event = None

    def shoot(self):
        if self.game_over or self.paused or self.reloading:
            return
        if self.ammo <= 0:
            return
        bullet = Bullet(self.player.center_x - 5, self.player.top)
        self.bullets.append(bullet)
        self.add_widget(bullet)
        self.ammo -= 1
        self.ammo_label.text = f"Патроны: {self.ammo}"
        if self.sound_shoot:
            self.sound_shoot.play()
        if self.ammo == 0:
            self.start_reload()
            if self.shooting_event:
                self.shooting_event.cancel()
                self.shooting_event = None

    def start_reload(self):
        self.reloading = True
        Clock.schedule_once(self.finish_reload, 2)

    def finish_reload(self, dt):
        self.ammo = 30
        self.ammo_label.text = f"Патроны: {self.ammo}"
        self.reloading = False

    def spawn_enemy(self, dt):
        if self.game_over or self.paused:
            return
        x = randint(0, Window.width - 40)
        enemy = Enemy(x, Window.height)
        self.enemies.append(enemy)
        self.add_widget(enemy)

    def update(self, dt):
        if self.game_over or self.paused:
            return
        self.player.move()

        for bullet in self.bullets[:]:
            if not bullet.update():
                self.remove_widget(bullet)
                self.bullets.remove(bullet)

        for enemy in self.enemies[:]:
            if not enemy.update():
                self.remove_widget(enemy)
                self.enemies.remove(enemy)
                self.lives -= 1
                self.lives_label.text = f"Жизни: {self.lives}"
                if self.sound_hit:
                    self.sound_hit.play()
                self.check_game_over()

        for enemy in self.enemies[:]:
            for bullet in self.bullets[:]:
                if enemy.collide_widget(bullet):
                    self.remove_widget(enemy)
                    self.remove_widget(bullet)
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    self.score += 1
                    self.score_label.text = f"Очки: {self.score}"
                    if self.sound_explosion:
                        self.sound_explosion.play()
                    break

    def check_game_over(self):
        if self.lives <= 0:
            self.game_over = True
            if self.shooting_event:
                self.shooting_event.cancel()
                self.shooting_event = None
            self.show_game_over()

    def show_game_over(self):
        self.game_over_label = Label(text="Игра окончена!\nНажмите 'Перезапуск'",
                                     font_size=40, halign='center', valign='middle',
                                     size_hint=(None, None), size=(Window.width, Window.height),
                                     color=(1,1,1,1))
        self.game_over_label.pos = (0, Window.height // 2 - 100)
        self.add_widget(self.game_over_label)

        self.restart_button = Button(text="Перезапуск", size_hint=(None, None), size=(200, 100),
                                     pos=(Window.width // 2 - 100, Window.height // 2 - 200))
        self.restart_button.bind(on_press=self.restart_game)
        self.add_widget(self.restart_button)

    def restart_game(self, instance):
        for enemy in self.enemies:
            self.remove_widget(enemy)
        for bullet in self.bullets:
            self.remove_widget(bullet)

        if self.paused:
            self.remove_widget(self.pause_menu)
            self.paused = False

        if self.shooting_event:
            self.shooting_event.cancel()
            self.shooting_event = None

        self.enemies.clear()
        self.bullets.clear()
        self.score = 0
        self.lives = 3
        self.ammo = 30
        self.reloading = False
        self.score_label.text = "Очки: 0"
        self.lives_label.text = "Жизни: 3"
        self.ammo_label.text = f"Патроны: {self.ammo}"
        self.game_over = False

        self.remove_widget(self.game_over_label)
        self.remove_widget(self.restart_button)

        self.spawn_event = Clock.schedule_interval(self.spawn_enemy, 1.5)

class MainMenu(Widget):
    def __init__(self, start_callback, **kwargs):
        super().__init__(**kwargs)
        self.start_callback = start_callback

        with self.canvas.before:
            Color(0.4, 0.7, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=Window.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.title = Label(text='Standoff 2', font_size=70,
                           pos=(0, Window.height - 100),
                           size_hint=(None, None),
                           size=(Window.width, 100),
                           halign='center', valign='middle',
                           color=(1,1,1,1))
        self.title.text_size = (Window.width, None)
        self.add_widget(self.title)

        self.start_button = Button(text='Начать игру', size_hint=(None, None),
                                   size=(200, 100),
                                   pos=(Window.width // 2 - 100, Window.height // 2 - 50))
        self.start_button.bind(on_press=self.start_game)
        self.add_widget(self.start_button)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def start_game(self, instance):
        self.start_callback()

class StandoffApp(App):
    def build(self):
        self.root_widget = Widget()
        self.menu = MainMenu(self.start_game)
        self.root_widget.add_widget(self.menu)
        return self.root_widget

    def start_game(self):
        self.root_widget.clear_widgets()
        self.game = ShooterGame(menu_callback=self.show_menu)
        self.root_widget.add_widget(self.game)

    def show_menu(self):
        self.root_widget.clear_widgets()
        self.menu = MainMenu(self.start_game)
        self.root_widget.add_widget(self.menu)

if __name__ == '__main__':
    StandoffApp().run()
#