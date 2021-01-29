import time
import yaml
import requests
from datetime import datetime
from croniter import croniter

# 知识共享 署名-相同方式共享 3.0协议 作者:IceTiki

def getYmlConfig(yaml_file):
    # 读取yaml文件，参数是str类型的文件名(带.yml结尾)
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)

def waitingforintmin():
    # 自动取整的1分钟计时器，会自动同步系统时间的00秒。
    print('触发~')
    waiting=60-(int(time.strftime("%S", time.localtime()))+30)%60
    for i in range(waiting):
        time.sleep(1)
        print(waiting-i)

def remind(table):
    # 按照列表，推送当前事件
    # 列表中必须有timetable，qq，key
    SendListByQmsg(matchlist(table['timetable']),table['qq'],table['key'])
    return 0

def pushweather(userinfo):
    # 依照用户位置,qq,key,设定推送今日天气时间。推送天气。
    # 列表中必须有citycode，wethertime，qq，key
    if istime(userinfo['weathertime']):
        SendByQmsg(getwether(userinfo['citycode']),userinfo['qq'],userinfo['key'])
    return 0

def istime(string):
    # 判断输入的cron表达式是否匹配现在时间，如果是返回1，反之0
    if croniter.match(string, datetime.now()):
        return 1
    else:
        return 0

def matchlist(timetable):
    # 返回匹配当前时间的所有事件
    thinglist=[]
    for item in timetable: 
        if istime(item['time']):
            thinglist.append(item['title'])
    return thinglist

def SendListByQmsg(thinglist,qq,key):
    # qmsg酱提醒(List类型)
    if len(thinglist)==0:
        return 0
    else:
        msg=List2Msg(thinglist)
    SendByQmsg(msg,qq,key)
    return 0

def SendByQmsg(msg,qq,key):
    # qmsg酱提醒
    msg=str(msg)
    res = requests.post(url='https://qmsg.zendee.cn/send/'+key,data={'msg': msg,'qq':qq})
    return 0

def List2Msg(thinglist):
    # 提醒事项(列表)转换为待发送信息
    msg=''
    for thing in thinglist:
        msg=msg+thing+'\n'
    msg=msg[0:-1]
    return msg

def getwether(citycode):
    # 使用SoJson提供的API，返还今明后三天的天气。(https://www.sojson.com/blog/305.html)
    # citycode请参考https://github.com/baichengzhou/weather.api/blob/master/src/main/resources/citycode-2019-08-23.json
    res=requests.get(url='http://t.weather.itboy.net/api/weather/city/'+str(citycode))
    if res.json()['status']!=200:
        WeatherError=('天气获取失败：\nHTTP状态码('+str(res.json()['status'])+')，返回信息：'+res.json()['message'])
        print(WeatherError)
        return WeatherError
    w=res.json()['data']
    cityinfo=(res.json()['cityInfo']['city']+'(更新时间')+res.json()['cityInfo']['updateTime']+')：\n'
    w0=w['forecast'][0]
    w1=w['forecast'][1]
    w2=w['forecast'][2]
    strw0=('今日('+w0['ymd']+')天气'+w0['type']+'\n'
        +'温度是：'+w0['high']+'——'+w0['low']+'\n'
        +'湿度'+w['shidu']+'，吹'+w0['fx']+'('+w0['fl']+')\n'
        +'空气质量：'+w['quality']+'(pm2.5：'+str(w['pm25'])+'，pm10：'+str(w['pm10'])+')\n'
        +'太阳将在'+w0['sunrise']+'升起，'+w0['sunset']+'落下\n'
        +'感冒指数：'+w['ganmao'])+'\n\n'
    strw1=('明日天气'+w1['type']+'\n'
        +'温度是：'+w1['high']+'——'+w1['low']+'\n'
        +'吹'+w1['fx']+'('+w1['fl']+')\n'
        +'太阳将在'+w1['sunrise']+'升起，'+w1['sunset']+'落下\n\n')
    strw2=('后日天气'+w2['type']+'\n'
        +'温度是：'+w2['high']+'——'+w2['low']+'\n'
        +'吹'+w2['fx']+'('+w2['fl']+')\n'
        +'太阳将在'+w2['sunrise']+'升起，'+w2['sunset']+'落下')
    return cityinfo+strw0+strw1+strw2

# -------------------------开始-------------------------

def main_handler(event, context):
    # 提供给腾讯云函数的main_handler
    timetable = getYmlConfig('timetable.yml')
    for user in timetable['trigger']:
        remind(user)
    for user in timetable['trigger']:
        pushweather(user)


# 本地测试用

# main_handler({},{})

# while 1:
#     main_handler({},{})
#     waitingforintmin()
