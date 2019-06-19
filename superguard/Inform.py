# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 16:06:42 2019

@author: yinchao
"""
import os
import json
import platform
from twilio.rest import Client

class Inform:
    def __init__(self):
        BASE_DIR = os.path.split(os.path.realpath(__file__))[0] #cur excute dir
        
        if "Linux" == platform.system():
            cfg_file = BASE_DIR + r'/Config/twilio_para.json'
        else:
            cfg_file = BASE_DIR + r'\Config\twilio_para.json'
        with open(cfg_file, 'r') as fh: #读取配置参数
            cfg = json.load(fh)
        self.phone_id = cfg['phone_id']
        account_sid = cfg['account_sid']
        auth_token = cfg['auth_token']
        self.client = Client(account_sid, auth_token)
    
    def SendMsg(self, phone_number, msg):
        msg = self.client.messages.create(
        to='+86'+phone_number,
        from_=self.phone_id, #your twilio code
        body=msg)
        return msg.sid

if __name__ == '__main__':
    msg = 'hello,world'
    phone = '15712091836'
    app = Inform()
    app.SendMsg(phone, msg)
