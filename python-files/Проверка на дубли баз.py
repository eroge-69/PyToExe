#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
import os
from dateutil import parser
import numpy as np


# In[2]:


path = r'D:\doubles\Старые базы'
all_files = glob.glob(os.path.join(path, "*.xlsx"))
data = pd.concat((pd.read_excel(f,dtype={'phone':str}) for f in all_files), ignore_index=True)


# In[3]:


data


# In[4]:


l = data['phone'].to_list()


# In[5]:


path = r'D:\doubles\Базы для сравнения'
all_files = glob.glob(os.path.join(path, "*.xlsx"))
check = pd.concat((pd.read_excel(f,dtype={'phone':str}) for f in all_files), ignore_index=True)


# In[6]:


check


# In[7]:


doubles = check.query('phone ==@l').reset_index(drop = True)


# In[8]:


doubles


# In[9]:


doubles['повторы']=1


# In[10]:


doubles


# In[13]:


doubles_p = doubles.pivot_table(index = 'phone', values =  'повторы', aggfunc = 'sum').reset_index()


# In[14]:


doubles_p


# In[15]:


doubles_p.to_excel(r'D:\doubles\итог.xlsx', index = False)


# In[ ]:




