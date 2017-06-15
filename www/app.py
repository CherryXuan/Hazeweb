#!/usr/bin/env python3
# -*- coding: utf8 *-

import logging
logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time, hashlib

from aiohttp import web

import orm
# 导入数据表单
from models import Messages
# 导入正则库
import re

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

# API 数据输入
async def messages(request):
    messagesdict = request_query_url(request.query_string)
    addr = messagesdict['addr']
    data = messagesdict['data']
    pm25 = messagesdict['pm25']
    pm10 = messagesdict['pm10']
    messages = Messages(addr = addr, data = data, pm25 = pm25, pm10 = pm10)
    await messages.save()
    response = '<h1>OK!!!</h1>'
    return web.Response(body=response.encode('utf-8'), content_type='text/html')

# 微信基本配置验证
# 微信接口测试发送请求为：
# "GET /weixin?signature=...&echostr=...&timestamp=...&nonce=... HTTP/1.0" 200 173 "-" "Mozilla/4.0"
async def getwx(request):
    wxdict = request_query_url(request.query_string)
    signature = wxdict['signature']
    echostr = wxdict['echostr']
    timestamp = wxdict['timestamp']
    nonce = wxdict['nonce']
    token='weixin' # 此处填写平台的token
    # 字典序排序
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = "%s%s%s" % tuple(tmp_list)
    tmp_str = hashlib.sha1(tmp_str.encode('utf8')).hexdigest()
    if tmp_str == signature:
        return web.Response(body=echostr)

async def init(loop):
    #创建数据库连接池
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='haze', password='hazepasswd', db='hazeserver')
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/messages', messages)
    app.router.add_route('GET', '/weixin', getwx)
    # app.router.add_route('POST','/weixin',postwx)
    # 监听0.0.0.0 IP的80端口的访问请求
    srv = await loop.create_server(app.make_handler(), '0.0.0.0', 80)
    logging.info('server started at http://139.199.82.84...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()