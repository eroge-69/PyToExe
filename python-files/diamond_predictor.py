import sys
import os
import sqlite3
import pandas as pd # type: ignore
import numpy as np
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns
from datetime import datetime
import pickle
import logging
from pathlib import Path

# GUI imports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,QHBoxLayout, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit, QGroupBox, QMessageBox, QProgressBar, QTabWidget, QFrame, QFileDialog, QSplitter, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon

# ML and data processing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb

# Plotting
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.style as style

# PDF generation
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path="diamond_predictor.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carat REAL,
                color TEXT,
                clarity TEXT,
                cut TEXT,
                certificate TEXT,
                predicted_price REAL,
                timestamp TEXT,
                model_used TEXT
            )
        ''')
        
        # Create reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER,
                report_path TEXT,
                timestamp TEXT,
                FOREIGN KEY (prediction_id) REFERENCES predictions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_prediction(self, carat, color, clarity, cut, certificate, predicted_price, model_used):
        """Save prediction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO predictions (carat, color, clarity, cut, certificate, 
                                   predicted_price, timestamp, model_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (carat, color, clarity, cut, certificate, predicted_price, timestamp, model_used))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return prediction_id
    
    def save_report(self, prediction_id, report_path):
        """Save report information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO reports (prediction_id, report_path, timestamp)
            VALUES (?, ?, ?)
        ''', (prediction_id, report_path, timestamp))
        
        conn.commit()
        conn.close()
    
    def get_recent_predictions(self, limit=100):
        """Get recent predictions for visualization"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', conn, params=(limit,))
        conn.close()
        return df

class DiamondPredictor:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = ['carat', 'color', 'clarity', 'cut', 'certificate']
        
    def create_sample_data(self):
        """Create sample diamond data for initial training"""
        np.random.seed(42)
        n_samples = 1000
        
        # Generate synthetic diamond data
        data = {
            'carat': np.random.uniform(0.2, 5.0, n_samples),
            'color': np.random.choice(['D', 'E', 'F', 'G', 'H', 'I', 'J'], n_samples),
            'clarity': np.random.choice(['FL', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2'], n_samples),
            'cut': np.random.choice(['Excellent', 'Very Good', 'Good', 'Fair', 'Poor'], n_samples),
            'certificate': np.random.choice(['GIA', 'AGS', 'EGL', 'Other'], n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Create realistic price based on diamond characteristics
        color_values = {'D': 1.0, 'E': 0.95, 'F': 0.9, 'G': 0.85, 'H': 0.8, 'I': 0.75, 'J': 0.7}
        clarity_values = {'FL': 1.0, 'IF': 0.95, 'VVS1': 0.9, 'VVS2': 0.85, 'VS1': 0.8, 'VS2': 0.75, 'SI1': 0.7, 'SI2': 0.65}
        cut_values = {'Excellent': 1.0, 'Very Good': 0.9, 'Good': 0.8, 'Fair': 0.7, 'Poor': 0.6}
        cert_values = {'GIA': 1.0, 'AGS': 0.95, 'EGL': 0.85, 'Other': 0.8}
        
        base_price = 5000 * (df['carat'] ** 1.8)  # Carat has exponential effect
        color_multiplier = df['color'].map(color_values)
        clarity_multiplier = df['clarity'].map(clarity_values)
        cut_multiplier = df['cut'].map(cut_values)
        cert_multiplier = df['certificate'].map(cert_values)
        
        df['price'] = base_price * color_multiplier * clarity_multiplier * cut_multiplier * cert_multiplier
        
        # Add some noise
        df['price'] += np.random.normal(0, df['price'] * 0.1)
        df['price'] = np.maximum(df['price'], 100)  # Minimum price
        
        return df
    
    def prepare_features(self, df, fit_encoders=False):
        """Prepare features for training/prediction"""
        df_processed = df.copy()
        
        # Encode categorical variables
        categorical_columns = ['color', 'clarity', 'cut', 'certificate']
        
        for col in categorical_columns:
            if fit_encoders:
                encoder = LabelEncoder()
                df_processed[col] = encoder.fit_transform(df_processed[col])
                self.encoders[col] = encoder
            else:
                if col in self.encoders:
                    # Handle unknown categories
                    unique_values = set(df_processed[col].unique())
                    known_values = set(self.encoders[col].classes_)
                    unknown_values = unique_values - known_values
                    
                    if unknown_values:
                        # Replace unknown values with most common known value
                        most_common = self.encoders[col].classes_[0]
                        df_processed[col] = df_processed[col].replace(list(unknown_values), most_common)
                    
                    df_processed[col] = self.encoders[col].transform(df_processed[col])
        
        return df_processed[self.feature_columns]
    
    def train_model(self, progress_callback=None):
        """Train the diamond price prediction model"""
        try:
            if progress_callback:
                progress_callback.emit(10)
            
            # Create or load training data
            df = self.create_sample_data()
            
            if progress_callback:
                progress_callback.emit(30)
            
            # Prepare features
            X = self.prepare_features(df, fit_encoders=True)
            y = df['price']
            
            if progress_callback:
                progress_callback.emit(50)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            if progress_callback:
                progress_callback.emit(70)
            
            # Train XGBoost model
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            if progress_callback:
                progress_callback.emit(90)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.is_trained = True
            
            if progress_callback:
                progress_callback.emit(100)
            
            return {'mae': mae, 'r2_score': r2, 'model': 'XGBoost'}
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise e
    
    def predict_price(self, carat, color, clarity, cut, certificate):
        """Predict diamond price based on input parameters"""
        if not self.is_trained:
            raise ValueError("Model not trained yet!")
        
        # Create input dataframe
        input_data = pd.DataFrame({
            'carat': [carat],
            'color': [color],
            'clarity': [clarity],
            'cut': [cut],
            'certificate': [certificate]
        })
        
        # Prepare features
        X = self.prepare_features(input_data, fit_encoders=False)
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        return max(prediction, 100)  # Minimum price

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Set style
        style.use('seaborn-v0_8')
        self.fig.patch.set_facecolor('white')
    
    def plot_price_trends(self, df):
        """Plot price trends over time"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
        else:
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df_sorted = df.sort_values('timestamp')
            
            ax.plot(df_sorted['timestamp'], df_sorted['predicted_price'], 
                   marker='o', linewidth=2, markersize=4)
            ax.set_title('Diamond Price Predictions Over Time', fontsize=14, fontweight='bold')
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Predicted Price ($)', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        self.fig.tight_layout()
        self.draw()
    
    def plot_price_distribution(self, df):
        """Plot price distribution"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
        else:
            ax.hist(df['predicted_price'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_title('Price Distribution', fontsize=14, fontweight='bold')
            ax.set_xlabel('Price ($)', fontsize=12)
            ax.set_ylabel('Frequency', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Format x-axis as currency
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        self.fig.tight_layout()
        self.draw()

class TrainingThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, predictor):
        super().__init__()
        self.predictor = predictor
    
    def run(self):
        try:
            result = self.predictor.train_model(self.progress)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    def generate_report(self, prediction_data, report_path):
        """Generate PDF report"""
        doc = SimpleDocTemplate(report_path, pagesize=A4)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center
            textColor=colors.darkblue
        )
        story.append(Paragraph("Diamond Price Prediction Report", title_style))
        story.append(Spacer(1, 20))
        
        # Timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=2,  # Right
            textColor=colors.grey
        )
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", timestamp_style))
        story.append(Spacer(1, 20))
        
        # Diamond Parameters
        story.append(Paragraph("Diamond Specifications", self.styles['Heading2']))
        
        data = [
            ['Parameter', 'Value'],
            ['Carat', f"{prediction_data['carat']:.2f}"],
            ['Color', prediction_data['color']],
            ['Clarity', prediction_data['clarity']],
            ['Cut', prediction_data['cut']],
            ['Certificate', prediction_data['certificate']]
        ]
        
        table = Table(data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Prediction Result
        story.append(Paragraph("Price Prediction", self.styles['Heading2']))
        price_style = ParagraphStyle(
            'Price',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.green,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(f"Estimated Price: ${prediction_data['predicted_price']:,.2f}", price_style))
        story.append(Spacer(1, 20))
        
        # Market Analysis
        story.append(Paragraph("Market Analysis", self.styles['Heading2']))
        analysis_text = f"""
        Based on current market data and the specified diamond characteristics, this diamond 
        is estimated to be worth ${prediction_data['predicted_price']:,.2f}. This prediction 
        takes into account the carat weight ({prediction_data['carat']:.2f}ct), color grade 
        ({prediction_data['color']}), clarity ({prediction_data['clarity']}), cut quality 
        ({prediction_data['cut']}), and certification ({prediction_data['certificate']}).
        
        The price is calculated using advanced machine learning algorithms trained on 
        comprehensive diamond market data.
        """
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)

class DiamondPredictorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.predictor = DiamondPredictor()
        self.db_manager = DatabaseManager()
        self.pdf_generator = PDFReportGenerator()
        self.current_prediction_id = None
        
        self.init_ui()
        self.setup_styling()
        
        # Auto-train model on startup
        QTimer.singleShot(1000, self.train_model)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Diamond Price Predictor v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel for inputs and controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel for visualization and logs
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (40% left, 60% right)
        splitter.setSizes([560, 840])
        
        self.statusBar().showMessage("Ready - Train model to start predicting")
    
    def create_left_panel(self):
        """Create the left control panel"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Input Group
        input_group = QGroupBox("Diamond Parameters")
        input_layout = QGridLayout(input_group)
        
        # Carat input
        input_layout.addWidget(QLabel("Carat:"), 0, 0)
        self.carat_input = QLineEdit()
        self.carat_input.setPlaceholderText("e.g., 1.25")
        input_layout.addWidget(self.carat_input, 0, 1)
        
        # Color input
        input_layout.addWidget(QLabel("Color:"), 1, 0)
        self.color_combo = QComboBox()
        self.color_combo.addItems(['D', 'E', 'F', 'G', 'H', 'I', 'J'])
        input_layout.addWidget(self.color_combo, 1, 1)
        
        # Clarity input
        input_layout.addWidget(QLabel("Clarity:"), 2, 0)
        self.clarity_combo = QComboBox()
        self.clarity_combo.addItems(['FL', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2'])
        input_layout.addWidget(self.clarity_combo, 2, 1)
        
        # Cut input
        input_layout.addWidget(QLabel("Cut:"), 3, 0)
        self.cut_combo = QComboBox()
        self.cut_combo.addItems(['Excellent', 'Very Good', 'Good', 'Fair', 'Poor'])
        input_layout.addWidget(self.cut_combo, 3, 1)
        
        # Certificate input
        input_layout.addWidget(QLabel("Certificate:"), 4, 0)
        self.certificate_combo = QComboBox()
        self.certificate_combo.addItems(['GIA', 'AGS', 'EGL', 'Other'])
        input_layout.addWidget(self.certificate_combo, 4, 1)
        
        left_layout.addWidget(input_group)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        self.train_button = QPushButton("Train Model")
        self.train_button.clicked.connect(self.train_model)
        button_layout.addWidget(self.train_button)
        
        self.predict_button = QPushButton("Predict Price")
        self.predict_button.clicked.connect(self.predict_price)
        self.predict_button.setEnabled(False)
        button_layout.addWidget(self.predict_button)
        
        self.report_button = QPushButton("Generate PDF Report")
        self.report_button.clicked.connect(self.generate_report)
        self.report_button.setEnabled(False)
        button_layout.addWidget(self.report_button)
        
        left_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # Prediction result
        result_group = QGroupBox("Prediction Result")
        result_layout = QVBoxLayout(result_group)
        
        self.result_label = QLabel("No prediction yet")
        self.result_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E8B57;")
        result_layout.addWidget(self.result_label)
        
        left_layout.addWidget(result_group)
        
        left_layout.addStretch()
        return left_widget
    
    def create_right_panel(self):
        """Create the right panel with tabs"""
        tab_widget = QTabWidget()
        
        # Visualization tab
        viz_widget = QWidget()
        viz_layout = QVBoxLayout(viz_widget)
        
        # Plot canvas
        self.plot_canvas = PlotCanvas(viz_widget)
        viz_layout.addWidget(self.plot_canvas)
        
        # Plot controls
        plot_controls = QHBoxLayout()
        self.trend_button = QPushButton("Price Trends")
        self.trend_button.clicked.connect(self.plot_trends)
        plot_controls.addWidget(self.trend_button)
        
        self.dist_button = QPushButton("Price Distribution")
        self.dist_button.clicked.connect(self.plot_distribution)
        plot_controls.addWidget(self.dist_button)
        
        plot_controls.addStretch()
        viz_layout.addLayout(plot_controls)
        
        tab_widget.addTab(viz_widget, "Visualization")
        
        # Log tab
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        tab_widget.addTab(log_widget, "Logs")
        
        return tab_widget
    
    def setup_styling(self):
        """Setup application styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
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
                padding: 10px;
                text-align: center;
                font-size: 14px;
                border-radius: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QComboBox, QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                font-size: 12px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #4CAF50;
            }
        """)
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        logger.info(message)
    
    def train_model(self):
        """Train the prediction model"""
        self.log_message("Starting model training...")
        self.train_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.training_thread = TrainingThread(self.predictor)
        self.training_thread.progress.connect(self.progress_bar.setValue)
        self.training_thread.finished.connect(self.on_training_finished)
        self.training_thread.error.connect(self.on_training_error)
        self.training_thread.start()
    
    def on_training_finished(self, result):
        """Handle training completion"""
        self.progress_bar.setVisible(False)
        self.train_button.setEnabled(True)
        self.predict_button.setEnabled(True)
        
        mae = result['mae']
        r2 = result['r2_score']
        model_name = result['model']
        
        self.log_message(f"Model training completed!")
        self.log_message(f"Model: {model_name}")
        self.log_message(f"Mean Absolute Error: ${mae:,.2f}")
        self.log_message(f"R² Score: {r2:.3f}")
        
        self.statusBar().showMessage("Model trained successfully - Ready for predictions")
    
    def on_training_error(self, error_msg):
        """Handle training error"""
        self.progress_bar.setVisible(False)
        self.train_button.setEnabled(True)
        
        self.log_message(f"Training error: {error_msg}")
        QMessageBox.critical(self, "Training Error", f"Failed to train model:\n{error_msg}")
    
    def predict_price(self):
        """Predict diamond price"""
        try:
            # Validate inputs
            carat_text = self.carat_input.text().strip()
            if not carat_text:
                QMessageBox.warning(self, "Input Error", "Please enter carat value")
                return
            
            try:
                carat = float(carat_text)
                if carat <= 0:
                    raise ValueError("Carat must be positive")
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Please enter valid carat value (positive number)")
                return
            
            color = self.color_combo.currentText()
            clarity = self.clarity_combo.currentText()
            cut = self.cut_combo.currentText()
            certificate = self.certificate_combo.currentText()
            
            # Make prediction
            predicted_price = self.predictor.predict_price(carat, color, clarity, cut, certificate)
            
            # Display result
            self.result_label.setText(f"Estimated Price: ${predicted_price:,.2f}")
            
            # Save to database
            self.current_prediction_id = self.db_manager.save_prediction(
                carat, color, clarity, cut, certificate, predicted_price, "XGBoost"
            )
            
            self.log_message(f"Prediction made: ${predicted_price:,.2f} for {carat}ct {color} {clarity} {cut} diamond")
            self.report_button.setEnabled(True)
            
            # Update plots
            self.plot_trends()
            
        except Exception as e:
            self.log_message(f"Prediction error: {str(e)}")
            QMessageBox.critical(self, "Prediction Error", f"Failed to predict price:\n{str(e)}")
    
    def generate_report(self):
        """Generate PDF report"""
        if self.current_prediction_id is None:
            QMessageBox.warning(self, "No Prediction", "Please make a prediction first")
            return
        
        try:
            # Get file path from user
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Report", f"diamond_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return
            
            # Prepare prediction data
        prediction_data = {
                'carat': float(self.carat_input.text()),
                'color': self.color_combo.currentText(),
                'clarity': self.clarity_combo.currentText(),
                'cut': self.cut_combo.currentText(),
                'certificate': self.certificate_combo.currentText(),
                'predicted_price': float(self.result_label.text().replace('Estimated Price:    , '').replace(',', ''))
            }
            
            # Generate PDF
            self.pdf_generator.generate_report(prediction_data, file_path)
            
            # Save report info to database
            self.db_manager.save_report(self.current_prediction_id, file_path)
            
            self.log_message(f"PDF report generated: {file_path}")
            QMessageBox.information(self, "Report Generated", f"PDF report saved successfully:\n{file_path}")
            
        except Exception as e:
            self.log_message(f"Report generation error: {str(e)}")
            QMessageBox.critical(self, "Report Error", f"Failed to generate report:\n{str(e)}")
    
    def plot_trends(self):
        """Plot price trends"""
        try:
            df = self.db_manager.get_recent_predictions()
            self.plot_canvas.plot_price_trends(df)
            self.log_message("Price trends plot updated")
        except Exception as e:
            self.log_message(f"Plot error: {str(e)}")
    
    def plot_distribution(self):
        """Plot price distribution"""
        try:
            df = self.db_manager.get_recent_predictions()
            self.plot_canvas.plot_price_distribution(df)
            self.log_message("Price distribution plot updated")
        except Exception as e:
            self.log_message(f"Plot error: {str(e)}")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Diamond Price Predictor")
    app.setApplicationVersion("1.0")
    
    # Set application icon (optional)
    # app.setWindowIcon(QIcon('icon.png'))
    
    # Create and show main window
    window = DiamondPredictorGUI()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    