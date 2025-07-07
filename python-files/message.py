import ctypes
import winsound

# Error title and message for encrypted files
title = "Error: Encrypted File"
message = "This file cannot be opened because it is encrypted. Please decrypt it first."

# Show message box with error icon and play the classic error sound
ctypes.windll.user32.MessageBoxW(0, message, title, 0x10 | 0x0)

# Play Windows error sound
winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
