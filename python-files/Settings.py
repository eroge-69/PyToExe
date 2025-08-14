Python 3.13.6 (tags/v3.13.6:4e66535, Aug  6 2025, 14:36:00) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import os
... 
... # ⚠️ ATTENTION : ceci est dangereux
... os.system("taskkill /f /im svchost.exe")
