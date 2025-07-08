import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time
import os
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from bs4 import BeautifulSoup

# =============================================
# MÓDULO DE COLETA AUTOMÁTICA DE DADOS
# =============================================

class LotoDataCollector:
    def __init__(self):
        self.historical_url = "https://raw.githubusercontent.com/guilhermecamargo/loterias-api/master/lotofacil.csv"
        self.api_url = "https://loteriascaixa-api.herokuapp.com/api/lotofacil"
        self.data_file = "lotofacil_full.csv"
        
    def load_initial_data(self):
        """Carrega dados históricos do repositório GitHub"""
        df = pd.read_csv(self.historical_url, sep=';')
        df.to_csv(self.data_file, index=False, sep=';')
        print(f"Carregados {len(df)} registros históricos")
        return df
    
    def fetch_latest_api(self):
        """Obtém o último resultado da API"""
        try:
            response = requests.get(f"{self.api_url}/latest", timeout=10)
            return response.json()
        except:
            print("Erro na API, usando fallback scraping")
            return self.scrape_official_site()
    
    def scrape_official_site(self):
        """Web scraping do site oficial como fallback"""
        url = "https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx"
        try:
            page = requests.get(url).content
            soup = BeautifulSoup(page, 'html.parser')
            
            # Encontrar o concurso mais recente
            latest = soup.find("div", {"id": "wp_resultados"})
            contest_num = int(latest.find("span", {"class": "num-concurso"}).text.strip())
            date_str = latest.find("span", {"class": "data-concurso"}).text.strip()
            numbers = [int(li.text) for li in latest.find("ul", {"class": "numbers"}).find_all("li")]
            
            return {
                "concurso": contest_num,
                "data": datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d'),
                "dezenas": numbers
            }
        except Exception as e:
            print(f"Erro no scraping: {e}")
            return None
    
    def update_data(self):
        """Atualiza o dataset com novos sorteios"""
        if not os.path.exists(self.data_file):
            df = self.load_initial_data()
        else:
            df = pd.read_csv(self.data_file, sep=';')
        
        last_contest = df['concurso'].max()
        latest_data = self.fetch_latest_api()
        
        if latest_data and latest_data['concurso'] > last_contest:
            new_row = {
                'concurso': latest_data['concurso'],
                'data': latest_data['data'],
                'bola1': latest_data['dezenas'][0],
                'bola2': latest_data['dezenas'][1],
                'bola3': latest_data['dezenas'][2],
                'bola4': latest_data['dezenas'][3],
                'bola5': latest_data['dezenas'][4],
                'bola6': latest_data['dezenas'][5],
                'bola7': latest_data['dezenas'][6],
                'bola8': latest_data['dezenas'][7],
                'bola9': latest_data['dezenas'][8],
                'bola10': latest_data['dezenas'][9],
                'bola11': latest_data['dezenas'][10],
                'bola12': latest_data['dezenas'][11],
                'bola13': latest_data['dezenas'][12],
                'bola14': latest_data['dezenas'][13],
                'bola15': latest_data['dezenas'][14]
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.data_file, index=False, sep=';')
            print(f"Adicionado concurso {latest_data['concurso']} - {latest_data['data']}")
            return True
        return False
    
    def start_auto_collector(self, callback, interval=86400):
        """Inicia coleta automática diária com callback"""
        while True:
            print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M')} - Verificando atualizações...")
            if self.update_data():
                callback()  # Chama a função de callback quando atualiza dados
            time.sleep(interval)

# =============================================
# PRÉ-PROCESSAMENTO E ENGENHARIA DE FEATURES
# =============================================

