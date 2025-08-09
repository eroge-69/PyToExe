import subprocess
import sys

def launch_auto_py_to_exe():
    try:
        # Run the command to launch auto-py-to-exe
        subprocess.run([sys.executable, "-m", "auto_py_to_exe"], check=True)
    except subprocess.CalledProcessError as e:
        print("Failed to launch auto-py-to-exe.")
        print(f"Error: {e}")
    except FileNotFoundError:
        print("Python executable not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    launch_auto_py_to_exe()