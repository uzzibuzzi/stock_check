import ssl
import os
import warnings

# Fix SSL certificate verification BEFORE importing yfinance
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['PYTHONHTTPSVERIFY'] = '0'
warnings.filterwarnings('ignore')

# Set environment to use curl_cffi with SSL verification disabled
os.environ['YFINANCE_USE_CURL'] = '1'

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Patch curl_cffi to disable SSL verification if it's being used
try:
    from curl_cffi import requests as curl_requests
    # Override the default verify setting
    original_request = curl_requests.Session.request
    
    def patched_request(self, *args, **kwargs):
        if 'verify' not in kwargs:
            kwargs['verify'] = False
        return original_request(self, *args, **kwargs)
    
    curl_requests.Session.request = patched_request
except:
    pass

# Try using older requests library instead of curl
try:
    import yfinance.utils
    yfinance.utils._REQUESTS_SESSION = None
except:
    pass

# -----------------------------
# PARAMETERS
# -----------------------------
# Available tickers
TICKERS_AVAILABLE = {
    "DAX": "^GDAXI",
    "Nasdaq": "^IXIC",
    "S&P 500": "^GSPC"
}

# Select ticker (change this to switch between DAX, Nasdaq, S&P 500)
SELECTED_TICKER = "Nasdaq"  # Options: "DAX", "Nasdaq", "S&P 500"
TICKER = TICKERS_AVAILABLE[SELECTED_TICKER]

START_DATE = "2006-01-01"
END_DATE = None            # up to today
ROLLING_HIGH_MONTHS = 12

# PT1 Smoothing Parameters (First-order lag filter)
# PT1_TAU: Time constant in months (higher = more smoothing)
# Formula: y[n] = y[n-1] + (1 - exp(-dt/tau)) * (x[n] - y[n-1])
PT1_TAU = 3.0  # Adjust this to control smoothing (1-6 months recommended)

# PT1 Allocation Smoothing (for portfolio weight transitions)
# PT1_ALLOC_TAU: Time constant for allocation transitions (higher = slower/longer transitions)
PT1_ALLOC_TAU = 6.0  # Adjust this (3-12 months recommended) - higher keeps 100% allocation longer

# -----------------------------
# DOWNLOAD DATA
# -----------------------------
print(f"Downloading data for {SELECTED_TICKER} ({TICKER})...")
try:
    data = yf.download(TICKER, start=START_DATE, end=END_DATE, auto_adjust=True)
except Exception as e:
    print(f"Download error: {e}")
    exit(1)

# Check if download succeeded
if data.empty or len(data) == 0:
    print(f"Error: Failed to download data for {TICKER}")
    exit(1)

print(f"Successfully downloaded {len(data)} records")

# Use monthly data
monthly = data[['Close']].resample('ME').last()
monthly.columns = ['price']

# -----------------------------
# ROLLING 12-MONTH HIGH
# -----------------------------
monthly['rolling_high'] = (
    monthly['price']
    .rolling(ROLLING_HIGH_MONTHS, min_periods=1)
    .max()
)

# -----------------------------
# DRAWDOWN
# -----------------------------
monthly['drawdown'] = monthly['price'] / monthly['rolling_high'] - 1

# -----------------------------
# TIME BELOW HIGH (MONTHS)
# -----------------------------
months_below = []
counter = 0

for price, high in zip(monthly['price'], monthly['rolling_high']):
    if price >= high:
        counter = 0
    else:
        counter += 1
    months_below.append(counter)

monthly['months_below_high'] = months_below

# -----------------------------
# DRAWDOWN SCORE (D)
# -----------------------------
def drawdown_score(dd):
    if dd > -0.05:
        return 0
    elif dd > -0.10:
        return 1
    elif dd > -0.20:
        return 2
    else:
        return 3

monthly['D'] = monthly['drawdown'].apply(drawdown_score)

# -----------------------------
# TIME SCORE (T)
# -----------------------------
def time_score(months):

    if months < 3:
        return 0
    elif months <= 9:
        return 1
    else:
        return 2

