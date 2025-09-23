import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess
import os
import datetime

# Define the log file path on the desktop
log_file_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'adb_log.txt')

def log_output(command, command_name, output, error_message=""):
    """Appends command execution details and output to a log file."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Command Name: {command_name}\n")
        f.write(f"Command Executed: {command}\n")
        if error_message:
            f.write(f"Status: ERROR\n")
            f.write(f"Error Message:\n{error_message}\n")
        else:
            f.write(f"Status: SUCCESS\n")
            f.write(f"Output:\n{output}\n")
        f.write("=" * 50 + "\n\n")

# Function to execute an adb command and show the output
def run_command(command, command_name):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        log_output(command, command_name, result.stdout)
        messagebox.showinfo(f"{command_name} Success", f"Command executed successfully.\nOutput:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed with error:\n{e.stderr}\nExit Code: {e.returncode}"
        log_output(command, command_name, e.stdout, error_msg)
        messagebox.showerror(f"{command_name} Error", error_msg)
    except FileNotFoundError:
        error_msg = "The 'adb' command was not found. Ensure Android SDK Platform Tools are in your system's PATH."
        log_output(command, command_name, "", error_msg)
        messagebox.showerror("Error", error_msg)

# Function for ADB Install
def run_install():
    install_folder = "C:\\adb_install"
    
    if not os.path.exists(install_folder):
        os.makedirs(install_folder)
        messagebox.showinfo("Directory Created", f"The directory '{install_folder}' was not found and has been created.")

    filepath = filedialog.askopenfilename(
        initialdir=install_folder,
        title="Select an APK file to install",
        filetypes=(("APK files", "*.apk"), ("All files", "*.*"))
    )
    
    if filepath:
        command = f"adb install \"{filepath}\""
        run_command(command, "ADB Install")

# Capture Screenshot Directly to PC
def capture_screenshot():
    file_name = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(os.path.expanduser('~'), 'Desktop', file_name)
    
    try:
        with open(filepath, "wb") as f:
            command = "adb exec-out screencap -p"
            process = subprocess.Popen(command, shell=True, stdout=f, stderr=subprocess.PIPE)
            _, stderr_output = process.communicate()
            
            if process.returncode == 0:
                log_output(command, "Capture Screenshot", f"Screenshot saved to: {filepath}")
                messagebox.showinfo("Screenshot Saved", f"Screenshot saved to:\n{filepath}")
            else:
                error_msg = f"Failed to capture screenshot:\n{stderr_output.decode()}"
                log_output(command, "Capture Screenshot", "", error_msg)
                messagebox.showerror("Screenshot Error", error_msg)
    except Exception as e:
        error_msg = f"An error occurred while saving the file:\n{e}"
        log_output("adb exec-out screencap -p", "Capture Screenshot", "", error_msg)
        messagebox.showerror("File Error", error_msg)

# Record Screen to PC
def record_screen():
    messagebox.showinfo("Screen Recording", "Screen recording will start now. Press OK to proceed. You may need to press Ctrl+C in the terminal or close the app to stop the recording.")
    file_name = f"screenrecord_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    filepath = os.path.join(os.path.expanduser('~'), 'Desktop', file_name)
    
    try:
        command = f"adb exec-out screenrecord --output-format=h264 - > \"{filepath}\""
        subprocess.run(command, shell=True)
        log_output(command, "Record Screen", f"Screen recording saved to: {filepath}")
        messagebox.showinfo("Recording Finished", f"Screen recording saved to:\n{filepath}")
    except Exception as e:
        error_msg = f"An error occurred during screen recording:\n{e}"
        log_output(command, "Record Screen", "", error_msg)
        messagebox.showerror("Recording Error", error_msg)

# View logs with a timeout
def view_logs(command, command_name):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        log_output_str = ""
        for i in range(20):
            line = process.stdout.readline()
            if not line:
                break
            log_output_str += line
        
        process.terminate()
        
        if log_output_str:
            log_output(command, command_name, log_output_str)
            messagebox.showinfo(f"{command_name} Output", f"Showing the first 20 lines of the output:\n\n{log_output_str}")
        else:
            stderr_output = process.stderr.read()
            if stderr_output:
                log_output(command, command_name, "", f"Command failed:\n{stderr_output}")
                messagebox.showerror(f"{command_name} Error", f"Command failed:\n{stderr_output}")
            else:
                log_output(command, command_name, "No output found or command timed out.", "")
                messagebox.showinfo(f"{command_name} Output", "No output found or command timed out.")
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        log_output(command, command_name, "", error_msg)
        messagebox.showerror("Error", error_msg)

# Get Build Number
def get_build_number():
    command = "adb shell getprop ro.build.version.incremental"
    command_name = "Get Build Number"
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        build_number = result.stdout.strip()
        if build_number:
            log_output(command, command_name, build_number)
            messagebox.showinfo(command_name, f"The current build number is:\n\n{build_number}")
        else:
            error_msg = "Could not retrieve build number. Is the device connected?"
            log_output(command, command_name, "", error_msg)
            messagebox.showerror(command_name, error_msg)
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed with error:\n{e.stderr}\nExit Code: {e.returncode}"
        log_output(command, command_name, e.stdout, error_msg)
        messagebox.showerror(f"{command_name} Error", error_msg)
    except FileNotFoundError:
        error_msg = "The 'adb' command was not found. Ensure Android SDK Platform Tools are in your system's PATH."
        log_output(command, command_name, "", error_msg)
        messagebox.showerror("Error", error_msg)

# Push a file
def push_file():
    filepath = filedialog.askopenfilename(
        title="Select a file to push to the device"
    )
    if filepath:
        command = f"adb push \"{filepath}\" \"/sdcard/Download/\""
        run_command(command, "ADB Push File")

# Pull a file
def pull_file():
    filename = simpledialog.askstring("Input", "Enter the filename to pull from /sdcard/Download/:")
    if filename:
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        command = f"adb pull \"/sdcard/Download/{filename}\" \"{desktop_path}\""
        run_command(command, "ADB Pull File")

def set_device_time():
    """Sets the device time to the computer's current time."""
    now = datetime.datetime.now()
    # Format: MMDDhhmmYYYY.ss
    time_str = now.strftime('%m%d%H%M%Y.%S')
    command = f"adb shell date {time_str}"
    run_command(command, "Set Device Time")

