import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import subprocess
import json
import os
import datetime
import locale
import threading
import time
import sys
from PIL import Image, ImageTk

# Remember last location where a .bat was saved/opened
LAST_BAT_DIR = os.getcwd()

# ZenZefi login imports
try:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service as EdgeService
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    from webdriver_manager.chrome import ChromeDriverManager

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


# ------------------ Placeholder Entry Helper ------------------

class PlaceholderEntry:
    def __init__(self, parent, textvariable, placeholder_text, **entry_kwargs):
        self.parent = parent
        self.textvariable = textvariable
        self.placeholder_text = placeholder_text
        self.is_placeholder_active = True

        # Create the entry widget
        self.entry = tk.Entry(parent, textvariable=textvariable, **entry_kwargs)

        # Set initial placeholder
        self._set_placeholder()

        # Bind events
        self.entry.bind('<FocusIn>', self._on_focus_in)
        self.entry.bind('<FocusOut>', self._on_focus_out)

        # Monitor StringVar changes (for Browse button updates)
        self.textvariable.trace('w', self._on_var_change)

    def _set_placeholder(self):
        """Set placeholder text and color"""
        self.is_placeholder_active = True
        self.entry.config(fg='gray')
        self.textvariable.set(self.placeholder_text)

    def _clear_placeholder(self):
        """Clear placeholder text and reset color"""
        if self.is_placeholder_active:
            self.is_placeholder_active = False
            self.entry.config(fg='black')
            self.textvariable.set('')

    def _on_focus_in(self, event):
        """Handle focus in event"""
        if self.is_placeholder_active:
            self._clear_placeholder()

    def _on_focus_out(self, event):
        """Handle focus out event"""
        if not self.textvariable.get().strip():
            self._set_placeholder()

    def _on_var_change(self, *args):
        """Handle StringVar changes (e.g., from Browse button)"""
        current_value = self.textvariable.get()

        # If Browse button set a real value (not placeholder)
        if current_value and current_value != self.placeholder_text:
            if self.is_placeholder_active:
                self.is_placeholder_active = False
                self.entry.config(fg='black')
        # If value was cleared programmatically
        elif not current_value and not self.is_placeholder_active:
            self._set_placeholder()

    def get_real_value(self):
        """Get the real value (empty string if placeholder is active)"""
        if self.is_placeholder_active:
            return ''
        return self.textvariable.get()

    def grid(self, **kwargs):
        return self.entry.grid(**kwargs)

    def pack(self, **kwargs):
        return self.entry.pack(**kwargs)

    def place(self, **kwargs):
        return self.entry.place(**kwargs)


# ------------------ Settings System ------------------

def load_settings():
    """Load application settings"""
    try:
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                return json.load(f)
    except:
        pass
    # Default settings
    return {
        'zenzefi_users': ['S1RSURDI', 'S1VADUVA', 'S1LCIUBE'],
        'autocheck_interval': 2  # minutes (default 2 minutes)
    }


def save_settings(settings):
    """Save application settings"""
    try:
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
        return False


