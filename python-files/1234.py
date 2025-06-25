import pyautogui as pg
import time
pg.hotkey('winleft')
time.sleep(0.4)
pg.typewrite("edge\n")
pg.typewrite(['enter'])
time.sleep(0.4)
pg.hotkey('winleft', 'up')
time.sleep(0.4)
pg.typewrite('https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1\n')
time.sleep(1.5)
pg.press('space')