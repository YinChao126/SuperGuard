# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 15:03:02 2019

@author: yinchao
"""
import os
import json

import TushareApp

class Algorithm:
    def __init__(self):
        BASE = os.path.split(os.path.realpath(__file__))[0]
        self.cfg_file = BASE + r'\Config\threshold.json' 
        with open(self.cfg_file, 'r') as fh: #读取配置参数
            parameter = json.load(fh)
            self.rate_th = parameter['rate_th']
            self.turnover_th = parameter['turnover_th']
            self.price_th = parameter['price_th']
        
        self.ts = TushareApp.ts_app()  
        
        self.whitelist = []
        
    def alarm_mask(self, id):
        '''
        如果已经预警，则加入白名单，停牌后会自动释放（中午11点半，下午3点）
        '''        
        self.whitelist.append(id)
        
    def reset(self):
        '''
        重置状态，将白名单剔除
        '''
        self.whitelist = []
    
    def check(self, item):
        '''
        辅助函数：
        描述：输入一条标准的tushare实时信息，判断是否正常，如果不正常，则返回异常值
        其中：item只能来源于TushareApp.BasicInfo函数
        其类型为DataFrame格式，字段由TushareApp决定
        
        返回值：
        -1 输入值非法
        0 正常
        1 异动（换手率、股价、估值）
        '''
        
        #1. 输入格式检查
        #2. 获取该个股的平均估值，平均换手率
        code = item.iloc[0]['ts_code']
        cur_turnover = item.iloc[0]['turnover_rate']
        
        
        if item.iloc[0]['ts_code'] in self.whitelist: #如果在白名单内，则
            return 0
        
        avg_turnover, pe, pb = self.ts.AvgExchangeInfo(code,3) #[换手率，PEttm, PB]
#        print(avg_turnover)
        #1. 换手率异常检测
        turover_change = (cur_turnover - avg_turnover) / cur_turnover
        if turover_change < self.turnover_th[0] or turover_change > self.turnover_th[1]:
            return 1
        
        #2. 涨跌幅异常检测
        
        #3. 估值异常检测
        
        return 0
        
if __name__ == '__main__':
    ts = TushareApp.ts_app()
    alg = Algorithm()
    test = ts.BasicInfo('600660.SH')
    app = alg.check(test)