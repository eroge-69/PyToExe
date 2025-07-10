import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import struct
import os
from typing import Dict, List, Optional, Tuple
import json

class SarinCapFileAnalyzer:
    """
    Sarin Technologies DiaExpert .cap file analyzer for 3D modeling data
    """
    
    def __init__(self):
        self.cap_data = {}
        self.file_path = None
        
    def read_cap_file(self, file_path: str) -> Dict:
        """Read and parse Sarin .cap file"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Parse file header
            header = self._parse_header(data)
            
            # Parse data sections
            sections = self._parse_sections(data, header)
            
            return {
                'header': header,
                'sections': sections,
                'file_size': len(data),
                'file_path': file_path
            }
            
        except Exception as e:
            raise Exception(f"Error reading .cap file: {str(e)}")
    
    def _parse_header(self, data: bytes) -> Dict:
        """Parse .cap file header"""
        header = {}
        try:
            # Basic header structure (this is a simplified example)
            header['magic'] = data[:4].decode('ascii', errors='ignore')
            header['version'] = struct.unpack('<I', data[4:8])[0]
            header['sections_count'] = struct.unpack('<I', data[8:12])[0]
            header['file_size'] = struct.unpack('<I', data[12:16])[0]
            
        except Exception as e:
            header['error'] = f"Header parsing error: {str(e)}"
            
        return header
    
    def _parse_sections(self, data: bytes, header: Dict) -> Dict:
        """Parse data sections from .cap file"""
        sections = {}
        
        # DiaExpert Surface Model Sections
        surface_sections = [
            'SURFACE_MESH',
            'SURFACE_POINTS', 
            'SURFACE_NORMALS',
            'SURFACE_TOPOLOGY',
            'SURFACE_QUALITY'
        ]
        
        # DiaExpert Measurement Sections
        measurement_sections = [
            'PROPORTION_DATA',
            'SYMMETRY_DATA',
            'POLISH_DATA',
            'ANGLES_DATA',
            'DIMENSIONS_DATA'
        ]
        
        # DiaExpert Analysis Sections
        analysis_sections = [
            'CUT_ANALYSIS',
            'LIGHT_PERFORMANCE',
            'INCLUSIONS_MAP',
            'GIRDLE_ANALYSIS'
        ]
        
        # Technical Sections
        technical_sections = [
            'SCAN_METADATA',
            'CALIBRATION_DATA',
            'PROCESSING_LOG'
        ]
        
        all_sections = surface_sections + measurement_sections + analysis_sections + technical_sections
        
        for section_name in all_sections:
            sections[section_name] = self._find_section_data(data, section_name)
            
        return sections
    
    def _find_section_data(self, data: bytes, section_name: str) -> Dict:
        """Find and extract section data"""
        section_info = {
            'name': section_name,
            'found': False,
            'size': 0,
            'offset': 0,
            'data_preview': None
        }
        
        try:
            # Search for section identifier in binary data
            section_bytes = section_name.encode('ascii')
            offset = data.find(section_bytes)
            
            if offset != -1:
                section_info['found'] = True
                section_info['offset'] = offset
                
                # Try to determine section size (simplified approach)
                remaining_data = data[offset:]
                section_info['size'] = min(1024, len(remaining_data))  # Limit preview size
                
                # Extract preview data
                preview_data = remaining_data[:section_info['size']]
                section_info['data_preview'] = preview_data[:100].hex()  # First 100 bytes as hex
                
        except Exception as e:
            section_info['error'] = str(e)
            
        return section_info

class SarinCapGUI:
    """
    GUI application for Sarin DiaExpert .cap file analysis
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sarin DiaExpert .cap File 3D Modeling Analyzer")
        self.root.geometry("1200x800")
        
        self.analyzer = SarinCapFileAnalyzer()
        self.current_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Sarin DiaExpert® 3D Rough Model Analyzer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Select .cap File", command=self.select_file).grid(row=0, column=0, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly').grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(file_frame, text="Analyze", command=self.analyze_file).grid(row=0, column=2, padx=(10, 0))
        
        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_file_info_tab()
        self.create_surface_model_tab()
        self.create_measurement_tab()
        self.create_analysis_tab()
        self.create_technical_tab()
        
    def create_file_info_tab(self):
        """Create file information tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="File Info")
        
        # File info text widget
        self.file_info_text = tk.Text(frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.file_info_text.yview)
        self.file_info_text.configure(yscrollcommand=scrollbar.set)
        
        self.file_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
    def create_surface_model_tab(self):
        """Create DiaExpert Surface Model tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="3D Surface Model")
        
        # Surface model sections
        surface_sections = [
            'SURFACE_MESH',
            'SURFACE_POINTS', 
            'SURFACE_NORMALS',
            'SURFACE_TOPOLOGY',
            'SURFACE_QUALITY'
        ]
        
        self.surface_tree = self.create_section_tree(frame, surface_sections)
        
    def create_measurement_tab(self):
        """Create DiaExpert Measurement tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Measurements")
        
        # Measurement sections
        measurement_sections = [
            'PROPORTION_DATA',
            'SYMMETRY_DATA',
            'POLISH_DATA',
            'ANGLES_DATA',
            'DIMENSIONS_DATA'
        ]
        
        self.measurement_tree = self.create_section_tree(frame, measurement_sections)
        
    def create_analysis_tab(self):
        """Create DiaExpert Analysis tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Analysis")
        
        # Analysis sections
        analysis_sections = [
            'CUT_ANALYSIS',
            'LIGHT_PERFORMANCE',
            'INCLUSIONS_MAP',
            'GIRDLE_ANALYSIS'
        ]
        
        self.analysis_tree = self.create_section_tree(frame, analysis_sections)
        
    def create_technical_tab(self):
        """Create Technical sections tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Technical")
        
        # Technical sections
        technical_sections = [
            'SCAN_METADATA',
            'CALIBRATION_DATA',
            'PROCESSING_LOG'
        ]
        
        self.technical_tree = self.create_section_tree(frame, technical_sections)
        
    def create_section_tree(self, parent, sections):
        """Create a treeview for section data"""
        # Create treeview
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        tree = ttk.Treeview(tree_frame, columns=('Status', 'Size', 'Offset'), show='tree headings')
        tree.heading('#0', text='Section')
        tree.heading('Status', text='Status')
        tree.heading('Size', text='Size (bytes)')
        tree.heading('Offset', text='Offset')
        
        tree.column('#0', width=200)
        tree.column('Status', width=100)
        tree.column('Size', width=100)
        tree.column('Offset', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        return tree
        
    def select_file(self):
        """Select .cap file"""
        file_path = filedialog.askopenfilename(
            title="Select Sarin .cap File",
            filetypes=[("CAP files", "*.cap"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            
    def analyze_file(self):
        """Analyze the selected .cap file"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a .cap file first")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Selected file does not exist")
            return
            
        try:
            # Show progress
            self.root.config(cursor="wait")
            self.root.update()
            
            # Analyze file
            self.current_data = self.analyzer.read_cap_file(file_path)
            
            # Update UI
            self.update_file_info()
            self.update_section_trees()
            
            messagebox.showinfo("Success", "File analyzed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze file: {str(e)}")
            
        finally:
            self.root.config(cursor="")
            
    def update_file_info(self):
        """Update file information display"""
        if not self.current_data:
            return
            
        info_text = f"""Sarin DiaExpert® 3D Rough Model Analysis
{'='*50}

File Path: {self.current_data['file_path']}
File Size: {self.current_data['file_size']:,} bytes

Header Information:
{'-'*20}
"""
        
        for key, value in self.current_data['header'].items():
            info_text += f"{key}: {value}\n"
            
        info_text += f"\nData Sections Found: {len(self.current_data['sections'])}\n"
        info_text += f"\nDiaExpert 3D Surface Model Sections:\n{'-'*40}\n"
        
        surface_sections = ['SURFACE_MESH', 'SURFACE_POINTS', 'SURFACE_NORMALS', 
                           'SURFACE_TOPOLOGY', 'SURFACE_QUALITY']
        
        for section in surface_sections:
            if section in self.current_data['sections']:
                found = self.current_data['sections'][section]['found']
                status = "✓ Found" if found else "✗ Not Found"
                info_text += f"{section}: {status}\n"
                
        self.file_info_text.delete(1.0, tk.END)
        self.file_info_text.insert(1.0, info_text)
        
    def update_section_trees(self):
        """Update all section trees"""
        if not self.current_data:
            return
            
        trees = [
            (self.surface_tree, ['SURFACE_MESH', 'SURFACE_POINTS', 'SURFACE_NORMALS', 
                                'SURFACE_TOPOLOGY', 'SURFACE_QUALITY']),
            (self.measurement_tree, ['PROPORTION_DATA', 'SYMMETRY_DATA', 'POLISH_DATA', 
                                    'ANGLES_DATA', 'DIMENSIONS_DATA']),
            (self.analysis_tree, ['CUT_ANALYSIS', 'LIGHT_PERFORMANCE', 'INCLUSIONS_MAP', 
                                 'GIRDLE_ANALYSIS']),
            (self.technical_tree, ['SCAN_METADATA', 'CALIBRATION_DATA', 'PROCESSING_LOG'])
        ]
        
        for tree, sections in trees:
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
                
            # Add section data
            for section in sections:
                if section in self.current_data['sections']:
                    section_data = self.current_data['sections'][section]
                    status = "Found" if section_data['found'] else "Not Found"
                    size = section_data['size'] if section_data['found'] else 0
                    offset = section_data['offset'] if section_data['found'] else 0
                    
                    tree.insert('', 'end', text=section, values=(status, size, offset))
                    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SarinCapGUI()
    app.run()