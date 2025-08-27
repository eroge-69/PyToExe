import subprocess
import os
import sys
import ctypes

# 콘솔창 제거
if ctypes.windll.kernel32.GetConsoleWindow() != 0:
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# EXE로 빌드됐는지 확인
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# 파일 경로
retroarch = os.path.join(base_dir, "retroarch.exe")
core = os.path.join(base_dir, "mesen_libretro.dll")
rom = os.path.join(base_dir, "Sample_Game.nes")
noui_cfg = os.path.join(base_dir, "retroarch_noui.cfg")

# 명령어
cmd = f'"{retroarch}" -L "{core}" "{rom}" --appendconfig "{noui_cfg}"'

# 게임 실행 (콘솔창 없이)
subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
