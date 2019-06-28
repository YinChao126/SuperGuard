# SuperGuard

​	SuperGuard是炒股程序员的福音，是一款开源自动盯盘与持仓分析的工具，主要具备如下功能：

- 实时监视股票异动并自动推送报警信息(券商的APP也有该功能，但是要付费，且有各种限制)
- 记录每日持仓的详细情况
- 记录持仓结构的总体分析，包括盈亏水平、股债比、股息率

## 1. 如何安装

在SuperGuard根目录下python build.py，自动安装

## 2. 如何配置

用户需要手动在./superguard/Config目录下完善如下信息

### 用户持仓信息：

hold_cash.json 记录账户现金和历史盈亏信息

- cash 账户现金
- acc_earn 已经结算的盈亏额（不是浮盈）

hold_record.csv 记录用户持仓信息

- amount代表持股数量
- id代表个股ID代码
- unit_price代表成本价
-  divd_eps代表最近的每股现金分红

### 工程配置信息：

threshold.json 实时监控参数配置（超标则触发报警信息推送）

- rate_th：个股涨跌幅上下限，单位是点数（百分之几，几个点）
- quant_th：量比
- price_est:[-0.2, 0.2] ，如果实时股价超过或低于价值线20%，触发报警

tushare_tocken.cfg，tushare使用所需的tocken值

twilio_para.json，twilio使用所需的配置参数，请参考 [利用twilio收发短信](http://uuxn.com/twilio-toll-free-sms)

## 3. 如何部署运行

直接运行下列指令即可，系统会无限运行下去。

nohup python3 main.py & 

## 4. 如何查看输出结果

请在./superguard/output文件夹下查看输出结果。每天会在AssetOverview文件里增添一条记录，每天会在收盘的时候创建一个HoldRecord_2019xxxx.csv文件，记录当天持仓情况

## 5. 如何自定义开发和调试

HoldRecordApp是一个持仓分析器，能够每日分析持股情况并记录再案

Analyse是一个实时盯盘器，能够在开盘阶段实时关测股价异动，并触发报警信息

用户可以自定义如上两个模块。其余均为基础模块，用户勿动

## Enjoy！





