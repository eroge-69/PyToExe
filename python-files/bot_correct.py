import win32gui
import win32con
import pyautogui
import time
import pydirectinput
from PIL import ImageGrab, Image
import numpy as np
import json
from collections import deque
import keyboard
import re

import cv2
import os
import sys
import uuid

from doctr.io import DocumentFile
from doctr.models import ocr_predictor


if getattr(sys, 'frozen', False):
    os.environ["PDFIUM_PATH"] = os.path.join(sys._MEIPASS, "pdfium.dll")


ocr_model = ocr_predictor(pretrained=True)
health_map_mask = Image.open("healh_map.jpg").convert("RGB")
moving_map_mask = Image.open("moving_cash_map.png").convert("RGB")


config = {}


def import_config():
    global config
    config = {"time_macros":[]}
    with open("config.txt","r") as file:
        macros = False
        for item in file:
            item = item.strip()
            data = item.split(":")
            if data[0] == "autoregeneration":
                config["autoregeneration"] = data[1]
            elif data[0] == "click_method":
                config["click_method"] = data[1]
            elif data[0] == "time_macros[":
                macros = True
            elif data[0] == "]time_macros":
                macros = False
            elif macros and (data[0] != "]time_macros"):
                time_sec = 0
                if data[1][-1] == "ms":
                    time_sec = int(data[1][:-2])/1000
                elif data[1][-1] == "s":
                    time_sec = int(data[1][:-1])
                elif data[1][-1] == "m":
                    time_sec = int(data[1][:-1])*60
                elif data[1][-1] == "h":
                    time_sec = int(data[1][:-1])*3600
                elif data[1][-1] == "d":
                    time_sec = int(data[1][:-1])*3600*24
                config["time_macros"].append([data[0],0,time_sec])


def get_neighbors(x, y):
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            neighbors.append((x + dx, y + dy))
    return neighbors

def find_path_bfs_optimized(start_coords, target_coords, current_map_cache):
    from collections import deque

    max_iterations = 800 * 800
    start = tuple(map(int, start_coords))
    goal = tuple(map(int, target_coords))

    queue = deque([goal])
    came_from = {goal: None}
    visited = set([goal])

    iterations = 0

    while queue and iterations < max_iterations:
        current = queue.popleft()
        iterations += 1

        if current == start:
            break

        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            neighbor = (current[0] + dx, current[1] + dy)

            if neighbor in visited:
                continue
            if current_map_cache.get(neighbor, True) is False:
                continue

            queue.append(neighbor)
            came_from[neighbor] = current
            visited.add(neighbor)

    if start not in came_from:
        print(f"[BFS] Start point {start} NOT found in came_from.")
        fallback = min(came_from, key=lambda p: (p[0]-start[0])**2 + (p[1]-start[1])**2)
        print(f"[BFS] Restore path to nearest {fallback} point instead of {start}.")
        current = fallback
    else:
        current = start

    path = []
    path_iter = 0
    while current is not None and path_iter < 1000:
        path.append(current)
        current = came_from.get(current)
        path_iter += 1

    path.reverse()
    return path


def save_zone_cache(zone_name, cache_data):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    cache_file_path = os.path.join(CACHE_DIR, f"{zone_name}.json")
    
    serializable_cache = {"name": cache_data.get("name", zone_name)}
    for key, value in cache_data.items():
        if isinstance(key, tuple):
            serializable_cache[str(key)] = value
        else:
            serializable_cache[key] = value

    try:
        with open(cache_file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_cache, f, indent=4, ensure_ascii=False)
        print(f"The cache for zone '{zone_name}' is saved to file '{cache_file_path}'.")
    except Exception as e:
        print(f"ERROR: Failed to save cache for zone '{zone_name}' to file '{cache_file_path}': {e}")


