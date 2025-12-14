import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# PARAMETERS
# -----------------------------
TICKER = "^GDAXI"          # DAX index
START_DATE = "2000-01-01"
END_DATE = None            # up to today
ROLLING_HIGH_MONTHS = 12

# -----------------------------
# DOWNLOAD DATA
# -----------------------------
data = yf.download(TICKER, start=START_DATE, end=END_DATE, auto_adjust=True)

# Use monthly data
monthly = data['Close'].resample('M').last().to_frame(name='price')

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

plt.figure(figsize=(14, 6))
plt.step(last_20y.index, last_20y['score'], where='post')
plt.ylim(-0.5, 5.5)
plt.yticks(range(6))
plt.title("DAX Market Stress Score (Last 20 Years)")
plt.xlabel("Date")
plt.ylabel("Stress Score (0 = Low, 5 = High)")
plt.grid(True)
plt.show()