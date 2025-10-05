import tkinter as tk
import pyautogui
import time
import threading
import random
import math

# Set pyautogui to fail-safe mode
pyautogui.FAILSAFE = True

# Global variables
running = True
show_box = True
box_size = 20

# Player health
player_health = 100
max_health = 100

# Weapon system
active_weapon = 0  # 0 = none, 1 = laser rifle, 2 = blaster
weapon_1_out = False
weapon_2_out = False
weapon_1_progress = 0.0
weapon_2_progress = 0.0
weapon_1_target = 0.0
weapon_2_target = 0.0

# Firing cooldowns
last_weapon_1_fire = 0
weapon_1_cooldown = 0.5
weapon_2_firing = False

# Mouse direction tracking with smoothing
mouse_angle = 0
target_mouse_angle = 0
last_mouse_x = 0
last_mouse_y = 0

# Laser shooting
lasers = []
laser_duration = 0.15
laser_particles = []

# Blaster shots
blaster_shots = []
blaster_shot_lifetime = 1.5

# Enemy lasers
enemy_lasers = []
enemy_laser_duration = 1.0

# Enemies
enemies = []
max_enemies = 7
enemy_size = 25

class LaserParticle:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * random.uniform(2, 5) + random.uniform(-2, 2)
        self.vy = math.sin(angle) * random.uniform(2, 5) + random.uniform(-2, 2)
        self.life = 0.3
        self.spawn_time = time.time()
        self.size = random.randint(2, 4)

class BlasterShot:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 15
        self.spawn_time = time.time()
        self.size = 8
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

class Enemy:
    def __init__(self, x, y, enemy_type="normal"):
        self.x = x
        self.y = y
        self.type = enemy_type  # "normal", "double", "speedy"
        self.offset_x = random.randint(-200, 200)
        self.offset_y = random.randint(-200, 200)
        
        if enemy_type == "speedy":
            self.speed = random.uniform(1.5, 2.5)
            self.shoot_cooldown = 2.0
            self.max_health = 45
        elif enemy_type == "double":
            self.speed = random.uniform(0.5, 1.0)
            self.shoot_cooldown = 1.5
            self.max_health = 85
        else:
            self.speed = random.uniform(0.5, 1.0)
            self.shoot_cooldown = 2.0
            self.max_health = 75
        
        self.health = self.max_health
        self.alive = True
        self.hit_time = 0
        self.last_shoot_time = time.time() + random.uniform(0, 2)
        
    def update(self, cursor_x, cursor_y):
        target_x = cursor_x + self.offset_x
        target_y = cursor_y + self.offset_y
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 5:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
    
    def try_shoot(self, target_x, target_y):
        current_time = time.time()
        if current_time - self.last_shoot_time >= self.shoot_cooldown:
            self.last_shoot_time = current_time
            
            dx = target_x - self.x
            dy = target_y - self.y
            angle = math.atan2(dy, dx)
            
            if self.type == "double":
                # Shoot two projectiles with slight spread
                offset_angle = 0.15
                enemy_lasers.append(EnemyLaser(self.x, self.y, angle - offset_angle))
                enemy_lasers.append(EnemyLaser(self.x, self.y, angle + offset_angle))
            else:
                enemy_lasers.append(EnemyLaser(self.x, self.y, angle))

class Laser:
    def __init__(self, x, y, angle):
        self.start_x = x
        self.start_y = y
        self.angle = angle
        self.end_x = x + math.cos(angle) * 2000
        self.end_y = y + math.sin(angle) * 2000
        self.spawn_time = time.time()

class EnemyLaser:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 8
        self.spawn_time = time.time()
        self.distance_traveled = 0
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.distance_traveled += self.speed

class OverlayApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cursor Overlay")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'black')
        self.root.configure(bg='black')
        
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.root.bind('<q>', self.quit_app)
        self.root.bind('<Q>', self.quit_app)
        
        self.root.wm_attributes('-transparentcolor', 'black')
        
        self.cursor_x = 0
        self.cursor_y = 0
        
        self.update_display()
        
    def quit_app(self, event=None):
        global running
        running = False
        self.root.quit()
        self.root.destroy()
    
    def draw_health_bar(self):
        bar_width = 80
        bar_height = 10
        bar_x = self.cursor_x - bar_width // 2
        bar_y = self.cursor_y - box_size - 20
        
        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
            fill='#400000', outline='#FF0000', width=2
        )
        
        health_width = int((player_health / max_health) * bar_width)
        if health_width > 0:
            if player_health > 60:
                health_color = '#00FF00'
            elif player_health > 30:
                health_color = '#FFFF00'
            else:
                health_color = '#FF0000'
            
            self.canvas.create_rectangle(
                bar_x, bar_y, bar_x + health_width, bar_y + bar_height,
                fill=health_color, outline=''
            )
        
        self.canvas.create_text(
            self.cursor_x, bar_y + bar_height // 2,
            text=f"{player_health}/{max_health}",
            fill='white', font=('Arial', 8, 'bold')
        )
    
    def draw_green_box(self):
        if show_box:
            self.canvas.create_rectangle(
                self.cursor_x - box_size, self.cursor_y - box_size,
                self.cursor_x + box_size, self.cursor_y + box_size,
                outline='#00FF00', width=3
            )
    
    def draw_laser_rifle(self, progress):
        """Draw weapon 1: Laser Rifle (original cool design)"""
        if progress <= 0:
            return
        
        cursor_x, cursor_y = pyautogui.position()
        nearest_enemy, distance = find_nearest_enemy(cursor_x, cursor_y)
        aim_assist_active = nearest_enemy and distance < 400
        
        gun_length = int(70 * progress)
        gun_width = 14
        x, y = self.cursor_x, self.cursor_y
        angle = mouse_angle
        
        if aim_assist_active and weapon_1_out:
            self.canvas.create_line(
                x, y, nearest_enemy.x, nearest_enemy.y,
                fill='#00FF00', width=1, dash=(5, 5), stipple='gray50'
            )
        
        perp_angle = angle + math.pi / 2
        
        # Main body
        body_start_x = x + math.cos(angle) * 5
        body_start_y = y + math.sin(angle) * 5
        body_end_x = x + math.cos(angle) * (gun_length + 5)
        body_end_y = y + math.sin(angle) * (gun_length + 5)
        
        width_offset_x = math.cos(perp_angle) * (gun_width / 2)
        width_offset_y = math.sin(perp_angle) * (gun_width / 2)
        
        outline_color = '#00FFFF' if aim_assist_active else '#00FF00'
        body_points = [
            body_start_x + width_offset_x, body_start_y + width_offset_y,
            body_end_x + width_offset_x, body_end_y + width_offset_y,
            body_end_x - width_offset_x, body_end_y - width_offset_y,
            body_start_x - width_offset_x, body_start_y - width_offset_y
        ]
        self.canvas.create_polygon(body_points, fill='#006400', outline=outline_color, width=2)
        
        # Energy core (glowing green circle)
        core_offset = 18 * progress
        core_x = x + math.cos(angle) * core_offset
        core_y = y + math.sin(angle) * core_offset
        
        core_color = '#00FFFF' if aim_assist_active else '#00FF00'
        self.canvas.create_oval(
            core_x - 10, core_y - 10, core_x + 10, core_y + 10,
            fill=core_color, outline=core_color
        )
        self.canvas.create_oval(
            core_x - 6, core_y - 6, core_x + 6, core_y + 6,
            fill='#64FF64', outline='#64FF64'
        )
        
        # Barrel tip (bright green)
        tip_length = int(12 * progress)
        tip_start_x = body_end_x
        tip_start_y = body_end_y
        tip_end_x = x + math.cos(angle) * (gun_length + 5 + tip_length)
        tip_end_y = y + math.sin(angle) * (gun_length + 5 + tip_length)
        
        tip_width = 5
        tip_perp_x = math.cos(perp_angle) * tip_width
        tip_perp_y = math.sin(perp_angle) * tip_width
        
        tip_points = [
            tip_start_x + tip_perp_x, tip_start_y + tip_perp_y,
            tip_end_x + tip_perp_x, tip_end_y + tip_perp_y,
            tip_end_x - tip_perp_x, tip_end_y - tip_perp_y,
            tip_start_x - tip_perp_x, tip_start_y - tip_perp_y
        ]
        self.canvas.create_polygon(tip_points, fill='#64FF64', outline=outline_color)
        
        # Energy chambers (animated - appear as gun extends)
        num_chambers = int(3 * progress)
        chamber_size = 4
        for i in range(num_chambers):
            chamber_offset = 35 + i * 15
            chamber_x = x + math.cos(angle) * chamber_offset
            chamber_y = y + math.sin(angle) * chamber_offset
            
            # Top chamber
            top_x = chamber_x + math.cos(perp_angle) * (gun_width/2 + 2)
            top_y = chamber_y + math.sin(perp_angle) * (gun_width/2 + 2)
            self.canvas.create_rectangle(
                top_x - chamber_size, top_y - chamber_size,
                top_x + chamber_size, top_y + chamber_size,
                fill='#00C800', outline=outline_color
            )
            
            # Bottom chamber
            bottom_x = chamber_x - math.cos(perp_angle) * (gun_width/2 + 2)
            bottom_y = chamber_y - math.sin(perp_angle) * (gun_width/2 + 2)
            self.canvas.create_rectangle(
                bottom_x - chamber_size, bottom_y - chamber_size,
                bottom_x + chamber_size, bottom_y + chamber_size,
                fill='#00C800', outline=outline_color
            )
        
        # Handle/grip
        grip_offset = -7
        grip_x = x + math.cos(angle) * grip_offset
        grip_y = y + math.sin(angle) * grip_offset
        
        grip_length = 15
        grip_width = 10
        
        grip_start_x = grip_x - math.cos(perp_angle) * (grip_width/2)
        grip_start_y = grip_y - math.sin(perp_angle) * (grip_width/2)
        grip_end_x = grip_x + math.cos(perp_angle) * (grip_width/2)
        grip_end_y = grip_y + math.sin(perp_angle) * (grip_width/2)
        
        grip_perp_angle = angle + math.pi / 2
        grip_forward_x = math.cos(grip_perp_angle) * grip_length
        grip_forward_y = math.sin(grip_perp_angle) * grip_length
        
        grip_points = [
            grip_start_x, grip_start_y,
            grip_start_x + grip_forward_x, grip_start_y + grip_forward_y,
            grip_end_x + grip_forward_x, grip_end_y + grip_forward_y,
            grip_end_x, grip_end_y
        ]
        self.canvas.create_polygon(grip_points, fill='#006400', outline=outline_color, width=2)
        
        # Grip detail
        grip_detail_offset = grip_perp_angle
        detail_x = grip_x + math.cos(grip_detail_offset) * 8
        detail_y = grip_y + math.sin(grip_detail_offset) * 8
        self.canvas.create_rectangle(
            detail_x - 6, detail_y - 7,
            detail_x + 6, detail_y + 7,
            fill='#00C800', outline=''
        )
        
        # Power lines (animated - appear as gun extends)
        if progress > 0.3:
            line_progress = min(1.0, (progress - 0.3) / 0.7)
            line_start_offset = 30
            line_end_offset = 30 + (gun_length - 30) * line_progress
            
            for offset_mult in [-3, 3]:
                line_start_x = x + math.cos(angle) * line_start_offset + math.cos(perp_angle) * offset_mult
                line_start_y = y + math.sin(angle) * line_start_offset + math.sin(perp_angle) * offset_mult
                line_end_x = x + math.cos(angle) * line_end_offset + math.cos(perp_angle) * offset_mult
                line_end_y = y + math.sin(angle) * line_end_offset + math.sin(perp_angle) * offset_mult
                
                self.canvas.create_line(
                    line_start_x, line_start_y,
                    line_end_x, line_end_y,
                    fill='#64FF64', width=2
                )
    
    def draw_blaster(self, progress):
        """Draw weapon 2: Blaster (premium orange/red style with glow effects)"""
        if progress <= 0:
            return
        
        gun_length = int(65 * progress)
        gun_width = 16
        x, y = self.cursor_x, self.cursor_y
        angle = mouse_angle
        
        perp_angle = angle + math.pi / 2
        
        # Main body (orange/red theme)
        body_start_x = x + math.cos(angle) * 5
        body_start_y = y + math.sin(angle) * 5
        body_end_x = x + math.cos(angle) * (gun_length + 5)
        body_end_y = y + math.sin(angle) * (gun_length + 5)
        
        width_offset_x = math.cos(perp_angle) * (gun_width / 2)
        width_offset_y = math.sin(perp_angle) * (gun_width / 2)
        
        body_points = [
            body_start_x + width_offset_x, body_start_y + width_offset_y,
            body_end_x + width_offset_x, body_end_y + width_offset_y,
            body_end_x - width_offset_x, body_end_y - width_offset_y,
            body_start_x - width_offset_x, body_start_y - width_offset_y
        ]
        self.canvas.create_polygon(body_points, fill='#8B4513', outline='#FF6347', width=3)
        
        # Inner body detail
        inner_width = gun_width - 6
        inner_offset_x = math.cos(perp_angle) * (inner_width / 2)
        inner_offset_y = math.sin(perp_angle) * (inner_width / 2)
        
        inner_points = [
            body_start_x + inner_offset_x, body_start_y + inner_offset_y,
            body_end_x + inner_offset_x, body_end_y + inner_offset_y,
            body_end_x - inner_offset_x, body_end_y - inner_offset_y,
            body_start_x - inner_offset_x, body_start_y - inner_offset_y
        ]
        self.canvas.create_polygon(inner_points, fill='#A0522D', outline='')
        
        # Energy cores (glowing orange circles with pulse) - two of them
        core1_offset = 20 * progress
        core1_x = x + math.cos(angle) * core1_offset
        core1_y = y + math.sin(angle) * core1_offset
        
        # Outer glow
        pulse_size = 1 + 0.3 * math.sin(time.time() * 5)
        self.canvas.create_oval(
            core1_x - 12 * pulse_size, core1_y - 12 * pulse_size, 
            core1_x + 12 * pulse_size, core1_y + 12 * pulse_size,
            fill='#FF8C00', outline='', stipple='gray25'
        )
        # Main core
        self.canvas.create_oval(
            core1_x - 9, core1_y - 9, core1_x + 9, core1_y + 9,
            fill='#FF4500', outline='#FF8C00', width=2
        )
        # Inner bright spot
        self.canvas.create_oval(
            core1_x - 5, core1_y - 5, core1_x + 5, core1_y + 5,
            fill='#FFA500', outline=''
        )
        # Center glow
        self.canvas.create_oval(
            core1_x - 2, core1_y - 2, core1_x + 2, core1_y + 2,
            fill='#FFFF00', outline=''
        )
        
        if progress > 0.5:
            core2_offset = 40 * progress
            core2_x = x + math.cos(angle) * core2_offset
            core2_y = y + math.sin(angle) * core2_offset
            
            # Outer glow
            self.canvas.create_oval(
                core2_x - 12 * pulse_size, core2_y - 12 * pulse_size,
                core2_x + 12 * pulse_size, core2_y + 12 * pulse_size,
                fill='#FF8C00', outline='', stipple='gray25'
            )
            # Main core
            self.canvas.create_oval(
                core2_x - 9, core2_y - 9, core2_x + 9, core2_y + 9,
                fill='#FF4500', outline='#FF8C00', width=2
            )
            # Inner bright spot
            self.canvas.create_oval(
                core2_x - 5, core2_y - 5, core2_x + 5, core2_y + 5,
                fill='#FFA500', outline=''
            )
            # Center glow
            self.canvas.create_oval(
                core2_x - 2, core2_y - 2, core2_x + 2, core2_y + 2,
                fill='#FFFF00', outline=''
            )
        
        # Wide barrel tip (glowing orange)
        barrel_length = int(15 * progress)
        barrel_start_x = body_end_x
        barrel_start_y = body_end_y
        barrel_end_x = x + math.cos(angle) * (gun_length + 5 + barrel_length)
        barrel_end_y = y + math.sin(angle) * (gun_length + 5 + barrel_length)
        
        barrel_width = 10
        barrel_perp_x = math.cos(perp_angle) * barrel_width
        barrel_perp_y = math.sin(perp_angle) * barrel_width
        
        barrel_points = [
            barrel_start_x + barrel_perp_x, barrel_start_y + barrel_perp_y,
            barrel_end_x + barrel_perp_x, barrel_end_y + barrel_perp_y,
            barrel_end_x - barrel_perp_x, barrel_end_y - barrel_perp_y,
            barrel_start_x - barrel_perp_x, barrel_start_y - barrel_perp_y
        ]
        self.canvas.create_polygon(barrel_points, fill='#FF8C00', outline='#FF6347', width=2)
        
        # Barrel inner glow
        barrel_inner_width = 6
        barrel_inner_perp_x = math.cos(perp_angle) * barrel_inner_width
        barrel_inner_perp_y = math.sin(perp_angle) * barrel_inner_width
        
        barrel_inner_points = [
            barrel_start_x + barrel_inner_perp_x, barrel_start_y + barrel_inner_perp_y,
            barrel_end_x + barrel_inner_perp_x, barrel_end_y + barrel_inner_perp_y,
            barrel_end_x - barrel_inner_perp_x, barrel_end_y - barrel_inner_perp_y,
            barrel_start_x - barrel_inner_perp_x, barrel_start_y - barrel_inner_perp_y
        ]
        self.canvas.create_polygon(barrel_inner_points, fill='#FFA500', outline='')
        
        # Heat vents (animated - appear as gun extends, with glow)
        num_vents = int(3 * progress)
        vent_size = 5
        for i in range(num_vents):
            vent_offset = 28 + i * 14
            vent_x = x + math.cos(angle) * vent_offset
            vent_y = y + math.sin(angle) * vent_offset
            
            # Top vent with glow
            top_x = vent_x + math.cos(perp_angle) * (gun_width/2 + 3)
            top_y = vent_y + math.sin(perp_angle) * (gun_width/2 + 3)
            
            # Glow
            self.canvas.create_oval(
                top_x - vent_size - 2, top_y - vent_size - 2,
                top_x + vent_size + 2, top_y + vent_size + 2,
                fill='#FF4500', outline='', stipple='gray50'
            )
            # Vent
            self.canvas.create_rectangle(
                top_x - vent_size, top_y - vent_size,
                top_x + vent_size, top_y + vent_size,
                fill='#FF4500', outline='#FF8C00', width=2
            )
            
            # Bottom vent with glow
            bottom_x = vent_x - math.cos(perp_angle) * (gun_width/2 + 3)
            bottom_y = vent_y - math.sin(perp_angle) * (gun_width/2 + 3)
            
            # Glow
            self.canvas.create_oval(
                bottom_x - vent_size - 2, bottom_y - vent_size - 2,
                bottom_x + vent_size + 2, bottom_y + vent_size + 2,
                fill='#FF4500', outline='', stipple='gray50'
            )
            # Vent
            self.canvas.create_rectangle(
                bottom_x - vent_size, bottom_y - vent_size,
                bottom_x + vent_size, bottom_y + vent_size,
                fill='#FF4500', outline='#FF8C00', width=2
            )
        
        # Handle/grip
        grip_offset = -7
        grip_x = x + math.cos(angle) * grip_offset
        grip_y = y + math.sin(angle) * grip_offset
        
        grip_length = 16
        grip_width = 12
        
        grip_start_x = grip_x - math.cos(perp_angle) * (grip_width/2)
        grip_start_y = grip_y - math.sin(perp_angle) * (grip_width/2)
        grip_end_x = grip_x + math.cos(perp_angle) * (grip_width/2)
        grip_end_y = grip_y + math.sin(perp_angle) * (grip_width/2)
        
        grip_perp_angle = angle + math.pi / 2
        grip_forward_x = math.cos(grip_perp_angle) * grip_length
        grip_forward_y = math.sin(grip_perp_angle) * grip_length
        
        grip_points = [
            grip_start_x, grip_start_y,
            grip_start_x + grip_forward_x, grip_start_y + grip_forward_y,
            grip_end_x + grip_forward_x, grip_end_y + grip_forward_y,
            grip_end_x, grip_end_y
        ]
        self.canvas.create_polygon(grip_points, fill='#8B4513', outline='#FF6347', width=2)
        
        # Grip detail with glow
        grip_detail_offset = grip_perp_angle
        detail_x = grip_x + math.cos(grip_detail_offset) * 8
        detail_y = grip_y + math.sin(grip_detail_offset) * 8
        
        # Detail glow
        self.canvas.create_oval(
            detail_x - 8, detail_y - 10,
            detail_x + 8, detail_y + 10,
            fill='#FF4500', outline='', stipple='gray50'
        )
        # Detail
        self.canvas.create_rectangle(
            detail_x - 6, detail_y - 8,
            detail_x + 6, detail_y + 8,
            fill='#FF4500', outline='#FF8C00', width=2
        )
        
        # Power lines (animated - appear as gun extends, thicker and glowing)
        if progress > 0.3:
            line_progress = min(1.0, (progress - 0.3) / 0.7)
            line_start_offset = 25
            line_end_offset = 25 + (gun_length - 25) * line_progress
            
            for offset_mult in [-4, 4]:
                line_start_x = x + math.cos(angle) * line_start_offset + math.cos(perp_angle) * offset_mult
                line_start_y = y + math.sin(angle) * line_start_offset + math.sin(perp_angle) * offset_mult
                line_end_x = x + math.cos(angle) * line_end_offset + math.cos(perp_angle) * offset_mult
                line_end_y = y + math.sin(angle) * line_end_offset + math.sin(perp_angle) * offset_mult
                
                # Glow
                self.canvas.create_line(
                    line_start_x, line_start_y,
                    line_end_x, line_end_y,
                    fill='#FF8C00', width=4
                )
                # Core
                self.canvas.create_line(
                    line_start_x, line_start_y,
                    line_end_x, line_end_y,
                    fill='#FFA500', width=2
                )
    
    def draw_blaster_shots(self):
        """Draw blaster projectiles (enhanced orange energy with trails)"""
        for shot in blaster_shots:
            # Energy trail effect
            trail_length = 15
            trail_x = shot.x - math.cos(shot.angle) * trail_length
            trail_y = shot.y - math.sin(shot.angle) * trail_length
            
            # Trail gradient (multiple segments)
            for i in range(3):
                segment_progress = i / 3
    def draw_blaster_shots(self):
        """Draw blaster projectiles (enhanced orange energy with trails)"""
        for shot in blaster_shots:
            # Energy trail effect
            trail_length = 15
            trail_x = shot.x - math.cos(shot.angle) * trail_length
            trail_y = shot.y - math.sin(shot.angle) * trail_length
            
            # Trail gradient (multiple segments)
            for i in range(3):
                segment_progress = i / 3
                segment_x = trail_x + (shot.x - trail_x) * segment_progress
                segment_y = trail_y + (shot.y - trail_y) * segment_progress
                trail_size = shot.size * (0.5 + 0.5 * segment_progress)
                
                self.canvas.create_oval(
                    segment_x - trail_size, segment_y - trail_size,
                    segment_x + trail_size, segment_y + trail_size,
                    fill='#FF8C00', outline=''
                )
            
            # Outer glow (pulsing)
            pulse = 1 + 0.3 * math.sin(time.time() * 15)
            glow_size = shot.size * 1.5 * pulse
            self.canvas.create_oval(
                shot.x - glow_size, shot.y - glow_size,
                shot.x + glow_size, shot.y + glow_size,
                fill='#FF8C00', outline='', stipple='gray50'
            )
            
            # Main projectile body
            self.canvas.create_oval(
                shot.x - shot.size, shot.y - shot.size,
                shot.x + shot.size, shot.y + shot.size,
                fill='#FF8C00', outline='#FFA500', width=2
            )
            
            # Middle layer
            self.canvas.create_oval(
                shot.x - shot.size * 0.7, shot.y - shot.size * 0.7,
                shot.x + shot.size * 0.7, shot.y + shot.size * 0.7,
                fill='#FFA500', outline=''
            )
            
            # Bright center core
            self.canvas.create_oval(
                shot.x - shot.size * 0.4, shot.y - shot.size * 0.4,
                shot.x + shot.size * 0.4, shot.y + shot.size * 0.4,
                fill='#FFFF00', outline=''
            )
            
            # Hot spot
            self.canvas.create_oval(
                shot.x - 2, shot.y - 2,
                shot.x + 2, shot.y + 2,
                fill='#FFFFFF', outline=''
            )
    
    def draw_laser_particles(self):
        current_time = time.time()
        for particle in laser_particles[:]:
            age = current_time - particle.spawn_time
            if age < particle.life:
                particle.x += particle.vx
                particle.y += particle.vy
                
                alpha = 1 - (age / particle.life)
                brightness = int(255 * alpha)
                color = f'#{brightness:02x}{255:02x}{brightness:02x}'
                
                self.canvas.create_oval(
                    particle.x - particle.size, particle.y - particle.size,
                    particle.x + particle.size, particle.y + particle.size,
                    fill=color, outline=''
                )
    
    def draw_lasers(self):
        current_time = time.time()
        for laser in lasers:
            if current_time - laser.spawn_time < laser_duration:
                pulse = 1 + 0.3 * math.sin(current_time * 20)
                self.canvas.create_line(
                    laser.start_x, laser.start_y,
                    laser.end_x, laser.end_y,
                    fill='#64FF64', width=int(8 * pulse)
                )
                self.canvas.create_line(
                    laser.start_x, laser.start_y,
                    laser.end_x, laser.end_y,
                    fill='#00FF00', width=4
                )
                self.canvas.create_line(
                    laser.start_x, laser.start_y,
                    laser.end_x, laser.end_y,
                    fill='#FFFFFF', width=2
                )
    
    def draw_enemy_lasers(self):
        for elaser in enemy_lasers:
            self.canvas.create_oval(
                elaser.x - 6, elaser.y - 6,
                elaser.x + 6, elaser.y + 6,
                fill='#FF0000', outline='#FF6666', width=2
            )
            self.canvas.create_oval(
                elaser.x - 3, elaser.y - 3,
                elaser.x + 3, elaser.y + 3,
                fill='#FFFF00', outline=''
            )
    
    def draw_enemies(self):
        """Draw enhanced enemy models with unique designs and health bars"""
        for enemy in enemies:
            if enemy.alive:
                ex, ey = int(enemy.x), int(enemy.y)
                
                if time.time() - enemy.hit_time < 0.1:
                    flash = True
                else:
                    flash = False
                
                # Draw health bar above enemy
                bar_width = 40
                bar_height = 5
                bar_x = ex - bar_width // 2
                bar_y = ey - enemy_size - 12
                
                # Background (dark)
                self.canvas.create_rectangle(
                    bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                    fill='#400000', outline='#800000', width=1
                )
                
                # Health (colored based on enemy type)
                health_width = int((enemy.health / enemy.max_health) * bar_width)
                if health_width > 0:
                    if enemy.type == "normal":
                        health_color = '#FF0000'
                    elif enemy.type == "speedy":
                        health_color = '#FFFF00'
                    elif enemy.type == "double":
                        health_color = '#FF00FF'
                    
                    self.canvas.create_rectangle(
                        bar_x, bar_y, bar_x + health_width, bar_y + bar_height,
                        fill=health_color, outline=''
                    )
                
                if enemy.type == "normal":
                    # Normal: Classic red box with core
                    color = '#FFFFFF' if flash else '#FF0000'
                    outline_color = '#FFAAAA' if flash else '#8B0000'
                    
                    # Main body
                    self.canvas.create_rectangle(
                        ex - enemy_size, ey - enemy_size,
                        ex + enemy_size, ey + enemy_size,
                        fill=color, outline=outline_color, width=3
                    )
                    
                    # Energy core (glowing red)
                    self.canvas.create_oval(
                        ex - 10, ey - 10, ex + 10, ey + 10,
                        fill='#8B0000', outline='#FF0000', width=2
                    )
                    self.canvas.create_oval(
                        ex - 6, ey - 6, ex + 6, ey + 6,
                        fill='#FF4444', outline=''
                    )
                    
                    # Corner accents
                    accent_size = 5
                    self.canvas.create_rectangle(
                        ex - enemy_size, ey - enemy_size,
                        ex - enemy_size + accent_size, ey - enemy_size + accent_size,
                        fill='#8B0000', outline=''
                    )
                    self.canvas.create_rectangle(
                        ex + enemy_size - accent_size, ey - enemy_size,
                        ex + enemy_size, ey - enemy_size + accent_size,
                        fill='#8B0000', outline=''
                    )
                    self.canvas.create_rectangle(
                        ex - enemy_size, ey + enemy_size - accent_size,
                        ex - enemy_size + accent_size, ey + enemy_size,
                        fill='#8B0000', outline=''
                    )
                    self.canvas.create_rectangle(
                        ex + enemy_size - accent_size, ey + enemy_size - accent_size,
                        ex + enemy_size, ey + enemy_size,
                        fill='#8B0000', outline=''
                    )
                
                elif enemy.type == "speedy":
                    # Speedy: Sleek yellow with speed lines
                    color = '#FFFFFF' if flash else '#FFFF00'
                    outline_color = '#FFFFAA' if flash else '#DAA520'
                    
                    # Main body (slightly smaller, more aerodynamic)
                    self.canvas.create_rectangle(
                        ex - enemy_size + 3, ey - enemy_size + 3,
                        ex + enemy_size - 3, ey + enemy_size - 3,
                        fill=color, outline=outline_color, width=3
                    )
                    
                    # Speed stripes
                    for i in range(3):
                        stripe_y = ey - 12 + i * 12
                        self.canvas.create_line(
                            ex - enemy_size + 5, stripe_y,
                            ex + enemy_size - 5, stripe_y,
                            fill='#DAA520', width=2
                        )
                    
                    # Energy trail effect (behind enemy)
                    trail_offset = 8
                    self.canvas.create_rectangle(
                        ex - enemy_size - trail_offset, ey - 8,
                        ex - enemy_size, ey + 8,
                        fill='#FFFF00', outline='#FFFF00', stipple='gray50'
                    )
                    
                    # Pulsing core
                    pulse = abs(math.sin(time.time() * 10))
                    core_size = 6 + int(pulse * 4)
                    self.canvas.create_oval(
                        ex - core_size, ey - core_size,
                        ex + core_size, ey + core_size,
                        fill='#FFD700', outline='#FFA500'
                    )
                
                elif enemy.type == "double":
                    # Double: Menacing purple with dual turrets
                    color = '#FFFFFF' if flash else '#8B008B'
                    outline_color = '#FFAAFF' if flash else '#4B0082'
                    
                    # Main body (larger and more imposing)
                    self.canvas.create_rectangle(
                        ex - enemy_size, ey - enemy_size,
                        ex + enemy_size, ey + enemy_size,
                        fill=color, outline=outline_color, width=3
                    )
                    
                    # Inner frame
                    self.canvas.create_rectangle(
                        ex - enemy_size + 5, ey - enemy_size + 5,
                        ex + enemy_size - 5, ey + enemy_size - 5,
                        fill='', outline='#FF00FF', width=2
                    )
                    
                    # Calculate facing direction
                    cursor_x, cursor_y = pyautogui.position()
                    dx = cursor_x - ex
                    dy = cursor_y - ey
                    face_angle = math.atan2(dy, dx)
                    
                    # Turret positioning
                    turret_forward = 15
                    turret_base_x = ex + math.cos(face_angle) * turret_forward
                    turret_base_y = ey + math.sin(face_angle) * turret_forward
                    
                    # Perpendicular for turret separation
                    perp_angle = face_angle + math.pi / 2
                    turret_separation = 10
                    
                    # Top turret
                    turret1_x = turret_base_x + math.cos(perp_angle) * turret_separation
                    turret1_y = turret_base_y + math.sin(perp_angle) * turret_separation
                    
                    self.canvas.create_rectangle(
                        turret1_x - 6, turret1_y - 5,
                        turret1_x + 10, turret1_y + 5,
                        fill='#4B0082', outline='#FF00FF', width=2
                    )
                    # Turret barrel
                    barrel1_end_x = turret1_x + math.cos(face_angle) * 8
                    barrel1_end_y = turret1_y + math.sin(face_angle) * 8
                    self.canvas.create_line(
                        turret1_x + 10, turret1_y,
                        barrel1_end_x + 10, barrel1_end_y,
                        fill='#FF00FF', width=3
                    )
                    
                    # Bottom turret
                    turret2_x = turret_base_x - math.cos(perp_angle) * turret_separation
                    turret2_y = turret_base_y - math.sin(perp_angle) * turret_separation
                    
                    self.canvas.create_rectangle(
                        turret2_x - 6, turret2_y - 5,
                        turret2_x + 10, turret2_y + 5,
                        fill='#4B0082', outline='#FF00FF', width=2
                    )
                    # Turret barrel
                    barrel2_end_x = turret2_x + math.cos(face_angle) * 8
                    barrel2_end_y = turret2_y + math.sin(face_angle) * 8
                    self.canvas.create_line(
                        turret2_x + 10, turret2_y,
                        barrel2_end_x + 10, barrel2_end_y,
                        fill='#FF00FF', width=3
                    )
                    
                    # Central energy cores (two glowing orbs)
                    core_offset = 8
                    self.canvas.create_oval(
                        ex - core_offset - 5, ey - 5,
                        ex - core_offset + 5, ey + 5,
                        fill='#FF00FF', outline='#FF00FF'
                    )
                    self.canvas.create_oval(
                        ex + core_offset - 5, ey - 5,
                        ex + core_offset + 5, ey + 5,
                        fill='#FF00FF', outline='#FF00FF'
                    )
    
    def update_display(self):
        self.cursor_x, self.cursor_y = pyautogui.position()
        
        self.canvas.delete('all')
        
        self.draw_enemies()
        self.draw_enemy_lasers()
        self.draw_blaster_shots()
        self.draw_laser_particles()
        self.draw_lasers()
        
        # Draw active weapon
        if active_weapon == 1:
            self.draw_laser_rifle(weapon_1_progress)
        elif active_weapon == 2:
            self.draw_blaster(weapon_2_progress)
        
        self.draw_green_box()
        self.draw_health_bar()
        
        if running:
            self.root.after(16, self.update_display)
    
    def run(self):
        self.root.mainloop()

