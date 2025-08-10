"""
dhan_signal_app.py

Final v1 - Option Crossover Strategy (Alerts-only; Dummy + Live placeholder)
- Instruments: NIFTY / BANKNIFTY / SENSEX
- Expiry: WEEKLY / MONTHLY
- Strike selection: ATM / OTM / ITM (offset)
- TF selectable: 5-min or 15-min (dropdown)
- Crossover both directions (CE>PE <-> PE>CE)
- Post-crossover: require CE & PE candle bodies NOT to overlap (strict)
- If crossover candle overlaps, wait until future candle has non-overlap, then enter next TF candle open
- Entry = buy the option type that is 'higher' after crossover (CE if CE>PE, PE if PE>CE)
- SL/Target per instrument (defaults), lots selectable, max trades/day, forced exit at 15:26 IST
- Logs: trade_log.csv, skipped_log.csv, event_log.csv, candle_log.csv, summary_log.csv
- Test run (simulator) included for quick checks
- Option C local key storage pattern included (no password)
"""

import os
import csv
import json
import time
import threading
from datetime import datetime, time as dtime, timedelta
import pytz
import random
import base64
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# -----------------------
# Constants & defaults
# -----------------------
IST = pytz.timezone("Asia/Kolkata")
CONFIG_FILE = "config.json"
KEY_FILE = "local_key.bin"
CSV_TRADE_LOG = "trade_log.csv"
CSV_SKIPPED_LOG = "skipped_log.csv"
CSV_EVENT_LOG = "event_log.csv"
CSV_CANDLE_LOG = "candle_log.csv"
CSV_SUMMARY_LOG = "summary_log.csv"

DEFAULTS = {
    "eval_minute": 14,   # 09:14
    "check_minute": 15,  # 09:15
    "forced_exit_time": "15:26",
    "max_trades": 3,
    "lots": 1,
    "tf_choice": "5-min",  # or '15-min'
    "strike_mode": "ATM",  # ATM/OTM/ITM
    "strike_offset": 0,
    "instrument": "NIFTY",
    "expiry": "WEEKLY",
    "contract_size": {"NIFTY":50, "BANKNIFTY":15, "SENSEX":5},
    "sl_target": {"NIFTY":[10,15], "BANKNIFTY":[30,40], "SENSEX":[30,40]}
}

# -----------------------
# Utilities
# -----------------------
def now_ist():
    return datetime.now(pytz.utc).astimezone(IST)

def parse_hhmm(s):
    h,m = map(int, s.split(':'))
    return dtime(hour=h, minute=m)

