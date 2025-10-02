from rich.progress import track
import time

for step in track(range(100), description="[cyan]Waiting..."):
    time.sleep(0.05)  # simulate work