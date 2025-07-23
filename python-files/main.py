# -*- coding: utf-8 -*-

import os
import sys
from pymxs import runtime as rt

# PySide2 v? ya PySide6 modulunu y�kl?yirik, hansisi varsa onu istifad? edirik
def VersionPysideLoadMax():
    global IS_PYSIDE6  # Bunu ?lav? edirik
    # PySide2 v? ya PySide6 modulunu y�kl?yirik
    try:
        from PySide2.QtWidgets import (
            QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
            QComboBox, QFrame, QMessageBox, QGridLayout, QSizePolicy, QScrollArea
        )
        from PySide2.QtCore import Qt, QSize
        from PySide2.QtGui import QIcon, QPixmap, QColor
        IS_PYSIDE6 = False
        print("?? PySide2 istifad? olunur")
    except ImportError:
        from PySide6.QtWidgets import (
            QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
            QComboBox, QFrame, QMessageBox, QGridLayout, QSizePolicy, QScrollArea
        )
        from PySide6.QtCore import Qt, QSize
        from PySide6.QtGui import QIcon, QPixmap, QColor
        IS_PYSIDE6 = True
        print("?? PySide6 istifad? olunur")







# 3ds Max versiyasinin ?sas qovlugunu tapmaq ���n funksiya
VersionPysideLoadMax()



def find_3dsmax_folder(sub_path):
    
    base_dir = r"C:\Program Files\Autodesk"
    if not os.path.exists(base_dir):
        return None
    versions = [d for d in os.listdir(base_dir) if d.startswith("3ds Max")]
    if not versions:
        return None
    versions.sort(reverse=True)  # Yeni versiyani se�irik
    latest = versions[0]
    return os.path.join(base_dir, latest, sub_path)
    
    
    
    # Material kitabxanalarinin fayl v? preview s?kil yollari
LIBRARY_PATHS = {
    "CollageMaterial": find_3dsmax_folder(r"scripts\LordFred_Tools\MaterialInteryer\CollageMaterial\CollageMat.mat"),
    "Fabric": find_3dsmax_folder(r"scripts\LordFred_Tools\MaterialInteryer\Fabric\fabric.mat"),
    "Stone": find_3dsmax_folder(r"scripts\LordFred_Tools\MaterialInteryer\Stone\Stone.mat")
}

PREVIEW_PATHS = {
    "CollageMaterial": find_3dsmax_folder(r"scripts\LordFred_Tools\MaterialInteryer\CollageMaterial\Preview"),
    "Fabric": find_3dsmax_folder(r"scripts\LordFred_Tools\MaterialInteryer\Fabric\Preview"),
    "Stone": find_3dsmax_folder(r"scripts\LordFred_Tools\MaterialInteryer\Stone\Preview")
}
# Icon faylinin yeri
ICON_INTERYER = find_3dsmax_folder(r"scripts\LordFred_Tools\iconFolder\tv.png")
ICON_EKSTIRYER = ICON_INTERYER  # Eyni fayl istifad? olunur



# Render d�ym?sin? klikl?ndikd? se�ilmis render �l��s�n� g�t�r�r v? render scriptini is? salir.
def renderResulationClick():
    resolution = resolution_combo.currentText()
    width, height = resolution.split("x")
    script_path = find_3dsmax_folder(os.path.join("scripts", "LordFred_Tools", "ScriptFolder", "renderResulation.ms"))

    if not script_path or not os.path.exists(script_path):
        status_label.setText("?? renderResulation.ms tapilmadi.")
        return
    try:
        rt.execute(f'renderWidth = {width}')
        rt.execute(f'renderHeight = {height}')
        with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        rt.execute(content)
        status_label.setText("? Render script isl?yir!")
    except Exception as e:
        status_label.setText(f"? X?ta: {e}")
        
        
        
        
        
        
        
        

# Instagram link scriptini is? salmaq ���n funksiya
def urlLinkclick():
    script_path = find_3dsmax_folder(os.path.join("scripts", "LordFred_Tools", "ScriptFolder", "linkUrl.ms"))
    if not script_path or not os.path.exists(script_path):
        status_label.setText("?? linkUrl.ms tapilmadi.")
        return
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(script_path, "r", encoding="latin-1") as f:
            content = f.read()
    try:
        rt.execute(content)
        status_label.setText("? Script isl?yir!")
    except Exception as e:
        status_label.setText(f"? Script x?tasi: {e}")

