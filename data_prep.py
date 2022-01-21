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
    
    
    
if __name__ == "__main__":
    dat=stockHandling()
    
    stockName,df = dat.get_Data_yahoo('TMV.DE') 
    
