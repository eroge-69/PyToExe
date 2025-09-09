# -*- coding: utf-8 -*-
import sys
import math

# Use the correct, modern backend for Matplotlib with PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox,
                             QGroupBox, QTabWidget, QTextEdit, QTableWidget, QTableWidgetItem, QMessageBox, QStatusBar,
                             QCheckBox) # Import QCheckBox
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors


class ReportGenerator:
    """A class to handle the creation of the PDF report."""
    def __init__(self, filename="Calculation_Report.pdf"):
        self.doc = SimpleDocTemplate(filename)
        self.styles = getSampleStyleSheet()
        self.story = []
        if 'Code' not in self.styles:
            self.styles.add(self.styles['Normal'].clone('Code', fontName='Courier', fontSize=9, leading=11))
        
    def add_title(self, text): self.story.append(Paragraph(text, self.styles['h1'])); self.story.append(Spacer(1, 0.25*inch))
    def add_heading(self, text, level=2): self.story.append(Paragraph(text, self.styles[f'h{level}'])); self.story.append(Spacer(1, 0.1*inch))
    def add_paragraph(self, text): self.story.append(Paragraph(text.replace('\n', '<br/>'), self.styles['Normal'])); self.story.append(Spacer(1, 0.1*inch))
    def add_calculation(self, text): self.story.append(Paragraph(text, self.styles['Code'])); self.story.append(Spacer(1, 0.1*inch))
    def add_table(self, data, col_widths=None):
        table = Table(data, colWidths=col_widths)
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('BACKGROUND', (0, 1), (-1, -1), colors.beige), ('GRID', (0, 0), (-1, -1), 1, colors.black)])
        table.setStyle(style); self.story.append(table); self.story.append(Spacer(1, 0.25*inch))
    def save(self):
        try:
            self.doc.build(self.story)
            return True, f"PDF report saved successfully as '{self.doc.filename}'"
        except Exception as e:
            return False, f"Error saving PDF: {e}"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Engineering Analysis Software")
        self.setGeometry(100, 100, 1400, 800)

        self.main_tabs = QTabWidget()
        self.setCentralWidget(self.main_tabs)

        self.tank_analysis_tab = self._create_tank_analysis_tab()
        self.earth_pressure_tab = self._create_earth_pressure_tab()

        self.main_tabs.addTab(self.tank_analysis_tab, "Tank Seismic Analysis")
        self.main_tabs.addTab(self.earth_pressure_tab, "Retaining Wall Analysis")
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready...")

        self._apply_styles()

    # TANK ANALYSIS TAB CREATION
    def _create_tank_analysis_tab(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.tank_inputs = {}
        input_panel = self._create_tank_input_panel()
        output_panel = self._create_tank_output_panel()
        main_layout.addWidget(input_panel, 1); main_layout.addWidget(output_panel, 3)
        return main_widget

    def _create_tank_input_panel(self):
        group_box = QGroupBox("Inputs")
        layout = QGridLayout()
        input_fields = {
            "Lx": ("Longitudinal Length (Lx) (m)", "5.0"), "Ly": ("Transverse Length (Ly) (m)", "15.8"), "HL": ("Water Height (HL) (m)", "5.6"),
            "A": ("Acceleration Coefficient A", "0.35"), "I": ("Importance Factor I", "1.25"), "R": ("Response Factor R", "2.5")
        }
        row = 0
        for name, (label, default_val) in input_fields.items():
            layout.addWidget(QLabel(label), row, 0)
            self.tank_inputs[name] = QLineEdit(default_val)
            self.tank_inputs[name].setValidator(QDoubleValidator(0.0, 1000.0, 4))
            layout.addWidget(self.tank_inputs[name], row, 1)
            row += 1
        layout.addWidget(QLabel("Soil Type"), row, 0)
        self.tank_inputs["soil_type"] = QComboBox(); self.tank_inputs["soil_type"].addItems(["I", "II", "III", "IV"]); layout.addWidget(self.tank_inputs["soil_type"], row, 1); row += 1
        layout.addWidget(QLabel("Seismic Hazard Zone"), row, 0)
        self.tank_inputs["zone"] = QComboBox(); self.tank_inputs["zone"].addItems(["Low / Moderate", "High / Very High"]); layout.addWidget(self.tank_inputs["zone"], row, 1); row += 1
        
        # --- ADDED PDF CHECKBOX ---
        self.tank_inputs["generate_pdf"] = QCheckBox("Generate PDF Report?")
        self.tank_inputs["generate_pdf"].setChecked(True)
        layout.addWidget(self.tank_inputs["generate_pdf"], row, 0, 1, 2)
        row += 1

        calc_button = QPushButton("Calculate & Generate Tank Report"); calc_button.clicked.connect(self.run_tank_calculations); layout.addWidget(calc_button, row, 0, 1, 2)
        group_box.setLayout(layout)
        return group_box

    def _create_tank_output_panel(self):
        self.tank_tabs = QTabWidget()
        self.tank_summary_table = QTableWidget()
        self.tank_log_output = QTextEdit(); self.tank_log_output.setReadOnly(True)
        plot_widget = QWidget(); plot_layout = QVBoxLayout(plot_widget)
        self.tank_figure = Figure(figsize=(8, 6)); self.tank_canvas = FigureCanvas(self.tank_figure); plot_layout.addWidget(self.tank_canvas)
        self.tank_tabs.addTab(self.tank_summary_table, "Final Summary"); self.tank_tabs.addTab(self.tank_log_output, "Calculation Details"); self.tank_tabs.addTab(plot_widget, "Force Distribution Plot")
        return self.tank_tabs
    
    # RETAINING WALL (EARTH PRESSURE) TAB CREATION
    def _create_earth_pressure_tab(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.ep_inputs = {}
        input_panel = self._create_ep_input_panel()
        output_panel = self._create_ep_output_panel()
        main_layout.addWidget(input_panel, 1); main_layout.addWidget(output_panel, 3)
        return main_widget

    def _create_ep_input_panel(self):
        group_box = QGroupBox("Inputs")
        layout = QGridLayout()
        input_fields = {"gamma_w": ("Soil Specific Weight (Ton/m³)", "1.8"), "Hs": ("Wall Height (Hs) (m)", "5.0"), "kh": ("Seismic Coefficient (kh)", "0.35"), "P_prime_0": ("Surcharge Pressure (Ton/m²)", "1.8")}
        row = 0
        for name, (label, default_val) in input_fields.items():
            layout.addWidget(QLabel(label), row, 0)
            self.ep_inputs[name] = QLineEdit(default_val)
            self.ep_inputs[name].setValidator(QDoubleValidator(0.0, 1000.0, 4))
            layout.addWidget(self.ep_inputs[name], row, 1)
            row += 1
        layout.setRowStretch(row, 1)

        # --- ADDED PDF CHECKBOX ---
        self.ep_inputs["generate_pdf"] = QCheckBox("Generate PDF Report?")
        self.ep_inputs["generate_pdf"].setChecked(True)
        layout.addWidget(self.ep_inputs["generate_pdf"], row + 1, 0, 1, 2)

        calc_button = QPushButton("Calculate & Generate Wall Report"); calc_button.clicked.connect(self.run_ep_calculations); layout.addWidget(calc_button, row + 2, 0, 1, 2)
        group_box.setLayout(layout)
        return group_box

    def _create_ep_output_panel(self):
        self.ep_tabs = QTabWidget()
        self.ep_log_output = QTextEdit(); self.ep_log_output.setReadOnly(True)
        plot_widget = QWidget(); plot_layout = QVBoxLayout(plot_widget)
        self.ep_figure = Figure(figsize=(8, 6)); self.ep_canvas = FigureCanvas(self.ep_figure); plot_layout.addWidget(self.ep_canvas)
        self.ep_tabs.addTab(self.ep_log_output, "Calculation Details"); self.ep_tabs.addTab(plot_widget, "Pressure Distribution Plot")
        return self.ep_tabs

    # STYLESHEET
    def _apply_styles(self):
        self.setStyleSheet(""" QWidget { font-family: Courier, 'Courier New', monospace; } QMainWindow { background-color: #f0f0f0; } QGroupBox { font-size: 14px; font-weight: bold; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; } QLabel { font-size: 12px; } QLineEdit, QComboBox, QCheckBox { padding: 5px; border: 1px solid #ccc; border-radius: 3px; font-size: 12px; } QPushButton { background-color: #0078d7; color: white; font-size: 14px; font-weight: bold; padding: 10px; border-radius: 5px; margin-top: 10px; } QPushButton:hover { background-color: #005a9e; } QTabWidget::pane { border: 1px solid #ccc; } QTabBar::tab { background: #e1e1e1; padding: 10px; border-top-left-radius: 4px; border-top-right-radius: 4px; } QTabBar::tab:selected { background: #f0f0f0; } QTableWidget { font-size: 11px; alternate-background-color: #f7f7f7; gridline-color: #d0d0d0; } """)

    # CALCULATION LOGIC FOR TANK ANALYSIS
    def run_tank_calculations(self):
        self.status_bar.showMessage("Calculating Tank Analysis...")
        self.tank_log_output.clear(); self.tank_summary_table.setRowCount(0); self.tank_figure.clear()
        try:
            Lx = float(self.tank_inputs["Lx"].text()); Ly = float(self.tank_inputs["Ly"].text()); HL = float(self.tank_inputs["HL"].text())
            A = float(self.tank_inputs["A"].text()); I = float(self.tank_inputs["I"].text()); R = float(self.tank_inputs["R"].text())
            soil_type = self.tank_inputs["soil_type"].currentText()
            zone_key = 'low_moderate' if self.tank_inputs["zone"].currentIndex() == 0 else 'high_very_high'
            should_generate_pdf = self.tank_inputs["generate_pdf"].isChecked()
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please fill all fields with valid numeric values."); self.status_bar.showMessage("Error in input values!"); return

        pdf_report = None
        if should_generate_pdf:
            pdf_report = ReportGenerator("Seismic_Calculation_Report.pdf")
            pdf_report.add_title("Seismic Analysis Report for Liquid Storage Tank")
        
        def log(message, pdf_level='calc'):
            self.tank_log_output.append(message.replace('\n', '<br>'))
            if pdf_report:
                clean_message = message.replace('<b>', '').replace('</b>', '')
                if pdf_level == 'h2': pdf_report.add_heading(clean_message)
                elif pdf_level == 'h3': pdf_report.add_heading(clean_message, level=3)
                else: pdf_report.add_calculation(clean_message)
        
        # --- FULL TANK CALCULATION LOGIC ---
        g = 9.81
        log("<b>--- Section 1: Calculated Periods (T) ---</b>", 'h2')
        T_long_convective, T_trans_convective, T_impulsive = self.calculate_period(Lx, HL, g), self.calculate_period(Ly, HL, g), 0.3
        log(f"Longitudinal Convective Period (Tx_c): {T_long_convective:.4f} s"); log(f"Transverse Convective Period (Ty_c):  {T_trans_convective:.4f} s"); log(f"Impulsive Period (T_i):   {T_impulsive:.4f} s")
        # ... (rest of the detailed tank calculation logic follows) ...
        log("\n<b>--- Section 2: Mass and Height Components ---</b>", 'h2')
        WL = Lx * Ly * HL
        Wi_long, hi_long = self.calculate_impulsive(Lx, HL, WL)
        Wi_trans, hi_trans = self.calculate_impulsive(Ly, HL, WL)
        Wc_long, hc_long = self.calculate_convective(Lx, HL, WL)
        Wc_trans, hc_trans = self.calculate_convective(Ly, HL, WL)
        log(f"Total Water Mass (WL) = {WL:.2f} Ton"); log("\n  <b>Impulsive Mass:</b>"); log(f"    Longitudinal: Wi = {Wi_long:.2f} Ton  |  hi = {hi_long:.2f} m"); log(f"    Transverse:   Wi = {Wi_trans:.2f} Ton  |  hi = {hi_trans:.2f} m"); log("\n  <b>Convective Mass:</b>"); log(f"    Longitudinal: Wc = {Wc_long:.2f} Ton  |  hc = {hc_long:.2f} m"); log(f"    Transverse:   Wc = {Wc_trans:.2f} Ton  |  hc = {hc_trans:.2f} m")

        log("\n<b>--- Section 3: Seismic Coefficient (C) Calculations ---</b>", 'h2')
        SOIL_DATA = { 'I': {'T0': 0.10, 'Ts': 0.4, 'low_moderate': {'S0': 1.0, 'S': 1.5}, 'high_very_high': {'S0': 1.0, 'S': 1.5}}, 'II': {'T0': 0.10, 'Ts': 0.5, 'low_moderate': {'S0': 1.0, 'S': 1.5}, 'high_very_high': {'S0': 1.0, 'S': 1.5}}, 'III': {'T0': 0.15, 'Ts': 0.7, 'low_moderate': {'S0': 1.1, 'S': 1.5}, 'high_very_high': {'S0': 1.1, 'S': 1.5}}, 'IV': {'T0': 0.15, 'Ts': 1.0, 'low_moderate': {'S0': 1.3, 'S': 1.5}, 'high_very_high': {'S0': 1.1, 'S': 1.75}}, }
        params = SOIL_DATA[soil_type]
        T0, Ts, S0, S = params['T0'], params['Ts'], params[zone_key]['S0'], params[zone_key]['S']
        c_results = {}
        for name, T_val in [("C x convective", T_long_convective), ("C y convective", T_trans_convective), ("C impulsive", T_impulsive)]:
            B1, N, B, C = self.calculate_c_coefficients(T_val, T0, Ts, S0, S, zone_key, A, I, R, "convective" in name.lower())
            c_results[name] = C; log(f"\n<b>=== Processing {name} (T = {T_val:.4f}s) ===</b>", 'h3'); log(f"1. Final B1 = {B1:.4f}"); log(f"2. N = {N:.4f}"); log(f"3. B = {B:.4f}"); log(f"4. C = {C:.4f}")
        Cx_convective, Cy_convective, C_impulsive = c_results["C x convective"], c_results["C y convective"], c_results["C impulsive"]

        log("\n<b>--- Section 4: Final Seismic Force (P) Calculations ---</b>", 'h2')
        Pix, Pcx, Piy, Pcy = Wi_long * C_impulsive, Wc_long * Cx_convective, Wi_trans * C_impulsive, Wc_trans * Cy_convective
        log(f"Pix = {Wi_long:.2f} * {C_impulsive:.4f} = {Pix:.2f} Ton"); log(f"Pcx = {Wc_long:.2f} * {Cx_convective:.4f} = {Pcx:.2f} Ton"); log(f"Piy = {Wi_trans:.2f} * {C_impulsive:.4f} = {Piy:.2f} Ton"); log(f"Pcy = {Wc_trans:.2f} * {Cy_convective:.4f} = {Pcy:.2f} Ton")

        log("\n<b>--- Section 5: Total Force Distribution Equation F(z) ---</b>", 'h2')
        A_dxi, B_dxi = self.formulate_distribution_equation(Pix, hi_long, HL); A_dyi, B_dyi = self.formulate_distribution_equation(Piy, hi_trans, HL); A_dxc, B_dxc = self.formulate_distribution_equation(Pcx, hc_long, HL); A_dyc, B_dyc = self.formulate_distribution_equation(Pcy, hc_trans, HL)
        log(f"Fdx-i(z) = {A_dxi:.4f} - {B_dxi:.4f} * z"); log(f"Fdy-i(z) = {A_dyi:.4f} - {B_dyi:.4f} * z"); log(f"Fdx-c(z) = {A_dxc:.4f} - {B_dxc:.4f} * z"); log(f"Fdy-c(z) = {A_dyc:.4f} - {B_dyc:.4f} * z")

        log("\n<b>--- Section 6: Force Distribution per Unit Length f(z) [Ton/m] ---</b>", 'h2')
        a_dxi, b_dxi = (A_dxi / Ly, B_dxi / Ly) if Ly != 0 else (0,0); a_dxc, b_dxc = (A_dxc / Ly, B_dxc / Ly) if Ly != 0 else (0,0)
        a_dyi, b_dyi = (A_dyi / Lx, B_dyi / Lx) if Lx != 0 else (0,0); a_dyc, b_dyc = (A_dyc / Lx, B_dyc / Lx) if Lx != 0 else (0,0)
        log(f"f_dx-i(z) = {a_dxi:.4f} - {b_dxi:.4f} * z"); log(f"f_dx-c(z) = {a_dxc:.4f} - {b_dxc:.4f} * z"); log(f"f_dy-i(z) = {a_dyi:.4f} - {b_dyi:.4f} * z"); log(f"f_dy-c(z) = {a_dyc:.4f} - {b_dyc:.4f} * z")
        
        summary_data = [ ["Impulsive X (Pix)", f"{T_impulsive:.4f}", f"{C_impulsive:.4f}", f"{Wi_long:.2f}", f"{Pix:.2f}"], ["Convective X (Pcx)", f"{T_long_convective:.4f}", f"{Cx_convective:.4f}", f"{Wc_long:.2f}", f"{Pcx:.2f}"], ["Impulsive Y (Piy)", f"{T_impulsive:.4f}", f"{C_impulsive:.4f}", f"{Wi_trans:.2f}", f"{Piy:.2f}"], ["Convective Y (Pcy)", f"{T_trans_convective:.4f}", f"{Cy_convective:.4f}", f"{Wc_trans:.2f}", f"{Pcy:.2f}"], ]
        self.tank_summary_table.setRowCount(len(summary_data)); self.tank_summary_table.setColumnCount(5); self.tank_summary_table.setHorizontalHeaderLabels(["Component", "Period (s)", "C Coeff.", "Mass (Ton)", "Force (Ton)"])
        for r, row_data in enumerate(summary_data):
            for c, cell_data in enumerate(row_data): self.tank_summary_table.setItem(r, c, QTableWidgetItem(cell_data))
        self.tank_summary_table.resizeColumnsToContents()
        
        z_vals = [0, HL]
        ax1 = self.tank_figure.add_subplot(121); ax1.plot([a_dxi - b_dxi * z for z in z_vals], z_vals, label="Impulsive (f_dxi)", color='r'); ax1.plot([a_dxc - b_dxc * z for z in z_vals], z_vals, label="Convective (f_dxc)", color='b', linestyle='--'); ax1.set_title("Force Distribution in X-Direction"); ax1.set_xlabel("Force per Unit Length (Ton/m)"); ax1.set_ylabel("Height (m)"); ax1.legend(); ax1.grid(True)
        ax2 = self.tank_figure.add_subplot(122); ax2.plot([a_dyi - b_dyi * z for z in z_vals], z_vals, label="Impulsive (f_dyi)", color='r'); ax2.plot([a_dyc - b_dyc * z for z in z_vals], z_vals, label="Convective (f_dyc)", color='b', linestyle='--'); ax2.set_title("Force Distribution in Y-Direction"); ax2.set_xlabel("Force per Unit Length (Ton/m)"); ax2.legend(); ax2.grid(True)
        self.tank_figure.tight_layout(); self.tank_canvas.draw()
        
        final_message = "Tank calculations complete."
        if pdf_report:
            success, message = pdf_report.save()
            final_message += f" {message}" if success else " Failed to save PDF."
        self.status_bar.showMessage(final_message)

    # CALCULATION LOGIC FOR EARTH PRESSURE
    def run_ep_calculations(self):
        self.status_bar.showMessage("Calculating Earth Pressure...")
        self.ep_log_output.clear(); self.ep_figure.clear()
        try:
            gamma_w = float(self.ep_inputs["gamma_w"].text()); Hs = float(self.ep_inputs["Hs"].text()); kh = float(self.ep_inputs["kh"].text()); P_prime_0 = float(self.ep_inputs["P_prime_0"].text())
            should_generate_pdf = self.ep_inputs["generate_pdf"].isChecked()
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please fill all fields with valid numeric values."); self.status_bar.showMessage("Error in input values!"); return
            
        pdf_report = None
        if should_generate_pdf:
            pdf_report = ReportGenerator("Earth_Pressure_Report.pdf")
            pdf_report.add_title("Dynamic Earth Pressure Analysis Report")

        def log_ep(message, pdf_level='calc'):
            self.ep_log_output.append(message.replace('\n', '<br>'))
            if pdf_report:
                clean_message = message.replace('<b>', '').replace('</b>', '')
                if pdf_level == 'h2': pdf_report.add_heading(clean_message)
                else: pdf_report.add_calculation(clean_message)

        log_ep("<b>--- Step 1: Total Dynamic Pressure Increment (ΔPae) ---</b>", 'h2')
        delta_Pae = gamma_w * (Hs**2) * kh
        log_ep(f"ΔPae = {gamma_w} * ({Hs}**2) * {kh} = {delta_Pae:.2f} Ton/m")
        log_ep("\n<b>--- Step 2: Dynamic Pressure from Surcharge (kh * P'_0) ---</b>", 'h2')
        kh_P_prime_0 = kh * P_prime_0
        log_ep(f"kh * P'_0 = {kh} * {P_prime_0} = {kh_P_prime_0:.2f} Ton/m^2")
        log_ep("\n<b>--- Step 3: Trapezoidal Pressures X and Y ---</b>", 'h2')
        Y = (2 * delta_Pae) / (5 * Hs) if Hs != 0 else 0
        X = 4 * Y
        log_ep(f"Y = (2 * {delta_Pae:.2f}) / (5 * {Hs}) = {Y:.2f}"); log_ep(f"X = 4 * {Y:.2f} = {X:.2f}")
        log_ep("\n<b>--- Step 4: Final Dynamic Stresses ---</b>", 'h2')
        S_dy_top = kh_P_prime_0 + X; S_dy_bot = kh_P_prime_0 + Y
        log_ep(f"S_top_dy = {kh_P_prime_0:.2f} + {X:.2f} = {S_dy_top:.2f} Ton/m^2"); log_ep(f"S_bot_dy = {kh_P_prime_0:.2f} + {Y:.2f} = {S_dy_bot:.2f} Ton/m^2")

        ax = self.ep_figure.add_subplot(111)
        ax.plot([S_dy_bot, S_dy_top], [0, Hs], label="Final Pressure", color='r', marker='o'); ax.fill_betweenx([0, Hs], [S_dy_bot, S_dy_top], color='orangered', alpha=0.3)
        ax.set_title("Dynamic Earth Pressure Distribution"); ax.set_xlabel("Pressure (Ton/m²)"); ax.set_ylabel("Wall Height (m)"); ax.grid(True); ax.invert_xaxis(); ax.yaxis.tick_right()
        self.ep_figure.tight_layout(); self.ep_canvas.draw()
        
        final_message = "Earth pressure calculations complete."
        if pdf_report:
            success, message = pdf_report.save()
            final_message += f" {message}" if success else " Failed to save PDF."
        self.status_bar.showMessage(final_message)

    # --- CALCULATION HELPER FUNCTIONS ---
    def calculate_period(self, L, HL, g):
        if L == 0: return float('inf')
        ratio = HL / L; lambda_val = math.sqrt(3.16 * g * math.tanh(3.16 * ratio))
        return (2 * math.pi) / lambda_val * math.sqrt(L) if lambda_val > 0 else float('inf')
    def calculate_impulsive(self, L, HL, WL):
        if HL == 0: return 0, 0
        L_div_HL = L / HL
        Wi_ratio = math.tanh(0.866 * L_div_HL) / (0.866 * L_div_HL) if L_div_HL != 0 else 1.0
        hi_ratio = 0.5 - 0.09375 * L_div_HL if L_div_HL < 1.333 else 0.375
        return Wi_ratio * WL, hi_ratio * HL
    def calculate_convective(self, L, HL, WL):
        if HL == 0 or L == 0: return 0, 0
        L_div_HL, HL_div_L = L / HL, HL / L
        Wc_ratio = 0.264 * L_div_HL * math.tanh(3.16 * HL_div_L)
        numerator = math.cosh(3.16 * HL_div_L) - 1
        denominator = (3.16 * HL_div_L) * math.sinh(3.16 * HL_div_L)
        hc_ratio = 1 - (numerator / denominator) if denominator != 0 else 0
        return Wc_ratio * WL, hc_ratio * HL
    def calculate_c_coefficients(self, T, T0, Ts, S0, S, zone_key, A, I, R, is_convective):
        if 0<=T<T0: B1_initial = S0+(S-S0+1)*(T/T0)
        elif T0<=T<Ts: B1_initial = S+1
        else: B1_initial = (S+1)*(Ts/T)
        B1_final = B1_initial*1.5 if is_convective else B1_initial
        if zone_key=='high_very_high': N = 1.0 if T<Ts else (1.7 if T>=4 else (0.7/(4-Ts))*(T-Ts)+1 if Ts!=4 else 1.7)
        else: N = 1.0 if T<Ts else (1.4 if T>=4 else (0.4/(4-Ts))*(T-Ts)+1 if Ts!=4 else 1.4)
        B, C = B1_final*N, (A*B1_final*N*I)/R if R!=0 else float('inf')
        return B1_final, N, B, C
    def formulate_distribution_equation(self, P, h, HL):
        if HL == 0: return 0, 0
        return P*(4*HL-6*h)/(2*HL**2), P*(6*HL-12*h)/(2*HL**3)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())