# Sag paneld?ki m�vcud widgetlari silm?k ���n funksiya
def clear_right_panel():
    while right_layout.count():
        item = right_layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

# Model faylini 3ds Max-? merge etm?k ���n funksiya
def merge_model(file_path):
    try:
        if os.path.exists(file_path):
            rt.mergeMaxFile(file_path, autoRenameDups=True, quiet=True)
            status_label.setText(f"? Model merge edildi: {os.path.basename(file_path)}")
        else:
            status_label.setText(f"?? Fayl tapilmadi: {file_path}")
    except Exception as e:
        status_label.setText(f"? Merge x?tasi: {e}")

# Material kitabxanasini y�kl?m?k ���n funksiya
def load_materials(mat_path):
    if os.path.isfile(mat_path):
        return rt.loadTempMaterialLibrary(mat_path)
    return None

# Preview s?kil faylini tapmaq ���n funksiya (material adina g�r?)
def find_preview(preview_path, mat_name):
    mat_name_clean = mat_name.replace(" ", "_").lower()
    if not os.path.isdir(preview_path):
        return ""
    for f in os.listdir(preview_path):
        if f.lower().endswith(".png"):
            name, _ = os.path.splitext(f)
            if name.lower() == mat_name_clean:
                return os.path.join(preview_path, f)
    return ""

# Se�ilmis obyektl?r? material t?tbiq ed?n funksiya
def apply_material(materials, index):
    mat = materials[index]
    selected_objs = rt.selection
    if selected_objs.count == 0:
        #QMessageBox.warning(None, "X?ta", "He� bir obyekt se�ilm?yib!")
        return
    for obj in selected_objs:
        obj.material = mat
        print(f"{obj.name} -> {mat.name}")
    #QMessageBox.information(None, "OK", f"'{mat.name}' t?tbiq edildi!")

# Material ���n d�ym? yaradan funksiya, preview varsa g�st?rir

 btn = QPushButton(name)
    btn.setIconSize(QSize(64, 64))
    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    if preview:
        btn.setIcon(QIcon(QPixmap(preview)))
    else:
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("gray"))
        btn.setIcon(QIcon(pixmap))

    btn.setStyleSheet("""
        QPushButton {
            text-align: bottom center;
            font-weight: bold;
            color: white;
            padding: 4px;
            border-radius: 6px;
            background-color: #444444;
        }
        QPushButton:hover {
            background-color: #555555;
        }
    """)
    btn.clicked.connect(lambda: apply_material(materials, index))
    return btn
    
    

# Material b�lm?si yaradir, basliq v? i�ind?ki material d�ym?l?ri il?
def create_material_button(name, preview, index, materials):
    btn = QPushButton(name)
    btn.setIconSize(QSize(64, 64))
    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    if preview:
        btn.setIcon(QIcon(QPixmap(preview)))
    else:
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor("gray"))
        btn.setIcon(QIcon(pixmap))

    btn.setStyleSheet("""
        QPushButton {
            text-align: bottom center;
            font-weight: bold;
            color: white;
            padding: 4px;
            border-radius: 6px;
            background-color: #444444;
        }
        QPushButton:hover {
            background-color: #555555;
        }
    """)
    btn.clicked.connect(lambda: apply_material(materials, index))
    return btn

    btn = QPushButton()
    btn.setIconSize(QSize(100, 100))
    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    if preview:
        btn.setIcon(QIcon(QPixmap(preview)))
    else:
        pixmap = QPixmap(100, 100)
        pixmap.fill(QColor("gray"))
        btn.setIcon(QIcon(pixmap))

    btn.setStyleSheet("""
        QPushButton {
            border-radius: 6px;
            
            border: none;
        }
        QPushButton:hover {
            cursor: pointer;
        }
    """)
    btn.clicked.connect(lambda: apply_material(materials, index))
    return btn

