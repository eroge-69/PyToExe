import pandas as pd
import unicodedata
import matplotlib.pyplot as plt
import glob

class StartPlanilhas:
    def __init__(self, mes):
        
    
        if not mes.isdigit() or len(mes) != 2:
            raise ValueError("Mês inválido. Por favor, insira um mês válido no formato MM.")
        self.mes = mes

    def Start(self):
        try:

            arquivos_xlsx = glob.glob('*.xlsx')
            if not arquivos_xlsx:
                print("Nenhuma planilha .xlsx encontrada na pasta.")
                return None

            
            df = pd.read_excel(arquivos_xlsx[0], sheet_name=None)
            print(f"Carregando: {arquivos_xlsx[0]}")
            return df
        except Exception as e:
            print(f"Erro ao carregar as planilhas: {e}")
            return None

    def remover_acentos(self, txt):
        if not isinstance(txt, str):
            txt = str(txt)
        return ''.join(
            c for c in unicodedata.normalize('NFD', txt)
            if unicodedata.category(c) != 'Mn'
        )

    def GerarPlanilha(self, retorno):

        primeira_aba = list(retorno.keys())[0]
        df = retorno[primeira_aba]

    
        df['Status'] = (
            df['Status']
            .astype(str)
            .str.strip()
            .str.lower()
            .apply(self.remover_acentos)
        )


        df['Data de Entrada'] = pd.to_datetime(df['Data de Entrada'], format='%d/%m/%Y', errors='coerce')

      
        mes_int = int(self.mes)
        df_mes = df[df['Data de Entrada'].dt.month == mes_int]

        
        encerrados = df_mes['Status'].str.contains('encerrad').sum()
        acompanhamento = df_mes['Status'].str.contains('acompanh').sum()

        print(f"Encerrados no mês {self.mes}:", encerrados)
        print(f"Acompanhamento no mês {self.mes}:", acompanhamento)

       
        status_labels = ['Encerrados', 'Acompanhamento']
        status_counts = [encerrados, acompanhamento]
        
        plt.figure(num="Gráfico da Planilha")  
        plt.bar(status_labels, status_counts, color=['green', 'blue'])
        plt.xlabel('Status')
        plt.ylabel('Quantidade')
        plt.title(f'Contagem de Status - Mês {self.mes}')
        plt.show()

print(""""
██████  ██    ██             █████  ██████  ██████  ██  █████  ███    ██  ██████       █████      ███    ██  ██████  ██  ██████  ██      ███████ ████████ ████████  ██████  
██   ██  ██  ██      ██     ██   ██ ██   ██ ██   ██ ██ ██   ██ ████   ██ ██    ██     ██   ██     ████   ██ ██       ██ ██    ██ ██      ██         ██       ██    ██    ██ 
██████    ████              ███████ ██   ██ ██████  ██ ███████ ██ ██  ██ ██    ██     ███████     ██ ██  ██ ██   ███ ██ ██    ██ ██      █████      ██       ██    ██    ██ 
██   ██    ██        ██     ██   ██ ██   ██ ██   ██ ██ ██   ██ ██  ██ ██ ██    ██     ██   ██     ██  ██ ██ ██    ██ ██ ██    ██ ██      ██         ██       ██    ██    ██ 
██████     ██               ██   ██ ██████  ██   ██ ██ ██   ██ ██   ████  ██████      ██   ██     ██   ████  ██████  ██  ██████  ███████ ███████    ██       ██     ██████  
                                                                                                                                                                            
                                                                                                                                                                              """)
mes = input("DIGITE O MES APENAS EM NUMERO EXEMPLO: 06 PARA JUNHO, NAO DIGITE NADA DIFERENTE DISSO!!!\n")
cls = StartPlanilhas(mes)
retorno = cls.Start()
if retorno:
    cls.GerarPlanilha(retorno)
else:
    print("Erro ao carregar a(s) planilha(s).")