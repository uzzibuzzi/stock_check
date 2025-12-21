import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('bt_80_20_backtest.csv', index_col=0, parse_dates=True)

# Display column names to identify column 18
print("Available columns:")
for i, col in enumerate(df.columns):
    print(f"  Column {i}: {col}")

# Plot portfolio_value (column 18 - typically)
fig, ax = plt.subplots(figsize=(14, 6))

# Plot portfolio_value
ax.plot(df.index, df['portfolio_value'], linewidth=2, label='Portfolio Value (80/20)', color='tab:blue')
ax.plot(df.index, df['buy_hold_value'], linewidth=2, label='Buy & Hold (100% DAX)', color='tab:orange', linestyle='--')
ax.plot(df.index, df['conservative_value'], linewidth=2, label='Conservative (80/20)', color='tab:green', linestyle=':')

ax.axhline(y=100000, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Initial Capital (€100,000)')
ax.set_xlabel("Date", fontsize=11)
ax.set_ylabel("Portfolio Value (€)", fontsize=11)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_title("Strategy Backtest Results - Full Period from 2000 (Initial Capital: €100,000)")
fig.tight_layout()
plt.savefig('portfolio_value_plot.png', dpi=150, bbox_inches='tight')
print("✓ Plot saved as: portfolio_value_plot.png (Full period from 2000)")

print("\nPortfolio statistics:")
print(f"Initial value: €100,000")
print(f"Final value: €{df['portfolio_value'].iloc[-1]:,.2f}")
print(f"Total gain: {((df['portfolio_value'].iloc[-1] - 100000) / 100000 * 100):+.2f}%")
