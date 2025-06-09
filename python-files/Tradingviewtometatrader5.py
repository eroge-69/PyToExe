from sanic import Sanic, response
import MetaTrader5 as mt5

app = Sanic("MT5Webhook")

if not mt5.initialize():
    print("MT5 initialization failed")
    exit()

def print_request(req):
    print("Sending order with parameters:")
    for k, v in req.items():
        print(f"  {k}: {v}")

def get_min_volume(symbol):
    info = mt5.symbol_info(symbol)
    if info is None:
        return None
    return info.volume_min

@app.route('/webhook', methods=['POST'])
async def webhook(request):
    data = request.json
    passphrase = data.get("passphrase")
    if passphrase != "SECRET123":
        return response.json({'status': 'unauthorized'}, status=401)

    action = data.get("action")  # 'buy' ou 'sell'
    symbol = data.get("symbol")
    if not symbol:
        return response.json({'status': 'error', 'message': 'symbol is required'}, status=400)

    lot_from_json = float(data.get("lot", 0.1))
    deviation = int(data.get("deviation", 20))
    magic = int(data.get("magic", 123456))

    if not mt5.symbol_select(symbol, True):
        return response.json({'status': f'failed to select symbol {symbol}'}, status=400)

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return response.json({'status': 'error', 'message': 'failed to get symbol tick'}, status=400)
    price_ask = tick.ask
    price_bid = tick.bid

    positions = mt5.positions_get(symbol=symbol) or []

    lot_to_use = lot_from_json

    pos = next((p for p in positions if p.magic == magic), None)
    if pos:
        price_open = pos.price_open
        current_price = price_bid if pos.type == mt5.ORDER_TYPE_BUY else price_ask
        profit = (current_price - price_open) * pos.volume if pos.type == mt5.ORDER_TYPE_BUY else (price_open - current_price) * pos.volume
        if profit < 0:
            lot_to_use = pos.volume * 2
        else:
            lot_to_use = lot_from_json

    min_vol = get_min_volume(symbol)
    if min_vol is not None and lot_to_use < min_vol:
        lot_to_use = min_vol

    if action not in ["buy", "sell"]:
        return response.json({'status': 'invalid action'}, status=400)

    desired_type = mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL
    price = price_ask if desired_type == mt5.ORDER_TYPE_BUY else price_bid

    # Fermer les positions opposées
    for p in positions:
        if p.magic == magic and p.type != desired_type:
            close_type = mt5.ORDER_TYPE_SELL if p.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            close_price = price_bid if close_type == mt5.ORDER_TYPE_SELL else price_ask
            close_req = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": p.volume,
                "type": close_type,
                "position": p.ticket,
                "price": close_price,
                "deviation": deviation,
                "magic": magic,
                "comment": "auto-close before reverse",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
            }
            print_request(close_req)
            close_res = mt5.order_send(close_req)
            print("Close opposite position result:", close_res)

    order_req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_to_use,
        "type": desired_type,
        "price": price,
        "deviation": deviation,
        "magic": magic,
        "comment": "open with martingale",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC
    }
    print_request(order_req)
    result = mt5.order_send(order_req)
    print("order_send result:", result)

    if result is None:
        return response.json({'status': 'order failed', 'error': 'order_send returned None'}, status=500)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return response.json({'status': 'order failed', 'retcode': result.retcode}, status=400)

    return response.json({'status': 'order placed', 'order_id': result.order, 'lot_used': lot_to_use})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
