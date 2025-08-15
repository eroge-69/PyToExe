import sys
import os
import subprocess
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QLabel, QListWidget, QComboBox,
    QTabWidget, QMessageBox, QProgressBar, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Signal, QObject, Qt, QThread

# Worker class for running shell commands in a separate thread
class CommandRunner(QObject):
    # Signals to communicate with the main thread
    output_received = Signal(str)
    command_finished = Signal(int, str) # exit_code, command_type
    command_error = Signal(str)
    progress_update = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = None

    def run_command(self, command, cwd=None, env=None, command_type="generic"):
        """
        Runs a shell command and emits its output.
        :param command: List of command and arguments.
        :param cwd: Working directory for the command.
        :param env: Environment variables for the command.
        :param command_type: A string to identify the type of command (e.g., "install", "create_env").
        """
        try:
            # Use Popen to run the command and capture output
            self._process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Redirect stderr to stdout
                text=True, # Decode output as text
                bufsize=1 # Line-buffered output
            )

            # Read output line by line
            for line in self._process.stdout:
                self.output_received.emit(line.strip())

            self._process.wait() # Wait for the process to finish
            exit_code = self._process.returncode
            self.command_finished.emit(exit_code, command_type)

        except FileNotFoundError:
            error_msg = f"Error: Command not found. Make sure '{command[0]}' is in your PATH."
            self.output_received.emit(error_msg)
            self.command_error.emit(error_msg)
            self.command_finished.emit(1, command_type) # Indicate failure
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            self.output_received.emit(error_msg)
            self.command_error.emit(error_msg)
            self.command_finished.emit(1, command_type) # Indicate failure

    def stop_command(self):
        """Terminates the running command if any."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self.output_received.emit("Command terminated by user.")

# Main application window
class PortableCondaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Portable Miniconda Manager")
        self.setGeometry(100, 100, 900, 700) # Increased width for better layout

        self.conda_root_path = os.path.join(os.getcwd(), "installer_files", "Miniconda")
        self.envs_dir = os.path.join(os.getcwd(), "installer_files", "Environments")
        self.pkgs_dir = os.path.join(self.conda_root_path, "pkgs")
        self.miniconda_installer_path = os.path.join(os.getcwd(), "installer_files", "miniconda_installer.exe")
        self.conda_exe_path = os.path.join(self.conda_root_path, "_conda.exe")

        self.current_active_env = "base" # Default to base environment

        self.init_ui()
        self.check_installation_status()

    def init_ui(self):
        # Create a central widget and a main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create a tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # --- Installation Tab ---
        self.installation_tab = QWidget()
        self.tab_widget.addTab(self.installation_tab, "Installation")
        self.setup_installation_tab()

        # --- Environment Management Tab ---
        self.env_management_tab = QWidget()
        self.tab_widget.addTab(self.env_management_tab, "Environment Management")
        self.setup_env_management_tab()

        # --- Utilities Tab ---
        self.utilities_tab = QWidget()
        self.tab_widget.addTab(self.utilities_tab, "Utilities")
        self.setup_utilities_tab()

        # --- Output Log ---
        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        self.output_log.setMinimumHeight(150)
        main_layout.addWidget(QLabel("Output Log:"))
        main_layout.addWidget(self.output_log)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Ready")
        self.progress_bar.hide() # Hide until needed
        main_layout.addWidget(self.progress_bar)

        # Worker thread for long-running commands
        self.worker_thread = QThread()
        self.command_runner = CommandRunner()
        self.command_runner.moveToThread(self.worker_thread)
        self.worker_thread.start()

        # Connect signals from worker to GUI slots
        self.command_runner.output_received.connect(self.append_log)
        self.command_runner.command_finished.connect(self.on_command_finished)
        self.command_runner.command_error.connect(self.show_error_message)
        self.command_runner.progress_update.connect(self.progress_bar.setValue)

    def setup_installation_tab(self):
        layout = QVBoxLayout(self.installation_tab)

        # Installation Status
        self.install_status_label = QLabel("Miniconda Installation Status: Checking...")
        layout.addWidget(self.install_status_label)

        # Install Button
        self.install_button = QPushButton("1. Run GetConda.bat (Download & Install Miniconda)")
        self.install_button.clicked.connect(self.run_get_conda_bat)
        layout.addWidget(self.install_button)

        # Spacer to push content to top
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def setup_env_management_tab(self):
        layout = QVBoxLayout(self.env_management_tab)

        # Section: Create Environment
        create_env_group = QVBoxLayout()
        create_env_group.addWidget(QLabel("<h3>Create New Environment:</h3>"))
        
        form_layout = QHBoxLayout()
        form_layout.addWidget(QLabel("Name:"))
        self.env_name_input = QLineEdit()
        self.env_name_input.setPlaceholderText("e.g., myenv")
        form_layout.addWidget(self.env_name_input)

        form_layout.addWidget(QLabel("Python Version:"))
        self.python_version_input = QLineEdit()
        self.python_version_input.setPlaceholderText("e.g., 3.10")
        form_layout.addWidget(self.python_version_input)
        
        self.create_env_button = QPushButton("Create Environment")
        self.create_env_button.clicked.connect(self.create_conda_environment)
        form_layout.addWidget(self.create_env_button)
        create_env_group.addLayout(form_layout)
        layout.addLayout(create_env_group)
        layout.addSpacing(20)

        # Section: Manage Existing Environments
        manage_env_group = QVBoxLayout()
        manage_env_group.addWidget(QLabel("<h3>Manage Existing Environments:</h3>"))

        # Environment List
        list_env_layout = QHBoxLayout()
        self.list_env_button = QPushButton("Refresh Environments")
        self.list_env_button.clicked.connect(self.list_conda_environments)
        list_env_layout.addWidget(self.list_env_button)
        
        self.env_list_widget = QListWidget()
        self.env_list_widget.itemClicked.connect(self.on_env_selected)
        list_env_layout.addWidget(self.env_list_widget)
        manage_env_group.addLayout(list_env_layout)

        # Activate/Deactivate/Remove Buttons
        env_actions_layout = QHBoxLayout()
        self.activate_env_button = QPushButton("Activate Selected")
        self.activate_env_button.clicked.connect(self.activate_conda_environment)
        self.activate_env_button.setEnabled(False) # Disable until an env is selected
        env_actions_layout.addWidget(self.activate_env_button)

        self.deactivate_env_button = QPushButton("Deactivate Current")
        self.deactivate_env_button.clicked.connect(self.deactivate_conda_environment)
        self.deactivate_env_button.setEnabled(False) # Disable initially
        env_actions_layout.addWidget(self.deactivate_env_button)

        self.remove_env_button = QPushButton("Remove Selected")
        self.remove_env_button.clicked.connect(self.remove_conda_environment)
        self.remove_env_button.setEnabled(False) # Disable until an env is selected
        env_actions_layout.addWidget(self.remove_env_button)
        manage_env_group.addLayout(env_actions_layout)
        
        self.current_env_label = QLabel(f"<b>Current Active Environment: {self.current_active_env}</b>")
        manage_env_group.addWidget(self.current_env_label)

        layout.addLayout(manage_env_group)
        layout.addSpacing(20)

        # Section: Install Packages
        install_pkg_group = QVBoxLayout()
        install_pkg_group.addWidget(QLabel("<h3>Install Packages:</h3>"))
        
        install_pkg_layout = QHBoxLayout()
        self.package_input = QLineEdit()
        self.package_input.setPlaceholderText("e.g., numpy pandas or pytorch torchvision pytorch-cuda=12.4 -c pytorch -c nvidia")
        install_pkg_layout.addWidget(self.package_input)
        
        self.install_pkg_button = QPushButton("Install Package(s)")
        self.install_pkg_button.clicked.connect(self.install_conda_package)
        install_pkg_layout.addWidget(self.install_pkg_button)
        install_pkg_group.addLayout(install_pkg_layout)
        layout.addLayout(install_pkg_group)

        # Spacer to push content to top
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def setup_utilities_tab(self):
        layout = QVBoxLayout(self.utilities_tab)

        # Update Environment Paths
        self.set_env_button = QPushButton("2. Run SetEnv.bat (Update Miniconda Paths)")
        self.set_env_button.clicked.connect(self.run_set_env_bat)
        layout.addWidget(self.set_env_button)

        # Open Conda CMD
        self.open_cmd_button = QPushButton("3. Run Cmd.bat (Open Conda Command Prompt)")
        self.open_cmd_button.clicked.connect(self.run_cmd_bat)
        layout.addWidget(self.open_cmd_button)
        layout.addSpacing(20)

        # Cleanup Options
        cleanup_group = QVBoxLayout()
        cleanup_group.addWidget(QLabel("<h3>Conda Cache Cleanup:</h3>"))
        
        cleanup_buttons_layout = QHBoxLayout()
        self.clean_packages_button = QPushButton("Clean Unused Packages")
        self.clean_packages_button.clicked.connect(lambda: self.run_conda_command(["conda", "clean", "--packages"], "clean_packages"))
        cleanup_buttons_layout.addWidget(self.clean_packages_button)

        self.clean_all_button = QPushButton("Clean All Cache")
        self.clean_all_button.clicked.connect(lambda: self.run_conda_command(["conda", "clean", "--all"], "clean_all"))
        cleanup_buttons_layout.addWidget(self.clean_all_button)
        cleanup_group.addLayout(cleanup_buttons_layout)
        layout.addLayout(cleanup_group)
        layout.addSpacing(20)

        # Update Conda/All
        update_group = QVBoxLayout()
        update_group.addWidget(QLabel("<h3>Conda Updates:</h3>"))
        
        update_buttons_layout = QHBoxLayout()
        self.update_conda_button = QPushButton("Update Conda")
        self.update_conda_button.clicked.connect(lambda: self.run_conda_command(["conda", "update", "conda", "-y"], "update_conda"))
        update_buttons_layout.addWidget(self.update_conda_button)

        self.update_all_button = QPushButton("Update All Packages in Current Env")
        self.update_all_button.clicked.connect(lambda: self.run_conda_command(["conda", "update", "--all", "-y"], "update_all"))
        update_buttons_layout.addWidget(self.update_all_button)
        update_group.addLayout(update_buttons_layout)
        layout.addLayout(update_group)

        # Spacer to push content to top
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def append_log(self, text):
        """Appends text to the output log."""
        self.output_log.append(text)

    def show_error_message(self, message):
        """Displays an error message box."""
        QMessageBox.critical(self, "Error", message)

    def show_info_message(self, title, message):
        """Displays an informational message box."""
        QMessageBox.information(self, title, message)

    def check_installation_status(self):
        """Checks if Miniconda is installed and updates the status label."""
        if os.path.exists(self.conda_exe_path):
            self.install_status_label.setText("Miniconda Installation Status: <font color='green'><b>Installed</b></font>")
            self.install_button.setEnabled(False)
            self.list_conda_environments() # Automatically list environments if installed
            self.deactivate_env_button.setEnabled(True) # Enable deactivate if conda is installed
        else:
            self.install_status_label.setText("Miniconda Installation Status: <font color='red'><b>Not Installed</b></font>")
            self.install_button.setEnabled(True)
            self.deactivate_env_button.setEnabled(False) # Disable deactivate if conda is not installed
            self.show_info_message("Installation Required",
                                   "Miniconda is not detected. Please run '1. Run GetConda.bat' first.")

    def get_conda_env(self):
        """Prepares the environment variables for Conda commands."""
        env = os.environ.copy()
        # Add Miniconda paths to the PATH environment variable
        env["PATH"] = os.path.join(self.conda_root_path) + os.pathsep + \
                      os.path.join(self.conda_root_path, "condabin") + os.pathsep + \
                      os.path.join(self.conda_root_path, "Scripts") + os.pathsep + \
                      os.path.join(self.conda_root_path, "Library", "bin") + os.pathsep + \
                      env["PATH"]
        # Set CONDA_ROOT_PREFIX and CONDA_ENVS_PATH for portable setup
        env["CONDA_ROOT_PREFIX"] = self.conda_root_path
        env["CONDA_ENVS_PATH"] = self.envs_dir
        # Ensure .condarc is correctly picked up
        env["CONDARC"] = os.path.join(self.conda_root_path, ".condarc")
        return env

    def run_batch_script(self, script_name, command_type):
        """Generic function to run a batch script."""
        script_path = os.path.join(os.getcwd(), script_name)
        if not os.path.exists(script_path):
            self.show_error_message("Script Not Found", f"The script '{script_name}' was not found at '{script_path}'.")
            return

        self.output_log.clear()
        self.append_log(f"Running {script_name}...\n")
        self.progress_bar.show()
        self.progress_bar.setFormat(f"Running {script_name}...")
        self.progress_bar.setValue(0)

        # Run in a separate thread
        self.worker_thread.start()
        self.command_runner.run_command(
            ["cmd.exe", "/c", script_path], # Use cmd.exe /c to run the batch file
            cwd=os.getcwd(),
            command_type=command_type
        )

    def run_get_conda_bat(self):
        """Runs the GetConda.bat script."""
        self.run_batch_script("GetConda.bat", "install_miniconda")

    def run_set_env_bat(self):
        """Runs the SetEnv.bat script."""
        self.run_batch_script("SetEnv.bat", "set_env")

    def run_cmd_bat(self):
        """Opens a new command prompt using Cmd.bat."""
        script_path = os.path.join(os.getcwd(), "Cmd.bat")
        if not os.path.exists(script_path):
            self.show_error_message("Script Not Found", f"The script 'Cmd.bat' was not found at '{script_path}'.")
            return

        self.append_log(f"Opening Conda Command Prompt using Cmd.bat...\n")
        try:
            # Use Popen to run the batch file without waiting for it to finish
            # This will open a new CMD window
            subprocess.Popen(["cmd.exe", "/K", script_path], cwd=os.getcwd())
            self.append_log("Conda Command Prompt opened successfully.")
        except Exception as e:
            self.show_error_message("Error", f"Failed to open Conda Command Prompt: {e}")
            self.append_log(f"Failed to open Conda Command Prompt: {e}")

    def run_conda_command(self, command_parts, command_type):
        """
        Runs a Conda command using the prepared environment.
        :param command_parts: List of command parts (e.g., ["conda", "env", "list"]).
        :param command_type: A string to identify the type of command.
        """
        if not os.path.exists(self.conda_exe_path):
            self.show_error_message("Miniconda Not Found", "Miniconda is not installed. Please run '1. Run GetConda.bat' first.")
            return

        self.output_log.clear()
        self.append_log(f"Executing Conda command: {' '.join(command_parts)}\n")
        self.progress_bar.show()
        self.progress_bar.setFormat(f"Executing: {' '.join(command_parts[:2])}...")
        self.progress_bar.setValue(0)

        # Prepend the full path to _conda.exe
        full_command = [self.conda_exe_path] + command_parts[1:] if command_parts[0] == "conda" else command_parts

        # Run in a separate thread
        self.worker_thread.start()
        self.command_runner.run_command(
            full_command,
            cwd=os.getcwd(),
            env=self.get_conda_env(),
            command_type=command_type
        )

    def on_command_finished(self, exit_code, command_type):
        """Slot to handle command completion."""
        self.progress_bar.hide()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Ready")

        if exit_code == 0:
            self.append_log(f"\nCommand '{command_type}' completed successfully.")
            if command_type == "install_miniconda":
                self.check_installation_status()
                self.show_info_message("Installation Complete", "Miniconda has been successfully installed. Please run '2. Run SetEnv.bat' to update paths.")
            elif command_type == "set_env":
                self.show_info_message("Paths Updated", ".condarc paths have been updated. You can now manage environments.")
                self.list_conda_environments() # Refresh env list after setting paths
            elif command_type == "list_envs":
                # Parse output and populate list widget
                self.parse_and_display_environments()
            elif command_type.startswith("create_env"):
                env_name = command_type.split(":")[1]
                self.show_info_message("Environment Created", f"Environment '{env_name}' created successfully.")
                self.list_conda_environments()
            elif command_type.startswith("remove_env"):
                env_name = command_type.split(":")[1]
                self.show_info_message("Environment Removed", f"Environment '{env_name}' removed successfully.")
                self.list_conda_environments()
                if self.current_active_env == env_name:
                    self.current_active_env = "base"
                    self.current_env_label.setText(f"<b>Current Active Environment: {self.current_active_env}</b>")
            elif command_type.startswith("activate_env"):
                env_name = command_type.split(":")[1]
                self.current_active_env = env_name
                self.current_env_label.setText(f"<b>Current Active Environment: {self.current_active_env}</b>")
                self.show_info_message("Environment Activated", f"Environment '{env_name}' is now active.")
            elif command_type == "deactivate_env":
                self.current_active_env = "base"
                self.current_env_label.setText(f"<b>Current Active Environment: {self.current_active_env}</b>")
                self.show_info_message("Environment Deactivated", "Deactivated current environment. Now in 'base'.")
            elif command_type.startswith("install_package"):
                package_name = command_type.split(":", 1)[1]
                self.show_info_message("Packages Installed", f"Package(s) '{package_name}' installed successfully.")

        else:
            self.append_log(f"\nCommand '{command_type}' failed with exit code {exit_code}.")
            self.show_error_message("Command Failed", f"Command '{command_type}' failed. Check log for details.")

    def list_conda_environments(self):
        """Lists all Conda environments."""
        self.run_conda_command(["conda", "env", "list"], "list_envs")

    def parse_and_display_environments(self):
        """Parses the output of 'conda env list' and populates the list widget."""
        output = self.output_log.toPlainText()
        environments = []
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split()
            if len(parts) >= 1:
                env_name = parts[0]
                # Check if the environment path is within our portable environments directory
                # This is a heuristic, a more robust check would parse the full path
                if len(parts) > 1 and self.envs_dir in parts[-1]:
                    environments.append(env_name)
                elif env_name == "base": # Always include base env
                    environments.append(env_name)

        self.env_list_widget.clear()
        if environments:
            for env in sorted(list(set(environments))): # Use set to remove duplicates, then sort
                self.env_list_widget.addItem(env)
        else:
            self.env_list_widget.addItem("No environments found.")
        
        self.activate_env_button.setEnabled(False)
        self.remove_env_button.setEnabled(False)

    def on_env_selected(self, item):
        """Enables/disables buttons based on selected environment."""
        selected_env = item.text()
        if selected_env == "No environments found.":
            self.activate_env_button.setEnabled(False)
            self.remove_env_button.setEnabled(False)
        else:
            self.activate_env_button.setEnabled(True)
            self.remove_env_button.setEnabled(selected_env != "base") # Cannot remove base env

    def create_conda_environment(self):
        """Creates a new Conda environment."""
        env_name = self.env_name_input.text().strip()
        python_version = self.python_version_input.text().strip()

        if not env_name:
            self.show_error_message("Input Error", "Please enter an environment name.")
            return

        command = ["conda", "create", "--name", env_name, "-y"]
        if python_version:
            command.append(f"python={python_version}")
        
        self.run_conda_command(command, f"create_env:{env_name}")

    def activate_conda_environment(self):
        """Activates the selected Conda environment."""
        selected_items = self.env_list_widget.selectedItems()
        if not selected_items:
            self.show_error_message("Selection Error", "Please select an environment to activate.")
            return
        
        env_name = selected_items[0].text()
        if env_name == self.current_active_env:
            self.show_info_message("Already Active", f"Environment '{env_name}' is already the current active environment.")
            return

        # Activating an environment requires setting environment variables in the current process.
        # This is tricky with subprocess as it creates a new process.
        # For simplicity, we'll just *report* it as active in the GUI,
        # and for actual commands, we'll ensure the correct env is used.
        # A true activation would involve re-launching the GUI or modifying the current process's env.
        # For now, we'll just run a simple command to confirm it exists and set the GUI label.

        # We can simulate activation by ensuring subsequent commands use this environment
        # by prepending `conda activate <env_name>` to the command list.
        # However, `conda activate` is a shell function, not a direct executable.
        # The best way to manage this is to ensure `_conda.exe` is called with `-n <env_name>`
        # for commands that need to run *within* that environment.
        # For now, we'll just update the GUI's internal state.

        # Let's run a dummy command to show it's "activating"
        self.run_conda_command(["conda", "run", "-n", env_name, "python", "--version"], f"activate_env:{env_name}")
        # The actual environment for subsequent commands will be managed by `get_conda_env`
        # and prepending `-n self.current_active_env` to the command.

    def deactivate_conda_environment(self):
        """Deactivates the current Conda environment."""
        if self.current_active_env == "base":
            self.show_info_message("No Active Environment", "The base environment is currently active. Nothing to deactivate.")
            return
        
        # Similar to activate, deactivation is a shell function.
        # We'll just reset the GUI's internal state to 'base'.
        self.run_conda_command(["conda", "info", "--envs"], "deactivate_env") # Dummy command to trigger finish signal

    def remove_conda_environment(self):
        """Removes the selected Conda environment."""
        selected_items = self.env_list_widget.selectedItems()
        if not selected_items:
            self.show_error_message("Selection Error", "Please select an environment to remove.")
            return
        
        env_name = selected_items[0].text()
        if env_name == "base":
            self.show_error_message("Error", "Cannot remove the base environment.")
            return

        reply = QMessageBox.question(self, "Confirm Removal",
                                     f"Are you sure you want to remove environment '{env_name}' and all its contents?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.run_conda_command(["conda", "remove", "--name", env_name, "--all", "-y"], f"remove_env:{env_name}")

    def install_conda_package(self):
        """Installs packages into the currently active environment."""
        packages = self.package_input.text().strip()
        if not packages:
            self.show_error_message("Input Error", "Please enter package(s) to install.")
            return
        
        # Split packages by space, but handle quoted arguments for channels etc.
        # This is a simplified split, for complex cases, shlex.split might be better.
        package_list = packages.split()

        command = ["conda", "install", "-n", self.current_active_env, "-y"] + package_list
        self.run_conda_command(command, f"install_package:{packages}")

    def closeEvent(self, event):
        """Handles application close event."""
        if self.worker_thread.isRunning():
            self.command_runner.stop_command()
            self.worker_thread.quit()
            self.worker_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PortableCondaGUI()
    window.show()
    sys.exit(app.exec())
