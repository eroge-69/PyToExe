# -------------------------------------------------------------------------
# Probe Identifier GUI Script
# The purpose of this script is to get the failing information for down Xiu
# v0.0.1 - initial version share to VF
# v1.0.0 - add bin99, EMR bin25 and legend on GUI
# v1.0.1 - add bin46/48 for JPANA/EMANA
# v1.0.3 - correction for bin11 fail_channel_list =[s[-5:] for s in fail_channel_list]
# v1.0.4 - add bin80, bin19, bin75 & bin51 for RPL feature
# v1.0.5 - Correction on Bin19
# v1.0.6 - Correction on Bin46/48 TGL/ADL PCH
# v1.0.7 - add bin32 for RPL
# v1.0.8 - Correction for MTL (TH display correction)
# v1.0.9
# v1.0.10 - J-Con display
# v1.0.11 - Correction on Bin10
# v1.0.12 - Include screening feature for SPR XCC FB817-820 solder joint issue
# v1.0.13 - Adding J-Con features and ADL PCH bin299
# v1.0.14 - Fixing NaN bugs
# v1.0.15 - Include screening feature for SPR XCC Bin88 & Bin99 solder joint issue
# v1.0.16 - Correction on bin48/bin46 SPR/EMR and add bin4 for SPR MCC
# v1.0.17 - Correction on bin8 by removing 'PARALLEL' in line
# v1.0.18 - Add bin42 for EMR XCC
# v1.0.18WIP - Add bin11/25 for MTL SOC M
# v1.0.19 - Add token for bin 99 'Type:BurstAlreadyRunning'
# v1.0.19BugFix - bin25 for MTL
# v1.0.20 - Correction for bin4
# v1.0.21 - Correction for bin8 ASSERTF
# v1.0.22 - Correction for bin42, add token FUS
# v1.0.23 - Add new tab for EZA and Config generator
# v1.0.24 - Hard code bin25 EMR XCC failing pins to MPE/TP team given pins
# v1.0.25 - Remove bin25 mpe/TP team failing pins
# v1.0.26 - Added tester issue flag for MTL68 bin99 and readded bin25 MPE pins for EMR
# v1.0.27 - Add NPI for EZA
# v2.1 - add bin 4819 for JSP PCH and Bin25 MTL SOC
# v2.2 - Correction on EZA part
# v2.3.1 - CORRECTION ON BIN99 FOR mtl soc    FROM "Type:DPSAssertFail" TO "DPSAs" and bin25 and 11 in MTL SOC
# v2.3.2 - optimize MTL soc bin25
# v2.3.3 - enable tester issue flag for MTL SOC M Bin99 "TYPE:DPSBurstAlreadyRunning"
# v2.3.4 - rename tester issue flag for general MTL
# v2.3.5 - SPR MCC bin25 correction
# v2.3.6 - add message box to "VI and UTP" for FB108-408 JSP PCH
# v2.3.7 - add message box to dispo for TPANA (LC14 and LC15)
# v2.3.8 - add message box to dispo for JPANA (FB108 - FB408 & FB109-409)
# v2.3.8 - add message box to 4 consecutive for JPANA (FB108 - FB408 & FB109-409)
# v2.3.11 - add bin88 on MTL soc
# v2.3.11 - add bin88 on MTL soc
# v2.4 - add bin46 GRN_IO
# v2.4.2 - add bin88 and 25 for LNL
# v2.4.3 - add bin77 for LNL SOC M
# v2.4.4 - consolidate all binning to same binning family, add bin25 and bin88 for soc S


# from sklearn import  linear_model
# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import  PolynomialFeatures
# from sklearn.ensemble import IsolationForest
import csv
import gzip
import os
import re
import shutil
import time
from datetime import datetime
# from sympy import *
from functools import lru_cache
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.pyplot import cm
# from sympy.solvers.ode.subscheck import checkodesol, checksysodesol
from matplotlib.pyplot import figure, show
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from PIL import Image, ImageTk
import matplotlib.cm as cm

# config_path = r'\\s33file1.kssm.intel.com\pcm\recipe\Common\PCM_FailPin_Python_config'

row_dict = {'3_dvtststdt': '', '3_dvtsteddt': '', '3_curftbin': '',
            '3_curitbin': '', '3_tiuid': '', '3_carrierxloc': '',
            '3_carrieryloc': '', '3_chuckid': '',
            '3_trslt': '', '3_siteid': '', '3_prttesterid': '', '3_virtualtested': '',
            '3_partialwafid': '', '3_cellid': '', 'fail_channel': '',
            '3_curtbin': '', '3_curibin': '', '3_curfbin': '',
            '6_lotid_': '', '6_prgnm_': '', '5_lcode': '', '4_sysid_': '', '4_begindt_': '', '3_comnt_SDSFB': '', '2_composite_8040': '', '2_composite_9004': '', '2_composite_9068': '',
            '3_comnt_SDTFB': '',}

item_gp = list(row_dict.keys())
channel_standardlize = {2: '00000', 3: '0000', 4: '000', 5: '00', 6: '0', 7: '', }
bin_list = [ 'Bin4 SPR MCC','Bin8/80', 'Bin9', 'Bin10', 'Bin11','Bin11 MTL SOC M', 'Bin13', 'Bin15','Bin19',
             'Bin25 FM4/GDR/JSPPCH','Bin25 LNL SOC M','Bin25 MTL SOC','Bin25 SPR/EMR','Bin28 MTL SOC M','Bin30',
             'Bin32 RPL','Bin39 JSP PCH','Bin39/40/41/42/46/48/74 MTL SOCM','Bin42','Bin46/48 SPR/EMR', 'Bin46 GNR_IO',
             'Bin46 JSP/EBG','Bin46/48 TGL/ADL/JSP PCH/EBG','Bin51 RPL','Bin54 SPR MCC','Bin75 RPL & JSP CPU',
             'Bin77 LNL SOC M', 'Bin88','Bin97','Bin99', 'All Bin']
#bin_list = [ 'Bin4 SPR MCC','Bin8/80','Bin9','Bin10','Bin11','Bin11 MTL SOC M','Bin13','Bin15','Bin19',
#             'Bin25 FM4/GDR/JSPPCH','Bin25 MTL SOC','Bin25 SPR/EMR','Bin30','Bin32 RPL','Bin39 JSP PCH',
#             'Bin39/40/41/42/46/48/74 MTL SOCM','Bin42','Bin46/48 SPR/EMR','Bin46 GNR_IO',
#             'Bin46/48 TGL/ADL/JSP PCH/EBG','Bin51 RPL','Bin54 SPR MCC','Bin54 RPL24C/ADL881','Bin60 FMx',
#             'Bin75 RPL & JSP CPU','Bin88','Bin97','Bin99','All Bin']
pin = {'PIN': '', 'bin': ''}


class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None

    def zoom_factory(self, ax, base_scale=2.):
        def zoom(event):
            cur_xlim, cur_ylim = ax.get_xlim(), ax.get_ylim()
            xdata, ydata = event.xdata, event.ydata

            scale_factor = 1 / base_scale if event.button == 'up' else base_scale if event.button == 'down' else 1

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * (rely)])
            ax.figure.canvas.draw()

        fig = ax.get_figure()
        fig.canvas.mpl_connect('scroll_event', zoom)
        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax: return
            self.cur_xlim, self.cur_ylim = ax.get_xlim(), ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None or event.inaxes != ax: return
            dx, dy = event.xdata - self.xpress, event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)
            ax.figure.canvas.draw()

        fig = ax.get_figure()
        fig.canvas.mpl_connect('button_press_event', onPress)
        fig.canvas.mpl_connect('button_release_event', onRelease)
        fig.canvas.mpl_connect('motion_notify_event', onMotion)
        return onMotion


def get_rows(file_in):
    row = {'tag_ib': '', 'data': [], 'flag': '', 'UltraBinner': ''}
    flag = 0
    Ultrabinner_flag = False
    for i in file_in:
        line = i.strip()
        if '3_lsep' in line: row = {'tag_ib': '', 'data': [], 'flag': '', 'UltraBinner': ''}
        row['data'].append(line)
        if Ultrabinner_flag:
            row['UltraBinner'] = line.split("|")[1].rsplit('_', 1)[0]
            Ultrabinner_flag = False
        if 'UltraBinner_FailingInfo' in line or 'Ultrabinner_CheckPoint_FailingInfo' in line: Ultrabinner_flag= True
        if '3_curtbin' in line or '3_curitbin' in line:  # end of die
            flag = 1
            row['tag_ib'] = 'Bin' + line.split('_')[-1]
            row['data'].append(line)
            if '3_curtbin' in line: row['flag'] = 'tbin'
            elif '3_curitbin' in line: row['flag'] = 'itbin'
            yield row
        elif '3_curibin' in line and flag == 0:
            row['tag_ib'] = 'Bin' + line.split('_')[-1]
            row['data'].append(line)
            row['flag'] = 'ibin'
            yield row


def get_file_name(file_in):
    lot, sdx, t_start, tprogram, operation = '', '', '', '', ''

    for i in file_in:
        line = i.strip()
        value = line.split('_')[-1].strip()
        if '6_lotid_' in line: lot = value
        if '6_prgnm_' in line: tprogram = value
        if '5_lcode' in line: operation = value
        if '4_sysid_' in line: sdx = value
        if '4_begindt_' in line:
            t_start = value
            break
    return sdx, lot, tprogram, operation, t_start


def get_xiu_name(file_in):
    flag, xiu = '', ''
    correctxiu = False
    for i in file_in:
        line = i.strip()
        value = line.split('_')[-1].strip()
        if '3_tiuid_' in line and len(value) > 7:
            xiu = value
            correctxiu = True
        if '3_curtbin' in line and correctxiu:
            flag = 'tbin'
            break
        if '3_curitbin' in line and correctxiu:
            flag = 'itbin'
            break
        if '3_curibin' in line and correctxiu:
            flag = 'ibin'
            break
    return xiu, flag


def Fail_Channel_Lookup(fail_channel_list, df1):
    probeID_list = '[' + ','.join(pd.DataFrame([s[-5:] for s in fail_channel_list], columns=['HDMT PIN#'])
                                  .astype({"HDMT PIN#": int}, errors='ignore')
                                  .merge(df1, how="left")
                                  .astype({"PIN_NUMBER": str})
                                  ['PIN_NUMBER'].values.tolist()) + ']'
    return probeID_list




def Fail_Channel_Lookup2(fail_channel_list, df1):
    fc = pd.DataFrame(fail_channel_list, columns=['PIN_NAME'])
    # fc = fc.astype({"PIN_NAME": int},errors = 'ignore')
    #print(fc)
    print(fc.to_string())
    rhs = (fc.PIN_NAME
               .apply(lambda x: df1[df1.PIN_NAME.str.find(x).ge(0)]['PIN_NUMBER'])
               .bfill(axis=1)
               .iloc[:, 0])
    print(rhs.to_string())
    probeID_list = rhs.values.tolist()
    #print(probeID_list.to_string())

    # probeID_list = ' '.join(map(str, probeID_list))

    return probeID_list

def Fail_Channel_Lookup3(fail_channel_list, df1,th):
    # Create a DataFrame from the fail_channel_list
    fc = pd.DataFrame(fail_channel_list, columns=['PIN_NAME'])
    rhs = df1[df1['PIN_NAME'].apply(lambda x: any(pin in x for pin in fc['PIN_NAME']))]
    # Filter rows where the first column starts with 'D' + th
    probeID_list = rhs[rhs['PIN_NUMBER'].str.startswith('D' + th)]['PIN_NUMBER'].tolist()
    print(probeID_list)
    return probeID_list


def check_limits(csv_path, token, value):
    # Load the CSV data into a DataFrame
    data = pd.read_csv(csv_path)

    # Look up the token in the DataFrame
    row = data[data['Token'].str.contains(token, case=False, na=False)]

    # Check if the token was found and if the value is within limits
    if not row.empty:
        limit_low = row['LimitLow'].values[0]
        limit_high = row['LimitHigh'].values[0]
        rail = row['Rail'].values[0]
        
        # Check if the value is within the specified limits
        if limit_low <= value <= limit_high:
            return "Pass", None
        else:
            return "Fail", rail
    else:
        return "Token not found", None

