#
#    Continent generator
#

import random
from tkinter import *
from math import cos, sin, sqrt, radians



def SetLists(read):
    return None



def Default():
    #Sets default settings when default key is pressed.
    global tilesize, twidth, theight, chance, rnNoise
    tilesize = 1
    twidth = 800
    theight = 600
    chance = 40
    rnNoise = 2
    ma = 2
    ms = 2
    Create()



def Read():
    #This function reads the values of the "Set Variables" window
    inw = inwid.get("1.0",END)
    valid = True
    try:
        global twidth
        twidth = int(inw)
        if twidth < 1:
            inwid.delete("1.0",END)
            inwid.insert("1.0","Must Be > 0")
            valid = False
    except:
        inwid.delete("1.0",END)
        inwid.insert("1.0","Invalid Value")
        valid = False
    inh = inhgt.get("1.0",END)
    try:
        global theight
        theight = int(inh)
        if theight < 1:
            inhgt.delete("1.0",END)
            inhgt.insert("1.0","Must Be > 0")
            valid = False
    except:
        inhgt.delete("1.0",END)
        inhgt.insert("1.0","Invalid Value")
        valid = False
    inc = inchance.get("1.0",END)
    try:
        global chance
        chance = float(inc)
        if chance <= 15 or chance >= 85:
            inchance.delete("1.0",END)
            if chance <= 15:
                inchance.insert("1.0","Too Small")
            else:
                inchance.insert("1.0","Too Large")
            valid = False
    except:
        inchance.delete("1.0",END)
        inchance.insert("1.0","Invalid Value")
        valid = False
    intl = intile.get("1.0",END)
    try:
        global tilesize
        tilesize = int(intl)
        if tilesize < 1:
            intile.delete("1.0",END)
            intile.insert("1.0","Too Small")
            valid = False
    except:
        intile.delete("1.0",END)
        intile.insert("1.0","Invalid Value")
        valid = False
    in_ma = inma.get("1.0",END)
    try:
        global ma
        ma = int(in_ma)
        if ma <= 0:
            inma.delete("1.0",END)
            inma.insert("1.0","Too Small")
            valid = False
    except:
        inma.delete("1.0",END)
        inma.insert("1.0","Invalid Value")
        valid = False
    in_ms = inms.get("1.0",END)
    try:
        global ms
        ms = int(in_ms)
        if ms <= 0:
            inms.delete("1.0",END)
            inms.insert("1.0","Too Small")
            valid = False
    except:
        inms.delete("1.0",END)
        inms.insert("1.0","Invalid Value")
        valid = False
    inn = innoise.get("1.0",END)
    try:
        global rnNoise
        rnNoise = int(inn)
        if rnNoise < 0:
            innoise.delete("1.0",END)
            innoise.insert("1.0","Too Small")
            valid = False
    except:
        innoise.delete("1.0",END)
        innoise.insert("1.0","Invalid Value")
        valid = False
    root.update()
    if valid:
        Create()



def AddLin(start, end, lradius):
    #Finds the closest distance between current x and y value and a given point.
    global x, y
    if ((x > start[0] - lradius and x < end[0] + lradius) or (x > end[0] - lradius and x < start[0] + lradius)) and ((y > start[1] - lradius and y < end[1] + lradius) or (y > end[1] - lradius and y < start[1] + lradius)):
        try:
            slope = (end[1] - start[1]) / (end[0] - start[0])
        except:
            slope = None
        if slope != 0 and slope != None:
            close_x = (slope * start[0] + y + (x / slope) - start[1]) / (slope + (1 / slope))
            close_y = slope * (close_x - start[0]) + start[1]
            if (close_x < end[0] and close_x > start[0]) or (close_x < start[0] and close_x > end[0]):
                return max(0, lradius - sqrt((x - close_x) ** 2 + (y - close_y) ** 2)) / lradius
            else:
                return max(AddCirc(end[0], end[1], lradius), AddCirc(start[0], start[1], lradius))
        elif slope == 0:
            return max(0, lradius - sqrt(x ** 2 + (y - start[1]) ** 2)) / lradius
        else:
            return max(0, lradius - sqrt((x - start[0]) ** 2 + y ** 2)) / lradius
    else:
        return 0



