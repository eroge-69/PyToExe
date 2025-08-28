# cook your dish here
import os
import shutil
import datetime

folder_name = datetime.date.today().strftime('%m%d')

server_folder = os.path.join('D:', folder_name)
lap_folder1 = os.path.join('D:', 'testF', '1base.txt')
lap_folder2 = os.path.join('D:', 'testF', 'baseExt.txt')

if not os.path.exists(server_folder):
    os.mkdir(server_folder)
else: 
    print("ERROR! Папка уже существует")

shutil.copy2(lap_folder1, server_folder)
shutil.copy2(lap_folder2, server_folder)
print("Скопировано")