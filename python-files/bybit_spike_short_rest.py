# bybit_spike_short_rest.py
# - Каждую ~1с тянет /v5/market/tickers?category=linear (фильтр: только USDT-пары)
# - Входит в SHORT, если рост за 1ч >= PRICE_THR (фронт-детектор + кулдаун)
# - По входу: TP reduceOnly BUY по PNL_TARGET (если ENABLE_TP) и лимитные SELL усреднения (ADD1/ADD2)
# - Автоподдержка TP: переустанавливает при изменении avgPrice/size
# - MAX_OPEN_POS: при достижении лимита скан рынка паузится (лечим только TP)
# - При старте подхватывает уже открытые шорты (USDT) для сопровождения
# - Если позиция закрыта (в т.ч. вручную) — все остаточные ордера по символу отменяются

import json
import math
import random
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlencode

import requests

from config import (
    API_KEY, API_SECRET,
    RISK_PCT, LEVERAGE, PRICE_THR,
    MAX_OPEN_POS, COOLDOWN_MIN,
    ENABLE_ADD1, ADD1_PCT, ENABLE_ADD2, ADD2_PCT,
    ENABLE_TP, PNL_TARGET,
    DRY_RUN, show_config, log_message
)

BASE = "https://api.bybit.com"
RECV_WINDOW = "20000"  # увеличенное окно на подпись

def now_ms() -> int:
    return int(time.time() * 1000)

def sleep_s(sec: float):
    time.sleep(sec + random.uniform(-0.1, 0.1))

# ------------------------- Подпись V5 -------------------------
def sign_v5_for_body_str(ts_ms: int, body_str: str) -> str:
    """Подписать СТРОКУ тела запроса (должна быть той же строкой, что уйдёт)."""
    pre = f"{ts_ms}{API_KEY}{RECV_WINDOW}{body_str}"
    import hmac, hashlib
    return hmac.new(API_SECRET.encode(), pre.encode(), hashlib.sha256).hexdigest()

def sign_v5_for_query_str(ts_ms: int, qs: str) -> str:
    """Подписать СТРОКУ query (должна быть той же строкой, что уйдёт)."""
    pre = f"{ts_ms}{API_KEY}{RECV_WINDOW}{qs}"
    import hmac, hashlib
    return hmac.new(API_SECRET.encode(), pre.encode(), hashlib.sha256).hexdigest()

def headers_private(ts_ms: int, sign: str) -> Dict[str, str]:
    return {
        "X-BAPI-API-KEY": API_KEY,
        "X-BAPI-TIMESTAMP": str(ts_ms),
        "X-BAPI-RECV-WINDOW": RECV_WINDOW,
        "X-BAPI-SIGN": sign,
        "Content-Type": "application/json",
    }

# ------------------------- Публичные -------------------------
def get_all_linear_tickers() -> List[dict]:
    try:
        r = requests.get(f"{BASE}/v5/market/tickers",
                         params={"category": "linear"},
                         timeout=10)
        r.raise_for_status()
        return r.json().get("result", {}).get("list", []) or []
    except Exception as e:
        log_message(f"Ошибка получения тикеров: {e}", "WARN")
        return []

_instrument_cache: Dict[str, dict] = {}

def get_instrument(symbol: str) -> Optional[dict]:
    if symbol in _instrument_cache:
        return _instrument_cache[symbol]
    try:
        res = requests.get(f"{BASE}/v5/market/instruments-info",
                           params={"category": "linear", "symbol": symbol},
                           timeout=10)
        res.raise_for_status()
        arr = res.json().get("result", {}).get("list", []) or []
        if not arr:
            return None
        _instrument_cache[symbol] = arr[0]
        return _instrument_cache[symbol]
    except Exception as e:
        log_message(f"Ошибка информации об инструменте {symbol}: {e}", "WARN")
        return None

def round_price(symbol: str, price: float) -> float:
    info = get_instrument(symbol)
    if not info:
        return float(price)
    tick = info.get("priceFilter", {}).get("tickSize")
    if not tick:
        return float(price)
    ts = float(tick)
    return math.floor(price / ts) * ts  # BUY (TP) округляем вниз (консервативно)

