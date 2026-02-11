from backtest import Backtester
from strategies import RSI2Strategy
import glob
import os
import pandas as pd
import itertools

def optimize_rsi2():
    files = glob.glob('data/*_1h.csv')
    
    # Grid Search Space
    # Aim: Reduce frequency, increase quality.
    
    rsi_entries = [2, 5, 10] # 2 is classic/extreme, 10 is the loose baseline
    # Corresponding short would be 98, 95, 90
    
    exit_smas = [5, 10, 20] # Hold longer? Standard is 5.
    
    sma_filters = [None, 200] # Trend Filter: Trade only with trend?
    
    combinations = list(itertools.product(rsi_entries, exit_smas, sma_filters))
    
    results_data = []

    print(f"Optimizing RSI-2. Combinations: {len(combinations)} per token...")
    
    for file in files:
        symbol = os.path.basename(file).split('_')[0]
        

        
        for rsi_entry, exit_sma, sma_filter in combinations:
            
            # Derived Short Threshold
            rsi_short = 100 - rsi_entry
            
            # Label
            filter_label = "Trend" if sma_filter else "NoFilter"
            variant_name = f"RSI{rsi_entry}/{rsi_short}_SMA{exit_sma}_{filter_label}"
            
            strategy = RSI2Strategy(
                rsi_window=2, # Keep 2 period RSI fixed (Connors standard)
                sma_filter=sma_filter, 
                exit_sma=exit_sma, 
                rsi_long_threshold=rsi_entry, 
                rsi_short_threshold=rsi_short,
                sl_atr=3.0 # Keep Catastrophe Stop
            )
            
            try:
                # Use Component Fee (0.1%)
                tester = Backtester(file, strategy, initial_capital=10000)
                res = tester.run()
                
                # Metric: Net Return
                net_return = res['total_return']
                trades = res['trades_count']
                
                # Filter: Must not be hyperactive (>2000 trades/year? ~17000 hours in 2 years)
                # Data is ~8 years? 70,000 hours.
                # 7000 trades = 1 per 10 hours.
                # We want maybe 1000 trades.
                
                results_data.append({
                    "Token": symbol,
                    "Config": variant_name,
                    "RSI_Thresh": rsi_entry,
                    "Exit_SMA": exit_sma,
                    "Filter": filter_label,
                    "Return%": round(net_return, 2),
                    "MaxDD%": round(res['max_drawdown'], 2),
                    "Trades": trades,
                    "WinRate%": round(res['win_rate'], 2)
                })
                
            except Exception:
                pass

    # Save Output
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_rsi2_optimization.csv', index=False)
    
    # Analyze Best per Token
    print("\n=== TOP 3 CONFIGS PER TOKEN (By Return) ===")
    for token in df_res['Token'].unique():
        token_df = df_res[df_res['Token'] == token].sort_values(by='Return%', ascending=False)
        print(f"\n--- {token} ---")
        print(token_df[['Config', 'Return%', 'MaxDD%', 'Trades']].head(3).to_markdown(index=False))

if __name__ == "__main__":
    optimize_rsi2()
