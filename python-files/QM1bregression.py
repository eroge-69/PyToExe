import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                             QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, QMessageBox)
from PyQt6.QtGui import QFont, QDoubleValidator
from PyQt6.QtCore import Qt
import numpy as np
from scipy.stats import t

# --- BACKEND LOGIC ---
class RegressionSolver:
    """
    A class to solve for missing values in a one-way ANOVA table and
    analyze the statistical significance of regression coefficients.
    """
    def __init__(self, **kwargs):
        self.table = {
            'df_reg': None, 'ss_reg': None, 'ms_reg': None,
            'df_res': None, 'ss_res': None, 'ms_res': None,
            'df_total': None, 'ss_total': None,
            'f_stat': None, 'r_squared': None, 'r': None,
            'n': None, 'k': None, 'ss_x': None,
            'coeff_slope': None, 'se_slope': None,
            't_stat_slope': None, 'p_value_slope': None,
            'ci_lower_slope': None, 'ci_upper_slope': None,
            'coeff_intercept': None, 'se_intercept': None,
            't_stat_intercept': None, 'p_value_intercept': None,
            'ci_lower_intercept': None, 'ci_upper_intercept': None,
            'confidence_level': 0.95
        }
        for key, value in kwargs.items():
            if key in self.table and value is not None:
                self.table[key] = float(value)

    def solve_all(self):
        """Runs all solving methods iteratively."""
        if self.table['n'] is not None and self.table['k'] is not None:
            if self.table['df_reg'] is None: self.table['df_reg'] = self.table['k']
            if self.table['df_res'] is None: self.table['df_res'] = self.table['n'] - self.table['k'] - 1
            if self.table['df_total'] is None: self.table['df_total'] = self.table['n'] - 1
        
        self.analyze_slope()
        self.analyze_intercept()
        
        for _ in range(10):
            if not self._solve_iteration():
                break
        
        if self.table['r_squared'] is None and self.table['ss_reg'] is not None and self.table['ss_total'] is not None and self.table['ss_total'] > 0:
            self.table['r_squared'] = self.table['ss_reg'] / self.table['ss_total']
        
        if self.table['r'] is None and self.table['r_squared'] is not None:
            r_val = np.sqrt(self.table['r_squared'])
            if self.table['coeff_slope'] is not None and self.table['coeff_slope'] < 0:
                r_val = -r_val
            self.table['r'] = r_val

    def analyze_slope(self):
        """Analyzes the slope coefficient."""
        if self.table['coeff_slope'] is None or self.table['se_slope'] is None: return
        if self.table['df_res'] is None:
            if self.table['n'] is not None and self.table['k'] is not None:
                self.table['df_res'] = self.table['n'] - self.table['k'] - 1
            else: return
        df_res, confidence_level = self.table['df_res'], self.table['confidence_level']
        if df_res <= 0: return
        
        t_stat = self.table['coeff_slope'] / self.table['se_slope']
        p_value = t.sf(abs(t_stat), df=df_res) * 2
        alpha = 1 - confidence_level
        t_critical = t.ppf(1 - alpha / 2, df=df_res)
        margin_of_error = t_critical * self.table['se_slope']
        
        self.table['t_stat_slope'] = t_stat
        self.table['p_value_slope'] = p_value
        self.table['ci_lower_slope'] = self.table['coeff_slope'] - margin_of_error
        self.table['ci_upper_slope'] = self.table['coeff_slope'] + margin_of_error

    def analyze_intercept(self):
        """Analyzes the intercept coefficient."""
        if self.table['coeff_intercept'] is None or self.table['se_intercept'] is None: return
        if self.table['df_res'] is None:
            if self.table['n'] is not None and self.table['k'] is not None:
                self.table['df_res'] = self.table['n'] - self.table['k'] - 1
            else: return
        df_res, confidence_level = self.table['df_res'], self.table['confidence_level']
        if df_res <= 0: return

        t_stat = self.table['coeff_intercept'] / self.table['se_intercept']
        p_value = t.sf(abs(t_stat), df=df_res) * 2
        
        alpha = 1 - confidence_level
        t_critical = t.ppf(1 - alpha / 2, df=df_res)
        margin_of_error = t_critical * self.table['se_intercept']

        self.table['t_stat_intercept'] = t_stat
        self.table['p_value_intercept'] = p_value
        self.table['ci_lower_intercept'] = self.table['coeff_intercept'] - margin_of_error
        self.table['ci_upper_intercept'] = self.table['coeff_intercept'] + margin_of_error
    
    def _solve_iteration(self):
        made_change, t = False, self.table
        if t['df_total'] is None and t['df_reg'] is not None and t['df_res'] is not None: t['df_total'] = t['df_reg'] + t['df_res']; made_change = True
        if t['df_res'] is None and t['df_total'] is not None and t['df_reg'] is not None: t['df_res'] = t['df_total'] - t['df_reg']; made_change = True
        if t['df_reg'] is None and t['df_total'] is not None and t['df_res'] is not None: t['df_reg'] = t['df_total'] - t['df_res']; made_change = True
        if t['ss_total'] is None and t['ss_reg'] is not None and t['ss_res'] is not None: t['ss_total'] = t['ss_reg'] + t['ss_res']; made_change = True
        if t['ss_res'] is None and t['ss_total'] is not None and t['ss_reg'] is not None: t['ss_res'] = t['ss_total'] - t['ss_reg']; made_change = True
        if t['ss_reg'] is None and t['ss_total'] is not None and t['ss_res'] is not None: t['ss_reg'] = t['ss_total'] - t['ss_res']; made_change = True
        if t['ms_reg'] is None and t['ss_reg'] is not None and t['df_reg'] is not None and t['df_reg'] > 0: t['ms_reg'] = t['ss_reg'] / t['df_reg']; made_change = True
        if t['ms_res'] is None and t['ss_res'] is not None and t['df_res'] is not None and t['df_res'] > 0: t['ms_res'] = t['ss_res'] / t['df_res']; made_change = True
        if t['ss_reg'] is None and t['ms_reg'] is not None and t['df_reg'] is not None: t['ss_reg'] = t['ms_reg'] * t['df_reg']; made_change = True
        if t['ss_res'] is None and t['ms_res'] is not None and t['df_res'] is not None: t['ss_res'] = t['ms_res'] * t['df_res']; made_change = True
        if t['f_stat'] is None and t['ms_reg'] is not None and t['ms_res'] is not None and t['ms_res'] > 0: t['f_stat'] = t['ms_reg'] / t['ms_res']; made_change = True
        if t['ms_reg'] is None and t['f_stat'] is not None and t['ms_res'] is not None: t['ms_reg'] = t['f_stat'] * t['ms_res']; made_change = True
        if t['ms_res'] is None and t['f_stat'] is not None and t['ms_reg'] is not None and t['f_stat'] > 0: t['ms_res'] = t['ms_reg'] / t['f_stat']; made_change = True
        if t['k'] == 1 and t['f_stat'] is None and t['t_stat_slope'] is not None: t['f_stat'] = t['t_stat_slope']**2; made_change = True
        if t['k'] == 1 and t['t_stat_slope'] is None and t['f_stat'] is not None: t['t_stat_slope'] = np.sqrt(t['f_stat']); made_change = True
        if t['coeff_slope'] is None and t['ss_reg'] is not None and t['ss_x'] is not None and t['ss_x'] > 0:
            t['coeff_slope'] = np.sqrt(t['ss_reg'] / t['ss_x']); made_change = True
        if t['ss_reg'] is None and t['coeff_slope'] is not None and t['ss_x'] is not None:
            t['ss_reg'] = (t['coeff_slope']**2) * t['ss_x']; made_change = True
        return made_change

