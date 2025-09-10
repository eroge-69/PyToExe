import pandas as pd
import os
from pathlib import Path
import random
import sys
import logging
import json
from typing import List, Dict, Tuple, Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import ssl

# PyQt5 imports with error handling
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QGroupBox, QPushButton, QLabel, QLineEdit, QTextEdit, QCheckBox,
                                 QListWidget, QFileDialog, QMessageBox, QTabWidget, QProgressBar)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QFont
except ImportError:
    print("PyQt5 is not installed. Please install it using: pip install PyQt5")
    sys.exit(1)

# =============================================================================
#                                 CONFIGURATION
# =============================================================================

DEFAULT_CONFIG = {
    "DATA_FILE": "PFC_less_.95.xlsx",
    "DATA_SHEET_NAME": "Sheet1",
    "FILTER_CATEGORY_COLUMN_NAME": "DESC",
    "SENDER_EMAIL": "your.email@gmail.com",
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 587,
    "EMAIL_SUBJECT": "Automated Report for {category}",
    "EMAIL_BODY": """Dear Recipient,

Please find the attached report for {category}.

Best regards,
Your Name
""",
    "TEMP_FOLDER_PATH": "TempReports",
    "TEST_EMAIL_ADDRESS": "your.test.email@example.com"
}

def print_troubleshooting_guide():
    """Print troubleshooting information for Gmail connection issues."""
    guide = """
=== GMAIL CONNECTION TROUBLESHOOTING GUIDE ===

Common Issues and Solutions:

1. Authentication Errors:
   - Ensure your email and password are correct
   - Enable 2-factor authentication in your Gmail account
   - Generate an "App Password" for this application
   - Go to: https://myaccount.google.com/apppasswords

2. Security Settings:
   - Make sure "Less secure app access" is enabled (if using regular password)
   - Go to: https://myaccount.google.com/lesssecureapps
   - Note: Google may disable this option in the future

3. App Password (Recommended):
   - Enable 2FA in your Google account
   - Generate an app-specific password
   - Use the 16-character app password instead of your regular password

4. Account Permissions:
   - Ensure the account has permission to send emails
   - Check if the account is not locked for security reasons

5. Network/Firewall Issues:
   - Check if your network blocks SMTP connections
   - Try from a different network
   - Check proxy settings

For Gmail with 2FA:
1. Go to https://myaccount.google.com
2. Enable 2-factor authentication
3. Navigate to "App passwords"
4. Generate an app password for this application
5. Use the app password instead of your regular password
"""
    print(guide)

# =============================================================================
#                                 GMAIL EMAIL CLIENT
# =============================================================================

class GmailEmailClient:
    """A custom email client for Gmail using SMTP."""
    def __init__(self, sender_email: str, sender_password: str):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = None
        self.port = None
        
    def connect(self):
        """Establishes a connection to the Gmail SMTP server."""
        try:
            logging.info(f"Connecting to Gmail SMTP server for user: {self.sender_email}")
            
            # Try different SMTP configurations
            smtp_configs = [
                ("smtp.gmail.com", 587),  # Standard TLS
                ("smtp.gmail.com", 465),  # SSL
            ]
            
            for server, port in smtp_configs:
                try:
                    logging.info(f"Trying {server}:{port}")
                    
                    if port == 587:
                        # TLS connection
                        self.smtp_server = smtplib.SMTP(server, port)
                        self.smtp_server.starttls()  # Upgrade to secure connection
                    else:
                        # SSL connection
                        context = ssl.create_default_context()
                        self.smtp_server = smtplib.SMTP_SSL(server, port, context=context)
                    
                    # Login to the server
                    self.smtp_server.login(self.sender_email, self.sender_password)
                    self.port = port
                    
                    logging.info(f"Successfully connected to {server}:{port}")
                    return True
                    
                except Exception as e:
                    logging.warning(f"Connection to {server}:{port} failed: {e}")
                    if self.smtp_server:
                        try:
                            self.smtp_server.quit()
                        except:
                            pass
                        self.smtp_server = None
                    continue
            
            logging.error("All connection methods failed")
            return False
            
        except Exception as e:
            logging.error(f"Fatal error during Gmail connection: {e}")
            self.smtp_server = None
            return False

    def send(self, to: str, subject: str, contents: str, attachments: Optional[List[str]] = None, cc: Optional[List[str]] = None):
        """Sends an email with attachments and CC using SMTP."""
        if not self.smtp_server:
            raise Exception("SMTP server not connected. Please call connect() first.")
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to
            msg['Subject'] = subject
            
            # Add CC recipients if they exist
            if cc:
                msg['Cc'] = ', '.join(cc)
                all_recipients = [to] + cc
            else:
                all_recipients = [to]
            
            # Add body to email
            msg.attach(MIMEText(contents, 'plain'))
            
            # Add attachments
            if attachments:
                for attachment_path in attachments:
                    try:
                        if os.path.exists(attachment_path):
                            with open(attachment_path, "rb") as f:
                                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
                            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
                            msg.attach(part)
                            logging.info(f"Attached file: {attachment_path}")
                        else:
                            logging.warning(f"Attachment file not found: {attachment_path}. Skipping.")
                    except Exception as attach_error:
                        logging.warning(f"Error attaching file {attachment_path}: {attach_error}. Skipping.")

            # Send the message
            self.smtp_server.sendmail(self.sender_email, all_recipients, msg.as_string())
            logging.info(f"Email sent successfully to {to}")
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            raise e

    def disconnect(self):
        """Close the SMTP connection."""
        if self.smtp_server:
            try:
                self.smtp_server.quit()
                logging.info("SMTP connection closed successfully.")
            except Exception as e:
                logging.warning(f"Error closing SMTP connection: {e}")
            finally:
                self.smtp_server = None

