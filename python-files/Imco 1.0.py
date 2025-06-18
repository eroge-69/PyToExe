import subprocess
import sys
import os
import shutil
import tempfile
import uuid
import winreg
import ctypes
import psutil
import platform
import hashlib
import json
import time
import threading
import queue
import socket
import ssl
import datetime
import logging
import configparser
import webbrowser
import zipfile
import pickle
import zlib
import statistics
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional, Any
from datetime import timedelta

# Install required packages
def install_package(package_name: str, import_name: str = None):
    """
    Try to import the package, and if fails, install it using pip.
    'package_name' is the PyPI name, 'import_name' is the module name to import if different.
    """
    import_name = import_name or package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"Package '{package_name}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# List all third-party PyPI packages your script depends on.
required_packages = [
    ("numpy", None),
    ("pandas", None),
    ("matplotlib", None),
    ("ibapi", None),
    ("psutil", None),
    ("scipy", None),  # For portfolio optimization
    ("pyinstaller", None),  # For creating executables
    ("requests", None),  # For web requests
    ("mplfinance", None),  # For candlestick charts
    ("seaborn", None),  # For enhanced visualizations
    ("cvxpy", None),  # For convex optimization (portfolio optimization)
    ("pyportfolioopt", None),  # Portfolio optimization library
    ("arch", None),  # For GARCH models (VaR calculation)
]

for package_name, import_name in required_packages:
    install_package(package_name, import_name)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import norm, t
from arch import arch_model
from pypfopt import expected_returns, risk_models, EfficientFrontier, objective_functions
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract, ContractDetails
from ibapi.execution import Execution
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.common import *
from ibapi.ticktype import *

# Constants
VERSION = "2.0.0"
COMPANY_NAME = "Advanced Trading Solutions"
APP_NAME = "Institutional Trading Pro"
SUPPORT_EMAIL = "support@advancedtrading.com"
WEBSITE_URL = "https://www.advancedtrading.com"
LICENSE_URL = f"{WEBSITE_URL}/license"
UPDATE_URL = f"{WEBSITE_URL}/api/check-update"
REGISTRY_KEY = f"Software\\{COMPANY_NAME}\\{APP_NAME}"
DEFAULT_DOWNLOAD_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')
INSTALL_DIR = os.path.join(os.environ['PROGRAMFILES'], COMPANY_NAME, APP_NAME)
START_MENU_DIR = os.path.join(os.environ['APPDATA'], "Microsoft", "Windows", "Start Menu", "Programs", COMPANY_NAME)
DESKTOP_SHORTCUT = os.path.join(os.environ['USERPROFILE'], 'Desktop', f"{APP_NAME}.lnk")

