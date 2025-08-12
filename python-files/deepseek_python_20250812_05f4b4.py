import sys
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QWidget, QLabel, QTextEdit, QSpinBox, 
                             QComboBox, QInputDialog, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class TradingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.trader = None
        self.mode = "PAPER"  # Default mode
        self.initUI()
        
    def initUI(self):
        # Main Window Setup
        self.setWindowTitle('QuantumTrader Pro')
        self.setGeometry(300, 300, 600, 700)
        
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        
        # 1. Mode Selection Group
        mode_group = QGroupBox("Trading Mode")
        mode_layout = QHBoxLayout()
        
        self.btn_paper = QPushButton('Paper Trading', self)
        self.btn_paper.setCheckable(True)
        self.btn_paper.setChecked(True)
        self.btn_paper.clicked.connect(lambda: self.set_mode("PAPER"))
        
        self.btn_backtest = QPushButton('Backtest', self)
        self.btn_backtest.setCheckable(True)
        self.btn_backtest.clicked.connect(lambda: self.set_mode("BACKTEST"))
        
        self.btn_live = QPushButton('Live Trading', self)
        self.btn_live.setCheckable(True)
        self.btn_live.clicked.connect(lambda: self.set_mode("LIVE"))
        
        mode_layout.addWidget(self.btn_paper)
        mode_layout.addWidget(self.btn_backtest)
        mode_layout.addWidget(self.btn_live)
        mode_group.setLayout(mode_layout)
        
        # 2. System Controls Group
        control_group = QGroupBox("System Controls")
        control_layout = QVBoxLayout()
        
        self.btn_start = QPushButton('Start', self)
        self.btn_start.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.btn_start.clicked.connect(self.start_trading)
        
        self.btn_stop = QPushButton('Emergency Stop', self)
        self.btn_stop.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.btn_stop.clicked.connect(self.emergency_stop)
        
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_stop)
        control_group.setLayout(control_layout)
        
        # 3. Manual Trading Group
        manual_group = QGroupBox("Manual Intervention")
        manual_layout = QHBoxLayout()
        
        self.btn_buy = QPushButton('BUY', self)
        self.btn_buy.setStyleSheet("background-color: #2196F3; color: white;")
        self.btn_buy.clicked.connect(self.manual_buy)
        
        self.btn_sell = QPushButton('SELL', self)
        self.btn_sell.setStyleSheet("background-color: #FF9800; color: white;")
        self.btn_sell.clicked.connect(self.manual_sell)
        
        manual_layout.addWidget(self.btn_buy)
        manual_layout.addWidget(self.btn_sell)
        manual_group.setLayout(manual_layout)
        
        # 4. Parameters Group
        param_group = QGroupBox("Parameters")
        param_layout = QVBoxLayout()
        
        # Capital Input
        capital_layout = QHBoxLayout()
        capital_layout.addWidget(QLabel('Capital:'))
        self.capital_input = QSpinBox(self)
        self.capital_input.setRange(1000, 10000000)
        self.capital_input.setValue(10000)
        self.capital_input.setPrefix('₹ ')
        capital_layout.addWidget(self.capital_input)
        
        # Risk Selection
        risk_layout = QHBoxLayout()
        risk_layout.addWidget(QLabel('Risk:'))
        self.risk_select = QComboBox(self)
        self.risk_select.addItems(['Conservative (0.5%)', 'Moderate (1%)', 'Aggressive (2%)'])
        risk_layout.addWidget(self.risk_select)
        
        # Backtest Period
        self.period_layout = QHBoxLayout()
        self.period_layout.addWidget(QLabel('Period:'))
        self.period_start = QComboBox(self)
        self.period_start.addItems([str(year) for year in range(2010, 2025)])
        self.period_start.setCurrentText('2021')
        self.period_layout.addWidget(self.period_start)
        
        self.period_layout.addWidget(QLabel('to'))
        self.period_end = QComboBox(self)
        self.period_end.addItems([str(year) for year in range(2010, 2025)])
        self.period_end.setCurrentText('2023')
        self.period_layout.addWidget(self.period_end)
        
        param_layout.addLayout(capital_layout)
        param_layout.addLayout(risk_layout)
        param_layout.addLayout(self.period_layout)
        param_group.setLayout(param_layout)
        
        # 5. Status Display
        self.status_display = QTextEdit(self)
        self.status_display.setReadOnly(True)
        self.status_display.setFont(QFont("Courier New", 10))
        
        # Assemble Main Layout
        main_layout.addWidget(mode_group)
        main_layout.addWidget(control_group)
        main_layout.addWidget(manual_group)
        main_layout.addWidget(param_group)
        main_layout.addWidget(QLabel('System Log:'))
        main_layout.addWidget(self.status_display)
        
        central.setLayout(main_layout)
        
        # Initialize UI State
        self.update_ui_for_mode()
        
    def update_ui_for_mode(self):
        """Enable/disable controls based on mode"""
        is_backtest = self.mode == "BACKTEST"
        
        # Show/hide backtest period controls
        self.period_start.setVisible(is_backtest)
        self.period_end.setVisible(is_backtest)
        self.findChild(QLabel, 'Period:').setVisible(is_backtest)
        self.findChild(QLabel, 'to').setVisible(is_backtest)
        
        # Update button states
        self.btn_paper.setChecked(self.mode == "PAPER")
        self.btn_backtest.setChecked(self.mode == "BACKTEST")
        self.btn_live.setChecked(self.mode == "LIVE")
        
        # Color indicators
        self.btn_paper.setStyleSheet("" if self.mode != "PAPER" else "background-color: #607D8B; color: white;")
        self.btn_backtest.setStyleSheet("" if self.mode != "BACKTEST" else "background-color: #607D8B; color: white;")
        self.btn_live.setStyleSheet("" if self.mode != "LIVE" else "background-color: #607D8B; color: white;")
        
    def set_mode(self, mode):
        self.mode = mode
        self.status_display.append(f"Mode changed to {mode}")
        self.update_ui_for_mode()
        
    def start_trading(self):
        capital = self.capital_input.value()
        risk_map = {'Conservative (0.5%)': 0.005, 'Moderate (1%)': 0.01, 'Aggressive (2%)': 0.02}
        risk = risk_map[self.risk_select.currentText()]
        
        if self.mode == "BACKTEST":
            start_year = int(self.period_start.currentText())
            end_year = int(self.period_end.currentText())
            self.status_display.append(f"Starting BACKTEST with ₹{capital:,} from {start_year}-{end_year}")
            self._run_in_thread(lambda: self.run_backtest(start_year, end_year, capital, risk))
        elif self.mode == "PAPER":
            self.status_display.append(f"Starting PAPER TRADING with ₹{capital:,}")
            self._run_in_thread(lambda: self.run_paper_trading(capital, risk))
        else:  # LIVE
            self.status_display.append(f"Starting LIVE TRADING with ₹{capital:,}")
            self._run_in_thread(lambda: self.run_live_trading(capital, risk))
            
    def run_backtest(self, start_year, end_year, capital, risk):
        # Initialize backtest trader
        self.trader = NanoOptimizedTrader(initial_capital=capital)
        self.trader.params['max_risk'] = risk
        self.trader.backtest(
            start_date=f"{start_year}-01-01",
            end_date=f"{end_year}-12-31"
        )
        
    def run_paper_trading(self, capital, risk):
        # Initialize paper trader
        self.trader = NanoOptimizedTrader(initial_capital=capital)
        self.trader.params['max_risk'] = risk
        self.trader.run(mode="PAPER")
        
    def run_live_trading(self, capital, risk):
        # Initialize live trader
        self.trader = NanoOptimizedTrader(initial_capital=capital)
        self.trader.params['max_risk'] = risk
        self.trader.run(mode="LIVE")
        
    def emergency_stop(self):
        if self.trader:
            self.trader.emergency_shutdown()
            self.status_display.append("!!! EMERGENCY STOP ACTIVATED !!!")
            
    def manual_buy(self):
        symbol, ok = QInputDialog.getText(self, 'Manual Buy', 'Enter Symbol:')
        if ok and symbol:
            self.status_display.append(f"Manual BUY: {symbol}")
            if self.trader:
                self._run_in_thread(lambda: self.trader.execute_order(symbol, 'BUY'))
                
    def manual_sell(self):
        symbol, ok = QInputDialog.getText(self, 'Manual Sell', 'Enter Symbol:')
        if ok and symbol:
            self.status_display.append(f"Manual SELL: {symbol}")
            if self.trader:
                self._run_in_thread(lambda: self.trader.execute_order(symbol, 'SELL'))
                
    def _run_in_thread(self, func):
        """Run trading functions in background thread"""
        thread = threading.Thread(target=func)
        thread.daemon = True
        thread.start()

def create_executable():
    """Build standalone executable"""
    from PyInstaller.__main__ import run
    opts = [
        '--onefile',
        '--windowed',
        '--name=QuantumTraderPro',
        '--icon=trading_icon.ico',
        '--add-data=trading_icon.ico;.',
        'trading_app.py'
    ]
    run(opts)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    ex = TradingApp()
    ex.show()
    
    # Uncomment to build executable
    # create_executable()
    
    sys.exit(app.exec_())