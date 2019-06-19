# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 10:08:49 2019

@author: yinchao
"""
import os
import pandas as pd
from datetime import datetime
import TimeConverter

import SinaApp
import TushareApp
import Analyse
import IdConvert

class hd_record:
    '''
    @类名： hd_record
    ---------------------------------------------------------------------------
    提供的API一览表：
    GetUserStockList: 获取用户持仓个股的ID号
    HoldRecordAnalyse: 实现持仓完整分析，并自动更新数据库（暂时存为本地csv文件）
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
        self.sina = SinaApp.SinaApp()
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
        return self.hold_record
    
    def GetUserStockList(self):
        '''
        获取用户持股记录，以list形式存在
        '''
#        print(self.hold_record)
        id_list = self.hold_record['id']
        result = []
        for s in id_list:
            result.append(IdConvert.tail2id(str(s)))
#        print(result)
        return result
        
        
    def HoldRecordAnalyse(self):
        '''
        @更新时间：2019-6-18
        @描述：实现持仓的完整分析与存档
        具体包括：总资产、盈亏率、股债比、股息率的宏观分析。个股盈亏，估值的微观分析
        @输入：系统自动读入./Config/hold_record.csv文件，获取用户持仓记录（需手动修改）
        @输出：
        1. ./output/文件夹下新建一个： HoldRecord_xxxxxx.csv，保存持仓个股详细记录
        2. ./output/AssetOverview.csv增加一条持仓的总体分析记录
        '''
        earn_list = [] #盈亏率
        guxi_list = [] #股息率
        curprice_list = [] #当前股价
        estprice_list = [] #当前估值
        
        now = TimeConverter.dday2str(datetime.now())
        #1. 个股分析
        id_list = self.hold_record['id']
        for i in range(len(id_list)): #每一个个股
            str_id = IdConvert.tail2id(str(id_list[i]))
            unit_price = self.hold_record.iloc[i]['unit_price']
            price = self.sina.RtPrice(str_id)
            if price <= 0:
                print('服务器维护，无法获取实时数据')
                return 0
            curprice_list.append(price)
            earn_rate = round(((price - unit_price) / unit_price) * 100,2)
            earn_list.append(earn_rate) #获取盈亏率
            est, level = self.anly.Estimation(str_id)
#            est = 1 #注释上一句，开启此处可以加快测试速度
            estprice_list.append(round(est,2)) #获取估值
            guxi_rate = round(self.hold_record.iloc[i]['divd_eps'] * 100 / price, 2) #股息率
            guxi_list.append(guxi_rate) #每股现金分红（暂时手动更新）
            
        data = {
                'earn_rate':earn_list,
                'cur_price':curprice_list,
                'est_price':estprice_list,
                'bond_rate':guxi_list
                }
        df2 = pd.DataFrame(data)
        single_record = pd.concat([self.hold_record,df2],axis=1)

        head = ['id','amount','divd_eps','unit_price','cur_price','est_price','earn_rate','bond_rate']
        single_record = single_record.reindex(columns=head)
        self.f_record += now + r'.csv'
        single_record.to_csv(self.f_record, index = False)

        #2. 总体分析
        # 先获取个股的当前股价、估值、股息率,再计算总资产、盈亏率、股债比、整体股息率
        total_cost = 0 #总成本
        total_asset = 0 #总资产
        stock_acc = 0 #股票总资产
        bond_acc = 0 #累积现金分红
        for i in range(len(single_record)):
            amount = single_record.iloc[i]['amount']
            unit_price = single_record.iloc[i]['unit_price']
            cur_price = single_record.iloc[i]['cur_price']
            bond_acc += single_record.iloc[i]['divd_eps'] * amount
            total_cost += amount * unit_price
            total_asset += amount * cur_price
            str_id = str(single_record.iloc[i]['id'])
            id_type = IdConvert.get_id_type(str_id)
            if id_type < 2:
                stock_acc += amount * cur_price
        total_cost = int(total_cost)
        t_earn = total_asset - total_cost
        t_earn_rate = int((total_asset - total_cost) / total_cost * 100)
        sb_rate = round((stock_acc / total_asset)*100,2)
        dividend_rate = round(bond_acc / total_asset * 100, 2)

        try:
            records = pd.read_csv(self.f_total, dtype=str)
        except:
            header = ['date','cost','asset','earn','earn_rate','sb_rate','divd_rate']
            records = pd.DataFrame(columns=header)
        if records.empty == True:
            print('empty')
        
        date = TimeConverter.dday2str(datetime.now())
        data = {
                'date':[date],
                'cost':[total_cost],
                'asset':[total_asset],
                'earn':[t_earn],
                'earn_rate':[t_earn_rate],
                'sb_rate':[sb_rate],
                'divd_rate':[dividend_rate]
                }
        new_record = pd.DataFrame(data) #新增的一条记录
        records = pd.concat([records,new_record],axis=0)
        
        records = records.drop_duplicates(subset=['date'],keep='last') #去重，防止多次运行
        head = ['date','cost','asset','earn','earn_rate','sb_rate','divd_rate']
        records = records.reindex(columns=head)    
        records.to_csv(self.f_total, index = False)
        return data
        
if __name__ == '__main__':
    app = hd_record()
    #直接运行持仓分析APP
    a = app.HoldRecordAnalyse()
    
    #获取用户持仓ID列表
#    a = app.GetUserStockList()
