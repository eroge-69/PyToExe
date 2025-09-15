import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

class WimaDecoder:
    def __init__(self, root):
        self.root = root
        self.root.title("WIMA Part Number Decoder")
        self.root.geometry("1400x800")
        
        # Initialize lookup dictionaries
        self.init_lookup_tables()
        
        # Store decoded parts for comparison
        self.decoded_parts = []
        
        # Default maximum parts (can be changed in GUI)
        self.max_parts = 10
        
        # Create GUI
        self.create_widgets()
        
    def init_lookup_tables(self):
        """Initialize all lookup dictionaries based on the WIMA specification"""
        
        # Type designations
        self.types = {
            'SMDT': 'SMD-PET',
            'SMDI': 'SMD-PPS', 
            'FKP0': 'FKP 02',
            'MKS0': 'MKS 02',
            'FKS2': 'FKS 2',
            'FKP2': 'FKP 2',
            'FKS3': 'FKS 3',
            'FKP3': 'FKP 3',
            'MKS2': 'MKS 2',
            'MKP2': 'MKP 2',
            'MKS4': 'MKS 4',
            'MKP4': 'MKP 4',
            'MKP1': 'MKP 10',
            'FKP4': 'FKP 4',
            'FKP1': 'FKP 1',
            'MKX2': 'MKP-X2',
            'MKX1': 'MKP-X1 R',
            'MKY2': 'MKP-Y2',
            'MKPF': 'MKP 4F',
            'SNMP': 'Snubber MKP',
            'SNFP': 'Snubber FKP',
            'GTOM': 'GTO MKP',
            'DCP4': 'DC-LINK MKP 4',
            'DCP6': 'DC-LINK MKP 6',
            'DCHC': 'DC-LINK HC'
        }
        
        # Voltages
        self.voltages = {
            'B0': '50 V-',
            'C0': '63 V-',
            'D0': '100 V-',
            'F0': '250 V-',
            'G0': '400 V-',
            'H0': '450 V-',
            'H2': '520 V-',
            'I0': '600 V-',
            'J0': '630 V-',
            'K0': '700 V-',
            'L0': '800 V-',
            'M0': '850 V-',
            'N0': '900 V-',
            'O1': '1000 V-',
            'P0': '1100 V-',
            'Q0': '1200 V-',
            'R0': '1250 V-',
            'S0': '1500 V-',
            'T0': '1600 V-',
            'TA': '1700 V-',
            'U0': '2000 V-',
            'V0': '2500 V-',
            'W0': '3000 V-',
            'X0': '4000 V-',
            'Y0': '6000 V-',
            '3Y': '230 V~',
            '1W': '275 V~',
            '2W': '300 V~',
            'AW': '305 V~',
            'BW': '350 V~',
            '4W': '440 V~'
        }
        
        # Capacitances
        self.capacitances = {
            '0022': '22 pF',
            '0047': '47 pF',
            '0100': '100 pF',
            '0150': '150 pF',
            '0220': '220 pF',
            '0330': '330 pF',
            '0470': '470 pF',
            '0680': '680 pF',
            '1100': '1000 pF',
            '1150': '1500 pF',
            '1220': '2200 pF',
            '1330': '3300 pF',
            '1470': '4700 pF',
            '1680': '6800 pF',
            '2100': '0.01 µF',
            '2220': '0.022 µF',
            '2470': '0.047 µF',
            '3100': '0.1 µF',
            '3220': '0.22 µF',
            '3470': '0.47 µF',
            '4100': '1 µF',
            '4220': '2.2 µF',
            '4470': '4.7 µF',
            '5100': '10 µF',
            '5220': '22 µF',
            '5470': '47 µF',
            '6100': '100 µF',
            '6220': '220 µF',
            '7100': '1000 µF',
            '7150': '1500 µF'
        }
        
        # Package types
        self.packages = {
            'KA': '4.8x3.3x3 Size1812',
            'KB': '4.8x3.3x4 Size1812',
            'QA': '5.7x5.1x3.5 Size2220',
            'QB': '5.7x5.1x4.5 Size2220',
            'TA': '7.2x6.1x3 Size2824',
            'TB': '7.2x6.1x5 Size2824',
            'VA': '10.2x7.6x5 Size4030',
            'XA': '12.7x10.2x6 Size5040',
            'YA': '15.3x13.7x7 Size6054',
            '0B': '2.5x7x4.6 RM2.5',
            '0C': '3x7.5x4.6 RM2.5',
            '1A': '2.5x6.5x7.2 RM5',
            '1B': '3x7.5x7.2 RM5',
            '2A': '2.5x7x10 RM7.5',
            '2B': '3x8.5x10 RM7.5',
            '3A': '3x9x13 RM10',
            '3C': '4x9x13 RM10',
            '4B': '5x11x18 RM15',
            '4C': '6x12.5x18 RM15',
            '5A': '5x14x26.5 RM22.5',
            '5B': '6x15x26.5 RM22.5',
            '6A': '9x19x31.5 RM27.5',
            '6B': '11x21x31.5 RM27.5',
            '7A': '9x19x41.5 RM37.5',
            '7B': '11x22x41.5 RM37.5',
            '8D': '19x31x56 RM48.5',
            '9D': '25x45x57 RM52.5'
        }
        
        # Version codes
        self.versions = {
            '00': 'Standard',
            '1A': 'Version A1',
            '1B': 'Version A1.1.1',
            '2A': 'Version A2'
        }
        
        # Tolerances
        self.tolerances = {
            'M': '±20%',
            'K': '±10%',
            'J': '±5%',
            'H': '±2.5%',
            'E': '±1%'
        }
        
        # Packaging
        self.packaging = {
            'A': 'AMMO H16.5 340x340',
            'B': 'AMMO H16.5 490x370',
            'C': 'AMMO H18.5 340x340',
            'D': 'AMMO H18.5 490x370',
            'F': 'REEL H16.5 360',
            'H': 'REEL H16.5 500',
            'I': 'REEL H18.5 360',
            'J': 'REEL H18.5 500',
            'N': 'ROLL H16.5',
            'O': 'ROLL H18.5',
            'P': 'BLISTER W12 180',
            'Q': 'BLISTER W12 330',
            'R': 'BLISTER W16 330',
            'T': 'BLISTER W24 330',
            'S': 'Schüttware/EPS Standard'
        }
        
        # Wire lengths
        self.wire_lengths = {
            'C9': '3.5±0.5',
            'SD': '6 -2',
            'P1': '16 ±1'
        }
    
    def create_widgets(self):
        """Create the GUI widgets"""
        print("Creating widgets...")  # Debug
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # ========== 1. INPUT SECTION ==========
        input_frame = ttk.LabelFrame(main_frame, text="Input Part Number", padding="5")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Part Number:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.part_entry = ttk.Entry(input_frame, width=25)
        self.part_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.part_entry.bind('<Return>', lambda e: self.decode_part())
        
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=2, padx=(5, 0))
        
        ttk.Button(button_frame, text="Paste from Clipboard", 
                  command=self.paste_from_clipboard).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Add Part", 
                  command=self.decode_part).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all).grid(row=0, column=2)
        
        # ========== 2. SETTINGS SECTION ==========
        print("Creating settings section...")  # Debug
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="5")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(4, weight=1)
        
        # Max Parts setting
        ttk.Label(settings_frame, text="Max Parts:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.max_parts_var = tk.StringVar(value=str(self.max_parts))
        self.max_parts_spinbox = ttk.Spinbox(settings_frame, from_=2, to=20, width=5, 
                                       textvariable=self.max_parts_var)
        self.max_parts_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Button(settings_frame, text="Apply Changes", 
                  command=self.update_max_parts).grid(row=0, column=2, sticky=tk.W, padx=(0, 15))
        
        # Highlight differences toggle
        self.highlight_differences = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Highlight Differences", 
                       variable=self.highlight_differences,
                       command=self.toggle_highlight_differences).grid(row=0, column=3, sticky=tk.W)
        
        # Bind events for auto-apply
        self.max_parts_spinbox.bind('<Return>', lambda e: self.update_max_parts())
        self.max_parts_spinbox.bind('<ButtonRelease-1>', lambda e: self.root.after(100, self.update_max_parts))
        
        # ========== 3. MANAGE PARTS SECTION ==========
        print("Creating manage parts section...")  # Debug
        manage_frame = ttk.LabelFrame(main_frame, text="Manage Parts", padding="5")
        manage_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        manage_frame.columnconfigure(1, weight=1)
        
        ttk.Label(manage_frame, text="Select Part to Remove:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.part_selector = ttk.Combobox(manage_frame, state="readonly", width=30)
        self.part_selector.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        manage_button_frame = ttk.Frame(manage_frame)
        manage_button_frame.grid(row=0, column=2, padx=(5, 0))
        
        ttk.Button(manage_button_frame, text="Remove Selected", 
                  command=self.remove_selected_part).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(manage_button_frame, text="Refresh List", 
                  command=self.update_part_selector).grid(row=0, column=1)
        
        # ========== 4. RESULTS SECTION ==========
        print("Creating results section...")  # Debug
        results_frame = ttk.LabelFrame(main_frame, text="Decoded Results", padding="5")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for comparison table
        self.create_treeview(results_frame)
        
        # Initialize empty comparison table
        self.initialize_comparison_table()
        
        # ========== 5. STATUS BAR ==========
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Enter a WIMA part number to decode")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        print("All widgets created!")  # Debug
    
    def create_treeview(self, parent_frame):
        """Create or recreate the treeview with current max_parts setting"""
        
        # Destroy existing treeview if it exists
        if hasattr(self, 'tree'):
            self.tree.destroy()
        if hasattr(self, 'v_scrollbar'):
            self.v_scrollbar.destroy()
        if hasattr(self, 'h_scrollbar'):
            self.h_scrollbar.destroy()
        
        # Create new treeview with updated columns
        columns = ['Parameter'] + [f'Part {i+1}' for i in range(self.max_parts)]
        self.tree = ttk.Treeview(parent_frame, columns=columns, show='headings', height=15)
        
        # Configure column headings and widths
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Parameter':
                self.tree.column(col, width=150, anchor='w')
            else:
                self.tree.column(col, width=200, anchor='w')
        
        # Configure tags for highlighting differences
        self.tree.tag_configure('different', background='#ffcccc')  # Light red for differences
        self.tree.tag_configure('same', background='#ccffcc')       # Light green for same values
        self.tree.tag_configure('normal', background='white')       # Normal background
        
        # Scrollbars
        self.v_scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=self.tree.yview)
        self.h_scrollbar = ttk.Scrollbar(parent_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Grid the treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def initialize_comparison_table(self):
        """Initialize the comparison table with parameter names"""
        parameters = [
            'Part Number',
            'Type Designation',
            'Rated Voltage',
            'Capacitance',
            'Package/Dimensions',
            'Version Code',
            'Tolerance',
            'Packaging',
            'Wire Length'
        ]
        
        for param in parameters:
            # Create row with parameter name and empty values for all part columns
            values = [param] + [''] * self.max_parts
            self.tree.insert('', 'end', values=values)
    
    def paste_from_clipboard(self):
        """Paste part number from clipboard"""
        try:
            clipboard_content = pyperclip.paste()
            self.part_entry.delete(0, tk.END)
            self.part_entry.insert(0, clipboard_content.strip())
            self.status_var.set(f"Pasted from clipboard: {clipboard_content.strip()}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not paste from clipboard: {str(e)}")
    
    def decode_part(self):
        """Decode the entered part number"""
        part_number = self.part_entry.get().strip().upper()
        
        if not part_number:
            messagebox.showwarning("Warning", "Please enter a part number")
            return
        
        if len(part_number) != 18:
            messagebox.showerror("Error", f"Part number must be exactly 18 characters. Got {len(part_number)} characters.")
            return
        
        # Check if part already exists
        for existing_part in self.decoded_parts:
            if existing_part['part_number'] == part_number:
                messagebox.showinfo("Info", f"Part {part_number} is already in the comparison table.")
                self.part_entry.delete(0, tk.END)
                return
        
        try:
            decoded = self.parse_part_number(part_number)
            self.add_to_comparison(decoded)
            self.update_part_selector()
            self.status_var.set(f"Successfully added: {part_number} (Total: {len(self.decoded_parts)} parts)")
            self.part_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not decode part number: {str(e)}")
    
    def parse_part_number(self, part_number):
        """Parse a WIMA part number into its components"""
        
        # Extract fields according to WIMA specification
        type_code = part_number[0:4]
        voltage_code = part_number[4:6]
        capacitance_code = part_number[6:10]
        package_code = part_number[10:12]
        version_code = part_number[12:14]
        tolerance_code = part_number[14:15]
        packaging_code = part_number[15:16]
        wire_length_code = part_number[16:18]
        
        # Decode each field
        decoded = {
            'part_number': part_number,
            'type': self.types.get(type_code, f"Unknown ({type_code})"),
            'voltage': self.voltages.get(voltage_code, f"Unknown ({voltage_code})"),
            'capacitance': self.capacitances.get(capacitance_code, f"Unknown ({capacitance_code})"),
            'package': self.packages.get(package_code, f"Unknown ({package_code})"),
            'version': self.versions.get(version_code, f"Unknown ({version_code})"),
            'tolerance': self.tolerances.get(tolerance_code, f"Unknown ({tolerance_code})"),
            'packaging': self.packaging.get(packaging_code, f"Unknown ({packaging_code})"),
            'wire_length': self.wire_lengths.get(wire_length_code, f"Unknown ({wire_length_code})")
        }
        
        return decoded
    
    def add_to_comparison(self, decoded_part):
        """Add decoded part to comparison table"""
        
        if len(self.decoded_parts) >= self.max_parts:
            messagebox.showwarning("Warning", f"Maximum of {self.max_parts} parts allowed. Please remove a part first.")
            return
        
        self.decoded_parts.append(decoded_part)
        
        # Find the column index for this part (1-based, since column 0 is Parameter)
        column_index = len(self.decoded_parts)
        
        # Update the tree view
        items = self.tree.get_children()
        
        # Update each row with the new part data
        values_map = {
            'Part Number': decoded_part['part_number'],
            'Type Designation': decoded_part['type'],
            'Rated Voltage': decoded_part['voltage'],
            'Capacitance': decoded_part['capacitance'],
            'Package/Dimensions': decoded_part['package'],
            'Version Code': decoded_part['version'],
            'Tolerance': decoded_part['tolerance'],
            'Packaging': decoded_part['packaging'],
            'Wire Length': decoded_part['wire_length']
        }
        
        for item in items:
            current_values = list(self.tree.item(item, 'values'))
            parameter = current_values[0]
            
            if parameter in values_map:
                current_values[column_index] = values_map[parameter]
                self.tree.item(item, values=current_values)
        
        # Update highlighting if enabled
        if self.highlight_differences.get():
            self.update_highlighting()
    
    def update_max_parts(self):
        """Update the maximum number of parts and recreate the table"""
        try:
            new_max = int(self.max_parts_var.get())
            if new_max < 2:
                messagebox.showerror("Error", "Minimum 2 parts required")
                self.max_parts_var.set(str(self.max_parts))
                return
            if new_max > 20:
                messagebox.showerror("Error", "Maximum 20 parts allowed")
                self.max_parts_var.set(str(self.max_parts))
                return
            
            # If no change, do nothing
            if new_max == self.max_parts:
                return
            
            # If reducing max parts, check if we need to remove existing parts
            if new_max < self.max_parts and len(self.decoded_parts) > new_max:
                result = messagebox.askyesno("Reduce Parts", 
                    f"Changing to {new_max} parts will remove {len(self.decoded_parts) - new_max} existing parts. Continue?")
                if not result:
                    self.max_parts_var.set(str(self.max_parts))
                    return
                
                # Remove excess parts (from the end)
                self.decoded_parts = self.decoded_parts[:new_max]
                self.update_part_selector()
            
            # Store old max for comparison
            old_max = self.max_parts
            self.max_parts = new_max
            
            # Recreate the entire results section
            self.recreate_results_section()
            
            self.status_var.set(f"Updated maximum parts from {old_max} to {new_max} (Current: {len(self.decoded_parts)} parts)")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            self.max_parts_var.set(str(self.max_parts))
    
    def recreate_results_section(self):
        """Recreate the entire results section with new max_parts"""
        # Find and destroy the existing results frame
        main_frame = None
        for child in self.root.winfo_children():
            if isinstance(child, ttk.Frame):
                main_frame = child
                break
        
        if main_frame:
            # Find and destroy the results frame
            for child in main_frame.winfo_children():
                if isinstance(child, ttk.LabelFrame) and hasattr(child, 'cget'):
                    try:
                        if "Decoded Results" in str(child.cget('text')):
                            child.destroy()
                            break
                    except:
                        continue
            
            # Recreate results section
            results_frame = ttk.LabelFrame(main_frame, text="Decoded Results", padding="5")
            results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
            results_frame.columnconfigure(0, weight=1)
            results_frame.rowconfigure(0, weight=1)
            
            # Create new treeview
            self.create_treeview(results_frame)
            
            # Initialize and repopulate
            self.initialize_comparison_table()
            self.repopulate_table()
            
            # Restore highlighting if it was enabled
            if hasattr(self, 'highlight_differences') and self.highlight_differences.get():
                self.update_highlighting()
    
    def repopulate_table(self):
        """Repopulate the table with existing parts after structure change"""
        temp_parts = self.decoded_parts.copy()
        self.decoded_parts = []
        
        for part in temp_parts:
            self.add_to_comparison(part)
    
    def remove_selected_part(self):
        """Remove the selected part from comparison"""
        selected_index = self.part_selector.current()
        
        if selected_index == -1:
            messagebox.showwarning("Warning", "Please select a part to remove")
            return
        
        if selected_index < len(self.decoded_parts):
            removed_part = self.decoded_parts.pop(selected_index)
            self.refresh_comparison_table()
            self.update_part_selector()
            
            # Update highlighting after removal
            if self.highlight_differences.get():
                self.update_highlighting()
            
            self.status_var.set(f"Removed: {removed_part['part_number']} (Total: {len(self.decoded_parts)} parts)")
        else:
            messagebox.showerror("Error", "Invalid part selection")
    
    def update_part_selector(self):
        """Update the part selector combobox with current parts"""
        part_list = [f"{i+1}: {part['part_number']}" for i, part in enumerate(self.decoded_parts)]
        self.part_selector['values'] = part_list
        
        if part_list:
            self.part_selector.set('')
        else:
            self.part_selector.set('')
    
    def refresh_comparison_table(self):
        """Refresh the entire comparison table after removing parts"""
        
        # Clear all data columns (keep parameter names)
        items = self.tree.get_children()
        for item in items:
            current_values = list(self.tree.item(item, 'values'))
            # Keep only the parameter name, clear all other columns
            new_values = [current_values[0]] + [''] * self.max_parts
            self.tree.item(item, values=new_values)
        
        # Re-add all current parts
        temp_parts = self.decoded_parts.copy()
        self.decoded_parts = []
        
        for part in temp_parts:
            self.add_to_comparison(part)
    
    def clear_all(self):
        """Clear all decoded parts and reset the table"""
        self.decoded_parts = []
        
        # Clear all data in the tree (keep headers)
        items = self.tree.get_children()
        for item in items:
            current_values = list(self.tree.item(item, 'values'))
            new_values = [current_values[0]] + [''] * self.max_parts
            self.tree.item(item, values=new_values)
        
        self.part_entry.delete(0, tk.END)
        self.update_part_selector()
        self.clear_highlighting()  # Clear any highlighting
        self.status_var.set("Cleared all parts - Ready for new input")
    
    def toggle_highlight_differences(self):
        """Toggle highlighting of differences between parts"""
        if self.highlight_differences.get():
            self.update_highlighting()
            self.status_var.set("Highlighting differences enabled")
        else:
            self.clear_highlighting()
            self.status_var.set("Highlighting differences disabled")
    
    def update_highlighting(self):
        """Update the highlighting of differences in the comparison table"""
        if len(self.decoded_parts) < 2:
            return  # Need at least 2 parts to compare
        
        items = self.tree.get_children()
        
        for item in items:
            values = list(self.tree.item(item, 'values'))
            parameter = values[0]
            
            # Skip the Part Number row as it's always different
            if parameter == 'Part Number':
                self.tree.item(item, tags=('normal',))
                continue
            
            # Get values for all parts (skip empty columns)
            part_values = []
            for i in range(1, len(self.decoded_parts) + 1):
                if i < len(values) and values[i].strip():
                    part_values.append(values[i])
            
            # Check if all values are the same
            if len(part_values) > 1:
                all_same = all(val == part_values[0] for val in part_values)
                if all_same:
                    self.tree.item(item, tags=('same',))
                else:
                    self.tree.item(item, tags=('different',))
            else:
                self.tree.item(item, tags=('normal',))
    
    def clear_highlighting(self):
        """Clear all highlighting from the table"""
        items = self.tree.get_children()
        for item in items:
            self.tree.item(item, tags=('normal',))

def main():
    root = tk.Tk()
    app = WimaDecoder(root)
    root.mainloop()

if __name__ == "__main__":
    main()