#!/usr/bin/env python3
"""
Main SDR Spectrum Analyzer Application
Comprehensive Windows application for telecommunications education and research
"""

import sys
import os
import time
import threading
import json
import numpy as np
from datetime import datetime
from typing import Optional, Dict, List

# PyQt5 imports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTabWidget, QMenuBar, QMenu, QAction,
                            QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox,
                            QDoubleSpinBox, QTextEdit, QTableWidget, QTableWidgetItem,
                            QGroupBox, QGridLayout, QSplitter, QProgressBar,
                            QStatusBar, QDialog, QDialogButtonBox, QFormLayout,
                            QCheckBox, QSlider, QFrame, QScrollArea, QListWidget,
                            QMessageBox, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QMutex
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

# Matplotlib for spectrum display
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

# Import our modules
from sdr_integration_enhanced import SDRController
from ai_protocol_identification import AIProtocolIdentifier
from protocol_decoders import ProtocolProcessor
from database_manager import DatabaseManager, MultiUserManager

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """User login dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SDR Spectrum Analyzer - Login")
        self.setFixedSize(300, 200)
        
        layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        
        layout.addRow("Username:", self.username_edit)
        layout.addRow("Password:", self.password_edit)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_credentials(self):
        return self.username_edit.text(), self.password_edit.text()


class SpectrumWidget(QWidget):
    """Spectrum display widget with waterfall"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Data
        self.frequencies = np.linspace(0, 6000, 1024)  # MHz
        self.power_spectrum = np.zeros(1024)
        self.waterfall_data = np.zeros((100, 1024))
        self.waterfall_row = 0
        
        # Colors
        self.spectrum_color = 'cyan'
        self.waterfall_colormap = 'viridis'
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        
        # Spectrum plot
        self.spectrum_ax = self.figure.add_subplot(2, 1, 1)
        self.spectrum_line, = self.spectrum_ax.plot([], [], color='cyan', linewidth=1)
        self.spectrum_ax.set_xlabel('Frequency (MHz)')
        self.spectrum_ax.set_ylabel('Power (dB)')
        self.spectrum_ax.set_title('Real-time Spectrum Display')
        self.spectrum_ax.grid(True, alpha=0.3)
        self.spectrum_ax.set_xlim(0, 6000)
        self.spectrum_ax.set_ylim(-120, 0)
        
        # Waterfall plot
        self.waterfall_ax = self.figure.add_subplot(2, 1, 2)
        self.waterfall_im = self.waterfall_ax.imshow(self.waterfall_data, 
                                                    aspect='auto', 
                                                    cmap='viridis',
                                                    extent=[0, 6000, 0, 100],
                                                    vmin=-120, vmax=0)
        self.waterfall_ax.set_xlabel('Frequency (MHz)')
        self.waterfall_ax.set_ylabel('Time (samples)')
        self.waterfall_ax.set_title('Waterfall Display')
        
        # Colorbar
        self.figure.colorbar(self.waterfall_im, ax=self.waterfall_ax, label='Power (dB)')
        
        self.figure.tight_layout()
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def update_spectrum(self, frequencies, power_spectrum):
        """Update spectrum display"""
        self.frequencies = frequencies / 1e6  # Convert to MHz
        self.power_spectrum = power_spectrum
        
        # Update spectrum plot
        self.spectrum_line.set_data(self.frequencies, power_spectrum)
        self.spectrum_ax.set_xlim(np.min(self.frequencies), np.max(self.frequencies))
        
        # Update waterfall
        self.waterfall_data[self.waterfall_row] = power_spectrum
        self.waterfall_row = (self.waterfall_row + 1) % self.waterfall_data.shape[0]
        
        # Roll waterfall data
        self.waterfall_data = np.roll(self.waterfall_data, -1, axis=0)
        self.waterfall_data[-1] = power_spectrum
        
        self.waterfall_im.set_array(self.waterfall_data)
        self.waterfall_im.set_extent([np.min(self.frequencies), np.max(self.frequencies), 0, 100])
        
        self.canvas.draw()
    
    def set_color_scheme(self, spectrum_color, waterfall_colormap):
        """Set color scheme"""
        self.spectrum_color = spectrum_color
        self.waterfall_colormap = waterfall_colormap
        
        self.spectrum_line.set_color(spectrum_color)
        self.waterfall_im.set_cmap(waterfall_colormap)
        self.canvas.draw()