def open_settings_window():
    """Open settings configuration window"""
    settings = load_settings()

    settings_window = tk.Toplevel(root)
    settings_window.title("Application Settings")
    settings_window.geometry("500x600")
    settings_window.configure(bg="#d0e7ff")

    # Make window stay on top but not modal
    settings_window.transient(root)
    settings_window.focus_set()

    # Title
    tk.Label(settings_window, text="Application Settings",
             font=("Arial", 14, "bold"), bg="#d0e7ff").pack(pady=10)

    # ZenZefi Users Section
    users_frame = tk.LabelFrame(settings_window, text="ZenZefi Users to Check",
                                padx=10, pady=10, bg="#d0e7ff")
    users_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Instructions
    tk.Label(users_frame, text="Enter usernames that should be checked for ZenZefi login status:",
             font=("Arial", 9), bg="#d0e7ff", fg="#666666").pack(anchor="w", pady=(0, 10))

    # Users listbox with scrollbar
    list_frame = tk.Frame(users_frame, bg="#d0e7ff")
    list_frame.pack(fill="both", expand=True, pady=(0, 10))

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    users_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                               font=("Arial", 10), height=6)
    users_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=users_listbox.yview)

    # Load current users
    for user in settings['zenzefi_users']:
        users_listbox.insert(tk.END, user)

    # Entry for new user
    entry_frame = tk.Frame(users_frame, bg="#d0e7ff")
    entry_frame.pack(fill="x", pady=(0, 10))

    new_user_var = tk.StringVar()
    tk.Label(entry_frame, text="Add User:", bg="#d0e7ff").pack(side="left")
    user_entry = tk.Entry(entry_frame, textvariable=new_user_var, width=15)
    user_entry.pack(side="left", padx=5)

    def add_user():
        user = new_user_var.get().strip().upper()
        if user and user not in users_listbox.get(0, tk.END):
            users_listbox.insert(tk.END, user)
            new_user_var.set("")

    def remove_user():
        selection = users_listbox.curselection()
        if selection:
            users_listbox.delete(selection[0])

    tk.Button(entry_frame, text="Add", command=add_user).pack(side="left", padx=5)
    tk.Button(entry_frame, text="Remove Selected", command=remove_user).pack(side="left", padx=5)

    # Bind Enter key to add user
    user_entry.bind('<Return>', lambda e: add_user())

    # Default users reset button
    def reset_to_default():
        users_listbox.delete(0, tk.END)
        default_users = ['S1RSURDI', 'S1VADUVA', 'S1LCIUBE']
        for user in default_users:
            users_listbox.insert(tk.END, user)

    tk.Button(users_frame, text="Reset to Default Users", command=reset_to_default,
              bg="#FFA500", fg="white").pack(pady=5)

    # Auto-check interval section
    autocheck_frame = tk.LabelFrame(settings_window, text="Auto-check Settings",
                                    padx=10, pady=10, bg="#d0e7ff")
    autocheck_frame.pack(pady=(10, 0), padx=20, fill="x")

    tk.Label(autocheck_frame, text="Auto-check interval for ZenZefi login status:",
             font=("Arial", 9), bg="#d0e7ff").pack(anchor="w", pady=(0, 5))

    interval_frame = tk.Frame(autocheck_frame, bg="#d0e7ff")
    interval_frame.pack(fill="x", pady=(0, 10))

    interval_var = tk.IntVar(value=settings.get('autocheck_interval', 2))
    interval_spinbox = tk.Spinbox(interval_frame, from_=1, to=30,
                                  textvariable=interval_var, width=10,
                                  font=("Arial", 10))
    interval_spinbox.pack(side="left")

    tk.Label(interval_frame, text="minutes (1-30 range)",
             font=("Arial", 9), fg="#666666", bg="#d0e7ff").pack(side="left", padx=(10, 0))

    # Interval examples
    tk.Label(autocheck_frame, text="Examples: 1min=frequent, 2min=normal, 5min=background, 10min=minimal",
             font=("Arial", 8), fg="#4A5568", bg="#d0e7ff").pack(anchor="w", pady=(0, 5))

    # Buttons
    button_frame = tk.Frame(settings_window, bg="#d0e7ff")
    button_frame.pack(pady=20)

    def save_and_close():
        # Get users from listbox
        user_list = list(users_listbox.get(0, tk.END))
        if not user_list:
            messagebox.showerror("Error", "At least one ZenZefi user must be specified.")
            return

        # Validate interval
        interval = interval_var.get()
        if interval < 1 or interval > 30:
            messagebox.showerror("Error", "Auto-check interval must be between 1 and 30 minutes.")
            return

        # Update settings
        settings['zenzefi_users'] = user_list
        settings['autocheck_interval'] = interval

        if save_settings(settings):
            messagebox.showinfo("Settings Saved",
                                f"Settings saved successfully!\n\n"
                                f"ZenZefi Users: {', '.join(user_list)}\n"
                                f"Auto-check Interval: {interval} minute{'s' if interval != 1 else ''}\n\n"
                                f"Changes will take effect on next auto-check cycle.")
            settings_window.destroy()

    tk.Button(button_frame, text="Save Settings", command=save_and_close,
              width=15, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white").pack(side="left", padx=10)
    tk.Button(button_frame, text="Cancel", command=settings_window.destroy,
              width=10, font=("Arial", 10)).pack(side="left", padx=5)


# ------------------ Help System ------------------

def open_help_window():
    """Open comprehensive help window"""
    help_window = tk.Toplevel(root)
    help_window.title("TestTool Launcher - Help")
    help_window.geometry("900x700")
    help_window.configure(bg="#d0e7ff")

    # Make window non-modal (can work with main app while help is open)
    help_window.transient(root)  # Keep on top of main window

    # Create scrollable text widget
    text_frame = tk.Frame(help_window, bg="#d0e7ff")
    text_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Scrollbar
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    # Text widget
    help_text = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set,
                        font=("Arial", 10), bg="white", fg="black",
                        padx=10, pady=10)
    help_text.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=help_text.yview)

    # Help content
    help_content = """TestTool Launcher - Complete User Guide

OVERVIEW
========
TestTool Launcher is an application that:
• Creates batch files (.bat) for running NEST, NTS, DIVA and EXAM tools
• Schedules these files through Windows Task Scheduler
• Checks ZenZefi login status with configurable monitoring

MAIN COMPONENTS
===============

1. ZenZefi Login Status Widget
--------------------------------
Located: At the top of the application
Function: Checks if users are logged into ZenZefi (configurable in Settings)

Buttons:
• Check Now: Manually checks login status
• Open Login: Opens ZenZefi login page in browser
• Auto-check (configurable): Automatic checking at configurable intervals (1-30 minutes)

Status Indicators:
• ● Not Checked (gray): Initial state
• ● Checking... (blue): Currently checking
• ● Logged In (green): User is logged in
• ● Not Logged In (red): No valid user found

2. Settings Configuration (⚙ button)
------------------------------------
• ZenZefi Users: Add/remove users to check for login
• Auto-check Interval: Set frequency from 1-30 minutes
• Persistent storage: Settings saved between sessions

Auto-check Examples:
• 1 minute: Frequent monitoring during active testing
• 2 minutes: Normal monitoring (default)
• 5 minutes: Background monitoring
• 10 minutes: Light monitoring
• 30 minutes: Minimal monitoring

3. Tool Configuration
----------------------

NEST Test Runner:
Steps to use:
1. Select "NEST" from dropdown
2. Press "Launch Configuration"
3. Fill in the fields:
   • NEST Executable Folder: Path to folder containing NEST.exe
   • Option: Choose between options 2, 3, or 4:
     - Option 2: Generate CANoe configuration and start tests automatically (requires ARXML & ODX)
     - Option 3: Generate CANoe configuration only (no auto-run, requires ARXML & ODX)
     - Option 4: Start tests only (Configuration must be done first with: 2 or 3 option!)
   • NEST File: The .nest file
   • ARXML File: The .arxml file (required for options 2 and 3)
   • ODX File: The .odx-d file (required for options 2 and 3)

Scheduling Options:
• Schedule Date: Date when to run (cannot be in the past)
• Schedule Time: Time in 24h format using dropdown menus
• Recurrence: Once/Daily/Weekly/Monthly
• Interval: How many units to repeat (e.g., every 2 days, every 3 weeks)

NTS Test Runner:
Steps to use:
1. Select "NTS" from dropdown
2. Press "Launch Configuration"
3. Fill in the required fields:
   • NTS CLI Executable: Path to NTS CLI executable
   • Config File: The .nts configuration file
   • Log Directory: Directory where logs will be saved
   • ZenZefi User: ZenZefi username
   • ZenZefi Password: Password (with show/hide option)

Security Note: NTS password is saved in plain text in configuration files!

4. Direct BAT Scheduler
------------------------
Function: Schedule any existing .bat file
Steps:
1. Press "Select BAT File"
2. Choose the .bat file using file browser
3. Set a unique task name
4. Configure date, time, and recurrence
5. Press "Save Schedule"

This is useful for scheduling previously created batch files or custom scripts.

MAIN BUTTONS
============
For each configured tool, you have 3 options:

• Save .bat: Creates and saves the batch file without running it
• Run .bat: Creates the batch file and runs it immediately
• Save & Schedule .bat: Creates the batch file and schedules it in Windows Task Scheduler

ADVANCED FEATURES
=================

Recurring Scheduling Examples:
• Once: One time execution at specified date/time
• Daily + Interval 1: Every day
• Daily + Interval 3: Every 3 days
• Weekly + Interval 2: Every 2 weeks (bi-weekly)
• Monthly + Interval 6: Every 6 months (semi-annually)

Configuration Management:
• Application automatically saves configurations in JSON files:
  - config.json for NEST settings
  - configNTS.json for NTS settings
  - settings.json for application settings (users, intervals)
• Settings are restored when you reopen the application
• Password storage: NTS passwords are stored in plain text for automation

Date and Time Handling:
• System date format detection (mm/dd/yyyy, dd/mm/yyyy, yyyy-mm-dd, etc.)
• 24-hour time format with dropdown selection
• Validation prevents scheduling tasks in the past
• Windows Task Scheduler integration for reliable execution

VALIDATIONS AND RESTRICTIONS
============================
The application includes several safety checks:

• Required Fields: All mandatory fields must be filled before creating batch files
• File Existence: Checks that selected files actually exist
• Date Validation: Cannot schedule tasks in the past
• Time Format: Validates 24-hour time format (HH:MM)
• Path Validation: Ensures executable paths are valid
• Option Dependencies: Options 2 and 3 for NEST require both ARXML and ODX files
• Settings Validation: Auto-check interval must be 1-30 minutes

TROUBLESHOOTING
===============

Common Issues:
1. "Selenium not available" message:
   - Install required packages: pip install selenium webdriver-manager

2. ZenZefi login check fails:
   - Ensure you have Edge or Chrome browser installed
   - Check if ZenZefi is accessible at https://localhost:61000
   - Verify users are configured in Settings

3. Task scheduling fails:
   - Run application as Administrator for Task Scheduler access
   - Check that selected batch file exists and is accessible

4. Batch file execution fails:
   - Verify all file paths are correct
   - Ensure executable files have proper permissions
   - Check that required dependencies are installed

5. Settings not saving:
   - Check write permissions in application directory
   - Ensure settings.json is not read-only

FILE LOCATIONS
==============
Generated files are saved in the application directory:
• run_nest_cli.bat: NEST batch file
• run_nts_cli.bat: NTS batch file
• config.json: NEST configuration
• configNTS.json: NTS configuration
• settings.json: Application settings (users, auto-check interval)

Windows Task Scheduler tasks are created with names:
• NEST_Test_Run: For NEST tasks
• NTS_Test_Run: For NTS tasks  
• Custom_BAT_Task: For direct BAT scheduling (or custom name)

WORKFLOW AUTOMATION
===================
The application is designed for complete test workflow automation:

1. Configure your test tools once
2. Set up ZenZefi users and monitoring intervals in Settings
3. Create batch files for automated execution
4. Schedule tests to run at optimal times
5. Monitor ZenZefi login status automatically (1-30 minute intervals)
6. Review execution through Windows Task Scheduler

This enables unattended testing scenarios, continuous integration workflows, and scheduled regression testing with automatic login monitoring.

For additional support or feature requests, refer to Catalin Diac."""

    # Insert text and make it read-only
    help_text.insert("1.0", help_content)
    help_text.config(state="disabled")

    # Close button
    close_frame = tk.Frame(help_window, bg="#d0e7ff")
    close_frame.pack(pady=10)

    tk.Button(close_frame, text="Close", command=help_window.destroy,
              width=15, height=2, font=("Arial", 10, "bold"),
              bg="#4CAF50", fg="white").pack()


# ------------------ ZenZefi Login Checker ------------------

class ZenZefiChecker:
    def __init__(self, callback_function=None):
        self.callback_function = callback_function
        self.is_checking = False

    def check_login_status(self):
        """Check if user is logged in to ZenZefi"""
        if not SELENIUM_AVAILABLE:
            return False, "Selenium not available. Please install: pip install selenium webdriver-manager"

        if self.is_checking:
            return False, "Already checking login status..."

        self.is_checking = True

        try:
            # Try Edge first, then Chrome
            for browser_type in ['edge', 'chrome']:
                try:
                    driver = self._create_driver(browser_type)
                    if driver:
                        result = self._check_with_driver(driver)
                        self.is_checking = False
                        return result
                except Exception as e:
                    continue

            self.is_checking = False
            return False, "Both Edge and Chrome browsers failed to start"

        except Exception as e:
            self.is_checking = False
            return False, f"Error checking login: {str(e)}"

    def _create_driver(self, browser_type):
        """Create browser driver"""
        try:
            if browser_type == 'edge':
                edge_options = EdgeOptions()
                edge_options.add_argument("--headless=new")
                edge_options.add_argument("--disable-gpu")
                edge_options.add_argument("--ignore-certificate-errors")
                edge_options.add_argument("--disable-web-security")
                edge_options.add_argument("--allow-running-insecure-content")
                return webdriver.Edge(
                    service=EdgeService(EdgeChromiumDriverManager().install()),
                    options=edge_options
                )
            else:  # chrome
                chrome_options = ChromeOptions()
                chrome_options.add_argument("--headless=new")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--ignore-certificate-errors")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--allow-running-insecure-content")
                return webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=chrome_options
                )
        except Exception:
            return None

    def _check_with_driver(self, driver):
        """Check login status with given driver"""
        try:
            driver.get("https://localhost:61000/#/zenzefi/ui/certificates")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            page_source = driver.page_source

            # Load users from settings
            settings = load_settings()
            users_to_check = settings.get('zenzefi_users', ['S1RSURDI', 'S1VADUVA', 'S1LCIUBE'])

            for user in users_to_check:
                if user in page_source:
                    return True, f"User '{user}' is logged in"

            return False, "No valid user found logged in"

        except Exception as e:
            return False, f"Error checking page: {str(e)}"
        finally:
            try:
                driver.quit()
            except:
                pass


