import pymem
import pymem.process
import requests
import win32api, win32con
import win32gui
import time
import random
import math
import threading
import tkinter as tk

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class TriggerBot:
    def __init__(self, random_delay=110, min_delay=240, attack_all=False):
        self.random_delay = random_delay
        self.min_delay = min_delay
        self.attack_all = attack_all
        self.pm, self.client = self.descriptor()
        self.offsets = self.get_offsets()
        
    def descriptor(self):
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        return pm, client
    
    def get_offsets(self):
        offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
        client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()
        return {
            'dwEntityList': offsets['client.dll']['dwEntityList'],
            'dwLocalPlayerPawn': offsets['client.dll']['dwLocalPlayerPawn'],
            'm_iTeamNum': client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum'],
            'm_iHealth': client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth'],
            'm_iIDEntIndex': client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_iIDEntIndex']
        }
    
    def run(self):
        while True:
            try:
                player = self.pm.read_longlong(self.client + self.offsets['dwLocalPlayerPawn'])
                entityId = self.pm.read_int(player + self.offsets['m_iIDEntIndex'])
                if entityId > 0:
                    entList = self.pm.read_longlong(self.client + self.offsets['dwEntityList'])
                    entEntry = self.pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                    entity = self.pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))
                    entityTeam = self.pm.read_int(entity + self.offsets['m_iTeamNum'])
                    playerTeam = self.pm.read_int(player + self.offsets['m_iTeamNum'])
                    if self.attack_all or entityTeam != playerTeam:
                        entityHp = self.pm.read_int(entity + self.offsets['m_iHealth'])
                        if entityHp > 0:
                            sleep_in = random.randint(self.min_delay, self.min_delay + self.random_delay)
                            time.sleep(sleep_in / 10000)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                            sleep_out = random.randint(self.min_delay, self.min_delay + self.random_delay)
                            time.sleep(sleep_out / 10000)
                            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            except:
                time.sleep(0.03)
                pass