class ProtocolInfoWidget(QWidget):
    """Protocol information display widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Protocol detection table
        self.protocol_table = QTableWidget()
        self.protocol_table.setColumnCount(5)
        self.protocol_table.setHorizontalHeaderLabels([
            'Protocol', 'Frequency (MHz)', 'Confidence', 'Modulation', 'Bandwidth'
        ])
        
        layout.addWidget(QLabel("Detected Protocols:"))
        layout.addWidget(self.protocol_table)
        
        # Unknown protocol analysis
        unknown_group = QGroupBox("Unknown Protocol Analysis")
        unknown_layout = QVBoxLayout()
        
        self.unknown_text = QTextEdit()
        self.unknown_text.setMaximumHeight(100)
        unknown_layout.addWidget(self.unknown_text)
        
        unknown_group.setLayout(unknown_layout)
        layout.addWidget(unknown_group)
        
        self.setLayout(layout)
    
    def update_protocols(self, protocols):
        """Update protocol information"""
        self.protocol_table.setRowCount(len(protocols))
        
        for i, protocol in enumerate(protocols):
            self.protocol_table.setItem(i, 0, QTableWidgetItem(protocol.get('name', 'Unknown')))
            self.protocol_table.setItem(i, 1, QTableWidgetItem(f"{protocol.get('frequency', 0)/1e6:.3f}"))
            self.protocol_table.setItem(i, 2, QTableWidgetItem(f"{protocol.get('confidence', 0):.3f}"))
            self.protocol_table.setItem(i, 3, QTableWidgetItem(protocol.get('modulation', 'Unknown')))
            self.protocol_table.setItem(i, 4, QTableWidgetItem(f"{protocol.get('bandwidth', 0)/1e3:.1f} kHz"))


class ControlWidget(QWidget):
    """Control panel widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # SDR Controls
        sdr_group = QGroupBox("SDR Controls")
        sdr_layout = QGridLayout()
        
        sdr_layout.addWidget(QLabel("Center Frequency (MHz):"), 0, 0)
        self.freq_spinbox = QDoubleSpinBox()
        self.freq_spinbox.setRange(0.1, 6000)
        self.freq_spinbox.setValue(100)
        self.freq_spinbox.setSuffix(" MHz")
        sdr_layout.addWidget(self.freq_spinbox, 0, 1)
        
        sdr_layout.addWidget(QLabel("Sample Rate (MHz):"), 1, 0)
        self.samplerate_combo = QComboBox()
        self.samplerate_combo.addItems(["0.25", "0.5", "1.0", "2.048", "2.4", "3.2"])
        self.samplerate_combo.setCurrentText("2.048")
        sdr_layout.addWidget(self.samplerate_combo, 1, 1)
        
        sdr_layout.addWidget(QLabel("Gain (dB):"), 2, 0)
        self.gain_spinbox = QSpinBox()
        self.gain_spinbox.setRange(0, 50)
        self.gain_spinbox.setValue(20)
        sdr_layout.addWidget(self.gain_spinbox, 2, 1)
        
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        
        sdr_layout.addWidget(self.start_button, 3, 0)
        sdr_layout.addWidget(self.stop_button, 3, 1)
        
        sdr_group.setLayout(sdr_layout)
        layout.addWidget(sdr_group)
        
        # Display Controls
        display_group = QGroupBox("Display Controls")
        display_layout = QGridLayout()
        
        display_layout.addWidget(QLabel("Spectrum Color:"), 0, 0)
        self.spectrum_color_combo = QComboBox()
        self.spectrum_color_combo.addItems(["cyan", "yellow", "green", "red", "white"])
        display_layout.addWidget(self.spectrum_color_combo, 0, 1)
        
        display_layout.addWidget(QLabel("Waterfall Colormap:"), 1, 0)
        self.waterfall_colormap_combo = QComboBox()
        self.waterfall_colormap_combo.addItems(["viridis", "plasma", "inferno", "magma", "jet"])
        display_layout.addWidget(self.waterfall_colormap_combo, 1, 1)
        
        display_layout.addWidget(QLabel("FFT Size:"), 2, 0)
        self.fft_size_combo = QComboBox()
        self.fft_size_combo.addItems(["512", "1024", "2048", "4096"])
        self.fft_size_combo.setCurrentText("1024")
        display_layout.addWidget(self.fft_size_combo, 2, 1)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # AI Controls
        ai_group = QGroupBox("AI Protocol Identification")
        ai_layout = QVBoxLayout()
        
        self.ai_enabled_checkbox = QCheckBox("Enable AI Protocol Identification")
        self.ai_enabled_checkbox.setChecked(True)
        ai_layout.addWidget(self.ai_enabled_checkbox)
        
        self.ai_confidence_slider = QSlider(Qt.Horizontal)
        self.ai_confidence_slider.setRange(0, 100)
        self.ai_confidence_slider.setValue(70)
        ai_layout.addWidget(QLabel("Confidence Threshold:"))
        ai_layout.addWidget(self.ai_confidence_slider)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        layout.addStretch()
        self.setLayout(layout)


