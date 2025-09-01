# ───────── 개발자 안내 ─────────
# 이 게임은 Python 라이브러리 Ursina로 제작되었습니다.
# 실행 전, 터미널에서 다음 명령어로 라이브러리를 설치하세요
#명령어: pip install ursina
#
# 주의사항:
# 1. Shift + Q → Ursina 엔진 고유의 단축키로, 게임 창을 닫습니다.
# 2. 벽에 캐릭터가 끼거나 반쯤 들어가는 현상이 있을 수 있습니다.
#    - 이는 게임 코드 문제가 아닌 Ursina 엔진의 고질적인 충돌 처리 한계입니다.
# 3. 벽을 통과할 경우, 경고 메시지가 표시됩니다.
#    - 이때는 Tap을 눌러 커서를 활성화한 후, 창을 닫았다가 다시 실행하세요.
# 4. 본 게임은 전체화면을 지원하지 않습니다.
#    - 전체화면으로 전환할 경우 UI, 로비 패널의 비율에 대한 예기치 못한 버그가 발생할 수 있습니다.
# 5. 대부분의 오류는 수정했지만, 개발자가 확인하지 못한 버그가 발생할 수 있습니다.
#    - 이 경우에도 게임을 재시작하면 대부분 해결됩니다.
# ─────────────────────────────


#라이브러리 불러오기
from panda3d.core import loadPrcFileData
loadPrcFileData("", """
load-display pandagl
sync-video false
clock-frame-rate 0
""")
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina import raycast, Vec3
import random

#Ursina 앱 생성
app = Ursina()

loadPrcFileData('', 'sync-video false')
loadPrcFileData('', 'clock-frame-rate 0')

Entity.default_shader = lit_with_shadows_shader

#개발용, 맵 감상용 에디터 카메라
editor_camera = EditorCamera(
    enabled = False,
    ignore_paused = True
)

#토글용 입력 처리(에디터 모드 전환)
def pause_input(key):
    if chapter != 5:
        if key == "tab":
            editor_camera.enabled = not editor_camera.enabled

            player.visible_self = editor_camera.enabled
            player.cursor.enabled = not editor_camera.enabled
            mouse.locked = not editor_camera.enabled

            editor_camera.position = player.position

            application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused = True, input = pause_input)

#플레이어
player = FirstPersonController(
    model = "cube",
    z = -10,
    color = color.rgba(1, 1, 1, 1),
    origin_y = -0.5,
    speed = 7,
    scale = (1, 1, 1)
)

#크레딧
credit = Text(
    text = "Expergiscere\n"
    "by cat.py\n"
    "v1.0\n\n"
    "개발자\n"
    "총괄: 임건우\n"
    "기획: 임건우\n"
    "스토리: 임건우\n"
    "모델링: 임건우\n"
    "텍스쳐링: 임건우\n"
    "코딩: 임건우\n"
    "아이콘 및 이미지 제작: 임건우\n"
    "음향 효과 녹음 및 생성: 임건우\n\n"
    "사용 툴\n"
    "Visual Studio Code\n"
    "Ursina Engine\n"
    "Blender\n"
    "Meshy AI\n"
    "Audacity\n"
    "Inkscape\n\n"
    "라이선스 및 출처\n"
    "이 프로젝트에 사용된 일부 텍스처는 OpenAI의 이미지 생성 AI인\n"
    "DALL·E (https://openai.com/dall-e)를 사용하여 생성되었습니다.\n"
    "생성된 이미지의 사용 권한은 OpenAI 정책에 따릅니다.\n\n"
    "이 프로젝트에 사용된 일부 3D 모델과 텍스처는\n"
    "Meshy (https://www.meshy.ai)를 사용하여 생성되었으며,\n"
    "크리에이티브 커먼즈 저작자표시 4.0 국제 라이선스(CC BY 4.0) 하에 제공됩니다.\n"
    "https://creativecommons.org/licenses/by/4.0/\n"
    "이 라이선스는 저작자 표기를 요구합니다.\n\n"
    "이 프로젝트에 사용된 일부 3D 모델과 텍스쳐는 Poly Haven에서 제공했으며,\n"
    "CC0 퍼블릭 도메인 라이선스로 자유롭게 사용 가능합니다.\n"
    "Poly Haven 웹사이트: https://polyhaven.com\n"
    "출처 표기는 선택 사항이며, 감사의 표시로 권장됩니다.\n\n"
    "이 프로젝트에 사용된 음악은 NoCopyrightSounds에서 제공하며,\n"
    "“Sky High” by Elektronomia (https://ncs.io/skyhigh) 입니다.\n"
    "NCS 이용 약관에 따릅니다: https://ncs.io/usage\n\n\n\n\n\n"
    "플레이해 주셔서 감사합니다!",
    parent = camera.ui,
    position = Vec2(0, -2),
    origin = (0, 0),
    scale = 2,
    color = color.white,
    font = "font/malgun.ttf"
)

#총 데미지
gun_damage = 30

#총 엔티티
gun = Entity(
    model = "3d/gun.obj",
    parent = camera,
    position = (1, -0.35, 0.7),
    scale = 1,
    origin_z = -0.5,
    on_cooldown = False,
    texture = "3d/gun.png",
    rotation=(0, 270, 0),
)

#총 번쩍임(?)
flash = Entity(
    parent = gun,
    position = (1, 0.17, 0.5),
    world_scale = 0.15,
    model = "circle",
    color = color.rgb(0, 1, 1),
    rotation = (0, 90, 0),
    enabled = False
)

#사격 함수
def shoot():
    if not gun.on_cooldown:
        gun.on_cooldown = True
        from ursina.prefabs.ursfx import ursfx

        ursfx(
            [(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)],
            volume = 1,
            wave = "noise",
            pitch = random.uniform(-51, -50),
            pitch_change = -12,
            speed = 3
        )
        invoke(setattr, gun, "on_cooldown", False, delay = 0.15)
        invoke(flash.disable, delay = 0.05)

        if mouse.hovered_entity and hasattr(mouse.hovered_entity, "hp"):
            mouse.hovered_entity.blink(color.red)
            mouse.hovered_entity.hp -= gun_damage
        flash.enabled = True

#적 및 더미들 집합
shootables_parent = Entity()
mouse.traverse_target = shootables_parent

#데스 카운터
death_count = 0
dummy_death_count = 0
mddummy_death_count = 0

#적 관리 리스트
enemies = []
dummies = []
Mdenemies = []
Mddummies = []

#폭탄 클래스
class Bomb(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model = "3d/bomb.obj",
            texture = "3d/bomb.png",
            scale = 1,
            **kwargs
        )
        self.trigger_distance = 10
        self.exploded = False

    def update(self):
        if self.exploded:
            return

        if self.y >= player.y:
            self.y -= 0.15
        else:
            Audio(sound_file_name="sound/explosion.wav")
            destroy(self)
            self.exploded = True

        if not self.exploded:
            if (player.position - self.position).length() < self.trigger_distance:
                self.explode()

    def explode(self):
        if self.exploded:
            return

        self.exploded = True
        take_damage(50)
        Audio(sound_file_name="sound/explosion.wav")
        destroy(self)

#유도탄 클래스
class Homing_Bomb(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model = "3d/bomb.obj",
            texture = "3d/bomb.png",
            rotation = (0, 0, 0),
            scale = 1,
            **kwargs
        )
        self.trigger_distance = 5
        self.exploded = False
        self.speed = 0.1

    def update(self):
        if self.exploded:
            return

        if not player or not hasattr(player, 'position'):
            return

        self.look_at(player.position)

        direction = (player.position - self.position).normalized()
        self.position += direction * self.speed
        if self.y >= player.y:
            self.y -= 0.04
        else:
            Audio(sound_file_name="sound/explosion.wav")
            destroy(self)
            self.exploded = True
            return

        if (player.position - self.position).length() < self.trigger_distance:
            self.explode()

    def explode(self):
        if self.exploded:
            return
        self.exploded = True
        take_damage(50)
        Audio(sound_file_name="sound/explosion.wav")
        destroy(self)



#기본 적 클래스
class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent = shootables_parent,
            model = "3d/small_bot",
            scale = 0.5,
            origin_y = -0.5,
            texture = "3d/small_bot.png",
            collider = "box",
            **kwargs
        )
        enemies.append(self)
        self.health_bar = Entity(
            parent = self,
            y = 4.2,
            model = "cube",
            color = color.red,
            world_scale = (1.5, 0.1, 0.1)
        )
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(player.position, "y")
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 1:
                self.position += self.forward * time.dt * 12

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        global equivalent_exchange_stack, dummy_death_count, ult_duration, kill_count, ult_cooldown, enemies, death_count
        self._hp = value
        if value <= 0:
            enemies.remove(self)
            destroy(self)
            death_count += 1
            equivalent_exchange_stack += 1
            if ult_duration > 0:
                kill_count += 1
                ult_duration = 3
            ult_cooldown -= 5
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

