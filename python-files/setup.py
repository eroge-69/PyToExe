from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    "packages": ["pygame"],
    "include_files": [],  # добавьте сюда шрифты или другие файлы
    "excludes": ["tkinter"]
}

setup(
    name="Салтийская Республика",
    version="1.0",
    description="Стратегия управления страной",
    options={"build_exe": build_exe_options},
    executables=[Executable("filename.py", base=base, icon="icon.ico")]
)