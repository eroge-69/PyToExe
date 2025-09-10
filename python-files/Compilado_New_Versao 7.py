import os
import requests
import xlsxwriter
import datetime
import time
import lxml.html
from requests.exceptions import HTTPError
import sys

# Funções para cada script
def script_web_scraping():
    #-------------MODULO BARRA DE PROGRESSO
    def progressbar(it, prefix="", size=60, output=sys.stdout):
        count = len(it)
        start_time = time.time()  # Captura o tempo inicial
        global last_iteration_time  # Declarando a variável como global
        last_iteration_time = start_time  # Captura o tempo da última iteração
        def show(j):
            global last_iteration_time  # Declarando a variável como global
            elapsed_time = time.time() - start_time  # Calcula o tempo decorrido total
            iteration_time = time.time() - last_iteration_time  # Calcula o tempo decorrido da última iteração
            last_iteration_time = time.time()  # Atualiza o tempo da última iteração
            x = int(size*j/count)
            total_minutes = int(elapsed_time // 60)  # Calcula os minutos totais
            total_seconds = int(elapsed_time % 60)   # Calcula os segundos restantes
            output.write(f"Tempo: {iteration_time:.2f}s\n")
            output.write(f"{prefix} [{'█'*x}{' '*(size-x)}] {j}/{count} - Tempo total: {total_minutes:02d}:{total_seconds:02d} \r")
            output.flush()        
        show(0)
        for i, item in enumerate(it):
            yield item
            show(i+1)
        output.write("\n")
        output.flush()

    #-------------MODULO PARA FAZER TENTATIVAS NA CAPTAÇÃO DOS DADOS
    def get_html(url, headers=None):
        max_attempts = 10  # Número máximo de tentativas
        attempt = 0
        wait_time = 5  # Tempo inicial de espera
        while attempt < max_attempts:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response  # Retorna o objeto Response se a solicitação for bem-sucedida
            except requests.exceptions.HTTPError as http_err:
                print(f'HTTPError: {http_err}. Tentativa {attempt+1}/{max_attempts}')
            except requests.exceptions.RequestException as req_err:
                print(f'RequestException: {req_err}. Tentativa {attempt+1}/{max_attempts}')
            attempt += 1
            if attempt < max_attempts:
                print(f"Erro na obtenção dos dados, nova tentativa será feita em {wait_time} segundos...")
                countdown(wait_time)  # Chamada da função countdown apenas uma vez
                wait_time += 2  # Aumenta o tempo de espera para a próxima tentativa
        print("Número máximo de tentativas atingido. Falha ao obter o HTML.")
        return None

    #-------------MODULO PARA CONTAGEM USADO NA BARRA
    def countdown(seconds):
        for i in range(seconds, 0, -1):
            print(f"Tentando novamente em {i} segundo(s)...")
            time.sleep(1)
          

    linha=0
    coluna=0
    timestr = time.strftime("%d.%m.%Y_%H.%M.%S")
    workbook = xlsxwriter.Workbook('relatorio_' + timestr + '.xlsx')
    worksheet = workbook.add_worksheet()

    print("+--------------------------------------------------------------------------------+")
    print("|\tVarredura Tabela URBS - Datas de alteração - Versão 7.1.0                |")
    print("|\tCódigo: Aramis Alves de Souza Filho\tÚltima Compilação: 10/09/2025      |")
    print("|\tWeb Scraping usando Python 'lxml'                                        |")
    print("|\tINFORMAÇÕES                                                              |")
    print("|\t*No console, linhas sem tabela será exibido como --/--/----              |")
    print("|\t*No arquivo .xls, linhas sem tabela serao exibidos como uma célula vazia |")
    print("|\t*No final da execução será gerado um arquivo .xlsx com o relatório       |")
    print("+--------------------------------------------------------------------------------+")
    input("Pressione ENTER para iniciar")
    print("Conectando")

    #Adição de Headers para engarnar servidor que não é um bot acessando o site
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Connection": "keep-alive"
    }
    
    try:
        html = requests.get("https://www.urbs.curitiba.pr.gov.br/", headers=headers)
        html.raise_for_status()
    except HTTPError as http_err:
        print(f'\nHTTPError: \n{http_err}')
        input("\nPressione ENTER para encerrar o programa")
        exit()
    except Exception as err:
        print(f'\nError: \n{err}')
        input("\nPressione ENTER para Encerrar")
        exit()
    else:
        print("Conexão feita com sucesso!")
      
    doc = lxml.html.fromstring(html.text)
    codlinhas=doc.xpath('//select[@id="compHritLinha"]/option')
    if codlinhas: #Se nao for um conjunto vazio, continua
        print("Linhas ativas:",len(codlinhas))
        time.sleep(1)
        lista=[] #Cria vetor lista
        for i in range(len(codlinhas)):
            teste=(codlinhas[i].text)[-4:-1]
            lista.append(teste)
    else:
        print("\nErro de extração:\nVetor codlinhas resultou em uma lista vazia")   
        input("\nPressione ENTER para Encerrar")
        exit()
        


    sub=0
    cont=0
    fim_lista = len(lista)
    #fim_lista = 10



    cell_format0 = workbook.add_format()
    cell_format1 = workbook.add_format()
    cell_format2 = workbook.add_format()
    cell_format3 = workbook.add_format()

    cell_format1.set_num_format('dd/mm/yy') 
    cell_format1.set_center_across()
     
    cell_format2.set_num_format('dd/mm/yy')  
    cell_format2.set_font_color('red')
    cell_format2.set_bold()
    cell_format2.set_center_across()
    cell_format2.set_font_size(13)

    cell_format3.set_num_format('dd/mm/yy')  
    cell_format3.set_font_color('green')
    cell_format3.set_bold()
    cell_format3.set_center_across()
    cell_format3.set_font_size(13)
    linha += 1

    print("Iniciando varredura")
    #for cont in range(fim_lista):
    for cont in progressbar(range(fim_lista), "Progresso: ", 30):

                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                        "Accept-Language": "pt-BR,pt;q=0.9",
                        "Connection": "keep-alive"
                    }
                    html = get_html("https://www.urbs.curitiba.pr.gov.br/horario-de-onibus/" + lista[cont] + "/0", headers=headers)
        
        
                   # html = get_html("https://www.urbs.curitiba.pr.gov.br/horario-de-onibus/" + lista[cont]+"/0")
                    doc = lxml.html.fromstring(html.text)
                    datas = doc.xpath('//table[@id="simpletext"]//p[@class="grey margin0"]/text()')
                    nome = doc.xpath(u'//h2[@class="schedule"]/text()')
                    print("                                                                                                            ",end="\r")
                    if nome:
                        print("\n")
                        print(nome[0])
                    quant_tab = len(datas)
                                    
                    #Cria listas para separar as tabelas por tipo de dia
                    data_util = [] 
                    data_sab = []
                    data_dom = []              
                   
                    #-------Extraimos e exibimos o dado requerido
                    if datas:                       #----Se não for um conjunto vazio, continua
                        quant_tab = len(datas)      #Verifica quantidade de tabelas
                        print("- Tabelas:",quant_tab)
                        #---Separa Dias Uteis, Sábado e Domingo
                        for i in range(quant_tab):
                            data_aux=datas[i].strip()

                            if data_aux[44] == "I": #Verifica o caracter 40
                                data_util.append(data_aux.strip())
                                
                            if data_aux[43] == "S":
                                data_sab.append(data_aux.strip())
                            if data_aux[44] == "O":
                                data_dom.append(data_aux.strip())
                        
                        if data_util:
                            #print("Qtd. Tabela Útil:", len(data_util))
                            #Se a 1ª data for igual a ultima data, significa que não há alteração recente
                            if data_util[0] == data_util[len(data_util)-1]:
                                data0 = data_util[0]                #Extrai a data
                                #data0 = data0.strip()              #Formata
                                print("- Dia Útil\t",data0[20:30])  #Imprime o prefixo e a data
                                worksheet.write(linha, coluna, nome[0])
                                date_time = datetime.datetime.strptime(data0[20:30], '%d/%m/%Y')
                                worksheet.write_datetime(linha, coluna + 1 ,date_time, cell_format1)                    
                            
                            #Se a 1ª data for diferenta da ultima significa que tem alteração em andamento
                            else: 
                                data0 = data_util[0]          
                                print("- Dia Útil\t",data0[20:30], "VENCENDO")
                                worksheet.write(linha, coluna, nome[0])
                                date_time = datetime.datetime.strptime(data0[20:30], '%d/%m/%Y')
                                worksheet.write_datetime(linha, coluna + 1 ,date_time, cell_format2)
                                data1 = data_util[len(data_util)-1]
                                print("- Dia Útil\t",data1[20:30], "NOVO")
                                worksheet.write(linha, coluna, nome[0])
                                date_time = datetime.datetime.strptime(data1[20:30], '%d/%m/%Y')
                                worksheet.write_datetime(linha, coluna + 2 ,date_time, cell_format3)  
                        else:    
                            print("- Dia Útil\t","--/--/----")


                        if data_sab:    
                            if data_sab[0] == data_sab[len(data_sab)-1]:
                                data0 = data_sab[0]                 #Extrai a data
                                print("- Sábado\t",data0[20:30])    #Imprime o prefixo e a data
                                worksheet.write(linha, coluna, nome[0])
                                date_time = datetime.datetime.strptime(data0[20:30], '%d/%m/%Y')
                                worksheet.write_datetime(linha, coluna + 3 ,date_time, cell_format1)                     
                            else:
                                data0 = data_sab[0]          
                                print("- Sábado\t",data0[20:30], "VENCENDO")
                                worksheet.write(linha, coluna, nome[0])
                                date_time = datetime.datetime.strptime(data0[20:30], '%d/%m/%Y')
                                worksheet.write_datetime(linha, coluna + 3 ,date_time, cell_format2)
                                data1 = data_sab[len(data_sab)-1] 
                                print("- Sábado\t",data1[20:30], "NOVO")
                                worksheet.write(linha, coluna, nome[0])
                                date_time = datetime.datetime.strptime(data1[20:30], '%d/%m/%Y')
                                worksheet.write_datetime(linha, coluna + 4 ,date_time, cell_format3) 
                        else:
                            print("- Sábado\t","--/--/----")


                        if data_dom:    
                            if data_dom[0] == data_dom[len(data_dom)-1]:
                                data0 = data_dom[0]                  #Extrai a data
                                print("- Domingo\t",data0[20:30])    #Imprime o prefixo e a data
                                worksheet.write(linha, coluna, nome[0])
                                date_time = datetime.datetime.strptime(data0[20:30], '%d/%m/%Y')
                                worksheet.write_datetime(linha, coluna + 5 ,date_time, cell_format1)
                            else:
                                data0 = data_dom[0]          
                                print("- Domingo\t",data0[20:30], "VENCENDO")
                                worksheet.write(linha, coluna, nome[0])
                                date_time = datetime.datetime.strptime(data0[20:30], '%d/%m/%Y')
                                worksheet.write_datetime(linha, coluna + 5 ,date_time, cell_format2)
                                #linha += 1 
                                data1 = data_dom[len(data_dom)-1]
                                
                                print("- Domingo\t",data1[20:30], "NOVO")
                                worksheet.write(linha, coluna, nome[0])
                                date_time = datetime.datetime.strptime(data1[20:30], '%d/%m/%Y')
                                worksheet.write_datetime(linha, coluna + 6 ,date_time, cell_format3) 
                                #linha += 1 
                        else:
                            print("- Domingo\t","--/--/----")
                        
                    linha += 1

    worksheet.add_table(0,0,linha-1,6, {'columns': [{'header': 'Código - Nome da Linha'},
                                                    {'header': 'DU Atual'},
                                                    {'header': 'DU Novo'},
                                                    {'header': 'SAB Atual'},
                                                    {'header': 'SAB Novo'},
                                                    {'header': 'DOM Atual'},
                                                    {'header': 'DOM Novo'}
                                                    ]})
    worksheet.set_column(0,0,45)
    worksheet.set_column(1,1,11.5)
    worksheet.set_column(2,2,11.5)
    worksheet.set_column(3,3,11.5)
    worksheet.set_column(4,4,11.5)
    worksheet.set_column(6,5,11.5)
    worksheet.set_column(6,6,11.5)
    worksheet.insert_textbox('I3', 'Datas em vermelho indicam tabela horária vencendo\nDatas em verde indicam tabela horária que entrará em vigor\n\nPara facilitar a vizualição das últimas alterações\nUtilize a função de filtrar e \n"Classificar do Mais Novo para o Mais Antigo"', {'width': 384})
    workbook.close()

    fim=input("\nFim da varredura\nGerando arquivo .xlsx\nPressione ENTER para fechar o console e abrir o arquivo .xlsx")
    os.startfile('relatorio_' + timestr + '.xlsx')
    pass