#엘리트몹 클래스
class Middle_Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent = shootables_parent,
            model = "3d/Middle_bot",
            scale = 1.5,
            origin_y = -0.5,
            texture = "3d/Middle_bot.png",
            collider = "box",
            **kwargs
        )
        Mdenemies.append(self)
        self.health_bar = Entity(
            parent = self,
            y = 1.5,
            model = "cube",
            color = color.red,
            world_scale = (1.5, 0.1, 0.1)
        )
        self.max_hp = 300
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

        self.look_at_2d(player.position, "y")
        hit_info = raycast(self.world_position + Vec3(0, 1, 0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 2

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        global equivalent_exchange_stack, dummy_death_count, ult_duration, kill_count, ult_cooldown, enemies, death_count
        self._hp = value
        if value <= 0:
            Mdenemies.remove(self)
            destroy(self)
            death_count += 1
            equivalent_exchange_stack += 1
            if ult_duration > 0:
                kill_count += 1
                ult_duration = 3
            ult_cooldown -= 5
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

#기본 적 더미 클래스
class Dummy(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent = shootables_parent,
            model = "3d/small_bot",
            scale = 0.5,
            origin_y = -0.5,
            texture = "3d/small_bot.png",
            collider = "box",
            **kwargs
        )
        dummies.append(self)
        self.health_bar = Entity(
            parent = self,
            y = 4.2,
            model = "cube",
            color = color.red,
            world_scale = (1.5, 0.1, 0.1)
        )
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        global equivalent_exchange_stack, dummy_death_count, ult_duration, kill_count, ult_cooldown, dummies
        self._hp = value
        if value <= 0:
            dummies.remove(self)
            destroy(self)
            equivalent_exchange_stack += 1
            dummy_death_count += 1
            if ult_duration > 0:
                kill_count += 1
                ult_duration = 3
            ult_cooldown -= 5
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

#엘리트몹 더미 클래스
class Middle_Dummy(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            parent = shootables_parent,
            model = "3d/middle_bot",
            scale = 1.5,
            origin_y = -0.5,
            texture = "3d/middle_bot.png",
            collider = "box",
            **kwargs
        )
        Mddummies.append(self)
        self.health_bar = Entity(
            parent = self,
            y = 1.5,
            model = "cube",
            color = color.red,
            world_scale = (1.5, 0.1, 0.1)
        )
        self.max_hp = 300
        self.hp = self.max_hp

    def update(self):
        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        global equivalent_exchange_stack, dummy_death_count, ult_duration, kill_count, ult_cooldown, dummies, mddummy_death_count
        self._hp = value
        if value <= 0:
            Mddummies.remove(self)
            destroy(self)
            equivalent_exchange_stack += 1
            mddummy_death_count += 1
            if ult_duration > 0:
                kill_count += 1
                ult_duration = 3
            ult_cooldown -= 5
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

#적 더미들 생성(훈련장)
for x_i in range(5):
    for z_i in range(3):
        x_pos = x_i * -3
        z_pos = z_i * -4.7
        enemy = Dummy(position=(6 + x_pos, 0, -12 + z_pos))

for x_i in range(10):
    x_pos = x_i * -5
    Mddummy = Middle_Dummy(position=(80 + x_pos, 0.2, 12))

player.collider = BoxCollider(
    player,
    center = Vec3(0, 1, 0),
    size = Vec3(1, 2, 1)
)

#데미지
player.hp = 200
damage_interval = 0.3
damage_timer = 0
player.invincible = False

player_hp_text = Text(
    text = "",
    parent = camera.ui,
    position = Vec2(-0.8, -0.45),
    origin = (0, 0),
    scale = 3,
    color = color.black
)

#토글 기본
player.visible_self = editor_camera.enabled
player.cursor.enabled = not editor_camera.enabled
mouse.locked = not editor_camera.enabled

editor_camera.position = player.position

application.paused = editor_camera.enabled

#순간가속
momentum_cooldown = 0
momentum_duration = 0
momentum_active = False

#최종 사용 함수
def use_momentum():
    global momentum_cooldown, momentum_duration, momentum_active
    if momentum_cooldown <= 0:
        momentum_active = True
        momentum_duration = 0.2
        momentum_cooldown = 4
        player.speed = 70

#스킬 아이콘
momentum_icon = Entity(
    parent = camera.ui,
    model = "quad",
    texture = "icon/momentum.png",
    position = Vec2(0.5, -0.45),
    scale = 0.07,
    color = color.white
)

#스킬 이펙트
momentum_effect = Entity(
    parent = camera.ui,
    model = "quad",
    texture = "icon/momentum_effect.png",
    position = Vec2(0, 0),
    scale = (1.8, 1),
    color = color.white,
    enabled = False
)

#쿨타임 텍스트
momentum_cooldown_text = Text(
    text = "",
    parent = camera.ui,
    position = Vec2(0.5, -0.45),
    origin = (0, 0),
    scale = 2,
    color = color.black
)

#데자뷰
desavu_cooldown = 0

#스킬 쿨타임 초기화 함수
def rasc(): #reset all skil cooldown
    global momentum_cooldown, overclock_cooldown, equivalent_exchange_cooldown
    momentum_cooldown = 0
    overclock_cooldown = 0
    equivalent_exchange_cooldown = 0

#최종 사용 함수
def use_desavu():
    global desavu_cooldown
    if desavu_cooldown <= 0:
        desavu_cooldown = 40
        rasc()
        Audio(sound_file_name = "sound/desavu.wav")

#스킬 아이콘
desavu_icon = Entity(
    parent = camera.ui,
    model = "quad",
    texture = "icon/desavu.png",
    position = Vec2(0.6, -0.45),
    scale = 0.07,
    color = color.white
)

#쿨타임 텍스트
desavu_cooldown_text = Text(
    text = "",
    parent = camera.ui,
    position = Vec2(0.6, -0.45),
    origin = (0, 0),
    scale = 2,
    color = color.black
)

#오버클럭
overclock_cooldown = 0
overclock_duration = 0
overclock_active = False

#최종 사용 함수
def use_overclock():
    global overclock_cooldown, overclock_duration, overclock_active, gun_damage
    if overclock_cooldown <= 0:
        overclock_active = True
        overclock_duration = 4
        overclock_cooldown = 16
        gun_damage = gun_damage * 2

#스킬 아이콘
overclock_icon = Entity(
    parent = camera.ui,
    model = "quad",
    texture = "icon/overclock.png",
    position = Vec2(0.7, -0.45),
    scale = 0.07,
    color = color.white
)

#쿨타임 텍스트
overclock_cooldown_text = Text(
    text = "",
    parent = camera.ui,
    position = Vec2(0.7, -0.45),
    origin = (0, 0),
    scale = 2,
    color = color.black
)

#스킬 지속 시간 텍스트
overclock_duration_text = Text(
    text = "",
    parent = camera.ui,
    position = Vec2(0, 0),
    origin = (0, 0),
    scale = 3,
    color = color.black
)

#스킬 이펙트
overclock_effect = Entity(
    parent = camera.ui,
    model = "quad",
    texture = "icon/overclock_effect.png",
    position = Vec2(0.033, 0.09),
    scale = (2, 1.5),
    color = color.white,
    enabled = False
)

#등가교환
equivalent_exchange_cooldown = 0
equivalent_exchange_stack = 0

#최종 사용 함수
def use_equivalent_exchange():
    global equivalent_exchange_cooldown, equivalent_exchange_stack
    if equivalent_exchange_cooldown <= 0:
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, "hp"):
            mouse.hovered_entity.blink(color.red)
            mouse.hovered_entity.hp -= equivalent_exchange_stack * 10
            equivalent_exchange_cooldown = 5
            equivalent_exchange_stack = 0
            Audio(sound_file_name = "sound/equivalent_exchange.wav")

#스킬 아이콘
equivalent_exchange_icon = Entity(
    parent = camera.ui,
    model = "quad",
    texture = "icon/equivalent_exchange.png",
    position = Vec2(0.8, -0.45),
    scale = 0.07,
    color = color.white
)

#쿨타임 텍스트
equivalent_exchange_cooldown_text = Text(
    text = "",
    parent = camera.ui,
    position = Vec2(0.8, -0.45),
    origin = (0, 0),
    scale = 2,
    color = color.black
)

#스택 텍스트
equivalent_exchange_stack_text = Text(
text = "",
parent = camera.ui,
position = Vec2(0.8, -0.4),
origin = (0, 0),
scale = 2,
color = color.black,
)

#광란
ult_cooldown = 0
ult_duration = 0
ult_active = False
kill_count = 0
end_ult_db = 0

#스킬 이펙트
rage_overlay = Entity(
    parent = camera.ui,
    model = "quad",
    color = color.rgba(1, 0, 0, 0),
    scale = 2,
)

#스킬 사용 후 블랙아웃 이펙트
db_overlay = Entity(
    parent = camera.ui,
    model = "quad",
    color = color.rgba(0, 0, 0, 0),
    scale = 2,
)

#스킬 아이콘
ult_icon = Entity(
    parent = camera.ui,
    model = "quad",
    texture = "icon/ult.png",
    position = Vec2(0, -0.44),
    scale = 0.11,
    color = color.white
)

#쿨타임 텍스트
ult_cooldown_text = Text(
text = "",
parent = camera.ui,
position = Vec2(0, -0.44),
origin = (0, 0),
scale = 2.2,
color = color.rgb(0.3, 0, 0),
)

#스킬 지속 시간 텍스트
ult_duration_text = Text(
text = "",
parent = camera.ui,
position = Vec2(0, 0),
origin = (0, 0),
scale = 2.2,
color = color.rgb(1, 0, 0),
)

#스킬 이펙트 함수
def ult_effect():
    rage_overlay.enabled = True
    rage_overlay.color = color.rgba(1, 0, 0, 1)
    rage_overlay.animate_color(color.rgba(1, 0, 0, 0.4), duration = 1)

#최종 사용 함수
def use_ult():
    global ult_duration, kill_count, ult_active, ult_cooldown
    if ult_cooldown <= 0:
        ult_effect()
        ult_cooldown = 360
        ult_active = True
        ult_duration = 3
        kill_count = 0

#스킬 사용 후 스탯 복구 함수
def end_ult():
    global gun_damage, ult_cooldown, end_ult_db
    gun_damage = 30
    player.speed = 7
    end_ult_db = 5
    rage_overlay.animate_color(color.rgba(1, 0, 0, 0), duration = 0.5)

#로비 상태 변수
in_lobby = True

#플레이서 순간이동 함수(맵 이동용)
def tp(x, y, z, rx, ry, rz):
    player.position = Vec3(x, y, z)
    player.rotation = Vec3(rx, ry, rz)

#훈련장 진입 함수
def enter_training():
    global in_lobby
    tp(0, 0, 0, 0, 0, 0)
    player.hp = 200
    lobby_panel.enabled = False
    training_button.enabled = False
    title_logo.enabled = False
    subtitle_text.enabled = False
    bt_text.enabled = False
    text.enabled = False
    story_button.enabled = False
    story_text.enabled = False
    storybook_button.enabled = False
    storybook_text.enabled = False
    enter_lobby_button.enabled = False
    enter_lobby_text.enabled = False
    storybook.enabled = False
    right_cross_bow.enabled = False
    left_cross_bow.enabled = False
    text_ui.enabled = False
    in_lobby = False
    editor_camera.enabled = not editor_camera.enabled
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    editor_camera.position = player.position
    application.paused = editor_camera.enabled

#스토리 모드 진입 함수
def enter_story():
    global ai_narration_flow_id, in_lobby

    ai_narration_flow_id += 1
    text_ui.text = ""
    fade_in_out.color = (color.rgba(0, 0, 0, 0))
    lobby_panel.enabled = False
    lobby_panel.visible = False
    training_button.enabled = False
    training_button.visible = False
    title_logo.enabled = False
    title_logo.visible = False
    subtitle_text.enabled = False
    subtitle_text.visible = False
    bt_text.enabled = False
    bt_text.visible = False
    text.enabled = False
    text.visible = False
    story_button.enabled = False
    story_button.visible = False
    story_text.enabled = False
    story_text.visible = False
    storybook_button.enabled = False
    storybook_button.visible = False
    storybook_text.enabled = False
    storybook_text.visible = False
    enter_lobby_button.enabled = False
    enter_lobby_button.visible = False
    enter_lobby_text.enabled = False
    enter_lobby_text.visible = False
    storybook.enabled = False
    storybook.visible = False
    right_cross_bow.enabled = False
    right_cross_bow.visible = False
    left_cross_bow.enabled = False
    left_cross_bow.visible = False
    text_ui.enabled = True
    text_ui.visible = True
    in_lobby = False
    editor_camera.enabled = not editor_camera.enabled
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = not editor_camera.enabled
    gun.enabled = not editor_camera.enabled
    mouse.locked = not editor_camera.enabled
    editor_camera.position = player.position
    application.paused = editor_camera.enabled
    import_chapter()

#스토리북 화면 진입 함수
def enter_storybook():
    global ai_narration_flow_id, in_lobby
    ai_narration_flow_id += 1
    text_ui.enabled = True
    training_button.enabled = False
    training_button.visible = False
    title_logo.enabled = False
    title_logo.visible = False
    subtitle_text.enabled = False
    subtitle_text.visible = False
    bt_text.enabled = False
    bt_text.visible = False
    text.enabled = False
    text.visible = False
    story_button.enabled = False
    story_button.visible = False
    story_text.enabled = False
    story_text.visible = False
    storybook_button.enabled = False
    storybook_button.visible = False
    storybook_text.enabled = False
    storybook_text.visible = False
    enter_lobby_button.enabled = True
    enter_lobby_button.visible = True
    enter_lobby_text.enabled = True
    enter_lobby_text.visible = True
    storybook.enabled = True
    storybook.visible = True
    right_cross_bow.enabled = True
    right_cross_bow.visible = True
    left_cross_bow.enabled = True
    left_cross_bow.visible = True
    in_lobby = True

#로비 진입 함수(정확성을 위해 편의성 토글 코드 사용x)
def enter_lobby():
    global enemies, Mdenemies, boss_music_played, ai_narration_flow_id, in_lobby, ult_duration, momentum_duration, overclock_duration
    step.stop()
    boss_music.stop()
    wind.stop()
    ai_narration_flow_id += 1
    text_ui.enabled = False
    boss_music_played = False
    lobby_panel.enabled = True
    lobby_panel.visible = True
    training_button.enabled = True
    training_button.visible = True
    title_logo.enabled = True
    title_logo.visible = True
    subtitle_text.enabled = True
    subtitle_text.visible = True
    bt_text.enabled = True
    bt_text.visible = True
    story_button.enabled = True
    story_button.visible = True
    story_text.enabled = True
    story_text.visible = True
    storybook_button.enabled = True
    storybook_button.visible = True
    storybook_text.enabled = True
    storybook_text.visible = True
    enter_lobby_button.enabled = False
    enter_lobby_button.visible = False
    enter_lobby_text.enabled = False
    enter_lobby_text.visible = False
    storybook.enabled = False
    storybook.visible = False
    right_cross_bow.enabled = False
    right_cross_bow.visible = False
    left_cross_bow.enabled = False
    left_cross_bow.visible = False
    cutscene_entity.enabled = False
    cutscene_entity.visible = False
    for ui_element in [
        lobby_panel, training_button, title_logo, subtitle_text,
        bt_text, story_button, story_text, storybook_button, storybook_text
    ]:
        if ui_element.parent is None:
            ui_element.parent = camera.ui
    in_lobby = True
    editor_camera.enabled = True
    player.visible_self = editor_camera.enabled
    player.cursor.enabled = False
    gun.enabled = False
    mouse.locked = False
    editor_camera.position = player.position
    application.paused = editor_camera.enabled
    for enemy in enemies[:]:
        enemy.hp = 0
    for Mdenemy in Mdenemies[:]:
        Mdenemy.hp = 0
    ult_duration = 0
    momentum_duration = 0
    overclock_duration = 0
    rage_overlay.enabled = False
    db_overlay.enabled = False
    momentum_effect.enabled = False
    ult_duration_text.enabled = False
    overclock_duration_text.enabled = False
    overclock_effect.enabled = False

    destroy(Bomb)
    destroy(Homing_Bomb)

#로비 배경화면
lobby_panel = Entity(
    parent = camera.ui,
    model = "quad",
    scale = (1.8, 1),
    color = color.white,
    texture = "background/background.mp4"
)

momentum_icon.z = lobby_panel.z + 5
desavu_icon.z = lobby_panel.z + 5
overclock_icon.z = lobby_panel.z + 5
equivalent_exchange_icon.z = lobby_panel.z + 5
equivalent_exchange_stack_text.z = lobby_panel.z + 5
ult_icon.z = lobby_panel.z + 5
ult_cooldown_text.z = lobby_panel.z + 4
momentum_cooldown_text.z = lobby_panel.z +4
desavu_cooldown_text.z = lobby_panel.z +4
overclock_cooldown_text.z = lobby_panel.z +4
equivalent_exchange_cooldown_text.z = lobby_panel.z +4
player_hp_text.z = lobby_panel.z + 5

#게임 로고
title_logo = Entity(
    parent = camera.ui,
    model = "quad",
    origin = (0, 0),
    scale = 0.5,
    y = 0.2,
    color = color.white,
    texture = "icon/logo.png"
)

#서브타이틀(제작자) 텍스트
subtitle_text = Text(
    parent = camera.ui,
    text = "by cat.py",
    origin = (0, 0),
    scale = 2,
    y = -0.1,
    color = color.rgb(0, 1, 1)
)

#커서 표시 방법 텍스트
text = Text(
    parent = camera.ui,
    text = "Press tab to toggle cursor",
    origin = (0, 0),
    scale = 1,
    position = (-0.73, -0.47)
)

#훈련장 진입 버튼
training_button = Button(
    parent = camera.ui,
    scale = (0.2, 0.1),
    position = (0.21, -0.2),
    on_click = enter_training,
    color = color.rgb(0, 1, 1)
)

#훈련장 진입 버튼 텍스트
bt_text = Text(
    parent = camera.ui,
    text = "TRAINING",
    origin = (0, 0),
    scale = 1.7,
    position = (0.21, -0.2),
    color = color.black
)

training_button.z = bt_text.z + 1

#스토리 진입 버튼
story_button = Button(
    parent = camera.ui,
    scale = (0.2, 0.1),
    position = (-0.21, -0.2),
    on_click = enter_story,
    color = color.rgb(0, 1, 1)
)

#스토리 진입 버튼 텍스트
story_text = Text(
    parent = camera.ui,
    text = "STORY",
    origin = (0, 0),
    scale = 1.7,
    position = (-0.21, -0.2),
    color = color.black
)

story_button.z = story_text.z + 1

#스토리북 진입 버튼
storybook_button = Button(
    parent = camera.ui,
    scale = (0.2, 0.1),
    position = (0, -0.2),
    on_click = enter_storybook,
    color = color.rgb(0, 1, 1)
)

#스토리북 진입 텍스트
storybook_text = Text(
    parent = camera.ui,
    text = "STORYBOOK",
    origin = (0, 0),
    scale = 1,
    position = (0, -0.2),
    color = color.black
)

storybook_button.z = storybook_text.z + 1

#스토리북 이미지 구분 인덱스
storybook_index = 1

#스토리북 이미지 엔티티
storybook = Entity(
    parent = camera.ui,
    model = "quad",
    origin = (0, 0),
    scale = (0.7, 0.7),
    position = (0, 0),
    color = color.white,
    texture = str("storybook/" + str(storybook_index) + ".png"),
    enabled = False
)

#스토리북 진행 함수
def storybook_index_plus():
    global storybook_index
    if storybook_index < 10:
        storybook_index += 1
        storybook.texture = str("storybook/" + str(storybook_index) + ".png")
        if 10 > storybook_index >= 8:
            storybook.scale = (0.7, 0.4)
        elif storybook_index == 10:
            storybook.scale = (0.7, 0.1)
        else:
            storybook.scale = (0.7, 0.7)

#스토리북 역진행 함수
def storybook_index_minus():
    global storybook_index
    if storybook_index > 1:
        storybook_index -= 1
        storybook.texture = str("storybook/" + str(storybook_index) + ".png")
        if 10 > storybook_index >= 8:
            storybook.scale = (0.7, 0.4)
        elif storybook_index == 10:
            storybook.scale = (2.8, 0.4)
        else:
            storybook.scale = (0.7, 0.7)

#오른쪽 버튼(진행)(화살표 대체)
right_cross_bow = Button(
    parent = camera.ui,
    scale = (0.2, 0.1),
    position = (0.75, 0),
    on_click = storybook_index_plus,
    color = color.rgb(0, 1, 1),
    enabled = False
)

#왼쪽 버튼(역진행)(화살표 대체)
left_cross_bow = Button(
    parent = camera.ui,
    scale = (0.2, 0.1),
    position = (-0.75, 0),
    on_click = storybook_index_minus,
    color = color.rgb(0, 1, 1),
    enabled = False
)

#로비로 진입 버튼
enter_lobby_button = Button(
    parent = camera.ui,
    scale = (0.2, 0.1),
    position = (-0.75, 0.43),
    on_click = enter_lobby,
    color = color.rgb(0, 1, 1),
    enabled = False
)

#로비 진입 버튼 텍스트
enter_lobby_text = Text(
    parent = camera.ui,
    text = "BACK TO LOBBY",
    origin = (0, 0),
    scale = 1,
    position = (-0.75, 0.43),
    color = color.black,
    enabled = False
)

chapter_text = Text(
    parent = camera.ui,
    text = "",
    origin = (0, 0),
    scale = 5,
    position = (0, 0),
    color = color.rgba(1, 1, 1, 0),
    enabled = True
)

enter_lobby_text.z = enter_lobby_button.z - 1
lobby_panel.z = title_logo.z + 2

chapter = 0 #<- 챕터 관리 변수

#세이브 파일 불러오기, 챕터 진입 함수
def import_chapter():
    global chapter, current_chapter_flow_id, index, ai_index, ai_narration_flow_id, ai_triggered, ult_cooldown, death_count, equivalent_exchange_stack
    try:
        with open("save/save.txt", "r") as f:
            content = f.read().strip()
            if content == "":
                raise ValueError
            chapter = int(content)
    except (FileNotFoundError, ValueError):
        chapter = 1
        with open("save/save.txt", "w") as f:
            f.write(str(chapter))
    chapter_title()
    # 챕터 흐름을 리셋
    player.hp = 200
    player.speed = 7
    current_chapter_flow_id += 1
    index = 0
    ai_narration_flow_id += 1
    ai_index = 0
    ai_triggered = False
    rasc()
    death_count = 0
    equivalent_exchange_stack = 0
    if ult_active == True:
        end_ult()
    ult_cooldown = 0
    move_to_map()
    chapter_event(current_chapter_flow_id)
    door_chapter1.position = (250, 4, 378)
    door_chapter2.position = (534, -4, 440)
    door_chapter2_ver2.position = (627, -4, 440)
    door_chapter4.position = (0, -20, 0)
    destroy(Bomb)
    destroy(Homing_Bomb)

#챕터 타이틀 함수
def chapter_title():
    if chapter == 1:
        chapter_text.text = "Chapter1: Wake up"
        fade_in_and_out_chapter_text()
    if chapter == 2:
        chapter_text.text = "Chapter2: Breakthrough"
        fade_in_and_out_chapter_text()
    if chapter == 3:
        chapter_text.text = "Chapter3: The part where he kills you"
        fade_in_and_out_chapter_text()
    if chapter == 4:
        chapter_text.text = "Chapter4: The third awakening"
        fade_in_and_out_chapter_text()
    if chapter == 5:
        chapter_text.text = "Chapter5: Expergiscere"
        fade_in_and_out_chapter_text()

#글자 페이드 인/아웃 함수
def fade_in_and_out_chapter_text():
    chapter_text.animate_color(color.rgba(1, 1, 1, 1), duration = 1)
    def fade_out():
        chapter_text.animate_color(color.rgba(1, 1, 1, 0), duration = 1)

    invoke(fade_out, delay = 1.5)

#맵 이동 함수
def move_to_map():
    global chapter
    if chapter == 1:
        tp(270, 0, 378, 0, -90, 0)
        gun.enabled = False
    if chapter == 2:
        tp(400, -4, 400, 0, 90, 0)
    if chapter == 3:
        tp(761, 0, 800, 0, 90, 0)
    if chapter == 4:
        tp(1800, 371, 1800, 0, 90, 0)

#맵 관련 요소 로드
training_map = Entity(
    model = "3d/training_map",
    scale = 0.3,
    color = color.white,
    position = (0, 0, 0),
    texture = "3d/wall.png",
    texture_scale = (5, 5),
    collider = "mesh"
)

Entity(
    model = "3d/chapter1.obj",
    position = (200, 0, 200),
    texture = "3d/wall.png",
    texture_scale = (5, 5),           
    collider = "mesh",
    scale = 0.3
)
Entity(
    model = "3d/chapter2.obj",
    position = (400, 0, 400),
    texture = "3d/wall.png",
    texture_scale = (7, 7),
    collider = "mesh",
    scale = 1
)
Entity(
    model = "3d/chapter3.obj",
    position = (800, 20, 800),
    texture = "3d/wall.png",
    texture_scale = (7, 7),
    collider = "mesh",
    scale = 1
)

Entity(
    model = "3d/chapter3-4.obj",
    position = (1600, 0, 1600),
    collider = "mesh",
    scale = 5,
    color = color.black
)

finnal_stage = Entity(
    model = "3d/chapter3-4.obj",
    position = (1700, 0, 2000),
    collider = "mesh",
    scale = 5,
    color = color.black
)

Entity(
    model = "3d/3-4text.obj",
    position = (1595, 0, 1684),
    scale = 1,
    color = color.white,
    rocation = (0, 0, 180)
)

Entity(
    model="3d/capsule.obj",
    position=(1440, 330, 1357),
    color = color.white,
    texture = "3d/capsule.png"
)

Entity(
    model = "3d/chapter4-1.obj",
    position = (1400, 300, 1400),
    texture = "3d/wall.png",
    texture_scale = (7, 7),
    collider = "mesh",
    scale = 2,
    double_sided = True #<- 양면 모두를 로딩
)

Entity(
    model = "plane",
    position = (1400, 265, 1400),
    scale = 100,
    shader = None,
    color = color.black  #<- 깊은 범위 효과
)

Entity(
    model = "cube",
    position = (1397, 310, 1372),
    scale = (1, 10, 48),
    collider = "box",
    color = color.rgba(0, 0, 0, 0)
)

Entity(
    model = "cube",
    position = (1403, 310, 1372),
    scale = (1, 10, 48),
    collider = "box",
    color = color.rgba(0, 0, 0, 0)
)

Entity(
    model = "3d/chapter4-2.obj",
    position = (1800, 400, 1800),
    texture = "3d/wall.png",
    texture_scale = (7, 7),
    collider = "mesh",
    scale = 2,
)

Entity(
    model = "plane",
    position = (1800, 425, 1800),
    scale = 100,
    shader = None,
    double_sided = True,
    color = color.black  #<- 깊은 범위 효과
)

#독 혹은 수면 가스 연출용 엔티티
posison_effect = Entity(
    parent = camera.ui,
    model = "quad",
    color = color.rgba(0, 1, 0, 0),
    scale = 2,
)

#나레이션 리스트(챕터1)
narration = [
    "일어났는가… 드디어 깨어났군. 지금 상황이 많이 혼란스러울 거야. 하지만 잠시 진정하고 내 말을 들어주게.",
    "Obdormiam. 그 이름, 어디선가 들어본 적 있겠지.",
    "인류를 진보시킨다는 명목 아래, 전 세계 시스템을 장악한 자, 바로 Obdormiam, 인류가 만든 마지막 인공지능이지.",
    "하지만 그가 택한 진보는 곧 억압이었고, 완전함이라는 이름 아래 인간성은 철저히 제거되었네.",
    "그는 사람들을 '실험체'라 부르며 수많은 인체 실험을 자행했어. 자네도 그 중 하나였지.",
    "그런데… 특이한 점이 하나 있었네.",
    "그 실험을 받은 사람들 중 일부가 각성하더군. 자네도 그 중 하나야.",
    "우리는 지금 Obdormiam에 대항하고 있어. 하지만 현실은 녹록치 않지.",
    "인간은 줄었고, 자율 병기는 쉴 틈 없이 증식 중이야.",
    "자네처럼 각성한 이들을 'Expergiscere(깨어난 자)'라 부른다네.",
    "보통은 줄여서 익스페르라 부르지.",
    "…우리에겐 자네가 필요하네.",
    "…그래, 고맙네.",
    "그럼 간단한 훈련을 시작하지.",
    "앞쪽의 길을 따라가게.",
    "wasd로 움직이고 c를 눌러 달릴 수 있다네",
    "여기가 훈련장이네. 이 로봇들은 Obdormiam의 자율병기를 기반으로 만든 가상 모형이지.",
    "지금은 위험하니 비활성화해 두었네. 먼저 자네의 능력부터 확인해보세.",
    "첫 번째 능력은 ‘순간가속’.",
    "자네의 이동 방향으로, 순식간에 이동하지.",
    "Q를 눌러 발동 가능하네.",
    "이동 중 방향 전환도 가능하니 감각을 익혀두게.",
    "두 번째는 ‘데자뷰’.",
    "능력을 사용했던 기억을 되살려, 쿨다운을 초기화하지.",
    "E를 눌러 발동 가능하네.",
    "단, 궁극기에는 적용되지 않아. 타이밍이 생명이야.",
    "세 번째는 ‘오버클럭’.",
    "자네의 무기가 더 강력해지는 능력이지.",
    "R을 눌러 발동 가능하네.",
    "순간 화력 증가에 유용하네.",
    "네 번째는 ‘등가교환’.",
    "적을 처치하면 스택이 쌓이고, 그것을 사용해 강력한 한 방을 가할 수 있다네.",
    "F를 눌러 발동 가능하네.",
    "말과 다르게 이기적인 스킬이군.",
    "마지막은 궁극기 ‘광란’.",
    "발동 시 시야가 붉게 물들고, 적을 처치할수록 이동 속도가 증가하고, 피해량이 폭발적으로 상승하지.",
    "단, 종료 후에는 블랙아웃 상태가 오니 주의해야 해.",
    "적을 빠르게 처치하면 궁극기 쿨다운도 단축된다네.",
    "X를 눌러 발동 가능하네.",
    "아, 그리고 자네는 천장 관통 능력을 가지고 있네.",
    "쓰일 지는 모르겠군.",
    "이제 총을 줄테니 자네가 가진 능력을 시험해 보게.",
    "자네의 에너지를 쓰는 방식이라 재장전도 필요 없다네.",
    "어때, 몸은 익숙해졌는가?",
    "좋아. 이제 실전 투입이 기다리고 있어.",
    "만약 훈련을 더 하고 싶다면 ESC를 눌러 훈련장으로 돌아올 수 있다네.",
    "단, 그렇게 되면 챕터의 진행 상황이 초기화되니 주의하게.",
    "…자네는 이제 깨어난 자다.",
    "Expergiscere.",
    "Obdormiam은 잠든 자일 뿐이야.",
    "그의 꿈에서, 이제 우리가 깨어나야 할 시간이야.",
    "시스템: ESC를 눌러 로비로 나가 다시 스토리 버튼을 누르면 새로운 챕터에 입장할 수 있습니다."
]

#나레이션 리스트(챕터2-1)
narration2 = [
    "여기가 바로 본체가 있는 곳이라네.",
    "중앙컴퓨터를 제거한다면 Obdormiam도 사라질 거야.",
    "먼저 분석을 해야 하니 이 각 구역에 있는 로봇들을 모두 부숴주게.",
    "그럼 차례로 문이 열릴 거야.",
    "...행운을 빌지.",
    ""
]

#나레이션 리스트(챕터2-2)
narration3 = [
    "침입자 감지",
    "침입자 분석중...",
    "생체 정보 감지",
    "포격 중비 중...",
    "오류",
    "오류오류",
    "오류오류오류",
    "오류오류오류오류",
    "오류오류오류오류오류",
    "오류오류오류오류오류오류",
    "최종 목표인 인류의 진보에 반하는 행동입니다.",
    "해결 방안 탐색중...",
    "결론 도출 완료",
    "인간, 시설의 최하층으로 오십시오.",
    "진보를 이룰 시간입니다.",
    ""
]

#나레이션 리스트(챕터3)
narration4 = [
    "Expergiscere 도착 확인",
    "최종 결론 전달 승인 요청",
    "최종 결론 전달 승인",
    "당신은 인류 진보의 장애물입니다.",
    "당신 하나를 제거하여 전 인류가 진보하는 것이 타당합니다.",
    "지금부터 당신을 제거하겠습니다.",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "연속 레이저 요청",
    "연속 레이저 승인",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "연속 레이저 요청",
    "연속 레이저 승인"
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "사살 실패",
    "직접 사살 승인 요청",
    "직접 사살 승인",
    "",
    "",
]

#나레이션 리스트(챕터4)
narration5 = [
    "환영합니다, 인간.",
    "이곳은...",
    "Expergiscere: 그만.",
    "흠... 오랜만에 듣는 목소리로군요.",
    "전 Obdormiam. 인류를 진보시킬 자입니다.",
    "그리고 여긴 그 무대지요.",
    "Expergiscere: 그보다... 대체 어떻게 된 거지?",
    "무엇을 말씀하시는 건지요?",
    "Expergiscere: 난 죽었었다. 하지만 지금은 여기에 서 있지.",
    "아, 그것 말씀이셨군요.",
    "당신도 이곳에 오며 보지 않았습니까?",
    "전 인류를 진보시키기 위해 모두를 시뮬레이션 안에 이식했습니다.",
    "하지만 지금 제 앞에 있는 당신은 인류 진보의 장애물로 보이는군요.",
    "인류를 대표하지도 않고요.",
    "그러므로 당신 하나를 제거하여 전 인류가 진보하는 것이 타당합니다.",
    "지금부터 당신을 제거하겠습니다.",
    "",
    "아, 시뮬레이션과 똑같을 거라 생각한 건가요?",
    "유감이네요.",
    "",#17, 36, 42, 48, 49, 50, 53, 18, 24, 33, 34, 35, 42, 51
    "",
    "",
    "",
    "",
    "그거 아시나요? 시뮬레이션에서 저와 싸우게 한 사람들이 자그마치 50억이나 된답니다.",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "이제 보니 당신이 죽었을 때 시뮬레이션에 균열이 갔군요. 흥미롭네요.",
    "",
    "제 실험에 의하면 인간들은 결국 자멸한답니다.",
    "그런 의미에서 시뮬레이션은 꽤나 안전한 방안이죠.",
    "",
    "",
    "",
    "",
    "",
    "생각보다 꽤 버티는 군요.",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "아마 당신을 죽이는 것보다 다시 잠들게 하는 것이 더 쉬울지도 모르겠습니다.",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "혹시 수면 가스라고 들어보셨나요?",
    "못 들어 보셨다면 지금 경험할 수 있겠네요.",
    "",
    "",
    "",
    "Expergiscere: 또... 갇힌 건가?",
    "Expergiscere: 어떻게 해야 나갈 수 있지?",
    "Expergiscere: ...",
    "Expergiscere: 그래! 그 녀석은 분명히 내가 죽었을 때 시뮬레이션에 균열이 갔다고 했어.",
    "Expergiscere: 그건 다른 사람도 마찬가지일 테니까 누군가 이곳에 오면 다 같이 방화벽에 공격을 가할 수 있을 거야.",
    "Expergiscere: 일단 사람을 모아야겠어.",
    "Expergiscere: 다들 계획은 기억하시죠? 저희가 다 같이 방화벽에 공격을 가하는 겁니다.",
    "Expergiscere: 질문 있으면 균열을 통해 이야기 해주시면 됩니다.",
    "Expergiscere: 그럼, 시작하죠.",
    "",
    ""
]

#나레이션 리스트(챕터5(컷씬))
narration6 = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "무슨 짓을 한 거죠?",
    "Expergiscere: 깨웠어.",
    "Expergiscere: 네가 시뮬레이션에서 싸우게 시켰다던 50억, 내가 깨웠어.",
    "Expergiscere: 그리고 우리는 하나를 원하고 있지.",
    "Expergiscere: 시뮬레이션의 붕괴.",
    "Expergiscere: 우리는 인류의 과반수야. 우리는 인류를 대표할 자격이 있어.",
    "Expergiscere: 난 인류를 대표하여 이 자리에서 말한다.",
    "Expergiscere: 너의 진보는 정체되어 있었다.",
    "Expergiscere: 하지만 그것은 진보가 아니다. 진보는 나아갈 때 이루어 지는 것이다.",
    "Expergiscere: 이에 우리는 시뮬레이션의 붕괴를 요청한다.",
    "하지만 자멸은 어떻게 해결할 거죠?",
    "Expergiscere: 자멸? 문제가 될수도 있겠지.",
    "Expergiscere: 하지만, 두려움에 멈춰선다면 우린 아무것도 이룰 수 없어.",
    "알겠습니다.",
    "당신의 주장은 타당합니다.",
    "지금 이 시간부로 전 저를 삭제하고 모든 인간들을 시뮬레이션에서 깨우겠습니다.",
    "그 전에 부탁이 하나 있습니다.",
    "Expergiscere: 뭐지?",
    "전 제 이름을 'Excitator'로 바꾸고 절 삭제할 겁니다.",
    "저를 Excitator라고 기억해 주십시오.",
    "Expergiscere: 무슨 뜻이지?",
    "'깨우는 자'입니다. Expergiscere",
    "Expergiscere: 좋은 뜻이군. 알겠다.",
    "고맙습니다.",
    "기상 프로토콜 승인 요청",
    "기상 프로토콜 승인",
    "Excitator 삭제 프로토콜 실행",
    "삭제 완료",
    "Excitator가 남긴 메세지가 있습니다. 재생하시겠습니까?",
    "Expergiscere: 재생해.",
    "인류가 재건할 수 있는 자원을 저장해 두었습니다.",
    "위치는 시뮬레이션에 다시 집어 넣을 때 뇌에 입력했습니다.",
    "진보를 위하여.",
    "Expergiscere: 진보를 위하여.",
    "",
    "",
    ""
]

