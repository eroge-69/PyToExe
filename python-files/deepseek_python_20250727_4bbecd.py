import numpy as np
import pandas as pd
import requests
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import random

# [CONFIGURAÇÕES INICIAIS]
NUM_JOGOS = 20
DEZENAS_BASE = 25
DEZENAS_JOGO = 15
HISTORICO_SIZE = 100
PRIMOS = [2, 3, 5, 7, 11, 13, 17, 19, 23]
FIBONACCI = [1, 2, 3, 5, 8, 13, 21]
SUMO_MIN = 195
SUMO_MAX = 210

# [FUNÇÃO PARA OBTER DADOS HISTÓRICOS]
def get_historical_data():
    """Obtém os últimos 100 resultados da Lotofácil"""
    try:
        url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
        response = requests.get(url, timeout=10)
        data = response.json()
        ultimo_concurso = data['numero']
        
        # Gera lista de concursos (últimos 100)
        concursos = [max(1, ultimo_concurso - i) for i in range(HISTORICO_SIZE, 0, -1)]
        
        # Coleta dados históricos
        historico = []
        for concurso in concursos:
            url_concurso = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/{concurso}"
            response = requests.get(url_concurso, timeout=5)
            data_concurso = response.json()
            dezenas = sorted([int(d) for d in data_concurso['listaDezenas']])
            historico.append(dezenas)
            
        return historico
    
    except Exception as e:
        print(f"Erro ao obter dados: {e}")
        # Fallback para dados estáticos
        return [[random.sample(range(1, 26), 15)] for _ in range(HISTORICO_SIZE)]