# Material b�lm?si yaratma funksiyasi (adlar previewlarin altinda ayrica QLabel kimi)
def create_material_section(title, mat_path, preview_path):
    section_widget = QWidget()
    layout = QVBoxLayout(section_widget)
    layout.setContentsMargins(4, 4, 4, 4)
    layout.setSpacing(4)

    header_layout = QHBoxLayout()
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(2)
    label = QLabel(f"<b>{title}</b>")
    toggle_btn = QPushButton("+")
    toggle_btn.setFixedWidth(30)
    toggle_btn.setStyleSheet("""
        background-color: #444444;
        color: white;
        font-weight: bold;
        border-radius: 4px;
    """)
    header_layout.addWidget(label)
    header_layout.addStretch()
    header_layout.addWidget(toggle_btn)
    layout.addLayout(header_layout)

    content_widget = QWidget()
    content_widget.setVisible(False)
    content_layout = QGridLayout(content_widget)
    content_layout.setSpacing(8)
    content_layout.setContentsMargins(4, 4, 4, 4)
    layout.addWidget(content_widget)

    materials = load_materials(mat_path)
    if not materials or not hasattr(materials, "count") or materials.count == 0:
        status_label.setText(f"?? {title} material tapilmadi.")
        return section_widget

    def toggle_expand():
        expanded = not content_widget.isVisible()
        toggle_btn.setText("-" if expanded else "+")
        content_widget.setVisible(expanded)
        if expanded and content_layout.count() == 0:
            columns = 4
            row = 0
            col = 0
            for i in range(materials.count):
                mat = materials[i]
                preview = find_preview(preview_path, mat.name)

                # Preview d�ym?
                btn = create_material_button(preview, i, materials)

                # Ad QLabel
                name_label = QLabel(mat.name)
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setStyleSheet("color: white; font-weight: bold;")

                # Bir layoutda (vertical) preview v? adi yerl?sdiririk
                item_widget = QWidget()
                item_layout = QVBoxLayout(item_widget)
                item_layout.setContentsMargins(2, 2, 2, 2)
                item_layout.setSpacing(2)
                item_layout.addWidget(btn)
                item_layout.addWidget(name_label)

                content_layout.addWidget(item_widget, row, col)
                col += 1
                if col >= columns:
                    col = 0
                    row += 1

    toggle_btn.clicked.connect(toggle_expand)
    return section_widget
    section_widget = QWidget()
    layout = QVBoxLayout(section_widget)
    layout.setContentsMargins(4, 4, 4, 4)
    layout.setSpacing(4)

    header_layout = QHBoxLayout()
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(2)
    label = QLabel(f"<b>{title}</b>")
    toggle_btn = QPushButton("+")
    toggle_btn.setFixedWidth(30)
    toggle_btn.setStyleSheet("""
        background-color: #444444;
        color: white;
        font-weight: bold;
        border-radius: 4px;
    """)
    header_layout.addWidget(label)
    header_layout.addStretch()
    header_layout.addWidget(toggle_btn)
    layout.addLayout(header_layout)

    content_widget = QWidget()
    content_widget.setVisible(False)  # Baslangicda gizlidir
    content_layout = QGridLayout(content_widget)
    content_layout.setSpacing(6)
    content_layout.setContentsMargins(4, 4, 4, 4)
    layout.addWidget(content_widget)

    materials = load_materials(mat_path)
    if not materials or not hasattr(materials, "count") or materials.count == 0:
        status_label.setText(f"?? {title} material tapilmadi.")
        return section_widget

    def toggle_expand():
        expanded = not content_widget.isVisible()
        toggle_btn.setText("-" if expanded else "+")
        content_widget.setVisible(expanded)
        if expanded and content_layout.count() == 0:
            columns = 4
            row = 0
            col = 0
            for i in range(materials.count):
                mat = materials[i]
                preview = find_preview(preview_path, mat.name)
                btn = create_material_button(mat.name, preview, i, materials)
                content_layout.addWidget(btn, row, col)
                col += 1
                if col >= columns:
                    col = 0
                    row += 1

    toggle_btn.clicked.connect(toggle_expand)
    return section_widget

# Sag panel? material b�lm?l?rini ?lav? ed?n funksiya
def interyermaterialAdd():
    for idx, key in enumerate(LIBRARY_PATHS):
        section = create_material_section(key, LIBRARY_PATHS[key], PREVIEW_PATHS[key])
        right_layout.addWidget(section)
        # B�lm?l?r arasinda x?tt ?lav? edirik
        if idx < len(LIBRARY_PATHS) - 1:
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet("background-color: #666666; height: 0.5px; margin: 2px 0;")
            right_layout.addWidget(line)
    status_label.setText("? Material b�lm?si y�kl?ndi.")