monthly['T'] = monthly['months_below_high'].apply(time_score)

#monthly['T'] = monthly['months_below_high'].apply(time_score)
# -----------------------------
# TOTAL MARKET STRESS SCORE
# -----------------------------
monthly['score_raw'] = monthly['D'] + monthly['T']



# -----------------------------
# HYSTERESIS LOGIC
# -----------------------------
scores = []
current_score = monthly['score_raw'].iloc[0]
months_in_state = 0

for s in monthly['score_raw']:
    if s > current_score:
        # Defensive move: immediate
        current_score = s
        months_in_state = 0
    elif s <= current_score - 2 or months_in_state >= 3:
        # Risk-on move: slow
        current_score = s
        months_in_state = 0
    else:
        months_in_state += 1

    scores.append(current_score)

monthly['score'] = scores

# -----------------------------
# PT1 SMOOTHING (SECOND SCORE)
# -----------------------------
def pt1_filter(data, tau=PT1_TAU, dt=1.0):
    """
    Apply PT1 (first-order lag) filter to data
    tau: time constant (months)
    dt: sampling time (1 for monthly data)
    """
    if len(data) == 0:
        return data
    
    smoothed = [data.iloc[0]]
    alpha = 1.0 - np.exp(-dt / tau)
    
    for i in range(1, len(data)):
        y_prev = smoothed[-1]
        x_curr = data.iloc[i]
        y_curr = y_prev + alpha * (x_curr - y_prev)
        smoothed.append(y_curr)
    
    return np.array(smoothed)

# Apply PT1 filter to raw score
monthly['score_pt1'] = pt1_filter(monthly['score_raw'], tau=PT1_TAU)

# Round to nearest 0.5 for easier interpretation
monthly['score_pt1_rounded'] = np.round(monthly['score_pt1'] * 2) / 2

# Optional: Apply hysteresis logic to PT1 score for discrete levels
score_pt1_discrete = []
current_score_pt1 = monthly['score_pt1'].iloc[0]
months_in_state_pt1 = 0

for s in monthly['score_pt1']:
    if s > current_score_pt1 + 0.5:
        # Defensive move: immediate
        current_score_pt1 = s
        months_in_state_pt1 = 0
    elif s <= current_score_pt1 - 0.5 or months_in_state_pt1 >= 2:
        # Risk-on move: slow
        current_score_pt1 = s
        months_in_state_pt1 = 0
    else:
        months_in_state_pt1 += 1

    score_pt1_discrete.append(current_score_pt1)

monthly['score_pt1_discrete'] = score_pt1_discrete

# -----------------------------
# BOND ALLOCATION
# -----------------------------
def bond_allocation(score):
    if score <= 1:
        return 0.30
    elif score == 2:
        return 0.20
    elif score == 3:
        return 0.10
    else:
        return 0.00

monthly['bond_weight'] = monthly['score'].apply(bond_allocation)
monthly['stock_weight'] = 1 - monthly['bond_weight']

