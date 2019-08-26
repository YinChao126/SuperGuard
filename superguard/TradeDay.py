# -*- coding: utf-8 -*-
"""
Created on Sun May 20 16:23:28 2018

@author: YinChao
@date: 20180520
"""

import urllib.request as request  
from datetime import datetime 
import time 
'''  
@query a single date: string '20170401';  
@api return day_type: 0 workday 1 weekend 2 holiday -1 err  
@function return day_type: 1 workday 0 weekend&holiday  
'''  
'''
更新时间：2019-6-18
提供的API一览表
is_work_time: 现在是否为交易时间
is_tradeday: 今天是否为交易日
get_day_type: 判断今天是工作日，周末还是节假日

'''
def is_work_time():
    '''
    辅助函数，用来判断当前是否为交易时间 （没有测试过）
    输出：False -> 非交易时间， True -> 交易时间
    备注：此处还有完善空间，如果是非工作日，也要判断为False！
    '''
    now = datetime.now()
    if now.hour >= 15 or now.hour < 9 or now.hour == 12:
        return False
    if now.hour == 9 and now.minute < 30:
        return False
    if now.hour == 11 and now.minute >= 30:
        return False
    return True
  
def is_tradeday():
    '''
    判断今天是否股市交易日（考虑了节假日的影响）
    '''  
    query_date = datetime.strftime(datetime.today(), '%Y%m%d')  
    return _is_tradeday(query_date)  


def get_day_type(query_date): 
    '''
    节假日求取辅助函数，从指定网址上获取当日状态
    0工作日    1周末     2节假日
    http://tool.bitefu.net/jiari/?d=20181009  返回0（工作日）
    http://tool.bitefu.net/jiari/?d=20181014  返回1（周末）
    http://tool.bitefu.net/jiari/?d=20181001  返回2（国庆节）
    '''
    url = 'http://tool.bitefu.net/jiari/?d=' + query_date  
    resp = request.urlopen(url)  
    try:
        content = resp.read().decode('utf-8')
        if '0' in content:
            return 0
        elif '1' in content:
            return 1
        elif '2' in content:
            return 2
        else:
            return -2
    except:
        return -1

###############################################################################
def isWorkingTime():
    '''
    判断当前时刻是否工作日上班时间（未考虑节假日影响）
    '''
    workTime=['09:00:00','18:00:00']
    dayOfWeek = datetime.now().weekday()
    beginWork=datetime.now().strftime("%Y-%m-%d")+' '+workTime[0]
    endWork=datetime.now().strftime("%Y-%m-%d")+' '+workTime[1]
    beginWorkSeconds=time.time()-time.mktime(time.strptime(beginWork, '%Y-%m-%d %H:%M:%S'))
    endWorkSeconds=time.time()-time.mktime(time.strptime(endWork, '%Y-%m-%d %H:%M:%S'))
    if (int(dayOfWeek) in range(5)) and int(beginWorkSeconds)>0 and int(endWorkSeconds)<0:
        return 1
    else:
        return 0   

def isWorkingDay():
    '''
    判断今天是否工作日
    '''
    dayOfWeek = datetime.now().weekday()   #今天星期几？
    if dayOfWeek < 6:
        return 1
    else:
        return 0     
  
def _is_tradeday(query_date):  
    '''
    辅助函数
    判断给定日期是否股市交易日（考虑了节假日的影响）
    '''
    weekday = datetime.strptime(query_date, '%Y%m%d').isoweekday() 
    if weekday <= 5 and get_day_type(query_date) == 0:  
        return True  
    else:  
        return False  
  
if __name__ == '__main__':  
    print(_is_tradeday('20190824'))  
    print(is_tradeday()) 
    