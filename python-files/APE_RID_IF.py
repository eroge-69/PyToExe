import xlwings as xw
import pandas as pd
import numpy as np
import tkinter as tk  
from tkinter import filedialog  



# Create a Tkinter root window  
root = tk.Tk()  
root.withdraw()  # Hide the root window  
  
# Prompt the user to select a file  
file_name = filedialog.askopenfilename(title="Select a file", filetypes=[("All Files", "*.*")])  

root.destroy()

#file_name = "APE_MP_032025.xlsx"
file_name_new = file_name[:len(file_name)-5]+"_riders_IF_test.xlsx"

workbook = xw.Book(file_name)
ws_UL_Riders = workbook.sheets["UL_Riders"]
ws_UL = workbook.sheets["UL_GenT"]

range_UL_Riders = 'D31:CW30000'
range_UL = 'C29:DM30000'


UL_Riders = ws_UL_Riders.range(range_UL_Riders).options(pd.DataFrame, index=False, header=True).value
UL_GenT = ws_UL.range(range_UL).options(pd.DataFrame, index=False, header=True).value

UL_Riders_cleaned = UL_Riders.dropna()
UL_GenT_cleaned = UL_GenT.dropna()

max_entry_month = UL_Riders_cleaned['Entry_Month'].max()


UL_Riders_cleaned = UL_Riders_cleaned[UL_Riders_cleaned['Entry_Month'] == max_entry_month]

UL_Riders_cleaned["Component_Identifier_MC"] = np.floor(UL_Riders_cleaned["Component_Identifier"] / 100)

lookup_dict = dict(zip(UL_GenT_cleaned['Component_Identifier'], UL_GenT_cleaned['Component_Identifier']))
UL_Riders_cleaned['Component_Identifier_UL'] = UL_Riders_cleaned['Component_Identifier_MC'].map(lookup_dict)
UL_Riders_cleaned = UL_Riders_cleaned.rename(columns={'Component_Identifier_UL': 'NB/IF'})
UL_Riders_cleaned['NB/IF'] = UL_Riders_cleaned['NB/IF'].fillna(0)
UL_Riders_cleaned = UL_Riders_cleaned[UL_Riders_cleaned['NB/IF'] == 0]

range_UL_Riders_to_clear = 'D31:CY30000'
ws_UL_Riders.range(range_UL_Riders_to_clear).clear_contents() 
ws_UL_Riders.range('D31').options(index=False, header=True).value = UL_Riders_cleaned 




ws_Trad_Riders = workbook.sheets["Trad_Riders"]
range_Trad_Riders = 'D99:CW30000'
Trad_Riders = ws_Trad_Riders.range(range_Trad_Riders).options(pd.DataFrame, index=False, header=True).value
Trad_Riders_cleaned = Trad_Riders.dropna()
max_entry_month = Trad_Riders_cleaned['Entry_Month'].max()
Trad_Riders_cleaned = Trad_Riders_cleaned[Trad_Riders_cleaned['Entry_Month'] == max_entry_month]
Trad_Riders_cleaned["Component_Identifier_MC"] = np.floor(Trad_Riders_cleaned["Component_Identifier"] / 100)

ws_END_3_5 = workbook.sheets["END_3_5"]
ws_END_3_5_SP = workbook.sheets["END_3_5_SP"]
ws_Health_RO = workbook.sheets["Health_RO"]
ws_Term_3_5 = workbook.sheets["Term_3_5"]
ws_TF_3_5 = workbook.sheets["TF_3_5"]

range_END_3_5 = 'C30:DB30000'
range_END_3_5_SP = 'C16:U30000'
range_Health_RO = 'C18:U30000'
range_Term_3_5 = 'C42:DB30000'
range_TF_3_5 = 'C17:DB30000'


END_3_5 = ws_END_3_5.range(range_END_3_5).options(pd.DataFrame, index=False, header=True).value
END_3_5_SP = ws_END_3_5_SP.range(range_END_3_5_SP).options(pd.DataFrame, index=False, header=True).value
Health_RO = ws_Health_RO.range(range_Health_RO).options(pd.DataFrame, index=False, header=True).value
Term_3_5 = ws_Term_3_5.range(range_Term_3_5).options(pd.DataFrame, index=False, header=True).value
TF_3_5 = ws_TF_3_5.range(range_TF_3_5).options(pd.DataFrame, index=False, header=True).value