def check_port_octet(csv_path, token):
    # Load the CSV data into a DataFrame
    data = pd.read_csv(csv_path)
    print(token)
    # Look up the token in the DataFrame
    result = data[data['Fail Name'].str.contains(token, case=False, na=False)]

    copied_df = result.copy()

    copied_df['Pad #'] = copied_df['Pad #'].astype(int)

    pinfail = copied_df['Pad #'].tolist()

    return pinfail

def check_fdpmv(csv_path, token,TH):
    # Load the CSV data into a DataFrame
    data = pd.read_csv(csv_path)
    print(token)
    # Look up the token in the DataFrame
    result = data[data['Field Vector Address'].str.contains(token, case=False, na=False)]

    copied_df = result.copy()

    pinfail = copied_df['Name'].tolist()

    return pinfail



    # Check if the token was found and if the value is within limits
    
        
        
    #     # Check if the value is within the specified limits
    #     if limit_low <= value <= limit_high:
    #         return "Pass", None
    #     else:
    #         return "Fail", rail
    # else:
    #     return "Token not found", None

def callbackbin(binning):
    flagbin = str(binning.get())
    return flagbin


def callbackProd(Product):
    flagProd = str(Product.get())
    
    return flagProd

def on_enter_pressed(event):
    for item in tv1.get_children(): tv1.delete(item)

    text_value = inputtxt1.get("1.0", "end-1c")
    #variables_to_check = re.split(r',\s*|\s+', text_value)
    variables_to_check = re.split(r'[,\s;]+', text_value)
    flagProd = callbackProd(Product)

    # Define the filename 
    subfolder_name = "SOC"  # Add the name of your subfolder here
    filename = flagProd + ".soc"

    # Combine the directory, folder, subfolder, and filename to get the full path
    
    Soc_path = os.path.join(config_path, subfolder_name, filename)

    df = pd.read_csv(config_path + r'\channel_' + flagProd + '.csv')
    df1 = df.drop(['PIN_X', 'PIN_Y'], axis=1).drop_duplicates()

    with open(Soc_path, 'r') as file:
        # Read each line in the file
        
        HDMT = []
        probeID = []
        Flag_DUT = FALSE
        for line in file:
            # Split the line by whitespace
            #token = re.split(r'[,\s]+', line.strip())
            tokens = line.strip().split()
            
            # Check if there are any tokens in the line
            
            if tokens:
                # Iterate over each variable in variables_to_check
                for var in variables_to_check:
                    # Check if the first token of the line matches the variable
                    if tokens[0] == var:
                        # Extract and print the value
                        if tokens[1] == '[U]':
                            value = tokens[2].rstrip(';')
                        else:
                            value = tokens[1].rstrip(';')

                        integer_string = value.replace(".", "")

                        HDMT.append(integer_string)

                        # Desired length of the resulting string
                        desired_length = 7

                        # Prepend "0" characters to the left until the string reaches the desired length
                        result_string = integer_string.zfill(desired_length)

                        # Convert the integer to a list containing a single element
                        result_list = [result_string]

                        probeID_list = Fail_Channel_Lookup(result_list, df1)

                        probeID_list_without_brackets = probeID_list[1:-1]
                        probeID.append(probeID_list_without_brackets)

                        if "D2_" in probeID_list:
                            DUT = 2
                            Flag_DUT = True
                        else:
                            DUT = 1
                        
                        # Insert into the Treeview
                        tv1.insert(parent='', index='end', text='', values=(var, value, probeID_list, DUT))
                        
    inputtxt1.delete('1.0', 'end')
    PlotJcon_tab4(HDMT)

    df1 = df.assign(PIN_INDICATOR=1, PIN_SIZE=20)
    
    if not Flag_DUT:
        df1['TH'] = 1
    else:
        df1.loc[df1['NET_NAME'].str.startswith('D1'), 'TH'] = 1
        df1.loc[df1['NET_NAME'].str.startswith('D2'), 'TH'] = 2

    for pin in set(probeID):
        print(pin)
        df1.loc[df1["PIN_NUMBER"] == pin, "PIN_INDICATOR"] = pin
    
    
    
    Plots_tab4(df1)
    

def PlotJcon(HDMT):
    global outputJconmain
    if outputJconmain:
        tab1.winfo_children()[-2].destroy()
        tab1.winfo_children()[-1].destroy()
    outputJconmain = None
    Jconlookup = pd.read_csv(config_path + r'\Jcon_lookup.csv')
    if HDMT == []:
        df2 = Jconlookup
        df2['Failed'] = ""
    else:

        
        FailHDMT = pd.DataFrame(HDMT, columns=['HDMT PIN#'])
        
        # Remove leading and trailing whitespaces from the column
        FailHDMT['HDMT PIN#'] = FailHDMT['HDMT PIN#'].str.strip()

        # Filter out rows with empty strings or whitespace
        FailHDMT = FailHDMT[FailHDMT['HDMT PIN#'].str.len() > 0]

        # Convert the column to integer type
        FailHDMT['HDMT PIN#'] = FailHDMT['HDMT PIN#'].astype(int)

        FailHDMT['Failed'] = "Y"
        FailHDMT = FailHDMT.drop_duplicates()
        df2 = pd.merge(Jconlookup.astype({"row_number": int, "column_number": int, "Slot": int}),
                       FailHDMT.astype({"HDMT PIN#": int}), how="left")
    outputJconmain = ttk.Frame(tab1)
    outputJconmain.pack(ipadx=5, ipady=5)
    for slot, group in df2.groupby('Slot'):
        desc_text = group.iloc[0]["name"]
        output_jcon = tk.LabelFrame(outputJconmain, text=desc_text)
        output_jcon.grid(row=0, column=slot, sticky="w")

        for _, item in group.iterrows():
            color = "red" if item["Failed"] == "Y" else "white"
            cell = tk.Label(output_jcon, text="",font=("Arial",1), bg=color, relief="ridge", borderwidth=1)
            cell.grid(row=item["row_number"] + 1, column=item["column_number"] + 1, sticky="w")

def PlotJcon_tab4(HDMT):
    global outputJconmain
    if outputJconmain:
        tab4.winfo_children()[-2].destroy()
        tab4.winfo_children()[-1].destroy()
    outputJconmain = None
    Jconlookup = pd.read_csv(config_path + r'\Jcon_lookup.csv')
    if HDMT == []:
        df2 = Jconlookup
        df2['Failed'] = ""
    else:

        
        FailHDMT = pd.DataFrame(HDMT, columns=['HDMT PIN#'])
        
        # Remove leading and trailing whitespaces from the column
        FailHDMT['HDMT PIN#'] = FailHDMT['HDMT PIN#'].str.strip()

        # Filter out rows with empty strings or whitespace
        FailHDMT = FailHDMT[FailHDMT['HDMT PIN#'].str.len() > 0]

        # Convert the column to integer type
        FailHDMT['HDMT PIN#'] = FailHDMT['HDMT PIN#'].astype(int)

        FailHDMT['Failed'] = "Y"
        FailHDMT = FailHDMT.drop_duplicates()
        df2 = pd.merge(Jconlookup.astype({"row_number": int, "column_number": int, "Slot": int}),
                       FailHDMT.astype({"HDMT PIN#": int}), how="left")
    outputJconmain = ttk.Frame(tab4)
    outputJconmain.pack(ipadx=5, ipady=5)
    for slot, group in df2.groupby('Slot'):
        desc_text = group.iloc[0]["name"]
        output_jcon = tk.LabelFrame(outputJconmain, text=desc_text)
        output_jcon.grid(row=0, column=slot, sticky="w")

        for _, item in group.iterrows():
            color = "red" if item["Failed"] == "Y" else "white"
            cell = tk.Label(output_jcon, text="",font=("Arial",1), bg=color, relief="ridge", borderwidth=1)
            cell.grid(row=item["row_number"] + 1, column=item["column_number"] + 1, sticky="w")


def Plots(df):
    global outputProbeMap
    outputProbeMap = None

    df2 = df[(df.PIN_INDICATOR == 1) & (df.TH == 1)]
    df3 = df[(df.PIN_INDICATOR != 1) & (df.TH == 1)]
    df4 = df[(df.PIN_INDICATOR == 1) & (df.TH == 2)]
    df5 = df[(df.PIN_INDICATOR != 1) & (df.TH == 2)]

    if 2 in df['TH'].unique():
        fig, axs = plt.subplots(1, 2, figsize=(8, 30))
        plot_scatter(axs[0], df2, df3)
        plot_scatter(axs[1], df4, df5)
        set_plot_properties(axs[0], 'Failing Pin Array Mapping TH1')
        set_plot_properties(axs[1], 'Failing Pin Array Mapping TH2')
    else:
        fig, axs = plt.subplots(figsize=(8, 30))
        plot_single_scatter(axs, df2, df3)
        set_plot_properties(axs, 'Failing Pin Array Mapping')

    outputProbeMap = FigureCanvasTkAgg(fig, tab1)
    outputProbeMap.get_tk_widget().pack(fill="none")

def Plots_tab4(df):
    global outputProbeMap
    outputProbeMap = None

    df2 = df[(df.PIN_INDICATOR == 1) & (df.TH == 1)]
    df3 = df[(df.PIN_INDICATOR != 1) & (df.TH == 1)]
    df4 = df[(df.PIN_INDICATOR == 1) & (df.TH == 2)]
    df5 = df[(df.PIN_INDICATOR != 1) & (df.TH == 2)]

    if 2 in df['TH'].unique():
        fig, axs = plt.subplots(1, 2, figsize=(8, 30))
        plot_scatter(axs[0], df2, df3)
        plot_scatter(axs[1], df4, df5)
        set_plot_properties(axs[0], 'Failing Pin Array Mapping TH1')
        set_plot_properties(axs[1], 'Failing Pin Array Mapping TH2')
    else:
        fig, axs = plt.subplots(figsize=(8, 30))
        plot_single_scatter(axs, df2, df3)
        set_plot_properties(axs, 'Failing Pin Array Mapping')

    outputProbeMap = FigureCanvasTkAgg(fig, tab4)
    outputProbeMap.get_tk_widget().pack(fill="none")


def plot_scatter(ax, df1, df2):
    PIN_X1 = np.array(df1[['PIN_X']])
    PIN_Y1 = np.array(df1[['PIN_Y']])
    ax.scatter(PIN_X1, PIN_Y1, color='grey', s=0.2)

    fail_item1 = df2['PIN_INDICATOR'].unique()
    color_map = cm.rainbow(np.linspace(0, 1, len(fail_item1)))

    for index, fail_item in enumerate(fail_item1):
        temp_df = df2[df2.PIN_INDICATOR == fail_item]
        PIN_X_list = np.array(temp_df[['PIN_X']])
        PIN_Y_list = np.array(temp_df[['PIN_Y']])
        c = color_map[index]
        ax.scatter(PIN_X_list, PIN_Y_list, color=c, s=10, label=fail_item)

    ax.axis('equal')
    ax.legend(loc='upper left')




def plot_single_scatter(ax, df2, df3):
    PIN_X = np.array(df2[['PIN_X']])
    PIN_Y = np.array(df2[['PIN_Y']])
    ax.scatter(PIN_X, PIN_Y, color='grey', s=0.2)

    fail_item = df3['PIN_INDICATOR'].unique()
    color_map = cm.rainbow(np.linspace(0, 1, len(fail_item)))
    for index, item in enumerate(fail_item):
        temp_df = df3[df3.PIN_INDICATOR == item]
        PIN_X_list = np.array(temp_df[['PIN_X']])
        PIN_Y_list = np.array(temp_df[['PIN_Y']])
        c = color_map[index]
        ax.scatter(PIN_X_list, PIN_Y_list, color=c, s=10, label=item)

    ax.axis('equal')
    ax.legend(loc='upper left')