# Interactive App Management
def app_management():
    try:
        result = subprocess.run("adb shell pm list packages", shell=True, check=True, capture_output=True, text=True)
        all_packages = [line.strip().replace("package:", "") for line in result.stdout.splitlines()]

        if not all_packages:
            messagebox.showerror("Error", "No packages found. Is the device connected?")
            return

        app_win = tk.Toplevel(root)
        app_win.title("App Management")
        app_win.geometry("400x600")

        frame = ttk.Frame(app_win)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        label = ttk.Label(frame, text="Select a package to manage:", font=("Helvetica", 12, "bold"))
        label.pack(pady=5)
        
        search_frame = ttk.Frame(frame)
        search_frame.pack(pady=5, fill='x')
        
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side="left", fill="x", expand=True)
        
        def filter_listbox():
            query = search_entry.get().lower()
            listbox.delete(0, tk.END)
            for pkg in sorted(all_packages):
                if query in pkg.lower():
                    listbox.insert(tk.END, pkg)

        search_btn = ttk.Button(search_frame, text="Search", command=filter_listbox)
        search_btn.pack(side="right", padx=5)

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        for pkg in sorted(all_packages):
            listbox.insert(tk.END, pkg)

        def perform_action(action):
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select an app first.")
                return
            
            selected_pkg = listbox.get(selected_indices[0])
            
            if action == "force_stop":
                command = f"adb shell am force-stop {selected_pkg}"
                run_command(command, f"Force Stop {selected_pkg}")
            elif action == "clear_data":
                command = f"adb shell pm clear {selected_pkg}"
                run_command(command, f"Clear Data {selected_pkg}")
            elif action == "open_app":
                try:
                    dumpsys_result = subprocess.run(f"adb shell dumpsys package {selected_pkg}", shell=True, check=True, capture_output=True, text=True)
                    dumpsys_output = dumpsys_result.stdout
                    log_output(f"adb shell dumpsys package {selected_pkg}", "Dumpsys for App Launch", dumpsys_output)

                    main_activity = ""
                    lines = dumpsys_output.splitlines()
                    for i, line in enumerate(lines):
                        line = line.strip()
                        # Find the unique marker line for the main launcher category
                        if "Category: \"android.intent.category.LAUNCHER\"" in line:
                            # The component name is two lines above this line
                            if i > 1:
                                candidate_line = lines[i-2].strip()
                                parts = candidate_line.split()
                                # The component name is the second token on this line
                                if len(parts) > 1 and selected_pkg in parts[1]:
                                    main_activity = parts[1]
                                    break
                    
                    if main_activity:
                        # Construct the full command as you confirmed works manually
                        start_command = f"adb shell am start -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -n {main_activity}"
                        run_command(start_command, f"Open {selected_pkg}")
                    else:
                        error_msg = f"Could not find a main launcher activity for {selected_pkg}. The app may not be designed to be launched this way."
                        log_output(f"adb shell dumpsys package {selected_pkg}", f"Open {selected_pkg}", dumpsys_output, error_msg)
                        messagebox.showerror("Open App Error", error_msg)
                except subprocess.CalledProcessError as e:
                    error_msg = f"Failed to get main activity. ADB command failed:\n{e.stderr}"
                    log_output(f"adb shell dumpsys package {selected_pkg}", f"Open {selected_pkg}", e.stdout, error_msg)
                    messagebox.showerror("Error", error_msg)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        open_app_btn = ttk.Button(button_frame, text="Open App", command=lambda: perform_action("open_app"))
        open_app_btn.pack(side="left", padx=5)

        force_stop_btn = ttk.Button(button_frame, text="Force Stop App", command=lambda: perform_action("force_stop"))
        force_stop_btn.pack(side="left", padx=5)

        clear_data_btn = ttk.Button(button_frame, text="Clear App Data", command=lambda: perform_action("clear_data"))
        clear_data_btn.pack(side="left", padx=5)

    except subprocess.CalledProcessError as e:
        error_msg = f"Could not list packages. ADB command failed:\n{e.stderr}"
        log_output("adb shell pm list packages", "App Management", "", error_msg)
        messagebox.showerror("Error", error_msg)
    except FileNotFoundError:
        error_msg = "The 'adb' command was not found."
        log_output("adb shell pm list packages", "App Management", "", error_msg)
        messagebox.showerror("Error", error_msg)

