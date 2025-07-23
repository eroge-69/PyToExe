from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QFileSystemWatcher
import requests
import pymem
import pymem.process
import win32api
import win32con
import win32gui
import json
import os
import sys
import time
from PySide6.QtGui import QKeySequence, QShortcut
import threading

PUBCHEAT_CONFIG_DIR = os.path.join(os.environ['LOCALAPPDATA'], 'temp', 'PubCheat')
PUBCHEAT_CONFIG_FILE = os.path.join(PUBCHEAT_CONFIG_DIR, 'pubcheat_config.json')
PUBCHEAT_DEFAULT_SETTINGS = {
    "esp_rendering": 1,
    "esp_mode": 1,
    "line_rendering": 1,
    "hp_bar_rendering": 1,
    "head_hitbox_rendering": 1,
    "bons": 1,
    "nickname": 1,
    "radius": 50,
    "weapon": 1,
    "bomb_esp": 1
}
pubcheat_BombPlantedTime = 0
pubcheat_BombDefusedTime = 0

PISTOL_WEAPON_INDICES = {32, 61, 4, 2, 36, 30, 63, 1, 3, 64}  # All pistol indices from pubcheat_get_weapon_name_by_index

def pubcheat_load_settings():
    if not os.path.exists(PUBCHEAT_CONFIG_DIR):
        os.makedirs(PUBCHEAT_CONFIG_DIR)
    if not os.path.exists(PUBCHEAT_CONFIG_FILE):
        with open(PUBCHEAT_CONFIG_FILE, "w") as f:
            json.dump(PUBCHEAT_DEFAULT_SETTINGS, f, indent=4)
    with open(PUBCHEAT_CONFIG_FILE, "r") as f:
        return json.load(f)

def pubcheat_get_offsets_and_client_dll():
    pubcheat_offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
    pubcheat_client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
    return pubcheat_offsets, pubcheat_client_dll

def pubcheat_get_window_size(window_title):
    pubcheat_hwnd = win32gui.FindWindow(None, window_title)
    if pubcheat_hwnd:
        pubcheat_rect = win32gui.GetClientRect(pubcheat_hwnd)
        return pubcheat_rect[2], pubcheat_rect[3]
    return None, None

def pubcheat_w2s(mtx, posx, posy, posz, width, height):
    pubcheat_screenW = (mtx[12] * posx) + (mtx[13] * posy) + (mtx[14] * posz) + mtx[15]
    if pubcheat_screenW > 0.001:
        pubcheat_screenX = (mtx[0] * posx) + (mtx[1] * posy) + (mtx[2] * posz) + mtx[3]
        pubcheat_screenY = (mtx[4] * posx) + (mtx[5] * posy) + (mtx[6] * posz) + mtx[7]
        pubcheat_camX = width / 2
        pubcheat_camY = height / 2
        pubcheat_x = pubcheat_camX + (pubcheat_camX * pubcheat_screenX / pubcheat_screenW)
        pubcheat_y = pubcheat_camY - (pubcheat_camY * pubcheat_screenY / pubcheat_screenW)
        return [int(pubcheat_x), int(pubcheat_y)]
    return [-999, -999]

