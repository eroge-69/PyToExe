import os
dir = os.getcwd()
folder = os.listdir(dir)
for file in folder:
    name = file.replace("[SPOTDOWNLOADER.COM] ", "")
    os.rename(file, name)