def AddCirc(centx, centy, radius):
    global x, y
    if x > centx - radius and x < centx + radius and y > centy - radius and y < centy + radius:
        return max(0, radius - sqrt((x - centx) ** 2 + (y - centy) ** 2)) / radius
    else:
        return 0



def AddACirc(centerx, centery, radius, AorS):
    adder = (centerx, centery, radius)
    if AorS == False:
        if centery - radius < theight / 2:
            if centerx - radius < twidth / 2:
                CircSub3.append(adder)
            if centerx + radius >= twidth / 2:
                CircSub4.append(adder)
        if centery + radius >= theight / 2:
            if centerx - radius < twidth / 2:
                CircSub2.append(adder)
            if centerx + radius >= twidth / 2:
                CircSub1.append(adder)
    else:
        if centery - radius < theight / 2:
            if centerx - radius < twidth / 2:
                CircAdd3.append(adder)
            if centerx + radius >= twidth / 2:
                CircAdd4.append(adder)
        if centery + radius >= theight / 2:
            if centerx - radius < twidth / 2:
                CircAdd2.append(adder)
            if centerx + radius >= twidth / 2:
                CircAdd1.append(adder)



def AddALin(start, end, radius, AorS):
    adder = (start, end, radius)
    if AorS == False:
        if start[1] - radius < theight / 2 or end[1] - radius < theight / 2:
            if start[0] - radius < twidth / 2 or end[0] - radius < twidth / 2:
                LinSub3.append(adder)
            if start[0] + radius >= twidth / 2 or end[0] + radius >= twidth / 2:
                LinSub4.append(adder)
        if start[1] + radius >= theight / 2 or end[1] + radius >= theight / 2:
            if start[0] - radius < twidth / 2 or end[0] - radius < twidth / 2:
                LinSub2.append(adder)
            if start[0] + radius >= twidth / 2 or end[0] + radius >= twidth / 2:
                LinSub1.append(adder)
    else:
        if start[1] - radius < theight / 2 or end[1] - radius < theight / 2:
            if start[0] - radius < twidth / 2 or end[0] - radius < twidth / 2:
                LinAdd3.append(adder)
            if start[0] + radius >= twidth / 2 or end[0] + radius >= twidth / 2:
                LinAdd4.append(adder)
        if start[1] + radius >= theight / 2 or end[1] + radius >= theight / 2:
            if start[0] - radius < twidth / 2 or end[0] - radius < twidth / 2:
                LinAdd2.append(adder)
            if start[0] + radius >= twidth / 2 or end[0] + radius >= twidth / 2:
                LinAdd1.append(adder)



def CreateOcean():
    centerx = random.randint(0, twidth)
    centery = random.randint(0, theight)
    again = 1
    while again > 0.2:
        for i in range(random.randint(3, 6)):
            deez = random.uniform(0,6.283)
            dis = random.uniform(30, 50)
            AddACirc(centerx + cos(deez) * dis, centery + sin(deez) * dis, random.randint(25,50), False)
        again = random.random()
        centerx += cos(deez) * dis
        centery += sin(deez) * dis




def CreatePlain():
    centerx = random.randint(0, twidth)
    centery = random.randint(0, theight)
    again = 1
    while again > 0.2:
        for i in range(random.randint(3,8)):
            deez = random.uniform(0,6.283)
            dis = random.uniform(5, 20)
            AddACirc(centerx + cos(deez) * dis, centery + sin(deez) * dis, random.randint(20, 50) + int(sqrt(chance)), True)
        again = random.random()
        centerx += cos(deez) * dis
        centery += sin(deez) * dis


