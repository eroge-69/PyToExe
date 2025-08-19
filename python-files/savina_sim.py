#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Savina 300-Style Ventilator Simulator (Educational)
Author: ChatGPT
License: MIT
DISCLAIMER: Educational simulator only. Not a medical device.
"""
import sys, math, random, time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    import pyqtgraph as pg
    import numpy as np
except Exception as e:
    print("This app needs PySide6, pyqtgraph, numpy.")
    print("Install with: pip install PySide6 pyqtgraph numpy")
    raise

# ------------------------------
# Theming (Savina-ish palette)
# ------------------------------
BG = "#dff3f1"            # main screen light teal
FRAME = "#bfe8e3"
WAVE = "#193b7a"
WAVE_FILL = (25, 59, 122, 80)  # semi-transparent navy
TEXT_DARK = "#0a1a1e"
SOFTKEY = "#eaf8f6"
GREEN_BTN = "#5fbf66"
AMBER = "#e5b40c"
RED = "#cc2b2b"
GREY = "#7f8b90"
DARK_UI = "#0f1b1f"

# ------------------------------
# Simulation Model
# ------------------------------
@dataclass
class VentSettings:
    mode: str = "VCV"        # VCV, PCV, SIMV, CPAP/PS, AutoFlow
    rr: int = 14             # breaths/min
    ie_i: float = 1.0        # I:E ratio numerator
    ie_e: float = 2.0        # I:E ratio denominator
    vt: float = 450.0        # mL (for VCV)
    pinsp: float = 18.0      # cmH2O (for PCV/PS)
    peep: float = 5.0        # cmH2O
    fio2: float = 40.0       # %
    ps: float = 10.0         # cmH2O
    trigger: float = 2.0     # L/min flow trigger
    autoflow: bool = True

@dataclass
class PatientModel:
    compliance_ml_cmH2O: float = 40.0  # mL/cmH2O
    resistance_cmH2O_Lps: float = 12.0 # cmH2O/(L/s)
    effort: float = 0.2                # 0..1

@dataclass
class SimState:
    t: float = 0.0
    breath_start: float = 0.0
    vol: float = 0.0     # L above FRC
    phase: str = "insp"  # insp/exp
    phase_time: float = 0.0

@dataclass
class Metrics:
    ppeak: float = 0.0
    pmean: float = 0.0
    tve: float = 0.0
    mv: float = 0.0
    spo2: float = 97.0

class LungSimulator:
    def __init__(self, settings: VentSettings, patient: PatientModel):
        self.settings = settings
        self.patient = patient
        self.state = SimState()

    def timing(self) -> Tuple[float, float, float]:
        cycle = 60.0 / max(1.0, self.settings.rr)
        i_frac = self.settings.ie_i / (self.settings.ie_i + self.settings.ie_e)
        ti = cycle * i_frac
        te = cycle - ti
        return cycle, ti, te

    def step(self, dt: float) -> Tuple[float, float, float]:
        s = self.settings
        p = self.patient
        st = self.state
        R = max(1e-3, p.resistance_cmH2O_Lps)
        C = max(1e-6, p.compliance_ml_cmH2O) / 1000.0  # L/cmH2O
        base = s.peep

        cycle, ti, _te = self.timing()
        in_cycle = (st.t - st.breath_start) % cycle
        new_phase = "insp" if in_cycle < ti else "exp"
        if new_phase != st.phase:
            st.phase = new_phase
            st.phase_time = 0.0
            if st.phase == "insp":
                st.breath_start = st.t
        else:
            st.phase_time += dt

        # Commanded flow / target pressure (simplified RC)
        targetP = base
        cmd_flow = 0.0  # L/s

        if s.mode == "VCV" or (s.mode == "AutoFlow" and s.autoflow):
            vtL = s.vt / 1000.0
            flow_const = vtL / max(1e-3, ti)
            cmd_flow = flow_const if in_cycle < ti else 0.0
            targetP = base + cmd_flow * R + st.vol / C
        elif s.mode == "PCV":
            targetP = base + s.pinsp if st.phase == "insp" else base
            dp = targetP - (base + st.vol / C)
            cmd_flow = dp / R
        elif s.mode == "SIMV":
            vtL = s.vt / 1000.0
            mandatory = vtL / max(1e-3, ti) if in_cycle < ti else 0.0
            spont = 0.0
            if st.phase == "exp" and random.random() < 0.03 * p.effort:
                spont = s.ps / R * math.exp(-st.phase_time / (R * C))
                targetP = base + s.ps
            else:
                targetP = base + mandatory * R + st.vol / C
            cmd_flow = mandatory + spont
        elif s.mode == "CPAP/PS":
            targetP = base
            if random.random() < 0.04 * p.effort:  # PS event
                targetP = base + s.ps
            dp = targetP - (base + st.vol / C)
            cmd_flow = dp / R

        # Expiration valve behavior
        flow = cmd_flow
        if s.mode != "CPAP/PS" and st.phase == "exp":
            dp = base - (base + st.vol / C)   # tends to empty to PEEP
            flow = dp / R  # negative

        # Integrate
        st.vol += flow * dt
        if st.vol < 0: st.vol = 0.0
        paw = base + st.vol / C + flow * R

        st.t += dt
        return paw, flow, st.vol

# ------------------------------
# UI Helpers
# ------------------------------
def big_label(text="", size=48, bold=True, color=TEXT_DARK, align=QtCore.Qt.AlignRight):
    lbl = QtWidgets.QLabel(text)
    f = lbl.font()
    f.setPointSize(int(size))
    f.setBold(bold)
    lbl.setFont(f)
    lbl.setStyleSheet(f"color: {color};")
    lbl.setAlignment(align | QtCore.Qt.AlignVCenter)
    return lbl

class SevenSeg(QtWidgets.QWidget):
    def __init__(self, value="0.0", unit="", parent=None):
        super().__init__(parent)
        self.lbl = big_label(value, size=44, bold=True)
        self.unit = QtWidgets.QLabel(unit)
        f = self.unit.font(); f.setPointSize(11); self.unit.setFont(f)
        self.unit.setStyleSheet(f"color:{TEXT_DARK};")
        lay = QtWidgets.QHBoxLayout(self); lay.setContentsMargins(0,0,0,0)
        lay.addWidget(self.lbl, 1)
        lay.addWidget(self.unit, 0, QtCore.Qt.AlignBottom)

    def set(self, value: str, unit: str=None):
        self.lbl.setText(value)
        if unit is not None: self.unit.setText(unit)

class SoftKey(QtWidgets.QPushButton):
    def __init__(self, text, color=SOFTKEY, parent=None):
        super().__init__(text, parent)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            QPushButton{{
              background:{color}; border:1px solid #9fd7d1; border-radius:6px;
              color:{TEXT_DARK}; padding:6px 10px;
            }}
            QPushButton:hover{{ filter:brightness(1.05); }}
        """)

