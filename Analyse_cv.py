import pandas as pd
import numpy as np

# Load both backtest results
df_80_20 = pd.read_csv('bt_80_20_backtest.csv', index_col=0, parse_dates=True)
df_70_30 = pd.read_csv('bt_70_30_backtest.csv', index_col=0, parse_dates=True)

# Portfolio Value Analysis
print("="*70)
print("PORTFOLIO VALUE COMPARISON")
print("="*70)

initial_capital = 100000

# Get final values
final_80_20 = df_80_20['portfolio_value'].iloc[-1]
final_70_30 = df_70_30['portfolio_value'].iloc[-1]
final_bh_80 = df_80_20['buy_hold_value'].iloc[-1]
final_cons_80 = df_80_20['conservative_value'].iloc[-1]

# Calculate gains
gain_80_20 = ((final_80_20 - initial_capital) / initial_capital) * 100
gain_70_30 = ((final_70_30 - initial_capital) / initial_capital) * 100
gain_bh_80 = ((final_bh_80 - initial_capital) / initial_capital) * 100
gain_cons_80 = ((final_cons_80 - initial_capital) / initial_capital) * 100

print(f"\nFinal Portfolio Values:")
print(f"  80/20 Strategy:        €{final_80_20:,.2f}  ({gain_80_20:+.2f}%)")
print(f"  70/30 Strategy:        €{final_70_30:,.2f}  ({gain_70_30:+.2f}%)")
print(f"  Buy & Hold (100% DAX): €{final_bh_80:,.2f}  ({gain_bh_80:+.2f}%)")
print(f"  Conservative (80/20):  €{final_cons_80:,.2f}  ({gain_cons_80:+.2f}%)")

print(f"\n80/20 vs 70/30:")
print(f"  Difference: €{final_80_20 - final_70_30:+,.2f}  ({gain_80_20 - gain_70_30:+.2f}%)")

# Drawdown Analysis on portfolio_value
print("\n" + "="*70)
print("DRAWDOWN ANALYSIS (Based on Portfolio Value)")
print("="*70)

for label, df in [("80/20 Strategy", df_80_20), ("70/30 Strategy", df_70_30), ("Buy & Hold", df_80_20[['buy_hold_value']].rename(columns={'buy_hold_value': 'portfolio_value'}))]:
    # Use appropriate column
    if label == "Buy & Hold":
        values = df_80_20['buy_hold_value']
    else:
        values = df['portfolio_value']
    
    # Calculate running maximum
    running_max = values.cummax()
    
    # Calculate drawdown
    drawdown = (values - running_max) / running_max
    
    # Find maximum drawdown
    max_dd = drawdown.min()
    max_dd_pct = max_dd * 100
    max_dd_date = drawdown.idxmin()
    
    print(f"\n{label}:")
    print(f"  Max Drawdown: {max_dd_pct:.2f}% (on {max_dd_date.strftime('%Y-%m-%d')})")
    print(f"  Mean Drawdown: {drawdown.mean() * 100:.2f}%")
    print(f"  Median Drawdown: {drawdown.median() * 100:.2f}%")
    print(f"  Std Dev: {drawdown.std() * 100:.2f}%")