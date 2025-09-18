import ctypes
ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
MB_SYSTEMMODAL = 0x00001000
ctypes.windll.user32.MessageBoxW(None, "Hit OK to close the program, otherwise leave it open to prevent the screen saver from coming on.", MB_SYSTEMMODAL)
ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)