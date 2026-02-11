from backtest import Backtester
from strategies import DonchianStrategy
import glob
import os
import pandas as pd

def run_variants():
    files = glob.glob('data/*_1h.csv')
    
    # Define Variants
    variants = {
        "V1_Standard": DonchianStrategy(window=20),
        "V2_Turtle": DonchianStrategy(window=55),
        "V3_Trend": DonchianStrategy(window=20, ema_filter=200),
        "V4_ATR_Trail": DonchianStrategy(window=20, atr_trailing=(14, 2.0)),
        "V5_Aggressive": DonchianStrategy(window=10, rsi_filter=50)
    }

    results_data = []

    print(f"Running {len(variants)} variants on {len(files)} tokens...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        
        for v_name, strategy in variants.items():
            try:
                # Re-instantiate strategy if it has state? No, current implementation is stateless or re-initialized in run?
                # Actually generate_signals returns new DF, so it's fine.
                
                tester = Backtester(file, strategy, initial_capital=10000)
                res = tester.run()
                
                results_data.append({
                    "Token": symbol,
                    "Variant": v_name,
                    "Return%": round(res['total_return'], 2),
                    "Trades": res['trades_count'],
                    "WinRate%": round(res['win_rate'], 1),
                    "MaxDD%": round(res['max_drawdown'], 2),
                    "FinalEquity": round(res['final_equity'], 2)
                })
                print(f"Done: {symbol} - {v_name}")
            except Exception as e:
                print(f"Error {symbol} {v_name}: {e}")

    # Create Summary DataFrame
    df_res = pd.DataFrame(results_data)
    
    # Save to CSV
    df_res.to_csv('results_variants_detailed.csv', index=False)
    
    # Print Pivot Tables
    print("\n=== Return % ===")
    print(df_res.pivot(index='Token', columns='Variant', values='Return%'))
    
    print("\n=== Max Drawdown % ===")
    print(df_res.pivot(index='Token', columns='Variant', values='MaxDD%'))
    
    with open('results_variants_detailed.txt', 'w') as f:
        f.write("=== DETAILED RESULTS ===\n\n")
        f.write(df_res.to_markdown(index=False))


if __name__ == "__main__":
    run_variants()
