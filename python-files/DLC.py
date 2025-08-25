import os
import json
import sys
import subprocess
from PyQt5 import QtWidgets
import xml.etree.ElementTree as ET

CONFIG_FILE = "config.json"

# Список популярних дефолтних машин GTA V
DEFAULT_VEHICLES = [
    "adder", "zentorno", "t20", "banshee", "comet2", "elegy2", 
    "sultan", "furoregt", "jester", "dominator", "buffalo2", "coquette"
]

# ---------- Загрузка/сохранение конфига ----------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"gta_path": ""}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- Пошук пов’язаних файлів для .ymap ----------
def find_map_files(map_name, search_dir):
    """Шукає .ymap, .ydr, .ytd файли за назвою карти"""
    map_files = []
    map_name = map_name.lower()

    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.lower().startswith(map_name) and file.endswith(('.ymap', '.ydr', '.ytd')):
                map_files.append(os.path.join(root, file))

    # Парсимо .ymap для пошуку додаткових залежностей
    for file in map_files:
        if file.endswith('.ymap'):
            try:
                tree = ET.parse(file)
                root = tree.getroot()
                for elem in root.iter():
                    if 'name' in elem.attrib:
                        name = elem.attrib['name']
                        if name.endswith(('.ydr', '.ytd')):
                            related_file = os.path.join(search_dir, name)
                            if os.path.exists(related_file) and related_file not in map_files:
                                map_files.append(related_file)
            except Exception as e:
                print(f"Помилка при парсингу {file}: {e}")

    return map_files

# ---------- Пошук файлів дефолтної машини ----------
def find_vehicle_files(vehicle_name, gta_path):
    """Шукає файли дефолтної машини в папці GTA V"""
    vehicle_files = []
    vehicle_name = vehicle_name.lower()
    vehicle_dirs = [
        os.path.join(gta_path, "x64", "vehicles.rpf"),
        os.path.join(gta_path, "update", "x64", "dlcpacks")
    ]

    for dir_path in vehicle_dirs:
        if os.path.exists(dir_path):
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.lower().startswith(vehicle_name) and file.endswith(('.yft', '.ytd')):
                        vehicle_files.append(os.path.join(root, file))

    return vehicle_files

# ---------- Перевірка цілісності файлів ----------
def check_files_integrity(files, is_vehicle=False):
    """Перевіряє наявність необхідних файлів"""
    if not files:
        return False, "Не знайдено жодного файлу"
    
    if is_vehicle:
        has_yft = any(f.endswith('.yft') for f in files)
        has_ytd = any(f.endswith('.ytd') for f in files)
        if not has_yft:
            return False, "Відсутній файл моделі (.yft)"
        if not has_ytd:
            return False, "Відсутній файл текстур (.ytd)"
    else:
        has_ymap = any(f.endswith('.ymap') for f in files)
        if not has_ymap:
            return False, "Відсутній файл карти (.ymap)"

    return True, "Усі необхідні файли знайдено"

# ---------- Створення vehicles.meta для машини ----------
def create_vehicles_meta(vehicle_name, dlc_path):
    """Створює базовий vehicles.meta для машини"""
    vehicles_meta = f"""<?xml version="1.0" encoding="UTF-8"?>
<CVehicleModelInfo__InitDataList>
  <residentTxdName>{vehicle_name}</residentTxdName>
  <residentAnims />
  <InitDatas>
    <Item>
      <modelName>{vehicle_name}</modelName>
      <txdName>{vehicle_name}</txdName>
      <handlingId>{vehicle_name.upper()}</handlingId>
      <gameName>{vehicle_name.upper()}</gameName>
      <vehicleMakeName />
      <expressionDictName />
      <type>VEHICLE_TYPE_CAR</type>
      <flags>FLAG_NO_BOOT FLAG_HAS_INTERIOR</flags>
      <layout>LAYOUT_STANDARD</layout>
      <modelFlags>0x400000</modelFlags>
      <handlingFlags>0x0</handlingFlags>
      <damageFlags>0x0</damageFlags>
      <anims>
        <Item />
      </anims>
    </Item>
  </InitDatas>
</CVehicleModelInfo__InitDataList>
"""
    meta_path = os.path.join(dlc_path, "dlc.rpf", "common", "data")
    os.makedirs(meta_path, exist_ok=True)
    with open(os.path.join(meta_path, "vehicles.meta"), "w", encoding="utf-8") as f:
        f.write(vehicles_meta)

