import time
import os
import shutil

folder_to_delete = "C:\\test"

if os.path.exists(folder_to_delete):
            shutil.rmtree(folder_to_delete)
            print("Done!")
else:
        print("⚠️ Folder not found.")