# ------------------ Login Status Widget ------------------

class LoginStatusWidget:
    def __init__(self, parent):
        self.parent = parent
        self.checker = ZenZefiChecker()
        self.check_thread = None
        self.auto_check_enabled = tk.BooleanVar(value=False)

        # Create the widget frame
        self.frame = tk.Frame(parent, bg="#d0e7ff", relief="ridge", bd=2)

        # Title
        tk.Label(self.frame, text="ZenZefi Login Status",
                 font=("Arial", 11, "bold"), bg="#d0e7ff").pack(pady=5)

        # Status display
        self.status_frame = tk.Frame(self.frame, bg="#d0e7ff")
        self.status_frame.pack(pady=5)

        self.status_label = tk.Label(self.status_frame, text="● Not Checked",
                                     font=("Arial", 10), bg="#d0e7ff", fg="gray")
        self.status_label.pack(side="left")

        # Buttons frame
        button_frame = tk.Frame(self.frame, bg="#d0e7ff")
        button_frame.pack(pady=5)

        self.check_button = tk.Button(button_frame, text="Check Now",
                                      command=self.manual_check,
                                      font=("Arial", 9), width=12)
        self.check_button.pack(side="left", padx=5)

        self.login_button = tk.Button(button_frame, text="Open Login",
                                      command=self.open_zenzefi_login,
                                      font=("Arial", 9), width=12)
        self.login_button.pack(side="left", padx=5)

        # Auto-check option
        auto_frame = tk.Frame(self.frame, bg="#d0e7ff")
        auto_frame.pack(pady=5)

        tk.Checkbutton(auto_frame, text="Auto-check (configurable in settings)",
                       variable=self.auto_check_enabled,
                       command=self.toggle_auto_check,
                       bg="#d0e7ff", font=("Arial", 9)).pack()

        # Auto-check timer
        self.auto_check_timer = None

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def place(self, **kwargs):
        self.frame.place(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def manual_check(self):
        """Manually check login status"""
        if self.check_thread and self.check_thread.is_alive():
            return

        self.update_status("● Checking...", "blue")
        self.check_button.config(state="disabled")

        self.check_thread = threading.Thread(target=self._perform_check)
        self.check_thread.daemon = True
        self.check_thread.start()

    def _perform_check(self):
        """Perform the actual login check"""
        success, message = self.checker.check_login_status()

        # Update UI in main thread
        self.parent.after(0, self._update_check_result, success, message)

    def _update_check_result(self, success, message):
        """Update the UI with check results"""
        if success:
            self.update_status("● Logged In", "green")
        else:
            self.update_status("● Not Logged In", "red")

        self.check_button.config(state="normal")

    def update_status(self, text, color):
        """Update the status display"""
        self.status_label.config(text=text, fg=color)

    def open_zenzefi_login(self):
        """Open ZenZefi login page in default browser"""
        try:
            import webbrowser
            webbrowser.open("https://localhost:61000/#/zenzefi/ui/certificates")
            messagebox.showinfo("Login",
                                "ZenZefi login page opened in your browser.\n"
                                "Please log in and then click 'Check Now' to verify.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser: {str(e)}")

    def toggle_auto_check(self):
        """Toggle automatic checking"""
        if self.auto_check_enabled.get():
            self.start_auto_check()
        else:
            self.stop_auto_check()

    def start_auto_check(self):
        """Start automatic login checking"""
        self.stop_auto_check()  # Stop any existing timer
        self._schedule_auto_check()

    def stop_auto_check(self):
        """Stop automatic login checking"""
        if self.auto_check_timer:
            self.parent.after_cancel(self.auto_check_timer)
            self.auto_check_timer = None

    def _schedule_auto_check(self):
        """Schedule the next auto-check"""
        if self.auto_check_enabled.get():
            # Get interval from settings (in minutes)
            settings = load_settings()
            interval_minutes = settings.get('autocheck_interval', 2)  # default 2 minutes
            interval_ms = interval_minutes * 60000  # Convert minutes to milliseconds
            self.auto_check_timer = self.parent.after(interval_ms, self._auto_check_callback)

    def _auto_check_callback(self):
        """Callback for automatic checking"""
        if self.auto_check_enabled.get():
            # Don't auto-check if manual check is in progress
            if not (self.check_thread and self.check_thread.is_alive()):
                self.manual_check()
            self._schedule_auto_check()


# ------------------ Shared Utilities ------------------

def get_system_date_format():
    """Get the system date format and return appropriate format string"""
    try:
        # Try to get system locale date format
        locale.setlocale(locale.LC_TIME, '')
        sample_date = datetime.datetime(2023, 12, 31)
        formatted = sample_date.strftime('%x')

        # Determine format based on formatted output
        if '/' in formatted:
            if formatted.startswith('12'):
                return 'mm/dd/yyyy'
            else:
                return 'dd/mm/yyyy'
        elif '-' in formatted:
            return 'yyyy-mm-dd'
        elif '.' in formatted:
            return 'dd.mm.yyyy'
        else:
            return 'yyyy-mm-dd'  # Default fallback
    except:
        return 'yyyy-mm-dd'  # Safe fallback


def format_date_for_system(date_obj):
    """Format date object for Windows schtasks (always mm/dd/yyyy)"""
    return date_obj.strftime('%m/%d/%Y')


def browse_file(var, filetypes=None):
    """Browse for a file with proper filetype handling"""
    # Provide default filetypes if none specified
    if filetypes is None:
        filetypes = [('All files', '*.*')]

    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        var.set(file_path)


def browse_folder(var):
    folder_path = filedialog.askdirectory()
    if folder_path:
        var.set(folder_path)


# ------------------ NEST Implementation ------------------

def load_nest_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return {}


def save_nest_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)


def build_nest_bat_content(nest_path, option, nest_file, arxml_file, odx_file):
    nest_file_bs = os.path.normpath(nest_file)
    arxml_file_bs = os.path.normpath(arxml_file) if arxml_file else ""
    odx_file_bs = os.path.normpath(odx_file) if odx_file else ""
    cmd = f'NEST.exe -o {option} -f {nest_file_bs}'
    if option in ['2', '3']:
        cmd += f' -e {arxml_file_bs} -x {odx_file_bs}'
    return f'@echo off\ncd /d {nest_path}\n{cmd}\n'