# ---------- Створення DLC ----------
def create_dlc(files, dlc_name, output_dir, is_vehicle=False):
    """Створює DLC-пак для карти або машини"""
    dlc_path = os.path.join(output_dir, dlc_name)
    rpf_path = os.path.join(dlc_path, "dlc.rpf", "x64", "levels", "gta5", "custom_maps" if not is_vehicle else "vehicles")
    os.makedirs(rpf_path, exist_ok=True)

    # Копіюємо файли
    for file_path in files:
        target_file = os.path.join(rpf_path, os.path.basename(file_path))
        if os.path.exists(file_path):
            with open(file_path, "rb") as src, open(target_file, "wb") as dst:
                dst.write(src.read())
        else:
            with open(target_file, "w") as f:
                f.write("")

    # Створюємо vehicles.meta для машин
    if is_vehicle:
        create_vehicles_meta(dlc_name.replace("_dlc", ""), dlc_path)

    # ---------- content.xml ----------
    content_xml = """<?xml version="1.0" encoding="UTF-8"?>\n<content>\n"""
    if is_vehicle:
        content_xml += "  <vehicleFiles>\n"
        content_xml += f"""    <Item>
      <filename>dlc_{dlc_name}:/common/data/vehicles.meta</filename>
      <fileType>VEHICLE_METADATA_FILE</fileType>
      <locked>false</locked>
    </Item>\n"""
    else:
        content_xml += "  <dataFiles>\n"
    
    for file_path in files:
        file_type = 'MAP' if file_path.endswith('.ymap') else 'MODEL' if file_path.endswith(('.ydr', '.yft')) else 'TEXTURE'
        content_xml += f"""    <Item>
      <filename>dlc_{dlc_name}:/x64/levels/gta5/{"vehicles" if is_vehicle else "custom_maps"}/{os.path.basename(file_path)}</filename>
      <fileType>{file_type}</fileType>
      <locked>false</locked>
    </Item>\n"""
    content_xml += "  </dataFiles>\n</content>\n" if not is_vehicle else "  </vehicleFiles>\n</content>\n"

    with open(os.path.join(dlc_path, "content.xml"), "w", encoding="utf-8") as f:
        f.write(content_xml)

    # ---------- setup2.xml ----------
    setup2_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<SSetup>
  <deviceName>{dlc_name}</deviceName>
  <titleName>{dlc_name}</titleName>
  <dlcName>dlc_{dlc_name}</dlcName>
  <contentChangeSetGroups>
    <Item>
      <Name>{dlc_name}</Name>
      <Type>{"VEHICLE" if is_vehicle else "MAP"}</Type>
    </Item>
  </contentChangeSetGroups>
