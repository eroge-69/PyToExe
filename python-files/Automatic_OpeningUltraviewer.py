import os
import time
import subprocess

def run_application_on_startup():
    """
    This script waits for 5 minutes and then launches the
    UltraViewer application from the specified path.
    """

    print("Script started. Waiting for 5 minutes...")
    # Wait for 5 minutes (5 minutes * 60 seconds/minute)
    time.sleep(1* 60)
    print("Wait period is over. Attempting to launch the application.")

    # The specific path to the UltraViewer application
    app_path = r"C:\Program Files (x86)\UltraViewer\UltraViewer_Desktop.exe"

    # Check if the file exists before trying to run it
    if os.path.exists(app_path):
        print(f"Found application at: {app_path}")
        try:
            # Launch the application using subprocess.Popen
            # This is a non-blocking call, allowing the script to exit
            subprocess.Popen([app_path])
            print(f"Successfully launched UltraViewer.")
        except Exception as e:
            print(f"An error occurred while trying to launch the application: {e}")
    else:
        print(f"Error: The application was not found at the specified path: {app_path}")

    print("Script finished.")

# This ensures the function runs when the script is executed
if __name__ == "__main__":
    run_application_on_startup()