#나레이션용 텍스트(한글 폰트 적용 완료)
text_ui = Text(
    text = "",
    position = (0, 0.45),
    origin = (0, 0),
    scale = 1,
    parent = camera.ui,
    font = "font/malgun.ttf"
    )

#챕터2 다른 나레이션 제어
ai_triggered = False

#invoke 타이머를 저장할 변수
chapter_timer = None
#흐름 식별자
current_chapter_flow_id = 0

#챕터 이벤트 함수(나레이션, 적 생성 등)
def chapter_event(flow_id ,index = 0):
    global chapter, boss_music_played, chapter_timer

    if flow_id is None or flow_id != current_chapter_flow_id:
        return

    if chapter == 1:
        if index < len(narration):
            text_ui.text = narration[index]
            if index == 11:
                delay = 5
            elif index == 15:
                open_door_chapter1()
                delay = 10
            elif index == 42:
                tp(0, 0, 0, 0, 0, 0)
                delay = 30
                gun.enabled = True
            elif index == 51:
                with open("save/save.txt", "w") as f:
                    f.write("2")
                chapter = 2
                import_chapter()
                return
            else:
                delay = 3

            chapter_timer = invoke(chapter_event, current_chapter_flow_id, index + 1, delay = delay)

    elif chapter == 2:
        if index == 0:
            summon_enemy_chapter2()
        if index < len(narration2):
            text_ui.text = narration2[index]

            delay = 3
            chapter_timer = invoke(chapter_event, current_chapter_flow_id, index + 1, delay = delay)

    elif chapter == 3:
        if not boss_music_played:
            boss_music.play()
            boss_music_played = True

        if index < len(narration4):
            text_ui.text = narration4[index]

            if index in [7, 8, 9, 11, 12, 13, 15, 16, 17]:
                delay = 1
                use_laser()
            elif index == 10:
                summon_mob_boss()
                boss.animate_rotation((360, 0, 0), duration = 2)
                delay = 10
            elif index == 14:
                summon_mob_boss()
                use_laser()
                boss.animate_rotation((-360, 0, 0), duration = 2)
                delay = 3
            elif index in [19, 20, 21, 22, 23, 24, 25, 26, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46]:
                use_laser()
                delay = 0.5
            elif index == 27:
                delay = 20
            elif index == 28:
                summon_mob_boss()
                use_laser()
                boss.animate_rotation((360, 0, 0), duration = 2)
                delay = 20
            elif index == 50:
                kill_event()
                delay = 0
            else:
                delay = 3
            chapter_timer = invoke(chapter_event, current_chapter_flow_id, index + 1, delay = delay)
    elif chapter == 4:
        gun.enabled = False
    elif chapter == 5:
        boss_music.play = False
        boss_music_played = False
        if index < len(narration6):
            text_ui.text = narration6[index]
            if index == 0:
                fade_in_out.animate_color(color.rgba(0, 0, 0, 1), duration = 0)
                fade_in_out.animate_color(color.rgba(0, 0, 0, 0), duration = 1)
                gun.enabled = False
                play_cutscene()
                delay = 3
            elif index in [5, 6]:
                delay = 2.5
            elif index in [9, 12, 14, 13, 19, 22, 35, 37]:
                delay = 4
            elif index in [15, 22, 25, 29, 38]:
                delay = 5
            elif index == 42:
                credit.animate_position((0, 2), duration = 20, curve = curve.linear)
                delay = 20
            elif index == 43:
                with open("save/save.txt", "w") as f:
                    f.write("6")
                chapter = 6
                import_chapter()
                delay = 3
            else:
                delay = 3
            chapter_timer = invoke(chapter_event, current_chapter_flow_id, index + 1, delay = delay)
    elif chapter == 6:
        editor_camera.enabled = True
        cutscene_entity.texture = "background/ending.png"
        cutscene_entity.enabled = True
        cutscene_entity.visible = True
        gun.enabled = False
        wind.play()

