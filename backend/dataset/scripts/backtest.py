import pandas as pd
import numpy as np

class Backtester:
    def __init__(self, filepath, strategy, initial_capital=10000, commission=0.001, start_date=None, end_date=None):
        """
        :param filepath: Path to the CSV data file.
        :param strategy: Function or class that takes a DataFrame and returns specific signals.
        :param initial_capital: Starting money.
        :param commission: Transaction cost per trade (e.g., 0.001 = 0.1%).
        :param start_date: Filter data start (YYYY-MM-DD).
        :param end_date: Filter data end (YYYY-MM-DD).
        """
        self.filepath = filepath
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.data = pd.read_csv(filepath)
        self.data['datetime'] = pd.to_datetime(self.data['timestamp'], unit='ms')
        self.data.set_index('datetime', inplace=True)
        
        # Date Filtering
        if start_date:
            self.data = self.data[self.data.index >= pd.to_datetime(start_date)]
        if end_date:
            self.data = self.data[self.data.index <= pd.to_datetime(end_date)]
            
        self.results = {}

    def run(self):
        # Apply strategy to get signals
        self.data = self.strategy.generate_signals(self.data)
        
        # Simulation Setup
        balance = self.initial_capital
        position = 0  # 0: None, 1: Long, -1: Short
        entry_price = 0.0
        shares = 0.0
        
        equity_curve = []
        trades = []
        
        # Pre-extract numpy arrays for speed (Vectorization)
        # 100x faster than .iloc inside loop
        n = len(self.data)
        closes = self.data['close'].values
        signals = self.data['signal'].values
        dates = self.data.index.values # PeriodIndex or DatetimeIndex
        
        # Loop
        for i in range(n):
            price = closes[i]
            signal = signals[i]
            date = dates[i]
            
            # --- Position Management ---
            
            # 1. Close Existing Position
            if position == 1 and (signal == -1 or signal == 0):
                # Close Long
                proceeds = shares * price * (1 - self.commission)
                balance = proceeds
                
                # PnL Calc
                last_trade_cap = trades[-1]['capital']
                trade_pnl = balance - last_trade_cap
                
                trades.append({
                    'type': 'SELL_CLOSE',
                    'date': date,
                    'price': price,
                    'capital': balance,
                    'pnl': trade_pnl
                })
                position = 0
                shares = 0
                entry_price = 0

            elif position == -1 and (signal == 1 or signal == 0):
                # Close Short
                # Cost to Close
                # cost_close = abs(shares) * price * (1 + self.commission) # Unused
                
                # Gross PnL
                gross_pnl = (entry_price - price) * abs(shares)
                
                # Net PnL (we need to deduct open/close costs from collateral?)
                # Simplified Cash Model:
                # We assume we put up 'balance' as collateral.
                # Balance matches current cash.
                # On Entry, Balance -> 0 (Locked).
                
                # Restore Collateral
                collateral = trades[-1]['collateral'] # Last specific short entry? 
                # Actually trades[-1] is the entry.
                
                # Cost of Open (was it deducted?)
                # Logic below: balance = 0.
                # Let's assume commission is paid from PnL or Collateral.
                cost_open = abs(shares) * entry_price * self.commission
                
                # Net = Gross - OpenComm - CloseComm
                net_pnl = gross_pnl - cost_open - (abs(shares) * price * self.commission)
                
                balance = collateral + net_pnl
                
                trades.append({
                    'type': 'BUY_COVER',
                    'date': date,
                    'price': price,
                    'capital': balance,
                    'pnl': net_pnl
                })
                position = 0
                shares = 0
                entry_price = 0
                
            # 2. Open New Position
            if position == 0:
                if signal == 1:
                    # Open Long
                    cost = balance * self.commission
                    net_balance = balance - cost
                    shares = net_balance / price
                    trades.append({'type': 'BUY_LONG', 'date': date, 'price': price, 'capital': balance}) 
                    balance = 0 
                    position = 1
                    entry_price = price
                    
                elif signal == -1:
                    # Open Short
                    # Collateral = Balance
                    collateral = balance
                    # Shares = - (Collateral / Price)
                    shares = - (collateral / price)
                    
                    trades.append({'type': 'SELL_SHORT', 'date': date, 'price': price, 'capital': balance, 'collateral': collateral})
                    balance = 0
                    position = -1
                    entry_price = price
            
            # Current Equity Calc (Mark to Market)
            if position == 1:
                current_equity = shares * price
            elif position == -1:
                # Equity = Collateral + PnL
                collateral = trades[-1]['collateral']
                pnl = (entry_price - price) * abs(shares)
                current_equity = collateral + pnl
            else:
                current_equity = balance
            
            equity_curve.append(current_equity)

        # Store Results
        self.data['equity'] = equity_curve
        final_equity = equity_curve[-1] if equity_curve else self.initial_capital
        
        # Trade Analysis
        completed_trades = [t for t in trades if 'pnl' in t]
        wins = [t for t in completed_trades if t['pnl'] > 0]
        loss_trades = [t for t in completed_trades if t['pnl'] <= 0]
        
        win_rate = (len(wins) / len(completed_trades) * 100) if completed_trades else 0.0
        
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.abs(np.mean([t['pnl'] for t in loss_trades])) if loss_trades else 0
        ratio = (avg_win / avg_loss) if avg_loss > 0 else 0
        
        self.results = {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': (final_equity - self.initial_capital) / self.initial_capital * 100,
            'trades_count': len(completed_trades),
            'max_drawdown': 0.0, # Placeholder, calc below
            'win_rate': win_rate,
            'profit_factor': ratio,
            'trades': trades
        }
        
        # Max DD Calc
        if equity_curve:
            eq_series = pd.Series(equity_curve)
            peak = eq_series.cummax()
            dd = (eq_series - peak) / peak
            self.results['max_drawdown'] = dd.min() * 100
            
        return self.results

    def summary(self):
        return (f"Initial: ${self.results['initial_capital']:.2f} | "
                f"Final: ${self.results['final_equity']:.2f} | "
                f"Return: {self.results['total_return']:.2f}% | "
                f"Trades: {self.results['trades_count']}")
