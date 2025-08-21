import sys
import math
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, 
                             QPushButton, QGroupBox, QGridLayout, QTextEdit,
                             QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QFontDatabase

class ModernMinesCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        # Remove window title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 620, 750)
        
        # Load modern font
        self.setup_fonts()
        
        # Set application style with modern dark theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #0d1117;
                border: 1px solid #21262d;
                border-radius: 12px;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid #21262d;
                border-radius: 10px;
                margin-top: 1ex;
                padding: 15px;
                background-color: #161b22;
                color: #e6edf3;
                font-family: '{self.font_family}';
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #58a6ff;
                font-size: 14px;
                font-family: '{self.font_family}';
            }}
            QLabel {{
                color: #e6edf3;
                padding: 6px;
                font-size: 13px;
                font-family: '{self.font_family}';
            }}
            QSpinBox, QDoubleSpinBox {{
                padding: 10px;
                border: 1px solid #30363d;
                border-radius: 6px;
                background-color: #0d1117;
                color: #e6edf3;
                selection-background-color: #58a6ff;
                font-size: 13px;
                font-family: '{self.font_family}';
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid #58a6ff;
            }}
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                width: 0px;
            }}
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                width: 0px;
            }}
            QPushButton {{
                background-color: #238636;
                color: #ffffff;
                border: none;
                padding: 12px;
                font-weight: bold;
                border-radius: 6px;
                font-size: 14px;
                font-family: '{self.font_family}';
            }}
            QPushButton:hover {{
                background-color: #2ea043;
            }}
            QPushButton:pressed {{
                background-color: #196c2e;
            }}
            QPushButton#closeButton {{
                background-color: #da3633;
            }}
            QPushButton#closeButton:hover {{
                background-color: #f85149;
            }}
            QPushButton#closeButton:pressed {{
                background-color: #b62324;
            }}
            QTextEdit {{
                background-color: #161b22;
                border: 1px solid #21262d;
                border-radius: 8px;
                color: #e6edf3;
                padding: 12px;
                font-size: 13px;
                font-family: '{self.font_family}';
            }}
            QTextEdit QScrollBar:vertical {{
                border: none;
                background: #161b22;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QTextEdit QScrollBar::handle:vertical {{
                background: #58a6ff;
                min-height: 20px;
                border-radius: 5px;
            }}
            QTextEdit QScrollBar::handle:vertical:hover {{
                background: #79c0ff;
            }}
            QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QTextEdit QScrollBar::add-page:vertical, QTextEdit QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QFrame#separator {{
                background-color: #21262d;
                max-height: 1px;
                min-height: 1px;
                border-radius: 1px;
            }}
        """)
        
        self.initUI()
        
    def setup_fonts(self):
        # Try to load a modern font, fall back to default if not available
        self.font_family = "Segoe UI"
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Stake Mines Calculator")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont(self.font_family, 18, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #58a6ff; padding: 10px; margin-bottom: 5px;")
        layout.addWidget(title)
        
        # Input section - Using GridLayout instead of FormLayout
        input_group = QGroupBox("Game Parameters")
        input_layout = QGridLayout()
        input_layout.setHorizontalSpacing(15)
        input_layout.setVerticalSpacing(12)
        input_layout.setContentsMargins(15, 20, 15, 15)
        
        # Create labels and inputs
        mines_label = QLabel("Number of Mines (1-24):")
        mines_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.mines_input = QSpinBox()
        self.mines_input.setRange(1, 24)
        self.mines_input.setValue(5)
        self.mines_input.valueChanged.connect(self.calculate)
        
        bet_label = QLabel("Bet Amount:")
        bet_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.bet_input = QDoubleSpinBox()
        self.bet_input.setRange(0.01, 1000000)
        self.bet_input.setValue(1.0)
        self.bet_input.setDecimals(8)
        self.bet_input.valueChanged.connect(self.calculate)
        
        clicks_label = QLabel("Number of Clicks (1-25):")
        clicks_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.clicks_input = QSpinBox()
        self.clicks_input.setRange(1, 25)
        self.clicks_input.setValue(3)
        self.clicks_input.valueChanged.connect(self.calculate)
        
        # Add to grid layout
        input_layout.addWidget(mines_label, 0, 0)
        input_layout.addWidget(self.mines_input, 0, 1)
        input_layout.addWidget(bet_label, 1, 0)
        input_layout.addWidget(self.bet_input, 1, 1)
        input_layout.addWidget(clicks_label, 2, 0)
        input_layout.addWidget(self.clicks_input, 2, 1)
        
        # Set column stretch to ensure proper alignment
        input_layout.setColumnStretch(0, 1)
        input_layout.setColumnStretch(1, 2)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("separator")
        layout.addWidget(separator)
        
        # Results section
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(10, 20, 10, 15)
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setMinimumHeight(280)
        results_layout.addWidget(self.results_display)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Calculate button
        self.calculate_btn = QPushButton("Calculate")
        self.calculate_btn.clicked.connect(self.calculate)
        buttons_layout.addWidget(self.calculate_btn)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Perform initial calculation
        self.calculate()
        
    def calculate_probability(self, total_mines, clicks):
        """Calculate the probability of successfully clicking all safe spots"""
        if clicks == 0:
            return 1.0
        
        safe_spots = 25 - total_mines
        if clicks > safe_spots:
            return 0.0
        
        probability = 1.0
        for i in range(clicks):
            probability *= (safe_spots - i) / (25 - i)
        
        return probability
    
    def calculate_payout(self, total_mines, clicks):
        """Calculate the payout multiplier for successfully clicking all safe spots"""
        if clicks == 0:
            return 1.0
        
        safe_spots = 25 - total_mines
        if clicks > safe_spots:
            return 0.0
        
        # The payout is based on the probability
        probability = self.calculate_probability(total_mines, clicks)
        
        # Add a small house edge (approximately 1%)
        return (1 / probability) * 0.99
    
    def calculate_winning(self, total_mines, clicks, bet_amount):
        """Calculate the potential winning amount"""
        payout = self.calculate_payout(total_mines, clicks)
        return bet_amount * payout
    
    def calculate(self):
        """Perform the calculation and update the results display"""
        try:
            total_mines = self.mines_input.value()
            bet_amount = self.bet_input.value()
            clicks = self.clicks_input.value()
            
            safe_spots = 25 - total_mines
            if clicks > safe_spots:
                self.results_display.setHtml(f"""
                <div style='color: #f85149; font-weight: bold; font-size: 13px; font-family: {self.font_family};'>
                    Error: You can't make {clicks} clicks with only {safe_spots} safe spots!
                </div>
                """)
                return
            
            probability = self.calculate_probability(total_mines, clicks)
            payout = self.calculate_payout(total_mines, clicks)
            potential_win = self.calculate_winning(total_mines, clicks, bet_amount)
            
            # Format the results with HTML for better presentation
            result_html = f"""
            <div style='font-size: 13px; font-family: {self.font_family};'>
                <table width='100%' cellspacing='8' cellpadding='8' style='border-collapse: separate; border-spacing: 0 8px;'>
                    <tr>
                        <td width='65%' style='padding: 8px;'><b>Number of mines:</b></td>
                        <td width='35%' style='padding: 8px; text-align: right;'>{total_mines}</td>
                    </tr>
                    <tr>
                        <td style='padding: 8px;'><b>Number of safe spots:</b></td>
                        <td style='padding: 8px; text-align: right;'>{safe_spots}</td>
                    </tr>
                    <tr>
                        <td style='padding: 8px;'><b>Number of clicks:</b></td>
                        <td style='padding: 8px; text-align: right;'>{clicks}</td>
                    </tr>
                    <tr>
                        <td style='padding: 8px;'><b>Probability of success:</b></td>
                        <td style='padding: 8px; text-align: right;'>{probability*100:.6f}%</td>
                    </tr>
                    <tr>
                        <td style='padding: 8px;'><b>Payout multiplier:</b></td>
                        <td style='padding: 8px; text-align: right;'>{payout:.6f}x</td>
                    </tr>
                    <tr>
                        <td style='padding: 8px;'><b>Bet amount:</b></td>
                        <td style='padding: 8px; text-align: right;'>{bet_amount:.8f}</td>
                    </tr>
                    <tr>
                        <td style='padding: 8px;'><b>Potential winning:</b></td>
                        <td style='padding: 8px; text-align: right;'><span style='color: #3fb950; font-weight: bold;'>{potential_win:.8f}</span></td>
                    </tr>
                </table>
            </div>
            """
            
            # Add probability breakdown for each click
            if clicks > 1:
                result_html += """
                <br>
                <div style='font-size: 12px; font-family: """ + self.font_family + """;'>
                    <table width='100%' cellspacing='5' cellpadding='5' style='border-collapse: collapse;'>
                        <tr style='background-color: #21262d; color: #58a6ff;'>
                            <th align='center' style='padding: 8px; border-bottom: 1px solid #30363d;'>Click#</th>
                            <th align='center' style='padding: 8px; border-bottom: 1px solid #30363d;'>Probability</th>
                            <th align='center' style='padding: 8px; border-bottom: 1px solid #30363d;'>Cumulative</th>
                        </tr>
                """
                
                cumulative_prob = 1.0
                for i in range(1, clicks + 1):
                    prob_this_click = (safe_spots - i + 1) / (25 - i + 1)
                    cumulative_prob *= prob_this_click
                    
                    # Color code based on probability
                    if prob_this_click < 0.5:
                        color = "#f85149"  # Red for low probability
                    elif prob_this_click > 0.8:
                        color = "#3fb950"  # Green for high probability
                    else:
                        color = "#d29922"  # Yellow for medium probability
                    
                    row_bg = "#161b22" if i % 2 == 1 else "#0d1117"
                    
                    result_html += f"""
                    <tr style='background-color: {row_bg};'>
                        <td align='center' style='padding: 7px;'>{i}</td>
                        <td align='center' style='padding: 7px;'><span style='color: {color}; font-weight: bold;'>{prob_this_click*100:.2f}%</span></td>
                        <td align='center' style='padding: 7px;'>{cumulative_prob*100:.4f}%</td>
                    </tr>
                    """
                
                result_html += "</table></div>"
            
            self.results_display.setHtml(result_html)
            
        except Exception as e:
            self.results_display.setHtml(f"""
            <div style='color: #f85149; font-weight: bold; font-size: 13px; font-family: {self.font_family};'>
                Error: {str(e)}
            </div>
            """)
            
    def mousePressEvent(self, event):
        # Allow dragging the frameless window
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        # Handle window dragging
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create a dark palette (GitHub Dark theme inspired)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(13, 17, 23))
    palette.setColor(QPalette.WindowText, QColor(230, 237, 243))
    palette.setColor(QPalette.Base, QColor(22, 27, 34))
    palette.setColor(QPalette.AlternateBase, QColor(13, 17, 23))
    palette.setColor(QPalette.ToolTipBase, QColor(88, 166, 255))
    palette.setColor(QPalette.ToolTipText, QColor(230, 237, 243))
    palette.setColor(QPalette.Text, QColor(230, 237, 243))
    palette.setColor(QPalette.Button, QColor(33, 38, 45))
    palette.setColor(QPalette.ButtonText, QColor(230, 237, 243))
    palette.setColor(QPalette.BrightText, QColor(248, 81, 73))
    palette.setColor(QPalette.Link, QColor(88, 166, 255))
    palette.setColor(QPalette.Highlight, QColor(35, 134, 54))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Create and show the calculator
    calculator = ModernMinesCalculator()
    calculator.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()