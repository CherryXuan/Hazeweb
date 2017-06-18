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

import xml.etree.ElementTree as ET

import re

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
    if recMsg.MsgType == 'text':
        content = "test"
        replyMsg = reply.TextMsg(toUser, fromUser, content)
        result = replyMsg.send()
    elif recMsg.MsgType == 'image':
        mediaId = recMsg.MediaId
        replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
        result = replyMsg.send()
    else:
        result = 'success'

    return web.Response(body=result)

