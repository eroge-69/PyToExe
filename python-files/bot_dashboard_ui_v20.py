# bot_dashboard_ui_v2.py
# -*- coding: utf-8 -*-

import os
import datetime as dt
import numpy as np
import pandas as pd

# --- Индикаторы без TA-Lib ---

def compute_bollinger(series, period=20, dev=2):
    ma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = ma + dev * std
    lower = ma - dev * std
    return ma, upper, lower

def compute_stochastic(df, k_period=14, d_period=3):
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
    stoch_d = stoch_k.rolling(window=d_period).mean()
    return stoch_k, stoch_d

import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh
from pybit.unified_trading import HTTP

# =========================
# CONFIG / ENV
# =========================
load_dotenv()  # load .env if present
API_KEY = os.getenv("BYBIT_API_KEY", "").strip()
API_SECRET = os.getenv("BYBIT_API_SECRET", "").strip()
CATEGORY = "linear"           # USDT Perpetuals
INTERVAL = "1"                # kline interval: "1","3","5","15","30","60","120","240","360","720","D","W","M"
CANDLES_LIMIT = 500
VOL_FILTER_USDT = 10000       # filter out illiquid pairs by 24h turnover (USD), adjust if needed

# =========================
# BYBIT SESSION (LIVE)
# =========================
session = HTTP(
    testnet=False,
    api_key=API_KEY,
    api_secret=API_SECRET,
)

# =========================
# HELPERS: Symbols / Data
# =========================
@st.cache_data(show_spinner=False)
def fetch_all_usdt_perp_pairs(category: str = CATEGORY) -> list[str]:
    """Получить список ликвидных линейных USDT-периодов по тикерам v5."""
    try:
        resp = session.get_tickers(category=category)
        items = (resp.get("result") or {}).get("list") or []
    except Exception:
        items = []

    out = []
    for it in items:
        sym = it.get("symbol", "")
        if (
            sym.endswith("USDT")
            and all(x not in sym for x in ("3L", "3S", "UP", "DOWN"))
        ):
            try:
                turn = float(it.get("turnover24h") or 0.0)
            except Exception:
                turn = 0.0
            if turn >= VOL_FILTER_USDT:
                out.append((sym, turn))

    uniq = {}
    for s, vol in out:
        if s not in uniq or vol > uniq[s]:
            uniq[s] = vol
    return [k for k, _ in sorted(uniq.items(), key=lambda kv: kv[1], reverse=True)]

