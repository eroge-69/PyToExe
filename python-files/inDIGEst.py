#!/usr/bin/env python
# coding: utf-8

# In[293]:


import csv
import os
import pandas as pd

chemin_entree = 'd:\\leotard-b\\OneDrive - Région Sud\\Bureau\\Jibé\\Entrée'
os.chdir(chemin_entree)


dataUsages = pd.read_csv('usages.csv', sep=";", encoding = ' utf-8', dtype=str, index_col=False)
dataUsages.drop(['Datetime','Date','Heure','Jour','Conducteur', 'Matricule', 'Plaque','Vehicule', 'Smartphone',\
           'Exploitant contractuel', 'Exploitant', 'Itinéraire', 'Sens', 'Course', 'Ref ext course',\
           'Historique', 'Provenance de l\'usage', 'Identifiant de vente', 'Position valideur', 'Type valideur',\
           'Type de validation', 'Numéro de dossier usager', 'Identifiant de support', 'Sélection des titres', \
           'Code arrêt montée réelle','Code arrêt montée théorique','Arrêt montée théorique','Code zone montée théorique',\
          'Code arrêt descente théorique','Arrêt descente théorique'], axis = 1, inplace = True)
#dataUsages.head(50)





# In[294]:


chemin_reference = 'd:\\leotard-b\\OneDrive - Région Sud\\Bureau\\Jibé\\Référence'
os.chdir(chemin_reference)

dataEpic = pd.read_csv('EPIC_csv.csv', sep=";", encoding = 'latin-1', dtype=str, index_col=False)

#dataEpic.head(50)



# In[295]:


mergence = pd.merge(dataUsages, dataEpic, how='left', left_on='Code zone montée réelle', right_on='CODGEO')
mergence.drop(['CODGEO','EPCI','DEP','REG'], axis = 1, inplace = True)
mergence = mergence[mergence['LIBEPCI'].notna()]
#mergence.head(50)


# In[296]:


chemin_reference = 'd:\\leotard-b\\OneDrive - Région Sud\\Bureau\\Jibé\\Référence'
os.chdir(chemin_reference)
dataScol = pd.read_csv('Scolaires_csv.csv', sep=";", encoding = 'latin-1', dtype=str, index_col=False)
dataAbo = pd.read_csv('Abonnements_csv.csv', sep=";", encoding = 'latin-1', dtype=str, index_col=False)
dataOccas = pd.read_csv('Occasionnels_csv.csv', sep=";", encoding = 'latin-1', dtype=str, index_col=False)


# In[297]:


mergencev1 = pd.merge(mergence, dataScol, how='left', left_on='Réf. usage', right_on='REF_USAGE1')
#mergencev1['PRODUIT_SCOLAIRE'] = mergencev1['PRODUIT_SCOLAIRE'].fillna("Non pris en compte")

mergencev2 = pd.merge(mergencev1, dataAbo, how='left', left_on='Réf. usage', right_on='REF_USAGE2')
#mergencev2['PRODUIT_ABONNEMENT'] = mergencev2['PRODUIT_ABONNEMENT'].fillna("Non pris en compte")

mergencev3 = pd.merge(mergencev2, dataOccas, how='left', left_on='Réf. usage', right_on='REF_USAGE3')
#mergencev3['PRODUIT_OCCASIONNEL'] = mergencev3['PRODUIT_OCCASIONNEL'].fillna("Non pris en compte")

mergencev3.drop(['REF_USAGE1','REF_USAGE2','REF_USAGE3'], axis = 1, inplace = True)
mergencev3['Colonne_id'] = range(1, len(mergencev3) + 1)
#mergencev3.head()


# In[298]:


chemin_sortie = 'd:\\leotard-b\\OneDrive - Région Sud\\Bureau\\Jibé\\Sortie'
os.chdir(chemin_sortie)
mergencev3.to_csv('export.csv', sep='\t', encoding='latin-1', index=False, header=True)


# In[299]:


mergencev3 = pd.pivot_table(mergencev3, values=['PRODUIT_SCOLAIRE','PRODUIT_ABONNEMENT','PRODUIT_OCCASIONNEL'], index=['Réseau', 'Ligne', 'LIBEPCI'],
                      	aggfunc={'PRODUIT_SCOLAIRE': ['count'],'PRODUIT_ABONNEMENT': ['count'],'PRODUIT_OCCASIONNEL':['count']})



mergencev4 = mergencev3


# In[300]:


mergencev4


# In[301]:


dataExcel = pd.ExcelWriter('ExportJibé_EPCI.xlsx')
mergencev4.to_excel(dataExcel)
dataExcel.close()
print('Le café est terminé.')


# In[ ]:




