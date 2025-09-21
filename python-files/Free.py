import tkinter
from time import sleep
from tkinter import ttk, Toplevel, Listbox, Button, SINGLE, END, filedialog
from tkinter import messagebox, simpledialog
from concurrent.futures import ThreadPoolExecutor
import uuid
import getpass
import platform
import pyautogui
import sys
from os import path
import difflib
import os
import numpy as np
from PIL import Image, ImageTk
import re
import datetime
from tkinter import messagebox
from ctypes import windll
import win32api
import win32con
import win32gui
import win32ui
import cv2
import requests
import hashlib
import easyocr
import threading
import keyboard
import time
import json
import psutil
import subprocess
import pyperclip
import base64
from typing import Dict, Optional, List
import torch
my_hwnd = win32gui.FindWindow(None,'Dota 2')
global_lock = threading.RLock()
selected_resolution = None
bot_start_key = None
bot_pause_key = None
bot_running = False
bot_paused = False
log_text_widget = None
mode = None
bad_flag = False
counter = None
s_x = None
s_y = None
difficulty = None
resolution_folder = None
talent_search = []
fate_search = []
heroes = []
Blue_search = []
Purple_search = []
item_counter = None
in_game = None
talent_flag = None
fate_flag = None
random_fate_flag = None
random_talent_flag = None
rainbow_flag = None
huscar_flag = None
arena_flag = None
heroes_flag = None
push_flag = None
gem_flag = None
blue_gem_flag = None
purple_gem_flag = None
orange_gem_flag = None
chalenge_up_flag = None
chalenge_flag = None
random_arena_flag = None
item_sel = None
item_pick = None
hero_pick = None
arena_skip = None
build_phys = None
build_eff = None
build_mag = None
green_stone = None
purple_stone = None
yellow_stone = None
totem_stone = None
authorization = False
investment_target = None
buy_itms = None
start_time = None
skills_state = None
already_start = False
thread_close = False
thread_end = False
thread_skills = False
thread_challenge = False
Moon_use = None
Grenate_use = None
investment_lvl = None
challenge_lvl = None
W_book_lvl = None
desolator = None
desolator_up = None
daedalus = None
daedalus_up = None
abyss = None
butterfly = None
link = None
aeon = None
trident = None
gleip = None
gleip_up = None
radiance = None
parasma = None
parasma_up = None
dagon = None
dagon_up = None
eul = None
eul_up = None
eul_up2 = None
blue_gem_all = {'Critical Chance':'critical chance','Critical Damage':'critical damage','Base Agility':'base agility','Base Streangth':'base strength','Base Intelligence':'base intelligence','Base Armor':'base armor','Attack Power':'attack power','Base Attack Power':'base attack power','Attack Range':'attack range','Attack Speed':'attack speed','Gold':'gold','Gold per Second':'gold per second','Health':'health','HP Regen':'hp regen'}
purple_gem_all = {'CurrentBase Attack Power':'currentbase attack power','CurrentHealth':'currenthealth','CurrentGold per Second':'currentgold per second','CurrentAttack Range':'currentattack range','Base Armor':'base armor','CurrentHP Regen':'currenthp regen'}
def clean_text(text: str,lower=True) -> str:
  text = text.lower if lower else text
  text = re.sub('[^a-zA-Z ]','',text)
  text = re.sub('\\s+',' ',text).strip()
  return text

ability_registry: Dict[(str,Dict)] = 'Stone Origin'
refresh_count = None
already_refresh = None
skills_done = False
priority_indices = [18,19,23,48]
set_attribut = [31,32,33]
set_phys = [34,35,36,37]
set_multidamage = [38,39,40]
set_onedeath = [48,28]
set_xp = [42,43]
set_spell = [23,29]
set_attribut_persentage = [50,51,52]
set_groups = [set_attribut,set_phys,set_multidamage,set_onedeath,set_xp,set_spell,set_attribut_persentage]
ability_names = [clean_text(name,False) for name in ability_registry]
original_name_map = dict(zip(ability_names,ability_registry.keys()))
skill_states = {}
active_skills = {}
slots = 0
bool_vars = []
class Logger:
  def __init__(self,filename):
    self.terminal = sys.stdout
    self.log = open(filename,'w',encoding='utf-8')
    return None

  def write(self,message):
    self.terminal.write(message)
    self.log.write(message)
    return None

  def flush(self):
    self.terminal.flush()
    self.log.flush()
    return None

os.makedirs('logs',exist_ok=True)
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_path = f'''logs/log_{timestamp}.txt'''
sys.stdout = Logger(log_path)
sys.stderr = sys.stdout
'CUDA доступна! Используем GPU.'
'CUDA не доступна. Используем CPU.'
use_gpu = True if torch.cuda.is_available() else False
reader = ea.Reader(['en'],gpu=use_gpu)
reader1 = ea.Reader(['en'],gpu=use_gpu)
reader2 = ea.Reader(['en'],gpu=use_gpu)
reader3 = ea.Reader(['en'],gpu=use_gpu)
def keyboard_f1():
  if bot_running:
    print('кликаю F1')
    pyautogui.press('f1')
    pyautogui.press('f1')
    return None
  else:
    return None

def keyboard_f1_one():
  if bot_running:
    print('кликаю F1')
    pyautogui.press('f1')
    return None
  else:
    return None

def keyboard_f2():
  if bot_running:
    print('кликаю F2')
    pyautogui.press('f2')
    return None
  else:
    return None

def move_up(times):
  if bot_running:
    with global_lock:
      original_x,original_y = pyautogui.position()
      pyautogui.moveTo(int(1280*s_x),int(735*s_y))
      pyautogui.mouseDown(button='middle')
      pyautogui.moveRel(0,times,0.1)
      pyautogui.mouseUp(button='middle')
      pyautogui.moveTo(original_x,original_y)

    return None
  else:
    return None

def move_down(times):
  if bot_running:
    with global_lock:
      original_x,original_y = pyautogui.position()
      pyautogui.moveTo(int(1280*s_x),int(735*s_y))
      pyautogui.mouseDown(button='middle')
      pyautogui.moveRel(0,-(times),0.1)
      pyautogui.mouseUp(button='middle')
      pyautogui.moveTo(original_x,original_y)

    return None
  else:
    return None

def move_right(times):
  if bot_running:
    with global_lock:
      original_x,original_y = pyautogui.position()
      pyautogui.moveTo(int(1280*s_x),int(735*s_y))
      pyautogui.mouseDown(button='middle')
      pyautogui.moveRel(-(times),0,0.1)
      pyautogui.mouseUp(button='middle')
      pyautogui.moveTo(original_x,original_y)

    return None
  else:
    return None

def move_left(times):
  if bot_running:
    with global_lock:
      original_x,original_y = pyautogui.position()
      pyautogui.moveTo(int(1280*s_x),int(735*s_y))
      pyautogui.mouseDown(button='middle')
      pyautogui.moveRel(times,0,0.1)
      pyautogui.mouseUp(button='middle')
      pyautogui.moveTo(original_x,original_y)

    return None
  else:
    return None

def mouse_and_keyboard(x,y):
  if bot_running:
    with global_lock:
      log('Жму атаку')
      original_x,original_y = pyautogui.position()
      pyautogui.moveTo(x,y)
      pyautogui.click(x,y)
      keyboard_f1_one()
      time.sleep(0.05)
      win32gui.PostMessage(my_hwnd,win32con.WM_KEYDOWN,ord('A'),0)
      win32gui.PostMessage(my_hwnd,win32con.WM_KEYUP,ord('A'),0)
      sleep(1)
      pyautogui.moveTo(original_x,original_y)

    return None
  else:
    return None

def blink(x,y):
  if bot_running:
    with global_lock:
      original_x,original_y = pyautogui.position()
      pyautogui.moveTo(x,y)
      time.sleep(0.05)
      win32gui.PostMessage(my_hwnd,win32con.WM_KEYDOWN,ord('D'),0)
      win32gui.PostMessage(my_hwnd,win32con.WM_KEYUP,ord('D'),0)
      sleep(0.3)
      pyautogui.moveTo(original_x,original_y)

    return None
  else:
    return None

def f3():
  if bot_running:
    print('[Сортировка предметов] кликаю F3')
    pyautogui.press('f3')
    return None
  else:
    return None

def l_click(x,y):
  if bot_running:
    with global_lock:
      click = win32api.MAKELONG(x,y)
      win32gui.PostMessage(my_hwnd,win32con.WM_MOUSEMOVE,win32con.MK_LBUTTON,click)
      win32gui.PostMessage(my_hwnd,win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,click)
      win32gui.PostMessage(my_hwnd,win32con.WM_LBUTTONUP,None,click)

    return None
  else:
    return None

def l_click_t(x,y,z):
  if bot_running:
    with global_lock:
      original_x,original_y = pyautogui.position()
      pyautogui.moveTo(x,y)
      time.sleep(0.1)
      pyautogui.scroll(z)
      pyautogui.moveTo(original_x,original_y)

    return None
  else:
    return None

def mouse_move(x,y):
  if bot_running:
    with global_lock:
      pyautogui.moveTo(x,y)

    return None
  else:
    return None

def mouse_safe():
  if bot_running:
    with global_lock:
      pyautogui.moveTo(int(162*s_x),int(693*s_y))
      sleep(0.3)

    return None
  else:
    return None

def l_click_py(x,y):
  if bot_running:
    with global_lock:
      original_x,original_y = pyautogui.position()
      pyautogui.moveTo(x,y)
      time.sleep(0.1)
      pyautogui.click(x,y)
      time.sleep(0.1)
      pyautogui.moveTo(original_x,original_y)

    return None
  else:
    return None

def r_click_py(x,y):
  if bot_running:
    with global_lock:
      original_x,original_y = pyautogui.position()
      pyautogui.moveTo(x,y)
      time.sleep(0.1)
      pyautogui.rightClick(x,y)
      time.sleep(0.1)
      pyautogui.moveTo(original_x,original_y)

    return None
  else:
    return None

def r_click(x,y):
  if bot_running:
    with global_lock:
      click = win32api.MAKELONG(x,y)
      win32gui.PostMessage(my_hwnd,win32con.WM_MOUSEMOVE,win32con.MK_RBUTTON,click)
      win32gui.PostMessage(my_hwnd,win32con.WM_RBUTTONDOWN,win32con.MK_RBUTTON,click)
      win32gui.PostMessage(my_hwnd,win32con.WM_RBUTTONUP,None,click)

    return None
  else:
    return None

def take_screenshot(region1=None,region2=None,region3=None,region4=None,path=None,name=None):
  with global_lock:
    hwnd = my_hwnd
    w,h = map(int,selected_resolution.get().split('x'))
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC,w,h)
    saveDC.SelectObject(saveBitMap)
    result = windll.user32.PrintWindow(hwnd,saveDC.GetSafeHdc(),2)
    im = None
    return_res = []
    if result == 1:
      bmpinfo = saveBitMap.GetInfo()
      bmpstr = saveBitMap.GetBitmapBits(True)
      im = Image.frombuffer('RGB',(bmpinfo['bmWidth'],bmpinfo['bmHeight']),bmpstr,'raw','BGRX',0,1)
      if path:
        left,top,right,bottom = region1
        im0 = im.crop((left,top,right,bottom))
        im0.save(f'''images/Item_Chosen/{path}''')

      if region1:
        left,top,right,bottom = region1
        im1 = im.crop((left,top,right,bottom))
        if name:
          im1.save(f'''images/tmp/{name}1.png''')

        return_res.append(im1)

      if region2:
        left,top,right,bottom = region2
        im2 = im.crop((left,top,right,bottom))
        if name:
          im2.save(f'''images/tmp/{name}2.png''')

        return_res.append(im2)

      if region3:
        left,top,right,bottom = region3
        im3 = im.crop((left,top,right,bottom))
        if name:
          im3.save(f'''images/tmp/{name}3.png''')

        return_res.append(im3)

      if region4:
        left,top,right,bottom = region4
        im4 = im.crop((left,top,right,bottom))
        if name:
          im4.save(f'''images/tmp/{name}4.png''')

        return_res.append(im4)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd,hwndDC)
    if region1:
      if __CHAOS_PY_NULL_PTR_VALUE_ERR__ == result:
        return im

    else:
      None(None,None)
      return (region2 or region3 or region4 or 1)

def preprocess_easyocr_image(pil_image):
  image = np.array(pil_image)
  gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
  gray = cv2.convertScaleAbs(gray,alpha=1.5,beta=0)
  scale_percent = 170
  width = int(gray.shape[1]*scale_percent/100)
  height = int(gray.shape[0]*scale_percent/100)
  gray = cv2.resize(gray,(width,height),interpolation=cv2.INTER_CUBIC)
  return gray

def find_image_on_screen(screenshot,image_to_find,color,hold,region=None,loger=True):
  try:
    screenshot_np = np.array(screenshot)
    image_to_find_np = np.array(image_to_find)
    if region:
      x1,y1,x2,y2 = region
      screenshot_np = screenshot_np[(y1:y2,x1:x2)]

    if __CHAOS_PY_NULL_PTR_VALUE_ERR__ == screenshot_np.ndim:
      pass

    if image_to_find_np.ndim == 3:
      pass

    result = cv2.matchTemplate(screenshot_np,image_to_find_np,cv2.TM_CCOEFF_NORMED)
    min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(result)
    if loger:
      print(f'''Процент совпадения: {max_val}''')

    if max_val >= hold:
      top_left = max_loc
      if region:
        top_left = (top_left[0]+x1,top_left[1]+y1)

      return top_left
    else:
      return None

  except Exception as e:
    print(f'''[Ошибка OpenCV] {e}''')
    return None

def find_images_on_screen_2(screenshot,image_to_find,color=False,hold: float = 0.9,region=None):
  try:
    screenshot_np = np.array(screenshot)
    template_np = np.array(image_to_find)
    h,w = template_np.shape[:2]
    x_offset,y_offset = (0, 0)
    if region:
      x1,y1,x2,y2 = region
      screenshot_np = screenshot_np[(y1:y2,x1:x2)]
      y_offset = y1
      x_offset = x1

    if __CHAOS_PY_NULL_PTR_VALUE_ERR__ == screenshot_np.ndim:
      pass

    if template_np.ndim == 3:
      pass

    result = cv2.matchTemplate(screenshot_np,template_np,cv2.TM_CCOEFF_NORMED)
    ys,xs = np.where(result >= hold)
    rects = []
    for x,y in zip(xs,ys):
      rects.append([x,y,w,h])
      rects.append([x,y,w,h])
      continue
      cv2.cvtColor(template_np,cv2.COLOR_BGR2GRAY)

    grouped,_ = cv2.groupRectangles(rects,groupThreshold=1,eps=0.5)
    return filtered_coords
  except Exception as e:
    print(f'''[Ошибка OpenCV] {e}''')
    return None

def log(message):
  print(message)
  if log_text_widget:
    log_text_widget.configure(state='normal')
    log_text_widget.insert(tk.END,message+'\n')
    log_text_widget.see(tk.END)
    log_text_widget.configure(state='disabled')
    return None
  else:
    return None

def log_update(message):
  print(f'''\x0d{message}''',end='',flush=True)
  if log_text_widget:
    log_text_widget.configure(state='normal')
    last_line_index = log_text_widget.index('end-1l linestart')
    log_text_widget.delete(last_line_index,tk.END)
    log_text_widget.insert(tk.END,message+'\n')
    log_text_widget.see(tk.END)
    log_text_widget.configure(state='disabled')
    return None
  else:
    return None

def read_from_screen_hero(region1,region2,region3=None):
  try:
    if int(hero_pick) == 2:
      for i in range(4):
        im1,im2 = take_screenshot(region1=region1,region2=region2,name='Hero')
        text = reader.readtext(np.array(im1))
        text2 = reader.readtext(np.array(im2))
        sorted_results = sorted(text,key=lambda r: (r[0][0][1],r[0][0][0]))
        sorted_results2 = sorted(text2,key=lambda r: (r[0][0][1],r[0][0][0]))
        text_list = ' '.join([t[1] for t in sorted_results]).lower()
        text_list2 = ' '.join([t[1] for t in sorted_results2]).lower()
        hero_idx1 = -1
        hero_idx2 = -1
        for idx,hero in enumerate(heroes):
          if hero in text_list:
            continue

          hero_idx1 = idx
          continue

        for idx,hero in enumerate(heroes):
          if hero in text_list2:
            continue

          hero_idx2 = idx
          continue

        if hero_idx1 != -1:
          l_click_py(int(1100*s_x),int(500*s_y))
          sleep(2)
          l_click_py(int(1440*s_x),int(850*s_y))
          break

        if hero_idx2 != -1:
          l_click_py(int(1600*s_x),int(500*s_y))
          sleep(2)
          l_click_py(int(1440*s_x),int(850*s_y))
          break

        if hero_idx1 == -1:
          continue

        if hero_idx2 == -1:
          continue

        l_click_py(int(1370*s_x),int(980*s_y))
        sleep(2)
        continue
      else:
        if int(hero_pick) == 3:
          for i in range(4):
            im1,im2,im3 = take_screenshot(region1=region1,region2=region2,region3=region3,name='Hero')
            text = reader.readtext(np.array(im1))
            text2 = reader.readtext(np.array(im2))
            text3 = reader.readtext(np.array(im3))
            sorted_results = sorted(text,key=lambda r: (r[0][0][1],r[0][0][0]))
            sorted_results2 = sorted(text2,key=lambda r: (r[0][0][1],r[0][0][0]))
            sorted_results3 = sorted(text3,key=lambda r: (r[0][0][1],r[0][0][0]))
            text_list = ' '.join([t[1] for t in sorted_results]).lower()
            text_list2 = ' '.join([t[1] for t in sorted_results2]).lower()
            text_list3 = ' '.join([t[1] for t in sorted_results3]).lower()
            hero_idx1 = -1
            hero_idx2 = -1
            hero_idx3 = -1
            for idx,hero in enumerate(heroes):
              if hero in text_list:
                continue

              hero_idx1 = idx
              continue

            for idx,hero in enumerate(heroes):
              if hero in text_list2:
                continue

              hero_idx2 = idx
              continue

            for idx,hero in enumerate(heroes):
              if hero in text_list3:
                continue

              hero_idx3 = idx
              continue

            if hero_idx1 != -1:
              l_click_py(int(900*s_x),int(500*s_y))
              sleep(2)
              l_click_py(int(1440*s_x),int(850*s_y))
              break

            if hero_idx2 != -1:
              l_click_py(int(1345*s_x),int(500*s_y))
              sleep(2)
              l_click_py(int(1440*s_x),int(850*s_y))
              break

            if hero_idx3 != -1:
              l_click_py(int(1840*s_x),int(500*s_y))
              sleep(2)
              l_click_py(int(1440*s_x),int(850*s_y))
              break

            if i == 3:
              l_click_py(int(1840*s_x),int(500*s_y))
              sleep(2)
              l_click_py(int(1440*s_x),int(850*s_y))
              break

            if hero_idx1 == -1:
              continue

            if hero_idx2 == -1:
              continue

            l_click_py(int(1370*s_x),int(980*s_y))
            sleep(2)
            continue
          else:
            return None
            return None

  except Exception as e:
    print(f'''Ошибка: {e}''')
    return None

