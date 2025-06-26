from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from math import sin
import socket
import threading

app = Ursina(title='Synapse 3D')

window.borderless = False
window.title = 'Synapse 3D'
window.size = (1280, 720)
window.color = color.azure

# Simple ground (collider enabled)
ground = Entity(model='plane', scale=(100,1,100), color=color.green, texture='white_cube', texture_scale=(100,100), collider='box', position=(0,0,0))

# First person controller
player = FirstPersonController(y=2, origin_y=-.5, speed=5)

# Add simple arms and legs as children of the camera_pivot for visibility
left_arm = Entity(parent=player.camera_pivot, model='cube', color=color.orange, scale=(0.18,0.6,0.18), position=(-0.25,-0.35,0.6), origin=(0,0.5,0))
right_arm = Entity(parent=player.camera_pivot, model='cube', color=color.orange, scale=(0.18,0.6,0.18), position=(0.25,-0.35,0.6), origin=(0,0.5,0))
left_leg = Entity(parent=player.camera_pivot, model='cube', color=color.brown, scale=(0.22,0.7,0.22), position=(-0.13,-0.95,0.7), origin=(0,0.5,0))
right_leg = Entity(parent=player.camera_pivot, model='cube', color=color.brown, scale=(0.22,0.7,0.22), position=(0.13,-0.95,0.7), origin=(0,0.5,0))

# Add punch state
punching = False
punch_timer = 0

def input(key):
    global punching, punch_timer
    if key == 'left mouse down' and not punching:
        punching = True
        punch_timer = 0.25  # punch duration in seconds
        left_arm.rotation_x = -90  # quick punch forward

# Networking setup
SERVER_IP = '127.0.0.1'  # Change to server's IP if needed
SERVER_PORT = 50007
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))
sock.setblocking(False)

other_players = {}

def sync_network():
    # Send our position
    pos = f'{player.x:.2f},{player.y:.2f},{player.z:.2f}'
    try:
        sock.sendall(pos.encode())
        data = sock.recv(4096)
        if data:
            lines = data.decode().split('\n')
            for line in lines:
                if not line.strip(): continue
                pid, p = line.split(':')
                if pid == str(sock.getsockname()):
                    continue  # Don't spawn yourself
                x, y, z = map(float, p.split(','))
                if pid not in other_players:
                    other_players[pid] = Entity(model='cube', color=color.red, scale=(0.5,1,0.5), position=(x,y,z))
                else:
                    other_players[pid].position = (x, y, z)
    except BlockingIOError:
        pass
    except Exception as e:
        print('Network error:', e)

def update():
    global punching, punch_timer
    t = time.time() * 8
    moving = held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']
    if punching:
        punch_timer -= time.dt
        if punch_timer <= 0:
            punching = False
    if not punching:
        if moving:
            arm_swing = sin(t) * 40
            leg_swing = sin(t) * 30
        else:
            arm_swing = 0
            leg_swing = 0
        left_arm.rotation_x = arm_swing
        right_arm.rotation_x = -arm_swing
        left_leg.rotation_x = -leg_swing
        right_leg.rotation_x = leg_swing
    sync_network()

app.run()
