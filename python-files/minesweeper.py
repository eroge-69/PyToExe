from tkinter import *
from random import randint

buttons = []
grid = [['n' for a in range(20)] for b in range(20)]
visible = [['0' for a in range(20)] for b in range(20)]
cell_size = 25
isFirstClick = True

def generate_mines():
    global grid
    c = 0
    while c < 70:
        a = randint(0,19)
        b = randint(0,19)
        if grid[a][b] == 'n':
            grid[a][b] = 'm'
            c += 1

def redraw():
    for a in range(20):
        for b in range(20):
            if visible[a][b] == '1':
                c = computeNumber(a, b)    
                if c == 0:
                    c = ""
                if grid[a][b] == 'm': c = 'x'
                if c != 'x':
                    if c == 7:
                        buttons[a][b]['fg'] = 'orange'
                    if c == 6:
                        buttons[a][b]['fg'] = 'orange'
                    if c == 5:
                        buttons[a][b]['fg'] = 'orange'
                    if c == 4:
                        buttons[a][b]['fg'] = 'purple'
                    if c == 3:
                        buttons[a][b]['fg'] = 'red'
                    if c == 2:
                        buttons[a][b]['fg'] = 'green'
                    if c == 1:
                        buttons[a][b]['fg'] = 'blue'
                else: buttons[a][b]['fg'] = 'black'
                buttons[a][b]['text'] = c
                buttons[a][b].place(x=cell_size*b,y=cell_size*a,width=cell_size,height=cell_size)
                if (grid[a][b] == 'm'):
                    buttons[a][b].config(bg='red')
                elif (c == 0 and grid[a][b] == 'n'):
                    buttons[a][b].config(bg='pale green')
                else:
                    buttons[a][b].config(bg='pale green')
                c = 0
            elif visible[a][b] == '2':
                buttons[a][b]['text'] = 'F'
                buttons[a][b].place(x=cell_size*b,y=cell_size*a,width=cell_size,height=cell_size)
                buttons[a][b].config(bg='orange')
            else:
                buttons[a][b]['text'] = ''
                buttons[a][b].place(x=cell_size*b,y=cell_size*a,width=cell_size,height=cell_size)
                buttons[a][b].config(bg='#cdc1b4')

def reload(e):
    global grid, buttons, visible, isFirstClick
    isFirstClick = True
    grid = [['n' for a in range(20)] for b in range(20)]
    visible = [['0' for a in range(20)] for b in range(20)]
    generate_mines()
    redraw()

def LMBClicked(x, y):
    global visible, grid, isFirstClick
    if (isFirstClick):
        isFirstClick = False
        for a in range(-1, 2):
            for b in range(-1, 2):
                ox = x + a
                oy = y + b
                if (ox< 20 and oy < 20 and ox >= 0 and oy >= 0):
                    grid[ox][oy] = 'n'
    visible[x][y] = '1'
    checkCell(x, y)
    redraw()

def RMBClicked(x, y):
    global visible
    currentValue = visible[x][y]
    if (currentValue == '0'):
        visible[x][y] = '2'
    elif (currentValue == '2'):
        visible[x][y] = '0'
    redraw()


root = Tk()

root.title('minesweeper')
root.geometry('500x500')
# funcs = [['' for a in range(20)] for b in range(20)]

buttons = [[Button(root,text = '',bg = '#cdc1b4',font = 'Arial 15 bold',fg = '#776e65') for a in range(20)] for b in range(20)]
a = 0
b = 0
for a in range(20):
    for b in range(20):
        funcLMB = (lambda e, x=a, y=b: LMBClicked(x, y))
        buttons[a][b].bind('<Button-1>', funcLMB)
        funcRMB = (lambda e, x=a, y=b: RMBClicked(x, y))
        buttons[a][b].bind('<Button-3>', funcRMB)


# root.bind('<Button-1>', LMBClicked)
# root.bind('<Button-3>', RMBClicked)

root.bind('<Key>', reload)

def checkCell(x, y):
    global visible
    currVal = grid[x][y]
    currNum = computeNumber(x, y)
    if (currVal == 'n'):
        visible[x][y] = '1'
        print(currNum)
        if (currNum == 0):
            for a in range(-1, 2):
                for b in range(-1, 2):
                    ox = x + a
                    oy = y + b
                    if (ox< 20 and oy < 20 and ox >= 0 and oy >= 0):
                        # if ((a == 1 and b == -1) or (a == 1 and b == 1) or (a == -1 and b == -1) or (a == -1 and b == 1)):
                            # pass
                        # else:
                        if (visible[x + a][y + b] == '0'):
                            checkCell(x + a, y + b)

        
def computeNumber(a, b):
    c = 0
    if (a > 0) and (b > 0) and (a < 19) and (b < 19):
        if grid[a-1][b] == 'm': c += 1
        if grid[a+1][b] == 'm': c += 1
        if grid[a][b-1] == 'm': c += 1
        if grid[a][b+1] == 'm': c += 1
        if grid[a-1][b-1] == 'm': c += 1
        if grid[a+1][b+1] == 'm': c += 1
        if grid[a-1][b+1] == 'm': c += 1
        if grid[a+1][b-1] == 'm': c += 1
    if (a == 0) and (b > 0) and (b < 19):
        if grid[a+1][b] == 'm': c += 1
        if grid[a][b-1] == 'm': c += 1
        if grid[a][b+1] == 'm': c += 1
        if grid[a+1][b+1] == 'm': c += 1
        if grid[a+1][b-1] == 'm': c += 1
    if (a == 19) and (b > 0) and (b < 19):
        if grid[a-1][b] == 'm': c += 1
        if grid[a][b-1] == 'm': c += 1
        if grid[a][b+1] == 'm': c += 1
        if grid[a-1][b-1] == 'm': c += 1
        if grid[a-1][b+1] == 'm': c += 1
    if (b == 0) and (a > 0) and (a < 19):
        if grid[a-1][b] == 'm': c += 1
        if grid[a+1][b] == 'm': c += 1
        if grid[a][b+1] == 'm': c += 1
        if grid[a+1][b+1] == 'm': c += 1
        if grid[a-1][b+1] == 'm': c += 1
    if (b == 19) and (a > 0) and (a < 19):
        if grid[a-1][b] == 'm': c += 1
        if grid[a+1][b] == 'm': c += 1
        if grid[a][b-1] == 'm': c += 1
        if grid[a-1][b-1] == 'm': c += 1
        if grid[a+1][b-1] == 'm': c += 1
    if (a == b == 0):
        if grid[a+1][b] == 'm': c += 1
        if grid[a][b+1] == 'm': c += 1
        if grid[a+1][b+1] == 'm': c += 1
    if (a == b == 19):
        if grid[a-1][b] == 'm': c += 1
        if grid[a][b-1] == 'm': c += 1
        if grid[a-1][b-1] == 'm': c += 1
    return c


generate_mines()
redraw()

root.mainloop()
