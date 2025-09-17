import win32com.client
import pandas as pd
import os
import tkinter as tk
from tkinter import ttk
import sys
import re

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.config(state='normal')  # Enable editing
        self.text_widget.insert(tk.END, message)  # Append message
        self.text_widget.see(tk.END)  # Scroll to end
        self.text_widget.config(state='disabled')  # Disable editing
        self.text_widget.update()

    def flush(self):
        pass  # Required for sys.stdout compatibility

#AutoDrawGui:
class AutoDrawGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AutoDraw")
        self.root.geometry("1000x600")

        #Creating Separate Frames
        self.LeftFrame = tk.Frame(self.root, width = 300, bg = "lightgray", bd = 2, relief = "groove")
        self.RightFrame= tk.Frame(self.root, width = 700, bg = "lightgray",bd = 2, relief = "groove")

        #Placing Separate Frames
        self.LeftFrame.pack(side = "left",fill = "both", expand = True)
        self.RightFrame.pack(side = "right",fill = "both", expand = True)

        #Path of Template Folder
        self.template_path_label = tk.Label(self.LeftFrame, text="Template Folder Path", font = ("Arial",24), width = 20, height = 2, bg = "Lightgray", fg = "Black")
        self.template_path_label.grid(row = 1, column = 0)

        #Entry for Template Path
        self.template_entry = tk.Entry(self.LeftFrame, width = 40 )
        self.template_entry.grid(row = 4, column = 0)

        #Output Folder Path
        self.output_path_label = tk.Label(self.LeftFrame, text="Output Folder Path", font = ("Arial",24), width = 15, height = 2, bg = "lightgray", fg = "Black")
        self.output_path_label.grid(row = 5, column = 0)

        #Entry for output folder
        self.output_entry = tk.Entry(self.LeftFrame, width = 40)
        self.output_entry.grid(row = 8, column = 0)

        #Panel List Path
        self.PanelList_path_label = tk.Label(self.LeftFrame, text="Panel List Path", font = ("Arial",24), width = 15, height = 2, bg = "lightgray", fg = "Black")
        self.PanelList_path_label.grid(row = 9, column = 0)

        #Entry for Panel List Path
        self.PanelList_entry = tk.Entry(self.LeftFrame, width = 40)
        self.PanelList_entry.grid(row = 12, column = 0)

        #Entry for job number
        self.JobNumberLabel = tk.Label(self.LeftFrame, text = "Job Number:", font = ("Arial", 24), width = 15, height = 2, bg = "lightgray", fg = "Black")
        self.JobNumberLabel.grid(row = 13, column = 0)
        self.JobNumberEntry = tk.Entry(self.LeftFrame, width = 40)
        self.JobNumberEntry.grid(row = 16, column = 0)

        #Entry for room number
        self.RoomNumberLabel = tk.Label(self.LeftFrame, text = "Room Number:", font = ("Arial", 24), width = 15, height = 2, bg = "lightgray", fg = "Black")
        self.RoomNumberLabel.grid(row = 17, column = 0)
        self.RoomNumberEntry = tk.Entry(self.LeftFrame, width = 40)
        self.RoomNumberEntry.grid(row = 20, column = 0)

