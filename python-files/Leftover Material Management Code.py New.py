import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import json
import csv
import os
import ctypes # Import ctypes to handle DPI scaling
import pandas as pd # Import pandas for Excel export functionality

# Define the file for storing data. This will be created in the same directory as the script.
DATA_FILE = "storage_data.json"

class StorageMatrix:
    """
    Manages the storage locations and the parts stored within them.
    Handles loading, saving, placing, and taking parts.
    """
    def __init__(self):
        # Define initial fixed locations (A1, A2, B1, B2, C1, C2)
        self.locations = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        # Add locations D through R dynamically
        self.locations.extend([chr(letter) for letter in range(ord('D'), ord('S'))]) 
        self.storage = self.load_data() # Load existing data or initialize new storage

    def load_data(self):
        """
        Loads storage data from the DATA_FILE. If the file doesn't exist,
        it initializes an empty storage dictionary for all defined locations.
        """
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    loaded_data = json.load(f)
                    # Ensure all defined locations are present in loaded data,
                    # initializing missing ones to avoid KeyError.
                    for loc in self.locations:
                        if loc not in loaded_data:
                            loaded_data[loc] = {"part": None, "qty": 0}
                    return loaded_data
            except json.JSONDecodeError:
                # Handle case where JSON file is empty or corrupted
                return {loc: {"part": None, "qty": 0} for loc in self.locations}
        # If file doesn't exist, create a new empty storage
        return {loc: {"part": None, "qty": 0} for loc in self.locations}

    def save_data(self):
        """Saves the current state of the storage matrix to the DATA_FILE."""
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.storage, f, indent=4) # Use indent for readability
        except IOError as e:
            pass # Silently fail or log to console if needed for debugging

    def place_part(self, part, qty):
        """
        Places a part in an available slot. Prioritizes existing slots with the same part.
        Returns the location if successful, None if no empty slot is available.
        """
        # First, try to add to an existing slot with the same part
        for loc in self.locations:
            if self.storage[loc]["part"] == part:
                self.storage[loc]["qty"] += qty
                return loc
        
        # If no existing slot, find the first empty slot
        for loc in self.locations:
            if self.storage[loc]["part"] is None:
                self.storage[loc] = {"part": part, "qty": qty}
                return loc
        return None # No empty slot found

    def take_part(self, part, qty):
        """
        Attempts to take a specified quantity of a part.
        Returns the location if successful, "not_enough" if quantity is insufficient,
        or None if the part is not found.
        """
        for loc in self.locations:
            if self.storage[loc]["part"] == part:
                if self.storage[loc]["qty"] > qty:
                    self.storage[loc]["qty"] -= qty
                    return loc
                elif self.storage[loc]["qty"] == qty:
                    self.storage[loc] = {"part": None, "qty": 0}
                    return loc
                else: # self.storage[loc]["qty"] < qty
                    return "not_enough"
        return None # Part not found

    def get_data(self):
        """Returns a copy of the current storage data."""
        return self.storage.copy()

    def get_all_parts(self):
        """Returns a set of all unique part numbers currently in storage."""
        return {v['part'] for v in self.storage.values() if v['part']}

