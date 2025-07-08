import sys
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import Cursor


from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QLabel, QComboBox, QListWidget, QScrollArea,
                             QDoubleSpinBox, QFileDialog, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt


class WellDataApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Well Data Analysis Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        # Data storage
        self.well_data = pd.DataFrame(columns=["Well", "MD", "DVD", "Porosity", "Saturation"])
        self.perf_data = pd.DataFrame(columns=["Well", "From_MD", "To_MD"])
        self.mdt_data = pd.DataFrame(columns=["Well", "MD", "Pressure", "Fluid_Type"])
        
        # Initialize UI
        self.init_ui()
        
        # Plotting variables
        self.current_scale = 200
        self.current_offset = 0
        self.selected_wells = []
        
    def init_ui(self):
        # Main tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Data Entry Tab
        self.data_entry_tab = QWidget()
        self.tabs.addTab(self.data_entry_tab, "Data Entry")
        self.setup_data_entry_tab()
        
        # Plotting Tab
        self.plotting_tab = QWidget()
        self.tabs.addTab(self.plotting_tab, "Plotting")
        self.setup_plotting_tab()
        
        # File menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        
        save_action = file_menu.addAction('Save')
        save_action.triggered.connect(self.save_data)
        
        open_action = file_menu.addAction('Open')
        open_action.triggered.connect(self.load_data)
        
    def setup_data_entry_tab(self):
        layout = QVBoxLayout()
        
        # Well Data Section
        well_data_group = QWidget()
        well_data_layout = QVBoxLayout()
        well_data_group.setLayout(well_data_layout)
        
        well_data_layout.addWidget(QLabel("Well Data (Well, MD, DVD, Porosity, Saturation):"))
        self.well_data_text = QTextEdit()
        self.well_data_text.setPlaceholderText("Paste comma-separated values here...")
        well_data_layout.addWidget(self.well_data_text)
        
        well_data_btn = QPushButton("Load Well Data")
        well_data_btn.clicked.connect(self.load_well_data)
        well_data_layout.addWidget(well_data_btn)
        
        # Perforation Data Section
        perf_data_group = QWidget()
        perf_data_layout = QVBoxLayout()
        perf_data_group.setLayout(perf_data_layout)
        
        perf_data_layout.addWidget(QLabel("Perforation Data (Well, From_MD, To_MD):"))
        self.perf_data_text = QTextEdit()
        self.perf_data_text.setPlaceholderText("Paste comma-separated values here...")
        perf_data_layout.addWidget(self.perf_data_text)
        
        perf_data_btn = QPushButton("Load Perforation Data")
        perf_data_btn.clicked.connect(self.load_perf_data)
        perf_data_layout.addWidget(perf_data_btn)
        
        # MDT Data Section
        mdt_data_group = QWidget()
        mdt_data_layout = QVBoxLayout()
        mdt_data_group.setLayout(mdt_data_layout)
        
        mdt_data_layout.addWidget(QLabel("MDT Data (Well, MD, Pressure, Fluid_Type):"))
        self.mdt_data_text = QTextEdit()
        self.mdt_data_text.setPlaceholderText("Paste comma-separated values here...")
        mdt_data_layout.addWidget(self.mdt_data_text)
        
        mdt_data_btn = QPushButton("Load MDT Data")
        mdt_data_btn.clicked.connect(self.load_mdt_data)
        mdt_data_layout.addWidget(mdt_data_btn)
        
        # Add sections to main layout with scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.addWidget(well_data_group)
        content_layout.addWidget(perf_data_group)
        content_layout.addWidget(mdt_data_group)
        scroll.setWidget(content)
        
        layout.addWidget(scroll)
        self.data_entry_tab.setLayout(layout)
        
    def setup_plotting_tab(self):
        # Create main horizontal layout
        main_layout = QHBoxLayout()
        
        # Left panel for controls (well selection and settings)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Plot type selection
        plot_type_layout = QHBoxLayout()
        plot_type_layout.addWidget(QLabel("Plot Type:"))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["MDT Plot", "Well Log Plot"])
        plot_type_layout.addWidget(self.plot_type_combo)
        left_layout.addLayout(plot_type_layout)
        
        # Well selection
        left_layout.addWidget(QLabel("Select Wells:"))
        self.well_list = QListWidget()
        self.well_list.setMaximumWidth(200)
        self.well_list.setSelectionMode(QListWidget.MultiSelection)
        left_layout.addWidget(self.well_list)
        
        # Scale control for Well Log Plot
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Depth Scale:"))
        self.scale_input = QDoubleSpinBox()
        self.scale_input.setRange(50, 2000)
        self.scale_input.setValue(200)
        self.scale_input.setSingleStep(50)
        scale_layout.addWidget(self.scale_input)
        left_layout.addLayout(scale_layout)
        
        self.apply_scale_btn = QPushButton("Apply Scale")
        left_layout.addWidget(self.apply_scale_btn)
        
        # Plot button
        plot_btn = QPushButton("Generate Plot")
        left_layout.addWidget(plot_btn)
        
        # Add stretch to push everything up
        left_layout.addStretch()
        
        # Right panel for plotting
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Figure and canvas
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        # Add to right layout
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        # Set stretch factors to make plot area take more space
        main_layout.addWidget(left_panel, stretch=1)
        main_layout.addWidget(right_panel, stretch=4)
        
        # Connect signals
        plot_btn.clicked.connect(self.generate_plot)
        self.apply_scale_btn.clicked.connect(self.update_scale)
        
        self.plotting_tab.setLayout(main_layout)
        
    def load_well_data(self):
        try:
            data = self.well_data_text.toPlainText().strip()
            if not data:
                QMessageBox.warning(self, "Warning", "No data entered!")
                return
                
            rows = [row.split(',') for row in data.split('\n') if row.strip()]
            new_data = pd.DataFrame(rows, columns=["Well", "MD", "DVD", "Porosity", "Saturation"])
            
            # Convert numeric columns
            for col in ["MD", "DVD", "Porosity", "Saturation"]:
                new_data[col] = pd.to_numeric(new_data[col], errors='coerce')
                
            # Drop rows with missing values
            new_data = new_data.dropna()
            
            # Update well list
            self.well_data = pd.concat([self.well_data, new_data]).drop_duplicates().reset_index(drop=True)
            self.update_well_list()
            
            QMessageBox.information(self, "Success", "Well data loaded successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load well data: {str(e)}")
            
    def load_perf_data(self):
        try:
            data = self.perf_data_text.toPlainText().strip()
            if not data:
                QMessageBox.warning(self, "Warning", "No data entered!")
                return
                
            rows = [row.split(',') for row in data.split('\n') if row.strip()]
            new_data = pd.DataFrame(rows, columns=["Well", "From_MD", "To_MD"])
            
            # Convert numeric columns
            for col in ["From_MD", "To_MD"]:
                new_data[col] = pd.to_numeric(new_data[col], errors='coerce')
                
            # Drop rows with missing values
            new_data = new_data.dropna()
            
            # Convert MD to DVD using well data
            new_data["From_DVD"] = np.nan
            new_data["To_DVD"] = np.nan
            
            for well in new_data["Well"].unique():
                well_mask = new_data["Well"] == well
                well_ref_data = self.well_data[self.well_data["Well"] == well]
                
                if not well_ref_data.empty:
                    md = well_ref_data["MD"].values
                    dvd = well_ref_data["DVD"].values
                    
                    # Create interpolation function
                    if len(md) > 1:
                        interp_func = interp1d(md, dvd, kind='linear', fill_value="extrapolate")
                        
                        # Apply interpolation
                        new_data.loc[well_mask, "From_DVD"] = interp_func(new_data.loc[well_mask, "From_MD"])
                        new_data.loc[well_mask, "To_DVD"] = interp_func(new_data.loc[well_mask, "To_MD"])
            
            # Update perforation data
            self.perf_data = pd.concat([self.perf_data, new_data]).drop_duplicates().reset_index(drop=True)
            QMessageBox.information(self, "Success", "Perforation data loaded successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load perforation data: {str(e)}")
            
    def load_mdt_data(self):
        try:
            data = self.mdt_data_text.toPlainText().strip()
            if not data:
                QMessageBox.warning(self, "Warning", "No data entered!")
                return
                
            rows = [row.split(',') for row in data.split('\n') if row.strip()]
            new_data = pd.DataFrame(rows, columns=["Well", "MD", "Pressure", "Fluid_Type"])
            
            # Convert numeric columns
            for col in ["MD", "Pressure"]:
                new_data[col] = pd.to_numeric(new_data[col], errors='coerce')
                
            # Drop rows with missing values
            new_data = new_data.dropna()
            
            # Convert MD to DVD using well data
            new_data["DVD"] = np.nan
            
            for well in new_data["Well"].unique():
                well_mask = new_data["Well"] == well
                well_ref_data = self.well_data[self.well_data["Well"] == well]
                
                if not well_ref_data.empty:
                    md = well_ref_data["MD"].values
                    dvd = well_ref_data["DVD"].values
                    
                    # Create interpolation function
                    if len(md) > 1:
                        interp_func = interp1d(md, dvd, kind='linear', fill_value="extrapolate")
                        new_data.loc[well_mask, "DVD"] = interp_func(new_data.loc[well_mask, "MD"])
            
            # Update MDT data
            self.mdt_data = pd.concat([self.mdt_data, new_data]).drop_duplicates().reset_index(drop=True)
            QMessageBox.information(self, "Success", "MDT data loaded successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load MDT data: {str(e)}")
            
    def update_well_list(self):
        self.well_list.clear()
        wells = self.well_data["Well"].unique()
        self.well_list.addItems(wells)
        
    def generate_plot(self):
        self.figure.clear()
        plot_type = self.plot_type_combo.currentText()
        self.selected_wells = [item.text() for item in self.well_list.selectedItems()]
        
        if not self.selected_wells:
            QMessageBox.warning(self, "Warning", "Please select at least one well!")
            return
            
        if plot_type == "MDT Plot":
            self.generate_mdt_plot()
        else:
            self.generate_well_log_plot()
            
        self.canvas.draw()
        
    def generate_mdt_plot(self):
        ax = self.figure.add_subplot(111)
        
        # Filter data for selected wells
        plot_data = self.mdt_data[self.mdt_data["Well"].isin(self.selected_wells)]
        
        if plot_data.empty:
            QMessageBox.warning(self, "Warning", "No MDT data available for selected wells!")
            return
            
        # Get min/max DVD and pressure for scaling
        min_dvd = plot_data["DVD"].min()
        max_dvd = plot_data["DVD"].max()
        min_pressure = plot_data["Pressure"].min()
        max_pressure = plot_data["Pressure"].max()
        
        # Create color map for fluid types
        fluid_types = plot_data["Fluid_Type"].unique()
        colors = plt.cm.tab10(np.linspace(0, 1, len(fluid_types)))
        color_map = dict(zip(fluid_types, colors))
        
        # Plot each point with color based on fluid type
        for fluid, color in color_map.items():
            fluid_data = plot_data[plot_data["Fluid_Type"] == fluid]
            ax.scatter(fluid_data["Pressure"], fluid_data["DVD"], 
                      c=[color], label=fluid, alpha=0.7)
        
        # Set axis properties
        ax.set_ylim(max_dvd, min_dvd)  # Reverse for depth
        ax.set_xlim(min_pressure - 0.1*(max_pressure-min_pressure), 
                   max_pressure + 0.1*(max_pressure-min_pressure))
        ax.set_xlabel("Pressure")
        ax.set_ylabel("DVD")
        ax.set_title("MDT Plot")
        ax.grid(True)
        ax.legend()
        
    def generate_well_log_plot(self):
        self.current_scale = self.scale_input.value()
        self.current_offset = 0
        
        # Calculate total width needed
        n_wells = len(self.selected_wells)
        width_per_well = 3  # inches
        total_width = n_wells * width_per_well
        
        # Create figure with appropriate size
        self.figure.set_size_inches(total_width, 10)
        
        # Create axes for each well
        axes = []
        for i, well in enumerate(self.selected_wells):
            ax = self.figure.add_subplot(1, n_wells, i+1)
            axes.append(ax)
            
            # Filter data for current well
            well_log_data = self.well_data[self.well_data["Well"] == well]
            perf_data = self.perf_data[self.perf_data["Well"] == well]
            
            if well_log_data.empty:
                ax.text(0.5, 0.5, "No data", ha='center', va='center')
                continue
                
            # Get min/max DVD for scaling
            min_dvd = well_log_data["DVD"].min()
            max_dvd = well_log_data["DVD"].max()
            
            # Plot porosity and saturation
            ax.plot(well_log_data["Porosity"], well_log_data["DVD"], 
                    color='blue', label='Porosity')
            ax.plot(well_log_data["Saturation"], well_log_data["DVD"], 
                    color='green', label='Saturation')
            
            # Plot perforations
            for _, row in perf_data.iterrows():
                ax.axhspan(row["From_DVD"], row["To_DVD"], 
                          xmin=0, xmax=1, color='red', alpha=0.3)
            
            # Set axis properties
            ax.set_ylim(self.current_offset + self.current_scale, self.current_offset)
            ax.set_xlim(0, 1)
            ax.set_xlabel(well)
            if i == 0:
                ax.set_ylabel("DVD")
            ax.grid(True)
            ax.legend()
        
        # Connect mouse events for scrolling
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        
    def on_scroll(self, event):
        if event.button == 'up':
            self.current_offset += self.current_scale * 0.1
        elif event.button == 'down':
            self.current_offset -= self.current_scale * 0.1
            
        # Update all axes
        for ax in self.figure.axes:
            ax.set_ylim(self.current_offset + self.current_scale, self.current_offset)
            
        self.canvas.draw()
        
    def update_scale(self):
        self.current_scale = self.scale_input.value()
        self.generate_plot()
        
    def save_data(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Data", "", 
                                                      "Well Data Files (*.well);;All Files (*)", 
                                                      options=options)
            if file_name:
                if not file_name.endswith('.well'):
                    file_name += '.well'
                    
                with open(file_name, 'wb') as f:
                    # Save all three dataframes
                    self.well_data.to_pickle(f)
                    self.perf_data.to_pickle(f)
                    self.mdt_data.to_pickle(f)
                    
                QMessageBox.information(self, "Success", "Data saved successfully!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
            
    def load_data(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Data", "", 
                                                      "Well Data Files (*.well);;All Files (*)", 
                                                      options=options)
            if file_name:
                with open(file_name, 'rb') as f:
                    # Load all three dataframes
                    self.well_data = pd.read_pickle(f)
                    self.perf_data = pd.read_pickle(f)
                    self.mdt_data = pd.read_pickle(f)
                    
                # Update UI
                self.update_well_list()
                QMessageBox.information(self, "Success", "Data loaded successfully!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WellDataApp()
    window.show()
    sys.exit(app.exec_())