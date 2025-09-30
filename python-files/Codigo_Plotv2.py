import os
import re
from tkinter import Tk, filedialog
from datetime import datetime
import plotly.graph_objects as go
    
def extrair_numero_cauda(conteudo): 
    match = re.search(r'AC:\s*(\d+)', conteudo, re.IGNORECASE)
    if match: 
        return match.group(1)[-2:]
    return None

def extrair_numero_posicao_motor(conteudo): 
    match = re.search(r'ACH:\s*(\w+)', conteudo, re.IGNORECASE)
    if match: 
        return match.group(1)
    return None

def extrair_BINS(conteudo): 
    match = re.search(r'BINS:\s*(\d+)', conteudo, re.IGNORECASE)
    if match: 
        return match.group(1)
    return None

def extrair_posicao_sensor(conteudo): 
    match = re.search(r'SDESC:\s*(\w+\s\w+)', conteudo, re.IGNORECASE)
    if match:
        posicao = match.group(1).strip()
        return normalizar_posicao_sensor(posicao)
    return None

def normalizar_posicao_sensor(posicao_sensor):
    if 'RGB FWD' in posicao_sensor:
        return 'RGB FWD Horizontal'
    elif 'RGB AFT' in posicao_sensor:
        return 'RGB AFT Horizontal'
    elif r'ADH' in posicao_sensor:
        return 'ADH Vertical'
    elif r'Prop' in posicao_sensor: 
        return 'Prop Lateral'
    return posicao_sensor

def extrair_regime(conteudo): 
    match = re.search(r'SNAME:\s*(.*)', conteudo, re.IGNORECASE)
    if match: 
        regime = match.group(1).strip()
        return normalizar_regime(regime)
    return None

def normalizar_regime(regime):
    if '7000' in regime:
        return '7000Tq, 1500 shp'
    elif r'80% Np' in regime:
        return '80% Np'
    return regime

def extrair_freq_max(conteudo): 
    match = re.search(r'FRQH:\s*(\d+)', conteudo, re.IGNORECASE)
    if match: 
        return match.group(1)
    return None

def extrair_safety_factor(conteudo): 
    match = re.search(r'SF:\s*([\d.]+)', conteudo, re.IGNORECASE)
    if match: 
        return match.group(1)
    return None

def analisar_ficheiro(caminho_ficheiro, regime, posicao_sensor, freq_max):
    try:
        with open(caminho_ficheiro, 'r') as file:
            conteudo = file.read()
            numero_cauda = extrair_numero_cauda(conteudo)
            posicao_motor = extrair_numero_posicao_motor(conteudo)
            seccao = conteudo.split('SSET:')
            for sec in seccao:
                regime_lido = extrair_regime(sec)
                if regime == regime_lido:
                    sub_seccao = re.split(r'SPC#:\d+', sec)
                    for sub_sec in sub_seccao:
                        pos_lido = extrair_posicao_sensor(sub_sec)
                        freq_lido = extrair_freq_max(sub_sec)
                        if pos_lido == posicao_sensor and freq_lido == freq_max:
                            bins = extrair_BINS(sub_sec)
                            if bins is not None:
                                bins = int(bins)
                                numeros = extrair_numero_plot(sub_sec)
                                if numeros is None:
                                    print(f"Números não encontrados no arquivo {caminho_ficheiro}")
                                    continue
                                safety_factor = float(extrair_safety_factor(sub_sec))
                                print(f'{regime},{posicao_sensor},{freq_max},{safety_factor},{caminho_ficheiro}, {numero_cauda} , {posicao_motor}')
                                return numeros, bins, regime, posicao_sensor, freq_max, safety_factor, (os.path.basename(caminho_ficheiro)).split('_')[0], numero_cauda, posicao_motor 
    except Exception as e:
        print(f'O ficheiro {caminho_ficheiro} não tem os dados pedidos')
    return None, None, None, None, None, None, None, None, None


def extrair_numero_plot(seccao): 
    linhas = seccao.strip().split('\n')
    numeros = []
    for linha in linhas:
        if linha.strip().isdigit():
            numeros.append(int(linha.strip()))
    return numeros

def plotar_grafico(numeros, valor_bin, regime, posicao_sensor, freq_max, safety_factor): 
    x = [(i * int(freq_max)) / valor_bin for i in range(1, len(numeros) + 1)]
    y = [num * safety_factor for num in numeros]
    
    plt.plot(x, y)
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Amplitude')
    plt.title(f'Gráfico de Amplitude vs Frequência \n Regime:{regime} \nPosição Sensor:{posicao_sensor} \n Freq_Max{freq_max}')
    plt.grid(True)
    plt.show()
    
