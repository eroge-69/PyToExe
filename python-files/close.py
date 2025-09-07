import os

# List of programs you want to close
programs_to_close = ["notepad.exe", "chrome.exe", "discord.exe"]

for program in programs_to_close:
    os.system(f"taskkill /f /im {program}")