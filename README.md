# Reminder

这是一个提醒小工具！通过**qq**提醒起床，吃饭，喝水，生日，去哪里上课(课表)等等！

在timetable中用[cron表达式](https://www.runoob.com/linux/linux-comm-crontab.html)定义提醒时间，qmsg酱就会提醒你了！

## 使用方式(腾讯云函数)

1. 参考[教程](https://github.com/ZimoLoveShuang/auto-submit#%E4%BA%91%E7%AB%AF%E7%B3%BB%E7%BB%9F%E5%8F%AF%E7%94%A8%E9%85%8D%E5%90%88%E8%85%BE%E8%AE%AF%E4%BA%91%E5%87%BD%E6%95%B0)的3-6步

> 小区别：
>
> 1. config.yml→timetable.yml
>
> 2. dependency.zip→req.zip
>
> 3. 触发器的Cron表达式建议换成*/15 * 7-23 * \*意思就是7-23点，每15分钟触发一次。注意timetable.yml里面设置的时间要刚好对得上触发器触发。(比如触发器是*/15 * 7-23 * \*，那事件最好是15 7 * * *而不要是20 7 * * *)

2. 如果没注册过[qmsg酱](https://qmsg.zendee.cn/)的去注册下，然后把自己的key和qq填进timetable.yml里面
3. 腾讯云函数默认UTC-0时区，在函数配置-环境变量中加上TZ=Asia/Shanghai就可以改为UTC-8
