# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 08:47:41 2019

@author: yinchao
"""
import os
import pandas as pd

import Analyse
import TushareApp

def ReadUserHoldRecord():
    '''
    获取用户持仓记录
    '''
    BASE = os.path.split(os.path.realpath(__file__))[0]
    CFG_PATH = BASE + '\\Config'
    hold_record_file = CFG_PATH+'\\hold_record.csv'
    return  pd.read_csv(hold_record_file, dtype={'source':str,'target':str})


ts = TushareApp.ts_app()
alg = Analyse.Analyse()

raw_record = ReadUserHoldRecord()
stock_list = raw_record['id']

alg.AlarmGuid(stock_list)

