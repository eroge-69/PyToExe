# nano_optimized_trader.py
import math
from decimal import Decimal, getcontext

class NanoOptimizedTrader(UltraOptimizedTrader):
    def __init__(self, initial_capital=10000):
        super().__init__()
        getcontext().prec = 6  # Precision for small account calculations
        self.MIN_LOT_SIZE = 100  # ₹100 minimum increment
        self.brokerage_model = {
            'equity': {
                'intraday': Decimal('0.00025'),  # 0.025%
                'delivery': Decimal('0.0001')    # 0.01%
            },
            'min_brokerage': Decimal('20')       # ₹20 minimum
        }
        
        # Adaptive thresholds for small accounts
        self.params.update({
            'micro': {
                'min_position': 100,          # ₹100 minimum
                'max_risk_ratio': Decimal('0.1'),  # 10% max allocation
                'brokerage_coverage': 3       # 3x brokerage as min profit
            }
        })

    def calculate_nano_position(self, symbol, risk_pct=0.01):
        """
        Enhanced position sizing for small accounts
        Returns: (quantity, price, order_type)
        """
        # Get volatility-adjusted base size
        base_size = super().calculate_position_size(symbol)
        
        # Apply small account constraints
        risk_amount = Decimal(str(self.portfolio_value)) * Decimal(str(risk_pct))
        max_position = Decimal(str(self.portfolio_value)) * self.params['micro']['max_risk_ratio']
        
        # Final position size (₹100 increments)
        final_amount = min(risk_amount, max_position, Decimal(str(base_size)))
        rounded_amount = self._round_to_lot(final_amount)
        
        # Convert to quantity
        price = Decimal(str(self.get_current_price(symbol)))
        quantity = int(rounded_amount / price)
        
        # Ensure minimum profitability
        min_profit = self._calculate_min_profit(quantity, price)
        if min_profit > (rounded_amount * Decimal('0.1')):  # >10% of position
            return 0, 0.0, 'SKIP'  # Skip unprofitable trades
        
        return quantity, float(price), 'LIMIT'

    def _round_to_lot(self, amount):
        """Round to nearest ₹100 increment"""
        return Decimal(math.floor(float(amount) / self.MIN_LOT_SIZE)) * self.MIN_LOT_SIZE

    def _calculate_min_profit(self, quantity, price):
        """Ensure 3x brokerage coverage"""
        trade_value = Decimal(quantity) * Decimal(str(price))
        brokerage = max(
            trade_value * self.brokerage_model['equity']['intraday'],
            self.brokerage_model['min_brokerage']
        )
        return brokerage * self.params['micro']['brokerage_coverage']

    def execute_order(self, symbol, amount):
        """Enhanced execution for small lots"""
        quantity, price, order_type = self.calculate_nano_position(symbol)
        
        if order_type == 'SKIP':
            return None
            
        # Apply nano-order execution improvements
        if quantity < 1:
            return None
            
        if price * quantity < self.params['micro']['min_position']:
            return self._execute_micro_lot(symbol, quantity, price)
            
        return super().execute_order(symbol, amount)

    def _execute_micro_lot(self, symbol, quantity, price):
        """Special handling for <₹100 positions"""
        # Bundle with other micro orders
        if self._should_bundle():
            return self._bundle_execution(symbol, quantity, price)
            
        # Use odd-lot market order
        return self.broker.place_order(
            symbol=symbol,
            quantity=quantity,
            price=price,
            type='MARKET_LIMIT',  # Special order type
            validity='IOC'         # Immediate or cancel
        )

    def _should_bundle(self):
        """Check if micro orders should be bundled"""
        pending_micro = self._count_pending_micro_orders()
        return pending_micro >= 3 or (
            time.time() - self.last_bundle > 300  # 5 minutes
        )

    def _bundle_execution(self, symbols, quantities, prices):
        """Execute multiple micro orders as one"""
        # Implementation varies by broker API
        pass

    # Preserved existing optimizations
    def process_market_data(self, tick):
        """Inherits GPU-accelerated processing"""
        return super().process_market_data(tick)
        
    def detect_market_regime(self):
        """Keeps HMM-based regime detection"""
        return super().detect_market_regime()