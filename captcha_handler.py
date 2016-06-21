# _*_coding:utf8 _*_
# !/usr/bin/python
import cookielib
import hashlib
import urllib
import urllib2
import uuid
import requests
import time
import random
import sys


class Ucode(object):
    # "110614", "469c0d8a805a40f39d3c1ec3c9281e9c", "zsqboy", "gih7c00", "1004"
    # 软件ID，软件key, 用户id，用户password，图片类型代码codetype
    # codetype及价格表详见.http://www.uuwise.com/price.html
    # 把pic改成你需要识别的验证码的地址，最好是jpg格式，
    # 如果不是要设置uu_captcha的codetype

    def __init__(self, user, pwd, softId="110614",
                 softKey="469c0d8a805a40f39d3c1ec3c9281e9c",
                 codeType="1004"):
        self.softId = softId
        self.softKey = softKey
        self.user = user
        self.pwd = pwd
        self.codeType = codeType
        self.uid = "100"
        self.initUrl = "http://common.taskok.com:9000/Service/ServerConfig.aspx"
        self.version = '1.1.1.2'
        self.cookieJar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cookieJar))
        self.loginUrl = None
        self.uploadUrl = None
        self.codeUrl = None
        self.params = []
        self.uKey = None

    def initialise(self):
        flag = False
        try:
            params = self.initHeader()
            if params:
                self.params = params
                self.opener.addheaders = params
                response = self.opener.open(self.initUrl, None, 30)
                if response.code == 200:
                    body = response.read()
                    if body is not None and len(body) > 0:
                        body = body.strip()
                        if body.find(",") != -1:
                            bs = body.split(",")
                            if bs is not None:
                                if len(bs) >= 4:
                                    self.loginUrl = bs[1][:-4]
                                    self.uploadUrl = bs[2][:-4]
                                    self.codeUrl = bs[3][:-4]
                                    flag = True
        except Exception, e:
            print "Error:can't initialise api"
            print e
        return flag

    def login(self):
        flag = True
        if self.loginUrl is not None:
            try:
                mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
                self.params.append(
                    ('KEY', self.md5(self.softKey.upper() + self.user.upper()) + mac))
                self.opener.addheaders = self.params
                url = "http://" + self.loginUrl
                url += "/Upload/Login.aspx?U=%s&p=%s" % (
                    self.user, self.md5(self.pwd))
                try:
                    response = self.opener.open(url, None, 60)
                    if response.code == 200:
                        body = response.read()
                        if body is not None:
                            if body.find("-") > 0:
                                us = body.split("_")
                                self.uid = us[0]
                                self.uKey = body.strip()
                                print '登录成功，用户ID是：', self.uid
                                flag = True
                            else:
                                print '登录失败,错误代码是：', body
                                flag = False
                except Exception, e:
                    print "Error:Login Request"
                    print e
            except Exception, e:
                print "Error:Login Params "
                print e
        return flag

    def upload(self, fileAddress=None, filemem=None):
        code = None
        if self.uKey is not None:
            try:
                image = open(fileAddress, 'rb')
                self.SKey = self.md5((self.uKey + self.softId + self.softKey).lower())
                data = {'KEY': self.uKey,
                        "SID": self.softId,
                        'SKey': self.md5((self.uKey + self.softId + self.softKey).lower()),
                        'Type': self.codeType}  # codetype及价格表详见.http://www.uuwise.com/price.html
                url = "http://" + self.uploadUrl + "/Upload/Processing.aspx"
                req = requests.post(
                    url, data=data, files={'IMG': image}, timeout=60)
                if req.status_code == 200:
                    body = req.text
                    if body is not None:
                        print '图片已上传，返回验证码ID：', body
                        self.capID = body
                        code = self.result(str(body))
                        print '正在获取识别结果...'
                        while (code == '-3'):
                            sys.stdout.write('.')
                            time.sleep(1)
                            code = self.result(str(body))
            except Exception, e:
                print e
        return code

    def result(self, body):
        code = None
        params = {'KEY': self.uKey, 'ID': body, 'random': (
            str(random.randint(1, 1000000)) + str(int(time.time())))}
        url = "http://" + self.codeUrl + \
            "/Upload/GetResult.aspx?" + urllib.urlencode(params)
        response = self.opener.open(url, None, 30)
        if response.code == 200:
            code = response.read()
        return code

    def initHeader(self):
        ps = None
        try:
            ps = [('SID', self.softId),
                  ('HASH', self.md5(self.softId + self.softKey.upper())),
                  ('UUVersion', self.version),
                  ('UID', self.uid),
                  ('User-Agent', self.md5(self.softKey.upper() + self.uid))]
        except Exception, e:
            print "Error: can't make http header"
            print e
        return ps

    def md5(self, key):
        return hashlib.md5(key.encode(encoding='utf-8')).hexdigest()

    def uu_captcha(self, pic):
        if self.initialise():
            if self.login():
                code = self.upload(pic)
                return code
        raise ValueError

    def fail_requests(self):
        failUrl = 'http://result.abc.com/Upload/ReportError.aspx?KEY=%s&ID=%s&SID=%s&SKEY=%s' % (self.uKey, self.capID, self.softId, self.SKey)
        print failUrl
        response = self.opener.open(failUrl)
        result = response.read()
        return result
