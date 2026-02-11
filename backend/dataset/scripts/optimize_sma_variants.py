from backtest import Backtester
from strategies import SMACrossoverStrategy
import glob
import os
import pandas as pd

def run_sma_variants_optimization():
    # Only optimizing BTC and ETH as requested
    targets = ['BTC', 'ETH']
    file_pattern = 'data/*_1h.csv'
    all_files = glob.glob(file_pattern)
    target_files = [f for f in all_files if os.path.basename(f).split('_')[0] in targets]
    
    # Best params from previous step (approx centers)
    # BTC: 40/80
    # ETH: 10/300 or 20/80
    
    # Grid for variants
    # We will test around the "best" SMA values found, but switching mode to EMA and adding ADX
    
    variants = [
        # 1. EMA Mode (Pure)
        {'name': 'EMA_Pure', 'use_ema': True, 'adx': None},
        # 2. SMA + ADX > 20
        {'name': 'SMA_ADX20', 'use_ema': False, 'adx': 20},
        # 3. SMA + ADX > 25
        {'name': 'SMA_ADX25', 'use_ema': False, 'adx': 25},
        # 4. EMA + ADX > 20
        {'name': 'EMA_ADX20', 'use_ema': True, 'adx': 20},
    ]
    
    # Parameter Search Space (Focused around previous bests)
    # BTC: Around 40/80
    btc_params = [(40, 80), (30, 60), (50, 100), (20, 50)]
    # ETH: Around 20/80 and 10/300
    eth_params = [(20, 80), (10, 300), (30, 100), (50, 200)]
    
    results_data = []

    print(f"Running SMA/EMA Variants Optimization on BTC & ETH...")
    
    for file in target_files:
        symbol = os.path.basename(file).split('_')[0]
        print(f"\nScanning {symbol}...")
        
        param_grid = btc_params if symbol == 'BTC' else eth_params
        
        for p in param_grid:
            fast, slow = p
            
            for v in variants:
                strategy = SMACrossoverStrategy(
                    fast_window=fast, 
                    slow_window=slow, 
                    use_ema=v['use_ema'], 
                    adx_threshold=v['adx']
                )
                
                try:
                    tester = Backtester(file, strategy, initial_capital=10000)
                    res = tester.run()
                    
                    calmar = res['total_return'] / abs(res['max_drawdown']) if res['max_drawdown'] != 0 else 0
                    
                    results_data.append({
                        "Token": symbol,
                        "Variant": v['name'],
                        "Fast": fast,
                        "Slow": slow,
                        "Return%": round(res['total_return'], 2),
                        "MaxDD%": round(res['max_drawdown'], 2),
                        "Calmar": round(calmar, 2)
                    })
                except Exception as e:
                    pass

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_sma_variants.csv', index=False)
    
    # Print Summary
    print("\n=== SMA/EMA VARIANTS RESULTS ===")
    if not df_res.empty:
        for symbol in df_res['Token'].unique():
            print(f"\n--- {symbol} ---")
            df_token = df_res[df_res['Token'] == symbol].sort_values(by='Return%', ascending=False)
            print(df_token.head(5).to_markdown(index=False))
            
        with open('results_sma_variants_summary.txt', 'w') as f:
            f.write("=== SMA VARIANTS RESULTS ===\n\n")
            f.write(df_res.to_markdown(index=False))

if __name__ == "__main__":
    run_sma_variants_optimization()
