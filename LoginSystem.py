# -*- coding:utf-8 -*-

__metaclass__ = type

import urllib, urllib2
import urlparse
import socket
import cookielib
import lxml.html
import re
import getpass
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
import smtplib
from pprint import pprint
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class LoginSystem:

    def __init__(self, username, password):
        self.logined = False
        self.sender_setted = False
        self.username = username
        self.password = password
        self.headers = {}
        # build openner with cookie
        cookie = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(cookie)
        self.opener = urllib2.build_opener(handler)



        self.domain = 'http://202.116.160.170/'
        # self.url_homepage = 'http://202.116.160.170/default2.aspx'
        # self.url_PublicCourse = 'http://202.116.160.170/xf_xsqxxxk.aspx?'
        self.url_homepage = self.domain+'default2.aspx'
        self.url_PublicCourse = self.domain+'xf_xsqxxxk.aspx?'
        self.url_Grade = self.domain+'xscjcx.aspx?'

        self.code_PublicCourse = 'N121104'
        self.code_Grade = 'N121605'

        print self.url_homepage


        self.headers = {
            'Host': '202.116.160.170',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',

            'Referer' : 'http://202.116.160.170/',
            # 'Referer': self.domain + 'xs_main.aspx?xh={}'.format(self.username),
            # 'Referer' : 'http://202.116.160.170/xs_main.aspx?xh={}'.format(self.username),

            # 'Cookie' : 'ASP.NET_SessionId=dqovqqjxbxmi4umopz1bf2j2',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            # 'Content-Length' : '196',
            # 'Content-Type' : 'application/x-www-form-urlencoded'

        }
        print self.headers['Referer']

        # using re to match secret code picture's url
        # Unicode Chinese \u4e00-\u9fa5
        self.match_secret_code_url = re.compile('\"(CheckCode\.aspx.*?)\"')
        self.match_alert = re.compile(u'alert\((.*?)\)')

        self.login()


    def login(self):

        html_loginpage = self.getresponse(self.url_homepage).read()
        # print html_loginpage.decode('gbk')
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

        pprint(self.headers)
        login_response = self.getresponse(url=self.url_homepage, encoded_data= encode_data, headers = self.headers)
        self.html_homepage = login_response.read()

        # login error have not handle yet
        result = self.match_alert.search(self.html_homepage)
        # print self.html_homepage.decode('gb2312')
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

        while True:
            try:

                picture = self.opener.open(fullurl).read()

                with open('image.jpg', 'wb') as file:
                    file.write(picture)
                return raw_input("Enter the secret code:")

            except urllib2.HTTPError as e:
                print e.code
                print e.reason
                time.sleep(0.25)

            except urllib2.URLError as e:
                print e.reason
                time.sleep(0.25)



    def getresponse(self, url, headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:50.0) Gecko/20100101 Firefox/50.0'}, encoded_data = None, ErrorSleep = 0.2):

        request = urllib2.Request(url, data=encoded_data, headers=headers)
        self.updateheaders(url)
        while True:
            try:
                response = self.opener.open(request)
                return response

            except urllib2.HTTPError as e:
                print e.code
                print e.reason
                time.sleep(ErrorSleep)

            except urllib2.URLError as e:
                print e.reason
                time.sleep(ErrorSleep)

            except socket.error as e:
                print e.errno
                time.sleep(ErrorSleep)



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
            'gnmkdm':self.code_PublicCourse,
        }
        encoded_data = urllib.urlencode(data_enterpage)
        # print encoded_data



        print 255 * '*'
        response_coursepage = self.getresponse(url=self.url_PublicCourse+encoded_data, headers=self.headers)
        html_coursepage = response_coursepage.read()
        # print html_coursepage.decode('gb2312')
        # Entered!!!

        postform = self.getpostform(html_coursepage)
        pprint(postform)

        # 筛选条件
        postform['ddl_kcgs'] = 'A系列'.encode('gb2312')      # 课程归属
        postform['dpkcmcGrid:txtPageSize'] = '30'
        # 若根据课程名称搜索，筛选条件无效
        postform['TextBox1'] = '蔬菜营养与保健(A系列)'.encode('gb2312')   # 根据课程名称搜索
        # postform['TextBox1'] = '昆虫与人类(A系列)'.encode('gb2312')  # 根据课程名称搜索
        postform['ddl_ywyl'] = ''   # 课程有无余量

        postform['ddl_xqbs'] = '2'                          # 1：主校区     2：东区    3：启林

        encoded = urllib.urlencode(postform)


        # 华丽的分割线
        # 以下为乱写的代码
        print 255 * '-='

        t1 = self.getresponse(url = self.url_PublicCourse+encoded_data, headers=self.headers, encoded_data=encoded)
        html = t1.read()
        print html.decode('gbk')

        data_bomb = self.getpostform(html)
        pprint(data_bomb)

        # 提交选课信息时只保留 "提交" 按钮，删除所有其他按钮
        del data_bomb['Button2']
        del data_bomb['Button4']
        del data_bomb['Button5']
        del data_bomb['btnClose']
        del data_bomb['dpkcmcGrid:btnFirstPage']
        del data_bomb['dpkcmcGrid:btnLastPage']
        del data_bomb['dpkcmcGrid:btnNextPage']
        del data_bomb['dpkcmcGrid:btnPrePage']
        del data_bomb['dpkcmcGrid:btnpost']
        try:
            del data_bomb['dpDataGrid2:btnFirstPage']
            del data_bomb['dpDataGrid2:btnPrePage']
            del data_bomb['dpDataGrid2:btnNextPage']
            del data_bomb['dpDataGrid2:btnLastPage']
            del data_bomb['dpDataGrid2:btnpost']
        except:
            pass

        # 提交当前显示页面的第  门课程，列表 第1门课程由 ctl2 开始计数
        data_bomb['kcmcGrid:_ctl2:xk'] = 'on'
        # data_bomb['kcmcGrid:_ctl5:xk'] = 'on'
        data_bomb['Button1'] = '  提交  '.encode('gb2312')
        pprint(data_bomb)

        self.BombingCourse(url_target=self.url_PublicCourse+encoded_data, data_dict=data_bomb, bomb_times=-1, sleep=0.2)


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
            print time.ctime()
            print "Times ==", times_bombed
            response = self.getresponse(url=url_target, headers=self.headers, encoded_data=encoded_data)
            html = response.read()

            # with open('output.txt', 'w') as somefile:
            #     somefile.write(html)

            match_alert = re.compile('alert\((.*?)\)'.encode('gb2312'))
            alert = match_alert.findall(html)
            # for i in alert:
            #     print i.decode('gb2312')
            print alert[0].decode('gb2312')
            time.sleep(sleep)

        pass


    def EnterGradePage(self, enable_check = False):

        if not self.logined:
            print "Have not logined yet"
            return

        # 以下数据为用户数据
        data_enterpage = {
            'xh':self.username,
            'xm':self.ChineseName.encode('gb2312'),
            'gnmkdm':self.code_Grade,
        }
        self.url_Grade_Personal = self.url_Grade + urllib.urlencode(data_enterpage)
        print self.url_Grade_Personal

        response_gradepage = self.getresponse(url = self.url_Grade_Personal, headers=self.headers)
        self.html_gradepage = response_gradepage.read()
        # print html_gradepage.decode('gb2312')

        self.grade_dict = self.LoadGradelist(self.html_gradepage)

        if enable_check:
            self.check_gradelist()




    def LoadGradelist(self, html_gradepage):

        post_form = self.getpostform(html_gradepage)
        try:
            del post_form['Button1']
            del post_form['Button2']
            del post_form['btn_dy']
            del post_form['btn_xn']
            del post_form['btn_xq']
            del post_form['btn_zg']
        except Exception as e:
            pass
        post_form['ddlXN'] = ''
        post_form['ddlXQ'] = ''
        post_form['ddl_kcxz'] = ''

        # pprint(post_form)
        encoded_postdata = urllib.urlencode(post_form)

        response_gradelist = self.getresponse(url = self.url_Grade_Personal, headers=self.headers, encoded_data=encoded_postdata)
        html_gradelist = response_gradelist.read()
        # print html_gradelist.decode('gb2312')

        tree = lxml.html.fromstring(html_gradelist)
        tr = tree.cssselect('td')


        info_end = 8
        info = tr[0:info_end]
        del tr[0:info_end]

        # 输出成绩单所属人信息
        # for i in info:
        #     print i.text_content()
        # print 512 * '='



        title_end = 19
        title = tr[0:title_end]
        del tr[0:title_end]

        # 以下内容输出成绩单

        # num = 0
        # for i in title:
        #     # print '%-30s' % i.text_content().strip(),
        #     print '{}{}'.format(num, i.text_content().strip()),
        #     num += 1
        # print
        # print 512 * '='

        # 0学年 1学期 2课程代码 3课程名称 4课程性质 5课程归属 6学分 7绩点 8平时成绩 9期中成绩
        # 10期末成绩 11实验成绩 12成绩 13辅修标记 14补考成绩 15重修成绩 16开课学院 17备注 18重修标记
        #

        #
        # line = 0
        # for i in tr:
        #     if line == 18:
        #         # print '%-30s' % i.text_content().strip()
        #         print '{}'.format(i.text_content().strip().ljust(30))
        #         line = 0
        #     else:
        #         line += 1
        #         # print '%-30s' % i.text_content().strip(),
        #         print '{}'.format(i.text_content().strip().ljust(30)),

        grade_dict = self.gradelist2dict(title, tr)

        # 用于打印存储成绩信息的字典
        # for key in self.grade_dict:
        #     print 512 * '='
        #     print '>>> {} <<<'.format(key)
        #     for i in self.grade_dict[key]:
        #         print i, self.grade_dict[key][i]

        return grade_dict


    def gradelist2dict(self, title, gradelist):
        dictionary = {}
        while gradelist:
            course_info = {}
            content = gradelist[0:19]
            del gradelist[0:19]

            for i in range(len(content)):
                course_info[title[i].text_content()] = content[i].text_content()

            dictionary[content[3].text_content()] = course_info

        # pprint(dictionary)

        return dictionary

    def set_sender(self, from_addr, password, to_addr):
        self.from_addr = from_addr
        self.password = password
        self.to_addr = to_addr
        self.sender_setted = True

    def check_gradelist(self, sleep_second = 60):
        """

        :param sleep_second: 此处刷新间隔不宜过长，否则会报重定向错误
        :return:
        """
        while True:
            temp_dict = self.LoadGradelist(self.html_gradepage)
            # temp_dict['测试Python课程提醒'] = {'课程名称':'Python网络测试', '平时成绩':'636.69', '期末成绩':'766.84'}
            for key in temp_dict:
                if key not in self.grade_dict:
                    print 512 * '*'
                    print time.ctime()
                    print "课程成绩发布"
                    for k in temp_dict[key]:
                        print k, temp_dict[key][k]
                    print 512 * '*'
                    self.send_new_grade(temp_dict[key], from_addr=self.from_addr, password=self.password, to_addr=self.to_addr)
                    self.grade_dict = temp_dict

            print '>>> Nothing <<<', time.ctime()

            # print 128 * '@'
            # for key in self.grade_dict:
            #     for i in self.grade_dict[key]:
            #         print self.grade_dict[key][i],
            #     print
            #
            # print 64*'-'
            # for key in temp_dict:
            #     for i in temp_dict[key]:
            #         print temp_dict[key][i],
            #     print
            #
            # print 128 * '@'

            time.sleep(sleep_second)


    def send_new_grade(self, dictionary, from_addr, password, to_addr, smtp_server = 'smtp.qq.com', port = 465):

        if self.sender_setted == False:
            print "Email sender hasn't been setted yet"
            return

        message = ''
        for key in dictionary:
            message += key+': '+dictionary[key]+'\n'

        msg = MIMEText(_text=message, _charset='utf-8')
        # msg['From'] = 'Python Email'
        # msg['To'] = self.ChineseName
        # msg['Subject'] = '课程成绩发布提醒'

        server = smtplib.SMTP_SSL(smtp_server, port)
        server.set_debuglevel(1)
        server.login(from_addr, password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()


    def updateheaders(self, url):
        self.referer = url
        self.headers['Referer'] = self.referer


def main():

    username = raw_input("Enter the user: ")
    passwd = getpass.getpass("Enter the password: ")

    test = LoginSystem(username, password=passwd)

    from_addr = raw_input("Email: ")
    email_password = getpass.getpass("Password: ")
    to_addr = raw_input("To whom: ")

    test.set_sender(from_addr = from_addr, password=email_password, to_addr = to_addr)

    # test.EnterCoursePage()
    # test.evaluateClass()
    # test.EnterGradePage(True)



if __name__ == '__main__':

    main()

