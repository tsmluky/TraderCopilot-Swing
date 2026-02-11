from backtest import Backtester
from strategies import SMACrossoverStrategy
import glob
import os
import pandas as pd

def run_sma_optimization():
    files = glob.glob('data/*_1h.csv')
    
    # Grid
    fast_windows = [10, 20, 30, 40, 50, 80]
    slow_windows = [50, 80, 100, 150, 200, 300]
    
    results_data = []

    print(f"Running SMA Optimization on {len(files)} tokens...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        print(f"\nScanning {symbol}...")
        
        for slow in slow_windows:
            for fast in fast_windows:
                if fast >= slow:
                    continue # Fast must be smaller
                
                strategy = SMACrossoverStrategy(fast_window=fast, slow_window=slow)
                
                try:
                    tester = Backtester(file, strategy, initial_capital=10000)
                    res = tester.run()
                    
                    calmar = res['total_return'] / abs(res['max_drawdown']) if res['max_drawdown'] != 0 else 0
                    
                    results_data.append({
                        "Token": symbol,
                        "Fast": fast,
                        "Slow": slow,
                        "Return%": round(res['total_return'], 2),
                        "MaxDD%": round(res['max_drawdown'], 2),
                        "Trades": res['trades_count'],
                        "Calmar": round(calmar, 2)
                    })
                except Exception:
                    pass

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_sma_optimization.csv', index=False)
    
    # Print Top 3 per Token
    print("\n=== SMA OPTIMIZATION RESULTS ===")
    if not df_res.empty:
        for symbol in df_res['Token'].unique():
            print(f"\n--- {symbol} ---")
            df_token = df_res[df_res['Token'] == symbol].sort_values(by='Calmar', ascending=False)
            print(df_token.head(3)[['Fast', 'Slow', 'Return%', 'MaxDD%', 'Calmar']].to_markdown(index=False))
            
        with open('results_sma_optimization_summary.txt', 'w') as f:
            f.write("=== SMA OPTIMIZATION (Ranked by Calmar) ===\n\n")
            f.write(df_res.to_markdown(index=False))

if __name__ == "__main__":
    run_sma_optimization()
