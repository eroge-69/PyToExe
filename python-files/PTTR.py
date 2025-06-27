import os
import sys
import subprocess

def terminate_process(process_name):
    """
    Terminates a specified process by its name.

    Args:
        process_name (str): The name of the process to terminate (e.g., "paintthetownred.exe").
    """
    print(f"Attempting to terminate process: {process_name}")

    if sys.platform == "win32":
        try:
            # Use taskkill command on Windows
            # /F: Forcefully terminate the process
            # /IM: Image name of the process
            command = f"taskkill /F /IM {process_name}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Successfully terminated '{process_name}'.")
            elif "not found" in result.stderr.lower() or "no running instance" in result.stdout.lower():
                print(f"Process '{process_name}' not found or not running.")
            else:
                print(f"Error terminating '{process_name}':")
                print(f"  Standard Output: {result.stdout}")
                print(f"  Standard Error: {result.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("This script is designed for Windows. Process termination may differ on other operating systems.")
        print("For Linux/macOS, you might use 'pkill' or 'killall'.")
        # Example for Linux/macOS (uncomment if needed for cross-platform)
        # try:
        #     command = f"pkill -f {process_name}" # or killall if you want exact match
        #     subprocess.run(command, shell=True, check=True)
        #     print(f"Successfully terminated '{process_name}'.")
        # except subprocess.CalledProcessError:
        #     print(f"Process '{process_name}' not found or not running.")
        # except Exception as e:
        #     print(f"An error occurred: {e}")

if __name__ == "__main__":
    process_to_kill = "paintthetownred.exe"
    terminate_process(process_to_kill)

    # Keep the console window open briefly so the user can see the output
    input("Press Enter to exit...")
