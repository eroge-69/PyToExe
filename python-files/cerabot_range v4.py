#WIP -- FUCKING PERFECT KITING
import pydirectinput
import time
import pymem
import pymem.exception
import threading
import frida
import pyautogui
import bresenham
import json
import random
import tkinter as tk
from pynput import mouse, keyboard
from tkinter import ttk
from queue import PriorityQueue

#memory addresses
walkAddress = "0xE8B70"
npcAddress = "0x1EA8A6"
directionalAddress = "0x6A66E"
varOffset = 0x9C
totalExp = None

START_ADDR = 0x00180000
END_ADDR   = 0x0019FFFF
STEP       = 4         

x_address = None
y_address = None
directional_address = None
combat_baseline_exp = None
current_target_npc = None
xstarted = 0
debug = 0
pyautogui.PAUSE = 0
last_direction = None
wandering_target = None
stuck_timer_start = None
last_position = None
pm = None  # Global pymem instance

def initialize_pymem():
    global pm
    if pm is None:
        pm = pymem.Pymem("Endless.exe")

def press_key(key, presses=2, delay=0.1):
    """
    Presses a key and optionally waits for a specified delay.
    """
    pydirectinput.press(key, presses)
    time.sleep(delay)

def hold_key(key):
    pydirectinput.keyDown(key)

def release_key(key):
    pydirectinput.keyUp(key)

def on_message_xy(message, data):
    global xstarted, x_address, y_address
    if message['type'] == 'send':
        addresses = message['payload']
        x_address = int(addresses['x_address'], 16)
        y_address = int(addresses['y_address'], 16)
        if debug == 1:
            print(f"X Address: {hex(x_address)}, Y Address: {hex(y_address)}")
        # Mark as completed and detach session
        xstarted = 1
        session.detach()
    else:
        print(f"Error: {message}")

def scan_for_exp_address(pm: pymem.Pymem, search_value: int) -> int:
    """
    Scan memory from START_ADDR up to END_ADDR in 4‑byte steps.
    Returns the first address where pm.read_int(addr) == search_value.
    """
    for addr in range(START_ADDR, END_ADDR, STEP):
        try:
            value = pm.read_int(addr)
        except pymem.exception.MemoryReadError:
            # some pages can’t be read—just skip them
            continue

        if value == search_value:
            print(f"[+] Found EXP value {search_value} at {hex(addr)}")
            return addr

    raise RuntimeError(f"Couldn’t find {search_value} in 0x{START_ADDR:X}–0x{END_ADDR:X}")

def start_frida_session_xy(walk_address):
    global session
    session = frida.attach("Endless.exe")
    print("XY Started - Waiting for you to move to begin")
    script_code = f"""
    var baseAddress = Module.findBaseAddress("Endless.exe").add(ptr({walk_address}));
    Interceptor.attach(baseAddress, {{
        onEnter: function(args) {{
            var xAddress = this.context.ecx.add(0x08);
            var yAddress = xAddress.add(0x04);
            send({{x_address: xAddress.toString(), y_address: yAddress.toString()}});
        }}
    }});
    """
    script = session.create_script(script_code)
    script.on('message', on_message_xy)
    script.load()

    while xstarted == 0:
        continue

    print("Session completed and detached.")

def on_message_directional(message, data):
    global directional_address, xstarted
    if message['type'] == 'send':
        payload = message['payload']
        directional_address = int(payload.get('directional_address'), 16)
        character_direction = payload.get('character_direction')
        if debug == 1:
            print(f"Character Direction Address: {directional_address}")
            print(f"Character Direction Value: {character_direction}")
        xstarted = 2
        session.detach()
    elif message['type'] == 'error':
        print(f"Error: {message['stack']}")

def start_frida_session_directional(target_address):
    global session
    session = frida.attach("Endless.exe")
    print("Directional Started - Waiting for mov [ebx+55],dl to execute")
    script_code = f"""
    var baseAddress = Module.findBaseAddress("Endless.exe").add(ptr("{target_address}"));
    Interceptor.attach(baseAddress, {{
        onEnter: function(args) {{
            var ebxValue = this.context.ebx;
            var characterDirectionAddress = ebxValue.add(0x55);
            var characterDirection = characterDirectionAddress.readU8();
            send({{directional_address: characterDirectionAddress.toString(), character_direction: characterDirection.toString()}});
        }}
    }});
    """
    script = session.create_script(script_code)
    script.on('message', on_message_directional)
    script.load()

    while xstarted == 1:
        continue

    print("Directional Session Completed.")

