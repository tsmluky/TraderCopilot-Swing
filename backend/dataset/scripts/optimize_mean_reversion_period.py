from backtest import Backtester
from strategies import MeanReversionStrategy
import glob
import os
import pandas as pd

def run_mean_reversion_period_optimization():
    files = glob.glob('data/*_1h.csv')
    
    # 2022-2024 Period
    start_date = "2022-01-01"
    end_date = "2024-12-31"
    
    # Grid
    adx_options = [None, 30, 25, 20] 
    rsi_options = [None, 30, 25, 20]
    
    results_data = []

    print(f"Running Mean Reversion Optimization (2022-2024) on {len(files)} tokens...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        print(f"\nScanning {symbol} (Bear/Lateral Period)...")
        
        for adx in adx_options:
            for rsi in rsi_options:
                
                strategy = MeanReversionStrategy(
                    window=20, 
                    std_dev=2.0, 
                    adx_threshold=adx, 
                    rsi_threshold=rsi
                )
                
                try:
                    tester = Backtester(file, strategy, initial_capital=10000, start_date=start_date, end_date=end_date)
                    res = tester.run()
                    
                    if res['trades_count'] < 10: # Ignore statistical noise
                        continue

                    results_data.append({
                        "Token": symbol,
                        "ADX_Thresh": adx if adx else 100,
                        "RSI_Thresh": rsi if rsi else 100,
                        "Return%": round(res['total_return'], 2),
                        "MaxDD%": round(res['max_drawdown'], 2),
                        "Trades": res['trades_count'],
                        "WinRate%": round(res['win_rate'], 1),
                        "FinalEquity": round(res['final_equity'], 2)
                    })
                except Exception:
                    pass

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_mean_reversion_2022_2024.csv', index=False)
    
    # Print Top 3 per Token
    print("\n=== MEAN REVERSION (2022-2024) OPTIMIZATION ===")
    if not df_res.empty:
        for symbol in df_res['Token'].unique():
            print(f"\n--- {symbol} ---")
            df_token = df_res[df_res['Token'] == symbol].sort_values(by='Return%', ascending=False)
            print(
                df_token.head(3)[['ADX_Thresh', 'RSI_Thresh', 'Return%', 'MaxDD%', 'Trades']]
                .to_markdown(index=False)
            )
            
        with open('results_mean_reversion_2022_2024_summary.txt', 'w') as f:
            f.write("=== MEAN REVERSION (2022-2024) ===\n\n")
            f.write(df_res.to_markdown(index=False))
    else:
        print("No valid results found (maybe no trades?).")

if __name__ == "__main__":
    run_mean_reversion_period_optimization()
