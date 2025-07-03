import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from bs4 import BeautifulSoup
import threading
import webbrowser
import json
import os

class XSSerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XSSer Pro - Advanced XSS Testing Tool")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)

        # Dark theme colors (CSS-like variables)
        self.theme = {
            'bg': '#2d2d2d',
            'fg': '#e0e0e0',
            'accent': '#4a90e2',
            'text_bg': '#1e1e1e',
            'text_fg': '#ffffff',
            'button_bg': '#3a3a3a',
            'button_active': '#4a4a4a',
            'entry_bg': '#252525',
            'tab_bg': '#333333',
            'tab_active': '#4a90e2',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336'
        }

        # Initialize UI components
        # FIX: Call load_payloads before create_widgets
        self.load_payloads() # Load default payloads initially (Sets self.payloads)
        self.setup_styles()
        self.create_widgets()
        self.update_payload_editor() # Populate payload editor after widgets are created

        # JavaScript-like event bindings
        self.setup_event_handlers()

        # Load settings
        self.load_settings()

        # Store scan results for export
        self.scan_results_data = []

    def setup_styles(self):
        """CSS-like style configuration"""
        style = ttk.Style()

        # Use clam theme as base for better customization
        style.theme_use('clam')

        # Main background
        style.configure('.',
                        background=self.theme['bg'],
                        foreground=self.theme['fg'])

        # Frame styles
        style.configure('TFrame', background=self.theme['bg'])
        style.configure('TLabelframe', background=self.theme['bg'], foreground=self.theme['fg'])
        style.configure('TLabelframe.Label', background=self.theme['bg'], foreground=self.theme['fg'])


        # Label styles
        style.configure('TLabel',
                        background=self.theme['bg'],
                        foreground=self.theme['fg'],
                        font=('Segoe UI', 10))

        style.configure('Header.TLabel',
                        font=('Segoe UI', 14, 'bold'))

        # Button styles (CSS-like)
        style.configure('TButton',
                        background=self.theme['button_bg'],
                        foreground=self.theme['fg'],
                        font=('Segoe UI', 10),
                        padding=6,
                        borderwidth=1,
                        relief="flat") # Make buttons flat by default

        style.map('TButton',
                  background=[('active', self.theme['button_active']),
                              ('pressed', self.theme['accent'])],
                  foreground=[('pressed', 'white')])

        # Entry styles
        style.configure('TEntry',
                        fieldbackground=self.theme['entry_bg'],
                        foreground=self.theme['fg'],
                        insertcolor=self.theme['fg'],
                        padding=5,
                        borderwidth=1,
                        relief="solid") # Give entries a solid border

        # Combobox styles
        style.configure('TCombobox',
                        fieldbackground=self.theme['entry_bg'],
                        foreground=self.theme['fg'])

        # Checkbutton styles
        style.configure('TCheckbutton',
                        background=self.theme['bg'],
                        foreground=self.theme['fg'])
        style.map('TCheckbutton',
                  background=[('active', self.theme['bg'])]) # Prevent background change on hover for checkbuttons

        # Radiobutton styles
        style.configure('TRadiobutton',
                        background=self.theme['bg'],
                        foreground=self.theme['fg'])
        style.map('TRadiobutton',
                  background=[('active', self.theme['bg'])]) # Prevent background change on hover for radiobuttons

        # Notebook (tabs) styles
        style.configure('TNotebook',
                        background=self.theme['bg'],
                        borderwidth=0) # Remove border around notebook tabs

        style.configure('TNotebook.Tab',
                        background=self.theme['tab_bg'],
                        foreground=self.theme['fg'],
                        padding=[10, 5],
                        font=('Segoe UI', 9, 'bold'),
                        borderwidth=0) # Remove border on tabs

        style.map('TNotebook.Tab',
                  background=[('selected', self.theme['tab_active'])],
                  foreground=[('selected', 'white')])

        # Scrollbar styles - these need to target the internal elements as well
        # Note: ttk scrollbar styling can be tricky and may not apply to the internal
        # elements of scrolledtext directly without custom Tkinter widgets.
        style.configure('Vertical.TScrollbar',
                        background=self.theme['button_bg'],
                        troughcolor=self.theme['bg'],
                        bordercolor=self.theme['bg'],
                        arrowcolor=self.theme['fg'],
                        relief="flat")
        style.map('Vertical.TScrollbar',
                  background=[('active', self.theme['button_active'])])

        style.configure('Horizontal.TScrollbar',
                        background=self.theme['button_bg'],
                        troughcolor=self.theme['bg'],
                        bordercolor=self.theme['bg'],
                        arrowcolor=self.theme['fg'],
                        relief="flat")
        style.map('Horizontal.TScrollbar',
                  background=[('active', self.theme['button_active'])])


    def create_widgets(self):
        """Create all GUI components"""
        # Main container (like a div in HTML)
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header (navbar-like)
        self.create_header()

        # Main content area with tabs (like a tabbed interface)
        self.create_tab_interface()

        # Status bar (footer-like)
        self.create_status_bar()

    def create_header(self):
        """Create header/navbar section"""
        header = ttk.Frame(self.main_container, style='TFrame')
        header.pack(fill=tk.X, pady=(0, 10))

        # Logo/Title (like a navbar-brand)
        logo_frame = ttk.Frame(header)
        logo_frame.pack(side=tk.LEFT)

        self.logo = ttk.Label(logo_frame,
                              text="🛡️ XSSer Pro",
                              style='Header.TLabel',
                              cursor='hand2')
        self.logo.pack(side=tk.LEFT)

        # Menu buttons (like navbar links)
        menu_frame = ttk.Frame(header)
        menu_frame.pack(side=tk.RIGHT)

        buttons = [
            ("Docs", lambda: webbrowser.open("https://xsser-docs.example.com")),
            ("About", self.show_about),
            ("GitHub", lambda: webbrowser.open("https://github.com/yourrepo/xsser"))
        ]

        for text, command in buttons:
            btn = ttk.Button(menu_frame,
                             text=text,
                             command=command,
                             style='TButton')
            btn.pack(side=tk.LEFT, padx=5)

    def create_tab_interface(self):
        """Create tabbed interface (like Bootstrap tabs)"""
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.create_scanner_tab()
        self.create_payloads_tab()
        self.create_settings_tab()

    def create_scanner_tab(self):
        """Create the scanner tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Scanner")

        # URL input (like a form group)
        url_frame = ttk.LabelFrame(tab, text=" Target URL ", padding=10)
        url_frame.pack(fill=tk.X, pady=5)

        ttk.Label(url_frame, text="Enter target URL:").pack(anchor=tk.W)

        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(fill=tk.X, pady=5)

        # Options frame
        options_frame = ttk.LabelFrame(tab, text=" Scan Options ", padding=10)
        options_frame.pack(fill=tk.X, pady=10)

        # Payload selection (like checkboxes)
        ttk.Label(options_frame, text="Payload Categories:").pack(anchor=tk.W)

        self.payload_vars = {}
        self.payload_checkbox_frame = ttk.Frame(options_frame) # Frame for checkboxes
        self.payload_checkbox_frame.pack(fill=tk.X, pady=5)

        # These will be updated dynamically later by update_payload_checkboxes
        self.update_payload_checkboxes()

        # Other options
        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame,
                        text="Verbose Output",
                        variable=self.verbose_var).pack(anchor=tk.W, pady=5)

        # Action buttons (like a button group)
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, pady=10)

        self.scan_btn = ttk.Button(button_frame,
                                   text="Start Scan",
                                   command=self.start_scan_thread)
        self.scan_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                   text="Clear Results",
                   command=self.clear_results).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                   text="Export Results",
                   command=self.export_results).pack(side=tk.LEFT, padx=5)

        # Results area (like a console/output panel)
        results_frame = ttk.LabelFrame(tab, text=" Scan Results ", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            bg=self.theme['text_bg'],
            fg=self.theme['text_fg'],
            insertbackground=self.theme['text_fg'],
            font=('Consolas', 10)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.configure(state=tk.DISABLED) # Make it read-only

        # Configure text tags (like CSS classes)
        self.results_text.tag_configure('success', foreground=self.theme['success'])
        self.results_text.tag_configure('warning', foreground=self.theme['warning'])
        self.results_text.tag_configure('error', foreground=self.theme['error'])
        self.results_text.tag_configure('info', foreground=self.theme['accent'])
        self.results_text.tag_configure('vulnerable', foreground='#ff5555', font=('Consolas', 10, 'bold'))

    def create_payloads_tab(self):
        """Create payload editor tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Payloads")

        # Payload editor (like a code editor)
        editor_frame = ttk.LabelFrame(tab, text=" Payload Editor ", padding=10)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.payload_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            bg=self.theme['text_bg'],
            fg=self.theme['text_fg'],
            insertbackground=self.theme['text_fg'],
            font=('Consolas', 10)
        )
        self.payload_editor.pack(fill=tk.BOTH, expand=True)

        # Payload controls (like a button toolbar)
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Button(control_frame,
                   text="Save Payloads",
                   command=self.save_payloads).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame,
                   text="Load Payloads",
                   command=self.load_payloads_file).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame,
                   text="Reset Defaults",
                   command=self.reset_payloads).pack(side=tk.LEFT, padx=5)

    def create_settings_tab(self):
        """Create settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Settings")

        # Proxy settings (like a form)
        proxy_frame = ttk.LabelFrame(tab, text=" Proxy Configuration ", padding=10)
        proxy_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(proxy_frame, text="HTTP Proxy:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.proxy_entry = ttk.Entry(proxy_frame)
        self.proxy_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        proxy_frame.grid_columnconfigure(1, weight=1) # Allow entry to expand

        # Theme selector (like radio buttons)
        theme_frame = ttk.LabelFrame(tab, text=" Appearance ", padding=10)
        theme_frame.pack(fill=tk.X, padx=5, pady=5)

        self.theme_var = tk.StringVar(value='dark')
        ttk.Radiobutton(theme_frame,
                        text="Dark Mode",
                        variable=self.theme_var,
                        value='dark').pack(anchor=tk.W)

        ttk.Radiobutton(theme_frame,
                        text="Light Mode",
                        variable=self.theme_var,
                        value='light').pack(anchor=tk.W)

        # Other settings
        misc_frame = ttk.LabelFrame(tab, text=" Miscellaneous ", padding=10)
        misc_frame.pack(fill=tk.X, padx=5, pady=5)

        self.auto_save_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(misc_frame,
                        text="Auto-save results after scan",
                        variable=self.auto_save_var).pack(anchor=tk.W)

        # Save button
        ttk.Button(tab,
                   text="Save Settings",
                   command=self.save_settings).pack(pady=10)

    def create_status_bar(self):
        """Create status bar (footer)"""
        self.status_var = tk.StringVar(value="Ready")

        status_bar = ttk.Frame(self.main_container, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(status_bar,
                  textvariable=self.status_var,
                  anchor=tk.W).pack(fill=tk.X, padx=5)

    def setup_event_handlers(self):
        """JavaScript-like event handlers"""
        # Logo click event
        self.logo.bind('<Button-1>', lambda e: webbrowser.open("https://github.com/yourrepo/xsser"))

        # URL entry focus effects - these are now handled by ttk styling
        # self.url_entry.bind('<FocusIn>', self.on_entry_focus_in)
        # self.url_entry.bind('<FocusOut>', self.on_entry_focus_out)

        # Theme change handler
        self.theme_var.trace_add('write', self.on_theme_changed)

    # Removed on_entry_focus_in and on_entry_focus_out as ttk styles handle this.
    # def on_entry_focus_in(self, event):
    #     """CSS-like focus effect"""
    #     event.widget.configure(style='TEntry.Focus') # Example if you defined a special focus style

    # def on_entry_focus_out(self, event):
    #     """CSS-like blur effect"""
    #     event.widget.configure(style='TEntry') # Reset to default style

    def on_theme_changed(self, *args):
        """Handle theme change (like a theme switcher)"""
        theme = self.theme_var.get()

        if theme == 'light':
            self.theme.update({
                'bg': '#f5f5f5',
                'fg': '#333333',
                'text_bg': '#ffffff',
                'text_fg': '#000000',
                'button_bg': '#e0e0e0',
                'button_active': '#d0d0d0',
                'entry_bg': '#ffffff',
                'tab_bg': '#e0e0e0',
                'tab_active': '#4a90e2'
            })
        else: # dark theme
            self.theme.update({
                'bg': '#2d2d2d',
                'fg': '#e0e0e0',
                'text_bg': '#1e1e1e',
                'text_fg': '#ffffff',
                'button_bg': '#3a3a3a',
                'button_active': '#4a4a4a',
                'entry_bg': '#252525',
                'tab_bg': '#333333',
                'tab_active': '#4a90e2'
            })

        # Update all widgets
        self.setup_styles()
        self.update_widget_colors()

    def update_widget_colors(self):
        """Update widget colors when theme changes"""
        # Update text widgets
        self.results_text.config(
            bg=self.theme['text_bg'],
            fg=self.theme['text_fg'],
            insertbackground=self.theme['text_fg']
        )

        if hasattr(self, 'payload_editor'):
            self.payload_editor.config(
                bg=self.theme['text_bg'],
                fg=self.theme['text_fg'],
                insertbackground=self.theme['text_fg']
            )

    def load_payloads(self):
        """Load default XSS payloads."""
        self.payloads = {
            'Basic': [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "';alert(String.fromCharCode(88,83,83))//",
                "<IMG SRC=\"javascript:alert('XSS');\">",
            ],
            'Image': [
                "<img src=x onerror=alert('XSS')>",
                "<img src='x' onerror=\"alert('XSS')\">",
                "<img src=x onmouseover=alert('XSS')>",
                "<body onpageshow=alert('XSS')>",
            ],
            'SVG': [
                "<svg/onload=alert('XSS')>",
                "<svg><script>alert('XSS')</script></svg>",
                "<svg onload=alert(1)>",
            ],
            'Advanced': [
                "<body onload=alert('XSS')>",
                "<iframe src=\"javascript:alert('XSS');\"></iframe>",
                "<script>alert(document.cookie)</script>",
                "<details open ontoggle=alert('XSS')>",
                "<video src=x onerror=alert('XSS')>",
            ],
            'DOM': [
                "\" onfocus=\"alert('XSS')\" autofocus=\"",
                "'); alert('XSS'); //",
                "<a href=\"javascript:alert('XSS')\">Click Me</a>",
                "<input type=\"text\" value=\"\" onblur=\"alert('XSS')\">"
            ]
        }

    def update_payload_editor(self):
        """Update payload editor content with current self.payloads."""
        if hasattr(self, 'payload_editor'):
            self.payload_editor.configure(state=tk.NORMAL)
            self.payload_editor.delete(1.0, tk.END)
            for category, payloads in self.payloads.items():
                self.payload_editor.insert(tk.END, f"# {category}\n", 'info')
                for payload in payloads:
                    self.payload_editor.insert(tk.END, f"{payload}\n")
                self.payload_editor.insert(tk.END, "\n")
            self.payload_editor.configure(state=tk.DISABLED)

    def update_payload_checkboxes(self):
        """Dynamically updates the payload category checkboxes in the scanner tab."""
        # Clear existing checkboxes
        for widget in self.payload_checkbox_frame.winfo_children():
            widget.destroy()

        self.payload_vars = {}
        categories = list(self.payloads.keys())
        for i, category in enumerate(categories):
            self.payload_vars[category] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(self.payload_checkbox_frame,
                                 text=category,
                                 variable=self.payload_vars[category])
            cb.grid(row=i // 3, column=i % 3, sticky=tk.W, padx=5, pady=2)


    def show_about(self):
        """Show about dialog"""
        about_text = """
        XSSer Pro - Advanced XSS Testing Tool

        Version: 2.0
        Author: Your Name (Update this!)
        License: MIT

        This tool is for educational and authorized
        security testing purposes only. Use responsibly.
        """
        messagebox.showinfo("About XSSer Pro", about_text.strip())

    def load_settings(self):
        """Load settings from file."""
        settings_file = 'xsser_settings.json'
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.theme_var.set(settings.get('theme', 'dark'))
                    self.auto_save_var.set(settings.get('auto_save', False))
                    self.proxy_entry.delete(0, tk.END) # Clear before inserting
                    self.proxy_entry.insert(0, settings.get('proxy', ''))
            # Apply theme immediately on load
            self.on_theme_changed()
        except Exception as e:
            self.log_message(f"Error loading settings: {str(e)}", 'error')

    def save_settings(self):
        """Save settings to file."""
        settings_file = 'xsser_settings.json'
        try:
            settings = {
                'theme': self.theme_var.get(),
                'auto_save': self.auto_save_var.get(),
                'proxy': self.proxy_entry.get().strip()
            }
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4) # Pretty print JSON
            self.log_message("Settings saved successfully.", 'success')
        except Exception as e:
            self.log_message(f"Error saving settings: {str(e)}", 'error')

    def log_message(self, message, tag=None):
        """Log message to results text (like console.log)."""
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.insert(tk.END, message + "\n", tag)
        self.results_text.configure(state=tk.DISABLED)
        self.results_text.see(tk.END)
        self.root.update_idletasks() # Ensure GUI updates immediately

    def clear_results(self):
        """Clear results text and scan_results_data."""
        self.results_text.configure(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.configure(state=tk.DISABLED)
        self.scan_results_data = [] # Clear stored results

    def start_scan_thread(self):
        """Start scan in a separate thread."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Input Error", "Please enter a target URL.")
            return

        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        selected_payloads = []
        for category, var in self.payload_vars.items():
            if var.get():
                selected_payloads.extend(self.payloads.get(category, []))

        if not selected_payloads:
            messagebox.showwarning("Payload Selection", "Please select at least one payload category.")
            return

        self.scan_btn.config(state=tk.DISABLED)
        self.status_var.set("Scanning...")
        self.clear_results() # Clear previous results
        self.scan_results_data = [] # Reset results data for new scan

        thread = threading.Thread(target=self.scan_url, args=(url, selected_payloads), daemon=True)
        thread.start()

    def scan_url(self, target_url, selected_payloads):
        """Scan URL for XSS vulnerabilities."""
        self.log_message(f"\n[+] Starting scan on: {target_url}", 'info')
        self.log_message(f"[+] Using {len(selected_payloads)} payloads.", 'info')

        proxies = None
        proxy_address = self.proxy_entry.get().strip()
        if proxy_address:
            proxies = {
                "http": proxy_address,
                "https": proxy_address,
            }
            self.log_message(f"[+] Using proxy: {proxy_address}", 'info')

        session = requests.Session()
        session.proxies = proxies
        
        try:
            # Step 1: Fetch the initial page
            self.log_message(f"[*] Fetching initial page: {target_url}", 'info')
            response = session.get(target_url, timeout=15)
            response.raise_for_status() # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            self.log_message("[+] Page fetched successfully.", 'success')

            # Step 2: Test URL parameters
            parsed_url = urlparse(target_url)
            query_params = parse_qs(parsed_url.query, keep_blank_values=True)
            if query_params:
                self.log_message("\n[*] Testing URL parameters...", 'info')
                for param_name in query_params:
                    for payload in selected_payloads:
                        self.test_parameter(target_url, param_name, payload, session)
            else:
                self.log_message("[*] No URL parameters found to test.", 'info')

            # Step 3: Test forms
            forms = soup.find_all('form')
            if forms:
                self.log_message(f"\n[*] Found {len(forms)} form(s). Testing forms...", 'info')
                for i, form in enumerate(forms):
                    self.log_message(f"[*] Testing Form {i+1}...", 'info')
                    self.test_form(target_url, form, selected_payloads, session)
            else:
                self.log_message("[*] No forms found on the page to test.", 'info')

            self.log_message("\n[+] Scan completed!", 'success')

        except requests.exceptions.RequestException as e:
            self.log_message(f"[-] Network/Request error accessing {target_url}: {e}", 'error')
            self.scan_results_data.append(f"Error: Network/Request error accessing {target_url}: {e}")
        except Exception as e:
            self.log_message(f"[-] An unexpected error occurred during scan: {e}", 'error')
            self.scan_results_data.append(f"Error: An unexpected error occurred during scan: {e}")
        finally:
            self.root.after(0, self.scan_complete) # Ensure scan_complete runs on main thread

    def test_form(self, base_url, form_tag, selected_payloads, session):
        """
        Tests a given HTML form by injecting XSS payloads into its input fields.
        """
        action = form_tag.get('action')
        method = form_tag.get('method', 'get').lower()
        form_url = urljoin(base_url, action) if action else base_url

        self.log_message(f"  [>] Form URL: {form_url}, Method: {method.upper()}", 'info')

        inputs = form_tag.find_all(['input', 'textarea'])
        form_data_template = {}
        for input_tag in inputs:
            name = input_tag.get('name')
            if name:
                form_data_template[name] = input_tag.get('value', '') # Use existing value or empty

        if not form_data_template:
            self.log_message("    [!] No exploitable input fields found in this form.", 'warning')
            return

        for payload in selected_payloads:
            for param_name, original_value in list(form_data_template.items()): # Iterate over a copy
                test_data = dict(form_data_template) # Create a fresh copy for each test
                test_data[param_name] = payload

                try:
                    response = None
                    if method == 'post':
                        response = session.post(form_url, data=test_data, timeout=10)
                    else: # Default to GET
                        response = session.get(form_url, params=test_data, timeout=10)

                    if response and self.check_vulnerability(response.text, payload):
                        self.log_message(f"    [!!!] VULNERABLE (Form): {form_url}\n        Parameter: '{param_name}' | Payload: '{payload}'", 'vulnerable')
                        self.scan_results_data.append(f"VULNERABLE (Form): {form_url} | Parameter: '{param_name}' | Payload: '{payload}'")
                        if not self.verbose_var.get():
                            return # Stop testing this form with other payloads if vulnerability found and not verbose
                    elif self.verbose_var.get():
                        self.log_message(f"    [<] Safe (Form): {form_url} | Param: '{param_name}' | Payload: '{payload}'", 'safe')
                except requests.exceptions.RequestException as e:
                    self.log_message(f"    [-] Request error for form {form_url} (Param: {param_name}, Payload: {payload[:30]}...): {e}", 'error')
                    break # Break if request fails for this form, try next form
                except Exception as e:
                    self.log_message(f"    [-] An error occurred during form test: {e}", 'error')
                    break # Break if any other error, try next form

    def test_parameter(self, url, param_name, payload, session):
        """
        Tests a specific URL query parameter by injecting an XSS payload.
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query, keep_blank_values=True) # keep_blank_values for empty params

        original_values = query_params.get(param_name, [])
        query_params[param_name] = [payload] # Replace with payload

        new_query = urlencode(query_params, doseq=True)
        test_url = parsed_url._replace(query=new_query).geturl()

        self.log_message(f"  [>] Testing URL parameter: '{param_name}' with payload: '{payload}'", 'info')

        try:
            response = session.get(test_url, timeout=10)

            if self.check_vulnerability(response.text, payload):
                self.log_message(f"    [!!!] VULNERABLE (URL Parameter): {test_url}\n        Parameter: '{param_name}' | Payload: '{payload}'", 'vulnerable')
                self.scan_results_data.append(f"VULNERABLE (URL Parameter): {test_url} | Parameter: '{param_name}' | Payload: '{payload}'")
            elif self.verbose_var.get():
                self.log_message(f"    [<] Safe (URL Parameter): {test_url} | Param: '{param_name}' | Payload: '{payload}'", 'safe')
        except requests.exceptions.RequestException as e:
            self.log_message(f"    [-] Request error for URL {test_url} (Param: {param_name}, Payload: {payload[:30]}...): {e}", 'error')
        except Exception as e:
            self.log_message(f"    [-] An error occurred during parameter test: {e}", 'error')

        # Restore original values (important if same session object is reused extensively)
        query_params[param_name] = original_values
        parsed_url._replace(query=urlencode(query_params, doseq=True)).geturl()


    def check_vulnerability(self, html_content, payload):
        """
        A basic check to see if the payload is reflected in the HTML content
        in an unencoded manner. This is a heuristic and can result in
        false positives/negatives. More advanced methods are needed for
        robust XSS detection (e.g., using a headless browser).
        """
        # Remove common HTML entities from the payload for a better comparison
        # This is a simplification; a full XSS check involves context-aware parsing
        # and likely JavaScript execution in a sandbox.
        normalized_payload = payload.replace("'", "&apos;").replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

        # Check if the raw payload is present, indicating direct reflection
        if payload in html_content:
            return True
        # Check if a slightly "sanitized" version is still present, which might bypass simple filters
        # This part can be greatly expanded.
        if normalized_payload in html_content and normalized_payload != payload:
             return True

        return False

    def scan_complete(self):
        """Called when scan completes."""
        self.scan_btn.config(state=tk.NORMAL)
        self.status_var.set("Scan completed.")

        if self.auto_save_var.get() and self.scan_results_data:
            self.export_results(auto=True)
        elif self.auto_save_var.get():
            self.log_message("[*] Auto-save is enabled, but no vulnerabilities were found to save.", 'info')

    def export_results(self, auto=False):
        """Export results to file."""
        if not self.scan_results_data and not auto:
            messagebox.showwarning("Warning", "No results to export.")
            return
        elif not self.scan_results_data and auto:
            # If auto-saving and no results, just exit
            return

        full_content = self.results_text.get(1.0, tk.END).strip()
        if not full_content:
            if not auto:
                messagebox.showwarning("Warning", "No results content in the display to export.")
            return

        file_name = f"xsser_scan_results_{urlparse(self.url_entry.get()).hostname or 'unknown'}_{os.urandom(4).hex()}.txt"

        if auto:
            file_path = file_name
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save scan results",
                initialfile=file_name
            )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(f"XSSer Pro Scan Results\n")
                    f.write(f"Target URL: {self.url_entry.get()}\n")
                    f.write(f"Scan Date: {os.path.getmtime(file_path) if os.path.exists(file_path) else 'N/A'}\n")
                    f.write("------------------------------------------------------------------\n\n")
                    f.write(full_content) # Write the entire content of the scrolledtext
                if not auto:
                    self.log_message(f"Results exported to {file_path}", 'success')
                else:
                    self.log_message(f"Results auto-saved to {file_path}", 'info')
            except Exception as e:
                self.log_message(f"Failed to export results: {str(e)}", 'error')
        elif not auto: # Only show this message if it was a manual export attempt
            self.log_message("Results export cancelled.", 'info')


    def save_payloads(self):
        """Save custom payloads from the editor to a file and update internal payloads."""
        content = self.payload_editor.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "Payload editor is empty. Nothing to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save payloads"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                self.log_message(f"Payloads saved to {file_path}", 'success')

                # Also update the internal payloads and checkboxes based on saved content
                self._parse_and_set_payloads(content)
                self.update_payload_checkboxes() # Refresh checkboxes in scanner tab

            except Exception as e:
                self.log_message(f"Error saving payloads: {str(e)}", 'error')
        else:
            self.log_message("Payloads save cancelled.", 'info')

    def load_payloads_file(self):
        """Load payloads from a file into the editor and update internal payloads."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Load payloads"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.payload_editor.configure(state=tk.NORMAL)
                self.payload_editor.delete(1.0, tk.END)
                self.payload_editor.insert(tk.END, content)
                self.payload_editor.configure(state=tk.DISABLED)

                # Update internal payloads and checkboxes based on loaded content
                self._parse_and_set_payloads(content)
                self.update_payload_checkboxes() # Refresh checkboxes in scanner tab

                self.log_message(f"Payloads loaded from {file_path}", 'success')
            except Exception as e:
                self.log_message(f"Error loading payloads: {str(e)}", 'error')
        else:
            self.log_message("Payloads load cancelled.", 'info')

    def _parse_and_set_payloads(self, content):
        """Parses the text content into the self.payloads dictionary."""
        new_payloads = {}
        current_category = "Uncategorized" # Default category for lines before any #
        new_payloads[current_category] = [] # Ensure it exists

        lines = content.splitlines()
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("#"):
                current_category = stripped_line[1:].strip()
                if current_category not in new_payloads:
                    new_payloads[current_category] = []
            elif stripped_line:
                new_payloads[current_category].append(stripped_line)
        
        # Remove empty uncategorized if no content was added to it
        if "Uncategorized" in new_payloads and not new_payloads["Uncategorized"]:
            del new_payloads["Uncategorized"]

        self.payloads = new_payloads


    def reset_payloads(self):
        """Reset payloads to defaults."""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all payloads to their factory defaults?"):
            self.load_payloads() # Reload original default payloads
            self.update_payload_editor() # Update editor with defaults
            self.update_payload_checkboxes() # Refresh checkboxes
            self.log_message("Payloads reset to defaults.", 'info')
        else:
            self.log_message("Payload reset cancelled.", 'info')

if __name__ == "__main__":
    root = tk.Tk()

    # Try to set window icon
    try:
        # It's better to provide a full path or ensure the .ico file is in the script's directory.
        root.iconbitmap(default='xsser.ico')
    except tk.TclError:
        # Fallback if icon is not found or invalid.
        pass

    app = XSSerGUI(root)
    root.mainloop()