# -----------------------------
# BACKTESTING STRATEGY
# -----------------------------
def backtest_strategy(data, allocation_80_20=True, initial_capital=100000, pt1_alloc_tau=PT1_ALLOC_TAU):
    """
    Backtest the investment strategy
    When score = 5: invest 100% in DAX, 0% in bonds
    When score < 5: allocate to DAX/bonds based on allocation ratio
    allocation_80_20: True for 80/20 split, False for 70/30 split
    pt1_alloc_tau: Time constant for allocation weight smoothing (months)
    """
    
    # Make a copy to avoid modifying original
    bt = data.copy()
    bt['returns'] = bt['price'].pct_change()
    
    # Determine allocation based on score (before smoothing)
    dax_weights = []
    bond_weights = []
    
    for score in bt['score']:
        if score >= 5:
            dax_weights.append(1.0)
            bond_weights.append(0.0)
        elif score == 4:
            dax_weights.append(0.95)
            bond_weights.append(0.05)
        elif score == 3:
            dax_weights.append(0.9)
            bond_weights.append(0.1)
        elif score == 2:
            dax_weights.append(0.85)
            bond_weights.append(0.15)
        else:  # score <= 1 or 0
            if allocation_80_20:
                dax_weights.append(0.8)
                bond_weights.append(0.2)
            else:
                dax_weights.append(0.7)
                bond_weights.append(0.3)
    
    bt['dax_weight'] = dax_weights
    bt['bond_weight'] = bond_weights
    
    # Apply PT1 smoothing to dax_weight (makes 100% allocation persist longer)
    dax_weights_raw = bt['dax_weight'].values
    dax_weights_smoothed = [dax_weights_raw[0]]
    alpha = 1.0 - np.exp(-1.0 / pt1_alloc_tau)
    
    for i in range(1, len(dax_weights_raw)):
        y_prev = dax_weights_smoothed[-1]
        x_curr = dax_weights_raw[i]
        y_curr = y_prev + alpha * (x_curr - y_prev)
        dax_weights_smoothed.append(y_curr)
    
    bt['dax_weight'] = dax_weights_smoothed
    bt['bond_weight'] = 1.0 - bt['dax_weight']
    
    # Assume bond returns (conservative estimate: 5% annual = 0.417% monthly)
    bond_monthly_return = 0.05 / 12
    
    # Calculate portfolio return
    bt['portfolio_return'] = bt['dax_weight'] * bt['returns'] + bt['bond_weight'] * bond_monthly_return
    
    # Calculate cumulative wealth
    bt['portfolio_value'] = initial_capital * (1 + bt['portfolio_return']).cumprod()
    
    # Also calculate Buy & Hold (100% DAX always)
    bt['buy_hold_value'] = initial_capital * (1 + bt['returns']).cumprod()
    
    # Also calculate Conservative (always 80/20 or 70/30)
    if allocation_80_20:
        bt['conservative_return'] = 0.8 * bt['returns'] + 0.2 * bond_monthly_return
    else:
        bt['conservative_return'] = 0.7 * bt['returns'] + 0.3 * bond_monthly_return
    bt['conservative_value'] = initial_capital * (1 + bt['conservative_return']).cumprod()
    print(bt['portfolio_return'])
    return bt

# Run backtests
print("\n" + "="*60)
print("BACKTESTING RESULTS (Initial Capital: 100,000)")
print("="*60)

bt_80_20 = backtest_strategy(monthly, allocation_80_20=True, initial_capital=100000)

bt_70_30 = backtest_strategy(monthly, allocation_80_20=False, initial_capital=100000)

# Export to CSV
bt_80_20.to_csv('bt_80_20_backtest.csv')
bt_70_30.to_csv('bt_70_30_backtest.csv')
print("✓ Exported: bt_80_20_backtest.csv")
print("✓ Exported: bt_70_30_backtest.csv")

# Final values
final_idx = -1
initial_capital = 100000

# 80/20 Strategy
final_80_20 = bt_80_20['portfolio_value'].iloc[final_idx]
final_80_20_bh = bt_80_20['buy_hold_value'].iloc[final_idx]
final_80_20_cons = bt_80_20['conservative_value'].iloc[final_idx]
gain_80_20 = ((final_80_20 - initial_capital) / initial_capital) * 100
gain_80_20_bh = ((final_80_20_bh - initial_capital) / initial_capital) * 100
gain_80_20_cons = ((final_80_20_cons - initial_capital) / initial_capital) * 100

# 70/30 Strategy
final_70_30 = bt_70_30['portfolio_value'].iloc[final_idx]
final_70_30_bh = bt_70_30['buy_hold_value'].iloc[final_idx]
final_70_30_cons = bt_70_30['conservative_value'].iloc[final_idx]
gain_70_30 = ((final_70_30 - initial_capital) / initial_capital) * 100
gain_70_30_bh = ((final_70_30_bh - initial_capital) / initial_capital) * 100
gain_70_30_cons = ((final_70_30_cons - initial_capital) / initial_capital) * 100

