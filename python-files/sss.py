import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QCheckBox, QDoubleSpinBox, QGroupBox, QPushButton
from PyQt5.QtCore import QTimer
import pyautogui
from pynput import mouse, keyboard

# ---------- Shared State ----------
state_lock = threading.Lock()
state = {
    "left_pressed": False,
    "right_pressed": False,
    "weapon": "AR",
    "crouch": False,
    "auto_smg_crouch": True,
    "scope": "Red Dot",
    "recoil_on": False,
    "x_move": -1.5,
    "y_move": 5.1,
    "delay": 0.006,
    "secondary_delay": 0.001,
    "sensitivity": 1.0
}

scope_multipliers = {
    "Red Dot": 1.0,
    "2x": 1.25,
    "3x": 1.5,
    "4x": 1.8,
    "6x": 2.2
}

# ---------- Recoil Loop ----------
def recoil_loop():
    while True:
        with state_lock:
            left = state["left_pressed"]
            right = state["right_pressed"]
            weapon = state["weapon"]
            scope = state["scope"]
            sens = state["sensitivity"]
            x_move = state["x_move"]
            y_move = state["y_move"]
            delay_val = state["delay"]
            sec_delay = state["secondary_delay"]

        if left and right:
            multiplier = scope_multipliers.get(scope, 1.0)
            pyautogui.moveRel(x_move * sens * multiplier, y_move * sens * multiplier)
            time.sleep(delay_val)
            time.sleep(sec_delay)
            with state_lock:
                state["recoil_on"] = True
        else:
            with state_lock:
                state["recoil_on"] = False
            time.sleep(0.001)

threading.Thread(target=recoil_loop, daemon=True).start()

# ---------- Crouch Logic ----------
def apply_crouch_logic():
    with state_lock:
        w = state["weapon"]
        c = state["crouch"]
        auto = state["auto_smg_crouch"]
    if auto and w == "SMG":
        new_w = "SMG_Crouch" if c else "SMG"
    elif c and w == "AR":
        new_w = "AR_Crouch"
    elif not c and w == "AR_Crouch":
        new_w = "AR"
    else:
        new_w = w
    with state_lock:
        state["weapon"] = new_w

# ---------- Mouse & Keyboard ----------
def on_click(x, y, button, pressed):
    with state_lock:
        if button == mouse.Button.left:
            state["left_pressed"] = pressed
        if button == mouse.Button.right:
            state["right_pressed"] = pressed

def on_press(key):
    try:
        k = key.char
    except AttributeError:
        k = None
    with state_lock:
        # Toggle crouch
        if k in ('c','C'):
            state["crouch"] = not state["crouch"]
            apply_crouch_logic()
        # Switch weapon (key '1')
        if k == '1':
            if state["weapon"].startswith("AR"):
                state["weapon"] = "SMG_Crouch" if state["crouch"] and state["auto_smg_crouch"] else "SMG"
            else:
                state["weapon"] = "AR_Crouch" if state["crouch"] else "AR"
        # ESC to exit
        if key == keyboard.Key.esc:
            mouse_listener.stop()
            kb_listener.stop()
            app.quit()

mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.daemon = True
mouse_listener.start()

kb_listener = keyboard.Listener(on_press=on_press)
kb_listener.daemon = True
kb_listener.start()

# ---------- GUI ----------
class RecoilGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recoil Helper")
        self.resize(400, 300)
        layout = QVBoxLayout()

        # Status
        self.lbl_weapon = QLabel()
        self.lbl_scope = QLabel()
        self.lbl_crouch = QLabel()
        self.lbl_recoil = QLabel()
        layout.addWidget(self.lbl_weapon)
        layout.addWidget(self.lbl_scope)
        layout.addWidget(self.lbl_crouch)
        layout.addWidget(self.lbl_recoil)

        # Settings
        group = QGroupBox("Recoil Settings")
        g_layout = QVBoxLayout()
        self.sens_spin = QDoubleSpinBox()
        self.sens_spin.setRange(0.1, 10.0)
        self.sens_spin.setSingleStep(0.05)
        self.sens_spin.setValue(state["sensitivity"])
        self.sens_spin.setPrefix("Sensitivity: ")
        g_layout.addWidget(self.sens_spin)

        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-50,50)
        self.x_spin.setSingleStep(0.1)
        self.x_spin.setValue(state["x_move"])
        self.x_spin.setPrefix("X Move: ")
        g_layout.addWidget(self.x_spin)

        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-50,50)
        self.y_spin.setSingleStep(0.1)
        self.y_spin.setValue(state["y_move"])
        self.y_spin.setPrefix("Y Move: ")
        g_layout.addWidget(self.y_spin)

        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.001,0.1)
        self.delay_spin.setSingleStep(0.001)
        self.delay_spin.setValue(state["delay"])
        self.delay_spin.setPrefix("Delay: ")
        g_layout.addWidget(self.delay_spin)

        self.sec_spin = QDoubleSpinBox()
        self.sec_spin.setRange(0.001,0.1)
        self.sec_spin.setSingleStep(0.001)
        self.sec_spin.setValue(state["secondary_delay"])
        self.sec_spin.setPrefix("Secondary Delay: ")
        g_layout.addWidget(self.sec_spin)

        group.setLayout(g_layout)
        layout.addWidget(group)

        # Auto SMG crouch
        self.chk_smg = QCheckBox("Auto SMG Crouch")
        self.chk_smg.setChecked(state["auto_smg_crouch"])
        layout.addWidget(self.chk_smg)

        # Apply Button
        self.btn_apply = QPushButton("Apply Settings")
        layout.addWidget(self.btn_apply)

        self.setLayout(layout)

        # Timer refresh
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(100)

        # Connections
        self.btn_apply.clicked.connect(self.apply_settings)
        self.chk_smg.stateChanged.connect(self.toggle_auto_smg)

    def refresh(self):
        with state_lock:
            self.lbl_weapon.setText(f"Weapon: {state['weapon']}")
            self.lbl_scope.setText(f"Scope: {state['scope']}")
            self.lbl_crouch.setText(f"Crouch: {'ON' if state['crouch'] else 'OFF'}")
            self.lbl_recoil.setText(f"Recoil Active: {'YES' if state['recoil_on'] else 'NO'}")

    def apply_settings(self):
        with state_lock:
            state["sensitivity"] = self.sens_spin.value()
            state["x_move"] = self.x_spin.value()
            state["y_move"] = self.y_spin.value()
            state["delay"] = self.delay_spin.value()
            state["secondary_delay"] = self.sec_spin.value()

    def toggle_auto_smg(self, val):
        with state_lock:
            state["auto_smg_crouch"] = True if val==2 else False
            apply_crouch_logic()

# ---------- Run App ----------
app = QApplication(sys.argv)
window = RecoilGUI()
window.show()
sys.exit(app.exec_())
