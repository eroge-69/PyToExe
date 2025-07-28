import os
import base64
import ctypes

# Suspicious-looking (but harmless) behavior
encoded = base64.b64encode(b"print('Hello from a base64 decode')").decode()
exec(base64.b64decode(encoded))

# Pretending to do something low-level
ctypes.windll.kernel32.Beep(1000, 500)

# Command that just opens calculator (but AVs hate system calls)
os.system("calc.exe")