def script_ver_tabelas_urbs():
    def obter_dados_tabela_linha(cod_linha):
        url_base = f"https://transporteservico.urbs.curitiba.pr.gov.br/getTabelaLinha.php?linha={cod_linha}&c=179c5"
        print(f"Buscando dados do seguinte endereço: \n{url_base}")  # Exibe o URL completo
        response = requests.get(url_base)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro ao buscar dados: {response.status_code}")
            return None
        
        
    import textwrap


    def abreviar_palavras(ponto):
        abreviacoes = {
            'PRACA': 'PÇA',
            'TERMINAL': 'TERM.',
            'RUA': 'R',
            'AVENIDA': 'AV',
            'CONJUNTO': 'CONJ',
            'JARDIM': 'JD',
            'PARQUE': 'PQ',
            'SENTIDO': 'SENT',
            'ESTACAO TUBO': 'TUBO',
            'CAPAO': 'C',
            'CAMPINA': 'C',
            'TERM.BAIRRO': 'TERM. B',
            'CAMPO': 'C',
            'SITIO CERCADO': 'S. CERCADO'
        }

        palavras = ponto.split()
        palavras_abreviadas = [abreviacoes.get(palavra.upper(), palavra) for palavra in palavras]
        return ' '.join(palavras_abreviadas)

    def ajustar_horario(horario):
        hora, minuto = map(int, horario.split(":"))
        if hora == 0:
            hora = 24
        elif hora == 1:
            hora = 25
        return f"{hora:02}:{minuto:02}"

    def processar_horarios(dados, dia_escolhido):
        organizado_por_dia_tabela = {}
        for item in dados:
            ponto = item['PONTO']
            dia = item['DIA']
            horario = item['HORA']
            tabela = item['TABELA']
            if dia_escolhido == '4' or dia == dia_escolhido:  # Filtra apenas o dia escolhido ou todos os dias se for '4'
                if dia not in organizado_por_dia_tabela:
                    organizado_por_dia_tabela[dia] = {}
                if tabela not in organizado_por_dia_tabela[dia]:
                    organizado_por_dia_tabela[dia][tabela] = []
                organizado_por_dia_tabela[dia][tabela].append((ponto, horario))
        
        return organizado_por_dia_tabela

    def imprimir_horarios_por_dia_tabela(organizado_por_dia_tabela):
        dias_traduzidos = {'1': 'DIAS ÚTEIS', '2': 'SÁBADO', '3': 'DOMINGO', '4': 'TODOS OS DIAS'}
        
        for dia, tabelas in organizado_por_dia_tabela.items():
            print("\n+--------------------+")
            dia_traduzido = dias_traduzidos.get(dia, f"DIA {dia}")
            print(f"| DIA DA SEMANA: {dia_traduzido} |")
            print("+--------------------+")
            
            for tabela, horarios in tabelas.items():
                print(f"\nTabela: {tabela}\n")
                
                # Calcula o maior ponto e horário para alinhamento
                maior_ponto = max(len(ponto) for ponto, _ in horarios)
                maior_horario = max(len(horario) for _, horario in horarios)
                
                for ponto, horario in horarios:
                    # Ajuste para alinhar os horários à direita
                    print(f"{ponto.ljust(maior_ponto)} : {horario.rjust(maior_horario)}")


    def quebra_linha(ponto, largura=15):
        # Usa o textwrap para quebrar o texto sem cortar palavras no meio
        if len(ponto) > largura:
            # Usar textwrap para quebrar mantendo a lógica correta sem confundir as palavras
            quebra = textwrap.wrap(ponto, width=largura)
            # Garante que a última linha tenha o espaço correto
            if len(quebra[-1]) < largura:
                quebra[-1] = quebra[-1].ljust(largura)
            return '\n'.join(quebra)
        return ponto


    def quebra_linha_com_alinhamento(pontos, largura=15):
        # Função para quebrar e alinhar os nomes dos pontos
        linhas = []
        max_linhas = 0

        # Quebra os nomes dos pontos e alinha-os em múltiplas linhas
        for ponto in pontos:
            # Quebrar o ponto em múltiplas linhas
            quebra = textwrap.wrap(ponto, width=largura)
            max_linhas = max(max_linhas, len(quebra))
            linhas.append(quebra)

        # Agora garantir que todas as colunas tenham o mesmo número de linhas
        for i, quebra in enumerate(linhas):
            if len(quebra) < max_linhas:
                # Completa com linhas vazias
                linhas[i] += [' ' * largura] * (max_linhas - len(quebra))

        # Transpor as linhas para manter o alinhamento vertical correto
        linhas_transpostas = [' | '.join(linha[i].ljust(largura) for linha in linhas) for i in range(max_linhas)]
        return '\n'.join(linhas_transpostas)

    def imprimir_horarios_visualizacao_avancada(organizado_por_dia_tabela):
        for dia, tabelas in organizado_por_dia_tabela.items():
            print("\n+--------------------+")
            print(f"| DIA DA SEMANA: {dia} |")
            print("+--------------------+")

            for tabela, horarios in tabelas.items():
                # Ajustar horários para tratar corretamente 00 como 24 e 01 como 25
                horarios_ajustados = [(ponto, ajustar_horario(horario)) for ponto, horario in horarios]

                # Organizar os horários por ponto original
                horarios_por_ponto = {ponto: [] for ponto, _ in horarios_ajustados}
                for ponto, horario in horarios_ajustados:
                    horarios_por_ponto[ponto].append(horario)

                # Ordenar os pontos pelo primeiro horário mais cedo
                pontos_ordenados = sorted(horarios_por_ponto.keys(), key=lambda p: min(horarios_por_ponto[p]))

                # Abreviar e quebrar os pontos para exibição
                pontos_abreviados = [quebra_linha(abreviar_palavras(ponto)) for ponto in pontos_ordenados]

                # Exibe os pontos com a quebra de linha e alinhamento
                print(f"\nTabela {tabela}:\n")
                print(quebra_linha_com_alinhamento(pontos_abreviados))
                print("-" * (len(pontos_abreviados[0]) * len(pontos_abreviados)))

                # Ordenar os horários dentro de cada ponto
                for ponto in pontos_ordenados:
                    horarios_por_ponto[ponto].sort()

                # Calcular o maior número de horários
                max_len = max(len(horarios_por_ponto[ponto]) for ponto in pontos_ordenados)

                # Imprimir os horários, agora respeitando a ordem dos pontos
                for i in range(max_len):
                    linha = ""
                    for ponto in pontos_ordenados:
                        if i < len(horarios_por_ponto[ponto]):
                            linha += horarios_por_ponto[ponto][i].ljust(15)
                        else:
                            linha += " ".ljust(15)
                        linha += " | "
                    print(linha.rstrip(" | "))


    def verificar_outra_linha():
        resposta = input("\nDeseja fazer uma nova pesquisa? (S/N): ")
        return resposta.strip().lower() == 's'

    # Integração das funcionalidades no script principal

    print("+--------------------------------------------------------------------------------+")
    print("|\tVer tabelas Operacionais URBS                                            |")
    print("|\tCódigo: Aramis Alves de Souza Filho\tÚltima Compilação: 28/12/24      |")
    print("+--------------------------------------------------------------------------------+")
    print("Script faz uso do método getTabelaLinha para extrair as tabelas das linhas.")


    while True:
        print(" ")
        cod_linha = input("Digite o código da linha desejada: ")
        print("Escolha o dia da semana (1-DIAS ÚTEIS, 2-SÁBADO, 3-DOMINGO, 4-TODOS OS DIAS): ")
        dia_escolhido = input("Digite a opção desejada: ")

        print("Escolha a forma de exibição (1-Simples, 2-Avançada(CLI.NALINHA)): ")
        modo_exibicao = input("Digite a opção desejada: ")

        dados = obter_dados_tabela_linha(cod_linha)
        if dados:
            organizado_por_dia_tabela = processar_horarios(dados, dia_escolhido)
            
            if modo_exibicao == '1':
                imprimir_horarios_por_dia_tabela(organizado_por_dia_tabela)
            elif modo_exibicao == '2':
                imprimir_horarios_visualizacao_avancada(organizado_por_dia_tabela)
            else:
                print("Opção de exibição inválida. Exibindo no modo Simples por padrão.")
                imprimir_horarios_por_dia_tabela(organizado_por_dia_tabela)
        else:
            print("Nenhum dado disponível para exibição.")

        if not verificar_outra_linha():
            break

# -----------------------------------------------------------------------------Função de menu principal
def menu_principal():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Limpa o console
        print("+----------------------------------------------------------------------------------------+")
        print("|                                   Menu Principal                                       |")
        print("+----------------------------------------------------------------------------------------+")
        print("|   1. Web Scraping URBS (Consultar vencimento tabelas), gera planilha excel             |")
        print("|   2. Apenas visualizar horários por Tabelas Operacionais                               |")
        print("|   3. Sair                                                                              |")
        print("+----------------------------------------------------------------------------------------+")
        
        escolha = input("Escolha uma opção: ")
        
        if escolha == '1':
            os.system('cls' if os.name == 'nt' else 'clear')  # Limpa o console
            script_web_scraping()
        elif escolha == '2':
            os.system('cls' if os.name == 'nt' else 'clear')  # Limpa o console
            script_ver_tabelas_urbs()
        elif escolha == '3':
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida! Por favor, escolha uma opção correta (1-4).")
        
        input("Pressione Enter para continuar...")

# Executar o menu principal
if __name__ == "__main__":
    menu_principal()