def append_csv(filename, row, header=None):
    exists = os.path.isfile(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if (not exists) and header:
            w.writerow(header)
        w.writerow(row)

def ensure_csv_headers():
    if not os.path.isfile(CSV_TRADE_LOG):
        append_csv(CSV_TRADE_LOG, [], header=["Date","Time","Instrument","Expiry","Strike","OptType","Lots","Direction","EntryPrice","SL","Target","ExitPrice","Result","Notes"])
    if not os.path.isfile(CSV_SKIPPED_LOG):
        append_csv(CSV_SKIPPED_LOG, [], header=["Date","Time","Instrument","Expiry","Strike","OptType","Reason","Details"])
    if not os.path.isfile(CSV_EVENT_LOG):
        append_csv(CSV_EVENT_LOG, [], header=["Date","Time","Instrument","Event","Detail"])
    if not os.path.isfile(CSV_CANDLE_LOG):
        append_csv(CSV_CANDLE_LOG, [], header=["Date","Time","Instrument","Expiry","Strike","TF","CE_open","CE_close","CE_high","CE_low","PE_open","PE_close","PE_high","PE_low"])
    if not os.path.isfile(CSV_SUMMARY_LOG):
        append_csv(CSV_SUMMARY_LOG, [], header=["Date","TotalTrades","Taken","Skipped","TotalPLPoints","TotalPLRs","WinRatePct","Notes"])

def load_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULTS.copy()
    else:
        return DEFAULTS.copy()

def save_config(cfg):
    with open(CONFIG_FILE,"w",encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

# -----------------------
# Local-key (Option C) helpers
# -----------------------
def ensure_local_key():
    if os.path.isfile(KEY_FILE):
        with open(KEY_FILE,"rb") as f:
            return f.read()
    else:
        if CRYPTO_AVAILABLE:
            key = Fernet.generate_key()
            with open(KEY_FILE,"wb") as f:
                f.write(key)
            return key
        else:
            key = base64.urlsafe_b64encode(os.urandom(32))
            with open(KEY_FILE,"wb") as f:
                f.write(key)
            return key

def encrypt_bytes(b):
    k = ensure_local_key()
    if CRYPTO_AVAILABLE:
        f = Fernet(k)
        return f.encrypt(b)
    else:
        return base64.b64encode(b)

def decrypt_bytes(b):
    k = ensure_local_key()
    if CRYPTO_AVAILABLE:
        f = Fernet(k)
        return f.decrypt(b)
    else:
        return base64.b64decode(b)

# -----------------------
# Dhan connector placeholders
# -----------------------
class DhanConnectorSim:
    """Simulator that emits TF candles for CE and PE. For testing only."""
    def __init__(self, tf='5-min'):
        self.tf = tf
        self.running = False
        self.subs = []
        self._rng = random.Random(int(time.time()) % 999999)
        self.spot = 22000.0

    def set_tf(self, tf):
        self.tf = tf

    def register(self, cb):
        self.subs.append(cb)

    def connect(self):
        self.running = True

    def disconnect(self):
        self.running = False

    def start_stream(self):
        t = threading.Thread(target=self._stream, daemon=True)
        t.start()

    def _stream(self):
        # speeded up intervals: 5-min -> 4s, 15-min -> 12s
        interval = 4 if self.tf == '5-min' else 12
        ce = 100.0 + self._rng.uniform(-3,3)
        pe = 100.0 + self._rng.uniform(-3,3)
        while self.running:
            ce_c = self._make_candle(ce)
            pe_c = self._make_candle(pe)
            ce = ce_c['close']
            pe = max(1.0, pe + (self._rng.uniform(-1.5,1.5) - (ce-100)*0.002))
            ts = now_ist().replace(second=0,microsecond=0)
            payload = {'time': ts, 'CE': ce_c, 'PE': pe_c, 'spot': self.spot}
            for cb in self.subs:
                try:
                    cb(payload, self.tf)
                except Exception as e:
                    print("Subscriber error:", e)
            time.sleep(interval)

    def _make_candle(self, center):
        o = round(max(1, center + self._rng.uniform(-2,2)),2)
        c = round(max(1, o + self._rng.uniform(-3,3)),2)
        high = round(max(o,c) + abs(self._rng.uniform(0,2)),2)
        low = round(min(o,c) - abs(self._rng.uniform(0,2)),2)
        return {'open':o,'high':high,'low':low,'close':c}

class DhanConnectorLive:
    """Stub for real Dhan integration. Replace methods to authenticate and push candle payloads
    with the same payload shape used by the simulator:
      payload = {'time': datetime_in_IST, 'CE':{'open':..,'high':..,'low':..,'close':..}, 'PE':{...}, 'spot': spot_price}
    Then call registered callbacks with (payload, tf)
    """
    def __init__(self):
        self.subs = []
        self.tf = '5-min'
        self.running = False

    def register(self, cb):
        self.subs.append(cb)

    def set_tf(self, tf):
        self.tf = tf

    def connect(self, client_id=None, access_token=None):
        # Implement actual Dhan websocket/login here
        self.running = True

    def disconnect(self):
        # close websocket
        self.running = False

    def start_stream(self):
        # start live streaming and call callbacks when candles are ready
        pass

# -----------------------
# Strategy Engine
# -----------------------
class OptionCrossoverEngine:
    def __init__(self, gui, connector):
        self.gui = gui
        self.connector = connector
        self.cfg = load_config()
        self.params = {}
        self.trades_taken = 0
        self.active_trade = None
        self.ce_pe_history = {}   # keyed by TF -> list of (ts,ce,pe)
        self.armed = {}           # keyed by TF -> {'armed_on_ts', 'direction'}
        self.waiting_for_non_overlap = {}  # keyed by TF -> bool
        self.initial_direction = {}  # keyed by TF -> initial
        self.summary = {'taken':0,'skipped':0,'pl_points':0.0,'pl_rs':0.0,'wins':0}
        ensure_csv_headers()
        self.connector.register(self.on_candle)
        self.running = False

    def set_params(self, params):
        # params from GUI
        self.params = params
        self.connector.set_tf(params.get('tf_choice','5-min'))
        # reset runtime state
        self.trades_taken = 0
        self.active_trade = None
        self.ce_pe_history = {}
        self.armed = {}
        self.waiting_for_non_overlap = {}
        self.initial_direction = {}
        self.summary = {'taken':0,'skipped':0,'pl_points':0.0,'pl_rs':0.0,'wins':0}

    def start(self):
        self.running = True
        self.connector.connect()
        self.connector.start_stream()
        self.gui.log(f"Engine started (mode={self.params.get('mode')}, TF={self.params.get('tf_choice')})")

    def stop(self):
        self.running = False
        self.connector.disconnect()
        self.gui.log("Engine stopped")

    def on_candle(self, payload, tf):
        # main callback for each TF candle
        if not self.running:
            return
        ts = payload['time']
        ce = payload['CE']
        pe = payload['PE']
        spot = payload.get('spot')

        # log candle
        append_csv(CSV_CANDLE_LOG, [ts.date(), ts.time(), self.params.get('instrument'), self.params.get('expiry'),
                                    self._strike_repr(), tf, ce['open'], ce['close'], ce['high'], ce['low'],
                                    pe['open'], pe['close'], pe['high'], pe['low']])

        # add to history
        self.ce_pe_history.setdefault(tf, []).append((ts,ce,pe))
        if len(self.ce_pe_history[tf]) > 500:
            self.ce_pe_history[tf].pop(0)

        # forced EOD exit
        forced_exit = parse_hhmm(self.cfg.get('forced_exit_time', DEFAULTS['forced_exit_time']))
        if ts.time() >= forced_exit:
            if self.active_trade:
                ex = self._get_exit_price(self.active_trade['direction'], ce, pe)
                self._close_trade(ex, "EOD Exit")
            self._write_summary()
            self.stop()
            return

        # if reached max trades, still detect crossovers and log as skipped
        if self.trades_taken >= int(self.params.get('max_trades', DEFAULTS['max_trades'])):
            self._detect_and_log_crossover(tf, ts, ce, pe, skipped_reason="Max Trades Reached")
            return

        # initial direction check at check_minute (only once per TF per day)
        check_minute = int(self.params.get('check_minute', DEFAULTS['check_minute']))
        flag_name = f"_initial_checked_{tf}"
        if (ts.minute == check_minute) and (not getattr(self, flag_name, False)):
            setattr(self, flag_name, True)
            ce_p = ce['close']; pe_p = pe['close']
            init = 'CE>PE' if (ce_p > pe_p) else ('PE>CE' if (pe_p > ce_p) else 'EQUAL')
            self.initial_direction[tf] = init
            append_csv(CSV_EVENT_LOG, [ts.date(), ts.time(), self.params.get('instrument'), f'INITIAL_{tf}', f'CE={ce_p} PE={pe_p} -> {init}'])
            self.gui.log(f"[{tf}] Initial check: {init}")

        # detect and handle crossovers
        self._detect_and_handle(tf, ts, ce, pe)

    def _detect_and_log_crossover(self, tf, ts, ce, pe, skipped_reason=None):
        hist = self.ce_pe_history.get(tf, [])
        if len(hist) < 2:
            return
        prev_ts, prev_ce, prev_pe = hist[-2]
        prev_state = 'CE>PE' if (prev_ce['close'] > prev_pe['close']) else ('PE>CE' if (prev_pe['close'] > prev_ce['close']) else 'EQUAL')
        curr_state = 'CE>PE' if (ce['close'] > pe['close']) else ('PE>CE' if (pe['close'] > ce['close']) else 'EQUAL')
        if (prev_state != curr_state) and (curr_state != 'EQUAL'):
            strike = self._strike_repr()
            opt_type = 'CE' if (curr_state=='CE>PE') else 'PE'
            append_csv(CSV_SKIPPED_LOG, [ts.date(), ts.time(), self.params.get('instrument'), self.params.get('expiry'), strike, opt_type, skipped_reason or 'Skipped', f'{prev_state}->{curr_state}'])
            self.summary['skipped'] += 1

    def _detect_and_handle(self, tf, ts, ce, pe):
        hist = self.ce_pe_history.get(tf, [])
        if len(hist) < 2:
            return
        prev_ts, prev_ce, prev_pe = hist[-2]
        prev_state = 'CE>PE' if (prev_ce['close'] > prev_pe['close']) else ('PE>CE' if (prev_pe['close'] > prev_ce['close']) else 'EQUAL')
        curr_state = 'CE>PE' if (ce['close'] > pe['close']) else ('PE>CE' if (pe['close'] > ce['close']) else 'EQUAL')

        if (prev_state != curr_state) and (curr_state != 'EQUAL'):
            # desired direction depends on initial; if we don't have initial, take any
            init = self.initial_direction.get(tf)
            wanted = None
            if init in ('CE>PE','PE>CE'):
                wanted = ('PE>CE' if init == 'CE>PE' else 'CE>PE')
            else:
                wanted = curr_state
            if curr_state == wanted:
                append_csv(CSV_EVENT_LOG, [ts.date(), ts.time(), self.params.get('instrument'), f'CROSSOVER_{tf}', f'{prev_state}->{curr_state}'])
                self.gui.log(f"[{tf}] Crossover detected {prev_state} -> {curr_state}")
                if self._bodies_do_not_overlap(ce, pe):
                    self.armed[tf] = {'armed_on_ts': ts, 'direction': curr_state}
                    append_csv(CSV_EVENT_LOG, [ts.date(), ts.time(), self.params.get('instrument'), f'BODY_OK_{tf}', 'Armed for entry next candle'])
                    self.gui.log(f"[{tf}] Bodies non-overlap on crossover candle — armed for entry next candle")
                else:
                    self.waiting_for_non_overlap[tf] = True
                    self.armed.pop(tf, None)
                    append_csv(CSV_EVENT_LOG, [ts.date(), ts.time(), self.params.get('instrument'), f'BODY_OVERLAP_{tf}', 'Waiting until bodies non-overlap'])
                    self.gui.log(f"[{tf}] Bodies overlap on crossover candle — will wait until non-overlap")
            else:
                append_csv(CSV_EVENT_LOG, [ts.date(), ts.time(), self.params.get('instrument'), f'CROSSOVER_IGNORED_{tf}', f'{prev_state}->{curr_state} not desired({wanted})'])
                self.gui.log(f"[{tf}] Crossover ignored (not desired direction)")
        else:
            # not a crossover; if waiting for non-overlap, re-check
            if self.waiting_for_non_overlap.get(tf, False):
                if self._bodies_do_not_overlap(ce, pe):
                    self.armed[tf] = {'armed_on_ts': ts, 'direction': curr_state}
                    self.waiting_for_non_overlap[tf] = False
                    append_csv(CSV_EVENT_LOG, [ts.date(), ts.time(), self.params.get('instrument'), f'BODY_OK_AFTER_WAIT_{tf}', 'Armed for entry next candle'])
                    self.gui.log(f"[{tf}] Bodies non-overlap after waiting — armed for entry next candle")

        # handle armed entries: enter on next candle (i.e., current ts > armed_on_ts)
        if tf in self.armed:
            info = self.armed[tf]
            armed_ts = info['armed_on_ts']
            if ts > armed_ts:
                direction = info['direction']
                opt_to_buy = 'CE' if direction == 'CE>PE' else 'PE'
                entry_price = ce['open'] if opt_to_buy == 'CE' else pe['open']
                self._place_trade(opt_to_buy, round(entry_price,2), ts)
                self.armed.pop(tf, None)
                self.waiting_for_non_overlap[tf] = False

    def _bodies_do_not_overlap(self, ce, pe):
        ce_max = max(ce['open'], ce['close'])
        ce_min = min(ce['open'], ce['close'])
        pe_max = max(pe['open'], pe['close'])
        pe_min = min(pe['open'], pe['close'])
        return (ce_max < pe_min) or (pe_max < ce_min)

    def _strike_repr(self):
        mode = self.params.get('strike_mode','ATM')
        offset = int(self.params.get('strike_offset',0))
        if mode == 'ATM':
            return 'ATM'
        return f"{mode}+{offset}"

    def _place_trade(self, opt_type, entry_price, ts):
        if self.trades_taken >= int(self.params.get('max_trades', DEFAULTS['max_trades'])):
            append_csv(CSV_SKIPPED_LOG, [ts.date(), ts.time(), self.params.get('instrument'), self.params.get('expiry'), self._strike_repr(), opt_type, 'Max Trades Reached', ''])
            self.summary['skipped'] += 1
            return
        inst = self.params.get('instrument')
        sl_pts, target_pts = self.cfg.get('sl_target', DEFAULTS['sl_target']).get(inst, DEFAULTS['sl_target'][inst])
        entry = entry_price
        sl = round(entry - sl_pts,2)
        target = round(entry + target_pts,2)
        trade = {
            'entry_time': ts,
            'instrument': inst,
            'expiry': self.params.get('expiry'),
            'strike': self._strike_repr(),
            'opt_type': opt_type,
            'lots': int(self.params.get('lots', DEFAULTS['lots'])),
            'direction': f"BUY_{opt_type}",
            'entry_price': entry,
            'SL': sl,
            'Target': target,
            'open': True
        }
        self.active_trade = trade
        self.trades_taken += 1
        self.summary['taken'] += 1
        append_csv(CSV_TRADE_LOG, [ts.date(), ts.time(), inst, trade['expiry'], trade['strike'], trade['opt_type'], trade['lots'], trade['direction'], trade['entry_price'], trade['SL'], trade['Target'], '', 'OPEN', 'Entered by strategy'])
        self.gui.alert(f"TRADE ALERT: {trade['direction']} {inst} {trade['strike']} Entry:{entry} SL:{sl} Target:{target} Lots:{trade['lots']}")
        self.gui.log(f"Placed paper trade: {trade['direction']} Entry {entry} SL {sl} Target {target}")

    def _get_exit_price(self, direction, ce, pe):
        return ce['close'] if direction.endswith('CE') else pe['close']

    def _close_trade(self, exit_price, reason):
        if not self.active_trade:
            return
        trade = self.active_trade
        trade['exit_time'] = now_ist()
        trade['exit_price'] = exit_price
        entry = trade['entry_price']
        if exit_price >= trade['Target']:
            result = 'Target Hit'
            self.summary['wins'] += 1
        elif exit_price <= trade['SL']:
            result = 'SL Hit'
        else:
            result = reason
        pl_points = round(exit_price - entry,2)
        contract_size = self.cfg.get('contract_size', DEFAULTS['contract_size']).get(trade['instrument'], DEFAULTS['contract_size'][trade['instrument']])
        pl_rs = round(pl_points * contract_size * trade['lots'],2)
        self.summary['pl_points'] += pl_points
        self.summary['pl_rs'] += pl_rs
        append_csv(CSV_TRADE_LOG, [trade['exit_time'].date(), trade['exit_time'].time(), trade['instrument'], trade['expiry'], trade['strike'], trade['opt_type'], trade['lots'], trade['direction'], trade['entry_price'], trade['SL'], trade['Target'], trade['exit_price'], result, reason])
        self.gui.log(f"Trade closed: Entry {entry} Exit {exit_price} Result {result} P/L pts {pl_points} Rs {pl_rs}")
        self.active_trade = None

    def _write_summary(self):
        date = now_ist().date()
        total = self.summary['taken']
        skipped = self.summary['skipped']
        plp = round(self.summary['pl_points'],2)
        plr = round(self.summary['pl_rs'],2)
        winrate = round((self.summary['wins']/total*100) if total>0 else 0.0,2)
        append_csv(CSV_SUMMARY_LOG, [date, total, self.summary['taken'], skipped, plp, plr, winrate, 'EOD Summary'])
        self.gui.log(f"EOD Summary: Trades {total} Skipped {skipped} P/L pts {plp} Rs {plr} Win% {winrate}")

# -----------------------
# GUI
# -----------------------
class AppGUI:
    def __init__(self, root):
        self.root = root
        root.title("Option Crossover Strategy - Dhan (v1)")
        self.cfg = load_config()
        self.connector_sim = DhanConnectorSim(tf=self.cfg.get('tf_choice', DEFAULTS['tf_choice']))
        self.connector_live = DhanConnectorLive()
        # default to dummy mode
        self.connector = self.connector_sim

        self.engine = OptionCrossoverEngine(self, self.connector)

        # GUI vars
        self.instrument_var = tk.StringVar(value=self.cfg.get('instrument', DEFAULTS['instrument']))
        self.expiry_var = tk.StringVar(value=self.cfg.get('expiry', DEFAULTS['expiry']))
        self.eval_min_var = tk.IntVar(value=self.cfg.get('eval_minute', DEFAULTS['eval_minute']))
        self.check_min_var = tk.IntVar(value=self.cfg.get('check_minute', DEFAULTS['check_minute']))
        self.tf_var = tk.StringVar(value=self.cfg.get('tf_choice', DEFAULTS['tf_choice']))
        self.strike_mode_var = tk.StringVar(value=self.cfg.get('strike_mode', DEFAULTS['strike_mode']))
        self.strike_offset_var = tk.IntVar(value=self.cfg.get('strike_offset', DEFAULTS['strike_offset']))
        self.lots_var = tk.IntVar(value=self.cfg.get('lots', DEFAULTS['lots']))
        self.max_trades_var = tk.IntVar(value=self.cfg.get('max_trades', DEFAULTS['max_trades']))
        self.mode_var = tk.StringVar(value='DUMMY')  # 'DUMMY' or 'LIVE'
        self.client_id_var = tk.StringVar(value=self.cfg.get('client_id',''))
        self.access_var = tk.StringVar(value=self.cfg.get('access_token',''))

        # build layout
        frm = ttk.Frame(root, padding=8)
        frm.grid(row=0, column=0, sticky="nw")

        ttk.Label(frm, text="Instrument:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(frm, textvariable=self.instrument_var, values=["NIFTY","BANKNIFTY","SENSEX"], width=12).grid(row=0, column=1, sticky="w")

        ttk.Label(frm, text="Expiry:").grid(row=1, column=0, sticky="w")
        ttk.Combobox(frm, textvariable=self.expiry_var, values=["WEEKLY","MONTHLY"], width=12).grid(row=1, column=1, sticky="w")

        ttk.Label(frm, text="Eval Minute (IST 9:14 -> 14):").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.eval_min_var, width=6).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="Check Minute (IST 9:15 -> 15):").grid(row=3, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.check_min_var, width=6).grid(row=3, column=1, sticky="w")

        ttk.Label(frm, text="Timeframe:").grid(row=4, column=0, sticky="w")
        ttk.Combobox(frm, textvariable=self.tf_var, values=["5-min","15-min"], width=10).grid(row=4, column=1, sticky="w")

        ttk.Label(frm, text="Strike Mode:").grid(row=5, column=0, sticky="w")
        ttk.Combobox(frm, textvariable=self.strike_mode_var, values=["ATM","OTM","ITM"], width=10).grid(row=5, column=1, sticky="w")
        ttk.Label(frm, text="Offset (strikes):").grid(row=5, column=2, sticky="w")
        ttk.Entry(frm, textvariable=self.strike_offset_var, width=6).grid(row=5, column=3, sticky="w")

        ttk.Label(frm, text="Lots:").grid(row=6, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.lots_var, width=6).grid(row=6, column=1, sticky="w")

        ttk.Label(frm, text="Max trades/day:").grid(row=7, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.max_trades_var, width=6).grid(row=7, column=1, sticky="w")

        ttk.Label(frm, text="Mode:").grid(row=8, column=0, sticky="w")
        ttk.Combobox(frm, textvariable=self.mode_var, values=["DUMMY","LIVE"], width=10).grid(row=8, column=1, sticky="w")

        ttk.Label(frm, text="Dhan Client ID (Live):").grid(row=9, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.client_id_var, width=30).grid(row=9, column=1, columnspan=2, sticky="w")
        ttk.Label(frm, text="Dhan Access Token (Live):").grid(row=10, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.access_var, width=30).grid(row=10, column=1, columnspan=2, sticky="w")

        btn_start = ttk.Button(frm, text="Start Strategy", command=self.start_strategy)
        btn_start.grid(row=11, column=0, pady=(8,0))
        btn_stop = ttk.Button(frm, text="Stop Strategy", command=self.stop_strategy)
        btn_stop.grid(row=11, column=1, pady=(8,0))
        btn_test = ttk.Button(frm, text="Run Test Simulation", command=self.run_test_simulation)
        btn_test.grid(row=11, column=2, pady=(8,0))

        # log area
        self.log_widget = tk.Text(root, height=20, width=100)
        self.log_widget.grid(row=1, column=0, padx=10, pady=8)
        self.log("App ready. Use DUMMY for quick tests. Configure and Start.")

    def log(self, text):
        ts = now_ist().strftime("%Y-%m-%d %H:%M:%S")
        self.log_widget.insert("end", f"[{ts}] {text}\n")
        self.log_widget.see("end")

    def alert(self, text):
        self.log("ALERT: " + text)
        # non-blocking popup
        threading.Thread(target=lambda: messagebox.showinfo("Trade Alert", text), daemon=True).start()

    def start_strategy(self):
        params = {
            'instrument': self.instrument_var.get(),
            'expiry': self.expiry_var.get(),
            'eval_minute': int(self.eval_min_var.get()),
            'check_minute': int(self.check_min_var.get()),
            'tf_choice': self.tf_var.get(),
            'strike_mode': self.strike_mode_var.get(),
            'strike_offset': int(self.strike_offset_var.get()),
            'lots': int(self.lots_var.get()),
            'max_trades': int(self.max_trades_var.get()),
            'mode': self.mode_var.get(),
            'client_id': self.client_id_var.get(),
            'access_token': self.access_var.get()
        }
        # save prefs
        self.cfg.update({k: params[k] for k in ['tf_choice','instrument','expiry','strike_mode','strike_offset','lots','max_trades']})
        save_config(self.cfg)

        # choose connector
        if params['mode'] == 'LIVE':
            # NOTE: Dhan live integration must be implemented in DhanConnectorLive
            self.connector = self.connector_live
            # store credentials locally (Option C encryption)
            creds = {'client_id':params['client_id'],'access_token':params['access_token']}
            try:
                enc = encrypt_bytes(json.dumps(creds).encode('utf-8'))
                with open("credentials.enc","wb") as f:
                    f.write(enc)
                self.log("Saved encrypted credentials locally (Option C).")
            except Exception as e:
                self.log(f"Failed to store credentials: {e}")
        else:
            self.connector = self.connector_sim

        # re-init engine with chosen connector
        self.engine = OptionCrossoverEngine(self, self.connector)
        self.engine.set_params(params)
        t = threading.Thread(target=self.engine.start, daemon=True)
        t.start()
        self.log("Strategy started.")

    def stop_strategy(self):
        self.engine.stop()
        self.log("Strategy stopped by user.")

    def run_test_simulation(self):
        """Run a short test simulation (speeded up) and produce logs."""
        ensure_csv_headers()
        # choose connector sim and run for 30s
        self.log("Starting test simulation (30s)...")
        self.connector_sim = DhanConnectorSim(tf=self.tf_var.get())
        self.connector = self.connector_sim
        self.engine = OptionCrossoverEngine(self, self.connector)
        params = {
            'instrument': self.instrument_var.get(),
            'expiry': self.expiry_var.get(),
            'eval_minute': int(self.eval_min_var.get()),
            'check_minute': int(self.check_min_var.get()),
            'tf_choice': self.tf_var.get(),
            'strike_mode': self.strike_mode_var.get(),
            'strike_offset': int(self.strike_offset_var.get()),
            'lots': int(self.lots_var.get()),
            'max_trades': int(self.max_trades_var.get()),
            'mode': 'DUMMY'
        }
        self.engine.set_params(params)
        self.connector.connect()
        self.connector.start_stream()
        # run for 30 seconds
        def short_run():
            time.sleep(30)
            self.connector.disconnect()
            # write summary if any trades
            self.engine._write_summary()
            self.log("Test simulation finished (30s). See CSV logs.")
        threading.Thread(target=short_run, daemon=True).start()

# -----------------------
# Entrypoint
# -----------------------
def main():
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
