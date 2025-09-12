import colorama
import os
import sys

def just_fix_windows_console():
    global fixed_windows_console

    if sys.platform != "win32":
        return
    if fixed_windows_console:
        return
    if wrapped_stdout is not None or wrapped_stderr is not None:
        # Someone already ran init() and it did stuff, so we won't second-guess them
        return

    # On newer versions of Windows, AnsiToWin32.__init__ will implicitly enable the
    # native ANSI support in the console as a side-effect. We only need to actually
    # replace sys.stdout/stderr if we're in the old-style conversion mode.
    new_stdout = AnsiToWin32(sys.stdout, convert=None, strip=None, autoreset=False)
    if new_stdout.convert:
        sys.stdout
just_fix_windows_console()
screenSize=[32,32]
#os.system('mode con: cols='+str(screenSize[1])+' lines='+str(int(screenSize[0]/2)))
screen_template=[["▀"'''▄''' for i1 in range(screenSize[0])] for i2 in range(int(screenSize[1]/2))]
screenColour=[[[0,0] for i1 in range(screenSize[0])] for i2 in range(int(screenSize[1]/2))]
ToDraw=[]
def abs(a):
	if a<0:
		return -a
	return a
def line(start,end):
	dx=end[0]-start[0]
	dy=end[1]-start[1]
	sign_x=1 if dx>0 else -1 if dx<0 else 0
	sign_y=1 if dy>0 else -1 if dy<0 else 0
	dx=abs(dx)
	dy=abs(dy)
	if dx>dy:
		pdx,pdy=sign_x,0
		S,L=dy,dx
	else:
		pdx,pdy=0,sign_y
		S,L=dx,dy
	x,y=start[0],start[1]
	error,t=L/2,0
	Line=[[x,y]]
	while t<L:
		error-=S
		if error<0:
			error+=L
			x+=sign_x
			y+=sign_y
		else:
			x+=pdx
			y+=pdy
		t+=1
		Line.append([x,y])
	return Line
def Line(start,end,colour="15"):
	ToDraw.append([line(start,end),colour])
def Draw():
	for object in ToDraw:
		for pixel in object[0]:
			screenColour[pixel[1]//2+pixel[1]%2][pixel[0]][pixel[1]%2]=object[1]
def Display():
	temp=screen_template.copy()
	Screen=""
	for Row,row in zip(temp,screenColour):
		for symbol,colour_code in zip(Row,row):
			if colour_code[0]==colour_code[1]:
				if colour_code==0:
					Screen+=" "
				else:
					Screen+='\033[38;5;'+str(colour_code[0])+"m█"
			else:
				Screen+='\033[38;5;'+str(colour_code[0])+';48;5;'+str(colour_code[1])+'m'+symbol+'\033[0m'
		Screen+='\n'
	print(Screen,end='')
def SimpleDraw():
	global draw
	draw=[[0 for i1 in range(screenSize[0])] for i2 in range(screenSize[1])]
	for object in ToDraw:
		for pixel in object[0]:
			draw[pixel[1]][pixel[0]]=1
def SimpleDisplay():
	for Y in range(screenSize[1]):
		for X in range(screenSize[0]):
			if draw[Y][X]==1:
				print("#",end='')
			else:
				print(".",end='')
		print()
Line([0,0],[30,30])
Line([7,9],[19,29])
Draw()
print(screenColour)
#Display()
#while True:
#        pass
