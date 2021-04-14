from datetime import datetime as dt
from croniter import croniter
import time
import calendar
import requests
import yaml

# ===============全局变量===============


def getYmlConfig(yaml_file):
    # 读取yaml文件，参数是str类型的文件名(带.yml结尾)
    # 返回：字典
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


def init_globalval():  # 配置全局变量
    global global_config
    global global_time
    global global_loggingtimes
    global_config = getYmlConfig('config.yml')
    global_time = Global_Time()
    global_loggingtimes = 0


class Global_Time():
    def __init__(self):
        self.dt = dt.now()
        # self.dt = dt.strptime('2021/02/24_16:00:00','%Y/%m/%d_%H:%M:%S')
        self.lt = time.localtime()


init_globalval()

# ===============通用函数===============

global_loggingtimes = 0


def log(*args):
    global global_loggingtimes
    global_loggingtimes += 1
    if args:
        string = '|||log|||'+nt('%Y/%m/%d_%H:%M:%S') + \
            '|'+str(global_loggingtimes)+'\n'
        for item in args:
            string += str(item)
        print(string)


def waitingforintmin():  # 1分钟延迟，会自动同步系统时间的00秒。
    print('触发~')
    waiting = 60-(int(time.strftime("%S", global_time.lt))+30) % 60
    for i in range(waiting):
        time.sleep(1)
        print(waiting-i)


def ifcron(strcron):  # 检查cron表达式是否匹配当前时间
    if strcron == 0:
        return 0
    else:
        return croniter.match(strcron, global_time.dt)


def nt(tstr):  # 格式化输出当前时间(使用time模块)
    return time.strftime(tstr, global_time.lt)


def timebar(sttime='2000/01/01', edtime='none', barlong=0, s=',,'):  # 时间条/倒计时(基本单位：天)
    # sttime，edtime：初始时间和结束时间(YYYY/MM/DD)，根据当前时间返回字符串。
    # 不输入结束时间的时候，输出倒计时
    # barlong：时间轴长度，如果为0或者负数，则自动取值
    # strin：直接读取字符串，格式为'sttime,edtime,barlong'
    # 例子timebar(s='2021/01/24,2021/03/06,0,)
    varlist = s.split(',')
    default = [sttime, edtime, barlong]
    for i in range(3):
        if varlist[i] == '':
            varlist[i] = default[i]
    sttime, edtime, barlong = varlist
    barlong = int(barlong)

    edtime = edtime if edtime != 'none' else sttime

    sttime = dt.strptime(sttime, '%Y/%m/%d')
    edtime = dt.strptime(edtime, '%Y/%m/%d')
    now = global_time.dt

    timerange = (edtime-sttime).days
    tostart = (now-sttime).days
    toend = (edtime-now).days+1

    barlong = barlong if barlong > 0 else timerange

    if timerange <= 0:
        if tostart < 0:
            return '还有'+str(-tostart)+'天'
        elif tostart == 0:
            return '今天'
        else:
            return '已经过去了'+str(tostart)+'天'
    else:
        if tostart < 0:
            return '还有'+str(-tostart)+'天开始'
        elif toend < 0:
            return '已经结束了'+str(-toend)+'天'
        else:
            return str(tostart)+'|'*int(tostart*(barlong/timerange))+'*'+':'*int(toend*(barlong/timerange))+str(toend)


# ===============学期===============

class Term:
    def __init__(self, config):
        # 参数说明
        # config是一个字典,参数要求：
        # self.now：需要{'firstday': '2000/01/01'}，学期开始第一天
        self.config = config
        self.now()

    def now(self):
        # 根据设置的学期第一天
        firstday = dt.strptime(self.config['firstday'], '%Y/%m/%d')
        nowweek = int((global_time.dt-firstday).days/7)+1
        self.now_week = nowweek
        self.now_issingularweek = nowweek % 2
        return self


# ===============cron匹配===============

