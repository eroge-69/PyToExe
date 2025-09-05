import pymem
import pymem.process
import win32gui, win32con
import time, os
import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw
import OpenGL.GL as gl
import requests

# Configuration
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
MENU_KEY = glfw.KEY_INSERT
MENU_VISIBLE = False

# Offsets
offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()

dwEntityList = offsets['client.dll']['dwEntityList']
dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
dwViewMatrix = offsets['client.dll']['dwViewMatrix']

m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']

# Cheat Settings
class CheatSettings:
    def __init__(self):
        self.esp_enabled = True
        self.esp_box = True
        self.esp_health = True
        self.esp_team = False
        self.triggerbot = False
        self.bhop = False
        self.radar = False

settings = CheatSettings()

# Wait for CS2
def wait_for_process():
    while True:
        time.sleep(1)
        try:
            pm = pymem.Pymem("cs2.exe")
            client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
            return pm, client
        except:
            pass

# World to Screen
def w2s(mtx, posx, posy, posz, width, height):
    screenW = mtx[12]*posx + mtx[13]*posy + mtx[14]*posz + mtx[15]
    if screenW > 0.001:
        screenX = mtx[0]*posx + mtx[1]*posy + mtx[2]*posz + mtx[3]
        screenY = mtx[4]*posx + mtx[5]*posy + mtx[6]*posz + mtx[7]
        camX = width / 2
        camY = height / 2
        x = camX + (camX * screenX / screenW) // 1
        y = camY - (camY * screenY / screenW) // 1
        return [x, y]
    return [-999, -999]

# ESP Function
def esp(draw_list, pm, client):
    if not settings.esp_enabled:
        return

    view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
    local_player = pm.read_longlong(client + dwLocalPlayerPawn)
    
    try:
        local_team = pm.read_int(local_player + m_iTeamNum)
    except:
        return

    for i in range(64):
        entity = pm.read_longlong(client + dwEntityList)
        if not entity:
            continue

        list_entry = pm.read_longlong(entity + ((8 * (i & 0x7FFF) >> 9) + 16))
        if not list_entry:
            continue

        entity_controller = pm.read_longlong(list_entry + (120) * (i & 0x1FF))
        if not entity_controller:
            continue

        entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
        if not entity_controller_pawn:
            continue

        list_entry = pm.read_longlong(entity + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
        if not list_entry:
            continue

        entity_pawn = pm.read_longlong(list_entry + (120) * (entity_controller_pawn & 0x1FF))
        if not entity_pawn or entity_pawn == local_player:
            continue

        if pm.read_int(entity_pawn + m_lifeState) != 256:
            continue

        entity_team = pm.read_int(entity_pawn + m_iTeamNum)
        if not settings.esp_team and entity_team == local_team:
            continue

        color = imgui.get_color_u32_rgba(1, 0, 0, 1) if entity_team != local_team else imgui.get_color_u32_rgba(0, 1, 0, 1)

        game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
        bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)

        try:
            headX = pm.read_float(bone_matrix + 6 * 0x20)
            headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
            headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8) + 8
            head_pos = w2s(view_matrix, headX, headY, headZ, WINDOW_WIDTH, WINDOW_HEIGHT)

            legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
            leg_pos = w2s(view_matrix, headX, headY, legZ, WINDOW_WIDTH, WINDOW_HEIGHT)

            if settings.esp_box:
                delta = abs(head_pos[1] - leg_pos[1])
                leftX = head_pos[0] - delta // 3
                rightX = head_pos[0] + delta // 3

                draw_list.add_line(leftX, leg_pos[1], rightX, leg_pos[1], color, 2.0)
                draw_list.add_line(leftX, leg_pos[1], leftX, head_pos[1], color, 2.0)
                draw_list.add_line(rightX, leg_pos[1], rightX, head_pos[1], color, 2.0)
                draw_list.add_line(leftX, head_pos[1], rightX, head_pos[1], color, 2.0)

            if settings.esp_health:
                entity_hp = pm.read_int(entity_pawn + m_iHealth)
                draw_list.add_text(head_pos[0] - 10, head_pos[1] - 20, color, str(entity_hp))

        except:
            continue

