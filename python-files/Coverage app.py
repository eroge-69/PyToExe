import sys
import pandas as pd
import os
import base64
import io
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox, QFrame,
    QSplitter, QSizePolicy, QTabWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Matplotlib imports for plotting
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def normalize_pn(pn_str):
    """
    Normalizes a part number by converting it to lowercase and removing the ':00000' suffix.
    """
    if not isinstance(pn_str, str):
        return None
    
    pn = pn_str.lower().strip()
    if pn.endswith(':00000'):
        pn = pn[:-6] # Remove ':00000'
    return pn

def greedy_set_cover(universe_of_pns, circuits_to_cover, pn_to_circuits_map):
    """
    Finds a minimal set of PNs (from the universe) to cover the target circuits
    using a greedy Set Cover algorithm.
    """
    covered_circuits = set()
    solution_pns = set()
    
    # Pre-calculate sets for quick lookups
    pn_sets = {pn: pn_to_circuits_map.get(pn, set()) for pn in universe_of_pns}
    
    while circuits_to_cover - covered_circuits:
        best_pn = None
        max_new_circuits = 0
        
        # Find the PN that covers the most new, uncovered circuits
        for pn in universe_of_pns:
            newly_covered = pn_sets[pn] - covered_circuits
            if len(newly_covered) > max_new_circuits:
                max_new_circuits = len(newly_covered)
                best_pn = pn

        if best_pn is None:
            break

        solution_pns.add(best_pn)
        covered_circuits.update(pn_sets[best_pn])
    
    return solution_pns, covered_circuits

class MaxWireOptimizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = ""
        self.results_data = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PNs Coverage App - Father PNs")
        self.setGeometry(100, 100, 1000, 800)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Splitter for the main panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Input and Controls Panel (Left Side)
        control_panel = QFrame()
        control_panel.setFrameShape(QFrame.StyledPanel)
        control_layout = QVBoxLayout(control_panel)
        control_panel.setMinimumWidth(350)
        splitter.addWidget(control_panel)

        # File selection
        self.file_label = QLabel("<b>No file selected</b>")
        self.file_label.setWordWrap(True)
        self.file_button = QPushButton("Select MaxWireList File")
        self.file_button.clicked.connect(self.select_file)
        
        control_layout.addWidget(self.file_label)
        control_layout.addWidget(self.file_button)
        
        # PN input
        pn_label = QLabel("<b>Enter Planned PNs (one per line):</b>")
        self.pn_input = QTextEdit()
        self.pn_input.setPlaceholderText("e.g.\n240130043R\n240130595R\n...")
        self.pn_input.setMinimumHeight(200)

        control_layout.addWidget(pn_label)
        control_layout.addWidget(self.pn_input)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.run_button = QPushButton("Run Analysis")
        self.run_button.setObjectName("runButton")
        self.run_button.clicked.connect(self.run_analysis)
        self.export_button = QPushButton("Export Report")
        self.export_button.setObjectName("exportButton")
        self.export_button.clicked.connect(self.export_report)
        self.export_button.setEnabled(False) # Disabled until analysis is run

        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.export_button)
        control_layout.addLayout(button_layout)
        control_layout.addStretch()

        # Results Display Panel (Right Side)
        self.results_panel = QFrame()
        self.results_panel.setFrameShape(QFrame.StyledPanel)
        results_layout = QVBoxLayout(self.results_panel)
        splitter.addWidget(self.results_panel)

        # Tab widget for report and graphs
        self.tab_widget = QTabWidget()
        results_layout.addWidget(self.tab_widget)
        
        # Tab 1: Analysis Report
        self.report_widget = QWidget()
        report_layout = QVBoxLayout(self.report_widget)
        
        results_label = QLabel("<b>Analysis Report</b>")
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        report_layout.addWidget(results_label)
        report_layout.addWidget(self.results_text)
        
        self.tab_widget.addTab(self.report_widget, "Text Report")
        
        # Tab 2: Graphs
        self.graphs_widget = QWidget()
        self.graphs_layout = QVBoxLayout(self.graphs_widget)
        self.graphs_layout.setContentsMargins(0, 0, 0, 0) # No margins
        self.tab_widget.addTab(self.graphs_widget, "Graphs")
        
        # Splitter initial sizes
        splitter.setSizes([350, 650])

        # Footer
        footer_label = QLabel("Powered By Yazaki YMM1 - Programmed By Shemyoub")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setObjectName("footerLabel")
        main_layout.addWidget(footer_label)

        # Apply styles
        self.set_styles()

    def set_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #f0f0f0;
                font-size: 16px;
            }
            QTextEdit, QLineEdit {
                background-color: #444;
                border: 1px solid #555;
                color: #fff;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #555;
                color: #fff;
                border: 1px solid #777;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #444;
            }
            #runButton {
                background-color: #c0392b;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            #runButton:hover {
                background-color: #e74c3c;
            }
            #runButton:pressed {
                background-color: #a52b1e;
            }
            #exportButton {
                background-color: #2980b9;
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }
            #exportButton:hover {
                background-color: #3498db;
            }
            #exportButton:pressed {
                background-color: #21618C;
            }
            #footerLabel {
                font-size: 10px;
                color: #888;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2e2e2e;
            }
            QTabBar::tab {
                background-color: #444;
                color: #f0f0f0;
                padding: 10px;
            }
            QTabBar::tab:selected {
                background-color: #555;
            }
            QTabBar::tab:hover {
                background-color: #666;
            }
        """)
        self.results_text.setFont(QFont("Arial", 13))
        self.pn_input.setFont(QFont("Arial", 14))

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select MaxWireList File",
            "",
            "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"<b>Selected file:</b> {os.path.basename(self.file_path)}")
            self.export_button.setEnabled(False)
            self.results_text.clear()
            # Clear graphs when a new file is selected
            for i in reversed(range(self.graphs_layout.count())): 
                self.graphs_layout.itemAt(i).widget().deleteLater()

    def run_analysis(self):
        self.results_text.clear()
        self.export_button.setEnabled(False)
        # Clear previous graphs
        for i in reversed(range(self.graphs_layout.count())): 
            self.graphs_layout.itemAt(i).widget().deleteLater()
            
        planned_pns_input = self.pn_input.toPlainText().strip()

        if not self.file_path:
            QMessageBox.warning(self, "Input Error", "Please select a file first.")
            return
        
        if not planned_pns_input:
            QMessageBox.warning(self, "Input Error", "Please enter at least one planned PN.")
            return

        try:
            report = "<h3>--- MaxWireList Optimization Report ---</h3>"
            report += "<p><b>Status:</b> Processing data...</p><hr>"
            self.results_text.setHtml(report)
            QApplication.processEvents()

            file_extension = os.path.splitext(self.file_path)[1].lower()
            if file_extension == '.csv':
                df = pd.read_csv(self.file_path)
            elif file_extension == '.xlsx':
                df = pd.read_excel(self.file_path) # Now reads the first sheet by default
            else:
                QMessageBox.critical(self, "File Error", "Unsupported file type. Please select a .csv or .xlsx file.")
                return

            circuit_col = 'Wire Internal Name'
            if circuit_col not in df.columns:
                QMessageBox.critical(self, "Column Error", f"The file must contain a '{circuit_col}' column.")
                return

            # Find PN columns starting from 'Wire Part Number' based on file format
            try:
                start_col_name = 'Wire Part Number'
                start_index = list(df.columns).index(start_col_name) + 1
            except ValueError:
                QMessageBox.critical(self, "Column Error", f"Could not find the starting column '{start_col_name}'.")
                return
            
            pn_cols = [col for col in df.columns[start_index:] if isinstance(col, str) and sum(c.isdigit() for c in col) > 5]
            
            if not pn_cols:
                QMessageBox.critical(self, "Column Error", "Could not identify any PN columns in the file after 'Wire Part Number'.")
                return
            
            report += f"<p>Found {len(pn_cols)} potential PN columns.</p>"
            report += f"<p>Using **{circuit_col}** as the circuit identifier.</p><hr>"
            self.results_text.setHtml(report)
            QApplication.processEvents()

            pn_to_circuits_full = defaultdict(set)
            all_circuits = set()
            
            for _, row in df.iterrows():
                circuit = str(row[circuit_col]).strip()
                if not circuit or pd.isna(circuit):
                    continue
                all_circuits.add(circuit)

                for pn_col_name in pn_cols:
                    cell_value = str(row.get(pn_col_name, '')).strip().lower()
                    if cell_value == 'x':
                        normalized_pn = normalize_pn(pn_col_name)
                        if normalized_pn:
                            pn_to_circuits_full[normalized_pn].add(circuit)
            
            total_circuits_count = len(all_circuits)
            
            if not all_circuits:
                QMessageBox.warning(self, "Data Error", "No circuits found in the file.")
                return

            report += f"<p><b>Data loaded successfully.</b> Total unique circuits: <b>{total_circuits_count}</b></p><hr>"
            self.results_text.setHtml(report)
            QApplication.processEvents()

            planned_pns = {normalize_pn(pn) for pn in planned_pns_input.splitlines() if normalize_pn(pn) and normalize_pn(pn) in pn_to_circuits_full}
            
            if not planned_pns:
                report += f"<p><b>Warning:</b> No valid planned PNs found that exist in the file. Please check your input and the file content.</p>"
                self.results_text.setHtml(report)
                return

            report += "<h3>1. Planned PNs Coverage</h3><ul>"
            circuits_covered_by_planned = set()
            for pn in sorted(list(planned_pns)):
                circuits_for_pn = pn_to_circuits_full.get(pn, set())
                coverage_percent = (len(circuits_for_pn) / total_circuits_count) * 100
                report += f"<li>PN '<b>{pn}</b>': Covers <b>{len(circuits_for_pn)}</b> circuits ({coverage_percent:.2f}%)</li>"
                circuits_covered_by_planned.update(circuits_for_pn)
            report += "</ul>"

            overall_coverage_count = len(circuits_covered_by_planned)
            overall_coverage_percent = (overall_coverage_count / total_circuits_count) * 100
            report += f"<p><b>Overall coverage with planned PNs:</b> <span style='color: #27ae60;'><b>{overall_coverage_count}</b></span> circuits ({overall_coverage_percent:.2f}%)</p>"
            
            missing_circuits = all_circuits - circuits_covered_by_planned
            missing_count = len(missing_circuits)
            missing_percent = (missing_count / total_circuits_count) * 100
            report += f"<p><b>Missing circuits:</b> <span style='color: #e74c3c;'><b>{missing_count}</b></span> circuits ({missing_percent:.2f}%)</p><hr>"
            
            self.results_text.setHtml(report)
            QApplication.processEvents()

            report += "<h3>2. Optimization within Planned PNs</h3>"
            optimized_planned_pns, _ = greedy_set_cover(
                universe_of_pns=planned_pns,
                circuits_to_cover=circuits_covered_by_planned,
                pn_to_circuits_map=pn_to_circuits_full
            )
            
            optimized_list = sorted(list(optimized_planned_pns))
            report += f"<p>Original planned PNs count: <b>{len(planned_pns)}</b></p>"
            report += f"<p>Optimized minimal set of planned PNs (<b>{len(optimized_list)}</b> PNs):</p><ul>"
            report += "".join([f"<li>{pn}</li>" for pn in optimized_list])
            report += "</ul><hr>"
            
            self.results_text.setHtml(report)
            QApplication.processEvents()
            
            report += "<h3>3. Suggestion for Missing Circuits</h3>"
            if missing_count == 0:
                report += "<p>No missing circuits to suggest PNs for. The planned PNs provide 100% coverage!</p>"
                circuits_covered_by_suggestion = set()
            else:
                universe_for_suggestion = set(pn_to_circuits_full.keys()) - optimized_planned_pns
                suggested_pns, circuits_covered_by_suggestion = greedy_set_cover(
                    universe_of_pns=universe_for_suggestion,
                    circuits_to_cover=missing_circuits,
                    pn_to_circuits_map=pn_to_circuits_full
                )

                suggested_list = sorted(list(suggested_pns))
                
                # CORRECTED LOGIC: Only count the circuits that were actually missing
                newly_covered_circuits_count = len(missing_circuits.intersection(circuits_covered_by_suggestion))
                if missing_count > 0:
                  suggestion_coverage_percent_of_missing = (newly_covered_circuits_count / missing_count) * 100
                else:
                  suggestion_coverage_percent_of_missing = 0
                
                report += f"<p>Minimal set of additional PNs to cover missing circuits (<b>{len(suggested_list)}</b> PNs):</p><ul>"
                report += "".join([f"<li>{pn}</li>" for pn in suggested_list])
                report += "</ul>"
                report += f"<p>This suggestion covers <b>{newly_covered_circuits_count}</b> out of {missing_count} missing circuits ({suggestion_coverage_percent_of_missing:.2f}%).</p>"
            report += "<hr>"

            self.results_text.setHtml(report)
            QApplication.processEvents()

            report += "<h3>4. Final Coverage</h3>"
            final_circuits_covered = circuits_covered_by_planned.union(circuits_covered_by_suggestion)
            final_coverage_count = len(final_circuits_covered)
            final_coverage_percent = (final_coverage_count / total_circuits_count) * 100
            
            report += f"<p><b>Final coverage with planned PNs + suggested PNs:</b></p>"
            report += f"<p>Total circuits covered: <b>{final_coverage_count}</b> / {total_circuits_count}</p>"
            report += f"<h2>Final Coverage: <span style='color: #2ecc71;'>{final_coverage_percent:.2f}%</span></h2>"
            report += "<hr>"

            self.results_text.setHtml(report)
            self.export_button.setEnabled(True)
            self.results_data = {
                'overall_coverage_count': overall_coverage_count,
                'missing_count': missing_count,
                'planned_pns_count': len(planned_pns),
                'optimized_pns_count': len(optimized_list),
                'report_html': report
            }
            self.plot_graphs(**self.results_data)

        except Exception as e:
            QMessageBox.critical(self, "An Error Occurred", f"An unexpected error occurred: {e}")

    def plot_graphs(self, overall_coverage_count, missing_count, planned_pns_count, optimized_pns_count, **kwargs):
        # Clear previous graphs
        for i in reversed(range(self.graphs_layout.count())): 
            self.graphs_layout.itemAt(i).widget().deleteLater()
        
        # Pie Chart for Coverage
        fig1, ax1 = plt.subplots(figsize=(6, 4), facecolor='#2e2e2e')
        labels = ['Covered', 'Missing']
        sizes = [overall_coverage_count, missing_count]
        colors = ['#27ae60', '#e74c3c']
        explode = (0.05, 0)
        
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=140)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.set_title('Circuit Coverage by Planned PNs', color='white')
        
        canvas1 = FigureCanvas(fig1)
        self.graphs_layout.addWidget(canvas1)
        
        # Bar Chart for PN Optimization
        fig2, ax2 = plt.subplots(figsize=(6, 4), facecolor='#2e2e2e')
        pn_counts = [planned_pns_count, optimized_pns_count]
        pn_labels = ['Planned PNs', 'Optimized PNs']
        bar_colors = ['#2980b9', '#8e44ad']

        bars = ax2.bar(pn_labels, pn_counts, color=bar_colors)
        ax2.set_title('PN Optimization', color='white')
        ax2.set_ylabel('Number of PNs', color='white')
        ax2.set_facecolor('#2e2e2e')
        
        # Add values on top of bars
        for bar in bars:
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom', color='white')

        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')
        ax2.xaxis.label.set_color('white')
        ax2.yaxis.label.set_color('white')
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')
        
        fig2.tight_layout()
        canvas2 = FigureCanvas(fig2)
        self.graphs_layout.addWidget(canvas2)
        
    def export_report(self):
        if not self.results_data:
            QMessageBox.warning(self, "Export Error", "No analysis results to export. Please run the analysis first.")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self,
            "Save Report",
            "MaxWire_Report.html",
            "HTML Files (*.html)"
        )

        if not file_path:
            return

        try:
            # Generate the text report HTML
            html_content = self.results_data['report_html']

            # Create the figures
            fig1, ax1 = plt.subplots(figsize=(8, 6), facecolor='#2e2e2e')
            labels = ['Covered', 'Missing']
            sizes = [self.results_data['overall_coverage_count'], self.results_data['missing_count']]
            colors = ['#27ae60', '#e74c3c']
            explode = (0.05, 0)
            ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
                    autopct='%1.1f%%', shadow=True, startangle=140, textprops={'color': 'white'})
            ax1.axis('equal')
            ax1.set_title('Circuit Coverage by Planned PNs', color='white')

            fig2, ax2 = plt.subplots(figsize=(8, 6), facecolor='#2e2e2e')
            pn_counts = [self.results_data['planned_pns_count'], self.results_data['optimized_pns_count']]
            pn_labels = ['Planned PNs', 'Optimized PNs']
            bar_colors = ['#2980b9', '#8e44ad']
            bars = ax2.bar(pn_labels, pn_counts, color=bar_colors)
            ax2.set_title('PN Optimization', color='white')
            ax2.set_ylabel('Number of PNs', color='white')
            ax2.set_facecolor('#2e2e2e')
            ax2.spines['bottom'].set_color('white')
            ax2.spines['left'].set_color('white')
            ax2.xaxis.label.set_color('white')
            ax2.yaxis.label.set_color('white')
            ax2.tick_params(axis='x', colors='white')
            ax2.tick_params(axis='y', colors='white')
            for bar in bars:
                yval = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom', color='white')
            fig2.tight_layout()

            # Save figures to in-memory bytes buffers
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format='png', facecolor='#2e2e2e')
            buf1.seek(0)
            image_b64_1 = base64.b64encode(buf1.getvalue()).decode('utf-8')
            plt.close(fig1)

            buf2 = io.BytesIO()
            fig2.savefig(buf2, format='png', facecolor='#2e2e2e')
            buf2.seek(0)
            image_b64_2 = base64.b64encode(buf2.getvalue()).decode('utf-8')
            plt.close(fig2)

            # Build the complete HTML string
            full_html = f"""
            <html>
            <head>
                <title>MaxWire Optimization Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #1e1e1e; color: #f0f0f0; padding: 20px; }}
                    .container {{ max-width: 900px; margin: auto; background: #2e2e2e; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.5); }}
                    h1, h2, h3 {{ color: #ffffff; }}
                    hr {{ border-color: #555; }}
                    ul {{ margin-left: 20px; }}
                    li {{ margin-bottom: 5px; }}
                    img {{ max-width: 100%; height: auto; display: block; margin: 20px 0; border: 1px solid #555; border-radius: 5px; }}
                    .chart-container {{ text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>MaxWire Optimization Report</h1>
                    <p>Report Generated: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    <hr>
                    {html_content}
                    
                    <h2>Graphs</h2>
                    <hr>
                    <div class="chart-container">
                        <h3>Circuit Coverage Pie Chart</h3>
                        <img src="data:image/png;base64,{image_b64_1}" alt="Circuit Coverage Pie Chart">
                    </div>
                    
                    <div class="chart-container">
                        <h3>PN Optimization Bar Chart</h3>
                        <img src="data:image/png;base64,{image_b64_2}" alt="PN Optimization Bar Chart">
                    </div>
                </div>
            </body>
            </html>
            """
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            QMessageBox.information(self, "Export Successful", f"Report successfully exported to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to save the file: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MaxWireOptimizer()
    ex.show()
    sys.exit(app.exec_())