# --- FRONTEND GUI (PyQt) ---
class AnovaAppPyQt(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ANOVA & Regression Solver (PyQt)")
        self.setGeometry(100, 100, 600, 700) # Increased height for new fields
        
        self.entries = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        anova_box = self._create_anova_box()
        middle_layout = QHBoxLayout()
        inputs_box = self._create_inputs_box()
        actions_box = self._create_actions_box()
        results_box = self._create_results_box()
        
        middle_layout.addWidget(inputs_box, 3)
        middle_layout.addWidget(actions_box, 1)
        
        main_layout.addWidget(anova_box)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(results_box)
        
    def _create_anova_box(self):
        group_box = QGroupBox("ANOVA Table")
        layout = QGridLayout(group_box)
        
        headers = ["", "df", "SS", "MS", "F"]
        for i, header in enumerate(headers):
            layout.addWidget(QLabel(f"<b>{header}</b>"), 0, i, Qt.AlignmentFlag.AlignCenter)
        
        rows = ["Regression", "Residual", "Total"]
        for i, row_name in enumerate(rows):
            layout.addWidget(QLabel(row_name), i + 1, 0)

        anova_keys = [['df_reg', 'ss_reg', 'ms_reg', 'f_stat'], ['df_res', 'ss_res', 'ms_res', None], ['df_total', 'ss_total', None, None]]
        for r, row_keys in enumerate(anova_keys):
            for c, key in enumerate(row_keys):
                if key:
                    entry = QLineEdit()
                    entry.setValidator(QDoubleValidator())
                    entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.entries[key] = entry
                    layout.addWidget(entry, r + 1, c + 1)
        return group_box

    def _create_inputs_box(self):
        group_box = QGroupBox("Model & Coefficient Inputs")
        layout = QGridLayout(group_box)
        
        other_inputs = {
            'n': "Observations (n):", 
            'k': "Predictors (k):", 
            'coeff_intercept': "Intercept Coefficient (a):",
            'se_intercept': "Std. Error of Intercept:",
            'coeff_slope': "Slope Coefficient (b):", 
            'se_slope': "Std. Error of Slope:", 
            'ss_x': "Sum of Squares of X (SSₓ):",
            'confidence_level': "Confidence Level:"
        }
        for i, (key, text) in enumerate(other_inputs.items()):
            layout.addWidget(QLabel(text), i, 0)
            entry = QLineEdit()
            entry.setValidator(QDoubleValidator())
            if key == 'confidence_level': entry.setText("0.95")
            self.entries[key] = entry
            layout.addWidget(entry, i, 1)
        return group_box

    def _create_actions_box(self):
        group_box = QGroupBox("Actions")
        layout = QVBoxLayout(group_box)
        
        solve_button = QPushButton("Solve")
        solve_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        solve_button.clicked.connect(self.solve_and_display)
        
        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_fields)
        
        layout.addWidget(solve_button)
        layout.addWidget(clear_button)
        layout.addStretch()
        return group_box

    def _create_results_box(self):
        group_box = QGroupBox("Results")
        layout = QVBoxLayout(group_box)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setText("Enter known values and click 'Solve'.")
        layout.addWidget(self.results_text)
        return group_box
        
    def gather_inputs(self):
        inputs = {}
        for key, entry in self.entries.items():
            value_str = entry.text().strip()
            inputs[key] = float(value_str) if value_str else None
        return inputs

    def solve_and_display(self):
        try:
            inputs = self.gather_inputs()
            solver = RegressionSolver(**inputs)
            solver.solve_all()
            
            for key, entry in self.entries.items():
                value = solver.table.get(key)
                if value is not None:
                    entry.setText(f"{value:.5g}")
            
            self.display_results(solver.table)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during calculation: {e}")

    def display_results(self, results):
        output = "--- Coefficient Analysis ---\n"
        ci_level = results['confidence_level'] * 100
        
        if results['t_stat_intercept'] is not None:
            output += "[Intercept]\n"
            output += f"  t-statistic: {results['t_stat_intercept']:.4f}\n"
            output += f"  p-value:     {results['p_value_intercept']:.4f}\n"
            if results['ci_lower_intercept'] is not None:
                output += f"  {ci_level:.0f}% Confidence Int: ({results['ci_lower_intercept']:.4f}, {results['ci_upper_intercept']:.4f})\n"
            output += "\n"

        if results['t_stat_slope'] is not None:
            output += "[Slope]\n"
            output += f"  t-statistic:      {results['t_stat_slope']:.4f}\n"
            output += f"  p-value:            {results['p_value_slope']:.4f}\n"
            if results['ci_lower_slope'] is not None:
                output += f"  {ci_level:.0f}% Confidence Int: ({results['ci_lower_slope']:.4f}, {results['ci_upper_slope']:.4f})\n"
        
        if results['t_stat_intercept'] is None and results['t_stat_slope'] is None:
            output += "Not possible with given inputs.\n"

        output += "\n--- Model Summary ---\n"
        if results['r_squared'] is not None:
            output += f"R-Squared (R²):     {results['r_squared']:.4f}\n"
        else:
            output += "R-Squared (R²):     Not calculated.\n"
        if results['r'] is not None:
            output += f"Correlation (r):    {results['r']:.4f}\n"
        else:
            output += "Correlation (r):    Not calculated.\n"

        self.results_text.setText(output)

    def clear_fields(self):
        for key, entry in self.entries.items():
            entry.clear()
        self.entries['confidence_level'].setText("0.95")
        self.results_text.setText("Enter known values and click 'Solve'.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnovaAppPyQt()
    window.show()
    sys.exit(app.exec())

