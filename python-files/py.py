import pandas as pd

# Charger les fichiers
df1 = pd.read_excel('Caisse dépense ACB.xlsx', usecols=['Libellé', 'Date'])
df2 = pd.read_excel('Caisse dépense NB.xlsx', usecols=['Libellé', 'Date'])

# Étape 1: Identifier les libellés communs et uniques
libelles_commun = set(df1['Libellé']).intersection(set(df2['Libellé']))
libelles_unique_df1 = set(df1['Libellé']) - set(df2['Libellé'])
libelles_unique_df2 = set(df2['Libellé']) - set(df1['Libellé'])

# Étape 2: Préparer les données avec libellés ET dates
def prepare_data(df, libelles):
    return df[df['Libellé'].isin(libelles)].sort_values(['Libellé', 'Date'])

# Données pour l'export
data_commun_df1 = prepare_data(df1, libelles_commun)
data_commun_df2 = prepare_data(df2, libelles_commun)
data_unique_df1 = prepare_data(df1, libelles_unique_df1)
data_unique_df2 = prepare_data(df2, libelles_unique_df2)

# Export vers Excel
with pd.ExcelWriter('Resultats_Comparaison_Integree.xlsx') as writer:
    # Libellés communs (avec dates des deux fichiers)
    data_commun_df1.to_excel(writer, sheet_name='Communs_F1', index=False)
    data_commun_df2.to_excel(writer, sheet_name='Communs_F2', index=False)
    
    # Libellés uniques avec leurs dates intégrées
    data_unique_df1.to_excel(writer, sheet_name='Uniques_F1', index=False)
    data_unique_df2.to_excel(writer, sheet_name='Uniques_F2', index=False)

    # Synthèse comparative
    pd.DataFrame({
        'Type': ['Libellés communs', 'Libellés uniques F1', 'Libellés uniques F2'],
        'Nombre': [len(libelles_commun), len(libelles_unique_df1), len(libelles_unique_df2)]
    }).to_excel(writer, sheet_name='Synthèse', index=False)

print("Analyse terminée. Fichier généré: 'Resultats_Comparaison_Integree.xlsx'")