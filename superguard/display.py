# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 10:18:49 2019

@author: yinchao
"""
from datetime import datetime
import json
import os
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Page, Radar, Pie, Line
from flask import Flask
from jinja2 import Markup, Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from datetime import timedelta

BASE = os.path.split(os.path.realpath(__file__))[0]

# =============================================================================
# #用户配置区域
# =============================================================================
# 1. 数据存放地址
ASSET_BASE = BASE + r'/output/'
CONFIG_BASE = BASE + r'/Config/'

# 2. 用户根据需要，配置如下三个参数，用于成分分析
growth_item = ['002597', '601012'] # 成长股列表
blue_item = ['000651', '600887'] #蓝筹股列表
defence_item = ['600660', '600377', '600104'] #防守股列表
bond_item = ['019536', '510300', '510310'] #债券列表
    
    
def PlotPie():
    '''
    饼状图，用以展示最新成长股、大蓝筹、防御股、债券的比例
    '''
    growth_amount = 0
    blue_amount = 0
    defence_amount = 0
    bond_amount = 0
    cnt = 0
    MAX_DAY = 30
    
    now = datetime.now()
    while cnt < MAX_DAY:
        try:
            cur_day = now.strftime('%Y%m%d')
            file_name = 'HoldRecord_%s.csv' % cur_day
            df = pd.read_csv(ASSET_BASE + file_name, dtype='str')
            break
        except:
            now -= timedelta(1)
    
    if cnt >= MAX_DAY:
        print('error, cannot find valid data in PlotPie!')
        return
    
    for i in range(len(df)):
        item = df.iloc[i]['id']
        while len(item) != 6:
            item = '0' + item
        print(item)
        price = float(df.iloc[i]['amount']) * float(df.iloc[i]['cur_price'])
        if item in growth_item:
            growth_amount += price
        if item in blue_item:
            blue_amount += price
        if item in defence_item:
            defence_amount += price
        if item in bond_item:
            bond_amount += price
    
    total = growth_amount + blue_amount + defence_amount + bond_amount
    x = round(growth_amount / total * 100, 2)
    y = round(blue_amount / total * 100, 2)
    z = round(defence_amount / total * 100, 2)
    b = round(bond_amount / total * 100, 2)
    
    #绘图
    attr = ["高成长", "大蓝筹", "防御股", "债券"]
    data = [x, y, z, b]
    pie_chart = Pie()
    pie_chart.add("", [list(z) for z in zip(attr, data)])
    pie_chart.set_colors(["red", "blue", "orange",  "green","pink", "purple"])
    pie_chart.set_global_opts(title_opts=opts.TitleOpts(title="持仓成分比"))
    pie_chart.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
#    pie_chart.render()
    return pie_chart

def PlotLine():
    '''
    折线图，用以展示历史资产变动
    '''
    
    df = pd.read_csv(ASSET_BASE + 'AssetOverview.csv',dtype='str')
    
    line_chart = Line()
    line_chart.add_xaxis(list(df['date']))
    line_chart.add_yaxis("asset", list(df['asset']), is_smooth=True)
    line_chart.add_yaxis("earn", list(df['earn']), is_smooth=True)
    line_chart.set_global_opts(title_opts=opts.TitleOpts(title="asset overview"))
    #line_chart.render()
    return line_chart

def PlotRadar():
    '''
    雷达图，用以展示最新的盈利、股债比、持仓率、beta系数、分红率
    '''
    with open(CONFIG_BASE + 'target.json', 'r') as fh:
        para = json.load(fh)
    df = pd.read_csv(ASSET_BASE + 'AssetOverview.csv')
    
    data = df.iloc[-1]
    v1 = [[data['earn_rate'], data['sb_rate'], data['hold_rate'], 1, data['divd_rate']]]
    
    radar_chart = Radar()
    radar_chart.add_schema(
                schema=[
                    opts.RadarIndicatorItem(name="earn_rate", max_=para['earn_rate']),
                    opts.RadarIndicatorItem(name="sb_rate", max_=para['sb_rate']),
                    opts.RadarIndicatorItem(name="hold_rate", max_=para['hold_rate']),
                    opts.RadarIndicatorItem(name="beta", max_=para['beta']),
                    opts.RadarIndicatorItem(name="divd_rate", max_=para['divd_rate']),
                ]
            )
    radar_chart.add("实时参数", v1)
    radar_chart.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    radar_chart.set_global_opts(title_opts=opts.TitleOpts(title="关键参数"))
    #radar_chart.render()
    return radar_chart

def CreateBasic():
    page = Page()
    page.add(PlotRadar())
    page.add(PlotPie())
    return page 
    
def CreateTotal():
    page = Page()
    page.add(PlotLine())
    page.add(PlotRadar())
    page.add(PlotPie())
    return page   

# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))

app = Flask(__name__, static_folder="templates")


@app.route("/")
def index0():
    page = CreateBasic()
    return Markup(page.render_embed())

@app.route("/total/")
def index1():
    page = CreateTotal()
    return Markup(page.render_embed())

# 下面仅供调试
@app.route("/asset/")
def index2():
    page = PlotLine()
    return Markup(page.render_embed())

@app.route("/scale")
def index3():
    page = PlotPie()
    return Markup(page.render_embed())


if __name__ == "__main__":
#    PlotPie()
#    PlotRadar()
    app.run(host='0.0.0.0')