# Sol v? orta panell?rd?ki d�ym?l?r? klikl? �agirilan funksiya
def clickList(name):
    print(f"?? {name} d�ym?sin? klik edildi!")
    clear_right_panel()  # Sag paneli t?mizl?yirik

    if name == "interiorMaterial":
        interyermaterialAdd()  # Material b�lm?sini y�kl?

    elif name == "interiorModel":
        models_dir = r"C:\Program Files\Autodesk\3ds Max 2023\scripts\LordFred_Tools\InteriorDesignModel\Model"
        if not os.path.exists(models_dir):
            status_label.setText(f"?? Qovluq tapilmadi: {models_dir}")
            return

        models = [f for f in os.listdir(models_dir) if f.lower().endswith(".max")]
        if not models:
            status_label.setText(f"?? He� bir .max fayli tapilmadi: {models_dir}")
            return

        for model in models:
            full_path = os.path.join(models_dir, model)
            btn = QPushButton(model)
            btn.setStyleSheet("""
                background-color: #AAAAAA;
                color: black;
                font-weight: bold;
                padding: 6px;
                border-radius: 4px;
            """)
            btn.clicked.connect(lambda checked=False, p=full_path: merge_model(p))
            right_layout.addWidget(btn)
        status_label.setText(f"? {len(models)} model tapildi.")
    else:
        status_label.setText(f"?? '{name}' ���n funksiya hazirlanmayib.")

# Sol v? orta panell?rd? b�lm?l?r yaratmaq ���n funksiya
def create_list_section(title, button_texts):
    container = QFrame()
    container.setStyleSheet("""
        background-color: #555555;
        border-radius: 6px;
    """)
    section_layout = QVBoxLayout(container)
    section_layout.setContentsMargins(4, 4, 4, 4)
    section_layout.setSpacing(3)

    main_btn = QPushButton(title)
    main_btn.setStyleSheet("""
        background-color: #777777;
        color: white;
        font-weight: bold;
        padding: 6px;
        border: none;
        border-radius: 4px;
    """)
    section_layout.addWidget(main_btn)

    sub_frame = QFrame()
    sub_layout = QVBoxLayout(sub_frame)
    sub_layout.setContentsMargins(16, 0, 0, 0)
    sub_layout.setSpacing(2)

    for text in button_texts:
        btn = QPushButton(text)
        btn.setStyleSheet("""
            background-color: #888888;
            color: white;
            padding: 5px;
            border: none;
            border-radius: 3px;
        """)
        btn.clicked.connect(lambda checked=False, t=text: clickList(t))
        sub_layout.addWidget(btn)

    sub_frame.setVisible(False)
    section_layout.addWidget(sub_frame)

    def toggle():
        sub_frame.setVisible(not sub_frame.isVisible())
    main_btn.clicked.connect(toggle)

    layout = QVBoxLayout()
    layout.addWidget(container)
    return layout

# Proqramin baslangici v? ?sas p?nc?r? qurulusu
app = QApplication.instance()
if not app:
    app = QApplication([])

window = QWidget()
window.setWindowTitle("LordFred Tool")
window.resize(900, 600)

# Status mesajlarini g�st?rm?k ���n QLabel
status_label = QLabel("")
status_label.setStyleSheet("color: white; font-weight: bold;")

# --- Yuxari panel --- #
top_layout = QHBoxLayout()
name_label = QLabel("Library")
name_label.setStyleSheet("font-weight: bold; font-size: 18px; color: white;")

resolution_combo = QComboBox()
resolution_combo.addItems(["1800x2200", "2500x1800", "3500x2500", "2000x3000", "1800x1800"])
resolution_combo.setFixedWidth(120)

render_button = QPushButton("Render")
render_button.setStyleSheet("""
    background-color: #777777;
    color: white;
    font-weight: bold;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
""")
render_button.clicked.connect(renderResulationClick)

top_layout.addWidget(name_label, alignment=Qt.AlignLeft)
top_layout.addStretch()
top_layout.addWidget(QLabel("List render resolution:"))
top_layout.addWidget(resolution_combo)
top_layout.addWidget(render_button)

# --- M?rk?zi b�lm? (Sol, Orta, Sag) --- #
center_layout = QHBoxLayout()

# --- Sol panel --- #
left_layout = QVBoxLayout()
left_layout.setSpacing(5)

btn_interyer = QPushButton("Selection Interyer Setup")
btn_interyer.setStyleSheet("""
    background-color: #555555;
    color: white;
    font-weight: bold;
    padding: 8px;
    border-radius: 6px;
    cursor: pointer;
""")
btn_interyer.setLayoutDirection(Qt.LeftToRight)

# Icon ?lav? edirik
if os.path.exists(ICON_INTERYER):
    btn_interyer.setIcon(QIcon(ICON_INTERYER))
    btn_interyer.setIconSize(QSize(24, 24))

