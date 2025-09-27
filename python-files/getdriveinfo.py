"""
v231027-__dsk-admin getdriveinfo.py programja
tartm.bat:
del *.txt
cd..
mkdir __%date:~2,2%"-"%date:~6,2%"-"%date:~10,2%%1
cd ./__dsk-admin
python getdriveinfo.py
"""
import shutil,psutil,os

def get_drive_label(drive_letter):
    try:
        label = os.popen(f"vol {drive_letter}:").read()
        label = label.splitlines()[0]
        label = label.replace("Volume in drive " + drive_letter + " is ", "").strip()
        return label
    except Exception as e:
        return None

def get_filesystem_info(path):
    partition = psutil.disk_usage(path)
    global total_gb,used_gb,free_gb
    total_gb = partition.total / (1024 ** 3)  # Konvertálás megabájtba
    used_gb = partition.used / (1024 ** 3)
    free_gb = partition.free / (1024 ** 3)

current_drive = os.path.splitdrive(os.getcwd())[0]
get_filesystem_info(current_drive)
label = get_drive_label(current_drive[0])
labst1=str(label)
labst = labst1.split()[-1]
targetxt=labst.lower()+'.txt'
fi = open(targetxt, "w",encoding='utf-8')
print(f"Name : {labst}",file=fi)
print(f"Drive: {current_drive}",file=fi)
print(f"Total: {total_gb:.2f} GB",file=fi)
print(f"Used : {used_gb:.2f} GB",file=fi)
print(f"Free : {free_gb:.2f} GB\n",file=fi)

fi.close()

# Aktuális mappa (meghajtó) lekérdezése
current_drive = os.path.splitdrive(os.getcwd())[0]
# DOS "tree" parancs kimenetét egy bináris fájlba írjuk
os.system(f'tree /F /A {current_drive}/. >> {targetxt}')
shutil.copy(targetxt, r"d:\0_pen-microsd")