def read_from_screen(region1,region2,region3=None,name=None):
  try:
    if int(item_sel) != 3:
      im1,im2 = take_screenshot(region1=region1,region2=region2,name=name)
      text = reader.readtext(np.array(im1))
      text2 = reader.readtext(np.array(im2))
      sorted_results = sorted(text,key=lambda r: (r[0][0][1],r[0][0][0]))
      sorted_results2 = sorted(text2,key=lambda r: (r[0][0][1],r[0][0][0]))
      text_list = ' '.join([t[1] for t in sorted_results]).lower()
      text_list2 = ' '.join([t[1] for t in sorted_results2]).lower()
      talent_idx1 = -1
      fate_idx1 = -1
      fate_idx2 = -1
      talent_idx2 = -1
      location_t7 = None
      location_t6 = None
      gs1 = -1
      gs2 = -1
      result = 0
      def find_best_index_from_text(text: str,search_pool: list[str],min_score: float = 0.75) -> int:
        match,score = get_best_match_from_pool(text,search_pool,min_score,ignore_order=True)
        if match:
          return search_pool.index(match)
        else:
          return -1

      fate_idx1 = find_best_index_from_text(text_list,fate_search)
      fate_idx2 = find_best_index_from_text(text_list2,fate_search)
      talent_idx1 = find_best_index_from_text(text_list,talent_search)
      talent_idx2 = find_best_index_from_text(text_list2,talent_search)
      for s in text_list:
        if re.fullmatch('\\d{5}',s):
          continue

        num = int(s)
        if num%100 != 0:
          continue

        gs1 = s
        break

      for s in text_list2:
        if re.fullmatch('\\d{5}',s):
          continue

        num = int(s)
        if num%100 != 0:
          continue

        gs2 = s
        break

      log(f'''{counter}:{item_counter}: gs1 : {gs1}, tal_idx1: {talent_search[talent_idx1] if talent_idx1 != -1 else -1}, fate_idx1: {fate_search[fate_idx1] if fate_idx1 != -1 else -1}''')
      log(f'''{counter}:{item_counter}: gs2 : {gs2}, tal_idx2: {talent_search[talent_idx1] if talent_idx2 != -1 else -1}, fate_idx2: {fate_search[fate_idx2] if fate_idx2 != -1 else -1}''')
      if random_talent_flag:
        location = wait_for_image(f'''images/{resolution_folder}/tire/t7_2.jpg''',True,1,hold=0.95)
        if location:
          x,y = location
          'Хочу взять левую потомучто рандомный талант т7'
          'Хочу взять правую потомучто рандомный талант т7'
          result = result if x < int(1318*s_x) else 1

      if log == result:
        if location:
          pass

        if location:
          'Хочу взять левую потомучто рандомный фейт т7'
          'Хочу взять правую потомучто рандомный фейт т7'

      if result if x < int(1318*s_x) else 1 != fate_idx2:
        if location_t7:
          pass

        if wait_for_image(f'''images/{resolution_folder}/tire/t7.jpg''',True,1,hold=0.95):
          pass
        else:
          if location_t6:
            pass

        f'''Хочу взять правую потомучто нашел нужный фейт: {fate_search[fate_idx2]}'''+' Т7' if location_t7 is not None else ''+' Т6' if location_t6 is not None else ''
        __CHAOS_PY_NO_FUNC_ERR__(log+' Т7' if f'''Хочу взять левую потомучто нашел нужный фейт: {fate_search[fate_idx1]}''' is not None else ''+' Т6' if location_t6 is not None else '')
        f'''Хочу взять правую потомучто нашел нужный фейт и у правой он приоритетнее: {fate_search[fate_idx2]}'''+' Т7' if location_t7 is not None else ''+' Т6' if location_t6 is not None else ''
        __CHAOS_PY_NO_FUNC_ERR__(log+' Т7' if f'''Хочу взять левую потомучто нашел нужный фейт и у левой он приоритетнее: {fate_search[fate_idx1]}''' is not None else ''+' Т6' if location_t6 is not None else '')

      f'''Хочу взять правую, потомучто нашел нужный талант: {talent_search[talent_idx2]}'''
      if log == talent_idx2:
        log(f'''Хочу взять правую, потомучто нашел нужный талант: {talent_search[talent_idx1]}''')

      f'''Хочу взять правую, потомучто нашел нужный талант и у правой он приоритетнее: {talent_search[talent_idx2]} < {talent_search[talent_idx1]}'''
      if log != talent_idx1:
        log(f'''Хочу взять левую, потомучто нашел нужный талант и у левой он приоритетнее: {talent_search[talent_idx1]} < {talent_search[talent_idx2]}''')

      if int(gs2) > 16000:
        pass

      return result
    else:
      def find_best_index_from_text(text: str,search_pool: list[str],min_score: float = 0.75) -> int:
        match,score = get_best_match_from_pool(text,search_pool,min_score,ignore_order=True)
        if match:
          return search_pool.index(match)
        else:
          return -1

      pass
      for s in talent_search:
        if s:
          continue

        if num%100 != 0:
          continue

        s
        int

      for s in __CHAOS_PY_NO_ITER_ERR__:
        if s:
          continue

        if num%100 != 0:
          continue

        s
        int

      for s in __CHAOS_PY_NO_ITER_ERR__:
        if s:
          continue

        if num%100 != 0:
          continue

        s
        int

      f'''{counter}:{item_counter}: gs1 : {gs1}, tal_idx1: {talent_search[talent_idx1] if talent_idx1 != -1 else -1}, fate_idx1: {fate_search[fate_idx1] if fate_idx1 != -1 else -1}'''
      f'''{counter}:{item_counter}: gs2 : {gs2}, tal_idx2: {talent_search[talent_idx2] if talent_idx2 != -1 else -1}, fate_idx2: {fate_search[fate_idx2] if fate_idx2 != -1 else -1}'''
      f'''{counter}:{item_counter}: gs3 : {gs2}, tal_idx3: {talent_search[talent_idx3] if talent_idx3 != -1 else -1}, fate_idx3: {fate_search[fate_idx3] if fate_idx3 != -1 else -1}'''
      if random_talent_flag:
        if location:
          if int < 990*s_x:
            'Хочу взять левую потомучто рандомный талант т7'
          else:
            'Хочу взять центральную потомучто рандомный талант т7'
            if int > 1710*s_x:
              'Хочу взять правую потомучто рандомный талант т7'

      if result if int < 1710*s_x else 2 == result:
        if location:
          pass

        if location:
          if x < int(990*s_x):
            log('Хочу взять левую потомучто рандомный талант т7')
          else:
            'Хочу взять центральную потомучто рандомный талант т7'
            if int > 1710*s_x:
              'Хочу взять правую потомучто рандомный талант т7'

      if __CHAOS_PY_NULL_PTR_VALUE_ERR__ != fate_idx3:
        if location_t7:
          pass

        if wait_for_image(f'''images/{resolution_folder}/tire/t7.jpg''',True,1,hold=0.95):
          pass
        else:
          if location_t6:
            pass

        if fate_idx1 == -1:
          if fate_idx2 != -1:
            if fate_idx3 == -1:
              if x > int(990*s_x):
                if x < int(1710*s_x):
                  log(f'''Хочу взять центральную потомучто нашел нужный фейт: {fate_search[fate_idx2]}'''+' Т7' if location_t7 is not None else ''+' Т6' if location_t6 is not None else '')
                else:
                  f'''Хочу взять левую потомучто нашел нужный фейт: {fate_search[fate_idx1]}'''+' Т7' if location_t7 is not None else ''+' Т6' if location_t6 is not None else ''
                  x(log+' Т7' if f'''Хочу взять правую потомучто нашел нужный фейт: {fate_search[fate_idx3]}''' is not None else ''+' Т6' if location_t6 is not None else '')

    if fate_idx1 != -1:
      if int < 990*s_x:
        f'''Хочу взять левую потомучто нашел нужный фейт: {fate_search[fate_idx1]}'''+' Т7' if location_t7 is not None else ''+' Т6' if location_t6 is not None else ''
      else:
        f'''Хочу взять центральную потомучто нашел нужный фейт: {fate_search[fate_idx2]}'''+' Т7' if location_t7 is not None else ''+' Т6' if location_t6 is not None else ''
        __CHAOS_PY_NO_FUNC_ERR__(log+' Т7' if f'''Хочу взять правую потомучто нашел нужный фейт: {fate_search[fate_idx3]}''' is not None else ''+' Т6' if location_t6 is not None else '')

  except Exception as e:
    f'''Ошибка: {e}'''
    return 0

  if (fate_idx3 != -1 and int(1710*s_x) and location_t7) == talent_idx1:
    if talent_idx2 != -1:
      if talent_idx3 == -1:
        log(f'''Хочу взять центральную, потомучто нашел нужный талант: {talent_search[talent_idx2]}''')
      else:
        f'''Хочу взять левую, потомучто нашел нужный талант: {talent_search[talent_idx1]}'''
        if __CHAOS_PY_NULL_PTR_VALUE_ERR__ != talent_idx3:
          log(f'''Хочу взять правую, потомучто нашел нужный талант: {talent_search[talent_idx3]}''')

  if talent_idx1 != -1:
    f'''Хочу взять левую, потомучто нашел нужный талант: {talent_search[talent_idx1]}'''
  else:
    f'''Хочу взять центральную, потомучто нашел нужный талант: {talent_search[talent_idx2]}'''
    if talent_idx3 != -1:
      f'''Хочу взять правую, потомучто нашел нужный талант: {talent_search[talent_idx3]}'''

  if int(gs2) > 16000:
    pass

  if int(gs3) > 16000:
    pass

  return result

def wait_for_image(image_path,color,tries,hold=0.9,check_interval=1,region=None,loger=True):
  if loger:
    log(f'''[Поиск изображения] Ожидаем появление изображения {image_path}...''')

  limit = 0
  location = None
  if location is None:
    if limit < tries:
      if bot_running:
        limit += 1
        if bot_running:
          pass
        else:
          screen = take_screenshot()
          image = Image.open(image_path)
          location = find_image_on_screen(screen,image,color,hold,region,loger)
          if loger:
            log(f'''[Поиск изображения] Не найдено, ждем {limit}/{tries} сек...''')

          time.sleep(check_interval)
          if location is None:
            if limit < tries:
              if bot_running:
                pass

  if location is None:
    if loger:
      bad_flag = True
      log(f'''[Поиск изображения] Изображение не найдено: {image_path}''')

    return location
  else:
    if loger:
      bad_flag = False
      log(f'''✅[Поиск изображения] Изображение найдено: {image_path}''')
      return location
    else:
      log(f'''\n✅[Поиск изображения] Изображение найдено: {image_path}\n''')
      return location

def get_scale():
  resolution = selected_resolution.get()
  if resolution == '1920x1080':
    return (0.75, 0.75)
  else:
    return (1, 1)

def Challenge():
  challenge_prices = [1500,3000,6000,9000,12000,15000,18000,21000,24000,30000]
  if thread_challenge:
    if bot_running:
      if desolator_up:
        if desolator:
          if dagon:
            if dagon_up:
              if gleip:
                if gleip_up:
                  __CHAOS_PY_IF_NO_BODY_ERR__

    return None

  return None

def try_hero_up():
  if heroes_flag:
    try_count = 0
    location = wait_for_image(f'''images/{resolution_folder}/Hero.jpg''',False,1,0.9)
    if location:
      if try_count < 5:
        try_count += 1
        x,y = location
        l_click_py(x,y)
        sleep(4)
        if int(hero_pick) == 2:
          read_from_screen_hero(region1=(int(960*s_x),int(628*s_y),int(1270*s_x),int(700*s_y)),region2=(int(1440*s_x),int(628*s_y),int(2016*s_x),int(700*s_y)))

        if int(hero_pick) == 3:
          read_from_screen_hero(region1=(int(725*s_x),int(628*s_y),int(1060*s_x),int(700*s_y)),region2=(int(1196*s_x),int(628*s_y),int(1524*s_x),int(700*s_y)),region3=(int(1673*s_x),int(628*s_y),int(1984*s_x),int(700*s_y)))

        keyboard_f1_one()
        sleep(1)
        location = wait_for_image(f'''images/{resolution_folder}/Hero.jpg''',False,1,0.9)
        if location:
          if try_count < 5:
            pass

          return None
        else:
          return None

      else:
        return None

    else:
      return None

  else:
    return None

def use_items():
  wait_if_paused()
  mouse_safe()
  location = wait_for_image(f'''images/{resolution_folder}/Chest.jpg''',True,1)
  if __CHAOS_PY_NULL_PTR_VALUE_ERR__:
    wait_if_paused()
    l_click_py(x,y)
    sleep(0.5)

  if (location and location):
    pass

  wait_if_paused()
  if Moon_use:
    location = wait_for_image(f'''images/{resolution_folder}/Moon.jpg''',True,1)
    if location:
      wait_if_paused()
      l_click_py(x,y)
      sleep(0.5)

    if (location and location):
      pass

    Moon_use = True

  wait_if_paused()
  if blue_gem_flag:
    try_count = 0
    location = wait_for_image(f'''images/{resolution_folder}/Blue_gem.jpg''',True,1)
    if __CHAOS_PY_NULL_PTR_VALUE_ERR__:
      wait_if_paused()
      l_click_py(x,y)
      sleep(0.5)
      if location:
        pass
      else:
        try_count += 1
        choice_gem_2(1)
        if wait_for_image(f'''images/{resolution_folder}/gem_close.jpg''',False,1) < time.time()-start_time:
          pass

        if (location and 5 and (850 or 950) and (location and 5 and 850)):
          pass

  wait_if_paused()
  if purple_gem_flag:
    if investment_lvl >= investment_target:
      try_count = 0
      location = wait_for_image(f'''images/{resolution_folder}/Purple_gem.jpg''',True,1)
      if __CHAOS_PY_NULL_PTR_VALUE_ERR__:
        wait_if_paused()
        l_click_py(x,y)
        sleep(0.5)
        if location:
          pass
        else:
          choice_gem_2(3)
          if wait_for_image(f'''images/{resolution_folder}/gem_close.jpg''',False,1) < time.time()-start_time:
            pass

          if (location and 3 and (850 or 950) and (location and 3 and 850)):
            pass

  wait_if_paused()
  if orange_gem_flag:
    if investment_lvl >= investment_target:
      try_count = 0
      location = wait_for_image(f'''images/{resolution_folder}/Orange_gem.jpg''',True,1)
      if location:
        if try_count != 3:
          if (time.time()-start_time < 850 or 950):
            if location:
              wait_if_paused()
              x,y = location
              l_click_py(x,y)
              sleep(0.5)
              location = wait_for_image(f'''images/{resolution_folder}/gem_close.jpg''',False,1)
              return None
              2

            location = wait_for_image(f'''images/{resolution_folder}/Orange_gem.jpg''',True,1)
            if location:
              if try_count != 3:
                if time.time()-start_time < 850:
                  pass

                if time.time()-start_time > 950:
                  pass

                return None
              else:
                return None

            else:
              return None

          else:
            return None

        else:
          return None

      else:
        return None

    else:
      return None

  else:
    return None

def choice_gem_2(type_gem):
  region1 = (int(797*s_x),int(488*s_y),int(1720*s_x),int(563*s_y))
  region2 = (int(797*s_x),int(590*s_y),int(1720*s_x),int(669*s_y))
  region3 = (int(797*s_x),int(693*s_y),int(1720*s_x),int(778*s_y))
  region4 = (int(797*s_x),int(795*s_y),int(1720*s_x),int(884*s_y))
  im1,im2,im3,im4 = take_screenshot(region1=region1,region2=region2,region3=region3,region4=region4,name='gem')
  readers = [reader,reader1,reader2,reader3]
  images = [im1,im2,im3,im4]
  results = []
  digit = type_gem == 2
  if type_gem == 1:
    search_list = Blue_search
  else:
    if type_gem == 3:
      search_list = Purple_search
    else:
      if type_gem == 2:
        if build_phys:
          search_list = ['currentbase attack power +30, currenthealth -12, currentarmor -12','currentbase attack power +10','gold per second +6, attack speed -25','base attack power +100, gold per second -2','base attack power +50, attack speed -20','gold +1000, armor -6','current health +10','armor +10, attack speed -25','attack speed +45, armor -10']
        else:
          if build_eff:
            search_list = []
          else:
            return None

  with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(lambda p: p,args))

  text1,match1,score1,gem_idx1,text2,match2,score2,gem_idx2,text3,match3,score3,gem_idx3,text4,match4,score4,gem_idx4 = results
  log(f'''[MATCH 1] \'{text1}\' → \'{match1}\' (score={score1:.2f}) index={gem_idx1}''')
  log(f'''[MATCH 2] \'{text2}\' → \'{match2}\' (score={score2:.2f}) index={gem_idx2}''')
  log(f'''[MATCH 3] \'{text3}\' → \'{match3}\' (score={score3:.2f}) index={gem_idx3}''')
  log(f'''[MATCH 4] \'{text4}\' → \'{match4}\' (score={score4:.2f}) index={gem_idx4}''')
  minimum = min(gem_idx1,gem_idx2,gem_idx3,gem_idx4)
  if gem_idx1 != 9999:
    if gem_idx1 == minimum:
      log('Выбран первый стат гема')
      l_click_py(int(1280*s_x),int(520*s_y))
      return None

  else:
    if gem_idx2 != 9999:
      if gem_idx2 == minimum:
        log('Выбран второй стат гема')
        l_click_py(int(1280*s_x),int(630*s_y))
        return None

    else:
      if gem_idx3 != 9999:
        if gem_idx3 == minimum:
          log('Выбран третий стат гема')
          l_click_py(int(1280*s_x),int(740*s_y))
          return None

      else:
        if gem_idx4 != 9999:
          if gem_idx4 == minimum:
            log('Выбран четвертый стат гема')
            l_click_py(int(1280*s_x),int(846*s_y))
            return None

        else:
          log('Совпадений не найдено — выбран рандомный стат гема')
          l_click_py(int(1280*s_x),int(520*s_y))
          return None

