Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import asyncio
import json
import pandas as pd
import aiosqlite
import websockets
import logging
from dash import Dash, dcc, html, Output, Input
import plotly.graph_objs as go

# === Configuração de logging ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

# === Storage Assíncrono ===
class Storage:
    def __init__(self, db_name="trades.db"):
        self.db_name = db_name

    async def initialize(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    symbol TEXT,
                    side TEXT,
                    price REAL,
                    pattern TEXT,
                    confidence REAL,
                    origin TEXT DEFAULT 'real'
                )
            """)
            await db.commit()
        logging.info("Banco inicializado.")

    async def log_trade(self, timestamp, symbol, side, price, pattern, confidence, origin="real"):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                INSERT INTO trades (timestamp, symbol, side, price, pattern, confidence, origin)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, symbol, side, price, pattern, confidence, origin))
            await db.commit()
        logging.info(f"Trade logado: {symbol} {side} {price} {pattern} {confidence}")

    async def fetch_recent_trades(self, limit=10):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute("""
                SELECT timestamp, symbol, side, price, confidence
                FROM trades
                WHERE side != 'ERROR'
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            await cursor.close()
            return rows

# === DataFeed Multiativo ===
class DataFeed:
    def __init__(self, symbols=["btcusdt", "ethusdt"], interval="1m"):
        self.symbols = symbols
        self.interval = interval
        self.data = {s: pd.DataFrame(columns=["time","open","high","low","close","volume"]) for s in symbols}
        self.ws_urls = [f"wss://stream.binance.com:9443/ws/{s}@kline_{interval}" for s in symbols]

    async def connect(self):
        while True:
            try:
                tasks = [self._listen(s, url) for s, url in zip(self.symbols, self.ws_urls)]
                await asyncio.gather(*tasks)
            except Exception as e:
                logging.error(f"Erro geral no WebSocket multiativo: {e}")
                await asyncio.sleep(5)

    async def _listen(self, symbol, url):
        while True:
            try:
                async with websockets.connect(url) as ws:
                    logging.info(f"Conectado ao WebSocket: {url}")
                    async for msg in ws:
                        try:
                            res = json.loads(msg)
                            k = res['k']
                            if k['x']:
                                new_row = {
                                    "time": pd.to_datetime(k['t'], unit='ms'),
                                    "open": float(k['o']),
                                    "high": float(k['h']),
                                    "low": float(k['l']),
                                    "close": float(k['c']),
                                    "volume": float(k['v'])
                                }
                                df = self.data[symbol]
                                self.data[symbol] = pd.concat([df, pd.DataFrame([new_row])]).tail(200).reset_index(drop=True)
                        except Exception as ex:
                            logging.warning(f"Erro ao processar msg {symbol}: {ex}")
            except websockets.ConnectionClosedError as e:
                logging.warning(f"Conexão WebSocket {symbol} fechada: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                logging.error(f"Erro WebSocket {symbol}: {e}")
                await asyncio.sleep(5)

# === Estratégia - Detecta Hammer ===
def detect_patterns(df):
    signals = []
    if len(df) < 20:
        return signals
    last = df.iloc[-1]
    body = abs(last['close'] - last['open'])
    shadow = min(last['open'], last['close']) - last['low']
    total_range = last['high'] - last['low']
    if total_range > 0 and body <= total_range * 0.3 and shadow >= body * 2:
        signals.append(("hammer", 0.7))
    return signals

# === Gestão de Capital Multiativo com limites ===
class MultiCapitalManager:
    MAX_STAKE = 1000

    def __init__(self, symbols, initial_balance=1000, mode="flat", stake=10, payout=0.8):
        self.balances = {s: initial_balance for s in symbols}
        self.modes = {s: mode for s in symbols}
        self.stakes = {s: stake for s in symbols}
        self.payouts = {s: payout for s in symbols}
        self.last_results = {s: None for s in symbols}
        self.current_stakes = {s: stake for s in symbols}

    def update(self, symbol, result):
        if result == "win":
            self.current_stakes[symbol] = self.stakes[symbol]
            self.balances[symbol] += self.current_stakes[symbol] * self.payouts[symbol]
        elif result == "loss":
            if self.modes[symbol] == "martingale":
                self.current_stakes[symbol] = min(self.current_stakes[symbol] * 2, self.MAX_STAKE)
            elif self.modes[symbol] == "soros":
                self.current_stakes[symbol] = self.stakes[symbol]
            else:
                self.current_stakes[symbol] = self.stakes[symbol]
            self.balances[symbol] -= self.current_stakes[symbol]
        self.last_results[symbol] = result
        logging.info(f"Capital atualizado: {symbol} saldo={self.balances[symbol]:.2f} stake={self.current_stakes[symbol]:.2f}")

# === Interface Dash ===
app = Dash(__name__)
datafeed = DataFeed()
storage = Storage()
capital_manager = MultiCapitalManager(datafeed.symbols)

async def initialize_storage():
    await storage.initialize()

app.layout = html.Div([
    html.H2("Plataforma Binária Estilo Quotex"),
    dcc.Dropdown(
        id="symbol-picker",
        options=[{"label": s.upper(), "value": s} for s in datafeed.symbols],
        value=datafeed.symbols[0]
    ),
    dcc.Graph(id="candles"),
    html.Div(id="alert"),
    html.Div(id="balance", style={"marginTop": "10px", "fontWeight": "bold"}),
    html.Div(id="history", style={"overflowY": "scroll", "height": "200px", "border": "1px solid #ccc", "padding": "5px"}),
    html.Audio(id="alert-sound", src="/assets/alert.mp3", autoPlay=False),
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)  # Atualiza a cada 10 segundos
])

