# app.py

import sys
import os
import re
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QColorDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
import matplotlib.pyplot as plt

# --- DataSet class ---
class DataSet:
    def __init__(self, path, span=2.0):
        self.path = path
        self.span = span
        self.factor = 1.0
        self.marker = None
        self.color = '#1f77b4'
        self.width = 1.5
        self.df = None
        self.load()

    def load(self):
        self.df = pd.read_csv(
            self.path,
            comment='#',
            delim_whitespace=True,
            header=None,
            names=['time','drag','lift','axial','tx','ty','tz']
        )

    def compute_coeffs(self, rho, U, D, Aref):
        q = 0.5 * rho * U**2
        self.df['Cd'] = (self.df['drag'] / (q * Aref)) * self.factor
        self.df['Cl'] = (self.df['lift'] / (q * Aref)) * self.factor

    def compute_strouhal(self, t0, t1, dt, U, D):
        sub = self.df[(self.df['time'] >= t0) & (self.df['time'] <= t1)]
        lift = sub['lift'].values - np.mean(sub['lift'].values)
        N = len(lift)
        if N < 2:
            return 0.0, 0.0
        fft_val = np.abs(np.fft.fft(lift))
        freqs = np.fft.fftfreq(N, dt)
        idx = np.argmax(fft_val[1:N//2]) + 1
        f_peak = abs(freqs[idx])
        St = f_peak * D / U
        return f_peak, St

# --- PlotWindow class ---
class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cylinder Force Plot")
        if os.path.exists('icon.png'):
            self.setWindowIcon(QIcon('icon.png'))
        zoom_btn = QtWidgets.QPushButton("Zoom")
        zoom_btn.clicked.connect(lambda: self.nav_toolbar.zoom())
        pan_btn = QtWidgets.QPushButton("Pan")
        pan_btn.clicked.connect(lambda: self.nav_toolbar.pan())
        reset_btn = QtWidgets.QPushButton("Reset")
        reset_btn.clicked.connect(lambda: self.nav_toolbar.home())

        self.canvas = FigureCanvasQTAgg(plt.figure())
        self.ax = self.canvas.figure.subplots()
        self.nav_toolbar = NavigationToolbar2QT(self.canvas, self)
        self.canvas.mpl_connect('scroll_event', self._on_scroll)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(zoom_btn)
        btn_layout.addWidget(pan_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(btn_layout)
        layout.addWidget(self.nav_toolbar)
        layout.addWidget(self.canvas)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _on_scroll(self, event):
        base_scale = 1.2
        ax = self.ax
        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        xleft = xdata - cur_xlim[0]
        xright = cur_xlim[1] - xdata
        ybottom = ydata - cur_ylim[0]
        ytop = cur_ylim[1] - ydata
        scale_factor = 1/base_scale if event.button == 'up' else base_scale
        ax.set_xlim([xdata - xleft*scale_factor, xdata + xright*scale_factor])
        ax.set_ylim([ydata - ybottom*scale_factor, ydata + ytop*scale_factor])
        self.canvas.draw()

    def update_plot(self, data_list, settings):
        self.ax.clear()
        t0, t1 = settings['t0'], settings['t1']
        yfield = settings['y']
        st_info = []
        for ds, show, rho, U, D, Aref, dt in data_list:
            if not show:
                continue
            ds.compute_coeffs(rho, U, D, Aref)
            sub = ds.df[(ds.df['time'] >= t0) & (ds.df['time'] <= t1)]
            plot_args = {'color': ds.color, 'linewidth': ds.width, 'label': os.path.basename(ds.path)}
            if ds.marker:
                plot_args['marker'] = ds.marker
                plot_args['markevery'] = max(len(sub)//50, 1)
            self.ax.plot(sub['time'], sub[yfield], **plot_args)
            f, St = ds.compute_strouhal(t0, t1, dt, U, D)
            st_info.append(f"{os.path.basename(ds.path)}: St={St:.12f}")
        if settings['overlay']:
            self.ax.legend(title=settings['legend'])
        self.ax.set_title(settings['title'])
        self.ax.set_xlabel(settings['xlabel'])
        self.ax.set_ylabel(settings['ylabel'])
        self.ax.grid(True)
        self.canvas.draw()
        self.statusBar().showMessage(" | ".join(st_info) + "    Credit: S-Ali Email: shahbaz.ali@unsw.edu.au")

# --- DataWindow class ---
class DataWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Loader & Controls")
        if os.path.exists('icon.png'):
            self.setWindowIcon(QIcon('icon.png'))
        self.datasets = []
        self.plot_window = None
        self._build_ui()
        about_act = QtWidgets.QAction("About", self)
        about_act.triggered.connect(self.show_about)
        menubar = self.menuBar()
        help_menu = menubar.addMenu('Help')
        help_menu.addAction(about_act)

    def _build_ui(self):
        self.table = QtWidgets.QTableWidget(0, 11)
        headers = ['Show','File','Factor','Marker','Color','Width','rho','U','D','Aref','dt']
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setStretchLastSection(True)

        load_btn = QtWidgets.QPushButton("Load Files")
        load_btn.clicked.connect(self.load_files)

        self.title_edit = QtWidgets.QLineEdit("Force Coefficients")
        self.xlabel_edit = QtWidgets.QLineEdit("Time step")
        self.ylabel_edit = QtWidgets.QLineEdit("Coefficient")
        self.legend_edit = QtWidgets.QLineEdit("Legend")
        form = QtWidgets.QFormLayout()
        form.addRow("Plot Title:", self.title_edit)
        form.addRow("X-label:", self.xlabel_edit)
        form.addRow("Y-label:", self.ylabel_edit)
        form.addRow("Legend Title:", self.legend_edit)

        self.y_combo = QtWidgets.QComboBox(); self.y_combo.addItems(['Cd','Cl'])
        self.t0_spin = QtWidgets.QSpinBox(); self.t0_spin.setRange(0,10**8); self.t0_spin.setValue(20000)
        self.t1_spin = QtWidgets.QSpinBox(); self.t1_spin.setRange(0,10**8); self.t1_spin.setValue(35000)
        self.overlay_chk = QtWidgets.QCheckBox("Overlay"); self.overlay_chk.setChecked(True)
        plot_btn = QtWidgets.QPushButton("Plot"); plot_btn.clicked.connect(self.do_plot)

        ctrl_layout = QtWidgets.QHBoxLayout()
        ctrl_layout.addWidget(QtWidgets.QLabel("Y:")); ctrl_layout.addWidget(self.y_combo)
        ctrl_layout.addWidget(QtWidgets.QLabel("t0:")); ctrl_layout.addWidget(self.t0_spin)
        ctrl_layout.addWidget(QtWidgets.QLabel("t1:")); ctrl_layout.addWidget(self.t1_spin)
        ctrl_layout.addWidget(self.overlay_chk); ctrl_layout.addWidget(plot_btn)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(load_btn)
        left_layout.addWidget(self.table)
        left_layout.addLayout(form)
        left_layout.addLayout(ctrl_layout)
        container = QtWidgets.QWidget()
        container.setLayout(left_layout)
        self.setCentralWidget(container)

    def load_files(self):
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Files", "", "DAT (*.dat)")
        for path in paths:
            if any(ds.path == path for ds in self.datasets): continue
            span = 2.0
            m = re.search(r'Lz([0-9\.]+)', os.path.basename(path))
            if m: span = float(m.group(1))
            ds = DataSet(path, span)
            self.datasets.append(ds)
            self._add_row(ds)

    def _add_row(self, ds):
        r = self.table.rowCount(); self.table.insertRow(r)
        chk = QtWidgets.QCheckBox(); chk.setChecked(True); self.table.setCellWidget(r,0,chk)
        item = QtWidgets.QTableWidgetItem(os.path.basename(ds.path))
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.table.setItem(r,1,item)
        spinF = QtWidgets.QDoubleSpinBox(); spinF.setRange(0.01,100); spinF.setSingleStep(0.1); spinF.setValue(ds.factor)
        self.table.setCellWidget(r,2,spinF)
        comboM = QtWidgets.QComboBox(); comboM.addItems(['None','o','s','^','v','x','+','*'])
        self.table.setCellWidget(r,3,comboM)
        col_btn = QtWidgets.QPushButton(); col_btn.setStyleSheet(f"background:{ds.color}"); col_btn.clicked.connect(lambda _,row=r: self.choose_color(row))
        self.table.setCellWidget(r,4,col_btn)
        wspin = QtWidgets.QDoubleSpinBox(); wspin.setRange(0.1,10); wspin.setSingleStep(0.1); wspin.setValue(ds.width)
        self.table.setCellWidget(r,5,wspin)
        rho_spin = QtWidgets.QDoubleSpinBox(); rho_spin.setRange(0.001,100); rho_spin.setSingleStep(0.1); rho_spin.setValue(1.0)
        self.table.setCellWidget(r,6,rho_spin)
        U_spin = QtWidgets.QDoubleSpinBox(); U_spin.setRange(0.001,10); U_spin.setSingleStep(0.01); U_spin.setValue(0.05)
        self.table.setCellWidget(r,7,U_spin)
        D_spin = QtWidgets.QDoubleSpinBox(); D_spin.setRange(0.001,10); D_spin.setSingleStep(0.01); D_spin.setValue(1.0)
        self.table.setCellWidget(r,8,D_spin)
        A_spin = QtWidgets.QDoubleSpinBox(); A_spin.setRange(0.001,100); A_spin.setSingleStep(0.1); A_spin.setValue(ds.span * D_spin.value())
        self.table.setCellWidget(r,9,A_spin)
        dt_spin = QtWidgets.QDoubleSpinBox(); dt_spin.setRange(0.0001,10.0); dt_spin.setSingleStep(0.001); dt_spin.setValue(1.0)
        self.table.setCellWidget(r,10,dt_spin)

    def choose_color(self, row):
        c = QColorDialog.getColor()
        if c.isValid():
            self.datasets[row].color = c.name()
            btn = self.table.cellWidget(row,4); btn.setStyleSheet(f"background:{c.name()}")

    def do_plot(self):
        if not hasattr(self, 'plot_window') or self.plot_window is None:
            self.plot_window = PlotWindow()
        settings = {
            'y': self.y_combo.currentText(),
            't0': self.t0_spin.value(),
            't1': self.t1_spin.value(),
            'overlay': self.overlay_chk.isChecked(),
            'title': self.title_edit.text(),
            'xlabel': self.xlabel_edit.text(),
            'ylabel': self.ylabel_edit.text(),
            'legend': self.legend_edit.text()
        }
        data_list = []
        for i, ds in enumerate(self.datasets):
            show = self.table.cellWidget(i,0).isChecked()
            ds.factor = self.table.cellWidget(i,2).value()
            mk = self.table.cellWidget(i,3).currentText(); ds.marker = None if mk=='None' else mk
            ds.width = self.table.cellWidget(i,5).value()
            rho = self.table.cellWidget(i,6).value()
            Uval = self.table.cellWidget(i,7).value()
            Dval = self.table.cellWidget(i,8).value()
            Aref = self.table.cellWidget(i,9).value()
            dt = self.table.cellWidget(i,10).value()
            data_list.append((ds, show, rho, Uval, Dval, Aref, dt))
        self.plot_window.update_plot(data_list, settings)
        self.plot_window.show()

    def show_about(self):
        QMessageBox.information(
            self, "About",
            "Cylinder Force Analyzer\nCredit: S-Ali\nEmail: shahbaz.ali@unsw.edu.au"
        )

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_win = DataWindow()
    main_win.resize(900, 700)
    main_win.show()
    sys.exit(app.exec_())
