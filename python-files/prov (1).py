import pandas as pd
import glob
import os
from dateutil import parser
import numpy as np
path = r'D:\doubles\Старые базы'
all_files = glob.glob(os.path.join(path, "*.xlsx"))
data = pd.concat((pd.read_excel(f,dtype={'phone':str}) for f in all_files), ignore_index=True)
l = data['phone'].to_list()
path = r'D:\doubles\Базы для сравнения'
all_files = glob.glob(os.path.join(path, "*.xlsx"))
check = pd.concat((pd.read_excel(f,dtype={'phone':str}) for f in all_files), ignore_index=True)
doubles = check.query('phone ==@l').reset_index(drop = True)
doubles['повторы']=1
doubles_p = doubles.pivot_table(index = 'phone', values =  'повторы', aggfunc = 'sum').reset_index()
doubles_p.to_excel(r'D:\doubles\итог.xlsx', index = False)