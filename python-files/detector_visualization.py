import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import struct
import webbrowser
import tempfile
import os
import sys

class DetectorVisualizationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector Analytics Visualization Tool")
        self.root.geometry("400x300")
        
        # Load detector positions (handle both development and executable)
        positions_file = self.get_resource_path('detector_positions.csv')
        self.positions_df = pd.read_csv(positions_file, index_col='name')
        
        # Variables
        self.selected_file = tk.StringVar(value="")
        self.filter_type = tk.StringVar(value="all")
        
        self.setup_ui()
    
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
        
    def setup_ui(self):
        # File selection
        file_frame = ttk.LabelFrame(self.root, text="Select CSV File", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(file_frame, text="Browse for CSV file", 
                  command=self.browse_file).pack(anchor="w")
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(anchor="w", pady=(5,0))
        
        # Filter selection
        filter_frame = ttk.LabelFrame(self.root, text="Detector Filter", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Radiobutton(filter_frame, text="All Detectors", variable=self.filter_type, 
                       value="all").pack(anchor="w")
        ttk.Radiobutton(filter_frame, text="Problematic Only", variable=self.filter_type, 
                       value="problematic").pack(anchor="w")
        ttk.Radiobutton(filter_frame, text="Good Only", variable=self.filter_type, 
                       value="good").pack(anchor="w")
        
        # Generate button
        ttk.Button(self.root, text="Generate Visualization", 
                  command=self.generate_visualization).pack(pady=20)
        
    def decode_wkb_point(self, wkb_hex):
        """Decode WKB hex string to lat/lon coordinates"""
        try:
            # Remove '0101000020E6100000' prefix (WKB header for SRID 4326 POINT)
            hex_coords = wkb_hex[18:]  # Skip the first 18 characters
            
            # Convert hex to bytes
            coord_bytes = bytes.fromhex(hex_coords)
            
            # Unpack as two double precision floats (little endian)
            lon, lat = struct.unpack('<dd', coord_bytes)
            
            return lat, lon
        except:
            return None, None
    
    def get_fail_reasons(self, row):
        """Determine if detector is problematic and why"""
        reasons = []
        if row['Completeness (%)'] < 70:
            reasons.append('Completeness < 70%')
        if row['Flat_Flow'] == 1:
            reasons.append('Flat FLOW')
        if row['Flat_Occ'] == 1:
            reasons.append('Flat OCC')
        if row['IQR_Flow'] < 1 or row['IQR_Occ'] < 1:
            reasons.append('Low IQR')
        if row['ZeroFlowRate (%)'] > 90:
            reasons.append('Zero FLOW > 90%')
        if row['PeakOffPeakRatio_Flow'] < 1.5:
            reasons.append('Flat Daily Profile')
        if row['FlowPhysCheck_ExceedRatio (%)'] > 80:
            reasons.append('Flow > 250 veh/5min in >80%')
        return '; '.join(reasons)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.selected_file.set(filename)
            self.file_label.config(text=f"Selected: {filename.split('/')[-1]}")
    
    def generate_visualization(self):
        if not self.selected_file.get():
            messagebox.showwarning("No File", "Please select a CSV file first.")
            return
            
        # Load selected file data
        df = pd.read_csv(self.selected_file.get())
        
        # Add failure reasons
        df['Fail_Reason'] = df.apply(self.get_fail_reasons, axis=1)
        df['Is_Problematic'] = df['Fail_Reason'] != ''
        
        # Filter data based on selection
        if self.filter_type.get() == "problematic":
            df = df[df['Is_Problematic']]
        elif self.filter_type.get() == "good":
            df = df[~df['Is_Problematic']]
        
        # Add coordinates
        coords = []
        for detector in df['Detector']:
            if detector in self.positions_df.index:
                lat, lon = self.decode_wkb_point(self.positions_df.loc[detector, 'osm_pos'])
                coords.append({'Detector': detector, 'lat': lat, 'lon': lon})
            else:
                coords.append({'Detector': detector, 'lat': None, 'lon': None})
        
        coords_df = pd.DataFrame(coords)
        df = df.merge(coords_df, on='Detector')
        
        # Remove detectors without coordinates
        df = df.dropna(subset=['lat', 'lon'])
        
        if len(df) == 0:
            tk.messagebox.showwarning("No Data", "No detectors found with valid coordinates.")
            return
        
        # Create HTML visualization
        self.create_html_visualization(df)
    
    def create_html_visualization(self, df):
        # Create HTML content
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Detector Analytics Visualization</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #1e1e1e; color: #ffffff; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .controls {{ margin-bottom: 20px; }}
        .stats-table {{ margin-top: 20px; }}
        table {{ border-collapse: collapse; width: 100%; background-color: #2d2d2d; }}
        th, td {{ border: 1px solid #555; padding: 8px; text-align: left; color: #ffffff; }}
        th {{ background-color: #404040; }}
        select {{ background-color: #2d2d2d; color: #ffffff; border: 1px solid #555; padding: 5px; }}
        h1, h3 {{ color: #ffffff; }}
        label {{ color: #ffffff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Detector Analytics - {self.selected_file.get().split('/')[-1].upper()} ({self.filter_type.get().title()})</h1>
        
        <div class="controls">
            <label for="detector-select">Select Detector:</label>
            <select id="detector-select" onchange="updateVisualization()">
                <option value="">Choose a detector...</option>
"""
        
        # Add detector options
        for _, row in df.iterrows():
            status = "[BAD]" if row['Is_Problematic'] else "[OK]"
            html_content += f'                <option value="{row["Detector"]}">{status} {row["Detector"]}</option>\n'
        
        html_content += """
            </select>
        </div>
        
        <div id="map" style="width:100%;height:500px;"></div>
        
        <div class="stats-table">
            <h3>Detector Statistics</h3>
            <div id="stats-content">Select a detector to view statistics</div>
        </div>
    </div>

    <script>
        const detectorData = {
"""
        
        # Add detector data as JavaScript object
        for _, row in df.iterrows():
            stats_html = "<table>"
            for col in df.columns:
                if col not in ['Detector', 'lat', 'lon', 'Is_Problematic', 'Fail_Reason']:
                    # Check if this row should be highlighted in red
                    cell_style = ""
                    if row['Is_Problematic']:
                        if (col == 'Completeness (%)' and row[col] < 70) or \
                           (col == 'Flat_Flow' and row[col] == 1) or \
                           (col == 'Flat_Occ' and row[col] == 1) or \
                           (col == 'IQR_Flow' and row[col] < 1) or \
                           (col == 'IQR_Occ' and row[col] < 1) or \
                           (col == 'ZeroFlowRate (%)' and row[col] > 90) or \
                           (col == 'PeakOffPeakRatio_Flow' and row[col] < 1.5) or \
                           (col == 'FlowPhysCheck_ExceedRatio (%)' and row[col] > 80):
                            cell_style = " style='color: #ff6b6b; font-weight: bold;'"
                    
                    stats_html += f"<tr><th{cell_style}>{col}</th><td{cell_style}>{row[col]}</td></tr>"
            stats_html += "</table>"
            
            # Add failed tests if problematic
            if row['Is_Problematic'] and row['Fail_Reason']:
                stats_html += f"<p style='color: red; font-weight: bold; margin-top: 15px;'>Failed Tests: {row['Fail_Reason']}</p>"
            
            html_content += f"""
            "{row['Detector']}": {{
                lat: {row['lat']},
                lon: {row['lon']},
                stats: `{stats_html}`,
                problematic: {str(row['Is_Problematic']).lower()}
            }},"""
        
        html_content += """
        };
        
        function updateVisualization() {
            const select = document.getElementById('detector-select');
            const selectedDetector = select.value;
            
            if (!selectedDetector) {
                document.getElementById('stats-content').innerHTML = 'Select a detector to view statistics';
                return;
            }
            
            const data = detectorData[selectedDetector];
            
            // Update map
            const mapData = [{
                type: 'scattermapbox',
                lat: [data.lat],
                lon: [data.lon],
                mode: 'markers',
                marker: {
                    size: 15,
                    color: data.problematic ? 'red' : 'green'
                },
                text: selectedDetector,
                hovertemplate: '<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>'
            }];
            
            const layout = {
                mapbox: {
                    style: 'open-street-map',
                    center: { lat: data.lat, lon: data.lon },
                    zoom: 12
                },
                margin: { r: 0, t: 0, l: 0, b: 0 }
            };
            
            Plotly.newPlot('map', mapData, layout);
            
            // Update stats
            document.getElementById('stats-content').innerHTML = data.stats;
        }
        
        // Initialize empty map
        const initialLayout = {
            mapbox: {
                style: 'open-street-map',
                center: { lat: 50.8, lon: 22.7 },
                zoom: 8
            },
            margin: { r: 0, t: 0, l: 0, b: 0 }
        };
        
        Plotly.newPlot('map', [], initialLayout);
    </script>
</body>
</html>
"""
        
        # Save and open HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            html_file = f.name
        
        webbrowser.open('file://' + html_file)
        print(f"Visualization opened in browser: {html_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DetectorVisualizationTool(root)
    root.mainloop()