def load_zone_cache(zone_name):
    global current_map_cache
    
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        print(f"DEBUG: Created directory for caches: {CACHE_DIR}")

    cache_file_path = os.path.join(CACHE_DIR, f"{zone_name}.json")

    if os.path.exists(cache_file_path):
        try:
            with open(cache_file_path, 'r', encoding='utf-8') as f:
                loaded_cache_data = json.load(f)
                
                processed_cache = {"name": loaded_cache_data.get("name", zone_name)}
                for key, value in loaded_cache_data.items():
                    if key != "name":
                        try:
                            coords = tuple(map(int, key.strip('()').split(',')))
                            processed_cache[coords] = value
                        except ValueError:
                            print(f"WARNING: Invalid key in cache file: {key}. Skipping.")
                            continue
                current_map_cache = processed_cache
                print(f"Loaded cache for zone '{zone_name}' from file '{cache_file_path}'.")
        except json.JSONDecodeError as e:
            print(f"ERROR: Error decoding JSON for file '{cache_file_path}': {e}. Creating new cache.")
            current_map_cache = {"name": zone_name}
            save_zone_cache(zone_name, current_map_cache)
        except Exception as e:
            print(f"ERROR: Unknown error loading cache '{cache_file_path}': {e}. Creating new cache.")
            current_map_cache = {"name": zone_name}
            save_zone_cache(zone_name, current_map_cache)
    else:
        current_map_cache = {"name": zone_name}
        print(f"Cache file for zone '{zone_name}' not found. Creating a new empty cache with the zone name.")
        save_zone_cache(zone_name, current_map_cache)

def save_current_zone_cache():
    global current_map_cache, current_zone_name

    if current_zone_name is None:
        print("There is no active area to save the cache.")
        return False

    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    filename = os.path.join(CACHE_DIR, f"{current_zone_name}.json")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(current_map_cache, f, indent=4, ensure_ascii=False)
        print(f"Cache for zone '{current_zone_name}' successfully saved to {filename}")
        return True
    except IOError as e:
        print(f"Error saving cache for zone '{current_zone_name}': {e}")
        return False

