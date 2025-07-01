import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk # Import ttk for themed widgets

# Global variable to store file content, used by plot_data to extract PWM
file_content_global = ""


def parse_data(file_content):
    """
    Parses the content of the data file, grouping coupled and decoupled data.
    Returns a dictionary where keys are 'Motor:Direction' (e.g., 'F:U', 'Z:D'),
    and values are dictionaries containing 'coupled' and 'decoupled' lists of
    [position, velocity] pairs.
    """
    data_sets = {}
    current_header = None
    # Initialize all expected headers and their coupled/decoupled states
    # This ensures all plots are created even if one type of data is missing
    expected_headers = ['F:U', 'F:D', 'Z:U', 'Z:D']
    for header_base in expected_headers:
        data_sets[header_base] = {'coupled': [], 'decoupled': []}

    for line in file_content.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        # Check if this is a header line (e.g., 'Z:U:76', 'f:D:76')
        if ':' in line and len(line.split(':')) == 3:
            current_header = line
            # Determine if it's coupled or decoupled and store the base header
            motor_type = current_header.split(':')[0]
            direction = current_header.split(':')[1]
            base_header = f"{motor_type.upper()}:{direction}"

            if motor_type.isupper():  # Coupled data
                if base_header not in data_sets:
                    data_sets[base_header] = {'coupled': [], 'decoupled': []}
                data_sets[base_header]['current_type'] = 'coupled'
            elif motor_type.islower():  # Decoupled data
                if base_header not in data_sets:
                    data_sets[base_header] = {'coupled': [], 'decoupled': []}
                data_sets[base_header]['current_type'] = 'decoupled'
            continue  # Move to the next line after processing header

        elif current_header:  # This is a data line, associate with the last header
            try:
                position, velocity = map(float, line.split(','))
                motor_type = current_header.split(':')[0]
                direction = current_header.split(':')[1]
                base_header = f"{motor_type.upper()}:{direction}"

                if data_sets[base_header]['current_type'] == 'coupled':
                    data_sets[base_header]['coupled'].append([position, velocity])
                elif data_sets[base_header]['current_type'] == 'decoupled':
                    data_sets[base_header]['decoupled'].append([position, velocity])
            except ValueError:
                # Use messagebox for error display in GUI
                messagebox.showwarning("Data Parsing Warning", f"Skipping malformed data line: {line}")
    return data_sets


def plot_data(data_sets, file_number):
    """
    Generates and saves four plots with coupled and decoupled data overlaid.
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))  # Adjusted figure size
    axes = axes.flatten()  # Flatten the 2x2 array of axes for easy iteration

    plot_configs = {
        'F:U': {"title_prefix": "Focus Motor Near to Far", "y_unit": "mm/ms", "y_lim": (0.0, 0.65)}, # Added y_lim
        'F:D': {"title_prefix": "Focus Motor Far to Near", "y_unit": "mm/ms", "y_lim": (0.0, 0.65)}, # Added y_lim
        'Z:U': {"title_prefix": "Zoom Motor Wide to Narrow", "y_unit": "deg/ms", "y_lim": (0, 75)}, # Added y_lim
        'Z:D': {"title_prefix": "Zoom Motor Narrow to Wide", "y_unit": "deg/ms", "y_lim": (0, 75)}  # Added y_lim
    }

    # Extract PWM from one of the headers for the main title calculation
    pwm_value = None
    if file_content_global:  # Ensure global content is available
        for header_line in file_content_global.strip().split('\n'):
            if ':' in header_line and len(header_line.split(':')) == 3:
                try:
                    pwm_value = int(header_line.split(':')[2])
                    break
                except ValueError:
                    continue

    if pwm_value is None:
        messagebox.showwarning("PWM Warning", "Could not extract PWM value from file. Using 0 for duty cycle.")
        pwm_value = 0

    duty_cycle_percentage = round((pwm_value / 255) * 100)  # Calculate with no significant figures

    for i, (header_base, data_info) in enumerate(data_sets.items()):
        ax = axes[i]

        # Plot coupled data with a solid line
        if data_info['coupled']:
            positions_coupled = [item[0] for item in data_info['coupled']]
            velocities_coupled = [item[1] for item in data_info['coupled']]
            ax.plot(positions_coupled, velocities_coupled, label='Coupled', color='blue', linestyle='-')

        # Plot decoupled data with a solid line
        if data_info['decoupled']:
            positions_decoupled = [item[0] for item in data_info['decoupled']]
            velocities_decoupled = [item[1] for item in data_info['decoupled']]
            ax.plot(positions_decoupled, velocities_decoupled, label='Decoupled', color='red', linestyle='-', alpha=0.5)


        # Set titles and labels based on configuration (removed duty cycle from subplot titles)
        config = plot_configs[header_base]
        title = f"{config['title_prefix']}"  # Subplot title without duty cycle
        y_axis_label = f"Velocity ({config['y_unit']})"


        ax.set_title(title)
        ax.set_xlabel("Position (% of Goal)")
        ax.set_ylabel(y_axis_label)
        ax.set_xlim(0, 100)  # Set x-axis limit from 0 to 100

        # Set fixed y-axis limits based on motor type (focus 0 to .6 and zoom 0 to 70)
        if "y_lim" in config:
            ax.set_ylim(config["y_lim"])

        ax.grid(True)
        ax.legend()  # Add legend to each subplot

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to make space for suptitle
    # Main title includes the duty cycle
    plt.suptitle(f"SN{file_number} Velocity Measurements ({duty_cycle_percentage}% Duty Cycle)", y=0.99, fontsize=18)

    # Save the plot as a PNG file
    output_filename = f"SN{file_number}_Velocity_Measurements.png"
    try:
        plt.savefig(output_filename)
        messagebox.showinfo("Success", f"Plot saved successfully as '{output_filename}'")
    except Exception as e:
        messagebox.showerror("Error Saving Plot", f"Failed to save plot: {e}")
    finally:
        plt.close(fig)  # Close the figure to free up memory


class PlotterApp:
    def __init__(self, master):
        self.master = master
        master.title("Motor Data Plotter")
        master.geometry("300x450")  # Set a default window size
        master.resizable(False, False)  # Make the window non-resizable for consistent look

        # Apply a modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 'clam', 'alt', 'default', 'classic'

        # Configure styles for widgets
        self.style.configure('TFrame', background='#e0e0e0')
        self.style.configure('TLabel', background='#e0e0e0', font=('Segoe UI', 10))
        self.style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=6)
        self.style.map('TButton',
                       background=[('active', '#007bff'), ('!disabled', '#0056b3')],
                       foreground=[('active', 'white'), ('!disabled', 'white')])
        self.style.configure('TEntry', font=('Segoe UI', 10))
        self.style.configure('TListbox', font=('Segoe UI', 10), background='white')

        # Main frame for padding and background color
        main_frame = ttk.Frame(master, padding="15 15 15 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame for file selection
        file_frame = ttk.LabelFrame(main_frame, text="Available SN Files", padding="10 10 10 10")
        file_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.label_listbox = ttk.Label(file_frame, text="Select a file:")
        self.label_listbox.pack(pady=(0, 5))

        # Create a scrollbar for the listbox
        scrollbar = ttk.Scrollbar(file_frame, orient=tk.VERTICAL)
        self.sn_listbox = tk.Listbox(file_frame, width=30, height=8, yscrollcommand=scrollbar.set,
                                     font=('Segoe UI', 10), bd=1,
                                     relief="solid")  # Use tk.Listbox as ttk doesn't have one
        scrollbar.config(command=self.sn_listbox.yview)

        self.sn_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.sn_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)

        self.load_files_to_listbox()  # Populate the listbox on startup

        # Manual entry section
        entry_frame = ttk.LabelFrame(main_frame, text="Manual SN Entry", padding="10 10 10 10")
        entry_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.label_entry = ttk.Label(entry_frame, text="Or enter 3-digit SN number:")
        self.label_entry.pack(pady=(0, 5))

        self.sn_entry = ttk.Entry(entry_frame, width=15)
        self.sn_entry.pack(pady=5)
        self.sn_entry.focus_set()  # Set focus to the entry field

        # Button
        self.plot_button = ttk.Button(main_frame, text="Generate Plot", command=self.run_plotter, style='TButton')
        self.plot_button.grid(row=2, column=0, columnspan=2, pady=15)

    def load_files_to_listbox(self):
        """Scans the current directory for SNxxx.txt files and populates the listbox."""
        self.sn_listbox.delete(0, tk.END)  # Clear existing items
        sn_files = []
        for filename in os.listdir('.'):
            if filename.startswith('sn') and filename.endswith('.txt') and len(filename) == 9 and filename[
                                                                                                   2:5].isdigit():
                sn_files.append(filename)

        sn_files.sort()  # Sort files alphabetically
        for sn_file in sn_files:
            self.sn_listbox.insert(tk.END, sn_file)

    def on_listbox_select(self, event):
        """Updates the entry field when a listbox item is selected."""
        selected_indices = self.sn_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_file = self.sn_listbox.get(index)
            # Extract the 3-digit number from the filename
            sn_number = selected_file[2:5]
            self.sn_entry.delete(0, tk.END)
            self.sn_entry.insert(0, sn_number)

    def run_plotter(self):
        global file_content_global  # Access the global variable

        file_number = ""
        selected_indices = self.sn_listbox.curselection()
        if selected_indices:
            # If an item is selected in the listbox, use its SN number
            index = selected_indices[0]
            selected_file = self.sn_listbox.get(index)
            file_number = selected_file[2:5]
        else:
            # Otherwise, use the manually entered SN number
            file_number = self.sn_entry.get().strip()

        if not (len(file_number) == 3 and file_number.isdigit()):
            messagebox.showerror("Invalid Input",
                                 "Please select a file from the list or enter a valid 3-digit number (e.g., 110).")
            return

        file_name = f"SN{file_number}.txt"
        if not os.path.exists(file_name):
            messagebox.showerror("File Not Found", f"File '{file_name}' not found in the current directory.")
            return

        try:
            with open(file_name, 'r') as f:
                file_content_global = f.read()  # Store content globally for PWM extraction
        except Exception as e:
            messagebox.showerror("File Read Error", f"Error reading file {file_name}: {e}")
            return

        parsed_data = parse_data(file_content_global)
        if parsed_data:
            plot_data(parsed_data, file_number)
        else:
            messagebox.showwarning("No Data", "No valid data was parsed from the file.")


def main():
    root = tk.Tk()
    app = PlotterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
