#!/usr/bin/env python3
# -*- coding: utf8 -*-

import urllib.request
import time
import json


class Basic:
    def __init__(self):
        self.__accessToken = ''
        self.__leftTime = 0

    async def __real_get_access_token(self):
        appId = "wxa0eb8dc937b215ab"
        appSecret = "470aea3146a835702a55ab9d07603766"
        postUrl = ("https://api.weixin.qq.com/cgi-bin/token?grant_type="
                   "client_credential&appid=%s&secret=%s" % (appId, appSecret))
        urlResp = urllib.request.urlopen(postUrl)
        urlResp = json.loads(urlResp.read())

        self.__accessToken = urlResp['access_token']
        self.__leftTime = urlResp['expires_in']

    def get_access_token(self):
        return self.__accessToken

    def run(self):
        while (True):
            if self.__leftTime > 10:
                time.sleep(2)
                self.__leftTime -= 2
            else:
                self.__real_get_access_token()