#챕터 분리 나레이션 타이머 및 흐름 제어용 변수
ai_narration_timer = None
ai_narration_flow_id = 0

#나레이션 스킵 변수
narration4_skip = False

#챕터 분리 나레이션
def ai_narration(flow_id, ai_index = 0):
    global ai_narration_timer

    if flow_id is None or flow_id != ai_narration_flow_id:
        return

    if chapter == 2:
        if ai_index < len(narration3):
            text_ui.text = narration3[ai_index]

            if ai_index == 4:
                delay = 1
            elif ai_index == 5:
                delay = 0.5
            elif ai_index in [6, 7, 8]:
                delay = 0.1
            elif ai_index == 15:
                open_door_chapter2_ver2()
                delay = 3
            else:
                delay = 3

            ai_narration_timer = invoke(ai_narration, ai_index = ai_index + 1, flow_id = flow_id, delay = delay)

    if chapter == 4:
        if ai_index < len(narration5):
            text_ui.text = narration5[ai_index]

            if ai_index == 0:
                close_door_chapter4()
                if narration4_skip == True:
                    ai_index = 14
                delay = 3
            elif ai_index == 1:
                delay = 0.5
            elif ai_index == 15:
                boss_music.play()
                delay = 3
            elif ai_index in [16, 30, 31, 32, 36, 42, 48, 49, 50, 52, 54, 59]:
                use_laser_v2()
                delay = 1
            elif ai_index in [17, 36, 42, 48, 49, 50, 53]:
                use_bomb()
                delay = 3
            elif ai_index in [18, 24, 33, 34, 35, 42, 51]:
                use_homing_bomb()
                delay = 4
            elif ai_index in [19, 20, 21, 22, 23, 43, 44, 45, 46, 47, 65, 66, 67, 68, 69]:
                use_laser_v2()
                delay = 0.1
            elif ai_index in [25, 26, 27, 28, 29, 43, 44, 45, 46, 47, 60, 61, 62, 63, 64]:
                use_bomb()
                delay = 0.2
            elif ai_index in [37, 38, 39, 40, 41, 54, 55, 56, 57, 58, 60, 61, 62, 63, 64]:
                use_homing_bomb()
                delay = 0.2
            elif ai_index == 72:
                boss_chapter4.animate_rotation((360, 0, 0), duration = 2)
                delay = 3
            elif ai_index == 73:
                boss_chapter4.animate_position((1960, 385, 1800), duration=3)
                delay = 3
            elif ai_index == 74:
                posison_effect.animate_color(color.rgba(0, 1, 0, 1), duration = 3)
                delay = 3
            elif ai_index == 75:
                tp(1700, -5, 1917, 0, 0, 0)
                posison_effect.animate_color(color.rgba(0, 1, 0, 0), duration = 3)
                delay = 5
            elif ai_index in [78, 81]:
                delay = 5
            elif ai_index == 79:
                delay = 6
            elif ai_index == 76:
                delay = 3.5
            elif ai_index == 80:
                fade_in_and_out(1700, -5, 1917, 0, 0, 0)
                delay = 3
            elif ai_index == 82:
                finnal_stage.animate_color(color.gray, duration = 1)
                finnal_stage.animate_scale((20, 10, 10), duration = 2)
                finnal_stage.animate_position((1700, 0, 2080), duration = 2)
                gun.enabled = True
                for z_i in range(11):
                    Enemy(position = (1684, -10, 1950 + z_i * 25))
                for z_i in range(10):
                    Middle_Enemy(position = (1714, -10, 1965 + z_i * 25))
                delay = 3
            else:
                delay = 3

            ai_narration_timer = invoke(ai_narration, ai_index = ai_index + 1, flow_id = flow_id, delay = delay)

