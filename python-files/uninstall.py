import winshell
import os
import shutil

path = os.path.join(os.getenv('APPDATA'), 'AgendaTurismo')
path_exe = os.path.join(path, 'agenda-turismo.exe')
path_ico = os.path.join(path, 'icon.ico')
path_lnk = os.path.join(winshell.desktop(), 'Agenda Turismo.lnk')
path_lnk_menu = os.path.join(winshell.start_menu(), 'Agenda Turismo.lnk')


if os.path.exists(path):
    shutil.rmtree(path)

if os.path.exists(path_lnk):
    os.remove(path_lnk)

if os.path.exists(path_lnk_menu):
    os.remove(path_lnk_menu)