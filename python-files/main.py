# %%
import os
import pandas as pd
import plotly.express as px

tabela = pd.read_excel('ruptura.xls')
#display(tabela)
quantidade_vendida_teorica = tabela['Quantidade Vendida Teórica'].sum()
venda_perdida_efetiva = tabela['Venda Perdida Efetiva'].sum()
venda_potencial = tabela['Potencial de Venda'].sum()

venda_realizada = tabela['Venda do Período'].sum()

col1 = ['Venda Perdida Efetiva.', 'Potencial de Venda.', 'Venda do Período.']
#'Quantidade Vendida Teórica.'

for coluna in tabela.columns:
    grafico = px.histogram(tabela, x = col1 , y = [venda_perdida_efetiva, venda_potencial, venda_realizada], color = ['Venda Perdida Efetiva.', 'Potencial de Venda.', 'Venda do Período.'])
    grafico.update_layout(bargap=0.2)
#quantidade_vendida_teorica 'Quantidade Vendida Teórica.'

grafico.write_html('Grafico.html', auto_open = True)

# %%
