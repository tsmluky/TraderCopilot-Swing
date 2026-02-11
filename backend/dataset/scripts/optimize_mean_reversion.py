from backtest import Backtester
from strategies import MeanReversionStrategy
import glob
import os
import pandas as pd
import numpy as np

def run_mean_reversion_optimization():
    files = glob.glob('data/*_1h.csv')
    
    # Parameter Grid
    # ADX Thresholds: [None (No Filter), 30 (Weak Trend), 25 (Sideways), 20 (Dead Market)]
    # We want to TRADE when ADX < Threshold.
    adx_options = [None, 30, 25, 20] 
    
    # RSI Thresholds: [None, 30 (Std), 20 (Deep), 15 (Extreme)]
    rsi_options = [None, 30, 25, 20]
    
    results_data = []

    print(f"Running Mean Reversion Optimization on {len(files)} tokens...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        print(f"\nOptimizing {symbol}...")
        
        for adx in adx_options:
            for rsi in rsi_options:
                
                strategy = MeanReversionStrategy(
                    window=20, 
                    std_dev=2.0, 
                    adx_threshold=adx, 
                    rsi_threshold=rsi
                )
                
                try:
                    tester = Backtester(file, strategy, initial_capital=10000)
                    res = tester.run()
                    
                    variant_name = f"ADX<{adx if adx else 'X'}_RSI<{rsi if rsi else 'X'}"
                    
                    results_data.append({
                        "Token": symbol,
                        "ADX_Thresh": adx if adx else 100, # 100 effectively means no filter
                        "RSI_Thresh": rsi if rsi else 100,
                        "Return%": round(res['total_return'], 2),
                        "MaxDD%": round(res['max_drawdown'], 2),
                        "Trades": res['trades_count'],
                        "WinRate%": round(res['win_rate'], 1),
                        "FinalEquity": round(res['final_equity'], 2)
                    })
                except Exception as e:
                    pass

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_mean_reversion_optimized.csv', index=False)
    
    # Print Top 3 per Token
    print("\n=== MEAN REVERSION OPTIMIZATION (Top 3 per Token) ===")
    for symbol in df_res['Token'].unique():
        print(f"\n--- {symbol} ---")
        df_token = df_res[df_res['Token'] == symbol].sort_values(by='Return%', ascending=False)
        print(df_token.head(3)[['ADX_Thresh', 'RSI_Thresh', 'Return%', 'MaxDD%', 'Trades']].to_markdown(index=False))
        
    with open('results_mean_reversion_optimized_summary.txt', 'w') as f:
        f.write("=== MEAN REVERSION OPTIMIZATION RESULTS ===\n\n")
        f.write(df_res.to_markdown(index=False))

if __name__ == "__main__":
    run_mean_reversion_optimization()
