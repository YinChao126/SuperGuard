# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 10:18:49 2019

@author: yinchao
"""

import json
import os
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Page, Radar, Grid
from pyecharts.charts import Line
from flask import Flask
from jinja2 import Markup, Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

BASE = os.path.split(os.path.realpath(__file__))[0]
ASSET_BASE = BASE + r'/output/'
CONFIG_BASE = BASE + r'/Config/'

def PlotLine():
    
    df = pd.read_csv(ASSET_BASE + 'AssetOverview.csv',dtype='str')
    
    app = Line()
    app.add_xaxis(list(df['date']))
    app.add_yaxis("asset", list(df['asset']), is_smooth=True)
    app.add_yaxis("earn", list(df['earn']), is_smooth=True)
    app.set_global_opts(title_opts=opts.TitleOpts(title="asset overview"))
    app.render()
    return app

def PlotRadar():
    '''
    绘出持仓结构分析图
    '''
    with open(CONFIG_BASE + 'target.json', 'r') as fh:
        para = json.load(fh)
    df = pd.read_csv(ASSET_BASE + 'AssetOverview.csv')
    
    data = df.iloc[-1]
    v1 = [[data['earn_rate'], data['sb_rate'], data['hold_rate'], 1, data['divd_rate']]]
    
    app = Radar()
    app.add_schema(
                schema=[
                    opts.RadarIndicatorItem(name="earn_rate", max_=para['earn_rate']),
                    opts.RadarIndicatorItem(name="sb_rate", max_=para['sb_rate']),
                    opts.RadarIndicatorItem(name="hold_rate", max_=para['hold_rate']),
                    opts.RadarIndicatorItem(name="β", max_=para['β']),
                    opts.RadarIndicatorItem(name="divd_rate", max_=para['divd_rate']),
                ]
            )
    app.add("实时参数", v1)
    app.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    app.set_global_opts(title_opts=opts.TitleOpts(title="持仓分析"))
    app.render()
    return app

def CreatePage():
    page = Page()
    
    df = pd.read_csv(ASSET_BASE + 'AssetOverview.csv',dtype='str')
    line = Line()
    line.add_xaxis(list(df['date']))
    data = list(df['asset'])
    asset = []
    for i in data:
        asset.append(round(float(i)/10000,2))
    line.add_yaxis("asset", asset, is_smooth=True)
    data = list(df['earn'])
    earn = []
    for i in data:
        earn.append(round(float(i)/10000,2))
    line.add_yaxis("earn", earn, is_smooth=True)
    line.set_global_opts(title_opts=opts.TitleOpts(title=" "))
    page.add(line)
    
    with open(CONFIG_BASE + 'target.json', 'r') as fh:
        para = json.load(fh)
    
    data = df.iloc[-1]
    v1 = [[data['earn_rate'], data['sb_rate'], data['hold_rate'], 1, data['divd_rate']]]
    
    radar = Radar()
    radar.add_schema(
                schema=[
                    opts.RadarIndicatorItem(name="earn_rate", max_=para['earn_rate']),
                    opts.RadarIndicatorItem(name="sb_rate", max_=para['sb_rate']),
                    opts.RadarIndicatorItem(name="hold_rate", max_=para['hold_rate']),
                    opts.RadarIndicatorItem(name="beta", max_=para['beta']),
                    opts.RadarIndicatorItem(name="divd_rate", max_=para['divd_rate']),
                ]
            )
    radar.add("实时参数", v1)
    radar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    radar.set_global_opts(title_opts=opts.TitleOpts(title=" "))
    page.add(radar)
    return page   

# 关于 CurrentConfig，可参考 [基本使用-全局变量]
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("./templates"))

app = Flask(__name__, static_folder="templates")
@app.route("/")
def index():
    page = CreatePage()
    return Markup(page.render_embed())

@app.route("/asset/")
def index2():
    page = PlotLine()
    return Markup(page.render_embed())

@app.route("/hold/")
def index3():
    page = PlotRadar()
    return Markup(page.render_embed())
if __name__ == "__main__":
    app.run(host='0.0.0.0')