print(f"\n80/20 ALLOCATION (80% DAX when score < 5, 100% when score = 5):")
print(f"  Strategy Result:        €{final_80_20:,.2f}  ({gain_80_20:+.2f}%)")
print(f"  Buy & Hold (100% DAX):  €{final_80_20_bh:,.2f}  ({gain_80_20_bh:+.2f}%)")
print(f"  Conservative (80/20):   €{final_80_20_cons:,.2f}  ({gain_80_20_cons:+.2f}%)")
print(f"  Strategy vs B&H:        {gain_80_20 - gain_80_20_bh:+.2f}% ({final_80_20 - final_80_20_bh:+,.0f}€)")

print(f"\n70/30 ALLOCATION (70% DAX when score < 5, 100% when score = 5):")
print(f"  Strategy Result:        €{final_70_30:,.2f}  ({gain_70_30:+.2f}%)")
print(f"  Buy & Hold (100% DAX):  €{final_70_30_bh:,.2f}  ({gain_70_30_bh:+.2f}%)")
print(f"  Conservative (70/30):   €{final_70_30_cons:,.2f}  ({gain_70_30_cons:+.2f}%)")
print(f"  Strategy vs B&H:        {gain_70_30 - gain_70_30_bh:+.2f}% ({final_70_30 - final_70_30_bh:+,.0f}€)")

print(f"\nCOMPARISON: 80/20 vs 70/30")
print(f"  80/20 Strategy:  €{final_80_20:,.2f}  ({gain_80_20:+.2f}%)")
print(f"  70/30 Strategy:  €{final_70_30:,.2f}  ({gain_70_30:+.2f}%)")
print(f"  Difference:      €{final_80_20 - final_70_30:+,.2f}  ({gain_80_20 - gain_70_30:+.2f}%)")
print("="*60 + "\n")

# Store for plotting
monthly['portfolio_80_20'] = bt_80_20['portfolio_value']
monthly['portfolio_70_30'] = bt_70_30['portfolio_value']
monthly['buy_hold'] = bt_80_20['buy_hold_value']

# -----------------------------
# PLOT: MARKET STRESS SCORE (20 YEARS)
# -----------------------------
last_20y = monthly.loc[monthly.index >= monthly.index[-1] - pd.DateOffset(years=20)]

fig, ax1 = plt.subplots(figsize=(14, 6))

# Plot stress scores on the left y-axis
color = 'tab:blue'
ax1.set_xlabel("Date")
ax1.set_ylabel("Score Components & Total", color=color)
# Plot individual score components
#ax1.step(last_20y.index, last_20y['D'], where='post', color='tab:red', linewidth=1.5, label='Drawdown Score (D)', alpha=0.7)
#ax1.step(last_20y.index, last_20y['T'], where='post', color='tab:purple', linewidth=1.5, label='Time Score (T)', alpha=0.7)
# Plot combined scores
ax1.step(last_20y.index, last_20y['score'], where='post', color=color, linewidth=2.5, label='Total Score (D+T) with Hysteresis', alpha=0.9)
ax1.step(last_20y.index, last_20y['score_pt1_discrete'], where='post', color='tab:green', linewidth=1.5, label='PT1 Discrete', alpha=0.6, linestyle='--')
ax1.set_ylim(-0.5, 5.5)
ax1.set_yticks(range(6))
ax1.tick_params(axis='y', labelcolor=color)
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)

# Create second y-axis for price in log scale
ax2 = ax1.twinx()
color = 'tab:orange'
ax2.set_ylabel(f"{SELECTED_TICKER} Price (Log Scale)", color=color)
ax2.semilogy(last_20y.index, last_20y['price'], color=color, linewidth=1.5, alpha=0.7, label=f"{SELECTED_TICKER} Price")
ax2.tick_params(axis='y', labelcolor=color)

plt.title(f"{SELECTED_TICKER} Market Stress Score & Price (Last 20 Years)")
fig.tight_layout()
plt.show()