def find_nearest_enemy(cursor_x, cursor_y):
    nearest_enemy = None
    min_distance = float('inf')
    
    for enemy in enemies:
        if enemy.alive:
            dx = enemy.x - cursor_x
            dy = enemy.y - cursor_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
    
    return nearest_enemy, min_distance

def check_laser_hits():
    """Check if laser rifle hits enemies - deals 25 damage"""
    for laser in lasers:
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            dx = laser.end_x - laser.start_x
            dy = laser.end_y - laser.start_y
            length = math.sqrt(dx*dx + dy*dy)
            
            if length == 0:
                continue
            
            t = max(0, min(1, ((enemy.x - laser.start_x) * dx + (enemy.y - laser.start_y) * dy) / (length * length)))
            closest_x = laser.start_x + t * dx
            closest_y = laser.start_y + t * dy
            
            dist = math.sqrt((enemy.x - closest_x)**2 + (enemy.y - closest_y)**2)
            
            if dist < enemy_size:
                enemy.health -= 5
                enemy.hit_time = time.time()
                if enemy.health <= 0:
                    enemy.alive = False

def check_blaster_hits():
    """Check if blaster shots hit enemies - deals 5 damage per shot"""
    for shot in blaster_shots[:]:
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            dist = math.sqrt((shot.x - enemy.x)**2 + (shot.y - enemy.y)**2)
            
            if dist < enemy_size + shot.size:
                enemy.health -= 3
                enemy.hit_time = time.time()
                if enemy.health <= 0:
                    enemy.alive = False
                if shot in blaster_shots:
                    blaster_shots.remove(shot)
                break