# Interyer setup d�ym?sin? klikl? rpsSetup.ms scripti icra edilir
def on_interyer_clicked():
    script_path = find_3dsmax_folder(os.path.join("scripts", "LordFred_Tools", "ScriptFolder", "rpsSetup.ms"))
    if not script_path or not os.path.exists(script_path):
        status_label.setText("?? rpsSetup.ms tapilmadi.")
        return
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(script_path, "r", encoding="latin-1") as f:
            content = f.read()
    try:
        rt.execute(content)
        status_label.setText("? rpsSetup.ms script isl?di!")
    except Exception as e:
        status_label.setText(f"? Script x?tasi: {e}")

btn_interyer.clicked.connect(on_interyer_clicked)
left_layout.addWidget(btn_interyer)

# Sol paneld? 3 siyahi yaradilir, h?r siyahi ���n d�ym?l?r ?lav? olunur
interior_names = [
    ["interiorMaterial", "interiorModel", "Ceiling"],
    ["Sofa", "Chair", "Table"],
    ["Lamp", "Curtain", "Shelf"]
]

for i in range(1, 4):
    section = create_list_section(f"List {i}", interior_names[i - 1])
    left_layout.addLayout(section)
    if i < 3:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #444; height: 1px; margin: 3px 0;")
        left_layout.addWidget(line)
left_layout.addStretch()

left = QFrame()
left.setStyleSheet("background-color: #666666;")
left.setLayout(left_layout)
left.setMinimumWidth(250)

# --- Orta panel --- #
middle_layout = QVBoxLayout()
middle_layout.setSpacing(5)

btn_eksteryer = QPushButton("Selection Eksteryer Setup")
btn_eksteryer.setStyleSheet("""
    background-color: #555555;
    color: white;
    font-weight: bold;
    padding: 8px;
    border-radius: 6px;
""")

# Icon ?lav? edirik (eyni icon)
if os.path.exists(ICON_EKSTIRYER):
    btn_eksteryer.setIcon(QIcon(ICON_EKSTIRYER))
    btn_eksteryer.setIconSize(QSize(24, 24))

def on_eksteryer_clicked():
    print("selection eksteryer setup")
    status_label.setText("selection eksteryer setup")

btn_eksteryer.clicked.connect(on_eksteryer_clicked)
middle_layout.addWidget(btn_eksteryer)

exterior_names = [
    ["ExteriorMaterial", "ExtiryerModels", "Close"],
    ["Import", "Export", "Merge"],
    ["Option A", "Option B", "Option C"]
]

for i in range(1, 4):
    section = create_list_section(f"List {i}", exterior_names[i - 1])
    middle_layout.addLayout(section)
    if i < 3:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #444; height: 1px; margin: 3px 0;")
        middle_layout.addWidget(line)
middle_layout.addStretch()

middle = QFrame()
middle.setStyleSheet("background-color: #666666;")
middle.setLayout(middle_layout)
middle.setMinimumWidth(250)

# --- Sag panel (Scroll Area il?) --- #
right_scroll = QScrollArea()
right_scroll.setWidgetResizable(True)
right_scroll.setStyleSheet("background-color: #666666;")

right_container = QWidget()
right_layout = QVBoxLayout(right_container)
right_layout.setContentsMargins(4, 4, 4, 4)
right_layout.setSpacing(6)
right_container.setLayout(right_layout)

right_scroll.setWidget(right_container)

# M?rk?zi b�lm?y? panell?ri ?lav? edirik
center_layout.addWidget(left)
center_layout.addWidget(middle)
center_layout.addWidget(right_scroll)

# --- Asagi panel --- #
bottom_layout = QHBoxLayout()
bottom_layout.addWidget(status_label)  # Status mesaji burda g�st?rilir
bottom_layout.addStretch()

youtube_btn = QPushButton("Link Instagram profile")
youtube_btn.setStyleSheet("""
    background-color: #777777;
    color: white;
    font-weight: bold;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
""")
youtube_btn.clicked.connect(urlLinkclick)
bottom_layout.addStretch()
bottom_layout.addWidget(youtube_btn)

# --- ?sas Layout --- #
main_layout = QVBoxLayout()
main_layout.addLayout(top_layout)
main_layout.addLayout(center_layout)
main_layout.addLayout(bottom_layout)

window.setStyleSheet("background-color: #333333;")  # P?nc?r? arxa fonu
window.setLayout(main_layout)
window.show()

# PySide app d�ng�s� is? d�s�r
if IS_PYSIDE6:
    app.exec()
else:
    app.exec_()
