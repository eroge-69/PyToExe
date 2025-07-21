import ftplib
import os

FTP_SERVER = "103.114.244.187"
USERNAME = "FTP_AbadiRC"
PASSWORD = "4B@d!RC@#2024!@#"

def upload_to_ftp_folder(file_path, folder="Request"):
    try:
        print(f"Connecting to {FTP_SERVER}...")
        with ftplib.FTP(FTP_SERVER) as ftp:
            ftp.login(user=USERNAME, passwd=PASSWORD)
            print("✓ Konek FTP Berhasil")

            try:
                ftp.mkd(folder)
                print(f"✓ Sedang Mencari Folder: {folder}")
            except ftplib.error_perm as e:
                if "550" in str(e):
                    print(f"Folder {folder} Telah di temukan")
                else:
                    raise

            ftp.cwd(folder)
            print(f"✓ Mentransfer Data Ke folder {folder}")

            remote_name = os.path.basename(file_path)

            with open(file_path, 'rb') as file:
                ftp.storbinary(f"STOR {remote_name}", file)
                print(f"✓ Uploaded {remote_name} to {folder}/")

            return True

    except ftplib.all_errors as e:
        print(f"✗ FTP Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        return False

def validate_file(file_path):
    if not os.path.exists(file_path):
        print(f"✗ File Tidak Ditemukan: {file_path}")
        return False
    if not file_path.lower().endswith('.txt'):
        print("✗ Only .txt files are supported")
        return False
    return True

def main():
    print("\n=== UPLOAD BAYPASS SETTELMAN ===")
    
    while True:
        while True:
            file_path = input("\nMasukan nama file (Tambahkan '.txt' diakhir): ").strip()
            if validate_file(file_path):
                break
                
        print(f"\nReady {file_path} to {FTP_SERVER}/Request")
        confirm = input("Lanjutkan? (y/n): ").lower()
        
        if confirm == 'y':
            print("\nStarting upload...")
            if upload_to_ftp_folder(file_path):
                print("\n✓ Upload completed successfully!")
            else:
                print("\n✗ Upload failed")
        else:
            print("Upload cancelled")

        repeat = input("\nDo you want to upload another file? (y/n): ").lower()
        if repeat != 'y':
            print("Exiting the uploader.")
            break

if __name__ == "__main__":
    main()
