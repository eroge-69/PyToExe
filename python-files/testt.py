"""
Portrait modern calculator (PyQt5)
- UI: Paid | Free (row 1), Quantity (row 2), Result (row 3)
- Behavior:
  * App auto-focuses on Paid on startup and whenever window becomes active.
  * Enter from Paid -> focus Free, Enter from Free -> focus Quantity,
    Enter from Quantity -> compute result and focus Paid again.
  * Fields retain previous values until replaced by new input.
  * Calculation uses Decimal for exactness and shows results with 2 decimals.
  * Handles invalid input (shows friendly tooltip but doesn't crash).
"""

import sys
from decimal import Decimal, InvalidOperation, getcontext, ROUND_HALF_UP

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QMessageBox,
    QPushButton,
)

# Set decimal precision sufficiently large for safe intermediate computations
getcontext().prec = 28


def dec_from_text(txt: str) -> Decimal:
    """
    Convert user text to Decimal reliably.
    Allows plain numbers with optional decimal point.
    Raises InvalidOperation on invalid input.
    """
    txt = txt.strip()
    if txt == "":
        # Empty treated as zero (keeps predictable behavior)
        return Decimal("0")
    # Replace commas (if user types thousands separators)
    txt = txt.replace(",", "")
    return Decimal(txt)


def format_two_decimals(d: Decimal) -> str:
    """Format Decimal to string with exactly two decimals, ROUND_HALF_UP."""
    quant = Decimal("0.01")
    rounded = d.quantize(quant, rounding=ROUND_HALF_UP)
    # Format with two decimals always (including trailing zeros)
    return f"{rounded:.2f}"


class PortraitCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Portrait Calculator")
        # Portrait size: width smaller than height (adjust as you wish)
        self.WIDTH = 380
        self.HEIGHT = 640
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setWindowFlags(
            Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint
        )

        self._build_ui()
        self._connect_signals()

        # Ensure initial focus
        self.paid_input.setFocus()

        # Install event filter to detect when window becomes active (foreground)
        QApplication.instance().installEventFilter(self)

    def _build_ui(self):
        # Styling (modern look)
        base_font = QFont("Segoe UI", 11)
        header_font = QFont("Segoe UI", 12, QFont.Bold)

        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f1724, stop:1 #0b1220);
                color: #E6EEF3;
            }
            QLineEdit {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
                padding: 12px;
                selection-background-color: rgba(255,255,255,0.14);
                color: #E6EEF3;
            }
            QLineEdit:focus {
                border: 1px solid #3AA1FF;
                background: rgba(255,255,255,0.08);
            }
            QLabel#labelTitle {
                color: #FFFFFF;
            }
            QLabel#labelResult {
                font-weight: 600;
                font-size: 18px;
                color: #DFF6FF;
            }
            QPushButton#calcBtn {
                border-radius: 10px;
                padding: 10px 14px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #21C3FF, stop:1 #2A9DF4);
                color: #02111A;
                font-weight: 600;
            }
            QPushButton#calcBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2AD8FF, stop:1 #3AAAF8);
            }
            """
        )

        outer = QVBoxLayout()
        outer.setContentsMargins(20, 24, 20, 24)
        outer.setSpacing(18)

        # Title
        title = QLabel("Modern Portrait Calculator")
        title.setObjectName("labelTitle")
        title.setFont(header_font)
        title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        outer.addWidget(title, alignment=Qt.AlignLeft)

        # Row 1: Paid and Free
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        paid_label = QLabel("Paid")
        paid_label.setFont(base_font)
        paid_label.setFixedWidth(54)
        self.paid_input = QLineEdit()
        self.paid_input.setFont(base_font)
        self.paid_input.setPlaceholderText("e.g. 5")
        self.paid_input.setObjectName("paidInput")

        free_label = QLabel("Free")
        free_label.setFont(base_font)
        free_label.setFixedWidth(54)
        self.free_input = QLineEdit()
        self.free_input.setFont(base_font)
        self.free_input.setPlaceholderText("e.g. 1")
        self.free_input.setObjectName("freeInput")

        # Numeric validators (allow decimals). We'll still parse using Decimal for safety.
        dbl_validator = QDoubleValidator(bottom=-1e12, top=1e12, decimals=6)
        dbl_validator.setNotation(QDoubleValidator.StandardNotation)
        self.paid_input.setValidator(dbl_validator)
        self.free_input.setValidator(dbl_validator)

        row1.addWidget(paid_label)
        row1.addWidget(self.paid_input, 1)
        row1.addWidget(free_label)
        row1.addWidget(self.free_input, 1)

        outer.addLayout(row1)

        # Row 2: Quantity (single wide input)
        qty_layout = QHBoxLayout()
        qty_layout.setSpacing(12)
        qty_label = QLabel("Quantity")
        qty_label.setFont(base_font)
        qty_label.setFixedWidth(80)
        self.qty_input = QLineEdit()
        self.qty_input.setFont(base_font)
        self.qty_input.setPlaceholderText("e.g. 12")
        self.qty_input.setObjectName("qtyInput")
        self.qty_input.setValidator(dbl_validator)
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(self.qty_input)
        outer.addLayout(qty_layout)

        # Row 3: Result label and a small Calculate button for mouse users
        result_box = QVBoxLayout()
        result_title = QLabel("Result (Paid & Free)")
        result_title.setFont(base_font)
        self.result_display = QLabel("0.00  &  0.00")
        self.result_display.setObjectName("labelResult")
        self.result_display.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.result_display.setMinimumHeight(48)

        # optional calc button for mouse users
        self.calc_button = QPushButton("Calculate")
        self.calc_button.setObjectName("calcBtn")
        self.calc_button.setFixedWidth(120)
        # layout for result and button
        row_result = QHBoxLayout()
        row_result.addWidget(self.result_display, 1)
        row_result.addWidget(self.calc_button, alignment=Qt.AlignRight)

        result_box.addWidget(result_title)
        result_box.addLayout(row_result)
        outer.addLayout(result_box)

        # Small hint
        hint = QLabel("Press Enter to move between fields and to calculate. Fields retain values until replaced.")
        hint.setWordWrap(True)
        hint.setFont(QFont("Segoe UI", 9))
        hint.setStyleSheet("color: #A6BDC9;")
        outer.addWidget(hint)

        # Make a tiny footer spacer so content centers nicely
        outer.addStretch()
        self.setLayout(outer)

    def _connect_signals(self):
        # Move focus in sequence on Enter
        self.paid_input.returnPressed.connect(self._focus_free)
        self.free_input.returnPressed.connect(self._focus_qty)
        self.qty_input.returnPressed.connect(self._calculate_and_cycle)

        # Calculate on clicking button
        self.calc_button.clicked.connect(self._calculate_and_cycle)

    def _focus_free(self):
        self.free_input.setFocus()
        # select all text so user can type new value and replace older value easily (excel-like)
        self.free_input.selectAll()

    def _focus_qty(self):
        self.qty_input.setFocus()
        self.qty_input.selectAll()

    def _calculate_and_cycle(self):
        # Compute result and then move focus to paid
        ok = self._compute_and_display()
        # After computing (even if invalid), cycle focus to paid and select all
        self.paid_input.setFocus()
        self.paid_input.selectAll()
        return ok

    def _compute_and_display(self) -> bool:
        """
        Perform the exact calculation as specified:
        - set_size = paid + free
        - sets = quantity / set_size
        - paid_result = sets * paid
        - free_result = sets * free
        Shows both with two decimals. Uses Decimal for exactness.
        Returns True on success, False on failure (invalid input).
        """
        try:
            paid = dec_from_text(self.paid_input.text())
            free = dec_from_text(self.free_input.text())
            qty = dec_from_text(self.qty_input.text())
        except InvalidOperation:
            self._show_error("Invalid number entered. Use digits and optional decimal point.")
            return False

        set_size = paid + free

        # Reject case where set_size is zero (both inputs zero) -> division by zero
        if set_size == Decimal("0"):
            self._show_error("Paid + Free cannot both be zero.")
            return False

        # For negative numbers: we allow them mathematically but show a warning (safer)
        # If you want to strictly disallow negative numbers, change behavior here.
        # We'll allow negatives but calculations will follow Decimal arithmetic.
        try:
            sets = qty / set_size
        except (InvalidOperation, ZeroDivisionError):
            self._show_error("Cannot compute the sets (division error). Check inputs.")
            return False

        paid_result = sets * paid
        free_result = sets * free

        # Format to two decimals always
        paid_str = format_two_decimals(paid_result)
        free_str = format_two_decimals(free_result)

        self.result_display.setText(f"{paid_str}  &  {free_str}")
        return True

    def _show_error(self, text: str):
        # Small non-blocking friendly message using tooltip-like QMesageBox information
        # We avoid raising exceptions to prevent any crash.
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Input Error")
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def eventFilter(self, obj, ev):
        """
        We installed a global event filter on the QApplication to detect
        when the application becomes active (window gains focus/foreground).
        On such ActivationChange, set focus to Paid field.
        """
        if ev.type() == QEvent.ApplicationActivate or ev.type() == QEvent.WindowActivate:
            # App became active — ensure Paid gets focus
            # Use singleShot to allow Qt to finish activation before focusing
            # But here we'll set focus directly as it's generally fine.
            self.paid_input.setFocus()
            self.paid_input.selectAll()
        return super().eventFilter(obj, ev)

    # Additionally handle direct widget activation changes (safety)
    def changeEvent(self, ev):
        super().changeEvent(ev)
        # QEvent.ActivationChange signals window activation
        if ev.type() == QEvent.ActivationChange:
            if self.isActiveWindow():
                self.paid_input.setFocus()
                self.paid_input.selectAll()


def main():
    app = QApplication(sys.argv)
    # High DPI support helps UI scale on modern displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = PortraitCalculator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()