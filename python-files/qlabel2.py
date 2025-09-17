# pyinstaller "D:\tmp\Ocaml\qlabel.py" --onefile --windowed --icon="D:\tmp\Ocaml\icons\apps_32.png"
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from functools import partial
import sys, os
from subprocess import*
#from threading import Timer

a, b, c, d, e = 'D:/tmp/Ocaml', 'D:/tmp/Dokumente', '.py', '.odt', '.ods'
act = []
for p, ex in [(b, d), (b, e), (a, c)]:
    os.chdir(p)
    list = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)
    n = 3
    for l in list[::-1]:
        if l.endswith(ex): act += [l.split('.')[0]]; n -=1
        if n==0: break
act = tuple(act)
#print(act)

icons = 'apps Buero text tabelle Internet chromium apps bilder calculator einstellungen explorer python scite solitaire\
 arduino sudoku chess'
 
icons = ';BUERO text_ %s %s %s tabelle_ %s %s %s rechner_ ;INTERNET chromium_\
 ;GRAFIK bilder_ svg_ openscad_ lineal_ ;MULTIMEDIA playlist_ audacity_ ;PROGRAM python_\
 %s %s %s ide_ arduino_ falstad_ octave_ alibre_ ;SPIELE chess_ sudoku_ tetris_\
 symbol_ solitaire_ kakuro_ ;SYSTEM explorer_ terminal_ einstellungen_ wifi_ bluetooth_\
 info_' % act
#print(icons.split())
   

app = QApplication(sys.argv)
app.setWindowIcon(QIcon('D:/tmp/Ocaml/icons/apps_32.ico'))
apps = QWidget()
apps.setGeometry(20, 180, 770, 470)
#apps.setWindowFlag(Qt. FramelessWindowHint)
apps.setStyleSheet("background-color : #E1EAFB; border-radius: 5; font: 10pt 'Segoe UI Variable'")
#apps.setStyleSheet("background-color : Gainsboro; border-color: gray; border-style: solid; border-width: 1px; border-radius: 8;")
x, y = -50, 10

"""
def task():
    timer.cancel()
    apps.close()
timer = Timer(2, task)
"""

def click(n, t, e):
    print(n, t)
    #timer.start()
    if n==1: os.startfile("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/LibreOffice/LibreOffice Writer.lnk")
    elif n in [2,3,4]: os.startfile('D:/tmp/Dokumente/%s.odt' % t)
    elif n==5: os.startfile("C:/ProgramData/Microsoft/Windows/Start Menu/Programs/LibreOffice/LibreOffice Calc.lnk")
    elif n in [6,7,8]: os.startfile('D:/tmp/Dokumente/%s.ods' % t)
    elif n==9:  os.popen("python D:/tmp/Ocaml/rechner.py")
    elif n==16:  os.startfile("D:/tmp/Ocaml/pyglet_lineal.pyw")
    elif n==11: os.startfile("Brave")
    elif n==13: os.startfile("D:/tmp/Bilder/accuweather.jpeg")
    elif n==31:  os.popen("python D:/tmp/Ocaml/chess/chess_html.py")
    elif n==32:  os.popen("python D:/tmp/Ocaml/sudoku7.py")
    elif n==33:  os.popen("python D:/tmp/Ocaml/Tetris5.py")
    elif n==39:  os.startfile("cmd")
    elif n==21:  os.popen("C:/Users/NONAME/Downloads/wscite556/wscite/SciTE.exe")
    elif n==23:  os.popen("C:/Users/NONAME/Downloads/wscite556/wscite/SciTE.exe D:/tmp/Ocaml/%s.py" % t)
    apps.close()
    
n = 0
def L(t):
    global x, y, n
    l3 = QLabel(apps)
    a, b = t[0]==';',  t[-1]=='_'
    if a: t = t[1:]; x += 100; y = 10
    l3.setGeometry(x, y, 100, 60 if b else 20)
    l3.setText(t[:-1] if b else t)
    l3.setAlignment(Qt.AlignHCenter | (Qt.AlignBottom if b else Qt.AlignVCenter))
    l3.setStyleSheet("background-color: #E1EAFB; border-radius: 3;  font: %ipt 'Segoe UI Variable'" % (12 if a else 10))
    if b:
        li = QLabel(l3)
        li.setGeometry(34, 6, 32, 32)
        pix = QPixmap('D:/tmp/Ocaml/icons/' + t + '32.png')
        li.setPixmap(pix)
    if not a:
        l3.enterEvent = lambda _: l3.setStyleSheet("background-color: white")
        l3.leaveEvent = lambda _: l3.setStyleSheet("background-color: #E1EAFB")
    y += 72 if b else 24
    l3.mousePressEvent = partial(click, n, l3.text())
    n += 1
    return l3

for t in icons.split(): L(t)
	
def keyPressed(e):
    if e.key() == Qt.Key_Escape:  apps.close()
apps.keyPressEvent = keyPressed

apps.show()
app.exec_()
"""
1 1 0 0 1 1 0 0 1
0 1 1 0 0 1 1 0 0
1 3 2 0 1 3 2 0 1


pacman -S xorg-server xorg-server-utils xorg-xinit xorg-twm xorg-xclock xterm

Buero		Internet	Grafik	Multimedia		Program	Spiele		System

text		+chrome	galery	playlist		+python	tetris			terminal
file 1				svg		audacity		file 1		+sudoku		+einstellungen
file 2				openscad				file 2		+chess		wifi
tabelle								ide		symbole		bluetooth											
file 1									arduino	kakuro
file 2									falstad	+solitaire
editor								octave	
									alibre
									

Buero text_ %s %s tabelle_ %s %s editor_ Internet chrome_ Grafik bilder_ svg_ openscad_\
 Multimedia playlist_ audacity_ Program python_ %s %s ide_ arduino_ falstad_ octave_\
 alibre_ Spiele chess_ sudoku_ tetris_ symbol_ solitaire_ kakuro_ System terminal_\
 einstellungen_ wifi_ bluetooth_ info_
"""
