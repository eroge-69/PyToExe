# chart_topcoin.py
# -*- coding: utf-8 -*-
import sys
import hmac, hashlib, base64, requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from PyQt6 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

API_KEY    = "290846b5-d0a3-4f44-b3e0-e986f9085697E"
SECRET_KEY = "B88038B4FF927CA87CBCA2365AE8737E"
PASSPHRASE = "APIkey-ar"
OKX_API    = "https://www.okx.com/api/v5/market/history-candles"

def _get_timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def _sign_request(ts, method, path, body="", secret="", passphrase=""):
    msg = ts + method + path + body
    mac = hmac.new(secret.encode(), msg.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()

class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(v).strftime("%m-%d\n%H:%M") for v in values]

class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        pic = pg.QtGui.QPicture()
        p = pg.QtGui.QPainter(pic)
        w = (self.data[1][0] - self.data[0][0]) * 0.3 if len(self.data)>1 else 0.3
        for t,o,h,l,c in self.data:
            color = pg.mkColor('g') if c>=o else pg.mkColor('r')
            p.setPen(pg.mkPen(color))
            p.drawLine(QtCore.QPointF(t,l), QtCore.QPointF(t,h))
            y = min(o,c); height = abs(c-o) or 1e-8
            rect = QtCore.QRectF(t-w, y, w*2, height)
            p.fillRect(rect, color); p.drawRect(rect)
        p.end(); self.picture = pic

    def paint(self, painter, option, widget):
        if self.picture:
            painter.drawPicture(0,0,self.picture)

    def boundingRect(self):
        xs = [t for t, *_ in self.data]
        ys = [v for row in self.data for v in row[1:]]
        return QtCore.QRectF(min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys))

