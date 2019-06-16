# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 10:08:49 2019

@author: yinchao
"""
import os
import pandas as pd
from datetime import datetime
import TimeConverter

import TushareApp
import Analyse
import IdConvert


class hd_record:
    '''
    @类名： hd_record
    ---------------------------------------------------------------------------
    提供的API一览表：
    HoldRecordAnalyse: 实现持仓完整分析，并自动更新数据库
    ---------------------------------------------------------------------------
    
    辅助函数（用户无需调用）
    get_user_record: 获取用户持仓原始数据（需手动更新！.\Config\hold_record.csv)
    
    特别备注：在使用该app之前，必须先确保手动更新了持仓数据，否则信息就不准了
    '''
    def __init__(self):        
        BASE = os.path.split(os.path.realpath(__file__))[0]
        CFG_PATH = BASE + '\\Config'
        OUT_PATH = BASE + '\\output'
        self.hold_record_file = CFG_PATH+'\\hold_record.csv'
        self.f_total = OUT_PATH + r'\AssetOverview.csv'
        self.f_record = OUT_PATH + r'\HoldRecord_' #备注，此文件名必须加入时间后缀
        self.get_user_record()
        
        self.ts = TushareApp.ts_app()
        self.anly = Analyse.Analyse()
        
    def get_user_record(self):
        '''
        获取用户持仓记录
        备注：该函数会在实例化类时自动调用，用户无需手动调用
        '''        
        self.hold_record = pd.read_csv(self.hold_record_file, dtype={'source':str,'target':str})

        #bug修复，csv文件读取后，会把002597变成3597
        idlist = self.hold_record['id']
        for i in range(len(idlist)):
            str_id = str(idlist[i])
            if len(str_id) != 6:
                n0 = 6 - len(str_id)
                str_id = n0*'0' + str_id
                self.hold_record.loc[i, 'id'] = str_id
#        print(self.hold_record)
        return self.hold_record
    
    def test(self):
        str_id = '600104.SH'
        est, level = self.anly.Estimation(str_id)
        print(est, level)
        
    def HoldRecordAnalyse(self):
        '''
        更新时间：2019-6-16
        描述：实现持仓的完整分析与存档
        具体包括：总资产、盈亏率、股债比、股息率的宏观分析。个股盈亏，估值的微观分析
        '''
        
        earn_list = [] #盈亏率
        guxi_list = [] #股息率
        curprice_list = [] #当前股价
        estprice_list = [] #当前估值
        
        now = TimeConverter.dtime2str(datetime.now())
        
        #1. 个股分析
        id_list = self.hold_record['id']
        for i in range(len(id_list)): #每一个个股
            str_id = IdConvert.tail2id(str(id_list[i]))
            print(str_id)
            unit_price = self.hold_record.iloc[i]['unit_price']
#            print(unit_price)
            price, pct_chg = self.ts.Daily(str_id)
            curprice_list.append(price)
            earn_rate = round(((price - unit_price) / unit_price) * 100,2)
            earn_list.append(earn_rate) #获取盈亏率
#            print(earn_rate)
            est, level = self.anly.Estimation(str_id)
            print(est, level)
            estprice_list.append(round(est,2)) #获取估值
            guxi_list.append(0) #获取股息率， 暂时不管
            print('finished\n')
        
        return
        data = {
                'earn_ratio':earn_list,
                'cur_price':curprice_list,
                'est_price':estprice_list,
                'bond_rate':guxi_list
                }
        df2 = pd.DataFrame(data)
        single_record = pd.concat([self.hold_record,df2],axis=1)
        print(single_record)
        self.f_record += now + r'.csv'
        single_record.to_csv(self.f_record)
        
        #2. 总体分析
        # 先获取个股的当前股价、估值、股息率
        # 再计算总资产、盈亏率、股债比、整体股息率
#        print(self.ts.GetPrice())
        total_cost = 0
        total_asset = 0 #总资产
        stock_acc = 0 
        for i in range(4):
#        for i in range(len(single_record)):
            amount = single_record.iloc[i]['amount']
            unit_price = single_record.iloc[i]['unit_price']
            cur_price = single_record.iloc[i]['cur_price']
            bond_rate = single_record.iloc[i]['bond_rate']
            total_cost += amount * unit_price
            total_asset += amount * cur_price
            str_id = str(single_record.iloc[i]['id'])
            id_type = IdConvert.get_id_type(str_id)
            print(str_id, id_type)
            if id_type < 2:
                stock_acc += amount * cur_price
        
        t_earn = total_asset - total_cost
        t_earn_rate = (total_asset - total_cost) / total_cost
        print(t_earn_rate)
        sb_rate = round((stock_acc / total_asset),2)
        print(sb_rate)

#        #写入文件
#        with open(self.f_total, 'a') as fh:
#            fh.write('')
#        
        
if __name__ == '__main__':
    app = hd_record()
    app.HoldRecordAnalyse()
#    app.test()