def update_graph(dataframe, signal=None):
    if dataframe.empty:
        fig = go.Figure()
        fig.update_layout(title="Aguardando dados do servidor...")
        return fig, "Sem dados"
    fig = go.Figure(data=[
        go.Candlestick(
            x=dataframe['time'],
            open=dataframe['open'],
            high=dataframe['high'],
            low=dataframe['low'],
            close=dataframe['close']
        )
    ])
    alert = ""
    if signal:
        alert = f"{signal[0]} detectado com confiança {int(signal[1]*100)}%"
    return fig, alert

@app.callback(
    Output("candles", "figure"),
    Output("alert", "children"),
    Output("history", "children"),
    Output("alert-sound", "autoPlay"),
    Output("balance", "children"),
    Input("symbol-picker", "value"),
    Input("interval-component", "n_intervals")
)
async def update_ui(symbol, n_intervals):
    df = datafeed.data.get(symbol)
    if df is None or df.empty or len(df) < 20:
        balance_text = f"Saldo {symbol.upper()}: {capital_manager.balances[symbol]:.2f}"
...         return {}, "Sem dados", "", False, balance_text
... 
...     signals = detect_patterns(df)
...     play_sound = False
...     if signals:
...         sig = signals[-1]
...         result = "win" if sig[1] >= 0.6 else "loss"
...         capital_manager.update(symbol, result)
...         await storage.log_trade(str(df['time'].iloc[-1]), symbol, result, df['close'].iloc[-1], sig[0], sig[1])
...         fig, alert = update_graph(df, sig)
...         play_sound = True
...     else:
...         fig, alert = update_graph(df)
... 
...     trades = await storage.fetch_recent_trades()
...     rows = [f"{t[0]} - {t[1]} {t[2]} @ {t[3]:.4f} ({int(t[4]*100)}%)" for t in trades]
...     history_list = html.Ul([html.Li(r) for r in rows])
...     balance_text = f"Saldo {symbol.upper()}: {capital_manager.balances[symbol]:.2f}"
...     return fig, alert, history_list, play_sound, balance_text
... 
... async def run_datafeed():
...     await datafeed.connect()
... 
... async def main_async():
...     await initialize_storage()
...     task_datafeed = asyncio.create_task(run_datafeed())
...     task_dash = asyncio.create_task(app.run_server(debug=True, use_reloader=False))
...     await asyncio.gather(task_datafeed, task_dash)
... 
... if __name__ == "__main__":
...     import nest_asyncio
...     nest_asyncio.apply()  # Para evitar erro de loop em alguns ambientes (ex: Jupyter)
...     asyncio.run(main_async())
