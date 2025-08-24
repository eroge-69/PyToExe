import pathlib 
import pandas as pd 
import time

import tkinter as tk
from tkinter import filedialog




print('Introduced By Mahmoud Sadiek')

print('Please Enter Path Folder Directory')

pathinput = filedialog.askdirectory(title="Select a Folder")
#pathinput =  input()
dirpath =  pathlib.Path(pathinput)


print("Your Data Path Is  " + pathinput)


files =  list(dirpath.glob("**/*.XLSX"))


alldata =  []
for f in files :
    print("Reading" + '   '+ f.name)
    file =  pd.read_excel(f)
    file['Date'] =  f.name
    alldata.append(file)


print('converting dataframe ')
time.sleep(10)
alldatadf =  pd.concat(alldata).reset_index(drop=True)

print('exporting csv total data  ')
time.sleep(10)
alldatadf.to_csv('alldata.csv')

print('Done , please send instapay 01091237000   :D ')
time.sleep(300)


