import threading
from tkinter import *
from tkinter import ttk
import pyautogui



butt = ['butt_1','down','help','t5frider']

x=0
y='2'
z=1
e='start'

def se(butt,x,y):
    try:
        if(x==3):
            pyautogui.click()
            find = pyautogui.locateOnScreen('butt/down.png', confidence=0.8)
            if(find[0]):
                x=8
                return x

        else:
            butt="butt/"+butt+".png"
            find = pyautogui.locateOnScreen(butt, confidence=0.8)
            center = pyautogui.center(find)
        if(x==1):
            pyautogui.click(center)
            pyautogui.click(center[0]-100,center[1]-265)
            pyautogui.typewrite(y)
            pyautogui.click(center[0]-100,center[1]+120)
        else:
            pyautogui.click(center)
        x=1
    except:
        x=2
    finally:
        timer = threading.Timer(1, click_button).start()
        return x



root = Tk()
root.title("Doomsday: Health")
root.geometry('500x100+400+200')
root.resizable(False, False)
icon = PhotoImage(file = "butt/down.png")
root.iconphoto(False, icon)


def click_button():
        if e == 'finish': return
        text = ['Поиск раненых', 'Даем указания', 'Печатаем', 'Лечение ручками', '']
        global x,y,z
        if x < 4:
            find = se(butt[x], x, y)
            if find == 1: x += 1
            if find == 8: x = 1
        elif x == 4:
            x = 0
        btn["text"] = f'{text[x]}'
        btn["state"] = DISABLED
        print(text[x])

def finish():
    global e
    e = 'finish'
    root.destroy()

btn = ttk.Button(text="Старт лечения",command=click_button)
btn.pack(anchor=W,ipadx=10)
btn.place(relwidth=0.33, relheight=1)


root.protocol("WM_DELETE_WINDOW", finish)
root.mainloop()






