from backtest import Backtester
from strategies import SuperTrendStrategy
import glob
import os
import pandas as pd

def run_supertrend_baseline():
    files = glob.glob('data/*_1h.csv')
    
    # Baseline Parameters
    # ATR 10, Multiplier 3 (Standard)
    
    results_data = []

    print("Running SuperTrend Strategy Baseline...")
    print("Parameters: ATR=10, Mult=3.0")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        
        # Force Long Only for all tokens to test hypothesis
        allow_short = False 
        
        strategy = SuperTrendStrategy(
            atr_window=10, 
            multiplier=3.0,
            allow_short=allow_short
        )
        
        try:
            tester = Backtester(file, strategy, initial_capital=10000)
            res = tester.run()
            
            results_data.append({
                "Token": symbol,
                "Mode": "Bi-Dir" if allow_short else "LongOnly",
                "Return%": round(res['total_return'], 2),
                "MaxDD%": round(res['max_drawdown'], 2),
                "Trades": res['trades_count'],
                "WinRate%": round(res['win_rate'], 2),
                "ProfitFactor": round(res['profit_factor'], 2)
            })
        except Exception as e:
            print(f"Error {symbol}: {e}")
            import traceback
            traceback.print_exc()

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_supertrend.csv', index=False)
    
    # Print Summary Table
    print("\n=== SUPERTREND BASELINE RESULTS ===")
    if not df_res.empty:
        print(df_res.to_markdown(index=False))
        
        with open('results_supertrend_summary.txt', 'w') as f:
            f.write("=== SUPERTREND BASELINE RESULTS ===\n\n")
            f.write(df_res.to_markdown(index=False))

if __name__ == "__main__":
    run_supertrend_baseline()