END_3_5_cleaned = END_3_5.dropna()
END_3_5_SP_cleaned = END_3_5_SP.dropna()
Health_RO_cleaned = Health_RO.dropna()
Term_3_5_cleaned = Term_3_5.dropna()
TF_3_5_cleaned = TF_3_5.dropna()

lookup_dict_END_3_5 = dict(zip(END_3_5_cleaned['Component_Identifier'], END_3_5_cleaned['Component_Identifier']))
lookup_dict_END_3_5_SP = dict(zip(END_3_5_SP_cleaned['Component_Identifier'], END_3_5_SP_cleaned['Component_Identifier']))
lookup_dict_Health_RO = dict(zip(Health_RO_cleaned['Component_Identifier'], Health_RO_cleaned['Component_Identifier']))
lookup_dict_Term_3_5 = dict(zip(Term_3_5_cleaned['Component_Identifier'], Term_3_5_cleaned['Component_Identifier']))
lookup_dict_TF_3_5 = dict(zip(TF_3_5_cleaned['Component_Identifier'], TF_3_5_cleaned['Component_Identifier']))


Trad_Riders_cleaned['Component_Identifier_END_3_5'] = Trad_Riders_cleaned['Component_Identifier_MC'].map(lookup_dict_END_3_5)
Trad_Riders_cleaned = Trad_Riders_cleaned.rename(columns={'Component_Identifier_END_3_5': 'END_3_5'})
Trad_Riders_cleaned['END_3_5'] = Trad_Riders_cleaned['END_3_5'].fillna(0)

Trad_Riders_cleaned['Component_Identifier_END_3_5_SP'] = Trad_Riders_cleaned['Component_Identifier_MC'].map(lookup_dict_END_3_5_SP)
Trad_Riders_cleaned = Trad_Riders_cleaned.rename(columns={'Component_Identifier_END_3_5_SP': 'END_3_5_SP'})
Trad_Riders_cleaned['END_3_5_SP'] = Trad_Riders_cleaned['END_3_5_SP'].fillna(0)


Trad_Riders_cleaned['Component_Identifier_Health_RO'] = Trad_Riders_cleaned['Component_Identifier_MC'].map(lookup_dict_Health_RO)
Trad_Riders_cleaned = Trad_Riders_cleaned.rename(columns={'Component_Identifier_Health_RO': 'Health_RO'})
Trad_Riders_cleaned['Health_RO'] = Trad_Riders_cleaned['Health_RO'].fillna(0)

Trad_Riders_cleaned['Component_Identifier_Term_3_5'] = Trad_Riders_cleaned['Component_Identifier_MC'].map(lookup_dict_Term_3_5)
Trad_Riders_cleaned = Trad_Riders_cleaned.rename(columns={'Component_Identifier_Term_3_5': 'Term_3_5'})
Trad_Riders_cleaned['Term_3_5'] = Trad_Riders_cleaned['Term_3_5'].fillna(0)

Trad_Riders_cleaned['Component_Identifier_TF_3_5'] = Trad_Riders_cleaned['Component_Identifier_MC'].map(lookup_dict_TF_3_5)
Trad_Riders_cleaned = Trad_Riders_cleaned.rename(columns={'Component_Identifier_TF_3_5': 'TF_3_5'})
Trad_Riders_cleaned['TF_3_5'] = Trad_Riders_cleaned['TF_3_5'].fillna(0)


Trad_Riders_cleaned['NB/IF'] = Trad_Riders_cleaned['END_3_5'] + Trad_Riders_cleaned['END_3_5_SP']+Trad_Riders_cleaned['Health_RO']+Trad_Riders_cleaned['Term_3_5']+Trad_Riders_cleaned['TF_3_5']
Trad_Riders_cleaned = Trad_Riders_cleaned[Trad_Riders_cleaned['NB/IF'] == 0]

Trad_Riders_cleaned = Trad_Riders_cleaned.iloc[:, :-7]


range_Trad_Riders_to_clear = 'D100:CW30000'
ws_Trad_Riders.range(range_Trad_Riders_to_clear).clear_contents() 
ws_Trad_Riders.range('D99').options(index=False, header=True).value = Trad_Riders_cleaned



workbook.save(file_name_new)

workbook.close()