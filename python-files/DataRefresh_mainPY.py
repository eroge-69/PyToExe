#!/usr/bin/env python
# coding: utf-8

# # Refresh Data

# ## Run updates as needed

# In[1]:


# pip install nbformat nbclient


# ## Run Scripts

# ### Import Data

# In[2]:


# Import Assessor Data
get_ipython().run_line_magic('run', './importData.py')


# ### Clean Data

# In[3]:


#Clean Assessor Data
get_ipython().run_line_magic('run', './CleanAssessor.py')


# In[4]:


#Lead project Data Clean
get_ipython().run_line_magic('run', './LeadRegistryCleanScript.py')


# In[5]:


#Combine EBL into Files for Analysis
get_ipython().run_line_magic('run', './CombineAllEBLData_SL.py')


# In[ ]:


#Clean Lead Project Stats
get_ipython().run_line_magic('run', './CleanLeadProjectStats.py')


# In[ ]:


#Master File EM Review
get_ipython().run_line_magic('run', './MasterFileEMReview.py')


# In[ ]:


#Create Assessor Data without properties withpositive tests or alredy recieved grant.
get_ipython().run_line_magic('run', './FinalDataClean.py')


# ### Model

# In[ ]:


# Run the Positive Unlabeled prediction model, trains model and runs against assessor data.
get_ipython().run_line_magic('run', './Prediction_Model.py')

