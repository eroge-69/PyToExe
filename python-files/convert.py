import os
import re

# Month to number mapping
month_map = {
    "January": "01", "February": "02", "March": "03", "April": "04",
    "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12"
}

def rename_files(folder):
    for filename in os.listdir(folder):
        match = re.match(r"([A-Za-z]+) (\d{4}) e-statement\.pdf", filename)
        if match:
            month_name = match.group(1)
            year = match.group(2)
            month_num = month_map.get(month_name)
            if month_num:
                new_name = f"{year}{month_num}_scotiabank_checkings.pdf"
                os.rename(os.path.join(folder, filename), os.path.join(folder, new_name))
                print(f"Renamed: {filename} ➜ {new_name}")
            else:
                print(f"❌ Unknown month in filename: {filename}")
        else:
            print(f"⏭️ Skipping file: {filename}")

if __name__ == "__main__":
    folder_path = os.getcwd()
    rename_files(folder_path)
    input("Done. Press Enter to exit.")