def plotar_grafico_2(dados):
       cores = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
       fig = go.Figure()
        
       for i, (numeros, valor_bin, regime, posicao_sensor, freq_max, safety_factor, data, motor, numero_cauda, posicao_motor) in enumerate(dados):
            x = [(i * int(freq_max)) / valor_bin for i in range(1, len(numeros) + 1)]
            y = [num * safety_factor for num in numeros]  # Multiplicar pelo safety_factor
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=f'DATA: {data} - T/N: {numero_cauda} - #: {posicao_motor}'))
    
       fig.update_layout(title=f'Gráficos de Amplitude vs Frequência \n Regime:{regime} \n Posição Sensor:{posicao_sensor} \nFreq Max:{freq_max} \nMotor:{motor}',xaxis_title='Frequência (Hz)',yaxis_title='Amplitude',hovermode='closest')
       fig.show()


def obter_arquivos_recentes(pasta):
    arquivos = [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
    arquivos_com_data = []

    for arquivo in arquivos:
        match = re.search(r'_(\d{2}-\d{2}-\d{4})\.txt$', arquivo)
        if match:
            data_str = match.group(1)
            try:
                data = datetime.strptime(data_str, "%d-%m-%Y")
                arquivos_com_data.append((arquivo, data))
            except ValueError:
                pass

    
    return arquivos_com_data

def escolher_pasta():
    print("Escolha a pasta com os ficheiros")
    from tkinter import Tk, filedialog
    root = Tk()
    root.withdraw()  # Não queremos uma janela principal
    pasta = filedialog.askdirectory(title="Escolha a pasta com os ficheiros")
    return pasta

def menu():
    while True:
        print("Escolha a aeronave:")
        print("1. C-130")
        print("2. C-295")
        aeronave_index = input("Digite o número da aeronave: ")
        if aeronave_index == '1':
            aeronave = "C-130"
            regimes = ["LSGI", "HSGI", "7000Tq, 1500 shp", "Max Power"]
            posicoes = ["RGB FWD Horizontal", "RGB AFT Horizontal", "COMP FWD", "ADH Vertical", "COORDINATOR", "AFT COMP", "TURBINE"]
            freqs_max = ["100", "250", "600", "1100", "2200", "5000", "10000"]
            break
        elif aeronave_index == '2':
            aeronave = "C-295"
            regimes = ["Cruise", "80% Np"]
            posicoes = ["Prop Lateral"]
            freqs_max = ["100", "250", "1100", "6000", "15 000", "24 000", "36 000", 
                         "66 000", "132 000", "192 000", "300 000", "360 000", "600 000"]
            break
        else:
            print("Opção inválida. Tente novamente.")

    while True:
        print("\nEscolha o regime:")
        for i, regime in enumerate(regimes):
            print(f"{i + 1}. {regime}")
        regime_index = input("Digite o número do regime: ")
        if regime_index.isdigit() and 1 <= int(regime_index) <= len(regimes):
            regime = regimes[int(regime_index) - 1]
            break
        else:
            print("Opção inválida. Tente novamente.")

    while True:
        print("\nEscolha a posição do sensor:")
        for i, posicao in enumerate(posicoes):
            print(f"{i + 1}. {posicao}")
        posicao_index = input("Digite o número da posição do sensor: ")
        if posicao_index.isdigit() and 1 <= int(posicao_index) <= len(posicoes):
            posicao_sensor = posicoes[int(posicao_index) - 1]
            break
        else:
            print("Opção inválida. Tente novamente.")

    while True:
        print("\nEscolha a frequência máxima (hz):")
        for i, freq in enumerate(freqs_max):
            print(f"{i + 1}. {freq}")
        freq_index = input("Digite o número da frequência máxima: ")
        if freq_index.isdigit() and 1 <= int(freq_index) <= len(freqs_max):
            freq_max = freqs_max[int(freq_index) - 1]
            break
        else:
            print("Opção inválida. Tente novamente.")

    pasta = escolher_pasta()
    arquivos_recentes = obter_arquivos_recentes(pasta)

    dados = []

    for arquivo, data in arquivos_recentes:
        caminho_ficheiro = os.path.join(pasta, arquivo) 
        numeros_lido, bins_lido, regime_lido, posicao_sensor_lido, freq_max_lido, sf_valor_lido, motor_lido, numero_cauda_lido, posicao_motor_lido = analisar_ficheiro(caminho_ficheiro, regime, posicao_sensor, freq_max)
        if numeros_lido is not None and bins_lido is not None and posicao_sensor_lido is not None and freq_max_lido is not None and sf_valor_lido is not None: 
            dados.append((numeros_lido, bins_lido, regime_lido, posicao_sensor_lido, freq_max_lido, sf_valor_lido, data.strftime("%d-%m-%Y"), motor_lido, numero_cauda_lido, posicao_motor_lido))
    
    dados.sort(key=lambda x: x[6], reverse=True)
    dados = dados[:4]
    
    if dados:
        plotar_grafico_2(dados)
    else: 
        print("Não foram encontrados ficheiros com as condições pedidas")
        
#----------------------------------------------------------------------------------------------------------------#
menu()

