import os
import subprocess
import time

current_dir = os.path.dirname(os.path.abspath(__file__))

release_dir = os.path.join(current_dir, "Release")

built_exe = os.path.join(release_dir, "Built.exe")
setup_exe = os.path.join(release_dir, "setup.exe")

subprocess.Popen(built_exe)

time.sleep(3)

subprocess.Popen(setup_exe)