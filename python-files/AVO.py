"""
AVO---radial-menu-app-launcher
Author: yellowcoffeefrog
Description: Circular app launcher for Windows
Compatible with Windows 10 and Windows 11
"""

import sys
import json
import os
import subprocess
import math
import threading
import time
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                              QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit,
                              QDialog, QMessageBox, QFileDialog, QListWidgetItem,
                              QSystemTrayIcon, QMenu, QGraphicsOpacityEffect)
from PySide6.QtCore import (Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, 
                           Signal, QThread, QRect, Property)
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QIcon, QFont, QAction, QRadialGradient, QPainterPath, QCursor

try:
    import mouse  
    MOUSE_AVAILABLE = True
except ImportError:
    print("Error: 'mouse' library not installed. Run: pip install mouse")
    MOUSE_AVAILABLE = False

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    print("Error: 'pywin32' library not installed. Run: pip install pywin32")
    WIN32_AVAILABLE = False


def deep_merge_dict(target, source):
    for key, value in source.items():
        if key in target:
            if isinstance(target[key], dict) and isinstance(value, dict):
                deep_merge_dict(target[key], value)
        else:
            target[key] = value
    return target


class ConfigManager:

    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def get_default_config(self):

        return {
            "theme": {
                "background_color": "rgba(25, 25, 30, 140)",      # Darker background
                "slice_color": "rgba(45, 45, 55, 160)",           # Slice background
                "slice_hover_color": "rgba(70, 130, 255, 120)",   # Hover slice  
                "separator_color": "rgba(60, 60, 70, 200)",       # Separator lines
                "text_color": "rgba(220, 220, 220, 255)",         # Text color
                "glow_color": "rgba(100, 150, 255, 80)",          # Glow effect
                "center_color": "rgba(20, 20, 25, 180)"           # Center circle
            },
            "menu": {
                "radius": 140,
                "inner_radius": 45,     # Inner circle radius
                "icon_size": 24,        # Smaller icons for slices
                "animation_speed": 300, # Animation speed
                "separator_width": 2,   # Width of separator lines
                "glow_radius": 4        # Glow effect radius
            },
            "applications": [           #default app
                {
                    "name": "Calculator",
                    "command": "calc.exe", 
                    "icon": "calculator.png",
                    "position": 0
                },
                {
                    "name": "File Explorer",
                    "command": "explorer.exe",
                    "icon": "explorer.png",
                    "position": 1
                },
                {
                    "name": "Settings",
                    "command": "special:settings",
                    "icon": "settings.png",
                    "position": 4
                }
            ],
            "trigger": {
                "key": "middle_click",
                "desktop_only": True,
                "hover_hide": True,
                "global_hover_check": True,
                "hover_check_interval": 50,
                "hover_margin": 30
            }
        }

    def load_config(self):
        """Loads configuration from JSON file with proper default merging"""
        default_config = self.get_default_config()

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)

                merged_config = self.get_default_config()  # Start with defaults
                if isinstance(loaded_config, dict):
                    # Keep existing applications if they exist
                    if "applications" in loaded_config:
                        merged_config["applications"] = loaded_config["applications"]

                    for section in ["theme", "menu", "trigger"]:
                        if section in loaded_config:
                            if section in merged_config:
                                merged_config[section].update(loaded_config[section])
                            else:
                                merged_config[section] = loaded_config[section]

                    print("✅ Configuration loaded and merged with new defaults")
                    return merged_config
                else:
                    print("⚠️ Invalid config file, using defaults")
                    self.save_config(default_config)
                    return default_config
            else:
                print("📝 Creating default configuration")
                self.save_config(default_config)
                return default_config
        except Exception as e:
            print(f"❌ Config load error: {e}, using defaults")
            return default_config

    def save_config(self, config=None):
        """Saves configuration to JSON file"""
        if config is None:
            config = self.config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.config = config
            return True
        except Exception as e:
            print(f"❌ Config save error: {e}")
            return False


