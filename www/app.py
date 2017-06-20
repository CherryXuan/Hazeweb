#!/usr/bin/env python3
# -*- coding: utf8 *-

import logging
logging.basicConfig(level=logging.INFO)

import asyncio

from aiohttp import web
from aiohttp import ClientSession

from coroweb import add_routes

import orm

async def init(loop):
    #创建数据库连接池
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='haze', password='hazepasswd', db='hazeserver')
    app = web.Application(loop=loop)
    add_routes(app, 'handlers')
    # 监听0.0.0.0 IP的80端口的访问请求
    srv = await loop.create_server(app.make_handler(), '0.0.0.0', 80)
    logging.info('server started at http://139.199.82.84...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()