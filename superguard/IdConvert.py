# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 10:13:17 2019

@author: yinchao
"""

'''
描述：本模块用于实现id号的切换，方便不同库需要不同的格式，同时实现股票类型的判断
前缀格式：sina财经的标准   shxxxxxx
后缀格式：tushare标准     xxxxxx.SH
无格式：xxxxxx

修改日期：2019-6-17

基础知识：
详细定义请见：https://www.cnblogs.com/xuliangxing/p/8492705.html
沪市： 600,601,603开头
深市： 000,002,300开头
债券： 159,019等（完全搞不清坨）
基金： 5xx开头

开放API一览表：
front2id
    描述：增加前缀，用于和sina库挂钩    
    600660 -> sh600660
    
tail2id
    描述：增加后缀，用于和tushare库挂钩
    600660 -> 600660.SH
    
get_id_type
    描述：给定一个id，判断该个股到底是什么类型（深市，沪市，债券，基金，指数？）
'''

hushi_prefix = ['600','601','603','019','510'] #上海证券前缀
shenshi_prefix = ['000','002','300','159'] #深圳证券前缀
stock_hu = ['600','601','603'] #上海A股前缀
stock_sz = ['000','002','300'] #深圳A股前缀

def front2id(id):
    '''
    输入：必须是不带前后缀的 600660
    描述：600660 -> sh600660
    '''
    if len(id) != 6:
        print('股票id输入非法')
        return 0
    prefix = id[:3]
    if prefix in hushi_prefix:
        return 'sh'+id
    if prefix in shenshi_prefix:
        return 'sz'+id
    print('错误，front2id不完善')
    
def tail2id(id):
    '''
    输入：必须是不带前后缀的 600660
    描述：600660 -> 600660.SH
    '''
    if len(id) != 6:
        print('股票id输入非法')
        return 0
    prefix = id[:3]
    if prefix  in hushi_prefix:
        return id+'.SH'
    if prefix  in shenshi_prefix:
        return id+'.SZ'


def get_id_type(id):
    '''
    输入：600660, sh600660, 600660.SH都支持
    描述：输入一个ID，判断其类型
    返回类型定义：
    0沪市
    1深市
    2债券
    3指数
    4基金(含指数基金和债券基金)
    '''
    if len(id) == 6:
        id = tail2id(id)
    elif len(id) == 8:
        id = tail2id(id[2:])
    elif len(id) == 9:
        pass
    else:
        print('股票id输入非法')
        return -1
    
    code = id[:6]
    sub_type = id[-2:]
    sub_type = sub_type.upper() #转大写
    
    if sub_type == 'SH':
        prefix = code[:3]
        if prefix in stock_hu:
            return 0
        elif prefix == '000':
            return 3
        elif prefix == '500' or prefix == '510':
            return 4
        else: #其余全是债券
            return 2 
        
    elif sub_type == 'SZ':
        prefix = code[:3]
        if prefix in stock_sz:
            return 1
        elif prefix == '159':
            return 4
        else: #其余全是债券
            return 2 
    else:
        print('股票id输入非法')
    return 1

if __name__ == '__main__':
    str_id = '600660'
    print(str_id)
    print(tail2id(str_id))
    print(front2id(str_id))
    print(get_id_type('019536.SH'))
