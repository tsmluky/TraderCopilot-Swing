from backtest import Backtester
from strategies import DonchianStrategy
import glob
import os
import pandas as pd

def run_optimization():
    files = glob.glob('data/*_1h.csv')
    
    # Parameter Grid
    entry_windows = [20, 35, 55, 80, 110]
    exit_windows = [10, 20, 35, 55, 80]
    
    all_results = []

    print(f"Starting Grid Search on {len(files)} tokens...")
    print(f"Testing {len(entry_windows) * len(exit_windows)} combinations per token.")

    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        print(f"\nOptimizing {symbol}...")
        
        token_results = []
        
        for entry_w in entry_windows:
            for exit_w in exit_windows:
                # Logic check: Usually Entry >= Exit for trend following (fast exit), 
                # but let's test all to be sure.
                
                strategy = DonchianStrategy(window=entry_w, exit_window=exit_w)
                try:
                    tester = Backtester(file, strategy, initial_capital=10000)
                    res = tester.run()
                    
                    # Calculate Calmar Ratio (Return / MaxDD)
                    # Handle 0 or positive DD (rare) to avoid div by zero
                    dd = abs(res['max_drawdown'])
                    calmar = res['total_return'] / dd if dd > 0 else 0
                    
                    token_results.append({
                        "Token": symbol,
                        "Entry": entry_w,
                        "Exit": exit_w,
                        "Return%": res['total_return'],
                        "MaxDD%": res['max_drawdown'],
                        "Trades": res['trades_count'],
                        "Calmar": calmar,
                        "WinRate%": res['win_rate']
                    })
                except Exception:
                    pass
        
        # Determine Best for this token (by Calmar)
        df_token = pd.DataFrame(token_results)
        if not df_token.empty:
            best = df_token.sort_values(by='Calmar', ascending=False).iloc[0]
            print(
                f"  -> BEST: Entry {best['Entry']} / Exit {best['Exit']} | "
                f"Return: {best['Return%']:.0f}% | DD: {best['MaxDD%']:.1f}% | "
                f"Calmar: {best['Calmar']:.2f}"
            )
            all_results.extend(token_results)

    # Save full results
    df_all = pd.DataFrame(all_results)
    df_all.to_csv('results_optimization.csv', index=False)
    
    # Save Summary of Best per Token
    best_per_token = df_all.loc[df_all.groupby("Token")["Calmar"].idxmax()]
    
    print("\n=== OPTIMIZATION RESULTS (Best Risk-Adjusted) ===")
    summary_cols = ['Token', 'Entry', 'Exit', 'Return%', 'MaxDD%', 'Calmar', 'Trades']
    print(best_per_token[summary_cols].round(2).to_markdown(index=False))
    
    with open('results_optimization_summary.txt', 'w') as f:
        f.write(best_per_token[summary_cols].round(2).to_markdown(index=False))

if __name__ == "__main__":
    run_optimization()
