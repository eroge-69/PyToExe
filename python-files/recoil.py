import keyboard
import mouse
import tkinter as tk
from tkinter import messagebox
import screeninfo
import configparser
import os
import time
import threading
import ctypes
import ast


# Setting up config file and tkinter GUI
aimCheck = False

xValue = 0
yValue = 0
delayValue = 0

if os.path.isfile('config.txt') == False:
    print('config.txt file not found. Creating new one...')
    with open('config.txt', 'w') as fp:
        pass
    config = configparser.ConfigParser()
    config['hotkey'] = {'hotkey': 'p',}
    config['loadouts'] = {}
    config.write(open('config.txt', 'w'))
    input('Press any key to exit...')
    exit()
else:
    config = configparser.ConfigParser()
    config.read('config.txt')

try:
    hotkey = config['hotkey']['hotkey']
except:
    print('Hotkey not found, adding hotkey line to config file...')
    config = configparser.ConfigParser()
    config['hotkey'] = {'hotkey': 'p'}
    config['loadouts'] = {}
    config.write(open('config.txt', 'w'))
    input('Press any key to exit...')
    exit()

print('Hotkey is: ',hotkey)

def setValues():
    global xValue, yValue, delayValue
    xValue = xControl.get()
    yValue = yControl.get()
    delayValue = delay.get() 
    print(f"Values set - X:{xValue} Y:{yValue} D:{delayValue}")

def toggleAimCheck():
    global aimCheck
    if aimCheck:
        aimCheck = False
        aimCheckButton.config(text='Aim Check Off')
    else:
        aimCheck = True
        aimCheckButton.config(text='Aim Check On')
    
    
def getResolution():
    screens = screeninfo.get_monitors()
    primary_monitor = screens[0] 
    return primary_monitor.width, primary_monitor.height 

def saveLoadout():
    setValues()
    name = str(loadoutName.get())
    loadoutName.delete(0, tk.END)
    config = configparser.ConfigParser()
    config.read('config.txt')
    if not config.has_section('loadouts'):
        config.add_section('loadouts')
    config.set('loadouts', name, f'[{xValue},{yValue},{delayValue}]')
    config.write(open('config.txt', 'w'))
    
def loadLoadout():
    global xValue, yValue, delayValue
    setValues()
    name = str(loadoutName.get())
    loadoutName.delete(0, tk.END)
    config = configparser.ConfigParser()
    config.read('config.txt')

    try:
        loadout = config['loadouts'][name]
    except KeyError:
        messagebox.showwarning("Error", f"No loadout called {name}")
        return None
    
    loadoutList = ast.literal_eval(loadout)
    xValue = loadoutList[0]
    yValue = loadoutList[1]
    delayValue = loadoutList[2]

    xControl.set(loadoutList[0])
    yControl.set(loadoutList[1])
    delay.set(loadoutList[2])




gui = tk.Tk()
gui.title("Recoil Macro")

tk.Label(gui, text="").pack() 

aimCheckButton = tk.Button(gui, text="Aim Check Off", command=toggleAimCheck)
aimCheckButton.pack()

label = tk.Label(gui, text='X Control')
label.pack()

xControl = tk.Scale(gui, from_=-50, to=50, orient=tk.HORIZONTAL, length=200)
xControl.pack()

tk.Label(gui, text="").pack() 

label = tk.Label(gui, text='Y Control')
label.pack()

yControl = tk.Scale(gui, from_=0, to=100, orient=tk.VERTICAL, length=200)
yControl.pack()

tk.Label(gui, text="").pack() 

label = tk.Label(gui, text='Delay Between Movements (ms)')
label.pack()

delay = tk.Scale(gui, from_=1, to=50, orient=tk.HORIZONTAL, length=150)
delay.set(10)
delay.pack()

tk.Label(gui, text="").pack() 

setButton = tk.Button(gui, text="Set", command=setValues)
setButton.pack()

tk.Label(gui, text="").pack() 

tk.Label(gui, text=f'Press {hotkey} to start/stop macro.').pack()
tk.Label(gui, text='Check out config.txt to change hotkey and manually edit loadouts.').pack()

tk.Label(gui, text="").pack()

loadoutName = tk.Entry(gui)
loadoutName.pack()

saveButton = tk.Button(gui, text='Save Loadout', command=saveLoadout)
saveButton.pack()

loadButton = tk.Button(gui, text='Load Loadout', command=loadLoadout)
loadButton.pack()

x, y = getResolution()
width = int(x/5)
height = int(y/1.5)
gui.geometry(f'{width}x{height}')





# Start of macro code
enabled = False

def moveRel(x,y):
    currentX, currentY = mouse.get_position()
    newX = currentX + x
    newY = currentY + y
    ctypes.windll.user32.mouse_event(0x0001, x, y, 0, 0) 

def toggleMacro():
    global enabled
    if enabled:
        enabled = False
        print('Macro Disabled!')
        ctypes.windll.user32.MessageBeep(0x00000010) 
    else:
        enabled = True
        print('Macro Enabled!')
        ctypes.windll.user32.MessageBeep(0xFFFFFFFF) 

keyboard.add_hotkey(hotkey, toggleMacro)


# Functions determine whether or not mouse buttons are held down using windows api
def leftClicked():
    if ctypes.windll.user32.GetAsyncKeyState(0x01) != 0:
        return True
    else:
        return False
def rightClicked():
    if ctypes.windll.user32.GetAsyncKeyState(0x02) != 0:
        return True
    else:
        return False



# Main macro thread, handles all mouse controlling
def macroTask():
    while True:
        if enabled:
            if aimCheck == False and leftClicked():
                moveRel(xValue, yValue)
            elif aimCheck == True and leftClicked() and rightClicked():
                moveRel(xValue, yValue)
        time.sleep(delayValue / 1000)

thread = threading.Thread(target=macroTask)
thread.daemon = True
thread.start() 



# Start main GUI loop after starting non-blocking macro thread
gui.mainloop()