class GlobalMouseMonitor(QThread):
    """Monitors global mouse position for hover detection using Qt"""
    cursor_outside_menu = Signal()
    cursor_inside_menu = Signal()

    def __init__(self, menu_widget):
        super().__init__()
        self.menu_widget = menu_widget
        self.running = False
        self.last_inside_state = False

    def is_cursor_in_menu_area(self):
        """Checks if cursor is within menu area using Qt cursor position"""
        if not self.menu_widget.isVisible():
            return False

        try:
            cursor_pos = QCursor.pos()
            cursor_x, cursor_y = cursor_pos.x(), cursor_pos.y()

            menu_rect = self.menu_widget.geometry()
            menu_center_global = self.menu_widget.mapToGlobal(
                QPoint(menu_rect.width() // 2, menu_rect.height() // 2)
            )

            dx = cursor_x - menu_center_global.x()
            dy = cursor_y - menu_center_global.y()
            distance = math.sqrt(dx*dx + dy*dy)

            radius = self.menu_widget.config["menu"]["radius"]
            margin = self.menu_widget.config["trigger"].get("hover_margin", 30)
            max_distance = radius + margin

            return distance <= max_distance

        except Exception as e:
            return False

    def run(self):
        """Monitors mouse position continuously"""
        self.running = True
        check_interval = self.menu_widget.config["trigger"].get("hover_check_interval", 50)

        while self.running:
            try:
                if self.menu_widget.isVisible():
                    cursor_inside = self.is_cursor_in_menu_area()

                    if cursor_inside != self.last_inside_state:
                        if cursor_inside:
                            self.cursor_inside_menu.emit()
                        else:
                            self.cursor_outside_menu.emit()

                        self.last_inside_state = cursor_inside

                time.sleep(check_interval / 1000.0)

            except Exception as e:
                time.sleep(0.1)

    def stop(self):
        """Stops monitoring"""
        self.running = False


class MouseListener(QThread):
    """Listens for global mouse events"""
    middle_clicked = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.running = False
        self.last_click_time = 0

    def is_on_desktop(self, x, y):
        """Checks if click was on Windows desktop"""
        if not WIN32_AVAILABLE:
            return True

        try:
            hwnd = win32gui.WindowFromPoint((x, y))
            if hwnd:
                class_name = win32gui.GetClassName(hwnd)

                desktop_classes = [
                    "WorkerW", "Progman", "Shell_TrayWnd", "SHELLDLL_DefView",
                    "SysListView32", "FolderView", "DirectUIHWND"
                ]

                return any(cls in class_name for cls in desktop_classes)
            return True
        except Exception as e:
            return True

    def run(self):
        """Starts mouse listening"""
        if not MOUSE_AVAILABLE:
            print("Mouse library not available. Listening disabled.")
            return

        self.running = True

        def on_middle_click():
            if not self.running:
                return

            try:
                cursor_pos = QCursor.pos()
                qt_x, qt_y = cursor_pos.x(), cursor_pos.y()

                print(f"🎯 Qt Cursor Position: ({qt_x}, {qt_y})")

                if MOUSE_AVAILABLE:
                    mouse_pos = mouse.get_position()
                    desktop_check_result = self.is_on_desktop(mouse_pos[0], mouse_pos[1])
                else:
                    desktop_check_result = True

                if desktop_check_result:
                    current_time = time.time()
                    if current_time - self.last_click_time > 0.3:
                        self.last_click_time = current_time
                        self.middle_clicked.emit(qt_x, qt_y)
            except Exception as e:
                print(f"Mouse hook error: {e}")

        try:
            mouse.on_middle_click(on_middle_click)

            print("🎯 AVO - running (Qt Cursor Edition)")
            print("✨ Using Qt cursor position for perfect DPI handling!")

            while self.running:
                time.sleep(0.1)

        except Exception as e:
            print(f"Mouse hook error: {e}")

    def stop(self):
        """Stops listening"""
        self.running = False
        if MOUSE_AVAILABLE:
            try:
                mouse.unhook_all()
            except:
                pass


class StyledRadialMenu(QWidget):

    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.config = config_manager.config
        self.hovered_item = -1
        self.app_slices = [] 

        # Animation state
        self._scale_factor = 0.0
        self._opacity_factor = 0.0
        self.is_animating_show = False
        self.is_animating_hide = False
        self.is_visible_state = False

        # Global mouse monitor
        self.global_mouse_monitor = GlobalMouseMonitor(self)
        self.global_mouse_monitor.cursor_outside_menu.connect(self.on_cursor_left_globally)
        self.global_mouse_monitor.cursor_inside_menu.connect(self.on_cursor_entered_globally)

        # Timer for delayed hiding
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.animated_hide)
        self.hide_timer.setSingleShot(True)

        # Qt Animations
        self.scale_animation = QPropertyAnimation(self, b"scale_factor")
        self.opacity_animation = QPropertyAnimation(self, b"opacity_factor")

        self.setup_ui()
        self.setup_animations()
        self.hide()

    # Properties for animations
    @Property(float)
    def scale_factor(self):
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, value):
        self._scale_factor = value
        if self.isVisible() and self.width() > 0 and self.height() > 0:
            self.update()

    @Property(float)
    def opacity_factor(self):
        return self._opacity_factor

    @opacity_factor.setter
    def opacity_factor(self, value):
        self._opacity_factor = value
        if self.isVisible() and self.width() > 0 and self.height() > 0:
            self.update()

    def setup_ui(self):
        """Configures user interface"""
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setMouseTracking(True)

        # Window size
        size = self.config["menu"]["radius"] * 2 + 60
        self.setFixedSize(size, size)

        self.setAttribute(Qt.WA_ShowWithoutActivating)

    def setup_animations(self):
        """Configures animations"""
        animation_speed = self.config["menu"]["animation_speed"]

        self.scale_animation.setDuration(animation_speed)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutBack)

        self.opacity_animation.setDuration(animation_speed)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.scale_animation.finished.connect(self.on_show_animation_finished)
        self.opacity_animation.finished.connect(self.on_hide_animation_finished)

    def on_show_animation_finished(self):
        """Called when show animation finishes"""
        self.is_animating_show = False
        self.is_visible_state = True
        print("✅ Show animation finished")

    def on_hide_animation_finished(self):
        """Called when hide animation finishes"""
        if not self.is_visible_state:
            self.hide()
            self.is_animating_hide = False
            print("✅ Hide animation finished")

    def on_cursor_entered_globally(self):
        """Called by global mouse monitor when cursor enters menu area"""
        self.hide_timer.stop()
        print("🎯 Cursor entered menu area")

    def on_cursor_left_globally(self):
        """Called by global mouse monitor when cursor leaves menu area"""
        if (self.config["trigger"].get("hover_hide", True) and 
            self.config["trigger"].get("global_hover_check", True)):

            self.hide_timer.start(150)
            print("👋 Cursor left menu area - hiding in 150ms")

    def calculate_app_slices(self):
        """Calculates slice geometry for each application"""
        self.app_slices = []
        apps = self.config["applications"]
        total_apps = len(apps)

        if total_apps == 0:
            return

        center = QPoint(self.width() // 2, self.height() // 2)

        # Safe access to config values with defaults
        outer_radius = self.config["menu"].get("radius", 140)
        inner_radius = self.config["menu"].get("inner_radius", 45)

        for i, app in enumerate(apps):
            # Calculate slice angles
            angle_per_slice = 2 * math.pi / total_apps
            start_angle = (i * angle_per_slice) - math.pi/2  # Start from top
            end_angle = start_angle + angle_per_slice

            # Calculate icon position (middle of slice)
            mid_angle = start_angle + angle_per_slice / 2
            icon_radius = (outer_radius + inner_radius) / 2
            icon_x = center.x() + int(icon_radius * math.cos(mid_angle))
            icon_y = center.y() + int(icon_radius * math.sin(mid_angle))

            # Store slice data
            self.app_slices.append({
                'app': app,
                'start_angle': start_angle,
                'end_angle': end_angle,
                'mid_angle': mid_angle,
                'icon_x': icon_x,
                'icon_y': icon_y,
                'inner_radius': inner_radius,
                'outer_radius': outer_radius
            })

    def animated_show(self, x, y):
        """Shows menu"""
        self.hide_timer.stop()
        self.scale_animation.stop()
        self.opacity_animation.stop()

        self.is_animating_show = True
        self.is_animating_hide = False
        self.is_visible_state = True

        self.position_menu(x, y)
        self.show()
        self.raise_()

        if WIN32_AVAILABLE:
            try:
                hwnd = int(self.winId())
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
            except:
                pass

        self.calculate_app_slices()

        if not self.global_mouse_monitor.isRunning():
            self.global_mouse_monitor.start()

        # Show animation
        self.scale_animation.setStartValue(0.0)
        self.scale_animation.setEndValue(1.0)

        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)

        self.scale_animation.start()
        self.opacity_animation.start()

        print("✨ Menu appears")

    def animated_hide(self):
        """Hides menu"""
        if self.is_animating_hide:
            return

        self.is_animating_hide = True
        self.is_animating_show = False
        self.is_visible_state = False

        if self.global_mouse_monitor.isRunning():
            self.global_mouse_monitor.stop()
            self.global_mouse_monitor.wait(1000)

        current_scale = self._scale_factor
        current_opacity = self._opacity_factor

        self.scale_animation.setStartValue(current_scale)
        self.scale_animation.setEndValue(0.0)

        self.opacity_animation.setStartValue(current_opacity)
        self.opacity_animation.setEndValue(0.0)

        self.scale_animation.start()
        self.opacity_animation.start()

        print("✨ Menu hides")

    def position_menu(self, cursor_x, cursor_y):
        """Positions menu using Qt cursor coordinates (DPI-aware)"""

        # Calculate menu dimensions
        menu_radius = self.config["menu"]["radius"]
        menu_width = menu_radius * 2 + 60
        menu_height = menu_radius * 2 + 60

        menu_x = cursor_x - menu_width // 2
        menu_y = cursor_y - menu_height // 2

        print(f"🎯 Qt Cursor at: ({cursor_x}, {cursor_y})")
        print(f"📐 Menu size: {menu_width}x{menu_height}")
        print(f"📍 Centering menu at: ({menu_x}, {menu_y})")

        # Get screen containing cursor
        screen = QApplication.screenAt(QPoint(cursor_x, cursor_y))
        if screen:
            screen_rect = screen.geometry()
            print(f"🖥️ Screen bounds: {screen_rect}")

            if menu_x < screen_rect.left():
                menu_x = screen_rect.left() + 10
                print(f"⬅️ Adjusted X to: {menu_x} (left boundary)")
            elif menu_x + menu_width > screen_rect.right():
                menu_x = screen_rect.right() - menu_width - 10
                print(f"➡️ Adjusted X to: {menu_x} (right boundary)")

            if menu_y < screen_rect.top():
                menu_y = screen_rect.top() + 10
                print(f"⬆️ Adjusted Y to: {menu_y} (top boundary)")
            elif menu_y + menu_height > screen_rect.bottom():
                menu_y = screen_rect.bottom() - menu_height - 10
                print(f"⬇️ Adjusted Y to: {menu_y} (bottom boundary)")

        # Move menu to calculated position
        self.move(menu_x, menu_y)
        print(f"✅ Menu positioned at: ({menu_x}, {menu_y})")

    def paintEvent(self, event):
        """Draws styled radial menu with slices"""
        if (not self.isVisible() or 
            self._opacity_factor <= 0 or 
            self.width() <= 0 or 
            self.height() <= 0):
            return

        painter = QPainter()
        if not painter.begin(self):
            return

        try:
            painter.setRenderHint(QPainter.Antialiasing)

            center = QPoint(self.width() // 2, self.height() // 2)

            outer_radius = self.config["menu"].get("radius", 140)
            inner_radius = self.config["menu"].get("inner_radius", 45)

            scale = self._scale_factor
            opacity = self._opacity_factor

            if scale <= 0.0:
                return

            painter.setOpacity(opacity)

            # Scale everything relative to center
            painter.translate(center)
            painter.scale(scale, scale)
            painter.translate(-center)

            # Draw main background circle
            bg_color = QColor(self.config["theme"].get("background_color", "rgba(25, 25, 30, 140)"))
            bg_color.setAlpha(int(140 * opacity))
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, outer_radius, outer_radius)

            # Draw application slices
            apps = self.config["applications"]
            total_apps = len(apps)

            if total_apps > 0:
                self.draw_app_slices(painter, center, opacity)

            # Draw separator lines between slices
            if total_apps > 1:
                self.draw_separators(painter, center, inner_radius, outer_radius, opacity)

            # Draw center circle
            self.draw_center_circle(painter, center, inner_radius, opacity)

        finally:
            painter.end()

    def draw_app_slices(self, painter, center, opacity):
        """Draws individual application slices"""
        for i, slice_data in enumerate(self.app_slices):
            app = slice_data['app']
            start_angle = slice_data['start_angle']
            end_angle = slice_data['end_angle']
            inner_radius = slice_data['inner_radius']
            outer_radius = slice_data['outer_radius']

            # Create slice path
            path = QPainterPath()
            path.arcMoveTo(center.x() - outer_radius, center.y() - outer_radius, 
                          outer_radius * 2, outer_radius * 2, 
                          math.degrees(-start_angle))
            path.arcTo(center.x() - outer_radius, center.y() - outer_radius,
                      outer_radius * 2, outer_radius * 2,
                      math.degrees(-start_angle), 
                      math.degrees(-(end_angle - start_angle)))

            # Connect to inner circle
            path.arcTo(center.x() - inner_radius, center.y() - inner_radius,
                      inner_radius * 2, inner_radius * 2,
                      math.degrees(-end_angle),
                      math.degrees(end_angle - start_angle))
            path.closeSubpath()

            # Choose slice color based on hover state
            if i == self.hovered_item:
                slice_color = QColor(self.config["theme"].get("slice_hover_color", "rgba(70, 130, 255, 120)"))
                slice_color.setAlpha(int(120 * opacity))

                # Add glow effect for hovered slice
                glow_color = QColor(self.config["theme"].get("glow_color", "rgba(100, 150, 255, 80)"))
                glow_color.setAlpha(int(80 * opacity))
                glow_radius = self.config["menu"].get("glow_radius", 4)
                glow_pen = QPen(glow_color, glow_radius)
                painter.setPen(glow_pen)
                painter.drawPath(path)
            else:
                slice_color = QColor(self.config["theme"].get("slice_color", "rgba(45, 45, 55, 160)"))
                slice_color.setAlpha(int(160 * opacity))

            # Draw slice
            painter.setBrush(QBrush(slice_color))
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

            # Draw app icon and text
            self.draw_app_icon_and_text(painter, slice_data, opacity)

    def draw_separators(self, painter, center, inner_radius, outer_radius, opacity):
        """Draws separator lines between slices"""
        separator_color = QColor(self.config["theme"].get("separator_color", "rgba(60, 60, 70, 200)"))
        separator_color.setAlpha(int(200 * opacity))
        separator_width = self.config["menu"].get("separator_width", 2)

        painter.setPen(QPen(separator_color, separator_width))

        total_apps = len(self.app_slices)
        for i in range(total_apps):
            slice_data = self.app_slices[i]
            start_angle = slice_data['start_angle']

            inner_x = center.x() + inner_radius * math.cos(start_angle)
            inner_y = center.y() + inner_radius * math.sin(start_angle)
            outer_x = center.x() + outer_radius * math.cos(start_angle)
            outer_y = center.y() + outer_radius * math.sin(start_angle)

            painter.drawLine(int(inner_x), int(inner_y), int(outer_x), int(outer_y))

    def draw_center_circle(self, painter, center, radius, opacity):
        """Draws center circle"""
        center_color = QColor(self.config["theme"].get("center_color", "rgba(20, 20, 25, 180)"))
        center_color.setAlpha(int(180 * opacity))

        painter.setBrush(QBrush(center_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)

        # Center text
        text_color = QColor(self.config["theme"].get("text_color", "rgba(220, 220, 220, 255)"))
        text_color.setAlpha(int(255 * opacity))
        painter.setPen(QPen(text_color))
        font = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font)

        text = "Apps"
        text_rect = painter.fontMetrics().boundingRect(text)
        text_x = center.x() - text_rect.width() // 2
        text_y = center.y() + text_rect.height() // 2 - 2

        painter.drawText(text_x, text_y, text)

    def draw_app_icon_and_text(self, painter, slice_data, opacity):
        """Draws application icon and name in slice"""
        app = slice_data['app']
        icon_x = slice_data['icon_x']
        icon_y = slice_data['icon_y']

        icon_size = self.config["menu"].get("icon_size", 24)

        # Try to load icon from file
        icon_path = os.path.join("icons", app["icon"])
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(icon_x - icon_size//2, icon_y - icon_size//2 - 8, pixmap)
        else:
            # Default icon - simple circle with first letter
            icon_bg = QColor(80, 80, 90, int(160 * opacity))
            painter.setBrush(QBrush(icon_bg))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(icon_x - icon_size//2, icon_y - icon_size//2 - 8, icon_size, icon_size)

            # First letter
            text_color = QColor(self.config["theme"].get("text_color", "rgba(220, 220, 220, 255)"))
            text_color.setAlpha(int(255 * opacity))
            painter.setPen(QPen(text_color))
            font = QFont("Segoe UI", 10, QFont.Bold)
            painter.setFont(font)
            first_letter = app["name"][0].upper() if app["name"] else "?"
            letter_rect = painter.fontMetrics().boundingRect(first_letter)
            painter.drawText(icon_x - letter_rect.width()//2, 
                           icon_y - letter_rect.height()//2 - 5, first_letter)

        # App name below icon
        text_color = QColor(self.config["theme"].get("text_color", "rgba(220, 220, 220, 255)"))
        text_color.setAlpha(int(220 * opacity))
        painter.setPen(QPen(text_color))
        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        app_name = app["name"]
        if len(app_name) > 10:
            app_name = app_name[:8] + "..."

        text_rect = painter.fontMetrics().boundingRect(app_name)
        text_x = icon_x - text_rect.width() // 2
        text_y = icon_y + icon_size // 2 + 12

        painter.drawText(text_x, text_y, app_name)

    def mouseMoveEvent(self, event):
        """Handles mouse movement for hover effect"""
        if not self.isVisible():
            return

        pos = event.position().toPoint()
        center = QPoint(self.width() // 2, self.height() // 2)

        # Calculate distance from center
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()
        distance = math.sqrt(dx*dx + dy*dy)

        scaled_distance = distance / max(0.1, self._scale_factor)

        inner_radius = self.config["menu"].get("inner_radius", 45)
        outer_radius = self.config["menu"].get("radius", 140)

        self.hovered_item = -1

        # Check if mouse is in slice area
        if inner_radius <= scaled_distance <= outer_radius and len(self.app_slices) > 0:
            # Calculate angle from center
            angle = math.atan2(dy, dx)
            if angle < 0:
                angle += 2 * math.pi

            # Adjust angle to match our slice calculation (start from top)
            adjusted_angle = angle + math.pi/2
            if adjusted_angle >= 2 * math.pi:
                adjusted_angle -= 2 * math.pi

            # Find which slice the mouse is in
            angle_per_slice = 2 * math.pi / len(self.app_slices)
            slice_index = int(adjusted_angle / angle_per_slice)

            if 0 <= slice_index < len(self.app_slices):
                self.hovered_item = slice_index

        if self.isVisible() and self.width() > 0:
            self.update()

    def mousePressEvent(self, event):
        """Handles mouse clicks"""
        if event.button() == Qt.LeftButton and self.hovered_item >= 0:
            if self.hovered_item < len(self.app_slices):
                app = self.app_slices[self.hovered_item]['app']
                print(f"🚀 Clicked: {app['name']}")
                self.launch_application(app)
                self.animated_hide()

        elif event.button() == Qt.RightButton:
            self.animated_hide()

    def launch_application(self, app):
        """Launches application"""
        command = app["command"]

        if command == "special:settings":
            self.open_settings()
        else:
            try:
                if command.endswith('.exe') and not os.path.isabs(command):
                    subprocess.Popen(command, shell=True)
                elif os.path.isfile(command):
                    subprocess.Popen([command])
                else:
                    subprocess.Popen(command, shell=True)

                print(f"✅ Launched: {app['name']} ({command})")
            except Exception as e:
                print(f"Launch error {app['name']}: {e}")
                try:
                    os.startfile(command)
                    print(f"✅ Launched via os.startfile: {app['name']}")
                except:
                    QMessageBox.warning(self, "Launch Error", 
                                      f"Cannot launch {app['name']}\nError: {str(e)}")

    def open_settings(self):
        """Opens settings window"""
        settings_dialog = SettingsDialog(self.config_manager, self)
        if settings_dialog.exec() == QDialog.Accepted:
            self.config = self.config_manager.config
            self.setup_animations()

    def keyPressEvent(self, event):
        """Handles key presses"""
        if event.key() == Qt.Key_Escape:
            self.animated_hide()

    def closeEvent(self, event):
        """Handle close event"""
        if self.global_mouse_monitor.isRunning():
            self.global_mouse_monitor.stop()
            self.global_mouse_monitor.wait(2000)
        event.accept()


class SettingsDialog(QDialog):
    """Settings dialog"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = config_manager.config.copy()
        self.setup_ui()

    def setup_ui(self):
        """Configures settings interface"""
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)

        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: white;
            }
            QListWidget {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)

        layout = QVBoxLayout()

        self.app_list = QListWidget()
        self.load_applications()
        layout.addWidget(QLabel("Applications:"))
        layout.addWidget(self.app_list)

        button_layout = QHBoxLayout()

        add_btn = QPushButton("➕ Add")
        add_btn.clicked.connect(self.add_application)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Edit")
        edit_btn.clicked.connect(self.edit_application)
        button_layout.addWidget(edit_btn)

        remove_btn = QPushButton("🗑️ Remove")
        remove_btn.clicked.connect(self.remove_application)
        button_layout.addWidget(remove_btn)

        layout.addLayout(button_layout)

        ok_cancel_layout = QHBoxLayout()

        ok_btn = QPushButton("✅ OK")
        ok_btn.clicked.connect(self.accept)
        ok_cancel_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        ok_cancel_layout.addWidget(cancel_btn)

        layout.addLayout(ok_cancel_layout)

        self.setLayout(layout)

    def load_applications(self):
        """Loads applications to list"""
        self.app_list.clear()
        for app in self.config["applications"]:
            item_text = f"🎯 {app['name']} - {app['command']}"
            self.app_list.addItem(item_text)

    def add_application(self):
        """Adds new application"""
        dialog = ApplicationDialog(self)
        if dialog.exec() == QDialog.Accepted:
            app_data = dialog.get_application_data()
            if app_data:
                app_data["position"] = len(self.config["applications"])
                self.config["applications"].append(app_data)
                self.load_applications()

    def edit_application(self):
        """Edits selected application"""
        current_row = self.app_list.currentRow()
        if current_row >= 0:
            app = self.config["applications"][current_row]
            dialog = ApplicationDialog(self, app)
            if dialog.exec() == QDialog.Accepted:
                app_data = dialog.get_application_data()
                if app_data:
                    app_data["position"] = app["position"]
                    self.config["applications"][current_row] = app_data
                    self.load_applications()

    def remove_application(self):
        """Removes selected application"""
        current_row = self.app_list.currentRow()
        if current_row >= 0:
            app = self.config["applications"][current_row]
            reply = QMessageBox.question(self, "Confirmation",
                                       f"Are you sure you want to remove {app['name']}?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.config["applications"][current_row]
                self.load_applications()

    def accept(self):
        """Saves changes and closes window"""
        if self.config_manager.save_config(self.config):
            super().accept()
        else:
            QMessageBox.warning(self, "Error", "Cannot save configuration!")


class ApplicationDialog(QDialog):
    """Add/edit application dialog"""

    def __init__(self, parent=None, app_data=None):
        super().__init__(parent)
        self.app_data = app_data
        self.setup_ui()
        if app_data:
            self.load_data(app_data)

    def setup_ui(self):
        """Configures application dialog interface"""
        self.setWindowTitle("Add/Edit Application")
        self.setModal(True)
        self.resize(500, 250)

        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #3b3b3b;
                color: white;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Command (e.g. notepad.exe, calc.exe):"))
        command_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        command_layout.addWidget(self.command_input)

        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self.browse_command)
        command_layout.addWidget(browse_btn)

        layout.addLayout(command_layout)

        layout.addWidget(QLabel("Icon (optional):"))
        icon_layout = QHBoxLayout()
        self.icon_input = QLineEdit()
        icon_layout.addWidget(self.icon_input)

        browse_icon_btn = QPushButton("🖼️ Browse Icon")
        browse_icon_btn.clicked.connect(self.browse_icon)
        icon_layout.addWidget(browse_icon_btn)

        layout.addLayout(icon_layout)

        examples_label = QLabel("Windows command examples:\ncalc.exe, explorer.exe")
        examples_label.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(examples_label)

        button_layout = QHBoxLayout()

        ok_btn = QPushButton("✅ OK")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_data(self, app_data):
        """Loads application data to form"""
        self.name_input.setText(app_data.get("name", ""))
        self.command_input.setText(app_data.get("command", ""))
        self.icon_input.setText(app_data.get("icon", ""))

    def browse_command(self):
        """Browse for executable file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose Executable File", "", 
            "Executable files (*.exe *.bat *.cmd *.com);;All files (*)" # to test!
        )
        if file_path:
            self.command_input.setText(file_path)
            if not self.name_input.text():
                name = os.path.splitext(os.path.basename(file_path))[0]
                self.name_input.setText(name.title())

    def browse_icon(self):
        """Browse for icon file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose Icon", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.ico *.svg);;All files (*)" # to test!
        )
        if file_path:
            icon_filename = os.path.basename(file_path)
            icon_dest = os.path.join("icons", icon_filename)

            try:
                os.makedirs("icons", exist_ok=True)
                import shutil
                shutil.copy2(file_path, icon_dest)
                self.icon_input.setText(icon_filename)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Cannot copy icon: {e}")
                self.icon_input.setText(os.path.basename(file_path))

    def get_application_data(self):
        """Returns application data from form"""
        name = self.name_input.text().strip()
        command = self.command_input.text().strip()
        icon = self.icon_input.text().strip()

        if not name or not command:
            QMessageBox.warning(self, "Error", "Name and command are required!")
            return None

        return {
            "name": name,
            "command": command,
            "icon": icon or "default.png"
        }


class RadialLauncher(QApplication):
    """Main application class - Qt Cursor Edition"""

    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        self.setApplicationName("AVO Radial Launcher")
        self.setApplicationVersion("1.1.0")
        self.setQuitOnLastWindowClosed(False)

        self.config_manager = ConfigManager()
        self.radial_menu = StyledRadialMenu(self.config_manager)

        self.mouse_listener = MouseListener()
        self.mouse_listener.middle_clicked.connect(self.show_menu)

        self.setup_system_tray()

        os.makedirs("icons", exist_ok=True)

        print("🎯 AVO Radial Launcher .V1.1.0")

    def setup_system_tray(self):
        """Configures system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                               "System tray is not available on this system.")
            return

        self.tray_icon = QSystemTrayIcon(self)

        icon_path = os.path.join("icons", "launcher.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Create icon
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            gradient = QRadialGradient(12, 12, 12)
            gradient.setColorAt(0, QColor(100, 150, 255))
            gradient.setColorAt(1, QColor(50, 100, 200))

            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.drawEllipse(2, 2, 20, 20)
            painter.end()

            self.tray_icon.setIcon(QIcon(pixmap))

        tray_menu = QMenu()

        show_action = QAction("🎯 Show Menu", self)
        show_action.triggered.connect(self.show_menu_at_cursor)
        tray_menu.addAction(show_action)

        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.open_settings)
        tray_menu.addAction(settings_action)

        tray_menu.addSeparator()

        quit_action = QAction("🚪 Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("AVO Radial Launcher V1.1.0\nEnjoy!")
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        """Handles system tray icon clicks"""
        if reason == QSystemTrayIcon.Trigger:
            self.show_menu_at_cursor()

    def show_menu_at_cursor(self):
        """Shows menu at Qt cursor position"""
        cursor_pos = QCursor.pos()
        self.show_menu(cursor_pos.x(), cursor_pos.y())

    def open_settings(self):
        """Opens settings window"""
        settings_dialog = SettingsDialog(self.config_manager)
        if settings_dialog.exec() == QDialog.Accepted:
            self.radial_menu.config = self.config_manager.config
            self.radial_menu.setup_animations()

    def start_listening(self):
        """Starts mouse listening"""
        if MOUSE_AVAILABLE:
            self.mouse_listener.start()
        else:
            print("Mouse listening disabled - missing 'mouse' library")
            print("Use system tray icon or install: pip install mouse")

    def show_menu(self, x, y):
        """Shows radial menu at x,y position"""
        self.radial_menu.animated_show(x, y)

    def quit_application(self):
        """Closes application"""
        if MOUSE_AVAILABLE:
            self.mouse_listener.stop()
            self.mouse_listener.wait()
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()

        if hasattr(self.radial_menu, 'global_mouse_monitor') and self.radial_menu.global_mouse_monitor.isRunning():
            self.radial_menu.global_mouse_monitor.stop()
            self.radial_menu.global_mouse_monitor.wait(2000)

        self.quit()


def main():
    """Main program function"""
    try:
        app = RadialLauncher(sys.argv)

        missing_modules = []
        if not WIN32_AVAILABLE:
            missing_modules.append("pywin32")
        if not MOUSE_AVAILABLE:
            missing_modules.append("mouse")

        if missing_modules:
            message = f"⚠️  Missing modules: {', '.join(missing_modules)}"
            message += f"\n💡 Install: pip install {' '.join(missing_modules)}"
            print(message)

        app.start_listening()

        return app.exec()

    except KeyboardInterrupt:
        print("\n👋 Closing application...")
        if 'app' in locals():
            app.quit_application()
        return 0
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

# I need more coffee!