class PubCheatOverlay(QtWidgets.QWidget):
    def __init__(self, pubcheat_settings):
        super().__init__()
        self.pubcheat_settings = pubcheat_settings
        self.setWindowTitle('ExPa Version 2.1 @ made by G3R')
        self.pubcheat_window_width, self.pubcheat_window_height = pubcheat_get_window_size("Counter-Strike 2")
        if self.pubcheat_window_width is None or self.pubcheat_window_height is None:
            print("Fout: spelvenster niet gevonden.")
            sys.exit(1)
        self.setGeometry(0, 0, self.pubcheat_window_width, self.pubcheat_window_height)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        pubcheat_hwnd = self.winId()
        win32gui.SetWindowLong(pubcheat_hwnd, win32con.GWL_EXSTYLE, win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

        self.pubcheat_file_watcher = QFileSystemWatcher([PUBCHEAT_CONFIG_FILE])
        self.pubcheat_file_watcher.fileChanged.connect(self.pubcheat_reload_settings)

        self.pubcheat_offsets, self.pubcheat_client_dll = pubcheat_get_offsets_and_client_dll()
        self.pubcheat_pm = pymem.Pymem("cs2.exe")
        self.pubcheat_client = pymem.process.module_from_name(self.pubcheat_pm.process_handle, "client.dll").lpBaseOfDll

        self.pubcheat_scene = QtWidgets.QGraphicsScene(self)
        self.pubcheat_view = QtWidgets.QGraphicsView(self.pubcheat_scene, self)
        self.pubcheat_view.setGeometry(0, 0, self.pubcheat_window_width, self.pubcheat_window_height)
        self.pubcheat_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.pubcheat_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.pubcheat_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.pubcheat_view.setStyleSheet("background: transparent;")
        self.pubcheat_view.setSceneRect(0, 0, self.pubcheat_window_width, self.pubcheat_window_height)
        self.pubcheat_view.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.pubcheat_timer = QtCore.QTimer(self)
        self.pubcheat_timer.timeout.connect(self.pubcheat_update_scene)
        self.pubcheat_timer.start(0)

        self.pubcheat_last_time = time.time()
        self.pubcheat_frame_count = 0
        self.pubcheat_fps = 0

        self.pubcheat_esp_visible = True
        self.pubcheat_radar_visible = True
        self.pubcheat_team_panel_visible = True
        self.pubcheat_shortcut_esp = QShortcut(QKeySequence('F1'), self)
        self.pubcheat_shortcut_esp.activated.connect(self.pubcheat_toggle_esp)
        self.pubcheat_shortcut_radar = QShortcut(QKeySequence('F2'), self)
        self.pubcheat_shortcut_radar.activated.connect(self.pubcheat_toggle_radar)
        self.pubcheat_shortcut_team = QShortcut(QKeySequence('F3'), self)
        self.pubcheat_shortcut_team.activated.connect(self.pubcheat_toggle_team_panel)

    def pubcheat_toggle_esp(self):
        self.pubcheat_esp_visible = not self.pubcheat_esp_visible
        self.pubcheat_update_scene()

    def pubcheat_toggle_radar(self):
        self.pubcheat_radar_visible = not self.pubcheat_radar_visible
        self.pubcheat_update_scene()

    def pubcheat_toggle_team_panel(self):
        self.pubcheat_team_panel_visible = not self.pubcheat_team_panel_visible
        self.pubcheat_update_scene()

    def pubcheat_reload_settings(self):
        self.pubcheat_settings = pubcheat_load_settings()
        self.pubcheat_window_width, self.pubcheat_window_height = pubcheat_get_window_size("Counter-Strike 2")
        if self.pubcheat_window_width is None or self.pubcheat_window_height is None:
            print("Fout: spelvenster niet gevonden.")
            sys.exit(1)
        self.setGeometry(0, 0, self.pubcheat_window_width, self.pubcheat_window_height)
        self.pubcheat_update_scene()

    def pubcheat_update_scene(self):
        self.pubcheat_scene.clear()
        if not self.pubcheat_is_game_window_active():
            return
        if self.pubcheat_esp_visible:
            pubcheat_draw_esp(self.pubcheat_scene, self.pubcheat_pm, self.pubcheat_client, self.pubcheat_offsets, self.pubcheat_client_dll, self.pubcheat_window_width, self.pubcheat_window_height, self.pubcheat_settings)
        if self.pubcheat_radar_visible:
            pubcheat_draw_radar(self.pubcheat_scene, self.pubcheat_pm, self.pubcheat_client, self.pubcheat_offsets, self.pubcheat_client_dll, self.pubcheat_window_width, self.pubcheat_window_height)
        if self.pubcheat_team_panel_visible:
            pubcheat_draw_team_panel(self.pubcheat_scene, self.pubcheat_pm, self.pubcheat_client, self.pubcheat_offsets, self.pubcheat_client_dll, self.pubcheat_window_width, self.pubcheat_window_height)
        pubcheat_current_time = time.time()
        self.pubcheat_frame_count += 1
        if pubcheat_current_time - self.pubcheat_last_time >= 1.0:
            self.pubcheat_fps = self.pubcheat_frame_count
            self.pubcheat_frame_count = 0
            self.pubcheat_last_time = pubcheat_current_time
        expa_fps_text = self.pubcheat_scene.addText(f"ExPa Version 2.1 @ made by G3R | FPS: {self.pubcheat_fps}", QtGui.QFont('DejaVu Sans', 12, QtGui.QFont.Bold))
        expa_fps_text.setPos(5, 5)
        expa_fps_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))

    def pubcheat_is_game_window_active(self):
        pubcheat_hwnd = win32gui.FindWindow(None, "Counter-Strike 2")
        if pubcheat_hwnd:
            pubcheat_foreground_hwnd = win32gui.GetForegroundWindow()
            return pubcheat_hwnd == pubcheat_foreground_hwnd
        return False

