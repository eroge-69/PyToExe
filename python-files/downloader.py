import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import csv
import os
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
import re
import time
import ssl
import threading
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

class ExcelReader:
    """Simple Excel reader using only built-in Python libraries"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.shared_strings = []
        self.worksheets = {}
        
    def read_excel(self):
        """Read Excel file and return headers and data"""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_file:
                # Read shared strings
                try:
                    shared_strings_xml = zip_file.read('xl/sharedStrings.xml')
                    self._parse_shared_strings(shared_strings_xml)
                except KeyError:
                    # No shared strings file
                    pass
                
                # Find worksheet files
                try:
                    workbook_xml = zip_file.read('xl/workbook.xml')
                    sheet_names = self._get_sheet_names(workbook_xml)
                except KeyError:
                    sheet_names = {'sheet1': 'xl/worksheets/sheet1.xml'}
                
                # Read first worksheet
                first_sheet_path = list(sheet_names.values())[0]
                try:
                    worksheet_xml = zip_file.read(first_sheet_path)
                    return self._parse_worksheet(worksheet_xml)
                except KeyError as e:
                    # Try alternative paths
                    for alt_path in ['xl/worksheets/sheet1.xml', 'xl/worksheets/sheet.xml']:
                        try:
                            worksheet_xml = zip_file.read(alt_path)
                            return self._parse_worksheet(worksheet_xml)
                        except KeyError:
                            continue
                    raise Exception(f"Could not find worksheet in Excel file: {e}")
                    
        except zipfile.BadZipFile:
            raise Exception("Invalid Excel file format")
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def _parse_shared_strings(self, xml_content):
        """Parse shared strings XML"""
        try:
            root = ET.fromstring(xml_content)
            # Handle namespaces
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            
            for si in root.findall('.//main:si', ns):
                t_elem = si.find('.//main:t', ns)
                if t_elem is not None:
                    self.shared_strings.append(t_elem.text or '')
                else:
                    self.shared_strings.append('')
        except ET.ParseError:
            # Try without namespace
            try:
                root = ET.fromstring(xml_content)
                for si in root.findall('.//si'):
                    t_elem = si.find('.//t')
                    if t_elem is not None:
                        self.shared_strings.append(t_elem.text or '')
                    else:
                        self.shared_strings.append('')
            except:
                pass
    
    def _get_sheet_names(self, xml_content):
        """Get sheet names and their file paths"""
        try:
            root = ET.fromstring(xml_content)
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            
            sheets = {}
            for sheet in root.findall('.//main:sheet', ns):
                name = sheet.get('name', 'Sheet1')
                r_id = sheet.get('r:id') or sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                if r_id:
                    # Simple mapping - most Excel files follow this pattern
                    sheet_num = r_id.replace('rId', '')
                    sheets[name] = f'xl/worksheets/sheet{sheet_num}.xml'
                else:
                    sheets[name] = 'xl/worksheets/sheet1.xml'
            
            return sheets if sheets else {'Sheet1': 'xl/worksheets/sheet1.xml'}
        except:
            return {'Sheet1': 'xl/worksheets/sheet1.xml'}
    
    def _parse_worksheet(self, xml_content):
        """Parse worksheet XML and return data"""
        try:
            root = ET.fromstring(xml_content)
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            
            # Find all rows
            rows_data = defaultdict(dict)
            
            # Try with namespace first
            rows = root.findall('.//main:row', ns)
            if not rows:
                # Try without namespace
                rows = root.findall('.//row')
            
            for row in rows:
                row_num = int(row.get('r', 0))
                if row_num == 0:
                    continue
                
                # Find cells in this row
                cells = row.findall('.//main:c', ns) if row.findall('.//main:c', ns) else row.findall('.//c')
                
                for cell in cells:
                    cell_ref = cell.get('r', '')
                    col_letter = ''.join(c for c in cell_ref if c.isalpha())
                    col_num = self._column_letter_to_number(col_letter)
                    
                    cell_type = cell.get('t', '')
                    value_elem = cell.find('.//main:v', ns) if cell.find('.//main:v', ns) is not None else cell.find('.//v')
                    
                    if value_elem is not None:
                        value = value_elem.text or ''
                        
                        # Handle shared strings
                        if cell_type == 's' and value.isdigit():
                            string_index = int(value)
                            if 0 <= string_index < len(self.shared_strings):
                                value = self.shared_strings[string_index]
                        
                        rows_data[row_num][col_num] = value
                    else:
                        rows_data[row_num][col_num] = ''
            
            # Convert to list format
            if not rows_data:
                return [], []
            
            max_row = max(rows_data.keys())
            max_col = max(max(row.keys()) if row else [0] for row in rows_data.values())
            
            result = []
            for row_num in range(1, max_row + 1):
                row_data = []
                for col_num in range(1, max_col + 1):
                    row_data.append(rows_data[row_num].get(col_num, ''))
                result.append(row_data)
            
            if result:
                headers = result[0]
                data = result[1:]
                return headers, data
            else:
                return [], []
                
        except Exception as e:
            raise Exception(f"Error parsing worksheet: {str(e)}")
    
    def _column_letter_to_number(self, column_letter):
        """Convert column letter to number (A=1, B=2, etc.)"""
        if not column_letter:
            return 1
        result = 0
        for char in column_letter:
            result = result * 26 + (ord(char.upper()) - ord('A') + 1)
        return result

class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Image Downloader - Excel Support")
        self.root.geometry("800x750")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.file_path = tk.StringVar()
        self.output_folder = tk.StringVar(value="Downloaded_Images")
        self.max_images = tk.IntVar(value=6)
        self.unit_column = tk.StringVar()
        self.notes_column = tk.StringVar()
        self.url_columns = []
        self.data = []
        self.headers = []
        self.is_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main title
        title_label = tk.Label(self.root, text="Universal Image Downloader", 
                              font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(self.root, text="Now supports Excel files directly!", 
                                 font=('Arial', 10, 'italic'), bg='#f0f0f0', fg='#27ae60')
        subtitle_label.pack(pady=(0, 10))
        
        # File selection frame
        file_frame = tk.LabelFrame(self.root, text="1. Select Excel or CSV File", 
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        file_frame.pack(fill='x', padx=20, pady=10)
        
        file_path_frame = tk.Frame(file_frame, bg='#f0f0f0')
        file_path_frame.pack(fill='x')
        
        tk.Entry(file_path_frame, textvariable=self.file_path, font=('Arial', 10), 
                state='readonly', width=60).pack(side='left', fill='x', expand=True)
        
        tk.Button(file_path_frame, text="Browse", command=self.browse_file,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold')).pack(side='right', padx=(10, 0))
        
        # Configuration frame
        config_frame = tk.LabelFrame(self.root, text="2. Configure Settings", 
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        config_frame.pack(fill='x', padx=20, pady=10)
        
        # Output folder
        output_frame = tk.Frame(config_frame, bg='#f0f0f0')
        output_frame.pack(fill='x', pady=5)
        tk.Label(output_frame, text="Output Folder Name:", bg='#f0f0f0', font=('Arial', 10)).pack(side='left')
        tk.Entry(output_frame, textvariable=self.output_folder, font=('Arial', 10), width=30).pack(side='left', padx=(10, 0))
        
        # Max images
        max_img_frame = tk.Frame(config_frame, bg='#f0f0f0')
        max_img_frame.pack(fill='x', pady=5)
        tk.Label(max_img_frame, text="Max Images per Unit:", bg='#f0f0f0', font=('Arial', 10)).pack(side='left')
        tk.Spinbox(max_img_frame, from_=1, to=20, textvariable=self.max_images, 
                  font=('Arial', 10), width=10).pack(side='left', padx=(10, 0))
        
        # Column selection frame
        column_frame = tk.LabelFrame(self.root, text="3. Select Columns", 
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        column_frame.pack(fill='x', padx=20, pady=10)
        
        # Unit column
        unit_frame = tk.Frame(column_frame, bg='#f0f0f0')
        unit_frame.pack(fill='x', pady=5)
        tk.Label(unit_frame, text="Unit/Name Column:", bg='#f0f0f0', font=('Arial', 10)).pack(side='left')
        self.unit_combo = ttk.Combobox(unit_frame, textvariable=self.unit_column, 
                                      font=('Arial', 10), width=30, state='readonly')
        self.unit_combo.pack(side='left', padx=(10, 0))
        
        # Notes column
        notes_frame = tk.Frame(column_frame, bg='#f0f0f0')
        notes_frame.pack(fill='x', pady=5)
        tk.Label(notes_frame, text="Notes Column (optional):", bg='#f0f0f0', font=('Arial', 10)).pack(side='left')
        self.notes_combo = ttk.Combobox(notes_frame, textvariable=self.notes_column, 
                                       font=('Arial', 10), width=30, state='readonly')
        self.notes_combo.pack(side='left', padx=(10, 0))
        
        # URL columns
        url_frame = tk.Frame(column_frame, bg='#f0f0f0')
        url_frame.pack(fill='both', expand=True, pady=5)
        tk.Label(url_frame, text="URL Columns (check all that contain image URLs):", 
                bg='#f0f0f0', font=('Arial', 10)).pack(anchor='w')
        
        # Scrollable frame for checkboxes
        self.url_canvas = tk.Canvas(url_frame, bg='#f0f0f0', height=100)
        self.url_scrollbar = ttk.Scrollbar(url_frame, orient="vertical", command=self.url_canvas.yview)
        self.url_scrollable_frame = tk.Frame(self.url_canvas, bg='#f0f0f0')
        
        self.url_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.url_canvas.configure(scrollregion=self.url_canvas.bbox("all"))
        )
        
        self.url_canvas.create_window((0, 0), window=self.url_scrollable_frame, anchor="nw")
        self.url_canvas.configure(yscrollcommand=self.url_scrollbar.set)
        
        self.url_canvas.pack(side="left", fill="both", expand=True)
        self.url_scrollbar.pack(side="right", fill="y")
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        self.analyze_btn = tk.Button(button_frame, text="Analyze File", command=self.analyze_file,
                                    bg='#e67e22', fg='white', font=('Arial', 12, 'bold'))
        self.analyze_btn.pack(side='left', padx=(0, 10))
        
        self.download_btn = tk.Button(button_frame, text="Start Download", command=self.start_download,
                                     bg='#27ae60', fg='white', font=('Arial', 12, 'bold'), state='disabled')
        self.download_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_download,
                                 bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'), state='disabled')
        self.stop_btn.pack(side='left')
        
        # Progress frame
        progress_frame = tk.LabelFrame(self.root, text="Progress", 
                                      font=('Arial', 12, 'bold'), bg='#f0f0f0', padx=10, pady=10)
        progress_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)
        
        self.status_label = tk.Label(progress_frame, text="Ready to start", 
                                    bg='#f0f0f0', font=('Arial', 10))
        self.status_label.pack(pady=5)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=8, font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True, pady=5)
        
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def browse_file(self):
        """Open file dialog to select Excel or CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel or CSV file",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.file_path.set(file_path)
            self.log_message(f"Selected file: {file_path}")
            
    def analyze_file(self):
        """Analyze the selected file and populate column options"""
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select a file first!")
            return
            
        try:
            self.log_message("Analyzing file...")
            file_path = self.file_path.get()
            
            if file_path.lower().endswith('.csv'):
                self.analyze_csv()
            else:
                self.analyze_excel()
                
            self.populate_column_options()
            self.download_btn.config(state='normal')
            self.log_message("File analysis complete!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing file: {str(e)}")
            self.log_message(f"Error: {str(e)}")
            
    def analyze_csv(self):
        """Analyze CSV file"""
        with open(self.file_path.get(), 'r', encoding='utf-8', newline='') as csvfile:
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            try:
                delimiter = sniffer.sniff(sample).delimiter
            except:
                delimiter = ','
                
            reader = csv.reader(csvfile, delimiter=delimiter)
            rows = list(reader)
            
        if rows:
            self.headers = [str(h) for h in rows[0]]
            self.data = rows[1:]
        else:
            raise Exception("CSV file is empty")
            
    def analyze_excel(self):
        """Analyze Excel file using built-in libraries"""
        try:
            excel_reader = ExcelReader(self.file_path.get())
            headers, data = excel_reader.read_excel()
            
            if not headers:
                raise Exception("Excel file appears to be empty or unreadable")
                
            self.headers = [str(h) for h in headers]
            self.data = [[str(cell) for cell in row] for row in data]
            
            self.log_message(f"Successfully read Excel file: {len(self.data)} rows, {len(self.headers)} columns")
            
        except Exception as e:
            raise Exception(f"Could not read Excel file: {str(e)}")
            
    def populate_column_options(self):
        """Populate column selection options"""
        # Add "None" option for optional columns
        column_options = ["(None)"] + self.headers
        
        # Unit column dropdown
        self.unit_combo['values'] = self.headers
        
        # Notes column dropdown (with None option)
        self.notes_combo['values'] = column_options
        self.notes_column.set("(None)")
        
        # Auto-select unit column
        unit_keywords = ['unit', 'apartment', 'room', 'number', 'name', 'id']
        for i, header in enumerate(self.headers):
            if any(keyword in str(header).lower() for keyword in unit_keywords):
                self.unit_column.set(header)
                break
        else:
            self.unit_column.set(self.headers[0] if self.headers else "")
            
        # Auto-select notes column
        notes_keywords = ['note', 'comment', 'description', 'remark', 'detail']
        for i, header in enumerate(self.headers):
            if any(keyword in str(header).lower() for keyword in notes_keywords):
                self.notes_column.set(header)
                break
            
        # Clear existing URL checkboxes
        for widget in self.url_scrollable_frame.winfo_children():
            widget.destroy()
        self.url_columns = []
        
        # Create URL column checkboxes
        url_keywords = ['url', 'link', 'image', 'photo', 'picture', 'img', 'http']
        for i, header in enumerate(self.headers):
            var = tk.BooleanVar()
            
            # Auto-select if header suggests URLs
            if any(keyword in str(header).lower() for keyword in url_keywords):
                var.set(True)
            else:
                # Check sample data for URLs
                sample_count = min(10, len(self.data))
                url_count = 0
                for row in self.data[:sample_count]:
                    if i < len(row) and row[i]:
                        value = str(row[i]).lower()
                        if any(pattern in value for pattern in ['http', 'www.', '.jpg', '.jpeg', '.png']):
                            url_count += 1
                if url_count > 0:
                    var.set(True)
                    
            checkbox = tk.Checkbutton(self.url_scrollable_frame, text=header, variable=var,
                                     bg='#f0f0f0', font=('Arial', 9))
            checkbox.pack(anchor='w', padx=10, pady=2)
            self.url_columns.append((header, var))
            
    def start_download(self):
        """Start the download process in a separate thread"""
        if self.is_running:
            return
            
        # Validate selections
        if not self.unit_column.get():
            messagebox.showerror("Error", "Please select a unit column!")
            return
            
        selected_url_columns = [header for header, var in self.url_columns if var.get()]
        if not selected_url_columns:
            messagebox.showwarning("Warning", "No URL columns selected. Only folders will be created.")
            
        self.is_running = True
        self.download_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.analyze_btn.config(state='disabled')
        
        # Start download in separate thread
        thread = threading.Thread(target=self.download_images)
        thread.daemon = True
        thread.start()
        
    def stop_download(self):
        """Stop the download process"""
        self.is_running = False
        self.download_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.analyze_btn.config(state='normal')
        self.log_message("Download stopped by user")
        
    def clean_filename(self, filename):
        """Clean filename to be filesystem-safe"""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename.strip('. ')
        return filename[:255]
        
    def create_notes_file(self, unit_folder, unit_name, notes_content, all_data_row):
        """Create a notes text file for the unit"""
        try:
            notes_file_path = os.path.join(unit_folder, f"{self.clean_filename(unit_name)}_notes.txt")
            
            with open(notes_file_path, 'w', encoding='utf-8') as notes_file:
                notes_file.write(f"Notes for Unit: {unit_name}\n")
                notes_file.write("=" * 50 + "\n\n")
                
                # Write specific notes if available
                if notes_content and notes_content.strip() and notes_content.lower() != 'nan':
                    notes_file.write("Notes:\n")
                    notes_file.write(notes_content.strip() + "\n\n")
                
                # Write all additional data
                notes_file.write("Additional Information:\n")
                notes_file.write("-" * 30 + "\n")
                
                for i, (header, value) in enumerate(zip(self.headers, all_data_row)):
                    if value and str(value).strip() and str(value).lower() != 'nan':
                        notes_file.write(f"{header}: {value}\n")
                
                notes_file.write(f"\nGenerated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
            return True
        except Exception as e:
            self.log_message(f"  ⚠️  Could not create notes file: {str(e)}")
            return False
        
    def download_image(self, url, filepath, timeout=30):
        """Download image from URL"""
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
                with open(filepath, 'wb') as f:
                    f.write(response.read())
                    
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                return True
            else:
                if os.path.exists(filepath):
                    os.remove(filepath)
                return False
                
        except Exception as e:
            return False
            
    def download_images(self):
        """Main download process"""
        try:
            output_folder = self.output_folder.get()
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                
            self.log_message(f"Created output folder: {output_folder}")
            
            # Get selected columns
            unit_column = self.unit_column.get()
            unit_col_index = self.headers.index(unit_column)
            
            notes_column = self.notes_column.get()
            notes_col_index = -1
            if notes_column != "(None)":
                notes_col_index = self.headers.index(notes_column)
            
            selected_url_columns = []
            for header, var in self.url_columns:
                if var.get():
                    selected_url_columns.append((self.headers.index(header), header))
                    
            self.log_message(f"Processing {len(self.data)} rows...")
            self.log_message(f"Unit column: {unit_column}")
            if notes_col_index >= 0:
                self.log_message(f"Notes column: {notes_column}")
            self.log_message(f"URL columns: {[header for _, header in selected_url_columns]}")
            
            total_downloaded = 0
            no_name_counter = 1
            
            # Setup progress bar
            self.progress_bar['maximum'] = len(self.data)
            
            for row_index, row in enumerate(self.data):
                if not self.is_running:
                    break
                    
                # Update progress
                self.progress_bar['value'] = row_index + 1
                self.status_label.config(text=f"Processing row {row_index + 1} of {len(self.data)}")
                
                # Get unit name
                unit_name = ""
                if unit_col_index < len(row) and row[unit_col_index]:
                    unit_name = str(row[unit_col_index]).strip()
                    
                if not unit_name or unit_name.lower() == 'nan' or unit_name == '':
                    unit_name = f"no_name_given_{no_name_counter}"
                    no_name_counter += 1
                    self.log_message(f"Row {row_index + 2}: No unit name, using: {unit_name}")
                    
                # Create unit folder
                clean_unit_name = self.clean_filename(unit_name)
                unit_folder = os.path.join(output_folder, clean_unit_name)
                
                if not os.path.exists(unit_folder):
                    os.makedirs(unit_folder)
                    
                self.log_message(f"🏠 Processing: {unit_name}")
                
                # Create notes file (always create it with all data)
                notes_content = ""
                if notes_col_index >= 0 and notes_col_index < len(row):
                    notes_content = str(row[notes_col_index]) if row[notes_col_index] else ""
                
                if self.create_notes_file(unit_folder, unit_name, notes_content, row):
                    self.log_message(f"  📝 Created notes file")
                
                # Download images with column header names
                image_count = 0
                for col_index, col_header in selected_url_columns:
                    if image_count >= self.max_images.get():
                        break
                        
                    if col_index >= len(row) or not row[col_index]:
                        continue
                        
                    url = str(row[col_index]).strip()
                    if not url or url.lower() == 'nan':
                        continue
                        
                    # Clean URL
                    if not (url.startswith('http://') or url.startswith('https://')):
                        if url.startswith('www'):
                            url = 'http://' + url
                        elif '.' in url:
                            url = 'http://' + url
                        else:
                            continue
                            
                    # Generate filename using column header
                    clean_header = self.clean_filename(col_header)
                    filename = f"{clean_header}.jpg"
                    
                    # If file already exists, add number
                    counter = 1
                    original_filename = filename
                    while os.path.exists(os.path.join(unit_folder, filename)):
                        name_part = clean_header
                        filename = f"{name_part}_{counter}.jpg"
                        counter += 1
                        
                    filepath = os.path.join(unit_folder, filename)
                    
                    # Download image
                    if self.download_image(url, filepath):
                        image_count += 1
                        total_downloaded += 1
                        self.log_message(f"  ✅ Downloaded: {filename}")
                    else:
                        self.log_message(f"  ❌ Failed to download from: {col_header}")
                    
                    time.sleep(0.1)  # Small delay
                    
                self.log_message(f"  📸 Downloaded {image_count} images for {unit_name}")
                
            if self.is_running:
                self.log_message(f"\n✅ Process completed!")
                self.log_message(f"📊 Total images downloaded: {total_downloaded}")
                self.log_message(f"📁 Output folder: {os.path.abspath(output_folder)}")
                messagebox.showinfo("Complete", f"Download completed!\nTotal images: {total_downloaded}\nOutput folder: {output_folder}")
            
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.is_running = False
            self.download_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.analyze_btn.config(state='normal')
            self.status_label.config(text="Ready")

def main():
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()