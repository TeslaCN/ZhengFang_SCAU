# -*- coding:utf-8 -*-

__metaclass__ = type

import selenium

from selenium import webdriver
import urllib, urllib2
import urlparse
import cookielib
import lxml.html
import re
from pprint import pprint
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class LoginScau:

    def __init__(self, username, password):
        self.username = username
        self.password = password

        # build openner with cookie
        cookie = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(cookie)
        self.opener = urllib2.build_opener(handler)


        self.domain = 'http://202.116.160.170/'
        self.url_homepage = 'http://202.116.160.170/default2.aspx'

        # using re to match secret code picture's url
        self.match_secret_code_url = re.compile('\"(CheckCode\.aspx.*?)\"')
        self.match_alert = re.compile(u'([\u4e00-\u9fa5]*?)')


        html_homepage = self.getresponse(self.url_homepage).read()
        # get login post form
        data = self.getpostform(html_homepage)
        #pprint(data)
        data['txtUserName'] = self.username
        data['TextBox2'] = self.password
        data['RadioButtonList1'] = u'\u5b66\u751f'
        #print data['RadioButtonList1']

        data['txtSecretCode'] = self.getsecretcode(html_homepage)
        pprint(data)
        encode_data = urllib.urlencode(data)
        login_headers = {
            'Host' : '202.116.160.170',
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding' : 'gzip, deflate',
            # 'Referer' : 'http://202.116.160.170/',
            # 'Cookie' : 'ASP.NET_SessionId=dqovqqjxbxmi4umopz1bf2j2',
            'Connection' : 'keep-alive',
            # 'Upgrade-Insecure-Requests' : '1',
            # 'Content-Length' : '196',
            # 'Content-Type' : 'application/x-www-form-urlencoded'

        }
        login_response = self.getresponse(url=self.url_homepage, data = encode_data, headers = login_headers)
        print '=' * 100
        print login_response.read().decode('gb2312')

        # input error have not handle yet
        result = self.match_alert.search(login_response.read().decode('gb2312').encode('utf8'))


    def getsecretcode(self, html):

        pictureurl = self.match_secret_code_url.search(html).groups()[0]
        fullurl = self.domain + pictureurl
        print fullurl
        picture = self.opener.open(fullurl).read()
        with open('image.jpg', 'wb') as file:
            file.write(picture)
        return raw_input("Enter the secret code:")


    def getresponse(self, url, headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0'}, data = None):

        request = urllib2.Request(url, data=data, headers=headers)

        response = self.opener.open(request)

        return response


    def getpostform(self, html):
        tree = lxml.html.fromstring(html)
        data = {}
        for info in tree.cssselect('form input'):
            if info.get('name'):
                data[info.get('name')] = info.get('value') or ''
        return data



def main():

    username = '201525050420'
    passwd = raw_input("Enter passwd of " + username + '\n')
    try:
        test = LoginScau(username, password=passwd)
    except urllib2.HTTPError as e:
        print e.code
        print e.reason
    pass


if __name__ == '__main__':

    main()

"""

 '__VIEWSTATE': 'dDwyODE2NTM0OTg7Oz6XQwtkC4IPj2mY5bsI42qRkaJNzw==',


POST /default2.aspx HTTP/1.1

Host: 202.116.160.170

User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

Referer: http://202.116.160.170/

Cookie: ASP.NET_SessionId=dqovqqjxbxmi4umopz1bf2j2

Connection: keep-alive

Upgrade-Insecure-Requests: 1


Content-Length	196
Content-Type	application/x-www-form-urlencoded



http://202.116.160.170/xf_xstyxk.aspx?xh=201525050420&xm=%CE%E2%CE%B0%BD%DC&gnmkdm=N121102


 """