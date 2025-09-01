import pandas as pd

def consolidar_em_uma_coluna(input_file, output_file):
    # Carregar os dados do arquivo Excel
    df = pd.read_excel(input_file)
    
    # Criar uma lista para armazenar os dados consolidados
    dados_consolidados = []
    
    # Iterar pelas colunas e adicionar as informações de cada clube
    for coluna in df.columns:
        # Extrair o código e nome do clube corretamente
        coluna_split = coluna.split(' - ')  # Dividir apenas pelo " - "
        
        if len(coluna_split) == 2:
            clube_codigo = coluna_split[0].strip()  # Parte do código, ex: "DE001"
            clube_nome = coluna_split[1].strip()    # Nome do clube, ex: "FC Köln"
        else:
            # Caso a coluna não siga o padrão esperado (código - nome)
            clube_codigo = coluna.strip()
            clube_nome = ""
        
        # Adicionar o nome completo do clube
        dados_consolidados.append(f"{clube_codigo} - {clube_nome}")  # Ex: "DE001 - FC Köln"
        
        # Adicionar os eventos do clube, sem incluir NaN
        for valor in df[coluna]:
            if pd.notna(valor):  # Verifica se o valor não é NaN
                dados_consolidados.append(valor)

    # Converter a lista de dados consolidados para um DataFrame
    df_consolidado = pd.DataFrame(dados_consolidados, columns=["Dados"])

    # Salvar o DataFrame consolidado em um novo arquivo Excel
    df_consolidado.to_excel(output_file, index=False)


# Exemplo de uso da função
input_file = r'C:\Users\DT\Desktop\yyyy.xlsx'  # Substitua pelo caminho do seu arquivo Excel de entrada
output_file = r'C:\Users\DT\Desktop\xlsxnovo_arquivo.xlsx'  # Caminho do arquivo de saída
consolidar_em_uma_coluna(input_file, output_file)
