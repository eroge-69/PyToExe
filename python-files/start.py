import subprocess
import os

def run_lvls_bat():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    bat_path = os.path.join(current_dir, "_Data", "lvls.bat")

    if not os.path.isfile(bat_path):
        print(f"Файл {bat_path} не найден.")
        return

    subprocess.Popen([bat_path], shell=True)

if __name__ == "__main__":
    run_lvls_bat()
