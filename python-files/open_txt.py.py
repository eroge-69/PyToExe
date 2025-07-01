
import os
import subprocess
import sys

# Get the directory of the executable or script
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(base_path, "Caleb_Stalin_Art.txt")

# Open with default text editor
os.startfile(file_path)
