# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 07:18:49 2021

@author: vollmera
"""
import pandas as pd

# creates an class of all orders
class myOrders():
    def __init__(self,old_orders):
        self.orders=old_orders
    def get_all(self):
        return self.orders
    def get_stock(self,stockname):
        return self.orders.loc[self.orders["Name"]==stockname]
    def get_this(self,column):
        return self.orders[column]
    def get_keys(self):
        return self.orders.keys()
    def add_Limit(self,Name,Limit_Value):
        abc=pd.DataFrame([{"Name":Name,"Limit":Limit_Value}]) 
        self.orders=pd.concat([ self.orders,abc])
    def save(self,as_name):
        self.orders.to_csv(as_name)
         

my=myOrders(pd.read_csv("myStockLimits.csv"))

print(my.get_all())



my.add_Limit("BAYER AG NA O.N", 50)



print(my.get_this("Limit"))

my.save("myStockLimits.csv")

myy=myOrders("TUI AG BZR",pd.read_csv("abc.csv"))

print(my.get_all())



