#Biologic Analyser GUi

from galvani import BioLogic
import pandas as pd
import os
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib import colormaps
import numpy as np
import re
import csv
from itertools import zip_longest

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import addcopyfighandler
import io
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication

# Create the main window
root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
frm.columnconfigure(1, weight=5)

# style = ttk.Style()
# style.configure("TButton",
#                          # foreground="red",
#                          background="black",
#                          font="Times 12",relief="raised")
#variables
FolderName = StringVar(root, name="FoldaName")
FileName = StringVar(root, name="FileNayme")
ActiveMassMG = DoubleVar(root, name="ActiveMass")
ElectrodeArea = DoubleVar(root, name="ElecArea")
ExtractActiveMassFromFileName = IntVar(root)
ActiveMassIsCathodeMass = IntVar(root)
DrawGraphsInHere = IntVar(root)
PlotCapacityFade = IntVar(root)
PlotEfficiency = IntVar(root)
PlotCycles = IntVar(root)
ChargeDischargeOrDischargeCharge = IntVar(root)
ListOfCycles = StringVar(root, name="CycleList")
cmap = colormaps['jet']

ExportTime = IntVar(root)
ExportCap= IntVar(root)
ExportCurrent = IntVar(root)
ExportVolt = IntVar(root)
ExportEfficiency = IntVar(root)

UpperLimit = DoubleVar(root, value=3.0)
LowerLimit = DoubleVar(root, value=1.8)
AxisSelection = StringVar(root)

# store data
processed_data = {}
axis_limits_storage = {} # NEW: To store user-defined slider settings

# init!
Initialize = IntVar(root)
if Initialize.get() == 0:
    fig1 = 1
    fig2 = 1
    Initialize.set(1)
    
#temp = self.zeros1.get()      
#ListOfCycles = [float(s) for s in re.findall(r'-?\d+\.?\d*', temp)]
# functions
def FindFolder():
    """Opens a dialog to select a folder and populates the file list."""
    FolderName.set(filedialog.askdirectory())
    if not FolderName.get(): return
    
    CellList.delete(0, END)
    for filename in sorted(os.listdir(FolderName.get())):
        if filename.endswith(".mpr"):
            CellList.insert(END, filename)
    
def SelectedFileFromFolder(event):
    #This extracts sulfur mass from filename - might be dodgy
    """Triggered on file selection. Loads and processes data."""
    try:
        selected_index = CellList.curselection()[0]
        selected_File = CellList.get(selected_index)
        FileName.set(selected_File)
        
        if ExtractActiveMassFromFileName.get()==1:
            tmpActiveMassMG = re.findall(r'(\d+)p(\d+)',selected_File)
            if tmpActiveMassMG:
                # Extract the numbers
                tmpActiveMassMG = [match for match_pair in tmpActiveMassMG for match in match_pair]
                tmpActiveMassMG = float(f"{tmpActiveMassMG[0]}.{tmpActiveMassMG[1]}")
                if ActiveMassIsCathodeMass.get()==1:
                    tmpActiveMassMG = (tmpActiveMassMG-6.6)*0.65 # FOR IF CATHODE MASS
                ActiveMassMG.set(tmpActiveMassMG)
        # --- Load and process the data from the selected file
        load_and_process_data()
    except IndexError:
        pass # Ignore errors if listbox is clicked when empty
        
def add_figure_to_clipboard(figNo):
    if fig1 != 1 and fig2 != 1:
        with io.BytesIO() as buffer:
            if figNo == 1:
                fig1.savefig(buffer)
            elif figNo == 2:
                fig2.savefig(buffer)
            QApplication.clipboard().setImage(QImage.fromData(buffer.getvalue()))
            
