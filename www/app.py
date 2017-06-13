#!/usr/bin/env python3
# -*- coding: utf8 *-

import logging
logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time

from aiohttp import web

import orm

from models import Messages

# API 数据输入
# message 格式：%7B'addr':'xaut','data':'1234','pm25':'100','pm10':'100'%7D
async def message(request):
    haze = request.match_info['message']
    hazedict = eval(haze)
    addr = hazedict['addr']
    data = hazedict['data']
    pm25 = hazedict['pm25']
    pm10 = hazedict['pm10']
    messages = Messages(addr = addr, data = data, pm25 = pm25, pm10 = pm10)
    await messages.save()
    response = '<h1>OK!!!</h1>'
    return web.Response(body=response.encode('utf-8'), content_type='text/html')

async def init(loop):
    #创建数据库连接池
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='haze', password='hazepasswd', db='hazeserver')
    app = web.Application(loop=loop)
    app.router.add_route('GET','/api/set-{message}',message)
    #监听127.0.0.1这个IP的9000端口的访问请求
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()