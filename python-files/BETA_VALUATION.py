
import sys
import traceback
from typing import Optional, List, Dict
from functools import lru_cache
from datetime import datetime, timedelta
import statistics

import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

import requests

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QLabel, QPushButton,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QProgressBar, QCheckBox
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
import configparser
from pathlib import Path

# -----------------------------
# Helpers
# -----------------------------

def fmt_money(val: Optional[float], currency: str = "$", allow_sign: bool = True) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    try:
        v = float(val)
    except Exception:
        return str(val)
    sign = "-" if allow_sign and v < 0 else ""
    v = abs(v)
    if v >= 1e12:
        return f"{sign}{currency}{v/1e12:,.2f}T"
    if v >= 1e9:
        return f"{sign}{currency}{v/1e9:,.2f}B"
    if v >= 1e6:
        return f"{sign}{currency}{v/1e6:,.2f}M"
    if v >= 1e3:
        return f"{sign}{currency}{v/1e3:,.0f}K"
    return f"{sign}{currency}{v:,.2f}"


def fmt_number(val: Optional[float], digits: int = 2) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    try:
        return f"{float(val):,.{digits}f}"
    except Exception:
        return str(val)


def fmt_percent(val: Optional[float], digits: int = 2) -> str:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    try:
        return f"{float(val):.{digits}f}%"
    except Exception:
        return str(val)


def validate_financial_data(df: pd.DataFrame, min_rows: int = 3, min_cols: int = 2) -> bool:
    """Validate financial data quality"""
    if df is None or df.empty or df.shape[0] < min_rows or df.shape[1] < min_cols:
        return False
    # Check if there are enough numeric values
    numeric_count = df.select_dtypes(include=[np.number]).count().sum()
    if numeric_count < min_rows * min_cols * 0.5:  # At least 50% numeric values
        return False
    return True


@lru_cache(maxsize=32)
def get_cached_ticker_info(symbol: str) -> Dict:
    """Cache API responses to avoid repeated calls"""
    try:
        tk = yf.Ticker(symbol)
        info = getattr(tk, 'info', {}) or {}
        return info
    except Exception:
        return {}