def process_gem(image,type_gem,reader,digit,search_list):
  def clean_text_gem(text: str,lower=True,digit=False) -> str:
    text = text.lower if lower else text
    if digit:
      text = re.sub('[^a-zA-Z ]','',text)

    text = text.replace(' z ','')
    text = text.replace(' z','')
    text = text.replace('z ','')
    text = text.replace('z','')
    text = text.replace(':','')
    text = text.replace('%','')
    text = re.sub('\\s+',' ',text).strip()
    return text

  def parse_modifiers(text: str) -> str:
    text = text.lower()
    text = re.sub('[^\\w\\s%+-]','',text)
    known_params = ['currenthealth','currentbase attack power','currenthp regen','currentarmor','gold','armor','attack speed','attack range','base attack power','gold per second']
    tokens = text.split()
    result = {}
    i = 0
    values = []
    if i < len(tokens):
      matched = False
      for j in range(min(i+5,len(tokens)),i,-1):
        candidate = ' '.join(tokens[i:j])
        if candidate in known_params:
          continue

        param = candidate
        i = j
        if i < len(tokens):
          if re.fullmatch('[+-]?\\d+%?',tokens[i]):
            result[param] = tokens[i]
            i += 1
          else:
            result[param] = None

    for key in result:
      if result[key] is not None:
        continue

      if values:
        continue

      result[key] = values.pop()
      continue
      (matched or re.fullmatch('[+-]?\\d+%?',tokens[i]))

    return (result,)((f'''{k} {v}''' for k,v in result.items() if result[k] is None))

  def get_best_match_from_gem_pool(text: str,search_pool: list[str],min_score: float = 0.8):
    try:
      best_match = None
      best_score = 0
      for candidate in search_pool:
        scores = []
        for input_item in input_items:
          best = 0
          for cand_item in candidate_items:
            match1 = re.match('(.+?)\\s+([+-]?\\d+%?)$',input_item)
            match2 = re.match('(.+?)\\s+([+-]?\\d+%?)$',cand_item)
            if match1:
              if match2:
                val1 = match1.group(2).strip()
                param1 = match1.group(1).strip()
                val2 = match2.group(2).strip()
                param2 = match2.group(1).strip()
                if param1 == param2:
                  try:
                    num1 = float(val1.replace('%',''))
                    num2 = float(val2.replace('%',''))
                    diff = abs(num1-num2)
                    max_diff = 30
                    sim = max(0,1-diff/max_diff)
                    sim = difflib.SequenceMatcher(None,input_item,cand_item).ratio()
                    sim = difflib.SequenceMatcher(None,input_item,cand_item).ratio()
                  except:
                    scores
                    sim = 1 if val1 == val2 else 0
                    match __CHAOS_PY_NULL_PTR_VALUE_ERR__:
                      case __CHAOS_PY_NULL_PTR_VALUE_ERR__:

                  except:
                    pass

    except:
      pass

    scores.append(best)
    continue
    similarity = len/scores if scores else 0
    if similarity > best_score:
      continue

    best_score = similarity
    best_match = candidate
    continue
    log(f''' → Лучшее совпадение для: "{text}" — "{best_match}" (сходство {best_score:.2f})''')
    if best_score >= min_score:
      return (best_match,best_score)
    else:
      return (None,best_score)

  if type_gem == 2:
    processed = preprocess_easyocr_image(image)
    text_raw = reader.readtext(processed)
  else:
    text_raw = reader.readtext(np.array(image))

  text_clean = clean_text_gem(' '.join([t[1] for t in sorted(text_raw,key=lambda r: (r[0][0][1],r[0][0][0]))]),digit=digit)
  if type_gem == 2:
    text_clean = parse_modifiers(text_clean)

  idx = match if match else 9999
  return (text_clean,match,score,idx)

def choice_gem(type_gem):
  try:
    def clean_text_gem(text: str,lower=True,digit=False) -> str:
      text = text.lower if lower else text
      if digit:
        text = re.sub('[^a-zA-Z ]','',text)

      text = text.replace(' z ','')
      text = text.replace(' z','')
      text = text.replace('z ','')
      text = text.replace('z','')
      text = text.replace(':','')
      text = text.replace('%','')
      text = re.sub('\\s+',' ',text).strip()
      return text

    def parse_modifiers(text: str) -> str:
      text = text.lower()
      text = re.sub('[^\\w\\s%+-]','',text)
      known_params = ['currenthealth','currentbase attack power','currenthp regen','currentarmor','gold','armor','attack speed','attack range','base attack power','gold per second']
      tokens = text.split()
      result = {}
      i = 0
      values = []
      if i < len(tokens):
        matched = False
        for j in range(min(i+5,len(tokens)),i,-1):
          candidate = ' '.join(tokens[i:j])
          if candidate in known_params:
            continue

          param = candidate
          i = j
          if i < len(tokens):
            if re.fullmatch('[+-]?\\d+%?',tokens[i]):
              result[param] = tokens[i]
              i += 1
            else:
              result[param] = None

      for key in result:
        if result[key] is not None:
          continue

        if values:
          continue

        result[key] = values.pop()
        continue
        (matched or re.fullmatch('[+-]?\\d+%?',tokens[i]))

      return (result,)((f'''{k} {v}''' for k,v in result.items() if result[k] is None))

    def get_best_match_from_gem_pool(text: str,search_pool: list[str],min_score: float = 0.8):
      try:
        best_match = None
        best_score = 0
        for candidate in search_pool:
          scores = []
          for input_item in input_items:
            best = 0
            for cand_item in candidate_items:
              match1 = re.match('(.+?)\\s+([+-]?\\d+%?)$',input_item)
              match2 = re.match('(.+?)\\s+([+-]?\\d+%?)$',cand_item)
              if match1:
                if match2:
                  val1 = match1.group(2).strip()
                  param1 = match1.group(1).strip()
                  val2 = match2.group(2).strip()
                  param2 = match2.group(1).strip()
                  if param1 == param2:
                    try:
                      num1 = float(val1.replace('%',''))
                      num2 = float(val2.replace('%',''))
                      diff = abs(num1-num2)
                      max_diff = 30
                      sim = max(0,1-diff/max_diff)
                      sim = difflib.SequenceMatcher(None,input_item,cand_item).ratio()
                      sim = difflib.SequenceMatcher(None,input_item,cand_item).ratio()
                    except:
                      scores
                      sim = 1 if val1 == val2 else 0
                      match __CHAOS_PY_NULL_PTR_VALUE_ERR__:
                        case __CHAOS_PY_NULL_PTR_VALUE_ERR__:

                    except:
                      pass

      except:
        pass

      scores.append(best)
      continue
      similarity = len/scores if scores else 0
      if similarity > best_score:
        continue

      best_score = similarity
      best_match = candidate
      continue
      log(f''' → Лучшее совпадение для: "{text}" — "{best_match}" (сходство {best_score:.2f})''')
      if best_score >= min_score:
        return (best_match,best_score)
      else:
        return (None,best_score)

    region1 = (int(797*s_x),int(488*s_y),int(1720*s_x),int(563*s_y))
    region2 = (int(797*s_x),int(590*s_y),int(1720*s_x),int(669*s_y))
    region3 = (int(797*s_x),int(693*s_y),int(1720*s_x),int(778*s_y))
    region4 = (int(797*s_x),int(795*s_y),int(1720*s_x),int(884*s_y))
    im1,im2,im3,im4 = take_screenshot(region1=region1,region2=region2,region3=region3,region4=region4,name='gem')
    if type_gem == 2:
      processed1 = preprocess_easyocr_image(im1)
      processed2 = preprocess_easyocr_image(im2)
      processed3 = preprocess_easyocr_image(im3)
      processed4 = preprocess_easyocr_image(im4)
      text1_raw = reader.readtext(processed1)
      text2_raw = reader.readtext(processed2)
      text3_raw = reader.readtext(processed3)
      text4_raw = reader.readtext(processed4)
    else:
      text1_raw = reader.readtext(np.array(im1))
      text2_raw = reader.readtext(np.array(im2))
      text3_raw = reader.readtext(np.array(im3))
      text4_raw = reader.readtext(np.array(im4))

    digit = digit if type_gem == 2 else True
    text1 = clean_text_gem(' '.join([t[1] for t in sorted(text1_raw,key=lambda r: (r[0][0][1],r[0][0][0]))]),digit=digit)
    text2 = clean_text_gem(' '.join([t[1] for t in sorted(text2_raw,key=lambda r: (r[0][0][1],r[0][0][0]))]),digit=digit)
    text3 = clean_text_gem(' '.join([t[1] for t in sorted(text3_raw,key=lambda r: (r[0][0][1],r[0][0][0]))]),digit=digit)
    text4 = clean_text_gem(' '.join([t[1] for t in sorted(text4_raw,key=lambda r: (r[0][0][1],r[0][0][0]))]),digit=digit)
    if type_gem == 2:
      text1 = parse_modifiers(text1)
      text2 = parse_modifiers(text2)
      text3 = parse_modifiers(text3)
      text4 = parse_modifiers(text4)

    log(f'''[OCR 1] {text1}''')
    log(f'''[OCR 2] {text2}''')
    log(f'''[OCR 3] {text3}''')
    log(f'''[OCR 4] {text4}''')
    gem_idx4 = (gem_idx3 := (gem_idx2 := (gem_idx1 := 9999)))
    match4 = (match3 := (match2 := (match1 := '')))
    score4 = (score3 := (score2 := (score1 := 0)))
    search_list = []
    if type_gem == 1:
      search_list = Blue_search
    else:
      if type_gem == 3:
        search_list = Purple_search
      else:
        if type_gem == 2:
          if build_phys:
            search_list = ['currentbase attack power +30, currenthealth -12, currentarmor -12','currentbase attack power +10','gold per second +6, attack speed -25','base attack power +100, gold per second -2','base attack power +50, attack speed -20','gold +1000, armor -6','current health +10','armor +10, attack speed -25','attack speed +45, armor -10']
          else:
            if build_eff:
              search_list = []
            else:
              return None

  except Exception as e:
    log(f'''[Ошибка выбора гема] {e}''')
    return None

  if type_gem == 2:
    match1,score1 = get_best_match_from_gem_pool(text1,search_list,0.9)
    match2,score2 = get_best_match_from_gem_pool(text2,search_list,0.9)
    match3,score3 = get_best_match_from_gem_pool(text3,search_list,0.9)
    match4,score4 = get_best_match_from_gem_pool(text4,search_list,0.9)
  else:
    match1,score1 = get_best_match_from_pool(text1,search_list,ignore_order=False)
    match2,score2 = get_best_match_from_pool(text2,search_list,ignore_order=False)
    match3,score3 = get_best_match_from_pool(text3,search_list,ignore_order=False)
    match4,score4 = get_best_match_from_pool(text4,search_list,ignore_order=False)

  if match1:
    gem_idx1 = search_list.index(match1)

  if match2:
    gem_idx2 = search_list.index(match2)

  if match3:
    gem_idx3 = search_list.index(match3)

  if match4:
    gem_idx4 = search_list.index(match4)

  log(f'''[MATCH 1] \'{text1}\' → \'{match1}\' (score={score1:.2f}) index={gem_idx1}''')
  log(f'''[MATCH 2] \'{text2}\' → \'{match2}\' (score={score2:.2f}) index={gem_idx2}''')
  log(f'''[MATCH 3] \'{text3}\' → \'{match3}\' (score={score3:.2f}) index={gem_idx3}''')
  log(f'''[MATCH 4] \'{text4}\' → \'{match4}\' (score={score4:.2f}) index={gem_idx4}''')
  minimum = min(gem_idx1,gem_idx2,gem_idx3,gem_idx4)
  if gem_idx1 != 9999:
    if gem_idx1 == minimum:
      log('Выбран первый стат гема')
      l_click_py(int(1280*s_x),int(520*s_y))
      return None

  else:
    if gem_idx2 != 9999:
      if gem_idx2 == minimum:
        log('Выбран второй стат гема')
        l_click_py(int(1280*s_x),int(630*s_y))
        return None

    else:
      if gem_idx3 != 9999:
        if gem_idx3 == minimum:
          log('Выбран третий стат гема')
          l_click_py(int(1280*s_x),int(740*s_y))
          return None

      else:
        if gem_idx4 != 9999:
          if gem_idx4 == minimum:
            log('Выбран четвертый стат гема')
            l_click_py(int(1280*s_x),int(846*s_y))
            return None

        else:
          log('Совпадений не найдено — выбран рандомный стат гема')
          l_click_py(int(1280*s_x),int(520*s_y))
          return None

def get_best_match_from_pool(text: str,search_pool: list[str],min_score: float = 0.8,ignore_order: bool = False):
  try:
    input_words = text.lower().split()
    best_match = None
    best_score = 0
    for item in search_pool:
      item_words = item.lower().split()
      if ignore_order:
        similarity = __CHAOS_PY_NULL_PTR_VALUE_ERR__/len+scores_item_to_input if ([(jw,)((difflib.SequenceMatcher(None,jw,iw).ratio() for iw in input_words)) for jw in [(iw,)((difflib.SequenceMatcher(None,iw,jw).ratio() for jw in item_words)) for iw in input_words]] or scores_item_to_input) else 0
      else:
        word_scores = []
        for iw in input_words:
          best_word_score = (iw,)((difflib.SequenceMatcher(None,iw,jw).ratio() for jw in item_words))
          word_scores.append(best_word_score)
          continue

        similarity = len/word_scores if word_scores else 0

      if similarity > best_score:
        continue

      best_score = similarity
      best_match = item
      continue

  except Exception as e:
    log(f'''[Ошибка в get_best_match_from_pool] {e}''')
    return (None, 0)

  log(f''' → Лучшее совпадение для: "{text}" — "{best_match}" (сходство {best_score:.2f})''')
  if best_score >= min_score:
    return (best_match,best_score)
  else:
    return (None,best_score)

def choice_skill(prior=False):
  try:
    region1 = (int(692*s_x),int(555*s_y),int(989*s_x),int(625*s_y))
    region2 = (int(1138*s_x),int(538*s_y),int(1414*s_x),int(587*s_y))
    region3 = (int(1593*s_x),int(541*s_y),int(1839*s_x),int(625*s_y))
    im1,im2,im3 = take_screenshot(region1=region1,region2=region2,region3=region3,name='skill')
    text1_raw = reader.readtext(np.array(im1))
    text2_raw = reader.readtext(np.array(im2))
    text3_raw = reader.readtext(np.array(im3))
    text1 = clean_text(' '.join([t[1] for t in sorted(text1_raw,key=lambda r: (r[0][0][1],r[0][0][0]))]))
    text2 = clean_text(' '.join([t[1] for t in sorted(text2_raw,key=lambda r: (r[0][0][1],r[0][0][0]))]))
    text3 = clean_text(' '.join([t[1] for t in sorted(text3_raw,key=lambda r: (r[0][0][1],r[0][0][0]))]))
    log(f'''[Считал навык 1] {text1}''')
    log(f'''[Считал навык 2] {text2}''')
    log(f'''[Считал навык 3] {text3}''')
    text1,_ = get_best_match_from_pool(text1,ability_names,ignore_order=True)
    text2,_ = get_best_match_from_pool(text2,ability_names,ignore_order=True)
    text3,_ = get_best_match_from_pool(text3,ability_names,ignore_order=True)
    log(f'''[Распознан навык 1] {text1}''')
    log(f'''[Распознан навык 2] {text2}''')
    log(f'''[Распознан навык 3] {text3}''')
    candidates = [(1,text1),(2,text2),(3,text3)]
  except Exception as e:
    log(f'''[Ошибка выбора навыка] {e}''')
    return None

  if prior:
    log(f'''[Распознанные навыки] candidates: {candidates}''')
    log(f'''[Распознанные навыки] priority_indices: {priority_indices}''')

  chosen_region = 0
  chosen_skill = None
  for group in __CHAOS_PY_NO_ITER_ERR__:
    if __CHAOS_PY_NULL_PTR_VALUE_ERR__:
      continue

    active_group_candidates.append(group)
    continue

  def get_set_completion_potential(skill_name):
    skill_index = skill_states[skill_name]['index']
    for group in active_group_candidates:
      if skill_index in group:
        continue

      current_count = (group,)((1 for s in active_skills.values() if s if s['index'] in group))
      if current_count < len(group):
        continue

      needed = len(group)-current_count-1
      needed
      break
    else:
      __CHAOS_PY_PASS_ERR__
    return float('inf')

  for idx,skill in float('inf'):
    if score < best_score:
      continue

    log('Нашел навык приоритет по сбору сета')
    continue
    skill

  if chosen_region == 0:
    for idx,skill in candidates:
      if skill_states[skill]['index'] in priority_indices:
        continue

      log('Нашел навык приоритет')
      chosen_region = idx
      chosen_skill = skill
      idx
      break
      score

  if get_set_completion_potential(skill) == chosen_region:
    for idx,skill in __CHAOS_PY_NO_ITER_ERR__:
      if skill_states[skill].get('set',False):
        continue

      log('Нашел навык приоритет с set=True')
      skill
      idx

  if (prior or 0) == chosen_region:
    for idx,skill in __CHAOS_PY_NO_ITER_ERR__:
      if skill_states[skill].get('replace',False):
        continue

      log('Нашел навык приоритет c replace=True')
      skill
      idx

  if __CHAOS_PY_NULL_PTR_VALUE_ERR__:
    pass

  if chosen_skill:
    log(f'''[Выбран навык] Позиция: {chosen_region}, Навык: {chosen_skill}''')
  else:
    log('[Не удалось выбрать навык из распознанных]')
    chosen_region = 0
    chosen_skill = None

  return (chosen_region,chosen_skill)

