# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 08:47:41 2019

@author: yinchao
"""
import threading
import Analyse
import HoldRecordApp
import ThreadQuit
import time


hd = HoldRecordApp.hd_record()
aly = Analyse.Analyse()
raw_record = hd.GetUserStockList() #获取监控列表

task_record_analyse = threading.Thread(target=hd.InfiniteHoldRecordAnalyse)
task_record_analyse.start()
print('成功创建持仓分析线程')

task_guard = threading.Thread(target=aly.AlarmGuard, args=[raw_record])
task_guard.start()
print('成功创建实时预警线程')


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt: #ctrl+c可以正常终止程序
    ThreadQuit.stop_thread(task_guard)
    ThreadQuit.stop_thread(task_record_analyse)
    print('成功销毁所有线程，安全退出')
