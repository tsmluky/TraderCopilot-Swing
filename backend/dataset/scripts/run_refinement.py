from backtest import Backtester
from strategies import DonchianStrategy
import glob
import os
import pandas as pd
import numpy as np

def run_refinement():
    files = glob.glob('data/*_1h.csv')
    
    # Define Refined Variants + Previous Winner (V2)
    variants = {
        "V2_Turtle_Classic": DonchianStrategy(window=55, exit_window=55),
        "V6_Turtle_Asym": DonchianStrategy(window=55, exit_window=20),
        "V7_Fast_Asym": DonchianStrategy(window=30, exit_window=15),
        "V8_ATR_Wide": DonchianStrategy(window=55, atr_trailing=(14, 4.0))
    }

    results_data = []

    print(f"Running Refinement (V2 vs V6, V7, V8) on {len(files)} tokens...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        
        for v_name, strategy in variants.items():
            try:
                tester = Backtester(file, strategy, initial_capital=10000)
                res = tester.run()
                
                results_data.append({
                    "Token": symbol,
                    "Variant": v_name,
                    "Return%": round(res['total_return'], 2),
                    "Trades": res['trades_count'],
                    "WinRate%": round(res['win_rate'], 1),
                    "MaxDD%": round(res['max_drawdown'], 2),
                    "FinalEquity": round(res['final_equity'], 2),
                    "ProfitFactor": round(res['profit_factor'], 2)
                })
                print(f"Done: {symbol} - {v_name}")
            except Exception as e:
                print(f"Error {symbol} {v_name}: {e}")

    # Create Summary DataFrame
    df_res = pd.DataFrame(results_data)
    
    # Save to CSV
    df_res.to_csv('results_refinement.csv', index=False)
    
    # Print Metrics
    metrics = ['Return%', 'MaxDD%', 'Trades']
    for m in metrics:
        print(f"\n=== {m} ===")
        print(df_res.pivot(index='Token', columns='Variant', values=m))
    
    with open('results_refinement_summary.txt', 'w') as f:
        f.write("=== REFINEMENT PHASE RESULTS ===\n\n")
        f.write(df_res.to_markdown(index=False))

if __name__ == "__main__":
    run_refinement()
