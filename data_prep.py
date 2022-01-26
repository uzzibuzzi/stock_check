# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 14:31:48 2021

@author: Achims_tab
"""
import yfinance as yf
import os
import pandas as pd
from datetime import date


class stockHandling:
    def __init__(self):
      self.failList = []

    
    def get_Data_yahoo(self,ticker):
        newDF=pd.DataFrame()
        today = date.today()
        try:
            msft = yf.Ticker(ticker)
            stockinfo=msft.info
            stockName=str(stockinfo.get("longName"))  
        except:
            self.failList.append(ticker)
            print("failed Ticker",ticker)
            return False,False
        try:
            newDF = yf.download(ticker, start="2020-02-01", end=today)    
        except:
            self.failList.append(ticker)
            print("failed download",ticker) 
            return False,False
        return stockName, newDF 
    


def plot_bollinger(DF):
    """ it plots bollinger from a DF "value"
    """
    mdf=pd.DataFrame()
    mdf["value"]=DF
    mdf=mdf.dropna()
    mdf["max"]=mdf["value"].rolling(10).max()
    mdf["min"]=mdf["value"].rolling(10).min()
    mdf['TP'] = (mdf['value'] + mdf['max'] + mdf['min'])/3
    mdf['MA-TP'] = mdf['TP'].rolling(4).mean()
    mdf['stdw'] = mdf['TP'].rolling(10).std(ddof=1)
    mdf['mean_max'] = mdf['MA-TP']+ 4*mdf['stdw']
    mdf['mean_min'] = mdf['MA-TP'] - 4*mdf['stdw']
    
    # Plotting it all together
    ax = mdf[['value', 'mean_max', 'mean_min']].plot(color=['blue', 'orange', 'yellow'])
    ax.fill_between(mdf.index, mdf['mean_max'], mdf['mean_min'], facecolor='orange', alpha=0.3)
    ax.set_xlim([today-datetime.timedelta(70), today])
    plt.show()
    



    
if __name__ == "__main__":
    dat=stockHandling()
    
    stockName,df = dat.get_Data_yahoo('TMV.DE') 
    