def check_enemy_laser_hits():
    global player_health, running
    
    cursor_x, cursor_y = pyautogui.position()
    
    for elaser in enemy_lasers[:]:
        dist = math.sqrt((elaser.x - cursor_x)**2 + (elaser.y - cursor_y)**2)
        
        if dist < box_size:
            player_health -= 10
            enemy_lasers.remove(elaser)
            print(f"Hit! Health: {player_health}/{max_health}")
            
            if player_health <= 0:
                print("GAME OVER!")
                running = False
                return

def spawn_enemies():
    cursor_x, cursor_y = pyautogui.position()
    alive_count = sum(1 for e in enemies if e.alive)
    
    while alive_count < max_enemies:
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(250, 450)
        x = cursor_x + math.cos(angle) * distance
        y = cursor_y + math.sin(angle) * distance
        
        # Spawn different enemy types
        enemy_type = random.choices(
            ["normal", "speedy", "double"],
            weights=[60, 25, 15]
        )[0]
        
        enemies.append(Enemy(x, y, enemy_type))
        alive_count += 1

def game_loop_thread():
    global running
    
    while running:
        try:
            cursor_x, cursor_y = pyautogui.position()
            
            for enemy in enemies[:]:
                if enemy.alive:
                    enemy.update(cursor_x, cursor_y)
                    enemy.try_shoot(cursor_x, cursor_y)
                elif time.time() - enemy.hit_time > 0.5:
                    enemies.remove(enemy)
            
            for elaser in enemy_lasers[:]:
                elaser.update()
                if elaser.distance_traveled > 1000:
                    enemy_lasers.remove(elaser)
            
            # Update blaster shots
            for shot in blaster_shots[:]:
                shot.update()
                if time.time() - shot.spawn_time > blaster_shot_lifetime:
                    blaster_shots.remove(shot)
            
            current_time = time.time()
            laser_particles[:] = [p for p in laser_particles if current_time - p.spawn_time < p.life]
            
            check_laser_hits()
            check_blaster_hits()
            check_enemy_laser_hits()
            
            lasers[:] = [l for l in lasers if current_time - l.spawn_time < laser_duration]
            enemy_lasers[:] = [l for l in enemy_lasers if current_time - l.spawn_time < enemy_laser_duration]
            
            spawn_enemies()
            
            time.sleep(0.03)
        except Exception as e:
            print(f"Game loop error: {e}")

