import sys
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit
from PyQt5.QtCore import Qt

class CalendarConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar Converter")
        self.setGeometry(100, 100, 400, 500)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Gregorian to Fixed Conversion
        self.gregorian_label = QLabel("Gregorian → Fixed Calendar")
        self.gregorian_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.layout.addWidget(self.gregorian_label)

        self.gregorian_input = QLineEdit()
        self.gregorian_input.setPlaceholderText("Enter Gregorian date (YYYY-MM-DD)")
        self.layout.addWidget(self.gregorian_input)

        self.gregorian_button = QPushButton("Convert")
        self.gregorian_button.clicked.connect(self.convert_gregorian_to_fixed)
        self.layout.addWidget(self.gregorian_button)

        self.gregorian_result = QTextEdit()
        self.gregorian_result.setReadOnly(True)
        self.gregorian_result.setMaximumHeight(50)
        self.layout.addWidget(self.gregorian_result)

        # Fixed to Gregorian Conversion
        self.fixed_label = QLabel("Fixed Calendar → Gregorian")
        self.fixed_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.layout.addWidget(self.fixed_label)

        self.fixed_year = QLineEdit()
        self.fixed_year.setPlaceholderText("Year")
        self.layout.addWidget(self.fixed_year)

        self.fixed_month = QLineEdit()
        self.fixed_month.setPlaceholderText("Month (1-13)")
        self.layout.addWidget(self.fixed_month)

        self.fixed_day = QLineEdit()
        self.fixed_day.setPlaceholderText("Day (1-28)")
        self.layout.addWidget(self.fixed_day)

        self.day_type = QComboBox()
        self.day_type.addItems(["Regular Day", "Year Day", "Leap Day"])
        self.layout.addWidget(self.day_type)

        self.day_type_note = QLabel("Note: Leap Day is only available in leap years.")
        self.day_type_note.setStyleSheet("font-size: 12px; color: gray;")
        self.layout.addWidget(self.day_type_note)

        self.fixed_button = QPushButton("Convert")
        self.fixed_button.clicked.connect(self.convert_fixed_to_gregorian)
        self.layout.addWidget(self.fixed_button)

        self.fixed_result = QTextEdit()
        self.fixed_result.setReadOnly(True)
        self.fixed_result.setMaximumHeight(50)
        self.layout.addWidget(self.fixed_result)

        # Update Leap Day option when year changes
        self.fixed_year.textChanged.connect(self.update_leap_day_option)

    def is_leap_year(self, year):
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def get_day_of_year(self, date):
        start = datetime(date.year, 1, 1)
        delta = date - start
        return delta.days + 1

    def update_leap_day_option(self):
        try:
            year = int(self.fixed_year.text())
            if not self.is_leap_year(year):
                self.day_type.setCurrentIndex(0)  # Reset to Regular Day
                self.day_type.model().item(2).setEnabled(False)  # Disable Leap Day
            else:
                self.day_type.model().item(2).setEnabled(True)  # Enable Leap Day
        except ValueError:
            self.day_type.model().item(2).setEnabled(False)  # Disable Leap Day if year is invalid

    def convert_gregorian_to_fixed(self):
        try:
            date = datetime.strptime(self.gregorian_input.text(), "%Y-%m-%d")
            year = date.year
            day_of_year = self.get_day_of_year(date)
            result = ""

            if day_of_year == 365 and not self.is_leap_year(year):
                result = f"Year {year}, Year Day (outside month)"
            elif day_of_year == 366 and self.is_leap_year(year):
                result = f"Year {year}, Leap Day (outside month)"
            elif day_of_year == 365 and self.is_leap_year(year):
                result = f"Year {year}, Year Day (outside month)"
            else:
                month = (day_of_year - 1) // 28 + 1
                day = day_of_year - (month - 1) * 28
                result = f"Year {year}, Month {month}, Day {day}"

            self.gregorian_result.setText(result)
        except ValueError:
            self.gregorian_result.setText("Please enter a valid date (YYYY-MM-DD).")

    def convert_fixed_to_gregorian(self):
        try:
            year = int(self.fixed_year.text())
            if year < 1:
                self.fixed_result.setText("Please enter a valid year.")
                return

            day_type = self.day_type.currentText()
            is_leap = self.is_leap_year(year)

            if day_type == "Year Day":
                day_of_year = 365
                date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
                self.fixed_result.setText(f"Gregorian Date: {date.strftime('%Y-%m-%d')} (Year Day)")
                return
            elif day_type == "Leap Day":
                if not is_leap:
                    self.fixed_result.setText("Leap Day is only valid in a leap year.")
                    return
                day_of_year = 366
                date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
                self.fixed_result.setText(f"Gregorian Date: {date.strftime('%Y-%m-%d')} (Leap Day)")
                return

            month = int(self.fixed_month.text())
            day = int(self.fixed_day.text())

            if month < 1 or month > 13 or day < 1 or day > 28:
                self.fixed_result.setText("Please enter a valid month (1-13) and day (1-28).")
                return

            day_of_year = (month - 1) * 28 + day
            date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
            self.fixed_result.setText(f"Gregorian Date: {date.strftime('%Y-%m-%d')}")
        except ValueError:
            self.fixed_result.setText("Please enter valid numeric inputs for year, month, and day.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalendarConverter()
    window.show()
    sys.exit(app.exec_())