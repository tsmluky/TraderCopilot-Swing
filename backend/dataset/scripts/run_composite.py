from backtest import Backtester
from strategies import CompositeStrategy
import glob
import os
import pandas as pd

def run_composite_baseline():
    files = glob.glob('data/*_1h.csv')
    
    results_data = []

    print("Running Composite Strategy (Regime Switching)...")
    print("Logic: ADX < 25 -> Mean Reversion | ADX >= 25 -> Donchian")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        
        # Donchian Params (Trend) - Proven winners
        donchian_params = {
            'window': 20,
            'allow_short': False # Keep it simple/robust for trend
        }
        
        # Mean Reversion Params (Range) - Standard
        mean_rev_params = {
            'window': 20,
            'std_dev': 2.0,
            'sl_atr': 3.0 # Protective stop
        }
        
        # Composite
        strategy = CompositeStrategy(
            donchian_params=donchian_params,
            mean_rev_params=mean_rev_params,
            adx_threshold=25
        )
        
        try:
            tester = Backtester(file, strategy, initial_capital=10000)
            res = tester.run()
            
            results_data.append({
                "Token": symbol,
                "Mode": "Composite",
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
    df_res.to_csv('results_composite.csv', index=False)
    
    # Print Summary Table
    print("\n=== COMPOSITE STRATEGY RESULTS ===")
    if not df_res.empty:
        print(df_res.to_markdown(index=False))
        
        with open('results_composite_summary.txt', 'w') as f:
            f.write("=== COMPOSITE STRATEGY RESULTS ===\n\n")
            f.write(df_res.to_markdown(index=False))

if __name__ == "__main__":
    run_composite_baseline()
