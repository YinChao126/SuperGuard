import os

passwd = 'yc123'
cmd = 'ls -al'
cmd = 'pwd'

os.system(cmd)

#1. clear first, pull github and merge new change next
cmd = 'git cc .'
os.system(cmd)
cmd = 'git pull origin master'
os.system(cmd)

#2. restart mian.py and display.py


cmd = ('nohup python3 main.py &>nohup.out')
os.system(cmd)

cmd = ('nohup python3 display.py &>display.out')
os.system(cmd)

#3. copy /site to /tomcat/webapp
# cmd = ('sudo cp -fr site/ /opt/tomcat/apache-tomcat-9.0.21/webapps/')
# os.system('echo %s|sudo -S %s' % (passwd, cmd))