class CronEvent:
    def __init__(self, ces=1, ces_keys=1, ces_table=1):
        # ces全称cronevents
        # 初始化后
        # self.mlist是所有匹配当前时间的事件列表
        # self.strml上述列表格式化后的字符串
        if ces == 1:
            ces = []
        # ces是一个列表，其中每一项都包含一个title和一个cron表达式
        # e.g. [{"title":"xxx","time":"* * * * *"},{"title":"yyy","time":"* * * * *"}]
        if ces_keys == 1:
            ces_keys = []
        # ces_keys是一个列表
        # 以其作为键值,在ces_table中抽取数据。
        # 比如['A','B']
        if ces_table == 1:
            ces_table = {}
        # ces_table是一个字典
        # 有多个键。每一个键都包含一个列表
        # 列表中每一项都包含一个title和一个cron表达式
        # e.g. {"A":[{"title":"xxx","time":"* * * * *"},{"title":"yyy","time":"* * * * *"}],"B":[{"title":"zzz","time":"* * * * *"}]}
        for key in ces_keys:
            ces += ces_table[key]
        self.mlist = self.matchlist(ces)
        self.strml = self.list2str(self.mlist)

    def __str__(self):
        return self.strml

    def matchlist(self, ces):
        # 返回匹配当前时间的所有事件
        thinglist = []
        for item in ces:
            if ifcron(item['time']):
                thinglist.append(item['title'])
        return thinglist

    def list2str(self, mlist):
        # 将列表格式化为str
        astr = ''
        for i in mlist:
            astr = astr+i+'\n'
        astr = astr[0:-1]
        return astr


# ===============天气===============

class Weather:
    def __init__(self, citycode=101010100):
        # 参数说明：
        # citycode：城市代码
        # 载入参数
        self.citycode = citycode
        self.updatewether()

    def updatewether(self):
        # 更新实例内的天气数据
        # 使用SoJson提供的API。(https://www.sojson.com/blog/305.html)
        # citycode请参考https://github.com/baichengzhou/weather.api/blob/master/src/main/resources/citycode-2019-08-23.json
        res = requests.get(
            url='http://t.weather.itboy.net/api/weather/city/'+str(self.citycode))
        self.wetherdate = res
        return self

    def f1(self):
        # 将updatewether获得的数据排版
        wetherdate = self.wetherdate
        if wetherdate.json()['status'] != 200:
            WeatherError = ('天气获取失败：\nHTTP状态码('+str(wetherdate.json()
                                                    ['status'])+')，返回信息：'+wetherdate.json()['message'])
            log(WeatherError)
            return WeatherError
        # 处理数据结构
        w = wetherdate.json()['data']
        w0 = w['forecast'][0]
        w1 = w['forecast'][1]
        w2 = w['forecast'][2]
        # 输出字符串---
        # 更新时间，城市名
        wstr = (wetherdate.json()['cityInfo']['city']+'(更新时间') + \
            wetherdate.json()['cityInfo']['updateTime']+')：\n'
        # 湿度
        wstr += '湿度：'
        # 湿度百分比条
        humidity = int(w['shidu'][0:-1])
        wstr += '■'*int(humidity/10)+'□'*(10-int(humidity/10))+w['shidu']+'\n'
        # 三日天气
        wstr += '三日天气：\n'+w0['type']+'\n'+w1['type']+'\n'+w2['type']+'\n'
        # 温度可视化
        wstr += '三日温度：\n\n'
        wl0, wl1, wl2, wh0, wh1, wh2 = map(lambda x: int(
            x[3:-1]), [w0['low'], w1['low'], w2['low'], w0['high'], w1['high'], w2['high']])
        temrange = list(range(min(wl0, wl1, wl2), max(wh0, wh1, wh2)+1))[::-1]
        wstr += w0['high'][3:]+w1['high'][3:]+w2['high'][3:]+'\n'
        for i in temrange:
            if i in range(wl0, wh0+1):
                wstr += '  ■'
            else:
                wstr += '  □'
            if i in range(wl1, wh1+1):
                wstr += '    ■'
            else:
                wstr += '    □'
            if i in range(wl2, wh2+1):
                wstr += '    ■'
            else:
                wstr += '    □'
            wstr += '\n'
        wstr += w0['low'][3:]+w1['low'][3:]+w2['low'][3:]+'\n\n'
        # 其他
        # wstr+='其他：\n'
        # wstr+='吹'+w0['fx']+'('+w0['fl']+')\n'
        # wstr+='空气质量：\n'+w['quality']+'(pm2.5：'+str(w['pm25'])+'，pm10：'+str(w['pm10'])+')\n'
        wstr += '太阳将在\n'+w0['sunrise']+'升起，'+w0['sunset']+'落下'  # 删掉了个\n
        # wstr+='感冒指数：'+w['ganmao']
        self.f1str = wstr
        return wstr

