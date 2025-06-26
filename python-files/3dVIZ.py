import sys
import math
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QButtonGroup, QLabel, QGroupBox, QDoubleSpinBox,
                             QFormLayout, QListWidget, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
class Line:
    def __init__(self, start=None, direction=None):
        self.start = start if start is not None else [0.0, 0.0, 0.0]
        self.direction = direction if direction is not None else [1.0, 0.0, 0.0]
        self.length = 5.0
        self.color = (1.0, 0.0, 0.0, 1.0)  # Красный по умолчанию
        self.selected = False

    def set_start(self, x, y, z):
        self.start = [x, y, z]
        
    def set_direction(self, dx, dy, dz):
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        if length > 1e-5:
            self.direction = [dx/length, dy/length, dz/length]
    
    # Добавлен метод для изменения длины
    def set_length(self, length):
        if length > 0:
            self.length = length

class GeometryVisualizer(QGLWidget):
    def __init__(self, parent=None):
        super(GeometryVisualizer, self).__init__(parent)
        self.setMinimumSize(800, 600)
        
        # Параметры камеры
        self.zoom = -10.0
        self.rotation_x = 30.0
        self.rotation_y = 30.0
        self.last_pos = None
        self.current_mouse_pos = (0, 0)  # Текущее положение мыши
        
        # Параметры фигуры
        self.current_shape = "cube"
        self.shapes = {
            "cube": self.draw_cube,
            "pyramid": self.draw_pyramid,
            "sphere": self.draw_sphere,
            "cylinder": self.draw_cylinder,
            "cone": self.draw_cone
        }
        
        # Система управления прямыми
        self.lines = []
        self.temp_points = []
        self.dragging_line = None
        self.drag_start_pos = None
        self.mode = "view"  # Режимы: view, add_line, move_line
        self.move_sensitivity = 3.0  # Чувствительность перемещения

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.95, 0.95, 0.95, 1.0)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)
        
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # Вручную создаем матрицу перспективы
        aspect = width / height if height != 0 else 1.0
        near, far = 0.1, 100.0
        fov = 45.0
        
        # Рассчитываем перспективную проекцию
        top = near * math.tan(math.radians(fov) / 2.0)
        bottom = -top
        right = top * aspect
        left = -right
        
        glFrustum(left, right, bottom, top, near, far)
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Позиция камеры
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        
        # Оси координат (Y и Z поменяны местами)
        self.draw_axes()
        
        # Текущая фигура
        if self.current_shape in self.shapes:
            self.shapes[self.current_shape]()
        
        # Рисуем прямые поверх фигур с отключенным тестом глубины
        glDisable(GL_DEPTH_TEST)  # Отключаем тест глубины для линий
        self.draw_lines()
        glEnable(GL_DEPTH_TEST)   # Включаем обратно
        
        # Рисуем временные точки при построении прямой
        self.draw_temp_points()
        
    def draw_lines(self):
        glLineWidth(3.0)
        for line in self.lines:
            if line.selected:
                glColor4f(0.0, 1.0, 0.0, 1.0)  # Зеленый для выбранной прямой
            else:
                glColor4f(*line.color)
            
            start = line.start
            direction = line.direction
            half_length = line.length / 2.0
            
            end1 = [
                start[0] - direction[0] * half_length,
                start[1] - direction[1] * half_length,
                start[2] - direction[2] * half_length
            ]
            
            end2 = [
                start[0] + direction[0] * half_length,
                start[1] + direction[1] * half_length,
                start[2] + direction[2] * half_length
            ]
            
            glBegin(GL_LINES)
            glVertex3fv(end1)
            glVertex3fv(end2)
            glEnd()
    
    def draw_temp_points(self):
        if self.mode == "add_line" and self.temp_points:
            glPointSize(8.0)
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_POINTS)
            for point in self.temp_points:
                glVertex3fv(point)
            glEnd()
            
            # Рисуем линию от последней точки к курсору
            if len(self.temp_points) == 1:
                # Получаем позицию курсора в мировых координатах
                cursor_pos = self.get_world_pos(self.current_mouse_pos[0], self.current_mouse_pos[1])
                if cursor_pos is not None:
                    glLineWidth(1.5)
                    glColor4f(1.0, 0.0, 0.0, 0.7)
                    glBegin(GL_LINES)
                    glVertex3fv(self.temp_points[0])
                    glVertex3fv(cursor_pos)
                    glEnd()
    
    def get_world_pos(self, x, y, z=0.0):
        try:
            # Преобразование координат экрана в мировые координаты
            viewport = glGetIntegerv(GL_VIEWPORT)
            mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
            projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
            
            # Проверка на наличие матриц
            if mvmatrix is None or projmatrix is None:
                return None
                
            winX = x
            winY = viewport[3] - y
            winZ = z
            
            # Получаем мировые координаты
            world_pos = gluUnProject(winX, winY, winZ, mvmatrix, projmatrix, viewport)
            return world_pos
        except:
            return None
    
    def draw_axes(self):
        glLineWidth(2.0)
        glBegin(GL_LINES)
        # X (красный)
        glColor3f(0.8, 0.2, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(3.0, 0.0, 0.0)
        
        # Z (зеленый) - теперь вертикальная ось
        glColor3f(0.2, 0.7, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 3.0)
        
        # Y (синий) - теперь горизонтальная ось "вглубь"
        glColor3f(0.2, 0.4, 0.9)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 3.0, 0.0)
        glEnd()
        
        self.renderText(3.2, 0.0, 0.0, "X")
        self.renderText(0.0, 3.2, 0.0, "Y")
        self.renderText(0.0, 0.0, 3.2, "Z")
        
    def draw_arrow_cone(self, radius=0.1, height=0.3):
        slices = 8
        # Боковая поверхность конуса
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.0, height, 0.0)  # Вершина
        for i in range(slices+1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, 0.0, z)
        glEnd()
        
        # Основание конуса
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0.0, 0.0, 0.0)
        for i in range(slices+1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, 0.0, z)
        glEnd()
        
    def draw_cube(self):
        # Кубик строится из начала координат (Y и Z поменяны местами)
        vertices = [
            [0, 0, 0], [2, 0, 0], [2, 2, 0], [0, 2, 0],  # Нижняя грань
            [0, 0, 2], [2, 0, 2], [2, 2, 2], [0, 2, 2]   # Верхняя грань
        ]
        
        faces = [
            [0, 1, 2, 3],  # Низ (Z=0)
            [4, 5, 6, 7],  # Верх (Z=2)
            [0, 4, 7, 3],  # Лево (Y=0)
            [1, 5, 6, 2],  # Право (Y=2)
            [0, 1, 5, 4],  # Перед (X=0)
            [3, 2, 6, 7]   # Зад (X=2)
        ]
        
        # Мягкие пастельные цвета
        colors = [
            [0.95, 0.65, 0.75, 0.7],  # Розовый
            [0.65, 0.85, 0.65, 0.7],  # Зеленый
            [0.70, 0.75, 0.95, 0.7],  # Голубой
            [0.95, 0.85, 0.55, 0.7],  # Желтый
            [0.85, 0.65, 0.85, 0.7],  # Фиолетовый
            [0.65, 0.85, 0.85, 0.7]   # Бирюзовый
        ]
        
        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            glColor4fv(colors[i])
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
        
    def draw_pyramid(self):
        vertices = [
            [0, 2, 0],   # Верх
            [-1, 0, 1], # Перед-лево
            [1, 0, 1],  # Перед-право
            [1, 0, -1], # Зад-право
            [-1, 0, -1]  # Зад-лево
        ]
        
        faces = [
            [0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1], # Боковые
            [1, 2, 3, 4] # Основание
        ]
        
        # Нежный бирюзовый
        glColor4f(0.4, 0.8, 0.8, 0.7)
        
        # Боковые грани
        glBegin(GL_TRIANGLES)
        for i in range(4):
            glVertex3fv(vertices[faces[i][0]])
            glVertex3fv(vertices[faces[i][1]])
            glVertex3fv(vertices[faces[i][2]])
        glEnd()
        
        # Основание (немного темнее)
        glColor4f(0.3, 0.7, 0.7, 0.7)
        glBegin(GL_QUADS)
        for vertex in faces[4]:
            glVertex3fv(vertices[vertex])
        glEnd()
        
    def draw_sphere(self, radius=1.0, slices=32, stacks=32):
        # Сфера строится из начала координат
        glColor4f(0.98, 0.65, 0.35, 0.7)
        
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + (i) / stacks)
            y0 = radius * math.sin(lat0)  # Бывшая Z-координата
            yr0 = radius * math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + (i+1) / stacks)
            y1 = radius * math.sin(lat1)
            yr1 = radius * math.cos(lat1)
            
            glBegin(GL_QUAD_STRIP)
            for j in range(slices+1):
                lng = 2 * math.pi * (j) / slices
                x = math.cos(lng)
                z = math.sin(lng)  # Бывшая Y-координата
                
                glNormal3f(x * yr0, y0, z * yr0)
                glVertex3f(x * yr0, y0, z * yr0)
                
                glNormal3f(x * yr1, y1, z * yr1)
                glVertex3f(x * yr1, y1, z * yr1)
            glEnd()
        
    def draw_cylinder(self, radius=0.8, height=2.0, slices=32):
        # Цилиндр строится из начала координат (Y и Z поменяны местами)
        # Нежный фиолетовый
        glColor4f(0.75, 0.55, 0.95, 0.7)
        
        # Боковая поверхность
        glBegin(GL_QUAD_STRIP)
        for i in range(slices+1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)  # Бывшая Y-координата
            
            glNormal3f(x, 0, z)
            glVertex3f(x, height, z)  # Верх
            glVertex3f(x, 0, z)       # Низ
        glEnd()
        
        # Верхняя крышка
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        glVertex3f(0, height, 0)
        for i in range(slices+1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, height, z)
        glEnd()
        
        # Нижняя крышка
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, -1, 0)
        glVertex3f(0, 0, 0)
        for i in range(slices+1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, 0, z)
        glEnd()
        
    def draw_cone(self, radius=0.8, height=2.0, slices=32):
        # Конус строится из начала координат (Y и Z поменяны местами)
        # Свежий зеленый
        glColor4f(0.45, 0.85, 0.55, 0.7)
        
        # Боковая поверхность
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 1, 0)
        glVertex3f(0, height, 0)  # Вершина
        for i in range(slices+1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)  # Бывшая Y-координата
            glVertex3f(x, 0, z)  # Основание
        glEnd()
        
        # Основание
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, -1, 0)
        glVertex3f(0, 0, 0)
        for i in range(slices+1):
            angle = 2 * math.pi * i / slices
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            glVertex3f(x, 0, z)
        glEnd()
        
    def mousePressEvent(self, event):
        self.last_pos = event.pos()
        self.current_mouse_pos = (event.x(), event.y())
        
        if event.button() == Qt.LeftButton:
            if self.mode == "add_line":
                # Добавляем точку для построения прямой
                world_pos = self.get_world_pos(event.x(), event.y(), 0.0)
                if world_pos is not None:
                    self.temp_points.append(world_pos)
                
                if len(self.temp_points) == 2:
                    # Создаем прямую из двух точек
                    start = self.temp_points[0]
                    end = self.temp_points[1]
                    direction = [end[i] - start[i] for i in range(3)]
                    
                    new_line = Line(start, direction)
                    self.lines.append(new_line)
                    self.temp_points = []
                    self.mode = "view"
                    self.update()
                    # Получаем главное окно через parent() дважды
                    if self.parent() and self.parent().parent():
                        self.parent().parent().update_line_list()
            
            elif self.mode == "move_line":
                # Проверяем, кликнули ли на прямую
                world_pos = self.get_world_pos(event.x(), event.y(), 0.0)
                if world_pos is not None:
                    self.dragging_line = self.find_line_at_position(world_pos)
                
                if self.dragging_line is not None:
                    self.drag_start_pos = world_pos
                    # Обновляем выделение
                    for line in self.lines:
                        line.selected = (line == self.dragging_line)
                    self.update()
                    if self.parent() and self.parent().parent():
                        self.parent().parent().update_line_list_selection()
    
    def find_line_at_position(self, pos, threshold=0.5):
        for line in self.lines:
            # Вектор от точки до начала прямой
            vec_to_start = [pos[i] - line.start[i] for i in range(3)]
            
            # Проекция на направление прямой
            projection = sum(vec_to_start[i] * line.direction[i] for i in range(3))
            
            # Перпендикулярная составляющая
            perpendicular = [
                vec_to_start[i] - projection * line.direction[i] for i in range(3)
            ]
            distance = math.sqrt(sum(comp*comp for comp in perpendicular))
            
            if distance < threshold and abs(projection) < line.length/2:
                return line
        return None
    
    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()
        self.current_mouse_pos = (event.x(), event.y())
        
        if event.buttons() & Qt.LeftButton:
            if self.dragging_line:
                # Перемещаем прямую
                world_pos = self.get_world_pos(event.x(), event.y(), 0.0)
                if world_pos is not None:
                    # Увеличиваем дельту для более быстрого перемещения
                    delta = [
                        (world_pos[0] - self.drag_start_pos[0]) * self.move_sensitivity,
                        (world_pos[1] - self.drag_start_pos[1]) * self.move_sensitivity,
                        (world_pos[2] - self.drag_start_pos[2]) * self.move_sensitivity
                    ]
                    
                    self.dragging_line.start = [
                        self.dragging_line.start[i] + delta[i] for i in range(3)
                    ]
                    self.drag_start_pos = world_pos
                    self.update()
                    if self.parent() and self.parent().parent():
                        self.parent().parent().update_line_list()
            else:
                # Вращение камеры
                self.rotation_x = (self.rotation_x + dy) % 360
                self.rotation_y = (self.rotation_y + dx) % 360
                self.update()
            
        self.last_pos = event.pos()
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging_line:
            self.dragging_line = None
            self.drag_start_pos = None

    def wheelEvent(self, event):
        self.zoom += event.angleDelta().y() * 0.01
        if self.zoom > -1: self.zoom = -1  # Ограничение приближения
        self.update()