class LeftoverApp:
    """
    Tkinter application for managing leftover materials, providing a visual
    representation of storage and functionalities to place and take parts.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Leftover Material Management")
        
        # --- DPI Awareness Fix for Windows ---
        # This helps prevent blurring on high-DPI displays by telling Windows that the application is DPI aware.
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass # Ignore if not running on a platform that supports this (e.g., Linux, macOS, or older Windows)
        # -------------------------------------

        self.root.attributes('-fullscreen', True) # Fullscreen mode

        self.matrix = StorageMatrix()

        # Title Label
        tk.Label(root, text="Leftover Material Management", font=("Arial", 24, "bold"), fg="#333333").pack(pady=20)

        # Buttons Frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Place Part", font=("Arial", 14), width=15, command=self.open_place_popup, bg="#A8E6CF", fg="#333333", relief=tk.RAISED, bd=3).pack(side=tk.LEFT, padx=30)
        tk.Button(btn_frame, text="Take Away", font=("Arial", 14), width=15, command=self.open_take_popup, bg="#FFADAD", fg="#333333", relief=tk.RAISED, bd=3).pack(side=tk.RIGHT, padx=30)
        
        # Removed Export to Excel Button as per user request
        # tk.Button(btn_frame, text="Export to Excel", font=("Arial", 14), width=15, command=self.export_to_excel, bg="#FFD3B5", fg="#333333", relief=tk.RAISED, bd=3).pack(side=tk.LEFT, padx=30)

        # Grid Frame for Storage Matrix
        self.grid_frame = tk.Frame(root, bg="#F0F0F0", bd=2, relief=tk.SUNKEN)
        self.grid_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=20)

        self.slot_labels = {} # Dictionary to hold references to the content labels
        self.build_matrix()

        # Initial update of the matrix display
        self.update_matrix()

    def build_matrix(self):
        """
        Constructs the visual grid for the storage matrix.
        Clears existing widgets and rebuilds based on defined locations.
        """
        # Clear existing widgets in the grid frame
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        idx = 0
        # First row: 3 cells, each split into two sub-sections (A1, A2), (B1, B2), (C1, C2)
        for col_idx in range(3):
            cell_frame = tk.Frame(self.grid_frame, bg="#CCCCCC", bd=1, relief="solid")
            cell_frame.grid(row=0, column=col_idx, sticky="nsew", padx=5, pady=5)
            self.grid_frame.grid_rowconfigure(0, weight=1)
            self.grid_frame.grid_columnconfigure(col_idx, weight=1)

            # Left sub-slot
            left_slot_name = self.matrix.locations[idx]
            left_label_frame = tk.Frame(cell_frame, bg="#E0F2F7", bd=1, relief="ridge")
            left_content_label = tk.Label(left_label_frame, text="", bg="#E0F2F7", font=("Arial", 12))
            left_content_label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            left_footer_label = tk.Label(left_label_frame, text=left_slot_name, bg="#333333", fg="white", font=("Arial", 10, "bold"))
            left_footer_label.pack(side=tk.BOTTOM, fill=tk.X)
            left_label_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2, pady=2)
            self.slot_labels[left_slot_name] = left_content_label

            # Right sub-slot
            right_slot_name = self.matrix.locations[idx+1]
            right_label_frame = tk.Frame(cell_frame, bg="#E0F2F7", bd=1, relief="ridge")
            right_content_label = tk.Label(right_label_frame, text="", bg="#E0F2F7", font=("Arial", 12))
            right_content_label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            right_footer_label = tk.Label(right_label_frame, text=right_slot_name, bg="#333333", fg="white", font=("Arial", 10, "bold"))
            right_footer_label.pack(side=tk.BOTTOM, fill=tk.X)
            right_label_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2, pady=2)
            self.slot_labels[right_slot_name] = right_content_label
            
            idx += 2

        # Remaining rows: single sections D to R
        row_idx = 1
        col_idx = 0
        while idx < len(self.matrix.locations):
            slot_name = self.matrix.locations[idx]
            label_frame = tk.Frame(self.grid_frame, bg="#E0F2F7", bd=1, relief="solid")
            content_label = tk.Label(label_frame, text="", bg="#E0F2F7", font=("Arial", 14))
            content_label.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
            loc_label = tk.Label(label_frame, text=slot_name, bg="#333333", fg="white", font=("Arial", 10, "bold"))
            loc_label.pack(side=tk.BOTTOM, fill=tk.X)
            
            label_frame.grid(row=row_idx, column=col_idx, sticky="nsew", padx=5, pady=5)
            self.slot_labels[slot_name] = content_label
            self.grid_frame.grid_rowconfigure(row_idx, weight=1)
            self.grid_frame.grid_columnconfigure(col_idx, weight=1)

            col_idx += 1
            if col_idx >= 3: # Reset column and increment row after 3 columns
                col_idx = 0
                row_idx += 1
            idx += 1

    def export_to_excel(self):
        """
        Exports the current storage data to an Excel (.xlsx) file.
        This method is now called automatically on data update.
        """
        # Prepare data for DataFrame
        data_to_export = []
        for loc, item in self.matrix.get_data().items():
            if item['part']: # Only export occupied slots
                data_to_export.append({"Location": loc, "Part Number": item['part'], "Quantity": item['qty']})

        if not data_to_export:
            # No data to export, silently return
            return

        df = pd.DataFrame(data_to_export)

        # Define a fixed file path for automatic saving
        # You can change this path to your desired location.
        # Example: C:/Users/YourUser/Documents/storage_data.xlsx
        # Or relative to the script: os.path.join(os.path.dirname(__file__), "storage_data.xlsx")
        
        # For this example, let's save it in the same directory as the script.
        excel_file_path = "storage_data.xlsx" 

        try:
            # Use pandas to_excel to save the DataFrame to an Excel file
            df.to_excel("//BOSCH.COM/DfsRB/DfsIN/LOC/Ja/DS/MFN/01_JaP_MFN/04_mfh1_common/Hard_stage_Format/Devanshu Sharma/Leftover App/Leftover Material Management Data .xlsx", index=False) # index=False prevents writing DataFrame index as a column
        except Exception as e:
            # Silently fail or log error if needed
            pass

    def update_matrix(self):
        """
        Updates the visual representation of the storage matrix and saves data.
        This now also triggers the automatic Excel export.
        """
        self.matrix.save_data() # Save data to JSON
        self.export_to_excel() # Automatically export data to Excel

        data = self.matrix.get_data()
        for loc, label_widget in self.slot_labels.items():
            content = data[loc]
            if content["part"]:
                label_widget.config(text=f"{content['part']} ({content['qty']})", bg="#C9FFD5", fg="#333333") # Lighter green for occupied
            else:
                label_widget.config(text="", bg="#E0F2F7", fg="#333333") # Lighter blue for empty

    def open_place_popup(self):
        """Opens the popup window for placing parts."""
        self.open_popup("place")
    def open_take_popup(self):
        """Opens the popup window for taking parts."""
        self.open_popup("take")

    def open_popup(self, action):
        """
        Handles the creation and logic for the place/take part popup window.
        """
        popup = tk.Toplevel(self.root)
        popup.title(f"{'Place' if action == 'place' else 'Take'} Part Info")
        popup.geometry("400x350") # Slightly larger popup
        popup.resizable(False, False) # Prevent resizing

        # Center the popup window
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

        # Part Number Input
        tk.Label(popup, text="Part Number:", font=("Arial", 12, "bold")).pack(pady=5)
        part_entry = tk.Entry(popup, font=("Arial", 12), width=30, bd=2, relief=tk.GROOVE)
        part_entry.pack(pady=5)

        # Quantity Input
        tk.Label(popup, text="Quantity:", font=("Arial", 12, "bold")).pack(pady=5)
        qty_entry = tk.Entry(popup, font=("Arial", 12), width=30, bd=2, relief=tk.GROOVE)
        qty_entry.pack(pady=5)

        location_var = tk.StringVar(popup)
        if action == "place":
            # For placing, offer "Auto" or specific locations
            location_var.set("Auto") # Default to auto-placement
            loc_options = ["Auto"] + self.matrix.locations
            tk.Label(popup, text="Select Location:", font=("Arial", 12, "bold")).pack(pady=5)
            loc_menu = tk.OptionMenu(popup, location_var, *loc_options)
            loc_menu.config(font=("Arial", 12), width=25)
            loc_menu.pack(pady=5)

        # Autocomplete for 'Take Away' action
        if action == "take":
            # Get all unique part numbers for autocomplete suggestions
            all_parts = sorted(list(self.matrix.get_all_parts()))
            
            # Autocomplete functionality
            def on_keyrelease(event):
                typed_text = part_entry.get().strip().lower()
                if hasattr(popup, 'dropdown_listbox'):
                    popup.dropdown_listbox.destroy()
                
                if typed_text:
                    # Filter parts that contain the typed text (case-insensitive)
                    matches = [p for p in all_parts if typed_text in p.lower()]
                    if matches:
                        popup.dropdown_listbox = tk.Listbox(popup, height=min(len(matches), 5), font=("Arial", 10), bd=1, relief=tk.SOLID)
                        for m in matches:
                            popup.dropdown_listbox.insert(tk.END, m)
                        
                        # Position the dropdown below the entry field
                        # Need to update_idletasks to get correct widget geometry
                        popup.update_idletasks() 
                        x_pos = part_entry.winfo_x()
                        y_pos = part_entry.winfo_y() + part_entry.winfo_height() + 5
                        popup.dropdown_listbox.place(x=x_pos, y=y_pos, width=part_entry.winfo_width())

                        def on_select(evt):
                            if popup.dropdown_listbox.curselection():
                                selection = popup.dropdown_listbox.get(popup.dropdown_listbox.curselection())
                                part_entry.delete(0, tk.END)
                                part_entry.insert(0, selection)
                                popup.dropdown_listbox.destroy()
                                part_entry.focus_set() # Return focus to entry after selection

                        popup.dropdown_listbox.bind("<Double-Button-1>", on_select)
                else:
                    if hasattr(popup, 'dropdown_listbox'):
                        popup.dropdown_listbox.destroy()

            part_entry.bind("<KeyRelease>", on_keyrelease)
            
            # Hide dropdown when focus leaves the entry or popup
            def hide_dropdown(event=None):
                if hasattr(popup, 'dropdown_listbox') and popup.dropdown_listbox.winfo_exists():
                    # Check if the click was outside the dropdown
                    if event and event.widget != popup.dropdown_listbox and event.widget != part_entry:
                        popup.dropdown_listbox.destroy()
                    elif not event: # If called without an event (e.g., on submit)
                        popup.dropdown_listbox.destroy()

            popup.bind("<Button-1>", hide_dropdown) # Bind to general click on popup
            part_entry.bind("<FocusOut>", hide_dropdown) # Hide when entry loses focus

        def submit():
            """Handles the submission of part and quantity for placing or taking."""
            part = part_entry.get().strip()
            if not part:
                return

            try:
                qty = int(qty_entry.get().strip())
                if qty <= 0:
                    return
            except ValueError:
                return

            if action == "place":
                loc_choice = location_var.get()
                if loc_choice == "Auto":
                    slot = self.matrix.place_part(part, qty)
                    if slot:
                        pass
                    else:
                        pass
                else: # Specific location chosen
                    current_content = self.matrix.storage[loc_choice]
                    if current_content["part"] is None:
                        self.matrix.storage[loc_choice] = {"part": part, "qty": qty}
                        pass
                    elif current_content["part"] == part:
                        self.matrix.storage[loc_choice]["qty"] += qty
                        pass
                    else:
                        return # Don't close popup if error
            else: # action == "take"
                result = self.matrix.take_part(part, qty)
                if result == "not_enough":
                    return # Don't close popup if error
                elif result:
                    pass
                else:
                    return # Don't close popup if error
            
            if hasattr(popup, 'dropdown_listbox') and popup.dropdown_listbox.winfo_exists():
                popup.dropdown_listbox.destroy() # Ensure dropdown is closed on submit
            popup.destroy() # Close popup on successful operation
            self.update_matrix() # Refresh the main display

        tk.Button(popup, text="Submit", command=submit, bg="#B5DFFF", fg="#333333", font=("Arial", 12, "bold"), relief=tk.RAISED, bd=3).pack(pady=15)

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = LeftoverApp(root)
    root.mainloop()

