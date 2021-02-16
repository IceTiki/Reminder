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
    # 处理数据结构
    w=res.json()['data']
    w0=w['forecast'][0]
    w1=w['forecast'][1]
    w2=w['forecast'][2]
    # 输出字符串---
    # 更新时间，城市名
    wstr=(res.json()['cityInfo']['city']+'(更新时间')+res.json()['cityInfo']['updateTime']+')：\n'
    # 湿度
    wstr+='湿度：'
    # 湿度百分比条
    humidity=int(w['shidu'][0:-1])
    wstr+='■'*int(humidity/10)+'□'*(10-int(humidity/10))+w['shidu']+'\n'
    # 三日天气
    wstr+='三日天气：\n'+w0['type']+'\n'+w1['type']+'\n'+w2['type']+'\n'
    # 温度可视化
    wstr+='三日温度：\n\n'
    wl0,wl1,wl2,wh0,wh1,wh2=map(lambda x:int(x[3:-1]),[w0['low'],w1['low'],w2['low'],w0['high'],w1['high'],w2['high']])
    temrange=list(range(min(wl0,wl1,wl2),max(wh0,wh1,wh2)+1))[::-1]
    wstr+=w0['high'][3:]+w1['high'][3:]+w2['high'][3:]+'\n'
    for i in temrange:
        if i in range(wl0,wh0+1):
            wstr+='  ■'
        else:
            wstr+='  □'
        if i in range(wl1,wh1+1):
            wstr+='    ■'
        else:
            wstr+='    □' 
        if i in range(wl2,wh2+1):
            wstr+='    ■'
        else:
            wstr+='    □'
        wstr+='\n'
    wstr+=w0['low'][3:]+w1['low'][3:]+w2['low'][3:]+'\n\n'
    # 其他
    # wstr+='其他：\n'
    # wstr+='吹'+w0['fx']+'('+w0['fl']+')\n'
    # wstr+='空气质量：\n'+w['quality']+'(pm2.5：'+str(w['pm25'])+'，pm10：'+str(w['pm10'])+')\n'
    wstr+='太阳将在\n'+w0['sunrise']+'升起，'+w0['sunset']+'落下'# 删掉了个\n
    # wstr+='感冒指数：'+w['ganmao']
    return wstr

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
