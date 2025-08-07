#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import glob
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d


# In[2]:


def devices_df(file):
    ''' Separate the file in different dataframes of different devices
        takes dictionary of excel file data with key as sheet names and values as dataframs of device data
        returns data, total_devices
        data is list of dataframes with iv data as [device 1, device 2, .... ] 
    '''
    total_devices = len(file.keys())-2
    data=[]
    # For all sheets remove comment
    # data  = [df for df in file.values()]

    for key, val in file.items():
        if key == 'Data' or key[0] == 'A':
            data.append(val)

    return data, total_devices


# In[3]:


def analyze_iv(data, area_cm2):
        ''' Calculating values from IV charectoristic given
            
        '''
       
        V = data["AnodeV"].to_numpy()
        I = data["AnodeI"].to_numpy()

        # Power and Maximum Power Point (MPP)
        P = V * I*-1
        idx_mpp = np.argmax(P)
        V_mpp = V[idx_mpp]
        I_mpp = I[idx_mpp]
        P_max = abs(P[idx_mpp])
                   
        # Voc (interpolated where I = 0)
        Voc = np.float64(interp1d(I, V, bounds_error=False, fill_value="extrapolate")(0))

        # Jsc (interpolated where V = 0), convert to mA/cm²
        Isc = abs(interp1d(V, I, bounds_error=False, fill_value="extrapolate")(0))*1000
        Jsc = Isc/area_cm2
    
        # Fill Factor (FF %)
        FF = abs((V_mpp * I_mpp) / (Voc * Isc /1000) * 100)

        # Power Conversion Efficiency (PCE %), assuming 100 mW/cm² input
        Pin = 100  # mW/cm²
        PCE = P_max *1000/ (Pin * area_cm2) * 100

        # Series Resistance (Rs), near Voc
        
        v0 = int(arrgument_find(V))
        i0 = int(arrgument_find(I))
        
        Rs = abs(1 / np.polyfit(V[i0-2:i0+2], I[i0-2:i0+2], 1)[0]) * area_cm2

        # Shunt Resistance (Rsh), near Jsc
        Rsh = abs(1 / np.polyfit(V[v0-2:v0+2], I[v0-2:v0+2], 1)[0]) * area_cm2

        return {
            
            "Voc (V)": Voc,
            "Jsc (mA/cm²)": Jsc,
            "Isc (mA)" : Isc,
            "Pmpp (mW)" : P_max*1000,
            "Fill Factor (%)": FF,
            "PCE (%)": PCE,
            "Rs (Ω·cm²)": Rs,
            "Rsh (Ω·cm²)": Rsh,
            #"v0":v0,"i0":i0
        }


# In[4]:


def fwd_rev_seperation(df):

    fwd_df=df.iloc[:int(len(df)/2)]
    rev_df=df.iloc[int(len(df)/2):]

    return fwd_df, rev_df


# In[5]:


def arrgument_find(V):
        
    signs = np.sign(V)
    
    # To handle zero values (e.g., [1, 0, -1]), forward fill signs to preserve crossings
    signs[signs == 0] = np.nan
    signs = pd.Series(signs).ffill().values

    # Detect where sign changes
    sign_change = np.diff(signs)
    crossing_indices = np.where(sign_change != 0)[0] + 1  # +1 to point to the crossing index

    #print (type(crossing_indices))
    return crossing_indices[0]


# In[6]:


def calculate_devices_in_sheet(df):
    
    area = 0.1
    # separating appends in list of dataframes and number of devices
    data, n = devices_df(df)
    
    fwd_lst=[]
    rev_lst=[]
    histres=[]
    devi = []
    # Separating forward and reverse and calculating
    for i in range(0,n):
    
        fwd_df, rev_df = fwd_rev_seperation(data[i])
    
        fwd = analyze_iv(fwd_df,area)
        rev = analyze_iv(rev_df,area)
    
        histres.append((rev['PCE (%)']-fwd['PCE (%)'])/rev['PCE (%)'])
        devi.append(f'Device {i+1}')
        
        fwd_lst.append(fwd.values())
        rev_lst.append(rev.values())
    
    
    # putting in dataframe
    
    df_fwd = pd.DataFrame(data=fwd_lst,columns=[val+'_f' for val in list(fwd.keys())]) 
    df_rev = pd.DataFrame(data=rev_lst,columns=[val+'_b' for val in list(fwd.keys())])
    df_final_values = pd.concat([df_fwd,df_rev],axis=1)
    df_final_values['Histresis']=histres
    df_final_values.insert(0,column='Device_Pixal',value=devi)
    return df_final_values


# In[7]:


def process_all_files(folder_path, output_file_path):
    txt_files = glob.glob(os.path.join(folder_path, "*.xls"))
    print(f"🔍 Found {len(txt_files)} files in: {folder_path}")

    results = []
    for file_path in txt_files:
        
        print(f"⚙️  Processing: {os.path.basename(file_path)}")
        df = pd.read_excel(file_path,sheet_name=None)
                
        data = calculate_devices_in_sheet(df)
        data['File'] = file_path.split("\\")[-1]
                
        results.append(data)
    
        final_results = pd.concat(results)
    final_results.to_excel("output.xlsx")
    


# In[8]:


in_path = input(f'Give path of files')
out_path = in_path
process_all_files(in_path, output_file_path=out_path)


# In[ ]:





# In[ ]:




