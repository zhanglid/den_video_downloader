# Design a student class to help organise the application
import urllib
import httplib
import re


class Student:
    @staticmethod
    def find_term_list(course_data):
        start_index = re.compile(r'"Payload":').search(course_data).start()
        end_index = re.compile(r'"OnLoad"').search(course_data).end() + 4
        payload = course_data[start_index:end_index]
        term_list_raw = re.compile(r'"d2l-heading vui-heading-3 \S+ id=[^>]+>[^<]+').findall(payload)
        term_list = []

        for s in term_list_raw:
            index = re.compile(r'>\w+ \d+').search(s).span()
            term_list.append(s[index[0] + 1:index[1]])

        return term_list

    def __init__(self, user, passwd):
        """This function initializes the student instance"""
        self.user = user
        self.passwd = passwd
        self.login_status = False
        self.location_id = None
        self.d2lSessionVal = None
        self.d2lSecureSessionVal = None
        self.xsrf = None
        self.term_list = []
        self.course_list = [[]]
        self.course_ou_list = [[]]

    def login(self):
        """Login the useden.net with user/passwd"""

        # prepare the login url
        host = "courses.uscden.net"
        login_url = r"/d2l/lp/auth/login/login.d2l"

        # prepare the post data
        post_dict = {
            'd2l_referrer': "",
            'userName': self.user,
            'password': self.passwd,
            'loginPath': "/d2l/login"
        }
        post_data = urllib.urlencode(post_dict)

        # prepare the post header
        post_headers = {
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.8',
            # 'Cache-Control': 'max-age=0',
            # 'Connection': 'keep-alive',
            # 'Content-Length': '89',
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Host': 'courses.uscden.net',
            # 'Origin': 'https://courses.uscden.net',
            # 'Referer': 'https://courses.uscden.net/d2l/login?logout=1',
            # 'Upgrade-Insecure-Requests': '1',
            # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) '
        }

        # start login
        conn = httplib.HTTPSConnection(host, 443)
        conn.request("POST", login_url, post_data, post_headers)
        resp = conn.getresponse()
        resp_data = resp.read()

        # check login status
        fail_match = re.compile(r'loginFailed\.d2l\?status=[^&]+').search(resp_data)
        if fail_match:
            print 'login failed: '+fail_match.group()[len('loginFailed.d2l?status='):]
            return False
        else:
            #print 'login successfully'
            self.login_status =True

        # extract the respond data
        self.location_id = resp.getheader("location")[len('/d2l/home/'):]
        cookie_raw = resp.getheader("set-cookie")
        self.d2lSessionVal = re.compile(r'd2lSessionVal=[\d\w]+').search(cookie_raw).group()
        self.d2lSecureSessionVal = re.compile(r'd2lSecureSessionVal=[\d\w]+').search(cookie_raw).group()
        xsrf_url = resp.getheader("location")

        # prepare to get xsrf
        xsrf_headers = {
            # 'Connection':   'keep-alive',
            'Cookie': self.d2lSessionVal + '; ' + self.d2lSecureSessionVal,
            # 'Host': 'courses.uscden.net',
            # 'Upgrade-Insecure-Requests': '1',
            # 'Cache-Control': 'max-age=0',
            # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, sdch, br',
            # 'Accept-Language': 'zh-CN,zh;q=0.8'
        }

        # get xsrf
        conn.request("GET", xsrf_url, None, xsrf_headers)
        resp_xsrf = conn.getresponse()
        xsrf_data = resp_xsrf.read()
        xsrf_index = re.compile(r"d2l_referrer").search(xsrf_data).end()
        self.xsrf = xsrf_data[xsrf_index + 5:xsrf_index + 37]

        conn.close()
        return True

    def set_course_info(self):
        """Get terms and courses information from uscden.net"""
        host = "courses.uscden.net"
        course_info_url = "/d2l/le/manageCourses/widget/myCourses/" + self.location_id + "/ContentPartial?defaultLeftRightPixelLength=10&defaultTopBottomPixelLength=7"

        # prepare post headers
        course_info_post_headers = {
            #'Host': ' courses.uscden.net',
            #'Connection': ' keep-alive',
            # 'Content-Length':   ' 229',
            # 'Pragma':   ' no-cache',
            # 'Cache-Control':    ' no-cache',
            #'Origin': ' https://courses.uscden.net',
            #'User-Agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4)',
            'Content-type': ' application/x-www-form-urlencoded',
            #'Accept': '*/*',
            #'Referer': 'https://courses.uscden.net/d2l/home/'+self.location_id,
            # 'Accept-Encoding':  'gzip, deflate, br',
            # 'Accept-Language':  'zh-CN,zh;q=0.8',
            'Cookie': self.d2lSessionVal + '; ' + self.d2lSecureSessionVal
        }
        # prepare post data
        course_info_post_dict = {
            'widgetId': '2',
            #'_d2l_prc$headingLevel': '3',
            #'_d2l_prc$scope': "",
            #'_d2l_prc$childScopeCounters': 'filtersData:0',
            #'_d2l_prc$hasActiveForm': 'false',
            #'filtersData$semesterId': 'All',
            #'isXhr': 'true',
            #'requestId': '2',
            'd2l_referrer': self.xsrf
        }
        course_info_post_data = urllib.urlencode(course_info_post_dict)
        conn = httplib.HTTPSConnection(host, 443)
        conn.request("POST", course_info_url, course_info_post_data, course_info_post_headers)
        resp = conn.getresponse()
        course_data = resp.read()
        self.term_list = Student.find_term_list(course_data)
        term_num = len(self.term_list)
        self.course_ou_list = [[]]*term_num
        self.course_list = [[]]*term_num
        if term_num == 0:
            return
        elif term_num == 1:
            stop_index = len(course_data)
            start_index = 0
        else:
            start_index = 0
            stop_index = re.compile(self.term_list[1]).search(course_data).start()

        for i in range(term_num):
            course_list_raw = re.compile(r'vui-link d2l-link \S+ href\=\\\"/d2l/lp/ouHome/home\.d2l\?ou=\d+\\\" title\=\\\"[^"^\\]+').findall(course_data[start_index:stop_index])
            ou_list = []
            c_list = []
            for c in course_list_raw:
                ou_list.append(re.compile(r'ou=\d+').search(c).group()[3:])
                c_list.append(re.compile(r'title\=\\\"[^"]+').search(c).group()[14:].replace('&amp;', '&'))

            self.course_ou_list[i] = ou_list
            self.course_list[i] = c_list
            start_index = stop_index
            if i+2 < term_num:
                stop_index = re.compile(self.term_list[i+2]).search(course_data).start()
            else:
                stop_index = len(course_data)


if __name__ == '__main__':
    s = Student(raw_input('user:'), raw_input('password:'))

    if s.login():
        print 'login successfully'
    else:
        exit()
    s.set_course_info()

    for t in range(len(s.term_list)):
        print s.term_list[t]+':'
        for c in range(len(s.course_list[t])):
            print '\t'+s.course_list[t][c]


    #for i in range(1000):
    #    s = Student('xxxxxx@usc.edu', 'xxxxx')
    #    s.login()
