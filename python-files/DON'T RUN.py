import pyautogui as pg
import os
 
pg.moveTo(x=612, y=594)
pg.confirm("hello bro")
pg.confirm("lets have some fun")

pg.keyDown("win")
pg.press("r")
pg.keyUp("WIN")

pg.typewrite("cmd")
pg.press("enter")

pg.sleep(1)

pg.typewrite("systeminfo")
pg.press("enter")
pg.sleep(2)
pg.typewrite("ipconfig/all")
pg.press("enter")
pg.sleep(5)
pg.typewrite("exit()")
pg.press("enter")

pg.press("win")
pg.typewrite("edge")
pg.sleep(1.5)
pg.typewrite("How to be not so cringe??")
pg.sleep(5)


pg.keyDown("alt")
pg.press("F4")
pg.keyUp("alt")

pg.alert("good night brother")
os.system("shutdown /s")

exit()