def set_plot_properties(ax, title):
    scale = 1.5
    zp = ZoomPan()
    figZoom = zp.zoom_factory(ax, base_scale=scale)
    figPan = zp.pan_factory(ax)
    ax.set_title(title)


def attach_file():

    file_name = file_name_entry.get()
    if file_name and file_name != 'Insert Prod Name':
        file_path = filedialog.askopenfilename()
        if file_path:
            
            
            if file_path.lower().endswith('.soc'):

                # Define the filename of your image
                folder_name = "Config"   # Add the name of your folder here
                subfolder_name = "SOC"  # Add the name of your subfolder here

                # Combine the directory, folder, subfolder, and filename to get the full path
                #destination_folder = os.path.join(file_directory, folder_name, subfolder_name)
                destination_path = os.path.join(config_path, subfolder_name, file_name + '.soc')


                if not os.path.exists(destination_path):
                    try:
                        shutil.copy(file_path, destination_path)
                        save_file_names_to_csv(file_name)
                        showinfo(title='Message', message=f"NPI for {file_name}'s EZA Completed!!")
                        file_name_entry.delete(0, tk.END)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        showinfo(title='Message', message='An error occurred')

                else:
                    messagebox.showinfo(title='Error', message='File already exists. Please choose a different name or remove the existing file.')

            else:
                showinfo(title='Message', message='Please input .soc file!!')
    else:
        showinfo(title='Message', message='Please enter file name!!')
           

def save_file_names_to_csv(file_name):
    print(file_name)

   

    # Define the filename of your image
    filenames = "Products.csv"
    foldername = "SOC"

    # Combine the directory and filename to get the full path
    file_path1 = os.path.join(config_path, foldername, filenames)

    
    with open(file_path1, 'a', newline='') as file:  # Open the file in append mode
        writer = csv.writer(file)
        writer.writerow([file_name])  # Append the list of file names as a new row


    update_dropdown_menu(file_path1)



def update_dropdown_menu(file_path):
    # Read the updated CSV file into a DataFrame
    Product_file = pd.read_csv(file_path)

    # Convert the DataFrame column to a list
    Product_list = Product_file['Products'].tolist()

    # Clear the current options in the dropdown menu
    bin_menu1['menu'].delete(0, 'end')

    # Add the new product list to the dropdown menu
    for product in Product_list:
        bin_menu1['menu'].add_command(label=product, command=lambda value=product: Product.set(value))

    # Optionally, set the default value of the dropdown to the first product or a placeholder
    Product.set('Select Product')

    

        
def find_consecutive(dataset):
    count = 1
    prev_num = None
    for num in dataset:
        if num == prev_num:
            count += 1
            if count == 4 and num in ['108', '208', '308', '408','109', '209', '309', '409']:
                print(f"Consecutive {num}")
                return True
        else:
            count = 1
            prev_num = num
    return False

    
