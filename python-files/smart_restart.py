from keyboard import add_hotkey, send
from pygetwindow import getActiveWindow
import pyautogui
import time
import os

exit_button_1080 = 'images/exit_button_1080.png'
start_lsb_1080 = 'images/start_lsb_1080.png'
ok_button_1080 = 'images/ok_button_1080.png'
update_button_1080 = 'images/update_button_1080.png'

errors_count = 0
exit_button_count = 0

def imageFind(path, pathType='string', grayscale=False):
  if pathType == 'string':
    try:
      point = pyautogui.locateOnScreen(path, confidence=0.8, grayscale=grayscale)
      if point:
        return point
    except Exception as e:
      pyautogui.sleep(0.1)
      #print('Error not found', path, e)
  elif pathType == 'list':
    array = list(Path(path).iterdir())
    for val in array:
      try:
        pathReady = str(val).replace('\\', '/')
        point = pyautogui.locateOnScreen(pathReady, confidence=0.8, grayscale=grayscale)
        if point:
          return point
      except Exception as e:
        #print('Error not found', val, e)
        continue

if not os.path.exists("LSB.exe"):
  print("LSB.exe not found. Please rename file and restart program.")
  pyautogui.sleep(10)
  os.sys.exit(1)
if not os.path.exists(exit_button_1080):
  print("exit_button_1080.png not found. Please put file and restart program.")
  pyautogui.sleep(10)
  os.sys.exit(1)
if not os.path.exists(start_lsb_1080):
  print("start_lsb_1080.png not found. Please put file and restart program.")
  pyautogui.sleep(10)
  os.sys.exit(1)
if not os.path.exists(ok_button_1080):
  print("ok_button_1080.png not found. Please put file and restart program.")
  pyautogui.sleep(10)
  os.sys.exit(1)

while True: 
  try:
    if not pyautogui.getWindowsWithTitle('Dota 2'):
      # Пытаемся все закрыть
      send('shift + f2')
      pyautogui.sleep(1)
      print("Dota 2 is closed: Restart game")
      os.system('taskkill /f /im "dota2.exe"')  # либо тут закрылись
      # Открыть бота
      os.startfile('LSB.exe')
      pyautogui.sleep(5)
      # Клацаем "Start"
      print("Start LSB and tap start button")
      start_lsb_button = imageFind(start_lsb_1080, grayscale=True)
      start_lsb_button_center = pyautogui.center(start_lsb_button)
      pyautogui.click(start_lsb_button)
      pyautogui.sleep(25)
    else:
      if imageFind(exit_button_1080, grayscale=True):
        exit_button_count += 1

        print("FOUND exit_button_1080")
        # Если появилась ошибка "Отключение от сервера"
        if imageFind(ok_button_1080, grayscale=True):    
          print("DISCONNECTED")
          errors_count += 1  
          print("restart_count: ", errors_count)
          # С задержкой закрываем LSB
          pyautogui.sleep(1)
          send('shift + f2')
          pyautogui.sleep(1)
          # Закрываем игру
          print("Disconneted: Restart game")
          os.system('taskkill /f /im "dota2.exe"') # либо тут закрылись
          # Даем ПК осознать че произошло
          pyautogui.sleep(15)

        # Обновляем кастомку, если требуется
        update_button = imageFind(update_button_1080, grayscale=True)
        if update_button:
          print("UPDATE")
          print("Download new version of Last Survivors")
          pyautogui.click(update_button)
          pyautogui.sleep(120) # Даем время кастомке обновиться 

        # Если долго находимся в главном меню доты - пытаемся все закрыть для холодного перезапуска
        print("try exit_button_count", exit_button_count)
        if exit_button_count == 2:
          print("DONE exit_button_count", exit_button_count)
          send('shift + f2')
          pyautogui.sleep(1)
          print("Dota 2 is stuck: Restart game")
          os.system('taskkill /f /im "dota2.exe"') # либо тут закрылись
          exit_button_count = 0

  except Exception as e:
    #print("Произошла ошибка", e)
    time.sleep(60) 
    continue
  
  # Проверку осуществляем раз в какое-то время
  time.sleep(60)