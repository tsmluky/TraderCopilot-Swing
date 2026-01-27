"""
Real Backtest Verification Script

This script:
1. Loads historical OHLCV data from C:/Users/lukx/Desktop/velasccxt/*.csv
2. Runs each strategy with real data
3. Compares results with pre-computed files in backend/data/strategies/
4. Reports discrepancies

Usage:
    python run_backtest_verification.py [--sample 5] [--verbose]
"""

import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from strategies.registry import get_registry, load_default_strategies

# Mapping of folder names to strategy IDs
FOLDER_TO_STRATEGY = {
    "TitanBreakout": "donchian_v2",
    "FlowMaster": "trend_following_native_v1",
    "MeanReversion": "mean_reversion_v1",
}

TOKENS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
TIMEFRAMES_MAP = {"1H": "1h", "4H": "4h"}  # File -> Code
PERIODS = ["6M", "2Y", "5Y"]

# Data paths
VELAS_DIR = Path("C:/Users/lukx/Desktop/velasccxt")
DATA_DIR = Path(__file__).parent / "data" / "strategies"


class BacktestRunner:
    """Runs backtests with real data and compares with pre-generated results."""
    
    def __init__(self, velas_dir: Path, data_dir: Path):
        self.velas_dir = velas_dir
        self.data_dir = data_dir
        self.registry = get_registry()
        load_default_strategies()
        self.cache = {}  # Cache loaded DataFrames
        
    def load_ohlcv(self, token: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Load OHLCV data from CSV."""
        cache_key = f"{token}_{timeframe}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        file_path = self.velas_dir / f"{token}_{timeframe}.csv"
        if not file_path.exists():
            print(f"⚠️  Data file not found: {file_path}")
            return None
        
        try:
            df = pd.read_csv(file_path)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.sort_values('datetime')
            self.cache[cache_key] = df
            return df
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return None
    
    def filter_by_period(self, df: pd.DataFrame, period: str) -> pd.DataFrame:
        """Filter dataframe by period (6M, 2Y, 5Y)."""
        now = datetime.utcnow()
        
        if period == "6M":
            cutoff = now - timedelta(days=180)
        elif period == "2Y":
            cutoff = now - timedelta(days=730)
        elif period == "5Y":
            cutoff = now - timedelta(days=1825)
        else:
            raise ValueError(f"Unknown period: {period}")
        
        return df[df['datetime'] >= cutoff].copy()
    
    def run_strategy_backtest(
        self, 
        strategy_id: str, 
        token: str, 
        timeframe: str, 
        period: str
    ) -> Optional[Dict]:
        """
        Run backtest for a single strategy configuration.
        
        Returns:
            Dict with keys: total_trades, win_rate, net_profit, wins, losses
        """
        # Load data
        df = self.load_ohlcv(token, timeframe)
        if df is None:
            return None
        
        # Filter by period
        df_filtered = self.filter_by_period(df, period)
        
        if len(df_filtered) < 100:
            print(f"⚠️  Not enough data for {token} {timeframe} {period}: {len(df_filtered)} candles")
            return None
        
        # Get strategy instance
        strategy = self.registry.get(strategy_id)
        if not strategy:
            print(f"❌ Strategy {strategy_id} not found")
            return None
        
        # Run backtest simulation
        # This is a SIMPLIFIED backtest - real strategies may have different logic
        signals = []
        wins = 0
        losses = 0
        net_profit = 0.0
        
        try:
            # Iterate through candles and generate signals
            for i in range(200, len(df_filtered)):  # Need lookback period
                window = df_filtered.iloc[max(0, i-200):i+1]
                
                # Convert to format expected by strategy
                context = {
                    'ohlcv': window.to_dict('records'),
                    'token': token,
                    'timeframe': timeframe,
                }
                
                # Try to get signal from strategy
                # NOTE: This depends on strategy interface - may need adjustment
                try:
                    if hasattr(strategy, 'analyze'):
                        signal = strategy.analyze(
                            token=token,
                            timeframe=timeframe,
                            context=context
                        )
                        
                        if signal and hasattr(signal, 'confidence'):
                            signals.append(signal)
                            
                            # Simulate outcome (simplified)
                            # In reality, we'd track entry/exit based on strategy rules
                            # For now, use a simple win/loss simulation
                            outcome = self._simulate_signal_outcome(signal, df_filtered.iloc[i:i+50])
                            
                            if outcome > 0:
                                wins += 1
                                net_profit += 2.2  # Typical win size
                            else:
                                losses += 1
                                net_profit -= 1.0  # Typical loss size
                except Exception as e:
                    # Strategy might not be compatible with this interface
                    pass
        
        except Exception as e:
            print(f"❌ Error running backtest: {e}")
            return None
        
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
        
        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 1),
            'net_profit': round(net_profit, 1),
            'wins': wins,
            'losses': losses,
        }
    
    def _simulate_signal_outcome(self, signal, future_df: pd.DataFrame) -> float:
        """
        Simplified simulation of signal outcome.
        In a real backtest, this would track actual entry/exit based on strategy rules.
        """
        if len(future_df) < 5:
            return -1.0  # Not enough data
        
        # Simplified: random outcome based on confidence
        # In reality, you'd calculate actual profit based on price movement
        import random
        if hasattr(signal, 'confidence'):
            threshold = 0.7
            return 1.0 if signal.confidence > threshold else -1.0
        return -1.0
    
    def parse_existing_result(self, folder: str, period: str, token: str, timeframe: str) -> Optional[Dict]:
        """Parse existing result file."""
        file_path = self.data_dir / folder / period / f"{token}{timeframe}.txt"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metrics
            result = {}
            for line in content.split('\n'):
                if "Total Trades:" in line:
                    result['total_trades'] = int(line.split(':')[1].strip())
                elif "Win Rate:" in line:
                    result['win_rate'] = float(line.split(':')[1].strip().replace('%', ''))
                elif "Total Net Profit:" in line:
                    result['net_profit'] = float(line.split(':')[1].strip().replace('R', ''))
                elif "Wins:" in line and "Losses:" in line:
                    parts = line.split('|')
                    result['wins'] = int(parts[0].split(':')[1].strip())
                    result['losses'] = int(parts[1].split(':')[1].strip())
            
            return result
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None
    
    def compare_results(self, actual: Dict, expected: Dict) -> Tuple[bool, List[str]]:
        """
        Compare actual vs expected results.
        
        Returns:
            (is_match, list_of_differences)
        """
        differences = []
        tolerance = 0.1  # 10% tolerance for win rate
        
        if actual['total_trades'] != expected['total_trades']:
            differences.append(f"Total Trades: {actual['total_trades']} vs {expected['total_trades']}")
        
        if abs(actual['win_rate'] - expected['win_rate']) > tolerance:
            differences.append(f"Win Rate: {actual['win_rate']}% vs {expected['win_rate']}%")
        
        if abs(actual['net_profit'] - expected['net_profit']) > 2.0:
            differences.append(f"Net Profit: {actual['net_profit']}R vs {expected['net_profit']}R")
        
        if actual['wins'] != expected['wins']:
            differences.append(f"Wins: {actual['wins']} vs {expected['wins']}")
        
        if actual['losses'] != expected['losses']:
            differences.append(f"Losses: {actual['losses']} vs {expected['losses']}")
        
        return (len(differences) == 0, differences)
    
    def verify_all(self, sample_size: Optional[int] = None, verbose: bool = False):
        """
        Verify all or a sample of backtest results.
        
        Args:
            sample_size: If set, only test this many random configs
            verbose: Print detailed progress
        """
        print("=" * 80)
        print("REAL BACKTEST VERIFICATION")
        print("=" * 80)
        print()
        print("⚠️  NOTE: This is a PROOF-OF-CONCEPT verification.")
        print("   Full backtest requires strategy-specific logic implementation.")
        print()
        
        results = {
            'total': 0,
            'verified': 0,
            'mismatches': 0,
            'errors': 0,
            'details': []
        }
        
        configs = []
        for folder in FOLDER_TO_STRATEGY.keys():
            for period in PERIODS:
                for token in TOKENS:
                    for tf_file, tf_code in TIMEFRAMES_MAP.items():
                        configs.append((folder, period, token, tf_file, tf_code))
        
        # Sample if requested
        if sample_size and sample_size < len(configs):
            import random
            configs = random.sample(configs, sample_size)
        
        for folder, period, token, tf_file, tf_code in configs:
            results['total'] += 1
            strategy_id = FOLDER_TO_STRATEGY[folder]
            
            if verbose:
                print(f"\n[{results['total']}/{len(configs)}] Testing: {folder}/{period}/{token}{tf_file}")
            
            # Load expected results
            expected = self.parse_existing_result(folder, period, token, tf_file)
            if not expected:
                print(f"  ❌ Could not load expected results")
                results['errors'] += 1
                continue
            
            # Run actual backtest
            actual = self.run_strategy_backtest(strategy_id, token, tf_code, period)
            if not actual:
                print(f"  ⚠️  Skipped (no data or error)")
                results['errors'] += 1
                continue
            
            # Compare
            is_match, differences = self.compare_results(actual, expected)
            
            if is_match:
                results['verified'] += 1
                if verbose:
                    print(f"  ✅ MATCH")
            else:
                results['mismatches'] += 1
                print(f"  ⚠️  MISMATCH:")
                for diff in differences:
                    print(f"     - {diff}")
            
            results['details'].append({
                'config': f"{folder}/{period}/{token}{tf_file}",
                'match': is_match,
                'expected': expected,
                'actual': actual,
                'differences': differences
            })
        
        # Summary
        print()
        print("=" * 80)
        print("VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Configs Tested: {results['total']}")
        print(f"✅ Verified (Match): {results['verified']}")
        print(f"⚠️  Mismatches: {results['mismatches']}")
        print(f"❌ Errors/Skipped: {results['errors']}")
        print()
        
        match_rate = (results['verified'] / results['total'] * 100) if results['total'] > 0 else 0
        print(f"Match Rate: {match_rate:.1f}%")
        
        # Save detailed report
        report_path = Path("backtest_verification_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify strategy backtests with real data")
    parser.add_argument('--sample', type=int, default=None,
                       help='Sample size (default: all configs)')
    parser.add_argument('--verbose', action='store_true',
                       help='Print detailed progress')
    
    args = parser.parse_args()
    
    # Check data directory
    if not VELAS_DIR.exists():
        print(f"❌ ERROR: Velas data directory not found: {VELAS_DIR}")
        sys.exit(1)
    
    runner = BacktestRunner(VELAS_DIR, DATA_DIR)
    runner.verify_all(sample_size=args.sample, verbose=args.verbose)


if __name__ == "__main__":
    main()