def animation_thread():
    global weapon_1_progress, weapon_2_progress, mouse_angle, target_mouse_angle, running
    
    while running:
        try:
            # Weapon 1 animation
            if abs(weapon_1_progress - weapon_1_target) > 0.01:
                if weapon_1_progress < weapon_1_target:
                    weapon_1_progress = min(weapon_1_target, weapon_1_progress + 0.12)
                else:
                    weapon_1_progress = max(weapon_1_target, weapon_1_progress - 0.12)
            
            # Weapon 2 animation
            if abs(weapon_2_progress - weapon_2_target) > 0.01:
                if weapon_2_progress < weapon_2_target:
                    weapon_2_progress = min(weapon_2_target, weapon_2_progress + 0.15)
                else:
                    weapon_2_progress = max(weapon_2_target, weapon_2_progress - 0.15)
            
            # Smooth rotation
            angle_diff = target_mouse_angle - mouse_angle
            
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            mouse_angle += angle_diff * 0.2
            
            time.sleep(0.016)
        except Exception as e:
            print(f"Animation error: {e}")

def mouse_direction_thread():
    global target_mouse_angle, last_mouse_x, last_mouse_y, running
    
    last_mouse_x, last_mouse_y = pyautogui.position()
    aim_assist_range = 400
    
    while running:
        try:
            current_x, current_y = pyautogui.position()
            
            dx = current_x - last_mouse_x
            dy = current_y - last_mouse_y
            
            if abs(dx) > 1 or abs(dy) > 1:
                base_angle = math.atan2(dy, dx)
                last_mouse_x = current_x
                last_mouse_y = current_y
            else:
                base_angle = target_mouse_angle
            
            # Aim assist only for weapon 1
            if active_weapon == 1:
                nearest_enemy, distance = find_nearest_enemy(current_x, current_y)
                
                if nearest_enemy and distance < aim_assist_range:
                    enemy_dx = nearest_enemy.x - current_x
                    enemy_dy = nearest_enemy.y - current_y
                    enemy_angle = math.atan2(enemy_dy, enemy_dx)
                    
                    assist_strength = 1.0 - (distance / aim_assist_range)
                    assist_strength = assist_strength ** 2
                    
                    angle_diff = enemy_angle - base_angle
                    
                    while angle_diff > math.pi:
                        angle_diff -= 2 * math.pi
                    while angle_diff < -math.pi:
                        angle_diff += 2 * math.pi
                    
                    target_mouse_angle = base_angle + (angle_diff * assist_strength)
                else:
                    target_mouse_angle = base_angle
            else:
                target_mouse_angle = base_angle
            
            time.sleep(0.03)
        except Exception as e:
            print(f"Direction tracking error: {e}")

