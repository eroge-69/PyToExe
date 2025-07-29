import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import zipfile
import xml.etree.ElementTree as ET
import os
import shutil
import json
from datetime import datetime

class MapManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Map Manager - Browse and Extract Maps")
        self.root.geometry("1000x750")
        
        # Variables
        self.maps_data = []
        self.filtered_data = []
        self.maps_folder = "MTA Maps"
        self.extracts_folder = "extracts"
        self.cache_file = "map_cache.json"
        
        # Create extracts directory if it doesn't exist
        os.makedirs(self.extracts_folder, exist_ok=True)
        
        self.setup_ui()
        self.load_maps_with_cache()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Map Manager", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Progress bar frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(1, weight=1)
        
        # Progress bar (initially hidden)
        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.grid(row=0, column=0, padx=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Hide progress bar initially
        self.hide_progress()
        
        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Search Maps", padding="10")
        search_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        # Search by dropdown
        ttk.Label(search_frame, text="Search by:").grid(row=0, column=0, padx=(0, 5))
        self.search_type = ttk.Combobox(search_frame, values=["All", "Map Name", "Author", "File Name", "Folder Path"], 
                                       state="readonly", width=12)
        self.search_type.set("All")
        self.search_type.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        
        # Search entry
        ttk.Label(search_frame, text="Search:").grid(row=0, column=2, padx=(10, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=3, padx=(0, 10), sticky=(tk.W, tk.E))
        search_frame.columnconfigure(3, weight=1)
        
        # Clear search button
        clear_btn = ttk.Button(search_frame, text="Clear", command=self.clear_search)
        clear_btn.grid(row=0, column=4, padx=(5, 0))
        
        # Maps list frame
        list_frame = ttk.LabelFrame(main_frame, text="Maps", padding="10")
        list_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview with scrollbars - updated columns to include folder path
        columns = ("file_name", "map_name", "author", "folder_path")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.tree.heading("file_name", text="File Name")
        self.tree.heading("map_name", text="Map Name")
        self.tree.heading("author", text="Author")
        self.tree.heading("folder_path", text="Folder Path")
        
        # Configure column widths
        self.tree.column("file_name", width=200, minwidth=150)
        self.tree.column("map_name", width=300, minwidth=200)
        self.tree.column("author", width=150, minwidth=100)
        self.tree.column("folder_path", width=250, minwidth=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # Buttons
        self.extract_btn = ttk.Button(button_frame, text="Extract Selected Map", 
                         command=self.extract_map)
        self.extract_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.refresh_btn = ttk.Button(button_frame, text="Refresh Maps", 
                                     command=self.refresh_maps_full)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.change_folder_btn = ttk.Button(button_frame, text="Change Maps Folder", 
                                           command=self.change_maps_folder)
        self.change_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_cache_btn = ttk.Button(button_frame, text="Clear Cache", 
                                         command=self.clear_cache)
        self.clear_cache_btn.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

    def find_zip_files_recursive(self, root_folder):
        """Recursively find all ZIP files in the given folder and its subdirectories."""
        zip_files = []
        
        try:
            for root, dirs, files in os.walk(root_folder):
                for file in files:
                    if file.lower().endswith('.zip'):
                        full_path = os.path.join(root, file)
                        # Calculate relative path from the maps folder
                        relative_folder = os.path.relpath(root, root_folder)
                        if relative_folder == '.':
                            relative_folder = ''  # Root folder
                        
                        zip_files.append({
                            'file_name': file,
                            'full_path': full_path,
                            'relative_folder': relative_folder
                        })
        except Exception as e:
            print(f"Error walking directory {root_folder}: {e}")
            
        return zip_files
        
    def extract_map_info(self, zip_file_path):
        """Extract name and author from meta.xml inside a ZIP file."""
        try:
            # Check if file is a valid ZIP
            if not zipfile.is_zipfile(zip_file_path):
                return "CORRUPTED_ZIP", "Invalid ZIP file"
            
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                if 'meta.xml' not in zip_ref.namelist():
                    return "NO_META", "No meta.xml found"
                
                try:
                    with zip_ref.open('meta.xml') as meta_file:
                        xml_content = meta_file.read().decode('utf-8', errors='ignore')
                        
                    # Try to parse XML with error recovery
                    try:
                        root = ET.fromstring(xml_content)
                    except ET.ParseError as xml_error:
                        # Try alternative parsing approaches
                        try:
                            # Remove XML namespace declarations that might cause issues
                            cleaned_xml = self.clean_xml_content(xml_content)
                            root = ET.fromstring(cleaned_xml)
                        except:
                            return "XML_ERROR", f"XML Parse Error: {str(xml_error)[:50]}..."
                    
                    # Look for info element
                    info_element = root.find('info')
                    if info_element is None:
                        # Try alternative element names or paths
                        info_element = root.find('.//info')
                    
                    if info_element is not None:
                        name = info_element.get('name', 'Unknown')
                        author = info_element.get('author', 'Unknown')
                        return name, author
                    else:
                        return "NO_INFO", "No info element found"
                        
                except UnicodeDecodeError:
                    return "ENCODING_ERROR", "File encoding error"
                except Exception as inner_e:
                    return "META_ERROR", f"Meta.xml error: {str(inner_e)[:50]}..."
                    
        except zipfile.BadZipFile:
            return "BAD_ZIP", "Corrupted ZIP file"
        except Exception as e:
            return "UNKNOWN_ERROR", f"Unknown error: {str(e)[:50]}..."
    
    def clean_xml_content(self, xml_content):
        """Clean XML content to handle common issues."""
        import re
        
        # Remove problematic namespace declarations
        xml_content = re.sub(r'xmlns[^=]*="[^"]*"', '', xml_content)
        
        # Remove XML declaration if it's causing issues
        if xml_content.startswith('<?xml'):
            lines = xml_content.split('\n')
            if len(lines) > 1:
                xml_content = '\n'.join(lines[1:])
        
        # Remove any non-printable characters except standard whitespace
        xml_content = ''.join(char for char in xml_content if ord(char) >= 32 or char in '\t\n\r')
        
        return xml_content
    
    def show_progress(self, text="Processing..."):
        """Show progress bar with text."""
        self.progress_label.config(text=text)
        self.progress_label.grid()
        self.progress_bar.grid()
        self.progress_var.set(0)
        
    def hide_progress(self):
        """Hide progress bar."""
        self.progress_label.grid_remove()
        self.progress_bar.grid_remove()
        
    def update_progress(self, value, text=""):
        """Update progress bar value and text."""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=text)
        self.root.update_idletasks()
        
    def get_file_hash(self, filepath):
        """Get a simple hash of file (size + modification time)."""
        try:
            stat = os.stat(filepath)
            return f"{stat.st_size}_{stat.st_mtime}"
        except:
            return None
    
    def get_directory_hash(self, directory):
        """Get a hash representing the state of all ZIP files in the directory tree."""
        try:
            zip_files = self.find_zip_files_recursive(directory)
            file_info = []
            
            for zip_info in zip_files:
                file_hash = self.get_file_hash(zip_info['full_path'])
                if file_hash:
                    file_info.append((zip_info['full_path'], file_hash))
            
            # Sort to ensure consistent ordering
            file_info.sort()
            return str(hash(str(file_info)))
        except:
            return None
    
    def load_cache(self):
        """Load map data from cache file."""
        try:
            if not os.path.exists(self.cache_file):
                return None
                
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                
            # Check if cache is for the same maps folder
            if cache_data.get('maps_folder') != self.maps_folder:
                return None
                
            return cache_data
        except Exception as e:
            print(f"Error loading cache: {e}")
            return None
    
    def save_cache(self, maps_data, directory_hash):
        """Save map data to cache file."""
        try:
            cache_data = {
                'maps_folder': self.maps_folder,
                'timestamp': datetime.now().isoformat(),
                'directory_hash': directory_hash,
                'maps_data': maps_data
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def clear_cache(self):
        """Clear the cache file."""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                messagebox.showinfo("Cache Cleared", "Cache file has been cleared. Next refresh will scan all files.")
                self.status_var.set("Cache cleared")
            else:
                messagebox.showinfo("No Cache", "No cache file found.")
        except Exception as e:
            messagebox.showerror("Error", f"Error clearing cache: {e}")
    
    def load_maps_with_cache(self):
        """Load maps using cache when possible."""
        if not os.path.exists(self.maps_folder):
            messagebox.showwarning("Warning", f"Maps folder '{self.maps_folder}' not found!")
            self.status_var.set("Maps folder not found")
            return
        
        # Get current directory hash
        current_dir_hash = self.get_directory_hash(self.maps_folder)
        
        # Load cache
        cache_data = self.load_cache()
        
        # Check if we can use cache
        if (cache_data and 
            cache_data.get('directory_hash') == current_dir_hash and
            current_dir_hash is not None):
            
            # Use cached data
            self.maps_data = cache_data['maps_data']
            self.update_tree_display()
            
            cache_time = cache_data.get('timestamp', 'Unknown')
            self.status_var.set(f"Loaded {len(self.maps_data)} maps from cache (updated: {cache_time[:19]})")
            return
        
        # Cache is invalid or doesn't exist, do full scan
        self.status_var.set("Cache outdated or missing, performing full scan...")
        self.root.update()
        self.load_maps_full()
    
    def refresh_maps_full(self):
        """Force a full refresh of all maps (ignore cache)."""
        self.load_maps_full()
    
    def load_maps_full(self):
        """Load all maps from the maps folder (full scan with recursive search)."""
        self.show_progress("Scanning maps folder recursively...")
        
        self.maps_data.clear()
        
        if not os.path.exists(self.maps_folder):
            messagebox.showwarning("Warning", f"Maps folder '{self.maps_folder}' not found!")
            self.status_var.set("Maps folder not found")
            self.hide_progress()
            return
        
        # Get all ZIP files recursively
        zip_files = self.find_zip_files_recursive(self.maps_folder)
        
        if not zip_files:
            messagebox.showinfo("Info", f"No ZIP files found in '{self.maps_folder}' folder or its subdirectories")
            self.status_var.set("No maps found")
            self.hide_progress()
            return
        
        # Counters for statistics
        successful_loads = 0
        corrupted_files = 0
        xml_errors = 0
        total_files = len(zip_files)
        
        # Process each ZIP file
        for i, zip_info in enumerate(zip_files):
            zip_path = zip_info['full_path']
            zip_file = zip_info['file_name']
            relative_folder = zip_info['relative_folder']
            
            # Update progress
            progress = (i / total_files) * 100
            folder_display = f" (in {relative_folder})" if relative_folder else ""
            self.update_progress(progress, f"Processing: {zip_file}{folder_display}")
            
            name, author = self.extract_map_info(zip_path)
            
            # Handle different error types
            if name in ["CORRUPTED_ZIP", "BAD_ZIP"]:
                display_name = f"⚠️ {os.path.splitext(zip_file)[0]}"
                display_author = "❌ Corrupted ZIP"
                corrupted_files += 1
            elif name in ["XML_ERROR", "META_ERROR", "ENCODING_ERROR"]:
                display_name = f"⚠️ {os.path.splitext(zip_file)[0]}"
                display_author = f"❌ {author}"
                xml_errors += 1
            elif name in ["NO_META", "NO_INFO"]:
                display_name = os.path.splitext(zip_file)[0]
                display_author = "⚠️ No metadata"
            elif name == "UNKNOWN_ERROR":
                display_name = f"⚠️ {os.path.splitext(zip_file)[0]}"
                display_author = f"❌ {author}"
            else:
                # Successful extraction
                display_name = name if name else os.path.splitext(zip_file)[0]
                display_author = author if author else "Unknown"
                successful_loads += 1
            
            self.maps_data.append({
                'file_name': zip_file,
                'map_name': display_name,
                'author': display_author,
                'folder_path': relative_folder if relative_folder else '(root)',
                'full_path': zip_path,
                'has_error': name in ["CORRUPTED_ZIP", "BAD_ZIP", "XML_ERROR", "META_ERROR", "ENCODING_ERROR", "UNKNOWN_ERROR"]
            })
        
        # Final progress update
        self.update_progress(100, "Finalizing...")
        
        # Sort by folder path first, then by map name
        self.maps_data.sort(key=lambda x: (x['folder_path'], x['map_name'].lower()))
        
        # Save cache with directory hash
        directory_hash = self.get_directory_hash(self.maps_folder)
        self.save_cache(self.maps_data, directory_hash)
        
        # Update display
        self.update_tree_display()
        self.hide_progress()
        
        # Show loading summary
        status_msg = f"Loaded {len(self.maps_data)} files: {successful_loads} OK"
        if corrupted_files > 0:
            status_msg += f", {corrupted_files} corrupted"
        if xml_errors > 0:
            status_msg += f", {xml_errors} XML errors"
        
        self.status_var.set(status_msg)
        
        # Show detailed error report if there are issues
        if corrupted_files > 0 or xml_errors > 0:
            self.show_error_report(corrupted_files, xml_errors)
    
    def update_tree_display(self, data=None):
        """Update the treeview display with given data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Use filtered data if available, otherwise use all maps
        display_data = data if data is not None else self.maps_data
        
        # Insert items
        for map_info in display_data:
            self.tree.insert("", tk.END, values=(
                map_info['file_name'],
                map_info['map_name'],
                map_info['author'],
                map_info['folder_path']
            ))
    
    def on_search_change(self, *args):
        """Handle search input changes."""
        search_text = self.search_var.get().lower()
        search_type = self.search_type.get()
        
        if not search_text:
            self.update_tree_display()
            return
        
        filtered_maps = []
        
        for map_info in self.maps_data:
            match = False
            
            if search_type == "All":
                match = (search_text in map_info['file_name'].lower() or
                        search_text in map_info['map_name'].lower() or
                        search_text in map_info['author'].lower() or
                        search_text in map_info['folder_path'].lower())
            elif search_type == "Map Name":
                match = search_text in map_info['map_name'].lower()
            elif search_type == "Author":
                match = search_text in map_info['author'].lower()
            elif search_type == "File Name":
                match = search_text in map_info['file_name'].lower()
            elif search_type == "Folder Path":
                match = search_text in map_info['folder_path'].lower()
            
            if match:
                filtered_maps.append(map_info)
        
        self.update_tree_display(filtered_maps)
        self.status_var.set(f"Found {len(filtered_maps)} maps matching search")
    
    def clear_search(self):
        """Clear the search field."""
        self.search_var.set("")
        self.search_type.set("All")
        self.update_tree_display()
        self.status_var.set(f"Showing all {len(self.maps_data)} maps")
    
    def show_error_report(self, corrupted_files, xml_errors):
        """Show a detailed error report window."""
        error_window = tk.Toplevel(self.root)
        error_window.title("File Processing Report")
        error_window.geometry("600x400")
        error_window.transient(self.root)
        
        # Main frame
        main_frame = ttk.Frame(error_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="File Processing Issues Found", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Summary
        summary_text = f"Found issues with {corrupted_files + xml_errors} files:\n"
        summary_text += f"• {corrupted_files} corrupted/invalid ZIP files\n"
        summary_text += f"• {xml_errors} XML parsing errors\n\n"
        summary_text += "Files with issues are marked with ⚠️ or ❌ in the list."
        
        summary_label = ttk.Label(main_frame, text=summary_text, justify=tk.LEFT)
        summary_label.pack(pady=(0, 15), anchor=tk.W)
        
        # Detailed list
        detail_label = ttk.Label(main_frame, text="Detailed Error List:", font=("Arial", 10, "bold"))
        detail_label.pack(anchor=tk.W)
        
        # Text widget with scrollbar for detailed errors
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        error_text = tk.Text(text_frame, wrap=tk.WORD, height=15)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=error_text.yview)
        error_text.configure(yscrollcommand=scrollbar.set)
        
        error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate error details
        for map_info in self.maps_data:
            if map_info.get('has_error', False):
                folder_info = f" (in {map_info['folder_path']})" if map_info['folder_path'] != '(root)' else ""
                error_text.insert(tk.END, f"{map_info['file_name']}{folder_info}\n")
                error_text.insert(tk.END, f"  Issue: {map_info['author']}\n\n")
        
        error_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Close", command=error_window.destroy)
        close_btn.pack(pady=(5, 0))
    
    def extract_map(self):
        """Extract the selected map to the extracts folder."""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showwarning("Warning", "Please select a map to extract")
            return
        
        # Get selected item data
        item = self.tree.item(selection[0])
        file_name = item['values'][0]
        folder_path = item['values'][3]
        
        # Find the map data
        selected_map = None
        for map_info in self.maps_data:
            if map_info['file_name'] == file_name and map_info['folder_path'] == folder_path:
                selected_map = map_info
                break
        
        if not selected_map:
            messagebox.showerror("Error", "Could not find selected map data")
            return
        
        # Check if file has errors
        if selected_map.get('has_error', False):
            result = messagebox.askyesno("Warning", 
                f"This file has processing errors:\n{selected_map['author']}\n\nExtract anyway?")
            if not result:
                return
        
        try:
            # Create extracts directory if it doesn't exist
            os.makedirs(self.extracts_folder, exist_ok=True)
            
            # Copy file to extracts folder
            source_path = selected_map['full_path']
            dest_path = os.path.join(self.extracts_folder, file_name)
            
            # Check if file already exists
            if os.path.exists(dest_path):
                result = messagebox.askyesno("File Exists", 
                    f"'{file_name}' already exists in extracts folder.\nOverwrite?")
                if not result:
                    return
            
            shutil.copy2(source_path, dest_path)
            
            folder_info = f" (from {selected_map['folder_path']})" if selected_map['folder_path'] != '(root)' else ""
            messagebox.showinfo("Success", 
                f"Map '{selected_map['map_name']}'{folder_info} extracted successfully!\nLocation: {dest_path}")
            
            self.status_var.set(f"Extracted: {file_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract map:\n{str(e)}")
    
    def change_maps_folder(self):
        """Change the maps folder location."""
        folder = filedialog.askdirectory(title="Select Maps Folder", initialdir=self.maps_folder)
        
        if folder:
            self.maps_folder = folder
            # Clear current data and load from new folder
            self.maps_data.clear()
            self.update_tree_display()
            self.load_maps_with_cache()

def main():
    root = tk.Tk()
    
    # Configure style for better appearance
    style = ttk.Style()
    if "Accent.TButton" not in style.theme_names():
        style.configure("Accent.TButton", foreground="white", background="#0078d4")
    
    app = MapManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()