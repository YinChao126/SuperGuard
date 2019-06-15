# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 08:47:41 2019

@author: yinchao
"""
import os
import pandas as pd

import Algorithm
import TushareApp
import IdConvert

def ReadUserHoldRecord():
    '''
    获取用户持仓记录
    '''
    BASE = os.path.split(os.path.realpath(__file__))[0]
    CFG_PATH = BASE + '\\Config'
    hold_record_file = CFG_PATH+'\\hold_record.csv'
    return  pd.read_csv(hold_record_file, dtype={'source':str,'target':str})


ts = TushareApp.ts_app()
alg = Algorithm.Algorithm()

raw_record = ReadUserHoldRecord()
stock_list = raw_record['id']

import time
cnt = 0
while cnt < 10:
    cnt += 1
    print(cnt)
    time.sleep(1)
    
    for s in stock_list:
        s = s.__int__()
        s = IdConvert.tail2id(str(s))
        if alg.check(ts.BasicInfo(s)):
            print(ts.BasicInfo(s))
            alg.alarm_mask(s)
            
    if cnt == 5:
        alg.reset()