# =============================================================================
#                                 CORE PROCESSING MODULE
# =============================================================================

class ExcelAutomationProcessor:
    def __init__(self, config: dict):
        self.config = config
        self.generated_files = {}
        self.email_mapping = {}
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('excel_automation.log', mode='a')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_data(self, file_path: str, sheet_name: str) -> pd.DataFrame:
        """Load and validate the Excel data."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File '{file_path}' not found")
                
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            if df.empty:
                raise ValueError(f"The Excel file '{file_path}' is empty or sheet '{sheet_name}' not found")
                
            self.logger.info(f"Successfully loaded data from {file_path} with {len(df)} rows")
            return df
        except FileNotFoundError as e:
            self.logger.error(str(e))
            raise
        except Exception as e:
            error_msg = f"Error loading data from {file_path}: {e}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def validate_data_columns(self, df: pd.DataFrame, required_column: str) -> bool:
        """Validate that the required column exists in the dataframe."""
        if required_column not in df.columns:
            self.logger.error(f"Required column '{required_column}' not found in data")
            self.logger.info(f"Available columns: {list(df.columns)}")
            return False
        return True

    def get_unique_categories(self, df: pd.DataFrame, category_column: str) -> List[str]:
        """Get unique categories from the dataframe."""
        unique_values = df[category_column].dropna().unique()
        categories = [str(cat).strip() for cat in unique_values if str(cat).strip() and str(cat).lower() != 'nan']
        self.logger.info(f"Found {len(categories)} unique categories")
        return categories

    def filter_data_by_category(self, df: pd.DataFrame, category_column: str, category: str) -> pd.DataFrame:
        """Filter dataframe for a specific category."""
        filtered_df = df[df[category_column] == category].copy()
        self.logger.info(f"Filtered data for category '{category}': {len(filtered_df)} rows")
        return filtered_df

    def sanitize_filename(self, name: str) -> str:
        """Sanitize category name for safe use in filenames."""
        invalid_chars = r'\/:*?"<>|'
        sanitized = "".join(c if c not in invalid_chars else "_" for c in str(name))
        # Limit filename length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized

    def setup_temp_directory(self, temp_folder: str) -> None:
        """Create temporary directory if it doesn't exist."""
        try:
            Path(temp_folder).mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Temporary directory setup: {temp_folder}")
        except Exception as e:
            self.logger.error(f"Error creating temporary directory {temp_folder}: {e}")
            raise

    def save_filtered_data(self, df: pd.DataFrame, output_path: str) -> bool:
        """Save filtered data to Excel file."""
        try:
            # Ensure the directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                
            df.to_excel(output_path, index=False, engine='openpyxl')
            self.logger.info(f"Successfully saved data to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving file {output_path}: {e}")
            return False

    def cleanup_temp_files(self, temp_folder: str) -> None:
        """Remove temporary files and directory."""
        try:
            temp_dir = Path(temp_folder)
            if temp_dir.exists():
                for file in temp_dir.glob("*"):
                    try:
                        if file.is_file():
                            file.unlink()
                            self.logger.info(f"Deleted temporary file: {file}")
                    except Exception as e:
                        self.logger.error(f"Error deleting {file}: {e}")
                
                try:
                    temp_dir.rmdir()
                    self.logger.info(f"Cleaned up temporary directory: {temp_folder}")
                except OSError as e:
                    self.logger.warning(f"Could not remove directory {temp_folder}: {e}")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def load_email_mapping(self, json_file_path: str) -> bool:
        """Load email mapping from JSON file."""
        try:
            if not os.path.exists(json_file_path):
                self.logger.error(f"Email mapping file not found: {json_file_path}")
                return False
                
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.email_mapping = json.load(f)
                
            if not isinstance(self.email_mapping, dict):
                self.logger.error("Email mapping must be a dictionary")
                return False
                
            self.logger.info(f"Successfully loaded email mapping from {json_file_path} with {len(self.email_mapping)} entries")
            return True
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in email mapping file: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading email mapping: {e}")
            return False

    def get_email_from_mapping(self, category: str) -> Optional[str]:
        """Get email address from mapping for a category."""
        return self.email_mapping.get(category)

    def initialize_email_client(self, sender_email: str, sender_password: str):
        """Initializes the Gmail email client."""
        try:
            if not sender_email or not sender_password:
                self.logger.error("Email credentials are required")
                return None
                
            client = GmailEmailClient(
                sender_email=sender_email,
                sender_password=sender_password
            )
            if client.connect():
                self.logger.info("Email client initialized successfully.")
                return client
            else:
                self.logger.error("Failed to initialize email client")
                return None
        except Exception as e:
            self.logger.error(f"Error initializing email client: {e}")
            return None

    def send_email(self, gmail_client, recipient: str, subject: str, body: str, 
                     attachment_path: Optional[str] = None, cc: Optional[List[str]] = None) -> bool:
        """Sends an email using the Gmail client."""
        try:
            if not gmail_client:
                raise Exception("Email client not initialized")
                
            attachments = [attachment_path] if attachment_path else []
            gmail_client.send(
                to=recipient,
                subject=subject,
                contents=body,
                attachments=attachments,
                cc=cc
            )
            self.logger.info(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending email to {recipient}: {e}")
            return False

    def generate_excel_files(self) -> Dict[str, Tuple[str, str]]:
        """Generate Excel files for each category and return file info."""
        self.logger.info("Starting Excel file generation...")
        
        results = {}
        try:
            # Validate configuration
            if not self.config.get("DATA_FILE"):
                raise ValueError("Data file path is required")
            if not self.config.get("DATA_SHEET_NAME"):
                raise ValueError("Sheet name is required")
            if not self.config.get("FILTER_CATEGORY_COLUMN_NAME"):
                raise ValueError("Category column name is required")
                
            df = self.load_data(self.config["DATA_FILE"], self.config["DATA_SHEET_NAME"])
            if not self.validate_data_columns(df, self.config["FILTER_CATEGORY_COLUMN_NAME"]):
                raise ValueError(f"Required column '{self.config['FILTER_CATEGORY_COLUMN_NAME']}' not found")
                
            categories = self.get_unique_categories(df, self.config["FILTER_CATEGORY_COLUMN_NAME"])
            if not categories:
                raise ValueError("No valid categories found in the data")
                
            self.setup_temp_directory(self.config["TEMP_FOLDER_PATH"])
            
            for category in categories:
                try:
                    recipient_email = self.get_email_from_mapping(category)
                    
                    if not recipient_email:
                        self.logger.warning(f"No email mapping found for category: {category}. Skipping.")
                        continue
                    
                    filtered_df = self.filter_data_by_category(df, self.config["FILTER_CATEGORY_COLUMN_NAME"], category)
                    if filtered_df.empty:
                        self.logger.warning(f"No data found for category: {category}. Skipping.")
                        continue
                        
                    safe_name = self.sanitize_filename(category)
                    output_path = os.path.join(self.config["TEMP_FOLDER_PATH"], f"{safe_name}_Report.xlsx")
                    
                    success = self.save_filtered_data(filtered_df, output_path)
                    if success:
                        results[category] = (output_path, recipient_email)
                        self.logger.info(f"Generated: {category} -> {output_path} -> {recipient_email}")
                    else:
                        self.logger.error(f"Failed to generate file for: {category}")
                        
                except Exception as cat_error:
                    self.logger.error(f"Error processing category {category}: {cat_error}")
                    continue
                    
            self.generated_files = results
            self.logger.info(f"Successfully generated {len(results)} Excel files")
            return results
                
        except Exception as e:
            self.logger.error(f"Error during Excel generation: {e}")
            return {}

    def send_test_emails(self, sender_password: str, test_recipient: str) -> Dict[str, bool]:
        """Send a single test email with a randomly selected attachment."""
        self.logger.info("Starting test email sending...")
        
        results = {}
        
        try:
            if not test_recipient:
                raise ValueError("Test recipient email is required")
                
            if not self.generated_files:
                self.logger.info("No files found, generating Excel files first...")
                self.generate_excel_files()
            
            if not self.generated_files:
                raise Exception("No files generated, cannot send test emails")
            
            client = self.initialize_email_client(self.config["SENDER_EMAIL"], sender_password)
            if not client:
                raise Exception("Failed to initialize email client")
            
            categories = list(self.generated_files.keys())
            test_category = random.choice(categories)
            test_file_path, _ = self.generated_files[test_category]
            
            subject = self.config["EMAIL_SUBJECT"].format(category="Test")
            body = self.config["EMAIL_BODY"].format(category="Test")
            
            success = self.send_email(client, test_recipient, subject, body, test_file_path)
            results["Test Email"] = success
            
            if success:
                self.logger.info(f"Test email sent to {test_recipient} with attachment for {test_category}")
            else:
                self.logger.error(f"Failed to send test email to {test_recipient}")

            client.disconnect()
            return results
            
        except Exception as e:
            self.logger.error(f"Error during test email sending: {e}")
            results["Test Email"] = False
            return results

    def send_final_emails(self, sender_password: str, cc_emails: Optional[List[str]] = None) -> Dict[str, bool]:
        """Send final emails to generated addresses with CC."""
        self.logger.info("Starting final email sending...")
        
        results = {}
        client = None
        
        try:
            if not self.generated_files:
                self.logger.info("No files found, generating Excel files first...")
                self.generate_excel_files()
            
            if not self.generated_files:
                raise Exception("No files generated, cannot send final emails")
            
            client = self.initialize_email_client(self.config["SENDER_EMAIL"], sender_password)
            if not client:
                raise Exception("Failed to initialize email client")
            
            for category, (file_path, recipient_email) in self.generated_files.items():
                try:
                    subject = self.config["EMAIL_SUBJECT"].format(category=category)
                    body = self.config["EMAIL_BODY"].format(category=category)
                    
                    success = self.send_email(client, recipient_email, subject, body, file_path, cc_emails)
                    results[category] = success
                    
                    if success:
                        cc_info = f" (CC: {', '.join(cc_emails)})" if cc_emails else ""
                        self.logger.info(f"Final email sent for {category} -> {recipient_email}{cc_info}")
                    else:
                        self.logger.error(f"Failed to send final email for {category}")
                        
                except Exception as email_error:
                    self.logger.error(f"Error sending email for {category}: {email_error}")
                    results[category] = False

        except Exception as e:
            self.logger.error(f"Error during final email sending: {e}")
            
        finally:
            if client:
                client.disconnect()
                
        return results

# =============================================================================
#                                 GRAPHICAL USER INTERFACE
# =============================================================================

class EmailWorker(QThread):
    """Worker thread for email operations to prevent UI freezing."""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, processor, operation, password=None, test_recipient=None, cc_emails=None):
        super().__init__()
        self.processor = processor
        self.operation = operation
        self.password = password
        self.test_recipient = test_recipient
        self.cc_emails = cc_emails
    
    def run(self):
        try:
            if self.operation == "generate":
                self.progress.emit("Generating Excel files...")
                result = self.processor.generate_excel_files()
                self.finished.emit(result)
                
            elif self.operation == "test_email":
                self.progress.emit("Sending test emails...")
                result = self.processor.send_test_emails(self.password, self.test_recipient)
                self.finished.emit(result)
                
            elif self.operation == "final_email":
                self.progress.emit("Sending final emails...")
                result = self.processor.send_final_emails(self.password, self.cc_emails)
                self.finished.emit(result)
                
        except Exception as e:
            self.error.emit(str(e))

class AutomationGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = None
        self.worker = None
        self.config = DEFAULT_CONFIG.copy()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Excel Automation Tool - Gmail Edition')
        self.setGeometry(100, 100, 1000, 800)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 5px;
            }
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #4a86e8;
                width: 10px;
            }
        """)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Configuration tab
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        config_layout.setSpacing(15)
        tabs.addTab(config_tab, "Configuration")
        
        # File configuration
        file_group = QGroupBox("File Configuration")
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(10)
        
        # Data file selection
        file_selector_layout = QHBoxLayout()
        file_selector_layout.addWidget(QLabel("Data File:"))
        self.data_file_edit = QLineEdit(self.config["DATA_FILE"])
        file_selector_layout.addWidget(self.data_file_edit)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_data_file)
        file_selector_layout.addWidget(browse_btn)
        file_layout.addLayout(file_selector_layout)
        
        # Sheet name
        sheet_layout = QHBoxLayout()
        sheet_layout.addWidget(QLabel("Sheet Name:"))
        self.sheet_edit = QLineEdit(self.config["DATA_SHEET_NAME"])
        sheet_layout.addWidget(self.sheet_edit)
        file_layout.addLayout(sheet_layout)
        
        # Category column
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category Column:"))
        self.category_edit = QLineEdit(self.config["FILTER_CATEGORY_COLUMN_NAME"])
        category_layout.addWidget(self.category_edit)
        file_layout.addLayout(category_layout)
        
        # Email mapping file
        email_map_layout = QHBoxLayout()
        email_map_layout.addWidget(QLabel("Email Mapping JSON:"))
        self.email_map_edit = QLineEdit("email_mapping.json")
        email_map_layout.addWidget(self.email_map_edit)
        browse_map_btn = QPushButton("Browse")
        browse_map_btn.clicked.connect(self.browse_email_mapping)
        email_map_layout.addWidget(browse_map_btn)
        file_layout.addLayout(email_map_layout)
        
        config_layout.addWidget(file_group)
        
        # Email configuration
        email_group = QGroupBox("Email Configuration")
        email_layout = QVBoxLayout(email_group)
        email_layout.setSpacing(10)
        
        # SMTP Server info
        smtp_layout = QHBoxLayout()
        smtp_layout.addWidget(QLabel("SMTP Server:"))
        self.smtp_server_edit = QLineEdit(self.config['SMTP_SERVER'])
        self.smtp_server_edit.setStyleSheet("font-weight: bold; color: #2c5aa0;")
        smtp_layout.addWidget(self.smtp_server_edit)
        
        # SMTP Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("SMTP Port:"))
        self.smtp_port_edit = QLineEdit(str(self.config['SMTP_PORT']))
        port_layout.addWidget(self.smtp_port_edit)
        email_layout.addLayout(port_layout)
        
        # Add help button
        smtp_help_btn = QPushButton("Gmail Help")
        smtp_help_btn.clicked.connect(self.show_connection_help)
        email_layout.addWidget(smtp_help_btn)
        
        email_layout.addLayout(smtp_layout)
        
        # Sender email
        sender_layout = QHBoxLayout()
        sender_layout.addWidget(QLabel("Sender Email:"))
        self.sender_edit = QLineEdit(self.config["SENDER_EMAIL"])
        sender_layout.addWidget(self.sender_edit)
        email_layout.addLayout(sender_layout)
        
        # Sender password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Sender Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_edit)
        email_layout.addLayout(password_layout)
        
        # Email subject
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel("Email Subject:"))
        self.subject_edit = QLineEdit(self.config["EMAIL_SUBJECT"])
        subject_layout.addWidget(self.subject_edit)
        email_layout.addLayout(subject_layout)
        
        # Email body
        email_layout.addWidget(QLabel("Email Body:"))
        self.body_edit = QTextEdit()
        self.body_edit.setPlainText(self.config["EMAIL_BODY"])
        self.body_edit.setMaximumHeight(150)
        email_layout.addWidget(self.body_edit)
        
        # Test recipient
        test_layout = QHBoxLayout()
        test_layout.addWidget(QLabel("Test Recipient:"))
        self.test_edit = QLineEdit(self.config["TEST_EMAIL_ADDRESS"])
        test_layout.addWidget(self.test_edit)
        email_layout.addLayout(test_layout)
        
        config_layout.addWidget(email_group)
        
        # Operations tab
        ops_tab = QWidget()
        ops_layout = QVBoxLayout(ops_tab)
        ops_layout.setSpacing(15)
        tabs.addTab(ops_tab, "Operations")
        
        # Operation buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.generate_btn = QPushButton("Generate Excel Files")
        self.generate_btn.clicked.connect(self.generate_files)
        buttons_layout.addWidget(self.generate_btn)
        
        self.test_email_btn = QPushButton("Send Test Emails")
        self.test_email_btn.clicked.connect(self.send_test_emails)
        buttons_layout.addWidget(self.test_email_btn)
        
        self.final_email_btn = QPushButton("Send Final Emails")
        self.final_email_btn.clicked.connect(self.send_final_emails)
        buttons_layout.addWidget(self.final_email_btn)
        
        ops_layout.addLayout(buttons_layout)
        
        # CC emails
        cc_layout = QHBoxLayout()
        cc_layout.addWidget(QLabel("CC Emails (comma separated):"))
        self.cc_edit = QLineEdit()
        cc_layout.addWidget(self.cc_edit)
        ops_layout.addLayout(cc_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        ops_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to start operations")
        self.status_label.setStyleSheet("font-weight: bold; color: #333333;")
        ops_layout.addWidget(self.status_label)
        
        # Results area
        results_group = QGroupBox("Operation Results")
        results_layout = QVBoxLayout(results_group)
        self.results_list = QListWidget()
        results_layout.addWidget(self.results_list)
        ops_layout.addWidget(results_group)
        
        # Cleanup checkbox
        self.cleanup_checkbox = QCheckBox("Clean up temporary files after operations")
        self.cleanup_checkbox.setChecked(True)
        ops_layout.addWidget(self.cleanup_checkbox)
        
        # Initialize processor
        self.update_config()
        
    def show_connection_help(self):
        """Show Gmail connection troubleshooting help."""
        help_text = """