def load_and_process_data():
    """Reads and parses the MPR file, storing results in the global processed_data dict."""
    global processed_data, axis_limits_storage
    processed_data = {} # Clear previous data
    axis_limits_storage = {} # Clear stored limits for the new file

    file_path = os.path.join(FolderName.get(), FileName.get())
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Processing {FileName.get()}...")
    mpr_file = BioLogic.MPRfile(file_path)
    Dataz = pd.DataFrame(mpr_file.data)

    CycleNumb = 1
    Time = 0
    DischargeCap = []
    ChargeCap = []
    Efficiency = []
    CapRetention = []
 
    # These will store the detailed data for each cycle
    ChargeExtract = []
    DischargeExtract = []
    
    # Main loop to parse the data file
    for i in range(len(Dataz)-1):
        if ((Dataz['Ns'][i]==1) and (Dataz['Ns'][i-1]==0)):
            Time = i
        # A new half-cycle begins when the current sign changes or at the very end of the file.
            #adjust for wierd current heading
        if 'control/mA' in Dataz.columns:
            TargetCurrent = 'control/mA'
        elif 'control/V/mA' in Dataz.columns:
            TargetCurrent = 'control/V/mA'
        else:
            print('No target current in file???')
        if 'I/mA' in Dataz.columns:
            ActualCurrent = 'I/mA'
        elif 'control/V/mA' in Dataz.columns:
            ActualCurrent = TargetCurrent
        else:
            print('No actual current in file???')
        
        if (Dataz[TargetCurrent][i+1]*Dataz[TargetCurrent][i])<0 or i+1 == len(Dataz)-1: 
            CurrentmA = abs(Dataz[TargetCurrent][i])
            TimeHours = (Dataz['time/s'][i] - Dataz['time/s'][Time])/3600
            # Capacity in mAh/g
            Cap = (CurrentmA * TimeHours) / (ActiveMassMG.get()/1000)
 
            cycle_data = {
                "time": Dataz['time/s'][Time:i],
                "voltage": Dataz['Ewe/V'][Time:i],
                "current": Dataz[ActualCurrent][Time:i],
                "capacity": (CurrentmA * ((Dataz['time/s'][Time:i] - Dataz['time/s'][Time]) / 3600)) / (ActiveMassMG.get() / 1000)
            }
 
            if Dataz[TargetCurrent][i] > 0: # Charge
                ChargeCap.append(Cap)
                ChargeExtract.append(cycle_data)
                if ChargeDischargeOrDischargeCharge.get() == 0:
                    if ChargeCap and DischargeCap:
                        Efficiency.append((DischargeCap[-1] / ChargeCap[-1]) * 100)
                    CycleNumb += 1
 
            elif Dataz[TargetCurrent][i] < 0: # Discharge
                DischargeCap.append(Cap)
                DischargeExtract.append(cycle_data)
                if DischargeCap:
                    CapRetention.append((DischargeCap[-1] / DischargeCap[0]) * 100)
                if ChargeDischargeOrDischargeCharge.get() == 1:
                    if ChargeCap and DischargeCap:
                        Efficiency.append((DischargeCap[-1] / ChargeCap[-1]) * 100)
                    CycleNumb += 1
            Time = i + 1
            
    # Store all results
    processed_data = {
        'DischargeCap': np.array(DischargeCap),
        'ChargeCap': np.array(ChargeCap),
        'Efficiency': np.array(Efficiency),
        'CapRetention': np.array(CapRetention),
        'ChargeExtract': ChargeExtract,
        'DischargeExtract': DischargeExtract
    }
    print("Processing complete.")
    update_slider_config() # Update sliders with new data ranges
    
def save_current_slider_values(*args):
    """Saves the current slider values to the storage dictionary whenever a slider is moved."""
    selection = AxisSelection.get()
    if selection in axis_limits_storage:
        axis_limits_storage[selection]['lower'] = LowerLimit.get()
        axis_limits_storage[selection]['upper'] = UpperLimit.get()