# Реализация gluUnProject для PyQt5
def gluUnProject(winX, winY, winZ, model, proj, view):
    try:
        # Преобразуем входные данные в массивы NumPy
        model = np.array(model).reshape(4,4)
        proj = np.array(proj).reshape(4,4)
        view = np.array(view)
        
        # Вычисляем обратную матрицу (projection * modelview)
        mvp = proj @ model
        
        # Проверяем определитель матрицы, чтобы избежать сингулярности
        if abs(np.linalg.det(mvp)) < 1e-10:
            return [0.0, 0.0, 0.0]
            
        inv_mvp = np.linalg.inv(mvp)
        
        # Преобразуем координаты окна в нормализованные координаты устройства (NDC)
        x = 2.0 * (winX - view[0]) / view[2] - 1.0
        y = 2.0 * (winY - view[1]) / view[3] - 1.0
        z = 2.0 * winZ - 1.0
        
        # Создаем вектор в однородных координатах
        in_vec = np.array([x, y, z, 1.0])
        
        # Умножаем на обратную матрицу
        out_vec = inv_mvp @ in_vec
        
        # Если w равно нулю, возвращаем нулевые координаты
        if out_vec[3] == 0.0:
            return [0.0, 0.0, 0.0]
        
        # Перспективное деление
        out_vec /= out_vec[3]
        
        return out_vec[:3]
    except:
        return [0.0, 0.0, 0.0]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Визуализатор Стереометрии")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        
        # Левая панель с кнопками
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setAlignment(Qt.AlignTop)
        control_layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("Выберите фигуру:")
        title_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            margin: 10px;
            color: #444;
        """)
        control_layout.addWidget(title_label)
        
        self.shape_buttons = QButtonGroup()
        shapes = [
            ("Куб", "cube"),
            ("Пирамида", "pyramid"),
            ("Сфера", "sphere"),
            ("Цилиндр", "cylinder"),
            ("Конус", "cone")
        ]
        
        # Приятные цвета для кнопок
        button_colors = [
            "#F5C6AA",  # Персиковый
            "#B8E0D2",  # Мятный
            "#FFD8BE",  # Абрикосовый
            "#D6E4F0",  # Голубой
            "#E5D1F9"   # Лавандовый
        ]
        
        for i, (text, shape) in enumerate(shapes):
            btn = QPushButton(text)
            btn.setMinimumHeight(45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 14px; 
                    font-weight: bold;
                    background-color: {button_colors[i]}; 
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    color: #333;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(button_colors[i])};
                }}
                QPushButton:checked {{
                    background-color: #a0c0f0;
                    border: 2px solid #6080c0;
                }}
                QPushButton:pressed {{
                    background-color: #90b0e0;
                }}
            """)
            btn.setCheckable(True)
            self.shape_buttons.addButton(btn, i)
            control_layout.addWidget(btn)
        
        # Выбрать куб по умолчанию
        self.shape_buttons.buttons()[0].setChecked(True)
        self.shape_buttons.buttonClicked.connect(self.change_shape)
        
        # Панель управления прямыми
        line_group = QGroupBox("Управление прямыми")
        line_layout = QVBoxLayout(line_group)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_line_btn = QPushButton("Добавить прямую")
        self.add_line_btn.clicked.connect(self.start_add_line)
        btn_layout.addWidget(self.add_line_btn)
        
        self.move_line_btn = QPushButton("Перемещать прямую")
        self.move_line_btn.clicked.connect(self.start_move_line)
        self.move_line_btn.setCheckable(True)
        btn_layout.addWidget(self.move_line_btn)
        
        delete_line_btn = QPushButton("Удалить прямую")
        delete_line_btn.clicked.connect(self.delete_selected_line)
        btn_layout.addWidget(delete_line_btn)
        
        line_layout.addLayout(btn_layout)
        
        # Список прямых
        self.line_list = QListWidget()
        self.line_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.line_list.itemSelectionChanged.connect(self.select_line)
        line_layout.addWidget(QLabel("Список прямых:"))
        line_layout.addWidget(self.line_list)
        
        # Редактор параметров
        param_group = QGroupBox("Параметры прямой")
        param_layout = QFormLayout(param_group)
        
        self.start_x = QDoubleSpinBox()
        self.start_x.setRange(-100, 100)
        self.start_x.setSingleStep(0.1)
        
        self.start_y = QDoubleSpinBox()
        self.start_y.setRange(-100, 100)
        self.start_y.setSingleStep(0.1)
        
        self.start_z = QDoubleSpinBox()
        self.start_z.setRange(-100, 100)
        self.start_z.setSingleStep(0.1)
        
        self.dir_x = QDoubleSpinBox()
        self.dir_x.setRange(-1, 1)
        self.dir_x.setSingleStep(0.1)
        
        self.dir_y = QDoubleSpinBox()
        self.dir_y.setRange(-1, 1)
        self.dir_y.setSingleStep(0.1)
        
        self.dir_z = QDoubleSpinBox()
        self.dir_z.setRange(-1, 1)
        self.dir_z.setSingleStep(0.1)
        
        # Добавлен элемент управления для длины прямой
        self.length_spin = QDoubleSpinBox()
        self.length_spin.setRange(0.1, 100.0)  # Минимальная и максимальная длина
        self.length_spin.setSingleStep(0.1)
        self.length_spin.setValue(5.0)  # Значение по умолчанию
        
        param_layout.addRow("Начало X:", self.start_x)
        param_layout.addRow("Начало Y:", self.start_y)
        param_layout.addRow("Начало Z:", self.start_z)
        param_layout.addRow("Направление X:", self.dir_x)
        param_layout.addRow("Направление Y:", self.dir_y)
        param_layout.addRow("Направление Z:", self.dir_z)
        param_layout.addRow("Длина:", self.length_spin)  # Добавлен спинбокс для длины
        
        # Регулятор чувствительности перемещения
        self.sensitivity_spin = QDoubleSpinBox()
        self.sensitivity_spin.setRange(1.0, 10.0)
        self.sensitivity_spin.setSingleStep(0.5)
        self.sensitivity_spin.setValue(3.0)
        self.sensitivity_spin.valueChanged.connect(self.update_sensitivity)
        param_layout.addRow("Чувствительность перемещения:", self.sensitivity_spin)
        
        update_btn = QPushButton("Обновить параметры")
        update_btn.clicked.connect(self.update_line_params)
        param_layout.addRow(update_btn)
        
        line_layout.addWidget(param_group)
        control_layout.addWidget(line_group)
        
        # Добавляем поясняющие надписи
        help_label = QLabel(
            "Управление:\n\n"
            "• ЛКМ + перемещение - вращение\n"
            "• Колесо мыши - приближение/отдаление\n"
            "• Режим 'Добавить прямую': клик в двух точках\n"
            "• Режим 'Перемещать прямую': перетаскивание ЛКМ\n\n"
            "Система координат:\n"
            "X - красная ось (вправо)\n"
            "Y - синяя ось (вглубь)\n"
            "Z - зеленая ось (вверх)"
        )
        help_label.setStyleSheet("""
            font-size: 14px; 
            margin: 20px 10px; 
            color: #555;
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        """)
        control_layout.addWidget(help_label)
        
        # Виджет OpenGL
        self.gl_widget = GeometryVisualizer()
        self.gl_widget.setParent(self.central_widget)
        
        main_layout.addWidget(control_panel, 1)
        main_layout.addWidget(self.gl_widget, 4)
        
    def lighten_color(self, hex_color, factor=0.2):
        """Осветлить цвет для эффекта hover"""
        r = min(255, int(int(hex_color[1:3], 16) + 255 * factor))
        g = min(255, int(int(hex_color[3:5], 16) + 255 * factor))
        b = min(255, int(int(hex_color[5:7], 16) + 255 * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def change_shape(self, button):
        shapes = ["cube", "pyramid", "sphere", "cylinder", "cone"]
        self.gl_widget.current_shape = shapes[self.shape_buttons.id(button)]
        self.gl_widget.update()
        
    def start_add_line(self):
        self.gl_widget.mode = "add_line"
        self.gl_widget.temp_points = []
        self.move_line_btn.setChecked(False)
        
    def start_move_line(self):
        if self.move_line_btn.isChecked():
            self.gl_widget.mode = "move_line"
        else:
            self.gl_widget.mode = "view"
    
    def delete_selected_line(self):
        if self.gl_widget.lines:
            selected_index = self.line_list.currentRow()
            if 0 <= selected_index < len(self.gl_widget.lines):
                del self.gl_widget.lines[selected_index]
                self.update_line_list()
                self.gl_widget.update()
    
    def select_line(self):
        selected_index = self.line_list.currentRow()
        if 0 <= selected_index < len(self.gl_widget.lines):
            # Сбрасываем выделение всех прямых
            for line in self.gl_widget.lines:
                line.selected = False
            
            # Выделяем выбранную прямую
            self.gl_widget.lines[selected_index].selected = True
            
            # Обновляем редактор параметров
            line = self.gl_widget.lines[selected_index]
            self.start_x.setValue(line.start[0])
            self.start_y.setValue(line.start[1])
            self.start_z.setValue(line.start[2])
            self.dir_x.setValue(line.direction[0])
            self.dir_y.setValue(line.direction[1])
            self.dir_z.setValue(line.direction[2])
            self.length_spin.setValue(line.length)  # Устанавливаем длину
            
            self.gl_widget.update()
    
    def update_line_params(self):
        selected_index = self.line_list.currentRow()
        if 0 <= selected_index < len(self.gl_widget.lines):
            line = self.gl_widget.lines[selected_index]
            
            # Обновляем параметры прямой
            line.set_start(
                self.start_x.value(),
                self.start_y.value(),
                self.start_z.value()
            )
            
            line.set_direction(
                self.dir_x.value(),
                self.dir_y.value(),
                self.dir_z.value()
            )
            
            # Обновляем длину прямой
            line.set_length(self.length_spin.value())
            
            self.update_line_list()
            self.gl_widget.update()
    
    def update_line_list(self):
        self.line_list.clear()
        for i, line in enumerate(self.gl_widget.lines):
            start = line.start
            direction = line.direction
            
            # Добавлена информация о длине в список
            self.line_list.addItem(
                f"Прямая {i+1}: "
                f"({start[0]:.1f}, {start[1]:.1f}, {start[2]:.1f}) -> "
                f"[{direction[0]:.2f}, {direction[1]:.2f}, {direction[2]:.2f}] "
                f"длина={line.length:.1f}"  # Отображение длины
            )
        
        # Выбираем последнюю добавленную прямую
        if self.gl_widget.lines:
            self.line_list.setCurrentRow(len(self.gl_widget.lines)-1)
    
    def update_line_list_selection(self):
        # Обновляем выделение в списке
        for i, line in enumerate(self.gl_widget.lines):
            if line.selected:
                self.line_list.setCurrentRow(i)
                break
                
    def update_sensitivity(self):
        self.gl_widget.move_sensitivity = self.sensitivity_spin.value()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Установка шрифта для лучшей читаемости
    font = app.font()
    font.setPointSize(12)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())