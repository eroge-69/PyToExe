import pandas as pd

# Dados iniciais
data = {
    'CMV (R$)': [288.16, 288.16],
    'PIS (%)': [1.65, 1.65],
    'COFINS (%)': [7.60, 7.60],
    'Preço Alvo (R$)': [440.00, 520.00]
}

# Criar DataFrame
df = pd.DataFrame(data)

# Calcular LL considerando PIS e COFINS
df['LL Calculado (%)'] = (1 - df['CMV (R$)'] / (df['Preço Alvo (R$)'] * (1 - df['PIS (%)']/100) * (1 - df['COFINS (%)']/100))) * 100

# Salvar em Excel
df.to_excel('/mnt/data/LL_Calculado.xlsx', index=False)
df