def check_slots():
  region = (int(1014*s_x),int(1195*s_y),int(1535*s_x),int(1249*s_y))
  screen = take_screenshot(name='slots')
  image_path = f'''images/{resolution_folder}/Slots.jpg'''
  image = Image.open(image_path)
  coords = find_images_on_screen_2(screen,image,False,0.9,region)
  log(f'''Обнаружено {len(coords)} свободных слотов для навыков''')
  return len(coords)

def skills(prior=False):
  def Wprice():
    region1 = (int(1265*s_x),int(1093*s_y),int(1613*s_x),int(1130*s_y))
    im1 = take_screenshot(region1=region1,name='Wprice')[0]
    text = reader.readtext(np.array(im1),low_text=0.4)
    sorted_results = sorted(text,key=lambda r: (r[0][0][1],r[0][0][0]))
    text_list = ' '.join([t[1] for t in sorted_results]).lower()
    digits_only = re.sub('\\D','',text_list)
    log(f'''Стоимость W: {digits_only}''')
    if digits_only:
      return int(digits_only)
    else:
      return 0

  def pick_skills(pos,aba=False):
    if pos == 1:
      log('\n==========')
      log('Кликаю первый навык')
      log('==========\n')
      l_click_py(int(843*s_x),int(561*s_y))
      return None
    else:
      if pos == 2:
        log('\n==========')
        log('Кликаю второй навык')
        log('==========\n')
        l_click_py(int(1287*s_x),int(533*s_y))
        return None
      else:
        if pos == 3:
          log('\n==========')
          log('Кликаю третий навык')
          log('==========\n')
          l_click_py(int(1727*s_x),int(569*s_y))
          return None
        else:
          if already_refresh != refresh_count:
            if aba:
              log('\n==========')
              log('Кликаю Refresh')
              log('==========\n')
              l_click_py(int(1124*s_x),int(1042*s_y))
              sleep(1)
              return None

          else:
            log('\n==========')
            log('Кликаю Abandon')
            log('==========\n')
            l_click_py(int(1465*s_x),int(1042*s_y))
            return None

  def can_complete_any_set():
    for group in set_groups:
      missing = set(group)-current_indices
      if len(missing) == 1:
        continue

      {s['index'] for s in active_skills.values() if s}
      break
    else:
      return False

  with global_lock:
    wait_if_paused()
    mouse_move(int(1175*s_x),int(1298*s_y))
    sleep(0.5)
    price = Wprice()
    budjet = check_budjet()
    find_skill_try = 0

  if priority_found:
    if prior == True:
      pass
    else:
      if prior == True:
        pass
        None(None,None)
        return None

  data['index'] in priority_indices
  if __CHAOS_PY_NULL_PTR_VALUE_ERR__ > len(active_skills):
    if skills_done:
      wait_if_paused()
      find_skill_try += 1
      mouse_safe()
      log(f'''Обнаружено {current_slots} свободных слотов для навыков''')
      if sum((1 for skill in active_skills.values() if skill is not None)) > len(active_skills):
        l_click_py(int(1177*s_x),int(1298*s_y))
        sleep(0.5)
        if current_slots > 0:
          if choice == 0:
            if already_refresh != refresh_count:
              pick_skills(choice)
              already_refresh += 1
              True
              pass
              None
              return None
              if choice == 0:
                if already_refresh != refresh_count:
                  pass

          choice
          if __CHAOS_PY_NULL_PTR_VALUE_ERR__ >= already_refresh:
            if ((prior and 0 and int(refresh_count/2)) or prior):
              pass
              None
              return None

          else:
            if name:
              for i in range:
                if i is not None:
                  continue

                active_skills[i] = new_skill
                i

              del(ability_registry[name][skill_states])
              check_and_collapse_sets(replace_slot=pos)

        else:
          if current_slots == 0:
            if choice == 0:
              if already_refresh != refresh_count:
                choice
                already_refresh += 1
                if choice == 0:
                  if already_refresh != refresh_count:
                    pass

            if name:
              for group in new_skill.get:
                if __CHAOS_PY_NULL_PTR_VALUE_ERR__ not in new_index:
                  continue

                if set(found+[new_index]) == set(group):
                  continue

                for slot,skill in [i for ability_registry[name] in [s['index'] for new_skill['index'] in False if s if s] if i if i in group]:
                  if skill:
                    continue

                  if skill['index'] in group:
                    continue

                  slot
                  True

                if can_replace_for_set:
                  continue

              if can_replace_for_set:
                for slot,skill in pick_skills:
                  if slot != replace_for_set_index:
                    continue

                  if skill['index'] in group:
                    continue

                  active_skills[slot] = None
                  continue
                  False

                active_skills[replace_for_set_index] = new_skill
                log('\n===========')
                log(f'''Заменяю навык в слоте {pos} (по групповой замене)''')
                log('============\n')
                log('\n===========')
                log(f'''Сет собран в слоте {replace_for_set_index} из группы {group}''')
                log('============\n')

              if already_replaced == False:
                for i in range:
                  if i:
                    continue

                  if 'replace':
                    continue

                  active_skills[i] = new_skill
                  '\n==========='
                  f'''Заменяю навык в слоте {i}'''
                  '============'
                  log
                  log

              del(log[skill_states])
              pick_skills(choice)
              slot_click(pos)
              if new_skill.get != pos:
                check_and_collapse_sets(replace_slot=pos)

            else:
              choice

      if already_refresh == refresh_count:
        if replacable_exists == False:
          'Свободные слоты или рероллы закончились, прекращаю искать навыки'
          pass
          None
          return None

      else:
        1298*s_y
        0.5
        mouse_safe
        if check_budjet > len(active_skills):
          if skill_states.items if choice == 0 else new_skill:
            pass

  None
  return None

def slot_click(i):
  coords = [(1011, 573),(1186, 573),(1361, 573),(1536, 573),(1011, 714),(1186, 714),(1361, 714),(1536, 714),(1011, 855),(1186, 855)]
  x,y = coords[i]
  sleep(1)
  l_click_py(int(x*s_x),int(y*s_y))
  return None

def check_and_collapse_sets(replace_slot=None):
  for group in set_groups:
    if active_skills[replace_slot]['index'] not in group:
      continue

    found_slots = []
    found_skill_indices = []
    for slot,skill in active_skills.items():
      if skill:
        continue

      if skill['index'] in group:
        continue

      found_slots.append(slot)
      found_skill_indices.append(skill['index'])
      continue

    if set(found_skill_indices) == set(group):
      continue

    for slot in found_slots:
      if slot != replace_slot:
        continue

      active_skills[slot] = None
      continue

    log(f'''Сет собран в слоте {replace_slot} из группы {group}''')
    break

  return None

def use_omni():
  if gem_flag:
    location = wait_for_image(f'''images/{resolution_folder}/Omni.jpg''',True,1)
    try_count = 0
    if location:
      if try_count != 5:
        if location:
          wait_if_paused()
          x,y = location
          l_click_py(x,y)
          try_count += 1

        location = wait_for_image(f'''images/{resolution_folder}/Omni.jpg''',True,1)
        if location:
          if try_count != 5:
            pass

          return None
        else:
          return None

      else:
        return None

    else:
      return None

  else:
    return None

def open_market(state):
  if state:
    l_click_py(int(2220*s_x),int(1400*s_y))
    sleep(1)
    l_click_py(int(2260*s_x),int(40*s_y))
    sleep(1)
    return None
  else:
    l_click_py(int(2220*s_x),int(1400*s_y))
    sleep(1)
    return None

def buy_items(end,count):
  if buy_itms:
    variable_names = ['desolator','desolator_up','daedalus','daedalus_up','abyss','butterfly','dagon','dagon_up','parasma','parasma_up','eul','eul_up','eul_up2','gleip','gleip_up','link','aeon','trident']
    already_buy = sum((1 for name in variable_names if globals().get(name) is True))
    with global_lock:
      if build_mag:
        budjet = check_budjet()
        if __CHAOS_PY_NULL_PTR_VALUE_ERR__ > budjet:
          if already_buy < count:
            wait_if_paused()
            log('\n=================')
            log('[Покупка предметов] Покупаю дагон мини')
            log('=================\n')
            open_market(True)
            r_click_py(int(2085*s_x),int(242*s_y))
            already_buy += 1
            open_market(False)

        if budjet == 0:
          budjet = check_budjet()

        if dagon:
          if dagon_up:
            __CHAOS_PY_IF_NO_BODY_ERR__

      if dagon:
        if dagon_up:
          __CHAOS_PY_IF_NO_BODY_ERR__

    if eul:
      if eul_up:
        if eul_up2:
          __CHAOS_PY_IF_NO_BODY_ERR__

  if eul:
    if eul_up:
      if eul_up2:
        __CHAOS_PY_IF_NO_BODY_ERR__

  if False == count:
    if already_buy < count:
      if location:
        wait_if_paused()
        log('\n=================')
        log('[Покупка предметов] Покупаю паразму')
        log('=================\n')
        open_market(True)
        l_click_py(x,y)
        sleep(1)
        r_click_py(int(2342*s_x),int(973*s_y))
        already_buy += 1
        open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if (parasma == False and False and 16000 and 6) > budjet:
    if find_images_on_screen_2(screenshot,f'''images/{resolution_folder}/items_t3/orb.jpg''',True,1) >= len(location):
      wait_if_paused()
      log('\n=================')
      log('[Покупка предметов] Апаю паразму')
      log('=================\n')
      open_market(True)
      l_click_py(x,y)
      sleep(1)
      r_click_py(int(2506*s_x),int(970*s_y))
      open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if dagon:
    if dagon_up:
      __CHAOS_PY_IF_NO_BODY_ERR__

  if eul:
    if eul_up:
      if eul_up2:
        __CHAOS_PY_IF_NO_BODY_ERR__

  if 0 == count:
    if already_buy < count:
      wait_if_paused()
      open_market(True)
      log('\n=================')
      log('[Покупка предметов] Покупаю тридент')
      log('=================\n')
      l_click_py(int(2332*s_x),int(302*s_y))
      sleep(1)
      l_click_py(int(2263*s_x),int(971*s_y))
      sleep(1)
      l_click_py(int(2296*s_x),int(971*s_y))
      sleep(1)
      l_click_py(int(2296*s_x),int(971*s_y))
      sleep(1)
      r_click_py(int(2296*s_x),int(971*s_y))
      already_buy += 1
      open_market(False)

  if build_phys:
    budjet = check_budjet()
    if (trident == False and 130000 and 6) == desolator:
      if already_buy < count:
        wait_if_paused()
        log('\n=================')
        log('[Покупка предметов] Покупаю дезолятор')
        log('=================\n')
        open_market(True)
        l_click_py(int(2090*s_x),int(301*s_y))
        sleep(1)
        r_click_py(int(2300*s_x),int(971*s_y))
        sleep(1)
        already_buy += 1
        open_market(False)

    if budjet == 0:
      budjet = check_budjet()

    if True > budjet:
      if already_buy < count:
        if location:
          wait_if_paused()
          log('\n=================')
          log('[Покупка предметов] Покупаю даедалус')
          log('=================\n')
          open_market(True)
          l_click_py(x,y)
          sleep(1)
          r_click_py(int(2213*s_x),int(973*s_y))
          already_buy += 1
          open_market(False)

    if budjet == 0:
      budjet = check_budjet()

    if desolator:
      if desolator_up:
        __CHAOS_PY_IF_NO_BODY_ERR__

  if 0 == count:
    if already_buy < count:
      if location:
        wait_if_paused()
        log('\n=================')
        log('[Покупка предметов] Покупаю абисал')
        log('=================\n')
        open_market(True)
        l_click_py(x,y)
        sleep(1)
        r_click_py(int(2455*s_x),int(974*s_y))
        already_buy += 1
        open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if desolator:
    if desolator_up:
      __CHAOS_PY_IF_NO_BODY_ERR__

  if 0 == count:
    if already_buy < count:
      if location:
        if location:
          wait_if_paused()
          log('\n=================')
          log('[Покупка предметов] Покупаю бабочку')
          log('=================\n')
          open_market(True)
          l_click_py(x,y)
          sleep(1)
          l_click_py(int(2328*s_x),int(972*s_y))
          sleep(1)
          r_click_py(int(2300*s_x),int(972*s_y))
          already_buy += 1
          open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if desolator:
    if desolator_up:
      __CHAOS_PY_IF_NO_BODY_ERR__

  if (butterfly == False and 85000 and 6) == count:
    if already_buy < count:
      if location:
        wait_if_paused()
        log('\n=================')
        log('[Покупка предметов] Покупаю линку')
        log('=================\n')
        open_market(True)
        l_click_py(x,y)
        sleep(1)
        r_click_py(int(2160*s_x),int(972*s_y))
        already_buy += 1
        open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if desolator:
    if desolator_up:
      __CHAOS_PY_IF_NO_BODY_ERR__

  if 0 == count:
    if already_buy < count:
      open_market(True)
      wait_if_paused()
      log('\n=================')
      log('[Покупка предметов] Покупаю тридент')
      log('=================\n')
      l_click_py(int(2332*s_x),int(302*s_y))
      sleep(1)
      l_click_py(int(2263*s_x),int(971*s_y))
      sleep(1)
      l_click_py(int(2296*s_x),int(971*s_y))
      sleep(1)
      l_click_py(int(2296*s_x),int(971*s_y))
      sleep(1)
      r_click_py(int(2296*s_x),int(971*s_y))
      already_buy += 1
      open_market(False)

  if build_eff:
    budjet = check_budjet()
    if 0 > budjet:
      if already_buy < count:
        wait_if_paused()
        log('\n=================')
        log('[Покупка предметов] Покупаю глейпнир мини')
        log('=================\n')
        open_market(True)
        l_click_py(int(2265*s_x),int(242*s_y))
        sleep(1)
        l_click_py(int(2273*s_x),int(978*s_y))
        sleep(1)
        r_click_py(int(2300*s_x),int(975*s_y))
        already_buy += 1
        open_market(False)

    if budjet == 0:
      budjet = check_budjet()

    if gleip:
      if gleip_up:
        __CHAOS_PY_IF_NO_BODY_ERR__

  if gleip:
    if gleip_up:
      __CHAOS_PY_IF_NO_BODY_ERR__

  if 0 > budjet:
    if already_buy < count:
      wait_if_paused()
      log('\n=================')
      log('[Покупка предметов] Покупаю аеон')
      log('=================\n')
      open_market(True)
      l_click_py(int(2090*s_x),int(520*s_y))
      sleep(0.5)
      l_click_py(int(2240*s_x),int(1130*s_y))
      sleep(0.5)
      r_click_py(int(2271*s_x),int(972*s_y))
      already_buy += 1
      open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if gleip:
    if gleip_up:
      __CHAOS_PY_IF_NO_BODY_ERR__

  if eul:
    if eul_up:
      if eul_up2:
        __CHAOS_PY_IF_NO_BODY_ERR__

  if 0 == count:
    if already_buy < count:
      if location:
        wait_if_paused()
        log('\n=================')
        log('[Покупка предметов] Покупаю даедалус')
        log('=================\n')
        open_market(True)
        l_click_py(x,y)
        sleep(1)
        r_click_py(int(2213*s_x),int(973*s_y))
        already_buy += 1
        open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if (daedalus == False and 20000 and 6) > budjet:
    if location:
      wait_if_paused()
      log('\n=================')
      log('[Покупка предметов] Апаю еула')
      log('=================\n')
      open_market(True)
      l_click_py(x,y)
      sleep(1)
      r_click_py(int(2269*s_x),int(974*s_y))
      open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if (eul_up == False and 7000) > budjet:
    if location:
      if location:
        wait_if_paused()
        log('\n=================')
        log('[Покупка предметов] Апаю еул лвл 3')
        log('=================\n')
        open_market(True)
        l_click_py(x,y)
        sleep(1)
        r_click_py(int(2382*s_x),int(973*s_y))
        open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if (eul_up2 == False and 40000) > budjet:
    if location:
      wait_if_paused()
      log('\n=================')
      log('[Покупка предметов] Апаю глейпнир')
      log('=================\n')
      open_market(True)
      l_click_py(x,y)
      sleep(1)
      r_click_py(int(2295*s_x),int(976*s_y))
      open_market(False)

  if budjet == 0:
    budjet = check_budjet()

  if gleip:
    if gleip_up:
      __CHAOS_PY_IF_NO_BODY_ERR__

  if eul:
    if eul_up:
      if eul_up2:
        __CHAOS_PY_IF_NO_BODY_ERR__

  if 0 == count:
    if already_buy < count:
      wait_if_paused()
      open_market(True)
      log('\n=================')
      log('[Покупка предметов] Покупаю тридент')
      log('=================\n')
      l_click_py(int(2332*s_x),int(302*s_y))
      sleep(1)
      l_click_py(int(2263*s_x),int(971*s_y))
      sleep(1)
      l_click_py(int(2296*s_x),int(971*s_y))
      sleep(1)
      l_click_py(int(2296*s_x),int(971*s_y))
      sleep(1)
      r_click_py(int(2296*s_x),int(971*s_y))
      already_buy += 1
      open_market(False)

  return None
  return None