class GreenRound(QtWidgets.QToolButton):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setText(label)
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QtCore.QSize(48,48))
        self.setFixedSize(86,86)
        self.setStyleSheet(f"""
            QToolButton{{
              background:{GREEN_BTN}; border:2px solid #3c9b42; border-radius:43px;
              color:white; font-weight:600;
            }}
            QToolButton:checked{{ border-color:white; box-shadow: 0 0 0 2px white inset; }}
        """)

class Knob(QtWidgets.QDial):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setNotchesVisible(True)
        self.setMinimum(0)
        self.setMaximum(1000)
        self.setSingleStep(1)
        self.setPageStep(5)
        self.setWrapping(False)
        self.setFixedSize(120, 120)
        self.setStyleSheet("""
            QDial { background: #ddeff0; }
        """)

# ------------------------------
# Main Window
# ------------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Savina 300 – Ventilator Simulator (Educational)")
        self.resize(1200, 720)

        # State
        self.settings = VentSettings()
        self.patient = PatientModel()
        self.model = LungSimulator(self.settings, self.patient)
        self.metrics = Metrics()
        self.running = True

        # Buffer for plots
        self.window_seconds = 18.0
        self.max_samples = int(self.window_seconds * 50) + 50
        self.ts: List[float] = []
        self.p_list: List[float] = []
        self.f_list: List[float] = []
        self.v_list: List[float] = []

        self._build_ui()
        self._setup_plots()
        self._setup_bottom_bar()
        self._setup_sidebar()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(20)  # 50 Hz

        self.update_all_labels()

    # --- UI Assembly ---
    def _build_ui(self):
        root = QtWidgets.QWidget()
        self.setCentralWidget(root)
        root.setStyleSheet(f"background:{BG};")
        hh = QtWidgets.QVBoxLayout(root)
        hh.setContentsMargins(8,8,8,8)
        hh.setSpacing(6)

        # Top area: plots + right panel
        top = QtWidgets.QHBoxLayout()
        hh.addLayout(top, 1)

        # Left: plots frame
        self.plot_frame = QtWidgets.QFrame()
        self.plot_frame.setStyleSheet(f"background:{FRAME}; border:1px solid #9fd7d1; border-radius:8px;")
        top.addWidget(self.plot_frame, 3)
        lv = QtWidgets.QVBoxLayout(self.plot_frame)
        lv.setContentsMargins(8,8,8,8)
        lv.setSpacing(6)

        self.plot_pressure = pg.PlotWidget()
        self.plot_flow = pg.PlotWidget()
        self.plot_volume = pg.PlotWidget()
        for w, label in [(self.plot_pressure, "AIRWAY PRESSURE (cmH₂O)"),
                         (self.plot_flow, "FLOW (L/min)"),
                         (self.plot_volume, "VOLUME (L)")]:

            title = QtWidgets.QLabel(label)
            ff = title.font(); ff.setPointSize(9); ff.setBold(True)
            title.setFont(ff)
            title.setStyleSheet(f"color:{TEXT_DARK};")
            lv.addWidget(title)
            lv.addWidget(w, 1)

        # Right panel
        right = QtWidgets.QFrame()
        right.setStyleSheet(f"background:{FRAME}; border:1px solid #9fd7d1; border-radius:8px;")
        right.setFixedWidth(320)
        top.addWidget(right, 0)
        rv = QtWidgets.QVBoxLayout(right); rv.setContentsMargins(8,8,8,8); rv.setSpacing(8)

        # Numbers (like seven-seg)
        grid = QtWidgets.QGridLayout()
        rv.addLayout(grid, 0)
        self.lbl_ppeak = SevenSeg("0.0", "cmH₂O")
        self.lbl_pmean = SevenSeg("0.0", "cmH₂O")
        self.lbl_tve   = SevenSeg("0", "mL")
        self.lbl_mv    = SevenSeg("0.0", "L/min")
        self.lbl_spo2  = SevenSeg("97", "%")
        labels = [("Ppeak", self.lbl_ppeak), ("Pmean", self.lbl_pmean),
                  ("TVe", self.lbl_tve), ("MV", self.lbl_mv), ("SpO₂", self.lbl_spo2)]
        r,c=0,0
        for name, widget in labels:
            caption = QtWidgets.QLabel(name)
            cf = caption.font(); cf.setPointSize(10); cf.setBold(True)
            caption.setFont(cf); caption.setStyleSheet(f"color:{TEXT_DARK};")
            grid.addWidget(caption, r, c, 1, 1)
            grid.addWidget(widget, r, c+1, 1, 1)
            if r%2==0: r+=1
            else: r=0; c+=2

        # Soft keys
        self.soft_alarm = SoftKey("Alarm...")
        self.soft_trend = SoftKey("Trends/Calc")
        self.soft_freeze= SoftKey("Freeze/Start")
        self.soft_hold_i= SoftKey("Insp Hold")
        self.soft_hold_e= SoftKey("Exp Hold")
        self.soft_setup = SoftKey("System/Setup")
        for b in [self.soft_alarm, self.soft_trend, self.soft_freeze, self.soft_hold_i, self.soft_hold_e, self.soft_setup]:
            rv.addWidget(b)

        # Wire soft keys
        self.soft_freeze.clicked.connect(self.toggle_run)
        self.soft_trend.clicked.connect(self.show_trends_dialog)
        self.soft_alarm.clicked.connect(self.show_alarm_dialog)
        self.soft_setup.clicked.connect(self.show_setup_dialog)

        # Bottom area: parameter buttons + knob + banner
        self.bottom_frame = QtWidgets.QFrame()
        self.bottom_frame.setStyleSheet(f"background:{FRAME}; border:1px solid #9fd7d1; border-radius:8px;")
        hh.addWidget(self.bottom_frame, 0)
        bv = QtWidgets.QVBoxLayout(self.bottom_frame); bv.setContentsMargins(8,8,8,8); bv.setSpacing(6)

        # Banner
        self.banner = QtWidgets.QLabel("System Ready • Training Mode")
        bf = self.banner.font(); bf.setPointSize(11); bf.setBold(True)
        self.banner.setFont(bf)
        self.banner.setStyleSheet(f"color:{TEXT_DARK};")
        bv.addWidget(self.banner)

        # Param row
        row = QtWidgets.QHBoxLayout(); row.setSpacing(8)
        bv.addLayout(row)

        # Mode + list
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["VCV","PCV","SIMV","CPAP/PS","AutoFlow"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.mode_combo.setStyleSheet("QComboBox { background:white; }")
        self.mode_combo.setFixedWidth(120)
        row.addWidget(QtWidgets.QLabel("Mode:"))
        row.addWidget(self.mode_combo)

        row.addStretch(1)

        # Green round buttons area
        self.btn_vt   = GreenRound("VT")
        self.btn_rr   = GreenRound("RR")
        self.btn_ie   = GreenRound("I:E")
        self.btn_peep = GreenRound("PEEP")
        self.btn_fio2 = GreenRound("FiO₂")
        self.btn_ps   = GreenRound("PS")
        self.btn_pinsp= GreenRound("P_insp")
        for b in [self.btn_vt, self.btn_rr, self.btn_ie, self.btn_peep, self.btn_fio2, self.btn_ps, self.btn_pinsp]:
            row.addWidget(b)
        row.addStretch(1)

        # Knob area
        knob_box = QtWidgets.QVBoxLayout()
        row.addLayout(knob_box, 0)
        self.knob = Knob(); knob_box.addWidget(self.knob, 0, QtCore.Qt.AlignCenter)
        self.param_label = QtWidgets.QLabel("Select parameter")
        pf = self.param_label.font(); pf.setPointSize(11); pf.setBold(True)
        self.param_label.setFont(pf)
        self.param_label.setStyleSheet(f"color:{TEXT_DARK};")
        self.param_value = big_label("—", size=30, bold=True, color=TEXT_DARK, align=QtCore.Qt.AlignCenter)
        knob_box.addWidget(self.param_label, 0, QtCore.Qt.AlignCenter)
        knob_box.addWidget(self.param_value, 0, QtCore.Qt.AlignCenter)

        # Button selection mapping
        self.param_spec = {
            "VT":      dict(get=lambda: self.settings.vt, set=self.set_vt,    min=200, max=800, step=10, unit="mL"),
            "RR":      dict(get=lambda: self.settings.rr, set=self.set_rr,    min=6,   max=35,  step=1,  unit="bpm"),
            "I:E":     dict(get=lambda: (self.settings.ie_i, self.settings.ie_e), set=self.set_ie, min=0.5, max=4.0, step=0.1, unit=""),
            "PEEP":    dict(get=lambda: self.settings.peep, set=self.set_peep, min=0,   max=18,  step=1,  unit="cmH₂O"),
            "FiO₂":    dict(get=lambda: self.settings.fio2, set=self.set_fio2, min=21,  max=100, step=1,  unit="%"),
            "PS":      dict(get=lambda: self.settings.ps, set=self.set_ps,     min=0,   max=25,  step=1,  unit="cmH₂O"),
            "P_insp":  dict(get=lambda: self.settings.pinsp, set=self.set_pinsp, min=8, max=35,  step=1,  unit="cmH₂O"),
        }
        self.selected_param = None

        # bind
        self.btn_vt.clicked.connect(lambda: self.select_param("VT"))
        self.btn_rr.clicked.connect(lambda: self.select_param("RR"))
        self.btn_ie.clicked.connect(lambda: self.select_param("I:E"))
        self.btn_peep.clicked.connect(lambda: self.select_param("PEEP"))
        self.btn_fio2.clicked.connect(lambda: self.select_param("FiO₂"))
        self.btn_ps.clicked.connect(lambda: self.select_param("PS"))
        self.btn_pinsp.clicked.connect(lambda: self.select_param("P_insp"))
        self.knob.valueChanged.connect(self.knob_changed)

    def _setup_plots(self):
        # common plot styling
        for pw in [self.plot_pressure, self.plot_flow, self.plot_volume]:
            pw.setBackground(BG)
            pw.showGrid(x=True, y=True, alpha=0.25)
            pw.setMenuEnabled(False)
            pw.setMouseEnabled(x=False, y=False)
            ax = pw.getAxis('bottom'); ax.setStyle(tickTextOffset=10)
            ax.setPen(pg.mkPen(GREY))
            ay = pw.getAxis('left'); ay.setPen(pg.mkPen(GREY))
        self.plot_pressure.setYRange(0, 50)
        self.plot_flow.setYRange(-60, 60)
        self.plot_volume.setYRange(0, 1.2)

        # data lines
        self.curve_p = self.plot_pressure.plot([], [], pen=pg.mkPen(WAVE, width=2))
        self.fill_p = pg.FillBetweenItem(
            self.plot_pressure.plot([], [], pen=None),
            self.plot_pressure.plot([], [], pen=None),
            brush=WAVE_FILL
        )
        self.plot_pressure.addItem(self.fill_p)

        self.curve_f = self.plot_flow.plot([], [], pen=pg.mkPen(WAVE, width=2))
        self.curve_v = self.plot_volume.plot([], [], pen=pg.mkPen(WAVE, width=2))

    def _setup_bottom_bar(self):
        pass

    def _setup_sidebar(self):
        pass

    # --- parameter setters ---
    def set_vt(self, v): self.settings.vt = float(max(200, min(800, round(v)))); self.update_all_labels()
    def set_rr(self, v): self.settings.rr = int(max(6, min(35, round(v)))); self.update_all_labels()
    def set_ie(self, vpair):
        # vpair is tuple, adjust using knob to modify E component
        i, e = self.settings.ie_i, self.settings.ie_e
        e = max(1.0, min(8.0, round(vpair, 1)))
        self.settings.ie_i, self.settings.ie_e = 1.0, e
        self.update_all_labels()
    def set_peep(self, v): self.settings.peep = float(max(0, min(18, round(v)))); self.update_all_labels()
    def set_fio2(self, v): self.settings.fio2 = float(max(21, min(100, round(v)))); self.update_all_labels()
    def set_ps(self, v): self.settings.ps = float(max(0, min(25, round(v)))); self.update_all_labels()
    def set_pinsp(self, v): self.settings.pinsp = float(max(8, min(35, round(v)))); self.update_all_labels()

    # --- parameter selection & knob ---
    def select_param(self, name: str):
        self.selected_param = name
        spec = self.param_spec[name]
        self.param_label.setText(name)
        # map current value to knob range 0..1000
        val = spec["get"]()
        if name == "I:E":
            # knob controls E part
            e = val[1]
            k = int(1000 * (e - spec["min"]) / (spec["max"] - spec["min"]))
        else:
            k = int(1000 * (float(val) - spec["min"]) / (spec["max"] - spec["min"]))
        self.knob.blockSignals(True)
        self.knob.setValue(max(0, min(1000, k)))
        self.knob.blockSignals(False)
        self.show_param_value()

    def knob_changed(self, k: int):
        if not self.selected_param: return
        spec = self.param_spec[self.selected_param]
        v = spec["min"] + (spec["max"] - spec["min"]) * (k / 1000.0)
        step = spec["step"]
        v = round(v / step) * step
        if self.selected_param == "I:E":
            spec["set"](v)
        else:
            spec["set"](v)
        self.show_param_value()

    def show_param_value(self):
        if not self.selected_param:
            self.param_value.setText("—")
            return
        spec = self.param_spec[self.selected_param]
        val = spec["get"]()
        unit = spec["unit"]
        if self.selected_param == "I:E":
            text = f"1:{val[1]:.1f}"
        else:
            text = f"{val:.0f}{(' '+unit) if unit else ''}"
        self.param_value.setText(text)

    # --- run toggle ---
    def toggle_run(self):
        self.running = not self.running
        if self.running:
            self.banner.setText("RUNNING")
            self.banner.setStyleSheet(f"color:{TEXT_DARK};")
        else:
            self.banner.setText("FROZEN")
            self.banner.setStyleSheet(f"color:{AMBER}; font-weight:600;")

    # --- dialogs ---
    def show_trends_dialog(self):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Trends / Calculations")
        dlg.setText("Trends page placeholder.\nComing next: P-V and Flow-Volume loops, logs, and trends.")
        dlg.exec()

    def show_alarm_dialog(self):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Alarms")
        dlg.setText("Alarm limits and history placeholder.\nCurrent simple alarms show in banner automatically.")
        dlg.exec()

    def show_setup_dialog(self):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("System Setup")
        dlg.setText("Setup placeholder. Model is educational and independent from Dräger.")
        dlg.exec()

    # --- update loop ---
    def _tick(self):
        dt = 0.02
        if self.running:
            paw, flow, vol = self.model.step(dt)
            t = self.model.state.t
            # store
            self.ts.append(t); self.p_list.append(paw); self.f_list.append(flow*60.0); self.v_list.append(vol)
            # prune
            cutoff = t - self.window_seconds
            while self.ts and self.ts[0] < cutoff:
                self.ts.pop(0); self.p_list.pop(0); self.f_list.pop(0); self.v_list.pop(0)

            # update metrics once per 0.2s
            if int(t*5) % 1 == 0:
                self.compute_metrics()

        # update plots regardless (for freeze view)
        if self.ts:
            x0 = np.array(self.ts) - self.ts[-1]  # relative time for x axis (negative to 0)
            self.curve_p.setData(x0, np.array(self.p_list))
            # fill under curve
            x = x0; y = np.array(self.p_list)
            lower = np.zeros_like(y)
            self.fill_p.curves[0].setData(x, lower)
            self.fill_p.curves[1].setData(x, y)
            self.curve_f.setData(x0, np.array(self.f_list))
            self.curve_v.setData(x0, np.array(self.v_list))

    def compute_metrics(self):
        # compute over last breath (since breath_start)
        st = self.model.state
        t0 = st.breath_start
        idx = [i for i,tt in enumerate(self.ts) if tt >= t0]
        if not idx: return
        start = idx[0]
        pseg = self.p_list[start:]
        vseg = self.v_list[start:]
        if not pseg: return
        ppeak = max(pseg); pmean = sum(pseg)/len(pseg)
        tve = (max(vseg) if vseg else 0.0) * 1000.0
        mv = (tve/1000.0) * self.settings.rr
        spo2 = max(85.0, min(100.0, 90.0 + (self.settings.fio2-21.0)*0.12 + (mv-5.0)*1.2))

        self.metrics = Metrics(ppeak=ppeak, pmean=pmean, tve=tve, mv=mv, spo2=spo2)
        self.update_numbers()
        self.check_alarms()

    def update_numbers(self):
        m = self.metrics
        self.lbl_ppeak.set(f"{m.ppeak:.0f}", "cmH₂O")
        self.lbl_pmean.set(f"{m.pmean:.0f}", "cmH₂O")
        self.lbl_tve.set(f"{m.tve:.0f}", "mL")
        self.lbl_mv.set(f"{m.mv:.1f}", "L/min")
        self.lbl_spo2.set(f"{m.spo2:.0f}", "%")

    def on_mode_changed(self, mode):
        self.settings.mode = mode

    def check_alarms(self):
        alarms = []
        m = self.metrics
        if m.ppeak > 35: alarms.append("HIGH Ppeak")
        if self.settings.mode != "CPAP/PS" and m.tve < self.settings.vt * 0.7: alarms.append("LOW VT")
        if m.spo2 < 90: alarms.append("LOW SpO₂")
        if alarms:
            self.banner.setText("  |  ".join(alarms))
            self.banner.setStyleSheet(f"color:{RED}; font-weight:600;")
        else:
            self.banner.setText("System Ready • Training Mode")
            self.banner.setStyleSheet(f"color:{TEXT_DARK};")

    def update_all_labels(self):
        # called after settings change
        self.update_numbers()
        self.check_alarms()
        # refresh bottom button tooltips with current values
        self.btn_vt.setToolTip(f"VT: {self.settings.vt:.0f} mL")
        self.btn_rr.setToolTip(f"RR: {self.settings.rr} bpm")
        self.btn_ie.setToolTip(f"I:E = 1:{self.settings.ie_e:.1f}")
        self.btn_peep.setToolTip(f"PEEP: {self.settings.peep:.0f} cmH₂O")
        self.btn_fio2.setToolTip(f"FiO₂: {self.settings.fio2:.0f}%")
        self.btn_ps.setToolTip(f"PS: {self.settings.ps:.0f} cmH₂O")
        self.btn_pinsp.setToolTip(f"P_insp: {self.settings.pinsp:.0f} cmH₂O")

# ------------------------------
# Entry
# ------------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Savina 300 – Ventilator Simulator (Educational)")
    # better fonts
    app.setFont(QtGui.QFont("Segoe UI", 10))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