def main():
    for item in tv.get_children(): tv.delete(item)
    flagBin = callbackbin(binning)
    # Create a new directory because it does not exist
    LotTray = inputtxt.get("1.0", "end-1c")
    lot = LotTray[0:16]
    tray = LotTray[17:20]
    try:
        abspath = os.path.abspath(os.path.dirname(sys.executable))

        with open(os.path.join(abspath, "Config\site_path.txt")) as site_file:
            site_path = site_file.readline()
    except:
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        with open(dname + "\\Config\\site_path.txt") as site_file:
            site_path = site_file.readline()
    found = False
    for folder in ['prod', 'eng']:      
        n = 1000
        while n < 1300:

            newpath = os.path.join(site_path, str(n), folder, lot, 'Ituff', tray)
            if os.path.exists(newpath):
                fl_path = filedialog.askopenfilename(initialdir=newpath)
                found = True 
                break
            n += 1
        if found:
            break

    if not os.path.exists(newpath): fl_path = filedialog.askopenfilename()
    fl_name = os.path.basename(fl_path)
    temp_file = os.path.join(temp_path, fl_name)
    #temp_file = temp_path + fl_name

    start_time = time.time()
    print('					  ')
    print('					  ')
    print(str(flagBin) + ' fail channel look up')
    print('........Loading...........Please wait')
    print('					  ')
    file_open = shutil.copy(fl_path, temp_file)
    # file_open.close()
    copy_time = time.time()

    if temp_file.endswith('.ITF'): file_in = open(temp_file)
    if temp_file.endswith('.gz') or temp_file.endswith('.GZ'): file_in = gzip.open(temp_file, 'rt')
    xiu, flag = get_xiu_name(file_in)
    xiu_productname = xiu[0:4] + xiu[6]
    df = pd.read_csv(config_path + r'\channel_' + xiu_productname + '.csv')
    df1 = df.drop(['PIN_X', 'PIN_Y'], axis=1).drop_duplicates()
    # reset 1 time reading
    file_in.close()
    if temp_file.endswith('.ITF'): file_in = open(temp_file)
    if temp_file.endswith('.gz') or temp_file.endswith('.GZ'): file_in = gzip.open(temp_file, 'rt')
    sdx, lot, tprogram, operation, t_start = get_file_name(file_in)
    # end reset reading
    if flag == 'tbin':
        print('|   XIU   |', '| SDX|', '| SDC |', '| HDS |', '|Oper|', '|  lot  |', '|Tray|', '|tbin|', '|SDSFB|',
              '|SDTFB|', '|TH|', '|NetName|')
    else:
        print('|   XIU   |', '| SDX|', '| SDC |', '| HDS |', '|Oper|', '|  lot  |', '|Tray|', '|itbin|', '|ftbin|',
              '|TH|', '|NetName|')
    HDMT, Pin, faildie = [], [], 0
    curit_list = []
    for block in get_rows(file_in):
        vcc_flag, hw_flag = False, False
        count = 1
        fail_channel, fail_channel_list, probeID_list = '', '', ''
        row = row_dict.copy()
        ib = block.get('tag_ib')
        item = list(row.keys())


        Binflag = False
        # Bin8 Start
        rows = []
        if flagBin == 'Bin8/80':
            if ib in ['Bin8', 'Bin208', 'Bin80', 'Bin280']:
                datasets = block.get('data')
                for line in datasets:
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                    if 'VCC' in line: vcc_flag = True
                    if 'faildata_' in line and vcc_flag:
                        fail_channel_list = re.search(r'\d+', value, re.I).group(0).split(',')
                    if '2_tname_HWALARM' in line and 'TYPE:DPS' in line.upper() and not 'Type:DPSAs' in line and not 'Type:DPSDataNotFound2' in line:
                        hw_flag = True
                        
                    if '2_strgval_Module' in line and hw_flag:
                        hw_flag = False
                        fail_channel_list = re.search(r'\d+', value, re.I).group(0).split(',')
                        

                if fail_channel_list != '':probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)
                binmodeflag = block.get('flag')
                curitbin_line = row.get(f'3_cur{binmodeflag}')
                rows.append(row)
                if binmodeflag in ['itbin', 'tbin']:
                    curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                elif binmodeflag == 'ibin':
                    curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'), fail_channel_list, probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
                if row.get('3_tiuid').startswith('TPAN') and "5016" in fail_channel_list:
                    messagebox.showinfo(f"Disposition for {row.get('3_tiuid')}","SWAP RELAY K5A & K5B AND TWEAK ALL D1_LC11 AND SURROUNDING GND PROBES WITHIN THE OVERLAY BOX AND PROCEED WITH NORMAL POR")
                elif row.get('3_tiuid').startswith('TPAN') and "5024" in fail_channel_list:
                    messagebox.showinfo(f"Disposition for {row.get('3_tiuid')}","SWAP RELAY K5A & K5B AND TWEAK ALL D2_LC11 AND SURROUNDING GND PROBES WITHIN THE OVERLAY BOX AND PROCEED WITH NORMAL POR")
                elif row.get('3_tiuid').startswith('TPAN') and "5019" in fail_channel_list:
                    messagebox.showinfo(f"Disposition for {row.get('3_tiuid')}","SWAP RELAY K6A & K6B AND TWEAK ALL D1_LC12 AND SURROUNDING GND PROBES WITHIN THE OVERLAY BOX AND PROCEED WITH NORMAL POR")
                elif row.get('3_tiuid').startswith('TPAN') and "5025" in fail_channel_list:
                    messagebox.showinfo(f"Disposition for {row.get('3_tiuid')}","SWAP RELAY K6A & K6B AND TWEAK ALL D2_LC12 AND SURROUNDING GND PROBES WITHIN THE OVERLAY BOX AND PROCEED WITH NORMAL POR")
                
                faildie += 1
                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)
                if curibin_line in ['817', '818', '820'] and row.get('3_tiuid').startswith(('SI', 'SA')):
                    messagebox.showinfo("Failed FB817-820", "Solder joint issue. Hold to ME")

                
                curit_list.append(curitbin_line)
            consec = find_consecutive(curit_list)

            for row in rows:
                if consec and row.get('3_tiuid').startswith('JP'):
                    messagebox.showinfo("JSP PCH FB108-408 & FB109-409", "Please VI, Clean and UTP")
                    break
                
                
        # Bin8 End

        # Bin9 Start
        if flagBin == 'Bin9':
            Binflag = False
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if 'LEAKAGE' in line and (block.get('tag_ib') == 'Bin9' or block.get('tag_ib') == 'Bin209'):
                    Binflag = True
                if '2_comnt_failpins_' in line:
                    # if Binflag and 'failpin' in line:
                    row['fail_channel'] = line.split('_')[-1].strip()
                    fail_channel_list = line.split('_')[3].replace('{', '').replace('}', '').split(',')

            if any(x in {'9', '209'} for x in [row['3_curitbin'], row['3_curtbin'], row['3_curibin']]):
                if row['fail_channel'] != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)
                if xiu[0:2]=="RM":
                    probeID_list = ['19260', '19261', '20294', '20295']
                    prefix = 'D1_' if row.get('3_chuckid') == '1' else 'D2_'
                    probeID_list = [prefix + item for item in probeID_list]
                binmodeflag = block.get('flag')
                curitbin_line = row.get(f'3_cur{binmodeflag}')
                if binmodeflag in ['itbin', 'tbin']:
                    curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                elif binmodeflag == 'ibin':
                    curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'), probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
                faildie += 1
                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)
        # Bin9 End

        # Bin10 Start
        if flagBin == 'Bin10':
            if ib == 'Bin10' or ib == 'Bin210':
                datasets = block.get('data')
                for line in datasets:
                    value = line.split('_')[-1].strip()
                    for i in item:
                        if i in line:row[i] = value
                    if '2_tname_HWALARM' in line and 'DPSCurrentClamp' in line:
                        hw_flag = True
                    if '2_strgval_Module' in line and hw_flag:
                        hw_flag = False
                        fail_channel = re.search(r'\d+', value, re.I).group(0)
                        fail_channel_list = fail_channel.split(',')
                    if 'VIPR' in line and 'short' in line and block.get('tag_ib') in['Bin10', 'Bin210']: Binflag = True
                    if 'faildata_' in line and Binflag:
                        fail_channel = re.search(r'\d+', value, re.I).group(0)
                        fail_channel_list = fail_channel.split(',')
                        probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)
                if len(fail_channel) < 7 and fail_channel != '':
                    fail_channel = channel_standardlize.get(len(fail_channel)) + fail_channel

                if row['fail_channel'] != '':
                    probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)


                if block.get('flag') == 'itbin':
                        curitbin_line = row.get('3_curitbin')
                        curibin_line = row.get('3_comnt_SDSFB')
                        curfbin_line = row.get('3_comnt_SDTFB')

                elif block.get('flag') == 'tbin':
                        curitbin_line = row.get('3_curtbin')
                        curibin_line = row.get('3_comnt_SDSFB')
                        curfbin_line = row.get('3_comnt_SDTFB')

                elif block.get('flag') == 'ibin':
                        curitbin_line = row.get('3_curibin')
                        curibin_line = row.get('3_curfbin')
                        curfbin_line = row.get('3_curfbin')

                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                      probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
                faildie += 1
                probeID_list = probeID_list.replace('[', '')
                probeID_list = probeID_list.replace(']', '')
                Pin.extend(probeID_list.split(','))
                HDMT.extend(fail_channel_list)
        # Bin10 End

        # Bin11
        if flagBin == 'Bin11':
            count = 1
            Binflag = False
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if 'VIX' in line or 'BSCANVI' in line and (
                        block.get('tag_ib') == 'Bin11' or block.get('tag_ib') == 'Bin211'): Binflag = True
                if '2_faildata_' in line:
                    row['fail_channel'] = line.split('_')[-1].strip()
                    fail_channel_list = line.split('_')[2].replace('{', '').replace('}', '').split(',')
                    Binflag = False
                if Binflag and 'failpin' in line:
                    row['fail_channel'] = line.split('_')[-1].strip()
                    fail_channel_list = line.split('_')[3].replace('{', '').replace('}', '').split(',')
                    Binflag = False
                if any(x in {'11', '211'} for x in
                       [row['3_curitbin'], row['3_curtbin'], row['3_curibin']]) and count == 1:
                    if row['fail_channel'] != '':
                        probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)


                    binmodeflag = block.get('flag')
                    curitbin_line = row.get(f'3_cur{binmodeflag}')
                    if binmodeflag in ['itbin', 'tbin']:
                        curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                    elif binmodeflag == 'ibin':
                        curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                          row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'), probeID_list)
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))
                    faildie += 1
                    count = 0
                    Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                    HDMT.extend(fail_channel_list)
        # Bin11 End

        # Bin13 Start
        if flagBin == 'Bin13':
            bin_flag = False
            

            if block.get('UltraBinner') and block.get('tag_ib') in ['Bin13', 'Bin213']:
                for line in block.get('data'):
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                    if bin_flag:
                        if "2_comnt_failpins_" in line or "2_faildata_" in line:
                            row['fail_channel'] = line.split('_')[-1].strip()
                            fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                            bin_flag = False
                    
                    if block.get('UltraBinner') in line: bin_flag = True


            if any(x in {'13', '213'} for x in [row['3_curitbin'], row['3_curtbin'], row['3_curibin']]):
                if row['fail_channel'] != '': 
                    probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)
                   

                binmodeflag = block.get('flag')
                curitbin_line = row.get(f'3_cur{binmodeflag}')
                

                if binmodeflag in ['itbin', 'tbin']:
                    curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                elif binmodeflag == 'ibin':
                    curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line,curfbin_line, row.get('3_chuckid'),fail_channel_list,  probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
                faildie += 1
                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)
        # Bin13 End



        
        # Bin15 Start
        if flagBin == 'Bin15':
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if 'VIPR' in line and 'open' in line and (
                        block.get('tag_ib') == 'Bin15' or block.get('tag_ib') == 'Bin215'):
                    Binflag = True
                if '2_faildata_' in line:
                    # if Binflag and '2_comnt_failpins_' in line:
                    row['fail_channel'] = line.split('_')[-1].strip()
                    fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')

                if any(x in {'15', '215'} for x in
                       [row['3_curitbin'], row['3_curtbin'], row['3_curibin']]) and count == 1:
                    if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                    binmodeflag = block.get('flag')
                    curitbin_line = row.get(f'3_cur{binmodeflag}')
                    if binmodeflag in ['itbin', 'tbin']:
                        curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                    elif binmodeflag == 'ibin':
                        curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                          row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'), probeID_list)
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))
                    count = 0
                    faildie += 1
                    Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                    HDMT.extend(fail_channel_list)

        # Bin15 End

        # Bin19 Start
        if flagBin == 'Bin19':
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if ('PGT_X_DC' in line or 'RESET' in line.upper()) and block.get('tag_ib') in[ 'Bin19','Bin219']:
                    Binflag = True
                if Binflag and 'faildata' in line:
                    # if Binflag and '2_comnt_failpins_' in line:
                    row['fail_channel'] = line.split('_')[-1].strip()
                    fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                    Binflag = False

                if any(x in {'19', '219'} for x in
                       [row['3_curitbin'], row['3_curtbin'], row['3_curibin']]) and count == 1:
                    if fail_channel_list != '':
                        probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                    binmodeflag = block.get('flag')
                    curitbin_line = row.get(f'3_cur{binmodeflag}')
                    if binmodeflag in ['itbin', 'tbin']:
                        curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                    elif binmodeflag == 'ibin':
                        curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                          row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'), probeID_list)
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))
                    faildie += 1
                    count = 0
                    Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                    HDMT.extend(fail_channel_list)
        # Bin19 End


        # SPR/EMR Bin25 Start
        if flagBin == 'Bin25 SPR/EMR':
            bin_flag = False
            PCIE_flag = False
            UPI_flag = False
            Both_flag = False
            probe_List = []

            for line in block.get('data'):

                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})

                if bin_flag:
                    line1 = line.replace('2_strgval_', '')
                    first_string = line1.find('|')
                    last_string = line1.rfind('|')
                    rep1 = line1[first_string + 1:last_string].replace('|', ',').split(',')
                    

                    if row.get('3_tiuid')[0:2] == 'SN':
                        rep1 = list(map(lambda st: str.replace(st, "PCIE", "PE"), rep1))
                       
                        rep1 = list(map(lambda st: str.replace(st, "_0", "_"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DN_", "DN"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP_", "DP"), rep1))

                    if row.get('3_tiuid')[0:2] == 'SI' or row.get('3_tiuid')[0:2] == 'SA':
                        rep1 = list(map(lambda st: str.replace(st, "DN", "DN_"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP", "DP_"), rep1))
                    if row.get('3_tiuid')[0:2] == 'ED' or row.get('3_tiuid')[0:2] == 'ER':
                        rep1 = list(map(lambda st: str.replace(st, "PE", "PCIE"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DN_00", "DN0"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP_00", "DP0"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DN_0", "DN"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP_0", "DP"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP_", "DP"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DN_", "DN"), rep1))

                    rep1 = list(map(lambda st: str.replace(st, "[", ""), rep1))
                    rep1 = list(map(lambda st: str.replace(st, "]", ""), rep1))
                   

                    line4 = [ele for ele in rep1 if
                             'UPI' in ele or 'PE' in ele or 'PCIE' in ele or 'DMI' in ele]
                    

                    for item in line4:
                        if item.startswith('PCIE'):
                            PCIE_flag = True
                        elif item.startswith('UPI'):
                            UPI_flag = True
                        elif item.startswith('PCIE') and item.startswith('UPI'):
                            Both_flag = True

                    probe_List.extend(line4)
                    bin_flag = False

                for i in item:
                    if i in line: row[i] = line.split('_')[-1].strip()

                if block.get('tag_ib') in ['Bin25', 'Bin225'] and '_fc1' in line and 'SIO' in line:
                    
                    bin_flag = True

            if block.get('tag_ib') in ['Bin25', 'Bin225'] and row.get('3_tiuid').startswith(('ER')) and UPI_flag == True:
                probe_List = ["61788","61789","61790","61791","63226", "63228", "63515","63517"]

            elif block.get('tag_ib') in ['Bin25', 'Bin225'] and row.get('3_tiuid').startswith(('ER')) and PCIE_flag == True:
                probe_List = ["66495", "66497", "66766", "66768", "68167", "68168", "68169", "68170"]

            elif block.get('tag_ib') in ['Bin25', 'Bin225'] and row.get('3_tiuid').startswith(('ER')) and Both_flag == True:
                probe_List = ["66495", "66497", "66766", "66768", "68167", "68168", "68169", "68170","61788","61789","61790","61791","63226", "63228", "63515","63517"]

            elif block.get('tag_ib') in ['Bin25', 'Bin225'] and row.get('3_tiuid').startswith(('ED')) and PCIE_flag == True:
                probe_List = ["462", "463", "464", "465", "1871", "1873", "2136", "2138"]

            elif block.get('tag_ib') in ['Bin25', 'Bin225'] and row.get('3_tiuid').startswith(('ED')) and UPI_flag == True:
                probe_List = ["5192", "5194", "5483", "5485", "6917", "6918", "6919", "6920"]

            elif block.get('tag_ib') in ['Bin25', 'Bin225'] and row.get('3_tiuid').startswith(('ED')) and Both_flag == True:
                probe_List = ["462", "463", "464", "465", "1871", "1873", "2136", "2138", "5192", "5194", "5483", "5485", "6917", "6918", "6919", "6920"]

            else:
                probe_List = [*set(probe_List)]

            if probe_List:
                probeID_list = probe_List
                if row.get('3_tiuid')[0:2] == 'SN':
                    probeID_list = Fail_Channel_Lookup2(probe_List, df1)

                Pin.extend(probeID_list)
                probeID_list = ' '.join(map(str, probeID_list))


                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                            row.get('3_partialwafid'), row.get('3_curftbin'), row.get('3_chuckid'), probeID_list, )
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'),
                    row.get('3_curitbin'), row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB'), row.get('3_chuckid'),
                    fail_channel_list, probeID_list))

            faildie += 1
        # SPR/EMR Bin25 End

            # Bin25 Start
            if flagBin == 'Bin25 FM4/GDR/JSPPCH':
                bin_flag = False
                if block.get('UltraBinner') and block.get('tag_ib') in ['Bin25', 'Bin225']:
                    for line in block.get('data'):
                        value = line.split('_')[-1].strip()
                        row.update({i: value for i in item if i in line})
                        if bin_flag:
                            if xiu[0:2] in ["GK", "JP"] and "2_comnt_failpins_" in line or "2_faildata_" in line:
                                row['fail_channel'] = line.split('_')[-1].strip()
                                fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                                bin_flag = False
                            if xiu[0:2] == "FA" and block.get(
                                    'UltraBinner') in line and not "testtime" in line and not "WASVADTL" in line:
                                row['fail_channel'] = line.split('_')[-2].strip()
                                probe_List = [line.split('_')[-2].strip()]
                                # bin_flag = False

                        if 'PCH_PSIO_BSCAN_TOGGLEALL_STRESS' in line: bin_flag = True
                        if block.get('UltraBinner') in line: bin_flag = True

                    if row['fail_channel'] != '' and xiu[0:2] == 'FA':
                        probeID_list = Fail_Channel_Lookup3(probe_List, df1, str(row.get('3_chuckid')))
                    if fail_channel_list != '' and xiu[0:2] == 'GK':
                        probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)
                    binmodeflag = block.get('flag')
                    curitbin_line = row.get(f'3_cur{binmodeflag}')

                    if binmodeflag in ['itbin', 'tbin']:
                        curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                    elif binmodeflag == 'ibin':
                        curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                          row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid')
                          , fail_channel_list, probeID_list)
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))
                    faildie += 1
                    Pin.extend(probeID_list)
                    HDMT.extend(fail_channel_list)
            # Bin25 End

            # Bin30 Start
            if flagBin == 'Bin30':
                count = 1
                Binflag = False
                for line in block.get('data'):
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                    if 'TPI_VIPR::VIPR_X_DC_K' in line and '_X_X_X_X_fpr1' in line and block.get('tag_ib') in ['Bin30',
                                                                                                               'Bin230']:
                        Binflag = True

                    if '2_strgval' in line and Binflag:
                        row['fail_channel'] = line.split('|')[-2].strip()
                        fail_channel_list = line.split('|')[-2].strip()
                        xiu_full = row.get('3_tiuid')
                        xiu_alias = xiu_full[:4] + xiu_full[6]
                        TH = row.get('3_chuckid')
                        probeID_list = Fail_Channel_Lookup_HDMT(fail_channel_list, xiu_alias, TH)
                        Binflag = False

                if block.get('tag_ib') in ['Bin30', 'Bin230']:

                    Pin.extend(probeID_list)
                    # HDMT.extend(fail_channel_list)

                    binmodeflag = block.get('flag')
                    curitbin_line = row.get(f'3_cur{binmodeflag}')
                    if binmodeflag in ['itbin', 'tbin']:
                        curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                    elif binmodeflag == 'ibin':
                        curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                          row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                          probeID_list)
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))
            # Bin30 End

        #Bin25 LNL
        if flagBin == 'Bin25 LNL SOC M':
            bin_flag = False
            

            if block.get('tag_ib') in ['Bin25', 'Bin225']:
                for line in block.get('data'):
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                    if bin_flag:
                        if "2_fdpmv" in line:
                            row['fail_channel'] = line.split('_')[-1].strip()
                            fdpmv = line.split('_')[-1]
                            bin_flag = False
                            
                            try:
                                # Attempt to convert the string to a float
                                csv_file_path = config_path + r'\LNL_SOC_M_Bin25_Lookup.csv'
                                TH = row.get('3_chuckid')
                                probeID_list = check_fdpmv(csv_file_path, fdpmv,TH)
                                probeID_list = Fail_Channel_Lookup3(probeID_list, df1, str(row.get('3_chuckid')))
                                
                                

                            except ValueError:
                                # If conversion fails, skip the rest of the code in this iteration
                                pass  # or continue if inside a loop

                        
                    if (("SIO_BSCAN_SXX::PULSE_BSCAN" in line or "SIO_BSCAN_SXX::TRAIN_BSCAN" in line)
                            and not 'testtime' in line): bin_flag = True


            if any(x in {'25', '225'} for x in [row['3_curitbin'], row['3_curtbin'], row['3_curibin']]):
                binmodeflag = block.get('flag')
                curitbin_line = row.get(f'3_cur{binmodeflag}')
                

                if binmodeflag in ['itbin', 'tbin']:
                    curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                elif binmodeflag == 'ibin':
                    curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line,curfbin_line, row.get('3_chuckid'),fail_channel_list,  probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
                faildie += 1
                probeID_list = ''.join(probeID_list)
                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
        # Bin25 LNL End

		
		# ADL PCH Bin299 Start
        if flagBin == 'Bin299 ADL PCH':
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
               
                
                if 'VIPR' in line and 'opens' in line and (
                        block.get('tag_ib') == 'Bin299'):
                    Binflag = True
                   
                if '2_faildata_' in line:
                    # if Binflag and '2_comnt_failpins_' in line:
                    row['fail_channel'] = line.split('_')[-1].strip()
                    fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')

                if any(x in {'299', '29901'} for x in
                       [row['3_curitbin'], row['3_curtbin'], row['3_curibin']]) and count == 1:
                    if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                    binmodeflag = block.get('flag')
                    #print(binmodeflag)
                    curitbin_line = row['3_curitbin']
                    #print(curitbin_line)
                    if binmodeflag in ['itbin', 'tbin']:
                        curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                    elif binmodeflag == 'ibin':
                        curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                          row.get('3_partialwafid'), row.get('3_curitbin'), curibin_line, curfbin_line, row.get('3_chuckid'), probeID_list)
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))
                    count = 0
                    faildie += 1
                    Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                    HDMT.extend(fail_channel_list)

        # ADL PCH Bin299 End

         # Bin28 MTL SOC Start
        if flagBin == 'Bin28 MTL SOC M':
            bin_flag = False
            if block.get('UltraBinner') and block.get('tag_ib') in ['Bin28', 'Bin228']:
                for line in block.get('data'):
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                    if bin_flag:
                        if "2_comnt_failpins_" in line or "2_faildata_" in line:
                            row['fail_channel'] = line.split('_')[-1].strip()
                            fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                            bin_flag = False
                    
                    if block.get('UltraBinner') in line: bin_flag = True


            if any(x in {'28', '228'} for x in [row['3_curitbin'], row['3_curtbin'], row['3_curibin']]):
                if row['fail_channel'] != '': 
                    probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)
                   

                binmodeflag = block.get('flag')
                curitbin_line = row.get(f'3_cur{binmodeflag}')
                

                if binmodeflag in ['itbin', 'tbin']:
                    curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                elif binmodeflag == 'ibin':
                    curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line,curfbin_line, row.get('3_chuckid'),fail_channel_list,  probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
                faildie += 1
                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)

        # # Bin28 MTL SOC End





        # RPL Bin32 Start
        if flagBin == 'Bin32 RPL':
            bin_flag = False
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if bin_flag and "2_comnt_failpins_" in line or "2_faildata_" in line:
                    fail_channel_list = line.split('_')[-1].strip().replace('{', '').replace('}', '').split(',')
                    bin_flag = False
                if block.get('tag_ib') in ['Bin32', 'Bin232'] and '_fc1' in line and 'MIO' in line: bin_flag = True

            if block.get('tag_ib') in ['Bin32', 'Bin232']:
                if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)
                curitbin_line = row.get('3_curitbin')
                curibin_line = row.get('3_comnt_SDSFB')
                curfbin_line = row.get('3_comnt_SDTFB')
                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                      probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
            faildie += 1
        # RPL Bin32 End

        # RPL Bin32 Start
        if flagBin == 'Bin39 JSP PCH':
            bin_flag = False
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if bin_flag and "2_comnt_failpins_" in line or "2_faildata_" in line:
                    fail_channel_list = line.split('_')[-1].strip().replace('{', '').replace('}', '').split(',')
                    bin_flag = False
                if block.get('tag_ib') in ['Bin39', 'Bin239'] and 'VCCPRIMCORE' in line: bin_flag = True

            if block.get('tag_ib') in ['Bin39', 'Bin239']:
                if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)
                curitbin_line = row.get('3_curtbin')
                curibin_line = row.get('3_comnt_SDSFB')
                curfbin_line = row.get('3_comnt_SDTFB')
                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                      probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
            faildie += 1

        if flagBin == 'Bin39/40/41/42/46/48/74 MTL SOCM':
            if block.get('tag_ib') in ['Bin39', 'Bin239', 'Bin40', 'Bin240', 'Bin41', 'Bin241', 'Bin42', 'Bin242',
                                       'Bin46', 'Bin246', 'Bin48', 'Bin248', 'Bin74', 'Bin274']:
                bin_flag = False
                for line in block.get('data'):
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                if block.get('tag_ib') in ['Bin39', 'Bin239']:
                    probeID_list = ['65995', '65996', '65997', '65998']
                elif block.get('tag_ib') in ['Bin40', 'Bin240']:
                    probeID_list = ['61375', '61339', '56644', '56645']
                elif block.get('tag_ib') in ['Bin41', 'Bin241', 'Bin42', 'Bin242']:
                    probeID_list = ['62450', '62452', '62454', '62456', '62462', '63723', '63729', '63731', '63733',
                                    '63735',
                                    '63741', '63743', '64317', '64321', '64323', '64325', '64327', '64335', '64872',
                                    '64874', '64878',
                                    '64880', '64882', '64884', '64886', '64888', '64890', '65351', '65353', '65355',
                                    '65357'
                        , '65359', '65361', '65365', '65369', '65920', '65922', '65926', '65928', '65932', '65936',
                                    '65940']
                elif block.get('tag_ib') in ['Bin46', 'Bin246']:
                    probeID_list = ['56644', '56645', '56756', '56757',
                                    '57294', '57295', '60895', '60896', '61339', '61375', '61458', '61459']
                elif block.get('tag_ib') in ['Bin48', 'Bin248']:
                    probeID_list = ['40117', '40120', '40748', '40750', '41743', '41746', '42373', '42375']
                elif block.get('tag_ib') in ['Bin74', 'Bin274']:
                    probeID_list = ['17915', '17916', '17917', '17379', '17380', '17381', '22125', '22126', '22127',
                                    '21442', '21443', '21444']
                prefix = 'D1_' if row.get('3_chuckid') == '1' else 'D2_'
                probeID_list = [prefix + item for item in probeID_list]

                if probeID_list:
                    Pin.extend(probeID_list)
                    binmodeflag = block.get('flag')
                    curitbin_line = row.get(f'3_cur{binmodeflag}')
                    if binmodeflag in ['itbin', 'tbin']:
                        curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                    elif binmodeflag == 'ibin':
                        curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                          row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'), probeID_list)
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))

                    faildie += 1
        # Bin40/41/42/46/48/74 SOCM End

        # Bin42 Start
        if flagBin == 'Bin42':
            bin_flag = False
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})

                if bin_flag and ("2_faildata_" in line):
                    fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                    bin_flag = False

                if block.get('tag_ib') in ['Bin42', 'Bin242'] and 'SCN_CORE' or 'FUS_' in line: bin_flag = True

            if block.get('tag_ib') in ['Bin42', 'Bin242']:
                if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)
                if row.get('3_comnt_SDSFB'):
                    curitbin_line = row.get('3_curitbin')
                    curibin_line = row.get('3_comnt_SDSFB')
                    curfbin_line = row.get('3_comnt_SDTFB')
                else:
                    curitbin_line = row.get('3_curibin')
                    curibin_line = row.get('3_curfbin')
                    curfbin_line = row.get('3_curfbin')


                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                      probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
            faildie += 1
        # Bin42 End


        # RPL Bin46 GNV Start
        if flagBin == 'Bin46 GNR_IO':
            bin_flag = False
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if bin_flag:
                    if "_upi." in line:
                        line = line.replace("_upi", "")
                    line = line.split(".")
                    sublist = line[2:5]
                    failname = '.'.join(sublist)

                    try:
                        # Attempt to convert the string to a float
                        csv_file_path = config_path + r'\GRN_IO_Bin46_Lookup.csv'
                        probeID_list = check_port_octet(csv_file_path, failname)
                        
                        if row.get('3_chuckid') == '1':
                            probeID_list = [f"D1_{num}" for num in probeID_list]

                        else:
                            probeID_list = [f"D2_{num}" for num in probeID_list]
                           

                    except ValueError:
                        # If conversion fails, skip the rest of the code in this iteration
                        pass  # or continue if inside a loop


                    bin_flag = False


                strings_to_check = [
                'DFXRXDET_UPI_CTVDEC_K_PREHVQK_X_FLEX_NOM_X',
                'DFXRXDET_UPI_CTVDEC_K_PREHVQK_X_FLEX_MIN_X_RXNODETECT',
                'DFXRXDET_X_CTVDEC_K_PREHVQK_X_PCIE_MIN_X_RXDET',
                'TXRXDET_PCIE_CTVDEC_K_PREHVQK_X_PCIE_MIN_X_RXNODETECT']

                if any(s in line for s in strings_to_check) and '_fc' in line:
                    bin_flag = True

            if block.get('tag_ib') in ['Bin46', 'Bin246']:
                #print(row.get('3_chuckid'))

                Pin.extend(probeID_list)
                
                if row.get('3_comnt_SDSFB'):
                    curitbin_line = row.get('3_curitbin')
                    curibin_line = row.get('3_comnt_SDSFB')
                    curfbin_line = row.get('3_comnt_SDTFB')
                else:
                    curitbin_line = row.get('3_curibin')
                    curibin_line = row.get('3_curfbin')
                    curfbin_line = row.get('3_curfbin')


                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                      probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
            faildie += 1
               
                    

		
		# SPR/EMR Bin4846 Start
        if flagBin in ['Bin25 SPR/EMR', 'Bin46/48 SPR/EMR', 'Bin4 SPR MCC', 'Bin54 SPR MCC']:
            bin_flag = False
            probe_List = []

            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})

                if bin_flag:
                    line1 = line.replace('2_strgval_', '')
                    first_string = line1.find('|')
                    last_string = line1.rfind('|')
                    rep1 = line1[first_string + 1:last_string].replace('|', ',').split(',')

                    if row.get('3_tiuid')[0:2] == 'SN':
                        rep1 = list(map(lambda st: str.replace(st, "PCIE", "PE"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "_0", "_"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DN_", "DN"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP_", "DP"), rep1))

                    if row.get('3_tiuid')[0:2] == 'SI' or row.get('3_tiuid')[0:2] == 'SA':
                        rep1 = list(map(lambda st: str.replace(st, "DN", "DN_"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP", "DP_"), rep1))
                    if row.get('3_tiuid')[0:2] == 'ED' or row.get('3_tiuid')[0:2] == 'ER':
                        rep1 = list(map(lambda st: str.replace(st, "PE", "PCIE"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DN_00", "DN0"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP_00", "DP0"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DN_0", "DN"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP_0", "DP"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DP_", "DP"), rep1))
                        rep1 = list(map(lambda st: str.replace(st, "DN_", "DN"), rep1))

                    rep1 = list(map(lambda st: str.replace(st, "[", ""), rep1))
                    rep1 = list(map(lambda st: str.replace(st, "]", ""), rep1))

                    line4 = [ele for ele in rep1 if 'UPI' in ele or 'PE' in ele or 'PCIE' in ele or 'DMI' in ele]

                    probe_List.extend(line4)
                    bin_flag = False

                for i in item:
                    if i in line: row[i] = line.split('_')[-1].strip()

                if (block.get('tag_ib') in ['Bin46', 'Bin246', 'Bin48', 'Bin248', 'Bin4', 'Bin54', 'Bin254']
                        and '_fc1' in line and 'SIO' in line and not 'SIO_BSCANLKG' in line): bin_flag = True
                if block.get('tag_ib') in ['Bin25', 'Bin225'] and '_fc1' in line and 'SIO' in line: bin_flag = True

            if block.get('tag_ib') in ['Bin46', 'Bin246', 'Bin48', 'Bin248', 'Bin25', 'Bin225', 'Bin4', 'Bin54',
                                       'Bin254']:

                probe_List = [*set(probe_List)]

                if probe_List:
                    probeID_list = Fail_Channel_Lookup2(probe_List, df1)
                    Pin.extend(probeID_list)
                    probeID_list = ' '.join(map(str, probeID_list))
                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                          row.get('3_partialwafid'), row.get('3_curftbin'), row.get('3_chuckid'), probeID_list, )
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'),
                        row.get('3_curitbin'), row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB'), row.get('3_chuckid'),
                        fail_channel_list, probeID_list))

                faildie += 1
            # SPR/EMR Bin4846 End

        # JPANA/EMANA Bin4846 Start
        if flagBin in ['Bin46/48 TGL/ADL/JSP PCH/EBG']:
            bin_flag = False
            probe_List = []
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if bin_flag:
                    if "2_comnt_failpins_" in line or "2_faildata_" in line:
                        fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                        bin_flag = False
                    if '2_mrslt' in line:
                        if (float(line.split('_')[-1].strip()) <= 40 or float(
                                line.split('_')[-1].strip()) >= 62): probe_List.append(temp_line)
                        bin_flag = False
                if block.get('tag_ib') in ['Bin46', 'Bin246', 'Bin48', 'Bin248']:
                    if xiu[0:2] == 'TP' and 'PSIO' in line: bin_flag = True
                    if '_fc1' in line and 'PSIO' in line: bin_flag = True
                    if ('PSIO_PCIE_SDS::PPCIE_X_ANALOG_K_END_X_X_VMIN' in line.upper()
                        and '_MODPHY_RTERM_TTM_IMP' in line.upper()) or (xiu[0:2] == "JP" and 'IMP' in line):
                        temp_line = line[line.find("IMP") + 4:]
                        bin_flag = True
            if block.get('tag_ib') in ['Bin46', 'Bin246', 'Bin48', 'Bin248']:
                if xiu[0:2] == "TP" or block.get('tag_ib') in ['Bin46', 'Bin246']:
                    if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)
                    Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                elif block.get('tag_ib') in ['Bin48', 'Bin248']:
                    probe_List = [*set(probe_List)]
                    if fail_channel_list != '': probeID_list = Fail_Channel_Lookup2(probe_List, df1)
                    probeID_list = list(map(lambda st: 'D' + str(row.get('3_chuckid')) + st[2:], probeID_list))
                    Pin.extend(probeID_list)
                probeID_list = ' '.join(map(str, probeID_list))

                HDMT.extend(fail_channel_list)
                curitbin_line = row.get('3_curtbin')
                curibin_line = row.get('3_comnt_SDSFB')
                curfbin_line = row.get('3_comnt_SDTFB')
                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                      probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
            faildie += 1
        # JPANA/EMANA Bin4648 End

        # RPL Bin51 Start
        if flagBin == 'Bin51 RPL':
            bin_flag = False
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})

                if bin_flag and ("2_comnt_failpins_" in line or "2_faildata_" in line):
                    fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                    bin_flag = False

                if block.get('tag_ib') in ['Bin51', 'Bin251'] and '_fc1' in line and 'MIO' in line: bin_flag = True

            if block.get('tag_ib') in ['Bin51', 'Bin251']:
                if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)
                curitbin_line = row.get('3_curitbin')
                curibin_line = row.get('3_comnt_SDSFB')
                curfbin_line = row.get('3_comnt_SDTFB')
                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                      probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
            faildie += 1
        # RPL Bin51 End

        # RPL Bin75 Start
        if flagBin == 'Bin75 RPL & JSP CPU':
            bin_flag = False
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if bin_flag:
                    if "2_comnt_failpins_" in line or "2_faildata_" in line:
                        fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                        bin_flag = False
                if block.get('tag_ib') in ['Bin75', 'Bin275']:
                    if '_fc1' in line and 'SIO' in line: bin_flag = True

            if block.get('tag_ib') in ['Bin75', 'Bin275']:
                if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)
                curitbin_line = row.get('3_curitbin')
                curibin_line = row.get('3_comnt_SDSFB')
                curfbin_line = row.get('3_comnt_SDTFB')
                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                      probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
            faildie += 1
        # RPL Bin75 End

        if flagBin == 'Ultrabiner':
            bin_flag = False

            if block.get('UltraBinner'): #and block.get('tag_ib') in ['Bin75', 'Bin275']:
                for line in block.get('data'):
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                    if bin_flag:
                        if "2_comnt_failpins_" in line or "2_faildata_" in line:
                            fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                            bin_flag = False
                    
                    if '_fc1' in line and block.get('UltraBinner') in line: bin_flag = True

                if block.get('tag_ib'):
                    #print(block.get('UltraBinner'))
                    if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                    Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                    HDMT.extend(fail_channel_list)
                    curitbin_line = row.get('3_curibin')
                    curibin_line = row.get('3_curftbin')
                    curfbin_line = row.get('3_comnt_SDTFB')
                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list, block.get('UltraBinner'))
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))
            faildie += 1


        if flagBin == 'Bin4819 JSP PCH':
            bin_flag = False
            if block.get('UltraBinner') and block.get('tag_ib') in ['Bin48', 'Bin248']:
                probe_List = []
                for line in block.get('data'):
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                    if bin_flag:
                        
                        IMP = line.split('_')[-1]
                        
                        #print(IMP)
                        if (float(line.split('_')[-1].strip()) >= 60):
                            #print(float(line.split('_')[-1].strip()))
                            temp_line = IMPline[IMPline.find("IMP") + 4:]
                            #print(IMPline)
                            #print(temp_line)
                            probe_List.append(temp_line)
                            IMPline = ''

                        #if "2_comnt_failpins_" in line or "2_faildata_" in line:
                            #fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                        bin_flag = False
                    
                    if 'IMP' in line and block.get('UltraBinner') in line: 
                        bin_flag = True
                        IMPline = line

                if block.get('tag_ib'):
                    #print(block.get('UltraBinner'))
                    if probe_List:
                        probeID_list = Fail_Channel_Lookup2(probe_List, df1)
                    Pin.extend(probeID_list)
                    probeID_list = ' '.join(map(str, probeID_list))

                    
                    
                    curitbin_line = row.get('3_curibin')
                    curibin_line = row.get('3_curftbin')
                    curfbin_line = row.get('3_comnt_SDTFB')
                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list)
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))
                    faildie += 1

        # Bin77 LNL SOC M Start
        if flagBin == 'Bin77 LNL SOC M':
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if 'SCN_SCAN_SXX' in line and 'STUCKAT' in line and (
                        block.get('tag_ib') == 'Bin77' or block.get('tag_ib') == 'Bin277'):
                    Binflag = True
                if '2_faildata_' in line:
                    # if Binflag and '2_comnt_failpins_' in line:
                    row['fail_channel'] = line.split('_')[-1].strip()
                    fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')

                if any(x in {'77', '277'} for x in
                       [row['3_curitbin'], row['3_curtbin'], row['3_curibin']]) and count == 1:
                    if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)

                    binmodeflag = block.get('flag')
                    curitbin_line = row.get(f'3_cur{binmodeflag}')
                    if binmodeflag in ['itbin', 'tbin']:
                        curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                    elif binmodeflag == 'ibin':
                        curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                    print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                          row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'), probeID_list)
                    tv.insert(parent='', index='end', text='', values=(
                        row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                        row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                        fail_channel_list, probeID_list))
                    count = 0
                    faildie += 1
                    Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                    HDMT.extend(fail_channel_list)

        # Bin77 LNL SOC M End

        # Bin88 Start
        if flagBin == 'Bin88':
            bin_flag = False
            probeID_list = []
            openkelvin_flag = False
            if ib in ['Bin88', 'Bin288']:
                for line in block.get('data'):
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                    if xiu[0:2] in["RM","LM"]:
                        if bin_flag:
                            value_to_check = line.split('_')[-1].strip()
                            try:
                               if xiu[0:2]=='RM': result, rail = check_limits(config_path + r'\MTL_SOC_M_Bin88_Limit_Lookup.csv',
                                                            Bin88_token, float(value_to_check))
                               if xiu[0:2]=='RO': result, rail = check_limits(config_path + r'\MTL_SOC_S_Bin88_Limit_Lookup.csv',
                                                            Bin88_token, float(value_to_check))                 
                               elif xiu[0:2]=='LM': result, rail = check_limits(config_path + r'\LNL_SOC_M_Bin88_Limit_Lookup.csv',
                                                                                Bin88_token, float(value_to_check))
                            except ValueError:
                                pass  # or continue if inside a loop

                            if rail is not None: probeID_list.append('D' + row.get('3_chuckid') + '_' + rail)
                            bin_flag = False

                        if (block.get('tag_ib') in ['Bin88', 'Bin288'] and ('TPI_SIUP_SXX' in line or 'PP_SICC' in line)
                                and not 'testtime' in line and not 'HWALARM' in line):
                            parts = line.split('_')
                            print(parts)
                            Bin88_token = '_'.join(parts[2:-1])
                            print(Bin88_token)
                            bin_flag = True
                    else:
                        if 'VCC' in line: vcc_flag = True
                        if 'faildata_' in line and vcc_flag: fail_channel_list = (re.search(r'\d+', value, re.I).
                                                                                  group(0).split(','))
                        if ('2_tname_HWALARM' in line and 'TYPE:DPS' in line.upper() and not 'Type:DPSAs' in line
                                and not 'Type:DPSDataNotFound2' in line): hw_flag = True
                        if '2_tname_HWALARM' in line and 'Type:DPSOpenKelvin' in line:
                            messagebox.showinfo("Failed IB88 OpenKelvin", "Solder joint issue. Hold to ME")
                        if '2_strgval_Module' in line and hw_flag:
                            hw_flag = False
                            fail_channel_list = re.search(r'\d+', value, re.I).group(0).split(',')

                if fail_channel_list != '' and probeID_list == []: probeID_list = Fail_Channel_Lookup(fail_channel_list,
                                                                                                      df1)

                binmodeflag = block.get('flag')
                curitbin_line = row.get(f'3_cur{binmodeflag}')
                if binmodeflag in ['itbin', 'tbin']:
                    curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                elif binmodeflag == 'ibin':
                    curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'), fail_channel_list,
                      probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
                faildie += 1
                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                HDMT.extend(fail_channel_list)
                if ((curibin_line in ['8819'] or curfbin_line in ['8819']) and row.get('3_tiuid').startswith(
                        ('SI', 'SA')) and openkelvin_flag == True):
                    messagebox.showinfo("Failed IB88 Open Kelvin", "Solder joint issue. Hold to ME")

        # bin88 End
                # Bin97 Start
        if flagBin == 'Bin97':
                    if block.get('tag_ib') in ['Bin97', 'Bin297']:
                        bin_flag = False
                        for line in block.get('data'):
                            value = line.split('_')[-1].strip()
                            row.update({i: value for i in item if i in line})

                        if row.get('3_tiuid').startswith('RM'):
                            probeID_list = ['747', '1854', '62493']
                            prefix = 'D1_' if row.get('3_chuckid') == '1' else 'D2_'
                            probeID_list = [prefix + item for item in probeID_list]
                        elif row.get('3_tiuid').startswith(('FS', 'FF', 'UD', 'FA', 'GK', 'UM')):
                            token = ['TMD_DIODE', 'DTS_CALIB']
                            probeID_list = thermal_pin_lookup(token, df1, row.get('3_chuckid'), row.get('3_tiuid'))
                        else:
                            token = ['THERM']
                            probeID_list = thermal_pin_lookup(token, df1, row.get('3_chuckid'), row.get('3_tiuid'))
                        Pin.extend(probeID_list)
                        if probeID_list:

                            binmodeflag = block.get('flag')
                            curitbin_line = row.get(f'3_cur{binmodeflag}')
                            if binmodeflag in ['itbin', 'tbin']:
                                curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                            elif binmodeflag == 'ibin':
                                curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                            print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation,
                                  lot,
                                  row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'),
                                  probeID_list)
                            tv.insert(parent='', index='end', text='', values=(
                                row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                                row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line,
                                row.get('3_chuckid'),
                                fail_channel_list, probeID_list))

                            faildie += 1
                # Bin97 End
        # Bin99 start
        if flagBin == 'Bin99':
            openkelvin_flag = False
            burst_flag = False

            if ib == 'Bin99' or ib == 'Bin299':
                datasets = block.get('data')
                CH = []
                for line in datasets:
                    value = line.split('_')[-1].strip()
                    row.update({i: value for i in item if i in line})
                    if row.get('3_tiuid').startswith('TPBN') and block.get('tag_ib') == 'Bin299':
                        if 'VIPR' in line and 'opens' in line and (
                                block.get('tag_ib') == 'Bin299'):
                            Binflag = True
                        if '2_faildata_' in line and Binflag:
                            # if Binflag and '2_comnt_failpins_' in line:
                            row['fail_channel'] = line.split('_')[-1].strip()
                            fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                            CH.extend(fail_channel_list)
                    else:
                        if '2_strgval_Module' in line and hw_flag:
                            hw_flag = False
                            fail_channel_list = re.search(r'\d+', value, re.I).group(0).split(',')
                            CH.extend(fail_channel_list)
                        if '2_tname_HWALARM' in line and 'TYPE:DPS' in line.upper() and 'PARALLEL' not in line and 'DPSAss' not in line:
                            hw_flag = True
                        if '2_tname_HWALARM' in line and 'Type:Burst' in line and not 'PARALLEL' in line and not 'DPSAs' in line:
                            hw_flag = True
                            burst_flag = True
                        if '2_tname_HWALARM' in line and 'Type:DPSOpenKelvin' in line:
                            openkelvin_flag = True

                if fail_channel_list:
                    CH = list(set(CH))
                    CHstring = ', '.join(CH)
                    HDMT.extend(CH)
                    probeID_list = Fail_Channel_Lookup(CH, df1)
                    # probeID_list = ', '.join(probeID_list)

                binmodeflag = block.get('flag')
                curitbin_line = row.get(f'3_cur{binmodeflag}')
                if binmodeflag in ['itbin', 'tbin']:
                    curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                elif binmodeflag == 'ibin':
                    curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'), CH, probeID_list)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    CH, probeID_list))
                faildie += 1
                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                if (curibin_line in ['9901'] or curfbin_line in ['9901']) and row.get('3_tiuid').startswith(('SI', 'SA')) and openkelvin_flag == True:
                    messagebox.showinfo("Failed IB99 Open Kelvin", "Solder joint issue. Hold to ME")
                elif burst_flag == True:
                    messagebox.showinfo(row.get('3_tiuid'), "Tester issue- BurstAlreadyRunning. Please VI and UTP")
        # Bin99 End

        # All Bin Start
        if flagBin == 'All Bin':
            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
            if any(row[key] != '' for key in ['3_curitbin', '3_curtbin', '3_curibin']):
                if row['fail_channel'] != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)
                Ultra =''
                if block.get('UltraBinner'):
                    Ultra = 'Ultrabinner'
                binmodeflag = block.get('flag')
                curitbin_line = row.get(f'3_cur{binmodeflag}')
                if binmodeflag in ['itbin', 'tbin']:
                    curibin_line, curfbin_line = row.get('3_comnt_SDSFB'), row.get('3_comnt_SDTFB')
                elif binmodeflag == 'ibin':
                    curibin_line, curfbin_line = row.get('3_curfbin'), row.get('3_curfbin')

                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), curitbin_line, curfbin_line, row.get('3_chuckid'), probeID_list, Ultra)
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), curitbin_line, curibin_line, curfbin_line, row.get('3_chuckid'),
                    fail_channel_list, probeID_list))
                faildie += 1
                Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
        # All Bin End
                # MTL SOC M Bin25/Bin11
        if flagBin in ['Bin11 MTL SOC M', 'Bin25 MTL SOC']:
            bin_flag = False
            probe_List = []

            if xiu[0:2] == "RM":  SOC_lookup = pd.read_csv(config_path + r'\MTL_SOC_M_Bin25_11_lookup_LVM.csv')
            elif xiu[0:2] == "RO":SOC_lookup = pd.read_csv(config_path + r'\MTL_SOC_S_Bin25_lookup_LVM.csv')

            for line in block.get('data'):
                value = line.split('_')[-1].strip()
                row.update({i: value for i in item if i in line})
                if bin_flag and "2_fdpmv_" in line:
                    line1 = line.replace('2_fdpmv_', '')
                    if pd.api.types.is_numeric_dtype(SOC_lookup['LVM']):
                        row_index = SOC_lookup.index[SOC_lookup['LVM'] == int(line1)].tolist()
                    else:
                        row_index = SOC_lookup.index[SOC_lookup['LVM'] == line1].tolist()
                    line4 = list(SOC_lookup.iloc[row_index, 0])
                    if line4 != []:
                        probe_List.extend(line4)
                        if probe_List != []:
                            probe_List = [*set(probe_List)]
                            print(probe_List)
                            probeID_list = Fail_Channel_Lookup3(probe_List, df1, str(row.get('3_chuckid')))
                            Pin.extend(probeID_list)
                            probeID_list = ' '.join(map(str, probeID_list))
                        bin_flag = False
                # if bin_flag and "2_faildata" in line:
                #   row['fail_channel'] = line.split('_')[-1].strip()
                #  fail_channel_list = line.split('_')[-1].replace('{', '').replace('}', '').split(',')
                # if fail_channel_list != '': probeID_list = Fail_Channel_Lookup(fail_channel_list, df1)
                # Pin.extend(probeID_list.replace('[', '').replace(']', '').split(','))
                # bin_flag = False
                for i in item:
                    if i in line: row[i] = line.split('_')[-1].strip()
                if block.get('tag_ib') in ['Bin11', 'Bin211', 'Bin25', 'Bin225'] and (
                        '2_tname_SSIO_BSCAN_SXX' in line and any(
                    keyword in line for keyword in ['ALL1', 'ALL0', 'VIXVOX', 'PULSE'])): bin_flag = True
            if block.get('tag_ib') in ['Bin11', 'Bin211', 'Bin25', 'Bin225']:
                print(row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                      row.get('3_partialwafid'), row.get('3_curibin'), row.get('3_chuckid'), probeID_list, )
                tv.insert(parent='', index='end', text='', values=(
                    row.get('3_tiuid'), sdx, row.get('3_cellid'), row.get('3_prttesterid'), operation, lot,
                    row.get('3_partialwafid'), row.get('3_curibin'), row.get('3_curfbin'), row.get('3_curfbin'),
                    row.get('3_chuckid'), fail_channel_list, probeID_list))
                faildie += 1
        

    file_in.close()
    os.remove(temp_file)
    fail_pins = ', '.join(set(str(pin) for pin in Pin))
    print("Fail Channel/Pin: " + fail_pins)
    hdm_t_pins = ' '.join(set(HDMT))
    df1 = df.assign(PIN_INDICATOR=1, PIN_SIZE=20)
    df1['Xiu'] = xiu
    if len(xiu) <= 10:
        df1['TH'] = 1
    else:
        df1.loc[df1['NET_NAME'].str.startswith('D1'), 'TH'] = 1
        df1.loc[df1['NET_NAME'].str.startswith('D2'), 'TH'] = 2
    for pin in set(Pin):
        df1.loc[df1["PIN_NUMBER"] == pin, "PIN_INDICATOR"] = pin
    PlotJcon(set(HDMT))
    
    Plots(df1)

    end_time = time.time()
    try:
        text_file = open(os.path.join(abspath, "Config/user_run_log.csv"), 'a')
    except:
        text_file = open(dname + "/Config/user_run_log.csv", 'a')
    total_time = end_time - start_time
    copying_time = copy_time - start_time
    execute_time = end_time - copy_time
    username = os.getlogin()
    # write string to file
    text_file.write(
        f"{username},{xiu},{flagBin},{fl_path},{hdm_t_pins},{fail_pins},{datetime.now().strftime('%m/%d/%Y %H:%M:%S')},{total_time},{copying_time},{execute_time}\n")

    # close file
    text_file.close()

	
