from backtest import Backtester
from strategies import DonchianStrategy, SMACrossoverStrategy
import glob
import os
import pandas as pd

def run_bidirectional_test():
    files = glob.glob('data/*_1h.csv')
    
    # Configuration to Test
    # 1. Donchian Bi-Directional (Default Params)
    # 2. SMA Bi-Directional (Optimized Params)
    
    # Optimized SMA Params from previous step
    sma_params = {
        'BNB': {'fast': 20, 'slow': 100},
        'BTC': {'fast': 40, 'slow': 80},
        'ETH': {'fast': 10, 'slow': 300},
        'SOL': {'fast': 10, 'slow': 300}
    }
    
    results_data = []

    print("Running Bi-Directional Strategy Tests...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        
        # --- 1. Donchian Bi-Directional ---
        # Using V1 Baseline Window 20 for apples-to-apples with original baseline?
        # Or using Optimized parameters if we had them per token?
        # Let's use Baseline 20/20 first to see impact of Shorting clearly.
        donchian_bi = DonchianStrategy(window=20, allow_short=True)
        donchian_long = DonchianStrategy(window=20, allow_short=False)
        
        # --- 2. SMA Bi-Directional ---
        s_params = sma_params.get(symbol, {'fast': 50, 'slow': 200})
        sma_bi = SMACrossoverStrategy(fast_window=s_params['fast'], slow_window=s_params['slow'], allow_short=True)
        sma_long = SMACrossoverStrategy(fast_window=s_params['fast'], slow_window=s_params['slow'], allow_short=False)
        
        strategies = [
            ('Donchian_Long', donchian_long),
            ('Donchian_BiDir', donchian_bi),
            ('SMA_Long', sma_long),
            ('SMA_BiDir', sma_bi)
        ]
        
        for name, strat in strategies:
            try:
                tester = Backtester(file, strat, initial_capital=10000)
                res = tester.run()
                
                results_data.append({
                    "Token": symbol,
                    "Strategy": name,
                    "Return%": round(res['total_return'], 2),
                    "MaxDD%": round(res['max_drawdown'], 2),
                    "Trades": res['trades_count']
                })
            except Exception as e:
                print(f"Error {symbol} {name}: {e}")

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_bidirectional.csv', index=False)
    
    # Print Summary Table
    print("\n=== BI-DIRECTIONAL VS LONG-ONLY ===")
    if not df_res.empty:
        # Pivot table for easier comparison
        pivot = df_res.pivot(index='Token', columns='Strategy', values='Return%')
        print(pivot.to_markdown())
        
        with open('results_bidirectional_summary.txt', 'w') as f:
            f.write("=== BI-DIRECTIONAL RESULTS ===\n\n")
            f.write(pivot.to_markdown())

if __name__ == "__main__":
    run_bidirectional_test()
