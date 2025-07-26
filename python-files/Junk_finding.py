import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from bs4 import BeautifulSoup
from collections import defaultdict
import unicodedata
from datetime import datetime

class EPUBJunkCharacterAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("EPUB Junk Character Analyzer")
        self.root.geometry("850x650")
        
        # Define what constitutes "junk" characters
        self.junk_categories = {
            'Control Characters': lambda c: unicodedata.category(c) == 'Cc',
            'Format Characters': lambda c: unicodedata.category(c) == 'Cf',
            'Private Use Characters': lambda c: unicodedata.category(c).startswith('Co'),
            'Unassigned Characters': lambda c: unicodedata.category(c) == 'Cn',
            'Non-ASCII Punctuation': lambda c: unicodedata.category(c).startswith('P') and ord(c) > 127,
            'Symbols': lambda c: unicodedata.category(c).startswith('S') and ord(c) > 127,
            'Non-Standard Whitespace': lambda c: c in '\u200b\u200c\u200d\u2060\ufeff',
            'Typographic Quotes': lambda c: c in '«»‹›‘’“”„‟',
            'Dashes/Hyphens': lambda c: c in '‐‑‒–—―',
        }
        
        self.create_widgets()
        self.setup_treeview()
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection
        file_frame = tk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        tk.Label(file_frame, text="EPUB File:").pack(side=tk.LEFT)
        self.file_entry = tk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)
        
        # Output selection
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        tk.Label(output_frame, text="Output Folder:").pack(side=tk.LEFT)
        self.output_entry = tk.Entry(output_frame, width=50)
        self.output_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Button(output_frame, text="Browse", command=self.browse_output).pack(side=tk.LEFT)
        
        # Options frame
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=10)
        
        # Character categories to check
        self.category_vars = {}
        for i, category in enumerate(self.junk_categories):
            var = tk.BooleanVar(value=True)
            self.category_vars[category] = var
            cb = tk.Checkbutton(options_frame, text=category, variable=var)
            cb.grid(row=i//3, column=i%3, sticky=tk.W, padx=5)
        
        # Filter frame
        filter_frame = tk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        tk.Label(filter_frame, text="Content Filter:").pack(side=tk.LEFT)
        self.content_filter = tk.StringVar(value="all")
        tk.Radiobutton(filter_frame, text="All Content", variable=self.content_filter, value="all").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(filter_frame, text="Headers Only", variable=self.content_filter, value="headers").pack(side=tk.LEFT, padx=5)
        
        # Analyze button
        tk.Button(main_frame, text="Analyze EPUB", command=self.analyze_epub,
                 bg="#4CAF50", fg="white", font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="", fg="blue")
        self.status_label.pack(pady=5)
    
    def setup_treeview(self):
        # Results frame
        results_frame = tk.Frame(self.root)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for results
        self.tree = ttk.Treeview(results_frame, columns=('File', 'Character', 'Unicode', 'Name', 'Category', 'Count', 'Location'), show='headings')
        self.tree.heading('File', text='File', command=lambda: self.sort_treeview('File', False))
        self.tree.heading('Character', text='Character', command=lambda: self.sort_treeview('Character', False))
        self.tree.heading('Unicode', text='Unicode', command=lambda: self.sort_treeview('Unicode', False))
        self.tree.heading('Name', text='Name', command=lambda: self.sort_treeview('Name', False))
        self.tree.heading('Category', text='Category', command=lambda: self.sort_treeview('Category', False))
        self.tree.heading('Count', text='Count', command=lambda: self.sort_treeview('Count', True))
        self.tree.heading('Location', text='Location', command=lambda: self.sort_treeview('Location', False))
        
        self.tree.column('File', width=150)
        self.tree.column('Character', width=60, anchor=tk.CENTER)
        self.tree.column('Unicode', width=80)
        self.tree.column('Name', width=150)
        self.tree.column('Category', width=120)
        self.tree.column('Count', width=60, anchor=tk.CENTER)
        self.tree.column('Location', width=100)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def sort_treeview(self, col, numeric):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        def sort_key(item):
            val = item[0]
            try:
                if numeric:
                    return float(val) if val else 0
                return val.lower()
            except ValueError:
                return val.lower()
        
        data.sort(key=sort_key)
        
        for i, item in enumerate(data):
            self.tree.move(item[1], '', i)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("EPUB Files", "*.epub")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, filename)
    
    def browse_output(self):
        foldername = filedialog.askdirectory()
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, foldername)
    
    def analyze_epub(self):
        epub_path = self.file_entry.get()
        output_folder = self.output_entry.get()
        
        if not epub_path or not output_folder:
            messagebox.showerror("Error", "Please select both EPUB file and output folder")
            return
        
        if not os.path.exists(epub_path):
            messagebox.showerror("Error", "EPUB file not found")
            return
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.status_label.config(text="Analyzing EPUB file...", fg="blue")
        self.progress['value'] = 0
        self.root.update()
        
        try:
            # Get selected categories
            active_categories = [cat for cat, var in self.category_vars.items() if var.get()]
            content_filter = self.content_filter.get()
            
            with zipfile.ZipFile(epub_path, 'r') as epub:
                html_files = [f for f in epub.namelist() if f.lower().endswith(('.html', '.xhtml'))]
                total_files = len(html_files)
                
                findings = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
                char_details = defaultdict(dict)
                header_findings = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
                
                for i, html_file in enumerate(html_files):
                    with epub.open(html_file) as f:
                        content = f.read().decode('utf-8', errors='replace')
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Get all text based on filter
                        if content_filter == "headers":
                            text_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                        else:
                            text_elements = [soup]
                        
                        for element in text_elements:
                            text = element.get_text()
                            location = "Header" if element.name and element.name.startswith('h') else "Body"
                            
                            for char in text:
                                for category in active_categories:
                                    if self.junk_categories[category](char):
                                        findings[html_file][char][category] += 1
                                        if char not in char_details:
                                            char_details[char] = {
                                                'name': unicodedata.name(char, 'UNKNOWN'),
                                                'code': f"U+{ord(char):04X}"
                                            }
                                        
                                        # Track header findings separately
                                        if location == "Header":
                                            header_findings[html_file][char][category] += 1
                    
                    # Update progress
                    progress = (i + 1) / total_files * 100
                    self.progress['value'] = progress
                    self.status_label.config(text=f"Processing {i+1}/{total_files}: {html_file}")
                    self.root.update()
                
                # Determine which findings to show based on filter
                display_findings = header_findings if content_filter == "headers" else findings
                
                # Populate treeview and prepare report data
                report_data = []
                for file in display_findings:
                    for char in display_findings[file]:
                        for category in display_findings[file][char]:
                            count = display_findings[file][char][category]
                            location = "Header" if content_filter == "headers" else (
                                "Header" if file in header_findings and char in header_findings[file] else "Body"
                            )
                            self.tree.insert('', tk.END, values=(
                                os.path.basename(file),
                                char,
                                char_details[char]['code'],
                                char_details[char]['name'],
                                category,
                                count,
                                location
                            ))
                            report_data.append({
                                'file': file,
                                'character': char,
                                'code': char_details[char]['code'],
                                'name': char_details[char]['name'],
                                'category': category,
                                'count': count,
                                'location': location
                            })
                
                # Generate HTML report with Excel-like filtering
                report_path = os.path.join(output_folder, "junk_characters_report.html")
                self.generate_html_report(report_path, report_data, active_categories, content_filter)
                
                self.status_label.config(text=f"Analysis complete! Found {len(report_data)} issues.", fg="green")
                messagebox.showinfo("Success", f"Report generated successfully at:\n{report_path}")
                
        except Exception as e:
            self.status_label.config(text="Error occurred", fg="red")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
    
    def generate_html_report(self, report_path, findings, active_categories, content_filter):
        # Prepare summary data
        total_issues = len(findings)
        unique_chars = len({f['character'] for f in findings})
        files_affected = len({f['file'] for f in findings})
        
        # Group findings by category for the summary
        category_counts = defaultdict(int)
        for f in findings:
            category_counts[f['category']] += f['count']
        
        # Group findings by location (header/body)
        location_counts = defaultdict(int)
        for f in findings:
            location_counts[f['location']] += f['count']
        
        # Get unique values for each column for filtering
        unique_files = sorted({os.path.basename(f['file']) for f in findings})
        unique_chars_report = sorted({f['character'] for f in findings})
        unique_codes = sorted({f['code'] for f in findings})
        unique_names = sorted({f['name'] for f in findings})
        unique_categories = sorted({f['category'] for f in findings})
        unique_locations = sorted({f['location'] for f in findings})
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EPUB Junk Characters Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                h1, h2 {{ color: #2c3e50; }}
                .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                .summary-table th, .summary-table td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                .summary-table th {{ background-color: #e9ecef; }}
                .findings-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .findings-table th, .findings-table td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                .findings-table th {{ background-color: #e9ecef; position: sticky; top: 0; }}
                .character-cell {{ font-family: monospace; font-size: 1.2em; }}
                .code-cell {{ font-family: monospace; }}
                .count-cell {{ text-align: right; }}
                .category-badge {{ 
                    display: inline-block; 
                    padding: 3px 6px; 
                    border-radius: 3px; 
                    font-size: 0.8em; 
                    background-color: #e9ecef; 
                    color: #495057;
                }}
                .location-badge {{
                    display: inline-block;
                    padding: 3px 6px;
                    border-radius: 3px;
                    font-size: 0.8em;
                    background-color: {"#d4edda" if content_filter == "headers" else "#f8d7da"};
                    color: {"#155724" if content_filter == "headers" else "#721c24"};
                }}
                .filter-row th {{ padding-bottom: 5px; }}
                .filter-select {{
                    width: 100%;
                    padding: 3px;
                    font-size: 0.9em;
                }}
            </style>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script>
                $(document).ready(function() {{
                    // Function to filter the table
                    function filterTable() {{
                        var fileFilter = $('#file-filter').val().toLowerCase();
                        var charFilter = $('#char-filter').val().toLowerCase();
                        var codeFilter = $('#code-filter').val().toLowerCase();
                        var nameFilter = $('#name-filter').val().toLowerCase();
                        var categoryFilter = $('#category-filter').val().toLowerCase();
                        var countFilter = $('#count-filter').val().toLowerCase();
                        var locationFilter = $('#location-filter').val().toLowerCase();
                        
                        $('.data-row').each(function() {{
                            var fileText = $(this).find('td:nth-child(1)').text().toLowerCase();
                            var charText = $(this).find('td:nth-child(2)').text().toLowerCase();
                            var codeText = $(this).find('td:nth-child(3)').text().toLowerCase();
                            var nameText = $(this).find('td:nth-child(4)').text().toLowerCase();
                            var categoryText = $(this).find('td:nth-child(5)').text().toLowerCase();
                            var countText = $(this).find('td:nth-child(6)').text().toLowerCase();
                            var locationText = $(this).find('td:nth-child(7)').text().toLowerCase();
                            
                            var fileMatch = fileFilter === '' || fileText.includes(fileFilter);
                            var charMatch = charFilter === '' || charText.includes(charFilter);
                            var codeMatch = codeFilter === '' || codeText.includes(codeFilter);
                            var nameMatch = nameFilter === '' || nameText.includes(nameFilter);
                            var categoryMatch = categoryFilter === '' || categoryText.includes(categoryFilter);
                            var countMatch = countFilter === '' || countText.includes(countFilter);
                            var locationMatch = locationFilter === '' || locationText.includes(locationFilter);
                            
                            if (fileMatch && charMatch && codeMatch && nameMatch && categoryMatch && countMatch && locationMatch) {{
                                $(this).show();
                            }} else {{
                                $(this).hide();
                            }}
                        }});
                    }}
                    
                    // Initialize filter dropdowns
                    function initFilters() {{
                        // File filter
                        $('#file-filter').append('<option value="">All Files</option>');
                        {''.join(f'$("#file-filter").append(\'<option value="{file}">{file}</option>\');' for file in unique_files)}
                        
                        // Character filter
                        $('#char-filter').append('<option value="">All Characters</option>');
                        {''.join(f'$("#char-filter").append(\'<option value="{char}">{char}</option>\');' for char in unique_chars_report)}
                        
                        // Unicode filter
                        $('#code-filter').append('<option value="">All Codes</option>');
                        {''.join(f'$("#code-filter").append(\'<option value="{code}">{code}</option>\');' for code in unique_codes)}
                        
                        // Name filter
                        $('#name-filter').append('<option value="">All Names</option>');
                        {''.join(f'$("#name-filter").append(\'<option value="{name}">{name}</option>\');' for name in unique_names)}
                        
                        // Category filter
                        $('#category-filter').append('<option value="">All Categories</option>');
                        {''.join(f'$("#category-filter").append(\'<option value="{cat}">{cat}</option>\');' for cat in unique_categories)}
                        
                        // Location filter
                        $('#location-filter').append('<option value="">All Locations</option>');
                        {''.join(f'$("#location-filter").append(\'<option value="{loc}">{loc}</option>\');' for loc in unique_locations)}
                    }}
                    
                    // Initialize filters and set up event handlers
                    initFilters();
                    $('.filter-select').change(filterTable);
                    $('.filter-select').keyup(filterTable);
                }});
            </script>
        </head>
        <body>
            <h1>EPUB Junk Characters Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <div class="location-badge">Showing: {"Headers Only" if content_filter == "headers" else "All Content"}</div>
            
            <div class="summary">
                <h2>Summary</h2>
                <table class="summary-table">
                    <tr><th>Total Issues Found</th><td>{total_issues}</td></tr>
                    <tr><th>Unique Problematic Characters</th><td>{unique_chars}</td></tr>
                    <tr><th>Files Affected</th><td>{files_affected}</td></tr>
                </table>
                
                <h3>Issues by Category</h3>
                <table class="summary-table">
                    {"".join(f'<tr><th>{cat}</th><td>{count}</td></tr>' for cat, count in sorted(category_counts.items()))}
                </table>
                
                <h3>Issues by Location</h3>
                <table class="summary-table">
                    {"".join(f'<tr><th>{loc}</th><td>{count}</td></tr>' for loc, count in sorted(location_counts.items()))}
                </table>
                
                <h3>Categories Checked</h3>
                <p>{", ".join(active_categories)}</p>
            </div>
            
            <h2>Detailed Findings</h2>
            <table class="findings-table">
                <thead>
                    <tr class="filter-row">
                        <th><select id="file-filter" class="filter-select"><option value="">Loading...</option></select></th>
                        <th><select id="char-filter" class="filter-select"><option value="">Loading...</option></select></th>
                        <th><select id="code-filter" class="filter-select"><option value="">Loading...</option></select></th>
                        <th><select id="name-filter" class="filter-select"><option value="">Loading...</option></select></th>
                        <th><select id="category-filter" class="filter-select"><option value="">Loading...</option></select></th>
                        <th><input id="count-filter" class="filter-select" type="text" placeholder="Filter count..."></th>
                        <th><select id="location-filter" class="filter-select"><option value="">Loading...</option></select></th>
                    </tr>
                    <tr>
                        <th>File</th>
                        <th>Character</th>
                        <th>Unicode</th>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Count</th>
                        <th>Location</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for finding in sorted(findings, key=lambda x: (x['file'], x['category'], x['character'])):
            html_template += f"""
                    <tr class="data-row">
                        <td>{os.path.basename(finding['file'])}</td>
                        <td class="character-cell">{finding['character']}</td>
                        <td class="code-cell">{finding['code']}</td>
                        <td>{finding['name']}</td>
                        <td><span class="category-badge">{finding['category']}</span></td>
                        <td class="count-cell">{finding['count']}</td>
                        <td><span class="location-badge">{finding['location']}</span></td>
                    </tr>
            """
        
        html_template += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_template)

if __name__ == "__main__":
    root = tk.Tk()
    app = EPUBJunkCharacterAnalyzer(root)
    root.mainloop()