</SSetup>
"""
    with open(os.path.join(dlc_path, "setup2.xml"), "w", encoding="utf-8") as f:
        f.write(setup2_xml)

    dlclist_line = f"<Item>dlcpacks:/{dlc_name}/</Item>"

    return dlc_path, dlclist_line

# ---------- Автоматичне редагування dlclist.xml ----------
def update_dlclist(gta_path, dlclist_line):
    """Додає рядок до dlclist.xml"""
    dlclist_path = os.path.join(gta_path, "mods", "update", "update.rpf", "common", "data", "dlclist.xml")
    if not os.path.exists(dlclist_path):
        dlclist_path = os.path.join(gta_path, "update", "update.rpf", "common", "data", "dlclist.xml")
        if not os.path.exists(dlclist_path):
            return False, "Не знайдено dlclist.xml"

    try:
        tree = ET.parse(dlclist_path)
        root = tree.getroot()
        paths = root.find("Paths")
        if paths is None:
            paths = ET.SubElement(root, "Paths")
        
        # Перевіряємо, чи рядок уже є
        for item in paths.findall("Item"):
            if item.text == f"dlcpacks:/{dlclist_line.split('/')[-2]}/":
                return True, "DLC уже додано до dlclist.xml"

        # Додаємо новий рядок
        new_item = ET.SubElement(paths, "Item")
        new_item.text = dlclist_line.split('<Item>')[1].split('</Item>')[0]
        tree.write(dlclist_path, encoding="utf-8", xml_declaration=True)
        return True, "dlclist.xml успішно оновлено"
    except Exception as e:
        return False, f"Помилка при оновленні dlclist.xml: {e}"

# ---------- GUI ----------
class MapperApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GTA V Mapper & Vehicle Tool")
        self.setGeometry(200, 200, 500, 600)

        self.config = load_config()
        layout = QtWidgets.QVBoxLayout()

        # Поле для GTA V
        self.gta_path_input = QtWidgets.QLineEdit(self.config.get("gta_path", ""))
        browse_gta_btn = QtWidgets.QPushButton("Выбрать папку GTA V")
        browse_gta_btn.clicked.connect(self.browse_gta)
        layout.addWidget(QtWidgets.QLabel("Путь к GTA V:"))
        layout.addWidget(self.gta_path_input)
        layout.addWidget(browse_gta_btn)

        # Поле для папки з файлами карти
        self.search_dir_input = QtWidgets.QLineEdit()
        browse_dir_btn = QtWidgets.QPushButton("Выбрать папку с файлами карты")
        browse_dir_btn.clicked.connect(self.browse_search_dir)
        layout.addWidget(QtWidgets.QLabel("Папка с файлами карты (.ymap, .ydr, .ytd):"))
        layout.addWidget(self.search_dir_input)
        layout.addWidget(browse_dir_btn)

        # Поле для назви карти
        self.map_name_input = QtWidgets.QLineEdit()
        layout.addWidget(QtWidgets.QLabel("Название части карты (без расширения):"))
        layout.addWidget(self.map_name_input)

        # Випадаюче меню для машин
        self.vehicle_combo = QtWidgets.QComboBox()
        self.vehicle_combo.addItem("Выберите машину (опционально)", "")
        for vehicle in DEFAULT_VEHICLES:
            self.vehicle_combo.addItem(vehicle, vehicle)
        layout.addWidget(QtWidgets.QLabel("Дефолтная машина:"))
        layout.addWidget(self.vehicle_combo)

        # Список знайдених файлів
        self.files_text = QtWidgets.QTextEdit()
        self.files_text.setReadOnly(True)
        layout.addWidget(QtWidgets.QLabel("Найденные файлы:"))
        layout.addWidget(self.files_text)

        # Кнопка пошуку файлів
        find_btn = QtWidgets.QPushButton("Найти файлы")
        find_btn.clicked.connect(self.find_files)
        layout.addWidget(find_btn)

        # Кнопка створення DLC
        generate_btn = QtWidgets.QPushButton("Собрать DLC")
        generate_btn.clicked.connect(self.generate_dlc)
        layout.addWidget(generate_btn)

        # Чекбокс для автоматичного оновлення dlclist.xml
        self.update_dlclist_check = QtWidgets.QCheckBox("Автоматически обновить dlclist.xml")
        layout.addWidget(self.update_dlclist_check)

        # Кнопка очищення полів
        clear_btn = QtWidgets.QPushButton("Очистить поля")
        clear_btn.clicked.connect(self.clear_fields)
        layout.addWidget(clear_btn)

        # Кнопка відкриття папки
        self.open_folder_btn = QtWidgets.QPushButton("Открыть папку DLC")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self.open_dlc_folder)
        layout.addWidget(self.open_folder_btn)

        # Вивід dlclist.xml
        self.result_text = QtWidgets.QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(QtWidgets.QLabel("Добавь это в dlclist.xml (если не оновлено автоматично):"))
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def browse_gta(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Укажи папку GTA V")
        if folder:
            self.gta_path_input.setText(folder)

    def browse_search_dir(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Укажи папку с файлами карты")
        if folder:
            self.search_dir_input.setText(folder)

    def clear_fields(self):
        """Очищає поля для наступного введення"""
        self.map_name_input.clear()
        self.vehicle_combo.setCurrentIndex(0)
        self.files_text.clear()
        self.result_text.clear()
        self.open_folder_btn.setEnabled(False)
        self.file_list = []

    def find_files(self):
        gta_path = self.gta_path_input.text()
        search_dir = self.search_dir_input.text()
        map_name = self.map_name_input.text().strip()
        vehicle_name = self.vehicle_combo.currentData()

        if not gta_path or not os.path.exists(gta_path):
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Укажи правильный путь к GTA V")
            return

        self.file_list = []
        is_vehicle = bool(vehicle_name)
        if map_name:
            if not search_dir or not os.path.exists(search_dir):
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Укажи папку с файлами карты")
                return
            self.file_list.extend(find_map_files(map_name, search_dir))

        if vehicle_name:
            self.file_list.extend(find_vehicle_files(vehicle_name, gta_path))

        # Перевірка цілісності
        success, message = check_files_integrity(self.file_list, is_vehicle)
        if not success:
            QtWidgets.QMessageBox.warning(self, "Ошибка", message)
            return

        self.files_text.setPlainText("\n".join(self.file_list))

    def generate_dlc(self):
        gta_path = self.gta_path_input.text()
        map_name = self.map_name_input.text().strip()
        vehicle_name = self.vehicle_combo.currentData()

        if not gta_path or not os.path.exists(gta_path):
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Укажи правильный путь к GTA V")
            return

        if not self.file_list:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сначала найди файлы")
            return

        # Запитуємо папку для збереження DLC
        output_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Выбери папку для сохранения DLC")
        if not output_dir:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выбери папку для сохранения")
            return

        # Зберігаємо конфіг
        self.config["gta_path"] = gta_path
        save_config(self.config)

        # Визначаємо ім’я DLC
        dlc_name = map_name or vehicle_name or "custom_dlc"
        dlc_name = f"{dlc_name}_dlc"
        is_vehicle = bool(vehicle_name)

        # Створюємо DLC
        self.generated_paths = []
        dlc_path, dlclist_line = create_dlc(self.file_list, dlc_name, output_dir, is_vehicle)
        self.generated_paths.append(dlc_path)
        self.result_text.setPlainText(dlclist_line)

        # Автоматичне оновлення dlclist.xml
        if self.update_dlclist_check.isChecked():
            success, message = update_dlclist(gta_path, dlclist_line)
            if not success:
                QtWidgets.QMessageBox.warning(self, "Ошибка", message)
            else:
                QtWidgets.QMessageBox.information(self, "Успех", message)

        self.open_folder_btn.setEnabled(True)
        QtWidgets.QMessageBox.information(self, "Готово", f"Создан DLC: {dlc_path}")

    def open_dlc_folder(self):
        if self.generated_paths:
            path = os.path.abspath(os.path.dirname(self.generated_paths[0]))
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

# ---------- Запуск ----------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MapperApp()
    window.show()
    sys.exit(app.exec_())