def select_file():
    filetypes = (('All files', '*.xlsx'),('text files', '*.txt'))
    filename1 = fd.askopenfilename(title='Insert Pindef File', initialdir='/', filetypes=filetypes)
    filename2 = fd.askopenfilename(title='Insert TTB File', initialdir='/', filetypes=filetypes)
    # filename3 = fd.askopenfilename(title='Insert New Excel File', initialdir='/', filetypes=filetypes) #config file
    lbl2['text'] = (filename1)
    lbl6['text'] = (filename2)
    # lbl6['text'] = (filename2)
    xlsx1 = pd.ExcelFile(filename1)
    xlsx2 = pd.ExcelFile(filename2)
    # xlsx3 = pd.ExcelFile(filename3)
    return xlsx1, xlsx2

def Create_Config():

    xlsx1, xlsx2 = select_file()

    li = ['J0_1']
    f4 = xlsx2
    f4_sht = f4.sheet_names
    result_df = pd.DataFrame()
    for name in f4_sht:
        if name.startswith('TTB'):
            f4_col = f4.parse(name, usecols='A, B, C, D, E, F, I')
            df4_col = f4_col.loc[f4_col['REFDES'].isin(li)]
			
            df4_col['HDMT PIN#'] = pd.to_numeric(df4_col['HDMT PIN#'], errors='coerce')
            df4_col['HDMT PIN#'] = df4_col['HDMT PIN#'].astype('float64', errors='ignore')
            df4_col.loc[df4_col['HDMT PIN#'] != "", 'HDMT PIN#'] = df4_col.loc[df4_col['HDMT PIN#'] != "", 'HDMT PIN#'] * 1000
            result_df = pd.concat([result_df, df4_col], ignore_index=True)

    f2 = xlsx1
    f2_col = f2.parse('HDMT_PINDEF_PWR', usecols='B:D')
    f2_col.loc[f2_col['NetName'].astype(str).str.contains('_JCON'), 'Master'] = 'Master'
	
    #f2_col = f2_col.loc[f2_col['Master'].str.contains('Master', na=False) ]
    f2_col = f2_col.drop(['Master'], axis=1)

   
    f2_col.loc[f2_col['NetName'].astype(str).str.contains('_JCON'), 'NetName'] = f2_col['NetName'].astype(str).str.replace('_JCONN','')
    f2_col.loc[f2_col['NetName'].astype(str).str.contains('_JCON'), 'NetName'] = f2_col['NetName'].astype(str).str.replace('_JCON', '')


    # f2_col.to_csv('testConfig.csv',index = False)
    f2_new = f2_col.rename(columns={'Trace':'HDMT PIN#','NetName':'NET_NAME'})

    f2_new.loc[f2_new['HDMT PIN#'].astype(str).str.contains('JSLOT0'), 'HDMT PIN#'] = f2_new['HDMT PIN#'].astype(str).str.split('.').str[1]

    f2_new.loc[f2_new['HDMT PIN#'].astype(str).str.contains('JSLOT11'), 'HDMT PIN#'] = f2_new['HDMT PIN#'].astype(str).str[5] + f2_new['HDMT PIN#'].astype(str).str[6] + '0' + f2_new['HDMT PIN#'].astype(str).str.split('.').str[1]

    f2_new.loc[f2_new['HDMT PIN#'].astype(str).str.contains('J'), 'HDMT PIN#'] = f2_new['HDMT PIN#'].astype(str).str[1] + f2_new['HDMT PIN#'].astype(str).str[2] + '0' + f2_new['HDMT PIN#'].astype(str).str.split('.').str[1]

    f2_new['HDMT PIN#'] = f2_new['HDMT PIN#'].astype(int)
	
    
    
    #df4_col['HDMT PIN#'] = pd.to_numeric(df4_col['HDMT PIN#'], errors='coerce')
    #df4_col['HDMT PIN#'] = df4_col['HDMT PIN#'].astype('float64', errors='ignore')
	
    
    #df4_col.loc[df4_col['HDMT PIN#'] != "", 'HDMT PIN#'] = df4_col['HDMT PIN#']*1000


    inner_join = pd.merge(result_df,f2_new, on='NET_NAME', how='left')
    inner_join['HDMT PIN#'] = inner_join['HDMT PIN#_x'].where(inner_join['HDMT PIN#_x'].notnull(), inner_join['HDMT PIN#_y'])
    inner_join=inner_join.drop(['HDMT PIN#_x', 'HDMT PIN#_y', 'REFDES'], axis=1)
    

    inner_join.loc[(inner_join['NET_NAME'].astype(str).str.contains("HV"))& (~inner_join['NET_NAME'].str.contains("TC")) , 'PIN_NUMBER'] = inner_join['NET_NAME']
    inner_join.loc[(inner_join['NET_NAME'].astype(str).str.contains("HC")) & (~inner_join['NET_NAME'].str.contains("TC")), 'PIN_NUMBER'] = inner_join['NET_NAME']
    inner_join.loc[(inner_join['NET_NAME'].astype(str).str.contains("LC")) & (~inner_join['NET_NAME'].str.contains("TC")), 'PIN_NUMBER'] = inner_join['NET_NAME']
    inner_join.loc[(inner_join['NET_NAME'].astype(str).str.contains("HV")) & (~inner_join['NET_NAME'].str.contains("TC")), 'PIN_NAME'] = inner_join['NET_NAME']
    inner_join.loc[(inner_join['NET_NAME'].astype(str).str.contains("HC")) & (~inner_join['NET_NAME'].str.contains("TC")), 'PIN_NAME'] = inner_join['NET_NAME']
    inner_join.loc[(inner_join['NET_NAME'].astype(str).str.contains("LC")) & (~inner_join['NET_NAME'].str.contains("TC")), 'PIN_NAME'] = inner_join['NET_NAME']
    inner_join.loc[(inner_join['NET_NAME'].astype(str).str.contains("GND")) & (~inner_join['NET_NAME'].str.contains("TC")) & (inner_join['PIN_NUMBER'].str.contains("D1_")), 'NET_NAME'] = 'D1_'+ inner_join['NET_NAME']
    inner_join.loc[(inner_join['NET_NAME'].astype(str).str.contains("GND")) & (~inner_join['NET_NAME'].str.contains("TC")) & (inner_join['PIN_NUMBER'].str.contains("D2_")), 'NET_NAME'] = 'D2_'+ inner_join['NET_NAME']
    
    inner_join.loc[inner_join['PIN_NAME'].astype(str).str.contains('\[', na=False, regex=True), 'PIN_NAME'] = inner_join['PIN_NAME'].astype(str).str.replace('\[','', regex=True)
    inner_join.loc[inner_join['PIN_NAME'].astype(str).str.contains('\]', na=False, regex=True), 'PIN_NAME'] = inner_join['PIN_NAME'].astype(str).str.replace('\]','', regex=True)

    inner_join = inner_join.replace(pd.NA, np.nan).round({'HDMT PIN#':1})
	
    
    inner_join.to_csv('channel_XXXXX.csv',index = False)
    # f3 = xlsx3
    # with pd.ExcelWriter(f3, mode='w') as writer:
        # inner_join.to_excel(writer, sheet_name='config', index=False, startcol=0)

    showinfo(title='Message', message='Config file created')

	


