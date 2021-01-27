import yfinance as yf
import os

import matplotlib.pyplot as plt
import seaborn
import pandas as pd

import mpl_finance
import numpy as np
import matplotlib.dates as mdates

from mpl_finance import candlestick_ohlc
from datetime import date

# creates rolling means acoring the list sind back string for positive or neagtive trend
def fastAnalyse(series):
    avrg=[2,5,25,96,200,500]
    resultStr=""
    for i in avrg:
        mean_gradient=series.rolling(window=i).mean().diff()[-1]
        #print(mean_gradient)
        if mean_gradient > 0 :
            resultStr=resultStr + "+"
        else :
            resultStr=resultStr+"-"
    return resultStr


def get_Data_yahoo(ticker):
        tickerSymbol=ticker
        try:
            msft = yf.Ticker(tickerSymbol)
            stockinfo=msft.info
            stockName=str(stockinfo.get("longName"))  
        except:
            stockName=str(mySupervisionList[i]).split(".")[0]
            print("failed Ticker",mySupervisionList[i])
        try:
            df = yf.download(tickerSymbol, start="2020-02-01", end=today)    
        except:
            failList.append(mySupervisionList[i])
            print("failed download",mySupervisionList[i])
        return stockName, df   


# return a list of limits froma requestest ticker -> add the same for name
def get_limits(tickerName,allStockLimits):
    ListOfLimits=[]   
    # can be added more columns for additionale lines
    for each in ["Limit"]: 
        ListOfLimits.append(list(allStockLimits.loc[allStockLimits["Name"]==tickerName][each]))
    cleanedList = [x for x in ListOfLimits[0] if x > 0]
    return cleanedList

def get_my_list():
    try:
        returnList=pd.read_csv("myChecklist.csv",header= None)
        returnList=returnList.iloc[0].to_list()
    
    except:    
        watchlist=["TMV.DE","AAPL","HEIA.AS","SHL.DE","VOS.DE","GE","SKT","JNJ","AVGO","SW1.F","SLT.DE","ASL.de"]
        mySupervisionList=["2338.HK","AAG.DE","BIDU","BMW.DE","BAYN.DE","COK.DE","CSCO","EVD.DE","FEV.DE","HAG.F","IRBT","JD","MTX.DE","N7G.DE","PRLB","SHL.DE","SIX2.DE","SLM","TCOM","TUI1.DE","VOW3.DE"]
        returnList=watchlist+mySupervisionList
        
    return returnList




today = date.today()
print("Today's date:", today)

failList=[]
RSL_List=[]
trendIndicatorList=[]
mdf=pd.DataFrame()
stockNameList=[]





mySupervisionList=get_my_list()
print(mySupervisionList)

try:
    os.mkdir("save//pics//"+str(today))
    os.mkdir("save//files//"+str(today))
except OSError:
    print ("Creation of the directory failed use existing" )
else:
    print ("Successfully created the directory " )
    
for i in range(len(mySupervisionList)):   
    stockName,df = get_Data_yahoo(mySupervisionList[i])   
    print(stockName)
    # hier was rein if df is epmty pass passiert bei download und empty df
    if (len(df) <1):
        print("hier war ein fheler",mySupervisionList[i])
        
    else:
        df_ohlc=df["Adj Close"].resample("2D").ohlc()
        df_ohlc_1d=df["Adj Close"].resample("1D").ohlc()
        df_Volume = df["Volume"].resample("2D").sum()
        df_100ma=df["Adj Close"].rolling(window=100).mean()
        df_20ma=df["Adj Close"].rolling(window=20).mean()
        df_dx= (df["Adj Close"]-df_100ma.rolling(window=50).mean())
        df_ohlc.reset_index(inplace=True)
        df_ohlc["Date"]= df_ohlc["Date"].map(mdates.date2num)
        df_ohlc_1d.reset_index(inplace=True)
        df_ohlc_1d["Date_time"]= df_ohlc_1d["Date"].map(mdates.date2num)
        
        RSL=df["Adj Close"].rolling(window=3).mean()/df["Adj Close"].rolling(window=5*26).mean()
        RSL_List.append(RSL[-1])
        trendIndicator=fastAnalyse(df["Adj Close"])
        trendIndicatorList.append(trendIndicator)
        stockNameList.append(str(stockName))
        
        df_ohlc_1d.to_csv("save//files//"+str(today)+"//"+str(stockName)+".csv")
        ax1=plt.subplot2grid((6,1),(0,0),rowspan=5,colspan=1)
        plt.title(str(stockName)+" RSL : "+str(RSL[-1])[:4]+trendIndicator)
        ax2=plt.subplot2grid((6,1),(5,0),rowspan=5,colspan=1,sharex=ax1)
        ax1.xaxis_date()
        candlestick_ohlc(ax1,df_ohlc.values,width=2,colorup="g")
        ax1.plot(df_100ma.index.map(mdates.date2num),df_100ma.values)
        ax1.plot(df_20ma.index.map(mdates.date2num),df_20ma.values)
        #from external csv read all availbale limits and draw it
        all_limits=get_limits(stockName,pd.read_csv("myStockLimits.csv"))
        for each in all_limits:  
            ax1.axhline(y=each, color='r', linestyle='-')    
            # #ax1.axhline(y=df["Adj Close"].min(), color='r', linestyle='-')
        
        
        ax2.fill_between(df_Volume.index.map(mdates.date2num), df_Volume.values,0)
        ax1.annotate(str(df["Adj Close"][-1])[:6],xy=(0.8, 0.9), xycoords='axes fraction')
        ax2.plot(df_dx.index.map(mdates.date2num),df_dx.values) 
        plt.savefig("save//pics//"+str(today)+"//"+str(stockName).split(".")[0]+str(today), dpi=800)
        # plt.show()

    


mdf=pd.DataFrame({"mySupervisionList":stockNameList,"RSL_List":RSL_List,"trendIndicator":trendIndicatorList}) 
mdf=mdf.sort_values(by=['RSL_List']).head()
mdf.to_csv("save//files//"+str(today)+"Result_"+str(today)+".csv")

abc=pd.read_csv()

print(mdf.sort_values(by=['RSL_List']).head())
print(mdf.sort_values(by=['RSL_List']).tail())