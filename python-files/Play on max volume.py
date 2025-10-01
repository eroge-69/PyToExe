# important setup
print("Getting ready...")
from os import system, chdir
chdir("C:")
def FixPip():
    print("Fixing pip [1/2]")
    system("pip config set global.index-url http://mirrors.sustech.edu.cn/pypi/web/simple --quiet")
    print("Fixing pip [2/2]")
    system("pip config set global.trusted-host mirrors.sustech.edu.cn --quiet")
FixPip()
system("pip install playsound")
system("pip install keyboard")
from playsound import playsound
import os
#locate sound file path(s)
dirrname = os.path.dirname(os.path.abspath(__file__))
print(dirrname)
filename = dirrname+"\\metadata\\ToI.mp3"
filename2 = dirrname+"\\metadata\\Rev.mp3"
#execute
playsound(filename)
playsound(filename2)