def CreateRiver():
    addir = random.randint(1,360)
    putx = random.randint(1, twidth)
    puty = random.randint(1, theight)
    nextx = max(-25, min(twidth + 25, putx + random.uniform(-20,20)))
    nexty = max(-25, min(theight + 25, puty + random.uniform(-20,20)))
    for i in range(random.randint(4,23)):
        dis = random.randint(10,40)
        AddALin((putx, puty), (nextx, nexty), random.randint(5,20), False)
        putx, nextx = nextx, max(-25, min(twidth + 25, nextx + dis * cos(radians(addir))))
        puty, nexty = nexty, max(-25, min(theight + 25, nexty + dis * sin(radians(addir))))
        addir += random.randint(-20,20)



def CreateMRange():
    addir = random.randint(1,360)
    putx = random.randint(1, twidth)
    puty = random.randint(1, theight)
    nextx = max(-25, min(twidth + 25, putx + random.uniform(-15,15)))
    nexty = max(-25, min(theight + 25, puty + random.randint(-15,15)))
    for i in range(random.randint(4,10)):
        dis = random.randint(5,30)
        addir += random.randint(-20,20)
        radius = random.randint(10,25)
        AddALin((putx, puty), (nextx, nexty), random.randint(10,25), True)
        AddACirc(putx, puty, random.randint(10, 35), True)
        putx, nextx = nextx, max(-25, min(twidth + 25, nextx + dis * cos(radians(addir))))
        puty, nexty = nexty, max(-25, min(theight + 25, nexty + dis * sin(radians(addir))))



def CreateNoise(iters):
    global noiseA, noiseS
    for itr in range(iters, 0, -1):
        for r in range(random.randint(int(amount/100/iters * rnNoise), int(amount/70/iters * rnNoise))):
            addnoise = (random.randint(0,twidth), random.randint(0,theight), random.uniform(13/itr,20/itr), itr)
            if addnoise[1] - addnoise[2] < theight / 2:
                if addnoise[0] - addnoise[2] < twidth / 2:
                    NoiseA3.append(addnoise)
                if addnoise[0] + addnoise[2] >= twidth / 2:
                    NoiseA4.append(addnoise)
            if addnoise[1] + addnoise[2] >= theight / 2:
                if addnoise[0] - addnoise[2] < twidth / 2:
                    NoiseA2.append(addnoise)
                if addnoise[0] + addnoise[2] >= twidth / 2:
                    NoiseA1.append(addnoise)
            addnoise = (random.randint(0,twidth), random.randint(0,theight), random.uniform(13/itr,20/itr), itr)
            if addnoise[1] - addnoise[2] < theight / 2:
                if addnoise[0] - addnoise[2] < twidth / 2:
                    NoiseS3.append(addnoise)
                if addnoise[0] + addnoise[2] >= twidth / 2:
                    NoiseS4.append(addnoise)
            if addnoise[1] + addnoise[2] >= theight / 2:
                if addnoise[0] - addnoise[2] < twidth / 2:
                    NoiseS2.append(addnoise)
                if addnoise[0] + addnoise[2] >= twidth / 2:
                    NoiseS1.append(addnoise)