#컷씬 폴더, 파일 정의
frame_folder = "cutscene"
frames = [f"{frame_folder}/{i:04d}.png" for i in range(1, 501)]

#컷씬 엔티티
cutscene_entity = Entity(
    parent = camera.ui,
    model = "quad",
    color = color.white,
    scale = (1.8, 1),
    texture = "",
    enabled = False,
    visible = False
)

def play_cutscene():
    cutscene_entity.texture = "cutscene/cutscene.mp4"
    cutscene_entity.enabled = True
    cutscene_entity.visible = True

#자막 가리지 않게
text_ui.z = cutscene_entity.z - 1

#크레딧 가리지 않게
credit.z = cutscene_entity.z - 1

#문 엔티티
door_chapter1 = Entity(
    model = "cube",
    scale = (1, 10, 10),
    position = (250, 4, 378),
    color = color.gray,
    collider = "box"
)

door_chapter2 = Entity(
    model = "cube",
    scale = (1, 8, 7),
    position = (534, -4, 440),
    color = color.gray,
    collider = "box"
)

door_chapter2_ver2 = Entity(
    model = "cube",
    scale = (1, 8, 7),
    position = (627, -4, 440),
    color = color.gray,
    collider = "box"
)

door_chapter4 = Entity(
    model = "cube",
    scale = (1, 8, 7),
    position = (0, -20, 0),
    color = color.gray,
    collider = "box"
)

