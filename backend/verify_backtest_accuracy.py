"""
Complete Backtest Verification - Production Grade

This script runs REAL backtests using the actual strategy code and compares
with pre-generated results in backend/data/strategies/.

It properly:
1. Loads historical OHLCV data from velasccxt
2. Runs strategies to generate signals with entry/tp/sl
3. Simulates trade outcomes based on actual price action
4. Compares with pre-computed files

Usage:
    python verify_backtest_accuracy.py [--tokens BTC ETH] [--period 2Y] [--verbose]
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from strategies.registry import get_registry, load_default_strategies

# Mapping
FOLDER_TO_STRATEGY = {
    "TitanBreakout": "donchian_v2",
    "FlowMaster": "trend_following_native_v1",
    "MeanReversion": "mean_reversion_v1",
}

TOKENS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
TIMEFRAMES_MAP = {"1H": "1h", "4H": "4h"}
PERIODS = ["6M", "2Y", "5Y"]

VELAS_DIR = Path("C:/Users/lukx/Desktop/velasccxt")
DATA_DIR = Path(__file__).parent / "data" / "strategies"


class BacktestEngine:
    """Full backtest engine with proper trade simulation."""
    
    def __init__(self, velas_dir: Path):
        self.velas_dir = velas_dir
        self.cache = {}
        self.registry = get_registry()
        load_default_strategies()
    
    def load_ohlcv(self, token: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Load and cache OHLCV data."""
        key = f"{token}_{timeframe}"
        if key in self.cache:
            return self.cache[key]
        
        file_path = self.velas_dir / f"{token}_{timeframe}.csv"
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_csv(file_path)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.sort_values('datetime').reset_index(drop=True)
            
            # Ensure float types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            self.cache[key] = df
            return df
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None
    
    def filter_by_period(self, df: pd.DataFrame, period: str) -> pd.DataFrame:
        """Filter by period."""
        now = datetime.utcnow()
        
        if period == "6M":
            cutoff = now - timedelta(days=180)
        elif period == "2Y":
            cutoff = now - timedelta(days=730)
        elif period == "5Y":
            cutoff = now - timedelta(days=1825)
        else:
            cutoff = now - timedelta(days=730)
        
        return df[df['datetime'] >= cutoff].copy()
    
    def simulate_trade(self, signal_dict: Dict, future_bars: pd.DataFrame) -> Tuple[str, float]:
        """
        Simulate a trade based on signal and future price action.
        
        Returns:
            (result, pnl_r) where result is 'WIN' or 'LOSS'
        """
        entry = signal_dict['entry']
        tp = signal_dict['tp']
        sl = signal_dict['sl']
        direction = signal_dict['direction'].lower()
        
        for idx, row in future_bars.iterrows():
            high = row['high']
            low = row['low']
            
            if direction == 'long':
                # Check if TP hit
                if high >= tp:
                    # Calculate R (should be ~2.2R typically)
                    risk = entry - sl
                    reward = tp - entry
                    r = reward / risk if risk > 0 else 0
                    return ('WIN', round(r, 1))
                
                # Check if SL hit
                if low <= sl:
                    return ('LOSS', -1.0)
            
            elif direction == 'short':
                # Check if TP hit
                if low <= tp:
                    risk = sl - entry
                    reward = entry - tp
                    r = reward / risk if risk > 0 else 0
                    return ('WIN', round(r, 1))
                
                # Check if SL hit
                if high >= sl:
                    return ('LOSS', -1.0)
        
        # Trade didn't close in available bars (open trade)
        return ('OPEN', 0.0)
    
    def run_backtest(
        self,
        strategy_id: str,
        token: str,
        timeframe: str,
        period: str,
        verbose: bool = False
    ) -> Optional[Dict]:
        """
        Run complete backtest for a strategy configuration.
        
        Returns:
            {'total_trades', 'win_rate', 'net_profit', 'wins', 'losses', 'trades': [...]}
        """
        # Load data
        df = self.load_ohlcv(token, timeframe)
        if df is None:
            if verbose:
                print(f"  No data for {token} {timeframe}")
            return None
        
        # Filter by period
        df_period = self.filter_by_period(df, period)
        
        if len(df_period) < 100:
            if verbose:
                print(f"  Insufficient data: {len(df_period)} bars")
            return None
        
        # Get strategy
        strategy = self.registry.get(strategy_id)
        if not strategy:
            if verbose:
                print(f"  Strategy {strategy_id} not found")
            return None
        
        # Run backtest by sliding window
        trades = []
        
        # We need a lookback window for indicators (200 bars min)
        lookback = 200
        
        for i in range(lookback, len(df_period)):
            # Get window for this iteration
            window = df_period.iloc[max(0, i-lookback):i+1].copy()
            
            # Prepare context
            context = {
                "data": {
                    token: window[['open', 'high', 'low', 'close', 'volume']].to_dict('records')
                }
            }
            
            try:
                # Generate signal
                signals = strategy.generate_signals([token], timeframe, context)
                
                if signals:
                    for signal in signals:
                        # Get future bars for simulation (next 50 bars or until end)
                        future_start = i + 1
                        future_end = min(i + 51, len(df_period))
                        future_bars = df_period.iloc[future_start:future_end]
                        
                        if len(future_bars) < 5:
                            continue
                        
                        # Convert signal to dict
                        signal_dict = {
                            'entry': signal.entry,
                            'tp': signal.tp,
                            'sl': signal.sl,
                            'direction': signal.direction,
                            'timestamp': df_period.iloc[i]['datetime'],
                            'price': df_period.iloc[i]['close']
                        }
                        
                        # Simulate trade
                        result, pnl_r = self.simulate_trade(signal_dict, future_bars)
                        
                        if result in ['WIN', 'LOSS']:
                            trades.append({
                                'timestamp': signal_dict['timestamp'],
                                'direction': signal_dict['direction'],
                                'entry': signal_dict['entry'],
                                'result': result,
                                'pnl_r': pnl_r
                            })
            
            except Exception as e:
                if verbose:
                    print(f"  Error at bar {i}: {e}")
                continue
        
        # Calculate metrics
        wins = len([t for t in trades if t['result'] == 'WIN'])
        losses = len([t for t in trades if t['result'] == 'LOSS'])
        total = wins + losses
        
        if total == 0:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'net_profit': 0.0,
                'wins': 0,
                'losses': 0,
                'trades': []
            }
        
        win_rate = (wins / total) * 100
        net_profit = sum([t['pnl_r'] for t in trades])
        
        return {
            'total_trades': total,
            'win_rate': round(win_rate, 1),
            'net_profit': round(net_profit, 1),
            'wins': wins,
            'losses': losses,
            'trades': trades
        }
    
    def parse_expected_results(self, folder: str, period: str, token: str, timeframe: str) -> Optional[Dict]:
        """Parse pre-generated result file."""
        file_path = DATA_DIR / folder / period / f"{token}{timeframe}.txt"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = {}
            for line in content.split('\n'):
                if "Total Trades:" in line:
                    result['total_trades'] = int(line.split(':')[1].strip())
                elif "Win Rate:" in line:
                    result['win_rate'] = float(line.split(':')[1].strip().replace('%', ''))
                elif "Total Net Profit:" in line:
                    result['net_profit'] = float(line.split(':')[1].strip().replace('R', ''))
                elif "Wins:" in line and "|" in line:
                    parts = line.split('|')
                    result['wins'] = int(parts[0].split(':')[1].strip())
                    result['losses'] = int(parts[1].split(':')[1].strip())
            
            return result
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def compare(self, actual: Dict, expected: Dict) -> Tuple[bool, List[str], float]:
        """
        Compare actual vs expected.
        
        Returns:
            (is_close_match, differences, similarity_score)
        """
        diffs = []
        
        # Calculate similarity score (0-100)
        score = 100.0
        
        # Total trades (10% weight)
        if actual['total_trades'] != expected['total_trades']:
            diff_pct = abs(actual['total_trades'] - expected['total_trades']) / max(expected['total_trades'], 1) * 100
            score -= min(10, diff_pct / 10)
            diffs.append(f"Trades: {actual['total_trades']} vs {expected['total_trades']}")
        
        # Win rate (40% weight)
        wr_diff = abs(actual['win_rate'] - expected['win_rate'])
        if wr_diff > 5.0:  # More than 5% different
            score -= min(40, wr_diff * 2)
            diffs.append(f"WinRate: {actual['win_rate']}% vs {expected['win_rate']}%")
        
        # Net profit (30% weight)
        if expected['net_profit'] != 0:
            profit_diff_pct = abs(actual['net_profit'] - expected['net_profit']) / abs(expected['net_profit']) * 100
            score -= min(30, profit_diff_pct / 10)
        if abs(actual['net_profit'] - expected['net_profit']) > 5.0:
            diffs.append(f"Profit: {actual['net_profit']}R vs {expected['net_profit']}R")
        
        # Wins/Losses (20% weight combined)
        if actual['wins'] != expected['wins']:
            score -= 10
            diffs.append(f"Wins: {actual['wins']} vs {expected['wins']}")
        if actual['losses'] != expected['losses']:
            score -= 10
            diffs.append(f"Losses: {actual['losses']} vs {expected['losses']}")
        
        is_close = score >= 80.0  # 80%+ similarity = close match
        
        return (is_close, diffs, round(score, 1))