# Bunny Hop
def bhop(pm, client):
    if not settings.bhop:
        return

    try:
        local_player = pm.read_longlong(client + dwLocalPlayerPawn)
        flags = pm.read_int(local_player + 0x3C8)  # m_fFlags
        if flags & 1 << 0 and glfw.get_key(glfw.get_current_context(), glfw.KEY_SPACE):
            pm.write_int(client + 0x52B9DE0, 65537)  # Force jump
            time.sleep(0.01)
            pm.write_int(client + 0x52B9DE0, 256)   # Reset jump
    except:
        pass

# Trigger Bot
def triggerbot(pm, client):
    if not settings.triggerbot:
        return

    try:
        local_player = pm.read_longlong(client + dwLocalPlayerPawn)
        crosshair_id = pm.read_int(local_player + 0x1584)  # m_iIDEntIndex
        if crosshair_id > 0 and crosshair_id < 64:
            entity = pm.read_longlong(client + dwEntityList + (crosshair_id - 1) * 0x8)
            if entity:
                entity_team = pm.read_int(entity + m_iTeamNum)
                local_team = pm.read_int(local_player + m_iTeamNum)
                if entity_team != local_team:
                    pm.write_int(client + 0x52B9DE8, 65537)  # Attack
                    time.sleep(0.05)
                    pm.write_int(client + 0x52B9DE8, 256)    # Stop attack
    except:
        pass

# Radar Hack
def radar_hack(pm, client):
    if not settings.radar:
        return

    try:
        for i in range(64):
            entity = pm.read_longlong(client + dwEntityList + i * 0x8)
            if entity:
                pm.write_int(entity + 0x3AD, 1)  # m_bSpotted
    except:
        pass

# Main Menu GUI
def draw_menu():
    global MENU_VISIBLE
    
    imgui.set_next_window_size(300, 400)
    imgui.set_next_window_position(50, 50)
    
    if imgui.begin("CS2 Cheat Menu", None, imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE):
        imgui.text("CS2 Cheat Menu")
        imgui.separator()
        
        # ESP Settings
        if imgui.collapsing_header("ESP Settings"):
            _, settings.esp_enabled = imgui.checkbox("ESP Enabled", settings.esp_enabled)
            _, settings.esp_box = imgui.checkbox("Box ESP", settings.esp_box)
            _, settings.esp_health = imgui.checkbox("Show Health", settings.esp_health)
            _, settings.esp_team = imgui.checkbox("Show Team", settings.esp_team)
        
        # Aim Assistance
        if imgui.collapsing_header("Aim Assistance"):
            _, settings.triggerbot = imgui.checkbox("Trigger Bot", settings.triggerbot)
            _, settings.bhop = imgui.checkbox("Bunny Hop", settings.bhop)
        
        # Other Hacks
        if imgui.collapsing_header("Other Hacks"):
            _, settings.radar = imgui.checkbox("Radar Hack", settings.radar)
        
        imgui.separator()
        imgui.text("Press INSERT to toggle menu")
        imgui.text("Status: Active")
        
    imgui.end()

# Overlay Window
def overlay_window(pm, client, draw_list):
    imgui.set_next_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    imgui.set_next_window_position(0, 0)
    imgui.begin("overlay", 
                flags=imgui.WINDOW_NO_TITLE_BAR | 
                imgui.WINDOW_NO_RESIZE | 
                imgui.WINDOW_NO_SCROLLBAR | 
                imgui.WINDOW_NO_COLLAPSE | 
                imgui.WINDOW_NO_BACKGROUND)
    
    esp(draw_list, pm, client)
    imgui.end()

# Main Function
def main():
    global MENU_VISIBLE
    
    pm, client = wait_for_process()
    
    glfw.init()
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "CS2 Overlay", None, None)
    
    hwnd = glfw.get_win32_window(window)
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    ex_style = win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, -2, -2, 0, 0,
                          win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
    
    glfw.make_context_current(window)
    imgui.create_context()
    impl = GlfwRenderer(window)
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        
        # Toggle menu with INSERT key
        if glfw.get_key(window, MENU_KEY) == glfw.PRESS:
            MENU_VISIBLE = not MENU_VISIBLE
            time.sleep(0.2)
        
        imgui.new_frame()
        
        # Draw overlay (always visible)
        draw_list = imgui.get_background_draw_list()
        overlay_window(pm, client, draw_list)
        
        # Draw menu if visible
        if MENU_VISIBLE:
            draw_menu()
        
        # Run other hacks
        bhop(pm, client)
        triggerbot(pm, client)
        radar_hack(pm, client)
        
        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
    
    impl.shutdown()
    glfw.terminate()

if __name__ == '__main__':
    main()