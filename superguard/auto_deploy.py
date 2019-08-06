import os
import re
import subprocess

passwd = 'yc123'

#1. find active process's ID and close it
cmd = 'ps -ef | grep main.py'
def killpid(process_name, passwd):
    cmd = 'ps ax | grep %s | grep -v grep | awk \'{print $1}\'' % process_name
    out = subprocess.getoutput(cmd)
    if len(out)==0:
        print('no such process')
        return
    if isinstance(out, str):
        cmd = 'sudo kill -9 %s' % out
        print(cmd)
        os.system('echo %s|sudo -S %s' % (passwd, cmd))
    elif isinstance(out, list):
        for pid in out:
            cmd = 'sudo kill -9 %s' % pid
            print(cmd)
            os.system('echo %s|sudo -S %s' % (passwd, cmd))
killpid('main.py',passwd)
killpid('display.py',passwd)

#2. pull github and merge new change
cmd = 'git checkout .'
os.system(cmd)
cmd = 'git pull origin master'
os.system(cmd)

#3. running process with nohup
cmd = ('nohup python main.py &>nohup.out')
os.system(cmd)
cmd = ('nohup python display.py &>display.out')
os.system(cmd)

