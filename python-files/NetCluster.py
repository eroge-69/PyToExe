import subprocess
import sys
import time

def run_intro_then_landing():
    # Start Intro.py with subprocess
    intro_process = subprocess.Popen([sys.executable, 'Intro.py'])

    # Wait for 5 seconds while intro runs
    time.sleep(5)

    # Forcefully terminate Intro.py after 5 seconds
    intro_process.terminate()

    # Start LandingPage.py with subprocess
    subprocess.Popen([sys.executable, 'LandingPage.py'])

if __name__ == '__main__':
    run_intro_then_landing()