def schedule_bat_file(bat_path, task_name, date_obj, time_str, recurrence_type=None, recurrence_interval=1):
    """
    Schedules the task so that it starts EXACTLY on the chosen date (azi sau mâine),
    on any Windows (locale-agnostic), and supports Daily/Weekly/Monthly/Once.
    - Weekly: sets the day with /D MON..SUN (including weekend).
    - Monthly: sets the day of the month with /D <1..31>.
    - Once: runs at the selected date + time only once.
    Returns True if succeeded, otherwise False.
    """
    try:
        # 1) Validate time HH:MM (24h)
        datetime.datetime.strptime(time_str, "%H:%M")

        # 2) Accepts parameter as date or datetime
        start_date = date_obj.date() if isinstance(date_obj, datetime.datetime) else date_obj


        # 4) Normalize recurrence type
        rec_map = {"Once": "ONCE", "Daily": "DAILY", "Weekly": "WEEKLY", "Monthly": "MONTHLY"}
        sc = rec_map.get((recurrence_type or "Once"), "ONCE")

        # 5) Common base
        cmd_base = (
            f'schtasks /Create '
            f'/TN "{task_name}" '
            f'/TR "{bat_path}" '
            f'/SC {sc} '
            f'/ST {time_str} '
            f'/F'
        )

        # 6) /MO only for recurrence (not for ONCE)
        if sc != "ONCE" and int(recurrence_interval) > 1:
            cmd_base += f' /MO {int(recurrence_interval)}'

        # 7) Specific parameters for WEEKLY and MONTHLY
        extra_switches = ""
        if sc == "WEEKLY":
            # Python weekday: Monday=0 .. Sunday=6
            weekday_names = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
            sch_wd = weekday_names[start_date.weekday()]
            extra_switches += f' /D {sch_wd}'

        elif sc == "MONTHLY":
            # Rulează în fiecare lună în ziua <n> (1..31) a datei alese
            day_of_month = start_date.day
            extra_switches += f' /D {day_of_month}'

        # 8) Build format variants for /SD (locale-agnostic)
        date_variants = [
            start_date.strftime('%m/%d/%Y'),  # mm/dd/yyyy
            start_date.strftime('%d/%m/%Y'),  # dd/mm/yyyy
            start_date.strftime('%Y/%m/%d'),  # yyyy/mm/dd
            start_date.strftime('%Y-%m-%d'),  # yyyy-mm-dd (acceptat uneori)
        ]

        attempted_cmds = []

        # 9) Try /SD with fallback for ALL types (inclusiv recurențe),
        #    ca să respecte EXACT data aleasă (azi sau mâine) pe orice Windows.
        for ds in date_variants:
            cmd = f"{cmd_base}{extra_switches} /SD {ds}"
            attempted_cmds.append(cmd)
            exit_code = os.system(cmd)
            if exit_code == 0:
                # Consistent success messages
                if sc == "ONCE":
                    messagebox.showinfo(
                        "Scheduled",
                        f"Task scheduled on {start_date.strftime('%Y-%m-%d')} la {time_str} (Once)."
                    )
                elif sc == "DAILY":
                    messagebox.showinfo(
                        "Scheduled",
                        f"Task scheduled to start on {start_date.strftime('%Y-%m-%d')} at {time_str}\n"
                        f"Recurrence: Daily (every {recurrence_interval})"
                    )
                elif sc == "WEEKLY":
                    messagebox.showinfo(
                        "Scheduled",
                        f"Task scheduled to start on {start_date.strftime('%Y-%m-%d')} at {time_str}\n"
                        f"Recurrence: Weekly (every {recurrence_interval})"
                    )
                else:  # MONTHLY
                    messagebox.showinfo(
                        "Scheduled",
                        f"Task scheduled to start on {start_date.strftime('%Y-%m-%d')} at {time_str}\n"
                        f"Recurrence: Monthly (every {recurrence_interval})"
                    )
                return True

        # 10) If no format worked, show the last attempted command
        messagebox.showerror(
            "Error",
            "Failed to schedule task. Windows a respins Start Date în toate formatele încercate.\n\n"
            "Tried formats: mm/dd/yyyy, dd/mm/yyyy, yyyy/mm/dd, yyyy-mm-dd.\n"
            f"Last command tried:\n{attempted_cmds[-1]}"
        )
        return False

    except ValueError:
        messagebox.showerror("Invalid Time", "Time must be in HH:MM (24h). Example: 21:30")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Failed to schedule task: {e}")
        return False


def save_nest_bat_file(nest_path_entry, option_var, nest_file_entry, arxml_file_entry, odx_file_entry):
    nest_path = nest_path_entry.get_real_value()
    option = option_var.get()
    nest_file = nest_file_entry.get_real_value()
    arxml_file = arxml_file_entry.get_real_value()
    odx_file = odx_file_entry.get_real_value()

    if not nest_path or not option or not nest_file:
        messagebox.showerror("Error", "Please fill in all required fields.")
        return None
    if option in ['2', '3'] and (not arxml_file or not odx_file):
        messagebox.showerror("Error", "Please select ARXML and ODX files for options 2 and 3.")
        return None

    config = {
        'nest_path': nest_path,
        'option': option,
        'nest_file': nest_file,
        'arxml_file': arxml_file,
        'odx_file': odx_file
    }
    save_nest_config(config)

    bat_content = build_nest_bat_content(nest_path, option, nest_file, arxml_file, odx_file)

    # Ask user where to save the .bat file
    bat_path = filedialog.asksaveasfilename(
        defaultextension=".bat",
        filetypes=[("Batch files", "*.bat"), ("All files", "*.*")],
        title="Save Batch File As",
        initialfile="run_nest_cli.bat"
    )
    if not bat_path:  # user cancelled
        return None

    with open(bat_path, "w") as f:
        f.write(bat_content)
    # remember folder
    global LAST_BAT_DIR
    LAST_BAT_DIR = os.path.dirname(bat_path)
    messagebox.showinfo("Saved", f"Batch file saved as: {bat_path}")
    return bat_path



