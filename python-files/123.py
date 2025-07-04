import os, time, ftputil

ftp = ftputil.FTPHost('192.168.1.99', 'FTP', '3575ftp0921')
mypath = '/'
ftp.chdir(mypath)

DAYS = 4
Total_deleted_size = 0
Total_deleted_file = 0

nowTime = time.time()
ageTime = nowTime - 60 * 60 * 24 * DAYS

print(1)

def delete_old_files(folder):
    global Total_deleted_size
    global Total_deleted_file
    print(f"Проверяется папка: {folder}")

    for path, dirs, files in ftp.walk(folder):
        print(f"Текущий путь: {path}, Файлы: {files}")
        for filename in files:
            try:
                full_path = ftp.path.join(path, filename)
                filetime = ftp.path.getmtime(full_path)
                filesize = ftp.path.getsize(full_path)
              

                if filetime < ageTime:
                    print(f"Удалён файл: {full_path} ({filesize // 1024} KB)")
                    ftp.remove(full_path)
                    Total_deleted_size += filesize
                    Total_deleted_file += 1
            except Exception as e:
                print(f"Ошибка с файлом {filename}: {e}")

starttime = time.asctime()

# Получаем список только папок в Apteka_26
all_items = ftp.listdir(ftp.curdir)
FOLDERS = [item for item in all_items if ftp.path.isdir(item)]

# Также проверим саму папку Apteka_26 (если там есть файлы)
delete_old_files('.')

# Проверяем каждую подпапку
for folder in FOLDERS:
    delete_old_files(folder)

finishtime = time.asctime()

print("Start " + str(starttime))
print("Deleted size " + str(int(Total_deleted_size / 1024 / 1024)) + "MB")
print("Deleted file " + str(Total_deleted_file))
print("Finish " + finishtime)
print('Closing FTP connection')
ftp.close()
print(6)
