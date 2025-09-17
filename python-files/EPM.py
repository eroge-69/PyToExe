import sys
import os
import json
import subprocess
import shutil
import psutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QLineEdit, QDialog, QStatusBar,
    QMessageBox, QListWidgetItem, QInputDialog
)
from PyQt6.QtCore import Qt

class ProfileManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Microsoft Edge Profile Manager")
        self.setGeometry(100, 100, 600, 450)

        # Set up the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # --- GUI Components ---
        self.profile_list_label = QLabel("Available Profiles:")
        self.layout.addWidget(self.profile_list_label)

        self.profile_list = QListWidget()
        self.profile_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.profile_list)

        # Selection Buttons
        self.selection_buttons_layout = QHBoxLayout()
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_profiles)
        self.selection_buttons_layout.addWidget(self.select_all_button)

        self.unselect_all_button = QPushButton("Unselect All")
        self.unselect_all_button.clicked.connect(self.unselect_all_profiles)
        self.selection_buttons_layout.addWidget(self.unselect_all_button)
        self.layout.addLayout(self.selection_buttons_layout)

        # Action Buttons - Top Row
        self.open_buttons_layout = QHBoxLayout()
        self.open_button = QPushButton("Open Profile")
        self.open_button.clicked.connect(self.open_selected_profile)
        self.open_buttons_layout.addWidget(self.open_button)

        self.open_multiple_button = QPushButton("Open Multiple")
        self.open_multiple_button.clicked.connect(self.open_multiple_profiles)
        self.open_buttons_layout.addWidget(self.open_multiple_button)
        
        self.open_url_button = QPushButton("Open URL on Selected")
        self.open_url_button.clicked.connect(self.open_url_on_selected_profiles)
        self.open_buttons_layout.addWidget(self.open_url_button)
        self.layout.addLayout(self.open_buttons_layout)

        # Action Buttons - Bottom Row
        self.manage_buttons_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit Profile")
        self.edit_button.clicked.connect(self.edit_selected_profile)
        self.manage_buttons_layout.addWidget(self.edit_button)

        self.add_button = QPushButton("Add New Profile")
        self.add_button.clicked.connect(self.add_new_profile)
        self.manage_buttons_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Profile(s)")
        self.delete_button.clicked.connect(self.delete_selected_profiles)
        self.manage_buttons_layout.addWidget(self.delete_button)
        self.layout.addLayout(self.manage_buttons_layout)

        # Process Control Buttons
        self.process_buttons_layout = QHBoxLayout()
        self.close_selected_button = QPushButton("Close Selected")
        self.close_selected_button.clicked.connect(self.close_selected_profile)
        self.process_buttons_layout.addWidget(self.close_selected_button)

        self.close_all_button = QPushButton("Close All Profiles")
        self.close_all_button.clicked.connect(self.close_all_open_profiles)
        self.process_buttons_layout.addWidget(self.close_all_button)
        self.layout.addLayout(self.process_buttons_layout)

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.load_profiles)
        self.layout.addWidget(self.refresh_button)

        self.load_profiles()

    def get_edge_user_data_path(self):
        """Returns the platform-specific path to the Edge user data directory."""
        if sys.platform.startswith('win'):
            path = os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data')
        elif sys.platform.startswith('darwin'):
            path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Microsoft Edge')
        elif sys.platform.startswith('linux'):
            path = os.path.join(os.path.expanduser('~'), '.config', 'microsoft-edge')
        else:
            path = None

        if path and not os.path.exists(path):
            self.status_bar.showMessage(f"Error: Edge user data directory not found at {path}", 5000)
            return None
        return path

    def get_edge_executable_path(self):
        """Returns the platform-specific path to the Edge executable."""
        path = None
        if sys.platform.startswith('win'):
            path_x86 = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'
            path_x64 = 'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
            if os.path.exists(path_x86):
                path = path_x86
            elif os.path.exists(path_x64):
                path = path_x64
            else:
                path = 'msedge.exe'
        elif sys.platform.startswith('darwin'):
            path = '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'
        elif sys.platform.startswith('linux'):
            path = 'microsoft-edge'
        
        if path and not os.path.exists(path) and not path.lower() == 'msedge.exe' and not path.lower() == 'microsoft-edge':
            self.status_bar.showMessage(f"Error: Microsoft Edge executable not found at '{path}'.", 5000)
            return None
        return path

    def load_profiles(self):
        """
        Scans for Edge profiles and populates the list widget.
        Each item stores the human-readable name and the directory name.
        """
        self.profile_list.clear()
        base_path = self.get_edge_user_data_path()
        
        if not base_path:
            return

        found_profiles = False
        for entry in os.scandir(base_path):
            if entry.is_dir() and (entry.name.startswith('Profile ') or entry.name == 'Default'):
                profile_dir = entry.path
                preferences_file = os.path.join(profile_dir, 'Preferences')
                
                if os.path.exists(preferences_file):
                    try:
                        with open(preferences_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            profile_name = data.get('profile', {}).get('name', entry.name)
                            item = QListWidgetItem(profile_name)
                            item.setData(Qt.ItemDataRole.UserRole, entry.name)
                            self.profile_list.addItem(item)
                            found_profiles = True
                    except (IOError, json.JSONDecodeError) as e:
                        self.status_bar.showMessage(f"Warning: Could not read Preferences for {entry.name}. Error: {e}", 5000)
        
        if not found_profiles:
            self.status_bar.showMessage("No Edge profiles found.", 5000)
        else:
            self.status_bar.showMessage("Profiles loaded successfully.", 3000)

    def select_all_profiles(self):
        """Selects all items in the profile list."""
        for i in range(self.profile_list.count()):
            self.profile_list.item(i).setSelected(True)
        self.status_bar.showMessage("All profiles selected.", 2000)

    def unselect_all_profiles(self):
        """Clears the selection in the profile list."""
        self.profile_list.clearSelection()
        self.status_bar.showMessage("Selection cleared.", 2000)

    def open_profile(self, profile_dir_name, url=None):
        """Opens a specific Edge profile with an optional URL."""
        edge_path = self.get_edge_executable_path()
        if not edge_path:
            return False

        try:
            command = [edge_path, f'--profile-directory={profile_dir_name}']
            if url:
                command.append(url)
            
            subprocess.Popen(command, shell=False)
            self.status_bar.showMessage(f"Opening profile: {profile_dir_name}...", 3000)
            return True
        except FileNotFoundError:
            self.status_bar.showMessage(f"Error: Microsoft Edge executable not found at '{edge_path}'.", 5000)
            return False
        except Exception as e:
            self.status_bar.showMessage(f"An unexpected error occurred: {e}", 5000)
            return False

    def open_selected_profile(self):
        """Opens the single selected profile."""
        selected_items = self.profile_list.selectedItems()
        if len(selected_items) == 1:
            profile_dir_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self.open_profile(profile_dir_name)
        elif len(selected_items) > 1:
            QMessageBox.warning(self, "Warning", "Please select only one profile to open this way. Use 'Open Multiple' for more.")
        else:
            self.status_bar.showMessage("Please select a profile to open.", 3000)

    def open_multiple_profiles(self):
        """Opens all selected profiles at once."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            self.status_bar.showMessage("Please select one or more profiles to open.", 3000)
            return

        opened_count = 0
        for item in selected_items:
            profile_dir_name = item.data(Qt.ItemDataRole.UserRole)
            if self.open_profile(profile_dir_name):
                opened_count += 1
        
        self.status_bar.showMessage(f"Attempted to open {opened_count} profile(s).", 5000)

    def edit_selected_profile(self):
        """Opens a dialog to edit the selected profile's name."""
        selected_items = self.profile_list.selectedItems()
        if len(selected_items) == 1:
            item = selected_items[0]
            current_display_name = item.text()
            profile_dir_name = item.data(Qt.ItemDataRole.UserRole)
            
            new_name, ok = QInputDialog.getText(self, "Edit Profile Name", "Enter new name:", QLineEdit.EchoMode.Normal, current_display_name)
            
            if ok and new_name and new_name != current_display_name:
                if self.update_profile_name(profile_dir_name, new_name):
                    item.setText(new_name)
                    self.status_bar.showMessage(f"Profile '{profile_dir_name}' renamed to '{new_name}'.", 5000)
                else:
                    self.status_bar.showMessage(f"Error: Failed to rename profile '{profile_dir_name}'.", 5000)
        else:
            QMessageBox.warning(self, "Warning", "Please select exactly one profile to edit.")

    def update_profile_name(self, profile_dir_name, new_name):
        """Updates the profile name in the Preferences file."""
        base_path = self.get_edge_user_data_path()
        if not base_path: return False

        preferences_file = os.path.join(base_path, profile_dir_name, 'Preferences')

        if not os.path.exists(preferences_file):
            return False

        try:
            with open(preferences_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            data['profile']['name'] = new_name
            
            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            return True
        except (IOError, json.JSONDecodeError):
            return False

    def delete_selected_profiles(self):
        """Deletes the selected profile directories."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            self.status_bar.showMessage("Please select one or more profiles to delete.", 3000)
            return

        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     "Are you sure you want to permanently delete the selected profile(s)? This action cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            deleted_count = 0
            base_path = self.get_edge_user_data_path()
            if not base_path: return
            
            for item in selected_items:
                profile_dir_name = item.data(Qt.ItemDataRole.UserRole)
                profile_path = os.path.join(base_path, profile_dir_name)
                
                try:
                    shutil.rmtree(profile_path)
                    deleted_count += 1
                except OSError as e:
                    QMessageBox.warning(self, "Deletion Failed", f"Could not delete '{profile_dir_name}': {e.strerror}. It may be in use.")
            
            self.load_profiles()
            self.status_bar.showMessage(f"Successfully deleted {deleted_count} profile(s).", 5000)

    def add_new_profile(self):
        """Creates a new, empty profile directory and then launches it to initialize."""
        base_path = self.get_edge_user_data_path()
        if not base_path:
            QMessageBox.critical(self, "Error", "Edge user data directory not found. Please ensure Microsoft Edge is installed and has been run at least once.")
            return
        
        i = 1
        while os.path.exists(os.path.join(base_path, f"Profile {i}")):
            i += 1
        
        new_profile_dir = f"Profile {i}"
        new_profile_path = os.path.join(base_path, new_profile_dir)
        
        try:
            os.makedirs(new_profile_path)
            self.status_bar.showMessage(f"New profile directory '{new_profile_dir}' created. Initializing now...", 5000)
            
            # --- The new step: Immediately launch Edge to initialize the profile ---
            if self.open_profile(new_profile_dir):
                # Wait a moment for Edge to create the files
                self.status_bar.showMessage(f"Successfully initialized '{new_profile_dir}'. Refreshing list...", 5000)
                # The profile list will now find the new profile because it has files
                self.load_profiles()
            else:
                self.status_bar.showMessage(f"Failed to launch Edge to initialize new profile. Please check executable path.", 5000)

        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to create new profile directory: {e.strerror}\nPath: {new_profile_path}\nThis may be a permissions issue.")

    def open_url_on_selected_profiles(self):
        """Opens a specific URL on selected profiles."""
        selected_items = self.profile_list.selectedItems()
        if not selected_items:
            self.status_bar.showMessage("Please select one or more profiles to open a URL.", 3000)
            return
            
        url, ok = QInputDialog.getText(self, "Open URL on Selected Profiles", "Enter URL to open:", QLineEdit.EchoMode.Normal)
        
        if ok and url:
            opened_count = 0
            for item in selected_items:
                profile_dir_name = item.data(Qt.ItemDataRole.UserRole)
                if self.open_profile(profile_dir_name, url=url):
                    opened_count += 1
            
            self.status_bar.showMessage(f"Attempted to open '{url}' on {opened_count} selected profile(s).", 5000)
        elif ok:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid URL.")

    def close_all_open_profiles(self):
        """Closes all running Edge browser processes."""
        reply = QMessageBox.question(self, 'Confirm Close All',
                                     "Are you sure you want to close all open Microsoft Edge browser windows?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            edge_executable = self.get_edge_executable_path().lower()
            if not edge_executable: return
            
            closed_count = 0
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() == edge_executable.split(os.sep)[-1].lower():
                        proc.terminate()
                        closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            self.status_bar.showMessage(f"Terminated {closed_count} Edge processes.", 5000)

    def close_selected_profile(self):
        """Closes the Edge process associated with the selected profile."""
        selected_items = self.profile_list.selectedItems()
        if len(selected_items) != 1:
            QMessageBox.warning(self, "Warning", "Please select exactly one profile to close.")
            return

        profile_dir_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        edge_executable = self.get_edge_executable_path().lower()
        if not edge_executable: return
        
        closed_count = 0
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if proc.info['name'].lower() == edge_executable.split(os.sep)[-1].lower():
                    cmdline = ' '.join(proc.info['cmdline'])
                    if f'--profile-directory={profile_dir_name}' in cmdline:
                        proc.terminate()
                        closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if closed_count > 0:
            self.status_bar.showMessage(f"Successfully closed the profile '{profile_dir_name}'.", 5000)
        else:
            self.status_bar.showMessage(f"No active browser window found for profile '{profile_dir_name}'.", 5000)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProfileManagerApp()
    window.show()
    sys.exit(app.exec())