class StatusWidget(QWidget):
    """Status display widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # System Status
        status_group = QGroupBox("System Status")
        status_layout = QGridLayout()
        
        status_layout.addWidget(QLabel("SDR Device:"), 0, 0)
        self.sdr_status_label = QLabel("Disconnected")
        status_layout.addWidget(self.sdr_status_label, 0, 1)
        
        status_layout.addWidget(QLabel("AI System:"), 1, 0)
        self.ai_status_label = QLabel("Not Loaded")
        status_layout.addWidget(self.ai_status_label, 1, 1)
        
        status_layout.addWidget(QLabel("User:"), 2, 0)
        self.user_status_label = QLabel("Not Logged In")
        status_layout.addWidget(self.user_status_label, 2, 1)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Performance Metrics
        perf_group = QGroupBox("Performance")
        perf_layout = QGridLayout()
        
        perf_layout.addWidget(QLabel("Acquisition Rate:"), 0, 0)
        self.acq_rate_label = QLabel("0 samples/s")
        perf_layout.addWidget(self.acq_rate_label, 0, 1)
        
        perf_layout.addWidget(QLabel("Processing Rate:"), 1, 0)
        self.proc_rate_label = QLabel("0 spectra/s")
        perf_layout.addWidget(self.proc_rate_label, 1, 1)
        
        perf_layout.addWidget(QLabel("CPU Usage:"), 2, 0)
        self.cpu_progress = QProgressBar()
        perf_layout.addWidget(self.cpu_progress, 2, 1)
        
        perf_layout.addWidget(QLabel("Memory Usage:"), 3, 0)
        self.memory_progress = QProgressBar()
        perf_layout.addWidget(self.memory_progress, 3, 1)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_status(self, sdr_status=None, ai_status=None, user_status=None):
        """Update status displays"""
        if sdr_status:
            self.sdr_status_label.setText(sdr_status)
        if ai_status:
            self.ai_status_label.setText(ai_status)
        if user_status:
            self.user_status_label.setText(user_status)
    
    def update_performance(self, acq_rate=None, proc_rate=None, cpu_usage=None, memory_usage=None):
        """Update performance metrics"""
        if acq_rate is not None:
            self.acq_rate_label.setText(f"{acq_rate:.1f} samples/s")
        if proc_rate is not None:
            self.proc_rate_label.setText(f"{proc_rate:.1f} spectra/s")
        if cpu_usage is not None:
            self.cpu_progress.setValue(int(cpu_usage))
        if memory_usage is not None:
            self.memory_progress.setValue(int(memory_usage))


class DataWorker(QThread):
    """Worker thread for SDR data processing"""
    
    spectrum_updated = pyqtSignal(np.ndarray, np.ndarray)
    protocols_detected = pyqtSignal(list)
    status_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sdr_controller = None
        self.ai_identifier = None
        self.protocol_processor = None
        self.running = False
        self.mutex = QMutex()
        
    def initialize(self, sdr_controller, ai_identifier, protocol_processor):
        """Initialize worker with components"""
        self.sdr_controller = sdr_controller
        self.ai_identifier = ai_identifier
        self.protocol_processor = protocol_processor
        
    def start_processing(self):
        """Start data processing"""
        self.running = True
        self.start()
        
    def stop_processing(self):
        """Stop data processing"""
        self.running = False
        self.wait()
        
    def run(self):
        """Main processing loop"""
        while self.running:
            try:
                if self.sdr_controller:
                    # Get latest spectrum data
                    spectrum_data = self.sdr_controller.get_latest_spectrum()
                    
                    if spectrum_data:
                        frequencies = spectrum_data['frequencies']
                        power_spectrum = spectrum_data['power_spectrum']
                        
                        # Emit spectrum update
                        self.spectrum_updated.emit(frequencies, power_spectrum)
                        
                        # AI protocol identification
                        if self.ai_identifier and self.ai_identifier.is_trained:
                            try:
                                # Generate some IQ samples for AI (simplified)
                                iq_samples = np.random.normal(0, 1, 1024) + 1j * np.random.normal(0, 1, 1024)
                                protocol_info = self.ai_identifier.identify_protocol(iq_samples)
                                
                                protocols = [{
                                    'name': protocol_info.name,
                                    'frequency': protocol_info.frequency,
                                    'confidence': protocol_info.confidence,
                                    'modulation': protocol_info.modulation,
                                    'bandwidth': protocol_info.bandwidth
                                }]
                                
                                self.protocols_detected.emit(protocols)
                            except Exception as e:
                                logger.error(f"AI identification error: {e}")
                        
                        # Update status
                        stats = self.sdr_controller.get_statistics()
                        self.status_updated.emit(stats)
                
                time.sleep(0.1)  # 10 Hz update rate
                
            except Exception as e:
                logger.error(f"Data worker error: {e}")
                time.sleep(1)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SDR Spectrum Analyzer - Telecommunications Education Platform")
        self.setGeometry(100, 100, 1400, 900)
        
        # Components
        self.sdr_controller = None
        self.ai_identifier = None
        self.protocol_processor = None
        self.db_manager = None
        self.multi_user_manager = None
        self.current_session = None
        
        # Worker thread
        self.data_worker = DataWorker()
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_connections()
        
        # Initialize components
        self.initialize_components()
        
        # Timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(100)  # 10 Hz
        
    def setup_ui(self):
        """Setup user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel - spectrum and waterfall
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Logo area
        logo_label = QLabel("SDR SPECTRUM ANALYZER")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        left_layout.addWidget(logo_label)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Spectrum tab
        self.spectrum_widget = SpectrumWidget()
        self.tab_widget.addTab(self.spectrum_widget, "Spectrum & Waterfall")
        
        # Protocol info tabs
        self.protocol_info_widget = ProtocolInfoWidget()
        self.tab_widget.addTab(self.protocol_info_widget, "Protocol Information")
        
        # Dump IQ tab
        dump_widget = QWidget()
        dump_layout = QVBoxLayout()
        dump_layout.addWidget(QLabel("IQ Data Dump"))
        self.dump_text = QTextEdit()
        dump_layout.addWidget(self.dump_text)
        dump_widget.setLayout(dump_layout)
        self.tab_widget.addTab(dump_widget, "Dump IQ")
        
        left_layout.addWidget(self.tab_widget)
        left_panel.setLayout(left_layout)
        
        # Right panel - controls and status
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Control widget
        self.control_widget = ControlWidget()
        right_layout.addWidget(self.control_widget)
        
        # Status widget
        self.status_widget = StatusWidget()
        right_layout.addWidget(self.status_widget)
        
        right_panel.setLayout(right_layout)
        right_panel.setMaximumWidth(350)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 3)
        main_layout.addWidget(right_panel, 1)
        
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        login_action = QAction('Login', self)
        login_action.triggered.connect(self.show_login_dialog)
        file_menu.addAction(login_action)
        
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout_user)
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        save_action = QAction('Save Session', self)
        save_action.triggered.connect(self.save_session)
        file_menu.addAction(save_action)
        
        load_action = QAction('Load Session', self)
        load_action.triggered.connect(self.load_session)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Options menu
        options_menu = menubar.addMenu('Options')
        
        preferences_action = QAction('Preferences', self)
        preferences_action.triggered.connect(self.show_preferences)
        options_menu.addAction(preferences_action)
        
        # Preset menu
        preset_menu = menubar.addMenu('Preset')
        
        fm_preset_action = QAction('FM Radio (88-108 MHz)', self)
        fm_preset_action.triggered.connect(lambda: self.apply_preset('fm_radio'))
        preset_menu.addAction(fm_preset_action)
        
        aircraft_preset_action = QAction('Aircraft (118-137 MHz)', self)
        aircraft_preset_action.triggered.connect(lambda: self.apply_preset('aircraft'))
        preset_menu.addAction(aircraft_preset_action)
        
        gsm_preset_action = QAction('GSM (890-960 MHz)', self)
        gsm_preset_action.triggered.connect(lambda: self.apply_preset('gsm'))
        preset_menu.addAction(gsm_preset_action)
        
        wifi_preset_action = QAction('WiFi 2.4G (2400-2500 MHz)', self)
        wifi_preset_action.triggered.connect(lambda: self.apply_preset('wifi_2g4'))
        preset_menu.addAction(wifi_preset_action)
        
        # More menu
        more_menu = menubar.addMenu('More')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        more_menu.addAction(about_action)
        
        help_action = QAction('Help', self)
        help_action.triggered.connect(self.show_help)
        more_menu.addAction(help_action)
        
    def setup_connections(self):
        """Setup signal connections"""
        # Control connections
        self.control_widget.start_button.clicked.connect(self.start_acquisition)
        self.control_widget.stop_button.clicked.connect(self.stop_acquisition)
        
        # Data worker connections
        self.data_worker.spectrum_updated.connect(self.spectrum_widget.update_spectrum)
        self.data_worker.protocols_detected.connect(self.protocol_info_widget.update_protocols)
        self.data_worker.status_updated.connect(self.update_status_from_worker)
        
        # Control change connections
        self.control_widget.freq_spinbox.valueChanged.connect(self.update_sdr_frequency)
        self.control_widget.spectrum_color_combo.currentTextChanged.connect(self.update_display_colors)
        self.control_widget.waterfall_colormap_combo.currentTextChanged.connect(self.update_display_colors)
        
    def initialize_components(self):
        """Initialize all components"""
        try:
            # Database
            self.db_manager = DatabaseManager("sdr_app.db")
            self.multi_user_manager = MultiUserManager(self.db_manager)
            
            # SDR Controller
            self.sdr_controller = SDRController()
            self.sdr_controller.initialize()
            
            # AI Identifier
            self.ai_identifier = AIProtocolIdentifier()
            # Train AI system (reduced samples for demo)
            self.ai_identifier.train_system(samples_per_protocol=50)
            
            # Protocol Processor
            self.protocol_processor = ProtocolProcessor()
            
            # Initialize worker
            self.data_worker.initialize(self.sdr_controller, self.ai_identifier, self.protocol_processor)
            
            # Update status
            self.status_widget.update_status(
                sdr_status="Connected (Simulation Mode)",
                ai_status="Loaded and Trained",
                user_status="Not Logged In"
            )
            
            self.status_bar.showMessage("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Component initialization error: {e}")
            self.status_bar.showMessage(f"Initialization error: {e}")
    
    def show_login_dialog(self):
        """Show login dialog"""
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            
            # Create default users if they don't exist
            self.create_default_users()
            
            result = self.multi_user_manager.login_user(username, password)
            if result:
                session, message = result
                self.current_session = session
                self.status_widget.update_status(user_status=f"{session.username} ({session.role})")
                self.status_bar.showMessage(f"Logged in as {session.username}")
                
                # Register SDR device
                if session.sdr_device_id:
                    self.status_widget.update_status(sdr_status=f"Connected: {session.sdr_device_id}")
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")
    
    def create_default_users(self):
        """Create default users for demo"""
        try:
            self.db_manager.create_user("admin", "admin@example.com", "admin123", "admin")
            self.db_manager.create_user("instructor", "instructor@example.com", "inst123", "instructor")
            self.db_manager.create_user("student", "student@example.com", "student123", "student")
            
            # Register SDR devices
            self.db_manager.register_sdr_device("rtlsdr_sim_001", "RTL-SDR Simulator 1", "RTL-SDR")
            self.db_manager.register_sdr_device("rtlsdr_sim_002", "RTL-SDR Simulator 2", "RTL-SDR")
        except:
            pass  # Users might already exist
    
    def logout_user(self):
        """Logout current user"""
        if self.current_session:
            self.multi_user_manager.logout_user(self.current_session.session_id)
            self.current_session = None
            self.status_widget.update_status(user_status="Not Logged In")
            self.status_bar.showMessage("Logged out")
    
    def start_acquisition(self):
        """Start SDR acquisition"""
        try:
            if self.sdr_controller:
                self.sdr_controller.start_acquisition()
                self.data_worker.start_processing()
                
                self.control_widget.start_button.setEnabled(False)
                self.control_widget.stop_button.setEnabled(True)
                
                self.status_bar.showMessage("Acquisition started")
        except Exception as e:
            logger.error(f"Start acquisition error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start acquisition: {e}")
    
    def stop_acquisition(self):
        """Stop SDR acquisition"""
        try:
            if self.sdr_controller:
                self.sdr_controller.stop_acquisition()
                self.data_worker.stop_processing()
                
                self.control_widget.start_button.setEnabled(True)
                self.control_widget.stop_button.setEnabled(False)
                
                self.status_bar.showMessage("Acquisition stopped")
        except Exception as e:
            logger.error(f"Stop acquisition error: {e}")
    
    def update_sdr_frequency(self):
        """Update SDR center frequency"""
        if self.sdr_controller:
            freq_mhz = self.control_widget.freq_spinbox.value()
            freq_hz = freq_mhz * 1e6
            self.sdr_controller.set_center_frequency(freq_hz)
    
    def update_display_colors(self):
        """Update display colors"""
        spectrum_color = self.control_widget.spectrum_color_combo.currentText()
        waterfall_colormap = self.control_widget.waterfall_colormap_combo.currentText()
        self.spectrum_widget.set_color_scheme(spectrum_color, waterfall_colormap)
    
    def update_status_from_worker(self, stats):
        """Update status from worker thread"""
        self.status_widget.update_performance(
            acq_rate=stats.get('acquisition_rate', 0),
            proc_rate=stats.get('processing_rate', 0)
        )
    
    def apply_preset(self, preset_name):
        """Apply frequency preset"""
        presets = {
            'fm_radio': {'freq': 100, 'sample_rate': '2.048'},
            'aircraft': {'freq': 125, 'sample_rate': '2.048'},
            'gsm': {'freq': 925, 'sample_rate': '2.048'},
            'wifi_2g4': {'freq': 2450, 'sample_rate': '2.4'}
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.control_widget.freq_spinbox.setValue(preset['freq'])
            self.control_widget.samplerate_combo.setCurrentText(preset['sample_rate'])
            self.update_sdr_frequency()
    
    def save_session(self):
        """Save current session"""
        if not self.current_session:
            QMessageBox.warning(self, "Warning", "Please log in first")
            return
        
        filename, _ = QFileDialog.getSaveFileName(self, "Save Session", "", "JSON Files (*.json)")
        if filename:
            session_data = {
                'frequency': self.control_widget.freq_spinbox.value(),
                'sample_rate': self.control_widget.samplerate_combo.currentText(),
                'gain': self.control_widget.gain_spinbox.value(),
                'spectrum_color': self.control_widget.spectrum_color_combo.currentText(),
                'waterfall_colormap': self.control_widget.waterfall_colormap_combo.currentText()
            }
            
            with open(filename, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            self.status_bar.showMessage(f"Session saved to {filename}")
    
    def load_session(self):
        """Load session from file"""
        filename, _ = QFileDialog.getOpenFileName(self, "Load Session", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'r') as f:
                    session_data = json.load(f)
                
                self.control_widget.freq_spinbox.setValue(session_data.get('frequency', 100))
                self.control_widget.samplerate_combo.setCurrentText(session_data.get('sample_rate', '2.048'))
                self.control_widget.gain_spinbox.setValue(session_data.get('gain', 20))
                self.control_widget.spectrum_color_combo.setCurrentText(session_data.get('spectrum_color', 'cyan'))
                self.control_widget.waterfall_colormap_combo.setCurrentText(session_data.get('waterfall_colormap', 'viridis'))
                
                self.update_sdr_frequency()
                self.update_display_colors()
                
                self.status_bar.showMessage(f"Session loaded from {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load session: {e}")
    
    def show_preferences(self):
        """Show preferences dialog"""
        QMessageBox.information(self, "Preferences", "Preferences dialog would be implemented here")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
                         "SDR Spectrum Analyzer\n"
                         "Telecommunications Education Platform\n\n"
                         "Features:\n"
                         "• Real-time spectrum analysis\n"
                         "• AI-powered protocol identification\n"
                         "• Multi-user support\n"
                         "• Protocol decoding\n"
                         "• Educational tools\n\n"
                         "Built with Python, PyQt5, and TensorFlow")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
        SDR Spectrum Analyzer Help
        
        Getting Started:
        1. Login with your credentials (demo: student/student123)
        2. Click 'Start' to begin spectrum analysis
        3. Adjust frequency and other parameters as needed
        
        Features:
        • Real-time spectrum display with waterfall
        • AI protocol identification
        • Multiple frequency presets
        • Session save/load
        • Multi-user support
        
        Controls:
        • Use frequency presets for common bands
        • Adjust colors and display options
        • Enable/disable AI identification
        • Monitor system performance
        """
        
        QMessageBox.information(self, "Help", help_text)
    
    def update_display(self):
        """Periodic display update"""
        # Update CPU and memory usage (simulated)
        import psutil
        try:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            self.status_widget.update_performance(cpu_usage=cpu_usage, memory_usage=memory_usage)
        except:
            pass
    
    def closeEvent(self, event):
        """Handle application close"""
        # Stop acquisition
        if self.sdr_controller:
            self.sdr_controller.stop_acquisition()
        
        # Stop worker
        self.data_worker.stop_processing()
        
        # Logout user
        if self.current_session:
            self.logout_user()
        
        # Cleanup
        if self.sdr_controller:
            self.sdr_controller.cleanup()
        
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("SDR Spectrum Analyzer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Telecommunications Education Platform")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

