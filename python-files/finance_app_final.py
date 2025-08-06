
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QLineEdit, QTreeView, QMainWindow, QMessageBox,
    QFileDialog
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
import sys
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as F_Canvas
from matplotlib.figure import Figure


os.system("cls" if os.name == "nt" else "clearpython -m PyInstaller --onefile --noconsole finance_app_final.py")

class Finance_app(QMainWindow):  
    def __init__(self):
        super(Finance_app, self).__init__()
        
        self.main_window = QWidget()

        # Window settings
        self.resize(800, 600)
        self.setWindowTitle("Finance App")

        # Input fields
        self.interest_rate = QLineEdit()
        self.interest_rate_text = QLabel('Interest Rate (%):')
        self.initial_investment = QLineEdit()
        self.initial_investment_text = QLabel("Principal:")
        self.Number_of_years = QLineEdit()
        self.Number_of_years_text = QLabel("Waiting Period:")

        # Tree view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Year", "Amount"])
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.header().setDefaultAlignment(Qt.AlignCenter)

        # Beautify the TreeView
        self.tree_view.setStyleSheet("""
            QTreeView {
                gridline-color: gray;
                font-size: 14px;
                selection-background-color: #d0eaff;
            }
            QTreeView::item {
                border-bottom: 1px solid lightgray;
            }
            QHeaderView::section {
                background-color: lightgray;
                padding: 10px;
                border: 1px solid gray;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }
        """)

        # Buttons
        self.calc_button = QPushButton("Calculate")
        self.clear_button = QPushButton("Wipe Data")
        self.save_button = QPushButton("Save")

        # Matplotlib Figure
        self.figure = Figure()
        self.canvas = F_Canvas(self.figure)

        # Layouts
        master_layout = QVBoxLayout()
        row_1 = QHBoxLayout()
        row_2 = QHBoxLayout()
        col_1 = QVBoxLayout()
        col_2 = QVBoxLayout()

        # Row 1: Inputs
        row_1.addWidget(self.initial_investment_text)
        row_1.addWidget(self.initial_investment)
        row_1.addWidget(self.interest_rate_text)
        row_1.addWidget(self.interest_rate)
        row_1.addWidget(self.Number_of_years_text)
        row_1.addWidget(self.Number_of_years)

        # Column 1: Tree and buttons
        col_1.addWidget(self.tree_view)
        col_1.addWidget(self.calc_button)
        col_1.addWidget(self.clear_button)
        col_1.addWidget(self.save_button)

        # Column 2: Chart
        col_2.addWidget(self.canvas)

        # Row 2: Columns
        row_2.addLayout(col_1, 20)  
        row_2.addLayout(col_2, 80)  

        master_layout.addLayout(row_1)
        master_layout.addLayout(row_2)

        self.main_window.setLayout(master_layout)
        self.setCentralWidget(self.main_window)
        
        # Button actions
        self.calc_button.clicked.connect(self.calc_interest_rate)
        self.clear_button.clicked.connect(self.clear)
        self.save_button.clicked.connect(self.savers)

    def calc_interest_rate(self):
        try:
            interest_rate = float(self.interest_rate.text())
            principal = float(self.initial_investment.text())
            years = int(self.Number_of_years.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numbers.")
            return

        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Year", "Amount"])
        self.tree_view.header().setDefaultAlignment(Qt.AlignCenter)

        total = principal
        year_values = []
        for x in range(1, years + 1):
            total += total * (interest_rate / 100)
            item_year = QStandardItem(str(x))
            item_amount = QStandardItem(f"{total:.2f}")
            item_year.setTextAlignment(Qt.AlignCenter)
            item_amount.setTextAlignment(Qt.AlignCenter)
            self.model.appendRow([item_year, item_amount])
            year_values.append(total)

        # Plotting
        self.figure.clear()
        ax = self.figure.subplots()
        ax.plot(range(1, years + 1), year_values, marker='o')
        ax.set_title("Interest Chart")
        ax.set_xlabel("Year")
        ax.set_ylabel("Incremented Values")
        ax.grid(True)
        self.canvas.draw()

    def savers(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            folder_path = os.path.join(dir_path, "Saved")
            os.makedirs(folder_path, exist_ok=True)

            file_path = os.path.join(folder_path, "results.csv")
            
            try:
                initial_investment = float(self.initial_investment.text())
                interest_rate = float(self.interest_rate.text())
                years = int(self.Number_of_years.text())
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Please make sure all inputs are filled in correctly.")
                return

            with open(file_path, "w") as file:
                file.write("Investment Details\n")
                file.write(f"Principal,{initial_investment}\n")
                file.write(f"Interest Rate,{interest_rate:.2f}%\n")
                file.write(f"Years,{years}\n")
                file.write("\nGrowth Over Time\n")
                file.write("Year,Total\n")
                for row in range(self.model.rowCount()):
                    year = self.model.index(row, 0).data()
                    total = self.model.index(row, 1).data()
                    file.write(f"{year},{total}\n")

            # Save the chart
            self.figure.savefig(os.path.join(folder_path, "chart.png"))

            QMessageBox.information(self, "Save Results", "Results Saved Successfully")
        else:
            QMessageBox.warning(self, "Save Results", "Save could not be done, Missing Directory")

    def clear (self):
            confirm = QMessageBox.question(
                self,
                "Do you want to clear the data?",
                "This will wipe off all your data (Bye-Bye Data), Do you wish to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm == QMessageBox.No:
                return

            self.model.clear()
            self.model.setHorizontalHeaderLabels(["Year", "Amount"])
            self.interest_rate.clear()
            self.initial_investment.clear()
            self.Number_of_years.clear()
            self.figure.clear()
            self.canvas.draw()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Finance_app()
    main.show()
    sys.exit(app.exec_())
