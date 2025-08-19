import sys
import MetaTrader5 as mt5
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLineEdit, QPushButton, QTextEdit, QLabel,
                             QGroupBox, QDoubleSpinBox, QFrame, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

class PositionCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Position Size Calculator Pro")
        self.setWindowIcon(QIcon("icon.png"))  # Add your icon file
        self.setGeometry(100, 100, 950, 750)
        
        # Professional dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
                color: #d9dce0;
            }
            QGroupBox {
                background-color: #27293d;
                border: 1px solid #3d405b;
                border-radius: 8px;
                margin-top: 1.5ex;
                padding-top: 1.5ex;
                font-weight: bold;
                font-size: 11pt;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #6cacff;
            }
            QPushButton {
                background-color: #3a7bd5;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #2d68b1;
            }
            QPushButton:pressed {
                background-color: #1c4f8e;
            }
            QLineEdit, QTextEdit, QDoubleSpinBox {
                background-color: #1e1e2e;
                color: #ffffff;
                border: 1px solid #3d405b;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                selection-background-color: #3a7bd5;
            }
            QLabel {
                color: #a0a5b0;
                font-size: 10pt;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
            }
            #resultBox {
                background-color: #27293d;
                border: 1px solid #3d405b;
                border-radius: 8px;
                padding: 15px;
            }
            #tpContainer {
                background-color: #1e1e2e;
                border-radius: 8px;
                padding: 10px;
            }
            .resultLabel {
                font-size: 11pt;
                font-weight: bold;
                color: #6cacff;
            }
            .valueLabel {
                font-size: 12pt;
                font-weight: bold;
                color: #ffffff;
            }
            .tpBox {
                background-color: #2c3e50;
                border-radius: 6px;
                padding: 10px;
                min-width: 120px;
            }
            .tpHeader {
                font-weight: bold;
                font-size: 11pt;
                color: #6cacff;
                text-align: center;
            }
            .tpValue {
                font-weight: bold;
                font-size: 13pt;
                color: #ffffff;
                text-align: center;
            }
            .logHeader {
                font-weight: bold;
                color: #6cacff;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Header
        header = QLabel("محاسبه گر حرفه‌ای حجم پوزیشن")
        header.setStyleSheet("font-size: 16pt; font-weight: bold; color: #6cacff;")
        header.setAlignment(Qt.AlignCenter)
        header.setMinimumHeight(40)
        main_layout.addWidget(header)
        
        # Input Section
        input_group = QGroupBox("تنظیمات معامله")
        input_layout = QGridLayout()
        input_layout.setSpacing(15)
        input_layout.setColumnMinimumWidth(0, 120)
        input_layout.setColumnStretch(1, 3)
        
        # Account Balance
        balance_label = QLabel("موجودی حساب:")
        self.balance_spin = QDoubleSpinBox()
        self.balance_spin.setRange(1, 10000000)
        self.balance_spin.setValue(1000)
        self.balance_spin.setDecimals(2)
        self.balance_spin.setSuffix(" $")
        self.balance_spin.setSingleStep(100)
        
        # Risk Percentage
        risk_label = QLabel("درصد ریسک:")
        self.risk_spin = QDoubleSpinBox()
        self.risk_spin.setRange(0.1, 100)
        self.risk_spin.setValue(2)
        self.risk_spin.setDecimals(1)
        self.risk_spin.setSuffix(" %")
        self.risk_spin.setSingleStep(0.5)
        
        # Entry Price
        entry_label = QLabel("قیمت ورود:")
        self.entry_spin = QDoubleSpinBox()
        self.entry_spin.setRange(0.00001, 1000000)
        self.entry_spin.setValue(44944)
        self.entry_spin.setDecimals(5)
        
        # Stop Loss Price
        stoploss_label = QLabel("قیمت حد ضرر:")
        self.stoploss_spin = QDoubleSpinBox()
        self.stoploss_spin.setRange(0.00001, 1000000)
        self.stoploss_spin.setValue(44960)
        self.stoploss_spin.setDecimals(5)
        
        # Symbol
        symbol_label = QLabel("نماد:")
        self.symbol_edit = QLineEdit("DJIUSD")
        
        # TP Ratios
        tp_label = QLabel("نسبت‌های TP:")
        tp_layout = QHBoxLayout()
        self.tp_ratios = []
        for i in range(4):
            spin = QDoubleSpinBox()
            spin.setRange(0.1, 20)
            spin.setValue(i+1)
            spin.setDecimals(1)
            spin.setSingleStep(0.5)
            tp_layout.addWidget(spin)
            self.tp_ratios.append(spin)
        
        # Add to grid
        input_layout.addWidget(balance_label, 0, 0)
        input_layout.addWidget(self.balance_spin, 0, 1)
        input_layout.addWidget(risk_label, 1, 0)
        input_layout.addWidget(self.risk_spin, 1, 1)
        input_layout.addWidget(entry_label, 2, 0)
        input_layout.addWidget(self.entry_spin, 2, 1)
        input_layout.addWidget(stoploss_label, 3, 0)
        input_layout.addWidget(self.stoploss_spin, 3, 1)
        input_layout.addWidget(symbol_label, 4, 0)
        input_layout.addWidget(self.symbol_edit, 4, 1)
        input_layout.addWidget(tp_label, 5, 0)
        input_layout.addLayout(tp_layout, 5, 1)
        
        # Calculate button
        self.calculate_btn = QPushButton("محاسبه حجم پوزیشن")
        self.calculate_btn.setMinimumHeight(45)
        self.calculate_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.calculate_btn.clicked.connect(self.calculate)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        main_layout.addWidget(self.calculate_btn)
        
        # Results Section
        results_group = QGroupBox("نتایج محاسبات")
        results_layout = QVBoxLayout()
        
        # Main results
        main_result_layout = QHBoxLayout()
        
        # Lot size and risk
        left_result = QVBoxLayout()
        self.lot_label = QLabel("-")
        self.lot_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #6cacff;")
        self.lot_label.setAlignment(Qt.AlignCenter)
        lot_title = QLabel("حجم پوزیشن (لات)")
        lot_title.setAlignment(Qt.AlignCenter)
        
        self.risk_label = QLabel("-")
        self.risk_label.setStyleSheet("font-size: 14pt; color: #ffffff;")
        self.risk_label.setAlignment(Qt.AlignCenter)
        risk_title = QLabel("ریسک معامله")
        risk_title.setAlignment(Qt.AlignCenter)
        
        left_result.addWidget(lot_title)
        left_result.addWidget(self.lot_label)
        left_result.addSpacing(20)
        left_result.addWidget(risk_title)
        left_result.addWidget(self.risk_label)
        
        # Stop distance and loss per lot
        center_result = QVBoxLayout()
        self.stop_distance_label = QLabel("-")
        self.stop_distance_label.setStyleSheet("font-size: 14pt; color: #ffffff;")
        self.stop_distance_label.setAlignment(Qt.AlignCenter)
        stop_title = QLabel("فاصله استاپ (پوینت)")
        stop_title.setAlignment(Qt.AlignCenter)
        
        self.loss_per_lot_label = QLabel("-")
        self.loss_per_lot_label.setStyleSheet("font-size: 14pt; color: #ffffff;")
        self.loss_per_lot_label.setAlignment(Qt.AlignCenter)
        loss_title = QLabel("زیان هر لات")
        loss_title.setAlignment(Qt.AlignCenter)
        
        center_result.addWidget(stop_title)
        center_result.addWidget(self.stop_distance_label)
        center_result.addSpacing(20)
        center_result.addWidget(loss_title)
        center_result.addWidget(self.loss_per_lot_label)
        
        # TP results
        right_result = QVBoxLayout()
        tp_title = QLabel("سطوح سود (TP)")
        tp_title.setAlignment(Qt.AlignCenter)
        
        tp_container = QWidget()
        tp_container.setObjectName("tpContainer")
        tp_grid = QGridLayout(tp_container)
        
        self.tp_labels = []
        for i in range(4):
            # TP header
            header = QLabel(f"TP{i+1} (1:{self.tp_ratios[i].value()})".replace(".0",""))
            header.setStyleSheet(".tpHeader")
            header.setAlignment(Qt.AlignCenter)
            
            # TP value
            value = QLabel("-")
            value.setStyleSheet(".tpValue")
            value.setAlignment(Qt.AlignCenter)
            
            # Profit label
            profit = QLabel("-")
            profit.setStyleSheet("font-size: 11pt; color: #4cd964; text-align: center;")
            profit.setAlignment(Qt.AlignCenter)
            
            tp_grid.addWidget(header, 0, i)
            tp_grid.addWidget(value, 1, i)
            tp_grid.addWidget(profit, 2, i)
            self.tp_labels.append((header, value, profit))
        
        right_result.addWidget(tp_title)
        right_result.addWidget(tp_container)
        
        # Add to main result layout
        main_result_layout.addLayout(left_result, 35)
        main_result_layout.addLayout(center_result, 30)
        main_result_layout.addLayout(right_result, 35)
        
        results_layout.addLayout(main_result_layout)
        
        # Log output
        log_title = QLabel("جزئیات محاسبات")
        log_title.setStyleSheet(".logHeader")
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("نتایج محاسبات در اینجا نمایش داده می‌شود...")
        
        results_layout.addWidget(log_title)
        results_layout.addWidget(self.log_output)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)
        
    def calculate(self):
        # Get values from inputs
        balance = self.balance_spin.value()
        risk_percent = self.risk_spin.value()
        entry_price = self.entry_spin.value()
        stop_loss_price = self.stoploss_spin.value()
        symbol = self.symbol_edit.text().strip()
        tp_ratios = [spin.value() for spin in self.tp_ratios]
        
        # Clear previous results
        self.lot_label.setText("-")
        self.risk_label.setText("-")
        self.stop_distance_label.setText("-")
        self.loss_per_lot_label.setText("-")
        
        for header, value, profit in self.tp_labels:
            value.setText("-")
            profit.setText("-")
        
        self.log_output.clear()
        
        # Connect to MT5
        if not mt5.initialize():
            error = mt5.last_error()
            self.log_output.append(f"<span style='color:#ff6b6b'>خطا در اتصال به متاتریدر: {error}</span>")
            return
        
        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.log_output.append(f"<span style='color:#ff6b6b'>نماد {symbol} یافت نشد</span>")
                return
            
            # Activate symbol if not visible
            if not symbol_info.visible:
                self.log_output.append(f"<span style='color:#ffd166'>⚠️ نماد {symbol} غیرفعال است، در حال فعال سازی...</span>")
                if not mt5.symbol_select(symbol, True):
                    self.log_output.append(f"<span style='color:#ff6b6b'>فعال سازی ناموفق: {symbol}</span>")
                    return
            
            # Calculate risk amount
            risk_amount = balance * (risk_percent / 100)
            
            # Get symbol properties
            contract_size = symbol_info.trade_contract_size
            tick_size = symbol_info.trade_tick_size
            tick_value = symbol_info.trade_tick_value
            
            # Calculate stop distance in points
            stop_distance_points = abs(entry_price - stop_loss_price)
            
            # Calculate loss per lot
            loss_per_lot = (stop_distance_points / tick_size) * tick_value
            
            # Calculate position size
            lots = risk_amount / loss_per_lot if loss_per_lot > 0 else 0
            
            # Apply broker constraints
            min_lot = symbol_info.volume_min
            max_lot = symbol_info.volume_max
            lot_step = symbol_info.volume_step
            
            if lots < min_lot:
                self.log_output.append(f"<span style='color:#ffd166'>⚠️ حجم محاسبه‌شده ({lots:.2f}) کوچکتر از حداقل مجاز ({min_lot}) است</span>")
                lots = min_lot
            elif lots > max_lot:
                self.log_output.append(f"<span style='color:#ffd166'>⚠️ حجم محاسبه‌شده ({lots:.2f}) بزرگتر از حداکثر مجاز ({max_lot}) است</span>")
                lots = max_lot
            
            # Round to nearest step
            if lot_step > 0:
                lots = round(lots / lot_step) * lot_step
            
            # Calculate actual risk
            actual_risk = lots * loss_per_lot
            
            # Update main results
            self.lot_label.setText(f"{lots:.2f}")
            self.risk_label.setText(f"{actual_risk:.2f} $")
            self.stop_distance_label.setText(f"{stop_distance_points:.2f}")
            self.loss_per_lot_label.setText(f"{loss_per_lot:.2f} $")
            
            # Calculate and display TPs
            direction = 1 if entry_price < stop_loss_price else -1
            for i, ratio in enumerate(tp_ratios):
                # Update TP header
                self.tp_labels[i][0].setText(f"TP{i+1} (1:{ratio})")
                
                # Calculate TP price
                tp_price = entry_price + (stop_distance_points * ratio * direction)
                self.tp_labels[i][1].setText(f"{tp_price:.5f}")
                
                # Calculate TP profit
                tp_profit = (stop_distance_points * ratio / tick_size) * tick_value * lots
                self.tp_labels[i][2].setText(f"{tp_profit:.2f} $")
            
            # Show detailed log
            self.log_output.append("<b>--- جزئیات نماد و محاسبات ---</b>")
            self.log_output.append(f"<b>نماد:</b> {symbol}")
            self.log_output.append(f"<b>موجودی حساب:</b> {balance:.2f} $")
            self.log_output.append(f"<b>درصد ریسک:</b> {risk_percent}%")
            self.log_output.append(f"<b>ریسک دلاری:</b> {risk_amount:.2f} $")
            self.log_output.append(f"<b>قیمت ورود:</b> {entry_price}")
            self.log_output.append(f"<b>قیمت حد ضرر:</b> {stop_loss_price}")
            self.log_output.append(f"<b>فاصله استاپ:</b> {stop_distance_points:.2f} پوینت")
            self.log_output.append(f"<b>اندازه قرارداد:</b> {contract_size}")
            self.log_output.append(f"<b>اندازه تیک:</b> {tick_size}")
            self.log_output.append(f"<b>ارزش تیک:</b> {tick_value}")
            self.log_output.append(f"<b>حداقل لات:</b> {min_lot}")
            self.log_output.append(f"<b>حداکثر لات:</b> {max_lot}")
            self.log_output.append(f"<b>گام لات:</b> {lot_step}")
            self.log_output.append(f"<b>زیان هر لات:</b> {loss_per_lot:.2f} $")
            self.log_output.append(f"<b>حجم پوزیشن:</b> {lots:.2f} لات")
            self.log_output.append(f"<b>ریسک واقعی:</b> {actual_risk:.2f} $")
            self.log_output.append("<b>--- پایان محاسبات ---</b>")
            
        except Exception as e:
            self.log_output.append(f"<span style='color:#ff6b6b'>خطا: {str(e)}</span>")
        finally:
            mt5.shutdown()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))
    window = PositionCalculator()
    window.show()
    sys.exit(app.exec_())