def pubcheat_draw_esp(scene, pm, client, offsets, client_dll, window_width, window_height, settings):
    if settings['esp_rendering'] == 0:
        return

    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    dwViewMatrix = offsets['client.dll']['dwViewMatrix']
    dwPlantedC4 = offsets['client.dll']['dwPlantedC4']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
    m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
    m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    m_iszPlayerName = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iszPlayerName']
    m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
    m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
    m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
    m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
    m_ArmorValue = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_ArmorValue']
    m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
    m_flTimerLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flTimerLength']
    m_flDefuseLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flDefuseLength']
    m_bBeingDefused = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_bBeingDefused']

    view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]

    local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
    try:
        local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
    except:
        return

    no_center_x = window_width / 2
    no_center_y = window_height * 0.9
    entity_list = pm.read_longlong(client + dwEntityList)
    entity_ptr = pm.read_longlong(entity_list + 0x10)

    def pubcheat_bombisplant():
        global pubcheat_BombPlantedTime
        bombisplant = pm.read_bool(client + dwPlantedC4 - 0x8)
        if bombisplant:
            if (pubcheat_BombPlantedTime == 0):
                pubcheat_BombPlantedTime = time.time()
        else:
            pubcheat_BombPlantedTime = 0
        return bombisplant
    
    def pubcheat_getC4BaseClass():
        plantedc4 = pm.read_longlong(client + dwPlantedC4)
        plantedc4class = pm.read_longlong(plantedc4)
        return plantedc4class
    
    def pubcheat_getPositionWTS():
        c4node = pm.read_longlong(pubcheat_getC4BaseClass() + m_pGameSceneNode)
        c4posX = pm.read_float(c4node + m_vecAbsOrigin)
        c4posY = pm.read_float(c4node + m_vecAbsOrigin + 0x4)
        c4posZ = pm.read_float(c4node + m_vecAbsOrigin + 0x8)
        bomb_pos = pubcheat_w2s(view_matrix, c4posX, c4posY, c4posZ, window_width, window_height)
        return bomb_pos
    
    def pubcheat_getBombTime():
        BombTime = pm.read_float(pubcheat_getC4BaseClass() + m_flTimerLength) - (time.time() - pubcheat_BombPlantedTime)
        return BombTime if (BombTime >= 0) else 0
    
    def pubcheat_isBeingDefused():
        global pubcheat_BombDefusedTime
        BombIsDefused = pm.read_bool(pubcheat_getC4BaseClass() + m_bBeingDefused)
        if (BombIsDefused):
            if (pubcheat_BombDefusedTime == 0):
                pubcheat_BombDefusedTime = time.time() 
        else:
            pubcheat_BombDefusedTime = 0
        return BombIsDefused
    
    def pubcheat_getDefuseTime():
        DefuseTime = pm.read_float(pubcheat_getC4BaseClass() + m_flDefuseLength) - (time.time() - pubcheat_BombDefusedTime)
        return DefuseTime if (pubcheat_isBeingDefused() and DefuseTime >= 0) else 0

    pubcheat_bfont = QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold)

    if settings.get('bomb_esp', 0) == 1:
        if pubcheat_bombisplant():
            BombPosition = pubcheat_getPositionWTS()
            BombTime = pubcheat_getBombTime()
            DefuseTime = pubcheat_getDefuseTime()
        
            if (BombPosition[0] > 0 and BombPosition[1] > 0):
                if DefuseTime > 0:
                    c4_name_text = scene.addText(f'BOMB {round(BombTime, 2)} | DIF {round(DefuseTime, 2)}', pubcheat_bfont)
                else:
                    c4_name_text = scene.addText(f'BOMB {round(BombTime, 2)}', pubcheat_bfont)
                c4_name_x = BombPosition[0]
                c4_name_y = BombPosition[1]
                c4_name_text.setPos(c4_name_x, c4_name_y)
                c4_name_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))

    for i in range(1, 64):
        try:
            if entity_ptr == 0:
                break

            entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
            if entity_controller == 0:
                continue

            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
            if entity_controller_pawn == 0:
                continue

            entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
            if entity_list_pawn == 0:
                continue

            entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
            if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                continue

            entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
            if entity_team == local_player_team and settings['esp_mode'] == 0:
                continue

            entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
            armor_hp = pm.read_int(entity_pawn_addr + m_ArmorValue)
            if entity_hp <= 0:
                continue

            entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
            if entity_alive != 256:
                continue

            weapon_pointer = pm.read_longlong(entity_pawn_addr + m_pClippingWeapon)
            weapon_index = pm.read_int(weapon_pointer + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
            weapon_name = pubcheat_get_weapon_name_by_index(weapon_index)

            color = QtGui.QColor(71, 167, 106) if entity_team == local_player_team else QtGui.QColor(196, 30, 58)
            game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
            bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)

            try:
                headX = pm.read_float(bone_matrix + 6 * 0x20)
                headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
                headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8) + 8
                head_pos = pubcheat_w2s(view_matrix, headX, headY, headZ, window_width, window_height)
                if head_pos[1] < 0:
                    continue
                if settings['line_rendering'] == 1:
                    legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                    leg_pos = pubcheat_w2s(view_matrix, headX, headY, legZ, window_width, window_height)
                    bottom_left_x = head_pos[0] - (head_pos[0] - leg_pos[0]) // 2
                    bottom_y = leg_pos[1]
                    line = scene.addLine(bottom_left_x, bottom_y, no_center_x, no_center_y, QtGui.QPen(color, 1))

                legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
                leg_pos = pubcheat_w2s(view_matrix, headX, headY, legZ, window_width, window_height)
                deltaZ = abs(head_pos[1] - leg_pos[1])
                leftX = head_pos[0] - deltaZ // 4
                rightX = head_pos[0] + deltaZ // 4
                rect = scene.addRect(QtCore.QRectF(leftX, head_pos[1], rightX - leftX, leg_pos[1] - head_pos[1]), QtGui.QPen(color, 1), QtCore.Qt.NoBrush)

                if settings['hp_bar_rendering'] == 1:
                    max_hp = 100
                    hp_percentage = min(1.0, max(0.0, entity_hp / max_hp))
                    hp_bar_width = 2
                    hp_bar_height = deltaZ
                    hp_bar_x_left = leftX - hp_bar_width - 2
                    hp_bar_y_top = head_pos[1]
                    hp_bar = scene.addRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_top, hp_bar_width, hp_bar_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(0, 0, 0))
                    current_hp_height = hp_bar_height * hp_percentage
                    hp_bar_y_bottom = hp_bar_y_top + hp_bar_height - current_hp_height
                    hp_bar_current = scene.addRect(QtCore.QRectF(hp_bar_x_left, hp_bar_y_bottom, hp_bar_width, current_hp_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(255, 0, 0))
                    max_armor_hp = 100
                    armor_hp_percentage = min(1.0, max(0.0, armor_hp / max_armor_hp))
                    armor_bar_width = 2
                    armor_bar_height = deltaZ
                    armor_bar_x_left = hp_bar_x_left - armor_bar_width - 2
                    armor_bar_y_top = head_pos[1]
                
                    armor_bar = scene.addRect(QtCore.QRectF(armor_bar_x_left, armor_bar_y_top, armor_bar_width, armor_bar_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(62, 95, 138))
                    current_armor_height = armor_bar_height * armor_hp_percentage
                    armor_bar_y_bottom = armor_bar_y_top + armor_bar_height - current_armor_height
                    armor_bar_current = scene.addRect(QtCore.QRectF(armor_bar_x_left, armor_bar_y_bottom, armor_bar_width, current_armor_height), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(62, 95, 138))

                if settings['head_hitbox_rendering'] == 1:
                    head_hitbox_size = (rightX - leftX) / 5
                    head_hitbox_radius = head_hitbox_size * 2 ** 0.5 / 2
                    head_hitbox_x = leftX + 2.5 * head_hitbox_size
                    head_hitbox_y = head_pos[1] + deltaZ / 9
                    ellipse = scene.addEllipse(QtCore.QRectF(head_hitbox_x - head_hitbox_radius, head_hitbox_y - head_hitbox_radius, head_hitbox_radius * 2, head_hitbox_radius * 2), QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(255, 0, 0, 128))

                if settings.get('bons', 0) == 1:
                    pubcheat_draw_bones(scene, pm, bone_matrix, view_matrix, window_width, window_height)

                if settings.get('nickname', 0) == 1:
                    player_name = pm.read_string(entity_controller + m_iszPlayerName, 32)
                    font_size = max(6, min(18, deltaZ / 25))
                    font = QtGui.QFont('DejaVu Sans', font_size, QtGui.QFont.Bold)
                    name_text = scene.addText(player_name, font)
                    text_rect = name_text.boundingRect()
                    name_x = head_pos[0] - text_rect.width() / 2
                    name_y = head_pos[1] - text_rect.height()
                    name_text.setPos(name_x, name_y)
                    name_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))
                
                if settings.get('weapon', 0) == 1:
                    weapon_name_text = scene.addText(weapon_name, font)
                    text_rect = weapon_name_text.boundingRect()
                    weapon_name_x = head_pos[0] - text_rect.width() / 2
                    weapon_name_y = head_pos[1] + deltaZ
                    weapon_name_text.setPos(weapon_name_x, weapon_name_y)
                    weapon_name_text.setDefaultTextColor(QtGui.QColor(255, 255, 255))

                if 'radius' in settings:
                    if settings['radius'] != 0:
                        center_x = window_width / 2
                        center_y = window_height / 2
                        screen_radius = settings['radius'] / 100.0 * min(center_x, center_y)
                        ellipse = scene.addEllipse(QtCore.QRectF(center_x - screen_radius, center_y - screen_radius, screen_radius * 2, screen_radius * 2), QtGui.QPen(QtGui.QColor(255, 255, 255, 16), 0.5), QtCore.Qt.NoBrush)

            except:
                return
        except:
            return