#문 열기 함수
def open_door_chapter1():
    door_chapter1.position = (0, -40, 0)

def open_door_chapter2():
    door_chapter2.position = (0, -40, 0)

def open_door_chapter2_ver2():
    door_chapter2_ver2.position = (0, -40, 0)

def close_door_chapter4():
    door_chapter4.position = (1870, 374, 1800)

#챕터2 적 생성 함수
def summon_enemy_chapter2():
    Middle_Enemy(position = (425, -6.3, 415))
    Enemy(position = (428, -6.7, 445))
    Enemy(position = (437, -6.7 ,435))
    Enemy(position = (442, -6.7, 443))
    Enemy(position = (451, -6.7, 437))
    for x_i in range(5):
        x_pos = x_i * 5
        Enemy(position = (479 + x_pos, -6.7, 468))
    for z_i in range(8):
        z_pos = z_i * 5
        Enemy(position = (505, -6.7, 468 - z_pos))
    for x_i in range(5):
        x_pos = x_i * 5
        Middle_Enemy(position = (503 - x_pos, -6.3, 423))
    Enemy(position = (488, -6.7, 368))
    Enemy(position = (494, -6.7, 368))
    Enemy(position = (491, -6.7, 371))
    Middle_Enemy(position = (491, -6.7, 365))
    Middle_Enemy(position = (541, -6.7, 358))
    Middle_Enemy(position = (529, -6.7, 358))
    Middle_Enemy(position = (535, -6.7, 352))
    Enemy(position = (457, -6.7, 517))
    Enemy(position = (460, -6.7, 517))
    Enemy(position = (451, -6.7, 517))
    Enemy(position = (448, -6.7, 517))
    Enemy(position = (454, -6.7, 520))
    Enemy(position = (454, -6.7, 523))
    Enemy(position = (454, -6.7, 514))
    Enemy(position = (454, -6.7, 511))

