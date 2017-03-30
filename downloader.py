import urllib
import urllib2
import httplib
import re
#import requests



host = "courses.uscden.net"
login_url = r"/d2l/lp/auth/login/login.d2l"


post_dict = {
    'd2l_referrer': "",
    'userName': "zhanglid@usc.edu",
    'password': "xxxxx",
    'loginPath': "/d2l/login"
}

post_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #'Accept-Encoding': 'gzip, deflate, br',
    #'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    #'Content-Length': '89',
    'Content-Type': 'application/x-www-form-urlencoded',
    #'Host': 'courses.uscden.net',
    #'Origin': 'https://courses.uscden.net',
    #'Referer': 'https://courses.uscden.net/d2l/login?logout=1',
    #'Upgrade-Insecure-Requests': '1',
    #'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}


post_data = urllib.urlencode(post_dict)

conn = httplib.HTTPSConnection(host, 443)

conn.request("POST", login_url, post_data, post_headers)
resp3 = conn.getresponse()
resp3.read()

print resp3.status
print resp3.getheader("location")
location_id = resp3.getheader("location")[len('/d2l/home/'):]
cookie = resp3.getheader("set-cookie")

print location_id

xsrf_url = resp3.getheader("location")
print xsrf_url
print cookie

d2lSessionVal = re.compile(r'd2lSessionVal=[\d\w]+').search(cookie).group()
d2lSecureSessionVal = re.compile(r'd2lSecureSessionVal=[\d\w]+').search(cookie).group()
print d2lSessionVal
print d2lSecureSessionVal

xsrf_headers = {
    'Connection':   'keep-alive',
    'Cookie': d2lSessionVal + '; ' + d2lSecureSessionVal,
    'Host': 'courses.uscden.net',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #'Accept-Encoding': 'gzip, deflate, sdch, br',
    #'Accept-Language': 'zh-CN,zh;q=0.8'
}


conn.request("GET", xsrf_url, None, xsrf_headers)
resp_xsrf = conn.getresponse()
xsrf_data = resp_xsrf.read()
begin_index = re.compile(r"d2l_referrer").search(xsrf_data).end()

xsrf = xsrf_data[begin_index+5:begin_index+37]
print xsrf


course_info_url = "/d2l/le/manageCourses/widget/myCourses/"+location_id+"/ContentPartial?defaultLeftRightPixelLength=10&defaultTopBottomPixelLength=7"
course_info_post_headers = {
    'Host': ' courses.uscden.net',
    'Connection':   ' keep-alive',
    #'Content-Length':   ' 229',
    #'Pragma':   ' no-cache',
    #'Cache-Control':    ' no-cache',
    'Origin':   ' https://courses.uscden.net',
    'User-Agent':' Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Content-type': ' application/x-www-form-urlencoded',
    'Accept':   '*/*',
    'Referer':  'https://courses.uscden.net/d2l/home/6623',
    #'Accept-Encoding':  'gzip, deflate, br',
    #'Accept-Language':  'zh-CN,zh;q=0.8',
    'Cookie': d2lSessionVal + '; ' + d2lSecureSessionVal
    #'Cookie': "d2lSessionVal=BJC063UxcznhT9DghgM0chWNO; d2lSecureSessionVal=O8WeusW47G7lhtvEERnSeVZ7f"
}
print course_info_post_headers
course_info_post_dict = {
    'widgetId': '2',
    '_d2l_prc$headingLevel':    '3',
    '_d2l_prc$scope': "",
    '_d2l_prc$childScopeCounters':  'filtersData:0',
    '_d2l_prc$hasActiveForm':   'false',
    'filtersData$semesterId':   'All',
    'isXhr':    'true',
    'requestId':    '2',
    'd2l_referrer': xsrf
}

course_info_post_data = urllib.urlencode(course_info_post_dict)
conn.request("POST", course_info_url, course_info_post_data, course_info_post_headers)

resp4 = conn.getresponse()

print resp4.status
print resp4.getheaders()
course_data = resp4.read()


def find_term_list(course_data):
    start_index = re.compile(r'"Payload":').search(course_data).start()
    end_index = re.compile(r'"OnLoad"').search(course_data).end()+4
    payload = course_data[start_index:end_index]
    term_list_raw = re.compile(r'"d2l-heading vui-heading-3 \S+ id=[^>]+>[^<]+').findall(payload)
    term_list = []
    for s in term_list_raw:
        index = re.compile(r'>\w+ \d+').search(s).span()
        term_list.append(s[index[0]+1:index[1]])

    return term_list

print find_term_list(course_data)
