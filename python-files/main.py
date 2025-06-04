from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import time as time_module


app = Ursina(development_mode=True)
screen = True

class Menu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, ignore_paused=True)

        self.main_menu = Entity(parent=self, enabled=True)

# стартовая надпись Minecraft
        Text("FPS SHOOTER", parent=self.main_menu, y=0.4, x=0, origin=(0, 0))

        ButtonList(button_dict={
            "Start": Func(lambda: (destroy(self), main())),
            "Exit": Func(lambda: application.quit())
        }, y=0, parent=self.main_menu)


main_menu = Menu()

player_hp = 100
kills = 0
start_time = time_module.time()


class GameUI(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)

        # Полоса здоровья игрока
        self.health_bar = Entity(
            parent=self,
            model='quad',
            color=color.red,
            scale=(0.3, 0.03),
            position=(-0.7, -0.45),
            texture='white_cube'
        )

        # Счетчик убийств
        self.kills_text = Text(
            parent=self,
            text=f'Kills: {kills}',
            position=(-0.54, -0.44),
            scale=1,
            color=color.white
        )

        # Таймер
        self.timer_text = Text(
            parent=self,
            text='00:00',
            position=(-0.04, 0.47),
            scale=1,
            color=color.white
        )

    def update(self):
        # Обновляем здоровье
        self.health_bar.scale_x = player_hp / 100 * 0.3

        # Обновляем счетчик убийств
        self.kills_text.text = f'Kills: {kills}'

        # Обновляем таймер
        elapsed = int(time_module.time() - start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        self.timer_text.text = f'{mins:02d}:{secs:02d}'


def update():
    if held_keys['left mouse']:
        shoot()


def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        gun.muzzle_flash.enabled = True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise',
              pitch=random.uniform(-13, -12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)
            if mouse.hovered_entity == player:  # Если попали в игрока
                global player_hp
                player_hp -= 5
                if player_hp <= 0:
                    print("Game Over!")
            else:
                mouse.hovered_entity.hp -= 10
                mouse.hovered_entity.blink(color.red)


def main():
    global main_menu, ground, editor_camera, player
    main_menu = None
    random.seed(0)
    Entity.default_shader = lit_with_shadows_shader
    mouse.locked = True

    # level = Entity(
    #     model='fps_shooter_game_arena_map_v3.glb',
    #     scale=1,
    #     collider='box',
    #     position=(5, -5, -10)
    # )
    ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))
    normal_speed = 8
    sprint_speed = normal_speed * 3
    editor_camera = EditorCamera(enabled=False, ignore_paused=True)
    player = FirstPersonController(model='cube', z=0, color=color.orange, origin_y=-.5, speed=normal_speed, collider='box')
    player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

    def update():
        if held_keys['shift'] and held_keys['w']:
            player.speed = sprint_speed  # Устанавливаем повышенную скорость
        else:
            player.speed = normal_speed  # Возвращаем обычную скорость

    global gun
    gun = Entity(model='low-poly_kimber_k6s.glb', rotation=(0, -90, 0), parent=camera, position=(0.25, -0.25, 0.5), scale=0.12, origin_z=-0.5, on_cooldown=False)
    gun.muzzle_flash = Entity(parent=camera, z=1, world_scale=.3, position=(0.3, -0.2, 1.2), model='quad', color=color.yellow, enabled=False)

    shootables_parent = Entity()
    mouse.traverse_target = shootables_parent


    # for i in range(16):
    #     Entity(model='cube', origin_y=-.5, scale=2, texture='brick', texture_scale=(1,2),
    #         x=random.uniform(-8,8),
    #         z=random.uniform(-8,8) + 8,
    #         collider='box',
    #         scale_y = random.uniform(2,3),
    #         color=color.hsv(0, 0, random.uniform(.9, 1))
    #         )


    from ursina.prefabs.health_bar import HealthBar

    game_ui = GameUI()

    # Добавляем обработку убийств врагов
    def enemy_killed():
        global kills
        kills += 1

    class Enemy(Entity):
        def __init__(self, **kwargs):
            super().__init__(parent=shootables_parent, model='cube', scale_y=2, origin_y=-.5, color=color.light_gray, collider='box', **kwargs)
            self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
            self.max_hp = 100
            self.hp = self.max_hp

        def update(self):
            dist = distance_xz(player.position, self.position)
            if dist > 40:
                return

            self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


            self.look_at_2d(player.position, 'y')
            hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
            # print(hit_info.entity)
            if hit_info.entity == player:
                if dist > 2:
                    self.position += self.forward * time.dt * 5

        @property
        def hp(self):
            return self._hp

        @hp.setter
        def hp(self, value):
            self._hp = value
            if value <= 0:
                enemy_killed()
                destroy(self)
                return

            self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
            self.health_bar.alpha = 1

    # Enemy()
    # enemies = [Enemy(x=x*4) for x in range(30)]

    sun = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()


def pause_input(key):
    global ground, editor_camera, player, main_menu
    if key == 'tab':  # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled
        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position
        application.paused = editor_camera.enabled

    if key == 'escape':
        quit()

    if key == 'n':
        main_menu = Menu()

pause_handler = Entity(ignore_paused=True, input=pause_input)

app.run()