def patch_adds_with_nops():
    # attach to the process
    session = frida.attach("Endless.exe")

    # inline the two absolute addresses you want to NOP
    js = """
    [0x005E9419, 0x005E9433].forEach(function(addr) {
        // make the 7 bytes at addr writeable
        Memory.protect(ptr(addr), 7, 'rwx');
        // overwrite them with NOP (0x90)
        for (var i = 0; i < 7; i++) {
          Memory.writeU8(ptr(addr).add(i), 0x90);
        }
        // restore as RX
        Memory.protect(ptr(addr), 7, 'r-x');
    });
    """

    script = session.create_script(js)
    script.load()
    session.detach()

class PlayerDataManager:
    def __init__(self):
        self.data = {
            "x": 0,
            "y": 0,
            "direction": 0
        }

    def update(self, x, y, direction):
        self.data["x"] = x
        self.data["y"] = y
        self.data["direction"] = direction

    def get_data(self):
        return self.data

class AddressManager:
    def __init__(self):
        self.addresses = {}

    def add_address(self, address):
        address1 = int(address, 16)
        address2 = address1 + 2
        address1_hex = hex(address1).upper()
        address2_hex = hex(address2).upper()
        if address1_hex not in self.addresses:
            self.addresses[address1_hex] = {
                "paired_address": address2_hex,
                "last_x": None,
                "last_y": None,
                "last_moved": time.time(),
                "is_dead_counter": 0,
                "last_is_dead_value": None
            }
            return True
        return False

    def remove_address(self, address):
        address1 = int(address, 16)
        address1_hex = hex(address1).upper()
        if address1_hex in self.addresses:
            del self.addresses[address1_hex]
            return True
        return False

    def list_addresses(self):
        return [{"X": x, "Y": data["paired_address"]} for x, data in self.addresses.items()]

manager = AddressManager()
player_data_manager = PlayerDataManager()
map_data = []

