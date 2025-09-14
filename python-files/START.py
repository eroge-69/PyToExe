import os
import sys

execute = 'cd ' + sys.prefix + ' && ' + r'"Scripts\python.exe" main.py'
os.system(execute)
print(execute)
os.system(execute)