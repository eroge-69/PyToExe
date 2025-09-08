#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns


# In[2]:


import pandas as pd
file_path = 'Checkpoint Report for 2025-11-08 to 2025-17-08.xlsx'
dataset = pd.read_excel(file_path)
print(dataset.head())


# In[3]:


context = dataset.to_string(index=False) # Or select specific columns and format them


# In[4]:


import google.generativeai as gemini
gemini.configure(api_key="AIzaSyAF7czNPbBwmukDgy4FrQ2j_GB7Cy3ptRI")
model = gemini.GenerativeModel('gemini-2.5-flash')


# In[5]:


question = "which date time Jordan Anderson visited Yellow 4?"
response = model.generate_content(f'Data: {context}\n\nQuestion: {question}')
print(response.text)


# In[ ]:




