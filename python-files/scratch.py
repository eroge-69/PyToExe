import tkinter as tk
from tkinter import filedialog, messagebox
import os
import xml.etree.ElementTree as ET
import tkinter.font as tkFont

def import_file():
    try:
        # Open a file dialog and allow the user to select only .xml files
        file_path = filedialog.askopenfilename(
            title="Select an XML file",
            filetypes=[("XML Files", "*.xml")]  # Restrict to .xml files
        )

        if file_path:  # Check if a file was selected
            # Get only the file name from the file path
            file_name = os.path.basename(file_path)
            # Display only the selected file name in the label
            file_label.config(text=file_name)
            # Store the file path for later use
            global selected_file
            selected_file = file_path
            # Show the analyze button
            analyze_button.pack(pady=20)  # Pack the button to make it visible
            # Clear previous results
            result_text.delete(1.0, tk.END)  # Clear any existing text
        else:
            messagebox.showinfo("No Selection", "No file was selected.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def analyze_storage():
    if not selected_file:
        messagebox.showerror("Error", "No file selected for analysis.")
        return

    try:
        # Validate and get the retention policies and collection rate
        try:
            hd_value = int(hd_entry.get())
            sd_value = int(sd_entry.get())
            collection_value = int(collection_entry.get())
            compression_ratio = float(compression_entry.get())  # Get compression ratio
            if hd_value < 0 or sd_value < 0 or collection_value <= 0 or compression_ratio <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid positive numeric values.")
            return

        tree = ET.parse(selected_file)
        root = tree.getroot()

        result = {}  # Dictionary to hold the count of Elements grouped by DataType

        for Controllers in root.findall('Controllers'):
            for Controller in Controllers.findall('Controller'):
                for DataBroadcasters in Controller.findall('DataBroadcasters'):
                    for DataBroadcaster in DataBroadcasters.findall('DataBroadcaster'):
                        if DataBroadcaster.get('Enabled') == '1':
                            for Channels in DataBroadcaster.findall('Channels'):
                                for Channel in Channels.findall('Channel'):
                                    if Channel.get('Enabled') == '1':
                                        data_type = Channel.get('DataType')
                                        # Initialize the dictionary entry if it doesn't exist
                                        if data_type not in result:
                                            result[data_type] = 0
                                        # Count the child Elements with Enabled = 1
                                        for Elements in Channel.findall('Elements'):
                                            enabled_element_count = sum(
                                                1 for Element in Elements.findall('Element') if
                                                Element.get('Enabled') == '1'
                                            )
                                            result[data_type] += enabled_element_count

        # Prepare the result message
        result_message = "Storage Requirements Analysis:\n"
        total_storage = 0
        num_samples_hd = hd_value * 24 * 60 * 60 * (1000 / collection_value)
        num_samples_sd = sd_value * 24 * 60 * 60
        for data_type, count in result.items():
            data_type_storage = 0
            if data_type == 'BOOL':
                data_type_storage = count / 1073741824 * (num_samples_hd + num_samples_sd) / compression_ratio
            if data_type == 'SINT':
                data_type_storage = count * 8 / 1073741824 * (num_samples_hd + num_samples_sd) / compression_ratio
            if data_type == 'INT':
                data_type_storage = count * 16 / 1073741824 * (num_samples_hd + num_samples_sd) / compression_ratio
            if data_type == 'DINT':
                data_type_storage = count * 32 / 1073741824 * (num_samples_hd + num_samples_sd) / compression_ratio
            if data_type == 'REAL':
                data_type_storage = count * 32 / 1073741824 * (num_samples_hd + num_samples_sd) / compression_ratio
            total_storage += data_type_storage

            result_message += f"DataType '{data_type}': {count} Enabled Elements ({data_type_storage:.2f} GB)\n"

        result_message += f"Estimated Storage Required: {total_storage:.2f} GB\n"

        # Show results in the Text widget
        result_text.delete(1.0, tk.END)  # Clear previous results
        result_text.insert(tk.END, result_message.strip())  # Insert new results

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during analysis: {e}")

# Create the main window
root = tk.Tk()
root.title("XML File Importer")
root.geometry("600x600")  # Adjusted size for new entries

# Create a button to import the file
import_button = tk.Button(root, text="Import XML File", command=import_file)
import_button.pack(pady=20)

# Label to display the selected file name
file_label = tk.Label(root, text="No file selected.")
file_label.pack(pady=10)

# Create a button for analyzing storage requirements (initially hidden)
analyze_button = tk.Button(
    root,
    text="Analyze Storage Requirements",
    command=analyze_storage,
    #bg="blue",  # Set background color to blue
    #fg="white",  # Set text color to white for better contrast
    font=tkFont.Font(size=16)  # Set font size to 16 (double the default size)
)
analyze_button.pack_forget()  # Hide the button initially

# Create a frame for Retention Policies
retention_frame = tk.Frame(root)
retention_frame.pack(pady=10)

# High Definition Retention Policy
hd_label = tk.Label(retention_frame, text="High Definition Retention (Days):")
hd_label.grid(row=0, column=0, padx=5)
hd_entry = tk.Entry(retention_frame)
hd_entry.grid(row=0, column=1, padx=5)
hd_entry.insert(0, "2")  # Default value for High Definition

# Standard Definition Retention Policy
sd_label = tk.Label(retention_frame, text="Standard Definition Retention (Days):")
sd_label.grid(row=1, column=0, padx=5)
sd_entry = tk.Entry(retention_frame)
sd_entry.grid(row=1, column=1, padx=5)
sd_entry.insert(0, "30")  # Default value for Standard Definition

# Collection Rate
collection_label = tk.Label(root, text="Collection Rate (ms):")
collection_label.pack(pady=(10, 0))
collection_entry = tk.Entry(root)
collection_entry.pack(pady=5)
collection_entry.insert(0, "50")  # Default value for Collection Rate

# Compression Ratio
compression_label = tk.Label(root, text="Compression Ratio:")
compression_label.pack(pady=(10, 0))
compression_entry = tk.Entry(root)
compression_entry.pack(pady=5)
compression_entry.insert(0, "3.0")  # Default value for Compression Ratio

# Create a Text widget to display results
result_text = tk.Text(root, height=10, width=50)
result_text.pack(pady=10)

# Variable to hold the selected file path
selected_file = None

# Start the GUI event loop
root.mainloop()