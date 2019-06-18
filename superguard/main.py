# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 08:47:41 2019

@author: yinchao
"""
import Analyse
import TushareApp
import HoldRecordApp

hd = HoldRecordApp.hd_record()
ts = TushareApp.ts_app()
alg = Analyse.Analyse()

raw_record = hd.GetUserStockList() #获取监控列表

alg.AlarmGuid(raw_record) #开始监控

