from backtest import Backtester
from strategies import DonchianStrategy
import glob
import os

def run_all():
    files = glob.glob('data/*_1h.csv')
    print(f"Found files: {files}")

    with open('results.txt', 'w') as f:
        f.write(f"{'Token':<10} | {'Return':<10} | {'Trades':<8} | {'Final Equity':<15}\n")
        f.write("-" * 50 + "\n")

        for file in files:
            symbol = os.path.basename(file).split('_')[0]
            
            # Standard Donchian Window = 20
            strategy = DonchianStrategy(window=20)
            
            tester = Backtester(file, strategy, initial_capital=10000)
            results = tester.run()
            
            line = f"{symbol:<10} | {results['total_return']:>6.2f}%    | {results['trades_count']:<8} | ${results['final_equity']:<15.2f}\n"
            print(line.strip())
            f.write(line)
            
        f.write("-" * 50 + "\n")
    print("Results saved to results.txt")

if __name__ == "__main__":
    run_all()