# Add these after your existing helper functions (after validate_financial_data)
def get_risk_free_rate() -> float:
    """Fetch current 10-year US Treasury yield as risk-free rate"""
    try:
        # Method 1: Try Yahoo Finance first
        try:
            treasury = yf.Ticker("^TNX")
            hist = treasury.history(period="1d")
            if not hist.empty and 'Close' in hist:
                return float(hist['Close'].iloc[-1])
        except:
            pass
        
        # Method 2: Try Treasury API as fallback
        try:
            url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates"
            params = {
                "filter": "security_desc:eq:Marketable",
                "sort": "-record_date",
                "page[size]": "1"
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['data']:
                    return float(data['data'][0]['avg_interest_rate'])
        except:
            pass
        
        # Method 3: Try FRED API as another fallback
        try:
            url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                lines = response.text.split('\n')
                if len(lines) > 1:
                    last_line = lines[1].split(',')
                    if len(last_line) > 1 and last_line[1].strip() != '.':
                        return float(last_line[1])
        except:
            pass
        
        # Final fallback: Use recent average
        return 4.0  # Conservative fallback
        
    except Exception:
        return 4.0  # Default fallback

def estimate_cost_of_debt(tk: yf.Ticker) -> float:
    """Estimate company's cost of debt using various methods"""
    try:
        info = getattr(tk, 'info', {}) or {}
        
        # Method 1: Try to get yield to maturity from bonds if available
        try:
            # For some companies, Yahoo Finance provides bond data
            bonds = getattr(tk, 'bonds', None)
            if bonds and not bonds.empty:
                # Take average of recent bond yields
                valid_yields = [y for y in bonds.get('yield', []) if not pd.isna(y) and y > 0]
                if valid_yields:
                    return np.mean(valid_yields) * 100  # Convert to percentage
        except:
            pass
        
        # Method 2: Use credit rating to estimate cost of debt
        credit_rating = info.get('creditRating', '').upper()
        if credit_rating:
            rating_spreads = {
                'AAA': 0.5, 'AA+': 0.7, 'AA': 0.9, 'AA-': 1.1,
                'A+': 1.3, 'A': 1.5, 'A-': 1.8,
                'BBB+': 2.0, 'BBB': 2.3, 'BBB-': 2.7,
                'BB+': 3.2, 'BB': 3.7, 'BB-': 4.3,
                'B+': 5.0, 'B': 5.8, 'B-': 6.7,
                'CCC+': 8.0, 'CCC': 9.5, 'CCC-': 11.0,
                'CC': 13.0, 'C': 15.0, 'D': 20.0
            }
            
            if credit_rating in rating_spreads:
                risk_free = get_risk_free_rate()
                return risk_free + rating_spreads[credit_rating]
        
        # Method 3: Use interest coverage ratio
        interest_expense = info.get('interestExpense', np.nan)
        operating_income = info.get('operatingIncome', np.nan)
        ebitda = info.get('ebitda', np.nan)
        
        if not pd.isna(interest_expense) and interest_expense > 0:
            if not pd.isna(operating_income):
                interest_coverage = operating_income / interest_expense
            elif not pd.isna(ebitda):
                interest_coverage = ebitda / interest_expense
            else:
                interest_coverage = np.nan
            
            if not pd.isna(interest_coverage):
                if interest_coverage > 8:
                    return get_risk_free_rate() + 1.5  # Very safe
                elif interest_coverage > 4:
                    return get_risk_free_rate() + 2.5  # Safe
                elif interest_coverage > 2:
                    return get_risk_free_rate() + 4.0  # Moderate risk
                elif interest_coverage > 1:
                    return get_risk_free_rate() + 6.0  # Risky
                else:
                    return get_risk_free_rate() + 10.0  # Very risky
        
        # Method 4: Industry averages as final fallback
        industry = info.get('industry', '').lower()
        risk_free = get_risk_free_rate()
        
        if any(x in industry for x in ['technology', 'software', 'internet']):
            return risk_free + 3.0  # Tech companies usually have low debt costs
        elif any(x in industry for x in ['utility', 'energy']):
            return risk_free + 2.0  # Stable utilities
        elif any(x in industry for x in ['financial', 'bank', 'insurance']):
            return risk_free + 2.5  # Financial institutions
        elif any(x in industry for x in ['consumer', 'retail']):
            return risk_free + 3.5  # Consumer goods
        else:
            return risk_free + 4.0  # Default spread
            
    except Exception:
        return get_risk_free_rate() + 4.0  # Conservative default

######################################################################################################
# -----------------------------
# Data Fetching Fallbacks (Yahoo -> Alpha Vantage -> FMP)
# -----------------------------

def load_api_config(path: str = "stockvaluationapi.ini") -> dict:
    cfg = configparser.ConfigParser()
    cfg.read(path)
    keys = cfg["keys"] if "keys" in cfg else {}
    return {
        "alpha_vantage_key": keys.get("alpha_vantage_key", "").strip(),
        "fmp_key": keys.get("fmp_key", "").strip()
    }

CONFIG = load_api_config()

def _safe_df(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    if isinstance(df, pd.DataFrame) and not df.empty:
        return df.copy()
    return None

def _validate_json(d):
    return isinstance(d, dict) and len(d) > 0

class UnifiedTicker:
    """
    Wrapper that mimics the subset of yfinance.Ticker interface your code uses:
    - .info (dict)
    - .financials, .balance_sheet, .cashflow (DataFrames)
    - .dividends (Series)
    - .history(period='5d') (DataFrame)
    - .fast_info (dict)
    Fallbacks: Yahoo -> Alpha Vantage -> Financial Modeling Prep (FMP)
    """
    def __init__(self, symbol: str, config: dict):
        self.symbol = symbol
        self._av_key = config.get("alpha_vantage_key", "")
        self._fmp_key = config.get("fmp_key", "")
        self._yf_tk = yf.Ticker(symbol)

        # Lazy caches
        self._info = None
        self._financials = None
        self._balance_sheet = None
        self._cashflow = None
        self._dividends = None
        self._fast_info = None

    # ------------- Public properties -------------
    @property
    def info(self) -> dict:
        if self._info is None:
            self._info = self._fetch_info()
        return self._info

    @property
    def fast_info(self) -> dict:
        if self._fast_info is None:
            self._fast_info = self._fetch_fast_info()
        return self._fast_info

    @property
    def financials(self) -> Optional[pd.DataFrame]:
        if self._financials is None:
            self._financials = self._fetch_financials()
        return self._financials

    @property
    def balance_sheet(self) -> Optional[pd.DataFrame]:
        if self._balance_sheet is None:
            self._balance_sheet = self._fetch_balance()
        return self._balance_sheet

    @property
    def cashflow(self) -> Optional[pd.DataFrame]:
        if self._cashflow is None:
            self._cashflow = self._fetch_cashflow()
        return self._cashflow

    @property
    def dividends(self) -> pd.Series:
        if self._dividends is None:
            self._dividends = self._fetch_dividends()
        return self._dividends

    # Keep backward-compat just in case your code references 'balance_sheet' via getattr(tk, 'balance_sheet', None)
    # It's already the property above.

    # ------------- Public methods -------------
    def history(self, period: str = "5d", interval: str = "1d") -> pd.DataFrame:
        # Try Yahoo first
        try:
            h = self._yf_tk.history(period=period, interval=interval)
            if isinstance(h, pd.DataFrame) and not h.empty:
                return h
        except Exception:
            pass
        # Fallback: Alpha Vantage (daily adjusted)
        h = self._av_history()
        if isinstance(h, pd.DataFrame) and not h.empty:
            return h
        # Fallback: FMP
        h = self._fmp_history()
        if isinstance(h, pd.DataFrame) and not h.empty:
            return h
        return pd.DataFrame()

    # ------------- Yahoo then AV then FMP fetchers -------------
    def _fetch_info(self) -> dict:
        # Yahoo
        try:
            inf = getattr(self._yf_tk, 'info', {}) or {}
            if _validate_json(inf):
                return inf
        except Exception:
            pass
        # Alpha Vantage: OVERVIEW
        if self._av_key:
            try:
                url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={self.symbol}&apikey={self._av_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    data = r.json()
                    if _validate_json(data) and "Symbol" in data:
                        # Normalize some key fields to roughly match Yahoo keys you use
                        out = {}
                        # MarketCap
                        if "MarketCapitalization" in data:
                            try:
                                out["marketCap"] = float(data["MarketCapitalization"])
                            except Exception:
                                pass
                        # Beta (sometimes provided)
                        if "Beta" in data:
                            try:
                                out["beta"] = float(data["Beta"])
                            except Exception:
                                pass
                        # SharesOutstanding
                        if "SharesOutstanding" in data:
                            try:
                                out["sharesOutstanding"] = float(data["SharesOutstanding"])
                            except Exception:
                                pass
                        # DividendRate & Yield
                        if "DividendPerShare" in data:
                            try:
                                out["dividendRate"] = float(data["DividendPerShare"])
                            except Exception:
                                pass
                        if "DividendYield" in data:
                            try:
                                out["dividendYield"] = float(data["DividendYield"])
                            except Exception:
                                pass
                        # PE, PB, PS approximations if present
                        if "PERatio" in data:
                            try: out["trailingPE"] = float(data["PERatio"])
                            except: pass
                        if "PriceToBookRatio" in data:
                            try: out["priceToBook"] = float(data["PriceToBookRatio"])
                            except: pass
                        # Currency (not always present)
                        if "Currency" in data:
                            out["currency"] = data["Currency"]
                        # Industry
                        if "Industry" in data:
                            out["industry"] = data["Industry"]
                        return out
            except Exception:
                pass
        # FMP: /profile
        if self._fmp_key:
            try:
                url = f"https://financialmodelingprep.com/api/v3/profile/{self.symbol}?apikey={self._fmp_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    js = r.json()
                    if isinstance(js, list) and js:
                        data = js[0]
                        out = {}
                        for k_map in [
                            ("mktCap", "marketCap"),
                            ("beta", "beta"),
                            ("volAvg", "averageVolume"),
                            ("price", "currentPrice"),
                            ("lastDiv", "dividendRate"),
                            ("currency", "currency"),
                            ("industry", "industry")
                        ]:
                            src, dst = k_map
                            if src in data:
                                out[dst] = data[src]
                        # sharesOutstanding sometimes in /key-metrics (skip for brevity)
                        return out
            except Exception:
                pass
        return {}

    def _fetch_fast_info(self) -> dict:
        # Yahoo
        try:
            fi = getattr(self._yf_tk, 'fast_info', None) or {}
            if _validate_json(fi):
                return fi
        except Exception:
            pass
        # Fallback: try to synthesize from other calls (current price via history)
        hist = self.history(period="5d")
        out = {}
        try:
            if isinstance(hist, pd.DataFrame) and not hist.empty:
                out["last_close"] = float(hist["Close"].dropna().iloc[-1])
        except Exception:
            pass
        return out

    def _fetch_financials(self) -> Optional[pd.DataFrame]:
        # Yahoo (annual financials / income statement)
        try:
            df = getattr(self._yf_tk, 'financials', None)
            df = _safe_df(df)
            if df is not None:
                return df
        except Exception:
            pass
        # Alpha Vantage: INCOME_STATEMENT (annual)
        if self._av_key:
            try:
                url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={self.symbol}&apikey={self._av_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    js = r.json()
                    ann = js.get("annualReports", [])
                    if isinstance(ann, list) and ann:
                        df = pd.DataFrame(ann).set_index("fiscalDateEnding").T
                        return df
            except Exception:
                pass
        # FMP: /income-statement?limit=5
        if self._fmp_key:
            try:
                url = f"https://financialmodelingprep.com/api/v3/income-statement/{self.symbol}?period=annual&limit=5&apikey={self._fmp_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    js = r.json()
                    if isinstance(js, list) and js:
                        df = pd.DataFrame(js)
                        df = df.set_index("date").T
                        return df
            except Exception:
                pass
        return None

    def _fetch_balance(self) -> Optional[pd.DataFrame]:
        # Yahoo
        try:
            df = getattr(self._yf_tk, 'balance_sheet', None)
            df = _safe_df(df)
            if df is not None:
                return df
        except Exception:
            pass
        # Alpha Vantage: BALANCE_SHEET
        if self._av_key:
            try:
                url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={self.symbol}&apikey={self._av_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    js = r.json()
                    ann = js.get("annualReports", [])
                    if isinstance(ann, list) and ann:
                        df = pd.DataFrame(ann).set_index("fiscalDateEnding").T
                        return df
            except Exception:
                pass
        # FMP
        if self._fmp_key:
            try:
                url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{self.symbol}?period=annual&limit=5&apikey={self._fmp_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    js = r.json()
                    if isinstance(js, list) and js:
                        df = pd.DataFrame(js).set_index("date").T
                        return df
            except Exception:
                pass
        return None

    def _fetch_cashflow(self) -> Optional[pd.DataFrame]:
        # Yahoo
        try:
            df = getattr(self._yf_tk, 'cashflow', None)
            df = _safe_df(df)
            if df is not None:
                return df
        except Exception:
            pass
        # Alpha Vantage: CASH_FLOW
        if self._av_key:
            try:
                url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={self.symbol}&apikey={self._av_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    js = r.json()
                    ann = js.get("annualReports", [])
                    if isinstance(ann, list) and ann:
                        df = pd.DataFrame(ann).set_index("fiscalDateEnding").T
                        return df
            except Exception:
                pass
        # FMP
        if self._fmp_key:
            try:
                url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{self.symbol}?period=annual&limit=5&apikey={self._fmp_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    js = r.json()
                    if isinstance(js, list) and js:
                        df = pd.DataFrame(js).set_index("date").T
                        return df
            except Exception:
                pass
        return None

    def _fetch_dividends(self) -> pd.Series:
        # Yahoo
        try:
            dv = self._yf_tk.dividends
            if isinstance(dv, pd.Series) and not dv.empty:
                return dv
        except Exception:
            pass
        # Alpha Vantage: monthly adjusted (has dividends/ splits per month)
        if self._av_key:
            try:
                url = f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={self.symbol}&apikey={self._av_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    js = r.json()
                    key = "Monthly Adjusted Time Series"
                    if key in js:
                        # Build Series of dividends (sum per month)
                        rows = []
                        for date_str, rec in js[key].items():
                            dv = rec.get("7. dividend amount", "0")
                            try:
                                dvf = float(dv)
                                if dvf != 0:
                                    rows.append((pd.to_datetime(date_str), dvf))
                            except Exception:
                                pass
                        if rows:
                            ser = pd.Series({d: v for d, v in rows}).sort_index()
                            return ser
            except Exception:
                pass
        # FMP: historical stock dividends
        if self._fmp_key:
            try:
                url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{self.symbol}?apikey={self._fmp_key}"
                r = requests.get(url, timeout=15)
                if r.ok:
                    js = r.json()
                    hist = js.get("historical", [])
                    if isinstance(hist, list) and hist:
                        ser = pd.Series({
                            pd.to_datetime(it["date"]): float(it.get("adjDividend", it.get("dividend", 0)))
                            for it in hist if "date" in it
                        }).sort_index()
                        return ser
            except Exception:
                pass
        return pd.Series(dtype=float)

    # --------- External fallbacks for price history ---------
    def _av_history(self) -> pd.DataFrame:
        if not self._av_key:
            return pd.DataFrame()
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={self.symbol}&outputsize=compact&apikey={self._av_key}"
            r = requests.get(url, timeout=15)
            if r.ok:
                js = r.json()
                key = "Time Series (Daily)"
                if key in js:
                    df = (pd.DataFrame(js[key]).T
                          .rename(columns={
                              "1. open": "Open",
                              "2. high": "High",
                              "3. low": "Low",
                              "4. close": "Close",
                              "5. adjusted close": "Adj Close",
                              "6. volume": "Volume"
                          }))
                    df.index = pd.to_datetime(df.index)
                    for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    return df.sort_index()
        except Exception:
            pass
        return pd.DataFrame()

    def _fmp_history(self) -> pd.DataFrame:
        if not self._fmp_key:
            return pd.DataFrame()
        try:
            url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{self.symbol}?serietype=line&timeseries=500&apikey={self._fmp_key}"
            r = requests.get(url, timeout=15)
            if r.ok:
                js = r.json()
                hist = js.get("historical", [])
                if isinstance(hist, list) and hist:
                    df = pd.DataFrame(hist)
                    if "date" in df.columns and "close" in df.columns:
                        df["date"] = pd.to_datetime(df["date"])
                        df = df.rename(columns={"close": "Close"}).set_index("date").sort_index()
                        return df
        except Exception:
            pass
        return pd.DataFrame()








#######################################################################################################

class StockValuationDialog(QDialog):
    """
    Professional Stock Valuation Tool with Bloomberg-style analysis:
      - DCF valuation
      - Comparable multiples
      - Dividend Discount Model
      - Residual Income Model
      - Graham Formula
      - Financial statement analysis
      - Relative valuation
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Equity Valuation Pro")
        self.setMinimumSize(1200, 900)
        self.setup_ui()
        self.current_ticker: Optional[str] = None  # as entered (may include suffix)
        self.currency: str = "$"  # Default currency

    # -----------------------------
    # UI Construction
    # -----------------------------
    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Input Section
        input_group = QGroupBox("Valuation Parameters")
        form_layout = QFormLayout()

        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("Enter ticker (e.g. AAPL US Equity)")
        form_layout.addRow("Ticker:", self.ticker_input)

        # Auto-fetch parameters checkbox
        self.auto_fetch_checkbox = QCheckBox("Automatically fetch parameters")
        self.auto_fetch_checkbox.setChecked(True)
        form_layout.addRow(self.auto_fetch_checkbox)

        # Valuation Parameters
        self.valuation_method = QComboBox()
        self.valuation_method.addItems(["DCF", "Comparables", "Dividend Discount", "Residual Income", "Graham Formula", "EBITDA Valuation", "Sum of Parts"])
        form_layout.addRow("Valuation Method:", self.valuation_method)

        # Time & Rates
        param_layout = QHBoxLayout()
        self.forecast_years = QSpinBox()
        self.forecast_years.setRange(1, 10)
        self.forecast_years.setValue(5)
        param_layout.addWidget(QLabel("Forecast Years:"))
        param_layout.addWidget(self.forecast_years)

        self.growth_rate = QDoubleSpinBox()
        self.growth_rate.setRange(-100, 500)
        self.growth_rate.setValue(5.0)
        self.growth_rate.setSingleStep(0.5)
        param_layout.addWidget(QLabel("Growth (%):"))
        param_layout.addWidget(self.growth_rate)

        self.discount_rate = QDoubleSpinBox()
        self.discount_rate.setRange(0, 50)
        self.discount_rate.setValue(10.0)
        self.discount_rate.setSingleStep(0.5)
        param_layout.addWidget(QLabel("Discount (%):"))
        param_layout.addWidget(self.discount_rate)
        form_layout.addRow(param_layout)

        # Terminal Growth Rate
        self.terminal_growth = QDoubleSpinBox()
        self.terminal_growth.setRange(0, 10)
        self.terminal_growth.setValue(2.5)
        self.terminal_growth.setSingleStep(0.1)
        form_layout.addRow("Terminal Growth (%):", self.terminal_growth)

        # Dividend Discount Model Parameters
        ddm_layout = QHBoxLayout()
        self.dividend_growth = QDoubleSpinBox()
        self.dividend_growth.setRange(0, 50)
        self.dividend_growth.setValue(5.0)
        self.dividend_growth.setSingleStep(0.5)
        ddm_layout.addWidget(QLabel("Div Growth (%):"))
        ddm_layout.addWidget(self.dividend_growth)
        
        
        self.dividend_amount = QLabel("N/A")  
        ddm_layout.addWidget(QLabel("Div Amount:"))
        ddm_layout.addWidget(self.dividend_amount)
        form_layout.addRow(ddm_layout)

        # Graham Formula Parameters
        graham_layout = QHBoxLayout()
        self.earnings_growth = QDoubleSpinBox()
        self.earnings_growth.setRange(0, 50)
        self.earnings_growth.setValue(7.5)
        self.earnings_growth.setSingleStep(0.5)
        graham_layout.addWidget(QLabel("Earnings Growth (%):"))
        graham_layout.addWidget(self.earnings_growth)
        
        self.aaa_yield = QDoubleSpinBox()
        self.aaa_yield.setRange(0, 20)
        self.aaa_yield.setValue(4.0)
        self.aaa_yield.setSingleStep(0.1)
        graham_layout.addWidget(QLabel("AAA Yield (%):"))
        graham_layout.addWidget(self.aaa_yield)
        form_layout.addRow(graham_layout)

        # Comparables Input
        self.comparables_input = QLineEdit()
        self.comparables_input.setPlaceholderText("Comma-separated tickers (e.g. MSFT,GOOGL)")
        form_layout.addRow("Comparables:", self.comparables_input)

        input_group.setLayout(form_layout)
        main_layout.addWidget(input_group)

        # Auto-calculated parameters display
        self.auto_params_group = QGroupBox("Automatically Calculated Parameters")
        auto_params_layout = QFormLayout()
        
        self.calculated_growth = QLabel("N/A")
        auto_params_layout.addRow("Calculated Growth (%):", self.calculated_growth)
        
        self.calculated_discount = QLabel("N/A")
        auto_params_layout.addRow("Calculated Discount (%):", self.calculated_discount)
        
        self.calculated_beta = QLabel("N/A")
        auto_params_layout.addRow("Beta:", self.calculated_beta)
        
        self.calculated_industry = QLabel("N/A")
        auto_params_layout.addRow("Industry:", self.calculated_industry)
        
        self.auto_params_group.setLayout(auto_params_layout)
        main_layout.addWidget(self.auto_params_group)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.calc_button = QPushButton("Calculate Valuation")
        self.calc_button.clicked.connect(self.calculate)
        self.export_button = QPushButton("Export to Excel")
        self.export_button.clicked.connect(self.export_results)
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.calc_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.refresh_button)
        main_layout.addLayout(button_layout)

        # Results Tabs
        self.tabs = QTabWidget()

        # 1. Summary Tab
        self.summary_tab = QWidget()
        self.setup_summary_tab()
        self.tabs.addTab(self.summary_tab, "Summary")

        # 2. DCF Tab
        self.dcf_tab = QWidget()
        self.setup_dcf_tab()
        self.tabs.addTab(self.dcf_tab, "DCF Analysis")

        # 3. Comparables Tab
        self.comps_tab = QWidget()
        self.setup_comps_tab()
        self.tabs.addTab(self.comps_tab, "Comparables")

        # 4. Dividend Discount Tab
        self.ddm_tab = QWidget()
        self.setup_ddm_tab()
        self.tabs.addTab(self.ddm_tab, "Dividend Discount")

        # 5. Residual Income Tab
        self.rim_tab = QWidget()
        self.setup_rim_tab()
        self.tabs.addTab(self.rim_tab, "Residual Income")

        # 6. Graham Formula Tab
        self.graham_tab = QWidget()
        self.setup_graham_tab()
        self.tabs.addTab(self.graham_tab, "Graham Formula")


        # 8. EBITDA Valuation Tab
        self.ebitda_tab = QWidget()
        self.setup_ebitda_tab()
        self.tabs.addTab(self.ebitda_tab, "EBITDA Valuation")

        # 7. Financials Tab
        self.financials_tab = QWidget()
        self.setup_financials_tab()
        self.tabs.addTab(self.financials_tab, "Financials")

        # 9. Final Conclusion Tab (new tab)
        self.conclusion_tab = QWidget()
        self.setup_conclusion_tab()
        self.tabs.addTab(self.conclusion_tab, "Final Conclusion")

        main_layout.addWidget(self.tabs)

    def setup_summary_tab(self):
        layout = QVBoxLayout(self.summary_tab)

        # Key Metrics Table
        self.metrics_table = QTableWidget(0, 4)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value", "Industry Avg", "Comment"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.metrics_table)

        # Valuation Summary
        summary_group = QGroupBox("Valuation Summary")
        summary_layout = QFormLayout()

        self.price_target = QLabel("N/A")
        self.price_target.setStyleSheet("font-weight: bold; font-size: 14px;")
        summary_layout.addRow("Price Target:", self.price_target)

        self.current_price = QLabel("N/A")
        summary_layout.addRow("Current Price:", self.current_price)

        self.upside = QLabel("N/A")
        self.upside.setStyleSheet("color: green; font-weight: bold;")
        summary_layout.addRow("Upside Potential:", self.upside)

        self.valuation_range = QLabel("N/A")
        summary_layout.addRow("Valuation Range:", self.valuation_range)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Recommendation
        self.recommendation = QLabel("N/A")
        self.recommendation.setAlignment(Qt.AlignCenter)
        self.recommendation.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.recommendation)

    def setup_dcf_tab(self):
        layout = QVBoxLayout(self.dcf_tab)

        # DCF Model Table
        self.dcf_table = QTableWidget(0, 5)
        self.dcf_table.setHorizontalHeaderLabels(["Year", "FCF", "Growth", "PV Factor", "PV FCF"])
        layout.addWidget(self.dcf_table)

        # DCF Charts
        chart_layout = QHBoxLayout()
        self.dcf_plot_canvas = FigureCanvas(plt.Figure(figsize=(8, 4)))
        chart_layout.addWidget(self.dcf_plot_canvas)
        self.sensitivity_canvas = FigureCanvas(plt.Figure(figsize=(8, 4)))
        chart_layout.addWidget(self.sensitivity_canvas)
        layout.addLayout(chart_layout)

    def setup_comps_tab(self):
        layout = QVBoxLayout(self.comps_tab)

        # Comparables Table
        self.comp_table = QTableWidget(0, 8)
        self.comp_table.setHorizontalHeaderLabels([
            "Ticker", "Price", "P/E", "EV/EBITDA", "P/B", "P/S", "Div Yield", "Implied Value"
        ])
        layout.addWidget(self.comp_table)

        # Multiples Charts
        chart_layout = QHBoxLayout()
        self.multiples_plot = FigureCanvas(plt.Figure(figsize=(8, 4)))
        chart_layout.addWidget(self.multiples_plot)
        self.implied_value_plot = FigureCanvas(plt.Figure(figsize=(8, 4)))
        chart_layout.addWidget(self.implied_value_plot)
        layout.addLayout(chart_layout)

    def setup_ddm_tab(self):
        layout = QVBoxLayout(self.ddm_tab)

        # DDM Model Table
        self.ddm_table = QTableWidget(0, 5)
        self.ddm_table.setHorizontalHeaderLabels(["Year", "Dividend", "Growth", "PV Factor", "PV Dividend"])
        layout.addWidget(self.ddm_table)

        # DDM Charts
        chart_layout = QHBoxLayout()
        self.ddm_plot_canvas = FigureCanvas(plt.Figure(figsize=(8, 4)))
        chart_layout.addWidget(self.ddm_plot_canvas)
        self.ddm_sensitivity_canvas = FigureCanvas(plt.Figure(figsize=(8, 4)))
        chart_layout.addWidget(self.ddm_sensitivity_canvas)
        layout.addLayout(chart_layout)

    def setup_rim_tab(self):
        layout = QVBoxLayout(self.rim_tab)

        # RIM Model Table
        self.rim_table = QTableWidget(0, 6)
        self.rim_table.setHorizontalHeaderLabels(["Year", "Book Value", "EPS", "Cost of Equity", "Residual Income", "PV RI"])
        layout.addWidget(self.rim_table)

        # RIM Charts
        chart_layout = QHBoxLayout()
        self.rim_plot_canvas = FigureCanvas(plt.Figure(figsize=(8, 4)))
        chart_layout.addWidget(self.rim_plot_canvas)
        layout.addLayout(chart_layout)

    def setup_graham_tab(self):
        layout = QVBoxLayout(self.graham_tab)

        # Graham Formula Inputs
        inputs_group = QGroupBox("Graham Formula Inputs")
        inputs_layout = QFormLayout()
        
        self.graham_eps = QLabel("N/A")
        inputs_layout.addRow("EPS (TTM):", self.graham_eps)
        
        self.graham_bvps = QLabel("N/A")
        inputs_layout.addRow("Book Value per Share:", self.graham_bvps)
        
        inputs_group.setLayout(inputs_layout)
        layout.addWidget(inputs_group)

        # Graham Formula Results
        results_group = QGroupBox("Graham Formula Results")
        results_layout = QFormLayout()
        
        self.graham_intrinsic = QLabel("N/A")
        results_layout.addRow("Intrinsic Value:", self.graham_intrinsic)
        
        self.graham_margin = QLabel("N/A")
        results_layout.addRow("Margin of Safety:", self.graham_margin)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Graham Formula Explanation
        explanation = QLabel(
            "Graham Formula: Intrinsic Value = √(22.5 × EPS × BVPS)\n"
            "Modified Formula: Intrinsic Value = EPS × (8.5 + 2g) × (4.4 / AAA Yield)\n"
            "Where g is the expected earnings growth rate"
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

    def setup_financials_tab(self):
        tab_widget = QTabWidget()

        # Income Statement
        self.income_table = QTableWidget()
        income_tab = QWidget()
        QVBoxLayout(income_tab).addWidget(self.income_table)
        tab_widget.addTab(income_tab, "Income Statement")

        # Balance Sheet
        self.balance_table = QTableWidget()
        balance_tab = QWidget()
        QVBoxLayout(balance_tab).addWidget(self.balance_table)
        tab_widget.addTab(balance_tab, "Balance Sheet")

        # Cash Flow
        self.cashflow_table = QTableWidget()
        cashflow_tab = QWidget()
        QVBoxLayout(cashflow_tab).addWidget(self.cashflow_table)
        tab_widget.addTab(cashflow_tab, "Cash Flow")

        # Ratios
        self.ratios_table = QTableWidget()
        ratios_tab = QWidget()
        QVBoxLayout(ratios_tab).addWidget(self.ratios_table)
        tab_widget.addTab(ratios_tab, "Key Ratios")

        QVBoxLayout(self.financials_tab).addWidget(tab_widget)
    def setup_ebitda_tab(self):
        layout = QVBoxLayout(self.ebitda_tab)

        # EBITDA Multiples Table
        self.ebitda_table = QTableWidget(0, 6)
        self.ebitda_table.setHorizontalHeaderLabels(["Ticker", "EV", "EBITDA", "EV/EBITDA", "Implied EV", "Implied Price"])
        layout.addWidget(self.ebitda_table)

        # EBITDA Charts
        chart_layout = QHBoxLayout()
        self.ebitda_multiples_plot = FigureCanvas(plt.Figure(figsize=(8, 4)))
        chart_layout.addWidget(self.ebitda_multiples_plot)
        self.ebitda_sensitivity_canvas = FigureCanvas(plt.Figure(figsize=(8, 4)))
        chart_layout.addWidget(self.ebitda_sensitivity_canvas)
        layout.addLayout(chart_layout)

        # EBITDA Calculation Explanation
        explanation = QLabel(
            "EBITDA Valuation Method:\n"
            "Enterprise Value = Market Cap + Debt - Cash\n"
            "EV/EBITDA Multiple = Enterprise Value ÷ EBITDA\n"
            "Implied Enterprise Value = EBITDA × Benchmark EV/EBITDA Multiple\n"
            "Implied Equity Value = Implied EV - Debt + Cash\n"
            "Implied Price = Implied Equity Value ÷ Shares Outstanding"
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

    # Add this method to set up the final conclusion tab
    def setup_conclusion_tab(self):
        layout = QVBoxLayout(self.conclusion_tab)
        
        # Valuation Models Summary Table
        summary_group = QGroupBox("Valuation Models Summary")
        summary_layout = QVBoxLayout()
        
        self.models_table = QTableWidget(0, 4)
        self.models_table.setHorizontalHeaderLabels(["Model", "Price Target", "Upside/Downside", "Weight"])
        summary_layout.addWidget(self.models_table)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Weight Controls
        weight_group = QGroupBox("Model Weights")
        weight_layout = QHBoxLayout()
        
        self.dcf_weight = QDoubleSpinBox()
        self.dcf_weight.setRange(0, 100)
        self.dcf_weight.setValue(30.0)
        self.dcf_weight.setSuffix("%")
        weight_layout.addWidget(QLabel("DCF Weight:"))
        weight_layout.addWidget(self.dcf_weight)
        
        self.comps_weight = QDoubleSpinBox()
        self.comps_weight.setRange(0, 100)
        self.comps_weight.setValue(25.0)
        self.comps_weight.setSuffix("%")
        weight_layout.addWidget(QLabel("Comparables Weight:"))
        weight_layout.addWidget(self.comps_weight)
        
        self.ebitda_weight = QDoubleSpinBox()
        self.ebitda_weight.setRange(0, 100)
        self.ebitda_weight.setValue(20.0)
        self.ebitda_weight.setSuffix("%")
        weight_layout.addWidget(QLabel("EBITDA Weight:"))
        weight_layout.addWidget(self.ebitda_weight)
        
        self.ddm_weight = QDoubleSpinBox()
        self.ddm_weight.setRange(0, 100)
        self.ddm_weight.setValue(15.0)
        self.ddm_weight.setSuffix("%")
        weight_layout.addWidget(QLabel("DDM Weight:"))
        weight_layout.addWidget(self.ddm_weight)
        
        self.graham_weight = QDoubleSpinBox()
        self.graham_weight.setRange(0, 100)
        self.graham_weight.setValue(10.0)
        self.graham_weight.setSuffix("%")
        weight_layout.addWidget(QLabel("Graham Weight:"))
        weight_layout.addWidget(self.graham_weight)
        
        weight_group.setLayout(weight_layout)
        layout.addWidget(weight_group)
        
        # Recalculate button
        self.recalculate_button = QPushButton("Recalculate Weighted Average")
        self.recalculate_button.clicked.connect(self.calculate_weighted_average)
        layout.addWidget(self.recalculate_button)
        
        # Final Valuation Summary
        final_group = QGroupBox("Final Valuation Summary")
        final_layout = QFormLayout()
        
        self.weighted_target = QLabel("N/A")
        self.weighted_target.setStyleSheet("font-weight: bold; font-size: 14px;")
        final_layout.addRow("Weighted Price Target:", self.weighted_target)
        
        self.current_price_summary = QLabel("N/A")
        final_layout.addRow("Current Price:", self.current_price_summary)
        
        self.weighted_upside = QLabel("N/A")
        self.weighted_upside.setStyleSheet("color: green; font-weight: bold;")
        final_layout.addRow("Weighted Upside Potential:", self.weighted_upside)
        
        self.valuation_consensus = QLabel("N/A")
        final_layout.addRow("Valuation Consensus:", self.valuation_consensus)
        
        self.confidence_level = QLabel("N/A")
        final_layout.addRow("Confidence Level:", self.confidence_level)
        
        final_group.setLayout(final_layout)
        layout.addWidget(final_group)
        
        # Recommendation
        self.final_recommendation = QLabel("N/A")
        self.final_recommendation.setAlignment(Qt.AlignCenter)
        self.final_recommendation.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.final_recommendation)
        
        # Key Risks and Considerations
        risks_group = QGroupBox("Key Risks and Considerations")
        risks_layout = QVBoxLayout()
        
        self.risks_text = QLabel("N/A")
        self.risks_text.setWordWrap(True)
        risks_layout.addWidget(self.risks_text)
        
        risks_group.setLayout(risks_layout)
        layout.addWidget(risks_group)

    # Add this method to store valuation results from each model
    def store_valuation_result(self, model_name, price_target, upside):
        """Store valuation results from each model for final conclusion tab"""
        if not hasattr(self, 'valuation_results'):
            self.valuation_results = {}
        
        self.valuation_results[model_name] = {
            'price_target': price_target,
            'upside': upside
        }
        
        # Update summary table if we're on the conclusion tab
        if hasattr(self, 'models_table'):
            self.update_conclusion_table()


    # Replace the update_conclusion_table method with this corrected version
    def update_conclusion_table(self):
        """Update the conclusion table with all valuation results"""
        if not hasattr(self, 'valuation_results') or not self.valuation_results:
            return
        
        self.models_table.setRowCount(len(self.valuation_results))
        
        row = 0
        for model_name, results in self.valuation_results.items():
            price_target = results.get('price_target', np.nan)
            upside = results.get('upside', np.nan)
            
            self.models_table.setItem(row, 0, QTableWidgetItem(model_name))
            self.models_table.setItem(row, 1, QTableWidgetItem("N/A" if pd.isna(price_target) else fmt_money(price_target, self.currency)))
            
            upside_text = "N/A"
            if not pd.isna(upside):
                upside_text = f"{upside:+.2f}%"
            
            upside_item = QTableWidgetItem(upside_text)
            upside_item.setData(Qt.EditRole, upside)  # For sorting
            
            # Set color using setForeground instead of setStyleSheet
            if not pd.isna(upside):
                color = QColor(0, 128, 0) if upside >= 0 else QColor(255, 0, 0)  # Green for positive, red for negative
                upside_item.setForeground(color)
            
            self.models_table.setItem(row, 2, upside_item)
            
            # Set default weights based on model type
            weight = 0
            if "DCF" in model_name:
                weight = self.dcf_weight.value()
            elif "Comparables" in model_name:
                weight = self.comps_weight.value()
            elif "EBITDA" in model_name:
                weight = self.ebitda_weight.value()
            elif "Dividend" in model_name:
                weight = self.ddm_weight.value()
            elif "Graham" in model_name:
                weight = self.graham_weight.value()
            
            weight_item = QTableWidgetItem(f"{weight:.1f}%")
            weight_item.setData(Qt.EditRole, weight)
            self.models_table.setItem(row, 3, weight_item)
            
            row += 1
        
        # Auto-adjust column widths
        self.models_table.resizeColumnsToContents()



    # Add this method to calculate weighted average
    def calculate_weighted_average(self):
        """Calculate weighted average of all valuation models"""
        if not hasattr(self, 'valuation_results') or not self.valuation_results:
            QMessageBox.warning(self, "Calculation Error", "No valuation results available")
            return
        
        total_weight = 0
        weighted_sum = 0
        valid_models = 0
        
        # Get current price for upside calculation
        current_price = None
        try:
            current_price_text = self.current_price.text()
            if current_price_text != "N/A":
                current_price = float(current_price_text.replace(self.currency, "").replace(",", ""))
        except:
            pass
        
        if current_price is None or current_price <= 0:
            QMessageBox.warning(self, "Calculation Error", "Current price not available")
            return
        
        # Calculate weighted average
        for model_name, results in self.valuation_results.items():
            price_target = results.get('price_target', np.nan)
            
            if pd.isna(price_target) or price_target <= 0:
                continue
            
            # Get weight for this model
            weight = 0
            if "DCF" in model_name:
                weight = self.dcf_weight.value()
            elif "Comparables" in model_name:
                weight = self.comps_weight.value()
            elif "EBITDA" in model_name:
                weight = self.ebitda_weight.value()
            elif "Dividend" in model_name:
                weight = self.ddm_weight.value()
            elif "Graham" in model_name:
                weight = self.graham_weight.value()
            
            weighted_sum += price_target * (weight / 100)
            total_weight += weight
            valid_models += 1
        
        if valid_models == 0:
            QMessageBox.warning(self, "Calculation Error", "No valid valuation results available")
            return
        
        # Normalize weights if they don't sum to 100%
        if total_weight != 100:
            weighted_sum = weighted_sum * (100 / total_weight)
        
        weighted_target = weighted_sum
        weighted_upside = ((weighted_target - current_price) / current_price) * 100.0
        
        # Update display
        self.weighted_target.setText(fmt_money(weighted_target, self.currency))
        self.current_price_summary.setText(fmt_money(current_price, self.currency))
        
        upside_text = f"{weighted_upside:+.2f}%"
        self.weighted_upside.setText(upside_text)
        
        # Set color using QColor
        color = QColor(0, 128, 0) if weighted_upside >= 0 else QColor(255, 0, 0)  # Green for positive, red for negative
        self.weighted_upside.setStyleSheet(f"font-weight: bold;")
        self.weighted_upside.setStyleSheet(f"color: {'green' if weighted_upside >= 0 else 'red'}; font-weight: bold;")


        # Determine valuation consensus
        price_targets = [r['price_target'] for r in self.valuation_results.values() if not pd.isna(r.get('price_target'))]
        if price_targets:
            min_target = min(price_targets)
            max_target = max(price_targets)
            self.valuation_consensus.setText(f"{fmt_money(min_target, self.currency)} - {fmt_money(max_target, self.currency)}")
        
        # Determine confidence level based on model agreement
        upsides = [r['upside'] for r in self.valuation_results.values() if not pd.isna(r.get('upside'))]
        if upsides:
            upside_std = np.std(upsides) if len(upsides) > 1 else 0
            if upside_std < 5:
                confidence = "High"
                color = "green"
            elif upside_std < 15:
                confidence = "Medium"
                color = "orange"
            else:
                confidence = "Low"
                color = "red"
            
            self.confidence_level.setText(confidence)
            self.confidence_level.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Generate final recommendation
        self.generate_final_recommendation(weighted_upside, valid_models)
        
        # Generate risks assessment
        self.assess_risks()

    # Add this method to generate final recommendation
    def generate_final_recommendation(self, weighted_upside, valid_models_count):
        """Generate final investment recommendation"""
        if weighted_upside > 25:
            rec, color, explanation = ("STRONG BUY", "green", 
                                    "Significant upside potential based on multiple valuation models")
        elif weighted_upside > 10:
            rec, color, explanation = ("BUY", "lightgreen", 
                                    "Attractive upside potential with reasonable risk")
        elif weighted_upside > -5:
            rec, color, explanation = ("HOLD", "gray", 
                                    "Fairly valued with limited near-term catalysts")
        elif weighted_upside > -15:
            rec, color, explanation = ("SELL", "red", 
                                    "Overvalued with downside risk")
        else:
            rec, color, explanation = ("STRONG SELL", "darkred", 
                                    "Significantly overvalued with high downside risk")
        
        # Adjust based on number of valid models
        if valid_models_count < 3:
            explanation += ". Note: Limited model coverage reduces confidence."
        
        self.final_recommendation.setText(f"{rec} - {explanation}")
        self.final_recommendation.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px; padding: 10px;")

    # Add this method to assess risks
    def assess_risks(self):
        """Assess key risks based on valuation results"""
        risks = []
        
        # Check for model disagreements
        upsides = [r['upside'] for r in self.valuation_results.values() if not pd.isna(r.get('upside'))]
        if len(upsides) >= 2:
            upside_range = max(upsides) - min(upsides)
            if upside_range > 30:
                risks.append("High model disagreement suggests uncertainty in fair value estimate")
            elif upside_range > 15:
                risks.append("Moderate model disagreement indicates some valuation uncertainty")
        
        # Check specific model availability
        model_names = list(self.valuation_results.keys())
        
        if "DCF" not in model_names:
            risks.append("DCF model not available - limited view of intrinsic value")
        
        if "Comparables" not in model_names:
            risks.append("Comparables analysis not available - missing relative valuation perspective")
        
        if "EBITDA Valuation" not in model_names:
            risks.append("EBITDA valuation not available - missing cash flow-based multiple analysis")
        
        # Check for extreme valuations in specific models
        for model_name, results in self.valuation_results.items():
            upside = results.get('upside', 0)
            if abs(upside) > 50:
                risks.append(f"Extreme valuation in {model_name} model ({upside:+.1f}%)")
        
        # Add general market risk disclaimer
        risks.append("All valuations are subject to market risk, including possible loss of principal")
        
        if risks:
            self.risks_text.setText("\n• ".join([""] + risks))
        else:
            self.risks_text.setText("No significant risks identified across valuation models")

    # -----------------------------
    # Automatic Parameter Calculation
    # -----------------------------
    def calculate_growth_rate(self, tk: yf.Ticker) -> float:
        """Calculate growth rate based on historical financial data"""
        try:
            # Try to get revenue growth from info
            info = getattr(tk, 'info', {}) or {}
            revenue_growth = info.get('revenueGrowth', np.nan)
            if not pd.isna(revenue_growth):
                return revenue_growth * 100
            
            # Calculate historical revenue growth from financials
            income_stmt = getattr(tk, 'financials', None)
            if isinstance(income_stmt, pd.DataFrame) and not income_stmt.empty:
                # Look for revenue row
                revenue_row = None
                for idx in income_stmt.index:
                    if 'total revenue' in str(idx).lower() or 'revenue' in str(idx).lower():
                        revenue_row = idx
                        break
                
                if revenue_row is not None:
                    revenues = income_stmt.loc[revenue_row]
                    # Convert to numeric and drop NaNs
                    numeric_revenues = pd.to_numeric(revenues, errors='coerce').dropna()
                    
                    if len(numeric_revenues) >= 3:
                        # Calculate CAGR
                        start_val = numeric_revenues.iloc[-1]
                        end_val = numeric_revenues.iloc[0]
                        years = len(numeric_revenues) - 1
                        if start_val > 0 and end_val > 0 and years > 0:
                            cagr = (end_val / start_val) ** (1/years) - 1
                            return cagr * 100
            
            # Fallback: use earnings growth if available
            earnings_growth = info.get('earningsGrowth', np.nan)
            if not pd.isna(earnings_growth):
                return earnings_growth * 100
                
            # Final fallback: industry average or conservative estimate
            industry = info.get('industry', '').lower()
            if any(x in industry for x in ['technology', 'software', 'internet' ,'Consumer Electronics']):
                return 10.0  # Higher growth for tech
            elif any(x in industry for x in ['financial', 'bank', 'insurance']):
                return 5.0   # Moderate growth for financials
            elif any(x in industry for x in ['utility', 'energy', 'consumer']):
                return 3.0   # Lower growth for stable industries
            else:
                return 5.0   # Default growth rate
                
        except Exception:
            return 5.0  # Default fallback


    def calculate_discount_rate(self, tk: yf.Ticker) -> float:
        """Calculate discount rate using CAPM or WACC with real-time data"""
        try:
            info = getattr(tk, 'info', {}) or {}
            
            # Get real risk-free rate
            risk_free_rate = get_risk_free_rate()
            
            # Try to get beta
            beta = info.get('beta', np.nan)
            if pd.isna(beta):
                # Calculate beta from historical data if not available
                beta = self.calculate_beta(tk)
            
            # Use reasonable beta if calculation failed
            if pd.isna(beta) or beta <= 0:
                beta = 1.0  # Market average
            
            # Market risk premium (based on historical average, can be adjusted)
            market_risk_premium = 5.5  # Historical US market premium
            
            # Calculate cost of equity using CAPM
            cost_of_equity = risk_free_rate + (beta * market_risk_premium)
            
            # If we can calculate WACC, use that instead (more comprehensive)
            wacc = self.calculate_wacc(tk, cost_of_equity)
            if not pd.isna(wacc):
                return min(wacc, 20.0)  # Reasonable cap
            
            return min(cost_of_equity, 20.0)  # Reasonable cap
            
        except Exception:
            return 10.0  # Default fallback


    def calculate_beta(self, tk: yf.Ticker) -> float:
        """Calculate beta by comparing stock returns to market returns (SPY)"""

        try:
            symbol = self.current_ticker.split()[0] if self.current_ticker else ""
            if not symbol:
                return 1.0

            stock_data = yf.download(symbol, period="5y", interval="1wk", progress=False)
            spy_data = yf.download("SPY",   period="5y", interval="1wk", progress=False)
            if stock_data is None or spy_data is None or stock_data.empty or spy_data.empty:
                return 1.0

            stock_returns = stock_data['Close'].pct_change().dropna()
            spy_returns   = spy_data['Close'].pct_change().dropna()
            stock_returns, spy_returns = stock_returns.align(spy_returns, join='inner')
            if len(stock_returns) < 30:
                return 1.0

            cov = np.cov(stock_returns, spy_returns, ddof=0)[0, 1]
            var = np.var(spy_returns, ddof=0)
            beta = cov / var if var != 0 else 1.0
            return float(beta)
        except Exception:
            return 1.0



    def calculate_wacc(self, tk: yf.Ticker, cost_of_equity: float) -> float:
        """Calculate Weighted Average Cost of Capital with real data"""
        try:
            info = getattr(tk, 'info', {}) or {}
            
            # Get market cap (equity value)
            market_cap = info.get('marketCap', np.nan)
            if pd.isna(market_cap):
                return np.nan
                
            # Get total debt
            total_debt = info.get('totalDebt', np.nan)
            if pd.isna(total_debt):
                return np.nan
            
            # Get cash and equivalents
            cash = info.get('cash', 0) or 0
            net_debt = max(total_debt - cash, 0)  # Net debt can't be negative
            
            # Estimate cost of debt
            cost_of_debt = estimate_cost_of_debt(tk)
            
            # Get effective tax rate
            tax_rate = info.get('taxRate', np.nan)
            if pd.isna(tax_rate):
                # Try to calculate from financials
                income_before_tax = info.get('incomeBeforeTax', np.nan)
                tax_provision = info.get('incomeTaxExpense', np.nan)
                
                if not pd.isna(income_before_tax) and not pd.isna(tax_provision) and income_before_tax > 0:
                    tax_rate = tax_provision / income_before_tax
                else:
                    tax_rate = 0.21  # US corporate tax rate as default
            
            # Adjust for tax shield
            cost_of_debt_after_tax = cost_of_debt * (1 - tax_rate)
            
            # Calculate weights
            equity_value = market_cap
            debt_value = net_debt  # Use net debt for WACC calculation
            total_value = equity_value + debt_value
            
            if total_value <= 0:
                return np.nan
                
            weight_equity = equity_value / total_value
            weight_debt = debt_value / total_value
            
            # Calculate WACC
            wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt_after_tax)
            
            return min(wacc, 20.0)  # Reasonable cap
            
        except Exception:
            return np.nan

    def update_rate_displays(self, discount_rate: float):
        """Update UI displays with the calculated rates"""
        try:
            # Update the discount rate spinbox
            self.discount_rate.setValue(discount_rate)
            
            # Update the calculated discount label
            self.calculated_discount.setText(f"{discount_rate:.2f}%")
            
            # Also update the AAA yield for Graham formula if it's using risk-free rate
            risk_free_rate = get_risk_free_rate()
            self.aaa_yield.setValue(risk_free_rate)
            
        except Exception:
            pass  # Silent fail - don't break the UI if this fails

    def calculate_terminal_growth(self, tk: yf.Ticker) -> float:
        """Calculate appropriate terminal growth rate"""
        try:
            info = getattr(tk, 'info', {}) or {}
            industry = info.get('industry', '').lower()
            
            # Mature industries have lower terminal growth
            if any(x in industry for x in ['technology', 'software', 'internet', 'biotech', 'Consumer Electronics']):
                return 3.0  # Higher for growth industries
            elif any(x in industry for x in ['financial', 'bank', 'insurance']):
                return 2.5  # Moderate for financials
            elif any(x in industry for x in ['utility', 'energy', 'consumer', 'manufacturing']):
                return 2.0  # Lower for stable industries
            else:
                return 2.5  # Default
                
        except Exception:
            return 2.5  # Default fallback

    def calculate_dividend_amount(self, tk: yf.Ticker) -> float:
        """Calculate annual dividend amount from available data"""
        try:
            info = getattr(tk, 'info', {}) or {}
            
            # Method 1: Try to get dividend rate directly
            dividend_rate = info.get('dividendRate', np.nan)
            if not pd.isna(dividend_rate) and dividend_rate > 0:
                return dividend_rate
            
            # Method 2: Try to get trailing annual dividends
            trailing_annual_dividend = info.get('trailingAnnualDividendRate', np.nan)
            if not pd.isna(trailing_annual_dividend) and trailing_annual_dividend > 0:
                return trailing_annual_dividend
            
            # Method 3: Calculate from dividend history
            dividends = tk.dividends
            if not dividends.empty:
                # Get dividends from the last 12 months
                one_year_ago = datetime.now() - timedelta(days=365)
                recent_dividends = dividends[dividends.index >= one_year_ago]
                if not recent_dividends.empty:
                    return float(recent_dividends.sum())
                
                # If no dividends in last year, use most recent 4 quarters
                recent_dividends = dividends.tail(4)
                if not recent_dividends.empty:
                    return float(recent_dividends.sum())
            
            # Method 4: Try to get from financials (cash flow)
            cashflow = getattr(tk, 'cashflow', None)
            if isinstance(cashflow, pd.DataFrame) and not cashflow.empty:
                for idx in cashflow.index:
                    if any(term in str(idx).lower() for term in ['dividend', 'dividends paid']):
                        dividends_paid = abs(cashflow.loc[idx].iloc[0])  # Dividends paid are usually negative
                        shares = info.get('sharesOutstanding', np.nan)
                        if not pd.isna(shares) and shares > 0:
                            return dividends_paid / shares
                        return dividends_paid
            
            # Method 5: If it's a dividend stock but no data, estimate from yield
            dividend_yield = info.get('dividendYield', np.nan)
            current_price = info.get('currentPrice', np.nan)
            if not pd.isna(dividend_yield) and not pd.isna(current_price) and dividend_yield > 0:
                return dividend_yield * current_price
            
            # Final fallback: check if company is known to pay dividends
            industry = info.get('industry', '').lower()
            if any(x in industry for x in ['utility', 'reit', 'energy', 'financial', 'consumer defensive']):
                # Typical dividend stocks - use small conservative estimate
                return current_price * 0.02 if not pd.isna(current_price) else 1.0
            
            return 0.0  # Likely not a dividend-paying company
            
        except Exception:
            return 0.0  # Default to no dividends

    def calculate_dividend_growth(self, tk: yf.Ticker) -> float:
        """Calculate dividend growth rate"""
        try:
            info = getattr(tk, 'info', {}) or {}
            
            # Try to get dividend growth rate directly
            dividend_growth = info.get('dividendGrowth', np.nan)
            if not pd.isna(dividend_growth):
                return dividend_growth * 100
                
            # Calculate from historical dividends
            dividends = tk.dividends
            if not dividends.empty and len(dividends) >= 4:
                # Get annual dividends (use 'YE' to avoid FutureWarning)
                annual_dividends = dividends.resample('YE').sum()
                if len(annual_dividends) >= 3:
                    # Calculate CAGR
                    start_val = annual_dividends.iloc[0]
                    end_val = annual_dividends.iloc[-1]
                    years = len(annual_dividends) - 1
                    if start_val > 0 and end_val > 0 and years > 0:
                        cagr = (end_val / start_val) ** (1/years) - 1
                        return cagr * 100
            
            # Fallback to earnings growth or revenue growth
            earnings_growth = info.get('earningsGrowth', np.nan)
            if not pd.isna(earnings_growth):
                return earnings_growth * 100
                
            revenue_growth = info.get('revenueGrowth', np.nan)
            if not pd.isna(revenue_growth):
                return revenue_growth * 100 * 0.8  # Assume dividend growth is 80% of revenue growth
                
            # Final fallback
            return 5.0
            
        except Exception:
            return 5.0  # Default fallback

    def calculate_earnings_growth(self, tk: yf.Ticker) -> float:
        """Calculate earnings growth rate"""
        try:
            info = getattr(tk, 'info', {}) or {}
            
            # Try to get earnings growth directly
            earnings_growth = info.get('earningsGrowth', np.nan)
            if not pd.isna(earnings_growth):
                return earnings_growth * 100
                
            # Calculate from historical EPS
            financials = getattr(tk, 'financials', None)
            if isinstance(financials, pd.DataFrame) and not financials.empty:
                # Look for net income row
                net_income_row = None
                for idx in financials.index:
                    if 'net income' in str(idx).lower():
                        net_income_row = idx
                        break
                
                if net_income_row is not None:
                    net_incomes = financials.loc[net_income_row]
                    # Convert to numeric and drop NaNs
                    numeric_incomes = pd.to_numeric(net_incomes, errors='coerce').dropna()
                    
                    if len(numeric_incomes) >= 3:
                        # Calculate CAGR
                        start_val = numeric_incomes.iloc[-1]
                        end_val = numeric_incomes.iloc[0]
                        years = len(numeric_incomes) - 1
                        if start_val > 0 and end_val > 0 and years > 0:
                            cagr = (end_val / start_val) ** (1/years) - 1
                            return cagr * 100
            
            # Fallback to analyst estimates or industry average
            industry = info.get('industry', '').lower()
            if any(x in industry for x in ['technology', 'software', 'internet', 'consumer electronics']):
                return 12.0  # Higher growth for tech
            elif any(x in industry for x in ['financial', 'bank', 'insurance']):
                return 7.0   # Moderate growth for financials
            elif any(x in industry for x in ['utility', 'energy', 'consumer']):
                return 4.0   # Lower growth for stable industries
            else:
                return 7.5   # Default growth rate
                
        except Exception:
            return 7.5  # Default fallback


    def calculate_sustainable_growth_rate(self, tk: yf.Ticker) -> float:
        """Calculate sustainable growth rate based on retention ratio and ROE"""
        try:
            info = getattr(tk, 'info', {}) or {}
            
            # Get return on equity
            roe = info.get('returnOnEquity', np.nan)
            if pd.isna(roe):
                # Calculate ROE from financials
                income_stmt = getattr(tk, 'financials', None)
                balance_sheet = getattr(tk, 'balance_sheet', None)
                
                if (isinstance(income_stmt, pd.DataFrame) and not income_stmt.empty and
                    isinstance(balance_sheet, pd.DataFrame) and not balance_sheet.empty):
                    
                    # Find net income
                    net_income = None
                    for idx in income_stmt.index:
                        if 'net income' in str(idx).lower():
                            net_income = income_stmt.loc[idx].iloc[0]
                            break
                    
                    # Find shareholders equity
                    equity = None
                    for idx in balance_sheet.index:
                        if any(term in str(idx).lower() for term in ['total equity', 'stockholders equity']):
                            equity = balance_sheet.loc[idx].iloc[0]
                            break
                    
                    if net_income is not None and equity is not None and equity > 0:
                        roe = net_income / equity
                    else:
                        roe = 0.15  # Reasonable default
                else:
                    roe = 0.15  # Reasonable default
            
            # Get retention ratio (1 - payout ratio)
            payout_ratio = info.get('payoutRatio', np.nan)
            if pd.isna(payout_ratio):
                # Estimate based on industry
                industry = info.get('industry', '').lower()
                if any(x in industry for x in ['technology', 'growth']):
                    retention_ratio = 0.8  # Growth companies retain more earnings
                elif any(x in industry for x in ['utility', 'consumer']):
                    retention_ratio = 0.4  # Mature companies pay more dividends
                else:
                    retention_ratio = 0.6  # Average
            else:
                retention_ratio = 1 - payout_ratio
            
            # Sustainable growth rate = ROE * Retention Ratio
            sustainable_growth = roe * retention_ratio
            
            # Cap at reasonable level
            return min(sustainable_growth, 0.12)  # Max 12% sustainable growth
            
        except Exception:
            return 0.06  # Conservative default


    def auto_calculate_parameters(self, tk: yf.Ticker):
        """Automatically calculate all parameters for valuation models"""
        if not self.auto_fetch_checkbox.isChecked():
            return
            
        try:
            # Calculate growth rate
            growth_rate = self.calculate_growth_rate(tk)
            self.growth_rate.setValue(growth_rate)
            self.calculated_growth.setText(f"{growth_rate:.2f}%")
            
            # Calculate discount rate
            discount_rate = self.calculate_discount_rate(tk)
            
            # Update UI displays with calculated rates
            self.update_rate_displays(discount_rate)
            
            # Calculate terminal growth rate
            terminal_growth = self.calculate_terminal_growth(tk)
            self.terminal_growth.setValue(terminal_growth)
            
            # Calculate dividend growth rate
            dividend_growth = self.calculate_dividend_growth(tk)
            self.dividend_growth.setValue(dividend_growth)
            
            # Calculate and display dividend amount
            dividend_amount = self.calculate_dividend_amount(tk)
            self.dividend_amount.setText(fmt_money(dividend_amount, self.currency))
            
            # Calculate earnings growth rate
            earnings_growth = self.calculate_earnings_growth(tk)
            self.earnings_growth.setValue(earnings_growth)
            
            # Display beta and industry
            info = getattr(tk, 'info', {}) or {}
            beta = info.get('beta', np.nan)
            if pd.isna(beta):
                beta = self.calculate_beta(tk)
            self.calculated_beta.setText(f"{beta:.2f}" if not pd.isna(beta) else "N/A")
            
            industry = info.get('industry', 'N/A')
            self.calculated_industry.setText(industry)
            
        except Exception as e:
            print(f"Error in auto_calculate_parameters: {e}")
            # Don't show error to user, just use default values


    def calculate_ebitda(self, tk: yf.Ticker) -> float:
        """Calculate EBITDA from financial statements"""
        try:
            income_stmt = getattr(tk, 'financials', None)
            if not isinstance(income_stmt, pd.DataFrame) or income_stmt.empty:
                return np.nan
                
            # Look for operating income (EBIT)
            ebit = None
            for idx in income_stmt.index:
                if any(term in str(idx).lower() for term in ['operating income', 'ebit', 'operating profit']):
                    ebit = income_stmt.loc[idx].iloc[0]  # Most recent year
                    break
                    
            if ebit is None:
                # Fallback: calculate from components
                revenue = None
                cogs = None
                opex = None
                for idx in income_stmt.index:
                    if 'total revenue' in str(idx).lower():
                        revenue = income_stmt.loc[idx].iloc[0]
                    elif 'cost of revenue' in str(idx).lower() or 'cogs' in str(idx).lower():
                        cogs = income_stmt.loc[idx].iloc[0]
                    elif 'operating expense' in str(idx).lower() or 'sga' in str(idx).lower():
                        opex = income_stmt.loc[idx].iloc[0]
                
                if revenue is not None and cogs is not None and opex is not None:
                    ebit = revenue - cogs - opex
                else:
                    return np.nan
            
            # Look for depreciation and amortization
            cashflow = getattr(tk, 'cashflow', None)
            if isinstance(cashflow, pd.DataFrame) and not cashflow.empty:
                for idx in cashflow.index:
                    if any(term in str(idx).lower() for term in ['depreciation', 'amortization', 'd&a']):
                        da = cashflow.loc[idx].iloc[0]  # Most recent year
                        return ebit + da
            
            # Fallback: try to get from info
            info = getattr(tk, 'info', {}) or {}
            ebitda = info.get('ebitda', np.nan)
            if not pd.isna(ebitda):
                return ebitda
                
            return np.nan
            
        except Exception:
            return np.nan

    # -----------------------------
    # Core Actions
    # -----------------------------
    def calculate(self):
        ticker = self.ticker_input.text().strip().upper()
        if not ticker:
            QMessageBox.warning(self, "Input Error", "Please enter a ticker symbol")
            return

        try:
            self.progress_bar.setVisible(True)
            self.current_ticker = ticker
            symbol = ticker.split()[0]  # Handle Bloomberg-style like "AAPL US Equity"
            tk = UnifiedTicker(symbol, CONFIG)

            # Get current price with fallbacks
            hist = tk.history(period="5d")
            current_price = None
            if hist is not None and not hist.empty and 'Close' in hist:
                current_price = float(hist['Close'].dropna().iloc[-1])
            else:
                fi = getattr(tk, 'fast_info', None) or {}
                current_price = fi.get('lastPrice') or fi.get('last_price') or fi.get('last_close')
            if current_price is None:
                raise ValueError("No recent price data available")
            current_price = float(current_price)
            self.current_price.setText(fmt_money(current_price, self.currency))

            # Automatically calculate parameters
            self.auto_calculate_parameters(tk)

            # Get financial data
            self.load_financial_statements(tk)

            # Run valuation models
            method = self.valuation_method.currentText()
            if method == "DCF":
                self.run_dcf_analysis(tk, current_price)
            elif method == "Comparables":
                self.run_comps_analysis(tk, current_price)
            elif method == "Dividend Discount":
                self.run_ddm_analysis(tk, current_price)
            elif method == "Residual Income":
                self.run_rim_analysis(tk, current_price)
            elif method == "Graham Formula":
                self.run_graham_analysis(tk, current_price)
            elif method == "EBITDA Valuation": 
                self.run_ebitda_analysis(tk, current_price)
            else:
                # Placeholders for other methods
                self.recommendation.setText("N/A")

            # Update summary
            self.update_summary(tk, current_price)

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Network Error", f"Network error while fetching data: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", f"Error processing {ticker}:\n{str(e)}")
            traceback.print_exc()
        finally:
            self.progress_bar.setVisible(False)

    def refresh_data(self):
        """Refresh data for the current ticker"""
        if not self.current_ticker:
            QMessageBox.warning(self, "Refresh Error", "No ticker selected to refresh")
            return
        self.calculate()


    def load_financial_statements(self, tk: yf.Ticker):
        """Load and display financial statements with proper error handling"""
        try:
            # Income Statement
            income = getattr(tk, 'financials', None)
            if isinstance(income, pd.DataFrame) and not income.empty and validate_financial_data(income):
                income = income.copy()
                income.columns = income.columns.astype(str)
                self.populate_table(self.income_table, income, "Income Statement")

            # Balance Sheet
            balance = getattr(tk, 'balance_sheet', None)
            if isinstance(balance, pd.DataFrame) and not balance.empty and validate_financial_data(balance):
                balance = balance.copy()
                balance.columns = balance.columns.astype(str)
                self.populate_table(self.balance_table, balance, "Balance Sheet")

            # Cash Flow
            cashflow = getattr(tk, 'cashflow', None)
            if isinstance(cashflow, pd.DataFrame) and not cashflow.empty and validate_financial_data(cashflow):
                cashflow = cashflow.copy()
                cashflow.columns = cashflow.columns.astype(str)
                self.populate_table(self.cashflow_table, cashflow, "Cash Flow")

            # Key Ratios
            ratios = self.calculate_ratios(tk)
            self.populate_table(self.ratios_table, ratios, "Key Ratios")

        except Exception as e:
            QMessageBox.warning(self, "Data Error", f"Error loading financials: {str(e)}")
            print(f"Debug - Financial Data Error: {e}")
            traceback.print_exc()

    # -----------------------------
    # Table population (single robust version)
    # -----------------------------
    def populate_table(self, table: QTableWidget, df: pd.DataFrame, title: str):
        """Populate a table with DataFrame/Series contents. Numeric values keep a numeric sort role."""
        try:
            table.setSortingEnabled(False)
            table.clear()

            if isinstance(df, pd.Series):
                df = df.to_frame(name="Value")

            if isinstance(df, pd.DataFrame):
                # Ensure string labels
                df = df.copy()
                df.columns = [str(c) for c in df.columns]
                df.index = [str(i) for i in df.index]

                table.setRowCount(df.shape[0])
                table.setColumnCount(df.shape[1])
                table.setHorizontalHeaderLabels([str(col).replace('_', ' ').title() for col in df.columns])

                for i in range(df.shape[0]):
                    for j in range(df.shape[1]):
                        val = df.iat[i, j]
                        display_text = "N/A"
                        if pd.isna(val):
                            display_text = "N/A"
                        elif isinstance(val, (int, float, np.floating)):
                            # Heuristic: money-like if magnitude is large and column looks like a statement period
                            display_text = fmt_money(float(val), self.currency)
                        else:
                            display_text = str(val)

                        item = QTableWidgetItem(display_text)
                        # Set numeric role to allow correct sorting when applicable
                        if isinstance(val, (int, float, np.floating)) and not pd.isna(val):
                            item.setData(Qt.EditRole, float(val))
                        table.setItem(i, j, item)

                table.resizeColumnsToContents()

            table.setSortingEnabled(True)
        except Exception as e:
            print(f"Error populating {title} table: {e}")
            QMessageBox.warning(self, "Table Error", f"Could not display {title} data.\n{str(e)}")

    # -----------------------------
    # Ratios
    # -----------------------------
    def calculate_ratios(self, tk: yf.Ticker) -> pd.DataFrame:
        """Calculate key financial ratios with safe .info access."""
        ratios: Dict[str, float] = {}
        info = getattr(tk, 'info', {}) or {}

        # Get currency for formatting
        self.currency = info.get('currency', '$')
        if self.currency == 'USD':
            self.currency = '$'
        elif self.currency == 'EUR':
            self.currency = '€'
        elif self.currency == 'GBP':
            self.currency = '£'
        elif self.currency == 'JPY':
            self.currency = '¥'

        def g(key, default=np.nan):
            v = info.get(key, default)
            try:
                return float(v)
            except Exception:
                return default

        # Profitability Ratios
        ratios['Gross Margin'] = g('grossMargins') * 100
        ratios['Operating Margin'] = g('operatingMargins') * 100
        ratios['Net Margin'] = g('profitMargins') * 100
        ratios['ROE'] = g('returnOnEquity') * 100
        ratios['ROA'] = g('returnOnAssets') * 100

        # Valuation Multiples
        ratios['P/E'] = g('trailingPE')
        ratios['Forward P/E'] = g('forwardPE')
        ratios['P/B'] = g('priceToBook')
        ratios['P/S'] = g('priceToSalesTrailing12Months')
        ratios['EV/EBITDA'] = g('enterpriseToEbitda')

        # Liquidity Ratios
        ratios['Current Ratio'] = g('currentRatio')
        ratios['Quick Ratio'] = g('quickRatio')

        # Leverage Ratios
        ratios['Debt/Equity'] = g('debtToEquity')
        ratios['Debt/EBITDA'] = np.nan  # Placeholder unless computed

        df = pd.DataFrame.from_dict(ratios, orient='index', columns=['Value'])
        out = pd.DataFrame(index=df.index, columns=['Value'])
        for k, v in df['Value'].items():
            if k in ['P/E','Forward P/E','P/B','P/S','EV/EBITDA','Current Ratio','Quick Ratio','Debt/Equity']:
                out.loc[k, 'Value'] = "N/A" if pd.isna(v) else f"{float(v):,.2f}"
            else:  # treat as percent
                out.loc[k, 'Value'] = "N/A" if pd.isna(v) else f"{float(v):.2f}%"
        return out

    # -----------------------------
    # DCF
    # -----------------------------
    def run_dcf_analysis(self, tk: yf.Ticker, current_price: float):
        """Perform detailed DCF valuation with robust FCF lookup and guards."""
        cashflow = getattr(tk, 'cashflow', None)
        if not isinstance(cashflow, pd.DataFrame) or cashflow.empty:
            raise ValueError("Cash Flow statement not available")

        # Case-insensitive lookup for Free Cash Flow (or compute it)
        idx_lower = {str(i).lower(): i for i in cashflow.index}
        fcf_row_key = next((idx_lower[k] for k in idx_lower if 'free cash flow' in k), None)

        if fcf_row_key is not None:
            fcf_series = pd.to_numeric(cashflow.loc[fcf_row_key], errors='coerce').dropna()
        else:
            # Try to compute: FCF = Operating Cash Flow - Capital Expenditures
            ocf_key = next((idx_lower[k] for k in idx_lower
                            if 'total cash from operating activities' in k or 'operating cash flow' in k), None)
            capex_key = next((idx_lower[k] for k in idx_lower
                            if 'capital expenditure' in k or 'capital expenditures' in k), None)
            if ocf_key is not None and capex_key is not None:
                fcf_series = (pd.to_numeric(cashflow.loc[ocf_key], errors='coerce') -
                            pd.to_numeric(cashflow.loc[capex_key], errors='coerce')).dropna()
            else:
                raise ValueError("Free Cash Flow data not available")

        if fcf_series.empty:
            raise ValueError("Free Cash Flow values are empty")


        # Use the average of the last 3 years if available, otherwise use the most recent
        if len(fcf_series) >= 3:
            last_fcf = float(fcf_series.sort_index(ascending=False).iloc[:3].mean())  # 3 most recent annuals
        else:
            last_fcf = float(fcf_series.iloc[0])

        years = int(self.forecast_years.value())
        g = float(self.growth_rate.value()) / 100.0
        r = float(self.discount_rate.value()) / 100.0
        terminal_g = min(float(self.terminal_growth.value()) / 100.0, 0.03)  # Cap terminal growth at 3%

        if r <= terminal_g:
            raise ValueError("Discount rate must exceed terminal growth rate")

        # Project FCF and discount
        projected = [last_fcf * ((1 + g) ** (i + 1)) for i in range(years)]
        discount_factors = [1 / ((1 + r) ** (i + 1)) for i in range(years)]
        pv_fcf = [cf * df for cf, df in zip(projected, discount_factors)]

        # Terminal Value (Gordon Growth)
        terminal = (projected[-1] * (1 + terminal_g)) / (r - terminal_g)
        pv_terminal = terminal / ((1 + r) ** years)

        # Enterprise Value
        info = getattr(tk, 'info', {}) or {}
        debt = float(info.get('totalDebt', 0) or 0)
        cash = float(info.get('cash', 0) or 0)
        
        # Get shares outstanding with proper unit handling
        shares = info.get('sharesOutstanding', np.nan)
        market_cap = info.get('marketCap', np.nan)

        if not (isinstance(shares, (int, float, np.floating)) and shares > 0):
            if isinstance(market_cap, (int, float, np.floating)) and market_cap > 0 and current_price > 0:
                shares = market_cap / current_price  # safe fallback



        # Calculate enterprise value and equity value
        ev = float(sum(pv_fcf) + pv_terminal)
        equity_value = ev - debt + cash

        # Populate DCF Table before any early return
        self.dcf_table.setRowCount(years + 1)
        for i in range(years):
            self.dcf_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.dcf_table.setItem(i, 1, QTableWidgetItem(fmt_money(projected[i], self.currency)))
            self.dcf_table.setItem(i, 2, QTableWidgetItem(fmt_percent(g * 100, 1)))
            self.dcf_table.setItem(i, 3, QTableWidgetItem(f"{discount_factors[i]:.4f}"))
            self.dcf_table.setItem(i, 4, QTableWidgetItem(fmt_money(pv_fcf[i], self.currency)))

        # Add terminal value
        self.dcf_table.setItem(years, 0, QTableWidgetItem("Terminal"))
        self.dcf_table.setItem(years, 1, QTableWidgetItem(fmt_money(terminal, self.currency)))
        self.dcf_table.setItem(years, 2, QTableWidgetItem(fmt_percent(terminal_g * 100, 1)))
        self.dcf_table.setItem(years, 3, QTableWidgetItem(f"{(1 / ((1 + r) ** years)):.4f}"))
        self.dcf_table.setItem(years, 4, QTableWidgetItem(fmt_money(pv_terminal, self.currency)))

        # Plot DCF Results
        fig = self.dcf_plot_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        labels = [f"Year {i}" for i in range(1, years + 1)] + ["Terminal"]
        values = pv_fcf + [pv_terminal]
        ax.bar(labels, values)
        ax.set_title(f"DCF Valuation - {self.current_ticker}")
        ax.set_ylabel(f"Present Value ({self.currency})")
        ax.tick_params(axis='x', rotation=45)
        for i, v in enumerate(values):
            if not (v is None or (isinstance(v, float) and np.isnan(v))):
                ax.text(i, v, fmt_money(v, self.currency, allow_sign=False), ha='center', va='bottom')
        fig.tight_layout()
        self.dcf_plot_canvas.draw()

        # Sensitivity Analysis (±2% around g and r)
        fig2 = self.sensitivity_canvas.figure
        fig2.clear()
        ax2 = fig2.add_subplot(111)
        
        growth_rates = np.linspace(g - 0.02, g + 0.02, 5)
        #growth_rates = np.linspace(max(g - 0.02, 0), g + 0.02, 5)  # Growth can't be negative
        discount_rates = np.linspace(max(r - 0.02, terminal_g + 0.01), r + 0.02, 5)  # Ensure r > terminal_g
        sens_matrix = np.zeros((len(growth_rates), len(discount_rates))) * np.nan

        for i, gr in enumerate(growth_rates):
            for j, dr in enumerate(discount_rates):
                if dr <= terminal_g:  # Skip if discount rate <= terminal growth
                    continue
                pv_seq = [last_fcf * ((1 + gr) ** (k + 1)) / ((1 + dr) ** (k + 1)) for k in range(years)]
                term = (last_fcf * ((1 + gr) ** years) * (1 + terminal_g)) / (dr - terminal_g) / ((1 + dr) ** years)
                ev_ = sum(pv_seq) + term
                eq_ = ev_ - debt + cash
                if isinstance(shares, (int, float, np.floating)) and shares > 0:
                    sens_matrix[i, j] = eq_ / shares

        im = ax2.imshow(sens_matrix, cmap='RdYlGn', aspect='auto')
        fig2.colorbar(im, ax=ax2, label='Price Target')
        ax2.set_xticks(np.arange(len(discount_rates)))
        ax2.set_xticklabels([f"{dr*100:.1f}%" for dr in discount_rates])
        ax2.set_xlabel("Discount Rate")
        ax2.set_yticks(np.arange(len(growth_rates)))
        ax2.set_yticklabels([f"{gr*100:.1f}%" for gr in growth_rates])
        ax2.set_ylabel("Growth Rate")
        ax2.set_title("Price Target Sensitivity")

        for i in range(len(growth_rates)):
            for j in range(len(discount_rates)):
                v = sens_matrix[i, j]
                if not (v is None or (isinstance(v, float) and np.isnan(v))):
                    ax2.text(j, i, f"{self.currency}{v:.1f}", ha="center", va="center", color="black")

        fig2.tight_layout()
        self.sensitivity_canvas.draw()

        # Now, decide how to present per-share value robustly
        if not isinstance(shares, (int, float, np.floating)) or shares <= 0:
            self.price_target.setText("N/A")
            self.upside.setText("N/A")
            self.valuation_range.setText("N/A")
            self.recommendation.setText("N/A")
            QMessageBox.warning(self, "DCF Warning", "Shares outstanding not available; per-share target cannot be computed.")
            return

        if equity_value <= 0:
            # Negative equity value: inform the user and avoid crashing
            self.price_target.setText("N/A")
            self.upside.setText("N/A")
            self.valuation_range.setText("N/A")
            self.recommendation.setText("N/A")
            QMessageBox.warning(self, "DCF Warning", "DCF produced a negative equity value (debt may exceed enterprise value). Adjust assumptions or use another method.")
            return

        price_target = equity_value / shares
        
        # Display results
        self.price_target.setText(fmt_money(price_target, self.currency))
        upside = ((price_target - current_price) / current_price) * 100.0
        self.upside.setText(f"{upside:+.2f}%")
        self.upside.setStyleSheet(f"color: {'green' if upside >= 0 else 'red'}; font-weight: bold;")

        # Recommendation bands
        if upside > 15:
            rec, color = ("STRONG BUY", "green")
        elif upside > 5:
            rec, color = ("BUY", "lightgreen")
        elif upside < -15:
            rec, color = ("STRONG SELL", "darkred")
        elif upside < -5:
            rec, color = ("SELL", "red")
        else:
            rec, color = ("HOLD", "gray")
        self.recommendation.setText(rec)
        self.recommendation.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px;")

        # Valuation range (80-120% of target price)
        low_range = price_target * 0.8
        high_range = price_target * 1.2
        self.valuation_range.setText(f"{fmt_money(low_range, self.currency)} - {fmt_money(high_range, self.currency)}")

        # Populate DCF Table
        self.dcf_table.setRowCount(years + 1)
        for i in range(years):
            self.dcf_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.dcf_table.setItem(i, 1, QTableWidgetItem(fmt_money(projected[i], self.currency)))
            self.dcf_table.setItem(i, 2, QTableWidgetItem(fmt_percent(g * 100, 1)))
            self.dcf_table.setItem(i, 3, QTableWidgetItem(f"{discount_factors[i]:.4f}"))
            self.dcf_table.setItem(i, 4, QTableWidgetItem(fmt_money(pv_fcf[i], self.currency)))

        # Add terminal value
        self.dcf_table.setItem(years, 0, QTableWidgetItem("Terminal"))
        self.dcf_table.setItem(years, 1, QTableWidgetItem(fmt_money(terminal, self.currency)))
        self.dcf_table.setItem(years, 2, QTableWidgetItem(fmt_percent(terminal_g * 100, 1)))
        self.dcf_table.setItem(years, 3, QTableWidgetItem(f"{(1 / ((1 + r) ** years)):.4f}"))
        self.dcf_table.setItem(years, 4, QTableWidgetItem(fmt_money(pv_terminal, self.currency)))

        # Plot DCF Results
        fig = self.dcf_plot_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        labels = [f"Year {i}" for i in range(1, years + 1)] + ["Terminal"]
        values = pv_fcf + [pv_terminal]
        ax.bar(labels, values)
        ax.set_title(f"DCF Valuation - {self.current_ticker}")
        ax.set_ylabel(f"Present Value ({self.currency})")
        ax.tick_params(axis='x', rotation=45)
        for i, v in enumerate(values):
            if not (v is None or (isinstance(v, float) and np.isnan(v))):
                ax.text(i, v, fmt_money(v, self.currency, allow_sign=False), ha='center', va='bottom')
        fig.tight_layout()
        self.dcf_plot_canvas.draw()

        # Sensitivity Analysis (±2% around g and r)
        fig2 = self.sensitivity_canvas.figure
        fig2.clear()
        ax2 = fig2.add_subplot(111)

        growth_rates = np.linspace(max(g - 0.02, 0), g + 0.02, 5)  # Growth can't be negative
        discount_rates = np.linspace(max(r - 0.02, terminal_g + 0.01), r + 0.02, 5)  # Ensure r > terminal_g
        sens_matrix = np.zeros((len(growth_rates), len(discount_rates))) * np.nan

        for i, gr in enumerate(growth_rates):
            for j, dr in enumerate(discount_rates):
                if dr <= terminal_g:  # Skip if discount rate <= terminal growth
                    continue
                pv_seq = [last_fcf * ((1 + gr) ** (k + 1)) / ((1 + dr) ** (k + 1)) for k in range(years)]
                term = (last_fcf * ((1 + gr) ** years) * (1 + terminal_g)) / (dr - terminal_g) / ((1 + dr) ** years)
                ev_ = sum(pv_seq) + term
                eq_ = ev_ - debt + cash
                sens_matrix[i, j] = eq_ / shares

        im = ax2.imshow(sens_matrix, cmap='RdYlGn', aspect='auto')
        fig2.colorbar(im, ax=ax2, label='Price Target')
        ax2.set_xticks(np.arange(len(discount_rates)))
        ax2.set_xticklabels([f"{dr*100:.1f}%" for dr in discount_rates])
        ax2.set_xlabel("Discount Rate")
        ax2.set_yticks(np.arange(len(growth_rates)))
        ax2.set_yticklabels([f"{gr*100:.1f}%" for gr in growth_rates])
        ax2.set_ylabel("Growth Rate")
        ax2.set_title("Price Target Sensitivity")
        
        self.store_valuation_result("DCF", price_target, upside)
        
        for i in range(len(growth_rates)):
            for j in range(len(discount_rates)):
                v = sens_matrix[i, j]
                if not (v is None or (isinstance(v, float) and np.isnan(v))):
                    ax2.text(j, i, f"{self.currency}{v:.1f}", ha="center", va="center", color="black")

        fig2.tight_layout()
        self.sensitivity_canvas.draw()

    # -----------------------------
    # Comparables
    # -----------------------------
    def run_comps_analysis(self, tk: yf.Ticker, current_price: float):
        """Perform comparable companies analysis with full data for implied prices."""
        comps = [c.strip().upper() for c in self.comparables_input.text().split(',') if c.strip()]
        if not comps:
            QMessageBox.warning(self, "Input Error", "Please enter comparable tickers")
            return

        target_sym = (self.current_ticker or "").split()[0]
        all_syms = [target_sym] + comps

        # Build full metric set
        fields_needed = [
            'currentPrice','trailingPE','enterpriseToEbitda','priceToBook',
            'priceToSalesTrailing12Months','dividendYield','marketCap',
            'ebitda','totalDebt','cash','sharesOutstanding',
            'trailingEps','bookValue','revenuePerShare'
        ]

        comp_rows: List[Dict[str, float]] = []
        for sym in all_syms:
            try:
                ci = get_cached_ticker_info(sym)
                row = {f: (ci.get(f, np.nan)) for f in fields_needed}
                # Normalize for display
                row['Ticker'] = sym
                row['Price'] = row.pop('currentPrice', np.nan)
                row['P/E'] = row.pop('trailingPE', np.nan)
                row['EV/EBITDA'] = row.pop('enterpriseToEbitda', np.nan)
                row['P/B'] = row.pop('priceToBook', np.nan)
                row['P/S'] = row.pop('priceToSalesTrailing12Months', np.nan)
                dy = row.pop('dividendYield', np.nan)
                row['Div Yield'] = (float(dy) * 100.0) if isinstance(dy, (int, float)) else np.nan
                comp_rows.append(row)
            except Exception as e:
                print(f"Error processing {sym}: {e}")

        if not comp_rows:
            raise ValueError("No valid comparable companies found")

        comp_df = pd.DataFrame(comp_rows)
        if comp_df.empty:
            raise ValueError("Comparable data frame is empty")

        if target_sym not in comp_df['Ticker'].values:
            raise ValueError("Target symbol row missing in comparables")

        target_row = comp_df.loc[comp_df['Ticker'] == target_sym].iloc[0]
        peers = comp_df.loc[comp_df['Ticker'] != target_sym]
        if peers.empty:
            raise ValueError("No peer data to compute medians")

        implied_values: Dict[str, float] = {}

        # Filter out negative or extreme multiples
        def filter_multiple(series, min_val=0, max_val=100):
            return series[(series >= min_val) & (series <= max_val)].dropna()

        # P/E -> price = median_PE * EPS
        valid_pe = filter_multiple(peers['P/E'], 0, 100)
        median_pe = valid_pe.median() if not valid_pe.empty else np.nan
        eps = target_row.get('trailingEps', np.nan)
        if pd.notna(median_pe) and pd.notna(eps):
            implied_values['P/E'] = float(median_pe) * float(eps)

        # P/B -> price = median_PB * BVPS
        valid_pb = filter_multiple(peers['P/B'], 0, 10)
        median_pb = valid_pb.median() if not valid_pb.empty else np.nan
        bvps = target_row.get('bookValue', np.nan)
        if pd.notna(median_pb) and pd.notna(bvps):
            implied_values['P/B'] = float(median_pb) * float(bvps)

        # P/S -> price = median_PS * Revenue per share
        valid_ps = filter_multiple(peers['P/S'], 0, 20)
        median_ps = valid_ps.median() if not valid_ps.empty else np.nan
        rps = target_row.get('revenuePerShare', np.nan)
        if pd.notna(median_ps) and pd.notna(rps):
            implied_values['P/S'] = float(median_ps) * float(rps)

        # EV/EBITDA -> (median multiple * EBITDA - debt + cash) / shares
        valid_ev_ebitda = filter_multiple(peers['EV/EBITDA'], 0, 30)
        median_ev_ebitda = valid_ev_ebitda.median() if not valid_ev_ebitda.empty else np.nan
        ebitda = target_row.get('ebitda', np.nan)
        debt = float(target_row.get('totalDebt', 0) or 0)
        cash = float(target_row.get('cash', 0) or 0)
        shares = target_row.get('sharesOutstanding', np.nan)


        if pd.notna(median_ev_ebitda) and pd.notna(ebitda) and pd.notna(shares) and float(shares) > 0:
            ev = float(median_ev_ebitda) * float(ebitda)
            equity_value = ev - debt + cash
            implied_values['EV/EBITDA'] = equity_value / float(shares)

        # Blend implied prices (median of methods)
        blended = np.nan
        non_nan_vals = [v for v in implied_values.values() if pd.notna(v)]
        if non_nan_vals:
            blended = float(np.median(non_nan_vals))
            self.price_target.setText(fmt_money(blended, self.currency))
            upside = ((blended - current_price) / current_price) * 100.0
            self.upside.setText(f"{upside:+.2f}%")
            self.upside.setStyleSheet(f"color: {'green' if upside >= 0 else 'red'}; font-weight: bold;")

            # Valuation range (80-120% of target price)
            low_range = blended * 0.8
            high_range = blended * 1.2
            self.valuation_range.setText(f"{fmt_money(low_range, self.currency)} - {fmt_money(high_range, self.currency)}")

            # Recommendation
            if upside > 15:
                rec, color = ("STRONG BUY", "green")
            elif upside > 5:
                rec, color = ("BUY", "lightgreen")
            elif upside < -15:
                rec, color = ("STRONG SELL", "darkred")
            elif upside < -5:
                rec, color = ("SELL", "red")
            else:
                rec, color = ("HOLD", "gray")
            self.recommendation.setText(rec)
            self.recommendation.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px;")

        # Populate Comparables Table (and fill Implied Value for target)
        self.comp_table.setRowCount(len(comp_df))
        headers = ["Ticker", "Price", "P/E", "EV/EBITDA", "P/B", "P/S", "Div Yield", "Implied Value"]
        self.comp_table.setColumnCount(len(headers))
        self.comp_table.setHorizontalHeaderLabels(headers)

        comp_df_reset = comp_df.reset_index(drop=True)
        for i, row in comp_df_reset.iterrows():
            self.comp_table.setItem(i, 0, QTableWidgetItem(str(row.get("Ticker", ""))))
            self.comp_table.setItem(i, 1, QTableWidgetItem("N/A" if pd.isna(row.get("Price")) else fmt_money(row.get("Price"), self.currency)))
            self.comp_table.setItem(i, 2, QTableWidgetItem("N/A" if pd.isna(row.get("P/E")) else f"{row['P/E']:.1f}"))
            self.comp_table.setItem(i, 3, QTableWidgetItem("N/A" if pd.isna(row.get("EV/EBITDA")) else f"{row['EV/EBITDA']:.1f}"))
            self.comp_table.setItem(i, 4, QTableWidgetItem("N/A" if pd.isna(row.get("P/B")) else f"{row['P/B']:.2f}"))
            self.comp_table.setItem(i, 5, QTableWidgetItem("N/A" if pd.isna(row.get("P/S")) else f"{row['P/S']:.2f}"))
            self.comp_table.setItem(i, 6, QTableWidgetItem("N/A" if pd.isna(row.get("Div Yield")) else f"{row['Div Yield']:.2f}%"))

            implied = "N/A"
            if row["Ticker"] == target_sym and pd.notna(blended):
                implied = fmt_money(blended, self.currency)
                for j in range(len(headers)):
                    item = self.comp_table.item(i, j)
                    if item:
                        item.setBackground(QColor(173, 216, 230))  # highlight target
            self.comp_table.setItem(i, 7, QTableWidgetItem(implied))

        # Plot Multiples Comparison (median peers vs target)
        fig = self.multiples_plot.figure
        fig.clear()
        ax = fig.add_subplot(111)

        multiples = ['P/E', 'EV/EBITDA', 'P/B', 'P/S']
        median_values = []
        target_values = []
        
        for m in multiples:
            valid_vals = filter_multiple(peers[m], 0, 100 if m != 'EV/EBITDA' else 30)
            if not valid_vals.empty:
                median_values.append(valid_vals.median())
                target_values.append(target_row.get(m, np.nan))
            else:
                median_values.append(np.nan)
                target_values.append(np.nan)

        # Filter out NaN values for plotting
        valid_indices = [i for i, v in enumerate(median_values) if not pd.isna(v)]
        multiples_filtered = [multiples[i] for i in valid_indices]
        median_values_filtered = [median_values[i] for i in valid_indices]
        target_values_filtered = [target_values[i] for i in valid_indices]

        if multiples_filtered:  # Only plot if we have valid data
            pos = np.arange(len(multiples_filtered))
            width = 0.35
            rects1 = ax.bar(pos - width / 2, median_values_filtered, width, label='Peer Median')
            rects2 = ax.bar(pos + width / 2, target_values_filtered, width, label=target_sym)

            ax.set_ylabel('Multiple Value')
            ax.set_title('Valuation Multiples Comparison')
            ax.set_xticks(pos)
            ax.set_xticklabels(multiples_filtered)
            ax.legend()

            for rect in list(rects1) + list(rects2):
                height = rect.get_height()
                if not pd.isna(height):
                    ax.text(rect.get_x() + rect.get_width() / 2., height, f'{height:.1f}', ha='center', va='bottom')

        fig.tight_layout()
        self.multiples_plot.draw()
        self.store_valuation_result("Comparables", blended, upside)
        # Plot Implied Values per method
        if implied_values:
            fig2 = self.implied_value_plot.figure
            fig2.clear()
            ax2 = fig2.add_subplot(111)

            methods = list(implied_values.keys())
            values = [implied_values[m] for m in methods]
            bars = ax2.bar(methods, values)
            ax2.axhline(current_price, linestyle='--', color='red', label='Current Price')
            ax2.set_ylabel(f'Price ({self.currency})')
            ax2.set_title('Implied Valuation from Different Multiples')
            ax2.tick_params(axis='x', rotation=45)
            ax2.legend()

            for b in bars:
                h = b.get_height()
                ax2.text(b.get_x() + b.get_width()/2., h, fmt_money(h, self.currency, allow_sign=False), ha='center', va='bottom')

            fig2.tight_layout()
            self.implied_value_plot.draw()


    def run_ebitda_analysis(self, tk: yf.Ticker, current_price: float):
        """Perform EBITDA-based valuation analysis"""
        # Get target company EBITDA
        target_ebitda = self.calculate_ebitda(tk)
        if pd.isna(target_ebitda):
            QMessageBox.warning(self, "Data Error", "EBITDA data not available for target company")
            return
        
        # Get comparables
        comps = [c.strip().upper() for c in self.comparables_input.text().split(',') if c.strip()]
        if not comps:
            QMessageBox.warning(self, "Input Error", "Please enter comparable tickers for EBITDA analysis")
            return
        
        # Get financial data for all companies
        all_companies = {}
        target_sym = (self.current_ticker or "").split()[0]
        
        # Add target company
        info = getattr(tk, 'info', {}) or {}
        market_cap = info.get('marketCap', np.nan)
        debt = info.get('totalDebt', 0) or 0
        cash = info.get('cash', 0) or 0
        shares = info.get('sharesOutstanding', np.nan)
        
        # Handle potential share count issues
        if pd.notna(market_cap) and pd.notna(current_price) and current_price > 0 and (pd.isna(shares) or shares <= 0):
            shares = market_cap / current_price
        
        all_companies[target_sym] = {
            'ebitda': target_ebitda,
            'market_cap': market_cap,
            'debt': debt,
            'cash': cash,
            'shares': shares,
            'ev': market_cap + debt - cash if pd.notna(market_cap) else np.nan
        }
        
        # Add comparable companies
        for sym in comps:
            try:
                comp_tk = yf.Ticker(sym)
                comp_info = getattr(comp_tk, 'info', {}) or {}
                comp_ebitda = comp_info.get('ebitda', np.nan)
                
                # If not available in info, calculate from financials
                if pd.isna(comp_ebitda):
                    comp_ebitda = self.calculate_ebitda(comp_tk)
                    
                comp_market_cap = comp_info.get('marketCap', np.nan)
                comp_debt = comp_info.get('totalDebt', 0) or 0
                comp_cash = comp_info.get('cash', 0) or 0
                comp_shares = comp_info.get('sharesOutstanding', np.nan)
                
                # Get current price for share calculation if needed
                comp_hist = comp_tk.history(period="5d")
                comp_current_price = None
                if comp_hist is not None and not comp_hist.empty and 'Close' in comp_hist:
                    comp_current_price = float(comp_hist['Close'].dropna().iloc[-1])
                
                # Handle potential share count issues
                if pd.notna(comp_market_cap) and pd.notna(comp_current_price) and comp_current_price > 0 and (pd.isna(comp_shares) or comp_shares <= 0):
                    comp_shares = comp_market_cap / comp_current_price
                    
                comp_ev = comp_market_cap + comp_debt - comp_cash if pd.notna(comp_market_cap) else np.nan
                
                all_companies[sym] = {
                    'ebitda': comp_ebitda,
                    'market_cap': comp_market_cap,
                    'debt': comp_debt,
                    'cash': comp_cash,
                    'shares': comp_shares,
                    'ev': comp_ev
                }
            except Exception as e:
                print(f"Error processing comparable {sym}: {e}")
        
        # Calculate EV/EBITDA multiples
        valid_comps = {}
        for sym, data in all_companies.items():
            if pd.notna(data['ev']) and pd.notna(data['ebitda']) and data['ebitda'] > 0:
                data['ev_ebitda'] = data['ev'] / data['ebitda']
                valid_comps[sym] = data
        
        if not valid_comps:
            QMessageBox.warning(self, "Data Error", "No valid EV/EBITDA multiples could be calculated")
            return
        
        # Calculate benchmark multiples (exclude target)
        comp_multiple_vals = [data['ev_ebitda'] for sym, data in valid_comps.items() if sym != target_sym]
        if not comp_multiple_vals:
            QMessageBox.warning(self, "Data Error", "No valid comparable multiples found")
            return
        
        median_multiple = float(np.median(comp_multiple_vals))
        mean_multiple = float(np.mean(comp_multiple_vals))
        
        # Calculate implied values for target
        target_data = valid_comps.get(target_sym, {})
        if not target_data:
            QMessageBox.warning(self, "Data Error", "Target company data not available")
            return
        
        implied_ev = target_data['ebitda'] * median_multiple
        implied_equity_value = implied_ev - target_data['debt'] + target_data['cash']
        
        if pd.notna(target_data['shares']) and target_data['shares'] > 0:
            implied_price = implied_equity_value / target_data['shares']
            
            # Display results
            self.price_target.setText(fmt_money(implied_price, self.currency))
            upside = ((implied_price - current_price) / current_price) * 100.0
            self.upside.setText(f"{upside:+.2f}%")
            self.store_valuation_result("EBITDA Valuation", implied_price, upside)

            self.upside.setStyleSheet(f"color: {'green' if upside >= 0 else 'red'}; font-weight: bold;")
            
            # Valuation range (80-120% of target price)
            low_range = implied_price * 0.8
            high_range = implied_price * 1.2
            self.valuation_range.setText(f"{fmt_money(low_range, self.currency)} - {fmt_money(high_range, self.currency)}")
            
            # Recommendation
            if upside > 15:
                rec, color = ("STRONG BUY", "green")
            elif upside > 5:
                rec, color = ("BUY", "lightgreen")
            elif upside < -15:
                rec, color = ("STRONG SELL", "darkred")
            elif upside < -5:
                rec, color = ("SELL", "red")
            else:
                rec, color = ("HOLD", "gray")
            self.recommendation.setText(rec)
            self.recommendation.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px;")
        
        # Populate EBITDA Table
        self.ebitda_table.setRowCount(len(valid_comps))
        headers = ["Ticker", "EV", "EBITDA", "EV/EBITDA", "Implied EV", "Implied Price"]
        self.ebitda_table.setColumnCount(len(headers))
        self.ebitda_table.setHorizontalHeaderLabels(headers)
        
        for i, (sym, data) in enumerate(valid_comps.items()):
            self.ebitda_table.setItem(i, 0, QTableWidgetItem(sym))
            self.ebitda_table.setItem(i, 1, QTableWidgetItem("N/A" if pd.isna(data['ev']) else fmt_money(data['ev'], self.currency)))
            self.ebitda_table.setItem(i, 2, QTableWidgetItem("N/A" if pd.isna(data['ebitda']) else fmt_money(data['ebitda'], self.currency)))
            self.ebitda_table.setItem(i, 3, QTableWidgetItem("N/A" if pd.isna(data.get('ev_ebitda')) else f"{data['ev_ebitda']:.2f}"))
            
            # Calculate implied values for all companies
            if sym == target_sym:
                # For target, use the median multiple from comparables
                comp_median = median_multiple
                implied_ev_val = data['ebitda'] * comp_median if pd.notna(data['ebitda']) else np.nan
                implied_price_val = (implied_ev_val - data['debt'] + data['cash']) / data['shares'] if pd.notna(implied_ev_val) and pd.notna(data['shares']) and data['shares'] > 0 else np.nan
            else:
                # For comparables, use their own multiple (should be close to their current EV)
                implied_ev_val = data['ev']  # Already at fair value
                implied_price_val = (implied_ev_val - data['debt'] + data['cash']) / data['shares'] if pd.notna(implied_ev_val) and pd.notna(data['shares']) and data['shares'] > 0 else np.nan
            
            self.ebitda_table.setItem(i, 4, QTableWidgetItem("N/A" if pd.isna(implied_ev_val) else fmt_money(implied_ev_val, self.currency)))
            self.ebitda_table.setItem(i, 5, QTableWidgetItem("N/A" if pd.isna(implied_price_val) else fmt_money(implied_price_val, self.currency)))
            
            # Highlight target row
            if sym == target_sym:
                for j in range(len(headers)):
                    item = self.ebitda_table.item(i, j)
                    if item:
                        item.setBackground(QColor(173, 216, 230))
        
        # Plot EV/EBITDA Multiples Comparison
        fig = self.ebitda_multiples_plot.figure
        fig.clear()
        ax = fig.add_subplot(111)
        
        comp_names = [sym for sym in valid_comps.keys() if sym != target_sym]
        comp_multiples = [valid_comps[sym]['ev_ebitda'] for sym in comp_names]
        target_multiple = valid_comps[target_sym]['ev_ebitda'] if target_sym in valid_comps else np.nan
        
        if comp_names and not all(pd.isna(m) for m in comp_multiples):
            x_pos = np.arange(len(comp_names) + 1)
            all_multiples = comp_multiples + [target_multiple]
            all_names = comp_names + [target_sym]
            
            bars = ax.bar(x_pos, all_multiples)
            ax.set_ylabel('EV/EBITDA Multiple')
            ax.set_title('EV/EBITDA Multiples Comparison')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(all_names, rotation=45)
            
            # Color target bar differently
            if not pd.isna(target_multiple):
                bars[-1].set_color('lightblue')
            
            # Add median line
            median_val = np.median(comp_multiples)
            ax.axhline(median_val, color='red', linestyle='--', label=f'Median: {median_val:.2f}')
            ax.legend()
            
            # Add values on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                if not pd.isna(height):
                    ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.2f}', ha='center', va='bottom')
        
        fig.tight_layout()
        self.ebitda_multiples_plot.draw()
        
        # Sensitivity Analysis
        fig2 = self.ebitda_sensitivity_canvas.figure
        fig2.clear()
        ax2 = fig2.add_subplot(111)
        
        if pd.notna(target_data['ebitda']) and pd.notna(target_data['shares']) and target_data['shares'] > 0:
            multiples_range = np.linspace(max(median_multiple * 0.7, 1), median_multiple * 1.3, 10)
            implied_prices = []
            
            for multiple in multiples_range:
                implied_ev = target_data['ebitda'] * multiple
                implied_equity = implied_ev - target_data['debt'] + target_data['cash']
                implied_price = implied_equity / target_data['shares']
                implied_prices.append(implied_price)
            
            ax2.plot(multiples_range, implied_prices, 'b-')
            ax2.axhline(current_price, color='r', linestyle='--', label=f'Current Price: {fmt_money(current_price, self.currency)}')
            ax2.axvline(median_multiple, color='g', linestyle='--', label=f'Median Multiple: {median_multiple:.2f}')
            ax2.set_xlabel('EV/EBITDA Multiple')
            ax2.set_ylabel('Implied Price')
            ax2.set_title('Price Sensitivity to EV/EBITDA Multiple')
            ax2.legend()
            ax2.grid(True)
        
        fig2.tight_layout()
        self.ebitda_sensitivity_canvas.draw()

    # -----------------------------
    # Summary
    # -----------------------------
    def update_summary(self, tk: yf.Ticker, current_price: float):
        """Update the summary tab with key metrics (safe info access)."""
        info = getattr(tk, 'info', {}) or {}

        def g(key, default=np.nan):
            v = info.get(key, default)
            try:
                return float(v)
            except Exception:
                return default

        metrics = [
            ("Market Cap (M)", g('marketCap')/1e6, "Market Value"),
            ("Enterprise Value (M)", g('enterpriseValue')/1e6, "Firm Value"),
            ("P/E (TTM)", g('trailingPE'), "Price/Earnings"),
            ("Forward P/E", g('forwardPE'), "Forward Earnings"),
            ("PEG Ratio", g('pegRatio'), "Growth Adjusted"),
            ("P/S", g('priceToSalesTrailing12Months'), "Price/Sales"),
            ("P/B", g('priceToBook'), "Price/Book"),
            ("EV/EBITDA", g('enterpriseToEbitda'), "Enterprise Multiple"),
            ("Dividend Yield", g('dividendYield')*100, "Income Return"),
            ("Beta", g('beta'), "Systematic Risk"),
            ("52W High", g('fiftyTwoWeekHigh'), "1Y High"),
            ("52W Low", g('fiftyTwoWeekLow'), "1Y Low"),
            ("Short % Float", g('shortPercentOfFloat')*100, "Short Interest"),
            ("Institutional %", g('heldPercentInstitutions')*100, "Inst. Ownership"),
            ("ROE", g('returnOnEquity')*100, "Profitability"),
            ("ROA", g('returnOnAssets')*100, "Asset Efficiency"),
            ("Current Ratio", g('currentRatio'), "Liquidity"),
            ("Debt/Equity", g('debtToEquity'), "Leverage"),
            ("Gross Margin", g('grossMargins')*100, "Profit Margin"),
            ("Operating Margin", g('operatingMargins')*100, "Operational Efficiency"),
            ("Revenue Growth (YoY)", g('revenueGrowth')*100, "Growth Rate"),
        ]

        self.metrics_table.setRowCount(len(metrics))

        for i, (name, value, desc) in enumerate(metrics):
            self.metrics_table.setItem(i, 0, QTableWidgetItem(name))

            # Format value appropriately
            if isinstance(value, (int, float)) and not np.isnan(value):
                if name.endswith("(M)"):
                    val_str = fmt_number(value, digits=0) + "M"
                elif any(x in name.lower() for x in ['yield', 'growth', 'roe', 'roa', 'margin', '%']):
                    val_str = fmt_percent(value, 2)
                elif name in ["52W High", "52W Low"]:
                    val_str = fmt_money(value, self.currency)
                else:
                    val_str = fmt_number(value, 2)
            else:
                val_str = "N/A"

            self.metrics_table.setItem(i, 1, QTableWidgetItem(val_str))
            self.metrics_table.setItem(i, 2, QTableWidgetItem("N/A"))  # industry avg placeholder
            self.metrics_table.setItem(i, 3, QTableWidgetItem(desc))

            # Color coding for key metrics (simple bands)
            if isinstance(value, (int, float)) and not np.isnan(value):
                if name in ["P/E (TTM)", "Forward P/E", "PEG Ratio"]:
                    if value < 15:
                        color = QColor(144, 238, 144)  # green-ish
                    elif value > 25:
                        color = QColor(255, 182, 193)  # red-ish
                    else:
                        color = QColor(255, 255, 224)  # yellow-ish
                    self.metrics_table.item(i, 1).setBackground(color)
                elif name == "Dividend Yield" and value > 4:
                    self.metrics_table.item(i, 1).setBackground(QColor(144, 238, 144))
                elif name == "Short % Float" and value > 10:
                    self.metrics_table.item(i, 1).setBackground(QColor(255, 182, 193))

    # -----------------------------
    # Export
    # -----------------------------
    def export_results(self):
        """Export valuation results to Excel (robust to empty cells)."""
        if not self.current_ticker:
            QMessageBox.warning(self, "Export Error", "No valuation results to export")
            return

        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Valuation Results",
                f"{self.current_ticker.split()[0]}_valuation.xlsx",
                "Excel Files (*.xlsx)"
            )

            if not file_path:
                return

            with pd.ExcelWriter(file_path) as writer:
                # Summary metrics
                summary_data = []
                for i in range(self.metrics_table.rowCount()):
                    name_item = self.metrics_table.item(i, 0)
                    value_item = self.metrics_table.item(i, 1)
                    comment_item = self.metrics_table.item(i, 3)
                    name = name_item.text() if name_item else ""
                    value = value_item.text() if value_item else ""
                    comment = comment_item.text() if comment_item else ""
                    summary_data.append([name, value, comment])

                pd.DataFrame(summary_data, columns=["Metric", "Value", "Comment"]).to_excel(
                    writer, sheet_name="Summary", index=False
                )

                # DCF results
                if self.dcf_table.rowCount() > 0:
                    dcf_cols = ["Year", "FCF", "Growth %", "Discount Factor", "PV FCF"]
                    dcf_data = []
                    for i in range(self.dcf_table.rowCount()):
                        row_vals = []
                        for j in range(self.dcf_table.columnCount()):
                            item = self.dcf_table.item(i, j)
                            row_vals.append(item.text() if item else "")
                        dcf_data.append(row_vals)
                    pd.DataFrame(dcf_data, columns=dcf_cols).to_excel(
                        writer, sheet_name="DCF Analysis", index=False
                    )

                # Comparables
                if self.comp_table.rowCount() > 0:
                    comp_cols = ["Ticker", "Price", "P/E", "EV/EBITDA", "P/B", "P/S", "Div Yield", "Implied Value"]
                    comp_data_out = []
                    for i in range(self.comp_table.rowCount()):
                        row = []
                        for j in range(self.comp_table.columnCount()):
                            item = self.comp_table.item(i, j)
                            row.append(item.text() if item else "")
                        comp_data_out.append(row)

                    pd.DataFrame(comp_data_out, columns=comp_cols).to_excel(
                        writer, sheet_name="Comparables", index=False
                    )


                # EBITDA results
                if self.ebitda_table.rowCount() > 0:
                    ebitda_cols = ["Ticker", "EV", "EBITDA", "EV/EBITDA", "Implied EV", "Implied Price"]
                    ebitda_data = []
                    for i in range(self.ebitda_table.rowCount()):
                        row_vals = []
                        for j in range(self.ebitda_table.columnCount()):
                            item = self.ebitda_table.item(i, j)
                            row_vals.append(item.text() if item else "")
                        ebitda_data.append(row_vals)
                    pd.DataFrame(ebitda_data, columns=ebitda_cols).to_excel(
                        writer, sheet_name="EBITDA Valuation", index=False
                    )

            QMessageBox.information(self, "Export Successful", f"Results saved to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results:\n{str(e)}")
            traceback.print_exc()

    # -----------------------------
    # Placeholder methods for other valuation models
    # -----------------------------


    def run_ddm_analysis(self, tk: yf.Ticker, current_price: float):
        """Implement Dividend Discount Model analysis using improved discount rate"""
        try:
            info = getattr(tk, 'info', {}) or {}
            
            # Get dividend data
            dividend_rate = info.get('dividendRate', np.nan)
            if pd.isna(dividend_rate):
                # Try to get from dividend history
                dividends = tk.dividends
                if not dividends.empty:
                    # Get most recent annual dividend (sum of last 4 quarters)
                    recent_dividends = dividends.tail(4)
                    dividend_rate = recent_dividends.sum()
                else:
                    QMessageBox.warning(self, "Data Error", "Dividend data not available")
                    return
            
            # Use the improved discount rate calculation instead of hardcoded value
            discount_rate = self.calculate_discount_rate(tk) / 100.0  # Convert from percentage to decimal
            
            # Get growth rate from input or calculate - ensure it's reasonable
            growth_rate_input = float(self.dividend_growth.value()) / 100.0
            
            # Calculate sustainable growth rate based on fundamentals
            sustainable_growth = self.calculate_sustainable_growth_rate(tk)
            
            # Use the more conservative of input growth or sustainable growth
            growth_rate = min(growth_rate_input, sustainable_growth)
            
            # Ensure growth rate is reasonable for DDM (max 8% for stable companies)
            growth_rate = min(growth_rate, 0.08)
            
            # Final validation - growth must be at least 1% below discount rate
            if growth_rate >= discount_rate - 0.01:
                growth_rate = discount_rate - 0.02  # Ensure 2% spread for stability
            
            # For very high discount rates, use more conservative growth assumptions
            if discount_rate > 0.12:  # High risk company
                growth_rate = min(growth_rate, 0.05)  # Max 5% growth for high-risk companies
                QMessageBox.information(self, "Conservative Assumption", 
                                    f"Using conservative growth rate of {growth_rate*100:.1f}% for high-risk company")
            
            # Calculate intrinsic value using Gordon Growth Model
            intrinsic_value = dividend_rate / (discount_rate - growth_rate)
            
            # Display results
            self.price_target.setText(fmt_money(intrinsic_value, self.currency))
            upside = ((intrinsic_value - current_price) / current_price) * 100.0
            self.upside.setText(f"{upside:+.2f}%")
            self.upside.setStyleSheet(f"color: {'green' if upside >= 0 else 'red'}; font-weight: bold;")
            
            # Show the actual rates used in the calculation
            QMessageBox.information(self, "DDM Parameters", 
                                f"Discount Rate: {discount_rate*100:.2f}%\n"
                                f"Growth Rate: {growth_rate*100:.2f}%\n"
                                f"Dividend: {fmt_money(dividend_rate, self.currency)}")
            
            # Valuation range
            low_range = intrinsic_value * 0.7  # Wider range for DDM
            high_range = intrinsic_value * 1.3
            self.valuation_range.setText(f"{fmt_money(low_range, self.currency)} - {fmt_money(high_range, self.currency)}")
            
            # Recommendation
            if upside > 20:
                rec, color = ("STRONG BUY", "green")
            elif upside > 10:
                rec, color = ("BUY", "lightgreen")
            elif upside > -5:
                rec, color = ("HOLD", "gray")
            elif upside > -15:
                rec, color = ("SELL", "red")
            else:
                rec, color = ("STRONG SELL", "darkred")
            self.recommendation.setText(rec)
            self.recommendation.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px;")
            
            # Store result for final conclusion tab
            self.store_valuation_result("Dividend Discount", intrinsic_value, upside)
            
            # Populate DDM Table
            years = 5  # Show 5 years of projections
            self.ddm_table.setRowCount(years)
            
            for i in range(years):
                dividend = dividend_rate * ((1 + growth_rate) ** (i + 1))
                discount_factor = 1 / ((1 + discount_rate) ** (i + 1))
                pv_dividend = dividend * discount_factor
                
                self.ddm_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.ddm_table.setItem(i, 1, QTableWidgetItem(fmt_money(dividend, self.currency)))
                self.ddm_table.setItem(i, 2, QTableWidgetItem(fmt_percent(growth_rate * 100, 1)))
                self.ddm_table.setItem(i, 3, QTableWidgetItem(f"{discount_factor:.4f}"))
                self.ddm_table.setItem(i, 4, QTableWidgetItem(fmt_money(pv_dividend, self.currency)))
            
            # Plot DDM Results
            fig = self.ddm_plot_canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            years_proj = list(range(1, years + 1))
            dividends_proj = [dividend_rate * ((1 + growth_rate) ** i) for i in years_proj]
            
            ax.plot(years_proj, dividends_proj, 'b-', marker='o')
            ax.set_xlabel('Year')
            ax.set_ylabel('Dividend per Share')
            ax.set_title(f'Dividend Growth Projection ({growth_rate*100:.1f}% CAGR)')
            ax.grid(True)
            
            fig.tight_layout()
            self.ddm_plot_canvas.draw()
            
            # Sensitivity Analysis
            fig2 = self.ddm_sensitivity_canvas.figure
            fig2.clear()
            ax2 = fig2.add_subplot(111)
            
            # Use reasonable ranges based on the calculated discount rate
            growth_rates = np.linspace(max(growth_rate - 0.02, 0), 
                                    min(growth_rate + 0.02, discount_rate - 0.01), 5)
            discount_rates = np.linspace(max(discount_rate - 0.02, growth_rate + 0.01), 
                                        min(discount_rate + 0.02, 0.25), 5)
            
            sens_matrix = np.zeros((len(growth_rates), len(discount_rates)))
            
            for i, gr in enumerate(growth_rates):
                for j, dr in enumerate(discount_rates):
                    if dr <= gr:
                        sens_matrix[i, j] = np.nan
                    else:
                        sens_matrix[i, j] = dividend_rate / (dr - gr)
            
            im = ax2.imshow(sens_matrix, cmap='RdYlGn', aspect='auto')
            fig2.colorbar(im, ax=ax2, label='Price Target')
            ax2.set_xticks(np.arange(len(discount_rates)))
            ax2.set_xticklabels([f"{dr*100:.1f}%" for dr in discount_rates])
            ax2.set_xlabel("Discount Rate")
            ax2.set_yticks(np.arange(len(growth_rates)))
            ax2.set_yticklabels([f"{gr*100:.1f}%" for gr in growth_rates])
            ax2.set_ylabel("Growth Rate")
            ax2.set_title("DDM Price Sensitivity")
            
            for i in range(len(growth_rates)):
                for j in range(len(discount_rates)):
                    v = sens_matrix[i, j]
                    if not pd.isna(v):
                        ax2.text(j, i, f"{self.currency}{v:.1f}", ha="center", va="center", color="black")
            
            fig2.tight_layout()
            self.ddm_sensitivity_canvas.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "DDM Error", f"Error in Dividend Discount Model: {str(e)}")
            self.price_target.setText("N/A")
            self.upside.setText("N/A")
            self.valuation_range.setText("N/A")
            self.recommendation.setText("N/A")


################################################################################



    def run_rim_analysis(self, tk: yf.Ticker, current_price: float):
        """Implement Residual Income Model analysis"""
        try:
            info = getattr(tk, 'info', {}) or {}
            balance_sheet = getattr(tk, 'balance_sheet', None)
            income_stmt = getattr(tk, 'financials', None)
            
            if not isinstance(balance_sheet, pd.DataFrame) or balance_sheet.empty:
                QMessageBox.warning(self, "Data Error", "Balance sheet data not available")
                return
                
            if not isinstance(income_stmt, pd.DataFrame) or income_stmt.empty:
                QMessageBox.warning(self, "Data Error", "Income statement data not available")
                return
            
            # Get shares outstanding
            shares = info.get('sharesOutstanding', np.nan)
            if pd.isna(shares) or shares <= 0:
                # Try to calculate from market cap and current price
                market_cap = info.get('marketCap', np.nan)
                if pd.notna(market_cap) and current_price > 0:
                    shares = market_cap / current_price
                else:
                    QMessageBox.warning(self, "Data Error", "Shares outstanding data not available")
                    return
            
            # Get book value (equity)
            book_value = None
            for idx in balance_sheet.index:
                if any(term in str(idx).lower() for term in ['total equity', 'stockholders equity', 'shareholders equity']):
                    book_value = balance_sheet.loc[idx].iloc[0]  # Most recent year
                    break
            
            if book_value is None or book_value <= 0:
                QMessageBox.warning(self, "Data Error", "Book value data not available or invalid")
                return
            
            # Calculate book value per share (ensure proper scaling)
            bvps = book_value / shares
            
            # Get net income for EPS calculation
            net_income = None
            for idx in income_stmt.index:
                if 'net income' in str(idx).lower():
                    net_income = income_stmt.loc[idx].iloc[0]
                    break
            
            if net_income is None or net_income <= 0:
                QMessageBox.warning(self, "Data Error", "Net income data not available or invalid")
                return
            
            # Calculate EPS
            eps = net_income / shares
            
            # Get cost of equity
            cost_of_equity = float(self.discount_rate.value()) / 100.0
            
            # Get growth rate
            growth_rate = float(self.growth_rate.value()) / 100.0
            
            years = int(self.forecast_years.value())
            
            # Calculate residual income
            rim_table_data = []
            current_bv = bvps
            total_pv_ri = 0
            
            for year in range(1, years + 1):
                # Project earnings (apply growth rate)
                eps_proj = eps * ((1 + growth_rate) ** year)
                
                # Calculate residual income: RI = EPS - (Cost of Equity × Book Value)
                ri = eps_proj - (cost_of_equity * current_bv)
                
                # Calculate PV of residual income
                pv_factor = 1 / ((1 + cost_of_equity) ** year)
                pv_ri = ri * pv_factor
                total_pv_ri += pv_ri
                
                # Update book value for next period: BV(t) = BV(t-1) + EPS(t) - Dividends(t)
                # For simplicity, assume all earnings are retained (no dividends)
                current_bv = current_bv + eps_proj
                
                rim_table_data.append({
                    'year': year,
                    'bvps': current_bv,
                    'eps': eps_proj,
                    'cost_equity': cost_of_equity,
                    'ri': ri,
                    'pv_ri': pv_ri
                })
            
            # Terminal value - assume residual income grows at perpetual growth rate
            # Using formula: TV = RI(t+1) / (r - g) / (1 + r)^t
            terminal_ri = rim_table_data[-1]['ri'] * (1 + growth_rate)
            terminal_value = terminal_ri / (cost_of_equity - growth_rate) / ((1 + cost_of_equity) ** years)
            
            # Intrinsic value = current book value + sum of PV of residual income + PV of terminal value
            intrinsic_value = bvps + total_pv_ri + terminal_value
            
            # Display results
            self.price_target.setText(fmt_money(intrinsic_value, self.currency))
            upside = ((intrinsic_value - current_price) / current_price) * 100.0
            self.upside.setText(f"{upside:+.2f}%")
            self.upside.setStyleSheet(f"color: {'green' if upside >= 0 else 'red'}; font-weight: bold;")
            
            # Valuation range
            low_range = intrinsic_value * 0.8
            high_range = intrinsic_value * 1.2
            self.valuation_range.setText(f"{fmt_money(low_range, self.currency)} - {fmt_money(high_range, self.currency)}")
            
            # Recommendation
            if upside > 15:
                rec, color = ("STRONG BUY", "green")
            elif upside > 5:
                rec, color = ("BUY", "lightgreen")
            elif upside < -15:
                rec, color = ("STRONG SELL", "darkred")
            elif upside < -5:
                rec, color = ("SELL", "red")
            else:
                rec, color = ("HOLD", "gray")
            self.recommendation.setText(rec)
            self.recommendation.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px;")
            
            # Store result for final conclusion tab
            self.store_valuation_result("Residual Income", intrinsic_value, upside)
            
            # Populate RIM Table
            self.rim_table.setRowCount(years)
            
            for i, data in enumerate(rim_table_data):
                self.rim_table.setItem(i, 0, QTableWidgetItem(str(data['year'])))
                self.rim_table.setItem(i, 1, QTableWidgetItem(fmt_money(data['bvps'], self.currency)))
                self.rim_table.setItem(i, 2, QTableWidgetItem(fmt_money(data['eps'], self.currency)))
                self.rim_table.setItem(i, 3, QTableWidgetItem(fmt_percent(data['cost_equity'] * 100, 1)))
                self.rim_table.setItem(i, 4, QTableWidgetItem(fmt_money(data['ri'], self.currency)))
                self.rim_table.setItem(i, 5, QTableWidgetItem(fmt_money(data['pv_ri'], self.currency)))
            
            # Add terminal value row
            self.rim_table.setRowCount(years + 1)
            self.rim_table.setItem(years, 0, QTableWidgetItem("Terminal"))
            self.rim_table.setItem(years, 1, QTableWidgetItem("N/A"))
            self.rim_table.setItem(years, 2, QTableWidgetItem("N/A"))
            self.rim_table.setItem(years, 3, QTableWidgetItem("N/A"))
            self.rim_table.setItem(years, 4, QTableWidgetItem(fmt_money(terminal_ri, self.currency)))
            self.rim_table.setItem(years, 5, QTableWidgetItem(fmt_money(terminal_value, self.currency)))
            
            # Plot RIM Results
            fig = self.rim_plot_canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            years_plot = [data['year'] for data in rim_table_data] + [years + 1]
            ri_values = [data['ri'] for data in rim_table_data] + [terminal_ri]
            
            bars = ax.bar(years_plot, ri_values)
            ax.set_xlabel('Year')
            ax.set_ylabel('Residual Income')
            ax.set_title('Residual Income Projection')
            ax.grid(True)
            
            # Color terminal value differently
            if len(bars) > 0:
                bars[-1].set_color('orange')
            
            for i, v in enumerate(ri_values):
                ax.text(i + 1, v, fmt_money(v, self.currency, allow_sign=False), ha='center', va='bottom')
            
            fig.tight_layout()
            self.rim_plot_canvas.draw()
            
        except Exception as e:
            QMessageBox.warning(self, "RIM Error", f"Error in Residual Income Model: {str(e)}")
            traceback.print_exc()
            self.price_target.setText("N/A")
            self.upside.setText("N/A")
            self.valuation_range.setText("N/A")
            self.recommendation.setText("N/A")


################################################################################


    def run_graham_analysis(self, tk: yf.Ticker, current_price: float):
        """Implement Graham Formula analysis"""
        try:
            info = getattr(tk, 'info', {}) or {}
            
            # Get EPS (TTM)
            eps = info.get('trailingEps', np.nan)
            if pd.isna(eps):
                # Try to calculate from financials
                income_stmt = getattr(tk, 'financials', None)
                if isinstance(income_stmt, pd.DataFrame) and not income_stmt.empty:
                    net_income = None
                    for idx in income_stmt.index:
                        if 'net income' in str(idx).lower():
                            net_income = income_stmt.loc[idx].iloc[0]
                            break
                    
                    if net_income is not None:
                        shares = info.get('sharesOutstanding', np.nan)
                        if not pd.isna(shares) and shares > 0:
                            eps = net_income / shares
            
            if pd.isna(eps) or eps <= 0:
                QMessageBox.warning(self, "Data Error", "EPS data not available or invalid")
                return
            
            # Get Book Value per Share
            bvps = info.get('bookValue', np.nan)
            if pd.isna(bvps):
                # Try to calculate from balance sheet
                balance_sheet = getattr(tk, 'balance_sheet', None)
                if isinstance(balance_sheet, pd.DataFrame) and not balance_sheet.empty:
                    equity = None
                    for idx in balance_sheet.index:
                        if any(term in str(idx).lower() for term in ['total equity', 'stockholders equity', 'shareholders equity']):
                            equity = balance_sheet.loc[idx].iloc[0]
                            break
                    
                    if equity is not None:
                        shares = info.get('sharesOutstanding', np.nan)
                        if not pd.isna(shares) and shares > 0:
                            bvps = equity / shares
            
            if pd.isna(bvps) or bvps <= 0:
                QMessageBox.warning(self, "Data Error", "Book value per share data not available or invalid")
                return
            
            # Update display with actual values
            self.graham_eps.setText(fmt_money(eps, self.currency))
            self.graham_bvps.setText(fmt_money(bvps, self.currency))


            # Inputs are in percent (e.g., 7.5, 4.0)
            g_pct = float(self.earnings_growth.value())
            aaa_pct = max(0.1, float(self.aaa_yield.value()))  # avoid div by zero

            # Calculate intrinsic value using both Graham formulas
            # Original formula: √(22.5 × EPS × BVPS)
            intrinsic_original = (22.5 * eps * bvps) ** 0.5
            
            # Modified formula: EPS × (8.5 + 2*g_pct) × (4.4 / AAA%)
            intrinsic_modified = eps * (8.5 + 2 * g_pct) * (4.4 / aaa_pct)
            
            # Use the average of both methods
            intrinsic_value = (intrinsic_original + intrinsic_modified) / 2
            
            # Display results
            self.graham_intrinsic.setText(fmt_money(intrinsic_value, self.currency))
            
            margin_of_safety = ((intrinsic_value - current_price) / intrinsic_value) * 100.0
            self.graham_margin.setText(fmt_percent(margin_of_safety, 1))
            
            # Also update main valuation display
            self.price_target.setText(fmt_money(intrinsic_value, self.currency))
            upside = ((intrinsic_value - current_price) / current_price) * 100.0
            self.upside.setText(f"{upside:+.2f}%")
            self.store_valuation_result("Graham Formula", intrinsic_value, upside)

            self.upside.setStyleSheet(f"color: {'green' if upside >= 0 else 'red'}; font-weight: bold;")
            
            # Valuation range
            low_range = intrinsic_value * 0.7  # Wider range for Graham formula
            high_range = intrinsic_value * 1.3
            self.valuation_range.setText(f"{fmt_money(low_range, self.currency)} - {fmt_money(high_range, self.currency)}")
            
            # Recommendation based on margin of safety
            if margin_of_safety > 30:
                rec, color = ("STRONG BUY", "green")
            elif margin_of_safety > 15:
                rec, color = ("BUY", "lightgreen")
            elif margin_of_safety < -30:
                rec, color = ("STRONG SELL", "darkred")
            elif margin_of_safety < -15:
                rec, color = ("SELL", "red")
            else:
                rec, color = ("HOLD", "gray")
            self.recommendation.setText(rec)
            self.recommendation.setStyleSheet(f"background-color: {color}; color: white; border-radius: 5px;")
            
        except Exception as e:
            QMessageBox.warning(self, "Graham Error", f"Error in Graham Formula: {str(e)}")
            self.price_target.setText("N/A")
            self.upside.setText("N/A")
            self.valuation_range.setText("N/A")
            self.recommendation.setText("N/A")
            self.graham_intrinsic.setText("N/A")
            self.graham_margin.setText("N/A")
            self.store_valuation_result("Graham Formula", intrinsic_value, upside)



################################################################################


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = StockValuationDialog()
    dlg.show()
    sys.exit(app.exec_())