# Configure logging
log_dir = os.path.join(os.environ['LOCALAPPDATA'], COMPANY_NAME, APP_NAME, 'Logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"{APP_NAME}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Exception classes
class TradingSystemError(Exception):
    """Base exception class for trading system errors"""
    pass

class InstallationError(TradingSystemError):
    """Exception raised during installation"""
    pass

class IBKRConnectionError(TradingSystemError):
    """Exception raised for IBKR connection issues"""
    pass

class OrderExecutionError(TradingSystemError):
    """Exception raised for order execution failures"""
    pass

class SlippageExceededError(OrderExecutionError):
    """Exception raised when slippage exceeds maximum allowed"""
    pass

class PortfolioAnalysisError(TradingSystemError):
    """Exception raised for portfolio analysis failures"""
    pass

# Portfolio Analysis Engine
class PortfolioAnalyzer:
    def __init__(self, returns_data: pd.DataFrame = None):
        """
        Initialize portfolio analyzer with returns data.
        
        Args:
            returns_data: DataFrame with datetime index and asset returns in columns
        """
        self.returns = returns_data
        self.portfolio_weights = None
        self.benchmark_returns = None
        self.risk_free_rate = 0.0  # Can be updated
    
    def set_returns_data(self, returns_data: pd.DataFrame):
        """Set or update returns data"""
        self.returns = returns_data
    
    def set_benchmark(self, benchmark_returns: pd.Series):
        """Set benchmark returns series"""
        self.benchmark_returns = benchmark_returns
    
    def set_risk_free_rate(self, rate: float):
        """Set annual risk-free rate (e.g., 0.02 for 2%)"""
        self.risk_free_rate = rate
    
    def calculate_basic_metrics(self, weights: dict = None) -> dict:
        """
        Calculate basic portfolio metrics.
        
        Args:
            weights: Dictionary of {asset: weight} pairs. If None, assumes equal weights.
        
        Returns:
            Dictionary of portfolio metrics
        """
        if self.returns is None:
            raise PortfolioAnalysisError("No returns data available")
        
        if weights is None:
            # Equal weighting if not specified
            weights = {col: 1/len(self.returns.columns) for col in self.returns.columns}
        
        self.portfolio_weights = pd.Series(weights)
        
        # Portfolio returns
        portfolio_returns = (self.returns * self.portfolio_weights).sum(axis=1)
        
        # Calculate metrics
        metrics = {
            'annual_return': self._annualize_return(portfolio_returns),
            'annual_volatility': self._annualize_volatility(portfolio_returns),
            'sharpe_ratio': self._calculate_sharpe(portfolio_returns),
            'sortino_ratio': self._calculate_sortino(portfolio_returns),
            'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
            'value_at_risk': self._calculate_var(portfolio_returns),
            'conditional_var': self._calculate_cvar(portfolio_returns),
            'beta': self._calculate_beta(portfolio_returns) if self.benchmark_returns is not None else None,
            'alpha': self._calculate_alpha(portfolio_returns) if self.benchmark_returns is not None else None,
            'information_ratio': self._calculate_information_ratio(portfolio_returns) if self.benchmark_returns is not None else None,
            'tail_ratio': self._calculate_tail_ratio(portfolio_returns),
            'common_sense_ratio': self._calculate_common_sense_ratio(portfolio_returns),
            'omega_ratio': self._calculate_omega_ratio(portfolio_returns),
            'skewness': portfolio_returns.skew(),
            'kurtosis': portfolio_returns.kurtosis(),
            'positive_periods': len(portfolio_returns[portfolio_returns > 0]) / len(portfolio_returns),
            'negative_periods': len(portfolio_returns[portfolio_returns < 0]) / len(portfolio_returns),
        }
        
        return metrics
    
    def optimize_portfolio(self, objective: str = 'max_sharpe', constraints: dict = None) -> dict:
        """
        Optimize portfolio weights using PyPortfolioOpt.
        
        Args:
            objective: Optimization objective ('max_sharpe', 'min_volatility', 'max_sortino', 'efficient_risk', 'efficient_return')
            constraints: Dictionary of constraints (e.g., {'weight_bounds': (0, 1)})
        
        Returns:
            Dictionary containing:
                - optimized_weights
                - performance_metrics
                - efficient_frontier_data
        """
        try:
            # Calculate expected returns and covariance matrix
            mu = expected_returns.mean_historical_return(self.returns)
            S = risk_models.sample_cov(self.returns)
            
            # Create Efficient Frontier object
            ef = EfficientFrontier(mu, S)
            
            # Add constraints if provided
            if constraints:
                if 'weight_bounds' in constraints:
                    ef.add_constraint(lambda w: w >= constraints['weight_bounds'][0])
                    ef.add_constraint(lambda w: w <= constraints['weight_bounds'][1])
                
                if 'sector_constraints' in constraints:
                    for sector, bounds in constraints['sector_constraints'].items():
                        ef.add_sector_constraints(bounds['lower'], bounds['upper'], bounds['sector_mapper'])
            
            # Optimize based on objective
            if objective == 'max_sharpe':
                ef.max_sharpe()
            elif objective == 'min_volatility':
                ef.min_volatility()
            elif objective == 'max_sortino':
                ef.max_quadratic_utility(risk_aversion=1)
                ef.add_objective(objective_functions.L2_reg)
            elif objective == 'efficient_risk':
                ef.efficient_risk(target_volatility=constraints.get('target_volatility', 0.2))
            elif objective == 'efficient_return':
                ef.efficient_return(target_return=constraints.get('target_return', 0.1))
            else:
                raise PortfolioAnalysisError(f"Unknown optimization objective: {objective}")
            
            # Get clean weights
            cleaned_weights = ef.clean_weights()
            
            # Get performance metrics
            perf = ef.portfolio_performance(verbose=True)
            
            # Get efficient frontier data
            ef_data = self._calculate_efficient_frontier(ef)
            
            return {
                'optimized_weights': cleaned_weights,
                'performance_metrics': {
                    'expected_return': perf[0],
                    'volatility': perf[1],
                    'sharpe_ratio': perf[2]
                },
                'efficient_frontier_data': ef_data
            }
        except Exception as e:
            raise PortfolioAnalysisError(f"Portfolio optimization failed: {str(e)}")
    
    def calculate_risk_contribution(self, weights: dict) -> dict:
        """
        Calculate risk contribution of each asset.
        
        Args:
            weights: Dictionary of {asset: weight} pairs
        
        Returns:
            Dictionary of risk contributions
        """
        try:
            cov_matrix = self.returns.cov()
            portfolio_variance = np.dot(np.dot(np.array(list(weights.values())), cov_matrix), np.array(list(weights.values())))
            
            risk_contributions = {}
            for asset in weights:
                marginal_contribution = np.dot(cov_matrix.loc[asset], np.array(list(weights.values())))
                risk_contributions[asset] = weights[asset] * marginal_contribution / portfolio_variance
            
            return risk_contributions
        except Exception as e:
            raise PortfolioAnalysisError(f"Risk contribution calculation failed: {str(e)}")
    
    def calculate_var_through_time(self, window: int = 63, alpha: float = 0.05) -> pd.DataFrame:
        """
        Calculate rolling Value at Risk.
        
        Args:
            window: Rolling window size in periods
            alpha: Confidence level (e.g., 0.05 for 95% VaR)
        
        Returns:
            DataFrame with rolling VaR
        """
        if self.returns is None:
            raise PortfolioAnalysisError("No returns data available")
        
        try:
            rolling_var = pd.DataFrame(index=self.returns.index)
            
            # Parametric (Gaussian) VaR
            rolling_var['parametric'] = self.returns.rolling(window).apply(
                lambda x: -x.mean() + x.std() * norm.ppf(alpha)
            ).sum(axis=1)
            
            # Historical VaR
            rolling_var['historical'] = self.returns.rolling(window).apply(
                lambda x: -np.percentile(x, alpha * 100)
            ).sum(axis=1)
            
            # EWMA VaR
            rolling_var['ewma'] = self._calculate_ewma_var(window, alpha)
            
            # GARCH VaR
            rolling_var['garch'] = self._calculate_garch_var(window, alpha)
            
            return rolling_var
        except Exception as e:
            raise PortfolioAnalysisError(f"Rolling VaR calculation failed: {str(e)}")
    
    def _calculate_efficient_frontier(self, ef: EfficientFrontier, points: int = 20) -> dict:
        """Calculate efficient frontier data points"""
        try:
            # Get range of target returns
            min_ret = ef.expected_returns.min()
            max_ret = ef.expected_returns.max()
            target_rets = np.linspace(min_ret, max_ret, points)
            
            # Calculate efficient frontier
            ef_data = {'returns': [], 'volatility': []}
            for ret in target_rets:
                try:
                    ef.efficient_return(target_return=ret)
                    _, vol, _ = ef.portfolio_performance()
                    ef_data['returns'].append(ret)
                    ef_data['volatility'].append(vol)
                except:
                    continue
            
            return ef_data
        except Exception as e:
            raise PortfolioAnalysisError(f"Efficient frontier calculation failed: {str(e)}")
    
    def _calculate_ewma_var(self, window: int, alpha: float) -> pd.Series:
        """Calculate EWMA VaR"""
        lambda_ = 0.94  # Decay factor
        ewma_var = pd.Series(index=self.returns.index)
        
        for i in range(window, len(self.returns)):
            # Calculate EWMA variance
            weights = np.array([(1 - lambda_) * lambda_**k for k in range(window)][::-1])
            weighted_returns = self.returns.iloc[i-window:i] * weights[:, None]
            ewma_std = np.sqrt(np.sum(weighted_returns**2) / np.sum(weights))
            
            # Calculate VaR
            ewma_var.iloc[i] = -ewma_std * norm.ppf(alpha)
        
        return ewma_var
    
    def _calculate_garch_var(self, window: int, alpha: float) -> pd.Series:
        """Calculate GARCH VaR"""
        garch_var = pd.Series(index=self.returns.index)
        
        for i in range(window, len(self.returns)):
            try:
                # Fit GARCH(1,1) model
                model = arch_model(self.returns.iloc[i-window:i], vol='Garch', p=1, q=1)
                res = model.fit(disp='off')
                
                # Forecast next period volatility
                forecast = res.forecast(horizon=1)
                pred_vol = np.sqrt(forecast.variance.iloc[-1, 0])
                
                # Calculate VaR
                garch_var.iloc[i] = -pred_vol * norm.ppf(alpha)
            except:
                garch_var.iloc[i] = np.nan
        
        return garch_var
    
    def _annualize_return(self, returns: pd.Series) -> float:
        """Annualize return series"""
        return np.prod(1 + returns) ** (252 / len(returns)) - 1
    
    def _annualize_volatility(self, returns: pd.Series) -> float:
        """Annualize volatility series"""
        return returns.std() * np.sqrt(252)
    
    def _calculate_sharpe(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - self.risk_free_rate / 252
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    def _calculate_sortino(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio"""
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return np.nan
        downside_risk = downside_returns.std() * np.sqrt(252)
        excess_return = self._annualize_return(returns) - self.risk_free_rate
        return excess_return / downside_risk
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        peak = cumulative.expanding(min_periods=1).max()
        drawdown = (cumulative - peak) / peak
        return drawdown.min()
    
    def _calculate_var(self, returns: pd.Series, alpha: float = 0.05) -> float:
        """Calculate Value at Risk"""
        return -np.percentile(returns, alpha * 100)
    
    def _calculate_cvar(self, returns: pd.Series, alpha: float = 0.05) -> float:
        """Calculate Conditional Value at Risk"""
        var = self._calculate_var(returns, alpha)
        return -returns[returns <= -var].mean()
    
    def _calculate_beta(self, portfolio_returns: pd.Series) -> float:
        """Calculate portfolio beta to benchmark"""
        cov = np.cov(portfolio_returns, self.benchmark_returns)
        return cov[0, 1] / cov[1, 1]
    
    def _calculate_alpha(self, portfolio_returns: pd.Series) -> float:
        """Calculate portfolio alpha"""
        beta = self._calculate_beta(portfolio_returns)
        portfolio_excess = self._annualize_return(portfolio_returns) - self.risk_free_rate
        benchmark_excess = self._annualize_return(self.benchmark_returns) - self.risk_free_rate
        return portfolio_excess - beta * benchmark_excess
    
    def _calculate_information_ratio(self, portfolio_returns: pd.Series) -> float:
        """Calculate information ratio"""
        active_returns = portfolio_returns - self.benchmark_returns
        return active_returns.mean() / active_returns.std() * np.sqrt(252)
    
    def _calculate_tail_ratio(self, returns: pd.Series) -> float:
        """Calculate tail ratio (right tail / left tail)"""
        right_tail = np.percentile(returns, 95)
        left_tail = abs(np.percentile(returns, 5))
        return right_tail / left_tail
    
    def _calculate_common_sense_ratio(self, returns: pd.Series) -> float:
        """Calculate common sense ratio (gain / pain)"""
        gains = returns[returns > 0].sum()
        pain = abs(returns[returns < 0].sum())
        return gains / pain if pain != 0 else np.nan
    
    def _calculate_omega_ratio(self, returns: pd.Series, threshold: float = 0.0) -> float:
        """Calculate Omega ratio"""
        excess_returns = returns - threshold
        upside = excess_returns[excess_returns > 0].sum()
        downside = abs(excess_returns[excess_returns < 0].sum())
        return upside / downside if downside != 0 else np.nan

# IBKR API Wrapper
class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.next_valid_id = None
        self.connected = False
        self._req_id_queue = queue.Queue()
        self._order_status_queue = queue.Queue()
        self._execution_data = {}
        self._market_data = {}
        self._historical_data = {}
        self._account_data = {}
        self._portfolio_positions = []
        self._contract_details = {}
        self._error_messages = []
        self._open_orders = []
        self._completed_orders = []
        self._news_bulletins = []
        self._volume_profile = defaultdict(list)
        self._vwap_data = {}
        self._poc_data = {}

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        if errorCode == 502:  # Could not connect to TWS
            self.connected = False
        self._error_messages.append((reqId, errorCode, errorString))
        logger.error(f"IBKR Error - ReqId: {reqId}, Code: {errorCode}, Msg: {errorString}")

    def connectAck(self):
        super().connectAck()
        if self.async_connect:
            self.startApi()

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.next_valid_id = orderId
        self._req_id_queue.put(orderId)

    def orderStatus(self, orderId: OrderId, status: str, filled: float,
                   remaining: float, avgFillPrice: float, permId: int,
                   parentId: int, lastFillPrice: float, clientId: int,
                   whyHeld: str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice,
                          permId, parentId, lastFillPrice, clientId, whyHeld,
                          mktCapPrice)
        self._order_status_queue.put({
            'orderId': orderId,
            'status': status,
            'filled': filled,
            'remaining': remaining,
            'avgFillPrice': avgFillPrice,
            'lastFillPrice': lastFillPrice,
            'whyHeld': whyHeld
        })

    def execDetails(self, reqId: int, contract: Contract, execution: Execution):
        super().execDetails(reqId, contract, execution)
        if reqId not in self._execution_data:
            self._execution_data[reqId] = []
        self._execution_data[reqId].append({
            'contract': contract,
            'execution': execution
        })

    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float,
                  attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        if reqId not in self._market_data:
            self._market_data[reqId] = {}
        self._market_data[reqId][tickType] = price

    def tickSize(self, reqId: TickerId, tickType: TickType, size: int):
        super().tickSize(reqId, tickType, size)
        if reqId not in self._market_data:
            self._market_data[reqId] = {}
        self._market_data[reqId][tickType] = size

    def tickString(self, reqId: TickerId, tickType: TickType, value: str):
        super().tickString(reqId, tickType, value)
        if tickType == TickTypeEnum.LAST_TIMESTAMP:
            if reqId not in self._market_data:
                self._market_data[reqId] = {}
            self._market_data[reqId][tickType] = value

    def historicalData(self, reqId: int, bar: BarData):
        super().historicalData(reqId, bar)
        if reqId not in self._historical_data:
            self._historical_data[reqId] = []
        self._historical_data[reqId].append(bar)

    def historicalDataUpdate(self, reqId: int, bar: BarData):
        super().historicalDataUpdate(reqId, bar)
        if reqId not in self._historical_data:
            self._historical_data[reqId] = []
        self._historical_data[reqId].append(bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        logger.info(f"Historical data received for reqId: {reqId}")

    def updatePortfolio(self, contract: Contract, position: float,
                       marketPrice: float, marketValue: float,
                       averageCost: float, unrealizedPNL: float,
                       realizedPNL: float, accountName: str):
        super().updatePortfolio(contract, position, marketPrice, marketValue,
                              averageCost, unrealizedPNL, realizedPNL, accountName)
        self._portfolio_positions.append({
            'contract': contract,
            'position': position,
            'marketPrice': marketPrice,
            'marketValue': marketValue,
            'averageCost': averageCost,
            'unrealizedPNL': unrealizedPNL,
            'realizedPNL': realizedPNL,
            'accountName': accountName
        })

    def accountSummary(self, reqId: int, account: str, tag: str, value: str,
                       currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        if account not in self._account_data:
            self._account_data[account] = {}
        self._account_data[account][tag] = value

    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        super().contractDetails(reqId, contractDetails)
        self._contract_details[reqId] = contractDetails

    def openOrder(self, orderId: OrderId, contract: Contract, order: Order,
                  orderState: OrderState):
        super().openOrder(orderId, contract, order, orderState)
        self._open_orders.append({
            'orderId': orderId,
            'contract': contract,
            'order': order,
            'orderState': orderState
        })

    def openOrderEnd(self):
        super().openOrderEnd()
        logger.info("All open orders received")

    def completedOrder(self, contract: Contract, order: Order, orderState: OrderState):
        super().completedOrder(contract, order, orderState)
        self._completed_orders.append({
            'contract': contract,
            'order': order,
            'orderState': orderState
        })

    def completedOrdersEnd(self):
        super().completedOrdersEnd()
        logger.info("All completed orders received")

    def updateNewsBulletin(self, msgId: int, msgType: int, newsMessage: str,
                           originExch: str):
        super().updateNewsBulletin(msgId, msgType, newsMessage, originExch)
        self._news_bulletins.append({
            'msgId': msgId,
            'msgType': msgType,
            'newsMessage': newsMessage,
            'originExch': originExch
        })

    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float,
                         size: int, tickAttribLast: TickAttribLast, exchange: str,
                         specialConditions: str):
        super().tickByTickAllLast(reqId, tickType, time, price, size, tickAttribLast,
                                exchange, specialConditions)
        # Update volume profile
        self._volume_profile[price].append(size)
        
        # Update VWAP data
        if reqId not in self._vwap_data:
            self._vwap_data[reqId] = {
                'cumulative_price_volume': 0.0,
                'cumulative_volume': 0
            }
        self._vwap_data[reqId]['cumulative_price_volume'] += price * size
        self._vwap_data[reqId]['cumulative_volume'] += size

    def calculate_vwap(self, reqId: int) -> float:
        if reqId in self._vwap_data and self._vwap_data[reqId]['cumulative_volume'] > 0:
            return self._vwap_data[reqId]['cumulative_price_volume'] / self._vwap_data[reqId]['cumulative_volume']
        return 0.0

    def calculate_poc(self, reqId: int) -> Tuple[float, int]:
        if not self._volume_profile:
            return (0.0, 0)
        
        max_volume_price = max(self._volume_profile.items(), key=lambda x: sum(x[1]))[0]
        total_volume = sum(self._volume_profile[max_volume_price])
        return (max_volume_price, total_volume)

# Trading Engine
class TradingEngine:
    def __init__(self, ib_api: IBApi):
        self.ib = ib_api
        self._active_orders = {}
        self._order_history = []
        self._position_tracker = {}
        self._slippage_tracker = {}
        self._execution_algorithms = {
            'VWAP': self._execute_vwap,
            'TWAP': self._execute_twap,
            'POC': self._execute_poc,
            'HYBRID': self._execute_hybrid,
            'AGGRESSIVE': self._execute_aggressive
        }
        self._market_conditions = {}
        self._risk_parameters = {
            'max_slippage_percent': 0.5,
            'max_position_size': 10000,
            'max_order_size': 5000,
            'daily_loss_limit': -5000
        }
        self._performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_slippage': 0.0,
            'total_slippage': 0.0,
            'total_commission': 0.0
        }

    def connect_to_ibkr(self, host: str = '127.0.0.1', port: int = 7497, client_id: int = 1) -> bool:
        """Connect to IBKR TWS/Gateway"""
        try:
            self.ib.connect(host, port, clientId=client_id)
            
            # Wait for connection to be established
            start_time = time.time()
            while not self.ib.connected and (time.time() - start_time) < 10:
                time.sleep(0.1)
            
            if not self.ib.connected:
                raise IBKRConnectionError("Failed to connect to IBKR within timeout period")
            
            logger.info("Successfully connected to IBKR API")
            return True
        except Exception as e:
            logger.error(f"Error connecting to IBKR: {str(e)}")
            raise IBKRConnectionError(f"Failed to connect to IBKR: {str(e)}")

    def disconnect_from_ibkr(self):
        """Disconnect from IBKR TWS/Gateway"""
        try:
            if self.ib.connected:
                self.ib.disconnect()
                logger.info("Disconnected from IBKR API")
        except Exception as e:
            logger.error(f"Error disconnecting from IBKR: {str(e)}")

    def place_order(self, contract: Contract, order: Order) -> int:
        """Place an order through IBKR API"""
        try:
            if not self.ib.connected:
                raise IBKRConnectionError("Not connected to IBKR")
            
            # Get next valid order ID
            order_id = self.ib._req_id_queue.get(timeout=10)
            
            # Place the order
            self.ib.placeOrder(order_id, contract, order)
            
            # Track the order
            self._active_orders[order_id] = {
                'contract': contract,
                'order': order,
                'status': 'SUBMITTED',
                'timestamp': datetime.datetime.now(),
                'fills': [],
                'slippage': 0.0
            }
            
            logger.info(f"Order placed - ID: {order_id}, Symbol: {contract.symbol}, "
                       f"Action: {order.action}, Quantity: {order.totalQuantity}, "
                       f"Type: {order.orderType}, Price: {order.lmtPrice if order.lmtPrice else 'MARKET'}")
            
            return order_id
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            raise OrderExecutionError(f"Failed to place order: {str(e)}")

    def execute_smart_order(self, contract: Contract, quantity: int, 
                          direction: str, max_slippage: float = 0.5,
                          time_frame: str = '1H', strategy: str = 'HYBRID') -> Dict:
        """
        Execute an order using smart routing to minimize slippage
        
        Args:
            contract: IBKR contract object
            quantity: Number of shares/contracts to trade
            direction: 'BUY' or 'SELL'
            max_slippage: Maximum allowed slippage percentage
            time_frame: Time frame for execution ('1M', '5M', '1H', '1D')
            strategy: Execution strategy ('VWAP', 'TWAP', 'POC', 'HYBRID', 'AGGRESSIVE')
        
        Returns:
            Dictionary with order execution details
        """
        try:
            # Validate inputs
            if direction.upper() not in ['BUY', 'SELL']:
                raise ValueError("Direction must be 'BUY' or 'SELL'")
            
            if strategy.upper() not in self._execution_algorithms:
                raise ValueError(f"Invalid strategy. Must be one of: {list(self._execution_algorithms.keys())}")
            
            # Check market conditions
            self._update_market_conditions(contract)
            
            # Check risk parameters
            self._check_risk_parameters(contract, quantity, direction)
            
            # Execute using selected strategy
            execution_func = self._execution_algorithms[strategy.upper()]
            result = execution_func(contract, quantity, direction, max_slippage, time_frame)
            
            # Update performance metrics
            self._update_performance_metrics(result)
            
            return result
        except Exception as e:
            logger.error(f"Error executing smart order: {str(e)}")
            raise OrderExecutionError(f"Failed to execute smart order: {str(e)}")

    def _execute_vwap(self, contract: Contract, quantity: int, 
                     direction: str, max_slippage: float, 
                     time_frame: str) -> Dict:
        """Execute order using VWAP strategy"""
        # Get historical VWAP data
        self.ib.reqHistoricalData(
            reqId=self.ib.next_valid_id,
            contract=contract,
            endDateTime="",
            durationStr=time_frame,
            barSizeSetting="1 min",
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
            keepUpToDate=True,
            chartOptions=[]
        )
        
        # Wait for data
        time.sleep(2)  # In production, use proper synchronization
        
        # Calculate current VWAP
        vwap = self.ib.calculate_vwap(self.ib.next_valid_id - 1)
        
        # Create VWAP order
        order = Order()
        order.action = direction.upper()
        order.totalQuantity = quantity
        order.orderType = 'VWAP'
        order.tif = 'DAY'
        
        # Place order
        order_id = self.place_order(contract, order)
        
        # Monitor execution
        execution_details = self._monitor_order_execution(order_id, max_slippage)
        
        return {
            'strategy': 'VWAP',
            'order_id': order_id,
            'vwap_price': vwap,
            'execution_details': execution_details
        }

    def _execute_twap(self, contract: Contract, quantity: int, 
                     direction: str, max_slippage: float, 
                     time_frame: str) -> Dict:
        """Execute order using TWAP strategy"""
        # Parse time frame
        if time_frame.endswith('M'):
            minutes = int(time_frame[:-1])
            duration = timedelta(minutes=minutes)
        elif time_frame.endswith('H'):
            hours = int(time_frame[:-1])
            duration = timedelta(hours=hours)
        elif time_frame.endswith('D'):
            days = int(time_frame[:-1])
            duration = timedelta(days=days)
        else:
            duration = timedelta(hours=1)  # Default to 1 hour
        
        # Calculate number of slices (1 slice per minute)
        num_slices = int(duration.total_seconds() / 60)
        slice_qty = max(1, quantity // num_slices)
        
        # Place parent order
        parent_order = Order()
        parent_order.action = direction.upper()
        parent_order.totalQuantity = quantity
        parent_order.orderType = 'LMT'
        parent_order.tif = 'GTC'
        parent_order.transmit = False
        
        parent_id = self.place_order(contract, parent_order)
        
        # Place child orders as TWAP slices
        for i in range(num_slices):
            slice_order = Order()
            slice_order.action = direction.upper()
            slice_order.totalQuantity = slice_qty
            slice_order.orderType = 'LMT'
            slice_order.tif = 'IOC'
            slice_order.parentId = parent_id
            slice_order.transmit = (i == num_slices - 1)
            
            # Schedule slice to execute at appropriate time
            execute_time = datetime.datetime.now() + timedelta(minutes=i)
            self._schedule_order(contract, slice_order, execute_time)
        
        # Monitor execution
        execution_details = self._monitor_order_execution(parent_id, max_slippage)
        
        return {
            'strategy': 'TWAP',
            'order_id': parent_id,
            'time_frame': time_frame,
            'num_slices': num_slices,
            'execution_details': execution_details
        }

    def _execute_poc(self, contract: Contract, quantity: int, 
                    direction: str, max_slippage: float, 
                    time_frame: str) -> Dict:
        """Execute order using Point of Control (POC) strategy"""
        # Get volume profile data
        self.ib.reqHistoricalData(
            reqId=self.ib.next_valid_id,
            contract=contract,
            endDateTime="",
            durationStr=time_frame,
            barSizeSetting="1 min",
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
            keepUpToDate=True,
            chartOptions=[]
        )
        
        # Wait for data
        time.sleep(2)  # In production, use proper synchronization
        
        # Calculate POC
        poc_price, poc_volume = self.ib.calculate_poc(self.ib.next_valid_id - 1)
        
        # Create POC order
        order = Order()
        order.action = direction.upper()
        order.totalQuantity = quantity
        order.orderType = 'LMT'
        order.lmtPrice = poc_price
        order.tif = 'DAY'
        
        # Place order
        order_id = self.place_order(contract, order)
        
        # Monitor execution
        execution_details = self._monitor_order_execution(order_id, max_slippage)
        
        return {
            'strategy': 'POC',
            'order_id': order_id,
            'poc_price': poc_price,
            'poc_volume': poc_volume,
            'execution_details': execution_details
        }

    def _execute_hybrid(self, contract: Contract, quantity: int, 
                       direction: str, max_slippage: float, 
                       time_frame: str) -> Dict:
        """Execute order using hybrid VWAP/POC strategy"""
        # Get market data
        self.ib.reqMarketDataType(1)  # Live data
        self.ib.reqMktData(self.ib.next_valid_id, contract, "", False, False, [])
        
        # Get historical data for VWAP/POC
        self.ib.reqHistoricalData(
            reqId=self.ib.next_valid_id + 1,
            contract=contract,
            endDateTime="",
            durationStr=time_frame,
            barSizeSetting="1 min",
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
            keepUpToDate=True,
            chartOptions=[]
        )
        
        # Wait for data
        time.sleep(2)  # In production, use proper synchronization
        
        # Calculate VWAP and POC
        vwap = self.ib.calculate_vwap(self.ib.next_valid_id)
        poc_price, poc_volume = self.ib.calculate_poc(self.ib.next_valid_id)
        
        # Determine optimal execution price
        if direction.upper() == 'BUY':
            execution_price = min(vwap, poc_price)
        else:  # SELL
            execution_price = max(vwap, poc_price)
        
        # Create order
        order = Order()
        order.action = direction.upper()
        order.totalQuantity = quantity
        order.orderType = 'LMT'
        order.lmtPrice = execution_price
        order.tif = 'DAY'
        
        # Place order
        order_id = self.place_order(contract, order)
        
        # Monitor execution
        execution_details = self._monitor_order_execution(order_id, max_slippage)
        
        return {
            'strategy': 'HYBRID',
            'order_id': order_id,
            'vwap_price': vwap,
            'poc_price': poc_price,
            'execution_price': execution_price,
            'execution_details': execution_details
        }

    def _execute_aggressive(self, contract: Contract, quantity: int, 
                          direction: str, max_slippage: float, 
                          time_frame: str) -> Dict:
        """Execute order aggressively with immediate execution"""
        # Get current market price
        self.ib.reqMktData(self.ib.next_valid_id, contract, "", False, False, [])
        time.sleep(1)  # Wait for price update
        
        current_price = self.ib._market_data.get(self.ib.next_valid_id, {}).get(TickTypeEnum.LAST, 0)
        if not current_price:
            current_price = self.ib._market_data.get(self.ib.next_valid_id, {}).get(TickTypeEnum.CLOSE, 0)
        
        # Create aggressive order
        order = Order()
        order.action = direction.upper()
        order.totalQuantity = quantity
        order.orderType = 'MKT'
        order.tif = 'IOC'
        
        # Place order
        order_id = self.place_order(contract, order)
        
        # Monitor execution
        execution_details = self._monitor_order_execution(order_id, max_slippage)
        
        return {
            'strategy': 'AGGRESSIVE',
            'order_id': order_id,
            'market_price': current_price,
            'execution_details': execution_details
        }

    def _monitor_order_execution(self, order_id: int, max_slippage: float) -> Dict:
        """Monitor order execution and calculate slippage"""
        start_time = time.time()
        timeout = 300  # 5 minutes timeout
        
        while time.time() - start_time < timeout:
            order_status = self._active_orders.get(order_id, {})
            
            if order_status.get('status') == 'FILLED':
                avg_fill_price = order_status.get('avg_fill_price', 0)
                expected_price = order_status.get('expected_price', avg_fill_price)
                
                # Calculate slippage
                if expected_price > 0:
                    slippage = ((avg_fill_price - expected_price) / expected_price) * 100
                    if order_status['order'].action == 'SELL':
                        slippage *= -1
                else:
                    slippage = 0.0
                
                # Check if slippage exceeds maximum allowed
                if abs(slippage) > max_slippage:
                    raise SlippageExceededError(
                        f"Slippage {slippage:.2f}% exceeds maximum allowed {max_slippage}%")
                
                # Update order status
                order_status['slippage'] = slippage
                self._active_orders[order_id] = order_status
                
                return {
                    'status': 'FILLED',
                    'avg_fill_price': avg_fill_price,
                    'filled_quantity': order_status.get('filled_quantity', 0),
                    'slippage': slippage,
                    'execution_time': time.time() - start_time
                }
            
            time.sleep(1)
        
        return {
            'status': 'TIMEOUT',
            'avg_fill_price': 0,
            'filled_quantity': 0,
            'slippage': 0,
            'execution_time': time.time() - start_time
        }

    def _update_market_conditions(self, contract: Contract):
        """Update current market conditions for the given contract"""
        # Get current market data
        self.ib.reqMktData(self.ib.next_valid_id, contract, "", False, False, [])
        time.sleep(0.5)  # Wait for data
        
        market_data = self.ib._market_data.get(self.ib.next_valid_id, {})
        
        # Calculate liquidity metrics
        bid_size = market_data.get(TickTypeEnum.BID_SIZE, 0)
        ask_size = market_data.get(TickTypeEnum.ASK_SIZE, 0)
        spread = market_data.get(TickTypeEnum.ASK, 0) - market_data.get(TickTypeEnum.BID, 0)
        
        self._market_conditions[contract.conId] = {
            'bid': market_data.get(TickTypeEnum.BID, 0),
            'ask': market_data.get(TickTypeEnum.ASK, 0),
            'last': market_data.get(TickTypeEnum.LAST, 0),
            'volume': market_data.get(TickTypeEnum.VOLUME, 0),
            'bid_size': bid_size,
            'ask_size': ask_size,
            'spread': spread,
            'liquidity': (bid_size + ask_size) / 2,
            'timestamp': datetime.datetime.now()
        }

    def _check_risk_parameters(self, contract: Contract, quantity: int, direction: str):
        """Check order against risk parameters"""
        # Check max position size
        position = self._position_tracker.get(contract.conId, 0)
        new_position = position + (quantity if direction == 'BUY' else -quantity)
        
        if abs(new_position) > self._risk_parameters['max_position_size']:
            raise OrderExecutionError(
                f"New position size {new_position} exceeds maximum allowed {self._risk_parameters['max_position_size']}")
        
        # Check max order size
        if quantity > self._risk_parameters['max_order_size']:
            raise OrderExecutionError(
                f"Order quantity {quantity} exceeds maximum allowed {self._risk_parameters['max_order_size']}")
        
        # Check daily loss limit (simplified)
        if self._performance_metrics['total_slippage'] < self._risk_parameters['daily_loss_limit']:
            raise OrderExecutionError(
                f"Daily loss limit {self._risk_parameters['daily_loss_limit']} reached")

    def _update_performance_metrics(self, execution_result: Dict):
        """Update performance metrics based on execution results"""
        self._performance_metrics['total_trades'] += 1
        
        if execution_result['execution_details']['status'] == 'FILLED':
            slippage = execution_result['execution_details']['slippage']
            self._performance_metrics['total_slippage'] += slippage
            
            if slippage >= 0:
                self._performance_metrics['winning_trades'] += 1
            else:
                self._performance_metrics['losing_trades'] += 1
            
            # Update average slippage
            if self._performance_metrics['total_trades'] > 0:
                self._performance_metrics['avg_slippage'] = (
                    self._performance_metrics['total_slippage'] / self._performance_metrics['total_trades'])

    def _schedule_order(self, contract: Contract, order: Order, execute_time: datetime.datetime):
        """Schedule an order to execute at a specific time"""
        delay = (execute_time - datetime.datetime.now()).total_seconds()
        if delay > 0:
            threading.Timer(delay, self.place_order, args=(contract, order)).start()
        else:
            self.place_order(contract, order)

# Enhanced GUI Application with Portfolio Analytics
class TradingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} - Professional Trading System")
        self.geometry("1400x900")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Initialize IBKR API and Trading Engine
        self.ib_api = IBApi()
        self.trading_engine = TradingEngine(self.ib_api)
        self.portfolio_analyzer = PortfolioAnalyzer()
        
        # Application state
        self.connected = False
        self.contracts = {}
        self.orders = {}
        self.positions = {}
        self.account_data = {}
        self.market_data = {}
        self.historical_data = {}
        self.portfolio_returns = None
        self.settings = self._load_settings()
        
        # Create UI
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        # Connect to IBKR in background
        self.after(100, self.connect_to_ibkr)
        
        # Start market data updates
        self.after(1000, self.update_market_data)
        
        # Configure styles
        self.configure_styles()

    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Connect to IBKR", command=self.connect_to_ibkr)
        file_menu.add_command(label="Disconnect from IBKR", command=self.disconnect_from_ibkr)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Trading menu
        trade_menu = tk.Menu(menubar, tearoff=0)
        trade_menu.add_command(label="New Order", command=self.show_new_order_dialog)
        trade_menu.add_command(label="Order History", command=self.show_order_history)
        trade_menu.add_command(label="Position Manager", command=self.show_position_manager)
        menubar.add_cascade(label="Trading", menu=trade_menu)
        
        # Analytics menu
        analytics_menu = tk.Menu(menubar, tearoff=0)
        analytics_menu.add_command(label="Market Scanner", command=self.show_market_scanner)
        analytics_menu.add_command(label="Volume Profile", command=self.show_volume_profile)
        analytics_menu.add_command(label="VWAP Analysis", command=self.show_vwap_analysis)
        analytics_menu.add_command(label="POC Analysis", command=self.show_poc_analysis)
        menubar.add_cascade(label="Analytics", menu=analytics_menu)
        
        # Portfolio menu
        portfolio_menu = tk.Menu(menubar, tearoff=0)
        portfolio_menu.add_command(label="Portfolio Metrics", command=self.show_portfolio_metrics)
        portfolio_menu.add_command(label="Risk Analysis", command=self.show_risk_analysis)
        portfolio_menu.add_command(label="Optimization", command=self.show_portfolio_optimization)
        portfolio_menu.add_command(label="Performance Attribution", command=self.show_performance_attribution)
        menubar.add_cascade(label="Portfolio", menu=portfolio_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menubar)

    def create_main_frame(self):
        """Create the main application frame with tabs"""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.create_dashboard()
        
        # Trading tab
        self.trading_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trading_frame, text="Trading")
        self.create_trading_panel()
        
        # Analytics tab
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytics")
        self.create_analytics_panel()
        
        # Account tab
        self.account_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.account_frame, text="Account")
        self.create_account_panel()
        
        # Portfolio tab
        self.portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.portfolio_frame, text="Portfolio")
        self.create_portfolio_panel()

    def create_dashboard(self):
        """Create dashboard with market overview and quick trading"""
        # Market overview
        market_group = ttk.LabelFrame(self.dashboard_frame, text="Market Overview", padding=10)
        market_group.pack(fill=tk.X, padx=5, pady=5)
        
        self.market_summary = ttk.Label(market_group, text="Connecting to market data...")
        self.market_summary.pack(anchor=tk.W)
        
        # Quick trade panel
        trade_group = ttk.LabelFrame(self.dashboard_frame, text="Quick Trade", padding=10)
        trade_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(trade_group, text="Symbol:").grid(row=0, column=0, sticky=tk.W)
        self.symbol_entry = ttk.Entry(trade_group, width=10)
        self.symbol_entry.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(trade_group, text="Quantity:").grid(row=1, column=0, sticky=tk.W)
        self.quantity_entry = ttk.Entry(trade_group, width=10)
        self.quantity_entry.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(trade_group, text="Action:").grid(row=2, column=0, sticky=tk.W)
        self.action_var = tk.StringVar(value="BUY")
        ttk.Radiobutton(trade_group, text="Buy", variable=self.action_var, value="BUY").grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(trade_group, text="Sell", variable=self.action_var, value="SELL").grid(row=2, column=2, sticky=tk.W)
        
        ttk.Label(trade_group, text="Strategy:").grid(row=3, column=0, sticky=tk.W)
        self.strategy_var = tk.StringVar(value="HYBRID")
        strategies = ["VWAP", "TWAP", "POC", "HYBRID", "AGGRESSIVE"]
        self.strategy_menu = ttk.OptionMenu(trade_group, self.strategy_var, "HYBRID", *strategies)
        self.strategy_menu.grid(row=3, column=1, sticky=tk.W)
        
        ttk.Label(trade_group, text="Time Frame:").grid(row=4, column=0, sticky=tk.W)
        self.timeframe_var = tk.StringVar(value="1H")
        timeframes = ["1M", "5M", "15M", "30M", "1H", "4H", "1D"]
        self.timeframe_menu = ttk.OptionMenu(trade_group, self.timeframe_var, "1H", *timeframes)
        self.timeframe_menu.grid(row=4, column=1, sticky=tk.W)
        
        ttk.Label(trade_group, text="Max Slippage (%):").grid(row=5, column=0, sticky=tk.W)
        self.slippage_entry = ttk.Entry(trade_group, width=10)
        self.slippage_entry.insert(0, "0.5")
        self.slippage_entry.grid(row=5, column=1, sticky=tk.W)
        
        self.execute_button = ttk.Button(trade_group, text="Execute Trade", command=self.execute_quick_trade)
        self.execute_button.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Recent activity
        activity_group = ttk.LabelFrame(self.dashboard_frame, text="Recent Activity", padding=10)
        activity_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Time", "Symbol", "Action", "Quantity", "Price", "Status", "Slippage")
        self.activity_tree = ttk.Treeview(activity_group, columns=columns, show="headings")
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=100, anchor=tk.CENTER)
        self.activity_tree.pack(fill=tk.BOTH, expand=True)
        
        # Performance metrics
        metrics_group = ttk.LabelFrame(self.dashboard_frame, text="Performance Metrics", padding=10)
        metrics_group.pack(fill=tk.X, padx=5, pady=5)
        
        self.metrics_text = tk.Text(metrics_group, height=5, state=tk.DISABLED)
        self.metrics_text.pack(fill=tk.X)
        
        self.update_performance_metrics()

    def create_trading_panel(self):
        """Create advanced trading panel"""
        # Contract selection
        contract_group = ttk.LabelFrame(self.trading_frame, text="Contract Details", padding=10)
        contract_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(contract_group, text="Symbol:").grid(row=0, column=0, sticky=tk.W)
        self.trade_symbol_entry = ttk.Entry(contract_group, width=15)
        self.trade_symbol_entry.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(contract_group, text="Security Type:").grid(row=0, column=2, sticky=tk.W)
        self.sec_type_var = tk.StringVar(value="STK")
        sec_types = ["STK", "FUT", "OPT", "CASH", "BOND"]
        self.sec_type_menu = ttk.OptionMenu(contract_group, self.sec_type_var, "STK", *sec_types)
        self.sec_type_menu.grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(contract_group, text="Exchange:").grid(row=1, column=0, sticky=tk.W)
        self.exchange_entry = ttk.Entry(contract_group, width=15)
        self.exchange_entry.grid(row=1, column=1, sticky=tk.W)
        self.exchange_entry.insert(0, "SMART")
        
        ttk.Label(contract_group, text="Currency:").grid(row=1, column=2, sticky=tk.W)
        self.currency_entry = ttk.Entry(contract_group, width=15)
        self.currency_entry.grid(row=1, column=3, sticky=tk.W)
        self.currency_entry.insert(0, "USD")
        
        self.lookup_button = ttk.Button(contract_group, text="Lookup Contract", command=self.lookup_contract)
        self.lookup_button.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Contract details display
        self.contract_details_text = tk.Text(contract_group, height=5, state=tk.DISABLED)
        self.contract_details_text.grid(row=3, column=0, columnspan=4, sticky=tk.EW)
        
        # Order entry
        order_group = ttk.LabelFrame(self.trading_frame, text="Order Entry", padding=10)
        order_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(order_group, text="Action:").grid(row=0, column=0, sticky=tk.W)
        self.trade_action_var = tk.StringVar(value="BUY")
        ttk.Radiobutton(order_group, text="Buy", variable=self.trade_action_var, value="BUY").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(order_group, text="Sell", variable=self.trade_action_var, value="SELL").grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(order_group, text="Quantity:").grid(row=1, column=0, sticky=tk.W)
        self.trade_quantity_entry = ttk.Entry(order_group, width=15)
        self.trade_quantity_entry.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(order_group, text="Order Type:").grid(row=2, column=0, sticky=tk.W)
        self.order_type_var = tk.StringVar(value="LMT")
        order_types = ["MKT", "LMT", "STP", "STP LMT", "TRAIL", "VWAP", "TWAP"]
        self.order_type_menu = ttk.OptionMenu(order_group, self.order_type_var, "LMT", *order_types)
        self.order_type_menu.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(order_group, text="Price:").grid(row=3, column=0, sticky=tk.W)
        self.price_entry = ttk.Entry(order_group, width=15)
        self.price_entry.grid(row=3, column=1, sticky=tk.W)
        
        ttk.Label(order_group, text="Time in Force:").grid(row=4, column=0, sticky=tk.W)
        self.tif_var = tk.StringVar(value="DAY")
        tifs = ["DAY", "GTC", "IOC", "FOK", "GTD"]
        self.tif_menu = ttk.OptionMenu(order_group, self.tif_var, "DAY", *tifs)
        self.tif_menu.grid(row=4, column=1, sticky=tk.W)
        
        ttk.Label(order_group, text="Strategy:").grid(row=5, column=0, sticky=tk.W)
        self.trade_strategy_var = tk.StringVar(value="HYBRID")
        strategies = ["VWAP", "TWAP", "POC", "HYBRID", "AGGRESSIVE"]
        self.trade_strategy_menu = ttk.OptionMenu(order_group, self.trade_strategy_var, "HYBRID", *strategies)
        self.trade_strategy_menu.grid(row=5, column=1, sticky=tk.W)
        
        ttk.Label(order_group, text="Time Frame:").grid(row=6, column=0, sticky=tk.W)
        self.trade_timeframe_var = tk.StringVar(value="1H")
        timeframes = ["1M", "5M", "15M", "30M", "1H", "4H", "1D"]
        self.trade_timeframe_menu = ttk.OptionMenu(order_group, self.trade_timeframe_var, "1H", *timeframes)
        self.trade_timeframe_menu.grid(row=6, column=1, sticky=tk.W)
        
        ttk.Label(order_group, text="Max Slippage (%):").grid(row=7, column=0, sticky=tk.W)
        self.trade_slippage_entry = ttk.Entry(order_group, width=15)
        self.trade_slippage_entry.insert(0, "0.5")
        self.trade_slippage_entry.grid(row=7, column=1, sticky=tk.W)
        
        self.place_order_button = ttk.Button(order_group, text="Place Order", command=self.place_advanced_order)
        self.place_order_button.grid(row=8, column=0, columnspan=2, pady=5)
        
        # Order management
        order_mgmt_group = ttk.LabelFrame(self.trading_frame, text="Order Management", padding=10)
        order_mgmt_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("ID", "Symbol", "Action", "Quantity", "Type", "Price", "Status", "Filled", "Remaining")
        self.order_tree = ttk.Treeview(order_mgmt_group, columns=columns, show="headings")
        for col in columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=80, anchor=tk.CENTER)
        self.order_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(order_mgmt_group, orient=tk.VERTICAL, command=self.order_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        
        # Order actions
        button_frame = ttk.Frame(order_mgmt_group)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel Order", command=self.cancel_order)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.modify_button = ttk.Button(button_frame, text="Modify Order", command=self.modify_order)
        self.modify_button.pack(side=tk.LEFT, padx=5)
        
        self.refresh_button = ttk.Button(button_frame, text="Refresh", command=self.refresh_orders)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

    def create_analytics_panel(self):
        """Create analytics panel with charts and tools"""
        # Chart frame
        chart_frame = ttk.Frame(self.analytics_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create figure for plotting
        self.fig, (self.ax_price, self.ax_volume) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
        self.fig.set_size_inches(8, 6)
        self.fig.set_facecolor('#f0f0f0')
        self.ax_price.set_facecolor('#f0f0f0')
        self.ax_volume.set_facecolor('#f0f0f0')
        
        # Create canvas for embedding matplotlib figure
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Analytics controls
        controls_frame = ttk.Frame(self.analytics_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Symbol:").grid(row=0, column=0, sticky=tk.W)
        self.analytics_symbol_entry = ttk.Entry(controls_frame, width=15)
        self.analytics_symbol_entry.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(controls_frame, text="Time Frame:").grid(row=0, column=2, sticky=tk.W)
        self.analytics_timeframe_var = tk.StringVar(value="1D")
        timeframes = ["1M", "5M", "15M", "30M", "1H", "4H", "1D", "1W", "1M"]
        self.analytics_timeframe_menu = ttk.OptionMenu(controls_frame, self.analytics_timeframe_var, "1D", *timeframes)
        self.analytics_timeframe_menu.grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(controls_frame, text="Periods:").grid(row=0, column=4, sticky=tk.W)
        self.analytics_periods_var = tk.StringVar(value="50")
        periods = ["10", "20", "50", "100", "200"]
        self.analytics_periods_menu = ttk.OptionMenu(controls_frame, self.analytics_periods_var, "50", *periods)
        self.analytics_periods_menu.grid(row=0, column=5, sticky=tk.W)
        
        self.load_chart_button = ttk.Button(controls_frame, text="Load Chart", command=self.load_chart_data)
        self.load_chart_button.grid(row=0, column=6, padx=5)
        
        # Indicators
        indicators_group = ttk.LabelFrame(controls_frame, text="Indicators", padding=5)
        indicators_group.grid(row=1, column=0, columnspan=7, sticky=tk.EW, pady=5)
        
        self.show_vwap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(indicators_group, text="VWAP", variable=self.show_vwap_var).pack(side=tk.LEFT, padx=5)
        
        self.show_poc_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(indicators_group, text="POC", variable=self.show_poc_var).pack(side=tk.LEFT, padx=5)
        
        self.show_ma_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(indicators_group, text="MA", variable=self.show_ma_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(indicators_group, text="MA Period:").pack(side=tk.LEFT, padx=5)
        self.ma_period_var = tk.StringVar(value="20")
        ttk.Entry(indicators_group, textvariable=self.ma_period_var, width=5).pack(side=tk.LEFT, padx=5)
        
        self.update_chart_button = ttk.Button(indicators_group, text="Update Chart", command=self.update_chart)
        self.update_chart_button.pack(side=tk.LEFT, padx=5)
        
        # Volume profile
        profile_frame = ttk.Frame(self.analytics_frame)
        profile_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.profile_fig, self.profile_ax = plt.subplots()
        self.profile_fig.set_size_inches(4, 6)
        self.profile_fig.set_facecolor('#f0f0f0')
        self.profile_ax.set_facecolor('#f0f0f0')
        
        self.profile_canvas = FigureCanvasTkAgg(self.profile_fig, master=profile_frame)
        self.profile_canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Profile stats
        stats_frame = ttk.Frame(profile_frame)
        stats_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Label(stats_frame, text="Volume Profile Stats", font=('Helvetica', 10, 'bold')).pack(pady=5)
        
        self.vwap_label = ttk.Label(stats_frame, text="VWAP: -")
        self.vwap_label.pack(anchor=tk.W)
        
        self.poc_label = ttk.Label(stats_frame, text="POC: -")
        self.poc_label.pack(anchor=tk.W)
        
        self.high_label = ttk.Label(stats_frame, text="High: -")
        self.high_label.pack(anchor=tk.W)
        
        self.low_label = ttk.Label(stats_frame, text="Low: -")
        self.low_label.pack(anchor=tk.W)
        
        self.volume_label = ttk.Label(stats_frame, text="Volume: -")
        self.volume_label.pack(anchor=tk.W)
        
        self.value_area_label = ttk.Label(stats_frame, text="Value Area (70%): -")
        self.value_area_label.pack(anchor=tk.W)

    def create_account_panel(self):
        """Create account information panel"""
        # Account summary
        summary_group = ttk.LabelFrame(self.account_frame, text="Account Summary", padding=10)
        summary_group.pack(fill=tk.X, padx=5, pady=5)
        
        columns = ("Account", "Key", "Value", "Currency")
        self.account_tree = ttk.Treeview(summary_group, columns=columns, show="headings")
        for col in columns:
            self.account_tree.heading(col, text=col)
            self.account_tree.column(col, width=120, anchor=tk.CENTER)
        self.account_tree.pack(fill=tk.X)
        
        # Positions
        positions_group = ttk.LabelFrame(self.account_frame, text="Positions", padding=10)
        positions_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        pos_columns = ("Symbol", "Position", "Avg Cost", "Market Price", "Market Value", "PnL")
        self.positions_tree = ttk.Treeview(positions_group, columns=pos_columns, show="headings")
        for col in pos_columns:
            self.positions_tree.heading(col, text=col)
            self.positions_tree.column(col, width=100, anchor=tk.CENTER)
        self.positions_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(positions_group, orient=tk.VERTICAL, command=self.positions_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.positions_tree.configure(yscrollcommand=scrollbar.set)
        
        # PnL chart
        pnl_group = ttk.LabelFrame(self.account_frame, text="Profit & Loss", padding=10)
        pnl_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.pnl_fig, self.pnl_ax = plt.subplots()
        self.pnl_fig.set_size_inches(8, 3)
        self.pnl_fig.set_facecolor('#f0f0f0')
        self.pnl_ax.set_facecolor('#f0f0f0')
        
        self.pnl_canvas = FigureCanvasTkAgg(self.pnl_fig, master=pnl_group)
        self.pnl_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_portfolio_panel(self):
        """Create portfolio analysis panel"""
        # Portfolio metrics
        metrics_group = ttk.LabelFrame(self.portfolio_frame, text="Portfolio Metrics", padding=10)
        metrics_group.pack(fill=tk.X, padx=5, pady=5)
        
        columns = ("Metric", "Value")
        self.metrics_tree = ttk.Treeview(metrics_group, columns=columns, show="headings")
        for col in columns:
            self.metrics_tree.heading(col, text=col)
            self.metrics_tree.column(col, width=200, anchor=tk.W)
        self.metrics_tree.pack(fill=tk.X)
        
        # Risk analysis
        risk_group = ttk.LabelFrame(self.portfolio_frame, text="Risk Analysis", padding=10)
        risk_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # VaR chart
        var_frame = ttk.Frame(risk_group)
        var_frame.pack(fill=tk.BOTH, expand=True)
        
        self.var_fig, self.var_ax = plt.subplots()
        self.var_fig.set_size_inches(8, 4)
        self.var_fig.set_facecolor('#f0f0f0')
        self.var_ax.set_facecolor('#f0f0f0')
        
        self.var_canvas = FigureCanvasTkAgg(self.var_fig, master=var_frame)
        self.var_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Optimization controls
        opt_group = ttk.LabelFrame(self.portfolio_frame, text="Portfolio Optimization", padding=10)
        opt_group.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(opt_group, text="Objective:").grid(row=0, column=0, sticky=tk.W)
        self.opt_objective_var = tk.StringVar(value="max_sharpe")
        objectives = ["max_sharpe", "min_volatility", "max_sortino", "efficient_risk", "efficient_return"]
        self.opt_objective_menu = ttk.OptionMenu(opt_group, self.opt_objective_var, "max_sharpe", *objectives)
        self.opt_objective_menu.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(opt_group, text="Target Return:").grid(row=1, column=0, sticky=tk.W)
        self.target_return_entry = ttk.Entry(opt_group, width=10)
        self.target_return_entry.insert(0, "0.10")
        self.target_return_entry.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(opt_group, text="Target Volatility:").grid(row=2, column=0, sticky=tk.W)
        self.target_vol_entry = ttk.Entry(opt_group, width=10)
        self.target_vol_entry.insert(0, "0.15")
        self.target_vol_entry.grid(row=2, column=1, sticky=tk.W)
        
        self.optimize_button = ttk.Button(opt_group, text="Optimize Portfolio", command=self.optimize_portfolio)
        self.optimize_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Efficient frontier
        frontier_frame = ttk.Frame(self.portfolio_frame)
        frontier_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.frontier_fig, self.frontier_ax = plt.subplots()
        self.frontier_fig.set_size_inches(8, 6)
        self.frontier_fig.set_facecolor('#f0f0f0')
        self.frontier_ax.set_facecolor('#f0f0f0')
        
        self.frontier_canvas = FigureCanvasTkAgg(self.frontier_fig, master=frontier_frame)
        self.frontier_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        """Create status bar at bottom of window"""
        self.status_var = tk.StringVar()
        self.status_var.set("Initializing...")
        
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Connection status indicator
        self.connection_status = ttk.Label(self.status_bar, text="Disconnected", foreground="red")
        self.connection_status.pack(side=tk.RIGHT, padx=5)

    def configure_styles(self):
        """Configure custom styles for the application"""
        style = ttk.Style()
        
        # Configure main window style
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0')
        style.configure('TButton', padding=5)
        style.configure('TNotebook.Tab', padding=[10, 5])
        
        # Configure treeview style
        style.configure("Treeview", 
                        background="#ffffff",
                        foreground="#000000",
                        rowheight=25,
                        fieldbackground="#ffffff")
        style.map('Treeview', background=[('selected', '#0078d7')])
        
        # Configure status bar
        style.configure("Status.TLabel", 
                       background="#e0e0e0",
                       foreground="#000000",
                       padding=5,
                       font=('Helvetica', 9))

    def _load_settings(self) -> Dict:
        """Load application settings from file"""
        settings_file = os.path.join(os.environ['LOCALAPPDATA'], COMPANY_NAME, APP_NAME, 'settings.ini')
        settings = {
            'ibkr': {
                'host': '127.0.0.1',
                'port': '7497',
                'client_id': '1'
            },
            'trading': {
                'default_quantity': '100',
                'default_slippage': '0.5',
                'default_timeframe': '1H'
            },
            'ui': {
                'theme': 'light',
                'font_size': '9'
            },
            'portfolio': {
                'risk_free_rate': '0.02',
                'var_confidence': '0.95',
                'optimization_window': '252'
            }
        }
        
        if os.path.exists(settings_file):
            config = configparser.ConfigParser()
            config.read(settings_file)
            
            for section in config.sections():
                for key in config[section]:
                    settings[section][key] = config[section][key]
        
        return settings

    def _save_settings(self):
        """Save application settings to file"""
        settings_dir = os.path.join(os.environ['LOCALAPPDATA'], COMPANY_NAME, APP_NAME)
        os.makedirs(settings_dir, exist_ok=True)
        settings_file = os.path.join(settings_dir, 'settings.ini')
        
        config = configparser.ConfigParser()
        for section, options in self.settings.items():
            config[section] = options
        
        with open(settings_file, 'w') as f:
            config.write(f)

    def connect_to_ibkr(self):
        """Connect to IBKR TWS/Gateway"""
        try:
            host = self.settings['ibkr']['host']
            port = int(self.settings['ibkr']['port'])
            client_id = int(self.settings['ibkr']['client_id'])
            
            self.status_var.set("Connecting to IBKR TWS/Gateway...")
            self.connection_status.config(text="Connecting...", foreground="orange")
            
            # Start connection in a separate thread
            def connect_thread():
                try:
                    if self.trading_engine.connect_to_ibkr(host, port, client_id):
                        self.connected = True
                        self.connection_status.config(text="Connected", foreground="green")
                        self.status_var.set("Successfully connected to IBKR")
                        
                        # Request account and position data
                        self.request_account_data()
                        self.request_positions()
                        self.request_historical_data_for_portfolio()
                    else:
                        self.connection_status.config(text="Disconnected", foreground="red")
                        self.status_var.set("Failed to connect to IBKR")
                except Exception as e:
                    self.connection_status.config(text="Disconnected", foreground="red")
                    self.status_var.set(f"Connection error: {str(e)}")
                    logger.error(f"Connection error: {str(e)}")
            
            threading.Thread(target=connect_thread, daemon=True).start()
            
        except Exception as e:
            self.connection_status.config(text="Disconnected", foreground="red")
            self.status_var.set(f"Connection error: {str(e)}")
            logger.error(f"Connection error: {str(e)}")

    def disconnect_from_ibkr(self):
        """Disconnect from IBKR TWS/Gateway"""
        try:
            self.trading_engine.disconnect_from_ibkr()
            self.connected = False
            self.connection_status.config(text="Disconnected", foreground="red")
            self.status_var.set("Disconnected from IBKR")
        except Exception as e:
            self.status_var.set(f"Disconnection error: {str(e)}")
            logger.error(f"Disconnection error: {str(e)}")

    def request_account_data(self):
        """Request account data from IBKR"""
        if not self.connected:
            return
            
        def request_thread():
            try:
                self.ib_api.reqAccountUpdates(True, "")
                time.sleep(1)  # Wait for data
                
                # Update UI with account data
                self.after(100, self.update_account_display)
            except Exception as e:
                logger.error(f"Error requesting account data: {str(e)}")
                self.status_var.set(f"Error requesting account data: {str(e)}")
        
        threading.Thread(target=request_thread, daemon=True).start()

    def request_positions(self):
        """Request position data from IBKR"""
        if not self.connected:
            return
            
        def request_thread():
            try:
                self.ib_api.reqPositions()
                time.sleep(1)  # Wait for data
                
                # Update UI with positions
                self.after(100, self.update_positions_display)
            except Exception as e:
                logger.error(f"Error requesting positions: {str(e)}")
                self.status_var.set(f"Error requesting positions: {str(e)}")
        
        threading.Thread(target=request_thread, daemon=True).start()

    def request_historical_data_for_portfolio(self):
        """Request historical data for portfolio analysis"""
        if not self.connected:
            return
            
        def request_thread():
            try:
                # Get list of positions
                positions = self.ib_api._portfolio_positions
                if not positions:
                    return
                
                # Request historical data for each position
                end_date = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
                duration = '1 Y'  # 1 year of data
                bar_size = '1 day'  # Daily bars
                
                for i, position in enumerate(positions):
                    contract = position['contract']
                    req_id = self.ib_api.next_valid_id + i
                    
                    self.ib_api.reqHistoricalData(
                        reqId=req_id,
                        contract=contract,
                        endDateTime=end_date,
                        durationStr=duration,
                        barSizeSetting=bar_size,
                        whatToShow="TRADES",
                        useRTH=True,
                        formatDate=1,
                        keepUpToDate=False,
                        chartOptions=[]
                    )
                
                # Wait for data
                time.sleep(5)
                
                # Process historical data
                self.process_portfolio_data()
                
            except Exception as e:
                logger.error(f"Error requesting portfolio data: {str(e)}")
                self.status_var.set(f"Error requesting portfolio data: {str(e)}")
        
        threading.Thread(target=request_thread, daemon=True).start()

    def process_portfolio_data(self):
        """Process historical data for portfolio analysis"""
        try:
            # Create DataFrame for returns
            returns_data = {}
            
            for req_id, bars in self.ib_api._historical_data.items():
                if not bars:
                    continue
                
                # Get contract symbol
                contract = None
                for pos in self.ib_api._portfolio_positions:
                    if pos['contract'].conId == bars[0].conId:
                        contract = pos['contract']
                        break
                
                if not contract:
                    continue
                
                # Create returns series
                closes = [bar.close for bar in bars]
                dates = [datetime.datetime.strptime(bar.date, '%Y%m%d %H:%M:%S') for bar in bars]
                returns = pd.Series(closes, index=dates).pct_change().dropna()
                
                returns_data[contract.symbol] = returns
            
            # Create DataFrame
            self.portfolio_returns = pd.DataFrame(returns_data)
            
            # Update portfolio analyzer
            self.portfolio_analyzer.set_returns_data(self.portfolio_returns)
            self.portfolio_analyzer.set_risk_free_rate(float(self.settings['portfolio']['risk_free_rate']))
            
            # Update UI
            self.after(100, self.update_portfolio_metrics)
            self.after(100, self.update_var_chart)
            
        except Exception as e:
            logger.error(f"Error processing portfolio data: {str(e)}")
            self.status_var.set(f"Error processing portfolio data: {str(e)}")

    def update_account_display(self):
        """Update account information display"""
        try:
            # Clear existing data
            for item in self.account_tree.get_children():
                self.account_tree.delete(item)
            
            # Add new data
            for account, data in self.ib_api._account_data.items():
                for key, value in data.items():
                    currency = key.split('_')[-1] if '_' in key else 'USD'
                    clean_key = key.replace(f'_{currency}', '')
                    self.account_tree.insert("", tk.END, values=(account, clean_key, value, currency))
            
            # Update PnL chart
            self.update_pnl_chart()
        except Exception as e:
            logger.error(f"Error updating account display: {str(e)}")

    def update_positions_display(self):
        """Update positions display"""
        try:
            # Clear existing data
            for item in self.positions_tree.get_children():
                self.positions_tree.delete(item)
            
            # Add new data
            for position in self.ib_api._portfolio_positions:
                contract = position['contract']
                symbol = contract.symbol
                market_value = float(position['marketValue'])
                avg_cost = float(position['averageCost'])
                pnl = float(position['unrealizedPNL'])
                
                self.positions_tree.insert("", tk.END, values=(
                    symbol,
                    position['position'],
                    f"{avg_cost:.2f}",
                    f"{position['marketPrice']:.2f}",
                    f"{market_value:.2f}",
                    f"{pnl:.2f} ({pnl/market_value*100:.2f}%)" if market_value != 0 else "0.00 (0.00%)"
                ))
        except Exception as e:
            logger.error(f"Error updating positions display: {str(e)}")

    def update_pnl_chart(self):
        """Update PnL chart"""
        try:
            self.pnl_ax.clear()
            
            # Sample data - in real app, use actual historical PnL data
            dates = pd.date_range(end=datetime.datetime.now(), periods=30, freq='D')
            pnl = np.cumsum(np.random.randn(30) * 1000)
            
            self.pnl_ax.plot(dates, pnl, color='green' if pnl[-1] >= 0 else 'red', linewidth=2)
            self.pnl_ax.fill_between(dates, pnl, 0, where=(pnl >= 0), facecolor='green', alpha=0.2)
            self.pnl_ax.fill_between(dates, pnl, 0, where=(pnl < 0), facecolor='red', alpha=0.2)
            
            self.pnl_ax.set_title("30-Day PnL Trend")
            self.pnl_ax.grid(True, linestyle='--', alpha=0.7)
            self.pnl_ax.set_facecolor('#f0f0f0')
            
            self.pnl_canvas.draw()
        except Exception as e:
            logger.error(f"Error updating PnL chart: {str(e)}")

    def update_portfolio_metrics(self):
        """Update portfolio metrics display"""
        try:
            if self.portfolio_returns is None:
                return
                
            # Calculate basic metrics
            metrics = self.portfolio_analyzer.calculate_basic_metrics()
            
            # Clear existing data
            for item in self.metrics_tree.get_children():
                self.metrics_tree.delete(item)
            
            # Add metrics to treeview
            for metric, value in metrics.items():
                if value is None:
                    continue
                    
                if isinstance(value, float):
                    display_value = f"{value:.4f}"
                else:
                    display_value = str(value)
                
                self.metrics_tree.insert("", tk.END, values=(metric.replace('_', ' ').title(), display_value))
                
        except Exception as e:
            logger.error(f"Error updating portfolio metrics: {str(e)}")
            self.status_var.set(f"Error updating portfolio metrics: {str(e)}")

    def update_var_chart(self):
        """Update Value at Risk chart"""
        try:
            if self.portfolio_returns is None:
                return
                
            # Calculate rolling VaR
            var_data = self.portfolio_analyzer.calculate_var_through_time(window=63, alpha=0.05)
            
            # Plot VaR
            self.var_ax.clear()
            
            for method in ['parametric', 'historical', 'ewma', 'garch']:
                if method in var_data.columns:
                    self.var_ax.plot(var_data.index, var_data[method], label=method.capitalize())
            
            self.var_ax.set_title("Rolling 3-Month Value at Risk (95% Confidence)")
            self.var_ax.set_ylabel("VaR")
            self.var_ax.legend()
            self.var_ax.grid(True, linestyle='--', alpha=0.7)
            self.var_ax.set_facecolor('#f0f0f0')
            
            self.var_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating VaR chart: {str(e)}")
            self.status_var.set(f"Error updating VaR chart: {str(e)}")

    def optimize_portfolio(self):
        """Optimize portfolio weights"""
        try:
            if self.portfolio_returns is None:
                messagebox.showwarning("Warning", "No portfolio data available")
                return
                
            # Get optimization parameters
            objective = self.opt_objective_var.get()
            target_return = float(self.target_return_entry.get())
            target_vol = float(self.target_vol_entry.get())
            
            constraints = {}
            
            if objective == 'efficient_risk':
                constraints['target_volatility'] = target_vol
            elif objective == 'efficient_return':
                constraints['target_return'] = target_return
            
            # Run optimization
            result = self.portfolio_analyzer.optimize_portfolio(objective=objective, constraints=constraints)
            
            # Update efficient frontier chart
            self.update_efficient_frontier(result['efficient_frontier_data'], 
                                         result['performance_metrics'])
            
            # Show optimized weights
            self.show_optimization_results(result['optimized_weights'], 
                                         result['performance_metrics'])
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {str(e)}")
            messagebox.showerror("Error", f"Failed to optimize portfolio: {str(e)}")

    def update_efficient_frontier(self, frontier_data: dict, performance: dict):
        """Update efficient frontier chart"""
        try:
            self.frontier_ax.clear()
            
            # Plot efficient frontier
            self.frontier_ax.plot(frontier_data['volatility'], frontier_data['returns'], 
                                label='Efficient Frontier', color='blue')
            
            # Mark optimal portfolio
            self.frontier_ax.scatter(performance['volatility'], performance['expected_return'],
                                   color='red', label='Optimal Portfolio')
            
            self.frontier_ax.set_title("Efficient Frontier")
            self.frontier_ax.set_xlabel("Volatility (Risk)")
            self.frontier_ax.set_ylabel("Expected Return")
            self.frontier_ax.legend()
            self.frontier_ax.grid(True, linestyle='--', alpha=0.7)
            self.frontier_ax.set_facecolor('#f0f0f0')
            
            self.frontier_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating efficient frontier: {str(e)}")
            self.status_var.set(f"Error updating efficient frontier: {str(e)}")

    def show_optimization_results(self, weights: dict, performance: dict):
        """Show portfolio optimization results in a dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Portfolio Optimization Results")
        dialog.geometry("600x400")
        
        # Create notebook for different views
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Weights tab
        weights_frame = ttk.Frame(notebook)
        notebook.add(weights_frame, text="Optimal Weights")
        
        # Create treeview for weights
        columns = ("Asset", "Weight")
        weights_tree = ttk.Treeview(weights_frame, columns=columns, show="headings")
        for col in columns:
            weights_tree.heading(col, text=col)
            weights_tree.column(col, width=200, anchor=tk.CENTER)
        weights_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add weights to treeview
        for asset, weight in weights.items():
            if weight > 0.001:  # Only show significant weights
                weights_tree.insert("", tk.END, values=(asset, f"{weight:.2%}"))
        
        # Performance tab
        perf_frame = ttk.Frame(notebook)
        notebook.add(perf_frame, text="Performance Metrics")
        
        # Create treeview for performance metrics
        columns = ("Metric", "Value")
        perf_tree = ttk.Treeview(perf_frame, columns=columns, show="headings")
        for col in columns:
            perf_tree.heading(col, text=col)
            perf_tree.column(col, width=200, anchor=tk.W)
        perf_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add performance metrics
        perf_tree.insert("", tk.END, values=("Expected Return", f"{performance['expected_return']:.2%}"))
        perf_tree.insert("", tk.END, values=("Volatility", f"{performance['volatility']:.2%}"))
        perf_tree.insert("", tk.END, values=("Sharpe Ratio", f"{performance['sharpe_ratio']:.2f}"))
        
        # Risk contribution tab
        risk_frame = ttk.Frame(notebook)
        notebook.add(risk_frame, text="Risk Contribution")
        
        # Calculate risk contributions
        risk_contributions = self.portfolio_analyzer.calculate_risk_contribution(weights)
        
        # Create treeview for risk contributions
        columns = ("Asset", "Risk Contribution")
        risk_tree = ttk.Treeview(risk_frame, columns=columns, show="headings")
        for col in columns:
            risk_tree.heading(col, text=col)
            risk_tree.column(col, width=200, anchor=tk.CENTER)
        risk_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add risk contributions
        for asset, contribution in risk_contributions.items():
            if weights[asset] > 0.001:  # Only show significant contributions
                risk_tree.insert("", tk.END, values=(asset, f"{contribution:.2%}"))

    def update_market_data(self):
        """Update market data display"""
        if not self.connected:
            self.after(1000, self.update_market_data)
            return
            
        try:
            # Get market data for watched symbols
            if hasattr(self, 'current_symbol') and self.current_symbol:
                req_id = list(self.contracts.keys())[0]  # Simplified for example
                market_data = self.ib_api._market_data.get(req_id, {})
                
                if market_data:
                    bid = market_data.get(TickTypeEnum.BID, 0)
                    ask = market_data.get(TickTypeEnum.ASK, 0)
                    last = market_data.get(TickTypeEnum.LAST, 0)
                    volume = market_data.get(TickTypeEnum.VOLUME, 0)
                    
                    summary_text = (f"{self.current_symbol}: Bid={bid:.2f} | Ask={ask:.2f} | Last={last:.2f} | "
                                  f"Volume={volume:,}")
                    self.market_summary.config(text=summary_text)
            
            # Schedule next update
            self.after(1000, self.update_market_data)
        except Exception as e:
            logger.error(f"Error updating market data: {str(e)}")
            self.after(1000, self.update_market_data)

    def update_performance_metrics(self):
        """Update performance metrics display"""
        try:
            metrics = self.trading_engine._performance_metrics
            win_rate = (metrics['winning_trades'] / metrics['total_trades'] * 100 
                       if metrics['total_trades'] > 0 else 0)
            
            text = (f"Total Trades: {metrics['total_trades']} | "
                   f"Win Rate: {win_rate:.1f}% | "
                   f"Avg Slippage: {metrics['avg_slippage']:.2f}% | "
                   f"Total Commission: ${metrics['total_commission']:.2f}")
            
            self.metrics_text.config(state=tk.NORMAL)
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(tk.END, text)
            self.metrics_text.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Error updating performance metrics: {str(e)}")

    def lookup_contract(self):
        """Lookup contract details"""
        symbol = self.trade_symbol_entry.get().strip()
        sec_type = self.sec_type_var.get()
        exchange = self.exchange_entry.get().strip()
        currency = self.currency_entry.get().strip()
        
        if not symbol:
            messagebox.showerror("Error", "Please enter a symbol")
            return
            
        self.status_var.set(f"Looking up contract details for {symbol}...")
        
        def lookup_thread():
            try:
                contract = Contract()
                contract.symbol = symbol
                contract.secType = sec_type
                contract.exchange = exchange
                contract.currency = currency
                
                req_id = self.ib_api.next_valid_id
                self.ib_api.reqContractDetails(req_id, contract)
                time.sleep(1)  # Wait for response
                
                details = self.ib_api._contract_details.get(req_id)
                if details:
                    self.contracts[req_id] = details.contract
                    self.current_symbol = symbol
                    
                    # Update UI with contract details
                    details_text = (f"Symbol: {details.contract.symbol}\n"
                                   f"Name: {details.longName}\n"
                                   f"Type: {details.contract.secType}\n"
                                   f"Exchange: {details.contract.exchange}\n"
                                   f"Currency: {details.contract.currency}\n"
                                   f"Min Tick: {details.minTick}\n"
                                   f"Order Types: {details.orderTypes}")
                    
                    self.after(100, lambda: self.update_contract_details(details_text))
                    self.status_var.set(f"Found contract details for {symbol}")
                else:
                    self.after(100, lambda: messagebox.showerror("Error", f"No contract found for {symbol}"))
                    self.status_var.set(f"No contract found for {symbol}")
            except Exception as e:
                logger.error(f"Error looking up contract: {str(e)}")
                self.after(100, lambda: messagebox.showerror("Error", f"Failed to lookup contract: {str(e)}"))
                self.status_var.set(f"Error looking up contract: {str(e)}")
        
        threading.Thread(target=lookup_thread, daemon=True).start()

    def update_contract_details(self, text: str):
        """Update contract details display"""
        self.contract_details_text.config(state=tk.NORMAL)
        self.contract_details_text.delete(1.0, tk.END)
        self.contract_details_text.insert(tk.END, text)
        self.contract_details_text.config(state=tk.DISABLED)

    def execute_quick_trade(self):
        """Execute quick trade from dashboard"""
        symbol = self.symbol_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        action = self.action_var.get()
        strategy = self.strategy_var.get()
        timeframe = self.timeframe_var.get()
        slippage = self.slippage_entry.get().strip()
        
        if not symbol or not quantity or not slippage:
            messagebox.showerror("Error", "Please fill all required fields")
            return
            
        try:
            quantity = int(quantity)
            max_slippage = float(slippage)
            
            # Get contract (simplified - in real app, use proper contract lookup)
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            self.status_var.set(f"Executing {action} order for {symbol} using {strategy} strategy...")
            
            # Execute order in background
            def execute_thread():
                try:
                    result = self.trading_engine.execute_smart_order(
                        contract=contract,
                        quantity=quantity,
                        direction=action,
                        max_slippage=max_slippage,
                        time_frame=timeframe,
                        strategy=strategy
                    )
                    
                    # Update UI with execution results
                    self.after(100, lambda: self.update_order_history(result))
                    self.status_var.set(f"Successfully executed {action} order for {symbol}")
                except Exception as e:
                    logger.error(f"Error executing order: {str(e)}")
                    self.after(100, lambda: messagebox.showerror("Error", f"Failed to execute order: {str(e)}"))
                    self.status_var.set(f"Error executing order: {str(e)}")
            
            threading.Thread(target=execute_thread, daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute order: {str(e)}")

    def place_advanced_order(self):
        """Place advanced order from trading panel"""
        if not hasattr(self, 'current_symbol') or not self.current_symbol:
            messagebox.showerror("Error", "Please lookup a contract first")
            return
            
        quantity = self.trade_quantity_entry.get().strip()
        action = self.trade_action_var.get()
        order_type = self.order_type_var.get()
        price = self.price_entry.get().strip()
        tif = self.tif_var.get()
        strategy = self.trade_strategy_var.get()
        timeframe = self.trade_timeframe_var.get()
        slippage = self.trade_slippage_entry.get().strip()
        
        if not quantity or (order_type != 'MKT' and not price) or not slippage:
            messagebox.showerror("Error", "Please fill all required fields")
            return
            
        try:
            quantity = int(quantity)
            max_slippage = float(slippage)
            limit_price = float(price) if price else 0.0
            
            contract = next(iter(self.contracts.values()))  # Get first contract
            
            self.status_var.set(f"Placing {action} order for {contract.symbol}...")
            
            # Place order in background
            def place_thread():
                try:
                    if strategy == 'MANUAL':
                        # Place manual order
                        order = Order()
                        order.action = action.upper()
                        order.totalQuantity = quantity
                        order.orderType = order_type
                        order.tif = tif
                        
                        if order_type in ['LMT', 'STP LMT']:
                            order.lmtPrice = limit_price
                        if order_type in ['STP', 'STP LMT']:
                            order.auxPrice = limit_price
                        
                        order_id = self.trading_engine.place_order(contract, order)
                        result = {'order_id': order_id, 'status': 'SUBMITTED'}
                    else:
                        # Use smart order routing
                        result = self.trading_engine.execute_smart_order(
                            contract=contract,
                            quantity=quantity,
                            direction=action,
                            max_slippage=max_slippage,
                            time_frame=timeframe,
                            strategy=strategy
                        )
                    
                    # Update UI with order details
                    self.after(100, lambda: self.update_order_history(result))
                    self.status_var.set(f"Successfully placed {action} order for {contract.symbol}")
                except Exception as e:
                    logger.error(f"Error placing order: {str(e)}")
                    self.after(100, lambda: messagebox.showerror("Error", f"Failed to place order: {str(e)}"))
                    self.status_var.set(f"Error placing order: {str(e)}")
            
            threading.Thread(target=place_thread, daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {str(e)}")

    def update_order_history(self, execution_result: Dict):
        """Update order history display"""
        try:
            order_id = execution_result.get('order_id')
            if not order_id:
                return
                
            # Get order details from trading engine
            order_status = self.trading_engine._active_orders.get(order_id, {})
            if not order_status:
                return
                
            contract = order_status['contract']
            order = order_status['order']
            
            # Add to activity tree
            timestamp = order_status['timestamp'].strftime("%H:%M:%S")
            symbol = contract.symbol
            action = order.action
            quantity = order.totalQuantity
            price = order.lmtPrice if order.lmtPrice else 'MARKET'
            status = order_status['status']
            slippage = f"{order_status.get('slippage', 0):.2f}%"
            
            self.activity_tree.insert("", tk.END, values=(
                timestamp, symbol, action, quantity, price, status, slippage
            ))
            
            # Update performance metrics
            self.update_performance_metrics()
            
            # Refresh orders display
            self.refresh_orders()
        except Exception as e:
            logger.error(f"Error updating order history: {str(e)}")

    def refresh_orders(self):
        """Refresh open orders display"""
        if not self.connected:
            return
            
        def refresh_thread():
            try:
                self.ib_api.reqAllOpenOrders()
                time.sleep(1)  # Wait for data
                
                # Update UI with open orders
                self.after(100, self.update_orders_display)
            except Exception as e:
                logger.error(f"Error refreshing orders: {str(e)}")
                self.status_var.set(f"Error refreshing orders: {str(e)}")
        
        threading.Thread(target=refresh_thread, daemon=True).start()

    def update_orders_display(self):
        """Update open orders display"""
        try:
            # Clear existing data
            for item in self.order_tree.get_children():
                self.order_tree.delete(item)
            
            # Add new data
            for order in self.ib_api._open_orders:
                contract = order['contract']
                order_info = order['order']
                order_state = order['orderState']
                
                filled = float(order_state.filled)
                remaining = float(order_state.remaining)
                
                self.order_tree.insert("", tk.END, values=(
                    order_info.orderId,
                    contract.symbol,
                    order_info.action,
                    order_info.totalQuantity,
                    order_info.orderType,
                    order_info.lmtPrice if order_info.lmtPrice else 'MARKET',
                    order_state.status,
                    filled,
                    remaining
                ))
        except Exception as e:
            logger.error(f"Error updating orders display: {str(e)}")

    def cancel_order(self):
        """Cancel selected order"""
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an order to cancel")
            return
            
        order_id = self.order_tree.item(selected[0], 'values')[0]
        
        try:
            order_id = int(order_id)
            self.status_var.set(f"Cancelling order {order_id}...")
            
            def cancel_thread():
                try:
                    self.ib_api.cancelOrder(order_id)
                    self.status_var.set(f"Order {order_id} cancellation requested")
                    
                    # Refresh orders display after cancellation
                    time.sleep(1)
                    self.after(100, self.refresh_orders)
                except Exception as e:
                    logger.error(f"Error cancelling order: {str(e)}")
                    self.after(100, lambda: messagebox.showerror("Error", f"Failed to cancel order: {str(e)}"))
                    self.status_var.set(f"Error cancelling order: {str(e)}")
            
            threading.Thread(target=cancel_thread, daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Invalid order ID")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel order: {str(e)}")

    def modify_order(self):
        """Modify selected order"""
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an order to modify")
            return
            
        # In a real app, implement proper order modification
        messagebox.showinfo("Info", "Order modification would be implemented here")

    def load_chart_data(self):
        """Load chart data for analytics"""
        symbol = self.analytics_symbol_entry.get().strip()
        timeframe = self.analytics_timeframe_var.get()
        periods = int(self.analytics_periods_var.get())
        
        if not symbol:
            messagebox.showerror("Error", "Please enter a symbol")
            return
            
        self.status_var.set(f"Loading {timeframe} chart data for {symbol}...")
        
        def load_thread():
            try:
                contract = Contract()
                contract.symbol = symbol
                contract.secType = "STK"
                contract.exchange = "SMART"
                contract.currency = "USD"
                
                # Determine duration string based on timeframe
                if timeframe.endswith('M'):
                    duration = f"{int(timeframe[:-1]) * periods} M"
                elif timeframe.endswith('H'):
                    duration = f"{int(timeframe[:-1]) * periods} H"
                elif timeframe.endswith('D'):
                    duration = f"{int(timeframe[:-1]) * periods} D"
                elif timeframe.endswith('W'):
                    duration = f"{int(timeframe[:-1]) * periods} W"
                else:  # Monthly
                    duration = f"{int(timeframe[:-1]) * periods} M"
                
                req_id = self.ib_api.next_valid_id
                self.ib_api.reqHistoricalData(
                    reqId=req_id,
                    contract=contract,
                    endDateTime="",
                    durationStr=duration,
                    barSizeSetting=timeframe,
                    whatToShow="TRADES",
                    useRTH=True,
                    formatDate=1,
                    keepUpToDate=False,
                    chartOptions=[]
                )
                
                # Wait for data
                time.sleep(2)
                
                # Update chart
                self.after(100, lambda: self.update_chart(req_id))
                self.status_var.set(f"Loaded {timeframe} chart data for {symbol}")
            except Exception as e:
                logger.error(f"Error loading chart data: {str(e)}")
                self.after(100, lambda: messagebox.showerror("Error", f"Failed to load chart data: {str(e)}"))
                self.status_var.set(f"Error loading chart data: {str(e)}")
        
        threading.Thread(target=load_thread, daemon=True).start()

    def update_chart(self, req_id: int):
        """Update price chart with historical data"""
        try:
            bars = self.ib_api._historical_data.get(req_id, [])
            if not bars:
                messagebox.showerror("Error", "No historical data received")
                return
                
            # Convert bars to DataFrame
            df = pd.DataFrame([{
                'Date': datetime.datetime.strptime(bar.date, '%Y%m%d %H:%M:%S'),
                'Open': bar.open,
                'High': bar.high,
                'Low': bar.low,
                'Close': bar.close,
                'Volume': bar.volume
            } for bar in bars])
            
            # Clear axes
            self.ax_price.clear()
            self.ax_volume.clear()
            
            # Plot candlesticks
            from mpl_finance import candlestick_ohlc
            import matplotlib.dates as mdates
            
            # Prepare data for candlestick plot
            quotes = []
            for idx, row in df.iterrows():
                date_num = mdates.date2num(row['Date'])
                quotes.append((date_num, row['Open'], row['High'], row['Low'], row['Close']))
            
            # Plot candlesticks
            candlestick_ohlc(self.ax_price, quotes, width=0.6/(len(quotes)**0.5), 
                            colorup='green', colordown='red')
            
            # Plot volume
            self.ax_volume.bar(df['Date'], df['Volume'], color=[
                'green' if close >= open_ else 'red' 
                for open_, close in zip(df['Open'], df['Close'])
            ], width=0.6/(len(quotes)**0.5))
            
            # Add indicators if enabled
            if self.show_vwap_var.get():
                vwap = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
                self.ax_price.plot(df['Date'], vwap, label='VWAP', color='blue', alpha=0.7)
            
            if self.show_poc_var.get():
                # Simplified POC calculation
                poc_price = df['Close'].mode()[0] if not df['Close'].mode().empty else df['Close'].iloc[-1]
                self.ax_price.axhline(poc_price, label='POC', color='purple', linestyle='--', alpha=0.7)
            
            if self.show_ma_var.get():
                try:
                    ma_period = int(self.ma_period_var.get())
                    ma = df['Close'].rolling(ma_period).mean()
                    self.ax_price.plot(df['Date'], ma, label=f'MA{ma_period}', color='orange', alpha=0.7)
                except ValueError:
                    pass
            
            # Format axes
            self.ax_price.set_title(f"{self.analytics_symbol_entry.get()} Price Chart")
            self.ax_price.grid(True, linestyle='--', alpha=0.7)
            self.ax_price.legend()
            
            self.ax_volume.set_title("Volume")
            self.ax_volume.grid(True, linestyle='--', alpha=0.7)
            
            # Rotate x-axis labels
            for ax in [self.ax_price, self.ax_volume]:
                for label in ax.get_xticklabels():
                    label.set_rotation(45)
                    label.set_horizontalalignment('right')
            
            # Update volume profile
            self.update_volume_profile(df)
            
            # Redraw canvas
            self.chart_canvas.draw()
        except Exception as e:
            logger.error(f"Error updating chart: {str(e)}")
            messagebox.showerror("Error", f"Failed to update chart: {str(e)}")

    def update_volume_profile(self, df: pd.DataFrame):
        """Update volume profile display"""
        try:
            self.profile_ax.clear()
            
            # Simplified volume profile calculation
            price_bins = np.linspace(df['Low'].min(), df['High'].max(), 20)
            volumes, prices = np.histogram(df['Close'], bins=price_bins, weights=df['Volume'])
            
            # Plot volume profile
            self.profile_ax.barh(prices[:-1], volumes, height=(prices[1]-prices[0]), 
                                color='skyblue', edgecolor='black')
            
            # Calculate and display stats
            vwap = (df['Close'] * df['Volume']).sum() / df['Volume'].sum()
            poc_price = prices[np.argmax(volumes)]
            total_volume = df['Volume'].sum()
            
            self.vwap_label.config(text=f"VWAP: {vwap:.2f}")
            self.poc_label.config(text=f"POC: {poc_price:.2f}")
            self.high_label.config(text=f"High: {df['High'].max():.2f}")
            self.low_label.config(text=f"Low: {df['Low'].min():.2f}")
            self.volume_label.config(text=f"Volume: {total_volume:,}")
            
            # Calculate value area (simplified)
            sorted_indices = np.argsort(volumes)[::-1]
            cumulative_volume = 0
            value_area_vol = 0.7 * total_volume
            value_prices = []
            
            for idx in sorted_indices:
                cumulative_volume += volumes[idx]
                value_prices.append(prices[idx])
                if cumulative_volume >= value_area_vol:
                    break
                    
            value_area = f"{min(value_prices):.2f} - {max(value_prices):.2f}"
            self.value_area_label.config(text=f"Value Area (70%): {value_area}")
            
            # Redraw canvas
            self.profile_canvas.draw()
        except Exception as e:
            logger.error(f"Error updating volume profile: {str(e)}")

    def show_new_order_dialog(self):
        """Show new order dialog"""
        # In a real app, implement a proper order dialog
        messagebox.showinfo("Info", "New order dialog would open here")

    def show_order_history(self):
        """Show order history dialog"""
        # In a real app, implement a proper history dialog
        messagebox.showinfo("Info", "Order history dialog would open here")

    def show_position_manager(self):
        """Show position manager dialog"""
        # In a real app, implement a proper position manager
        messagebox.showinfo("Info", "Position manager dialog would open here")

    def show_market_scanner(self):
        """Show market scanner dialog"""
        # In a real app, implement a proper market scanner
        messagebox.showinfo("Info", "Market scanner dialog would open here")

    def show_volume_profile(self):
        """Show volume profile dialog"""
        # In a real app, implement a proper volume profile viewer
        messagebox.showinfo("Info", "Volume profile dialog would open here")

    def show_vwap_analysis(self):
        """Show VWAP analysis dialog"""
        # In a real app, implement a proper VWAP analyzer
        messagebox.showinfo("Info", "VWAP analysis dialog would open here")

    def show_poc_analysis(self):
        """Show POC analysis dialog"""
        # In a real app, implement a proper POC analyzer
        messagebox.showinfo("Info", "POC analysis dialog would open here")

    def show_portfolio_metrics(self):
        """Show portfolio metrics dialog"""
        # In a real app, implement a proper portfolio metrics viewer
        messagebox.showinfo("Info", "Portfolio metrics dialog would open here")

    def show_risk_analysis(self):
        """Show risk analysis dialog"""
        # In a real app, implement a proper risk analyzer
        messagebox.showinfo("Info", "Risk analysis dialog would open here")

    def show_portfolio_optimization(self):
        """Show portfolio optimization dialog"""
        # In a real app, implement a proper portfolio optimizer
        messagebox.showinfo("Info", "Portfolio optimization dialog would open here")

    def show_performance_attribution(self):
        """Show performance attribution dialog"""
        # In a real app, implement a proper performance attribution tool
        messagebox.showinfo("Info", "Performance attribution dialog would open here")

    def show_settings(self):
        """Show settings dialog"""
        # In a real app, implement a proper settings dialog
        messagebox.showinfo("Info", "Settings dialog would open here")

    def show_documentation(self):
        """Open documentation in browser"""
        webbrowser.open(f"{WEBSITE_URL}/docs")

    def show_about(self):
        """Show about dialog"""
        about_text = (f"{APP_NAME} - Professional Trading System\n"
                     f"Version {VERSION}\n\n"
                     f"© {datetime.datetime.now().year} {COMPANY_NAME}\n"
                     f"All rights reserved\n\n"
                     f"Contact: {SUPPORT_EMAIL}\n"
                     f"Website: {WEBSITE_URL}")
        messagebox.showinfo("About", about_text)

    def on_close(self):
        """Handle application close"""
        try:
            self.disconnect_from_ibkr()
            self._save_settings()
            self.destroy()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            self.destroy()

# Installer Application
class TradingSystemInstaller(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} Installer")
        self.geometry("600x400")
        
        # Installation variables
        self.install_path = tk.StringVar(value=INSTALL_DIR)
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_menu_shortcut = tk.BooleanVar(value=True)
        self.accept_license = tk.BooleanVar(value=False)
        
        # Create UI
        self.create_widgets()
        
        # Load license text
        self.load_license_text()
    
    def create_widgets(self):
        """Create installer UI widgets"""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text=f"{APP_NAME} Setup", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)
        
        # Main notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Welcome page
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="Welcome")
        
        welcome_text = (f"Welcome to the {APP_NAME} Setup Wizard\n\n"
                       "This will install {APP_NAME} on your computer.\n\n"
                       "Click Next to continue, or Cancel to exit Setup.")
        ttk.Label(welcome_frame, text=welcome_text, justify=tk.CENTER).pack(expand=True, padx=20, pady=20)
        
        # License agreement page
        license_frame = ttk.Frame(self.notebook)
        self.notebook.add(license_frame, text="License Agreement")
        
        license_text_frame = ttk.Frame(license_frame)
        license_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(license_text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.license_text = tk.Text(license_text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.license_text.pack(fill=tk.BOTH, expand=True)
        self.license_text.config(state=tk.DISABLED)
        
        scrollbar.config(command=self.license_text.yview)
        
        accept_frame = ttk.Frame(license_frame)
        accept_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(accept_frame, text="I accept the license agreement", 
                       variable=self.accept_license).pack(anchor=tk.W)
        
        # Installation location page
        location_frame = ttk.Frame(self.notebook)
        self.notebook.add(location_frame, text="Installation Location")
        
        ttk.Label(location_frame, text="Install to:").pack(anchor=tk.W, padx=10, pady=5)
        
        path_frame = ttk.Frame(location_frame)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Entry(path_frame, textvariable=self.install_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="Browse...", command=self.browse_install_path).pack(side=tk.LEFT, padx=5)
        
        # Shortcuts page
        shortcuts_frame = ttk.Frame(self.notebook)
        self.notebook.add(shortcuts_frame, text="Shortcuts")
        
        ttk.Checkbutton(shortcuts_frame, text="Create desktop shortcut", 
                       variable=self.create_desktop_shortcut).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Checkbutton(shortcuts_frame, text="Create Start Menu shortcut", 
                       variable=self.create_start_menu_shortcut).pack(anchor=tk.W, padx=10, pady=5)
        
        # Ready to install page
        ready_frame = ttk.Frame(self.notebook)
        self.notebook.add(ready_frame, text="Ready to Install")
        
        ready_text = (f"Setup is now ready to install {APP_NAME} on your computer.\n\n"
                     "Click Install to continue with the installation, or Back if you want to review or change any settings.")
        ttk.Label(ready_frame, text=ready_text, justify=tk.CENTER).pack(expand=True, padx=20, pady=20)
        
        # Installation progress page
        self.progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.progress_frame, text="Installing")
        
        self.progress_label = ttk.Label(self.progress_frame, text="Installing...")
        self.progress_label.pack(pady=10)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.pack(pady=10)
        
        self.status_label = ttk.Label(self.progress_frame, text="")
        self.status_label.pack(pady=5)
        
        # Completion page
        self.complete_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.complete_frame, text="Complete")
        
        complete_text = (f"{APP_NAME} has been successfully installed on your computer.\n\n"
                        "Click Finish to close Setup.")
        self.complete_label = ttk.Label(self.complete_frame, text=complete_text, justify=tk.CENTER)
        self.complete_label.pack(expand=True, padx=20, pady=20)
        
        # Navigation buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.back_button = ttk.Button(button_frame, text="< Back", command=self.prev_page)
        self.back_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(button_frame, text="Next >", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Disable back button on first page
        self.back_button.config(state=tk.DISABLED)
        
        # Track current page
        self.current_page = 0
    
    def load_license_text(self):
        """Load license text from file or URL"""
        try:
            # Try to load from local file first
            license_file = os.path.join(os.path.dirname(__file__), "LICENSE.txt")
            if os.path.exists(license_file):
                with open(license_file, "r") as f:
                    license_content = f.read()
            else:
                # Fall back to fetching from web
                import requests
                response = requests.get(LICENSE_URL)
                response.raise_for_status()
                license_content = response.text
            
            self.license_text.config(state=tk.NORMAL)
            self.license_text.delete(1.0, tk.END)
            self.license_text.insert(tk.END, license_content)
            self.license_text.config(state=tk.DISABLED)
        except Exception as e:
            self.license_text.config(state=tk.NORMAL)
            self.license_text.delete(1.0, tk.END)
            self.license_text.insert(tk.END, f"Failed to load license text: {str(e)}")
            self.license_text.config(state=tk.DISABLED)
    
    def browse_install_path(self):
        """Browse for installation path"""
        path = filedialog.askdirectory(initialdir=self.install_path.get())
        if path:
            self.install_path.set(path)
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.notebook.select(self.current_page)
            self.next_button.config(text="Next >")
            
            if self.current_page == 0:
                self.back_button.config(state=tk.DISABLED)
            
            if self.current_page < self.notebook.index("end") - 2:
                self.next_button.config(state=tk.NORMAL)
    
    def next_page(self):
        """Go to next page or start installation"""
        if self.current_page == 1 and not self.accept_license.get():
            messagebox.showerror("Error", "You must accept the license agreement to continue")
            return
        
        if self.current_page < self.notebook.index("end") - 2:
            self.current_page += 1
            self.notebook.select(self.current_page)
            self.back_button.config(state=tk.NORMAL)
            
            if self.current_page == self.notebook.index("end") - 2:
                self.next_button.config(text="Install")
            else:
                self.next_button.config(text="Next >")
        elif self.current_page == self.notebook.index("end") - 2:
            # Start installation
            self.start_installation()
        else:
            # Installation complete
            self.destroy()
            self.launch_application()
    
    def start_installation(self):
        """Start the installation process"""
        self.notebook.select(self.current_page + 1)
        self.back_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)
        
        # Start installation in background
        threading.Thread(target=self.install_files, daemon=True).start()
    
    def install_files(self):
        """Install application files"""
        try:
            install_dir = self.install_path.get()
            
            # Create installation directory
            self.update_status("Creating installation directory...", 10)
            os.makedirs(install_dir, exist_ok=True)
            
            # Copy files (in a real installer, this would copy actual files)
            self.update_status("Copying application files...", 30)
            time.sleep(1)  # Simulate file copy
            
            # Create executable using PyInstaller
            self.update_status("Creating executable...", 50)
            self.create_executable(install_dir)
            
            # Create shortcuts if requested
            if self.create_desktop_shortcut.get():
                self.update_status("Creating desktop shortcut...", 70)
                self.create_shortcut(os.path.join(install_dir, f"{APP_NAME}.exe"), DESKTOP_SHORTCUT)
            
            if self.create_start_menu_shortcut.get():
                self.update_status("Creating Start Menu shortcut...", 80)
                os.makedirs(START_MENU_DIR, exist_ok=True)
                self.create_shortcut(os.path.join(install_dir, f"{APP_NAME}.exe"), 
                                    os.path.join(START_MENU_DIR, f"{APP_NAME}.lnk"))
            
            # Add registry entries (Windows only)
            if platform.system() == "Windows":
                self.update_status("Updating registry...", 90)
                try:
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY)
                    winreg.SetValueEx(key, "InstallPath", 0, winreg.REG_SZ, install_dir)
                    winreg.SetValueEx(key, "Version", 0, winreg.REG_SZ, VERSION)
                    winreg.CloseKey(key)
                except Exception as e:
                    logger.warning(f"Failed to update registry: {str(e)}")
            
            # Installation complete
            self.update_status("Installation complete!", 100)
            self.next_button.config(state=tk.NORMAL, text="Finish")
            self.cancel_button.config(state=tk.NORMAL, text="Close")
        except Exception as e:
            self.update_status(f"Installation failed: {str(e)}", 0)
            messagebox.showerror("Error", f"Installation failed: {str(e)}")
            self.destroy()
    
    def create_executable(self, install_dir: str):
        """Create executable using PyInstaller"""
        try:
            # Create a temporary spec file
            spec_content = f"""
# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('{APP_NAME}')

block_cipher = None

a = Analysis(['{__file__}'],
             pathex=[],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='{APP_NAME}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='{APP_NAME}')
"""
            # Write spec file
            spec_file = os.path.join(tempfile.gettempdir(), f"{APP_NAME}.spec")
            with open(spec_file, 'w') as f:
                f.write(spec_content)
            
            # Run PyInstaller
            subprocess.run([
                sys.executable,
                "-m", "PyInstaller",
                "--distpath", install_dir,
                "--workpath", os.path.join(tempfile.gettempdir(), "build"),
                "--noconfirm",
                spec_file
            ], check=True)
            
        except Exception as e:
            raise InstallationError(f"Failed to create executable: {str(e)}")
    
    def create_shortcut(self, target: str, shortcut_path: str):
        """Create a Windows shortcut"""
        try:
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.save()
        except Exception as e:
            logger.warning(f"Failed to create shortcut: {str(e)}")
    
    def update_status(self, message: str, progress: int):
        """Update installation progress"""
        self.status_label.config(text=message)
        self.progress_bar["value"] = progress
        self.update()
    
    def launch_application(self):
        """Launch the installed application"""
        install_dir = self.install_path.get()
        exe_path = os.path.join(install_dir, f"{APP_NAME}.exe")
        
        try:
            subprocess.Popen([exe_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch application: {str(e)}")

# Main entry point
if __name__ == "__main__":
    # Check if we're running as installer or application
    if "--install" in sys.argv:
        installer = TradingSystemInstaller()
        installer.mainloop()
    else:
        # Check if installed
        try:
            # Try to read registry to find installation path
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY)
            install_path = winreg.QueryValueEx(key, "InstallPath")[0]
            winreg.CloseKey(key)
            
            # Verify installation
            exe_path = os.path.join(install_path, f"{APP_NAME}.exe")
            if not os.path.exists(exe_path):
                raise FileNotFoundError("Installation not found")
            
            # Launch installed version
            subprocess.Popen([exe_path])
        except Exception:
            # Not installed or error accessing installed version - run in portable mode
            app = TradingApp()
            app.mainloop()