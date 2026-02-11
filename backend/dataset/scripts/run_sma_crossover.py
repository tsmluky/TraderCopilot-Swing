from backtest import Backtester
from strategies import SMACrossoverStrategy
import glob
import os
import pandas as pd

def run_sma_baseline():
    files = glob.glob('data/*_1h.csv')
    
    # Baseline: Classic Golden Cross (50/200)
    strategy = SMACrossoverStrategy(fast_window=50, slow_window=200)
    
    results = []
    
    print("Running SMA Crossover Baseline (50/200)...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        try:
            tester = Backtester(file, strategy, initial_capital=10000)
            res = tester.run()
            
            results.append({
                "Token": symbol,
                "Fast": 50,
                "Slow": 200,
                "Return%": round(res['total_return'], 2),
                "MaxDD%": round(res['max_drawdown'], 2),
                "Trades": res['trades_count'],
                "WinRate%": round(res['win_rate'], 1),
                "ProfitFactor": round(res['profit_factor'], 2),
                "FinalEquity": round(res['final_equity'], 2)
            })
            print(f"Done: {symbol}")
        except Exception as e:
            print(f"Error {symbol}: {e}")

    # Output
    df = pd.DataFrame(results)
    df.to_csv('results_sma_baseline.csv', index=False)
    
    print("\n=== SMA CROSSOVER BASELINE (50/200) ===")
    print(df.sort_values(by='Return%', ascending=False).to_markdown(index=False))
    
    with open('results_sma_baseline.txt', 'w') as f:
        f.write("=== SMA CROSSOVER BASELINE (50/200) ===\n\n")
        f.write(df.sort_values(by='Return%', ascending=False).to_markdown(index=False))

if __name__ == "__main__":
    run_sma_baseline()