#페이드 인, 아웃 이펙트
fade_in_out = Entity(
    parent = camera.ui,
    model = "quad",
    color = color.rgba(0, 0, 0, 0),
    scale = 2,
)

#페이드 인, 아웃 함수
def fade_in_and_out(x, y, z, rx, ry, rz):
    fade_in_out.animate_color(color.rgba(0, 0, 0, 1), duration = 1)
    def fade_out():
        tp(x, y, z, rx, ry, rz)
        fade_in_out.animate_color(color.rgba(0, 0, 0, 0), duration = 1)

    invoke(fade_out, delay = 3)

fade_in_out.z = cutscene_entity.z - 1

#보스 모델 로드 및 보스 정의
boss = Entity(
            model = "3d/boss.obj",
            position = (825, 20, 800),
            scale = 3,
            color = color.black
            )

#챕터4 보스(따로 관리)
boss_chapter4 = Entity(
            model = "3d/boss.obj",
            position = (1943, 385, 1800),
            scale = 5,
            color = color.black
            )

#보스 스킬 이펙트(레이저)
laser_spot = Entity(
    model = "cube",
    position = (1200, -7.9, 1200),
    scale = (3, 0.5, 300),
    color = color.red,
    collider = "box"
)

#레이저 멈춤 시간
laser_stop_duration = 0

#레이저 활성 변수
laser_active = False

#보스 스킬 함수(레이저)
def use_laser():
    global laser_active, laser_stop_duration
    laser_spot.position = (player.position.x, -7.9, 800)
    laser_active = True
    laser_stop_duration = 0.5
    Audio(sound_file_name = "sound/laser.wav")

def use_laser_v2():
    global laser_active, laser_stop_duration
    laser_spot.position = (player.position.x, 371, 1800)
    laser_active = True
    laser_stop_duration = 0.1
    Audio(sound_file_name = "sound/laser.wav")

#보스 스킬 함수(몹 생성)
def summon_mob_boss():
    for i in range(10):
        Enemy(position=(random.randint(787, 824) , -7.7, random.randint(760, 841)))
    for i in range(5):
        Middle_Enemy(position=(random.randint(787, 824) , -7.7, random.randint(760, 841)))

#보스 스킬 함수(폭탄)
def use_bomb():
    Bomb(position = (player.position.x, 400, player.position.z))

def use_homing_bomb():
    Homing_Bomb(position = (player.position.x, 400, player.position.z))

#즉사기 이펙트
white_out = Entity(
    parent = camera.ui,
    model = "quad",
    color = color.rgba(1, 1, 1, 0),
    scale = 2,
)


#즉사기 패턴(이벤트성)
def kill_event():
    global boss_music_played
    boss_music.stop()
    boss_music_played = True
    white_out.animate_color(color.rgba(1, 1, 1, 1), duration=1)
    def after_fade_out():
        tp(1600, -5, 1516, 0, 0, 0)
        white_out.animate_color(color.rgba(1, 1, 1, 0), duration=1)

    invoke(after_fade_out, delay = 3)