def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--tokens', nargs='+', default=TOKENS)
    parser.add_argument('--period', default='2Y', choices=PERIODS)
    parser.add_argument('--timeframe', default='4H', choices=['1H', '4H'])
    parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    
    if not VELAS_DIR.exists():
        print(f"ERROR: Data directory not found: {VELAS_DIR}")
        sys.exit(1)
    
    engine = BacktestEngine(VELAS_DIR)
    
    print("=" * 80)
    print("BACKTEST ACCURACY VERIFICATION")
    print("=" * 80)
    print()
    
    results = []
    
    for folder, strategy_id in FOLDER_TO_STRATEGY.items():
        print(f"\nStrategy: {folder} ({strategy_id})")
        print("-" * 80)
        
        for token in args.tokens:
            tf_code = TIMEFRAMES_MAP[args.timeframe]
            
            print(f"\n  {token} {args.timeframe} {args.period}:")
            
            # Run backtest
            actual = engine.run_backtest(strategy_id, token, tf_code, args.period, args.verbose)
            
            if not actual:
                print("    ⚠️  Skipped (no data)")
                continue
            
            # Load expected
            expected = engine.parse_expected_results(folder, args.period, token, args.timeframe)
            
            if not expected:
                print("    ⚠️  No expected results file")
                continue
            
            # Compare
            is_match, diffs, score = engine.compare(actual, expected)
            
            print(f"    Similarity: {score}%")
            print(f"    Actual:   {actual['total_trades']} trades, {actual['win_rate']}% WR, {actual['net_profit']}R")
            print(f"    Expected: {expected['total_trades']} trades, {expected['win_rate']}% WR, {expected['net_profit']}R")
            
            if is_match:
                print(f"    ✅ CLOSE MATCH")
            else:
                print(f"    ⚠️  DISCREPANCY:")
                for diff in diffs:
                    print(f"       - {diff}")
            
            results.append({
                'strategy': folder,
                'token': token,
                'timeframe': args.timeframe,
                'period': args.period,
                'match': is_match,
                'score': score,
                'actual': actual,
                'expected': expected
            })
    
    # Summary
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Configs Tested: {len(results)}")
    print(f"Close Matches: {len([r for r in results if r['match']])}")
    print(f"Discrepancies: {len([r for r in results if not r['match']])}")
    
    if results:
        avg_score = sum([r['score'] for r in results]) / len(results)
        print(f"Average Similarity: {avg_score:.1f}%")
    
    # Save report
    report_path = Path("backtest_accuracy_report.json")
    with open(report_path, 'w') as f:
        # Convert trades to serializable format
        for r in results:
            if 'actual' in r and 'trades' in r['actual']:
                for trade in r['actual']['trades']:
                    trade['timestamp'] = trade['timestamp'].isoformat()
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Report saved: {report_path}")


if __name__ == "__main__":
    main()