def pubcheat_get_weapon_name_by_index(index):
    pubcheat_weapon_names = {
    32: "P2000",
    61: "USP-S",
    4: "Glock",
    2: "Dual Berettas",
    36: "P250",
    30: "Tec-9",
    63: "CZ75-Auto",
    1: "Desert Eagle",
    3: "Five-SeveN",
    64: "R8",
    35: "Nova",
    25: "XM1014",
    27: "MAG-7",
    29: "Sawed-Off",
    14: "M249",
    28: "Negev",
    17: "MAC-10",
    23: "MP5-SD",
    24: "UMP-45",
    19: "P90",
    26: "Bizon",
    34: "MP9",
    33: "MP7",
    10: "FAMAS",
    16: "M4A4",
    60: "M4A1-S",
    8: "AUG",
    43: "Galil",
    7: "AK-47",
    39: "SG 553",
    40: "SSG 08",
    9: "AWP",
    38: "SCAR-20",
    11: "G3SG1",
    43: "Flashbang",
    44: "Hegrenade",
    45: "Smoke",
    46: "Molotov",
    47: "Decoy",
    48: "Incgrenage",
    49: "C4",
    31: "Taser",
    42: "Knife",
    41: "Knife Gold",
    59: "Knife",
    80: "Knife Ghost",
    500: "Knife Bayonet",
    505: "Knife Flip",
    506: "Knife Gut",
    507: "Knife Karambit",
    508: "Knife M9",
    509: "Knife Tactica",
    512: "Knife Falchion",
    514: "Knife Survival Bowie",
    515: "Knife Butterfly",
    516: "Knife Rush",
    519: "Knife Ursus",
    520: "Knife Gypsy Jackknife",
    522: "Knife Stiletto",
    523: "Knife Widowmaker"
}
    return pubcheat_weapon_names.get(index, 'Unknown')

