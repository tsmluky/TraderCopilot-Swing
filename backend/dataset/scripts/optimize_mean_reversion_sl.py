from backtest import Backtester
from strategies import MeanReversionStrategy
import glob
import os
import pandas as pd

def run_mean_reversion_sl_optimization():
    files = glob.glob('data/*_1h.csv')
    
    # 2022-2024 Period (Bear/Lateral)
    start_date = "2022-01-01"
    end_date = "2024-12-31"
    
    # Grid
    # Focused on finding "Safe" mean reversion
    sl_atr_options = [None, 1.0, 2.0, 3.0, 5.0]
    
    # Fixed best filters from previous step to save time, or iterate small grid
    # Previous bests were roughly: ADX<20/30, RSI<20/30.
    # Let's fix RSI < 30 and ADX < 25 (Middle ground) and optimize SL.
    
    defaults = {'adx': 25, 'rsi': 30}
    
    results_data = []

    print(f"Running Mean Reversion SL Optimization (2022-2024) on {len(files)} tokens...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        print(f"\nScanning {symbol} with filters ADX<{defaults['adx']} RSI<{defaults['rsi']}...")
        
        for sl in sl_atr_options:
            strategy = MeanReversionStrategy(
                window=20, 
                std_dev=2.0, 
                adx_threshold=defaults['adx'], 
                rsi_threshold=defaults['rsi'],
                sl_atr=sl
            )
            
            try:
                tester = Backtester(file, strategy, initial_capital=10000, start_date=start_date, end_date=end_date)
                res = tester.run()
                
                if res['trades_count'] < 5:
                    continue

                results_data.append({
                    "Token": symbol,
                    "SL_ATR": sl if sl else "None",
                    "Return%": round(res['total_return'], 2),
                    "MaxDD%": round(res['max_drawdown'], 2),
                    "Trades": res['trades_count'],
                    "WinRate%": round(res['win_rate'], 1),
                    "ProfitFactor": round(res['profit_factor'], 2),
                })
            except Exception as e:
                print(e)

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_mean_reversion_sl.csv', index=False)
    
    # Print Summary
    print("\n=== MEAN REVERSION STOP LOSS TEST (2022-2024) ===")
    if not df_res.empty:
        for symbol in df_res['Token'].unique():
            print(f"\n--- {symbol} ---")
            df_token = df_res[df_res['Token'] == symbol].sort_values(by='Return%', ascending=False)
            print(df_token.to_markdown(index=False))
            
        with open('results_mean_reversion_sl_summary.txt', 'w') as f:
            f.write(df_res.to_markdown(index=False))
    else:
        print("No trades generated.")

if __name__ == "__main__":
    run_mean_reversion_sl_optimization()
