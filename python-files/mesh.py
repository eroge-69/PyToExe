import json
import numpy as np
import matplotlib.pyplot as plt
import paramiko
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.colors import Normalize, LinearSegmentedColormap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QLabel,
                             QMessageBox, QLineEdit, QSizePolicy,
                             QFormLayout, QGroupBox, QToolTip, QTabWidget,
                             QSpacerItem, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import matplotlib.ticker as ticker
import plotly.graph_objects as go
from PyQt5.QtWebEngineWidgets import QWebEngineView
from scipy.ndimage import gaussian_filter


def parse_points(points_str):
    cleaned = points_str.replace("\\n", "\n").replace("\r", "").strip()
    rows = cleaned.split("\n")
    parsed = []
    for row in rows:
        if not row.strip():
            continue
        elements = row.strip().split(",")
        parsed.append([float(e.strip()) for e in elements if e.strip() != ''])
    return np.array(parsed)


class PrinterBedMap(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализатор стола 3D-принтера")
        self.setGeometry(100, 100, 1400, 800)
        QToolTip.setFont(QFont('SansSerif', 10))

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)

        self.right_panel = QWidget()
        self.right_panel.setMinimumWidth(300)
        self.right_panel.setMaximumWidth(350)
        self.right_layout = QVBoxLayout(self.right_panel)

        self.tabs = QTabWidget()
        self.left_layout.addWidget(self.tabs)

        self.matplotlib_tab = QWidget()
        self.matplotlib_layout = QVBoxLayout(self.matplotlib_tab)

        self.plotly_tab = QWidget()
        self.plotly_layout = QVBoxLayout(self.plotly_tab)
        self.plotly_view = QWebEngineView()
        self.plotly_layout.addWidget(self.plotly_view)

        self.tabs.addTab(self.matplotlib_tab, "2D вид")
        self.tabs.addTab(self.plotly_tab, "3D вид")

        self.figure = plt.figure(figsize=(10, 7), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.matplotlib_layout.addWidget(self.toolbar)
        self.matplotlib_layout.addWidget(self.canvas)

        self.load_group = QGroupBox("Управление загрузкой")
        self.load_layout = QVBoxLayout()

        self.load_button = QPushButton("📂 Загрузить из файла")
        self.load_button.clicked.connect(self.load_config)
        self.load_layout.addWidget(self.load_button)

        self.load_layout.addWidget(QLabel("Или"))

        self.ssh_form = QFormLayout()

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.1.100")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("2222")
        self.port_input.setFixedWidth(60)

        self.ssh_form.addRow("IP адрес:", self.ip_input)
        self.ssh_form.addRow("Порт:", self.port_input)

        self.ssh_button = QPushButton("🔗 Загрузить по SSH")
        self.ssh_button.clicked.connect(self.load_config_ssh)
        self.load_layout.addLayout(self.ssh_form)
        self.load_layout.addWidget(self.ssh_button)

        self.load_group.setLayout(self.load_layout)
        self.right_layout.addWidget(self.load_group)

        self.mesh_info_group = QGroupBox("Информация о сетке")
        self.mesh_info_layout = QFormLayout()

        self.max_dev_label = QLabel("N/A")
        self.min_dev_label = QLabel("N/A")
        self.range_label = QLabel("N/A")
        self.points_label = QLabel("N/A")

        self.mesh_info_layout.addRow("Макс. отклонение:", self.max_dev_label)
        self.mesh_info_layout.addRow("Мин. отклонение:", self.min_dev_label)
        self.mesh_info_layout.addRow("Размах отклонений:", self.range_label)
        self.mesh_info_layout.addRow("Точек сетки:", self.points_label)

        self.mesh_info_group.setLayout(self.mesh_info_layout)
        self.right_layout.addWidget(self.mesh_info_group)

        self.view_group = QGroupBox("Настройки 3D вида")
        self.view_layout = QVBoxLayout()

        self.wireframe_check = QCheckBox("Каркасный режим")
        self.wireframe_check.setChecked(True)
        self.wireframe_check.stateChanged.connect(self.update_plotly_view)
        self.view_layout.addWidget(self.wireframe_check)

        self.base_plane_check = QCheckBox("Базовая плоскость")
        self.base_plane_check.setChecked(True)
        self.base_plane_check.stateChanged.connect(self.update_plotly_view)
        self.view_layout.addWidget(self.base_plane_check)

        self.smooth_check = QCheckBox("Сглаживание")
        self.smooth_check.setChecked(True)
        self.smooth_check.stateChanged.connect(self.update_plotly_view)
        self.view_layout.addWidget(self.smooth_check)

        self.view_group.setLayout(self.view_layout)
        self.right_layout.addWidget(self.view_group)

        self.right_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.hover_x = None
        self.hover_y = None
        self.hover_z = None

        self.main_layout.addWidget(self.left_panel, stretch=1)
        self.main_layout.addWidget(self.right_panel)

        self.Z_data = None
        self.X = self.Y = None
        self.X_edges = self.Y_edges = None
        self.X_centers = self.Y_centers = None
        self.X_grid = self.Y_grid = None
        self.mesh_min = (0, 0)
        self.mesh_max = (220, 220)
        self.smoothed_Z = None

    def load_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть конфиг", "", "Config Files (*.cfg *.json);;All Files (*)"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.parse_and_load(content)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось загрузить файл:\n{str(e)}")

    def load_config_ssh(self):
        ip = self.ip_input.text().strip()
        if not ip:
            QMessageBox.warning(self, "Ошибка", "Введите IP адрес принтера")
            return
        try:
            port = int(self.port_input.text().strip()) if self.port_input.text().strip() else 2222
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Порт должен быть числом")
            return
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=port, username="root", password="rockchip", timeout=10)

            sftp = ssh.open_sftp()
            try:
                with sftp.open("/userdata/app/gk/printer_mutable.cfg", "r") as file:
                    content = file.read().decode('utf-8')
            finally:
                sftp.close()
                ssh.close()

            self.parse_and_load(content)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка SSH", f"Не удалось подключиться:\n{str(e)}")

    def parse_and_load(self, content):
        try:
            json_start = content.find('{')
            if json_start == -1:
                raise ValueError("Не найден JSON в файле конфигурации")

            json_data = json.loads(content[json_start:])

            mesh_data = json_data.get("bed_mesh default") or json_data.get("bed_mesh")
            if not mesh_data:
                raise ValueError("Не найдены данные bed_mesh в конфигурации")

            self.mesh_min = (float(mesh_data["min_x"]), float(mesh_data["min_y"]))
            self.mesh_max = (float(mesh_data["max_x"]), float(mesh_data["max_y"]))

            points_str = mesh_data["points"]
            self.Z_data = parse_points(points_str)
            self.Z_data = np.rot90(self.Z_data)
            self.smoothed_Z = gaussian_filter(self.Z_data, sigma=1.2)

            rows, cols = self.Z_data.shape
            self.X_edges = np.linspace(self.mesh_min[0], self.mesh_max[0], cols + 1)
            self.Y_edges = np.linspace(self.mesh_min[1], self.mesh_max[1], rows + 1)
            self.X_centers = np.linspace(self.mesh_min[0], self.mesh_max[0], cols)
            self.Y_centers = np.linspace(self.mesh_min[1], self.mesh_max[1], rows)
            self.X_grid, self.Y_grid = np.meshgrid(self.X_centers, self.Y_centers)
            self.X, self.Y = np.meshgrid(
                (self.X_edges[:-1] + self.X_edges[1:]) / 2,
                (self.Y_edges[:-1] + self.Y_edges[1:]) / 2
            )

            self.analyze()
            self.update_view()
            self.update_plotly_view()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка парсинга", f"Ошибка обработки данных:\n{str(e)}")

    def get_colormap(self):
        return LinearSegmentedColormap.from_list('bed_colormap', ['#ff0000', '#ffff00', '#00ff00'])

    def analyze(self):
        if self.Z_data is None:
            return

        z = self.Z_data
        self.max_dev_label.setText(f"{np.max(z):.3f} мм")
        self.min_dev_label.setText(f"{np.min(z):.3f} мм")
        self.range_label.setText(f"{(np.max(z) - np.min(z)):.3f} мм")
        self.points_label.setText(f"{z.shape[1]} × {z.shape[0]}")

    def update_view(self):
        if self.Z_data is None:
            return

        self.figure.clf()
        cmap = self.get_colormap()
        ax = self.figure.add_subplot(111)
        norm = Normalize(vmin=np.min(self.Z_data), vmax=np.max(self.Z_data))

        mesh = ax.pcolormesh(self.X_edges, self.Y_edges, self.Z_data,
                              cmap=cmap, norm=norm, edgecolors='black', linewidths=0.3)

        for i in range(self.Z_data.shape[0]):
            for j in range(self.Z_data.shape[1]):
                x_center = (self.X_edges[j] + self.X_edges[j + 1]) / 2
                y_center = (self.Y_edges[i] + self.Y_edges[i + 1]) / 2
                ax.text(x_center, y_center, f"{self.Z_data[i, j]:.3f}",
                        ha='center', va='center', color='black', fontsize=8,
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

        cbar = self.figure.colorbar(mesh, ax=ax, label="Отклонение (мм)")
        cbar.ax.tick_params(labelsize=8)

        ax.set_xlim(self.mesh_min[0], self.mesh_max[0])
        ax.set_ylim(self.mesh_min[1], self.mesh_max[1])
        ax.set_aspect('equal')
        ax.set_title(f"2D карта стола ({self.Z_data.shape[1]}×{self.Z_data.shape[0]})", pad=20)
        ax.set_xlabel("X (мм)", fontsize=9)
        ax.set_ylabel("Y (мм)", fontsize=9)

        ax.xaxis.set_major_locator(ticker.MultipleLocator(20))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(20))
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.grid(True, linestyle=':', color='gray', alpha=0.3)

        offset = 10
        ax.text(self.mesh_min[0] - offset, self.mesh_min[1] - offset, "Левый ближний",
                fontsize=8, ha='right', va='top')
        ax.text(self.mesh_max[0] + offset, self.mesh_min[1] - offset, "Правый ближний",
                fontsize=8, ha='left', va='top')
        ax.text(self.mesh_min[0] - offset, self.mesh_max[1] + offset, "Левый дальний",
                fontsize=8, ha='right', va='bottom')
        ax.text(self.mesh_max[0] + offset, self.mesh_max[1] + offset, "Правый дальний",
                fontsize=8, ha='left', va='bottom')

        self.figure.tight_layout()
        self.canvas.draw()

    def update_plotly_view(self):
        if self.Z_data is None:
            return

        rows, cols = self.Z_data.shape
        colorscale = [
            [0, '#ff0000'],
            [0.5, '#ffff00'],
            [1, '#00ff00']
        ]

        fig = go.Figure()

        z_data = self.smoothed_Z if self.smooth_check.isChecked() else self.Z_data

        fig.add_trace(go.Surface(
            z=z_data,
            x=self.X_centers,
            y=self.Y_centers,
            colorscale=colorscale,
            showscale=True,
            opacity=0.85 if self.wireframe_check.isChecked() else 0.9,
            contours=dict(
                x=dict(show=self.wireframe_check.isChecked(), color='gray', width=1,
                       start=self.mesh_min[0], end=self.mesh_max[0],
                       size=(self.mesh_max[0] - self.mesh_min[0]) / cols),
                y=dict(show=self.wireframe_check.isChecked(), color='gray', width=1,
                       start=self.mesh_min[1], end=self.mesh_max[1],
                       size=(self.mesh_max[1] - self.mesh_min[1]) / rows),
                z=dict(show=False)
            ),
            showlegend=False,
            hoverinfo='skip'
        ))

        if self.base_plane_check.isChecked():
            fig.add_trace(go.Surface(
                z=np.zeros_like(z_data),
                x=self.X_centers,
                y=self.Y_centers,
                colorscale=[[0, 'rgba(200,200,200,0.25)'], [1, 'rgba(200,200,200,0.25)']],
                showscale=False,
                opacity=0.25,
                showlegend=False,
                hoverinfo='skip'
            ))

        z_min = np.min(z_data)
        corners = [
            (self.mesh_min[0], self.mesh_min[1], "Левый ближний", 'right', 'top'),
            (self.mesh_max[0], self.mesh_min[1], "Правый ближний", 'left', 'top'),
            (self.mesh_min[0], self.mesh_max[1], "Левый дальний", 'right', 'bottom'),
            (self.mesh_max[0], self.mesh_max[1], "Правый дальний", 'left', 'bottom')
        ]

        annotations = []
        for x, y, text, xanchor, yanchor in corners:
            annotations.append(dict(
                x=x,
                y=y,
                z=z_min - 0.1,
                text=text,
                showarrow=False,
                font=dict(color='black', size=10),
                xanchor=xanchor,
                yanchor=yanchor
            ))

        fig.update_layout(
            scene=dict(
                xaxis=dict(title='X (мм)', title_font=dict(size=10), tickfont=dict(size=8)),
                yaxis=dict(title='Y (мм)', title_font=dict(size=10), tickfont=dict(size=8)),
                zaxis=dict(title='Отклонение (мм)', title_font=dict(size=10), tickfont=dict(size=8)),
                annotations=annotations,
                aspectratio=dict(x=1, y=1, z=0.7),
                camera_eye=dict(x=1.5, y=1.5, z=0.8)
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            font=dict(family="Arial", size=10),
            hovermode=False
        )

        self.plotly_view.setHtml(fig.to_html(include_plotlyjs='cdn'))

    def on_mouse_move(self, event):
        if not event.inaxes or self.Z_data is None:
            return

        self.hover_x = event.xdata
        self.hover_y = event.ydata

        x_idx = np.abs(self.X[0, :] - event.xdata).argmin()
        y_idx = np.abs(self.Y[:, 0] - event.ydata).argmin()
        value = self.Z_data[y_idx, x_idx]

        QToolTip.showText(
            self.mapToGlobal(self.canvas.pos()),
            f"X: {self.X_centers[x_idx]:.1f} мм\nY: {self.Y_centers[y_idx]:.1f} мм\nОтклонение: {value:.4f} мм",
            self.canvas
        )

        self.update_plotly_view()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    try:
        window = PrinterBedMap()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Критическая ошибка:\n{str(e)}")
        sys.exit(1)