def pubcheat_draw_bones(scene, pm, bone_matrix, view_matrix, width, height):
    pubcheat_bone_ids = {
        "head": 6,
        "neck": 5,
        "spine": 4,
        "pelvis": 0,
        "left_shoulder": 13,
        "left_elbow": 14,
        "left_wrist": 15,
        "right_shoulder": 9,
        "right_elbow": 10,
        "right_wrist": 11,
        "left_hip": 25,
        "left_knee": 26,
        "left_ankle": 27,
        "right_hip": 22,
        "right_knee": 23,
        "right_ankle": 24,
    }
    pubcheat_bone_connections = [
        ("head", "neck"),
        ("neck", "spine"),
        ("spine", "pelvis"),
        ("pelvis", "left_hip"),
        ("left_hip", "left_knee"),
        ("left_knee", "left_ankle"),
        ("pelvis", "right_hip"),
        ("right_hip", "right_knee"),
        ("right_knee", "right_ankle"),
        ("neck", "left_shoulder"),
        ("left_shoulder", "left_elbow"),
        ("left_elbow", "left_wrist"),
        ("neck", "right_shoulder"),
        ("right_shoulder", "right_elbow"),
        ("right_elbow", "right_wrist"),
    ]
    pubcheat_bone_positions = {}
    try:
        for pubcheat_bone_name, pubcheat_bone_id in pubcheat_bone_ids.items():
            boneX = pm.read_float(bone_matrix + pubcheat_bone_id * 0x20)
            boneY = pm.read_float(bone_matrix + pubcheat_bone_id * 0x20 + 0x4)
            boneZ = pm.read_float(bone_matrix + pubcheat_bone_id * 0x20 + 0x8)
            bone_pos = pubcheat_w2s(view_matrix, boneX, boneY, boneZ, width, height)
            if bone_pos[0] != -999 and bone_pos[1] != -999:
                pubcheat_bone_positions[pubcheat_bone_name] = bone_pos
        for pubcheat_connection in pubcheat_bone_connections:
            if pubcheat_connection[0] in pubcheat_bone_positions and pubcheat_connection[1] in pubcheat_bone_positions:
                scene.addLine(
                    pubcheat_bone_positions[pubcheat_connection[0]][0], pubcheat_bone_positions[pubcheat_connection[0]][1],
                    pubcheat_bone_positions[pubcheat_connection[1]][0], pubcheat_bone_positions[pubcheat_connection[1]][1],
                    QtGui.QPen(QtGui.QColor(255, 255, 255, 128), 1)
                )
    except Exception as pubcheat_e:
        print(f"Error drawing bones: {pubcheat_e}")

