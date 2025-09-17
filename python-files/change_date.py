import zipfile
import os
import shutil

game_root = os.path.dirname(os.path.abspath(__file__))

# Список архивов
archives = [
    "data/Mode_Modifier.pak",
    "data/Universe_mod.pak",
    "data/universe_mod_texts_ru.pak"
]

# Новая дата для всех файлов
new_date = (2020, 1, 1, 0, 0, 0)

for archive_rel_path in archives:
    archive_path = os.path.join(game_root, archive_rel_path)
    if not os.path.exists(archive_path):
        print(f"Архив не найден: {archive_path}")
        continue

    temp_archive_path = archive_path + "_temp"

    with zipfile.ZipFile(archive_path, 'r') as archive:
        with zipfile.ZipFile(temp_archive_path, 'w') as temp_archive:
            for item in archive.infolist():
                new_info = zipfile.ZipInfo(item.filename, date_time=new_date)
                new_info.external_attr = item.external_attr
                data = archive.read(item.filename)
                temp_archive.writestr(new_info, data)

    shutil.move(temp_archive_path, archive_path)
    print(f"Даты файлов в {archive_path} установлены на 2020 год")