def Create():
    global chance, screen, mod, amount, x, y
    intile.destroy()
    default.destroy()
    temp.destroy()
    inchance.destroy()
    inwid.destroy()
    inhgt.destroy()
    intile.destroy()
    fin.destroy()
    inms.destroy()
    inma.destroy()
    innoise.destroy()
    amount = twidth * theight
    root.title("Continent Generator")
    chance *= 1.15
    screen = Canvas(root, width = tilesize * twidth, height = tilesize * theight)
    screen.pack()
    root.update_idletasks()
    root.update()
    ms = 2
    ma = 2
    for i in range(random.randint(int(ms * (amount / 90000) * (100 - chance) / 50), int(ms * (amount / 15000) * (100 - chance) / 50))):
        CreateOcean()
    for i in range(random.randint(int(ma * (amount / 130000) * chance / 50 + 1), int(ma * (amount / 25000) * chance / 50 + 1))):
        CreatePlain()
    for i in range(random.randint(int(ms * (amount / 40000) * (100 - chance) / 50), int(ms * (amount / 15000) * (100 - chance) / 50))):
        CreateRiver()
    for i in range(random.randint(int(ma * (amount / 70000) * chance / 50), int(ma * (amount / 20000) * chance / 50))):
        CreateMRange()
    CreateNoise(5)
    screen.create_rectangle(0, 0, twidth * tilesize, theight * tilesize, fill = '#0000be', width = 0)
    root.update_idletasks()
    root.update()
    for i in range(twidth):
        mod.append([1] * theight)
    for x in range(twidth):
        for y in range(theight):
            if y < theight / 2:
                if x < twidth / 2:
                    for circle in CircAdd3:
                        mod[x][y] += min(0.8, AddCirc(circle[0], circle[1], circle[2])) / 2
                    for line in LinAdd3:
                        mod[x][y] += min(0.8, AddLin(line[0],line[1],line[2])) / 2
                    for circle in CircSub3:
                        mod[x][y] -= min(0.8, AddCirc(circle[0], circle[1], circle[2])) / 2
                    for line in LinSub3:
                        mod[x][y] -= min(0.8, AddLin(line[0],line[1],line[2])) / 2
                    for noise in NoiseA3:
                        mod[x][y] += min(0.8 ,AddCirc(noise[0], noise[1], noise[2])) / 4 / noise[3] ** 1.5
                    for noise in NoiseS3:
                        mod[x][y] -= min(0.8 ,AddCirc(noise[0], noise[1], noise[2])) / 4 / noise[3] ** 1.5
                else:
                    for circle in CircAdd4:
                        mod[x][y] += min(0.8, AddCirc(circle[0], circle[1], circle[2])) / 2
                    for line in LinAdd4:
                        mod[x][y] += min(0.8, AddLin(line[0],line[1],line[2])) / 2
                    for circle in CircSub4:
                        mod[x][y] -= min(0.8, AddCirc(circle[0], circle[1], circle[2])) / 2
                    for line in LinSub4:
                        mod[x][y] -= min(0.8, AddLin(line[0],line[1],line[2])) / 2
                    for noise in NoiseA4:
                        mod[x][y] += min(0.8 ,AddCirc(noise[0], noise[1], noise[2])) / 4 / noise[3] ** 1.5
                    for noise in NoiseS4:
                        mod[x][y] -= min(0.8 ,AddCirc(noise[0], noise[1], noise[2])) / 4 / noise[3] ** 1.5
            else:
                if x < twidth / 2:
                    for circle in CircAdd2:
                        mod[x][y] += min(0.8, AddCirc(circle[0], circle[1], circle[2])) / 2
                    for line in LinAdd2:
                        mod[x][y] += min(0.8, AddLin(line[0],line[1],line[2])) / 2
                    for circle in CircSub2:
                        mod[x][y] -= min(0.8, AddCirc(circle[0], circle[1], circle[2])) / 2
                    for line in LinSub2:
                        mod[x][y] -= min(0.8, AddLin(line[0],line[1],line[2])) / 2
                    for noise in NoiseA2:
                        mod[x][y] += min(0.8 ,AddCirc(noise[0], noise[1], noise[2])) / 4 / noise[3] ** 1.5
                    for noise in NoiseS2:
                        mod[x][y] -= min(0.8 ,AddCirc(noise[0], noise[1], noise[2])) / 4 / noise[3] ** 1.5
                else:
                    for circle in CircAdd1:
                        mod[x][y] += min(0.8, AddCirc(circle[0], circle[1], circle[2])) / 2
                    for line in LinAdd1:
                        mod[x][y] += min(0.8, AddLin(line[0],line[1],line[2])) / 2
                    for circle in CircSub1:
                        mod[x][y] -= min(0.8, AddCirc(circle[0], circle[1], circle[2])) / 2
                    for line in LinSub1:
                        mod[x][y] -= min(0.8, AddLin(line[0],line[1],line[2])) / 2
                    for noise in NoiseA1:
                        mod[x][y] += min(0.8 ,AddCirc(noise[0], noise[1], noise[2])) / 4 / noise[3] ** 1.5
                    for noise in NoiseS1:
                        mod[x][y] -= min(0.8 ,AddCirc(noise[0], noise[1], noise[2])) / 4 / noise[3] ** 1.5
            mod[x][y] = max(0.4, mod[x][y])
            if mod[x][y] <= 1.3:
                screen.create_rectangle(x * tilesize, y * tilesize, x * tilesize + tilesize, y * tilesize + tilesize, width = 0, fill = '#0000%02x' % int(mod[x][y] * 190))
            elif mod[x][y] > 1.3 and mod[x][y] < 1.5:
                addcol= round((mod[x][y] - 1.45) * 400)
                screen.create_rectangle(x * tilesize, y * tilesize, x * tilesize + tilesize, y * tilesize + tilesize, width = 0, fill = '#%02x%02x%02x' % (194 + addcol, 178 + addcol, 128 + addcol))
            else:
                screen.create_rectangle(x * tilesize, y * tilesize, x * tilesize + tilesize, y * tilesize + tilesize, width = 0, fill = '#4b9629')
        root.update_idletasks()
        root.update()