class ChartWidget(QtWidgets.QWidget):
    def __init__(self, api_key, secret_key, passphrase):
        super().__init__()
        self.api_key, self.secret_key, self.passphrase = api_key, secret_key, passphrase
        self.symbol, self.interval, self.limit = "BTC-USDT","1m",200
        self.zone_items = []
        self._build_ui()
        self.update_chart()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_chart)
        timer.start(5000)

    def _build_ui(self):
        ctrl = QtWidgets.QHBoxLayout()
        self.sym_cb = QtWidgets.QComboBox()
        self.sym_cb.addItems(["BTC-USDT","ETH-USDT","SOL-USDT"])
        self.sym_cb.currentTextChanged.connect(self.on_change)
        ctrl.addWidget(QtWidgets.QLabel("Symbol:")); ctrl.addWidget(self.sym_cb)

        self.interval_cb = QtWidgets.QComboBox()
        self.interval_cb.addItems(["1m","5m","15m","1h","4h","1d"])
        self.interval_cb.currentTextChanged.connect(self.on_change)
        ctrl.addWidget(QtWidgets.QLabel("Interval:")); ctrl.addWidget(self.interval_cb)

        self.limit_cb = QtWidgets.QComboBox()
        self.limit_cb.addItems(["50","100","200","500"])
        self.limit_cb.setCurrentText(str(self.limit))
        self.limit_cb.currentTextChanged.connect(self.on_change)
        ctrl.addWidget(QtWidgets.QLabel("Candles:")); ctrl.addWidget(self.limit_cb)
        ctrl.addStretch()

        glw = pg.GraphicsLayoutWidget()
        self.plot_candle = glw.addPlot(row=0,col=0,axisItems={'bottom':TimeAxisItem('bottom')})
        self.plot_vol    = glw.addPlot(row=1,col=0,axisItems={'bottom':TimeAxisItem('bottom')})
        self.plot_vol.setMaximumHeight(150); self.plot_vol.setXLink(self.plot_candle)
        self.plot_rsi    = glw.addPlot(row=2,col=0,axisItems={'bottom':TimeAxisItem('bottom')})
        self.plot_rsi.setMaximumHeight(120); self.plot_rsi.setXLink(self.plot_candle)
        for p in (self.plot_candle,self.plot_vol,self.plot_rsi):
            p.showGrid(x=True,y=True); p.setMenuEnabled(False)

        vlay = QtWidgets.QVBoxLayout(self)
        vlay.addLayout(ctrl); vlay.addWidget(glw)
        self.candle_item = None; self.vol_item = None

    def on_change(self,_):
        # clear existing items before redraw
        self.symbol   = self.sym_cb.currentText()
        self.interval = self.interval_cb.currentText()
        self.limit    = int(self.limit_cb.currentText())
        self.plot_candle.clear(); self.plot_vol.clear(); self.plot_rsi.clear()
        for z in self.zone_items:
            self.plot_candle.removeItem(z)
        self.zone_items.clear()
        self.candle_item = None
        self.vol_item = None
        self.update_chart()

    def fetch_ohlc(self):
        bar = self.interval
        if bar.endswith('h'): bar = bar[:-1].upper()+'H'
        if bar.endswith('d'): bar = bar[:-1].upper()+'D'
        ts = _get_timestamp(); path="/api/v5/market/history-candles"
        query=f"?instId={self.symbol}&bar={bar}&limit={self.limit}"
        sig=_sign_request(ts,"GET",path+query,secret=self.secret_key,passphrase=self.passphrase)
        hdr={"OK-ACCESS-KEY":self.api_key,"OK-ACCESS-SIGN":sig,
             "OK-ACCESS-TIMESTAMP":ts,"OK-ACCESS-PASSPHRASE":self.passphrase,
             "Content-Type":"application/json"}
        r=requests.get(OKX_API,params={"instId":self.symbol,"bar":bar,"limit":self.limit},headers=hdr).json()
        if r.get("code")!="0": return None
        df=pd.DataFrame(r["data"],columns=["ts","o","h","l","c","v","_","_","_"])
        df["ts"]=pd.to_datetime(df["ts"].astype(int),unit="ms"); df.set_index("ts",inplace=True)
        return df.astype({"o":float,"h":float,"l":float,"c":float,"v":float})

    def update_chart(self):
        df = self.fetch_ohlc()
        if df is None: return

        # indicators
        df["ma20"] = df["c"].rolling(20).mean()
        df["ma50"] = df["c"].rolling(50).mean()
        df["ema200"] = df["c"].ewm(span=200).mean()
        d = df["c"].diff()
        g = d.where(d>0,0).rolling(14).mean()
        l = -d.where(d<0,0).rolling(14).mean()
        df["rsi"] = 100 - (100/(1 + (g/l)))

        times = df.index.astype("int64")//10**9
        ohlc  = list(zip(times, df["o"].values, df["h"].values, df["l"].values, df["c"].values))

        # clear past zones/trendlines
        for z in self.zone_items: self.plot_candle.removeItem(z)
        self.zone_items.clear()

        # draw candles
        if self.candle_item: self.plot_candle.removeItem(self.candle_item)
        self.candle_item = CandlestickItem(ohlc)
        self.plot_candle.addItem(self.candle_item)

        # draw MA/EMA
        for col,clr in [("ma20","y"),("ma50","c"),("ema200","w")]:
            self.plot_candle.plot(times, df[col].values, pen=pg.mkPen(clr, width=1))

        # draw volume
        if self.vol_item: self.plot_vol.removeItem(self.vol_item)
        w = (times[1]-times[0])*0.8 if len(times)>1 else 0.5
        self.vol_item = pg.BarGraphItem(x=times, height=df["v"].values, width=w, brush='b')
        self.plot_vol.addItem(self.vol_item)

        # draw RSI
        self.plot_rsi.clear()
        self.plot_rsi.plot(times, df["rsi"].values, pen=pg.mkPen("m", width=1))
        self.plot_rsi.addLine(y=70, pen=pg.mkPen("r", style=QtCore.Qt.PenStyle.DashLine))
        self.plot_rsi.addLine(y=30, pen=pg.mkPen("g", style=QtCore.Qt.PenStyle.DashLine))
        self.plot_rsi.setYRange(0,100)

        # pivots for trendlines & zones
        wdw = 5
        highs, lows = df["h"].values, df["l"].values
        piv_h = [i for i in range(wdw, len(df)-wdw) if highs[i] == highs[i-wdw:i+wdw+1].max()]
        piv_l = [i for i in range(wdw, len(df)-wdw) if lows[i] == lows[i-wdw:i+wdw+1].min()]

        # draw all trendlines
        for seq, clr in [(piv_h,'r'), (piv_l,'g')]:
            for j in range(1, len(seq)):
                x0, x1 = times[seq[j-1]], times[seq[j]]
                y0 = (highs if clr=='r' else lows)[seq[j-1]]
                y1 = (highs if clr=='r' else lows)[seq[j]]
                self.plot_candle.plot([x0,x1],[y0,y1],
                    pen=pg.mkPen(clr, width=1, style=QtCore.Qt.PenStyle.DashLine))

        # support/resistance zones: last 3 unique highs & lows
        min_t, max_t = times[0], times[-1]
        for lvl in np.unique(highs[piv_h])[-3:]:
            half = lvl*0.002
            rect = QtWidgets.QGraphicsRectItem(min_t, lvl-half, max_t-min_t, half*2)
            rect.setBrush(QtGui.QColor(255,0,0,40)); rect.setPen(pg.mkPen(None))
            self.plot_candle.addItem(rect); self.zone_items.append(rect)
        for lvl in np.unique(lows[piv_l])[:3]:
            half = lvl*0.002
            rect = QtWidgets.QGraphicsRectItem(min_t, lvl-half, max_t-min_t, half*2)
            rect.setBrush(QtGui.QColor(0,255,0,40)); rect.setPen(pg.mkPen(None))
            self.plot_candle.addItem(rect); self.zone_items.append(rect)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = ChartWidget(API_KEY, SECRET_KEY, PASSPHRASE)
    win.resize(1000, 800)
    win.setWindowTitle("Topcoin: MA/EMA, RSI, Trendlines & S/R Zones")
    win.show()
    sys.exit(app.exec())
