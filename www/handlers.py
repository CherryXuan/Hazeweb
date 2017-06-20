#!/usr/bin/env python3
# -*- coding: utf8 -*-

' url handlers '
import hashlib

from aiohttp import web
from coroweb import get, post
# 导入数据表单
from models import Messages

import receive
import reply

@get('/')
async def index():
    response = '<h1>WEIXIN</h1>'
    return web.Response(body=response.encode('utf-8'), content_type='text/html')

# 数据输入
@get('/messages')
async def messages(addr, data, pm25, pm10):
    messages = Messages(addr = addr, data = data, pm25 = pm25, pm10 = pm10)
    await messages.save()
    response = '<h1>OK!!!</h1>'
    return web.Response(body=response.encode('utf-8'), content_type='text/html')

# 微信基本配置验证
# 微信接口测试发送请求为：
# "GET /weixin?signature=...&echostr=...&timestamp=...&nonce=... HTTP/1.0" 200 173 "-" "Mozilla/4.0"
@get('/weixin')
async def getwx(signature,echostr,timestamp,nonce):
    # wxdict = request_query_url(request.query_string)
    # signature = wxdict['signature']
    # echostr = wxdict['echostr']
    # timestamp = wxdict['timestamp']
    # nonce = wxdict['nonce']
    token='weixin' # 此处填写平台的token
    # 字典序排序（以下为微信验证哈希处理）
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = "%s%s%s" % tuple(tmp_list)
    tmp_str = hashlib.sha1(tmp_str.encode('utf8')).hexdigest()
    if tmp_str == signature:
        return web.Response(body=echostr)

# 微信
@post('/weixin')
async def postwx(request):
    data = await request.text() # 读取请求body
    recMsg = receive.parse_xml(data)
    toUser = recMsg.FromUserName
    fromUser = recMsg.ToUserName
    print(recMsg.Content.decode('ascii'))
    if recMsg.MsgType == 'text':
        flag = True
        if recMsg.Content.decode('ascii') == '1':
            addr = 'addr="xaut"'
            addrp = '西安理工大学金花校区'
        elif recMsg.Content.decode('ascii') == '2':
            addr = 'addr="xautnew"'
            addrp = '西安理工大学曲江校区'
        else:
            flag = False
            content = '''雾霾实时检测：
请输入对应地址标号
1 西安理工大学金花校区
2 西安理工大学曲江校区
...'''
        if flag :
            hz = await Messages.findAll(where=addr, orderBy='id desc', limit=(0, 1))
            hzdict = dict(hz)
            if int(hzdict['pm25']) <= 50:
                quality = '优'
            elif int(hzdict['pm25']) <= 100:
                quality = '良'
            elif int(hzdict['pm25']) <= 150:
                quality = '轻度污染'
            elif int(hzdict['pm25']) <= 200:
                quality = '中度污染'
            elif int(hzdict['pm25']) <= 300:
                quality = '重度污染'
            content = '''空气质量 %s
PM2.5指数 %s
PM10 指数 %s
监测地点  %s
实时时间  %s''' % (quality, hzdict['pm25'], hzdict['pm10'], addrp, hzdict['data'])

        replyMsg = reply.TextMsg(toUser, fromUser, content)
        result = replyMsg.send()
    elif recMsg.MsgType == 'image':
        mediaId = recMsg.MediaId
        replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
        result = replyMsg.send()
    else:
        result = 'success'

    return web.Response(body=result)

