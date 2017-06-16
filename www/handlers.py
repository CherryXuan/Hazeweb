#!/usr/bin/env python3
# -*- coding: utf8 -*-

' url handlers '
import hashlib

from aiohttp import web
from coroweb import get, post
# 导入数据表单
from models import Messages

# 导入正则库
import re
'''
# url的请求参数解析函数
def request_query_url(query_url_string):
    # 正则分割把参数提取转换成列表
    rq = re.split(r'[&=]', query_url_string)
    # 把参数中的变量和值分别对应放入两个列表
    i = 0
    rq1 = []
    rq2 = []
    for element in rq:
        if i % 2 == 0:
            rq1.append(element)
        else:
            rq2.append(element)
        i = i + 1
    # 将两个列表转换为字典
    rq_dict = dict(zip(rq1, rq2))
    # 返回字典
    return rq_dict
'''
# API 数据输入
@get('/messages')
async def messages(addr, data, pm25, pm10):
    # messagesdict = request_query_url(request.query_string)
    # addr = messagesdict['addr']
    # data = messagesdict['data']
    # pm25 = messagesdict['pm25']
    # pm10 = messagesdict['pm10']
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

@get('/')
async def index():
    response = '<h1>OK!!!</h1>'
    return web.Response(body=response.encode('utf-8'), content_type='text/html')