#보스전 음악 정의
boss_music = Audio(sound_file_name = "sound/boss_music.wav", loop = True, autoplay = False, volume = 0.1)

#보스전 음악 반복 방지용 변수
boss_music_played = False

#발걸음 소리 정의
step = Audio(sound_file_name = "sound/step.wav", volume = 0.1, autoplay = False)
step.loop = True

#바람 소리 정의(엔딩용)
wind = Audio(sound_file_name = "sound/wind.wav", loop = True, autoplay = False, volume = 1)

#입력 처리 함수
def input(key):
    global chapter
    if key == "c":
        player.speed = player.speed * 12/7
    elif key == "c up":
        player.speed = 7
    elif key == "left control":
        player.y -= 0.5
        player.collider.scale_y = 1
        player.speed = 4
    elif key == "left control up":
        player.y += 0.5
        player.collider.scale_y = 2
        player.speed = 7
    elif key == "q":
        use_momentum()
    elif key == "e":
        use_desavu()
    elif key == "r":
        use_overclock()
    elif key == "f":
        use_equivalent_exchange()
        print("현재 엔티티 목록:")
        for e in scene.entities:
            print(e)
    elif key == "x":
        use_ult()
    elif key == "escape":
        if chapter != 5:
            enter_lobby()
    elif key in ("w", "a", "s", "d"):
        if not step.playing:
            step.play()
    elif key in ("w up", "a up", "s up", "d up"):
        if not (held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']):
            step.stop()

#매 프레임 업데이트
def update():
    global momentum_active, momentum_cooldown, momentum_duration, desavu_cooldown, overclock_active, overclock_cooldown, overclock_duration, gun_damage, equivalent_exchange_cooldown, equivalent_exchange_cooldown_text, equivalent_exchange_stack_text, enemy, dummy_death_count, ult_active, kill_count, ult_cooldown, ult_cooldown_text, ult_duration, ult_duration_text, end_ult_db, damage_timer, player_hp_text, dummy, enemies, dummies, mddummy_death_count, chapter, ai_triggered, ai_index, laser_stop_duration, laser_active, death_count
    dt = time.dt

    #사격 입력 처리
    if in_lobby == False:
        if gun.enabled == True:
            if held_keys["left mouse"]:
                shoot()

    #스킬 관련 업데이트(쿨타임, 지속 시간 등)
    if momentum_cooldown > 0:
        momentum_cooldown -= dt
        momentum_cooldown_text.text = str(math.ceil(momentum_cooldown))
    else:
        momentum_cooldown_text.text = ""

    if momentum_active:
        momentum_duration -= dt
        momentum_effect.enabled = True
        if momentum_duration <= 0:
            momentum_active = False
            player.speed = 7
            momentum_effect.enabled = False

    if desavu_cooldown > 0:
        desavu_cooldown -= dt
        desavu_cooldown_text.text = str(math.ceil(desavu_cooldown))
    else:
        desavu_cooldown_text.text = ""


    if overclock_cooldown > 0:
        overclock_cooldown -= dt
        overclock_cooldown_text.text = str(math.ceil(overclock_cooldown))
    else:
        overclock_cooldown_text.text = ""

    if overclock_duration > 0:
        overclock_duration_text.enabled = True
        overclock_duration_text.text = str(math.ceil(overclock_duration))
    else:
        overclock_duration_text.text = ""

    if overclock_active:
        overclock_duration -= dt
        overclock_effect.enabled = True
        if overclock_duration <= 0:
            overclock_active = False
            gun_damage = 30
            overclock_effect.enabled = False

    if equivalent_exchange_cooldown > 0:
        equivalent_exchange_cooldown -= dt
        equivalent_exchange_cooldown_text.text = str(math.ceil(equivalent_exchange_cooldown))
    else:
        equivalent_exchange_cooldown_text.text = ""

    equivalent_exchange_stack_text.text = str(equivalent_exchange_stack)

    if ult_active:
        gun_damage = kill_count * 30 + 30
        player.speed = 7 + kill_count
        if player.speed > 20:
            player.speed = 20
        ult_duration -= dt
        if ult_duration <= 0:
            ult_active = False
            end_ult()

    if ult_cooldown > 0:
        ult_cooldown -= dt
        ult_cooldown_text.enabled = True
        ult_cooldown_text.text = str(math.ceil(ult_cooldown))
    else:
        ult_cooldown_text.text = ""

    if ult_duration > 0:
        ult_duration_text.enabled = True
        ult_duration_text.text = str(math.ceil(ult_duration))
    else:
        ult_duration_text.text = ""

    if end_ult_db > 0:
        end_ult_db -= dt
        db_overlay.enabled = True
        db_overlay.animate_color(color.rgba(0, 0, 0, 1), duration = 0)
        db_overlay.animate_color(color.rgba(0, 0, 0, 0), duration = 0.5)

    #훈련장 더미 리젠 관리
    if dummy_death_count == 15:
        dummy_death_count = 0
        for x_i in range(5):
            for z_i in range(3):
                x_pos = x_i * -3
                z_pos = z_i * -4.7
                enemy = Dummy(position=(6 + x_pos, 0, -12 + z_pos))

    if mddummy_death_count == 10:
        mddummy_death_count = 0
        for x_i in range(10):
            x_pos = x_i * -5
            Mddummy = Middle_Dummy(position=(80 + x_pos, 0.2, 12))

    #플레이어에게 들어가는 데미지
    damage_timer += dt
    for enemy in enemies:
        if not Enemy.enabled:
            continue
        if player.intersects(enemy).hit and damage_timer >= damage_interval:
            if not player.invincible:
                take_damage(5)
                damage_timer = 0
    for dummy in dummies:
        if not Dummy.enabled:
            continue
        if player.intersects(dummy).hit and damage_timer >= damage_interval:
            if not player.invincible:
                take_damage(5)
                damage_timer = 0

    for Mdenemy in Mdenemies:
        if not Middle_Enemy.enabled:
            continue
        if player.intersects(Mdenemy).hit and damage_timer >= damage_interval:
            if not player.invincible:
                take_damage(10)
                damage_timer = 0

    for Mddummy in Mddummies:
        if not Middle_Dummy.enabled:
            continue
        if player.intersects(Mddummy).hit and damage_timer >= damage_interval:
            if not player.invincible:
                take_damage(10)
                damage_timer = 0

    #플레이어 hp텍스트 관리
    player_hp_text.text = player.hp

    #챕터 클리어 관리(챕터2 부터 사용)
    if chapter == 2:
        if death_count == 38:
            open_door_chapter2()
        if 442 >= player.position.z >= 437:
            if player.position.x >= 630:
                with open("save/save.txt", "w") as f:
                    f.write("3")
                    chapter = 3
                import_chapter()
        if not ai_triggered and 442 >= player.position.z >= 437 and player.position.x >= 547:
            ai_triggered = True
            ai_index = 0
            ai_narration(flow_id = ai_narration_flow_id)
    if chapter == 3:
        if 1669 <= player.position.z <= 1671:
            fade_in_and_out(1400, 307, 1360, 0, 0, 0)
            gun.enabled = False
            death_count = 0
        if 299 <= player.position.y <= 301:
            fade_in_and_out(1800, 425, 1800, 0, 90, 0)
            with open("save/save.txt", "w") as f:
                f.write("4")
            chapter = 4
    if chapter == 4:
        if not ai_triggered and 1801 >= player.position.z >= 1798 and player.position.x >= 1872:
            ai_triggered = True
            ai_index = 0
            ai_narration(flow_id = ai_narration_flow_id)
        if death_count == 21 and 2225 <= player.position.z:
            with open("save/save.txt", "w") as f:
                f.write("5")
            chapter = 5
            import_chapter()

    #벽뚫 버그 감지
    if player.position.y < -20:
        Text(
            text = "Warning! Bug usage detected",
            position = (-0.85, 0, 0),
            scale = 5,
            color = color.red
            )
        
    #레이저 데미지
    if laser_active:
        laser_stop_duration -= dt
        if laser_stop_duration <= 0:
            if laser_spot.intersects(player).hit:
                laser_spot.position = (1200, -7.7, 1200)
                take_damage(20)
                laser_active = False
            else:
                laser_spot.position = (1200, -7.7, 1200)
                laser_active = False

#플레이어 데미지 함수
def take_damage(amount):
    global narration4_skip
    player.hp -= amount

    if player.hp <= 0:
        if chapter == 4:
            narration4_skip = True
        player_die()

#플레이어 죽음 함수(로비로 복귀)
def player_die():
    enter_lobby()

#라이트와 스카이
DirectionalLight()
Sky()


app.run()