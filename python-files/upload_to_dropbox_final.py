
import dropbox
import sys

ACCESS_TOKEN = "sl.u.AF2fD-iSWnKp76Pnop03UyL6uIxJZJMtuY-zriBHOv8OIfP4StkihbsxzOx2ydTHNuJQsCdjzmLKinymGAdQi073gPjy6r1aZGJlj4SobQ70Dg0-f5ZBzcwR2oSGTPmj_QfUQL_KSaqj4"

def upload_file(local_path, dropbox_path):
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    with open(local_path, "rb") as f:
        dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
    print("✅ File uploaded to Dropbox successfully.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: upload_to_dropbox.exe <local_file_path>")
        sys.exit(1)

    local_file = sys.argv[1]
    dropbox_file = "/licenses.json"  # Dropbox root path
    upload_file(local_file, dropbox_file)
