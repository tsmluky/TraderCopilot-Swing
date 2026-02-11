from backtest import Backtester
from strategies import RSI2Strategy
import glob
import os
import pandas as pd

def run_rsi2_baseline():
    files = glob.glob('data/*_1h.csv')
    
    # Baseline Parameters
    # RSI(2)
    # Filter: SMA 200
    # Exit: SMA 5
    # Thresholds: 10 / 90
    
    results_data = []

    print("Running RSI-2 Strategy Baseline...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        
        # Configuration: Trend Filter ON, No Stop Loss (Pure Mean Reversion)
        strategy = RSI2Strategy(
            rsi_window=2, 
            sma_filter=200, 
            exit_sma=5, 
            rsi_long_threshold=10, 
            rsi_short_threshold=90,
            sl_atr=3.0  # Added Catastrophe Stop
        )
        
        try:
            # Diagnostic: 0 Commission to check Alpha
            tester = Backtester(file, strategy, initial_capital=10000, commission=0.0)
            res = tester.run()
            
            results_data.append({
                "Token": symbol,
                "Return%": round(res['total_return'], 2),
                "MaxDD%": round(res['max_drawdown'], 2),
                "Trades": res['trades_count'],
                "WinRate%": round(res['win_rate'], 2)
            })
        except Exception as e:
            print(f"Error {symbol}: {e}")

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_rsi2.csv', index=False)
    
    # Print Summary Table
    print("\n=== RSI-2 BASELINE RESULTS ===")
    if not df_res.empty:
        print(df_res.to_markdown(index=False))
        
        with open('results_rsi2_summary.txt', 'w') as f:
            f.write("=== RSI-2 BASELINE RESULTS ===\n\n")
            f.write(df_res.to_markdown(index=False))

if __name__ == "__main__":
    run_rsi2_baseline()
