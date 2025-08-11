# pip install PySide6 numpy
import math
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QWidget, QFormLayout, QDoubleSpinBox, QSpinBox,
    QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt

STRENGTH_MAP = {
    3.6: (300, 180, 290, 170),
    4.6: (400, 240, 390, 230),
    4.8: (400, 320, 390, 310),
    5.6: (500, 300, 490, 290),
    5.8: (600, 360, 590, 350),
    6.6: (600, 360, 590, 350),
    6.8: (800, 640, 780, 620),
    8.8: (800, 640, 780, 620),
    9.8: (900, 720, 880, 700),
    10.9: (1000, 900, 980, 880),
    12.9: (1200, 1080, 1170, 1050),
}

def sigma_tw(R_T_p02: float) -> float:
    return R_T_p02 / 2.0

def x_coeff(T: float) -> float:
    # Табличные данные (примерные)
    T_table = np.array([20, 200, 300])     # °C
    x_table = np.array([1.0, 1.5, 2.0])    # коэффициент x
    return float(np.round(np.interp(T, T_table, x_table), 2))

def compute(params: dict) -> dict:
    T   = params["T"]
    P   = params["P"]
    Ph  = params["Ph"]
    sc  = params["strength_class"]
    d0  = params["d0"]   # не используется в формулах ниже, но оставлен как вход
    z   = params["z"]
    Dn  = params["Dn"]
    b0  = params["b0"]
    sigma_g = params["sigma"]    # толщина прокладки
    is_ring = params["is_ring"]

    R_Th_m, R_Th_p02, R_T_m, R_T_p02 = STRENGTH_MAP[sc]

    Dm = float(Dn - b0)
    b  = math.sqrt(10.0 * b0)
    q0 = 5.0 if is_ring else 80.0 / math.sqrt(10.0 * sigma_g)

    # Автоподбор m по правилу
    m = 1.2 if b0 < 5.0 else 1.6

    X1 = x_coeff(T)

    F_ob  = math.pi * Dm * b * q0
    F_prp = math.pi * Dm * b * m * P  * X1
    F_prh = math.pi * Dm * b * m * Ph
    F_p   = 0.785 * (Dm ** 2) * P
    F_ph  = 0.785 * (Dm ** 2) * Ph

    F_0   = max(F_ob, F_prh + F_ph, F_prp + F_p)
    d_0_min = math.sqrt(1.27 * (F_0 / (z * sigma_tw(R_T_p02))))

    return {
        "R_T_p02": R_T_p02,
        "X1": X1,
        "q0": q0,
        "sigma_tw": sigma_tw(R_T_p02),
        "m": m,
        "Dm": Dm,
        "b": b,
        "F_ob": F_ob,
        "F_prp": F_prp,
        "F_prh": F_prh,
        "F_p": F_p,
        "F_ph": F_ph,
        "F_0": F_0,
        "d_0_min": d_0_min
    }

class BoltCalcUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расчёт минимального диаметра шпилек (ПНАЭ)")
        self.build_ui()

    def build_ui(self):
        form = QFormLayout()

        self.in_T = QDoubleSpinBox(); self.in_T.setRange(-1000, 2000); self.in_T.setValue(45); self.in_T.setSuffix(" °C")
        self.in_P = QDoubleSpinBox(); self.in_P.setRange(0, 10000); self.in_P.setDecimals(3); self.in_P.setValue(11.77); self.in_P.setSuffix(" МПа")
        self.in_Ph = QDoubleSpinBox(); self.in_Ph.setRange(0, 10000); self.in_Ph.setDecimals(3); self.in_Ph.setValue(15); self.in_Ph.setSuffix(" МПа")

        self.in_strength = QComboBox()
        for k in sorted(STRENGTH_MAP.keys(), key=lambda v:(float(str(v).split('.')[0]), float(str(v).split('.')[1]))):
            self.in_strength.addItem(str(k))
        self.in_strength.setCurrentText("5.6")

        self.in_d0 = QDoubleSpinBox(); self.in_d0.setRange(0, 1000); self.in_d0.setDecimals(3); self.in_d0.setValue(13.835); self.in_d0.setSuffix(" мм")
        self.in_z  = QSpinBox(); self.in_z.setRange(1, 1000); self.in_z.setValue(8)
        self.in_Dn = QDoubleSpinBox(); self.in_Dn.setRange(0, 10000); self.in_Dn.setDecimals(3); self.in_Dn.setValue(94); self.in_Dn.setSuffix(" мм")
        self.in_b0 = QDoubleSpinBox(); self.in_b0.setRange(0, 1000); self.in_b0.setDecimals(3); self.in_b0.setValue(5.8); self.in_b0.setSuffix(" мм")
        self.in_sigma = QDoubleSpinBox(); self.in_sigma.setRange(0, 1000); self.in_sigma.setDecimals(3); self.in_sigma.setValue(3.6); self.in_sigma.setSuffix(" мм")
        self.in_is_ring = QCheckBox("Резиновое кольцо (is_ring)"); self.in_is_ring.setChecked(True)

        form.addRow("Расчётная температура T:", self.in_T)
        form.addRow("Расчётное давление P:", self.in_P)
        form.addRow("Давление гидроиспытаний Ph:", self.in_Ph)
        form.addRow("Класс прочности болта:", self.in_strength)
        form.addRow("Внутренний диаметр болта d₀:", self.in_d0)
        form.addRow("Число болтов z:", self.in_z)
        form.addRow("Наружный диаметр паза Dₙ:", self.in_Dn)
        form.addRow("Ширина прокладки b₀:", self.in_b0)
        form.addRow("Толщина прокладки σ:", self.in_sigma)
        form.addRow(self.in_is_ring)

        self.btn_calc = QPushButton("Рассчитать")
        self.btn_calc.clicked.connect(self.on_calc)

        self.out = QTextEdit(); self.out.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addLayout(form)

        btn_row = QHBoxLayout(); btn_row.addWidget(self.btn_calc); btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addWidget(QLabel("Результаты:"))
        layout.addWidget(self.out)
        self.setLayout(layout)
        self.resize(700, 650)

        # Автопересчёт по изменениям (удобно при подборе)
        for w in [self.in_T, self.in_P, self.in_Ph, self.in_d0, self.in_z, self.in_Dn, self.in_b0, self.in_sigma]:
            w.valueChanged.connect(self.on_calc)
        self.in_strength.currentTextChanged.connect(self.on_calc)
        self.in_is_ring.stateChanged.connect(self.on_calc)

        self.on_calc()

    def gather(self) -> dict:
        return {
            "T": self.in_T.value(),
            "P": self.in_P.value(),
            "Ph": self.in_Ph.value(),
            "strength_class": float(self.in_strength.currentText()),
            "d0": self.in_d0.value(),
            "z": self.in_z.value(),
            "Dn": self.in_Dn.value(),
            "b0": self.in_b0.value(),
            "sigma": self.in_sigma.value(),
            "is_ring": self.in_is_ring.isChecked(),
        }

    def on_calc(self):
        try:
            params = self.gather()
            res = compute(params)

            txt = []
            txt.append("Дополнение к входным данным:")
            txt.append(f"  R_T_p0.2: {res['R_T_p02']:.3f} МПа")
            txt.append(f"  X1: {res['X1']:.3f}")
            txt.append(f"  q0: {res['q0']:.3f}")
            txt.append(f"  σ_tw: {res['sigma_tw']:.3f} МПа")
            txt.append(f"  m (автоподбор): {res['m']:.2f}")
            txt.append(f"  Dm: {res['Dm']:.3f} мм")
            txt.append(f"  b: {res['b']:.3f} мм")

            txt.append("\nСиловые параметры:")
            txt.append(f"  F_ob : {res['F_ob']:.6f}")
            txt.append(f"  F_prp: {res['F_prp']:.6f}")
            txt.append(f"  F_prh: {res['F_prh']:.6f}")
            txt.append(f"  F_p  : {res['F_p']:.6f}")
            txt.append(f"  F_ph : {res['F_ph']:.6f}")
            txt.append(f"  F_0  : {res['F_0']:.6f}")

            txt.append("\nИтог:")
            txt.append(f"  d₀_min: {res['d_0_min']:.6f} мм")

            self.out.setPlainText("\n".join(txt))
        except Exception as e:
            self.out.setPlainText(f"Ошибка расчёта: {e}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = BoltCalcUI()
    w.show()
    sys.exit(app.exec())
