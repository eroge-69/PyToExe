import subprocess
import pandas as pd
from bs4 import BeautifulSoup
import os
from datetime import datetime

def run_baqup(token, thread_id):
    try:
        cmd = f"python -m baqup.main --token {token} --id {thread_id}"
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running baqup: {e}")
        return False

def parse_backup_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        # Find table data in the HTML
        table = soup.find('table')
        if table:
            data = []
            for row in table.find_all('tr'):
                cols = row.find_all(['td', 'th'])
                data.append([col.text.strip() for col in cols])
            return pd.DataFrame(data[1:], columns=data[0])
    return None

def save_to_excel(df, output_path):
    df.to_excel(output_path, index=False)

def main():
    # Configuration
    QUIP_TOKEN = "SkFHOU1BMHZlSXU=|1781854073|HXYijkAThQtEcgB9O7TeS0zMrZanVrIlhF2XC69sicE="
    THREAD_ID = "Yvt4A1b871XH"
    
    # Create timestamp for backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Run backup
    if run_baqup(QUIP_TOKEN, THREAD_ID):
        # Find the latest backup file (you'll need to adjust the path based on baqup output)
        backup_dir = "C:\Users\caitlchr\Downloads"
        backup_file = os.path.join(backup_dir, f"{THREAD_ID}.html")
        
        if os.path.exists(backup_file):
            # Parse the backup and save to Excel
            df = parse_backup_file(backup_file)
            if df is not None:
                excel_path = f"quip_data_{timestamp}.xlsx"
                save_to_excel(df, excel_path)
                print(f"Data successfully exported to {excel_path}")
            else:
                print("No table data found in the backup file")
        else:
            print("Backup file not found")
    else:
        print("Backup failed")

if __name__ == "__main__":
    main()