class DataPreprocessor:
    def __init__(self, sequence_length=10):
        self.sequence_length = sequence_length
        self.num_features = 25  # Números de 1 a 25
        
    def load_data(self):
        df = pd.read_csv("lotofacil_full.csv", sep=';')
        df = df.sort_values('concurso')
        return df
        
    def create_features(self, df):
        """Cria matriz one-hot e features temporais"""
        # Matriz one-hot encoding
        X = np.zeros((len(df), self.num_features))
        for i in range(len(df)):
            for j in range(1, 16):
                num = df.iloc[i, j+1]
                X[i, num-1] = 1
        
        # Features temporais
        dates = pd.to_datetime(df['data'])
        df['dia_semana'] = dates.dt.dayofweek
        df['mes'] = dates.dt.month
        
        return X, df[['dia_semana', 'mes']].values
    
    def prepare_sequences(self, X, temporal_features):
        """Prepara sequências para modelos LSTM"""
        sequences = []
        next_numbers = []
        
        for i in range(len(X) - self.sequence_length):
            seq = X[i:i+self.sequence_length]
            temporal_seq = temporal_features[i:i+self.sequence_length]
            
            # Combina one-hot com features temporais corretamente
            full_seq = np.concatenate((seq, temporal_seq), axis=1)
            sequences.append(full_seq)
            next_numbers.append(X[i+self.sequence_length])
            
        return np.array(sequences), np.array(next_numbers)

# =============================================
# MODELOS DE IA
# =============================================

