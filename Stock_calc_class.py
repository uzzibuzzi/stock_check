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
        self.DF=pd.DataFrame()
        
    def changeBackLook(HistoryLength):
        
        self.backlooklength= HistoryLength

        
    def pullData(ticker):
        
        self.newDF=pd.DataFrame()
        try:
            self.msft = yf.Ticker(ticker)
            self.stockinfo=msft.info
            self.stockName=str(stockinfo.get("longName"))  
        except:
             self.stockName=str(ticker)
             print("failed Ticker",ticker)
        try:
             newDF = yf.download( self.ticker, start=self.backlooklength, end=self.today)    
        except:
             print("failed download",mySupervisionList[i])
        
        print(stockName) 
        print(self.newDF.describe())  
        
        
abc=AnalyseStock("app")
abc.pullData()
        
        