def pubcheat_triggerbot_thread(pm, client, offsets, client_dll, settings):
    import win32api
    import win32con
    import time
    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
    m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
    m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
    m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
    m_iIDEntIndex = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex']

    while True:
        try:
            local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
            weapon_pointer = pm.read_longlong(local_player_pawn_addr + m_pClippingWeapon)
            weapon_index = pm.read_int(weapon_pointer + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
            if weapon_index not in PISTOL_WEAPON_INDICES:
                time.sleep(0.05)
                continue
            local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
            crosshair_entity_id = pm.read_int(local_player_pawn_addr + m_iIDEntIndex)
            if crosshair_entity_id <= 0:
                time.sleep(0.01)
                continue
            entity_list = pm.read_longlong(client + dwEntityList)
            entEntry = pm.read_longlong(entity_list + 0x8 * (crosshair_entity_id >> 9) + 0x10)
            entity = pm.read_longlong(entEntry + 0x78 * (crosshair_entity_id & 0x1FF))
            if entity == 0 or entity == local_player_pawn_addr:
                time.sleep(0.01)
                continue
            entity_team = pm.read_int(entity + m_iTeamNum)
            if entity_team == local_player_team:
                time.sleep(0.01)
                continue
            entity_hp = pm.read_int(entity + m_iHealth)
            if entity_hp <= 0:
                time.sleep(0.01)
                continue
            entity_alive = pm.read_int(entity + m_lifeState)
            if entity_alive != 256:
                time.sleep(0.01)
                continue
            # Simulate a single mouse click (1-tap)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.025)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.2)  # Prevent double tap
        except Exception:
            time.sleep(0.1)

def pubcheat_draw_radar(scene, pm, client, offsets, client_dll, window_width, window_height):
    # Radar settings
    radar_size = 200
    radar_x = 20
    radar_y = window_height - radar_size - 20
    radar_center = radar_x + radar_size // 2, radar_y + radar_size // 2
    radar_scale = 4.0  # Smaller = more zoomed in
    # Get local player
    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
    local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
    try:
        local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
        local_player_pos = [
            pm.read_float(pm.read_longlong(local_player_pawn_addr + m_hPlayerPawn) + m_vecAbsOrigin),
            pm.read_float(pm.read_longlong(local_player_pawn_addr + m_hPlayerPawn) + m_vecAbsOrigin + 0x4),
        ]
    except:
        return
    entity_list = pm.read_longlong(client + dwEntityList)
    entity_ptr = pm.read_longlong(entity_list + 0x10)
    for i in range(1, 64):
        try:
            if entity_ptr == 0:
                break
            entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
            if entity_controller == 0:
                continue
            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
            if entity_controller_pawn == 0:
                continue
            entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
            if entity_list_pawn == 0:
                continue
            entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
            if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                continue
            entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
            color = QtGui.QColor(71, 167, 106) if entity_team == local_player_team else QtGui.QColor(196, 30, 58)
            entity_pos = [
                pm.read_float(entity_pawn_addr + m_vecAbsOrigin),
                pm.read_float(entity_pawn_addr + m_vecAbsOrigin + 0x4),
            ]
            dx = (entity_pos[0] - local_player_pos[0]) / radar_scale
            dy = (entity_pos[1] - local_player_pos[1]) / radar_scale
            px = radar_center[0] + dx
            py = radar_center[1] + dy
            scene.addEllipse(px - 3, py - 3, 6, 6, QtGui.QPen(QtCore.Qt.NoPen), color)
        except:
            continue
    # Draw radar border
    scene.addRect(radar_x, radar_y, radar_size, radar_size, QtGui.QPen(QtGui.QColor(255,255,255,128), 2))
    # Draw local player dot
    scene.addEllipse(radar_center[0] - 4, radar_center[1] - 4, 8, 8, QtGui.QPen(QtCore.Qt.NoPen), QtGui.QColor(255,255,255))

def pubcheat_draw_team_panel(scene, pm, client, offsets, client_dll, window_width, window_height):
    # Team info panel settings
    panel_x = window_width - 220
    panel_y = 40
    panel_width = 200
    row_height = 22
    # Get local player
    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    m_ArmorValue = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_ArmorValue']
    m_iszPlayerName = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iszPlayerName']
    local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
    try:
        local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
    except:
        return
    entity_list = pm.read_longlong(client + dwEntityList)
    entity_ptr = pm.read_longlong(entity_list + 0x10)
    row = 0
    for i in range(1, 64):
        try:
            if entity_ptr == 0:
                break
            entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
            if entity_controller == 0:
                continue
            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
            if entity_controller_pawn == 0:
                continue
            entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
            if entity_list_pawn == 0:
                continue
            entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
            if entity_pawn_addr == 0:
                continue
            entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
            if entity_team != local_player_team:
                continue
            entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
            entity_armor = pm.read_int(entity_pawn_addr + m_ArmorValue)
            player_name = pm.read_string(entity_controller + m_iszPlayerName, 32)
            font = QtGui.QFont('DejaVu Sans', 10, QtGui.QFont.Bold)
            text = f"{player_name} | HP:{entity_hp} | AR:{entity_armor}"
            text_item = scene.addText(text, font)
            text_item.setPos(panel_x, panel_y + row * row_height)
            text_item.setDefaultTextColor(QtGui.QColor(71, 167, 106))
            row += 1
        except:
            continue
    # Draw panel border
    scene.addRect(panel_x - 5, panel_y - 5, panel_width, max(row * row_height, row_height), QtGui.QPen(QtGui.QColor(255,255,255,128), 2))

def pubcheat_legit_aimbot_thread(pm, client, offsets, client_dll, settings):
    import win32api
    import win32con
    import time
    # Use m_bDormant for visibility check
    m_bDormant = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_bDormant']
    dwEntityList = offsets['client.dll']['dwEntityList']
    dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
    dwViewMatrix = offsets['client.dll']['dwViewMatrix']
    m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
    m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
    m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
    m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
    m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
    m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
    m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
    m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
    m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
    m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
    smoothing = 0.2  # 0.1 = very slow, 1.0 = instant
    while True:
        try:
            # Only run if RMB is held
            if not win32api.GetAsyncKeyState(win32con.VK_RBUTTON) & 0x8000:
                time.sleep(0.01)
                continue
            local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
            local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
            view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
            window_width, window_height = pubcheat_get_window_size("Counter-Strike 2")
            cx, cy = window_width // 2, window_height // 2
            entity_list = pm.read_longlong(client + dwEntityList)
            entity_ptr = pm.read_longlong(entity_list + 0x10)
            closest_dist = 9999
            closest_delta = (0, 0)
            for i in range(1, 64):
                if entity_ptr == 0:
                    break
                entity_controller = pm.read_longlong(entity_ptr + 0x78 * (i & 0x1FF))
                if entity_controller == 0:
                    continue
                entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
                if entity_controller_pawn == 0:
                    continue
                entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
                if entity_list_pawn == 0:
                    continue
                entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x78 * (entity_controller_pawn & 0x1FF))
                if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
                    continue
                # Visibility check: skip if dormant
                if pm.read_bool(entity_pawn_addr + m_bDormant):
                    continue
                entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
                if entity_team == local_player_team:
                    continue
                entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
                if entity_hp <= 0:
                    continue
                entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
                if entity_alive != 256:
                    continue
                game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
                bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
                headX = pm.read_float(bone_matrix + 6 * 0x20)
                headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
                headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8) + 8
                head_pos = pubcheat_w2s(view_matrix, headX, headY, headZ, window_width, window_height)
                dist = ((head_pos[0] - cx) ** 2 + (head_pos[1] - cy) ** 2) ** 0.5
                if dist < 300 and dist < closest_dist:
                    closest_dist = dist
                    closest_delta = (head_pos[0] - cx, head_pos[1] - cy)
            if closest_dist < 300:
                # Smoothly move mouse toward the closest enemy head
                move_x = int(closest_delta[0] * smoothing)
                move_y = int(closest_delta[1] * smoothing)
                if move_x != 0 or move_y != 0:
                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)
            time.sleep(0.01)
        except Exception:
            time.sleep(0.05)

