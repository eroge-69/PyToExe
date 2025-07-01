import pyautogui as pag
import time as t

browser_position = (984, 1179)



def open_browser():
    pag.click(browser_position)
    t.sleep(2)

def open_tab():
    pag.hotkey('ctrl', 't')

def write_url(url):
    pag.typewrite(url)
    pag.press('enter')

url = 'https://www.youtube.com/watch?v=YlUKcNNmywk'