def extract_coords_with_subtraction(rect):
    left, top, right, bottom = rect
    region = (left + 2, top + 26, left + 160, top + 80) 

    img_with_coords_pil = ImageGrab.grab(bbox=region).convert("RGB")
    np_img_with_coords_original = np.array(img_with_coords_pil)
    
    pydirectinput.press('m')
    time.sleep(0.1) 

    img_background_pil = ImageGrab.grab(bbox=region).convert("RGB")

    pydirectinput.press('m')
    time.sleep(0.1) 

    np_img_with_coords_int16 = np.array(img_with_coords_pil, dtype=np.int16)
    np_img_background_int16 = np.array(img_background_pil, dtype=np.int16)

    np_diff_rgb = cv2.absdiff(np_img_with_coords_int16, np_img_background_int16).astype(np.uint8)
    
    full_pixel_mask = np.any(np_diff_rgb > 0, axis=-1)
    
    height, width, _ = np_img_with_coords_original.shape
    zone_height_px_original = 16
    
    zone_image_processed = np.full(
        (zone_height_px_original, width, 3),
        255, dtype=np.uint8
    )
    zone_mask = full_pixel_mask[0:zone_height_px_original, 0:width]
    zone_image_processed[zone_mask] = np_img_with_coords_original[0:zone_height_px_original, 0:width][zone_mask]

    coords_image_processed = np.full(
        (height - zone_height_px_original, width, 3),
        0, dtype=np.uint8
    )
    coords_mask = full_pixel_mask[zone_height_px_original:height, 0:width]
    coords_image_processed[coords_mask] = np_img_with_coords_original[zone_height_px_original:height, 0:width][coords_mask]

    scale_factor = 4
    upscaled_zone_image = cv2.resize(zone_image_processed, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    enhanced_zone_image = cv2.convertScaleAbs(upscaled_zone_image, alpha=2.0, beta=0)
    enhanced_zone_image = cv2.cvtColor(enhanced_zone_image, cv2.COLOR_BGR2GRAY)

    coords_image_processed_inverted = cv2.bitwise_not(coords_image_processed)
    upscaled_coords_image = cv2.resize(coords_image_processed_inverted, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    upscaled_coords_image = cv2.cvtColor(upscaled_coords_image, cv2.COLOR_BGR2GRAY)

    zone_temp_file_path = "doctr_zone_input.png"
    coords_temp_file_path = "doctr_coords_input.png"

    try:
        Image.fromarray(enhanced_zone_image).save(zone_temp_file_path)
        Image.fromarray(upscaled_coords_image).save(coords_temp_file_path)
        print("DEBUG: Split area images and coordinates saved.")
    except Exception as e:
        print(f"DEBUG: DEBUG: ERROR saving split images: {e}")
        return "ERROR_SAVING_IMAGES"

    combined_ocr_image = np.vstack((enhanced_zone_image, upscaled_coords_image))
    
    combined_temp_file_path = "doctr_combined_input.png"
    try:
        Image.fromarray(combined_ocr_image).save(combined_temp_file_path)
        print(f"DEBUG: The combined image is saved as '{combined_temp_file_path}'.")
    except Exception as e:
        print(f"DEBUG: ERROR saving merged image: {e}")
        return "ERROR_SAVING_COMBINED_IMAGE"

    recognized_text = ""
    try:
        doc_combined = DocumentFile.from_images([combined_temp_file_path])
        result_combined = ocr_model(doc_combined)
        
        lines = []
        for page in result_combined.pages:
            for block in page.blocks:
                for line in block.lines:
                    text = " ".join([word.value for word in line.words]).strip()
                    if text:
                        lines.append(text)
        
        recognized_text = " ".join(lines) 
        print(f"Final recognized text (Doctr - merged): '{recognized_text}'")
        return recognized_text

    except Exception as e:
        print(f"OCR ERROR merged image: {e}")



def get_game_window(title="MixMaster Online"):
    hwnd = win32gui.FindWindow(None, title)
    if not hwnd:
        raise Exception(f"Window with title '{title}' not found")

    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    win32gui.BringWindowToTop(hwnd)
    win32gui.SetActiveWindow(hwnd)

    rect = win32gui.GetWindowRect(hwnd)
    x, y, right, bottom = rect
    width = right - x
    height = bottom - y

    data = {
        "hwnd": hwnd,
        "x": x,
        "y": y,
        "width": width,
        "height": height
    }

    return {0:data,
            1:rect}


ORIGIN_TILE_CENTER_X_OFFSET = 515 
ORIGIN_TILE_CENTER_Y_OFFSET = 383.5 

DELTA_X_FOR_LX = 32
DELTA_Y_FOR_LX = -16

DELTA_X_FOR_LY = 32
DELTA_Y_FOR_LY = 16

def logical_to_screen_corrected(lx, ly, info):
    print(info)
    base_pixel_x = info['x'] + ORIGIN_TILE_CENTER_X_OFFSET
    base_pixel_y = info['y'] + ORIGIN_TILE_CENTER_Y_OFFSET

    target_pixel_x = base_pixel_x + (lx * DELTA_X_FOR_LX) + (ly * DELTA_X_FOR_LY)
    target_pixel_y = base_pixel_y + (lx * DELTA_Y_FOR_LX) + (ly * DELTA_Y_FOR_LY)

    return int(target_pixel_x), int(target_pixel_y)

def screen_to_logical(target_x, target_y, info):
    # Базовые смещения
    base_pixel_x = info['x'] + ORIGIN_TILE_CENTER_X_OFFSET
    base_pixel_y = info['y'] + ORIGIN_TILE_CENTER_Y_OFFSET

    X = target_x - base_pixel_x
    Y = target_y - base_pixel_y


    det = DELTA_X_FOR_LX * DELTA_Y_FOR_LY - DELTA_X_FOR_LY * DELTA_Y_FOR_LX

    if det == 0:
        raise ValueError("Матрица не обратима, проверьте коэффициенты.")

    inv_A = [
        [ DELTA_Y_FOR_LY / det, -DELTA_X_FOR_LY / det],
        [-DELTA_Y_FOR_LX / det,  DELTA_X_FOR_LX / det]
    ]

    lx = inv_A[0][0] * X + inv_A[0][1] * Y
    ly = inv_A[1][0] * X + inv_A[1][1] * Y

    return lx, ly

bot_speed = 0.5
def char_move(lx, ly, info):
    pixel_x, pixel_y = logical_to_screen_corrected(lx, ly, info)

    pyautogui.moveTo(pixel_x, pixel_y, duration=0.1)
    mouseDown()
    mouseUp()

    time.sleep(0.4 / bot_speed - 0.2)

def cusor_like_move(lx, ly, info):
    pixel_x, pixel_y = logical_to_screen_corrected(lx, ly, info)

    pyautogui.moveTo(pixel_x, pixel_y, duration=0.001)

def skan_land(lx, ly, accuracy, info):
    global current_map_cache

    if [lx,ly] == [0,0]:
        print("[0,0] is always passable, since there is a character on it, there is no need for analysis")
        current_map_cache[current_cords[0]+lx,current_cords[1]+ly] = True
        return True


    target_x = lx 
    target_y = ly 

    screen_x, screen_y = logical_to_screen_corrected(target_x, target_y, info)

    region = (screen_x - 31, screen_y - 20, screen_x + 31, screen_y)

    cusor_like_move(lx+2, ly+2, info)
    time.sleep(0.001)
    
    img1 = ImageGrab.grab(bbox=region).convert("RGB")

    cusor_like_move(lx, ly, info)
    time.sleep(0.001)

    img2 = ImageGrab.grab(bbox=region).convert("RGB")

    np_img1_int16 = np.array(img1, dtype=np.int16)
    np_img2_int16 = np.array(img2, dtype=np.int16)

    np_diff_rgb = cv2.absdiff(np_img1_int16, np_img2_int16).astype(np.uint8)
    img = Image.fromarray(np_diff_rgb)
    try:
        img.save("cash.jpg")
    except Exception as err:
        pass

    special_pixels = [
        [128, 128, 128],
        [59, 36, 44],
        [6, 6, 6]
    ]

    width, height = img.size
    pixel_count = 0

    for x_img in range(width):
        for y_img in range(height):
            r, g, b = img.getpixel((x_img, y_img))
            if [r,g,b] != [0,0,0]:
                pixel_count += 1

    if pixel_count < accuracy:
        print(f"DEBUG: Obstacle detected at ({target_x}, {target_y}). Count: {pixel_count} < Accuracy: {accuracy}")
        current_map_cache[current_cords[0]+lx,current_cords[1]+ly] = False
        return False
    else:
        print(f"DEBUG: Point ({target_x}, {target_y}) is passable. Count: {pixel_count} >= Accuracy: {accuracy}")
        current_map_cache[current_cords[0]+lx,current_cords[1]+ly] = True
        return True





def is_mob(rect):
    left, top, right, bottom = rect
    region = (left + 489, top + 90, left + 543, top + 93)
    img = ImageGrab.grab(bbox=region).convert("RGB")
    red_pixel_count = 0
    width, height = img.size
    for x in range(width):
        for y in range(height):
            r, g, b = img.getpixel((x, y))
            if r >= 136 and g <= 24 and b <= 24:
                red_pixel_count += 1
                
    return red_pixel_count

def char_healh(rect):
    left, top, right, bottom = rect
    region = (left + 746, top + 43, left + 771, top + 101)
    img = ImageGrab.grab(bbox=region).convert("RGB")
    red_pixel_count = 0
    width, height = img.size
    for x in range(width):
        for y in range(height):
            mask_r, mask_g, mask_b = health_map_mask.getpixel((x, y))
            if mask_r == 255 and mask_g == 255 and mask_b == 255:
                r, g, b = img.getpixel((x, y))
                if r >= 100 and g <= 24 and b <= 24:
                    red_pixel_count += 1
    return red_pixel_count

def calculate_distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def cursor_destroer(rect,rad=3):
    break2 = False
    for i in range(-rad,rad+1):
        if break2:
            break
        for j in range(-rad,rad+2):
            cusor_like_move(i,j,rect)
            if is_mob(rect) > 100:
                mouseDown()
                mouseUp()
                break
                break2 = True

x_except, y_except = [0,0]
def find_moving_pixels(rect, detection_region=None, pixel_diff_threshold=30, min_distance_between_mobs=30):
    global x_except, y_except
    left, top, right, bottom = rect
    
    game_window_width = right - left
    game_window_height = bottom - top
    print(f"{game_window_width}X{game_window_height}")

    if detection_region is None:
        print("Scans the entire game window for moving pixels.")
        region_abs_x = left
        region_abs_y = top
        region_abs_width = game_window_width
        region_abs_height = game_window_height
    else:
        region_abs_x = detection_region[0]
        region_abs_y = detection_region[1]
        region_abs_width = detection_region[2]
        region_abs_height = detection_region[3]
    
    screenshot_bbox = (region_abs_x, region_abs_y, 
                       region_abs_x + region_abs_width, region_abs_y + region_abs_height)

    x_except = region_abs_x + region_abs_width/2
    y_except = region_abs_y + region_abs_height/2
    pyautogui.moveTo(x_except,y_except,duration=0.01)

    img1 = ImageGrab.grab(bbox=screenshot_bbox).convert("RGB")
    time.sleep(0.01)
    img2 = ImageGrab.grab(bbox=screenshot_bbox).convert("RGB")
    #img1.save("moving_cash2.png")
    

    np_img1 = np.array(img1, dtype=np.int16)
    np_img2 = np.array(img2, dtype=np.int16)

    if np_img1.ndim == 2:
        np_img1 = np.stack((np_img1, np_img1, np_img1), axis=-1)
    if np_img2.ndim == 2:
        np_img2 = np.stack((np_img2, np_img2, np_img2), axis=-1)

    potential_mob_movement_centers = []

    

    for y_offset in range(region_abs_height):
        for x_offset in range(region_abs_width):
##            mask_r, mask_g, mask_b = moving_map_mask.getpixel((x_offset, y_offset))
##            if [mask_r, mask_g, mask_b] != [255,255,255]:
##                continue
##            if x_except - 128 <= x_offset <= x_except + 128 and y_except - 128 <= y_offset <= y_except + 128:
##                continue
            
            r1, g1, b1 = np_img1[y_offset, x_offset]
            r2, g2, b2 = np_img2[y_offset, x_offset]

            if (abs(r1 - r2) > pixel_diff_threshold or
                abs(g1 - g2) > pixel_diff_threshold or
                abs(b1 - b2) > pixel_diff_threshold):
                    
                current_pixel_global_coords = (region_abs_x + x_offset, region_abs_y + y_offset)
                    
                is_too_close_to_existing_center = False
                for existing_center in potential_mob_movement_centers:
                    if calculate_distance(current_pixel_global_coords, existing_center) < min_distance_between_mobs:
                        is_too_close_to_existing_center = True
                        break
                    
                if not is_too_close_to_existing_center:
                    if (x_except - 64 <= x_offset <= x_except + 64) and (y_except - 64 <= y_offset <= y_except + 64):
                        continue
                    else:
                        potential_mob_movement_centers.append(current_pixel_global_coords)

    return potential_mob_movement_centers

def extract_data(ocr_raw_data):
    zone_name = ""
    x_coord = None
    y_coord = None

    words = ocr_raw_data.strip().split()

    for i, word in enumerate(words):
        if re.search(r'\d|[XYxy,:]', word): 
            break
        zone_name += word + " "
    zone_name = zone_name.strip()

    numbers_only_str = re.sub(r'\D', ' ', ocr_raw_data)
    numbers_list_str = [num for num in numbers_only_str.split(' ') if num.isdigit()]

    print(f"DEBUG_EXTRACT_DATA: Extracted string numbers: {numbers_list_str}")

    if len(numbers_list_str) >= 2:
        try:
            x_coord = int(numbers_list_str[0])
            print(f"DEBUG_EXTRACT_DATA: X-coordinate successfully converted: {x_coord}")
        except ValueError:
            print(f"DEBUG_EXTRACT_DATA: ERROR: Could not convert X '{numbers_list_str[0]}' to number.")

        try:
            y_coord = int(numbers_list_str[1])
            print(f"DEBUG_EXTRACT_DATA: Y-coordinate successfully converted: {y_coord}")
        except ValueError:
            print(f"DEBUG_EXTRACT_DATA: ERROR: Could not convert Y '{numbers_list_str[1]}' to number.")
    else:
        print(f"Not enough numbers for X and Y.")

    zone_correct_name = ""
    for frame in zone_name.split():
        if len(frame) < 3:
            continue
        else:
            zone_correct_name += frame + " "
        

    data = {
        "name": zone_correct_name,
        "x": x_coord,
        "y": y_coord
    }
    print(f"[data]: {data}")
    return data

def select_item_in_inventory(slotx, sloty, info):
    pyautogui.moveTo(int(slotx) * 42 + info['x'] + 740, int(sloty) * 36 + info['y'] + 380, duration=0.01)

def select_item_in_slot(slot, info):
    pyautogui.moveTo(info['x'] + 1005, int(slot) * 33 + info['y'] + 176, duration=0.01)

import_config()
##struct_config = {"autoregeneration":"f1",
##                 "click_method":"0",
##          "time_macros":[
##              ["i01",0,0],
##              ["i02",0,0]]}
print(config)

def mouseDown():
    if config["click_method"] == "0":
        pyautogui.mouseDown()#
    elif config["click_method"] == "1":
        pydirectinput.mouseDown()
    elif config["click_method"] == "2":
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)

def mouseUp():
    if config["click_method"] == "0":
        pyautogui.mouseUp()#
    elif config["click_method"] == "1":
        pydirectinput.mouseUp()
    elif config["click_method"] == "2":
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    

current_map_cache = {"name":None, 
                     (0,0): None} 
path_cache = {}
current_zone_name = None
current_cords = [0,0]
names = ["Rudis","Southern Rudis","Valcan Access Road","White Prairie",
          "Twin Valley","Fork Road","VeHerseba","Southern VeHerseba",
          "Rollingcores Field","Cheseva Ruins","Herseba","Herseba Entrance",
          "Magirita West Sea","Northern Magirita","Magirita","Eastern Magirita",
          "Mekrita Central Prairie","Mekrita East Sea","Mekrita","Mekrita South Prairie",
          "Islaba Damp Area","Fishcroll","Owalljae Prairie","Tamer's Field",
          "Valcan Valley","White Seashore","Purmai","Iskai Forest","Ruins of Silence",
          "Summer Snow Field"]

CACHE_DIR = "map_caches"

stop_bot_flag = False
bot_stuck_or_off_path = False 

task = {
    "type":"<None>",
    "stage":"<None>",
    "target":[0,0],
    "full_path": None,
    "path_segment_index": 0,
    "expected_lx": None,
    "expected_ly": None,
    "last_char_move_time": 0,
    "recalculate_path": False,
    "status": "<None>",
    "tasks":[]
}
task_standard = {
    "type":"<None>",
    "stage":"<None>",
    "target":[0,0],
    "full_path": None,
    "path_segment_index": 0,
    "expected_lx": None,
    "expected_ly": None,
    "last_char_move_time": 0,
    "recalculate_path": False,
    "status": "<None>",
    "tasks":[]
}


PATH_SEGMENT_LENGTH = 10 
OCR_REQUEST_INTERVAL = 1.0 
MAP_SCAN_INTERVAL = 2.0 
MIN_TIME_BEFORE_PATH_CHECK = 1.0 

last_ocr_request_time = time.time()
last_map_scan_time = time.time()
last_use_slot1_time = time.time()
last_use_slot2_time = time.time()


keyboard.add_hotkey('q', lambda: setattr(__import__('__main__'), 'stop_bot_flag', True))
print("Bot started. Press 'Q' to stop.")

task = {"type":"<None>",
        "stage":"<None>"}

task_critical = {"type":"<Critical>"}

task_standard = {"type":"<None>",
                "stage":"<None>"}


struct_time = {"type":"<wait>",
               "time":0}

struct_move = {"type":"<moving>",
                "stage":"<None>",
                "target":[0,0],
                "range": 3,
                "tasks":[],
                "crash":False,
                "skan_range":[[-6,6],[-6,6]],
                "jump":{}}

struct_farm = {"type":"<farm>",
               "stage":"<None>",
               "time":2*60}

task = struct_farm


char_avatar = [770,68]
Attack_Mob = True
Attack_Mob_time = 60 + time.time()

if __name__ == "__main__":
    try:
        while not stop_bot_flag:
            try:
                print(task)
                data_ = get_game_window()
                info = data_[1]
                info2 = data_[0]

                if char_healh(info) < 100:
                    task = task_standard
                    Attack_Mob = True
                    Attack_Mob_time += 2*60
                    if config["autoregeneration"][0] == "f":
                        pydirectinput.press(config["autoregeneration"])
                    elif config["autoregeneration"][0] == "s":
                        select_item_in_slot(int(config["autoregeneration"][1:]),info2)
                        mouseDown()
                        mouseUp()
                        sl_x = char_avatar[0] + info[0]
                        sl_y = char_avatar[1] + info[1]
                        pyautogui.moveTo(sl_x, sl_y, duration=0.01)
                        mouseDown()
                        mouseUp()
                    elif config["autoregeneration"][0] == "i":
                        pydirectinput.press("u")
                        select_item_in_inventory(int(config["autoregeneration"][1]),int(config["autoregeneration"][2]),info2)
                        mouseDown()
                        mouseUp()
                        sl_x = char_avatar[0] + info[0]
                        sl_y = char_avatar[1] + info[1]
                        pyautogui.moveTo(sl_x, sl_y, duration=0.01)
                        mouseDown()
                        mouseUp()
                        pydirectinput.press("u")
                    if char_healh(info) < 50:
                        continue

                if True: #just so it would be in a separate block
                    for time_event in config["time_macros"]:
                        if time_event[1] < time.time():
                            time_event[1] = time_event[2] + time.time()
                            print("detected")
                            print(time_event[0], time_event)
                            
                            if time_event[0][0] == "f":
                                pydirectinput.press(config["autoregeneration"])
                                print("f")
                            elif time_event[0][0] == "s":
                                select_item_in_slot(int(time_event[1:],info))
                                mouseDown()
                                x, y = char_avatar
                                pyautogui.moveTo(x, y, duration=0.01)
                                mouseUp()
                                print("s")
                            elif time_event[0][0] == "i":
                                pydirectinput.press("u")
                                select_item_in_inventory(int(time_event[0][1]),int(time_event[0][2]),info2)
                                mouseDown()
                                x, y = char_avatar
                                pyautogui.moveTo(x+info2["x"], y+info2["y"], duration=0.01)
                                mouseUp()
                                pydirectinput.press("u")
                                print("i")
                        
                if current_map_cache["name"] == None:
                    date = extract_coords_with_subtraction(info)
                    date = extract_data(date)
                    current_zone_name = date["name"]
                    current_cords = [date["x"],date["y"]]
                if current_map_cache["name"] != current_zone_name:
                    load_zone_cache(current_zone_name)
                if task["type"] == "<None>":
                    task = struct_farm
                elif task["type"] == "<wait>":
                    if task["time"] < time.time:
                        task["type"] = task_standard
                elif task["type"] == "<moving>":
                    if task["stage"] == "<None>":
                        if (task["target"][0]-task["range"] <= current_cords[0] <= task["target"][0]+task["range"]) and (task["target"][1]-task["range"] <= current_cords[1] <= task["target"][1]+task["range"]):
                            task["stage"] = "<completed>"
                            continue
                        path_cache = {}
                        date = extract_coords_with_subtraction(info)
                        date = extract_data(date)
                        current_zone_name = date["name"]
                        current_cords = [date["x"],date["y"]]
                        task["stage"] = "<search>"
                    elif task["stage"] == "<search>":
                        path = find_path_bfs_optimized(current_cords,task["target"],current_map_cache)
                        task["stage"] = "<build>"
                        print(f"[PATH SEARCHED] Path found: {path}")
                    elif task["stage"] == "<build>":
                        task["tasks"] = []
                        path = path[::-1]
                        new = True
                        for vec in path:
                            if new:
                                start = vec
                                new = False
                                task["tasks"].append([start])
                                continue
                            if isinstance(vec[0], str):
                                vec = (int(vec[0]), int(vec[1]))
                            if isinstance(start[0], str):
                                start = (int(start[0]), int(start[1]))
                            if vec == start:
                                continue
                            if ((vec[0]-start[0])**2+(vec[1]-start[1])**2)**0.5 < 5:
                                if vec in current_map_cache:
                                    if current_map_cache[vec]:
                                        task["tasks"][-1].append(vec)
                                    else:
                                        new = True
                                else:
                                    task["tasks"][-1].append(vec)
                            else:
                                new = True
                        task["stage"] = "<process>"
                    elif task["stage"] == "<process>":
                        if len(task["tasks"]) != 0:
                            skan = False
                            for item in task["tasks"][0][-1]:
                                if item != current_zone_name:
                                    skan = True
                                    break
                            if not skan:
                                lx = task["tasks"][0][-1][0] - current_cords[0]
                                ly = task["tasks"][0][-1][1] - current_cords[1]
                                print(lx,ly)
                                char_move(lx, ly, info2)
                                current_cords = task["tasks"][0][0]
                                del task["tasks"][0]
                            else:
                                is_there_an_obstacle = False
                                for item in task["tasks"][0]:
                                    sx = item[0] - current_cords[0]
                                    sy = item[1] - current_cords[1]
                                    print(item[0], current_cords[0])
                                    print(item[1], current_cords[1])
                                    if not skan_land(sx, sy, 200, info2):
                                        is_there_an_obstacle = True
                                        task["stage"] = "<fail>"
                                        break
                                    time.sleep(0.01)
                                if not is_there_an_obstacle:
                                    lx = task["tasks"][0][-1][0] - current_cords[0]
                                    ly = task["tasks"][0][-1][1] - current_cords[1]
                                    print(lx,ly)
                                    char_move(lx, ly, info2)
                                    current_cords = task["tasks"][0][0]
                                    del task["tasks"][0][-1]
                                    if len(task["tasks"][0]) == 0:
                                        del task["tasks"][0]
                        elif (task["target"][0]-task["range"] <= current_cords[0] <= task["target"][0]+task["range"]) and (task["target"][1]-task["range"] <= current_cords[1] <= task["target"][1]+task["range"]):
                            if task["jump"] != {}:
                                task = task["jump"]
                            else:
                                task["stage"] = "<completed>"
                        else:
                            if task["jump"] != {}:
                                task = task["jump"]
                            else:
                                task["stage"] = "<completed>"

                    elif task["stage"] == "<fail>":
##                        if task["crash"] "crash":
##                            task = task_standard
                        Attack_Mob = True
##                            continue
                        i, j = task["skan_range"][0][0], task["skan_range"][1][0]

                        if i > task["skan_range"][0][1]:  # закончили строку — переход на следующую строку
                            task["skan_range"][0][0] = -6
                            task["skan_range"][1][0] += 1
                            i = -6
                            j = task["skan_range"][1][0]

                        if j > task["skan_range"][1][1]:  # закончили весь диапазон
                            task["stage"] = "<None>"
                        else:
                            if [i, j] != [0, 0]:
                                skan_land(i, j, 200, info2)

                            task["skan_range"][0][0] += 1  # инкремент X
                            
                    elif task["stage"] == "<completed>":
                        print("[moving] process completed!")
                        task = task_standard
                        Attack_Mob = True

                if Attack_Mob:
                    print("Search for target by proximity")
                    if Attack_Mob_time  < time.time():
                        task = struct_farm
                        Attack_Mob = False
                    pixels = find_moving_pixels(info,detection_region=[info[2]/2-90,info[3]/2-240,480,480])
                    if len(pixels) > 200:
                        continue
                    for entity in pixels:
                        if (x_except - 64 <= entity[0] <= x_except + 64) and (y_except - 64 <= entity[1] <= y_except + 64):
                            continue
                        pyautogui.moveTo(entity[0],entity[1],duration=0.01)
                        if is_mob(info) > 100:
                            if "mob" not in current_map_cache:
                                current_map_cache["mob"] = []
                            else:
                                local_cord = screen_to_logical(entity[0], entity[1], info2)
                                current_map_cache["mob"].append([round(local_cord[0])+current_cords[0],round(local_cord[1])+current_cords[1]])
                            mouseDown()
                            mouseUp()
                            Attack_Mob_time = 60 + time.time()
                            print("Target detected and identified, destroying!")
                            break

                elif task["type"] == "<farm>":
                    if task["stage"] == "<None>":
                        pixels = find_moving_pixels(info)
                        list_range_ = []
                        range_entity_dict = {}

                        if pixels != []:
                            
                            for entity in pixels:
                                #x, y, right, bottom
                                range_entity = ((entity[0]-(info[0]+info[2]/2))**2+(entity[1]-(info[1]+info[3]/2))**2)**0.5
                                list_range_.append(range_entity)
                                range_entity_dict[range_entity] = entity
                            
                            entity = range_entity_dict[min(list_range_)]
                            local_cord = screen_to_logical(entity[0], entity[1], info2)

                            print(round(local_cord[0]),"+",current_cords[0],";",round(local_cord[1]),"+",current_cords[1])
                            print(entity)
                                        
                            task = {"type":"<moving>",
                                    "stage":"<None>",
                                    "target":[round(local_cord[0])+current_cords[0],round(local_cord[1])+current_cords[1]],
                                    "range": 3,
                                    "tasks":[],
                                    "skan_range":[[-6,6],[-6,6]],
                                    "jump":{"type":"<farm>",
                                            "stage":"<Attack>",
                                            "time":2*60+time.time()}}
                        else:
                            mob_spawn = min(current_map_cache["mob"])
                            task = {"type":"<moving>",
                                    "stage":"<None>",
                                    "target":mob_spawn,
                                    "range": 3,
                                    "tasks":[],
                                    "skan_range":[[-6,6],[-6,6]],
                                    "jump":{"type":"<farm>",
                                            "stage":"<Attack>",
                                            "time":2*60+time.time()}}


                    elif task["stage"] == "<Attack>":
                        Attack_Mob = True
                                
            except pyautogui.FailSafeException:
                break
            except Exception as e:
                print(f"[Error] {e}")

    finally:
        save_zone_cache(current_map_cache["name"],current_map_cache)