# --- ALL GUI SETUP CODE GOES HERE ---

root = tk.Tk()
root.title("ADB Automotive & Debugging Tool")
root.geometry("600x750")

notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True, fill='both')

# --- Tab 1: VHAL Commands ---
vhal_frame = ttk.Frame(notebook)
notebook.add(vhal_frame, text="VHAL Commands")
vhal_label = ttk.Label(vhal_frame, text="Automotive VHAL Commands", font=("Helvetica", 16, "bold"))
vhal_label.pack(pady=10)

connect_btn = ttk.Button(vhal_frame, text="Connect to Device (172.16.250.248)", command=lambda: run_command("adb connect 172.16.250.248", "ADB Connect"))
connect_btn.pack(pady=5, padx=20, fill='x')

commands_vhal = {
    "Set Speed to 0": "adb shell dumpsys activity service com.android.car inject-vhal-event 0x11600207 0",
    "Set Gear to Parked": "adb shell dumpsys activity service com.android.car inject-vhal-event 0x11400400 4",
    "Set Gear to Drive": "adb shell dumpsys activity service com.android.car inject-vhal-event 0x11400400 8",
    "Set Speed to 30 m/s": "adb shell dumpsys activity service com.android.car inject-vhal-event 0x11600207 30",
}
for name, cmd in commands_vhal.items():
    btn = ttk.Button(vhal_frame, text=name, command=lambda c=cmd, n=name: run_command(c, n))
    btn.pack(pady=5, padx=20, fill='x')

# --- Tab 2: Basic Device Management ---
device_frame = ttk.Frame(notebook)
notebook.add(device_frame, text="Device Management")
device_label = ttk.Label(device_frame, text="Basic Device Management", font=("Helvetica", 16, "bold"))
device_label.pack(pady=10)

commands_device = {
    "List Connected Devices": "adb devices",
    "Restart adbd as Root": "adb root",
    "Remount Partitions": "adb remount",
    "Reboot Device": "adb reboot",
    "Reboot to Bootloader": "adb reboot bootloader",
    "Reboot to Recovery": "adb reboot recovery",
}
for name, cmd in commands_device.items():
    btn = ttk.Button(device_frame, text=name, command=lambda c=cmd, n=name: run_command(c, n))
    btn.pack(pady=5, padx=20, fill='x')

ttk.Separator(device_frame, orient='horizontal').pack(fill='x', padx=20, pady=10)
install_btn = ttk.Button(device_frame, text="Install APK from C:\\adb_install", command=run_install)
install_btn.pack(pady=5, padx=20, fill='x')

ttk.Separator(device_frame, orient='horizontal').pack(fill='x', padx=20, pady=10)
file_transfer_label = ttk.Label(device_frame, text="File Transfer", font=("Helvetica", 12, "bold"))
file_transfer_label.pack(pady=5)
btn_push = ttk.Button(device_frame, text="Push File to Device (/sdcard/Download)", command=push_file)
btn_push.pack(pady=5, padx=20, fill='x')
btn_pull = ttk.Button(device_frame, text="Pull File from Device (/sdcard/Download)", command=pull_file)
btn_pull.pack(pady=5, padx=20, fill='x')

