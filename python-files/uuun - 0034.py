import keyboard
import os
import time
 
p0 = ['欢迎','开始','退出']
p1 = ['主页','队列1','队列2','返回']
p2 = ['队列1','t1','t2','t3','t4','返回']
p3 = ['队列2','t1','t2','t3','返回']
p = 0
s = 1

def stp(pg,st,ap):
    for i in pg:
        if ap == st:
           print('>'+i)
        else:
           print(' '+i)
        ap = ap + 1

def srf(pnl,sn):
    if sn < 1:
        sn = 1
    if sn >= len(pnl):
        sn = len(pnl) - 1
    return sn

while True:
    if p == 0:
        s = srf(p0,s)
        stp(p0,s,0)
    if p == 1:
        s = srf(p1,s)
        stp(p1,s,0)
    if p == 2:
        s = srf(p2,s)
        stp(p2,s,0)
    if p == 3:
        s = srf(p3,s)
        stp(p3,s,0)
    time.sleep(0)

    while True:
        if keyboard.is_pressed('up'):
            s -= 1
            break
        if keyboard.is_pressed('down'):
            s += 1
            break
        if keyboard.is_pressed('space'):
            if p == 0:
                if s == 1:
                    p = 1
                    break
                if s == 2:
                    exit()
            if p == 1:
                if s == 1:
                    p = 2
                    break
                if s == 2:
                    p = 3
                    break
                if s == 3:
                    p = 0
                    break
            if p == 2:
                if s == 5:
                    p = 1
                    break
            if p == 3:
                if s== 4:
                    p = 1
                    break

        #if keyboard.is_pressed('right'):
        if keyboard.is_pressed('o'):
            exit()
    time.sleep(0.125)
    os.system('cls')