def input_thread():
    global running, weapon_1_out, weapon_2_out, weapon_1_target, weapon_2_target, active_weapon
    global last_weapon_1_fire, weapon_2_firing
    
    ctrl_1_pressed = False
    ctrl_2_pressed = False
    left_click_was_down = False
    
    print("🎮 Controls:")
    print("  Ctrl+1: Laser Rifle (single shot, 0.5s cooldown, aim assist)")
    print("  Ctrl+2: Blaster (hold to fire, semi-auto)")
    print("  Q: Quit")
    print("💀 Enemies:")
    print("  Red: Normal")
    print("  Yellow: Speedy (fast movement)")
    print("  Magenta: Double (fires 2 shots)")
    
    while running:
        try:
            import win32api
            import win32con
            
            ctrl_pressed = win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000
            key_1_pressed = win32api.GetAsyncKeyState(ord('1')) & 0x8000
            key_2_pressed = win32api.GetAsyncKeyState(ord('2')) & 0x8000
            
            # Weapon 1 toggle
            if ctrl_pressed and key_1_pressed and not ctrl_1_pressed:
                ctrl_1_pressed = True
                weapon_1_out = not weapon_1_out
                weapon_1_target = 1.0 if weapon_1_out else 0.0
                
                if weapon_1_out:
                    active_weapon = 1
                    weapon_2_out = False
                    weapon_2_target = 0.0
                    print("⚡ Laser Rifle deployed")
                else:
                    active_weapon = 0
                    print("⚡ Laser Rifle retracted")
            elif not (ctrl_pressed and key_1_pressed):
                ctrl_1_pressed = False
            
            # Weapon 2 toggle
            if ctrl_pressed and key_2_pressed and not ctrl_2_pressed:
                ctrl_2_pressed = True
                weapon_2_out = not weapon_2_out
                weapon_2_target = 1.0 if weapon_2_out else 0.0
                
                if weapon_2_out:
                    active_weapon = 2
                    weapon_1_out = False
                    weapon_1_target = 0.0
                    print("💥 Blaster deployed")
                else:
                    active_weapon = 0
                    print("💥 Blaster retracted")
            elif not (ctrl_pressed and key_2_pressed):
                ctrl_2_pressed = False
            
            # Shooting
            left_click = win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000
            
            if left_click and not left_click_was_down:
                left_click_was_down = True
                
                # Weapon 1: Single shot with cooldown
                if active_weapon == 1 and weapon_1_progress > 0.9:
                    current_time = time.time()
                    if current_time - last_weapon_1_fire >= weapon_1_cooldown:
                        last_weapon_1_fire = current_time
                        cursor_x, cursor_y = pyautogui.position()
                        
                        gun_tip_offset = int(70 * weapon_1_progress) + 12
                        gun_tip_x = cursor_x + math.cos(mouse_angle) * gun_tip_offset
                        gun_tip_y = cursor_y + math.sin(mouse_angle) * gun_tip_offset
                        
                        lasers.append(Laser(gun_tip_x, gun_tip_y, mouse_angle))
                        
                        for _ in range(8):
                            laser_particles.append(LaserParticle(gun_tip_x, gun_tip_y, mouse_angle))
            
            # Weapon 2: Hold to fire (semi-auto)
            if left_click and active_weapon == 2 and weapon_2_progress > 0.9:
                if not weapon_2_firing:
                    weapon_2_firing = True
                    cursor_x, cursor_y = pyautogui.position()
                    
                    gun_tip_offset = int(60 * weapon_2_progress) + 20
                    gun_tip_x = cursor_x + math.cos(mouse_angle) * gun_tip_offset
                    gun_tip_y = cursor_y + math.sin(mouse_angle) * gun_tip_offset
                    
                    blaster_shots.append(BlasterShot(gun_tip_x, gun_tip_y, mouse_angle))
            else:
                weapon_2_firing = False
            
            if not left_click:
                left_click_was_down = False
            
            time.sleep(0.005)
            
        except Exception as e:
            print(f"Input error: {e}")
            time.sleep(0.1)

def main():
    global running
    
    print("🚀 Starting game...")
    
    game_thread = threading.Thread(target=game_loop_thread, daemon=True)
    game_thread.start()
    
    anim_thread = threading.Thread(target=animation_thread, daemon=True)
    anim_thread.start()
    
    direction_thread = threading.Thread(target=mouse_direction_thread, daemon=True)
    direction_thread.start()
    
    input_t = threading.Thread(target=input_thread, daemon=True)
    input_t.start()
    
    try:
        app = OverlayApp()
        app.run()
    except KeyboardInterrupt:
        print("\n❌ Interrupted")
    finally:
        running = False
        print("👋 Game Over! Thanks for playing!")

if __name__ == "__main__":
    main()
