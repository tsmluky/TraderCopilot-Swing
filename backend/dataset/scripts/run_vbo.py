from backtest import Backtester
from strategies import BollingerBreakoutStrategy
import glob
import os
import pandas as pd

def run_vbo_baseline():
    files = glob.glob('data/*_1h.csv')
    
    # Baseline Parameters
    # Window: 20
    # BB Std: 2.0
    # KC Mult: 1.5 (Standard TTM Squeeze setting)
    
    results_data = []

    print("Running Volatility Breakout (Squeeze) Baseline...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        
        # Determine Allow Short based on Token (from previous learnings)
        # ETH/SOL -> Allow Short
        # BTC/BNB -> Long Only
        allow_short = True if symbol in ['ETH', 'SOL'] else False
        
        strategy = BollingerBreakoutStrategy(
            window=20, 
            std_dev=2.0, 
            keltner_mult=1.5,
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

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_vbo.csv', index=False)
    
    # Print Summary Table
    print("\n=== VBO (SQUEEZE) BASELINE RESULTS ===")
    if not df_res.empty:
        print(df_res.to_markdown(index=False))
        
        with open('results_vbo_summary.txt', 'w') as f:
            f.write("=== VBO (SQUEEZE) BASELINE RESULTS ===\n\n")
            f.write(df_res.to_markdown(index=False))

if __name__ == "__main__":
    run_vbo_baseline()