root = Tk()
root.geometry('1200x1200')
root.title('Probe Identifier GUI Rev2.4.2')

# Create the main frame for the tabs
main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True, side='top', anchor='center')


# Create the notebook (tabs bar)
notebook = ttk.Notebook(main_frame)

# Add tabs to the notebook
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text='Probe Identifier')

tab2 = ttk.Frame(notebook)
notebook.add(tab2, text='Config Generator - NPI')

tab3 = ttk.Frame(notebook)
notebook.add(tab3, text='EZA Config Generator - NPI')

# Create labels and buttons inside tab3
label_NPI_EZA = tk.Label(tab3, text='EZA Config Generator NPI', font=('Helvetica', 10, 'underline'))
label_NPI_EZA.grid(column=3, row=0)


# Create labels and buttons inside tab2
label_NPI = tk.Label(tab2, text='Probe Identifier Config NPI', font=('Helvetica', 10, 'underline'))
label_NPI.grid(column=0, row=0)

lbl1 = tk.Label(tab2, text="Input Pindef File")
lbl1.grid(column=0,row=1)

lbl2 = tk.Label(tab2, text='---> None')
lbl2.grid(column=2,row=1)

lbl6 = tk.Label(tab2, text="Input TTB File")
lbl6.grid(column=0,row=2)