def AutoDraw():

    #excel_file_loc = input("Path of Panel List: ")
    #template_folder = input("Path of template folder: ")
    #save_folder = input("Path of job folder: ")
    job = AutoDrawGUI.JobNumberEntry.get().strip(' "')
    room = AutoDrawGUI.RoomNumberEntry.get().strip(' "')

    # Paths - Replace <YourUsername> with your Windows username (e.g., 'caden.crenshaw')
    template_folder = AutoDrawGUI.template_entry.get().strip(' "')
    output_folder = AutoDrawGUI.output_entry.get().strip(' "')
    excel_file = AutoDrawGUI.PanelList_entry.get().strip(' "')  # Update if Excel is elsewhere 

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Read Excel data starting from row 4 (index 3), columns E-N (indices 4-13)
    df = pd.read_excel(excel_file, sheet_name= AutoDrawGUI.RoomNumberEntry.get().strip(), header=None, skiprows=3)
    df = df.iloc[:, 4:10]  # Columns E-N (0-indexed: 4 to 9)
    df.columns = ['Panel Label', 'Type', 'Height', 'Bend 1/ Left', 'Bend 2/ Right', "Bend 3"]

    print("Excel data loaded:")
    print(df)

    # Template paths
    template_paths = {
        "FLAT": os.path.join(template_folder, "Flat Panel 2886.psm"),
        "IN90": os.path.join(template_folder, "Inside 90 2886.psm"),
        "OUT90": os.path.join(template_folder, "Outside 90 2886.psm"),
        "IN135": os.path.join(template_folder, "Inside 135 2886.psm"),
        "OUT135": os.path.join(template_folder, "Outside 135 2886.psm"),
        "FLAT1": os.path.join(template_folder, "Lower Flat Panel 2886.psm"),
        "FLAT2": os.path.join(template_folder, "Upper Flat Panel 2886.psm"),
        "ZIN": os.path.join(template_folder, "Z Inside Panel 2886.psm"),
        "ZOUT": os.path.join(template_folder, "Z OutSide Panel 2886.psm"),
        "WIN": os.path.join(template_folder, "Window.psm"),
        "MON": os.path.join(template_folder, "Monitor.psm"),
        "UPANEL": os.path.join(template_folder, "U-Panel 2886.psm"),
        "BACK BOX" or "BACKBOX": os.path.join(template_folder, "Back Box.psm"),
        "STORY POLE" or "STORYPOLE": os.path.join(template_folder, "Story Pole.psm"),
    }

    # Initialize Solid Edge
    try:
        se_app = win32com.client.GetActiveObject("SolidEdge.Application")
    except:
        se_app = win32com.client.Dispatch("SolidEdge.Application")
    se_app.Visible = False  # Set to False for faster processing after testing
    se_app.DisplayAlerts = False  # Suppress dialog boxes

    # Process each row
    for index, row in df.iterrows():
        part_name = row['Panel Label']
        part_type = row['Type']
        
        # Skip empty rows
        if pd.isna(part_name) or pd.isna(part_type):
            print(f"Skipping empty row {index + 4}")
            continue
        
        print(f"Processing {part_name} ({part_type})")
        
        if part_type not in template_paths:
            print(f"Unknown part type: {part_type}")
            continue
        
        template_path = template_paths[part_type]
        
        # Check if template exists
        if not os.path.exists(template_path):
            print(f"Template not found: {template_path}")
            continue
        
        # Open the template
        try:
            print(f"Opening template: {template_path}")
            se_doc = se_app.Documents.Open(template_path)
            se_vars = se_doc.Variables
            
            # Update variables based on part type
            if part_type == "FLAT" or "FLAT1":
                se_vars.Item("Height").Value = row['Height']
                se_vars.Item("Bend1").Value = row['Bend 1/ Left']
                print(f"Updated Flat: Height={row['Height']}, Bend 1/ Left={row['Bend 1/ Left']}")
            elif part_type == "FLAT2":
                se_vars.Item("Height").Value = row['Height']
                se_vars.Item("Bend1").Value = row['Bend 1/ Left']
                print(f"Updated Flat: Height={row['Height']}, Bend 1/ Left={row['Bend 1/ Left']}")
            elif part_type == "IN90" or "OUT90":
                se_vars.Item("Height").Value = row['Height']
                se_vars.Item("Bend1").Value = row['Bend 1/ Left']
                se_vars.Item("Bend2").Value = row['Bend 2/ Right']
                print(f"Updated 90: Height={row['Height']}, Bend 1/ Left={row['Bend 1/ Left']}, Bend 2/ Right={row['Bend 2/ Right']}")
            elif part_type == "IN135" or "OUT135":
                se_vars.Item("Height").Value = row['Height']
                se_vars.Item("Bend1").Value = row['Bend 1/ Left']
                se_vars.Item("Bend2").Value = row['Bend 2/ Right']
                print(f"Updated 135: Height={row['Height']}, Bend 1/ Left={row['Bend 1/ Left']}, Bend 2/ Right={row['Bend 2/ Right']}")
            elif part_type == "UPANEL":
                se_vars.Item("Height").Value = row['Height']
                se_vars.Item("Bend1").Value = row['Bend 1/ Left']
                se_vars.Item("Bend2").Value = row['Bend 2/ Right']
                se_vars.Item("Bend3").Value = row['Bend 3']
                print(f"Updated U Panel: Height={row['Height']}, Bend 1/ Left={row['Bend 1/ Left']}, Bend 2/ Right={row['Bend 2/ Right']}, Bend 3 = {row['Bend 3']}")
            elif part_type == "ZOUT" or "ZIN":
                se_vars.Item("Height").Value = row['Height']
                se_vars.Item("Bend1").Value = row['Bend 1/ Left']
                se_vars.Item("Bend2").Value = row['Bend 2/ Right']
                se_vars.Item("Bend3").Value = row['Bend 3']
                print(f"Updated Z Panel: Height={row['Height']}, Bend 1/ Left={row['Bend 1/ Left']}, Bend 2/ Right={row['Bend 2/ Right']}")
            #elif part_type == "TRIM":
                #se_vars.Item("Height").Value = row['Height']
                #se_vars.Item("Bend1").Value = row['Bend 1/ Left']
                #se_vars.Item("Bend2").Value = row['Bend 2/ Right']
                #print(f"Updated Trim: Height={row['Height']}, Bend 1/ Left={row['Bend 1/ Left']}, Bend 2/ Right={row['Bend 2/ Right']}")
            elif part_type == "WIN" or "MON":
                se_vars.Item("Height").Value = row['Height']
                se_vars.Item("Bend1").Value = row['Bend 1/ Left']
                print(f"Updated Z Panel: Height={row['Height']}, Bend 1/ Left={row['Bend 1/ Left']}")
            #elif part_type == "PCT-R" or "PCT-L":
                #se_vars.Item("Height").Value = row['Height']
                #print(f"Updated Panel Trim: Height={row['Height']}")
            elif part_type == "STORY POLE":
                se_vars.Item("Height").Value = row['Height']
                print(f"Updated Story Pole: Height={row['Height']}")
            elif part_type == "BACK BOX" or "BACKBOX":
                se_vars.Item("Height").Value = row['Height']
                se_vars.Item("Bend1").Value = row['Bend 1/ Left']
                print(f"Updated Back Box: Height={row['Height']}, Bend 1/ Left={row['Bend 1/ Left']}")



            # Save the updated part

            save_path = os.path.join(output_folder, f"{job}-{room}-{part_name}.psm")

            #update_solid_edge_model()
            
            se_doc.SaveAs(save_path)
            se_doc.Close()
            print(f"Generated: {save_path}")
        
        except Exception as e:
            print(f"Error processing {part_name}: {str(e)}")
            if 'se_doc' in locals():
                se_doc.Close()

    # Clean up
    se_app.Quit()
    print("Automation complete!")
    print("Update panel labels.")

class OutPutLabel:
    def __init__(self, AutoDrawGUI):
        self.output_label = tk.Label(AutoDrawGUI.RightFrame, text = "Output Log", font = ("Arial", 18), bg = "lightgrey", fg = "Black",)
        self.output_label.pack(pady = 5)
        self.output_text = tk.Text(AutoDrawGUI.RightFrame, height = 15, width = 50, state = "disabled", wrap = tk.WORD, bg = "white", fg = "Black")
        self.output_text.pack(padx=10, pady=5, fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(AutoDrawGUI.RightFrame, orient="vertical", command=self.output_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=self.scrollbar.set)

        self.sys.stdout = TextRedirector(OutPutLabel.output_text)    

class RunButton:
    def __init__ (self, AutoDrawGUI):
        self.RunButton = tk.Button(AutoDrawGUI.LeftFrame, width  = 10, height = 2, text = "Run", font = ("Arial",24),bg = "red2", command = AutoDraw, relief = "raised") 
        self.RunButton.grid(row = 24, column = 0, padx = 10, pady = 10,) 

AutoDrawGUI.root.mainloop()
    
