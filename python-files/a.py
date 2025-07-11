Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import time
... import os
... import glob
... 
... SETTINGS_PATH = r"A:\Settings"
... SLEEP_TIME = 600
... 
... def delete_sga_files():
...     pattern = os.path.join(SETTINGS_PATH, "sga_*")
...     for sga_file in glob.glob(pattern):
...         os.remove(sga_file)
... 
... if __name__ == "__main__":
...     while True:
...         delete_sga_files()