lbl6 = tk.Label(tab2, text='---> None')
lbl6.grid(column=2,row=2)



attach_button = ttk.Button(tab3, text="Attach File", command=attach_file)
attach_button.grid(column=3, row=2)

file_name_entry = ttk.Entry(tab3)
file_name_entry.grid(column=3, row=1)
file_name_entry.insert(0, "Insert Prod Name")


tab4 = ttk.Frame(notebook)
notebook.add(tab4, text='EZA')




# Pack the notebook to top-left corner
notebook.pack(expand=1, fill='both')

# Create the title label inside tab1
title_lb = Label(tab1, text='Probe Identifier', font=('Helvetica', 20, 'underline'))
title_lb.pack()

# Create the dropdown menu for selecting bins inside tab1
binning = StringVar(root)
binning.set('Select Bin')
bin_menu = OptionMenu(tab1, binning, *bin_list, command=callbackbin)
bin_menu.pack()

# Create the input text area inside tab1
inputtxt = Text(tab1, height=1, width=25, bg="light yellow")
inputtxt.pack()

# Create the "Run" button inside tab1
Button(tab1, text='Run', command=main).pack()


# Create the button inside tab2
open_button = ttk.Button(tab2, text='Create Config', command=Create_Config)
open_button.grid(column=0, row=3)