<h3>Gmail Connection Help</h3>

<h4>Quick Setup:</h4>
<ol>
<li>Use your Gmail address as the sender email</li>
<li>If you have 2FA enabled, generate an App Password:
    <ul>
    <li>Go to: https://myaccount.google.com/apppasswords</li>
    <li>Select "Mail" as the app</li>
    <li>Select your device or "Other" and give it a name</li>
    <li>Use the generated 16-character password</li>
    </ul>
</li>
<li>If you don't have 2FA enabled, you may need to enable "Less secure app access":
    <ul>
    <li>Go to: https://myaccount.google.com/lesssecureapps</li>
    <li>Note: This option may not be available for all accounts</li>
    </ul>
</li>
</ol>

<h4>Troubleshooting Steps:</h4>
<ol>
<li>Verify your email and password are correct</li>
<li>For 2FA accounts, use an App Password, not your regular password</li>
<li>Check if your account allows less secure apps (if not using App Password)</li>
<li>Ensure your network isn't blocking SMTP connections</li>
<li>Try using a different network if issues persist</li>
</ol>

<h4>Recommended Approach:</h4>
<p>Enable 2FA and use an App Password for the most secure and reliable connection.</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Gmail Connection Help")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def test_connection(self):
        """Test Gmail connection without sending emails."""
        password = self.password_edit.text()
        if not password:
            QMessageBox.warning(self, "Password Required", "Please enter your email password to test connection")
            return
            
        self.update_config()
        
        # Show progress
        progress_dialog = QMessageBox(self)
        progress_dialog.setWindowTitle("Testing Connection")
        progress_dialog.setText("Testing Gmail connection, please wait...")
        progress_dialog.setStandardButtons(QMessageBox.NoButton)
        progress_dialog.show()
        
        # Process events to show the dialog
        QApplication.processEvents()
        
        try:
            client = self.processor.initialize_email_client(self.config["SENDER_EMAIL"], password)
            progress_dialog.close()
            
            if client:
                client.disconnect()
                QMessageBox.information(self, "Connection Test", 
                                      "✓ Connection successful!\nYou can now send emails.")
            else:
                QMessageBox.critical(self, "Connection Test", 
                                   "✗ Connection failed!\nPlease check your settings and try again.\n\n"
                                   "Click 'Gmail Help' for troubleshooting tips.")
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(self, "Connection Test", 
                               f"✗ Connection failed with error:\n{str(e)}\n\n"
                               "Click 'Gmail Help' for troubleshooting tips.")
        
    def browse_data_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.data_file_edit.setText(file_path)
            self.update_config()
            
    def browse_email_mapping(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Email Mapping JSON File", "", "JSON Files (*.json)"
        )
        if file_path:
            self.email_map_edit.setText(file_path)
            self.update_config()
                
    def update_config(self):
        try:
            self.config.update({
                "DATA_FILE": self.data_file_edit.text().strip(),
                "DATA_SHEET_NAME": self.sheet_edit.text().strip(),
                "FILTER_CATEGORY_COLUMN_NAME": self.category_edit.text().strip(),
                "SENDER_EMAIL": self.sender_edit.text().strip(),
                "SMTP_SERVER": self.smtp_server_edit.text().strip(),
                "SMTP_PORT": int(self.smtp_port_edit.text().strip()),
                "EMAIL_SUBJECT": self.subject_edit.text().strip(),
                "EMAIL_BODY": self.body_edit.toPlainText().strip(),
                "TEST_EMAIL_ADDRESS": self.test_edit.text().strip()
            })
            self.processor = ExcelAutomationProcessor(self.config)
            
            # Load email mapping if file exists
            email_map_file = self.email_map_edit.text().strip()
            if email_map_file and os.path.exists(email_map_file):
                if self.processor.load_email_mapping(email_map_file):
                    self.status_label.setText("Email mapping loaded successfully")
                    self.results_list.addItem("✓ Email mapping loaded successfully")
                    
                    mapping_count = len(self.processor.email_mapping)
                    self.results_list.addItem(f"✓ Loaded {mapping_count} email mappings")
                else:
                    self.status_label.setText("Error loading email mapping")
                    self.results_list.addItem("✗ Error loading email mapping")
            else:
                if email_map_file:
                    self.status_label.setText("Warning: Email mapping file not found")
                    self.results_list.addItem("⚠ Email mapping file not found")
                else:
                    self.status_label.setText("Warning: Please select email mapping file")
                    self.results_list.addItem("⚠ Please select email mapping file")
                    
        except Exception as e:
            self.status_label.setText(f"Configuration error: {str(e)}")
            self.results_list.addItem(f"✗ Configuration error: {str(e)}")
            
    def validate_inputs(self) -> Tuple[bool, str]:
        """Validate user inputs before operations."""
        if not self.config.get("DATA_FILE"):
            return False, "Please select a data file"
        if not os.path.exists(self.config["DATA_FILE"]):
            return False, "Selected data file does not exist"
        if not self.config.get("DATA_SHEET_NAME"):
            return False, "Please enter sheet name"
        if not self.config.get("FILTER_CATEGORY_COLUMN_NAME"):
            return False, "Please enter category column name"
        if not self.config.get("SENDER_EMAIL"):
            return False, "Please enter sender email"
        if not self.config.get("SMTP_SERVER"):
            return False, "Please enter SMTP server"
        if not self.email_map_edit.text().strip():
            return False, "Please select email mapping JSON file"
        if not os.path.exists(self.email_map_edit.text().strip()):
            return False, "Email mapping JSON file does not exist"
        return True, ""
        
    def generate_files(self):
        valid, error_msg = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
            
        self.update_config()
        self.start_worker("generate")
        
    def send_test_emails(self):
        valid, error_msg = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
            
        password = self.password_edit.text()
        if not password:
            QMessageBox.warning(self, "Password Required", "Please enter your email password")
            return
            
        test_recipient = self.test_edit.text().strip()
        if not test_recipient:
            QMessageBox.warning(self, "Test Recipient Required", "Please enter test recipient email")
            return
            
        self.update_config()
        self.start_worker("test_email", password, test_recipient)
        
    def send_final_emails(self):
        valid, error_msg = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
            
        password = self.password_edit.text()
        if not password:
            QMessageBox.warning(self, "Password Required", "Please enter your email password")
            return
            
        # Confirm final email sending
        reply = QMessageBox.question(
            self, 'Confirm Final Email Sending', 
            'Are you sure you want to send emails to all recipients? This action cannot be undone.',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
            
        cc_emails = [email.strip() for email in self.cc_edit.text().split(",") if email.strip()]
        self.update_config()
        self.start_worker("final_email", password, cc_emails=cc_emails)
            
    def start_worker(self, operation, password=None, test_recipient=None, cc_emails=None):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Operation in Progress", "Please wait for the current operation to complete.")
            return
            
        self.worker = EmailWorker(self.processor, operation, password, test_recipient, cc_emails)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.operation_finished)
        self.worker.error.connect(self.operation_error)
        
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.results_list.clear()
        
        self.worker.start()
        
    def update_status(self, message):
        self.status_label.setText(message)
        self.results_list.addItem(message)
        # Auto-scroll to bottom
        self.results_list.scrollToBottom()
        
    def operation_finished(self, results):
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        
        if isinstance(results, dict) and results:
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            self.status_label.setText(f"Operation completed. Success: {success_count}/{total_count}")
            
            for key, value in results.items():
                status = "✓ SUCCESS" if value else "✗ FAILED"
                self.results_list.addItem(f"{status} - {key}")
                
            # Show summary message
            if success_count == total_count:
                QMessageBox.information(self, "Success", f"All operations completed successfully! ({success_count}/{total_count})")
            elif success_count > 0:
                QMessageBox.warning(self, "Partial Success", f"Some operations failed. Success: {success_count}/{total_count}")
            else:
                QMessageBox.critical(self, "Failed", "All operations failed. Please check the logs.")
        else:
            self.status_label.setText("Operation completed with no results")
            self.results_list.addItem("⚠ Operation completed with no results")
            
        # Cleanup if requested
        if (self.cleanup_checkbox.isChecked() and 
            hasattr(self.processor, 'generated_files') and 
            self.processor.generated_files):
            try:
                self.processor.cleanup_temp_files(self.config["TEMP_FOLDER_PATH"])
                self.results_list.addItem("✓ Temporary files cleaned up.")
            except Exception as e:
                self.results_list.addItem(f"⚠ Cleanup warning: {str(e)}")

    def operation_error(self, message):
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        self.status_label.setText(f"Error: {message}")
        self.results_list.addItem(f"✗ ERROR: {message}")
        QMessageBox.critical(self, "Operation Error", f"An error occurred: {message}")

    def set_buttons_enabled(self, enabled):
        self.generate_btn.setEnabled(enabled)
        self.test_email_btn.setEnabled(enabled)
        self.final_email_btn.setEnabled(enabled)
        
    def closeEvent(self, event):
        """Handle application closing."""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, 'Confirm Exit', 
                'An operation is currently running. Are you sure you want to exit?',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.terminate()
                self.worker.wait(3000)  # Wait up to 3 seconds
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

