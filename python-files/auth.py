import sys
import json
import os
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QFormLayout,
                             QDialog, QMessageBox, QMenu, QScrollArea,
                             QFrame, QToolButton)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QClipboard

import pyotp


class AccountWidget(QFrame):
    """Widget to display a single 2FA account"""
    def __init__(self, account_name, totp, parent=None, app_ref=None):
        super().__init__(parent)
        self.account_name = account_name
        self.totp = totp
        self.app_ref = app_ref
        self.parent_widget = parent

        # Set up the widget style
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                background-color: white;
                margin: 5px;
                padding: 10px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        # Header with account name and buttons
        header_layout = QHBoxLayout()

        # Account name
        self.name_label = QLabel(account_name)
        self.name_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.name_label.setStyleSheet("color: #333;")
        header_layout.addWidget(self.name_label)

        header_layout.addStretch()

        # Copy button
        self.copy_btn = QToolButton()
        self.copy_btn.setText("📋")
        self.copy_btn.setToolTip("Copy code")
        self.copy_btn.setFixedSize(30, 30)
        self.copy_btn.clicked.connect(self.copy_code)
        header_layout.addWidget(self.copy_btn)

        # Delete button
        self.delete_btn = QToolButton()
        self.delete_btn.setText("❌")
        self.delete_btn.setToolTip("Delete account")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.clicked.connect(self.delete_account)
        header_layout.addWidget(self.delete_btn)

        self.layout.addLayout(header_layout)

        # Code display
        self.code_label = QLabel("000000")
        self.code_label.setFont(QFont("Courier", 18, QFont.Bold))
        self.code_label.setAlignment(Qt.AlignCenter)
        self.code_label.setStyleSheet("color: #0066cc; margin: 10px 0;")
        self.layout.addWidget(self.code_label)

        # Timer display
        self.timer_label = QLabel("Expires in 30 seconds")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("color: #666; font-style: italic;")
        self.layout.addWidget(self.timer_label)

        # Initialize the code
        self.update_code()

    def update_code(self):
        try:
            code = self.totp.now()
            self.code_label.setText(code)

            # Calculate time until code refresh (30 seconds period)
            current_time = int(time.time())
            time_remaining = 30 - (current_time % 30)
            self.timer_label.setText(f"Expires in {time_remaining} seconds")

            # Change color as expiration approaches
            if time_remaining <= 5:
                self.timer_label.setStyleSheet("color: #cc0000; font-weight: bold;")
                # Pulse effect
                if time_remaining % 2 == 0:
                    self.timer_label.setText(f"Expires in {time_remaining} seconds!")
            else:
                self.timer_label.setStyleSheet("color: #666; font-style: italic;")

        except Exception as e:
            self.code_label.setText("Error")
            self.timer_label.setText("Invalid secret")

    def copy_code(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_label.text())

        # Visual feedback
        original_style = self.code_label.styleSheet()
        self.code_label.setStyleSheet("color: #009933;")
        QTimer.singleShot(300, lambda: self.code_label.setStyleSheet(original_style))

    def delete_account(self):
        if self.app_ref:
            self.app_ref.remove_account(self.account_name)


class AuthenticatorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("2FA Authenticator")
        self.setGeometry(100, 100, 700, 600)

        # Data file to store accounts
        self.data_file = "authenticator_data.json"
        self.accounts = {}  # name: {'secret': secret, 'totp': totp_object}

        # Load existing accounts
        self.load_accounts()

        # Create GUI
        self.create_gui()

        # Start timer update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_codes)
        self.timer.start(1000)  # Update every second

    def create_gui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("2FA Authenticator")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #ddd; margin: 15px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # Add account button
        self.add_btn = QPushButton("➕ Add Account")
        self.add_btn.setFixedWidth(150)
        self.add_btn.clicked.connect(self.add_account)
        title_layout.addWidget(self.add_btn)

        layout.addLayout(title_layout)

        # Scroll area for accounts
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { border: none; }
            QScrollBar:vertical {
                border: 1px solid #dcdcdc;
                background: #f0f0f0;
                width: 12px;
                margin: 2px 0 2px 0;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
            }
        """)

        # Container for account widgets
        self.accounts_container = QWidget()
        self.accounts_layout = QVBoxLayout(self.accounts_container)
        self.accounts_layout.setAlignment(Qt.AlignTop)
        self.accounts_layout.setSpacing(10)

        self.scroll_area.setWidget(self.accounts_container)
        layout.addWidget(self.scroll_area)

        # Add some empty space at the bottom
        layout.addStretch()

        # Initialize account widgets
        self.update_accounts_display()

    def update_accounts_display(self):
        # Clear existing widgets
        for i in reversed(range(self.accounts_layout.count())):
            widget = self.accounts_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        if not self.accounts:
            # Empty state
            empty_label = QLabel("No accounts added yet.\nClick 'Add Account' to get started.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #888; font-style: italic; margin: 50px;")
            empty_label.setFont(QFont("Arial", 10))
            self.accounts_layout.addWidget(empty_label)
            return

        # Sort accounts by name
        sorted_accounts = sorted(self.accounts.items(), key=lambda x: x[0].lower())

        for account_name, account_data in sorted_accounts:
            widget = AccountWidget(
                account_name,
                account_data['totp'],
                app_ref=self
            )
            self.accounts_layout.addWidget(widget)

    def add_account(self):
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Account")
        dialog.setModal(True)
        dialog.resize(400, 200)

        # Dialog layout
        layout = QVBoxLayout(dialog)

        # Form
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Google, GitHub, etc.")
        form_layout.addRow("Account Name:", self.name_input)

        self.secret_input = QLineEdit()
        self.secret_input.setPlaceholderText("Enter the secret key (base32)")
        form_layout.addRow("Secret Key:", self.secret_input)

        layout.addLayout(form_layout)

        # Instructions
        instructions = QLabel(
            "The secret key is usually provided as a QR code or text when enabling 2FA.\n"
            "Remove spaces if present in the key."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("font-size: 11px; color: #666; margin: 10px 0;")
        layout.addWidget(instructions)

        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Account")
        add_btn.clicked.connect(lambda: self.save_account(dialog))
        add_btn.setDefault(True)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Show dialog
        result = dialog.exec_()

        if result == QDialog.Accepted:
            self.save_account(dialog)

    def save_account(self, dialog):
        name = self.name_input.text().strip()
        secret = self.secret_input.text().strip().replace(" ", "").upper()

        # Validate secret
        try:
            totp = pyotp.TOTP(secret)
            # Test by generating a code
            totp.now()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Invalid secret key: {str(e)}"
            )
            return

        # Check if account name already exists
        if name in self.accounts:
            reply = QMessageBox.question(
                self,
                "Account Exists",
                f"An account named '{name}' already exists. Do you want to replace it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Add or update account
        self.accounts[name] = {
            'secret': secret,
            'totp': pyotp.TOTP(secret)
        }

        # Save and update display
        self.save_accounts()
        self.update_accounts_display()

        # Close dialog
        dialog.accept()

        # Clear inputs for next use
        self.name_input.clear()
        self.secret_input.clear()

    def remove_account(self, account_name):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{account_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if account_name in self.accounts:
                del self.accounts[account_name]
                self.save_accounts()
                self.update_accounts_display()

    def update_all_codes(self):
        for account_data in self.accounts.values():
            if 'totp' in account_data:
                # We need to find the widget to update it
                # This is a bit inefficient but works for this demo
                for i in range(self.accounts_layout.count()):
                    widget = self.accounts_layout.itemAt(i).widget()
                    if hasattr(widget, 'account_name') and widget.account_name in self.accounts:
                        widget.update_code()

    def save_accounts(self):
        # Save accounts to file
        save_data = {}
        for name, data in self.accounts.items():
            save_data[name] = {'secret': data['secret']}

        try:
            with open(self.data_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not save accounts: {str(e)}"
            )

    def load_accounts(self):
        # Load accounts from file
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    saved_data = json.load(f)

                for name, data in saved_data.items():
                    self.accounts[name] = {
                        'secret': data['secret'],
                        'totp': pyotp.TOTP(data['secret'])
                    }
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Could not load accounts: {str(e)}"
                )


def main():
    # Check if required packages are installed
    try:
        import pyotp
    except ImportError:
        print("Please install pyotp: pip install pyotp")
        return

    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        print("Please install PyQt5: pip install PyQt5")
        return

    # Create the application
    app = QApplication(sys.argv)
    window = AuthenticatorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