class PlayerDataPopup:
    def __init__(self, player_data_manager):
        self.player_data_manager = player_data_manager
        self.root = tk.Tk()
        self.root.title("Player Data")
        self.labels = {}
        self.create_widgets()
        self.create_styles()
        self.update_ui()

    def create_widgets(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        for idx, text in enumerate(["X", "Y", "Direction"], start=2):
            ttk.Label(self.frame, text=text).grid(row=idx, column=0, sticky=tk.W)
            value_label = ttk.Label(self.frame, text="0")
            value_label.grid(row=idx, column=1, sticky=tk.E)
            self.labels[text] = value_label
        self.canvas = tk.Canvas(self.frame, width=200, height=200, bg="white")
        self.canvas.grid(row=0, column=2, rowspan=6, padx=10)

    def create_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('default')
        style.configure("red.Horizontal.TProgressbar", troughcolor='white', background='red')
        style.configure("blue.Horizontal.TProgressbar", troughcolor='white', background='blue')

    def update_ui(self):
        data = self.player_data_manager.get_data()
        self.labels["X"].config(text=data["x"])
        self.labels["Y"].config(text=data["y"])
        self.labels["Direction"].config(text=data["direction"])
        self.draw_map()
        self.root.after(100, self.update_ui)

    def draw_map(self):
        # Clear previous drawings.
        self.canvas.delete("all")
        # Set canvas and grid parameters.
        canvas_size = 200
        max_x = 20
        max_y = 20
        cell_width = canvas_size / max_x
        cell_height = canvas_size / max_y
        # Draw a gray background covering the entire canvas.
        self.canvas.create_rectangle(0, 0, canvas_size, canvas_size, fill="gray", outline="")     
        # Draw vertical grid lines.
        for i in range(max_x + 1):
            x = i * cell_width
            self.canvas.create_line(x, 0, x, canvas_size, fill="black")
        # Draw horizontal grid lines.
        for j in range(max_y + 1):
            y = j * cell_height
            self.canvas.create_line(0, y, canvas_size, y, fill="black")
        # Get player data.
        data = self.player_data_manager.get_data()
        player_x = data["x"]
        player_y = data["y"]
        # Define the center of the canvas.
        center_x = canvas_size / 2
        center_y = canvas_size / 2
        player_radius = 5
        # Draw the player at the center of the canvas.
        self.canvas.create_oval(center_x - player_radius, center_y - player_radius,
                                center_x + player_radius, center_y + player_radius,
                                fill="orange", outline="black")
        # Draw NPC markers.
        for item in map_data:
            if item["type"] == "npc":
                npc_x = item["X"]
                npc_y = item["Y"]
                # Map world coordinates to canvas positions relative to the player.
                canvas_x = center_x + (npc_x - player_x) * cell_width
                canvas_y = center_y + (npc_y - player_y) * cell_height
                self.canvas.create_oval(canvas_x - 3, canvas_y - 3,
                                        canvas_x + 3, canvas_y + 3,
                                        fill="red", outline="black")
    def run(self):
        self.root.mainloop()

def check_player_data(x_address, y_address, directional_address):
    global pm
    initialize_pymem()
    try:
        temp_map_data = []
        while True:
            try:
                x = pm.read_short(x_address)
                y = pm.read_short(y_address)
                direction = pm.read_bytes(directional_address, 1)[0]
                player_data_manager.update(x, y, direction)
                temp_map_data = [{
                    "type": "player",
                    "X": x,
                    "Y": y,
                    "direction": direction
                }]
                for addr, data in list(manager.addresses.items()):
                    address_x = int(addr, 16)
                    address_y = int(data["paired_address"], 16)
                    try:
                        value_x = pm.read_short(address_x)
                        value_y = pm.read_short(address_y)
                        # --- Keep track of NPC last position for looting ---
                        manager.addresses[addr]["last_x"] = value_x
                        manager.addresses[addr]["last_y"] = value_y
                        temp_map_data.append({
                            "type": "npc",
                            "X": value_x,
                            "Y": value_y,
                            "address_x": addr,
                            "address_y": data["paired_address"]
                        })
                    except:
                        pass
                map_data.clear()
                map_data.extend(temp_map_data)
            except Exception as e:
                print(f"Error reading player data: {e}")
            time.sleep(0.1)
    except Exception as e:
        print(f"Failed to initialize memory reading: {e}")

def on_message(message, data):
    if message['type'] == 'send':
        payload = message['payload']
        action = payload.get('action')
        address = payload.get('address')
        if action == 'add' and address is not None:
            manager.add_address(address)

def start_frida(npc_address):
    print("Npc Started")
    frida_script = f"""
Interceptor.attach(Module.findBaseAddress("Endless.exe").add({npc_address}), {{
    onEnter: function(args) {{
        var eax = this.context.eax.toInt32();
        var offset = {varOffset};
        var address = eax + offset;
        var addressHex = '0x' + address.toString(16).toUpperCase();
        send({{action: 'add', address: addressHex}});
    }}
}});
"""
    session = frida.attach("Endless.exe")
    script = session.create_script(frida_script)
    script.on('message', on_message)
    script.load()

def load_walkable_tiles(file_path='walkable.json'):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if 'safe_tiles' in data and data['safe_tiles']:
                return {(tile['X'], tile['Y']) for tile in data['safe_tiles']}
            else:
                print("No valid tiles found in file, using default walkable tiles.")
                return {(x, y) for x in range(101) for y in range(101)}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading walkable tiles: {e}. Using default walkable tiles.")
        return {(x, y) for x in range(101) for y in range(101)}

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar_pathfinding(start, goal, walkable_tiles):
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    while not open_set.empty():
        _, current = open_set.get()
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in walkable_tiles:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    open_set.put((f_score[neighbor], neighbor))
    return None

def find_closest_npc(player_x, player_y, npcs):
    closest_npc = None
    min_distance = float('inf')
    for npc in npcs:
        distance = abs(player_x - npc['X']) + abs(player_y - npc['Y'])
        if distance < min_distance:
            min_distance = distance
            closest_npc = npc
    return closest_npc

pause_flag = False

def key_listener():
    global pause_flag
    import keyboard
    while True:
        if keyboard.is_pressed(','):
            pause_flag = True
            print("Pausing for 1 minute...")
            time.sleep(60)
            pause_flag = False
            print("Resuming combat...")
        time.sleep(0.1)

last_combat_time = time.time()
sitting = False

def combat_thread():
    global last_combat_time, sitting, pause_flag
    walkable_tiles = set(load_walkable_tiles()) or {(x, y) for x in range(101) for y in range(101)}
    last_direction = None
    wandering_target = None
    stuck_timer_start = None
    last_position = None
    ctrl_pressed = False
    blocked_tiles = {}
    movement_start_time = None
    target_tile = None

    while True:
        if pause_flag:
            time.sleep(1)
            continue

        current_time = time.time()
        blocked_tiles = {tile: expire_time for tile, expire_time in blocked_tiles.items() if expire_time > current_time}
        adjusted_walkable_tiles = walkable_tiles.difference(blocked_tiles.keys())

        if map_data:
            player = next(item for item in map_data if item["type"] == "player")
            npcs = [item for item in map_data if item["type"] == "npc"]
            valid_npcs = [npc for npc in npcs if (npc['X'], npc['Y']) in adjusted_walkable_tiles]

            if not valid_npcs:
                if ctrl_pressed:
                    release_key('ctrl')
                    ctrl_pressed = False
                else:
                    if last_position and (player['X'], player['Y']) == last_position:
                        if not stuck_timer_start:
                            stuck_timer_start = time.time()
                        elif time.time() - stuck_timer_start > 2:
                            print("Detected being stuck for 2 seconds, regenerating wandering target.")
                            wandering_target = random.choice(list(adjusted_walkable_tiles))
                            stuck_timer_start = None
                    else:
                        stuck_timer_start = None
                        last_position = (player['X'], player['Y'])
                    if not wandering_target or (player['X'], player['Y']) == wandering_target:
                        wandering_target = random.choice(list(adjusted_walkable_tiles))
                    path_to_wander = astar_pathfinding((player['X'], player['Y']), wandering_target, adjusted_walkable_tiles)
                    if path_to_wander and len(path_to_wander) > 1:
                        move_to_x, move_to_y = path_to_wander[1]
                        current_direction = None
                        if player['X'] < move_to_x:
                            current_direction = 'right'
                        elif player['X'] > move_to_x:
                            current_direction = 'left'
                        if player['Y'] < move_to_y:
                            current_direction = 'down'
                        elif player['Y'] > move_to_y:
                            current_direction = 'up'
                        if current_direction:
                            if current_direction != last_direction:
                                press_key(current_direction, 2, 0.05)
                            else:
                                press_key(current_direction, 1, 0.05)
                            last_direction = current_direction
                        player['X'], player['Y'] = move_to_x, move_to_y
                        print(f"Moving to tile: ({move_to_x}, {move_to_y})")
                continue

            if not sitting:
                npc_positions = {(npc['X'], npc['Y']) for npc in valid_npcs}
                extended_walkable_tiles = adjusted_walkable_tiles.difference(npc_positions)
                if valid_npcs:
                    closest_npc = find_closest_npc(player['X'], player['Y'], valid_npcs)
                    # Set the global current target using the NPC's address key.
                    global current_target_npc
                    current_target_npc = closest_npc.get("address_x")
                    print(f"Current target set to: {current_target_npc}")

                    npc_x, npc_y = closest_npc['X'], closest_npc['Y']
                    player_x, player_y = player['X'], player['Y']
                    distance_x = abs(player_x - npc_x)
                    distance_y = abs(player_y - npc_y)
                    if (distance_x == 2 and player_y == npc_y) or (distance_y == 2 and player_x == npc_x):
                        line_of_sight = list(bresenham.bresenham(player_x, player_y, npc_x, npc_y))
                        line_of_sight_safe = all((x, y) in walkable_tiles for x, y in line_of_sight)
                        if line_of_sight_safe:
                            target_direction = None
                            if npc_x > player_x:
                                target_direction = 3  # East
                            elif npc_x < player_x:
                                target_direction = 1  # West
                            elif npc_y > player_y:
                                target_direction = 0  # South
                            elif npc_y < player_y:
                                target_direction = 2  # North
                            if player['direction'] != target_direction:
                                time.sleep(0.2)
                                press_key(['down', 'left', 'up', 'right'][target_direction], 1, 0.05)
                            if not ctrl_pressed:
                                hold_key('ctrl')
                                ctrl_pressed = True
                            last_combat_time = time.time()
                            continue

                    else:
                        if ctrl_pressed:
                            release_key('ctrl')
                            ctrl_pressed = False
                        potential_positions = [
                            (npc_x - 2, npc_y), (npc_x + 2, npc_y),
                            (npc_x, npc_y - 2), (npc_x, npc_y + 2)
                        ]
                        valid_positions = [pos for pos in potential_positions if pos in extended_walkable_tiles]
                        if valid_positions:
                            paths = [(astar_pathfinding((player_x, player_y), target, extended_walkable_tiles), target) for target in valid_positions]
                            paths = [path for path in paths if path[0]]
                            if paths:
                                best_path, best_target = min(paths, key=lambda x: len(x[0]))
                                move_to_x, move_to_y = best_path[1]
                                if (move_to_x, move_to_y) != target_tile:
                                    movement_start_time = current_time
                                    target_tile = (move_to_x, move_to_y)
                                current_direction = None
                                if player_x < move_to_x:
                                    current_direction = 'right'
                                elif player_x > move_to_x:
                                    current_direction = 'left'
                                if player_y < move_to_y:
                                    current_direction = 'down'
                                elif player_y > move_to_y:
                                    current_direction = 'up'
                                if current_direction:
                                    if current_direction != last_direction:
                                        press_key(current_direction, 2, 0.05)
                                    else:
                                        press_key(current_direction, 1, 0.05)
                                    last_direction = current_direction
                                player['X'], player['Y'] = move_to_x, move_to_y
                                print(f"Moving to tile: ({move_to_x}, {move_to_y})")
                                if movement_start_time and (current_time - movement_start_time) > 2:
                                    if (player['X'], player['Y']) != move_to_x or (player['X'], player['Y']) != move_to_y:
                                        blocked_tiles[(move_to_x, move_to_y)] = current_time + 3
                                        print(f"Marking tile as blocked: ({move_to_x}, {move_to_y}) for 3 seconds")
                                    movement_start_time = None
                            continue
                        else:
                            paths = [(astar_pathfinding((player_x, player_y), target, walkable_tiles), target) for target in potential_positions]
                            paths = [path for path in paths if path[0]]
                            if paths:
                                best_path, best_target = min(paths, key=lambda x: len(x[0]))
                                move_to_x, move_to_y = best_path[1]
                                if (move_to_x, move_to_y) != target_tile:
                                    movement_start_time = current_time
                                    target_tile = (move_to_x, move_to_y)
                                current_direction = None
                                if player_x < move_to_x:
                                    current_direction = 'right'
                                elif player_x > move_to_x:
                                    current_direction = 'left'
                                if player_y < move_to_y:
                                    current_direction = 'down'
                                elif player_y > move_to_y:
                                    current_direction = 'up'
                                if current_direction:
                                    if current_direction != last_direction:
                                        press_key(current_direction, 2, 0.05)
                                    else:
                                        press_key(current_direction, 1, 0.05)
                                    last_direction = current_direction
                                player['X'], player['Y'] = move_to_x, move_to_y
                                print(f"Moving to tile: ({move_to_x}, {move_to_y})")
                                if movement_start_time and (current_time - movement_start_time) > 2:
                                    if (player['X'], player['Y']) != move_to_x or (player['X'], player['Y']) != move_to_y:
                                        blocked_tiles[(move_to_x, move_to_y)] = current_time + 3
                                        print(f"Marking tile as blocked: ({move_to_x}, {move_to_y}) for 3 seconds")
                                    movement_start_time = None
                            continue
        if ctrl_pressed:
            release_key('ctrl')
            ctrl_pressed = False

# =========================
# AUT0-LOOT PATCH STARTS HERE
# =========================

def convert_to_screen_coordinates(game_x, game_y):
    # You may need to adjust this function to map game coords to screen coords.
    # If game world and window are 1:1, this works; otherwise add scaling/offset logic.
    return int(game_x), int(game_y)

def loot_npc(npc_address):
    # Looks up the last known X, Y of the NPC and clicks there.
    data = manager.addresses.get(npc_address)
    if data:
        last_x = data.get('last_x')
        last_y = data.get('last_y')
        if last_x is not None and last_y is not None:
            screen_x, screen_y = convert_to_screen_coordinates(last_x, last_y)
            pyautogui.click(x=screen_x, y=screen_y)
            print(f"Clicked at {screen_x}, {screen_y} to loot drop.")

# =========================
# AUT0-LOOT PATCH ENDS HERE
# =========================

def check_values():
    global pm, combat_baseline_exp, current_target_npc, pickup_points
    initialize_pymem()

    if combat_baseline_exp is None:
        try:
            combat_baseline_exp = pm.read_int(totalExp)
            print(f"Combat baseline EXP initialized: {combat_baseline_exp}")
        except Exception as e:
            print(f"Error initializing baseline EXP: {e}")

    while True:
        try:
            current_exp = pm.read_int(totalExp)
            if current_exp > combat_baseline_exp:
                print(f"EXP increased from {combat_baseline_exp} to {current_exp}.")
                # NPC just died:
                if current_target_npc is not None:
                    print(f"Removing and looting NPC: {current_target_npc}")
                    loot_npc(current_target_npc) # <------ Call our loot function!
                    manager.remove_address(current_target_npc)
                combat_baseline_exp = current_exp

            addresses_to_remove = []
            current_time = time.time()
            player_x = player_data_manager.data["x"]
            player_y = player_data_manager.data["y"]

            # Check all NPC addresses for stale or invalid data.
            for x in list(manager.addresses.keys()):
                data = manager.addresses[x]
                address_x = int(x, 16)
                address_y = int(data["paired_address"], 16)
                try:
                    value_x = pm.read_short(address_x)
                    value_y = pm.read_short(address_y)

                    # Update last known position if the NPC has moved.
                    last_x = data.get("last_x")
                    last_y = data.get("last_y")
                    last_moved = data.get("last_moved")
                    if value_x != last_x or value_y != last_y:
                        manager.addresses[x]["last_x"] = value_x
                        manager.addresses[x]["last_y"] = value_y
                        manager.addresses[x]["last_moved"] = current_time
                    else:
                        if current_time - last_moved > 25:
                            addresses_to_remove.append(x)
                    # Remove NPC if values are out of expected bounds.
                    if value_x == 0 or value_x > 100 or value_y == 0 or value_y > 100:
                        addresses_to_remove.append(x)
                except Exception as e:
                    addresses_to_remove.append(x)

            for address in addresses_to_remove:
                manager.remove_address(address)
        except Exception as e:
            print(f"Error in check_values: {e}")
        time.sleep(0.05)

def main():

    global totalExp, combat_baseline_exp
    attacknumber = 8

    # Hardcoded memory addresses
    walk_address = walkAddress
    npc_address = npcAddress
    directional_offset = directionalAddress

    print("Using hardcoded offsets:")
    print(f"Walk Address: {walk_address}")
    print(f"NPC Address: {npc_address}")
    print(f"Directional Address: {directional_offset}")

    patch_adds_with_nops()
   
    initialize_pymem()  # sets pm = Pymem("Endless.exe")

    search_value = int(input("Enter your current TOTAL EXP: "))
    totalExp = scan_for_exp_address(pm, search_value)
    combat_baseline_exp = pm.read_int(totalExp)
    print(f"[+] Using discovered totalExp pointer: {hex(totalExp)}")

    # 3) Start Frida hooks
    threading.Thread(target=start_frida, args=(npcAddress,), daemon=True).start()
    start_frida_session_xy(walkAddress)
    start_frida_session_directional(directionalAddress)

    # 4) Spawn background threads
    threading.Thread(target=check_player_data,
                     args=(x_address, y_address, directional_address),
                     daemon=True).start()
    threading.Thread(target=check_values, daemon=True).start()
    threading.Thread(target=combat_thread, daemon=True).start()
    threading.Thread(target=key_listener, daemon=True).start()

    # 5) Launch your GUI (blocks until closed)
    PlayerDataPopup(player_data_manager).run()


if __name__ == "__main__":
    main()