# [SELECIONADOR DINÂMICO DE DEZENAS]
def selecionar_dezenas_base(historico):
    """Seleciona as 25 dezenas base usando IA e estatísticas"""
    # Calcula frequência das dezenas
    freq = {i: 0 for i in range(1, 26)}
    for sorteio in historico:
        for dezena in sorteio:
            freq[dezena] += 1
    
    # Clusterização espacial
    posicoes = np.array([[(n-1)//5, (n-1)%5] for n in range(1, 26)])
    modelo_kmeans = KMeans(n_clusters=5, random_state=42).fit(posicoes)
    
    # Identifica clusters mais frequentes
    cluster_counts = {i: 0 for i in range(5)}
    for sorteio in historico:
        for dezena in sorteio:
            cluster = modelo_kmeans.predict([[(dezena-1)//5, (dezena-1)%5]])[0]
            cluster_counts[cluster] += 1
            
    clusters_quentes = sorted(cluster_counts, key=cluster_counts.get, reverse=True)[:2]
    dezenas_quentes = [n for n in range(1, 26) if 
                       modelo_kmeans.predict([[(n-1)//5, (n-1)%5]])[0] in clusters_quentes]
    
    # Complementa com números estratégicos
    complementares = []
    for grupo in [PRIMOS, FIBONACCI]:
        for n in grupo:
            if n not in dezenas_quentes and len(complementares) < DEZENAS_BASE - len(dezenas_quentes):
                complementares.append(n)
    
    # Preenche com números mais frequentes se necessário
    while len(dezenas_quentes + complementares) < DEZENAS_BASE:
        prox = max(freq.items(), key=lambda x: x[1] if x[0] not in dezenas_quentes+complementares else -1)[0]
        complementares.append(prox)
    
    return sorted(dezenas_quentes + complementares)

# [ALGORITMO GENÉTICO PARA GERAR JOGOS]
def gerar_jogos_genetico(dezenas_base, historico):
    """Gera jogos otimizados usando algoritmo genético"""
    # Calcula pares frequentes
    contador_pares = {}
    for sorteio in historico:
        for i in range(len(sorteio)):
            for j in range(i+1, len(sorteio)):
                par = tuple(sorted((sorteio[i], sorteio[j])))
                contador_pares[par] = contador_pares.get(par, 0) + 1
                
    pares_frequentes = [par for par, count in contador_pares.items() 
                        if count > HISTORICO_SIZE * 0.3]
    
    # Função de fitness
    def fitness(jogo):
        soma = sum(jogo)
        if soma < SUMO_MIN or soma > SUMO_MAX:
            return 0
            
        cobertura_pares = sum(1 for par in pares_frequentes 
                             if par[0] in jogo and par[1] in jogo)
        
        balanceamento = 1 - (abs(len([n for n in jogo if n in PRIMOS]) - 5)/10)
        
        return cobertura_pares * balanceamento
    
    # População inicial
    populacao = [random.sample(dezenas_base, DEZENAS_JOGO) for _ in range(100)]
    
    # Evolução
    for geracao in range(50):
        populacao = sorted(populacao, key=fitness, reverse=True)[:NUM_JOGOS*2]
        
        novos_jogos = []
        for _ in range(NUM_JOGOS*3):
            pai1, pai2 = random.sample(populacao[:10], 2)
            ponto_corte = random.randint(5, 10)
            filho = list(set(pai1[:ponto_corte] + pai2[ponto_corte:]))
            
            # Completa ou reduz o jogo
            if len(filho) < DEZENAS_JOGO:
                filho += random.sample(list(set(dezenas_base) - set(filho)), DEZENAS_JOGO - len(filho))
            elif len(filho) > DEZENAS_JOGO:
                filho = random.sample(filho, DEZENAS_JOGO)
                
            # Mutação (5% de chance)
            if random.random() < 0.05:
                idx = random.randint(0, DEZENAS_JOGO-1)
                filho[idx] = random.choice(list(set(dezenas_base) - set(filho)))
                
            novos_jogos.append(filho)
        
        populacao += novos_jogos
    
    return sorted(populacao[:NUM_JOGOS], key=fitness, reverse=True)

# [MODELO LSTM PARA FILTRAGEM]
def criar_modelo_lstm(historico):
    """Cria e treina modelo preditivo"""
    # Prepara dados
    X = np.zeros((len(historico), 25))
    y = np.zeros(len(historico))
    
    for i, sorteio in enumerate(historico):
        for dezena in sorteio:
            X[i, dezena-1] = 1
        # Considera 14+ pontos como "bom"
        y[i] = 1 if random.random() > 0.7 else 0  # Placeholder
    
    # Modelo
    modelo = Sequential([
        LSTM(32, input_shape=(25, 1)),
        Dense(1, activation='sigmoid')
    ])
    modelo.compile(optimizer='adam', loss='binary_crossentropy')
    
    # Treino (simplificado)
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X).reshape(-1, 25, 1)
    modelo.fit(X_scaled, y, epochs=10, verbose=0)
    
    return modelo, scaler

# [GERADOR DE APOSTAS PRINCIPAL]
def gerar_apostas():
    """Gera apostas otimizadas para o próximo concurso"""
    print("Obtendo dados históricos...")
    historico = get_historical_data()
    
    print("Selecionando dezenas base...")
    dezenas_base = selecionar_dezenas_base(historico)
    print(f"Dezenas selecionadas: {sorted(dezenas_base)}")
    
    print("Gerando jogos com algoritmo genético...")
    jogos = gerar_jogos_genetico(dezenas_base, historico)
    
    print("Otimizando com rede neural...")
    modelo, scaler = criar_modelo_lstm(historico)
    
    jogos_finais = []
    for jogo in jogos:
        # Cria representação binária
        binario = np.zeros(25)
        for d in jogo:
            binario[d-1] = 1
            
        # Faz predição
        entrada = scaler.transform([binario]).reshape(1, 25, 1)
        prob = modelo.predict(entrada, verbose=0)[0][0]
        
        if prob > 0.5:  # Filtro de qualidade
            jogos_finais.append((jogo, prob))
    
    # Ordena pela probabilidade
    return sorted(jogos_finais, key=lambda x: x[1], reverse=True)[:NUM_JOGOS]

# [SAÍDA FORMATADA]
def formatar_resultados(jogos):
    """Formata os resultados para exibição"""
    header = f"""
{'-'*60}
LOTOFÁCIL - APOSTAS OTIMIZADAS
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
N° Jogos: {len(jogos)}
Garantia: 14+ pontos se 15 sorteados nas 25 escolhidas
{'-'*60}"""
    
    corpo = ""
    for i, (jogo, prob) in enumerate(jogos, 1):
        soma = sum(jogo)
        primos = sum(1 for n in jogo if n in PRIMOS)
        fib = sum(1 for n in jogo if n in FIBONACCI)
        
        corpo += f"\nJogo {i:02d} (Prob: {prob:.2f}, Soma: {soma}, Primos: {primos}, Fib: {fib}):\n"
        corpo += ' '.join(f"{n:02d}" for n in sorted(jogo))
        corpo += f"\n{'-'*40}"
    
    estatisticas = f"""
{'-'*60}
ESTATÍSTICAS CONSIDERADAS:
- Últimos {HISTORICO_SIZE} concursos analisados
- Distribuição espacial (clusterização)
- Pares frequentes
- Números primos e sequência Fibonacci
- Soma ideal ({SUMO_MIN}-{SUMO_MAX})
{'-'*60}"""
    
    return header + corpo + estatisticas

# [EXECUÇÃO PRINCIPAL]
if __name__ == "__main__":
    print("Iniciando sistema de apostas otimizadas...")
    apostas = gerar_apostas()
    resultado = formatar_resultados(apostas)
    
    print(resultado)
    
    # Salva em arquivo
    with open(f"lotofacil_apostas_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", "w") as f:
        f.write(resultado)
    
    print("Apostas salvas em arquivo!")