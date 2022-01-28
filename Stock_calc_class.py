# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 16:36:50 2022

@author: vollmera
"""

import yfinance as yf
import pandas as pd
from datetime import date


class AnalyseStock:
    def __init__(self,ticker,):
        self.ticker=ticker
        self.stockName=""
        self.backlooklength= "2020-02-01"
        self.today = date.today()
        self.newDF=pd.DataFrame()
        self.stockName=""
        self.msft=""
        self.stockinfo=""
        
    def changeBackLook(self,HistoryLength):
        self.backlooklength= HistoryLength

        
    def pullData(self):
        print(self.ticker)
        
        try:
            self.msft = yf.Ticker(self.ticker)
            
            print(self.ticker)
            self.stockinfo=self.msft.info
            print("info")
            self.stockName=str(self.stockinfo.get("longName"))  
            print(self.stockinfo.get("longName"))
        except:
             self.stockName=str(self.ticker)
             print("failed Ticker",self.ticker)
        try:
             self.newDF = yf.download( self.ticker, start=self.backlooklength, end=self.today)    
        except:
             print("failed download",self.ticker)
        
        print(self.stockName) 
        print(self.newDF.describe())  
        
        
abc=AnalyseStock("TMV.DE")
print("init done")
print("change stoc")
abc.pullData()
        
        

