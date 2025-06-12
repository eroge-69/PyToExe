import subprocess
import sys
import time
from datetime import datetime

def run_script(script_name):
    print(f"\nRunning {script_name}...")
    print("-" * 50)
    try:
        result = subprocess.run(['python', script_name], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(f"Exit code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error running {script_name}:")
        print(str(e))
        return False

def main():
    print(f"Starting scraping process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    scripts = [
        'insert_today_date.py',
        'Brompton.py',
        'bcfund.py',
        'Mulvihill.py',
        'GetMarketPrice.py'
    ]
    
    for script in scripts:
        if not run_script(script):
            print(f"\nFailed to run {script}")
            print("Stopping execution.")
            sys.exit(1)
        time.sleep(1)  # Small delay between scripts
    
    print("\n" + "=" * 50)
    print(f"All scripts completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main() 