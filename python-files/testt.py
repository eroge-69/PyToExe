import time

filepath = r"C:\path\to\your\excel_file.xlsx"

while True:
    try:
        df = pd.read_excel(filepath)
        print("Read successful!")
        break
    except PermissionError:
        print("File locked, retrying...")
        time.sleep(2)  # wait 2 seconds before retrying

input("Press Enter to exit...")