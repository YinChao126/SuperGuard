# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 08:47:41 2019

@author: yinchao
"""
import os,sys
import numpy as np
import pandas as pd
from pandas import DataFrame
import datetime

import SinaApp
import TushareApp
import IdConvert
import TimeConverter as tc


#1. path
BASE = os.path.split(os.path.realpath(__file__))[0]
CFG_PATH = BASE + '\\Config'
#DATA_PATH = BASE + '\\Data'


#2. read hold record
hold_record_file = CFG_PATH+'\\hold_record.csv'
raw_record = pd.read_csv(hold_record_file)

#3. base the record, get a hold list name
print(raw_record)
stock_list = raw_record['id']

ts = TushareApp.ts_app()
for s in stock_list:
    s = s.__int__()
    print(s)
    s = IdConvert.tail2id(str(s))
    print(ts.GetPrice(s))