# ===============每日英语===============

def shanbayDailyQuote():
    _today=time.strftime("%Y-%m-%d", time.localtime())
    sb_url = "https://apiv3.shanbay.com/weapps/dailyquote/quote/?date=" + _today
    result = {}
    record = requests.get(sb_url).json()
    result['date'] = _today
    result['content'] = record['content']
    result['translation'] = record['translation']
    strQuote="扇贝每日: \n%s\n%s"%(result['content'],result['translation'])
    return strQuote

def youdaoDailyQuote():
    _today=time.strftime("%Y-%m-%d", time.localtime())
    yd_url = "https://dict.youdao.com/infoline?mode=publish&date=" + _today + "&update=auto&apiversion=5.0"
    result = {}
    for record in requests.get(yd_url).json()[_today]:
        if record['type'] == '壹句':
            result['date'] = _today
            result['content'] = record['title']
            result['translation'] = record['summary']
            break
    strQuote="有道壹句: \n%s\n%s"%(result['content'],result['translation'])
    return strQuote

# ===============推送===============

class Qmsg:  # Qmsg推送
    def __init__(self, qmsg):
        # 参数说明：
        # qmsg={'key':'*****','qq':'*****','isgroup':0}
        self.qmsg = qmsg

    def send(self, msg):  # 消息推送函数
        # 参数说明：
        # msg：要发送的信息
        msg = str(msg)
        if msg == '':
            return
        sendtype = 'group/' if self.qmsg['isgroup'] else 'send/'
        res = requests.post(url='https://qmsg.zendee.cn/'+sendtype +
                            self.qmsg['key'], data={'msg': msg, 'qq': self.qmsg['qq']})
        log(res)


# ===============消息整合===============

class Fmsg():  # 字符串整合
    def __init__(self, msg=''):
        # 静态变量
        # self.msg：整合后的字符串
        self.msg = msg

    def __str__(self):
        return self.msg

    def add(self, addmsg):  # 整合新的字符串进来
        # 参数说明
        # addmsg：要整合进来的字符串，可以是定义了__str__的类
        addmsg = str(addmsg)
        if addmsg == '':
            return
        if not self.msg == '':
            self.msg += '\n' + '='*10 + '\n'
        self.msg += addmsg

    def clean(self):
        self.msg = ''


# ===============函数调试用参数===============
# try_config=getYmlConfig('timetable.yml')
try_2M = Qmsg({'key': '627696c2fb6a9223198dc941aa9d8fae',
               'qq': '1796494817', 'isgroup': 0})
try_2G = Qmsg({'key': '627696c2fb6a9223198dc941aa9d8fae',
               'qq': '489935275', 'isgroup': 1})
try_weather = Weather(citycode=101281904)
try_s = '2021/01/24,2021/03/06,0'

# ===============调试函数===============
# try_2M.send('寒假进度条\n'+timebar(s=try_s))
# if ifcron('0 7 * * *'):
#     Qmsg({'key': '627696c2fb6a9223198dc941aa9d8fae',
#             'qq': '489935275', 'isgroup': 1}).send('寒假进度条\n'+timebar(s='2021/01/24,2021/03/06,0'))
# try_2G.send(Weather(101280301).f1())
# ===============Main===============


def main_handler(event, context):
    init_globalval()
    for user in global_config['users']:
        msg = Fmsg()
        # Weather
        if ifcron(user['weather']['cron']):
            str_Weather_f1 = Weather(user['weather']['citycode']).f1()
            msg.add(str_Weather_f1)
        # ShanBay
        if ifcron(user['shanbayDailyQuote']):
            msg.add(shanbayDailyQuote())
        # YouDao
        if ifcron(user['youdaoDailyQuote']):
            msg.add(youdaoDailyQuote())
        # CronEvent
        str_CronEvent = CronEvent(
            ces_keys=user['cronevents_keys'], ces_table=global_config['cronevents_table'])
        msg.add(str_CronEvent)
        # 推送
        Qmsg(user['qmsg']).send(msg)


# 本地测试用

# main_handler({}, {})

# while 1:
#     main_handler({},{})
#     waitingforintmin()
