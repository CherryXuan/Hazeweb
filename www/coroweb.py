#!/usr/bin/env python3
# -*- coding: utf8 -*-

import asyncio, os, inspect,logging

from aiohttp import web

import functools

# apis.py是自己定义的(主要是API调用出错时应用)
from apierr import APIError

from urllib import parse

# 装饰器，给http请求添加方法和请求路径两个属性(应用于handler中)
# 三层嵌套装饰器，可以在decorator本身传参
# decorator将函数映射为http请求处理函数
def get(path):
    # Define decorate @get('/path')
    def decorator(func): # 传入参数是函数（handler定义的函数）
        # python内置的functools.wraps装饰器作用是把装饰后的函数的__name__属性变为原始的属性
        # 因为当使用装饰器后，函数的__name__属性会变为wrapper
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET' # 原始函数添加请求方法‘GET’
        wrapper.__route__ = path  # 原始函数添加路径
        return wrapper
    return decorator

def post(path):
    # Define decorate @get('/path')
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator

# 作用是把handlers中url处理函数需接收的参数分析出来
# 从request(http请求的对象)中获取请求的参数
# 把request的参数放入对应的url处理函数中
class RequestHandler(object):
    def __init__(self, func):
        self._func = func
    # 定义__call__方法可是为函数，导入request参数（对request处理）
    async def __call__(self, request):
        # 获取函数的需传入参数存入required_args字典｛key(参数名),value(inspect.Parameter对象(包含参数信息))｝
        required_args = inspect.signature(self._func).parameters
        logging.info('requerid args:%s' % required_args)

        # 获取url请求参数存入request_data字典
        if request.method == 'GET':
            qs = request.query_string
            request_data = {key:value[0] for key,value in parse.parse_qs(qs, True).items()}
            logging.info('request form:%s' % request_data)
        elif request.method == 'POST':
            if not request.content_type:
                return web.HTTPBadRequest(text='Missing Content-Type.')
            content_type = request.content_type.lower()
            if content_type.startswith('application/json'):
                request_data = await request.json()
                if not isinstance(request_data, dict):
                    return web.HTTPBadRequest(text='JSON body must be object.')
                logging.info('request json: %s' % request_data)
            elif content_type.startswith(('application/x-www-form-urlencoded', 'multipart/form-data')):
                params = await request.post()
                request_data = dict(**params)
                logging.info('request form: %s' % request_data)
            else:
                return web.HTTPBadRequest(text='Unsupported Content-Type: %s' % content_type)
        else:
            request_data = {}

        # kw字典即是把函数需要的参数从request中提取出来
        kw = { arg : value for arg, value in request_data.items() if arg in required_args}

        # 添加request参数
        if 'request' in required_args:
            kw['request'] = request
        # 检测参数表中有没有缺失
        for key, arg in required_args.items():
            # request参数不能为可变长参数
            if key == 'request' and arg.kind in (arg.VAR_POSITIONAL, arg.VAR_KEYWORD):
                return web.HTTPBadRequest(text='request parameter cannot be the var argument.')
            # 如果参数类型不是变长列表和变长字典，变长参数是可缺省的
            if arg.kind not in (arg.VAR_POSITIONAL, arg.VAR_KEYWORD):
                # 如果还是没有默认值，而且还没有传值的话就报错
                if arg.default == arg.empty and arg.name not in kw:
                    return web.HTTPBadRequest(text='Missing argument: %s' % arg.name)

        logging.info('call with args: %s' % kw)
        # 将request参数填入函数
        try:
            return await self._func(**kw)
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)

# 向app中添加静态文件目录
def add_static(app):
    # os.path.abspath(__file__), 返回当前脚本的绝对路径(包括文件名)
    # os.path.dirname(), 去掉文件名,返回目录路径
    # os.path.join(), 将分离的各部分组合成一个路径名
    # 因此以下操作就是将本文件同目录下的static目录(即www/static/)加入到应用的路由管理器中
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    # app = web.Application(loop=loop)这是在app.py模块中定义的
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))

# 将请求函数(fn)注册到app
# fn为handler被@get或@post装饰过的函数
def add_route(app, fn):
    # 获取函数的路径方法相关属性
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    # 如果函数属性为空，则报错
    if method is None or path is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    # 如果函数不是协程或生成器，把函数协程
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s ==> %s(%s)' % (method, path,fn.__name__,', '.join(inspect.signature(fn).parameters.keys())))
    # 注册request handler
    app.router.add_route(method, path, RequestHandler(fn))

# 将handlers模块所有请求处理函数交给add_route()处理
def add_routes(app, module_name):
    mod = __import__(module_name, globals(), locals())
    # 遍历mod的方法和属性
    # 因为@get或@post处理函数(方法)肯定有'__method__'和'__route__'属性
    for attr in dir(mod):
        # 如果是以'_'开头，pass
        if attr.startswith('_'):
            continue
        # 获取到非'_'开头属性
        fn = getattr(mod, attr)
        # 查看提取属性是不是函数
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            # 如果是函数，再判断是否有__method__和__route__属性，如果存在则使用app_route函数注册
            if method and path:
                add_route(app, fn)