def pubcheat_main():
    print("Waiting for cs2.exe...")
    while True:
        time.sleep(1)
        try:
            pubcheat_pm = pymem.Pymem("cs2.exe")
            pubcheat_client = pymem.process.module_from_name(pubcheat_pm.process_handle, "client.dll").lpBaseOfDll
            break
        except Exception:
            pass
    print("Starting ExPa Version 2.1 @ made by G3R ESP overlay!")
    time.sleep(2)
    pubcheat_settings = pubcheat_load_settings()
    pubcheat_offsets, pubcheat_client_dll = pubcheat_get_offsets_and_client_dll()
    # Start triggerbot thread
    triggerbot_thread = threading.Thread(target=pubcheat_triggerbot_thread, args=(pubcheat_pm, pubcheat_client, pubcheat_offsets, pubcheat_client_dll, pubcheat_settings), daemon=True)
    triggerbot_thread.start()
    # Start legit aimbot thread
    legit_aimbot_thread = threading.Thread(target=pubcheat_legit_aimbot_thread, args=(pubcheat_pm, pubcheat_client, pubcheat_offsets, pubcheat_client_dll, pubcheat_settings), daemon=True)
    legit_aimbot_thread.start()
    pubcheat_app = QtWidgets.QApplication(sys.argv)
    pubcheat_window = PubCheatOverlay(pubcheat_settings)
    pubcheat_window.show()
    sys.exit(pubcheat_app.exec())

if __name__ == "__main__":
    pubcheat_main()