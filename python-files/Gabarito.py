#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Nome: Milena Karie Silva Neco
quest = input("Número de questões:")
gabar = input("Gabarito:")
resp = input("Respostas:")

numq = int(quest)
nota = 0

for x in range (numq):
        if gabar[x] == resp[x]:
            nota+= 1

print (nota)


# In[ ]:




