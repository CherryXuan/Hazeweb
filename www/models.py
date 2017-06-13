#!/usr/bin/env python3
# -*- coding: utf8 -*-

#web APP 所用到数据库表单定义

import time
# python中生成唯一ID库
import uuid

#调用orm,数据库的对象映射模块
from orm import Model, StringField, BooleanField, FloatField, TextField

#生成基于时间唯一的id,作为数据库表每一行主键
def next_id():
    # time.time() 返回当前时间戳
    # uuid.uuid4() 由伪随机数得到
    return  '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

# 用户信息存储表
class Messages(Model):
    # 表名定义
    __table__='messages'
    # id 为主键，唯一标识
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    # 地点
    addr = StringField(ddl='varchar(50)')
    # 时间
    data = StringField(ddl='varchar(50)')
    # pm2.5
    pm25 = StringField(ddl='varchar(20)')
    # pm10
    pm10 = StringField(ddl='varchar(20)')