def pick_up_items(end=False):
  if build_mag:
    if build_phys:
      if build_eff:
        __CHAOS_PY_IF_NO_BODY_ERR__

  f3()
  sleep(1)
  image_to_inventory = ['Blue_gem.jpg','Purple_gem.jpg','Orange_gem.jpg','Omni.jpg']
  def sell_unwanted_items():
    log('[Сортировка предметов] Продаем ненужные предметы')
    def process_item(image_name):
      image_path = f'''images/{resolution_folder}/{image_name}'''
      try_count = 0
      location = wait_for_image(image_path,True,1,loger=False)
      if location:
        if try_count < 2:
          wait_if_paused()
          try_count += 1
          x,y = location
          with global_lock:
            r_click_py(x+10,y+10)
            location_sell = wait_for_image(f'''images/{resolution_folder}/sell.jpg''',True,3,loger=False)
            if location_sell:
              l_click_py(location_sell[0]+10,location_sell[1]+5)

          location = wait_for_image(image_path,True,1,loger=False)
          if location:
            if try_count < 2:
              pass

            return None
          else:
            return None

        else:
          return None

      else:
        return None

    with ThreadPoolExecutor(max_workers=6) as executor:
      executor.map(process_item,image_to_sell)

    return None

  def move_items_to_stash():
    inventory_region = (int(1525*s_x),int(1251*s_y),int(1836*s_x),int(1428*s_y))
    def process_item(image_name):
      image_path = f'''images/{resolution_folder}/{image_name}'''
      try_count = 0
      location = wait_for_image(image_path,True,1,region=inventory_region,loger=False)
      if location:
        if try_count < 2:
          wait_if_paused()
          log(f'''[Сортировка предметов] Переносим предметы в стэш: {image_name}''')
          try_count += 1
          x,y = location
          with global_lock:
            r_click_py(x+10,y+10)
            location_stash = wait_for_image(f'''images/{resolution_folder}/to_stash.jpg''',True,3,loger=False)
            if location_stash:
              l_click_py(location_stash[0]+10,location_stash[1]+5)

          location = wait_for_image(image_path,True,1,region=inventory_region,loger=False)
          if location:
            if try_count < 2:
              pass

            return None
          else:
            return None

        else:
          return None

      else:
        return None

    with ThreadPoolExecutor(max_workers=6) as executor:
      executor.map(process_item,image_to_stash.keys())

    return None

  def sell_duplicate_kept_items():
    stash_region = (int(2135*s_x),int(1174*s_y),int(2544*s_x),int(1347*s_y))
    def process_item(image_name,keep_count):
      image_path = f'''images/{resolution_folder}/{image_name}'''
      template_image = Image.open(image_path)
      screenshot = take_screenshot()
      locations = find_images_on_screen_2(screenshot,template_image,False,0.9,region=stash_region)
      if locations:
        if len(locations) > keep_count:
          log(f'''[Сортировка предметов] Продаем ненужные дубликаты нужного предмета: {image_name}''')
          for x,y in locations[keep_count:]:
            with global_lock:
              wait_if_paused()
              r_click_py(x+10,y+10)
              location_sell = wait_for_image(f'''images/{resolution_folder}/sell.jpg''',True,3,loger=False)
              if location_sell:
                l_click_py(location_sell[0]+10,location_sell[1]+5)

            continue

          return None
        else:
          return None

      else:
        return None

    with ThreadPoolExecutor(max_workers=4) as executor:
      for __CHAOS_PY_NO_TARGETS_ERR__ in __CHAOS_PY_NO_ITER_ERR__:
        f.result()
        continue
        [executor.submit(process_item,name,count) for name,count in image_to_stash.items()]

    None(None,None)
    return None

  def move_gems_to_inventory():
    stash_region = (int(2135*s_x),int(1174*s_y),int(2544*s_x),int(1347*s_y))
    def process_item(image_name):
      image_path = f'''images/{resolution_folder}/{image_name}'''
      location = 1 if end else wait_for_image(image_path,True,1,region=stash_region,loger=False)
      if location:
        log(f'''[Сортировка предметов] Переносим камни в инвентарь: {image_name}''')
        x,y = location
        with global_lock:
          wait_if_paused()
          r_click_py(x+10,y+10)
          location_target = False
          if location_target:
            l_click_py(location_target[0]+10,location_target[1]+5)

        return None
      else:
        return None

    with ThreadPoolExecutor(max_workers=4) as executor:
      executor.map(process_item,image_to_inventory)

    return None

  sell_unwanted_items()
  move_items_to_stash()
  sell_duplicate_kept_items()
  move_gems_to_inventory()
  return None
  return None

def check_budjet(loger=True):
  region1 = (int(2135*s_x),int(1380*s_y),int(2287*s_x),int(1430*s_y))
  im1 = take_screenshot(region1=region1,name='budjet')[0]
  text = reader.readtext(np.array(im1),low_text=0.4)
  sorted_results = sorted(text,key=lambda r: (r[0][0][1],r[0][0][0]))
  text_list = ' '.join([t[1] for t in sorted_results]).lower()
  digits_only = re.sub('\\D','',text_list)
  if loger:
    log(f'''[Проверка бюджета] Текущий бюджет: {digits_only}''')

  if digits_only:
    return int(digits_only)
  else:
    return 0

def error_cheker():
  if thread_close:
    if bot_running:
      location = wait_for_image(f'''images/{resolution_folder}/close.jpg''',False,1,loger=False)
      if location:
        sleep(3)
        location = wait_for_image(f'''images/{resolution_folder}/close.jpg''',False,1,loger=False)
        if location:
          l_click_py(location[0]+15*s_x,location[1]+15*s_y)

      sleep(1)
      if thread_close:
        if bot_running:
          pass

        return None
      else:
        return None

    else:
      return None

  else:
    return None

def end_cheker():
  if thread_end:
    if bot_running:
      if time.time()-start_time < 1200:
        location = wait_for_image(f'''images/{resolution_folder}/End.png''',False,1,0.9,loger=False)
        if location:
          log('Кликаем подтвердить окно отчета')
          l_click_py(location[0]+10,location[1]+10)
          thread_end = True
          return None
        else:
          sleep(5)
          if thread_end:
            if bot_running:
              if time.time()-start_time < 1200:
                pass

              return None
            else:
              return None

          else:
            return None

      else:
        return None

    else:
      return None

  else:
    return None

def skills_cheker():
  if thread_skills:
    if bot_running:
      location = wait_for_image(f'''images/{resolution_folder}/replace.jpg''',False,1,loger=False)
      if location:
        sleep(5)
        location = wait_for_image(f'''images/{resolution_folder}/replace.jpg''',False,1,loger=False)
        if __CHAOS_PY_NULL_PTR_VALUE_ERR__:
          log('[БАГ] было обнаружено зависшее окно замены навыка, пытаемся убрать')
          l_click_py(int(1177*s_x),int(1298*s_y))
          sleep(0.5)
          l_click_py(int(1465*s_x),int(1042*s_y))

        if location:
          slot_click(0)

        if (location and location):
          pass

      if thread_skills:
        if bot_running:
          pass

        return None
      else:
        return None

    else:
      return None

  else:
    return None

def investment_up():
  if investment_lvl < investment_target:
    if investment_lvl < 50:
      if bot_running:
        wait_if_paused()
        if __CHAOS_PY_NULL_PTR_VALUE_ERR__ not in priority_indices:
          priority_indices.append(6)

        budget = check_budjet(False)
        if (investment_lvl+5 > investment_target and 6) > time.time()-start_time:
          if desolator:
            if desolator_up:
              if gleip:
                if gleip_up:
                  if dagon_up:
                    __CHAOS_PY_IF_NO_BODY_ERR__

      return None

  else:
    return None

  return None

def FarmT7():
  if bot_running:
    if authorization:
      log('🔁 Выполняется действие бота...')
      sleep(1)
      start(int(difficulty))
      log('ожидаем 15 минут')
      sleep(5)
      start_time = time.time()
      last_pick_up_time = time.time()
      location = wait_for_image(f'''images/{resolution_folder}/in_game.jpg''',True,10,loger=False)
      if location:
        slots = check_slots()
        active_skills = {i: None for i in range(slots)}

      if bot_running:
        return None
      else:
        pick_up_count = 0
        threading.Thread(target=error_cheker,daemon=True).start()
        threading.Thread(target=end_cheker,daemon=True).start()
        if skills_state:
          threading.Thread(target=skills_cheker,daemon=True).start()

        if investment_target > 0:
          threading.Thread(target=investment_up,daemon=True).start()

        if chalenge_up_flag:
          if chalenge_flag:
            __CHAOS_PY_IF_NO_BODY_ERR__

      if bot_running:
        return None
      else:
        wait_if_paused()
        pick_up_items()
        wait_if_paused()
        use_items()
        wait_if_paused()
        use_omni()
        wait_if_paused()
        buy_items(False,2)
        if bot_running:
          return None
        else:
          thread_challenge = False
          wait_if_paused()
          log('[Уведомление] Иду бить рошана')
          move_left(500*s_x)
          move_left(500*s_x)
          move_left(500*s_x)
          move_up(500*s_y)
          move_up(500*s_y)
          move_up(500*s_y)
          move_up(100*s_y)
          sleep(0.5)
          mouse_and_keyboard(int(567*s_x),int(182*s_y))
          if (skills_state and (10 or False)) < time.time()-start_time:
            wait_if_paused()
            sleep(5)
            mouse_and_keyboard(int(567*s_x),int(182*s_y))
            blink(int(567*s_x),int(182*s_y))
            if (thread_end or 1200 or 1200):
              pass

          pass
          if thread_end:
            log('[Уведомление] Рошан убит')
            if bot_running:
              return None
            else:
              wait_if_paused()
              blink(int(1512*s_x),int(887*s_y))
              blink(int(1512*s_x),int(887*s_y))
              blink(int(1512*s_x),int(887*s_y))
              wait_if_paused()
              use_omni()
              wait_if_paused()
              pick_up_items(True)
              wait_if_paused()
              buy_items(True,6)
              wait_if_paused()
              buy_items(True,6)
              bad_flag = False
              if push_flag:
                Push()

              if bad_flag:
                if fate_flag:
                  if random_fate_flag:
                    if random_talent_flag:
                      if talent_flag:
                        if random_arena_flag:
                          if rainbow_flag:
                            if arena_flag:
                              __CHAOS_PY_IF_NO_BODY_ERR__

          log('[Уведомление] Не убил рошана за 20 минут')
          restart(True)
          thread_close = False
          thread_end = True
          thread_challenge = False
          thread_skills = False
          bad_flag = False

        if authorization:
          pass

        return None
        return None

  return None
  return None

def Push():
  keyboard_f2()
  sleep(1)
  keyboard_f2()
  sleep(2)
  mouse_safe()
  log('Кликаем на пуш')
  if bot_running:
    return None
  else:
    l_click_py(int(1732*s_x),int(840*s_y))
    sleep(1)
    l_click_py(int(1090*s_x),int(830*s_y))
    sleep(1)
    log('Бьем первого босса')
    sleep(5)
    offset = 500
    location = wait_for_image(f'''images/{resolution_folder}/Push.jpg''',False,3,0.9)
    if location:
      move_up(offset*s_y)
      offset-500
      sleep(1)
      mouse_and_keyboard(int(1275*s_x),int(113*s_y))
      location = wait_for_image(f'''images/{resolution_folder}/Push.jpg''',False,50,0.9)

    if location:
      x,y = location
      l_click_py(x+20,y+30)
      sleep(0.5)
      l_click_py(int(1282*s_x),int(1154*s_y))
      sleep(0.5)

    if offset > 0:
      move_up(offset*s_y)

    r_click_py(int(1280*s_x),int(540*s_y))
    blink(int(1280*s_x),int(540*s_y))
    r_click_py(int(1280*s_x),int(540*s_y))
    sleep(1)
    log('Бьем второго босса')
    sleep(1)
    move_right(500*s_x)
    r_click_py(int(2043*s_x),int(589*s_y))
    move_right(500*s_x)
    move_right(500*s_x)
    move_right(500*s_x)
    move_right(500*s_x)
    move_right(500*s_x)
    move_right(500*s_x)
    move_right(500*s_x)
    blink(int(2043*s_x),int(589*s_y))
    r_click_py(int(2043*s_x),int(589*s_y))
    blink(int(2043*s_x),int(589*s_y))
    r_click_py(int(2043*s_x),int(589*s_y))
    blink(int(2043*s_x),int(589*s_y))
    mouse_and_keyboard(int(2290*s_x),int(780*s_y))
    if bad_flag:
      location = wait_for_image(f'''images/{resolution_folder}/Push.jpg''',False,50,0.9)
      if location:
        x,y = location
        l_click_py(x+20,y+30)
        sleep(0.5)
        l_click_py(int(1282*s_x),int(1154*s_y))
        sleep(0.5)

    r_click_py(int(1467*s_x),int(579*s_y))
    blink(int(1467*s_x),int(579*s_y))
    r_click_py(int(1467*s_x),int(579*s_y))
    sleep(1)
    log('Бьем третьего босса')
    move_down(500*s_y)
    move_down(500*s_y)
    r_click_py(int(1405*s_x),int(1100*s_y))
    move_down(500*s_y)
    move_down(500*s_y)
    move_down(500*s_y)
    move_down(500*s_y)
    blink(int(1405*s_x),int(1100*s_y))
    r_click_py(int(1405*s_x),int(1100*s_y))
    blink(int(1405*s_x),int(1100*s_y))
    r_click_py(int(1405*s_x),int(1100*s_y))
    blink(int(1405*s_x),int(1100*s_y))
    mouse_and_keyboard(int(1534*s_x),int(940*s_y))
    if bad_flag:
      location = wait_for_image(f'''images/{resolution_folder}/Push.jpg''',False,50,0.9)
      if location:
        x,y = location
        l_click_py(x+20,y+30)
        sleep(1)
        l_click_py(int(1282*s_x),int(1154*s_y))
        sleep(1)

    r_click_py(int(1403*s_x),int(247*s_y))
    blink(int(1403*s_x),int(247*s_y))
    blink(int(1403*s_x),int(247*s_y))
    r_click_py(int(1403*s_x),int(247*s_y))
    sleep(1)
    log('Бьем четвертого босса')
    move_left(500*s_x)
    move_left(500*s_x)
    r_click_py(int(340*s_x),int(269*s_y))
    move_left(500*s_x)
    move_left(500*s_x)
    move_left(500*s_x)
    move_left(500*s_x)
    move_left(500*s_x)
    move_left(500*s_x)
    blink(int(340*s_x),int(269*s_y))
    r_click_py(int(340*s_x),int(269*s_y))
    blink(int(340*s_x),int(269*s_y))
    r_click_py(int(340*s_x),int(269*s_y))
    blink(int(340*s_x),int(269*s_y))
    mouse_and_keyboard(int(340*s_x),int(386*s_y))
    if bad_flag:
      location = wait_for_image(f'''images/{resolution_folder}/Push.jpg''',False,50,0.9)
      if location:
        x,y = location
        l_click_py(x+20,y+30)
        sleep(1)
        l_click_py(int(1282*s_x),int(1154*s_y))
        sleep(1)

    r_click_py(int(1235*s_x),int(270*s_y))
    blink(int(1235*s_x),int(270*s_y))
    blink(int(1235*s_x),int(270*s_y))
    r_click_py(int(1235*s_x),int(270*s_y))
    sleep(1)
    log('Бьем пятого босса')
    sleep(1)
    move_down(500*s_y)
    move_down(500*s_y)
    r_click_py(int(340*s_x),int(269*s_y))
    move_down(500*s_y)
    move_down(500*s_y)
    move_down(300*s_y)
    blink(int(1330*s_x),int(1100*s_y))
    r_click_py(int(1330*s_x),int(1100*s_y))
    blink(int(1330*s_x),int(1100*s_y))
    r_click_py(int(1330*s_x),int(1100*s_y))
    blink(int(1330*s_x),int(1100*s_y))
    mouse_and_keyboard(int(1982*s_x),int(1070*s_y))
    if bad_flag:
      location = wait_for_image(f'''images/{resolution_folder}/Push.jpg''',False,50,0.9)
      if location:
        x,y = location
        l_click_py(x+20,y+30)
        sleep(1)
        l_click_py(int(1282*s_x),int(1154*s_y))
        sleep(1)

    log('Выходим')
    sleep(0.3)
    l_click_py(int(1282*s_x),int(1154*s_y))
    sleep(0.3)
    l_click_py(int(1282*s_x),int(1154*s_y))
    sleep(0.3)
    l_click_py(int(1282*s_x),int(1154*s_y))
    sleep(0.3)
    location = wait_for_image(f'''images/{resolution_folder}/Return.jpg''',True,50)
    if bad_flag:
      return None
    else:
      if location:
        x,y = location
        l_click_py(x,y+10)
        sleep(1)
        l_click_py(int(1094*s_x),int(836*s_y))
        sleep(1)
        keyboard_f1()
        sleep(1)
        return None
      else:
        return None

def Huscar():
  keyboard_f2()
  sleep(1)
  keyboard_f2()
  sleep(2)
  mouse_safe()
  log('Кликаем на хускара')
  if bot_running:
    return None
  else:
    l_click_py(int(1419*s_x),int(840*s_y))
    sleep(1)
    l_click_py(int(1090*s_x),int(830*s_y))
    sleep(1)
    mouse_and_keyboard(int(1236*s_x),int(635*s_y))
    sleep(1)
    wait_for_image(f'''images/{resolution_folder}/Stone/Huskar.jpg''',False,150,0.9)
    sleep(10)
    screen = take_screenshot()
    types = {'green':('Green.jpg',green_stone),'yellow':('Yellow.jpg',yellow_stone),'purple':('Purple.jpg',purple_stone),'totem':('Totem.jpg',totem_stone),'Moneta':('Moneta.jpg', 0)}
    found_rewards = []
    for name,filename,priority in types.items():
      image_path = f'''images/{resolution_folder}/Stone/{filename}'''
      image = Image.open(image_path)
      coords = find_images_on_screen_2(screen,image,False,0.9)
      for coord in coords:
        found_rewards.append((coord[0],coord[1],name,priority))
        continue

      continue

    found_rewards.sort(key=lambda x: x[3],reverse=True)
    log(f'''Найдено наград: {len(found_rewards)} — собираем по приоритету''')
    for coord_x,coord_y,name,prio in found_rewards:
      l_click_py(int(coord_x),int(coord_y))
      sleep(0.3)
      continue

    log('Выходим с арена хускара')
    l_click_py(int(1279*s_x),int(1153*s_y))
    sleep(3)
    keyboard_f2()
    keyboard_f1()
    return None

