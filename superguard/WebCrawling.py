# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 11:04:49 2019

@author: yinchao
"""

import requests
from requests.exceptions import RequestException
import re
import json
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}

def get_one_page(url):
    '''
    给定网址，获取原始网页内容
    '''
    try:
        response = requests.get(url,headers = headers)
        response.encoding = 'GB2312'
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None
    
def GetTable(html):
    '''
    根据输入的网页，解析出表格信息，以DataFrame格式给出
    未完成，无法实现解析
    '''    
    try:
        soup = BeautifulSoup(html,'html5lib')
#        print(soup)
        l = soup.select('table')
        l = l[13] #找到那个表
        ls = l.tbody
        lls = ls.select('td')
        for i in lls:
            print(i.attrs)
    except:
        return 0
    
if __name__ == '__main__':
    url = 'http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/600660.phtml'
    html = get_one_page(url)
    
    GetTable(html)
#    print(html)    