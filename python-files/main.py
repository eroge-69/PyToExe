import cmu_graphics
import time

from cmu_graphics import *

app.stepsPerSecond = 400
app.width=1366
app.height=768
width = app.width
height = app.height
width50 = width/2
height50 = height/2

app.background='gray'

# fire
fire = Star(width50, height50, 540, 500, fill='yellow', visible=False)
busrtDebug = Rect(0, 0, 20, 20, fill='red')

# gun
pointer = Star(width50, height50, 10, 100, fill='red')
gun1 = RegularPolygon(width50, height50+320, 20+50, 10)
gun2 = RegularPolygon(width50, height50+300, 70+50, 10)
gun3 = RegularPolygon(width50, height50+290, 60+50, 10)
gun4 = RegularPolygon(width50, height50+245, 50+50, 10)

def shootBurst():
    if (fire.visible == True):
        fire.visible=False
    elif (fire.visible == False):
        fire.visible=True

def onStep():
    if (busrtDebug.fill == 'green'):
        shootBurst()
    elif (busrtDebug.fill == 'red'):
        fire.visible=False

def onMouseMove(x, y):
    fire.centerX=x
    fire.centerY=y
    pointer.centerX=((y-180))+x/2  
    pointer.centerY=(y/2)-y/10
    gun1.centerX=x
    gun1.centerY=y
    gun2.centerX=(-x)+width
    gun2.centerY=(-y)+(width-100) 
    gun3.centerX=(width-(x+340))+x/2
    gun3.centerY=(height-y)+470
    gun3.centerX=(width-(x+340))+x/2
    gun3.centerY=(height-(y-180))+y/2    

def onMouseDrag(x, y):
    fire.centerX=x
    fire.centerY=y
    pointer.centerX=(x/2)+width50/2
    pointer.centerY=(y/2)-y/10
    gun1.centerX=x
    gun1.centerY=y
    gun2.centerX=(-x)+width
    gun2.centerY=(-y)+(width-100) 
    gun3.centerX=(width-(x+340))+x/2
    gun3.centerY=(height-y)+470
    gun3.centerX=(width-(x+340))+x/2
    gun3.centerY=(height-(y-180))+y/2    

def onMousePress(x, y):
    busrtDebug.fill='green'

def onMouseRelease(x, y):
    busrtDebug.fill='red'
    fire.visible=False

cmu_graphics.run()