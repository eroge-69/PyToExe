# -*- coding: utf-8 -*-
"""
Created on Thu May  8 15:45:28 2025

@author: m.taekema
"""

import tkinter as tk                                                            #Import tkinter for UI
from tkinter import filedialog, ttk                                             #import file search 
import csv                                                                      #import to open CSV files
import plotly.graph_objs as go                                                  #import plotly
from plotly.subplots import make_subplots                                       #import subplots to make multiple plots per page
import webbrowser                                                               #import browser to plot in browser
import os                                                                       #import os to safe and open files

selected_file_path = None                                                       # Will store the selected file path
current_fig = None                                                              # Stores the last generated plot

def show_plot(fig):
    temp_file = "temp_plot.html"                                                #define a temporary file to show in browser
    fig.write_html(temp_file, auto_open=False)                                  #saves it. Prevents it from auto opening
    webbrowser.open('file://' + os.path.realpath(temp_file))                    #opens the plot manually using the os_path from the selected data file
    
def read_csv_file(filepath):
    with open(filepath, newline='') as csvfile:                                 #opens a file for the given path as CSV
        reader = csv.reader(csvfile, delimiter=',')                             #Created an CSV object with the , as seperator
        next(reader)                                                            # Skip the header row
        data = []                                                               #initialise an empty list
        for row in reader:                                                      #loops through each row of file
            try:
                float_row = list(map(float, row))                               #tries to convert string to float
                data.append(float_row)                                          #append to data if succesful
            except ValueError:
                continue                                                        #skip row if in the row float conversion fails 
    if not data:
        print("No data in file.")                                               #give a message if a file is empty
        return []
    columns = list(zip(*data))                                                  #Transpose to get columns
    return columns                                                              #return the columns

def plot_data(columns, sensor_type):
    global current_fig                                                          #define as global variable
    if len(columns) < 6:                                                        #check if datafile is valid 
        print("Not enough columns in data.")                                    #output if not valid datafile
        return

    fig = make_subplots(                                                        #define different subplots
        rows=1,                                                                 #on 1 row
        cols=2,                                                                 #on 2 column (plot next to eachother on page)
        subplot_titles=("Redundant Deviation", "Position Deviation"),           #titles for plot from left to right
        horizontal_spacing = 0.075)                                             #spacing between plots in % of pixels. (7.5%) 

    # Plot 1: Column 2 vs Column 6
    fig.add_trace(go.Scattergl(                                                 #define GPU accelerated plot scatter
        x=columns[1],                                                           #define X values from column list
        y=columns[5],                                                           #define Y values from column list
        mode='markers',                                                         #plotmode
        marker=dict(size=3),                                                    #define thickness of scatter points
        name="Sensor dieA vs dieB"                                              #name the plot 
    ), row=1, col=1)                                                            #define plot position in subplots
    fig.update_xaxes(title_text="Sensor dieA", row=1, col=1)                    #X axis label
    fig.update_yaxes(title_text="Sensor dieB", row=1, col=1)    	            #Y axis label
 
    # Plot 2: Column 4 vs Column 5
    fig.add_trace(go.Scattergl(                                                 #define GPU accelerated plot scatter
        x=columns[3],                                                           #define X values from column list
        y=columns[4],                                                           #define Y values from column list
        mode='markers',                                                         #plotmode
        marker=dict(size=3, color='orange'),                                    #define thickness and color of scatter points
        name="RLS Encoder vs Sensor dieA"                                       #name the plot
    ), row=1, col=2)                                                            #define plot position in subplots
    fig.update_xaxes(title_text="RLS Rotary Encoder", row=1, col=2)             #X axis label
    fig.update_yaxes(title_text="Sensor dieA", row=1, col=2)                    #Y axis label

    # Set layout properties
    fig.update_layout(  
        title_text=f"Sensor: {sensor_type}",                                    #page title
        height=900,                                                             #plot size Y (scales)
        width=2000,                                                             #plot size X (scales)
        showlegend=True                                                         #view the legend on the page
    )

    # Fix Y-axis for both plots
    fig.update_yaxes(range=[-10, 10], row=1, col=1)                             #fix values for Y axis
    fig.update_yaxes(range=[-10, 10], row=1, col=2)                             #fix values for Y axis

    current_fig = fig                                                           # Save the figure for potential export
    show_plot(fig)                                                              # Show fig in browser.
    
def on_save():
    global current_fig                                                          #define variable as global
    if not current_fig:                                                         #if no plot exists                            
        print("No plot to save.")                                               #output message 
        return                                                                  #return from function

    # Suggest a default filename based on the loaded data file (if available)
    default_name = "plot.html"                                                  #suggest dummy file name
    if selected_file_path:                                                          #if a file path is defined (Selected file)
        base_filename = os.path.splitext(os.path.basename(selected_file_path))[0]   #use file path for name
        default_name = f"{base_filename}_plot.html"                                 #use selected file for naming

    # Open save dialog (for file path location)
    save_path = filedialog.asksaveasfilename(
        defaultextension=".html",
        filetypes=[("HTML files", "*.html")],
        initialfile=default_name,
        title="Save Plot As"
    )

    if save_path:
        current_fig.write_html(save_path)                                       #save file to selected path
        print(f"Plot saved to {save_path}")                                     #output to console
    
    
def on_browse():
    global selected_file_path                                                   #declare as global variable
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")]) #define file path variable
    if file_path:                                                               #check if path is valid
        selected_file_path = file_path                                          #update global file path
        file_entry_var.set(file_path)                                               

def on_plot():
    if not selected_file_path:                                                  #check is file path is choosen
        print("No file selected.")                                              #output if its not
        return                                                                  #return from function
    sensor_type = sensor_var.get()                                              #get the selected sensor
    columns = read_csv_file(selected_file_path)                                 #get the column from read csv function from file
    plot_data(columns, sensor_type)                                             #plot the column using a function

def main():
    global sensor_var, file_entry_var                                           #define globals

    root = tk.Tk()                                                              #initialise tinker UI
    root.title("Melexis HALL Sensor Dataplotter")                               #give it a title
    root.geometry("500x250")                                                    #size it as standard size

    # Sensor dropdown
    tk.Label(root, text="Select Sensor Type:", font=("Arial", 12)).pack(pady=5)
    sensor_var = tk.StringVar(value="MLX90316")
    sensor_dropdown = ttk.Combobox(root, textvariable=sensor_var, values=["MLX90316", "MLX90333"], state="readonly", font=("Arial", 11))
    sensor_dropdown.pack(pady=5)

    # File browser
    browse_button = tk.Button(root, text="Browse for data file", command=on_browse, font=("Arial", 11), width=25)
    browse_button.pack(pady=5)

    # File path entry
    file_entry_var = tk.StringVar()
    file_entry = tk.Entry(root, textvariable=file_entry_var, font=("Arial", 10), width=180, state='readonly')
    file_entry.pack(pady=5)

    # Plot button
    plot_button = tk.Button(root, text="Plot", command=on_plot, font=("Arial", 11), width=25)
    plot_button.pack(pady=10)
    
    # Save button
    save_button = tk.Button(root, text="Save Plot as HTML", command=on_save, font=("Arial", 11), width=25)
    save_button.pack(pady=5)

    root.mainloop()                                                             #run async tk loop

if __name__ == "__main__":                                                      #define namespace main
    main()                                                                      #run main
