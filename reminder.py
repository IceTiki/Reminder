import time
import yaml
import requests
from datetime import datetime
from croniter import croniter

# 知识共享 署名-相同方式共享 3.0协议 作者:IceTiki

# 读取配置
def getYmlConfig(yaml_file):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)

# 自动取整的1分钟计时器，会自动同步系统时间的00秒。
def waitingforintmin():
    print('触发~')
    waiting=60-(int(time.strftime("%S", time.localtime()))+30)%60
    for i in range(waiting):
        time.sleep(1)
        print(waiting-i)

# 封装好的提醒实例
class remind:
    # 构造函数
    def __init__(self,table):
        self.SendListByQmsg(self.matchlist(table['timetable']),table['qq'],table['key'])

    # 判断是否匹配现在时间，如果是返回1，反之0
    def istime(self,string):
        if croniter.match(string, datetime.now()):
            return 1
        else:
            return 0

    # 返回匹配当前时间的所有事件
    def matchlist(self,timetable):
        thinglist=[]
        for item in timetable: 
            if self.istime(item['time']):
                thinglist.append(item['title'])
        return thinglist

    # qmsg酱提醒
    def SendListByQmsg(self,thinglist,qq,key):
        if len(thinglist)==0:
            return 0
        else:
            msg=self.List2Msg(thinglist)
        posturl='https://qmsg.zendee.cn/send/'+key
        res = requests.post(url=posturl,data={'msg': msg,'qq':qq})
        return 0

    # 提醒事项(列表)转换为待发送信息
    def List2Msg(self,thinglist):
        msg=''
        for thing in thinglist:
            msg=msg+thing+'\n'
        msg=msg[0:-1]
        return msg


# -------------------------开始-------------------------
# 提供给腾讯云函数的main_handler
def main_handler(event, context):
    timetable = getYmlConfig('timetable.yml')
    for user in timetable['trigger']:
        remind(user)

# 本地测试用

# main_handler({},{})

# while 1:
#     main_handler({},{})
#     waitingforintmin()