# =============================================================================
#                         EMAIL MAPPING GENERATOR UTILITY
# =============================================================================

def create_sample_email_mapping():
    """Create a sample email mapping JSON file."""
    sample_mapping = {
        "Category1": "recipient1@example.com",
        "Category2": "recipient2@example.com",
        "Category3": "recipient3@example.com"
    }
    
    try:
        with open("email_mapping_sample.json", "w", encoding='utf-8') as f:
            json.dump(sample_mapping, f, indent=2, ensure_ascii=False)
        print("Sample email mapping file 'email_mapping_sample.json' created successfully!")
        print("Please edit this file with your actual categories and email addresses.")
    except Exception as e:
        print(f"Error creating sample email mapping: {e}")

# =============================================================================
#                                 MAIN APPLICATION ENTRY
# =============================================================================

def main():
    """Main application entry point."""
    import sys
    
    # Check if running in GUI mode or utility mode
    if len(sys.argv) > 1 and sys.argv[1] == "--create-sample-mapping":
        create_sample_email_mapping()
        return
    
    # Set up application
    app = QApplication(sys.argv)
    app.setApplicationName("Excel Automation Tool - Gmail Edition")
    app.setApplicationVersion("2.0")
    
    # Create and show main window
    try:
        window = AutomationGUI()
        window.show()
        
        # Show initial setup message if no email mapping exists
        if not os.path.exists("email_mapping.json"):
            reply = QMessageBox.question(
                window,
                'Setup Required',
                'No email mapping file found. Would you like to create a sample mapping file?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                create_sample_email_mapping()
                QMessageBox.information(
                    window,
                    'Sample Created',
                    'Sample email mapping file created as "email_mapping_sample.json".\n'
                    'Please edit it with your actual categories and email addresses, '
                    'then rename it to "email_mapping.json" or select it in the configuration.'
                )
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()