class AimCircleOverlay:
    def __init__(self, circle_radius=100, attack_all=False):
        self.circle_radius = circle_radius
        self.attack_all = attack_all
        
        # Setup CS2 connection
        self.pm, self.client = self.connect_to_cs2()
        self.offsets = self.get_cs2_offsets()
        
        # Screen setup
        self.screen_width = win32api.GetSystemMetrics(0)
        self.screen_height = win32api.GetSystemMetrics(1)
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        # Aimbot settings
        self.locked_target = None
        self.last_aim_time = 0
        self.aim_smoothing = 0.3  # Lower = more aggressive
        self.max_aim_distance = 50  # Max pixels to move per frame
        
        # Setup tkinter overlay
        self.setup_overlay()
        
        print(f"🎯 AimCircle Overlay Ready!")
        print(f"⭕ Circle Radius: {self.circle_radius}")
        print(f"🎮 Attack Mode: {'ALL PLAYERS' if self.attack_all else 'ENEMIES ONLY'}")
        print(f"🔧 Controls: F9/F8 to change circle size")
        
    def connect_to_cs2(self):
        """Connect to CS2 process"""
        while True:
            try:
                pm = pymem.Pymem("cs2.exe")
                client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
                print("✅ Connected to CS2!")
                return pm, client
            except:
                print("⏳ Waiting for CS2...")
                time.sleep(2)
    
    def get_cs2_offsets(self):
        """Get CS2 offsets for memory reading"""
        try:
            offsets_response = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json')
            client_dll_response = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json')
            
            offsets = offsets_response.json()
            client_dll = client_dll_response.json()
            
            base_entity = client_dll['client.dll']['classes']['C_BaseEntity']['fields']
            player_pawn = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']
            skeleton = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']
            controller = client_dll['client.dll']['classes']['CCSPlayerController']['fields']
            game_scene = client_dll['client.dll']['classes']['CGameSceneNode']['fields']
            
            return {
                'dwEntityList': offsets['client.dll']['dwEntityList'],
                'dwLocalPlayerPawn': offsets['client.dll']['dwLocalPlayerPawn'],
                'dwViewMatrix': offsets['client.dll']['dwViewMatrix'],
                'm_iTeamNum': base_entity['m_iTeamNum'],
                'm_iHealth': base_entity['m_iHealth'],
                'm_lifeState': base_entity['m_lifeState'],
                'm_pGameSceneNode': base_entity['m_pGameSceneNode'],
                'm_modelState': skeleton['m_modelState'],
                'm_hPlayerPawn': controller['m_hPlayerPawn'],
                'm_vecOrigin': game_scene.get('m_vecAbsOrigin', base_entity.get('m_vecOrigin', 0x1274)),
            }
        except:
            print("⚠️ Using fallback offsets")
            return {
                'dwEntityList': 0x17BB8C8,
                'dwLocalPlayerPawn': 0x16C8E28,
                'dwViewMatrix': 0x18254F0,
                'm_iTeamNum': 0x3BF,
                'm_iHealth': 0x32C,
                'm_lifeState': 0x330,
                'm_pGameSceneNode': 0x310,
                'm_modelState': 0x160,
                'm_hPlayerPawn': 0x7EC,
                'm_vecOrigin': 0x1274,
            }
    
    def setup_overlay(self):
        """Create tkinter overlay"""
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.config(bg="black")
        
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        # Make window non-clickable
        self.root.wm_attributes("-disabled", True)
        
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, 
                               bg="black", highlightthickness=0)
        self.canvas.pack()
        
        self.circle_id = None
        self.draw_circle()
    
    def draw_circle(self):
        """Draw the aim circle"""
        if self.circle_id:
            self.canvas.delete(self.circle_id)
        
        color = 'lime' if self.locked_target else 'red'
        x0 = self.center_x - self.circle_radius
        y0 = self.center_y - self.circle_radius
        x1 = self.center_x + self.circle_radius
        y1 = self.center_y + self.circle_radius
        
        self.circle_id = self.canvas.create_oval(x0, y0, x1, y1, outline=color, width=2)
    
    def safe_read_int(self, address, default=0):
        """Safely read integer from memory"""
        try:
            return self.pm.read_int(address) if address != 0 else default
        except:
            return default
    
    def safe_read_longlong(self, address, default=0):
        """Safely read longlong from memory"""
        try:
            return self.pm.read_longlong(address) if address != 0 else default
        except:
            return default
    
    def safe_read_float(self, address, default=0.0):
        """Safely read float from memory"""
        try:
            return self.pm.read_float(address) if address != 0 else default
        except:
            return default
    
    def read_vector3(self, address):
        """Read Vector3 from memory"""
        try:
            x = self.pm.read_float(address)
            y = self.pm.read_float(address + 4)
            z = self.pm.read_float(address + 8)
            return Vector3(x, y, z)
        except:
            return Vector3()
    
    def world_to_screen(self, view_matrix, world_pos):
        """Convert 3D world position to 2D screen coordinates"""
        try:
            if not view_matrix or len(view_matrix) < 16:
                return None
                
            screen_w = (view_matrix[12] * world_pos.x + 
                       view_matrix[13] * world_pos.y + 
                       view_matrix[14] * world_pos.z + 
                       view_matrix[15])
            
            if screen_w < 0.01:
                return None
            
            screen_x = (view_matrix[0] * world_pos.x + 
                       view_matrix[1] * world_pos.y + 
                       view_matrix[2] * world_pos.z + 
                       view_matrix[3])
            
            screen_y = (view_matrix[4] * world_pos.x + 
                       view_matrix[5] * world_pos.y + 
                       view_matrix[6] * world_pos.z + 
                       view_matrix[7])
            
            cam_x = self.screen_width * 0.5
            cam_y = self.screen_height * 0.5
            
            x = cam_x + (cam_x * screen_x / screen_w)
            y = cam_y - (cam_y * screen_y / screen_w)
            
            return Vector2(x, y)
        except:
            return None
    
    def get_bone_position(self, bone_matrix, bone_index, z_offset=0):
        """Get bone position from bone matrix"""
        try:
            if bone_matrix == 0:
                return None
            position = self.read_vector3(bone_matrix + bone_index * 0x20)
            if position.magnitude() == 0:
                return None
            position.z += z_offset
            return position
        except:
            return None
    
    def is_in_circle(self, screen_pos):
        """Check if screen position is within circle"""
        try:
            dx = screen_pos.x - self.center_x
            dy = screen_pos.y - self.center_y
            distance = math.sqrt(dx * dx + dy * dy)
            return distance <= self.circle_radius
        except:
            return False
    
    def move_mouse_to_target(self, target_screen_pos):
        """Move mouse smoothly to target position"""
        try:
            current_time = time.time()
            if current_time - self.last_aim_time < 0.01:  # Limit aim rate
                return
            
            self.last_aim_time = current_time
            
            # Calculate movement needed
            offset_x = target_screen_pos.x - self.center_x
            offset_y = target_screen_pos.y - self.center_y
            
            # Apply smoothing
            move_x = int(offset_x * self.aim_smoothing)
            move_y = int(offset_y * self.aim_smoothing)
            
            # Limit maximum movement per frame
            move_x = max(-self.max_aim_distance, min(self.max_aim_distance, move_x))
            move_y = max(-self.max_aim_distance, min(self.max_aim_distance, move_y))
            
            if abs(move_x) > 1 or abs(move_y) > 1:
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)
                print(f"🎯 Moving mouse: ({move_x}, {move_y}) towards target")
        except Exception as e:
            print(f"❌ Mouse movement error: {e}")
    
    def scan_for_enemies(self):
        """Scan for enemies in circle and return closest target"""
        try:
            # Get view matrix
            view_matrix = []
            for i in range(16):
                val = self.safe_read_float(self.client + self.offsets['dwViewMatrix'] + i * 4)
                view_matrix.append(val)
            
            if not view_matrix or all(v == 0 for v in view_matrix):
                return None
            
            # Get local player data
            local_pawn = self.safe_read_longlong(self.client + self.offsets['dwLocalPlayerPawn'])
            if not local_pawn:
                return None
            
            local_team = self.safe_read_int(local_pawn + self.offsets['m_iTeamNum'])
            entity_list = self.safe_read_longlong(self.client + self.offsets['dwEntityList'])
            if not entity_list:
                return None
            
            closest_target = None
            closest_distance = float('inf')
            
            # Scan entities
            for i in range(64):
                try:
                    # Get entity
                    list_entry = self.safe_read_longlong(entity_list + ((8 * (i & 0x7FFF) >> 9) + 16))
                    if not list_entry:
                        continue
                    
                    entity_controller = self.safe_read_longlong(list_entry + (120) * (i & 0x1FF))
                    if not entity_controller:
                        continue
                    
                    entity_controller_pawn = self.safe_read_longlong(entity_controller + self.offsets['m_hPlayerPawn'])
                    if not entity_controller_pawn:
                        continue
                    
                    list_entry2 = self.safe_read_longlong(entity_list + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
                    if not list_entry2:
                        continue
                    
                    entity_pawn_addr = self.safe_read_longlong(list_entry2 + (120) * (entity_controller_pawn & 0x1FF))
                    if not entity_pawn_addr or entity_pawn_addr == local_pawn:
                        continue
                    
                    # Validate entity
                    life_state = self.safe_read_int(entity_pawn_addr + self.offsets['m_lifeState'])
                    if life_state != 256:
                        continue
                    
                    entity_team = self.safe_read_int(entity_pawn_addr + self.offsets['m_iTeamNum'])
                    if entity_team == 0:
                        continue
                    
                    # Team check
                    if not self.attack_all and entity_team == local_team:
                        continue
                    
                    # Health check
                    health = self.safe_read_int(entity_pawn_addr + self.offsets['m_iHealth'])
                    if health <= 0:
                        continue
                    
                    # Get head position
                    game_scene = self.safe_read_longlong(entity_pawn_addr + self.offsets['m_pGameSceneNode'])
                    if not game_scene:
                        continue
                    
                    bone_matrix = self.safe_read_longlong(game_scene + self.offsets['m_modelState'] + 0x80)
                    if not bone_matrix:
                        continue
                    
                    head_world_pos = self.get_bone_position(bone_matrix, 6, 2.0)  # Head bone
                    if not head_world_pos:
                        continue
                    
                    # Convert to screen
                    head_screen_pos = self.world_to_screen(view_matrix, head_world_pos)
                    if not head_screen_pos:
                        continue
                    
                    # Check if in circle
                    if self.is_in_circle(head_screen_pos):
                        distance_to_center = Vector2(self.center_x, self.center_y).distance_to(head_screen_pos)
                        if distance_to_center < closest_distance:
                            closest_distance = distance_to_center
                            closest_target = {
                                'screen_pos': head_screen_pos,
                                'health': health,
                                'team': entity_team,
                                'distance': distance_to_center
                            }
                            print(f"✅ Target in circle: HP:{health} Team:{entity_team} Dist:{distance_to_center:.1f}")
                
                except:
                    continue
            
            return closest_target
            
        except Exception as e:
            print(f"❌ Enemy scan error: {e}")
            return None
    
    def aim_loop(self):
        """Main aiming loop"""
        while True:
            try:
                # Scan for enemies
                target = self.scan_for_enemies()
                
                if target:
                    self.locked_target = target
                    # Move mouse towards target
                    self.move_mouse_to_target(target['screen_pos'])
                else:
                    self.locked_target = None
                
                # Update circle color
                self.draw_circle()
                
                time.sleep(0.01)  # 100 FPS
                
            except Exception as e:
                print(f"❌ Aim loop error: {e}")
                time.sleep(0.01)
    
    def check_keys(self):
        """Check for key presses"""
        # F9 - Increase circle size
        if win32api.GetAsyncKeyState(win32con.VK_F9) & 0x8000:
            self.circle_radius = min(self.circle_radius + 10, 300)
            print(f"⭕ Circle radius: {self.circle_radius}")
            time.sleep(0.1)
        
        # F8 - Decrease circle size
        if win32api.GetAsyncKeyState(win32con.VK_F8) & 0x8000:
            self.circle_radius = max(self.circle_radius - 10, 30)
            print(f"⭕ Circle radius: {self.circle_radius}")
            time.sleep(0.1)
        
        # F7 - Toggle attack mode
        if win32api.GetAsyncKeyState(win32con.VK_F7) & 0x8000:
            self.attack_all = not self.attack_all
            mode = "ALL PLAYERS" if self.attack_all else "ENEMIES ONLY"
            print(f"🎯 Attack mode: {mode}")
            time.sleep(0.3)
        
        # Schedule next check
        self.root.after(50, self.check_keys)
    
    def run(self):
        """Start the overlay and aimbot"""
        # Start aiming thread
        aim_thread = threading.Thread(target=self.aim_loop, daemon=True)
        aim_thread.start()
        
        # Start key checking
        self.check_keys()
        
        # Start tkinter main loop
        self.root.mainloop()

if __name__ == "__main__":
    print("="*60)
    print("🎯 AimCircle Overlay + TriggerBot")
    print("="*60)
    print("1. AimCircle Overlay (aims for triggerbot)")
    print("2. TriggerBot Only (shoots when crosshair on target)")
    print("3. Both Together (recommended)")
    
    choice = input("\nSelect mode (1/2/3): ").strip()
    
    if choice == "1":
        print("🎯 Starting AimCircle Overlay...")
        overlay = AimCircleOverlay(circle_radius=100, attack_all=False)
        overlay.run()
    
    elif choice == "2":
        print("🔫 Starting TriggerBot...")
        bot = TriggerBot()
        bot.run()
    
    else:  # Default to both
        print("🎯🔫 Starting AimCircle + TriggerBot...")
        
        # Start triggerbot in separate thread
        bot = TriggerBot()
        bot_thread = threading.Thread(target=bot.run, daemon=True)
        bot_thread.start()
        
        # Start overlay (main thread)
        overlay = AimCircleOverlay(circle_radius=100, attack_all=False)
        overlay.run()