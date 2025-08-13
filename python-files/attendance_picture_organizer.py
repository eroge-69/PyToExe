import os
import shutil
import pandas as pd
from datetime import datetime

def organize_pictures(existing_folder_path, new_pictures_path, csv_path, report_path):
    # Read CSV/XLSX into DataFrame
    if csv_path.lower().endswith(".xlsx"):
        df = pd.read_excel(csv_path)
    else:
        df = pd.read_csv(csv_path)
    
    roll_numbers = df.iloc[:, 0].astype(str).tolist()  # First column = Roll Nos

    report_data = []

    for roll_no in roll_numbers:
        folder_created = "No"
        file_transferred = "No"
        error_msg = ""
        picture_filename = ""
        timestamp = ""

        target_folder = os.path.join(existing_folder_path, roll_no)
        picture_found = False

        # Ensure folder exists
        if not os.path.exists(target_folder):
            try:
                os.makedirs(target_folder)
                folder_created = "Yes"
            except Exception as e:
                error_msg = f"Failed to create folder: {e}"
                report_data.append([roll_no, folder_created, file_transferred, picture_filename, timestamp, error_msg])
                continue

        # Find picture file
        for ext in [".jpg", ".jpeg", ".png"]:
            picture_path = os.path.join(new_pictures_path, roll_no + ext)
            if os.path.exists(picture_path):
                picture_found = True
                picture_filename = os.path.basename(picture_path)
                try:
                    shutil.copy(picture_path, target_folder)
                    file_transferred = "Yes"
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    error_msg = f"Copy failed: {e}"
                break
        
        if not picture_found:
            error_msg = "Picture not found"

        report_data.append([roll_no, folder_created, file_transferred, picture_filename, timestamp, error_msg])

    # Save report
    report_df = pd.DataFrame(report_data, columns=["Roll No", "Folder Created", "File Transferred", "Picture Filename", "Timestamp", "Error"])
    report_df.to_csv(report_path, index=False)
    print(f"\n✅ Report saved at: {report_path}")


if __name__ == "__main__":
    print("📂 Attendance Picture Organizer")
    existing_folder_path = input("Enter path to existing folders (Location 1): ").strip('"')
    new_pictures_path = input("Enter path to new pictures (Location 2): ").strip('"')
    csv_path = input("Enter path to Roll Numbers CSV/XLSX file: ").strip('"')
    report_path = input("Enter path to save report CSV: ").strip('"')

    organize_pictures(existing_folder_path, new_pictures_path, csv_path, report_path)
    print("\n✅ Task completed successfully!")
