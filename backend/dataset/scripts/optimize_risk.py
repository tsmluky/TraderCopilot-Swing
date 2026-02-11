from backtest import Backtester
from strategies import DonchianStrategy
import glob
import os
import pandas as pd
import numpy as np

def run_risk_optimization():
    # Only optimizing SOL and BNB as requested
    targets = {
        'SOL': {'window': 110, 'exit_window': 80},
        'BNB': {'window': 55, 'exit_window': 55}
    }
    
    # Parameter Grid
    # SL ATR Multipliers (None means rely on Channel Exit only)
    sl_atr_options = [None, 1.0, 2.0, 3.0]
    
    # TP ATR Multipliers (None means let it ride)
    tp_atr_options = [None, 5.0, 10.0, 20.0, 50.0] 
    
    results_data = []

    print(f"Starting Risk Optimization on SOL and BNB...")
    
    for symbol, params in targets.items():
        file_pattern = f"data/{symbol}_*_1h.csv"
        files = glob.glob(file_pattern)
        if not files: continue
        file = files[0]
        
        print(f"\nAnalyzing {symbol} (Base: W{params['window']}-E{params['exit_window']})...")
        
        for sl in sl_atr_options:
            for tp in tp_atr_options:
                # If both None, it's the Base Case, run it once
                
                strategy = DonchianStrategy(
                    window=params['window'],
                    exit_window=params['exit_window'],
                    fixed_sl_atr=sl,
                    fixed_tp_atr=tp
                )
                
                try:
                    tester = Backtester(file, strategy, initial_capital=10000)
                    res = tester.run()
                    
                    variant_name = "Base"
                    if sl or tp:
                        variant_name = f"SL{sl if sl else 'X'}_TP{tp if tp else 'X'}"
                    
                    results_data.append({
                        "Token": symbol,
                        "SL_ATR": sl if sl else "None",
                        "TP_ATR": tp if tp else "None",
                        "Return%": round(res['total_return'], 2),
                        "MaxDD%": round(res['max_drawdown'], 2),
                        "Trades": res['trades_count'],
                        "WinRate%": round(res['win_rate'], 1),
                        "ProfitFactor": round(res['profit_factor'], 2),
                        "FinalEquity": round(res['final_equity'], 2)
                    })
                except Exception as e:
                    print(f"Err {symbol} SL{sl} TP{tp}: {e}")

    # Save Results
    df_res = pd.DataFrame(results_data)
    df_res.to_csv('results_risk_optimization.csv', index=False)
    
    # Create Summaries per token
    with open('results_risk_optimized_summary.txt', 'w') as f:
        f.write("=== RISK PARAMETER OPTIMIZATION ===\n")
        
        for symbol in targets.keys():
            f.write(f"\n--- {symbol} RESULTS ---\n")
            df_token = df_res[df_res['Token'] == symbol].sort_values(by='Return%', ascending=False)
            f.write(df_token.head(10).to_markdown(index=False))
            f.write("\n")
            print(f"\nTop 5 Configs for {symbol}:")
            print(df_token.head(5)[['SL_ATR', 'TP_ATR', 'Return%', 'MaxDD%', 'WinRate%']].to_markdown(index=False))

if __name__ == "__main__":
    run_risk_optimization()