def round_qty(symbol: str, qty: float) -> float:
    info = get_instrument(symbol)
    if not info:
        return float(qty)
    lf = info.get("lotSizeFilter", {})
    step = lf.get("qtyStep")
    min_qty = lf.get("minOrderQty")
    if step:
        st = float(step)
        qty = math.floor(qty / st) * st
    if min_qty and qty < float(min_qty):
        qty = float(min_qty)
    return float(qty)

# ------------------------- Приватные (строгое совпадение строк) -------------------------
def post_private(path: str, body: Dict[str, Any]) -> dict:
    """
    Для POST формируем body_str компактно (без пробелов) и
    подписываем именно эту строку, её же отправляем в data.
    """
    ts = now_ms()
    body_str = json.dumps(body or {}, separators=(',', ':'), ensure_ascii=False)
    sign = sign_v5_for_body_str(ts, body_str)
    r = requests.post(f"{BASE}{path}",
                      headers=headers_private(ts, sign),
                      data=body_str,
                      timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("retCode") != 0:
        raise RuntimeError(f"Bybit error {data.get('retCode')}: {data.get('retMsg')}")
    return data

def get_private(path: str, params: Dict[str, Any]) -> dict:
    """
    Для GET строим отсортированный query-string, подписываем его и
    отправляем запрос с ЭТИМ ЖЕ qs в URL (без params=), чтобы строки совпали.
    """
    ts = now_ms()
    params = params or {}
    items = sorted(params.items())              # детерминированный порядок
    qs = urlencode(items, doseq=True)
    sign = sign_v5_for_query_str(ts, qs)
    url = f"{BASE}{path}?{qs}" if qs else f"{BASE}{path}"
    r = requests.get(url,
                     headers=headers_private(ts, sign),
                     timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("retCode") != 0:
        raise RuntimeError(f"Bybit error {data.get('retCode')}: {data.get('retMsg')}")
    return data

def set_leverage(symbol: str, lev: float):
    if DRY_RUN or not API_KEY or not API_SECRET:
        return
    body = {"category": "linear", "symbol": symbol,
            "buyLeverage": str(lev), "sellLeverage": str(lev)}
    try:
        post_private("/v5/position/set-leverage", body)
        log_message(f"Плечо {lev} установлено для {symbol}", "INFO")
    except Exception as e:
        msg = str(e)
        if "110043" in msg:  # leverage not modified
            log_message(f"Плечо уже {lev} для {symbol} (не изменено)", "INFO")
        else:
            log_message(f"Ошибка установки плеча {symbol}: {e}", "WARN")

def wallet_usdt_free() -> float:
    if DRY_RUN or not API_KEY or not API_SECRET:
        return 1000.0  # фиктивный баланс в DRY
    for acc_type in ("UNIFIED", "CONTRACT"):
        try:
            data = get_private("/v5/account/wallet-balance", {"accountType": acc_type})
            for acc in data.get("result", {}).get("list", []) or []:
                for c in acc.get("coin", []):
                    if c.get("coin") == "USDT":
                        v = c.get("availableToWithdraw") or c.get("walletBalance") or "0"
                        return float(v)
        except Exception as e:
            log_message(f"Ошибка получения баланса ({acc_type}): {e}", "WARN")
    return 0.0

# ------------------------- Ордера -------------------------
def place_market_short(symbol: str, qty: float) -> Optional[str]:
    if qty <= 0:
        log_message(f"[SKIP] {symbol}: qty=0", "WARN")
        return None
    if DRY_RUN or not API_KEY or not API_SECRET:
        log_message(f"[DRY] SELL market {symbol} qty={qty}", "INFO")
        return "dry-order-id"
    try:
        body = {"category": "linear", "symbol": symbol, "side": "Sell",
                "orderType": "Market", "qty": str(qty)}
        data = post_private("/v5/order/create", body)
        oid = data.get("result", {}).get("orderId")
        log_message(f"[TRADE] SELL market {symbol} qty={qty} id={oid}", "TRADE")
        return oid
    except Exception as e:
        log_message(f"Ошибка рыночного SELL {symbol}: {e}", "ERROR")
        return None

def place_limit_sell(symbol: str, qty: float, price: float) -> Optional[str]:
    price = round_price(symbol, price)
    qty = round_qty(symbol, qty)
    if qty <= 0:
        log_message(f"[SKIP] ADD {symbol}: qty=0", "WARN")
        return None
    if DRY_RUN or not API_KEY or not API_SECRET:
        log_message(f"[DRY] ADD SELL {symbol} qty={qty} price={price}", "INFO")
        return "dry-add-id"
    try:
        body = {"category": "linear", "symbol": symbol, "side": "Sell",
                "orderType": "Limit", "qty": str(qty), "price": str(price)}
        data = post_private("/v5/order/create", body)
        oid = data.get("result", {}).get("orderId")
        log_message(f"[ORDER] ADD SELL {symbol} qty={qty} price={price} id={oid}", "ORDER")
        return oid
    except Exception as e:
        log_message(f"Ошибка лимитного SELL {symbol}: {e}", "ERROR")
        return None

def place_reduceonly_tp(symbol: str, qty: float, price: float) -> Optional[str]:
    price = round_price(symbol, price)
    qty = round_qty(symbol, qty)
    if qty <= 0:
        log_message(f"[SKIP] TP {symbol}: qty=0", "WARN")
        return None
    if DRY_RUN or not API_KEY or not API_SECRET:
        log_message(f"[DRY] TP BUY (reduceOnly) {symbol} qty={qty} price={price}", "INFO")
        return "dry-tp-id"
    try:
        body = {"category": "linear", "symbol": symbol, "side": "Buy",
                "orderType": "Limit", "qty": str(qty), "price": str(price), "reduceOnly": True}
        data = post_private("/v5/order/create", body)
        oid = data.get("result", {}).get("orderId")
        log_message(f"[ORDER] TP set {symbol} qty={qty} price={price} id={oid}", "ORDER")
        return oid
    except Exception as e:
        log_message(f"Ошибка установки TP {symbol}: {e}", "ERROR")
        return None

def cancel_order(symbol: str, order_id: str) -> bool:
    if DRY_RUN or not API_KEY or not API_SECRET:
        log_message(f"[DRY] CANCEL {symbol} id={order_id}", "INFO")
        return True
    try:
        body = {"category": "linear", "symbol": symbol, "orderId": order_id}
        post_private("/v5/order/cancel", body)
        log_message(f"[CANCEL] {symbol} id={order_id}", "INFO")
        return True
    except Exception as e:
        log_message(f"Ошибка отмены ордера {symbol}: {e}", "ERROR")
        return False

def list_open_orders(symbol: str) -> List[dict]:
    if DRY_RUN or not API_KEY or not API_SECRET:
        return []
    try:
        data = get_private("/v5/order/realtime", {"category": "linear", "symbol": symbol})
        return (data.get("result", {}) or {}).get("list", []) or []
    except Exception as e:
        log_message(f"Ошибка получения ордеров {symbol}: {e}", "WARN")
        return []

# ---------- утилита: отменить все ордера по символу ----------
def cancel_all_orders_for_symbol(symbol: str):
    orders = list_open_orders(symbol)
    cnt = 0
    for o in orders:
        oid = o.get("orderId")
        if oid:
            if cancel_order(symbol, oid):
                cnt += 1
    if cnt > 0:
        log_message(f"[CLEANUP] Отменено ордеров по {symbol}: {cnt}", "INFO")

def get_short_position_info(symbol: str) -> Tuple[float, Optional[float]]:
    if DRY_RUN or not API_KEY or not API_SECRET:
        return (0.0, None)
    try:
        params = {"category": "linear", "symbol": symbol, "settleCoin": "USDT"}
        data = get_private("/v5/position/list", params)
        for p in (data.get("result", {}) or {}).get("list", []) or []:
            if p.get("symbol") == symbol and p.get("side") == "Sell":
                sz = float(p.get("size", "0") or 0)
                ap = p.get("avgPrice")
                return (sz, float(ap) if ap else None)
    except Exception as e:
        log_message(f"Ошибка получения позиции {symbol}: {e}", "WARN")
    return (0.0, None)

# ------------------------- TP математика -------------------------
def compute_tp_price_short(entry_price: float) -> float:
    # +PNL_TARGET на маржу при плече LEVERAGE ≈ падение цены на PNL_TARGET/LEVERAGE
    move = PNL_TARGET / max(LEVERAGE, 1e-9)
    return entry_price * (1.0 - move)

def ensure_up_to_date_tp_for_short(symbol: str) -> None:
    if not ENABLE_TP:
        return
    size, avg_price = get_short_position_info(symbol)
    if size <= 0 or not avg_price or avg_price <= 0:
        return

    desired_qty = round_qty(symbol, size)
    desired_price = round_price(symbol, compute_tp_price_short(avg_price))

    orders = list_open_orders(symbol)
    tp_orders = []
    for o in orders:
        try:
            if (o.get("side") == "Buy"
                and str(o.get("reduceOnly", "false")).lower() == "true"
                and o.get("orderType") == "Limit"):
                tp_orders.append(o)
        except Exception:
            continue

    match = False
    for o in tp_orders:
        try:
            o_price = round_price(symbol, float(o.get("price")))
            o_qty = round_qty(symbol, float(o.get("qty")))
            if o_price == desired_price and o_qty >= desired_qty:
                match = True
                break
        except Exception:
            continue

    if match:
        return

    for o in tp_orders:
        oid = o.get("orderId")
        if oid:
            cancel_order(symbol, oid)

    place_reduceonly_tp(symbol, desired_qty, desired_price)

# ------------------------- Подсчёт позиций / инициализация -------------------------
def count_open_positions_linear() -> int:
    if DRY_RUN or not API_KEY or not API_SECRET:
        return 0
    try:
        params = {"category": "linear", "settleCoin": "USDT"}
        data = get_private("/v5/position/list", params)
        cnt = 0
        for p in (data.get("result", {}) or {}).get("list", []) or []:
            sz = float(p.get("size", "0") or 0)
            if sz > 0:
                cnt += 1
        return cnt
    except Exception as e:
        log_message(f"Ошибка подсчёта позиций: {e}", "WARN")
        return 0

def seed_managed_symbols() -> Set[str]:
    if DRY_RUN or not API_KEY or not API_SECRET:
        return set()
    syms = set()
    try:
        params = {"category": "linear", "settleCoin": "USDT"}
        data = get_private("/v5/position/list", params)
        for p in (data.get("result", {}) or {}).get("list", []) or []:
            if p.get("side") == "Sell" and float(p.get("size", "0") or 0) > 0:
                sym = p.get("symbol", "")
                if "USDT" in sym:
                    syms.add(sym)
                    log_message(f"Найдена открытая позиция: {sym}", "INFO")
    except Exception as e:
        log_message(f"Ошибка инициализации позиций: {e}", "WARN")
    return syms

# ------------------------- Главный цикл -------------------------
last_entry_ts: Dict[str, int] = {}
prev_above: Dict[str, bool] = {}
managed_symbols: Set[str] = set()

def main():
    global managed_symbols
    show_config()

    log_message(
        f"Старт | THR={PRICE_THR*100:.1f}% | LEV={LEVERAGE} | RISK={RISK_PCT*100:.2f}% | "
        f"TP={'ON' if ENABLE_TP else 'OFF'}({PNL_TARGET*100:.0f}%) | "
        f"ADD1={'ON' if ENABLE_ADD1 else 'OFF'}({ADD1_PCT*100:.0f}%) | "
        f"ADD2={'ON' if ENABLE_ADD2 else 'OFF'}({ADD2_PCT*100:.0f}%) | "
        f"MAX_OPEN_POS={MAX_OPEN_POS}",
        "INFO"
    )

    # Подхват уже открытых шортов (для сопровождения)
    managed_symbols = seed_managed_symbols()
    if managed_symbols:
        log_message(f"[INIT] Уже открытые шорты: {managed_symbols}", "INFO")

    while True:
        try:
            # 0) лимит позиций
            open_cnt = count_open_positions_linear()
            if open_cnt >= MAX_OPEN_POS:
                log_message(f"[LIMIT] Открыто {open_cnt}/{MAX_OPEN_POS}. Скан пауза; сопровождаем/чистим.", "INFO")
                for sym in list(managed_symbols):
                    size, _ = get_short_position_info(sym)
                    if size <= 0:
                        # позиция закрыта -> чистим ВСЕ ордера по символу
                        cancel_all_orders_for_symbol(sym)
                        managed_symbols.discard(sym)
                        continue
                    ensure_up_to_date_tp_for_short(sym)
                sleep_s(1.0)
                continue

            # 1) скан рынка
            tickers = get_all_linear_tickers()
            tnow = int(time.time())

            for tkr in tickers:
                symbol = tkr.get("symbol", "")
                if "USDT" not in symbol:
                    continue  # белый список: только USDT

                # перепроверка лимита прямо во время скана
                open_cnt = count_open_positions_linear()
                if open_cnt >= MAX_OPEN_POS:
                    log_message(f"[LIMIT] Достигнут во время скана: {open_cnt}/{MAX_OPEN_POS}", "INFO")
                    break

                last_s, prev1h_s = tkr.get("lastPrice"), tkr.get("prevPrice1h")
                if not last_s or not prev1h_s:
                    continue
                try:
                    last = float(last_s)
                    prev1h = float(prev1h_s)
                except ValueError:
                    continue
                if prev1h <= 0:
                    continue

                change = (last - prev1h) / prev1h
                above = change >= PRICE_THR

                was = prev_above.get(symbol, False)
                prev_above[symbol] = above
                if (not above or was) or (tnow - last_entry_ts.get(symbol, 0) < COOLDOWN_MIN * 60):
                    continue  # нет фронта или кулдаун

                # плечо (в live)
                if not DRY_RUN and API_KEY and API_SECRET:
                    set_leverage(symbol, LEVERAGE)

                # размер позиции: (free_USDT * RISK_PCT * LEVERAGE) / last
                free = wallet_usdt_free()
                notional = max(free, 0.0) * RISK_PCT * LEVERAGE
                if notional <= 0:
                    log_message(f"[SKIP] {symbol}: notional=0", "WARN")
                    continue
                qty = round_qty(symbol, notional / max(last, 1e-9))
                if qty <= 0:
                    log_message(f"[SKIP] {symbol}: qty<=0", "WARN")
                    continue

                # вход
                oid = place_market_short(symbol, qty)
                if oid is None:
                    continue

                # entry
                _, avg_price = get_short_position_info(symbol)
                entry = avg_price if avg_price else last

                # тейк-профит
                if ENABLE_TP:
                    tp_price = round_price(symbol, compute_tp_price_short(entry))
                    place_reduceonly_tp(symbol, qty, tp_price)

                # усреднения
                if ENABLE_ADD1:
                    add1_price = round_price(symbol, entry * (1.0 + ADD1_PCT))
                    place_limit_sell(symbol, qty, add1_price)
                if ENABLE_ADD2:
                    add2_price = round_price(symbol, entry * (1.0 + ADD2_PCT))
                    place_limit_sell(symbol, qty, add2_price)

                last_entry_ts[symbol] = tnow
                managed_symbols.add(symbol)

                parts = [f"СИГНАЛ: {symbol} +{change*100:.2f}%/1h -> SHORT qty={qty:.6f} entry~{entry:.6f}"]
                if ENABLE_TP:  parts.append(f"TP@{tp_price:.6f}")
                if ENABLE_ADD1: parts.append(f"ADD1@{add1_price:.6f}")
                if ENABLE_ADD2: parts.append(f"ADD2@{add2_price:.6f}")
                log_message(" | ".join(parts), "SIGNAL")

            # 2) сопровождение / очистка после закрытия
            for sym in list(managed_symbols):
                size, _ = get_short_position_info(sym)
                if size <= 0:
                    # позиция закрылась (руками или по TP) -> убираем остаточные ордера
                    cancel_all_orders_for_symbol(sym)
                    managed_symbols.discard(sym)
                    continue
                # позиция жива -> поддерживаем TP
                ensure_up_to_date_tp_for_short(sym)

            sleep_s(1.0)

        except KeyboardInterrupt:
            log_message("Остановка бота по Ctrl+C", "INFO")
            break
        except Exception as e:
            log_message(f"Ошибка в основном цикле: {e}", "ERROR")
            time.sleep(3)

if __name__ == "__main__":
    main()