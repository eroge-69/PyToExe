cmd = [
    "pyinstaller",
    "--name=AuraLauncher",
    "--windowed",
    "--onefile",
    "--icon=assets/icon.ico",
    "--add-data=assets;assets",
    "aura_launcher.py"
]