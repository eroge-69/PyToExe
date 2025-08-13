import subprocess
import os

def launch_dashboard():
    dashboard_path = os.path.expanduser("~/AdvisorOne/FluidDashboard.py")
    subprocess.run(["python", dashboard_path])

if __name__ == "__main__":
    launch_dashboard()