ttk.Separator(device_frame, orient='horizontal').pack(fill='x', padx=20, pady=10)
btn_set_time = ttk.Button(device_frame, text="Set Device Time to Now", command=set_device_time)
btn_set_time.pack(pady=5, padx=20, fill='x')


# --- Tab 3: App Debugging & System Info ---
app_debug_frame = ttk.Frame(notebook)
notebook.add(app_debug_frame, text="App Debugging")

app_mgmt_label = ttk.Label(app_debug_frame, text="App Management", font=("Helvetica", 16, "bold"))
app_mgmt_label.pack(pady=10)
btn_app_mgmt = ttk.Button(app_debug_frame, text="Open App Management Tool", command=app_management)
btn_app_mgmt.pack(pady=5, padx=20, fill='x')

ttk.Separator(app_debug_frame, orient='horizontal').pack(fill='x', padx=20, pady=10)

system_info_label = ttk.Label(app_debug_frame, text="System Information", font=("Helvetica", 12, "bold"))
system_info_label.pack(pady=5)
btn_build_number = ttk.Button(app_debug_frame, text="Show Current Build Number", command=get_build_number)
btn_build_number.pack(pady=5, padx=20, fill='x')
btn_device_model = ttk.Button(app_debug_frame, text="Get Device Model", command=lambda: run_command("adb shell getprop ro.product.model", "Get Device Model"))
btn_device_model.pack(pady=5, padx=20, fill='x')
btn_android_version = ttk.Button(app_debug_frame, text="Get Android Version", command=lambda: run_command("adb shell getprop ro.build.version.release", "Get Android Version"))
btn_android_version.pack(pady=5, padx=20, fill='x')

ttk.Separator(app_debug_frame, orient='horizontal').pack(fill='x', padx=20, pady=10)
btn_open_url = ttk.Button(app_debug_frame, text='Open Google.com', command=lambda: run_command('adb shell am start -a android.intent.action.VIEW -d "http://www.google.com"', 'Open URL'))
btn_open_url.pack(pady=5, padx=20, fill='x')

# --- Tab 4: Viewing Device Logs ---
logs_frame = ttk.Frame(notebook)
notebook.add(logs_frame, text="Device Logs")
logs_label = ttk.Label(logs_frame, text="Viewing Device Logs", font=("Helvetica", 16, "bold"))
logs_label.pack(pady=10)

commands_logs = {
    "View All Logs (First 20 lines)": "adb logcat",
    "Show Logs with Timestamps (First 20 lines)": "adb logcat -v time",
    "Show Only Error Logs (First 20 lines)": "adb logcat *:E",
    "Show Radio-Specific Logs (First 20 lines)": "adb shell logcat -b radio",
}
for name, cmd in commands_logs.items():
    btn = ttk.Button(logs_frame, text=name, command=lambda c=cmd, n=name: view_logs(c, n))
    btn.pack(pady=5, padx=20, fill='x')

# --- Tab 5: Automotive & I/O Utilities ---
automotive_frame = ttk.Frame(notebook)
notebook.add(automotive_frame, text="Automotive Utilities")
automotive_label = ttk.Label(automotive_frame, text="Automotive-Specific Utilities", font=("Helvetica", 16, "bold"))
automotive_label.pack(pady=10)

commands_automotive = {
    "Simulate Home button": "adb shell input keyevent 3",
    "Simulate Back button": "adb shell input keyevent 4",
    "Forward Ports for AA": "adb forward tcp:5277 tcp:5277",
}
for name, cmd in commands_automotive.items():
    btn = ttk.Button(automotive_frame, text=name, command=lambda c=cmd, n=name: run_command(c, n))
    btn.pack(pady=5, padx=20, fill='x')

ttk.Separator(automotive_frame, orient='horizontal').pack(fill='x', padx=20, pady=10)
io_label = ttk.Label(automotive_frame, text="Device I/O", font=("Helvetica", 12, "bold"))
io_label.pack(pady=5)
btn_screenshot = ttk.Button(automotive_frame, text="Capture Screenshot to Desktop", command=capture_screenshot)
btn_screenshot.pack(pady=5, padx=20, fill='x')
btn_record = ttk.Button(automotive_frame, text="Record Screen to Desktop", command=record_screen)
btn_record.pack(pady=5, padx=20, fill='x')

root.mainloop()