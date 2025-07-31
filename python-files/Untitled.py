#!/usr/bin/env python
# coding: utf-8

# In[20]:


from re import finditer
import pandas as pd
from datetime import datetime
from locale import setlocale
pattern1 = '&nbsp;'
pattern2 = r"9..00\d{7}"
pattern3 = r"\d{2} janvier \d{4}|\d{2} février \d{4}|\d{2} mars \d{4}|\d{2} avril \d{4}|\d{2} mai \d{4}|\d{2} juin \d{4}|\d{2} juillet \d{4}|\d{2} août \d{4}|\d{2} septembre \d{4}|\d{2} octobre \d{4}|\d{2} novembre \d{4}|\d{2} décembre \d{4}"

with open('Vos factures, Espace Client SFR Business.html', 'r') as in_file: 
    C=[]
    Montant = []
    A = in_file.read()
    positions = [match.start() for match in finditer(pattern1, A)]
    B = [A[i-9:i] for i in positions]
    
    for i in range(0,len(B)):
        espace = [match.start() for match in finditer(" |¯", B[i])]
        E = B[i]
        Montant.append(E[espace[0]+1:].replace("â€¯"," "))
    #print(Montant)
    positions = [match.start() for match in finditer(pattern2, A)]
    Facture = [A[i:i+12].strip() for i in positions]
    #print(Facture,len(Facture))
    positions = [match.start() for match in finditer(pattern3, A)]
    Date = [datetime.strptime(A[i:i+15].strip(),"%d %B %Y").strftime("%d/%m/%Y") for i in positions]
    #print(Date,len(Date))
col1 = "N° facture"
col2 = "Montant"
col3 = "Date"
data= pd.DataFrame({col1:Facture, col2:Montant, col3:Date})
data.to_excel("Factures_SFR.xlsx",sheet_name="sheet1", index=False)


# In[ ]:


import datetime as dt
pattern3 = r"\d{2} janvier \d{4}|\d{2} février \d{4}|\d{2} mars \d{4}|\d{2} avril \d{4}|\d{2} mai \d{4}|\d{2} juin \d{4}|\d{2} juillet \d{4}|\d{2} août \d{4}|\d{2} septembre \d{4}|\d{2} octobre \d{4}|\d{2} novembre \d{4}|\d{2} décembre \d{4}"
with open('Vos factures, Espace Client SFR Business.html', 'r') as in_file:
    A = in_file.read()
    positions = [match.start() for match in re.finditer(pattern3, A)]
    Date = [dt.strptime(A[i:i+15].strip(),'% for i in positions]


# In[16]:


from datetime import datetime
from locale import setlocale
setlocale(locale.LC_ALL, 'fr_FR')
A = "25 décembre 2024"
B = datetime.strptime(A,"%d %B %Y").strftime("%d/%m/%Y")
print(B)


# In[14]:


print(B)