def HeckNo():
    neg.destroy()
    aff.destroy()
    ques.destroy()
    root.title("Set Creation Values")
    inwid.pack()
    inhgt.pack()
    inma.pack()
    inms.pack()
    innoise.pack()
    inchance.pack(pady = 2)
    intile.pack(pady = 3)
    global fin
    fin = Button(root, text="Begin", command=Read)
    fin.pack(pady=10)
    global default
    default = Button(root, text='Default', command=Default)
    default.pack(pady=2)



def HeckYes():
    root.destroy()
    reader = input("Copy and paste text file here: \n")
    SetLists(reader)


#setting all windows and window widgets
twidth = theight = chance = tilesize = 0
root = Tk()
root.title("Continent Generator")
root.wm_attributes('-topmost',1)
root.resizable(0,0)
temp = Canvas(root, height = 1, width = 300)
temp.pack()
inwid = Text(root, width =15, height=1)
inhgt = Text(root, width=15, height=1)
inchance = Text(root, width=15, height=1)
intile = Text(root, width = 15, height = 1)
inms = Text(root, width = 15, height = 1)
inma = Text(root, width = 15, height = 1)
innoise = Text(root, width = 15, height = 1)
inwid.insert("1.0","Width in tiles")
inhgt.insert("1.0","Height in tiles")
inchance.insert("1.0","Object Density")
intile.insert("1.0","Tile Size")
inms.insert("1.0","Valley Density")
inma.insert("1.0","Ridge Density")
innoise.insert("1.0","Random Noise")
neg = Button(root, text="No", command=HeckNo)
aff = Button(root, text="Yes", command=HeckYes)
ques = Text(root, width=15, height=1)
ques.pack()
ques.insert("1.0", "Import a file?")
ques.config(state=DISABLED)
neg.pack()
aff.pack()
#setting variables
mod = [] #the grid containing everythin
NoiseA1 = []
NoiseA2 = []
NoiseA3 = []
NoiseA4 = []
NoiseS1 = []
NoiseS2 = []
NoiseS3 = []
NoiseS4 = []
LinAdd1 = []
LinAdd2 = []
LinAdd3 = []
LinAdd4 = []
CircAdd1 = []
CircAdd2 = []
CircAdd3 = []
CircAdd4 = []
LinSub1 = []
LinSub2 = []
LinSub3 = []
LinSub4 = []
CircSub1 = []
CircSub2 = []
CircSub3 = []
CircSub4 = []



root.mainloop()


