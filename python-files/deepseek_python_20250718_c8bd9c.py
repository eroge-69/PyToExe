import sys
import numpy as np
import matplotlib.pyplot as plt
from sympy import symbols, simplify, Poly
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QComboBox, QFileDialog)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import requests
from bs4 import BeautifulSoup

class PolynomialTab(QWidget):
    def __init__(self):
        super().__init__()
        # GUI elements
        self.equation_input = QLineEdit("x**2 - 4")
        self.calculate_btn = QPushButton("Анализировать")
        self.result_display = QTextEdit()
        self.plot_btn = QPushButton("Построить график")
        self.analysis_type = QComboBox()
        self.analysis_type.addItems(["Корни", "Факторизация", "Производная", "Интеграл"])
        
        # Layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Уравнение:"))
        input_layout.addWidget(self.equation_input)
        input_layout.addWidget(self.analysis_type)
        input_layout.addWidget(self.calculate_btn)
        input_layout.addWidget(self.plot_btn)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.result_display)
        self.setLayout(main_layout)
        
        # Signals
        self.calculate_btn.clicked.connect(self.analyze)
        self.plot_btn.clicked.connect(self.plot)

    def analyze(self):
        try:
            x = symbols('x')
            expr = simplify(self.equation_input.text())
            analysis = self.analysis_type.currentText()
            
            if analysis == "Корни":
                result = f"Корни: {Poly(expr).all_roots()}"
            elif analysis == "Факторизация":
                result = f"Факторы: {expr.factor()}"
            elif analysis == "Производная":
                result = f"Производная: {expr.diff(x)}"
            elif analysis == "Интеграл":
                result = f"Интеграл: {expr.integrate(x)}"
                
            self.result_display.setText(result)
        except Exception as e:
            self.result_display.setText(f"Ошибка: {str(e)}")

    def plot(self):
        try:
            x = symbols('x')
            expr = simplify(self.equation_input.text())
            f = lambda val: expr.subs(x, val)
            
            x_vals = np.linspace(-10, 10, 400)
            y_vals = [f(x_val) for x_val in x_vals]
            
            plt.figure()
            plt.plot(x_vals, y_vals)
            plt.title(f"График: {expr}")
            plt.grid(True)
            plt.savefig("polynomial_plot.png")
            plt.show()
        except Exception as e:
            self.result_display.setText(f"Ошибка построения: {str(e)}")

class OSINTTab(QWidget):
    def __init__(self):
        super().__init__()
        # GUI elements
        self.url_input = QLineEdit("https://example.com")
        self.fetch_btn = QPushButton("Получить данные")
        self.analyze_btn = QPushButton("Анализировать")
        self.result_display = QTextEdit()
        self.browser = QWebEngineView()
        
        # Layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("URL:"))
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.fetch_btn)
        input_layout.addWidget(self.analyze_btn)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.browser, 40)
        main_layout.addWidget(self.result_display, 60)
        self.setLayout(main_layout)
        
        # Signals
        self.fetch_btn.clicked.connect(self.load_url)
        self.analyze_btn.clicked.connect(self.analyze_content)

    def load_url(self):
        url = self.url_input.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.browser.load(QUrl(url))

    def analyze_content(self):
        try:
            url = self.url_input.text()
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Military-relevant analysis
            text_content = soup.get_text()
            keywords = ["воен", "атака", "оборон", "конфликт"]
            found = [kw for kw in keywords if kw in text_content]
            
            report = f"""
            Анализ сайта {url}:
            - Заголовок: {soup.title.string if soup.title else 'N/A'}
            - Ключевые слова: {', '.join(found) if found else 'не обнаружены'}
            - Количество ссылок: {len(soup.find_all('a'))}
            - Количество изображений: {len(soup.find_all('img'))}
            """
            self.result_display.setText(report)
        except Exception as e:
            self.result_display.setText(f"Ошибка анализа: {str(e)}")

class TitanOSApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TitanOS Community Edition")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(PolynomialTab(), "Анализ полиномов")
        self.tabs.addTab(OSINTTab(), "Военный OSINT")
        
        # Add export button
        self.export_btn = QPushButton("Экспорт результатов")
        self.export_btn.clicked.connect(self.export_results)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.export_btn)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def export_results(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчет", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    # Collect data from all tabs
                    content = "=== ОТЧЕТ TITANOS ===\n\n"
                    
                    # Polynomial analysis
                    poly_tab = self.tabs.widget(0)
                    content += f"[МАТЕМАТИЧЕСКИЙ АНАЛИЗ]\n"
                    content += f"Уравнение: {poly_tab.equation_input.text()}\n"
                    content += f"Результат: {poly_tab.result_display.toPlainText()}\n\n"
                    
                    # OSINT analysis
                    osint_tab = self.tabs.widget(1)
                    content += f"[ВОЕННЫЙ OSINT]\n"
                    content += f"Анализируемый сайт: {osint_tab.url_input.text()}\n"
                    content += f"Отчет:\n{osint_tab.result_display.toPlainText()}"
                
                f.write(content)
            except Exception as e:
                print(f"Export error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TitanOSApp()
    window.show()
    sys.exit(app.exec())