def Mars():
  in_game = False
  to_restart = 0
  keyboard_f2()
  sleep(1)
  keyboard_f2()
  sleep(2)
  mouse_safe()
  log('Кликаем на марса')
  if bot_running:
    return None
  else:
    l_click_py(int(2054*s_x),int(867*s_y))
    sleep(1)
    if arena_flag:
      l_click_py(int(1455*s_x),int(888*s_y))

    sleep(1)
    l_click_py(int(1800*s_x),int(900*s_y))
    if bot_running:
      return None
    else:
      for o in range(29):
        location = None
        if bot_running:
          break

        sleep(1)
        mouse_and_keyboard(int(457*s_x),int(1243*s_y))
        sleep(1)
        wait_for_image(f'''images/{resolution_folder}/Arena.jpg''',False,50,0.9)
        if bad_flag:
          break

        if bot_running:
          break

        location = None
        if random_arena_flag:
          if rainbow_flag:
            if int(item_sel) == 3:
              choice = read_from_screen(region1=(int(372*s_x),int(932*s_y),int(980*s_x),int(1328*s_y)),region2=(int(1064*s_x),int(932*s_y),int(1672*s_x),int(1328*s_y)),region3=(int(1756*s_x),int(932*s_y),int(2364*s_x),int(1328*s_y)))
            else:
              choice = read_from_screen(region1=(int(712*s_x),int(932*s_y),int(1316*s_x),int(1328*s_y)),region2=(int(1412*s_x),int(932*s_y),int(2016*s_x),int(1328*s_y)))
              if rainbow_flag:
                location = wait_for_image(f'''images/{resolution_folder}/Atribut.jpg''',True,1,0.93)
                if location:
                  x,y = location
                  if int(item_sel) == 3:
                    if x < 1000*s_x:
                      choice = 1
                    else:
                      if x < 1756*s_x:
                        choice = 2
                      else:
                        if x < 2400*s_x:
                          choice = 3
                        else:
                          choice = 0
                          if x < 1400*s_x:
                            choice = 1
                          else:
                            if x < 2100*s_x:
                              choice = 2
                            else:
                              choice = 0
                              choice = 0
                              choice = 1

  location = wait_for_image(f'''images/{resolution_folder}/Return.jpg''',True,5)
  if location:
    x,y = location
    l_click_py(x,y+10)
    sleep(1)
    location = wait_for_image(f'''images/{resolution_folder}/restart.jpg''',True,5)
    if location:
      x,y = location
      l_click_py(x+100*s_x,y+30*s_y)
      return None
    else:
      return None

  else:
    l_click_py(int(1269*s_x),int(395*s_y))
    sleep(1)
    l_click_py(int(1082*s_x),int(832*s_y))
    return None

def pick_item(pos,count=-1):
  log('')
  log('==============')
  log('')
  if int(item_sel) == 3:
    if pos == 1:
      log(f'''{count}: Берем левую''')
      take_screenshot(region1=(int(372*s_x),int(320*s_y),int(2364*s_x),int(1328*s_y)),path=f'''игра{counter}_выбор{count}_L.png''')
      l_click_py(int(650*s_x),int(700*s_y))
    else:
      if pos == 2:
        log(f'''{count}: Берем центральную''')
        take_screenshot(region1=(int(372*s_x),int(320*s_y),int(2364*s_x),int(1328*s_y)),path=f'''игра{counter}_выбор{count}_M.png''')
        l_click_py(int(1350*s_x),int(700*s_y))
      else:
        if pos == 3:
          log(f'''{count}: Берем правую''')
          take_screenshot(region1=(int(372*s_x),int(320*s_y),int(2364*s_x),int(1328*s_y)),path=f'''игра{counter}_выбор{count}_R.png''')
          l_click_py(int(2050*s_x),int(700*s_y))
        else:
          log('Кликаем крестик')
          take_screenshot(region1=(int(372*s_x),int(320*s_y),int(2364*s_x),int(1328*s_y)),path=f'''игра{counter}_выбор{count}_SKIP.png''')
          l_click_py(int(2500*s_x),int(297*s_y))
          if pos == 1:
            log(f'''{count}: Берем левую''')
            take_screenshot(region1=(int(713*s_x),int(320*s_y),int(2016*s_x),int(1328*s_y)),path=f'''игра{counter}_выбор{count}_L.png''')
            l_click_py(int(1000*s_x),int(700*s_y))
          else:
            if pos == 2:
              log(f'''{count}: Берем правую''')
              take_screenshot(region1=(int(713*s_x),int(320*s_y),int(2016*s_x),int(1328*s_y)),path=f'''игра{counter}_выбор{count}_R.png''')
              l_click_py(int(1700*s_x),int(700*s_y))
            else:
              log('Кликаем крестик')
              take_screenshot(region1=(int(713*s_x),int(320*s_y),int(2016*s_x),int(1328*s_y)),path=f'''игра{counter}_выбор{count}_SKIP.png''')
              l_click_py(int(2142*s_x),int(312*s_y))

  log('')
  log('==============')
  log('')
  return None

def Auto_lose():
  if bot_running:
    if authorization:
      log('🔁 Выполняется действие бота...')
      sleep(1)
      start(1)
      time.sleep(12)
      log('Юзаем сундук')
      location = wait_for_image(f'''images/{resolution_folder}/Chest.jpg''')
      if location:
        x,y = location
        l_click_py(x,y)

      sleep(2)
      log('ожидаем 5 минут')
      time.sleep(2)
      if bot_running:
        return None
      else:
        for o in range(250):
          sleep(1)
          continue

        log('кликаем на афк')
        r_click_py(int(1755*s_x),int(1120*s_y))
        if bot_running:
          return None
        else:
          log('Ждём конец игры')
          wait_for_image(f'''images/{resolution_folder}/End.png''',False,120,0.9)
          if bad_flag:
            sleep(1)
            log('Кликаем подтвердить окно отчета')
            l_click_py(int(1285*s_x),int(1088*s_y))
            time.sleep(1)
            restart()
            counter += 1
          else:
            restart()
            bad_flag = False

          if bot_running:
            if authorization:
              pass

            return None
          else:
            return None

    else:
      return None

  else:
    return None

def start(dificculty):
  thread_close = True
  thread_end = False
  thread_skills = True
  thread_challenge = True
  investment_lvl = 0
  challenge_lvl = 0
  active_skills = {}
  already_refresh = 0
  skills_done = False
  slots = 0
  Grenate_use = False
  Moon_use = False
  desolator = False
  desolator_up = False
  daedalus = False
  daedalus_up = False
  abyss = False
  butterfly = False
  link = False
  aeon = False
  trident = False
  gleip = False
  gleip_up = False
  radiance = False
  parasma = False
  parasma_up = False
  dagon = False
  dagon_up = False
  eul = False
  eul_up = False
  eul_up2 = False
  log('Загружаю выбранные навыки')
  initial_selected = set(load_selected_skills())
  skill_states = {}
  for name in initial_selected:
    if name in ability_registry:
      continue

    data = ability_registry[name]
    skill_states[name] = {'index':data['index'],'name':name,'set':data['set'],'replace':data['replace']}
    continue

  log(f'''Загруженные навыки: {skill_states}''')
  mouse_safe()
  if already_start:
    log('жмём начать игру')
    if bot_running:
      return None
    else:
      location = wait_for_image(f'''images/{resolution_folder}/update.jpg''',True,3)
      if location:
        l_click_py(location[0],location[1])
        sleep(5)

      l_click_py(int(1863*s_x),int(1080*s_y))
      location = wait_for_image(f'''images/{resolution_folder}/Play.jpg''',True,100)
      if location:
        l_click_py(location[0]+200*s_x,location[1])

      log('ждём принять игру')
      location = wait_for_image(f'''images/{resolution_folder}/Accept.jpg''',True,20)
      if location:
        l_click_py(location[0],location[1]+10)
        location = wait_for_image(f'''images/{resolution_folder}/Accept.jpg''',True,1)
        if location:
          pass

      return None
      'ждём прогрузки игры'

  location = wait_for_image(f'''images/{resolution_folder}/Start.jpg''',False,120,0.9)
  if location == None:
    if bad_flag:
      if already_start:
        already_start = False
        restart(True)
        sleep(1)
        start(dificculty)
        return None
      else:
        l_click_py(int(1272*s_x),int(772*s_y))
        time.sleep(1)
        if bot_running:
          return None
        else:
          l_click_py(int(1272*s_x),int(772*s_y))
          time.sleep(1)
          if bot_running:
            return None
          else:
            l_click_py(int(1272*s_x),int(800*s_y))
            time.sleep(1)
            if bot_running:
              return None
            else:
              l_click_py(int(1272*s_x),int(800*s_y))
              time.sleep(1)
              if bot_running:
                return None
              else:
                log('❌ Не удалось найти стартовый экран. Выходим из Dota 2...')
                l_click_py(int(2518*s_x),int(50*s_y))
                time.sleep(2)
                l_click_py(int(1145*s_x),int(780*s_y))
                time.sleep(200)
                for attempt in range(99999):
                  dota_running = False
                  for proc in psutil.process_iter(['name']):
                    try:
                      if 'dota2' in proc.info['name'].lower():
                        dota_running = True
                        log if bot_running else __CHAOS_PY_NULL_PTR_VALUE_ERR__
                        break

                    except (psutil.NoSuchProcess,psutil.AccessDenied):
                      subprocess.run('start steam://run/570',shell=True)

                    continue

                  if dota_running:
                    print(f'''✅ Dota 2 запущена на попытке {attempt+1}.''')
                    sleep(15)
                    for i in range(50):
                      my_hwnd = win32gui.FindWindow(None,'Dota 2')
                      location = wait_for_image(f'''images/{resolution_folder}/Arcade.jpg''',False,1,0.9)
                      if location:
                        continue

                      __CHAOS_PY_NULL_PTR_VALUE_ERR__ if location else __CHAOS_PY_NULL_PTR_VALUE_ERR__
                      break

                    break

                  if attempt%5 == 0:
                    print(f'''🔁 Попытка запуска Steam (попытка {attempt+1})...''')
                    subprocess.run('start steam://run/570',shell=True)

                  time.sleep(3)
                  continue
                else:
                  print('❌ Dota 2 не была запущена после 30 попыток.')
                  return None

                bad_flag = False
                l_click_py(int(1486*s_x),int(43*s_y))
                sleep(1)
                l_click_py(int(2172*s_x),int(121*s_y))
                sleep(1)
                pyperclip.copy('Дота-Рейнджер')
                sleep(0.5)
                keyboard.press_and_release('ctrl+v')
                sleep(2)
                l_click_py(int(2211*s_x),int(196*s_y))
                sleep(2)

    start(int(dificculty))
    return None
  else:
    log('Меняем сложность')
    if bot_running:
      return None
    else:
      if already_start:
        l_click_py(int(1615*s_x),int(1080*s_y))
        time.sleep(1)

      if bot_running:
        return None
      else:
        if __CHAOS_PY_NULL_PTR_VALUE_ERR__ > dificculty:
          if dificculty < 20:
            if bot_running:
              return None
            else:
              if already_start:
                l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                sleep(1)

              l_click_py(int(1300*s_x),int(385+70*dificculty-10*s_y))

          else:
            if dificculty >= 20:
              if dificculty < 30:
                if bot_running:
                  return None
                else:
                  if already_start:
                    l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                    sleep(1)
                    l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                    sleep(1)

                  l_click_py(int(1300*s_x),int(385+70*dificculty-20*s_y))

              else:
                if dificculty >= 30:
                  if dificculty < 39:
                    if bot_running:
                      return None
                    else:
                      if already_start:
                        l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                        sleep(1)
                        l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                        sleep(1)
                        l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                        sleep(1)

                      l_click_py(int(1300*s_x),int(385+70*dificculty-29*s_y))

                  else:
                    if dificculty >= 39:
                      if dificculty < 48:
                        if already_start:
                          l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                          sleep(1)
                          l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                          sleep(1)
                          l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                          sleep(1)
                          l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                          sleep(1)

                        l_click_py(int(1300*s_x),int(385+70*dificculty-39*s_y))
                      else:
                        if dificculty >= 48:
                          if already_start:
                            l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                            sleep(1)
                            l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                            sleep(1)
                            l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                            sleep(1)
                            l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                            sleep(1)
                            l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                            sleep(1)

                          l_click_py(int(1300*s_x),int(385+70*dificculty-46*s_y))
                        else:
                          l_click_py(int(1300*s_x),int(385+70*dificculty-1*s_y))

    if (resolution_folder == 2560 and 10) > dificculty:
      if dificculty < 20:
        if bot_running:
          return None
        else:
          if already_start:
            l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
            sleep(1)

          l_click_py(int(1300*s_x),int(385+70*dificculty-10*s_y))

      else:
        if dificculty >= 20:
          if dificculty < 29:
            if bot_running:
              return None
            else:
              if already_start:
                l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                sleep(1)
                l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                sleep(1)

              l_click_py(int(1300*s_x),int(385+70*dificculty-19*s_y))

          else:
            if dificculty >= 29:
              if dificculty < 38:
                if bot_running:
                  return None
                else:
                  if already_start:
                    l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                    sleep(1)
                    l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                    sleep(1)
                    l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                    sleep(1)

                  l_click_py(int(1300*s_x),int(385+70*dificculty-28*s_y))

              else:
                if dificculty >= 38:
                  if dificculty < 46:
                    if already_start:
                      l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                      sleep(1)
                      l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                      sleep(1)
                      l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                      sleep(1)
                      l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                      sleep(1)

                    l_click_py(int(1300*s_x),int(385+70*dificculty-37*s_y))
                  else:
                    if dificculty >= 46:
                      if already_start:
                        l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                        sleep(1)
                        l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                        sleep(1)
                        l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                        sleep(1)
                        l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                        sleep(1)
                        l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
                        sleep(1)

                      l_click_py(int(1300*s_x),int(385+70*dificculty-46*s_y))
                    else:
                      l_click_py(int(1300*s_x),int(385+70*dificculty-1*s_y))

  time.sleep(1)
  log('стартуем игру')
  if bot_running:
    return None
  else:
    l_click_py(int(2300*s_x),int(1300*s_y))
    already_start = False
    return None

def restart(hard=True):
  if hard:
    if bot_running:
      return None
    else:
      log('Кликаем выйти в главное меню Доты')
      l_click_py(int(40*s_x),int(35*s_y))
      time.sleep(3)
      if bot_running:
        return None
      else:
        log('Кликаем отключится')
        location = wait_for_image(f'''images/{resolution_folder}/Play.jpg''',True,1)
        if location:
          l_click_py(int(2250*s_x),int(1280*s_y))
          if bot_running:
            return None
          else:
            location2 = wait_for_image(f'''images/{resolution_folder}/Error.jpg''',True,1)
            if location2:
              l_click_py(location2[0]+20,location2[1]+10)

            location = wait_for_image(f'''images/{resolution_folder}/Play.jpg''',True,1)
            if location:
              pass

        return None

  else:
    mouse_safe()
    keyboard_f2()
    keyboard_f2()
    sleep(0.5)
    keyboard_f1()
    keyboard_f1()
    sleep(1)
    move_down(200*s_y)
    l_click_py(int(1453*s_x),int(909*s_y))
    log('Выходим')
    location = wait_for_image(f'''images/{resolution_folder}/restart.jpg''',True,4)
    if bad_flag:
      restart(True)
      return None
    else:
      if location:
        x,y = location
        l_click_py(x+100*s_x,y+30*s_y)
        already_start = True

      return None

def test():
  import subprocess
  investment_lvl = 0
  challenge_lvl = 0
  active_skills = {}
  already_refresh = 0
  skills_done = False
  slots = 0
  Grenate_use = False
  Moon_use = False
  desolator = False
  desolator_up = False
  daedalus = False
  daedalus_up = False
  abyss = False
  butterfly = False
  link = False
  aeon = False
  trident = False
  gleip = False
  gleip_up = False
  radiance = False
  parasma = False
  parasma_up = False
  dagon = False
  dagon_up = False
  eul = False
  eul_up = False
  eul_up2 = False
  if len(active_skills) < 5:
    slots = check_slots()
    active_skills = {i: None for i in range(slots)}

  if bot_running:
    if authorization:
      slots = check_slots()
      active_skills = {i: None for i in range(slots)}
      start_time = time.time()
      l_click_t(int(1273*s_x),int(937*s_y),int(-950*s_y))
      sleep(3)
      return None
      pass
      if authorization:
        pass

      return None
      return None
    else:
      return None

  else:
    return None

def run_bot_toggle():
  bot_running = not(bot_running)
  counter = 1
  item_counter = 1
  __CHAOS_PY_NULL_PTR_VALUE_ERR__,__CHAOS_PY_NULL_PTR_VALUE_ERR__ = get_scale()
  if selected_resolution.get() == '1920x1080':
    resolution_folder = 1920
  else:
    resolution_folder = 2560

  my_hwnd = win32gui.FindWindow(None,'Dota 2')
  if bot_running:
    if authorization:
      in_game = False
      log('✅ Бот ЗАПУЩЕН!')
      if mode.get() == 'Фарм фейт т7 (сл5)':
        threading.Thread(target=FarmT7,daemon=True).start()

      if mode.get() == 'Фарм ключей автолуз':
        threading.Thread(target=Auto_lose,daemon=True).start()

      if mode.get() == 'Тест кода (для разработчиков)':
        threading.Thread(target=test,daemon=True).start()
        return None
      else:
        return None

  else:
    log('🛑 Бот ОСТАНОВЛЕН.')
    return None

def pause_bot_toggle():
  if bot_running:
    log('⚠ Бот не запущен — нечего ставить на паузу.')
    return None
  else:
    bot_paused = not(bot_paused)
    if bot_paused:
      log('⏸ Бот ПРИОСТАНОВЛЕН.')
      return None
    else:
      log('▶ Бот ПРОДОЛЖЕН.')
      return None

def wait_if_paused(delay=0.5):
  if bot_paused:
    if bot_running:
      time.sleep(delay)
      if bot_paused:
        if bot_running:
          pass

        return None
      else:
        return None

    else:
      return None

  else:
    return None

def start_hotkey_listener():
  key = bot_start_key.get()
  pause_key = bot_pause_key.get()
  if key:
    log('⛔ Клавиша запуска не задана.')
    return None
  else:
    log(f'''⌨ Ожидание клавиши \'{key}\' для ВКЛ/ВЫКЛ бота...''')
    pass
    try:
      keyboard.remove_hotkey(key)
    except:
      pass
    except:
      pass

    try:
      keyboard.remove_hotkey(pause_key)
      keyboard.add_hotkey(key,run_bot_toggle)
      keyboard.add_hotkey(pause_key,pause_bot_toggle)
      keyboard.wait()
      return None
    except:
      pass
    except Exception as e:
      log(f'''❌ Ошибка добавления горячей клавиши: {e}''')
      log('👉 Запусти программу от имени администратора.')
      return None

