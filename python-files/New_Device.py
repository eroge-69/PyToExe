# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 10:38:57 2025

@author: akhattab
"""

#Ask user to select Sciospec folder and load spec files from its subfolders
from scipy import signal

import os
import csv
from pandas import ExcelWriter

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import auc
import openpyxl

import tkinter as tk
from tkinter import filedialog


from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Create the main GUI window
root = tk.Tk()
root.title("Electrical Impedance Spectroscopy analyzer")

root.geometry("800x300")


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_path_var.set(folder_path)





def close_window():   
        root.destroy()
        


def read_csv_to_array(file_path):
    data_array = []
    with open(file_path, 'r', newline='') as csvfile:
        csv_reader = list(csv.reader(csvfile,delimiter=","))
        for row in csv_reader:
            data_array.append(row)
    return data_array

# Main function to process CSV files in subfolders
def process_subfolders(root_dir):
    csv_arrays = {}  # Dictionary to store arrays with subfolder names as keys

    for folder_name, subfolders, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('01.spec'):
                file_path = os.path.join(folder_name, filename)
                data_array = read_csv_to_array(file_path)
                csv_arrays[file_path] = data_array

    return csv_arrays


select_button = tk.Button(root, text="Select Sciospec data", command=select_folder)
select_button.pack(pady=5)

close_button = tk.Button(root, text="Close", command=close_window)
close_button.pack(padx=20, pady=10)


folder_path_var = tk.StringVar()
folder_path_label = tk.Label(root, textvariable=folder_path_var)
folder_path_label.pack(pady=10)








def plot_impedance():

    selected_folder_path = folder_path_var.get()
    root_directory = selected_folder_path
    csv_data_arrays = process_subfolders(root_directory)
    keys = []
    values = []

    for key in csv_data_arrays:
        keys.append(key)
        values.append(csv_data_arrays[key])

          
    fig, ax = plt.subplots(1,dpi=200) # higher resolution
    #plt.title("Impedance Spectra")
    plt.xlabel("Frequency [Hz]", fontsize=20) #use predefined x-axis label in the raw data file
    plt.ylabel("|Z| [\u03A9]", fontsize=20) #use predefined y-axis label in the raw data file
    plt.yscale("log") # scale the y axis to log
    plt.xscale("log") # scale the x axis to log

    colors = [
    "#000000", "#FE420F", "#0000FF", "#C0C0C0", "#12239E", "#0AAC00", "#8250C4", "#000000", "#FE420F", "#C0C0C0", "#12239E", 
    "#0AAC00", "#8250C4", "#000000", "#FE420F", "#C0C0C0", "#12239E", "#0AAC00", "#8250C4", "#000000", "#FE420F", 
    "#C0C0C0", "#12239E", "#0AAC00", "#8250C4", "#000000", "#FE420F", "#C0C0C0", "#12239E", "#0AAC00", "#8250C4",
    "#FFFFCB", "#FFFFCB", "#FFFFCB", "#FFFFCB", "#FFFFCB", "#FFFFCB", "#F97306", "#A52A2A", "#D2691A", "#FF7F50",
    "#7E1E9C", "#00FFFF", "#00008B", "#FFD700", "#069AF3", "#E6DAA6", "#563700", "#000000", "#FC5A50", "#8C000F",
    "#054907", "#ED0DD9", "#DBB40C", "#4B0082", "#F0E68C", "#E6E6FA", "#800000", "#7BC8F6", "#C20078", "#FFC0CB", 
    "#D2691A", "#FF7F50", "#7E1E9C", "#00FFFF", "#00008B", "#FFD700", "#069AF3", "#E6DAA6", "#563700", "#C1F80A", 
    "#FC5A50", "#8C000F", "#054907", "#ED0DD9", "#DBB40C", "#4B0082", "#F0E68C", "#E6E6FA", "#800000", "#7BC8F6", 
    "#C20078", "#FFC0CB", "#15B01A", "#C79FEF", "#650021", "#6E750E", "#7FFF00", "#FE420F", "#C875C4", "#FF81C0", 
    "#380282", "#929591", "#800080", "#A0522D", "#C0C0C0", "#008080", "#FF6347", "#580F41", "#E50000", "#FF796C", 
    "#D1B26F", "#06C2AC", "#9A0EEA", "#FFFF14"    
]
    
    # Store results for Excel export
    auc_output_data = []  # For AUC of output_signal[50:75]
    auc_impedance_data = []  # For AUC of impedance_mag[25:58]

    for file, color in zip(values, colors):
        df = np.array(file[8:], dtype=np.float64)
        electrode_data = np.array(file[:8], dtype=object)
        electrode_label = electrode_data[5][-1]

        index = electrode_label.find("(Ext)")
        label = electrode_label[index + len("(Ext)"):].strip()

        Freq = df[:, 0]
        Zreal = df[:, 1]
        Zimg = df[:, 2]

        impedance_mag = np.sqrt(Zreal**2 + Zimg**2)

        # Apply Butterworth filter
        fs = 100
        cutoff_frequency = 10
        order = 4
        b, a = signal.butter(order, cutoff_frequency / (fs / 2), 'low')
        output_signal = signal.lfilter(b, a, impedance_mag)

        # Compute AUCs
        auc1 = auc(Freq[50:75], impedance_mag[50:75])  # 10476.0986328125 Hz --> 97700.9765625 Hz
        auc2 = auc(Freq[25:58], impedance_mag[25:58])  #1023.5235595703125 Hz --> 20092.353515625 Hz Hz

        # Round for clarity
        auc_output_data.append({'Electrode': label, 'AUC_10kHz-100kHz': round(auc1, 2)})
        auc_impedance_data.append({'Electrode': label, 'AUC_1kHz-20kHz': round(auc2, 2)})

        # Plotting as usual
        plt.plot(Freq[8:120], impedance_mag[8:120], label=label, color=color)

    global stored_auc_data_10kHz_100kHz
    global stored_auc_data_1kHz_20kHz
    stored_auc_data_10kHz_100kHz = pd.DataFrame(auc_output_data)
    stored_auc_data_1kHz_20kHz = pd.DataFrame(auc_impedance_data)


    
    
    
    
    
    ax.set_axisbelow(True) # Don't allow the axis to be on top of your data
    ax.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
    ax.grid(which='major', linestyle='-', linewidth='0.5', color='darkgrey') # Customize the major grid
    ax.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')# Customize the minor grid

    # Embed the plot in a Tkinter window
    plot_window = tk.Toplevel(root)
    plot_canvas = FigureCanvasTkAgg(fig, master=plot_window)
    plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
    plot_canvas.draw()
    print("------------finished-------------")
    
    
    
    # Create a menu bar
    menu_bar = tk.Menu(plot_window)
    plot_window.config(menu=menu_bar)

    # Create a File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)


    # Add options to the File menu
   
    file_menu.add_command(label="Save", command=save_plot)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=plot_window.destroy)
    
 


def save_plot():
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        plt.savefig(file_path)
        #tk.messagebox.showinfo("Success", "Plot saved successfully!")











def plot_phase():

    selected_folder_path = folder_path_var.get()
    root_directory = selected_folder_path
    csv_data_arrays = process_subfolders(root_directory)
    keys = []
    values = []

    for key in csv_data_arrays:
        keys.append(key)
        values.append(csv_data_arrays[key])

          
    fig, ax = plt.subplots(1,dpi=200) # higher resolution
    #plt.title("Phase Plot")
    plt.xlabel("Frequency [Hz]") #use predefined x-axis label in the raw data file
    plt.ylabel("Φ [°]") #use predefined y-axis label in the raw data file
    
    plt.xscale("log") # scale the x axis to log

    colors = [
    "#000000", "#FE420F", "#0000FF",  "#C0C0C0", "#12239E", "#0AAC00", "#8250C4", "#000000", "#FE420F", "#C0C0C0", "#12239E", 
    "#0AAC00", "#8250C4", "#000000", "#FE420F", "#C0C0C0", "#12239E", "#0AAC00", "#8250C4", "#000000", "#FE420F", 
    "#C0C0C0", "#12239E", "#0AAC00", "#8250C4", "#000000", "#FE420F", "#C0C0C0", "#12239E", "#0AAC00", "#8250C4",
    "#FFFFCB", "#FFFFCB", "#FFFFCB", "#FFFFCB", "#FFFFCB", "#FFFFCB", "#F97306", "#A52A2A", "#D2691A", "#FF7F50",
    "#7E1E9C", "#00FFFF", "#00008B", "#FFD700", "#069AF3", "#E6DAA6", "#563700", "#000000", "#FC5A50", "#8C000F",
    "#054907", "#ED0DD9", "#DBB40C", "#4B0082", "#F0E68C", "#E6E6FA", "#800000", "#7BC8F6", "#C20078", "#FFC0CB", 
    "#D2691A", "#FF7F50", "#7E1E9C", "#00FFFF", "#00008B", "#FFD700", "#069AF3", "#E6DAA6", "#563700", "#C1F80A", 
    "#FC5A50", "#8C000F", "#054907", "#ED0DD9", "#DBB40C", "#4B0082", "#F0E68C", "#E6E6FA", "#800000", "#7BC8F6", 
    "#C20078", "#FFC0CB", "#15B01A", "#C79FEF", "#650021", "#6E750E", "#7FFF00", "#FE420F", "#C875C4", "#FF81C0", 
    "#380282", "#929591", "#800080", "#A0522D", "#C0C0C0", "#008080", "#FF6347", "#580F41", "#E50000", "#FF796C", 
    "#D1B26F", "#06C2AC", "#9A0EEA", "#FFFF14"
    
]
    
    pi=np.pi
    
    for file, color in zip(values,colors):
        df = np.array(file[8:],dtype=np.float64)
        electrode_data= np.array(file[:8],dtype=object)
        electrode_label=electrode_data[5][-1]
    
           
        # Find the index of the keyword
        index = electrode_label.find("(Ext)")
        
        # If the keyword is found, extract and print the text after it
        label1 = electrode_label[index + len("(Ext)"):].strip()
        #print(label1)
        
        
        Freq=df[:,0]
        Zreal=df[:,1]
        Zimg=df[:,2]
        
        phase=np.arctan(Zimg/Zreal)
        phase_deg=(phase*180)/pi
        #print(phase_deg)

        # Design a low-pass Butterworth filter
        #fs2 = 100  # Sampling frequency (Hz)
        #cutoff_frequency = 10  # Cutoff frequency (Hz)
        #order = 4  # Filter order
        #b, a = signal.butter(order, cutoff_frequency / (fs2 / 2), 'low')

        # Apply the filter to the signal
        #phase_deg = signal.lfilter(b, a, phase_deg)
            
            
        
        #plt.plot(Freq[7:120],impedance_mag[7:120],linestyle='dotted',label=label1,color='k')
        plt.ylim(-100, 25)
        plt.rcParams['font.family'] = 'Times New Roman'
        plt.plot(Freq[1:120],phase_deg[1:120],label=label1,color=color)
        #plt.legend(fontsize="8",loc ="upper right") # normal value =3
    
    
    
    
    
    ax.set_axisbelow(True) # Don't allow the axis to be on top of your data
    ax.minorticks_on() # Turn on the minor TICKS, which are required for the minor GRID
    ax.grid(which='major', linestyle='-', linewidth='0.5', color='darkgrey') # Customize the major grid
    ax.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')# Customize the minor grid

    # Embed the plot in a Tkinter window
    plot_window = tk.Toplevel(root)
    plot_canvas = FigureCanvasTkAgg(fig, master=plot_window)
    plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
    plot_canvas.draw()
    
    
    
    
    # Create a menu bar
    menu_bar = tk.Menu(plot_window)
    plot_window.config(menu=menu_bar)

    # Create a File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="File", menu=file_menu)


    # Add options to the File menu
   
    file_menu.add_command(label="Save", command=save_plot)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=plot_window.destroy)
    
 


def save_plot():
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        plt.savefig(file_path)
        #tk.messagebox.showinfo("Success", "Plot saved successfully!")





def generate_excel():
    try:
        import tempfile
        import subprocess

        if stored_auc_data_10kHz_100kHz.empty or stored_auc_data_1kHz_20kHz.empty:
            print("No data available. Run |Z| plot first.")
            return

        # Create a temporary Excel file
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            temp_excel_path = tmp.name

        with pd.ExcelWriter(temp_excel_path, engine='openpyxl') as writer:
            stored_auc_data_10kHz_100kHz.to_excel(writer, sheet_name='AUC_10kHz-100kHz', index=False)
            stored_auc_data_1kHz_20kHz.to_excel(writer, sheet_name='AUC_1kHz-20kHz', index=False)

        # Open in Excel for user to review/save manually
        print(f"Opening Excel for manual saving: {temp_excel_path}")
        os.startfile(temp_excel_path)  # Windows only

    except Exception as e:
        print("Error generating Excel file:", e)



excel_button = ttk.Button(root, text='Generate AUC values', command=generate_excel)
excel_button.pack(pady=10)



# Create buttons
button1 = ttk.Button(root, text='|Z|', command=plot_impedance)
button1.pack(pady=10)

button2 = ttk.Button(root, text='phase', command=plot_phase)
button2.pack(pady=10)











# Start the Tkinter event loop
root.mainloop()



















#colors = [
    #"#000000", "#0000FF", "#E50000", "#6E750E", "#F97306", "#FE420F", "#C875C4", "#FF81C0", "#380282", "#929591",
    #"#800080", "#A0522D", "#C0C0C0", "#008080", "#FF6347", "#580F41", "#C79FEF", "#FF796C", "#D1B26F", "#06C2AC",
    #"#9A0EEA", "#FFFF14", "#FFFFCB", "#7FFFD4", "#808080", "#F5F5DC", "#C1F80A", "#0000FF", "#15B01A", "#A52A2A",
    #"#FFFFCB", "#7FFFD4", "#808080", "#F5F5DC", "#7FFF00", "#650021", "#F97306", "#A52A2A", "#D2691A", "#FF7F50",
    #"#7E1E9C", "#00FFFF", "#00008B", "#FFD700", "#069AF3", "#E6DAA6", "#563700", "#000000", "#FC5A50", "#8C000F",
    #"#054907", "#ED0DD9", "#DBB40C", "#4B0082", "#F0E68C", "#E6E6FA", "#800000", "#7BC8F6", "#C20078", "#FFC0CB", 
    #"#D2691A", "#FF7F50", "#7E1E9C", "#00FFFF", "#00008B", "#FFD700", "#069AF3", "#E6DAA6", "#563700", "#C1F80A", 
    #"#FC5A50", "#8C000F", "#054907", "#ED0DD9", "#DBB40C", "#4B0082", "#F0E68C", "#E6E6FA", "#800000", "#7BC8F6", 
    #"#C20078", "#FFC0CB", "#15B01A", "#C79FEF", "#650021", "#6E750E", "#7FFF00", "#FE420F", "#C875C4", "#FF81C0", 
    #"#380282", "#929591", "#800080", "#A0522D", "#C0C0C0", "#008080", "#FF6347", "#580F41", "#E50000", "#FF796C", 
    #"#D1B26F", "#06C2AC", "#9A0EEA", "#FFFF14"
    
#]
