def fetch_klines(symbol: str, interval: str = INTERVAL, limit: int = CANDLES_LIMIT) -> pd.DataFrame:
    """Get OHLCV from Bybit Unified Trading v5 (via pybit)."""
    try:
        resp = session.get_kline(category=CATEGORY, symbol=symbol, interval=interval, limit=limit)
        raw = (resp.get("result") or {}).get("list") or []
        if not raw:
            return pd.DataFrame()
        df = pd.DataFrame(raw, columns=["ts","open","high","low","close","volume","turnover"])
        for c in ["open","high","low","close","volume","turnover"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["timestamp"] = pd.to_datetime(df["ts"].astype(np.int64), unit="ms")
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки свечей: {e}")
        return pd.DataFrame()

# =========================
# INDICATORS & STRATEGY
# =========================

def add_indicators(df: pd.DataFrame, ema_short: int, ema_long: int, stoch_k: int, stoch_d: int, bb_period: int, bb_dev: int) -> pd.DataFrame:
    if df.empty: return df

    # EMA
    df["EMA_short"] = df["close"].ewm(span=ema_short, adjust=False).mean()
    df["EMA_long"]  = df["close"].ewm(span=ema_long, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    # Volume MA
    df["VolMA"] = df["volume"].rolling(20).mean()

    # Stochastic
    low_min = df["low"].rolling(window=stoch_k).min()
    high_max = df["high"].rolling(window=stoch_k).max()
    df["StochK"] = 100 * (df["close"] - low_min) / (high_max - low_min)
    df["StochD"] = df["StochK"].rolling(window=stoch_d).mean()

    # Bollinger Bands
    df["BB_middle"] = df["close"].rolling(window=bb_period).mean()
    df["BB_upper"]  = df["BB_middle"] + bb_dev * df["close"].rolling(window=bb_period).std()
    df["BB_lower"]  = df["BB_middle"] - bb_dev * df["close"].rolling(window=bb_period).std()

    return df

    df["EMA_short"] = df["close"].ewm(span=ema_short, adjust=False).mean()
    df["EMA_long"]  = df["close"].ewm(span=ema_long, adjust=False).mean()
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    df["VolMA"] = df["volume"].rolling(20).mean()
    return df

def strategy_signal(df: pd.DataFrame, vol_mult: float = 0.5, rsi_buy: float = 55.0, rsi_sell: float = 45.0) -> str | None:
    if df is None or len(df) < 50: return None
    prev, last = df.iloc[-2], df.iloc[-1]
    if pd.notna(last.get("VolMA", np.nan)) and last["VolMA"] > 0:
        if last["volume"] < last["VolMA"] * max(vol_mult, 0.0):
            return None
    crossed_up = prev["EMA_short"] <= prev["EMA_long"] and last["EMA_short"] > last["EMA_long"]
    crossed_dn = prev["EMA_short"] >= prev["EMA_long"] and last["EMA_short"] < last["EMA_long"]
    if crossed_up and last.get("RSI", 50) > float(rsi_buy):
        return "Buy"
    if crossed_dn and last.get("RSI", 50) < float(rsi_sell):
        return "Sell"
    return None

# =========================
# ORDERS
# =========================
def place_market_order_with_brackets(symbol: str, side: str, qty: float,
                                     price: float, tp_pct: float, sl_pct: float,
                                     trail_pct: float):
    if side == "Buy":
        tp_price = price * (1 + tp_pct / 100.0)
        sl_price = price * (1 - sl_pct / 100.0)
    else:
        tp_price = price * (1 - tp_pct / 100.0)
        sl_price = price * (1 + sl_pct / 100.0)
    trailing_str = f"{trail_pct:.8g}" if trail_pct and trail_pct > 0 else None

    try:
        resp = session.place_order(
            category=CATEGORY,
            symbol=symbol,
            side=side,
            orderType="Market",
            qty=str(qty),
            timeInForce="IOC",
            reduceOnly=False,
            closeOnTrigger=False,
            takeProfit=str(tp_price),
            stopLoss=str(sl_price),
            tpTriggerBy="LastPrice",
            slTriggerBy="LastPrice",
            trailingStop=trailing_str,
        )
        return resp, tp_price, sl_price
    except Exception as e:
        st.error(f"Ошибка выставления ордера: {e}")
        return {}, None, None

def close_position_market(symbol: str, side: str, qty: float):
    closing_side = "Sell" if side == "Buy" else "Buy"
    try:
        resp = session.place_order(
            category=CATEGORY,
            symbol=symbol,
            side=closing_side,
            orderType="Market",
            qty=str(qty),
            timeInForce="IOC",
            reduceOnly=True,
            closeOnTrigger=True,
        )
        return resp
    except Exception as e:
        st.error(f"Ошибка закрытия позиции: {e}")
        return {}

# =========================
# DATA FROM EXCHANGE
# =========================
def fetch_open_positions(symbol: str | None = None) -> list[dict]:
    try:
        kwargs = {"category": CATEGORY}
        if symbol:
            kwargs["symbol"] = symbol
        else:
            kwargs["settleCoin"] = "USDT"
        resp = session.get_positions(**kwargs)
        return (resp.get("result") or {}).get("list") or []
    except Exception as e:
        st.warning(f"fetch_open_positions error: {e}")
        return []

def get_usdt_balance() -> float:
    try:
        resp = session.get_wallet_balance(accountType="UNIFIED")
        items = (resp.get("result") or {}).get("list") or []
        total = 0.0
        for acc in items:
            for coin in acc.get("coin", []):
                if coin.get("coin") == "USDT":
                    total += float(coin.get("equity") or 0.0)
        return total
    except Exception:
        return 0.0

def fetch_closed_orders_and_pnl(symbol: str | None = None, limit: int = 200) -> dict:
    result = {"orders": [], "closed_pnl": []}
    try:
        kwargs = {"category": CATEGORY, "limit": limit}
        if symbol:
            kwargs["symbol"] = symbol
        else:
            kwargs["settleCoin"] = "USDT"
        resp_hist = session.get_order_history(**kwargs)
        result["orders"] = (resp_hist.get("result") or {}).get("list") or []
        resp_pnl = session.get_closed_pnl(**kwargs)
        result["closed_pnl"] = (resp_pnl.get("result") or {}).get("list") or []
    except Exception as e:
        st.warning(f"fetch_closed_orders_and_pnl error: {e}")
    return result

# =========================
# STREAMLIT APP
# =========================
st.set_page_config(page_title="Bot Dashboard", layout="wide", initial_sidebar_state="expanded")
st_autorefresh(interval=10_000, key="autorf")

if "bot_running" not in st.session_state: st.session_state.bot_running = False
if "closed_from_exchange" not in st.session_state: st.session_state.closed_from_exchange = {"orders": [], "closed_pnl": []}
if "log" not in st.session_state: st.session_state.log = []

def log_event(text: str, toast=False):
    msg = f"{dt.datetime.utcnow().isoformat()} — {text}"
    st.session_state.log.append(msg)
    if toast:
        st.toast(text)

# Sidebar controls
with st.sidebar:
    st.markdown("## ⚙️ Управление")
    all_syms = fetch_all_usdt_perp_pairs()
    disabled_controls = st.session_state.bot_running

    symbol = st.selectbox("USDT Perp pair", all_syms, index=0 if all_syms else None, disabled=disabled_controls, placeholder="Загрузка...")

    st.markdown("### 📐 Параметры стратегии")
    ema_short = st.number_input("EMA short", 3, 100, 20, 1, disabled=disabled_controls)
    ema_long  = st.number_input("EMA long", 5, 300, 50, 1, disabled=disabled_controls)
    rsi_buy   = st.number_input("RSI Buy", 0, 100, 55, 1, disabled=disabled_controls)
    rsi_sell  = st.number_input("RSI Sell", 0, 100, 45, 1, disabled=disabled_controls)
    stoch_k = st.slider("Stochastic %K период", 3, 50, 14)
    stoch_d = st.slider("Stochastic %D период", 3, 50, 3)
    stoch_overbought = st.slider("Stoch Overbought", 50, 100, 80)
    stoch_oversold = st.slider("Stoch Oversold", 0, 50, 20)

    bb_period = st.slider("Bollinger период", 5, 50, 20)
    bb_dev = st.slider("Bollinger множитель", 1, 5, 2)

    volume_filter = st.slider("Фильтр по объёму", min_value=0, max_value=1000000, value=0, step=1000, help="Игнорировать сигналы на свечах с объёмом ниже этого значения", key="volume_filter")


    st.markdown("### 🧯 Риск-менеджмент")
    order_size = st.number_input("Объём (контракты)", 1.0, 1e9, 10.0, 1.0, disabled=disabled_controls)
    tp_pct = st.number_input("TP %", 0.1, 100.0, 2.0, 0.1, disabled=disabled_controls)
    sl_pct = st.number_input("SL %", 0.1, 100.0, 2.0, 0.1, disabled=disabled_controls)
    trail_pct = st.number_input("Trailing %", 0.0, 50.0, 0.5, 0.1, disabled=disabled_controls)

    st.markdown("### 🎛 Управление ботом")
    start_btn = st.button("🟢 Старт", use_container_width=True, disabled=st.session_state.bot_running)
    stop_btn  = st.button("🔴 Стоп", use_container_width=True, disabled=not st.session_state.bot_running)
    sync_btn  = st.button("🔵 Синхронизация", use_container_width=True)
    force_buy = st.button("🟢 Принудительный Buy", use_container_width=True)
    force_sell= st.button("🔴 Принудительный Sell", use_container_width=True)

if start_btn:
    st.session_state.bot_running = True
    log_event("Бот запущен", toast=True)
if stop_btn:
    st.session_state.bot_running = False
    log_event("Бот остановлен", toast=True)

balance = get_usdt_balance()
st.metric("USDT Balance", f"{balance:,.2f}")

df = pd.DataFrame()
if symbol:
    df = fetch_klines(symbol, INTERVAL, CANDLES_LIMIT)
    if not df.empty:
        df = add_indicators(df, ema_short, ema_long, stoch_k, stoch_d, bb_period, bb_dev)

if sync_btn:
    st.session_state.closed_from_exchange = fetch_closed_orders_and_pnl(symbol=None, limit=200)
    log_event("Синхронизация с биржей", toast=True)

if symbol and not df.empty and st.session_state.bot_running:
    open_pos = fetch_open_positions(symbol=symbol)
    have_open = any(float(p.get("size") or 0) > 0 for p in open_pos)
    sig = strategy_signal(df, vol_mult=0.5, rsi_buy=rsi_buy, rsi_sell=rsi_sell)
    last_price = float(df.iloc[-1]["close"])
    if sig and not have_open:
        place_market_order_with_brackets(symbol, sig, order_size, last_price, tp_pct, sl_pct, trail_pct)
        log_event(f"Сигнал {sig} по {symbol} — ордер открыт", toast=True)

if symbol and not df.empty:
    last_price = float(df.iloc[-1]["close"])
    if force_buy:
        place_market_order_with_brackets(symbol, "Buy", order_size, last_price, tp_pct, sl_pct, trail_pct)
        log_event(f"Force Buy {symbol}", toast=True)
    if force_sell:
        place_market_order_with_brackets(symbol, "Sell", order_size, last_price, tp_pct, sl_pct, trail_pct)
        log_event(f"Force Sell {symbol}", toast=True)

# Chart
if symbol:
    st.markdown("#### Chart")
    chart_source = st.radio("", ["TradingView", "Bybit"], horizontal=True, label_visibility="collapsed")
    st.markdown(f"#### {symbol}")
    if chart_source == "TradingView":
        tv_html = f"""
        <div class="tradingview-widget-container">
          <div id="tv_embed_container"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
            new TradingView.widget({{
              "symbol": "BYBIT:{symbol}",
              "interval": "1",
              "timezone": "Etc/UTC",
              "theme": "dark",
              "style": "1",
              "locale": "en",
              "container_id": "tv_embed_container",
              "height": 620,
              "width": "100%",
            }});
          </script>
        </div>
        """
        st.components.v1.html(tv_html, height=640)
    else:
        base = symbol.replace("USDT","").lower()
        url = f"https://www.bybit.com/trade/usdt/{base}usdt"
        st.components.v1.html(f'<iframe src="{url}" width="100%" height="640" frameborder="0"></iframe>', height=650)

# Open positions
st.subheader("📂 Открытые позиции (Биржа)")
live_pos = fetch_open_positions(symbol=None)
if live_pos:
    df_pos = pd.DataFrame(live_pos).copy()
    if not df.empty:
        lp = float(df.iloc[-1]["close"])
        def upnl(row):
            side = row.get("side","Buy")
            entry = float(row.get("entryPrice") or 0)
            qty = float(row.get("size") or 0)
            if entry == 0 or qty == 0: return 0.0
            return ((lp - entry) if side == "Buy" else (entry - lp)) * qty
        df_pos["unrealized_pnl_calc"] = df_pos.apply(upnl, axis=1)
    # >>> НОВЫЙ НОРМАЛЬНЫЙ ВИД ТАБЛИЦЫ (без "квадратиков")
    df_pos_display = df_pos.copy()
    display_cols = [
        "symbol","side","size","leverage","avgPrice","entryPrice","markPrice",
        "takeProfit","stopLoss","trailingStop","unrealisedPnl","unrealizedPnl","updatedTime","createdTime"
    ]
    cols_exist = [c for c in display_cols if c in df_pos_display.columns]
    if cols_exist:
        st.dataframe(df_pos_display[cols_exist], use_container_width=True)
    else:
        st.dataframe(df_pos_display, use_container_width=True)

    # Отдельный список кнопок закрытия позиций (строка на кнопку)
    if not df_pos_display.empty:
        st.markdown("##### Быстрые действия")
        for i, row in df_pos_display.iterrows():
            sym = row.get("symbol","?")
            side = row.get("side","?")
            qty  = float(row.get("size") or 0)
            if st.button(f"❌ Закрыть {sym} {side} (qty={qty})", key=f"close_btn_simple_{i}"):
                close_position_market(sym, side, qty)
                log_event(f"Закрыта позиция {sym} {side}", toast=True)

    # Отключаем устаревший построчный рендер (он давал 'квадратики'), не удаляя код ниже
    _legacy_df_pos = df_pos.copy()
    df_pos = df_pos.iloc[0:0]  # теперь цикл ниже не отрисуется
    # <<< КОНЕЦ НОВОГО ВИДА

    # add close buttons
    for i, row in df_pos.iterrows():
        cols = st.columns(len(row)+1)
        for j, (colname, val) in enumerate(row.items()):
            cols[j].write(f"**{colname}**: {val}")
        if cols[-1].button("❌ Close", key=f"close_{i}"):
            close_position_market(row["symbol"], row["side"], float(row.get("size") or 0))
            log_event(f"Закрыта позиция {row['symbol']} {row['side']}", toast=True)
else:
    st.info("Нет открытых позиций.")

# Closed deals
st.subheader("📜 Закрытые сделки (Биржа)")
tabs = st.tabs(["Ордеры", "Закрытый PnL"])
with tabs[0]:
    exch_orders = st.session_state.closed_from_exchange.get("orders") or []
    if exch_orders:
        st.dataframe(pd.DataFrame(exch_orders), use_container_width=True)
    else:
        st.info("Нет закрытых ордеров. Нажмите Синхронизация.")
with tabs[1]:
    exch_pnl = st.session_state.closed_from_exchange.get("closed_pnl") or []
    if exch_pnl:
        st.dataframe(pd.DataFrame(exch_pnl), use_container_width=True)
    else:
        st.info("Нет закрытого PnL. Нажмите Синхронизация.")

# Log
st.subheader("🪵 Журнал действий")
if st.session_state.log:
    st.code("\n".join(st.session_state.log))
else:
    st.info("Журнал пуст.")




# =========================
# ДОБАВЛЕНО В v6: Таймфрейм, кол-во свечей, проверка EMA short>=EMA long, бэктест
# =========================

# Доп. элементы в sidebar
with st.sidebar:
    st.markdown("### ⏱ Таймфрейм и глубина истории")
    interval_map = {
        "1 минута": "1",
        "5 минут": "5",
        "15 минут": "15",
        "1 час": "60",
        "4 часа": "240",
        "1 день": "D"
    }
    interval_label = st.selectbox("Интервал свечей", list(interval_map.keys()), index=2)
    interval = interval_map[interval_label]
    candle_limit = st.slider("Количество свечей", 100, 2000, 300, step=50)

    # Проверка EMA отключена по просьбе пользователя

# Бэктест стратегии на реальных свечах Bybit
st.subheader("📊 Бэктест стратегии (реальные свечи Bybit)")

if symbol:
    df_bt = fetch_klines(symbol, interval, candle_limit)
    df_bt = add_indicators(df_bt, ema_short, ema_long, stoch_k, stoch_d, bb_period, bb_dev)
    if not df_bt.empty:
        capital = 10000
        equity = capital
        equity_curve = []
        position = None
        entry_price = 0
        trade_log = []

        for i in range(1, len(df_bt)):
            price = df_bt.iloc[i]["close"]
            time = df_bt.iloc[i]["timestamp"]
            prev, last = df_bt.iloc[i-1], df_bt.iloc[i]
            crossed_up = prev["EMA_short"] <= prev["EMA_long"] and last["EMA_short"] > last["EMA_long"]
            crossed_dn = prev["EMA_short"] >= prev["EMA_long"] and last["EMA_short"] < last["EMA_long"]
            buy_sig = crossed_up and last["RSI"] > rsi_buy
            sell_sig = crossed_dn and last["RSI"] < rsi_sell
            if position is None:
                if buy_sig:
                    position = "long"; entry_price = price
                    trade_log.append((time, "Buy", price))
                elif sell_sig:
                    position = "short"; entry_price = price
                    trade_log.append((time, "Sell", price))
            else:
                if position == "long" and sell_sig:
                    pnl = price - entry_price
                    equity += pnl
                    trade_log.append((time, "Close Long", price, pnl, equity))
                    position = None
                elif position == "short" and buy_sig:
                    pnl = entry_price - price
                    equity += pnl
                    trade_log.append((time, "Close Short", price, pnl, equity))
                    position = None
            equity_curve.append((time, equity))

        # Визуализация
        fig, (ax1, ax2, ax3) = plt.subplots(3,1,figsize=(14,12),sharex=True)
        ax1.plot(df_bt["timestamp"], df_bt["close"], label="Цена", color="gray")
        ax1.plot(df_bt["timestamp"], df_bt["EMA_short"], label=f"EMA {ema_short}", color="blue")
        ax1.plot(df_bt["timestamp"], df_bt["EMA_long"], label=f"EMA {ema_long}", color="red")
        for tr in trade_log:
            if tr[1]=="Buy":
                ax1.scatter(tr[0], tr[2], marker="^", color="green", s=100)
            elif tr[1]=="Sell":
                ax1.scatter(tr[0], tr[2], marker="v", color="red", s=100)
        ax1.set_title(f"Бэктест {symbol} [{interval_label}]")
        ax1.legend(); ax1.grid(True)

        ax2.plot(df_bt["timestamp"], df_bt["RSI"], label="RSI", color="purple")
        ax2.axhline(rsi_buy, color="green", linestyle="--", label="RSI Buy")
        ax2.axhline(rsi_sell, color="red", linestyle="--", label="RSI Sell")
        ax2.set_ylim(0,100)
        ax2.set_title("RSI")
        ax2.grid(True); ax2.legend()

        if equity_curve:
            times, values = zip(*equity_curve)
            ax3.plot(times, values, label="Equity", color="black")
            ax3.set_title("Equity Curve")
            ax3.grid(True)

        st.pyplot(fig)
        st.write("Журнал сделок:", trade_log[:20])
    else:
        st.warning("Не удалось получить свечи для бэктеста.")
else:
    st.info("Выберите торговую пару для бэктеста.")



# =========================
# ДОБАВЛЕНО В v8: Форматирование таблиц через pandas.DataFrame
# =========================

def show_positions_table(positions, title="Таблица"):
    if positions:
        try:
            df = pd.DataFrame(positions)
            st.dataframe(df)
        except Exception as e:
            st.write(positions)
    else:
        st.info(f"Нет данных: {title}")

# Перепишем вывод позиций и сделок
if "open_positions" in locals():
    st.markdown("### 📂 Открытые позиции (Биржа)")
    show_positions_table(open_positions, "Открытые позиции")

if "closed_positions" in locals():
    st.markdown("### 📂 Закрытые сделки (Биржа)")
    show_positions_table(closed_positions, "Закрытые сделки")

# Для бэктеста: журнал сделок в DataFrame
if "trade_log" in locals() and trade_log:
    try:
        df_trades = pd.DataFrame(trade_log)
        st.markdown("### 📒 Журнал сделок (бэктест)")
        st.dataframe(df_trades)
    except Exception:
        st.write(trade_log)



# =========================
st.subheader("📊 Бэктест стратегии (EMA+RSI+Stoch+BB+Volume Filter)")

if symbol:
    df_bt = fetch_klines(symbol, interval, candle_limit)
    df_bt = add_indicators(df_bt, ema_short, ema_long, stoch_k, stoch_d, bb_period, bb_dev)
    if not df_bt.empty:
        capital = 10000
        equity = capital
        equity_curve = []
        position = None
        entry_price = 0
        trade_log = []

        for i in range(1, len(df_bt)):
            price = df_bt.iloc[i]["close"]
            time = df_bt.iloc[i]["timestamp"]
            vol = df_bt.iloc[i]["volume"]
            prev, last = df_bt.iloc[i-1], df_bt.iloc[i]

            crossed_up = prev["EMA_short"] <= prev["EMA_long"] and last["EMA_short"] > last["EMA_long"]
            crossed_dn = prev["EMA_short"] >= prev["EMA_long"] and last["EMA_short"] < last["EMA_long"]
            rsi_buy_cond = last["RSI"] > rsi_buy
            rsi_sell_cond = last["RSI"] < rsi_sell

            stoch_buy = last["StochK"] < stoch_oversold and last["StochK"] > last["StochD"]
            stoch_sell = last["StochK"] > stoch_overbought and last["StochK"] < last["StochD"]

            bb_buy = last["close"] <= last["BB_lower"]
            bb_sell = last["close"] >= last["BB_upper"]

            buy_sig = crossed_up and rsi_buy_cond and (stoch_buy or bb_buy) and vol >= volume_filter
            sell_sig = crossed_dn and rsi_sell_cond and (stoch_sell or bb_sell) and vol >= volume_filter

            if position is None:
                if buy_sig:
                    position = "long"; entry_price = price
                    trade_log.append((time, "Buy", price, vol, last["RSI"], last["StochK"], last["BB_lower"]))
                elif sell_sig:
                    position = "short"; entry_price = price
                    trade_log.append((time, "Sell", price, vol, last["RSI"], last["StochK"], last["BB_upper"]))
            else:
                if position == "long" and sell_sig:
                    pnl = price - entry_price
                    equity += pnl
                    trade_log.append((time, "Close Long", price, pnl, equity, vol))
                    position = None
                elif position == "short" and buy_sig:
                    pnl = entry_price - price
                    equity += pnl
                    trade_log.append((time, "Close Short", price, pnl, equity, vol))
                    position = None
            equity_curve.append((time, equity))

        # Визуализация
        fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5,1,figsize=(14,18),sharex=True)
        ax1.plot(df_bt["timestamp"], df_bt["close"], label="Цена", color="gray")
        ax1.plot(df_bt["timestamp"], df_bt["EMA_short"], label=f"EMA {ema_short}", color="blue")
        ax1.plot(df_bt["timestamp"], df_bt["EMA_long"], label=f"EMA {ema_long}", color="red")
        ax1.plot(df_bt["timestamp"], df_bt["BB_upper"], linestyle="--", color="orange", label="BB Upper")
        ax1.plot(df_bt["timestamp"], df_bt["BB_middle"], linestyle="--", color="black", label="BB Middle")
        ax1.plot(df_bt["timestamp"], df_bt["BB_lower"], linestyle="--", color="orange", label="BB Lower")
        for tr in trade_log:
            if tr[1]=="Buy":
                ax1.scatter(tr[0], tr[2], marker="^", color="green", s=100)
            elif tr[1]=="Sell":
                ax1.scatter(tr[0], tr[2], marker="v", color="red", s=100)
        ax1.set_title(f"Бэктест {symbol} [{interval_label}] EMA+RSI+Stoch+BB+Volume Filter")
        ax1.legend(); ax1.grid(True)

        ax2.plot(df_bt["timestamp"], df_bt["RSI"], label="RSI", color="purple")
        ax2.axhline(rsi_buy, color="green", linestyle="--", label="RSI Buy")
        ax2.axhline(rsi_sell, color="red", linestyle="--", label="RSI Sell")
        ax2.set_ylim(0,100)
        ax2.set_title("RSI")
        ax2.grid(True); ax2.legend()

        ax3.plot(df_bt["timestamp"], df_bt["StochK"], label="Stoch %K", color="blue")
        ax3.plot(df_bt["timestamp"], df_bt["StochD"], label="Stoch %D", color="red")
        ax3.axhline(stoch_overbought, color="red", linestyle="--")
        ax3.axhline(stoch_oversold, color="green", linestyle="--")
        ax3.set_ylim(0,100)
        ax3.set_title("Stochastic")
        ax3.grid(True); ax3.legend()

        if equity_curve:
            times, values = zip(*equity_curve)
            ax4.plot(times, values, label="Equity", color="black")
            ax4.set_title("Equity Curve")
            ax4.grid(True)

        ax5.bar(df_bt["timestamp"], df_bt["volume"],
                color=["red" if v < volume_filter else "blue" for v in df_bt["volume"]],
                alpha=0.6)
        ax5.axhline(volume_filter, color="orange", linestyle="--", label="Фильтр")
        ax5.set_title("Объемы")
        ax5.legend()
        ax5.grid(True)

        st.pyplot(fig)
        try:
            df_trades = pd.DataFrame(trade_log,
                                     columns=["time","action","price","volume","RSI","StochK","BB_ref"])
            st.markdown("### 📒 Журнал сделок (v12)")
            st.dataframe(df_trades)
        except Exception:
            st.write(trade_log)
    else:
        st.warning("Не удалось получить свечи для бэктеста.")
else:
    st.info("Выберите торговую пару для бэктеста.")
