import subprocess

# Path to Edge browser (update if yours is in a different location)
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Target URL (no iframe now)
url = "https://hianimez.is/"

# Launch Edge in App Mode with fullscreen and flags
flags = [
    f"--app={url}",
    "--start-fullscreen",
    "--disable-infobars",
    "--force-dark-mode",
    "--window-size=1920,1080"
]

subprocess.Popen([edge_path] + flags)
