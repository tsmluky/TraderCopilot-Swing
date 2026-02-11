from backtest import Backtester
from strategies import MeanReversionStrategy
import glob
import os
import pandas as pd
import numpy as np

def run_mean_reversion_baseline():
    files = glob.glob('data/*_1h.csv')
    
    # Baseline Parameters
    strategy = MeanReversionStrategy(window=20, std_dev=2.0)
    
    results_data = []

    print(f"Running Mean Reversion Baseline (BB 20, 2.0) on {len(files)} tokens...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        
        try:
            tester = Backtester(file, strategy, initial_capital=10000)
            res = tester.run()
            
            # Calculate Calmar for consistency
            dd = abs(res['max_drawdown'])
            calmar = res['total_return'] / dd if dd > 0 else 0
            
            results_data.append({
                "Token": symbol,
                "Return%": round(res['total_return'], 2),
                "Trades": res['trades_count'],
                "WinRate%": round(res['win_rate'], 1),
                "MaxDD%": round(res['max_drawdown'], 2),
                "Calmar": round(calmar, 2),
                "FinalEquity": round(res['final_equity'], 2)
            })
            print(f"Done: {symbol}")
        except Exception as e:
            print(f"Error {symbol}: {e}")

    # Create Summary DataFrame
    df_res = pd.DataFrame(results_data)
    
    # Save to CSV
    df_res.to_csv('results_mean_reversion_baseline.csv', index=False)
    
    # Print Table
    print("\n=== MEAN REVERSION BASELINE RESULTS ===")
    print(df_res.sort_values(by='Return%', ascending=False).to_markdown(index=False))
    
    with open('results_mean_reversion_baseline.txt', 'w') as f:
        f.write("=== MEAN REVERSION BASELINE (BB 20, 2.0) ===\n\n")
        f.write(df_res.sort_values(by='Return%', ascending=False).to_markdown(index=False))

if __name__ == "__main__":
    run_mean_reversion_baseline()
