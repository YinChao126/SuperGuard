# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 10:59:27 2018

@author: yinchao

时间处理模块
APP一览表：
str2dday:输入一个str类型的日期，转换为datetime格式的日期
dday2str:输入datetime日期，转换为str格式的日期（默认'xxxxxxxx'）

str2time:输入一个str类型的时间(默认为xx:xx:xx)，转换为datetime格式的时间
time2str:输入一个time类型的时间，转换为str

time2unix:输入任意格式的时间，转换为int类型的UNIX时间
unix2time:输入UNIX时间，转换为datetime时间

is_equal:判断两个日期是否相等
"""
import time
from datetime import datetime
from datetime import timedelta

    
def str2dday(str_time):
    '''
    str类型的时间转换为datetime类型的时间
    @输入：str类型的时间
    @输出：datetime类型的时间（只有日期，时间统一为0）
    @备注：支持 ". / - "等各种时间格式
          月份和日期必须保证 xx, xx 比如：01 03
    '''
    separator = str_time[4]
    if separator <= '9' and separator >= '0':
        separator = ''
    day_formate = '%Y' + separator + '%m' + separator + '%d'
    return datetime.strptime(str_time,day_formate)
 

def dday2str(dtime,separator = ''):
    '''
    格式转换
    datetime格式转为str
    '''
    day_formate = '%Y' + separator + '%m' + separator + '%d'
    return dtime.strftime(day_formate)

def is_equal(time1, time2):
    '''
    @描述：判断两个日期是否相等
    @输入：time1/time2->两个时间，可以是str格式，亦可以是datetime格式
    @输出：True->相等， False->不等
    '''
    if isinstance(time1, str):
        time1 = str2dday(time1)
    if isinstance(time2, str):
        time2 = str2dday(time2)
    return dday2str(time1) == dday2str(time2)

def str2time(str_time):
    '''
    @描述：输入一个str类型的时间（xx:xx:xx），输出time格式的时间
    @输入：str类型，xx:xx:xx
    @输出：time时间
    @备注：此时日期默认为1900-01-01，为垃圾值，只有时间字段才有用
    '''
    return datetime.strptime(str_time, '%H:%M:%S')
    
    
def time2str(dtime_time):
    '''
    @描述：输入time格式的时间，输出一个str类型的时间（xx:xx:xx）
    @输入：time时间
    @输出：str类型，xx:xx:xx
    '''
    return datetime.strftime(dtime_time, '%H:%M:%S')

def time2unix(datetime_time):
    '''
    @描述：输入一个datetime类型的时间，转换为10位unix时间
    @输入：datetime时间
    @输出：int类型的unix时间
    '''
    a = datetime_time.timetuple()   
    return int(time.mktime(a))
    
def unix2dtime(unix_time):
    '''
    @描述：输入一个unix类型的时间，转换为datetime
    @输入：int类型的unix时间
    @输出：datetime时间
    '''
    return datetime.fromtimestamp(unix_time)
    
if __name__ == '__main__':
    #datetime和str的转换示例
    a = str2dday('2018/2/1') 
    print(a)
    b =dday2str(a,'/')
    print(b)   
    
#    #time和str时间转换
#    a = str2time('13:45:12')
#    print(a)
#    b = time2str(a)
#    print(b)
    
#    #UNIX时间和datetime时间转换示例
#    now = datetime.now()
#    unix_time = time2unix(now)
#    print(unix_time)
#    d_time = unix2dtime(unix_time)
#    print(d_time)
    
    
