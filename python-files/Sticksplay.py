# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 13:43:35 2025

@author: MVomScheidt31
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 13:40:21 2025

@author: MVomScheidt31
"""

import sys
import random
import time
import math
import win32gui
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF

# Constants
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
WS_EX_LAYERED = 0x00080000
SWP_NOACTIVATE = 0x0010
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040
HWND_BOTTOM = 1

HEAD_SIZE = 40
BODY_LENGTH = 60
STEP_DELAY = 30  # ms

FRIEND_COLORS = [
    QColor(0, 128, 255),    # Blue
    QColor(255, 255, 0),    # Yellow
    QColor(128, 0, 255),    # Purple
    QColor(0, 255, 0),      # Green
    QColor(255, 0, 0),      # Red


]



class Stickman:
    def __init__(self, x, y, color, name=""):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.velocity_y = 0
        self.direction = 1
        self.is_dragging = False
        self.drag_offset = QPoint()
        self.walk_cycle = 0.0
        self.run_after_drag = False
        self.state = "idle"
        self.state_timer = 0
        self.climb_progress = 0
        self.topwalk_counter = 0
        self.wave_counter = 0
        self.waving = False
        screen = QDesktopWidget().screenGeometry()
        self.screen_width = screen.width()
        self.ground_level = screen.height() - 180  # Adjusted for typical taskbar + head height

    def apply_gravity(self):
        if self.y < self.ground_level:
            self.velocity_y += 1
            self.y += self.velocity_y
            if self.y > self.ground_level:
                self.y = self.ground_level
                self.velocity_y = 0

    def update_ai(self):
        if self.is_dragging:
            return

        if self.run_after_drag:
            self.x += self.direction * 10
            self.walk_cycle += 0.3
            if self.state not in ("climb", "topwalk"):
                self.apply_gravity()
            # Fix: Ensure animation plays when running away
            self.state = "walk"
            if self.x < -100 or self.x > self.screen_width + 100:
                self.run_after_drag = False
                self.state = "idle"
                self.velocity_y = 0
                self.y = self.ground_level
                self.walk_cycle = 0
                self.direction *= -1
            return

        if self.waving:
            self.wave_counter += 1
            if self.wave_counter > 20:
                self.waving = False
                self.wave_counter = 0
                self.state = "idle"
            return

        if self.state_timer > 0:
            self.state_timer -= 1

        if self.state == "idle":
            self.walk_cycle = 0
            if self.state_timer <= 0:
                next_action = random.choices(["walk", "jump", "wave", "idle"], weights=[20, 1, 1, 3])[0]
                if next_action == "walk":
                    self.state = "walk"
                    self.state_timer = random.randint(30, 80)
                elif next_action == "jump" and self.y == self.ground_level:
                    self.state = "jump"
                    self.velocity_y = -15
                elif next_action == "wave" and self.y == self.ground_level:
                    self.waving = True
                    self.wave_counter = 0
                else:
                    self.state_timer = random.randint(20, 50)

        elif self.state == "walk":
            self.x += self.direction * 5
            self.walk_cycle += 0.2

            if (self.x >= self.screen_width - HEAD_SIZE and self.direction == 1) or (self.x <= 0 and self.direction == -1):
                self.state = "climb"
                self.climb_progress = 0

            if self.state_timer <= 0:
                if random.random() < 0.7:
                    self.direction *= -1
                self.state = "idle"
                self.state_timer = random.randint(20, 50)

            if random.random() < 0.02 and self.y == self.ground_level:
                self.state = "jump"
                self.velocity_y = -15

        elif self.state == "jump":
            self.x += self.direction * 3
            self.velocity_y += 1
            self.y += self.velocity_y
            if self.y >= self.ground_level:
                self.y = self.ground_level
                self.velocity_y = 0
                self.state = "idle"
                self.state_timer = random.randint(20, 50)
                self.walk_cycle = 0

        elif self.state == "climb":
            self.y -= 10
            self.climb_progress += 5
            if self.y <= 0:
                self.y = 0
                self.state = "topwalk"
                self.topwalk_counter = 0
                self.direction *= -1

        elif self.state == "topwalk":
            self.x += self.direction * 5
            self.walk_cycle += 0.2
            self.topwalk_counter += 0.5

            if self.topwalk_counter >= 33 or \
               (self.direction == 1 and self.x >= self.screen_width - HEAD_SIZE) or \
               (self.direction == -1 and self.x <= 0):
                self.state = "drop"
            elif random.random() < 0.01 and self.y == self.ground_level:
                self.waving = True
                self.wave_counter = 0

        elif self.state == "drop":
            self.y += 10
            if self.y >= self.ground_level:
                self.y = self.ground_level
                self.state = "idle"
                self.state_timer = random.randint(20, 50)

        if self.state not in ("climb", "topwalk"):
            self.apply_gravity()

    def draw(self, painter):
        pen = QPen(self.color, 4)
        painter.setPen(pen)
        painter.setBrush(self.color)

        painter.drawEllipse(self.x, self.y, HEAD_SIZE, HEAD_SIZE)

        body_x = self.x + HEAD_SIZE // 2
        head_center_y = self.y + HEAD_SIZE // 2
        body_top = head_center_y
        body_bottom = body_top + BODY_LENGTH
        painter.drawLine(body_x, body_top, body_x, body_bottom)


        arm_y = body_top + 20
        if self.waving:
            wave_up = (self.wave_counter // 5) % 2 == 0
            painter.drawLine(body_x, arm_y, body_x + 20 * self.direction, arm_y - (20 if wave_up else 0))
        else:
            painter.drawLine(body_x, arm_y, body_x - 20, arm_y + 30)
            painter.drawLine(body_x, arm_y, body_x + 20, arm_y + 30)

        self.draw_legs(painter, body_x, body_bottom)

    def draw_legs(self, painter, body_x, leg_top_y):
        if self.state == "idle":
            left_leg_end = QPointF(body_x - 15, leg_top_y + 40)
            right_leg_end = QPointF(body_x + 15, leg_top_y + 40)
            painter.drawLine(QPointF(body_x, leg_top_y), left_leg_end)
            painter.drawLine(QPointF(body_x, leg_top_y), right_leg_end)
        else:
            walk_phase = self.walk_cycle
            stride = 15
            lift = 10

            left_dx = math.sin(walk_phase) * stride
            left_dy = abs(math.cos(walk_phase)) * lift

            right_dx = math.sin(walk_phase + math.pi) * stride
            right_dy = abs(math.cos(walk_phase + math.pi)) * lift

            painter.drawLine(QPointF(body_x, leg_top_y),
                             QPointF(body_x + left_dx, leg_top_y + 30 + left_dy))
            painter.drawLine(QPointF(body_x, leg_top_y),
                             QPointF(body_x + right_dx, leg_top_y + 30 + right_dy))


class DesktopOverlay(QWidget):
    def __init__(self):
        super().__init__()
        screen = QDesktopWidget().screenGeometry()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, screen.width(), screen.height())

        self.orange = Stickman(500, screen.height() - 180, QColor(255, 165, 0), "Orange")
        self.friends = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(STEP_DELAY)

        self.start_time = time.time()
        self.last_friend_join_time = 0
        self.friend_join_interval = 5 * 60
        self.max_cycle_time = 999999999999999999999999999 * 3600

        self.show()
        QTimer.singleShot(1000, self.move_behind_windows)

    def move_behind_windows(self):
        hwnd = win32gui.FindWindow(None, "PyQt5")
        if hwnd:
            style = win32gui.GetWindowLong(hwnd, GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, GWL_EXSTYLE,
                                   style | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE | WS_EX_LAYERED)
            win32gui.SetWindowPos(hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                                  SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW)

    def update_scene(self):
        now = time.time()
        if now - self.start_time > self.max_cycle_time:
            self.friends.clear()
            self.start_time = now
            self.last_friend_join_time = 0

        if now - self.last_friend_join_time > self.friend_join_interval and len(self.friends) < len(FRIEND_COLORS):
            color = FRIEND_COLORS[len(self.friends)]
            screen = QDesktopWidget().screenGeometry()
            new_friend = Stickman(-100, screen.height() - 180, color, f"Friend{len(self.friends)+1}")
            new_friend.direction = 1
            new_friend.state = "walk"
            new_friend.state_timer = random.randint(30, 80)
            self.friends.append(new_friend)
            self.last_friend_join_time = now

        self.orange.update_ai()
        for f in self.friends[:]:
            f.update_ai()
            if f.x < -150 or f.x > self.width() + 150:
                self.friends.remove(f)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.orange.draw(painter)
        for f in self.friends:
            f.draw(painter)

    def mousePressEvent(self, event):
        pos = event.pos()
        for sm in [self.orange] + self.friends:
            if sm.x <= pos.x() <= sm.x + HEAD_SIZE and sm.y <= pos.y() <= sm.y + HEAD_SIZE + BODY_LENGTH + 40:
                sm.is_dragging = True
                sm.drag_offset = pos - QPoint(sm.x, sm.y)
                sm.run_after_drag = False
                sm.state = "idle"
                sm.state_timer = 0
                return

    def mouseMoveEvent(self, event):
        pos = event.pos()
        for sm in [self.orange] + self.friends:
            if sm.is_dragging:
                sm.x = max(0, min(pos.x() - sm.drag_offset.x(), self.width() - HEAD_SIZE))
                sm.y = max(0, min(pos.y() - sm.drag_offset.y(), sm.ground_level))
                sm.velocity_y = 0

    def mouseReleaseEvent(self, event):
        for sm in [self.orange] + self.friends:
            if sm.is_dragging:
                sm.is_dragging = False
                sm.run_after_drag = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DesktopOverlay()
    sys.exit(app.exec_())
