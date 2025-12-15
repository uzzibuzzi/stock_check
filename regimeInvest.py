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
SELECTED_TICKER = "DAX"  # Options: "DAX", "Nasdaq", "S&P 500"
TICKER = TICKERS_AVAILABLE[SELECTED_TICKER]

START_DATE = "2000-01-01"
END_DATE = None            # up to today
ROLLING_HIGH_MONTHS = 12

# PT1 Smoothing Parameters (First-order lag filter)
# PT1_TAU: Time constant in months (higher = more smoothing)
# Formula: y[n] = y[n-1] + (1 - exp(-dt/tau)) * (x[n] - y[n-1])
PT1_TAU = 3.0  # Adjust this to control smoothing (1-6 months recommended)

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

# -----------------------------
# TOTAL MARKET STRESS SCORE
# -----------------------------
monthly['score_raw'] = monthly['D'] #+ monthly['T']



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
# PLOT: MARKET STRESS SCORE (20 YEARS)
# -----------------------------
last_20y = monthly.loc[monthly.index >= monthly.index[-1] - pd.DateOffset(years=20)]

fig, ax1 = plt.subplots(figsize=(14, 6))

# Plot stress scores on the left y-axis
color = 'tab:blue'
ax1.set_xlabel("Date")
ax1.set_ylabel("Stress Score (0 = Low, 5 = High)", color=color)
ax1.step(last_20y.index, last_20y['score'], where='post', color=color, linewidth=2, label='Raw Score (with Hysteresis)', alpha=0.7)
ax1.plot(last_20y.index, last_20y['score_pt1'], color='tab:red', linewidth=2, label=f'PT1 Smoothed (τ={PT1_TAU}m)', alpha=0.8)
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