try:
    abspath = os.path.abspath(os.path.dirname(sys.executable))
    dname = os.path.abspath(os.path.dirname(sys.executable))
except:
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)

with open(os.path.join(dname, "Config\product_config_path.txt")) as config_file:
    config_path = config_file.readline()

# Define the filename of your image
filename = "Products.csv"
foldername = "SOC"

# Combine the directory and filename to get the full path
file_path = os.path.join(config_path, foldername, filename)


# Read the CSV file into a DataFrame
Product_file = pd.read_csv(file_path)

# Convert the DataFrame column to a list
Product_list = Product_file['Products'].tolist()



Product = StringVar(root)
Product.set('Select Product')
bin_menu1 = OptionMenu(tab4, Product, *Product_list, command=callbackProd)
bin_menu1.pack()

# Create the input text area inside tab1
inputtxt1 = Text(tab4, height=1, width=25, bg="light yellow")
inputtxt1.pack()

# Bind the <Return> event to the callback function
inputtxt1.bind("<Return>", on_enter_pressed)






# Define the filename of your image
filename = "guidelines.jpg"
foldername ="Config"

# Combine the directory and filename to get the full path
image_path = os.path.join(dname, foldername, filename)

print("Image path:", image_path)

image = Image.open(image_path)

width, height = image.size
new_width = int(width * 0.70)
new_height = int(height * 0.70)

# Resize the image to 85% of its original size
resized_image = image.resize((new_width, new_height))

photo = ImageTk.PhotoImage(resized_image)

# Create a label and set the image inside tab2
image_label = Label(tab2, image=photo)
image_label.grid(row=100, column=4, columnspan=3)
image_label.image = photo


# Define the filename of your image
filename = "EZA_Guidelines.jpg"

# Combine the directory and filename to get the full path
image_path = os.path.join(dname,foldername, filename)

print("Image path:", image_path)

image = Image.open(image_path)

width, height = image.size
new_width = int(width * 1)
new_height = int(height * 1)

# Resize the image to 85% of its original size
resized_image = image.resize((new_width, new_height))

photo = ImageTk.PhotoImage(resized_image)

# Create a label and set the image inside tab2
image_label = Label(tab3, image=photo)
image_label.grid(row=100, column=4, columnspan=3)
image_label.image = photo




# Create the Treeview and associated widgets inside tab1
tv = ttk.Treeview(tab1, columns=tuple(range(1, 14)), show='headings', height=10)
headings = ['|XIU|', '|SDX|', '|SDC|', '|HDS|', '|Opr|', '|Lot|', '|Tray|', '|Tbin|', '|SDSFB|', '|SDTFB|', '|TH|',
            '|HDMT_PIN|', '|PIN|']
for index, heading in enumerate(headings, start=1):
    tv.heading(index, text=heading)
    tv.column(index, width=100, stretch=YES, anchor=CENTER)

sb_y = Scrollbar(tab1, orient=VERTICAL, command=tv.yview)
sb_y.pack(side=RIGHT, fill=Y)
sb_x = Scrollbar(tab1, orient=HORIZONTAL, command=tv.xview)
sb_x.pack(side=BOTTOM, fill=X)

tv.config(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
sb_y.config(command=tv.yview)
sb_x.config(command=tv.xview)
tv.pack(expand=True, fill="both")



# Create the Treeview and associated widgets inside tab1
tv1 = ttk.Treeview(tab4, columns=tuple(range(1, 5)), show='headings', height=10)
headings = ['|DiePinName|', '|HDMTPin|', '|PinNumber|', '|DUT|']
for index, heading in enumerate(headings, start=1):
    tv1.heading(index, text=heading)
    tv1.column(index, width=20, stretch=YES, anchor=CENTER)

sb_y = Scrollbar(tab4, orient=VERTICAL, command=tv.yview)
sb_y.pack(side=RIGHT, fill=Y)
sb_x = Scrollbar(tab4, orient=HORIZONTAL, command=tv.xview)
sb_x.pack(side=BOTTOM, fill=X)

tv1.config(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
sb_y.config(command=tv.yview)
sb_x.config(command=tv.xview)
tv1.pack(expand=True, fill="both")


outputJconmain = None
outputProbeMap = None




try:
    abspath = os.path.abspath(os.path.dirname(sys.executable))
    dname = os.path.abspath(os.path.dirname(sys.executable))
except:
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)

with open(os.path.join(dname, "Config\product_config_path.txt")) as config_file:
    config_path = config_file.readline()
    #temp_path = os.path.join(dname, "Config\\temp_ituff\\")
    temp_path = r'C:\temp\temp_ituff'

isExist = os.path.exists(temp_path)
if not isExist: os.makedirs(temp_path)
#else: shutil.rmtree(temp_path) 
root.mainloop() 