def update_slider_config(event=None):
    """Adjusts sliders by loading stored settings or creating new ones from data."""
    # If settings for this selection are already stored, use them
    selection = AxisSelection.get()
    if not processed_data: return

    if selection in axis_limits_storage:
        stored_settings = axis_limits_storage[selection]
        LowerPotentialSlider.config(from_=stored_settings['from'], to=stored_settings['to'], resolution=stored_settings['res'])
        UpperPotentialSlider.config(from_=stored_settings['from'], to=stored_settings['to'], resolution=stored_settings['res'])
        LowerLimit.set(stored_settings['lower'])
        UpperLimit.set(stored_settings['upper'])
        return
    # Otherwise, calculate defaults for the first time
    min_val, max_val, resolution = 0, 100, 1

    if not processed_data: # No data loaded yet
        return

    try:
        if selection == "Potential Range (Cycles)":
            all_volts = pd.concat([d['voltage'] for d in processed_data['ChargeExtract']] + [d['voltage'] for d in processed_data['DischargeExtract']])
            min_val, max_val, resolution = all_volts.min(), all_volts.max(), 0.05
        elif selection in ["Capacity Range (Cycles)", "Capacity Range (Fade)"]:
            all_caps = np.concatenate([d['capacity'] for d in processed_data['ChargeExtract']] + [d['capacity'] for d in processed_data['DischargeExtract']])
            min_val, max_val, resolution = 0, all_caps.max(), 10
        elif selection == "Efficiency Range" and len(processed_data['Efficiency']) > 0:
            min_val, max_val, resolution = processed_data['Efficiency'].min(), processed_data['Efficiency'].max(), 1
        elif selection == "Cycle Range" and len(processed_data['DischargeCap']) > 0:
            min_val, max_val, resolution = 1, len(processed_data['DischargeCap']), 1
    except (ValueError, KeyError): # Handle empty data cases
        print(f"Could not determine range for {selection}. Using defaults.")
        return

    # Add 50% padding to the Slider range for better selection
    paddingSlide = (max_val - min_val) * 0.5
    paddedSlide_min = min_val - paddingSlide
    paddedSlide_max = max_val + paddingSlide
    # Add 5% padding to the default setting for better visualization
    paddingView = (max_val - min_val) * 0.05
    paddedView_min = min_val - paddingView
    paddedView_max = max_val + paddingView
    
    # Configure sliders
    LowerPotentialSlider.config(from_=paddedSlide_min, to=paddedSlide_max, resolution=resolution)
    UpperPotentialSlider.config(from_=paddedSlide_min, to=paddedSlide_max, resolution=resolution)
    
    # Set default slider values to match the data range
    LowerLimit.set(paddedView_min)
    UpperLimit.set(paddedView_max)
    
    # Store these new defaults in the storage dictionary
    axis_limits_storage[selection] = {
        'from': paddedSlide_min, 'to': paddedSlide_max, 'res': resolution,
        'lower': paddedView_min, 'upper': paddedView_max
    }
