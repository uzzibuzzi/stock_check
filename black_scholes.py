# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 11:15:02 2022

@author: Achims_tab
"""

import pandas_datareader.data as web
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

import seaborn as sns

import numpy as np
from scipy.stats import norm

N = norm.cdf

def BS_CALL(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * N(d1) - K * np.exp(-r*T)* N(d2)

def BS_PUT(S, K, T, r, sigma):
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
    d2 = d1 - sigma* np.sqrt(T)
    return K*np.exp(-r*T)*N(-d2) - S*N(-d1)
"""
S : current asset price

K: strike price of the option

r: risk free rate 

T : time until option expiration 

σ: annualized volatility of the asset's returns """


"""
S Effect on Option Value

"""

K = 100
r = 0.1
T = 1
sigma = 0.3

S = np.arange(60,140,0.1)

calls = [BS_CALL(s, K, T, r, sigma) for s in S]
puts = [BS_PUT(s, K, T, r, sigma) for s in S]
plt.plot(S, calls, label='Call Value')
plt.plot(S, puts, label='Put Value')
plt.xlabel('$S_0$')
plt.ylabel(' Value')
plt.legend()

"""
σ  Effect on Black-Scholes Value
increase the volatility parameter both calls and puts increase in value,"""


K = 100
r = 0.1
T = 1
Sigmas = np.arange(0.1, 1.5, 0.01)
S = 100

calls = [BS_CALL(S, K, T, r, sig) for sig in Sigmas]
puts = [BS_PUT(S, K, T, r, sig) for sig in Sigmas]
plt.plot(Sigmas, calls, label='Call Value')
plt.plot(Sigmas, puts, label='Put Value')
plt.xlabel('$\sigma$')
plt.ylabel(' Value')
plt.legend()


"""
Time Effect of Time on Black-Scholes Price
 

"""

K = 100
r = 0.05
T = np.arange(0, 4, 0.01)
sigma = 0.25
S = 100

calls = [BS_CALL(S, K, t, r, sigma) for t in T]
puts = [BS_PUT(S, K, t, r, sigma) for t in T]
plt.plot(T, calls, label='Call Value')
plt.plot(T, puts, label='Put Value')
plt.xlabel('$T$ in years')
plt.ylabel(' Value')
plt.legend()

"""

Main Problem with Black Scholes
 

The script below calculates the rolling standard deviation for APPLE over approximately 10 years. Notice that the volatility is in no way stable, if we take the standard deviation over the entire sample it is approximately 0.28 , however, notice that in early-mid 2020 during there is a large spike. As mentioned, the Black-Scholes model assumes this parameter is constant. 

"""



start = dt.datetime(2018,1,1)    
end =dt.datetime(2022,1,1) 
symbol = 'aapl' ###using Apple as an example
source = 'yahoo'
data = web.DataReader(symbol, source, start, end)
data['change'] = data['Adj Close'].pct_change()
data['rolling_sigma'] = data['change'].rolling(20).std() * np.sqrt(255)


data.rolling_sigma.plot()
plt.ylabel('$\sigma$')
plt.title('appl')
plt.show()




std = data.change.std()
WT = np.random.normal(data.change.mean() ,std)
plt.hist(np.exp(WT)-1,bins=300,color='red',alpha=0.4);
plt.hist(data.change,bins=200,color='black', alpha=0.4);
plt.xlim([-0.03,0.03])


fig, ax = plt.subplots()
ax = sns.kdeplot(data=data['change'].dropna(), label='Empirical', ax=ax,shade=True)
#ax = sns.kdeplot(data=WT, label='Log Normal', ax=ax,shade=True)
plt.xlim([-0.15,0.15])
plt.ylim([-1,40])
plt.xlabel('return')
plt.ylabel('Density')

plt.hist(data["change"],bins=100)


plt.hist(aapl,bins=100)

plt.hist(db,bins=100,alpha=0.3)

plt.hist(tsla,bins=100,alpha=0.3)

plt.show()
aapl=data["change"]