def create_ui():
  window = tk.Tk()
  window.title('Настройки бота')
  window.geometry('400x850')
  def save_settings(file):
    settings = {'selected_resolution':selected_resolution.get(),'mode':mode.get(),'bot_start_key':bot_start_key.get(),'bot_pause_key':bot_pause_key.get(),'difficulty_num':difficulty_num.get()}
    with open(f'''config/{file}.json''','w',encoding='utf-8') as f:
      json.dump(settings,f,ensure_ascii=False,indent=4)

    return None

  def load_settings(file):
    if os.path.exists(f'''config/{file}.json'''):
      with open(f'''config/{file}.json''','r',encoding='utf-8') as f:
        return json.load(f)
        return {}

  def show_authorization_window(parent):
    CONFIG_DIR = 'config'
    KEY_FILE = os.path.join(CONFIG_DIR,'key.txt')
    def get_hardware_id():
      username = getpass.getuser()
      computer = platform.node()
      raw_id = f'''{username}-{computer}'''
      mac = uuid.getnode()
      hwid = hashlib.sha256(raw_id.encode()).hexdigest()
      return hwid

    def save_key_to_file(key):
      os.makedirs(CONFIG_DIR,exist_ok=True)
      with open(KEY_FILE,'w',encoding='utf-8') as f:
        f.write(key)

      return None

    auth_win = tk.Toplevel(parent)
    auth_win.title('Авторизация')
    auth_win.geometry('450x250')
    auth_win.grab_set()
    hwid = get_hardware_id()
    ttk.Label(auth_win,text='ID устройства (HWID):').pack(pady=5)
    hwid_entry = ttk.Entry(auth_win,width=64)
    hwid_entry.insert(0,hwid)
    hwid_entry.config(state='readonly')
    hwid_entry.pack(pady=5)
    def copy_hwid_to_clipboard():
      auth_win.clipboard_clear()
      auth_win.clipboard_append(hwid)
      auth_win.update()
      messagebox.showinfo('HWID','ID устройства скопирован в буфер обмена')
      return None

    copy_hwid_btn = ttk.Button(auth_win,text='Скопировать ID устройства',command=copy_hwid_to_clipboard)
    copy_hwid_btn.pack(pady=5)
    ttk.Label(auth_win,text='Введите ключ авторизации:').pack(pady=5)
    user_key = tk.StringVar()
    key_entry = ttk.Entry(auth_win,textvariable=user_key,width=64)
    key_entry.pack(pady=5)
    def paste_key_from_clipboard():
      try:
        clip = auth_win.clipboard_get().strip()
        user_key.set(clip)
        return None
      except:
        messagebox.showerror('Ошибка','Буфер обмена пуст или содержит некорректные данные')

      return None

    paste_key_btn = ttk.Button(auth_win,text='Вставить ключ из буфера',command=paste_key_from_clipboard)
    paste_key_btn.pack(pady=5)
    def on_submit():
      key = user_key.get().strip()
      if key:
        messagebox.showwarning('Ошибка','Введите ключ!')
        return None
      else:
        save_key_to_file(key)
        check_key()
        auth_win.destroy()
        return None

    submit_btn = ttk.Button(auth_win,text='Подтвердить',command=on_submit)
    submit_btn.pack(pady=10)
    return None

  def check_key():
    CONFIG_DIR = 'config'
    KEY_FILE = os.path.join(CONFIG_DIR,'key.txt')
    try:
      with open(KEY_FILE,'r',encoding='utf-8') as f:
        key = f.read().strip()

    except Exception:
      subscription_status.set('Не авторизован (ключ не найден)')
      authorization = False
      return None

    if key:
      subscription_status.set('Не авторизован (ключ пустой)')
      authorization = False
      return None
    else:
      def get_hardware_id():
        username = getpass.getuser()
        computer = platform.node()
        raw_id = f'''{username}-{computer}'''
        mac = uuid.getnode()
        hwid = hashlib.sha256(raw_id.encode()).hexdigest()
        return hwid

      current_hwid = get_hardware_id()
      try:
        url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL1NhcmNhc21EZXYvbGFiNi1lZHVjYXRpb24vcmVmcy9oZWFkcy9tYXN0ZXIvYXBpLmpzb24='
        response = requests.get(base64.b64decode(url).decode('utf-8'),timeout=5)
        if response.status_code != 200:
          authorization = False
          subscription_status.set('Ошибка проверки ключа (нет связи)')
          return None
        else:
          data = response.json()
          if key not in data:
            authorization = False
            subscription_status.set('Не авторизован (ключ не найден в базе)')
            return None
          else:
            key_data = data[key]
            hwid_from_server = key_data.get('hwid','')
            expires_str = key_data.get('expires','')
            if hwid_from_server != current_hwid:
              authorization = False
              subscription_status.set('Не авторизован (hwid не совпадает)')
              return None
            else:
              expires_date = datetime.datetime.strptime(expires_str,'%Y-%m-%d %H:%M:%S')
              now = datetime.datetime.now()
              if expires_date < now:
                authorization = False
                subscription_status.set('Подписка истекла')
                return None
              else:
                authorization = True
                subscription_status.set(f'''Авторизован. Действует до {expires_str}''')
                return None

      except Exception as e:
        subscription_status.set('Ошибка проверки')
        return None

  def check_authorization():
    pass
    check_key()
    sleep(300)

  def show_image_in_new_window():
    filepath = 'images/tmp/coffe.jpg'
    if os.path.exists(filepath):
      print('Файл не найден:',filepath)
      return None
    else:
      try:
        img = Image.open(filepath)
        img = img.resize((400, 400))
        photo = ImageTk.PhotoImage(img)
        img_window = tk.Toplevel(window)
        img_window.title('Просмотр изображения')
        label_text = ttk.Label(img_window,text='Вот ваш вкуснейший кофе',font=('Arial', 14))
        label_text.pack(pady=(10, 5))
        label_img = ttk.Label(img_window,image=photo)
        label_img.image = photo
        label_img.pack(padx=10,pady=10)
        return None
      except Exception as e:
        print('Ошибка при открытии изображения:',e)
        return None

  auth_button = ttk.Button(window,text='Авторизация',command=lambda : show_authorization_window(window))
  auth_button.pack(pady=(10, 0))
  img_button = ttk.Button(window,text='Отправить умному чайнику команду сварить кофе',command=show_image_in_new_window)
  img_button.pack(pady=(10, 0))
  subscription_status = tk.StringVar(value='Проверка авторизации...')
  status_label = ttk.Label(window,textvariable=subscription_status,foreground='green')
  status_label.pack(pady=(5, 10))
  threading.Thread(target=check_authorization,daemon=True).start()
  loaded = load_settings('settings')
  selected_resolution = tk.StringVar(value=loaded.get('selected_resolution','2560x1440'))
  mode = tk.StringVar(value=loaded.get('mode','Фарм фейт т7 (сл5)'))
  bot_start_key = tk.StringVar(value=loaded.get('bot_start_key','f6'))
  bot_pause_key = tk.StringVar(value=loaded.get('bot_pause_key','f8'))
  difficulty_num = tk.StringVar(value=loaded.get('difficulty_num','5'))
  ttk.Label(window,text='Выберите разрешение экрана:').pack(pady=5)
  resolution_dropdown = ttk.Combobox(window,textvariable=selected_resolution,values=['2560x1440','1920x1080'],state='readonly')
  resolution_dropdown.pack(pady=5)
  ttk.Label(window,text='Режим игры:').pack(pady=5)
  mode_dropdown = ttk.Combobox(window,textvariable=mode,values=['Фарм фейт т7 (сл5)','Фарм ключей автолуз','Тест кода (для разработчиков)'],state='readonly')
  mode_dropdown.pack(pady=5)
  ttk.Label(window,text='Клавиша запуска бота:').pack(pady=5)
  key_entry2 = ttk.Entry(window,textvariable=bot_start_key)
  key_entry2.pack(pady=5)
  ttk.Label(window,text='Клавиша паузы бота:').pack(pady=5)
  key_entry2 = ttk.Entry(window,textvariable=bot_pause_key)
  key_entry2.pack(pady=5)
  ttk.Label(window,text='Сложность для фарма т7: 1-50').pack(pady=5)
  key_entry2 = ttk.Entry(window,textvariable=difficulty_num)
  key_entry2.pack(pady=5)
  status_label = ttk.Label(window,text='',foreground='green')
  status_label.pack(pady=10)
  def set_fields_state(state):
    resolution_dropdown.configure(state=state)
    key_entry2.configure(state=state)
    mode_dropdown.configure(state=state)
    return None

  def on_submit():
    difficulty = difficulty_num.get()
    print(f'''окно :{my_hwnd}''')
    log(f'''📐 Разрешение: {selected_resolution.get()}''')
    log(f'''🖱 Режим игры: {mode.get()}''')
    log(f'''▶ Клавиша запуска бота: {bot_start_key.get()}''')
    save_settings('settings')
    print(talent_search)
    print('===========================')
    print(fate_search)
    print(' ==========================')
    print(str(fate_flag)+' --- '+str(talent_flag)+' --- '+str(random_fate_flag)+' --- '+str(random_talent_flag)+' --- '+str(huscar_flag))
    print('===========================')
    print(f'''Выбор из: {item_sel}, Выбираем шмоток: {item_pick}''')
    set_fields_state('disabled')
    submit_button.configure(state='disabled')
    edit_button.configure(state='normal')
    status_label.config(text=f'''Нажмите \'{bot_start_key.get()}\' для запуска/остановки бота.''')
    threading.Thread(target=start_hotkey_listener,daemon=True).start()
    return None

  def on_edit():
    set_fields_state('readonly')
    resolution_dropdown.configure(state='readonly')
    key_entry2.configure(state='normal')
    mode_dropdown.configure(state='normal')
    submit_button.configure(state='normal')
    edit_button.configure(state='disabled')
    status_label.config(text='Редактирование настроек...')
    return None

  def update_counter_label():
    counter_var.set(str(counter))
    window.after(1000,update_counter_label)
    return None

  def open_talent_input():
    def open_text_input(filename,label):
      def save():
        text = text_widget.get('1.0',tk.END).strip()
        with open(f'''config/{filename}''','w',encoding='utf-8') as f:
          __CHAOS_PY_PASS_ERR__
        f.write(text)
        None(None,None)
        popup.destroy()
        return None

      popup = tk.Toplevel(window)
      popup.title(label)
      popup.geometry('400x300')
      text_widget = tk.Text(popup,height=6,wrap='word')
      text_widget.pack(padx=10,pady=5,fill='both',expand=True)
      if os.path.exists(f'''config/{filename}'''):
        with open(f'''config/{filename}''','r',encoding='utf-8') as f:
          text_widget.insert('1.0',f.read())

      ttk.Button(popup,text='Сохранить',command=save).pack(pady=10)
      return None

    def prepare_vars():
      def on_var_change(name):
        if bool_vars[name].get():
          skill_states[name] = ability_registry[name]
          return None
        else:
          if name in skill_states:
            del(skill_states[name])
            return None
          else:
            return None

      selected_names = set(load_selected_skills())
      skill_states = {name: ability_registry[name] for name in selected_names if name in ability_registry}
      bool_vars = {}
      for name in ability_registry:
        var = tk.BooleanVar(value=name in skill_states)
        'write'({'n':name},lambda : on_var_change(n))
        bool_vars[name] = var
        continue

      return None

    def open_skill_selection_window():
      prepare_vars()
      selection_window = tk.Toplevel(window)
      selection_window.title('Выбор навыков')
      canvas = tk.Canvas(selection_window)
      scrollbar = ttk.Scrollbar(selection_window,orient='vertical',command=canvas.yview)
      scroll_frame = ttk.Frame(canvas)
      scroll_frame.bind('<Configure>',lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
      canvas.create_window((0, 0),window=scroll_frame,anchor='nw')
      canvas.configure(yscrollcommand=scrollbar.set)
      canvas.pack(side='left',fill='both',expand=True)
      scrollbar.pack(side='right',fill='y')
      for name in ability_registry.keys():
        cb = ttk.Checkbutton(scroll_frame,text=name,variable=bool_vars[name])
        cb.pack(anchor='w',padx=10,pady=2)
        continue

      def on_close():
        save_selected_skills()
        selection_window.destroy()
        return None

      ttk.Button(selection_window,text='OK',command=on_close).pack(pady=10)
      return None

    def open_priority_list_with_mapping(filename,window_title,mapping,global_var_name):
      import os
      popup = tk.Toplevel()
      popup.title(window_title)
      popup.geometry('300x400')
      listbox = tk.Listbox(popup,selectmode=tk.SINGLE,activestyle='dotbox')
      listbox.pack(fill='both',expand=True,padx=10,pady=10)
      filepath = f'''config/{filename}'''
      saved_values = []
      if (os.path.exists(filepath) and 0):
        saved_values = list(mapping.values())
        with open(filepath,'w',encoding='utf-8') as f:
          f.write(', '.join(saved_values))

      else:
        with open(filepath,'r',encoding='utf-8') as f:
          content = f.read()

        None(None,None)

      for val in saved_values:
        if val in reverse_map:
          continue

        listbox.insert(tk.END,reverse_map[val])
        continue
        {v.lower(): k for k,v in mapping.items()}

      for display_name in mapping.keys():
        if display_name not in listbox.get(0,tk.END):
          continue

        listbox.insert(tk.END,display_name)
        continue

      def move_up():
        sel = listbox.curselection()
        if sel:
          if sel[0] > 0:
            idx = sel[0]
            item = listbox.get(idx)
            listbox.delete(idx)
            listbox.insert(idx-1,item)
            listbox.selection_set(idx-1)
            return None
          else:
            return None

        else:
          return None

      def move_down():
        sel = listbox.curselection()
        if sel:
          if sel[0] < listbox.size()-1:
            idx = sel[0]
            item = listbox.get(idx)
            listbox.delete(idx)
            listbox.insert(idx+1,item)
            listbox.selection_set(idx+1)
            return None
          else:
            return None

        else:
          return None

      def save_and_close():
        ordered_keys = listbox.get(0,tk.END)
        globals()[global_var_name] = ordered_values
        with open(filepath,'w',encoding='utf-8') as f:
          f.write(', '.join(ordered_values))

        popup.destroy()
        return None

      btn_frame = ttk.Frame(popup)
      btn_frame.pack(pady=5)
      ttk.Button(btn_frame,text='Вверх',command=move_up).pack(side='left',padx=5)
      ttk.Button(btn_frame,text='Вниз',command=move_down).pack(side='left',padx=5)
      ttk.Button(btn_frame,text='Сохранить и закрыть',command=save_and_close).pack(side='left',padx=5)
      return None

    def save_checkboxes():
      filters = blue_gem_flag_var.get()
      os.makedirs('config',exist_ok=True)
      with open('config/filters.json','w',encoding='utf-8') as f:
        json.dump(filters,f,ensure_ascii=False,indent=2)

      fate_flag = only_useful_var.get()
      talent_flag = only_talents_var.get()
      random_fate_flag = random_fate_var.get()
      random_talent_flag = random_talent_var.get()
      huscar_flag = huscar_var.get()
      item_sel = int(item_sel_var.get())
      item_pick = int(item_pick_var.get())
      arena_flag = arena_flag_var.get()
      heroes_flag = heroes_flag_var.get()
      push_flag = push_flag_var.get()
      random_arena_flag = random_arena_flag_var.get()
      hero_pick = int(hero_pick_var.get())
      chalenge_up_flag = chalenge_up_flag_var.get()
      chalenge_flag = chalenge_flag_var.get()
      gem_flag = gem_flag_var.get()
      blue_gem_flag = blue_gem_flag_var.get()
      purple_gem_flag = purple_gem_flag_var.get()
      orange_gem_flag = orange_gem_flag_var.get()
      build_mag = build_mag_var.get()
      build_phys = build_phys_var.get()
      build_eff = build_eff_var.get()
      green_stone = int(green_stone_var.get())
      purple_stone = int(purple_stone_var.get())
      yellow_stone = int(yellow_stone_var.get())
      totem_stone = int(totem_stone_var.get())
      investment_target = int(investment_target_var.get())
      buy_itms = buy_itms_var.get()
      arena_skip = int(arena_skip_var.get())
      skills_state = skills_var.get()
      rainbow_flag = rainbow_flag_var.get()
      refresh_count = int(refresh_count_var.get())
      input_window.destroy()
      return None

    input_window = tk.Toplevel(window)
    input_window.title('Настройки поиска')
    input_window.geometry('900x1050')
    container = ttk.Frame(input_window)
    container.pack(fill='both',expand=True)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container,orient='vertical',command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind('<Configure>',lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.create_window((0, 0),window=scrollable_frame,anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side='left',fill='both',expand=True)
    scrollbar.pack(side='right',fill='y')
    only_useful_var = tk.BooleanVar()
    only_talents_var = tk.BooleanVar()
    random_fate_var = tk.BooleanVar()
    random_talent_var = tk.BooleanVar()
    rainbow_flag_var = tk.BooleanVar()
    huscar_var = tk.BooleanVar()
    item_sel_var = tk.StringVar()
    item_pick_var = tk.StringVar()
    arena_flag_var = tk.BooleanVar()
    heroes_flag_var = tk.BooleanVar()
    push_flag_var = tk.BooleanVar()
    random_arena_flag_var = tk.BooleanVar()
    hero_pick_var = tk.StringVar()
    chalenge_up_flag_var = tk.BooleanVar()
    chalenge_flag_var = tk.BooleanVar()
    gem_flag_var = tk.BooleanVar()
    blue_gem_flag_var = tk.BooleanVar()
    purple_gem_flag_var = tk.BooleanVar()
    orange_gem_flag_var = tk.BooleanVar()
    build_mag_var = tk.BooleanVar()
    build_phys_var = tk.BooleanVar()
    build_eff_var = tk.BooleanVar()
    green_stone_var = tk.StringVar()
    yellow_stone_var = tk.StringVar()
    purple_stone_var = tk.StringVar()
    totem_stone_var = tk.StringVar()
    investment_target_var = tk.StringVar()
    buy_itms_var = tk.BooleanVar()
    arena_skip_var = tk.StringVar()
    skills_var = tk.BooleanVar()
    refresh_count_var = tk.StringVar()
    if os.path.exists('config/filters.json'):
      with open('config/filters.json','r',encoding='utf-8') as f:
        saved_filters = json.load(f)
        only_useful_var.set(saved_filters.get('only_useful_fate',False))
        only_talents_var.set(saved_filters.get('only_talents',False))
        random_fate_var.set(saved_filters.get('random_fate',False))
        random_talent_var.set(saved_filters.get('random_talent',False))
        huscar_var.set(saved_filters.get('huscar_farm',False))
        item_sel_var.set(saved_filters.get('item_sel',False))
        item_pick_var.set(saved_filters.get('item_pick',False))
        arena_flag_var.set(saved_filters.get('arena_flag',False))
        heroes_flag_var.set(saved_filters.get('heroes_flag',False))
        push_flag_var.set(saved_filters.get('push_flag',False))
        random_arena_flag_var.set(saved_filters.get('random_arena_flag',False))
        hero_pick_var.set(saved_filters.get('hero_pick',False))
        chalenge_up_flag_var.set(saved_filters.get('chalenge_up',False))
        chalenge_flag_var.set(saved_filters.get('chalenge',False))
        gem_flag_var.set(saved_filters.get('gem',False))
        blue_gem_flag_var.set(saved_filters.get('blue_gem',False))
        purple_gem_flag_var.set(saved_filters.get('purple_gem',False))
        orange_gem_flag_var.set(saved_filters.get('orange_gem',False))
        build_mag_var.set(saved_filters.get('build_mag',False))
        build_phys_var.set(saved_filters.get('build_phys',False))
        build_eff_var.set(saved_filters.get('build_eff',False))
        green_stone_var.set(saved_filters.get('green_stone',False))
        purple_stone_var.set(saved_filters.get('purple_stone',False))
        yellow_stone_var.set(saved_filters.get('yellow_stone',False))
        totem_stone_var.set(saved_filters.get('totem_stone',False))
        investment_target_var.set(saved_filters.get('inv_target',False))
        buy_itms_var.set(saved_filters.get('buy_items',False))
        arena_skip_var.set(saved_filters.get('arena_skip',False))
        skills_var.set(saved_filters.get('skills_state',False))
        rainbow_flag_var.set(saved_filters.get('rainbow',False))
        refresh_count_var.set(saved_filters.get('refresh_count',False))

    arena_frame = ttk.LabelFrame(scrollable_frame,text='Арена')
    arena_frame.pack(padx=10,pady=10,fill='x')
    row1 = ttk.Frame(arena_frame)
    row1.pack(anchor='center',pady=5)
    ttk.Checkbutton(row1,text='Нужные фейты (т6–7)',variable=only_useful_var).grid(row=0,column=0,sticky='w',padx=5)
    ttk.Checkbutton(row1,text='Нужные таланты (все Т)',variable=only_talents_var).grid(row=0,column=1,sticky='w',padx=5)
    ttk.Checkbutton(row1,text='Рандомный фейт (т6-7)',variable=random_fate_var).grid(row=0,column=2,sticky='w',padx=5)
    ttk.Checkbutton(row1,text='Рандомный талант (т7)',variable=random_talent_var).grid(row=0,column=3,sticky='w',padx=5)
    row2 = ttk.Frame(arena_frame)
    row2.pack(anchor='center',pady=5)
    ttk.Button(row2,text='Искомые фейты',command=lambda : open_text_input('feats.txt','Искомые фейты')).grid(row=0,column=0,padx=10)
    ttk.Button(row2,text='Искомые таланты',command=lambda : open_text_input('talents.txt','Искомые таланты')).grid(row=0,column=1,padx=10)
    row3 = ttk.Frame(arena_frame)
    row3.pack(anchor='center',pady=5)
    ttk.Label(row3,text='Арена, выбор из:').pack(side='left',padx=5)
    ttk.Entry(row3,textvariable=item_sel_var,width=5).pack(side='left',padx=5)
    ttk.Label(row3,text='Арена, забираем шмоток:').pack(side='left',padx=10)
    ttk.Entry(row3,textvariable=item_pick_var,width=5).pack(side='left',padx=10)
    ttk.Label(row3,text='Скипаем первые n этажей:').pack(side='left',padx=15)
    ttk.Entry(row3,textvariable=arena_skip_var,width=5).pack(side='left',padx=15)
    row4 = ttk.Frame(arena_frame)
    row4.pack(anchor='center',pady=5)
    ttk.Checkbutton(row4,text='Арена - повышенная',variable=arena_flag_var).pack(side='left',padx=5)
    ttk.Label(row4,text='Боссы жирнее, зибараем шмоток +1 (необходимо указать в поле ввода выше на 1 предмет больше)').pack(side='left',padx=5)
    row5 = ttk.Frame(arena_frame)
    row5.pack(anchor='center',pady=5)
    ttk.Checkbutton(row5,text='Арена - спидран?',variable=random_arena_flag_var).pack(side='left',padx=5)
    ttk.Label(row5,text='Забираем первые n шмоток с арены и рестарт (n - количество указанное в поле \'Арена, забираем шмоток\')').pack(side='left',padx=5)
    row6 = ttk.Frame(arena_frame)
    row6.pack(anchor='center',pady=5)
    ttk.Checkbutton(row6,text='Пуш?',variable=push_flag_var).pack(side='left',padx=5)
    ttk.Label(row6,text='Прокачка кодекса, рекомендую отключить \'Фарм монеток(хускар)\' и включить \'Арена спидран\'').pack(side='left',padx=5)
    row7 = ttk.Frame(arena_frame)
    row7.pack(anchor='center',pady=5)
    ttk.Checkbutton(row7,text='Цветные и красные шмотки на голдишко',variable=rainbow_flag_var).pack(side='left',padx=5)
    ttk.Label(row7,text='Арена спидран выключай!!!!!!! и \'Скипаем этажей\' ставь = 0').pack(side='left',padx=5)
    huska_frame = ttk.LabelFrame(scrollable_frame,text='Батл Рояль')
    huska_frame.pack(padx=10,pady=10,fill='x')
    row1 = ttk.Frame(huska_frame)
    row1.pack(anchor='center',pady=5)
    ttk.Checkbutton(row1,text='Батл Рояль',variable=huscar_var).pack(side='left',padx=5)
    row2 = ttk.Frame(huska_frame)
    row2.pack(anchor='center',pady=5)
    ttk.Label(row2,text='Зеленые точки:').pack(side='left',padx=10)
    ttk.Entry(row2,textvariable=green_stone_var,width=5).pack(side='left',padx=10)
    ttk.Label(row2,text='Желтые точки:').pack(side='left',padx=10)
    ttk.Entry(row2,textvariable=yellow_stone_var,width=5).pack(side='left',padx=10)
    ttk.Label(row2,text='Фиолетовые точки:').pack(side='left',padx=10)
    ttk.Entry(row2,textvariable=purple_stone_var,width=5).pack(side='left',padx=10)
    ttk.Label(row2,text='Тотем точки:').pack(side='left',padx=10)
    ttk.Entry(row2,textvariable=totem_stone_var,width=5).pack(side='left',padx=10)
    row3 = ttk.Frame(huska_frame)
    row3.pack(anchor='center',pady=5)
    ttk.Label(row3,text='''Введите числа приоритета для камней, 10 - высший приоритет, 0 - низший приоритет, сначало заберёт ВСЕ с высшим приоритет и на уменьшение

Зеленые - рерол атрибутов
Желтые - точка уровня
Фиолетовые - рерол чисел атрибутов''').pack(side='left',padx=5)
    hero_frame = ttk.LabelFrame(scrollable_frame,text='Герои')
    hero_frame.pack(padx=10,pady=10,fill='x')
    row1 = ttk.Frame(hero_frame)
    row1.pack(anchor='center',pady=5)
    ttk.Checkbutton(row1,text='Качаем героев?',variable=heroes_flag_var).pack(side='left',padx=5)
    ttk.Label(row1,text='Герои, выбор из:').pack(side='left',padx=10)
    ttk.Entry(row1,textvariable=hero_pick_var,width=5).pack(side='left',padx=10)
    ttk.Button(row1,text='Герои для прокачки',command=lambda : open_text_input('heroes.txt','Герои для прокачки')).pack(side='left',padx=10)
    chalenge_frame = ttk.LabelFrame(scrollable_frame,text='Челеджи')
    chalenge_frame.pack(padx=10,pady=10,fill='x')
    row1 = ttk.Frame(chalenge_frame)
    row1.pack(anchor='center',pady=5)
    ttk.Checkbutton(row1,text='Прокачка челеджей',variable=chalenge_up_flag_var).pack(side='left',padx=5)
    ttk.Checkbutton(row1,text='Вызов челеджей',variable=chalenge_flag_var).pack(side='left',padx=5)
    gem_frame = ttk.LabelFrame(scrollable_frame,text='Гемы')
    gem_frame.pack(padx=10,pady=10,fill='x')
    row1 = ttk.Frame(gem_frame)
    row1.pack(anchor='center',pady=5)
    ttk.Checkbutton(row1,text='Омни гемы',variable=gem_flag_var).pack(side='left',padx=5)
    ttk.Checkbutton(row1,text='Синие гемы',variable=blue_gem_flag_var).pack(side='left',padx=5)
    ttk.Checkbutton(row1,text='Фиолетовые гемы',variable=purple_gem_flag_var).pack(side='left',padx=5)
    ttk.Checkbutton(row1,text='Оранжевые гемы',variable=orange_gem_flag_var).pack(side='left',padx=5)
    row2 = ttk.Frame(gem_frame)
    row2.pack(anchor='center',pady=5)
    ttk.Button(row2,text='Искомые синие гемы',command=lambda : open_priority_list_with_mapping('Blue_gem.txt','Искомые синие гемы',blue_gem_all,'Blue_search')).grid(row=0,column=0,padx=10)
    ttk.Button(row2,text='Искомые фиолетовые гемы',command=lambda : open_priority_list_with_mapping('Purple_gem.txt','Искомые фиолетовые гемы',purple_gem_all,'Purple_search')).grid(row=0,column=1,padx=10)
    row3 = ttk.Frame(gem_frame)
    row3.pack(anchor='center',pady=5)
    ttk.Label(row3,text='Если введеные статы в геме не найдены, выберется стат в первой строке, !!!!ВСЕ СТАТЫ МОЖНО ПОСМОТРЕТЬ В CONFIG/ALL!!!!').pack(side='left',padx=5)
    build_frame = ttk.LabelFrame(scrollable_frame,text='Билд')
    build_frame.pack(padx=10,pady=10,fill='x')
    row1 = ttk.Frame(build_frame)
    row1.pack(anchor='center',pady=5)
    ttk.Checkbutton(row1,text='Маг',variable=build_mag_var).pack(side='left',padx=5)
    ttk.Checkbutton(row1,text='Физ',variable=build_phys_var).pack(side='left',padx=5)
    ttk.Checkbutton(row1,text='Эффект',variable=build_eff_var).pack(side='left',padx=5)
    row2 = ttk.Frame(build_frame)
    row2.pack(anchor='center',pady=5)
    ttk.Label(row2,text='Галочку ставьте только на один билд если не хотите ничего запороть себе (от этого зависит какую шмотку бот купит перед убийством Рошана)').pack(side='left',padx=5)
    row3 = ttk.Frame(build_frame)
    row3.pack(anchor='center',pady=5)
    ttk.Checkbutton(row3,text='Покупаем предметы',variable=buy_itms_var).pack(side='left',padx=5)
    ttk.Label(row3,text='Качаем Q Инвест до (0 - не качаем):').pack(side='left',padx=10)
    ttk.Entry(row3,textvariable=investment_target_var,width=5).pack(side='left',padx=10)
    W_frame = ttk.LabelFrame(scrollable_frame,text='Дабалью Дабалью')
    W_frame.pack(padx=10,pady=10,fill='x')
    row1 = ttk.Frame(W_frame)
    row1.pack(anchor='center',pady=5)
    ttk.Checkbutton(row1,text='Вкл/Выкл',variable=skills_var).pack(side='left',padx=5)
    ttk.Button(row1,text='Выбрать навыки',command=open_skill_selection_window).pack(side='left',pady=10)
    ttk.Label(row1,text='Количество реролов:').pack(side='left',padx=15)
    ttk.Entry(row1,textvariable=refresh_count_var,width=5).pack(side='left',padx=15)
    ttk.Button(input_window,text='Сохранить фильтры',command=save_checkboxes).pack(pady=5)
    desc_text = tk.StringVar()
    desc_text.set('''Если выбраны:
1) «Нужные фейты» — ищем только фейты из списка \'Искомые фейты\' выше - приоритетнее (т6–7)
2) «Нужные таланты» — ищем только таланты из списка \'Искомые таланты\' выше - приоритетнее (все Т)
3) «Рандомный фейт» — любой фейт т6-7 без фильтра, 
приоритет ниже если вместе с галочкой \'рандомный талант\'
4) «Рандомный талант» — любой талант т7 без фильтра, 
приоритет выше если вместе с галочкой \'рандомный фейт
\'5) Фарм монеток(хускара) - ботинок зафармит батл рояль и выберет монетки
''')
    desc_label = tk.Label(scrollable_frame,textvariable=desc_text,background='#f0f0f0',anchor='center',justify='center')
    desc_label.pack(fill='x',padx=10,pady=(5, 10))
    return None

  talents_button = ttk.Button(window,text='Настройки поиска',command=open_talent_input)
  talents_button.pack(pady=5)
  submit_button = ttk.Button(window,text='Сохранить',command=on_submit)
  submit_button.pack(pady=10)
  edit_button = ttk.Button(window,text='Редактировать',command=on_edit)
  edit_button.pack(pady=5)
  edit_button.configure(state='disabled')
  counter_frame = ttk.Frame(window)
  counter_frame.pack(side=tk.RIGHT,fill=tk.Y,padx=10,pady=10)
  ttk.Label(counter_frame,text='Счётчик:').pack(pady=(0, 5))
  counter_var = tk.StringVar(value='0')
  counter_label = ttk.Label(counter_frame,textvariable=counter_var,background='#e0e0e0',width=10,anchor='center')
  counter_label.pack()
  frame = ttk.Frame(window)
  frame.pack(fill=tk.BOTH,expand=True,padx=10,pady=10)
  log_text_widget = tk.Text(frame,height=10,wrap=tk.WORD,state='disabled',bg='#f0f0f0')
  scrollbar = ttk.Scrollbar(frame,orient='vertical',command=log_text_widget.yview)
  log_text_widget.configure(yscrollcommand=scrollbar.set)
  scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
  log_text_widget.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
  initial_selected = set(load_selected_skills())
  skill_states = {}
  for name in initial_selected:
    if name in ability_registry:
      continue

    data = ability_registry[name]
    skill_states[name] = {'index':data['index'],'name':name,'set':data['set'],'replace':data['replace']}
    continue

  talent_search = []
  fate_search = []
  if os.path.exists('config/talents.txt'):
    with open('config/talents.txt','r',encoding='utf-8') as f:
      content = f.read().lower()

    talent_search = [tal.strip()() for tal in content.split(',')]
    None(None,None)

  if os.path.exists('config/feats.txt'):
    with open('config/feats.txt','r',encoding='utf-8') as f:
      content = f.read().lower()

    fate_search = [tal.strip()() for tal in content.split(',')]
    None(None,None)

  if os.path.exists('config/heroes.txt'):
    with open('config/heroes.txt','r',encoding='utf-8') as f:
      content = f.read().lower()

    heroes = [tal.strip()() for tal in content.split(',')]
    None(None,None)

  if os.path.exists('config/Blue_gem.txt'):
    with open('config/Blue_gem.txt','r',encoding='utf-8') as f:
      content = f.read().lower()

    Blue_search = [tal.strip()() for tal in content.split(',')]
    None(None,None)

  if os.path.exists('config/Purple_gem.txt'):
    with open('config/Purple_gem.txt','r',encoding='utf-8') as f:
      content = f.read().lower()

    Purple_search = [tal.strip()() for tal in content.split(',')]
    None(None,None)

  loaded = load_settings('filters')
  fate_flag = loaded.get('only_useful_fate',False)
  talent_flag = loaded.get('only_talents',False)
  random_fate_flag = loaded.get('random_fate',False)
  random_talent_flag = loaded.get('random_talent',False)
  rainbow_flag = loaded.get('rainbow',False)
  huscar_flag = loaded.get('huscar_farm',False)
  item_sel = int(loaded.get('item_sel',False))
  item_pick = int(loaded.get('item_pick',False))
  investment_target = int(loaded.get('inv_target',False))
  arena_flag = loaded.get('arena_flag',False)
  heroes_flag = loaded.get('heroes_flag',False)
  push_flag = loaded.get('push_flag',False)
  random_arena_flag = loaded.get('random_arena_flag',False)
  hero_pick = int(loaded.get('hero_pick',False))
  chalenge_up_flag = loaded.get('chalenge_up',False)
  chalenge_flag = loaded.get('chalenge',False)
  gem_flag = loaded.get('gem',False)
  blue_gem_flag = loaded.get('blue_gem',False)
  purple_gem_flag = loaded.get('purple_gem',False)
  orange_gem_flag = loaded.get('orange_gem',False)
  build_mag = loaded.get('build_mag',False)
  build_phys = loaded.get('build_phys',False)
  build_eff = loaded.get('build_eff',False)
  green_stone = int(loaded.get('green_stone',False))
  purple_stone = int(loaded.get('purple_stone',False))
  yellow_stone = int(loaded.get('yellow_stone',False))
  totem_stone = int(loaded.get('totem_stone',False))
  buy_itms = loaded.get('buy_items',False)
  arena_skip = int(loaded.get('arena_skip',False))
  skills_state = loaded.get('skills_state',False)
  refresh_count = int(loaded.get('refresh_count',False))
  update_counter_label()
  window.mainloop()
  return None

def load_selected_skills(path='config/skills.json'):
  if os.path.exists(path):
    return []
  else:
    with open(path,'r') as f:
      return json.load(f)

def save_selected_skills(path='config/skills.json'):
  with open(path,'w') as f:
    json.dump(selected_names,f,indent=2)

  return None

if __name__ == '__main__':
  create_ui()
else:
  pass

