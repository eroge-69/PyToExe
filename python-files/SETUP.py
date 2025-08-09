#setup
import os
while True:
    folder_name = "Config files"
    file_name = "Music folder path"
    full_file_path = os.path.join(folder_name, file_name)
    with open(full_file_path, 'w', encoding = "UTF-8") as f:
        f.write("")
    music_list = "Music List"
    music_full_path = os.path.join(folder_name, music_list)
    with open(music_full_path, 'w', encoding = "UTF-8") as f:
        f.write("")