# -----------------------------
# PLOT: ALLOCATION RATIO (20 YEARS)
# -----------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Plot 1: DAX Allocation for 80/20 strategy
ax1.fill_between(last_20y.index, 0, bt_80_20.loc[last_20y.index, 'dax_weight'] * 100, 
                 alpha=0.6, color='tab:blue', label='DAX Allocation (80/20)')
ax1.fill_between(last_20y.index, bt_80_20.loc[last_20y.index, 'dax_weight'] * 100, 100, 
                 alpha=0.3, color='tab:green', label='Bonds (80/20)')
ax1.step(last_20y.index, last_20y['score'] * 20, where='post', color='tab:red', linewidth=2, 
         label='Stress Score (x20 for scale)', alpha=0.7, linestyle='--')
ax1.set_ylabel("Allocation %", fontsize=11)
ax1.set_ylim(0, 120)
ax1.set_yticks(range(0, 101, 20))
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_title(f"{SELECTED_TICKER} - 80/20 Allocation Strategy (Last 20 Years)")

# Plot 2: DAX Allocation for 70/30 strategy
ax2.fill_between(last_20y.index, 0, bt_70_30.loc[last_20y.index, 'dax_weight'] * 100, 
                 alpha=0.6, color='tab:purple', label='DAX Allocation (70/30)')
ax2.fill_between(last_20y.index, bt_70_30.loc[last_20y.index, 'dax_weight'] * 100, 100, 
                 alpha=0.3, color='tab:orange', label='Bonds (70/30)')
ax2.step(last_20y.index, last_20y['score'] * 20, where='post', color='tab:red', linewidth=2, 
         label='Stress Score (x20 for scale)', alpha=0.7, linestyle='--')
ax2.set_xlabel("Date", fontsize=11)
ax2.set_ylabel("Allocation %", fontsize=11)
ax2.set_ylim(0, 120)
ax2.set_yticks(range(0, 101, 20))
ax2.legend(loc='upper left', fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.set_title(f"{SELECTED_TICKER} - 70/30 Allocation Strategy (Last 20 Years)")

fig.tight_layout()
plt.show()

# Plot 3: Portfolio Performance Comparison (Last 20 Years)
fig, ax = plt.subplots(figsize=(14, 6))

# Get starting values for last 20 years
start_portfolio_80_20 = bt_80_20.loc[last_20y.index[0], 'portfolio_value']
start_portfolio_70_30 = bt_70_30.loc[last_20y.index[0], 'portfolio_value']
start_buy_hold = bt_80_20.loc[last_20y.index[0], 'buy_hold_value']

# Plot with actual values (preserving the growth from previous 5 years)
ax.plot(last_20y.index, bt_80_20.loc[last_20y.index, 'portfolio_value'], 
        linewidth=2, label='80/20 Strategy', color='tab:blue')
ax.plot(last_20y.index, bt_70_30.loc[last_20y.index, 'portfolio_value'], 
        linewidth=2, label='70/30 Strategy', color='tab:purple')
ax.plot(last_20y.index, bt_80_20.loc[last_20y.index, 'buy_hold_value'], 
        linewidth=2, label='Buy & Hold (100% DAX)', color='tab:orange', linestyle='--')

# Mark starting values
ax.axhline(y=start_portfolio_80_20, color='tab:blue', linestyle=':', alpha=0.5, linewidth=1)
ax.text(last_20y.index[0], start_portfolio_80_20, f'  €{start_portfolio_80_20:,.0f}', fontsize=9, color='tab:blue')

ax.set_xlabel("Date", fontsize=11)
ax.set_ylabel("Portfolio Value (€)", fontsize=11)
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_title(f"Strategy Backtest Results - Last 20 Years (Allocation: {bt_80_20.loc[last_20y.index[0], 'dax_weight']*100:.0f}% DAX / {bt_80_20.loc[last_20y.index[0], 'bond_weight']*100:.0f}% Bonds)")
fig.tight_layout()
plt.show()