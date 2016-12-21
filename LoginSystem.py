# -*- coding:utf-8 -*-

__metaclass__ = type

import urllib, urllib2
import urlparse
import cookielib
import lxml.html
import re
from pprint import pprint
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class LoginSystem:

    def __init__(self, username, password):
        self.logined = False
        self.username = username
        self.password = password
        self.headers = {}
        # build openner with cookie
        cookie = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(cookie)
        self.opener = urllib2.build_opener(handler)



        self.domain = 'http://202.116.160.170/'
        self.url_homepage = 'http://202.116.160.170/default2.aspx'
        self.url_PublicCourse = 'http://202.116.160.170/xf_xsqxxxk.aspx?'

        # using re to match secret code picture's url
        # Unicode Chinese \u4e00-\u9fa5
        self.match_secret_code_url = re.compile('\"(CheckCode\.aspx.*?)\"')
        self.match_alert = re.compile(u'alert\((.*?)\)')


        html_loginpage = self.getresponse(self.url_homepage).read()
        # get login post form
        data = self.getpostform(html_loginpage)
        #pprint(data)
        data['txtUserName'] = self.username
        data['TextBox2'] = self.password
        data['RadioButtonList1'] = u'\u5b66\u751f'
        #print data['RadioButtonList1']

        data['txtSecretCode'] = self.getsecretcode(html_loginpage)
        pprint(data)
        encode_data = urllib.urlencode(data)
        self.headers = {
            'Host' : '202.116.160.170',
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language' : 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding' : 'gzip, deflate',
            # 'Referer' : 'http://202.116.160.170/',
            'Referer' : 'http://202.116.160.170/xs_main.aspx?xh={}'.format(self.username),

            #'Cookie' : 'ASP.NET_SessionId=dqovqqjxbxmi4umopz1bf2j2',
            'Connection' : 'keep-alive',
            'Upgrade-Insecure-Requests' : '1',
            # 'Content-Length' : '196',
            # 'Content-Type' : 'application/x-www-form-urlencoded'

        }
        pprint(self.headers)
        login_response = self.getresponse(url=self.url_homepage, encoded_data= encode_data, headers = self.headers)
        self.html_homepage = login_response.read()

        # login error have not handle yet
        result = self.match_alert.search(self.html_homepage)
        print self.html_homepage.decode('gb2312')
        ChineseName = re.findall('>(.*?)同学<'.encode('gb2312'), self.html_homepage)
        if result is not None:
            print "ERROR:", result.groups()[0].decode('gb2312')
            return
        elif not bool(ChineseName):
            print "Login Failed!"
            return
        else:
            print "Login succeeded"
            self.referer = 'http://202.116.160.170/xs_main.aspx?xh={}'.format(self.username)
            self.logined = True

        print '=' * 100


        self.ChineseName = ChineseName[0].decode('gb2312')
        print "Welcome!", self.ChineseName


    def getsecretcode(self, html):

        pictureurl = self.match_secret_code_url.search(html).groups()[0]
        fullurl = self.domain + pictureurl
        print fullurl
        picture = self.opener.open(fullurl).read()
        with open('image.jpg', 'wb') as file:
            file.write(picture)
        return raw_input("Enter the secret code:")


    def getresponse(self, url, headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0'}, encoded_data = None):

        request = urllib2.Request(url, data=encoded_data, headers=headers)
        self.updateheaders(url)
        response = self.opener.open(request)

        return response


    def getpostform(self, html):
        tree = lxml.html.fromstring(html)
        data = {}

        for info in tree.cssselect('form input'):
            if info.get('name'):
                data[info.get('name')] = info.get('value') or ''

        return data



    def getclasscode(self, html):

        match_classcode = re.compile('href=["\'](xsjxpj\.aspx\?.*?)["\']', re.IGNORECASE)
        result = match_classcode.findall(html)

        if result is not None:
            #pprint(result)

            return result
        else:
            print "RESULT IS NONE"

    def evaluateClass(self):
        self.urllist_teachingevaluation = self.getclasscode(self.html_homepage)
        for url in self.urllist_teachingevaluation:
            self.evaluate(url=url)
        # self.evaluate(self.urllist_teachingevaluation[0])

    def evaluate(self, url):
        full_url = self.domain + url
        print full_url
        print 'Referer:', self.referer
        response = self.getresponse(full_url, headers = self.headers)
        html = response.read()
        #print html.decode('gb2312')

        data = self.getpostform(html)

        tree = lxml.html.fromstring(html)
        selected = []
        for i in tree.cssselect('option[selected=selected]'):
            # print i.get('value')
            selected.append(i.get('value') or u'\u4f18')

        selected.reverse()

        pprint(selected)
        for info in tree.cssselect('form select'):
            if info.get('name'):
                try:
                    data[info.get('name')] = selected.pop()
                except IndexError as e:
                    data[info.get('name')] = "Waiting"
                    pass
                    # \u4f18 优
                    # \u826f 良

        data['Button1'] = u' \u4fdd  \u5b58 '.encode('gb2312')

        first = True
        for key in data:
            if data[key] == 'Waiting':
                if first:
                    data[key] = u'\u826f'.encode('gb2312')
                    first = False
                else:
                    data[key] = u'\u4f18'.encode('gb2312')

        del data['RadioButtonList1']
        del data['Button3']
        del data['Button4']

        pprint(data)
        pprint(self.headers)

        encoded_data = urllib.urlencode(data)
        # print encoded_data
        print 'length of post ==', len(encoded_data)
        html = self.getresponse(url=full_url, headers=self.headers, encoded_data=encoded_data).read()
        # print '-' * 255
        # print html.decode('gb2312')
        match_finished = re.compile('所有评价已完成，现在可以提交！'.encode('gb2312'))
        finished = match_finished.search(html)

        if finished is not None:
            print '*' * 255
            print finished.group().decode('gb2312')

            #data['__EVENTTARGET'] = 'pjkc'
            del data['Button1']
            data['Button2'] = u' \u63d0  \u4ea4 '.encode('gb2312') # ' 提  交 '
            finish_data = self.getpostform(html)
            # print data['__VIEWSTATE']
            # print finish_data['__VIEWSTATE']
            data['__VIEWSTATE'] = finish_data['__VIEWSTATE']
            pprint(data)
            submit_data = urllib.urlencode(data)
            html = self.getresponse(url=full_url, headers=self.headers, encoded_data=submit_data)
            print '*' * 255

        else:
            print "Didn't finished yet!"


    def EnterCoursePage(self):
        if not self.logined:
            print "Have not logined yet"
            return
        # url_temp = 'http://202.116.160.170/xf_xsqxxxk.aspx?gnmkdm=N121104&xh={}&xm={}'

        # 以下数据为用户数据
        data_enterpage = {
            'xh':self.username,
            'xm':self.ChineseName.encode('gb2312'),
            'gnmkdm':'N121104',
        }
        encoded_data = urllib.urlencode(data_enterpage)
        print encoded_data



        print 255 * '*'
        response_coursepage = self.getresponse(url=self.url_PublicCourse+encoded_data, headers=self.headers)
        html_coursepage = response_coursepage.read()
        # print html_coursepage.decode('gb2312')
        # Entered!!!

        postform = self.getpostform(html_coursepage)
        pprint(postform)

        # 筛选条件
        postform['ddl_kcgs'] = 'A系列'.encode('gb2312')      # 课程归属
        postform['dpkcmcGrid:txtPageSize'] = '20'
        # 若根据课程名称搜索，筛选条件无效
        postform['TextBox1'] = '影视艺术鉴赏(A系列)'.encode('gb2312')   # 根据课程名称搜索

        postform['ddl_xqbs'] = '2'                          # 1：主校区     2：东区    3：启林

        encoded = urllib.urlencode(postform)


        # 华丽的分割线
        # 以下为乱写的代码
        print 255 * '-='

        t1 = self.getresponse(url = self.url_PublicCourse+encoded_data, headers=self.headers, encoded_data=encoded)
        html = t1.read()
        # print html.decode('gbk')
        data_bomb = self.getpostform(html)
        del data_bomb['Button2']
        del data_bomb['Button4']
        del data_bomb['Button5']
        del data_bomb['btnClose']
        del data_bomb['dpkcmcGrid:btnFirstPage']
        del data_bomb['dpkcmcGrid:btnLastPage']
        del data_bomb['dpkcmcGrid:btnNextPage']
        del data_bomb['dpkcmcGrid:btnPrePage']
        del data_bomb['dpkcmcGrid:btnpost']
        data_bomb['kcmcGrid:_ctl3:xk'] = 'on'
        data_bomb['kcmcGrid:_ctl6:xk'] = 'on'
        data_bomb['Button1'] = '  提交  '.encode('gb2312')
        pprint(data_bomb)

        self.BombingCourse(url_target=self.url_PublicCourse+encoded_data, data_dict=data_bomb, bomb_times=100, sleep=0.1)


        pass

    def BombingCourse(self, url_target, data_dict, bomb_times = -1, sleep = 3):
        encoded_data = urllib.urlencode(data_dict)
        # print encoded_data
        times_bombed = 0
        while bomb_times!= 0:
            times_bombed += 1
            if bomb_times > 0:
                bomb_times-=1

            print 128 * '~'
            print "Tried times ==", times_bombed
            response = self.getresponse(url=url_target, headers=self.headers, encoded_data=encoded_data)
            html = response.read()

            # with open('output.txt', 'w') as somefile:
            #     somefile.write(html)

            match_alert = re.compile('alert\((.*?)\)'.encode('gb2312'))
            alert = match_alert.findall(html)
            # pprint(alert)
            print alert[0].decode('gb2312')
            # time.sleep(sleep)

        pass

    def updateheaders(self, url):
        self.referer = url
        self.headers['Referer'] = self.referer


def main():

    username = raw_input("Enter the user:\n")
    passwd = raw_input("Enter the password:\n")

    try:
        test = LoginSystem(username, password=passwd)

        test.EnterCoursePage()
        # test.evaluateClass()


    except urllib2.HTTPError as e:
        print e.code
        print e.reason
    pass


if __name__ == '__main__':

    main()

"""

'所有评价已完成，现在可以提交！'

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



__EVENTTARGET
__EVENTARGUMENT
ddl_kcxz
ddl_ywyl
ddl_kcgs
ddl_xqbs
2
ddl_sksj
TextBox1
(A
Button2
È·¶¨
kcmcGrid:_ctl2:jcnr
|||
kcmcGrid:_ctl3:jcnr
|||
kcmcGrid:_ctl4:jcnr
|||
kcmcGrid:_ctl5:jcnr
|||
kcmcGrid:_ctl6:jcnr
|||
kcmcGrid:_ctl7:jcnr
|||
kcmcGrid:_ctl8:jcnr
|||
kcmcGrid:_ctl9:jcnr
|||
kcmcGrid:_ctl10:jcnr
|||
kcmcGrid:_ctl11:jcnr
|||
kcmcGrid:_ctl12:jcnr
|||
kcmcGrid:_ctl13:jcnr
|||
kcmcGrid:_ctl14:jcnr
|||
kcmcGrid:_ctl15:jcnr
|||
kcmcGrid:_ctl16:jcnr
Ò©ÓÃÖ²ÎïÑ§|¿ÆÑ§³ö°æÉç|ÍõµÂÈº£¬Ì¸Ï×ºÍ|1
dpkcmcGrid:txtChoosePage
1
dpkcmcGrid:txtPageSize
15



 """