def AnalyseBattery(Purpose):
    """Generates graphs or a spreadsheet from the globally stored processed_data."""
    if not processed_data:
        print("Please select and load a file first.")
        return

    # Unpack data for easier access
    DischargeCap = processed_data['DischargeCap']
    Efficiency = processed_data['Efficiency']
    ChargeExtract = processed_data['ChargeExtract']
    DischargeExtract = processed_data['DischargeExtract']
    
    CycleToExtract = [int(s) for s in re.findall(r'-?\d+\.?\d*', ListOfCycles.get())]
    CycleToExtract.sort()
    # Using theoretical capacity of Sulfur: 1675 mAh/g
    # This calculation seems to relate active mass to area, adjust if needed.
    Loading = ActiveMassMG.get() / float(ElectrodeArea.get())
    TitleText = f'Sulfur Mass = {ActiveMassMG.get()} mg, Loading = {Loading:.2f} mg/cm²'
    
   
    # --- GRAPHING LOGIC (Unchanged) ---
    if Purpose == "graph":
        selected_axis = AxisSelection.get()
        # *** KEY CHANGE: Retrieve limits directly from storage ***
        if selected_axis in axis_limits_storage:
            lower_lim = axis_limits_storage[selected_axis]['lower']
            upper_lim = axis_limits_storage[selected_axis]['upper']
        else: # Fallback just in case
            lower_lim, upper_lim = LowerLimit.get(), UpperLimit.get()
            
        # figure 1, cap fade and efficiency
        if PlotCapacityFade.get() == 1 or PlotEfficiency.get() == 1:
            fig1, ax1 = plt.subplots()
            ax1.set_xlabel('Cycle Number')
            ax1.grid(True, which='both', axis='both', alpha=0.2)
            
            if "Cycle Range" in axis_limits_storage:
                ax1.set_xlim(axis_limits_storage["Cycle Range"]['lower'], axis_limits_storage["Cycle Range"]['upper'])
            
            if PlotCapacityFade.get() == 1 and len(DischargeCap) > 0:
                ax1.set_ylabel('Capacity (mA h g⁻¹)', color='tab:red')
                ax1.plot(range(1, len(DischargeCap) + 1), DischargeCap, 'o', mfc='none', 
                         mec='tab:red', label='Discharge Capacity')
                ax1.tick_params(axis='y', labelcolor='tab:red')
            if "Capacity Range (Fade)" in axis_limits_storage:
                ax1.set_ylim(axis_limits_storage["Capacity Range (Fade)"]['lower'], axis_limits_storage["Capacity Range (Fade)"]['upper'])
 
            if PlotEfficiency.get() == 1 and len(Efficiency) > 0:
                ax2 = ax1.twinx()
                ax2.set_ylabel('Coulombic Efficiency (%)', color='tab:blue')
                ax2.plot(range(1, len(Efficiency) + 1), Efficiency, 'x',
                         mec='tab:blue', label='Efficiency')
                ax2.tick_params(axis='y', labelcolor='tab:blue')
                # Set y-axis for efficiency, e.g., from 80% to 110%
                if "Efficiency Range" in axis_limits_storage:
                    ax2.set_ylim(axis_limits_storage["Efficiency Range"]['lower'], axis_limits_storage["Efficiency Range"]['upper'])
            
            fig1.suptitle(FileName.get())
            fig1.tight_layout(rect=[0, 0.03, 1, 0.95])
            fig1.text(0.01, 0.01, TitleText, fontsize=8, ha='left', va='bottom')
            plt.show()
 
        # figure 2, cycling
        if PlotCycles.get() == 1:
            fig2, axl1 = plt.subplots()
            num_cycles = max(len(ChargeExtract), len(DischargeExtract))
            colors = cmap(np.linspace(0, 1, num_cycles))

            for l in range(num_cycles):
                cycle_num_label = l + 1
                if CycleToExtract and cycle_num_label not in CycleToExtract: continue
                
                if l < len(ChargeExtract):
                    if ChargeDischargeOrDischargeCharge.get() == 0:# dishcarge first
                        axl1.plot(ChargeExtract[l]['capacity'], ChargeExtract[l]['voltage'], color=colors[l])
                    else: # charge first
                        axl1.plot(ChargeExtract[l]['capacity'], ChargeExtract[l]['voltage'], color=colors[l], label=f'Cycle {cycle_num_label}')
                if l < len(DischargeExtract):
                    if ChargeDischargeOrDischargeCharge.get() == 0:# dishcarge first
                        axl1.plot(DischargeExtract[l]['capacity'], DischargeExtract[l]['voltage'], color=colors[l], label=f'Cycle {cycle_num_label}')
                    else: # charge first
                        axl1.plot(DischargeExtract[l]['capacity'], DischargeExtract[l]['voltage'], color=colors[l])
                    
            axl1.set_xlabel('Capacity (mA h g⁻¹)')
            axl1.set_ylabel('Potential (V vs. Li/Li⁺)')
            
            # *** KEY CHANGE: Apply limits for each axis independently ***
            if "Potential Range (Cycles)" in axis_limits_storage:
                axl1.set_ylim(axis_limits_storage["Potential Range (Cycles)"]['lower'], axis_limits_storage["Potential Range (Cycles)"]['upper'])
            if "Capacity Range (Cycles)" in axis_limits_storage:
                axl1.set_xlim(axis_limits_storage["Capacity Range (Cycles)"]['lower'], axis_limits_storage["Capacity Range (Cycles)"]['upper'])
            
            fig2.suptitle(FileName.get())
            fig2.text(0.01, 0.01, TitleText, fontsize=8, ha='left', va='bottom')
            axl1.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
            fig2.tight_layout(rect=[0, 0.03, 1, 0.95])
            # axl1.legend()

            plt.show()
 
        # Logic for embedding graphs in Tkinter window (unchanged)
        if DrawGraphsInHere.get() == 1:
            # show the graph
                # creating the Tkinter canvas
                # containing the Matplotlib figure
            CapCanvas = FigureCanvasTkAgg(fig1, root)
            CapCanvas.draw()
                # placing the canvas on the Tkinter window
            CapCanvas.get_tk_widget().grid(column=0,row=7,sticky = NW)
                # creating the Matplotlib toolbar
            CapToolbar = NavigationToolbar2Tk(CapCanvas, root, pack_toolbar=False)
            CapToolbar.update()
                # placing the toolbar on the Tkinter window
            CapToolbar.grid(column=0,row=8,sticky = NW)
            
                # creating the Tkinter canvas
                # containing the Matplotlib figure
            TraceCanvas = FigureCanvasTkAgg(fig2, root)
            TraceCanvas.draw()
                # placing the canvas on the Tkinter window
            TraceCanvas.get_tk_widget().grid(column=1,row=7,sticky = NW)
                # creating the Matplotlib toolbar
            TraceToolbar = NavigationToolbar2Tk(TraceCanvas, root, pack_toolbar=False)
            TraceToolbar.update()
                # placing the toolbar on the Tkinter window
            TraceToolbar.grid(column=1,row=8,sticky = NW)
 
    # --- SPREADSHEET EXPORT LOGIC (Revised) ---
    elif Purpose == "spreadsheet":
        print('Preparing data for spreadsheet...')
        SaveLocation = filedialog.askdirectory()
        if not SaveLocation:
            print("Save cancelled.")
            return
        file_name = FileName.get().replace('.mpr', '_processed.csv')
        full_path = os.path.join(SaveLocation, file_name)
 
        all_columns = []
        all_headers = []
        # Determine the number of cycles to process based on the longer list
        num_cycles = max(len(DischargeExtract), len(ChargeExtract))
 
        for i in range(num_cycles):
            cycle_num = CycleToExtract[i] if CycleToExtract and i < len(CycleToExtract) else i + 1
            # Get charge and discharge data for the current cycle, if they exist
            charge_cycle_data = ChargeExtract[i] if i < len(ChargeExtract) else None
            discharge_cycle_data = DischargeExtract[i] if i < len(DischargeExtract) else None
            # Define the order of processing based on user selection
            if ChargeDischargeOrDischargeCharge.get() == 0: # Discharge first
                process_order = [
                    ('Discharge', discharge_cycle_data),
                    ('Charge', charge_cycle_data)
                ]
            else: # Charge first
                process_order = [
                    ('Charge', charge_cycle_data),
                    ('Discharge', discharge_cycle_data)
                ]
 
            for step_name, data in process_order:
                if data is None: continue # Skip if this half-cycle doesn't exist
 
                if ExportTime.get() == 1:
                    all_columns.append(data['time'].reset_index(drop=True))
                    all_headers.append(f'Cycle {cycle_num} {step_name}: Time (s)')
                if ExportCap.get() == 1:
                    all_columns.append(data['capacity'].reset_index(drop=True))
                    all_headers.append(f'Cycle {cycle_num} {step_name}: Capacity (mAh/g)')
                if ExportCurrent.get() == 1:
                    all_columns.append(data['current'].reset_index(drop=True))
                    all_headers.append(f'Cycle {cycle_num} {step_name}: Current (mA)')
                if ExportVolt.get() == 1:
                    all_columns.append(data['voltage'].reset_index(drop=True))
                    all_headers.append(f'Cycle {cycle_num} {step_name}: Voltage (V)')
 
        # Create the final DataFrame
        if all_columns:
            output_df = pd.concat(all_columns, axis=1)
            output_df.columns = all_headers
 
            # Save to CSV
            output_df.to_csv(full_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
            print(f"CSV file saved successfully to: {full_path}")
        else:
            print("No data selected for export.")
        
root.title("KoferAnalyser v0.86")

# want label, which introduced the app
ttk.Label(frm, text="Battery time!").grid(column=0, row=0)
# want secttion of setting variables
    #first selecting folder
ttk.Label(frm, text="Pick your folder:").grid(column=0, row=1, sticky=W)
ttk.Entry(frm, textvariable=FolderName, width=60).grid(column=1, row=1, columnspan=2, sticky='ew')
ttk.Button(frm, text="Browse...", command=FindFolder).grid(column=3, row=1)

    # then file (list of mprs)
ttk.Label(frm, text="Pick your file:").grid(column=0, row=2, sticky=W)
CellList = Listbox(frm, width=60, height=5)
CellList.grid(column=1, row=2, columnspan=2, sticky='ew')
CellList.bind("<<ListboxSelect>>", SelectedFileFromFolder)
    # buttons for graph control
ChargeOrderBut1 = Radiobutton(frm, text="Discharge/Charge", variable=ChargeDischargeOrDischargeCharge, value=0)
ChargeOrderBut1.grid(column=3, row=2, sticky='sw')
ChargeOrderBut2 = Radiobutton(frm, text="Charge/Discharge", variable=ChargeDischargeOrDischargeCharge, value=1)
ChargeOrderBut2.grid(column=3, row=2, sticky='nw')
    # then find active mass, or let manually enter
ttk.Label(frm, text="Active Mass (mg):").grid(column=0, row=3, sticky=W)
ttk.Entry(frm, textvariable=ActiveMassMG).grid(column=1, row=3, sticky=W)
ChkBttnActiveMassFilename = Checkbutton(frm, variable=ExtractActiveMassFromFileName, text="from filename (e.g. 4p2)")
ChkBttnActiveMassFilename.select()
ChkBttnActiveMassFilename.grid(column=1, row=3, sticky=E, padx=5)
ChkBttnActiveMassCathMass = Checkbutton(frm, variable=ActiveMassIsCathodeMass, text="Is Cathode Mass?")
ChkBttnActiveMassCathMass.grid(column=2, row=3, sticky=W)
#Loading
ttk.Label(frm, text="Area (cm²):").grid(column=3, row=3, sticky=W, padx=5)
ElectroAreaEntry = ttk.Entry(frm, textvariable=ElectrodeArea); ElectroAreaEntry.delete(0, END)
ElectroAreaEntry.insert(-1, 1.5393804)
ElectroAreaEntry.grid(column=4, row=3, sticky=W)

    #OUTPUT THE DATA?
ttk.Label(frm, text="Data Export", font='Helvetica 10 bold').grid(column=0, row=4, columnspan=5, pady=(10,0))
ttk.Label(frm, text="What to output?").grid(column=0, row=5)
ChkBttnTime = Checkbutton(frm, variable = ExportTime, text = "Time?")
ChkBttnTime.select()
ChkBttnTime.grid(column=1, row=5, sticky = W)
ChkBttnCap = Checkbutton(frm, variable = ExportCap, text = "Capacity?")
ChkBttnCap.select()
ChkBttnCap.grid(column=1, row=5,sticky = E)
ChkBttnVolt = Checkbutton(frm, variable = ExportVolt, text = "Voltage?")
ChkBttnVolt.select()
ChkBttnVolt.grid(column=2, row=5)
ChkBttnCurrent = Checkbutton(frm, variable = ExportCurrent, text = "Current?")
ChkBttnCurrent.select()
ChkBttnCurrent.grid(column=3, row=5)
ChkBttnEff = Checkbutton(frm, variable = ExportEfficiency, text = "Efficiency?")
ChkBttnEff.select()
ChkBttnEff.grid(column=4, row=5)
ttk.Button(frm, text="Output as Spreadsheet", command = lambda: AnalyseBattery("spreadsheet")).grid(column=2, row=6)

ttk.Label(frm, text="Graphing Options", font='Helvetica 10 bold').grid(column=0, row=7, columnspan=5, pady=(10,0))
    # then set cycles to extract
ttk.Label(frm, text="Specific cycles:").grid(column=0, row=8, sticky=W)
ttk.Entry(frm, textvariable=ListOfCycles).grid(column=1, row=8, sticky='ew', columnspan=2)
    #   which graphs to make
ChkBttnPltCycles = Checkbutton(frm, variable=PlotCycles, text='Plot Cycles')
ChkBttnPltCycles.select()
ChkBttnPltCycles.grid(column=0, row=9, sticky=W)
ChkBttnPltCapFad = Checkbutton(frm, variable=PlotCapacityFade, text='Plot Capacity Fade')
ChkBttnPltCapFad.select()
ChkBttnPltCapFad.grid(column=1, row=9, sticky=W)
ChkBttnPlotEff = Checkbutton(frm, variable=PlotEfficiency, text='Plot Efficiency')
ChkBttnPlotEff.select()
ChkBttnPlotEff.grid(column=2, row=9, sticky=W)
    # also do we wanna draw the graphs in here??
ChkBttnDrawGraph = Checkbutton(frm,variable = DrawGraphsInHere, text = "Draw graph in this window?")
ChkBttnDrawGraph.grid(column=3, row=9)
    # button to copy figs
# ttk.Button(frm, text="Copy Left Fig", command=add_figure_to_clipboard(1)).grid(column=2, row=5)
# ttk.Button(frm, text="Copy Right Fig", command=add_figure_to_clipboard(2)).grid(column=3, row=5)

# --- AXIS CONTROL SECTION ---
ttk.Label(frm, text="Axis Control", font='Helvetica 10 bold').grid(column=0, row=10, columnspan=5, pady=(10,0), sticky=W)
ttk.Label(frm, text="Axis to Control:").grid(column=0, row=11, sticky=W)
axis_options = ["Potential Range (Cycles)", "Capacity Range (Cycles)", "Capacity Range (Fade)", "Efficiency Range", "Cycle Range"]
AxisComboBox = ttk.Combobox(frm, textvariable=AxisSelection, values=axis_options, state="readonly")
AxisComboBox.grid(column=1, row=11, sticky='ew', columnspan=2)
AxisComboBox.set("Potential Range (Cycles)")
AxisComboBox.bind("<<ComboboxSelected>>", update_slider_config)
ttk.Label(frm, text="Lower Limit:").grid(column=0, row=12, sticky=W)
LowerPotentialSlider = Scale(frm, orient=HORIZONTAL, variable=LowerLimit, command=save_current_slider_values)
LowerPotentialSlider.grid(column=1, row=12, sticky='ew', columnspan=2)
ttk.Label(frm, text="Upper Limit:").grid(column=0, row=13, sticky=W)
UpperPotentialSlider = Scale(frm, orient=HORIZONTAL, variable=UpperLimit, command=save_current_slider_values)
UpperPotentialSlider.grid(column=1, row=13, sticky='ew', columnspan=2)

# Action Buttons
ttk.Button(frm, text="Make Graphs!", command=lambda: AnalyseBattery("graph")).grid(column=0, row=14, pady=(10,0))
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=14, sticky=W, pady=(10,0))

    # Initialize slider configuration on startup
update_slider_config()

# run the app
root.mainloop()

