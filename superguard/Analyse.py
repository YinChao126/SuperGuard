# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 15:03:02 2019

@author: yinchao
"""
import os
import json
import time
from datetime import datetime
from datetime import timedelta
import pandas as pd
import TimeConverter
import IdConvert
import Inform
import TradeDay

import TushareApp
import SinaApp

class Analyse:
    '''
    类名：Analyse
    功能：实现给定标的的分析功能，包括预警分析，持仓结构分析，收益率分析，并提出建议
    更新时间：2019-6-16
    API一览表：
    Estimation：实现个股的估值功能
    AlarmGuard: 实现预警监测功能
    '''
    def __init__(self):
        self.log = False #关闭log
        
        BASE = os.path.split(os.path.realpath(__file__))[0]
        self.cfg_file = BASE + r'\Config\threshold.json' 
        self.rate_th = [] #涨跌幅阈值【下限，上限】
        self.turnover_th = [] #换手率阈值【下限，上限】
        self.price_est = [] #估值预警线【低估，高估】
        with open(self.cfg_file, 'r') as fh: #读取配置参数
            parameter = json.load(fh)
            self.rate_th = parameter['rate_th']
            self.quant_th = parameter['quant_th']
            self.price_est = parameter['price_est']
            
        self.ts = TushareApp.ts_app()  
        self.sina = SinaApp.SinaApp()
        self.hold_record = [] #用户持仓记录
        self.whitelist = [] #警报白名单，防止多次预警
        
        #短信预警配置
        self.phone = '15712091836'
        self.info_msg = Inform.Inform()
    def AlarmMask(self, str_id):
        '''
        如果已经预警，则加入白名单，停牌后会自动释放（中午11点半，下午3点）
        '''        
        self.whitelist.append(str_id)
        
    def AlarmReset(self):
        '''
        重置状态，将白名单剔除
        '''
        self.whitelist = []
            
    def AlarmGuard(self, item_list):
        '''
        @描述：给定一组监控标的的参数，自动启动线程进行监视，
        当成交量、涨跌幅、估值任意指标异常，都会触发手机短信预警机制，同时该个股被锁定一段
        时间防止重复告警
        备注：机制仍然不完善，没有优先级，如果低级别预警触发，则高级别的预警也会失效。
        
        '''
        print('参数初始化,请等待。。。')
        interval_seconds = 30  #每30秒自动检查一次
        unlock_time_minute = 15 #每15分钟清除锁定状态
        
        self.est_list = {}
        for s in item_list:
            est, level = self.Estimation(s) #自动更新获取估计值
            self.est_list[s]=est
        print('开始监控')
        cnt = 0
        while True:
            if TradeDay.is_work_time() == False: #非工作时间
                print('不是交易时间')
                time.sleep(60)
                continue
            
            for s in item_list: #依次检查列表，判断是否正常
                if s in self.whitelist: #如果该ID被列入白名单，则解锁前不会再次预警
                    continue
                
                status = self.check(s)
                if status < 0:
                    print('输入值非法，检测失败')
                elif status == 1:
                    msg = s+'成交量异常，量比突破3，请检查！'
                    print(msg)
                    self.info_msg.SendMsg(self.phone, msg)
                    self.AlarmMask(s)
                elif status == 2:
                    msg = s+'涨跌幅异常，请注意！'
                    print(msg)
                    self.info_msg.SendMsg(self.phone, msg)
                    self.AlarmMask(s)
                elif status == 3:
                    msg = s+'成交量异常，涨跌幅异常，请仔细检查！'
                    print(msg)
                    self.info_msg.SendMsg(self.phone, msg)
                    self.AlarmMask(s)
                elif status == 4:
                    msg = s+'估值异常，请注意！'
                    print(msg)
                    self.info_msg.SendMsg(self.phone, msg)
                    self.AlarmMask(s)
                elif status == 5:
                    msg = s+'成交量异常，估值异常，请仔细检查！'
                    print(msg)
                    self.info_msg.SendMsg(self.phone, msg)
                    self.AlarmMask(s)
                elif status == 6:
                    msg = s+'涨跌幅异常，估值异常，请仔细检查！'
                    print(msg)
                    self.info_msg.SendMsg(self.phone, msg)
                    self.AlarmMask(s)
                elif status == 7:
                    msg = s+'全部异常，机会来了请把握'
                    print(msg)
                    self.info_msg.SendMsg(self.phone, msg)
                    self.AlarmMask(s)
                    
            if cnt >= 60 / interval_seconds * unlock_time_minute: #定期解锁白名单
                cnt = 0
                self.AlarmReset()
                
            cnt += 1
            print(cnt)
            time.sleep(interval_seconds) #每次检查完毕，休息一定时间
            
    def check(self, str_id):
        '''
        辅助函数：
        描述：输入id，判断是否正常，如果不正常，则返回异常值
        其中：str_id可以是xxxxxx,shxxxxxx,xxxxxx.SH三种中的任意类型
        
        返回值：
        -1 输入值非法
        0 正常
        ret 异常反应（3-7位为0）
        bit0: 量比异常
        bit1: 股价异常
        bit2: 估值异常
        例如： ret=3（量比异常+股价异常） ret=7（全部异常）
        '''
        ret = 0
        
        if str_id in self.whitelist: #如果在白名单内，则
            return 0
        
        #1. 换手率异常检测
        if self.sina.RtQuant(str_id) > self.quant_th:
            ret += 1
        
        #2. 涨跌幅异常检测
        rate_change = self.sina.RtChg(str_id)
        if rate_change < self.rate_th[0] or rate_change > self.rate_th[1]:
            ret += 2
        
        #3. 估值异常检测
        cur_price = self.sina.RtPrice(str_id)
        est_price = self.est_list.get(str_id)
        percentage = (cur_price - est_price) / est_price
        if percentage < self.price_est[0] or percentage > self.price_est[1]:
            ret += 4
        return ret
        
        
#    def check(self, item):
#        '''
#        辅助函数：
#        描述：输入一条标准的tushare实时信息，判断是否正常，如果不正常，则返回异常值
#        其中：item只能来源于TushareApp.BasicInfo函数
#        其类型为DataFrame格式，字段由TushareApp决定
#        
#        返回值：
#        -1 输入值非法
#        0 正常
#        ret 异常反应（3-7位为0）
#        bit0: 换手率异常
#        bit1: 股价异常
#        bit2: 估值异常
#        例如： ret=3（换手率异常+股价异常） ret=7（全部异常）
#        '''
#        
#        #1. 输入格式检查
#        #2. 获取该个股的平均估值，平均换手率
#        code = item.iloc[0]['ts_code']
#        cur_turnover = item.iloc[0]['turnover_rate']
#        ret = 0
#        
#        if item.iloc[0]['ts_code'] in self.whitelist: #如果在白名单内，则
#            return 0
#        
#        avg_turnover, pe, pb = self.ts.AvgExchangeInfo(code,3) #[换手率，PEttm, PB]
##        print(avg_turnover)
#        #1. 换手率异常检测
#        turover_change = (cur_turnover - avg_turnover) / cur_turnover
#        if turover_change < self.turnover_th[0] or turover_change > self.turnover_th[1]:
#            ret += 1
#        
#        #2. 涨跌幅异常检测
#        cur_price, rate_change = self.ts.Daily(code)
#        if rate_change < self.rate_th[0] or rate_change > self.rate_th[1]:
#            ret += 2
#        
#        #3. 估值异常检测
#        est_price, level = self.Estimation(code)
#        percentage = (cur_price - est_price) / est_price
#        if percentage < self.price_est[0] or percentage > self.price_est[1]:
#            ret += 4
#        return ret
        
    

    def Estimation(self, ID, est_growth=0, confidence=0.5):
        '''
        更新：2019-6-15
        描述：输入ID和增长率手算值，自动得到目标价和溢价比率，提供投资建议
        输入：
        @ID(str)->个股ID号
        @est_growth(float)[0~1]->手动预测今年的增长率
        @confidence(float)[0~1]->计算结果的不确定度[0-1]，越是可预测的，confidence越高
        输出：无
        返回值：
        @ est_price(float)-> 年底目标价
        @ flow_level(int) -> 溢价等级[-3,3],详见下文的溢价表定义
        '''
        #1.参数输入
        if IdConvert.get_id_type(ID) >= 2: #如果是非A股的标的，直接返回当前现价
            est_price = self.sina.RtPrice(ID)
            return est_price, 0
        
        ts_app = TushareApp.ts_app()
        avg_growth = ts_app.AvgGrowthInfo(ID,5)#过去5年eps平均增长率，财报爬取
        if est_growth == 0:
            est_growth = avg_growth
        turnover, avg_pe, avg_pb = ts_app.AvgExchangeInfo(ID, 3)#过去3年平均PE、换手率
        basic = ts_app.BasicInfo(ID) #最近收盘的基本情况
        cur_pe= basic.iloc[-1]['pe']
        cur_pe_ttm= basic.iloc[-1]['pe_ttm']
        cur_price = basic.iloc[-1]['close']
        cur_eps = cur_price / cur_pe #当前的eps
        if self.log:
            print('统计参数一览表\n当天水平：(price, pe, pe_ttm):',cur_price,cur_pe,cur_pe_ttm)
#        print(basic)
        avg_pe_raw = avg_pe
        #成长型股票PE修正
        company_type = 0
        if avg_growth > 0.5: #50%以上算高增长，PE打8折，此时的PE不靠谱！
            avg_pe *= 0.8
            company_type = '高成长'
        elif avg_growth > 0.3: #30%以上算中高速增长，PE打9折
            avg_pe *= 0.9
            company_type = '中高成长'
        elif avg_growth > 0.15: #15%以上算中速,PE打95折
            avg_pe *= 0.95
            company_type = '稳健型'
        else:
            company_type = '低成长成熟企业'
        confidence = 0.2 + confidence * 0.6#实际权值范围[0.2-0.8]，防止过分自信和悲观
        growth = round(avg_growth * (1-confidence) + est_growth * confidence, 4)
        if self.log:
            print('历史平均PE_TTM:',avg_pe_raw,'平均增长率：',avg_growth)
            print('加权PE_TTM:',avg_pe,'\t加权growth:',growth)
            print('--------------------------------------------------')
            #2.中间变量计算
            
            
            print('开始估值...')

        '''
        静态估值（年报+平均市盈率+平均增长率估值）： 
        年尾价格 = 历史加权平均市盈率 * 去年年报上除非每股收益 * （1 + 增长率）
        说明：该方法估值相对较准确，但是
        备注：此种方法必须等最近一年年报出来才有用，一般是5月以后再查比较好
        '''
        t1 = datetime.now()
        data = ts_app.GetFinanceTable(ID,1)
        dt_eps = data.iloc[0]['dt_eps']
        if isinstance(dt_eps,float) == False:
            print('警告：无法获取除非每股收益，用每股收益替代，有风险')
            dt_eps = data.iloc[0]['eps']
        report_time = data.iloc[0]['end_date']
        report_time = TimeConverter.str2dday(report_time)
        delta = t1 - report_time
        if delta.days > 365:
            if self.log:
                print('警告：去年的年报还没出来，静态预测值没意义')
        static_est = avg_pe * dt_eps * (1+growth)
        if self.log:
            print('静态预测值：',static_est)
            print('(pe,eps,growth):',avg_pe,dt_eps,growth)
        
        '''
        动态估值（现价+动态市盈率估值）： 
        年尾价格 = 当前价格 / 当前PE_TTM * 预期PE_TTM * （1 + 增长率/4）
        备注：此处由于是PE_TTM，所以增长预期基本上已经包含在股价里去了，
        只有最近一个季度增长没有反应到股价上去，所以增长率除以4
        '''
        est_price_growth = cur_price / cur_pe_ttm * avg_pe * (1+growth/4)
        if self.log:
            print('动态预测值：',est_price_growth)
            print('(cur_price, cur_pe, avg_pe):',cur_price, cur_pe_ttm, avg_pe)
        
#        print('估值定义：增长估值指根据已有增长形势估计年末的估价，现价估值指当前价格估计')
#        print('现价:',cur_price,'增长估值：',round(est_price_growth,2),'现价估值：',round(est_price_pe,2))

        est_price = min(static_est, est_price_growth)
        overflow_rate = (cur_price - est_price) / est_price
        '''
        市值表现核对，估值溢价计算与投资建议
        溢价定义：
        [ >  0.20] 绝对高估，  【空仓】
        [ 0.10 ~ 0.20]明显高估 【停止增持->减仓】
        [ 0.05 ~ 0.10]略高估， 【谨慎增持->停止增持】
        [-0.05 ~ 0.05]正常    【正常定投】
        [-0.10 ~-0.05]略低估， 【开始增持】
        [-0.20 ~-0.10]明显低估 【大幅增持】
        [ ~ -0.20] 绝对低估，  【满仓】
        返回值表示：溢价水平[-3,-2,-1,0,1,2,3]从低估到高估排列
        '''  
        
        flow_level = 0 #溢价水平
        if overflow_rate > 0.2:
            flow_level = 3
        elif overflow_rate > 0.1 and overflow_rate <= 0.2:
            flow_level = 2
        elif overflow_rate > 0.05 and overflow_rate <= 0.1:
            flow_level = 1
        elif overflow_rate > -0.05 and overflow_rate <= 0.05:
            flow_level = 0
        elif overflow_rate > -0.1 and overflow_rate <= -0.05:
            flow_level = -1
        elif overflow_rate > -0.2 and overflow_rate <= -0.1:
            flow_level = -2
        else:
            flow_level = -3
        if self.log:
            print('--------------------------------------------------')
            print('结论：')
            print('企业类型判断：',company_type)
            print('参考溢价等级：',flow_level)
        return est_price, flow_level
    
if __name__ == '__main__':
    app = Analyse()
    
#    #估值
#    est_price, flow_level = app.Estimation('510300.SH',0.1,0.7)
#    print(est_price)
    
    #预警
    item_list = ['600660.SH', '601012.SH']
    app.AlarmGuard(item_list)
    