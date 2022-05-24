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
        self.currentPrice=0
        
    def changeBackLook(self,HistoryLength):
        self.backlooklength= HistoryLength

        
    def pullData(self):
        print(self.ticker)
        
        try:
            self.msft = yf.Ticker(self.ticker)
            self.stockinfo=self.msft.info
            self.stockName=str(self.stockinfo.get("longName"))  
            print(self.stockinfo.get("longName"))
        except:
             self.stockName=str(self.ticker)
             print("failed Ticker",self.ticker)
        try:
             self.newDF = yf.download( self.ticker, start=self.backlooklength, end=self.today)    
        except:
             print("failed download",self.ticker)
        

    def makeMeans(self):
        print("makeing meand")           
        avrg=[2,5,25,96,200,500]
        for each in avrg:
            self.newDF["ma"+str(each)]=self.newDF["Open"].rolling(each).mean()
        
    def segmentAnalyse(self,segment):
        """
        check the segment and compare it with the moving averages and create a string
        + for higer - for lower actual price to moving average
        order is avrg=[2,5,25,96,200,500]
            """
        resultstring=[]
        dfNameOfMeans = {
            0: "ma2",
            1: "ma5",
            2: "ma25",
            3: "ma96",
            4: "ma200"               }
        
        sectorWKN = {
         "Technology": "IITU.L",
         "Utilities": "XDW0.L",
         "Industrials": 1964
             }
        if segment in sectorWKN.keys() : 
            self=AnalyseStock(str(sectorWKN[str(segment)]))
            self.pullData()     
            self.currentPrice=  self.stockinfo.get("currentPrice")
            
        actvalue=self.currentPrice
        print("current price",actvalue)
        arr=self.newDF.keys() == dfNameOfMeans[0]
        if (any(arr)):
            self.makeMeans()
            
   
            
        for each in range(len(dfNameOfMeans)):
           #iterates over time perdiods
           print(dfNameOfMeans[each])
           print(abc.newDF[dfNameOfMeans[each]].iloc[-1])
           res_timePeriod=abc.newDF[dfNameOfMeans[each]].iloc[-1]
           if (res_timePeriod >= actvalue):
               resultstring+="+"
           else: 
               resultstring+="-"

        return resultstring [::-1]       # depends on the order of the moving averages
    


abc=AnalyseStock("VQT.DE")

abc.pullData()

sector = abc.stockinfo.get("sector")
        
values=abc.segmentAnalyse(sector)
make_price():

try:
    aa=abc.stockinfo.get("regularMarketPrice")
    print(aa)
except:
    print("no pirce")