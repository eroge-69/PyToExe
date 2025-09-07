import os
import shutil
import tarfile
import json
import logging
from datetime import datetime

# SharePoint class
class SharePoint:
    def __init__(self, config):
        self.config = config

    def auth(self):
        # Assuming Office365, Site, Version are defined elsewhere
        self.authcookie = Office365(self.config['url'], username=self.config['user'], password=self.config['password']).GetCookies()
        self.site = Site(self.config['site'], version=Version.v365, authcookie=self.authcookie)
        return self.site

    def connect_folder(self, folder_name):
        self.auth_site = self.auth()
        self.sharepoint_dir = '/'.join([self.config['doc_library'], folder_name])
        self.folder = self.auth_site.Folder(self.sharepoint_dir)
        return self.folder

    def upload_file(self, file, file_name, folder_name):
        self._folder = self.connect_folder(folder_name)
        with open(file, mode='rb') as file_obj:
            file_content = file_obj.read()
            self._folder.upload_file(file_content, file_name)

    def delete_file(self, file_name, folder_name):
        self._folder = self.connect_folder(folder_name)
        self._folder.delete_file(file_name)

# Function to copy and extract files
def copy_and_extract_files(source_path, destination_path):
    today = datetime.today().date()
    date_folder_name = today.strftime("%Y-%m-%d")  # Daily folder inside the month folder
    full_destination_path = os.path.join(destination_path, date_folder_name)
    os.makedirs(full_destination_path, exist_ok=True)

    files_to_copy = [
        f for f in os.listdir(source_path)
        if os.path.isfile(os.path.join(source_path, f)) and datetime.fromtimestamp(os.path.getmtime(os.path.join(source_path, f))).date() == today
    ]

    logging.info(f"Files to copy from {source_path}: {files_to_copy}")

    copied_files = []
    for file_name in files_to_copy:
        source_file = os.path.join(source_path, file_name)
        destination_file = os.path.join(full_destination_path, file_name)

        try:
            shutil.copy2(source_file, destination_file)
            copied_files.append(destination_file)
            logging.info(f"Copied file: {file_name} to {full_destination_path}")

            if file_name.endswith(".tar.gz"):
                extract_folder = os.path.join(full_destination_path, file_name.replace('.tar.gz', ''))
                os.makedirs(extract_folder, exist_ok=True)
                with tarfile.open(destination_file, "r:gz") as tar:
                    tar.extractall(path=extract_folder)
                for root, _, files in os.walk(extract_folder):
                    for f in files:
                        copied_files.append(os.path.join(root, f))

        except Exception as e:
            logging.error(f"Error processing file {file_name}: {e}")

    return copied_files

# Function to upload files to SharePoint
def upload_files_to_sharepoint(copied_files, sharepoint_folder, config):
    sp = SharePoint(config)
    for file_path in copied_files:
        file_name = os.path.basename(file_path)
        try:
            sp.upload_file(file_path, file_name, sharepoint_folder)
            logging.info(f"Uploaded: {file_name}")
        except FileNotFoundError:
            logging.error(f"File not found: {file_name}")
        except PermissionError:
            logging.error(f"Permission denied for file: {file_name}")
        except Exception as upload_err:
            logging.error(f"Failed to upload {file_name}: {upload_err}")

# Function to run the main process
def run_process():
    now = datetime.now()
    current_year = now.year
    current_month_name = now.strftime("%B")  # e.g., August

    # Dynamically create base local folder for this month
    base_local_folder = f"C:/Users/suresh.babubonam2/Vodafone Group/Testplanung Archiv - {current_month_name}"

    # Map source folder to destination folders with dynamic month folder path
    source_dest_pairs = {
        "Y:/Protected/Reproductions/Letters/MPI_Output_DMS/BW": os.path.join(base_local_folder, "Letters/KBW"),
        "Y:/Protected/Reproductions/Letters/MPI_Output_DMS/NW": os.path.join(base_local_folder, "Letters/NRW")
    }

    # Dynamically create SharePoint folder path for this month
    # Here the year range "2025_June_To_December" is assumed fixed; update if needed for other years
    sharepoint_folder = f"Environment Mgmt/Testplanungen_2025/2025_June_To_December/{current_month_name}/Letters"

    config_path = "C:/Users/suresh.babubonam2/OneDrive - Vodafone Group/Desktop/MPI Letters/config.json"

    try:
        with open(config_path) as config_file:
            config = json.load(config_file)['share_point']
    except Exception as e:
        logging.error(f"Failed to read config file: {e}")
        return

    all_copied_files = []
    try:
        for source, destination in source_dest_pairs.items():
            logging.info(f"Processing source: {source} to destination: {destination}")
            copied_files = copy_and_extract_files(source, destination)
            all_copied_files.extend(copied_files)

        upload_files_to_sharepoint(all_copied_files, sharepoint_folder, config)
        logging.info("Files copied, extracted, and uploaded successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    logging.basicConfig(filename='file_upload.log', level=logging.INFO, 
                        format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    run_process()
