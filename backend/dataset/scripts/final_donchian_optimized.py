from backtest import Backtester
from strategies import DonchianStrategy
import glob
import os
import pandas as pd

# === OPTIMAL CONFIGURATION PER TOKEN ===
# Derived from Grid Search Optimization (Phase 4)
OPTIMAL_PARAMS = {
    'SOL': {'window': 110, 'exit_window': 80},  # The Giant Hunter (+11,000%)
    'BNB': {'window': 55, 'exit_window': 55},   # The Turtle (+8,800%)
    'BTC': {'window': 80, 'exit_window': 80},   # The Elephant (+1,100%)
    'ETH': {'window': 55, 'exit_window': 35},   # Nervous Trend (+2,200%)
}

def run_final_strategy():
    print("=== RUNNING FINAL OPTIMIZED DONCHIAN STRATEGY ===")
    
    results_data = []
    
    for symbol, params in OPTIMAL_PARAMS.items():
        file_pattern = f"data/{symbol}_*_1h.csv"
        files = glob.glob(file_pattern)
        
        if not files:
            print(f"Warning: No data file found for {symbol}")
            continue
            
        file = files[0] # Assuming one file per token
        
        # Initialize Strategy with Optimal Params
        strategy = DonchianStrategy(
            window=params['window'],
            exit_window=params['exit_window']
        )
        
        tester = Backtester(file, strategy, initial_capital=10000)
        res = tester.run()
        
        results_data.append({
            "Token": symbol,
            "Entry_W": params['window'],
            "Exit_W": params['exit_window'],
            "Return%": round(res['total_return'], 2),
            "MaxDD%": round(res['max_drawdown'], 2),
            "Trades": res['trades_count'],
            "FinalEquity": round(res['final_equity'], 2),
            "WinRate%": round(res['win_rate'], 1)
        })
        print(f"Processed {symbol}...")

    # Output Results
    df = pd.DataFrame(results_data)
    df = df.set_index('Token')
    
    print("\n--- PERFORMANCE SUMMARY ---")
    print(df.to_markdown())
    
    # Save to CSV for external validation
    df.to_csv('final_results_optimized.csv')
    print("\nResults saved to 'final_results_optimized.csv'")

if __name__ == "__main__":
    run_final_strategy()
