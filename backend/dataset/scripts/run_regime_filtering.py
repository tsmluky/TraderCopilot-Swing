from backtest import Backtester
from strategies import DonchianStrategy
import glob
import os
import pandas as pd

def run_regime_filtering_test():
    files = glob.glob('data/*_1h.csv')
    
    results_data = []

    print("Running Comparative Test: Donchian Classic vs. Smart Donchian (ADX > 25)...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        
        # 1. Classic Donchian (Baseline)
        strat_classic = DonchianStrategy(window=20)
        
        # 2. Smart Donchian (Regime Filtered). ADX > 25
        strat_smart = DonchianStrategy(window=20, adx_threshold=25)
        
        try:
            # Run Classic
            tester_classic = Backtester(file, strat_classic, initial_capital=10000)
            res_c = tester_classic.run()
            
            # Run Smart
            tester_smart = Backtester(file, strat_smart, initial_capital=10000)
            res_s = tester_smart.run()
            
            # Calmar Ratio calc (avoid div by zero)
            c_calmar = res_c['total_return'] / abs(res_c['max_drawdown']) if res_c['max_drawdown'] != 0 else 0
            s_calmar = res_s['total_return'] / abs(res_s['max_drawdown']) if res_s['max_drawdown'] != 0 else 0
            
            results_data.append({
                "Token": symbol,
                "Mode": "Classic",
                "Return%": round(res_c['total_return'], 2),
                "MaxDD%": round(res_c['max_drawdown'], 2),
                "Calmar": round(c_calmar, 2),
                "Trades": res_c['trades_count']
            })
            
            results_data.append({
                "Token": symbol,
                "Mode": "Smart (ADX>25)",
                "Return%": round(res_s['total_return'], 2),
                "MaxDD%": round(res_s['max_drawdown'], 2),
                "Calmar": round(s_calmar, 2),
                "Trades": res_s['trades_count']
            })
            
        except Exception as e:
            print(f"Error {symbol}: {e}")

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_regime_filter.csv', index=False)
    
    # Pivot for easier comparison
    df_pivot = df_res.pivot(index='Token', columns='Mode', values=['Return%', 'MaxDD%', 'Calmar'])
    
    # Print Summary Table
    print("\n=== REGIME FILTER COMPARISON ===")
    if not df_res.empty:
        print(df_pivot.to_markdown())
        
        with open('results_regime_summary.txt', 'w') as f:
            f.write("=== REGIME FILTER COMPARISON ===\n\n")
            f.write(df_pivot.to_markdown())

if __name__ == "__main__":
    run_regime_filtering_test()
