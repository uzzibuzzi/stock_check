# -*- coding: utf-8 -*-
"""
Created on Wed May 12 21:36:50 2021

@author: vollmera
"""

import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np


# return a list of limits froma requestest ticker -> add the same for name
def get_limits(tickerName,allStockLimits):
    ListOfLimits=[]   
    # can be added more columns for additionale lines
    for each in ["Limit"]: 
        ListOfLimits.append(list(allStockLimits.loc[allStockLimits["Name"]==tickerName][each]))
    cleanedList = [x for x in ListOfLimits[0] if x > 0]
    return cleanedList



all_limits=get_limits("Volkswagen AG",pd.read_csv("myStockLimits.csv"))

stockName="Apple Inc."
stockName=stockName.split()[0]
def find_thresholds(name):
    limit_DF=pd.read_csv("myStockLimits.csv")
    ListOfLimits=[]   
    for each in range(len(limit_DF)):
        if name in limit_DF.loc[each,"Name"]:      
            print(each,limit_DF.loc[each,"Limit"])
            ListOfLimits.append(limit_DF.loc[each,"Limit"])
    return [x for x in ListOfLimits if math.isnan(x) == False]


ax1=plt.subplot2grid((6,1),(0,0),rowspan=5,colspan=1)

all_limits=find_thresholds(stockName)
for each in all_limits:  
    ax1.axhline(y=each, color='r', linestyle='-')    
plt.show()


limit_DF.keys()[0]

limit_DF=pd.read_csv("myStockLimits.csv")
limit_DF=limit_DF.drop(columns=[limit_DF.keys()[0]])
limit_DF["dyn. Limit in last days"]=20

limit_DF.to_csv("next_limit.csv")

limit_DF["dyn. Limit in last days"][-5:].max()


numbers=[8,7,6,5,4,4,5,6,7,7,8,1,1,8,9,7,6,5,5,4,3]
mdf=pd.DataFrame()
mdf["value"]=numbers
limit=5

def find_trigger(kurs,limit):
    mdf["trigger"]=(kurs>limit).shift(periods=1)!=(kurs>limit)
    triggerArray=np.array(mdf["trigger"])
    trigger_index=np.argwhere(triggerArray>0.5)
    plt.scatter(mdf.index,mdf["value"])
    plt.hlines(limit,0,len(kurs))
    plt.scatter(mdf.index,mdf["trigger"])
    
    for counter in range(len(trigger_index)):
        print(trigger_index[counter])
        plt.axvline(x=trigger_index[counter][0])
    plt.show()

find_trigger(mdf["value"],6)


ml=[]
len(ml)>0

kurs=mdf["value"]
aaa=pd.DataFrame(kurs)