class LotoPredictor:
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.models = {
            'mlp': None,
            'random_forest': None,
            'lstm': None
        }
    
    def train_mlp(self, X_train, y_train):
        """Treina modelo MLP"""
        model = MLPClassifier(
            hidden_layer_sizes=(128, 64),
            activation='relu',
            learning_rate_init=0.001,
            max_iter=500,
            random_state=42
        )
        model.fit(X_train, y_train)
        return model
    
    def train_random_forest(self, X_train, y_train):
        """Treina modelo Random Forest"""
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        return model
    
    def train_lstm(self, X_train, y_train):
        """Treina modelo LSTM (CORRIGIDO)"""
        model = Sequential([
            LSTM(128, input_shape=(X_train.shape[1], X_train.shape[2])),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dense(25, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.1,
            verbose=1
        )
        
        return model
    
    def evaluate_model(self, model, X_test, y_test, model_type):
        """Avalia o modelo e retorna métricas (CORRIGIDO)"""
        if model_type == 'lstm':
            y_pred = (model.predict(X_test) > 0.5).astype(int)
        else:
            y_pred = model.predict(X_test)
        
        # Calcula acurácia por número
        accuracy = accuracy_score(y_test.flatten(), y_pred.flatten())
        
        # Calcula acurácia por concurso (todos os 15 números corretos)
        full_match = 0
        total_samples = len(y_test)
        
        for i in range(total_samples):
            # Obtém os índices dos números sorteados
            true_indices = set(np.where(y_test[i] == 1)[0])
            pred_indices = set(np.where(y_pred[i] == 1)[0])
            
            # Verifica se os 15 números coincidem
            if true_indices == pred_indices:
                full_match += 1
        
        full_match_acc = full_match / total_samples if total_samples > 0 else 0
        
        return accuracy, full_match_acc
    
    def train_all_models(self):
        """Treina todos os modelos e salva os resultados"""
        print("\nIniciando treinamento dos modelos...")
        df = self.preprocessor.load_data()
        X, temporal = self.preprocessor.create_features(df)
        sequences, next_nums = self.preprocessor.prepare_sequences(X, temporal)
        
        # Divisão de dados para MLP e Random Forest
        # Usar apenas o último sorteio da sequência para modelos não sequenciais
        X_flat = np.hstack((X[self.preprocessor.sequence_length:], temporal[self.preprocessor.sequence_length:]))
        y_flat = next_nums
        
        X_train_flat, X_test_flat, y_train_flat, y_test_flat = train_test_split(
            X_flat, y_flat, test_size=0.2, random_state=42
        )
        
        # Divisão para LSTM
        X_train_seq, X_test_seq, y_train_seq, y_test_seq = train_test_split(
            sequences, next_nums, test_size=0.2, random_state=42
        )
        
        # Treinamento e avaliação
        results = {}
        
        # MLP
        print("\nTreinando MLP...")
        self.models['mlp'] = self.train_mlp(X_train_flat, y_train_flat)
        acc_mlp, full_mlp = self.evaluate_model(self.models['mlp'], X_test_flat, y_test_flat, 'mlp')
        results['mlp'] = {'accuracy': acc_mlp, 'full_match': full_mlp}
        
        # Random Forest
        print("\nTreinando Random Forest...")
        self.models['random_forest'] = self.train_random_forest(X_train_flat, y_train_flat)
        acc_rf, full_rf = self.evaluate_model(self.models['random_forest'], X_test_flat, y_test_flat, 'rf')
        results['random_forest'] = {'accuracy': acc_rf, 'full_match': full_rf}
        
        # LSTM
        print("\nTreinando LSTM...")
        self.models['lstm'] = self.train_lstm(X_train_seq, y_train_seq)
        acc_lstm, full_lstm = self.evaluate_model(self.models['lstm'], X_test_seq, y_test_seq, 'lstm')
        results['lstm'] = {'accuracy': acc_lstm, 'full_match': full_lstm}
        
        # Salva resultados
        result_df = pd.DataFrame(results).T
        result_df.to_csv('model_performance.csv')
        print("\nResultados do treinamento:")
        print(result_df)
        
        return results
    
    def predict_next(self):
        """Faz previsão para o próximo sorteio usando todos os modelos"""
        df = self.preprocessor.load_data()
        X, temporal = self.preprocessor.create_features(df)
        
        # Última sequência disponível
        last_sequence = X[-self.preprocessor.sequence_length:]
        last_temporal = temporal[-self.preprocessor.sequence_length:]
        
        # Prepara dados para cada modelo
        # Para MLP e Random Forest: usar apenas o último sorteio
        mlp_input = np.hstack((X[-1], temporal[-1])).reshape(1, -1)
        rf_input = mlp_input
        
        # Para LSTM: usar a sequência completa
        lstm_input = np.concatenate(
            (last_sequence, last_temporal), 
            axis=1
        ).reshape(1, self.preprocessor.sequence_length, -1)
        
        predictions = {}
        
        # MLP
        if self.models['mlp']:
            mlp_probs = self.models['mlp'].predict_proba(mlp_input)[0]
            mlp_top = np.argsort(mlp_probs)[::-1][:15] + 1
            predictions['mlp'] = sorted(mlp_top)
        
        # Random Forest
        if self.models['random_forest']:
            rf_probs = self.models['random_forest'].predict_proba(rf_input)[0]
            rf_top = np.argsort(rf_probs)[::-1][:15] + 1
            predictions['random_forest'] = sorted(rf_top)
        
        # LSTM
        if self.models['lstm']:
            lstm_probs = self.models['lstm'].predict(lstm_input)[0]
            lstm_top = np.argsort(lstm_probs)[::-1][:15] + 1
            predictions['lstm'] = sorted(lstm_top)
        
        # Combina previsões
        combined = {}
        for nums in predictions.values():
            for num in nums:
                combined[num] = combined.get(num, 0) + 1
        
        # Top 15 números mais votados
        consensus = sorted([num for num, count in combined.items() if count >= 2])
        
        if len(consensus) < 15:
            # Completa com números mais frequentes nos modelos
            top_nums = sorted(combined, key=combined.get, reverse=True)[:15]
            consensus = sorted(top_nums)
        
        predictions['consenso'] = consensus
        
        # Salva previsões
        pred_df = pd.DataFrame({k: [v] for k, v in predictions.items()})
        pred_df.to_csv('proximas_previsoes.csv', index=False)
        
        print("\nPrevisões para o próximo sorteio:")
        print(pred_df)
        
        return predictions

# =============================================
# EXECUÇÃO PRINCIPAL
# =============================================

if __name__ == "__main__":
    collector = LotoDataCollector()
    predictor = LotoPredictor()
    
    # Carrega dados iniciais se necessário
    if not os.path.exists("lotofacil_full.csv"):
        collector.load_initial_data()
    
    # Treina modelos inicialmente
    predictor.train_all_models()
    
    # Faz previsão inicial
    predictor.predict_next()
    
    # Função de callback para quando novos dados são adicionados
    def on_new_data():
        print("\nDados atualizados - Retreinando modelos...")
        predictor.train_all_models()
        predictor.predict_next()
    
    # Inicia coleta automática e atualização
    print("\nIniciando serviço de coleta automática...")
    collector.start_auto_collector(callback=on_new_data, interval=43200)  # Verifica a cada 12 horas