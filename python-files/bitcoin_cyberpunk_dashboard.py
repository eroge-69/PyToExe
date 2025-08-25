#!/usr/bin/env python3
"""
🚀 BITCOIN CYBERPUNK DASHBOARD 🚀
Sistema avançado de monitoramento BTC com tema dark cyberpunk
Desenvolvido para Google Colab
"""

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import time
import warnings
warnings.filterwarnings('ignore')

# Configuração do tema cyberpunk
plt.style.use('dark_background')
CYBER_COLORS = {
    'primary': '#00ff41',
    'secondary': '#ff0080', 
    'accent': '#00ffff',
    'warning': '#ffff00',
    'danger': '#ff4444',
    'bg_dark': '#0a0a0a',
    'bg_light': '#1a1a1a'
}

class BitcoinCyberpunkDashboard:
    def __init__(self):
        self.api_urls = {
            'coingecko': 'https://api.coingecko.com/api/v3',
            'coinapi': 'https://rest.coinapi.io/v1',
            'blockchain': 'https://api.blockchain.info',
            'mempool': 'https://mempool.space/api'
        }
        
        print("🔮 INICIALIZANDO BITCOIN CYBERPUNK DASHBOARD...")
        print("=" * 60)
        
    def get_headers(self):
        """Headers para requisições API"""
        return {
            'User-Agent': 'Bitcoin-Cyberpunk-Dashboard/1.0',
            'Accept': 'application/json'
        }
    
    def print_cyber_header(self, text):
        """Imprime cabeçalho no estilo cyberpunk"""
        print(f"\n{'█' * 60}")
        print(f"█ {text.center(56)} █")
        print(f"{'█' * 60}")
    
    def fetch_price_data(self):
        """Dados de preço em tempo real (PRIORIDADE MÁXIMA)"""
        try:
            url = f"{self.api_urls['coingecko']}/simple/price"
            params = {
                'ids': 'bitcoin',
                'vs_currencies': 'usd,eur,brl',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = requests.get(url, params=params, headers=self.get_headers())
            data = response.json()['bitcoin']
            
            return {
                'price_usd': data['usd'],
                'price_eur': data['eur'], 
                'price_brl': data['brl'],
                'market_cap': data['usd_market_cap'],
                'volume_24h': data['usd_24h_vol'],
                'change_24h': data['usd_24h_change'],
                'last_updated': data['last_updated_at']
            }
        except Exception as e:
            print(f"❌ Erro ao buscar dados de preço: {e}")
            return None
    
    def fetch_market_data(self):
        """Dados detalhados do mercado (PRIORIDADE ALTA)"""
        try:
            url = f"{self.api_urls['coingecko']}/coins/bitcoin"
            response = requests.get(url, headers=self.get_headers())
            data = response.json()
            
            market = data['market_data']
            
            return {
                'market_cap_rank': data['market_cap_rank'],
                'market_cap_dominance': market.get('market_cap_change_percentage_24h', 0),
                'total_supply': market['total_supply'],
                'circulating_supply': market['circulating_supply'],
                'max_supply': market['max_supply'],
                'ath': market['ath']['usd'],
                'ath_change': market['ath_change_percentage']['usd'],
                'ath_date': market['ath_date']['usd'],
                'atl': market['atl']['usd'],
                'atl_change': market['atl_change_percentage']['usd'],
                'price_change_7d': market.get('price_change_percentage_7d', 0),
                'price_change_30d': market.get('price_change_percentage_30d', 0),
                'price_change_1y': market.get('price_change_percentage_1y', 0)
            }
        except Exception as e:
            print(f"❌ Erro ao buscar dados de mercado: {e}")
            return None
    
    def fetch_blockchain_data(self):
        """Dados da blockchain (PRIORIDADE ALTA)"""
        try:
            # Stats gerais
            stats_url = f"{self.api_urls['blockchain']}/stats"
            stats_response = requests.get(stats_url, headers=self.get_headers())
            stats = stats_response.json()
            
            # Mempool data
            mempool_url = f"{self.api_urls['mempool']}/mempool"
            mempool_response = requests.get(mempool_url, headers=self.get_headers())
            mempool = mempool_response.json()
            
            # Difficulty
            difficulty_url = f"{self.api_urls['mempool']}/difficulty-adjustment"  
            difficulty_response = requests.get(difficulty_url, headers=self.get_headers())
            difficulty = difficulty_response.json()
            
            return {
                'total_bitcoins': stats['totalbc'] / 100000000,  # Convert from satoshis
                'market_price_usd': stats['market_price_usd'],
                'hash_rate': stats['hash_rate'],
                'difficulty': stats['difficulty'],
                'minutes_between_blocks': stats['minutes_between_blocks'],
                'blocks_size': stats['blocks_size'],
                'total_fees_btc': stats['total_fees_btc'] / 100000000,
                'trade_volume_btc': stats['trade_volume_btc'],
                'trade_volume_usd': stats['trade_volume_usd'],
                'mempool_size': mempool['count'],
                'mempool_vsize': mempool['vsize'],
                'next_difficulty_estimate': difficulty.get('difficultyChange', 0)
            }
        except Exception as e:
            print(f"❌ Erro ao buscar dados blockchain: {e}")
            return None
    
    def fetch_fear_greed_index(self):
        """Índice Fear & Greed (PRIORIDADE MÉDIA)"""
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, headers=self.get_headers())
            data = response.json()['data'][0]
            
            return {
                'value': int(data['value']),
                'classification': data['value_classification'],
                'timestamp': data['timestamp']
            }
        except Exception as e:
            print(f"❌ Erro ao buscar Fear & Greed: {e}")
            return None
    
    def fetch_global_metrics(self):
        """Métricas globais crypto (PRIORIDADE MÉDIA)"""
        try:
            url = f"{self.api_urls['coingecko']}/global"
            response = requests.get(url, headers=self.get_headers())
            data = response.json()['data']
            
            return {
                'total_market_cap': data['total_market_cap']['usd'],
                'total_volume': data['total_volume']['usd'],
                'btc_dominance': data['market_cap_percentage']['bitcoin'],
                'active_cryptocurrencies': data['active_cryptocurrencies'],
                'markets': data['markets'],
                'defi_volume': data.get('defi_volume_24h', 0),
                'defi_dominance': data.get('defi_market_cap_percentage', 0)
            }
        except Exception as e:
            print(f"❌ Erro ao buscar métricas globais: {e}")
            return None
    
    def calculate_technical_indicators(self, prices):
        """Indicadores técnicos básicos"""
        if len(prices) < 20:
            return {}
            
        prices_array = np.array(prices)
        
        # Médias móveis
        sma_20 = np.mean(prices_array[-20:])
        sma_50 = np.mean(prices_array[-50:]) if len(prices) >= 50 else sma_20
        
        # RSI simplificado
        deltas = np.diff(prices_array[-14:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains)
        avg_loss = np.mean(losses)
        rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss != 0 else 50
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi,
            'volatility': np.std(prices_array[-30:]) if len(prices) >= 30 else 0
        }
    
    def create_price_chart(self, historical_data):
        """Gráfico de preços cyberpunk"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), facecolor=CYBER_COLORS['bg_dark'])
        
        # Preços
        dates = pd.to_datetime(historical_data['timestamps'], unit='ms')
        prices = historical_data['prices']
        
        ax1.plot(dates, prices, color=CYBER_COLORS['primary'], linewidth=2, alpha=0.9)
        ax1.fill_between(dates, prices, alpha=0.1, color=CYBER_COLORS['primary'])
        ax1.set_title('🚀 BITCOIN PRICE EVOLUTION', color=CYBER_COLORS['accent'], fontsize=16, weight='bold')
        ax1.grid(True, alpha=0.3, color=CYBER_COLORS['accent'])
        ax1.set_facecolor(CYBER_COLORS['bg_light'])
        
        # Volume
        if 'volumes' in historical_data:
            volumes = historical_data['volumes']
            ax2.bar(dates, volumes, color=CYBER_COLORS['secondary'], alpha=0.7, width=0.8)
            ax2.set_title('💎 TRADING VOLUME', color=CYBER_COLORS['accent'], fontsize=14)
            ax2.set_facecolor(CYBER_COLORS['bg_light'])
            ax2.grid(True, alpha=0.3, color=CYBER_COLORS['accent'])
        
        plt.tight_layout()
        plt.show()
    
    def display_priority_data(self, all_data):
        """Exibe dados por ordem de prioridade"""
        
        # PRIORIDADE 1: DADOS DE PREÇO
        self.print_cyber_header("⚡ PRIORIDADE 1: DADOS DE PREÇO ⚡")
        if all_data['price']:
            price = all_data['price']
            print(f"💰 Preço USD: ${price['price_usd']:,.2f}")
            print(f"💶 Preço EUR: €{price['price_eur']:,.2f}")  
            print(f"💵 Preço BRL: R${price['price_brl']:,.2f}")
            print(f"📈 Mudança 24h: {price['change_24h']:.2f}%")
            print(f"💎 Market Cap: ${price['market_cap']:,.0f}")
            print(f"📊 Volume 24h: ${price['volume_24h']:,.0f}")
            
        # PRIORIDADE 2: DADOS BLOCKCHAIN  
        self.print_cyber_header("🔗 PRIORIDADE 2: DADOS BLOCKCHAIN 🔗")
        if all_data['blockchain']:
            bc = all_data['blockchain']
            print(f"⛏️  Hash Rate: {bc['hash_rate']:.2e} H/s")
            print(f"🎯 Dificuldade: {bc['difficulty']:,.0f}")
            print(f"⏱️  Tempo entre blocos: {bc['minutes_between_blocks']:.1f} min")
            print(f"💰 Total BTC: {bc['total_bitcoins']:,.2f}")
            print(f"🏊 Mempool: {bc['mempool_size']} transações")
            print(f"💸 Taxas totais: {bc['total_fees_btc']:.2f} BTC")
            
        # PRIORIDADE 3: DADOS DE MERCADO
        self.print_cyber_header("📊 PRIORIDADE 3: ANÁLISE DE MERCADO 📊")
        if all_data['market']:
            market = all_data['market']
            print(f"👑 Market Cap Rank: #{market['market_cap_rank']}")
            print(f"🔄 Suprimento Circulante: {market['circulating_supply']:,.0f}")
            print(f"📈 ATH: ${market['ath']:,.2f} ({market['ath_change']:.1f}%)")
            print(f"📉 ATL: ${market['atl']:,.2f} ({market['atl_change']:.1f}%)")
            print(f"📅 Mudança 7d: {market['price_change_7d']:.2f}%")
            print(f"📅 Mudança 30d: {market['price_change_30d']:.2f}%")
            print(f"📅 Mudança 1a: {market['price_change_1y']:.2f}%")
            
        # PRIORIDADE 4: MÉTRICAS GLOBAIS
        self.print_cyber_header("🌍 PRIORIDADE 4: MÉTRICAS GLOBAIS 🌍")
        if all_data['global']:
            glob = all_data['global']
            print(f"🏆 BTC Dominance: {glob['btc_dominance']:.1f}%")
            print(f"💹 Market Cap Total: ${glob['total_market_cap']:,.0f}")
            print(f"📈 Volume Total: ${glob['total_volume']:,.0f}")
            print(f"🪙 Cryptos Ativas: {glob['active_cryptocurrencies']:,}")
            print(f"🏪 Mercados: {glob['markets']:,}")
            
        # PRIORIDADE 5: SENTIMENTO
        self.print_cyber_header("😨 PRIORIDADE 5: ÍNDICE FEAR & GREED 😨")
        if all_data['fear_greed']:
            fg = all_data['fear_greed']
            emoji = "😱" if fg['value'] < 25 else "😰" if fg['value'] < 50 else "😐" if fg['value'] < 75 else "🤑"
            print(f"{emoji} Fear & Greed: {fg['value']}/100 - {fg['classification'].upper()}")
    
    def fetch_historical_data(self, days=30):
        """Dados históricos para gráficos"""
        try:
            url = f"{self.api_urls['coingecko']}/coins/bitcoin/market_chart"
            params = {'vs_currency': 'usd', 'days': days}
            
            response = requests.get(url, params=params, headers=self.get_headers())
            data = response.json()
            
            return {
                'prices': [price[1] for price in data['prices']],
                'volumes': [vol[1] for vol in data['total_volumes']],
                'timestamps': [price[0] for price in data['prices']]
            }
        except Exception as e:
            print(f"❌ Erro ao buscar dados históricos: {e}")
            return None
    
    def run_dashboard(self):
        """Executa o dashboard completo"""
        print("🔥 INICIANDO SCAN COMPLETO...")
        
        # Coleta todos os dados
        all_data = {
            'price': self.fetch_price_data(),
            'market': self.fetch_market_data(), 
            'blockchain': self.fetch_blockchain_data(),
            'fear_greed': self.fetch_fear_greed_index(),
            'global': self.fetch_global_metrics()
        }
        
        # Exibe dados por prioridade
        self.display_priority_data(all_data)
        
        # Gráficos históricos
        historical = self.fetch_historical_data(30)
        if historical:
            self.create_price_chart(historical)
            
        # Status final
        print("\n" + "="*60)
        print("🚀 BITCOIN CYBERPUNK DASHBOARD - SCAN COMPLETO 🚀")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        return all_data

# FUNÇÃO PRINCIPAL PARA EXECUÇÃO NO COLAB
def iniciar_dashboard():
    """Função principal para rodar no Google Colab"""
    dashboard = BitcoinCyberpunkDashboard()
    return dashboard.run_dashboard()

# EXECUÇÃO AUTOMÁTICA
if __name__ == "__main__":
    # Instalar dependências se necessário
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("📦 Instalando dependências...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'matplotlib', 'seaborn', 'requests', 'pandas', 'numpy'])
    
    print("""
    ██████╗ ████████╗ ██████╗    ██████╗  █████╗ ███████╗██╗  ██╗
    ██╔══██╗╚══██╔══╝██╔════╝    ██╔══██╗██╔══██╗██╔════╝██║  ██║
    ██████╔╝   ██║   ██║         ██║  ██║███████║███████╗███████║
    ██╔══██╗   ██║   ██║         ██║  ██║██╔══██║╚════██║██╔══██║
    ██████╔╝   ██║   ╚██████╗    ██████╔╝██║  ██║███████║██║  ██║
    ╚═════╝    ╚═╝    ╚═════╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    
    🌟 BITCOIN CYBERPUNK DASHBOARD v1.0 🌟
    """)
    
    dados = iniciar_dashboard()