def run_nest_bat_file(nest_path_entry, option_var, nest_file_entry, arxml_file_entry, odx_file_entry):
    # Ask user to select an existing .bat and run it
    global LAST_BAT_DIR
    start_dir = LAST_BAT_DIR if os.path.isdir(LAST_BAT_DIR) else os.getcwd()
    bat_path = filedialog.askopenfilename(
        initialdir=start_dir,
        title="Select .bat file already created for running now",
        filetypes=[("Batch files", "*.bat"), ("All files", "*.*")]
    )
    if not bat_path:
        return
    if not os.path.exists(bat_path):
        messagebox.showerror("Error", "Selected BAT file does not exist.")
        return
    try:
        import subprocess
        subprocess.run(['cmd', '/c', bat_path], shell=True)
        # remember folder
        LAST_BAT_DIR = os.path.dirname(bat_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run batch file: {e}")




def open_nest_window():
    config = load_nest_config()
    nest_window = tk.Toplevel(root)
    nest_window.grid_columnconfigure(0, weight=1)
    nest_window.grid_columnconfigure(1, weight=1)
    nest_window.grid_columnconfigure(2, weight=1)
    nest_window.title("NEST Test Runner")
    nest_window.geometry("760x600")  # Base height
    nest_window.configure(bg="#d0e7ff")

    nest_path_var = tk.StringVar(value=config.get('nest_path', ''))
    option_var = tk.StringVar(value=config.get('option', ''))
    nest_file_var = tk.StringVar(value=config.get('nest_file', ''))
    arxml_file_var = tk.StringVar(value=config.get('arxml_file', ''))
    odx_file_var = tk.StringVar(value=config.get('odx_file', ''))

    # Help visibility toggle
    show_help = tk.BooleanVar(value=False)

    # NEST Executable Folder with placeholder
    tk.Label(nest_window, text="NEST Executable Folder:", bg="#d0e7ff").grid(row=0, column=0, sticky='e', padx=5,
                                                                             pady=5)
    nest_path_entry = PlaceholderEntry(nest_window, nest_path_var,
                                       "Select the folder containing NEST.exe", width=90)
    nest_path_entry.grid(row=0, column=1, padx=5)
    tk.Button(nest_window, text="Browse", command=lambda: browse_folder(nest_path_var)).grid(row=0, column=2, padx=5)

    option_frame = tk.LabelFrame(nest_window, text="Option (required)", padx=10, pady=10, bg="#d0e7ff")
    option_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

    # Enhanced option selection with checkboxes
    def select_option(val):
        option_var.set(val)
        for key, var in option_vars.items():
            if key != val:
                var.set(0)

    option_vars = {'2': tk.IntVar(), '3': tk.IntVar(), '4': tk.IntVar()}
    for idx, key in enumerate(option_vars):
        cb = tk.Checkbutton(option_frame, text=f"Option {key}", variable=option_vars[key],
                            command=lambda k=key: select_option(k), bg="#d0e7ff")
        cb.grid(row=0, column=idx, padx=10)

    option_desc = (
        "2: Generating CANoe configuration and auto-start tests (requires ARXML & ODX)\n"
        "3: Generating CANoe configuration only (no auto-run, requires ARXML & ODX)\n"
        "4: Start tests only (configuration must be done with 2 or 3 first)"
    )
    tk.Label(option_frame, text=option_desc, justify='left', anchor='w', font=("Consolas", 10), bg="#d0e7ff").grid(
        row=1, column=0,
        columnspan=3,
        sticky='w')

    # NEST File with placeholder
    tk.Label(nest_window, text="NEST File (.nest):", bg="#d0e7ff").grid(row=2, column=0, sticky='e', padx=5, pady=5)
    nest_file_entry = PlaceholderEntry(nest_window, nest_file_var,
                                       "Choose the .nest file", width=90)
    nest_file_entry.grid(row=2, column=1, padx=5)
    tk.Button(nest_window, text="Browse",
              command=lambda: browse_file(nest_file_var, [('NEST files', '*.nest'), ('All files', '*.*')])).grid(row=2,
                                                                                                                 column=2,
                                                                                                                 padx=5)

    # ARXML File with placeholder
    tk.Label(nest_window, text="ARXML File (.arxml):", bg="#d0e7ff").grid(row=3, column=0, sticky='e', padx=5, pady=5)
    arxml_file_entry = PlaceholderEntry(nest_window, arxml_file_var,
                                        "Choose the .arxml file", width=90)
    arxml_file_entry.grid(row=3, column=1, padx=5)
    tk.Button(nest_window, text="Browse",
              command=lambda: browse_file(arxml_file_var, [('ARXML files', '*.arxml'), ('All files', '*.*')])).grid(
        row=3, column=2, padx=5)

    # ODX File with placeholder
    tk.Label(nest_window, text="ODX File (.odx-d):", bg="#d0e7ff").grid(row=4, column=0, sticky='e', padx=5, pady=5)
    odx_file_entry = PlaceholderEntry(nest_window, odx_file_var,
                                      "Choose the .odx-d file", width=90)
    odx_file_entry.grid(row=4, column=1, padx=5)
    tk.Button(nest_window, text="Browse",
              command=lambda: browse_file(odx_file_var, [('ODX files', '*.odx-d'), ('All files', '*.*')])).grid(row=4,
                                                                                                                column=2,
                                                                                                                padx=5)

    # Scheduling section with improved date handling and recurrence
    schedule_frame = tk.LabelFrame(nest_window, text="Scheduling (Optional)", padx=10, pady=10, bg="#d0e7ff")
    schedule_frame.grid(row=5, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

    # Get system date format
    system_date_format = get_system_date_format()

    tk.Label(schedule_frame, text="Schedule Date:", bg="#d0e7ff").grid(row=0, column=0, sticky='e', padx=5, pady=5)
    date_entry = DateEntry(schedule_frame, date_pattern=system_date_format,
                           locale='en_US', selectmode='day', mindate=datetime.date.today())
    date_entry.grid(row=0, column=1, sticky='w', padx=5)

    tk.Label(schedule_frame, text="Schedule Time (24h format):", bg="#d0e7ff").grid(row=1, column=0, sticky='e', padx=5,
                                                                                    pady=5)
    time_entry_frame = tk.Frame(schedule_frame, bg="#d0e7ff")
    time_entry_frame.grid(row=1, column=1, sticky='w', padx=5)

    # Hour dropdown
    hour_var = tk.StringVar(value="09")
    hour_combo = ttk.Combobox(time_entry_frame, textvariable=hour_var,
                              values=[f"{i:02d}" for i in range(24)],
                              state="readonly", width=4)
    hour_combo.pack(side="left")

    tk.Label(time_entry_frame, text=":", font=("Arial", 10), bg="#d0e7ff").pack(side="left")

    # Minute dropdown
    minute_var = tk.StringVar(value="00")
    minute_combo = ttk.Combobox(time_entry_frame, textvariable=minute_var,
                                values=[f"{i:02d}" for i in range(0, 60, 5)],  # every 5 minutes
                                state="readonly", width=4)
    minute_combo.pack(side="left")

    tk.Label(time_entry_frame, text="(24h format)", font=("Arial", 8), fg="gray", bg="#d0e7ff").pack(side="left",
                                                                                                     padx=(5, 0))

    # Recurrence options
    tk.Label(schedule_frame, text="Recurrence:", bg="#d0e7ff").grid(row=2, column=0, sticky='e', padx=5, pady=5)
    recurrence_var = tk.StringVar(value="Once")
    recurrence_combo = ttk.Combobox(schedule_frame, textvariable=recurrence_var,
                                    values=["Once", "Daily", "Weekly", "Monthly"],
                                    state="readonly", width=15)
    recurrence_combo.grid(row=2, column=1, sticky='w', padx=5)

    # Interval with help toggle button
    interval_frame = tk.Frame(schedule_frame, bg="#d0e7ff")
    interval_frame.grid(row=3, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

    tk.Label(interval_frame, text="Interval:", bg="#d0e7ff").grid(row=0, column=0, sticky='e', padx=5)
    interval_var = tk.IntVar(value=1)
    interval_spinbox = tk.Spinbox(interval_frame, from_=1, to=365, textvariable=interval_var,
                                  width=10, state="readonly")
    interval_spinbox.grid(row=0, column=1, sticky='w', padx=5)

    # Help toggle button
    help_button = tk.Button(interval_frame, text="Show Help", font=("Arial", 8),
                            command=lambda: toggle_help())
    help_button.grid(row=0, column=2, padx=10)

    # Help explanation (initially hidden)
    schedule_explanation = tk.Label(schedule_frame,
                                    text="Recurrence Options:\n"
                                         "• Once: Run only one time at the specified date/time\n"
                                         "• Daily: Run every day (or every X days if interval > 1)\n"
                                         "• Weekly: Run every week (or every X weeks if interval > 1)\n"
                                         "• Monthly: Run every month (or every X months if interval > 1)\n\n"
                                         "Interval Examples:\n"
                                         "• Daily + Interval 1 = Every day\n"
                                         "• Daily + Interval 3 = Every 3 days\n"
                                         "• Weekly + Interval 2 = Every 2 weeks\n"
                                         "• Monthly + Interval 6 = Every 6 months\n\n"
                                         "Time Format: Use dropdown lists to select hour and minute",
                                    justify='left', font=("Arial", 9), fg="blue", bg="#d0e7ff")

    def toggle_help():
        if show_help.get():
            schedule_explanation.grid_remove()
            help_button.config(text="Show Help")
            nest_window.geometry("760x600")  # Smaller height
            show_help.set(False)
        else:
            schedule_explanation.grid(row=4, column=0, columnspan=3, sticky='w', padx=5, pady=10)
            help_button.config(text="Hide Help")
            nest_window.geometry("760x780")  # Larger height
            show_help.set(True)

    # Enable/disable interval based on recurrence selection
    def on_recurrence_change(*args):
        if recurrence_var.get() == "Once":
            interval_spinbox.config(state="disabled")
        else:
            interval_spinbox.config(state="readonly")

    recurrence_var.trace('w', on_recurrence_change)
    on_recurrence_change()  # Initial state

    button_frame = tk.Frame(nest_window, bg="#d0e7ff")
    button_frame.grid(row=6, column=0, columnspan=3, pady=15)

    def save_and_schedule():
        bat_path = save_nest_bat_file(nest_path_entry, option_var, nest_file_entry, arxml_file_entry, odx_file_entry)
        if bat_path and hour_var.get() and minute_var.get():
            selected_date = date_entry.get_date()
            selected_time = f"{hour_var.get()}:{minute_var.get()}"

            # Check if selected date and time is in the past
            try:
                selected_datetime = datetime.datetime.combine(
                    selected_date,
                    datetime.datetime.strptime(selected_time, "%H:%M").time()
                )
                if selected_datetime < datetime.datetime.now():
                    messagebox.showerror("Invalid Schedule",
                                         "Cannot schedule a task in the past. Please select a future date and time.")
                    return
            except ValueError:
                pass  # Time validation will be handled by schedule_bat_file

            schedule_bat_file(bat_path, "NEST_Test_Run", selected_date, selected_time,
                              recurrence_var.get(), interval_var.get())

    tk.Button(button_frame, text="Save .bat",
              command=lambda: save_nest_bat_file(nest_path_entry, option_var, nest_file_entry, arxml_file_entry,
                                                 odx_file_entry), width=20).pack(side="left", padx=10)
    tk.Button(button_frame, text="Run .bat",
              command=lambda: run_nest_bat_file(nest_path_entry, option_var, nest_file_entry, arxml_file_entry,
                                                odx_file_entry),
              width=20).pack(side="left", padx=10)
    tk.Button(button_frame, text="Save & Schedule .bat", command=save_and_schedule, width=25).pack(side="left", padx=10)

    # --- add modal window ---
    nest_window.transient(root)
    nest_window.grab_set()
    nest_window.focus_set()
    nest_window.wait_window()


# ------------------ NTS Implementation ------------------

def load_nts_config():
    if os.path.exists('configNTS.json'):
        with open('configNTS.json', 'r') as f:
            return json.load(f)
    return {}


def save_nts_config(config):
    with open('configNTS.json', 'w') as f:
        json.dump(config, f)


def build_nts_bat_content(cli_path, config_file, log_dir, zuser, zpassword):
    cli_path = os.path.normpath(cli_path)
    config_file = os.path.normpath(config_file)
    log_dir = os.path.normpath(log_dir)
    return (
        '@echo off\n'
        f'set NTS_CLI_PATH="{cli_path}"\n'
        f'set CONFIG_FILE_PATH="{config_file}"\n'
        f'set LOG_DIRECTORY="{log_dir}"\n'
        f'set ZENZEFI_USER="{zuser}"\n'
        f'set ZENZEFI_PASSWORD="{zpassword}"\n'
        f'%NTS_CLI_PATH% run %CONFIG_FILE_PATH% -log %LOG_DIRECTORY% -zuser %ZENZEFI_USER% -zpassword %ZENZEFI_PASSWORD%\n'
    )


def save_nts_bat_file(cli_path_entry, config_file_entry, log_dir_entry, zuser_var, zpassword_var):
    cli_path = cli_path_entry.get_real_value()
    config_file = config_file_entry.get_real_value()
    log_dir = log_dir_entry.get_real_value()
    zuser = zuser_var.get()
    zpassword = zpassword_var.get()

    if not cli_path or not config_file or not log_dir or not zuser or not zpassword:
        messagebox.showerror("Error", "Please fill in all fields.")
        return None

    config = {
        'cli_path': cli_path,
        'config_file': config_file,
        'log_dir': log_dir,
        'zuser': zuser,
        'zpassword': zpassword
    }
    save_nts_config(config)

    bat_content = build_nts_bat_content(cli_path, config_file, log_dir, zuser, zpassword)

    # Ask user where to save the .bat file
    bat_path = filedialog.asksaveasfilename(
        defaultextension=".bat",
        filetypes=[("Batch files", "*.bat"), ("All files", "*.*")],
        title="Save Batch File As",
        initialfile="run_nts_cli.bat"
    )
    if not bat_path:  # user cancelled
        return None

    with open(bat_path, "w") as f:
        f.write(bat_content)
    # remember folder
    global LAST_BAT_DIR
    LAST_BAT_DIR = os.path.dirname(bat_path)
    messagebox.showinfo("Saved", f"Batch file saved as: {bat_path}")
    return bat_path



def run_nts_bat_file(cli_path_entry, config_file_entry, log_dir_entry, zuser_var, zpassword_var):
    # Ask user to select an existing .bat and run it
    global LAST_BAT_DIR
    start_dir = LAST_BAT_DIR if os.path.isdir(LAST_BAT_DIR) else os.getcwd()
    bat_path = filedialog.askopenfilename(
        initialdir=start_dir,
        title="Select .bat file already created for running now",
        filetypes=[("Batch files", "*.bat"), ("All files", "*.*")]
    )
    if not bat_path:
        return
    if not os.path.exists(bat_path):
        messagebox.showerror("Error", "Selected BAT file does not exist.")
        return
    try:
        import subprocess
        subprocess.run(['cmd', '/c', bat_path], shell=True)
        # remember folder
        LAST_BAT_DIR = os.path.dirname(bat_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run batch file: {e}")




def open_nts_window():
    config = load_nts_config()
    nts_window = tk.Toplevel(root)
    nts_window.grid_columnconfigure(0, weight=1)
    nts_window.grid_columnconfigure(1, weight=1)
    nts_window.grid_columnconfigure(2, weight=1)
    nts_window.title("NTS Test Runner")
    nts_window.geometry("750x550")  # Base height
    nts_window.configure(bg="#d0e7ff")

    cli_path_var = tk.StringVar(value=config.get('cli_path', ''))
    config_file_var = tk.StringVar(value=config.get('config_file', ''))
    log_dir_var = tk.StringVar(value=config.get('log_dir', ''))
    zuser_var = tk.StringVar(value=config.get('zuser', ''))
    zpassword_var = tk.StringVar(value=config.get('zpassword', ''))

    # Help visibility toggle for NTS
    nts_show_help = tk.BooleanVar(value=False)

    # NTS CLI Executable with placeholder
    tk.Label(nts_window, text="NTS CLI Executable:", bg="#d0e7ff").grid(row=0, column=0, sticky='e', padx=5, pady=5)
    cli_path_entry = PlaceholderEntry(nts_window, cli_path_var,
                                      "Select NTS CLI .exe:", width=90)
    cli_path_entry.grid(row=0, column=1, padx=5)
    tk.Button(nts_window, text="Browse",
              command=lambda: browse_file(cli_path_var, [('Executable', '*.exe'), ('All files', '*.*')])).grid(row=0,
                                                                                                               column=2,
                                                                                                               padx=5)

    # Config File with placeholder
    tk.Label(nts_window, text="Config File (.nts):", bg="#d0e7ff").grid(row=1, column=0, sticky='e', padx=5, pady=5)
    config_file_entry = PlaceholderEntry(nts_window, config_file_var,
                                         "Choose the .nts configuration file", width=90)
    config_file_entry.grid(row=1, column=1, padx=5)
    tk.Button(nts_window, text="Browse",
              command=lambda: browse_file(config_file_var, [('NTS Config', '*.nts'), ('All files', '*.*')])).grid(row=1,
                                                                                                                  column=2,
                                                                                                                  padx=5)

    # Log Directory with placeholder
    tk.Label(nts_window, text="Log Directory:", bg="#d0e7ff").grid(row=2, column=0, sticky='e', padx=5, pady=5)
    log_dir_entry = PlaceholderEntry(nts_window, log_dir_var,
                                     "Choose the directory for logs", width=90)
    log_dir_entry.grid(row=2, column=1, padx=5)
    tk.Button(nts_window, text="Browse", command=lambda: browse_folder(log_dir_var)).grid(row=2, column=2, padx=5)

    tk.Label(nts_window, text="ZenZefi User:", bg="#d0e7ff").grid(row=3, column=0, sticky='e', padx=5, pady=5)
    tk.Entry(nts_window, textvariable=zuser_var, width=45).grid(row=3, column=1, sticky='w', padx=5)

    tk.Label(nts_window, text="ZenZefi Password:", bg="#d0e7ff").grid(row=4, column=0, sticky='e', padx=5, pady=5)
    password_entry = tk.Entry(nts_window, textvariable=zpassword_var, width=45, show='*')
    password_entry.grid(row=4, column=1, sticky='w', padx=5, pady=5)

    # Checkbox immediately next to password entry
    show_password_var = tk.BooleanVar(value=False)

    def toggle_password():
        if password_entry.cget('show') == '':
            password_entry.config(show='*')
            show_password_var.set(False)
        else:
            password_entry.config(show='')
            show_password_var.set(True)

    show_password_cb = tk.Checkbutton(nts_window, text="Show Password", variable=show_password_var,
                                      command=toggle_password, bg="#d0e7ff")
    show_password_cb.grid(row=4, column=1, sticky='w', padx=(350, 5), pady=5)

    # Scheduling section for NTS with improved date handling and recurrence
    schedule_frame = tk.LabelFrame(nts_window, text="Scheduling (Optional)", padx=10, pady=10, bg="#d0e7ff")
    schedule_frame.grid(row=5, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

    # Get system date format
    system_date_format = get_system_date_format()

    tk.Label(schedule_frame, text="Schedule Date:", bg="#d0e7ff").grid(row=0, column=0, sticky='e', padx=5, pady=5)
    nts_date_entry = DateEntry(schedule_frame, date_pattern=system_date_format,
                               locale='en_US', selectmode='day', mindate=datetime.date.today())
    nts_date_entry.grid(row=0, column=1, sticky='w', padx=5)

    tk.Label(schedule_frame, text="Schedule Time (24h format):", bg="#d0e7ff").grid(row=1, column=0, sticky='e', padx=5,
                                                                                    pady=5)
    nts_time_entry_frame = tk.Frame(schedule_frame, bg="#d0e7ff")
    nts_time_entry_frame.grid(row=1, column=1, sticky='w', padx=5)

    # NTS Hour dropdown
    nts_hour_var = tk.StringVar(value="09")
    nts_hour_combo = ttk.Combobox(nts_time_entry_frame, textvariable=nts_hour_var,
                                  values=[f"{i:02d}" for i in range(24)],
                                  state="readonly", width=4)
    nts_hour_combo.pack(side="left")

    tk.Label(nts_time_entry_frame, text=":", font=("Arial", 10), bg="#d0e7ff").pack(side="left")

    # NTS Minute dropdown
    nts_minute_var = tk.StringVar(value="00")
    nts_minute_combo = ttk.Combobox(nts_time_entry_frame, textvariable=nts_minute_var,
                                    values=[f"{i:02d}" for i in range(0, 60, 5)],  # every 5 minutes
                                    state="readonly", width=4)
    nts_minute_combo.pack(side="left")

    tk.Label(nts_time_entry_frame, text="(24h format)", font=("Arial", 8), fg="gray", bg="#d0e7ff").pack(side="left",
                                                                                                         padx=(5, 0))

    # Recurrence options for NTS
    tk.Label(schedule_frame, text="Recurrence:", bg="#d0e7ff").grid(row=2, column=0, sticky='e', padx=5, pady=5)
    nts_recurrence_var = tk.StringVar(value="Once")
    nts_recurrence_combo = ttk.Combobox(schedule_frame, textvariable=nts_recurrence_var,
                                        values=["Once", "Daily", "Weekly", "Monthly"],
                                        state="readonly", width=15)
    nts_recurrence_combo.grid(row=2, column=1, sticky='w', padx=5)

    # Interval with help toggle for NTS
    nts_interval_frame = tk.Frame(schedule_frame, bg="#d0e7ff")
    nts_interval_frame.grid(row=3, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

    tk.Label(nts_interval_frame, text="Interval:", bg="#d0e7ff").grid(row=0, column=0, sticky='e', padx=5)
    nts_interval_var = tk.IntVar(value=1)
    nts_interval_spinbox = tk.Spinbox(nts_interval_frame, from_=1, to=365, textvariable=nts_interval_var,
                                      width=10, state="readonly")
    nts_interval_spinbox.grid(row=0, column=1, sticky='w', padx=5)

    # Help toggle button for NTS
    nts_help_button = tk.Button(nts_interval_frame, text="Show Help", font=("Arial", 8),
                                command=lambda: toggle_nts_help())
    nts_help_button.grid(row=0, column=2, padx=10)

    # Help explanation for NTS (initially hidden)
    nts_schedule_explanation = tk.Label(schedule_frame,
                                        text="Scheduling Help:\n"
                                             "• Once: Run only one time\n"
                                             "• Daily + Interval 1: Every day\n"
                                             "• Daily + Interval 3: Every 3 days\n"
                                             "• Weekly + Interval 2: Every 2 weeks\n"
                                             "• Monthly + Interval 6: Every 6 months\n\n"
                                             "Time Format: Use dropdown lists to select hour and minute",
                                        justify='left', font=("Arial", 9), fg="blue", bg="#d0e7ff")

    def toggle_nts_help():
        if nts_show_help.get():
            nts_schedule_explanation.grid_remove()
            nts_help_button.config(text="Show Help")
            nts_window.geometry("750x550")  # Smaller height
            nts_show_help.set(False)
        else:
            nts_schedule_explanation.grid(row=4, column=0, columnspan=3, sticky='w', padx=5, pady=10)
            nts_help_button.config(text="Hide Help")
            nts_window.geometry("750x680")  # Larger height
            nts_show_help.set(True)

    # Enable/disable interval based on recurrence selection
    def on_nts_recurrence_change(*args):
        if nts_recurrence_var.get() == "Once":
            nts_interval_spinbox.config(state="disabled")
        else:
            nts_interval_spinbox.config(state="readonly")

    nts_recurrence_var.trace('w', on_nts_recurrence_change)
    on_nts_recurrence_change()  # Initial state

    button_frame = tk.Frame(nts_window, bg="#d0e7ff")
    button_frame.grid(row=6, column=0, columnspan=3, pady=20)

    def save_and_schedule_nts():
        bat_path = save_nts_bat_file(cli_path_entry, config_file_entry, log_dir_entry, zuser_var, zpassword_var)
        if bat_path and nts_hour_var.get() and nts_minute_var.get():
            selected_date = nts_date_entry.get_date()
            selected_time = f"{nts_hour_var.get()}:{nts_minute_var.get()}"

            # Check if selected date and time is in the past
            try:
                selected_datetime = datetime.datetime.combine(
                    selected_date,
                    datetime.datetime.strptime(selected_time, "%H:%M").time()
                )
                if selected_datetime < datetime.datetime.now():
                    messagebox.showerror("Invalid Schedule",
                                         "Cannot schedule a task in the past. Please select a future date and time.")
                    return
            except ValueError:
                pass  # Time validation will be handled by schedule_bat_file

            schedule_bat_file(bat_path, "NTS_Test_Run", selected_date, selected_time,
                              nts_recurrence_var.get(), nts_interval_var.get())

    tk.Button(button_frame, text="Save .bat",
              command=lambda: save_nts_bat_file(cli_path_entry, config_file_entry, log_dir_entry, zuser_var,
                                                zpassword_var),
              width=20).pack(side="left", padx=10)
    tk.Button(button_frame, text="Run .bat",
              command=lambda: run_nts_bat_file(cli_path_entry, config_file_entry, log_dir_entry, zuser_var,
                                               zpassword_var),
              width=20).pack(side="left", padx=10)
    tk.Button(button_frame, text="Save & Schedule .bat", command=save_and_schedule_nts, width=25).pack(side="left",
                                                                                                       padx=10)

    desc = (
        "This tool generates a .bat file for running NTS CLI in headless mode with ZenZefi credentials.\n"
        "Fields are saved for next use. Password is stored in plain text in configNTS.json and run_nts_cli.bat!"
    )
    tk.Label(nts_window, text=desc, fg="gray", justify="left", bg="#d0e7ff").grid(row=7, column=0, columnspan=3,
                                                                                  sticky='w', padx=5,
                                                                                  pady=5)

    # --- add modal window ---
    nts_window.transient(root)
    nts_window.grab_set()
    nts_window.focus_set()
    nts_window.wait_window()


def proceed():
    selected_tool = tool_var.get()
    if selected_tool == "NEST":
        open_nest_window()
    elif selected_tool == "NTS":
        open_nts_window()
    else:
        messagebox.showinfo("Info", f"Tool '{selected_tool}' is not yet implemented.")


# ------------------ Direct BAT Scheduler ------------------

def open_bat_scheduler():
    scheduler_window = tk.Toplevel(root)
    scheduler_window.title("Schedule a Run")
    scheduler_window.geometry("650x450")  # Base height
    scheduler_window.configure(bg="#d0e7ff")

    bat_file_var = tk.StringVar()
    task_name_var = tk.StringVar(value="Set name")

    # Help visibility toggle for BAT scheduler
    bat_show_help = tk.BooleanVar(value=False)

    # BAT file selection with placeholder
    tk.Label(scheduler_window, text="Select BAT File:", font=("Arial", 12, "bold"), bg="#d0e7ff").pack(pady=10)

    file_frame = tk.Frame(scheduler_window, bg="#d0e7ff")
    file_frame.pack(pady=5, padx=20, fill="x")

    bat_file_entry = PlaceholderEntry(file_frame, bat_file_var,
                                      "Choose the .bat file for scheduling", width=70)
    bat_file_entry.pack(side="left", padx=5)
    tk.Button(file_frame, text="Browse",
              command=lambda: browse_file(bat_file_var, [('Batch files', '*.bat'), ('All files', '*.*')])).pack(
        side="left", padx=5)

    # Task name
    tk.Label(scheduler_window, text="Task Name:", font=("Arial", 11), bg="#d0e7ff").pack(pady=(20, 5))
    tk.Entry(scheduler_window, textvariable=task_name_var, width=50).pack(pady=5)

    # Scheduling section
    schedule_frame = tk.LabelFrame(scheduler_window, text="Scheduling", padx=10, pady=10, bg="#d0e7ff")
    schedule_frame.pack(pady=20, padx=20, fill="x")

    # Get system date format
    system_date_format = get_system_date_format()

    tk.Label(schedule_frame, text="Schedule Date:", bg="#d0e7ff").grid(row=0, column=0, sticky='e', padx=5, pady=5)
    date_entry = DateEntry(schedule_frame, date_pattern=system_date_format,
                           locale='en_US', selectmode='day', mindate=datetime.date.today())
    date_entry.grid(row=0, column=1, sticky='w', padx=5)

    tk.Label(schedule_frame, text="Schedule Time (24h format):", bg="#d0e7ff").grid(row=1, column=0, sticky='e', padx=5,
                                                                                    pady=5)
    time_entry_frame = tk.Frame(schedule_frame, bg="#d0e7ff")
    time_entry_frame.grid(row=1, column=1, sticky='w', padx=5)

    # BAT Scheduler Hour dropdown
    bat_hour_var = tk.StringVar(value="09")
    bat_hour_combo = ttk.Combobox(time_entry_frame, textvariable=bat_hour_var,
                                  values=[f"{i:02d}" for i in range(24)],
                                  state="readonly", width=4)
    bat_hour_combo.pack(side="left")

    tk.Label(time_entry_frame, text=":", font=("Arial", 10), bg="#d0e7ff").pack(side="left")

    # BAT Scheduler Minute dropdown
    bat_minute_var = tk.StringVar(value="00")
    bat_minute_combo = ttk.Combobox(time_entry_frame, textvariable=bat_minute_var,
                                    values=[f"{i:02d}" for i in range(0, 60, 5)],  # every 5 minutes
                                    state="readonly", width=4)
    bat_minute_combo.pack(side="left")

    tk.Label(time_entry_frame, text="(24h format)", font=("Arial", 8), fg="gray", bg="#d0e7ff").pack(side="left",
                                                                                                     padx=(5, 0))

    # Recurrence options
    tk.Label(schedule_frame, text="Recurrence:", bg="#d0e7ff").grid(row=2, column=0, sticky='e', padx=5, pady=5)
    recurrence_var = tk.StringVar(value="Once")
    recurrence_combo = ttk.Combobox(schedule_frame, textvariable=recurrence_var,
                                    values=["Once", "Daily", "Weekly", "Monthly"],
                                    state="readonly", width=15)
    recurrence_combo.grid(row=2, column=1, sticky='w', padx=5)

    # Interval with help toggle for BAT scheduler
    bat_interval_frame = tk.Frame(schedule_frame, bg="#d0e7ff")
    bat_interval_frame.grid(row=3, column=0, columnspan=3, sticky='ew', padx=5, pady=5)

    tk.Label(bat_interval_frame, text="Interval:", bg="#d0e7ff").grid(row=0, column=0, sticky='e', padx=5)
    interval_var = tk.IntVar(value=1)
    interval_spinbox = tk.Spinbox(bat_interval_frame, from_=1, to=365, textvariable=interval_var,
                                  width=10, state="readonly")
    interval_spinbox.grid(row=0, column=1, sticky='w', padx=5)

    # Help toggle button for BAT scheduler
    bat_help_button = tk.Button(bat_interval_frame, text="Show Help", font=("Arial", 8),
                                command=lambda: toggle_bat_help())
    bat_help_button.grid(row=0, column=2, padx=10)

    # Help explanation for BAT scheduler (initially hidden)
    bat_schedule_explanation = tk.Label(schedule_frame,
                                        text="How to Schedule:\n"
                                             "• Once: Run only one time at specified date/time\n"
                                             "• Daily + Interval 1: Run every day\n"
                                             "• Daily + Interval 2: Run every 2 days\n"
                                             "• Weekly + Interval 1: Run every week\n"
                                             "• Monthly + Interval 3: Run every 3 months\n\n"
                                             "Time Format: Use dropdown lists to select hour and minute\n"
                                             "Note: Task will be created in Windows Task Scheduler",
                                        justify='left', font=("Arial", 9), fg="blue", bg="#d0e7ff")

    def toggle_bat_help():
        if bat_show_help.get():
            bat_schedule_explanation.grid_remove()
            bat_help_button.config(text="Show Help")
            scheduler_window.geometry("650x450")  # Smaller height
            bat_show_help.set(False)
        else:
            bat_schedule_explanation.grid(row=4, column=0, columnspan=3, sticky='w', padx=5, pady=10)
            bat_help_button.config(text="Hide Help")
            scheduler_window.geometry("650x600")  # Larger height
            bat_show_help.set(True)

    # Enable/disable interval based on recurrence selection
    def on_recurrence_change(*args):
        if recurrence_var.get() == "Once":
            interval_spinbox.config(state="disabled")
        else:
            interval_spinbox.config(state="readonly")

    recurrence_var.trace('w', on_recurrence_change)
    on_recurrence_change()  # Initial state

    # Buttons
    button_frame = tk.Frame(scheduler_window, bg="#d0e7ff")
    button_frame.pack(pady=20)

    def schedule_bat():
        bat_file = bat_file_entry.get_real_value()
        task_name = task_name_var.get()
        selected_time = f"{bat_hour_var.get()}:{bat_minute_var.get()}"

        if not bat_file:
            messagebox.showerror("Error", "Please select a BAT file.")
            return
        if not os.path.exists(bat_file):
            messagebox.showerror("Error", "Selected BAT file does not exist.")
            return
        if not task_name.strip():
            messagebox.showerror("Error", "Please enter a task name.")
            return
        if not bat_hour_var.get() or not bat_minute_var.get():
            messagebox.showerror("Error", "Please select both hour and minute.")
            return

        selected_date = date_entry.get_date()

        # Check if selected date and time is in the past
        try:
            selected_datetime = datetime.datetime.combine(
                selected_date,
                datetime.datetime.strptime(selected_time, "%H:%M").time()
            )
            if selected_datetime < datetime.datetime.now():
                messagebox.showerror("Invalid Schedule",
                                     "Cannot schedule a task in the past. Please select a future date and time.")
                return
        except ValueError:
            messagebox.showerror("Invalid Time",
                                 "Please select valid hour and minute values.")
            return

        # Schedule the BAT file
        try:
            ok = schedule_bat_file(bat_file, task_name, selected_date, selected_time,
                                   recurrence_var.get(), interval_var.get())
            # Close the window only if it succeeded
            if ok:
                scheduler_window.destroy()
        except Exception as e:
            messagebox.showerror("Scheduling Failed", f"Failed to create scheduled task:\n{str(e)}")

    tk.Button(button_frame, text="Save Schedule", command=schedule_bat,
              width=18, height=2, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white").pack(side="left", padx=10)
    tk.Button(button_frame, text="Close", command=scheduler_window.destroy,
              width=12, height=2, font=("Arial", 10)).pack(side="left", padx=10)

    # Make window modal
    scheduler_window.transient(root)
    scheduler_window.grab_set()
    scheduler_window.focus_set()


# ------------------ Main Application ------------------

root = tk.Tk()
root.configure(bg="#d0e7ff")  # Light blue
root.title("ZF TestTool Launcher")
try:
    root.iconbitmap("TTL_Icon.ico")
except:
    pass  # Icon file not found, continue without it
root.geometry("600x580")  # Increased size for help button
root.resizable(False, False)

# Title
tk.Label(root, text="ZF TestTool Launcher", font=("Arial", 16, "bold"), bg="#d0e7ff").pack(pady=10)

# Small help button in top-right corner
help_button = tk.Button(root, text="?", command=open_help_window,
                        font=("Arial", 8, "bold"), bg="#6B7DB3", fg="white",
                        width=2, height=1)
help_button.place(x=570, y=10)

# Small settings button next to help button
settings_button = tk.Button(root, text="⚙", command=open_settings_window,
                            font=("Arial", 8, "bold"), bg="#6B7DB3", fg="white",
                            width=2, height=1)
settings_button.place(x=540, y=10)

# ZenZefi Login Status Widget
login_widget = LoginStatusWidget(root)
login_widget.pack(pady=10, padx=20, fill="x")

# Tool configuration section
tk.Label(root, text="Select Tool for TASK configuration:", font=("Arial", 11), bg="#d0e7ff").pack(pady=5)

tools = ["NEST", "NTS", "EXAM", "DIVA"]
tool_var = tk.StringVar(value=tools[0])
tool_menu = ttk.Combobox(root, textvariable=tool_var, values=tools, state="readonly")
tool_menu.pack(pady=5)

# Call-to-action text
tk.Label(root, text="Create .bat files for automatic schedule run",
         font=("Arial", 9), fg="#4A5568", bg="#d0e7ff").pack(pady=(0, 5))

tk.Button(root, text="Launch Configuration", command=proceed,
          width=25, font=("Arial", 10)).pack(pady=10)

# Separator
separator = tk.Frame(root, height=2, bg="gray")
separator.pack(fill="x", padx=20, pady=10)

# Direct scheduler section
tk.Label(root, text="Schedule a Test Tool Run:", font=("Arial", 11), bg="#d0e7ff").pack(pady=5)

# Call-to-action for direct scheduling
tk.Label(root, text="Already have a .bat file? Schedule it directly here",
         font=("Arial", 9), fg="#4A5568", bg="#d0e7ff").pack(pady=(0, 5))

tk.Button(root, text="Select BAT File", command=open_bat_scheduler,
          width=25, height=2, font=("Arial", 10, "bold"), bg="#90EE90").pack(pady=10)

# Pro tip at the bottom
tk.Label(root, text="Tip: Use scheduling for automated overnight testing",
         font=("Arial", 8, "italic"), fg="#718096", bg="#d0e7ff").pack(pady=(10, 5))

# Load images with error handling
try:
    image = Image.open("TestTool_L.png")
    image = image.resize((60, 60), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    image_label = tk.Label(root, image=photo, bg="#d0e7ff")
    image_label.image = photo  # keep reference
    image_label.place(x=5, y=510)  # position bottom-left (adjusted for new height)
except Exception as e:
    print(f"Failed to load TestTool_L.png: {e}")

try:
    image = Image.open("ZF_Logo.png")
    image = image.resize((30, 30), Image.ANTIALIAS)
    photo2 = ImageTk.PhotoImage(image)
    image_label2 = tk.Label(root, image=photo2, bg="#d0e7ff")
    image_label2.image = photo2  # keep reference
    image_label2.place(x=550, y=520)  # position bottom-right (adjusted for new height)
except Exception as e:
    print(f"Failed to load ZF_Logo.png: {e}")

# Show selenium availability status
if not SELENIUM_AVAILABLE:
    tk.Label(root, text="⚠️ Install selenium for ZenZefi login check: pip install selenium webdriver-manager",
             font=("Arial", 8), fg="orange", bg="#d0e7ff").pack(side="bottom", pady=5)

if __name__ == "__main__":
    root.mainloop()