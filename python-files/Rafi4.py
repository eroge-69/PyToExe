import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                             QPushButton, QGroupBox, QComboBox, QSpinBox, 
                             QDoubleSpinBox, QMessageBox, QTabWidget, QTextEdit,
                             QAction, QFileDialog, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextDocument
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog

class EJuiceCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("E-Juice Calculator")
        self.setGeometry(100, 100, 800, 600)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#calculateButton {
                background-color: #2196F3;
            }
            QPushButton#calculateButton:hover {
                background-color: #0b7dda;
            }
            QPushButton#printButton {
                background-color: #FF9800;
            }
            QPushButton#printButton:hover {
                background-color: #F57C00;
            }
            QLabel {
                padding: 4px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
        """)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Create calculator tab
        calculator_tab = QWidget()
        calculator_layout = QVBoxLayout(calculator_tab)
        tabs.addTab(calculator_tab, "Calculator")
        
        # Create notes tab
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        tabs.addTab(notes_tab, "Recipe Notes")
        
        # Notes area
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter your recipe notes here...")
        notes_layout.addWidget(self.notes_edit)
        
        # Recipe Information Group
        recipe_group = QGroupBox("Recipe Information")
        recipe_layout = QGridLayout()
        
        recipe_layout.addWidget(QLabel("Recipe Name:"), 0, 0)
        self.recipe_name = QLineEdit("My Custom E-Juice")
        recipe_layout.addWidget(self.recipe_name, 0, 1)
        
        recipe_layout.addWidget(QLabel("Batch Size (ml):"), 1, 0)
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 1000)
        self.batch_size.setValue(60)
        self.batch_size.setSuffix(" ml")
        recipe_layout.addWidget(self.batch_size, 1, 1)
        
        recipe_layout.addWidget(QLabel("PG/VG Ratio:"), 2, 0)
        ratio_layout = QHBoxLayout()
        self.pg_ratio = QSpinBox()
        self.pg_ratio.setRange(0, 100)
        self.pg_ratio.setValue(30)
        self.pg_ratio.setSuffix("%")
        ratio_layout.addWidget(self.pg_ratio)
        ratio_layout.addWidget(QLabel("PG"))
        
        ratio_layout.addWidget(QLabel("/"))
        
        self.vg_ratio = QSpinBox()
        self.vg_ratio.setRange(0, 100)
        self.vg_ratio.setValue(70)
        self.vg_ratio.setSuffix("%")
        ratio_layout.addWidget(self.vg_ratio)
        ratio_layout.addWidget(QLabel("VG"))
        recipe_layout.addLayout(ratio_layout, 2, 1)
        
        self.pg_ratio.valueChanged.connect(self.update_vg_ratio)
        self.vg_ratio.valueChanged.connect(self.update_pg_ratio)
        
        recipe_group.setLayout(recipe_layout)
        calculator_layout.addWidget(recipe_group)
        
        # Nicotine Information Group
        nicotine_group = QGroupBox("Nicotine Information")
        nicotine_layout = QGridLayout()
        
        nicotine_layout.addWidget(QLabel("Nicotine Strength:"), 0, 0)
        self.nic_strength = QDoubleSpinBox()
        self.nic_strength.setRange(0, 100)
        self.nic_strength.setValue(100)
        self.nic_strength.setSuffix(" mg/ml")
        nicotine_layout.addWidget(self.nic_strength, 0, 1)
        
        nicotine_layout.addWidget(QLabel("Nicotine Base:"), 1, 0)
        self.nic_base = QComboBox()
        self.nic_base.addItems(["PG", "VG", "50/50"])
        nicotine_layout.addWidget(self.nic_base, 1, 1)
        
        nicotine_layout.addWidget(QLabel("Target Strength:"), 2, 0)
        self.target_strength = QDoubleSpinBox()
        self.target_strength.setRange(0, 50)
        self.target_strength.setValue(6)
        self.target_strength.setSuffix(" mg/ml")
        nicotine_layout.addWidget(self.target_strength, 2, 1)
        
        nicotine_group.setLayout(nicotine_layout)
        calculator_layout.addWidget(nicotine_group)
        
        # Flavorings Group
        flavor_group = QGroupBox("Flavorings")
        flavor_layout = QVBoxLayout()
        
        # Flavor input fields will be added dynamically
        self.flavor_layout = QGridLayout()
        self.flavor_layout.addWidget(QLabel("Flavor"), 0, 0)
        self.flavor_layout.addWidget(QLabel("Percentage"), 0, 1)
        self.flavor_layout.addWidget(QLabel(""), 0, 2)  # For remove buttons
        
        self.flavor_inputs = []
        self.add_flavor_row()
        
        flavor_layout.addLayout(self.flavor_layout)
        
        add_flavor_btn = QPushButton("Add Another Flavor")
        add_flavor_btn.clicked.connect(self.add_flavor_row)
        flavor_layout.addWidget(add_flavor_btn)
        
        flavor_group.setLayout(flavor_layout)
        calculator_layout.addWidget(flavor_group)
        
        # Results Group
        results_group = QGroupBox("Results")
        results_layout = QGridLayout()
        
        # Create a bold font for result labels
        result_font = QFont()
        result_font.setBold(True)
        
        results_layout.addWidget(QLabel("Nicotine Base:"), 0, 0)
        self.result_nic = QLabel("0.00 ml")
        self.result_nic.setFont(result_font)
        results_layout.addWidget(self.result_nic, 0, 1)
        
        results_layout.addWidget(QLabel("PG:"), 1, 0)
        self.result_pg = QLabel("0.00 ml")
        self.result_pg.setFont(result_font)
        results_layout.addWidget(self.result_pg, 1, 1)
        
        results_layout.addWidget(QLabel("VG:"), 2, 0)
        self.result_vg = QLabel("0.00 ml")
        self.result_vg.setFont(result_font)
        results_layout.addWidget(self.result_vg, 2, 1)
        
        results_layout.addWidget(QLabel("Total Flavoring:"), 3, 0)
        self.result_flavor = QLabel("0.00 ml")
        self.result_flavor.setFont(result_font)
        results_layout.addWidget(self.result_flavor, 3, 1)
        
        results_layout.addWidget(QLabel("Total:"), 4, 0)
        self.result_total = QLabel("0.00 ml")
        self.result_total.setFont(result_font)
        results_layout.addWidget(self.result_total, 4, 1)
        
        results_group.setLayout(results_layout)
        calculator_layout.addWidget(results_group)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Calculate button
        calculate_btn = QPushButton("Calculate Recipe", objectName="calculateButton")
        calculate_btn.clicked.connect(self.calculate_recipe)
        buttons_layout.addWidget(calculate_btn)
        
        # Print button
        print_btn = QPushButton("Print Recipe", objectName="printButton")
        print_btn.clicked.connect(self.print_recipe)
        buttons_layout.addWidget(print_btn)
        
        calculator_layout.addLayout(buttons_layout)
        
        # Initialize calculation
        self.calculate_recipe()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Print action
        print_action = QAction('Print Recipe', self)
        print_action.setShortcut('Ctrl+P')
        print_action.triggered.connect(self.print_recipe)
        file_menu.addAction(print_action)
        
        # Export action
        export_action = QAction('Export as PDF', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def update_pg_ratio(self):
        self.pg_ratio.setValue(100 - self.vg_ratio.value())
    
    def update_vg_ratio(self):
        self.vg_ratio.setValue(100 - self.pg_ratio.value())
    
    def add_flavor_row(self):
        row = len(self.flavor_inputs)
        
        flavor_name = QLineEdit()
        flavor_name.setPlaceholderText("Flavor name")
        
        flavor_percentage = QDoubleSpinBox()
        flavor_percentage.setRange(0, 100)
        flavor_percentage.setValue(5)
        flavor_percentage.setSuffix("%")
        
        remove_btn = QPushButton("Remove")
        remove_btn.setStyleSheet("background-color: #f44336;")
        remove_btn.clicked.connect(lambda: self.remove_flavor_row(row))
        
        self.flavor_layout.addWidget(flavor_name, row + 1, 0)
        self.flavor_layout.addWidget(flavor_percentage, row + 1, 1)
        self.flavor_layout.addWidget(remove_btn, row + 1, 2)
        
        self.flavor_inputs.append((flavor_name, flavor_percentage, remove_btn))
    
    def remove_flavor_row(self, row):
        if len(self.flavor_inputs) <= 1:
            QMessageBox.warning(self, "Warning", "You need at least one flavor!")
            return
        
        # Remove widgets from layout
        for widget in self.flavor_inputs[row]:
            self.flavor_layout.removeWidget(widget)
            widget.deleteLater()
        
        # Remove from list
        self.flavor_inputs.pop(row)
        
        # Re-index remaining rows
        for i, (name, percent, btn) in enumerate(self.flavor_inputs):
            btn.clicked.disconnect()
            btn.clicked.connect(lambda checked, idx=i: self.remove_flavor_row(idx))
    
    def calculate_recipe(self):
        try:
            batch_size = self.batch_size.value()
            pg_ratio = self.pg_ratio.value() / 100
            vg_ratio = self.vg_ratio.value() / 100
            nic_strength = self.nic_strength.value()
            target_strength = self.target_strength.value()
            nic_base = self.nic_base.currentText()
            
            # Calculate nicotine amount
            nic_ml = (target_strength * batch_size) / nic_strength if nic_strength > 0 else 0
            
            # Calculate total flavor percentage and amount
            total_flavor_percent = 0
            flavor_breakdown = []
            
            for name, percent, _ in self.flavor_inputs:
                flavor_percent = percent.value()
                total_flavor_percent += flavor_percent
                flavor_name = name.text() or "Unnamed Flavor"
                flavor_breakdown.append(f"{flavor_name}: {flavor_percent}%")
            
            flavor_ml = batch_size * total_flavor_percent / 100
            
            # Calculate base liquids
            # First subtract nicotine and flavor from total
            base_ml = batch_size - nic_ml - flavor_ml
            
            # Calculate PG and VG amounts based on ratio
            # Adjust for nicotine base type
            if nic_base == "PG":
                pg_from_nic = nic_ml
                vg_from_nic = 0
            elif nic_base == "VG":
                pg_from_nic = 0
                vg_from_nic = nic_ml
            else:  # 50/50
                pg_from_nic = nic_ml * 0.5
                vg_from_nic = nic_ml * 0.5
            
            # Calculate additional PG and VG needed
            total_pg_required = batch_size * pg_ratio
            total_vg_required = batch_size * vg_ratio
            
            additional_pg = total_pg_required - pg_from_nic
            additional_vg = total_vg_required - vg_from_nic
            
            # Ensure non-negative values
            additional_pg = max(0, additional_pg)
            additional_vg = max(0, additional_vg)
            
            # Update results
            self.result_nic.setText(f"{nic_ml:.2f} ml")
            self.result_pg.setText(f"{additional_pg:.2f} ml")
            self.result_vg.setText(f"{additional_vg:.2f} ml")
            self.result_flavor.setText(f"{flavor_ml:.2f} ml")
            self.result_total.setText(f"{batch_size:.2f} ml")
            
            # Update notes with recipe summary
            notes_text = f"Recipe: {self.recipe_name.text()}\n"
            notes_text += f"Batch Size: {batch_size} ml\n"
            notes_text += f"Target Nicotine: {target_strength} mg/ml\n"
            notes_text += f"PG/VG Ratio: {self.pg_ratio.value()}/{self.vg_ratio.value()}\n\n"
            notes_text += "Ingredients:\n"
            notes_text += f"- Nicotine Base ({nic_strength} mg/ml, {nic_base}): {nic_ml:.2f} ml\n"
            notes_text += f"- PG: {additional_pg:.2f} ml\n"
            notes_text += f"- VG: {additional_vg:.2f} ml\n"
            notes_text += f"- Flavoring: {flavor_ml:.2f} ml\n\n"
            notes_text += "Flavor Breakdown:\n"
            for flavor in flavor_breakdown:
                notes_text += f"- {flavor}\n"
            
            self.notes_edit.setPlainText(notes_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during calculation: {str(e)}")
    
    def print_recipe(self):
        try:
            # Create a printer object
            printer = QPrinter(QPrinter.HighResolution)
            
            # Create print dialog
            print_dialog = QPrintDialog(printer, self)
            
            if print_dialog.exec_() == QPrintDialog.Accepted:
                # Create a document for printing
                document = QTextDocument()
                
                # Get the recipe text from notes
                recipe_text = self.notes_edit.toPlainText()
                
                # Format for printing with HTML
                html_content = f"""
                <html>
                <head>
                <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; }}
                .recipe-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .ingredients {{ margin-top: 20px; }}
                .ingredient-list {{ margin-left: 20px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #7f8c8d; text-align: center; }}
                </style>
                </head>
                <body>
                <h1>E-Juice Recipe: {self.recipe_name.text()}</h1>
                <div class="recipe-info">
                """
                
                # Add recipe details
                lines = recipe_text.split('\n')
                for line in lines:
                    if line.strip() and ':' in line:
                        parts = line.split(':', 1)
                        html_content += f"<p><strong>{parts[0]}:</strong>{parts[1]}</p>"
                    elif line.strip():
                        html_content += f"<h2>{line}</h2>"
                    else:
                        html_content += "<br/>"
                
                html_content += """
                </div>
                <div class="footer">
                    <p>Printed from E-Juice Calculator</p>
                </div>
                </body>
                </html>
                """
                
                document.setHtml(html_content)
                document.print_(printer)
                
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"An error occurred while printing: {str(e)}")
    
    def export_pdf(self):
        try:
            # Get file path for saving
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export PDF", f"{self.recipe_name.text()}.pdf", "PDF Files (*.pdf)"
            )
            
            if file_path:
                # Create a printer object set to output PDF
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)
                
                # Create a document for printing
                document = QTextDocument()
                
                # Get the recipe text from notes
                recipe_text = self.notes_edit.toPlainText()
                
                # Format for printing with HTML
                html_content = f"""
                <html>
                <head>
                <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; }}
                .recipe-info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .ingredients {{ margin-top: 20px; }}
                .ingredient-list {{ margin-left: 20px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #7f8c8d; text-align: center; }}
                </style>
                </head>
                <body>
                <h1>E-Juice Recipe: {self.recipe_name.text()}</h1>
                <div class="recipe-info">
                """
                
                # Add recipe details
                lines = recipe_text.split('\n')
                for line in lines:
                    if line.strip() and ':' in line:
                        parts = line.split(':', 1)
                        html_content += f"<p><strong>{parts[0]}:</strong>{parts[1]}</p>"
                    elif line.strip():
                        html_content += f"<h2>{line}</h2>"
                    else:
                        html_content += "<br/>"
                
                html_content += """
                </div>
                <div class="footer">
                    <p>Exported from E-Juice Calculator</p>
                </div>
                </body>
                </html>
                """
                
                document.setHtml(html_content)
                document.print_(printer)
                
                QMessageBox.information(self, "Export Successful", f"Recipe exported to {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred while exporting: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont()
    font.setPointSize(10)
    app.setFont(font)
    
    window = EJuiceCalculator()
    window.show()
    sys.exit(app.exec_())