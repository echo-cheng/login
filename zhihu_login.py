import requests
import re
import time
import http.cookiejar

#构造Requests headers
agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
headers = {
    "Host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    'User-Agent': agent
}

session = requests.Session()
session.cookies = http.cookiejar.LWPCookieJar(filename='cookies')#The LWPCookieJar saves a sequence of "Set-Cookie3" lines
#获取_xsrf:这种参数，一般叫做页面校检码，是来检查你是否是从正常的登录页面过来的
#_xsrf是动态变化的参数
def get_xsrf():
    url = 'https://www.zhihu.com/#signin'
    response = requests.get(url,headers = headers)
    page_content = response.text
    re_xsrf = re.compile(r'name="_xsrf" value="(.*)"')
    #这里的_xsrf是一个list
    _xsrf =re_xsrf.findall(page_content)
    _xsrf = _xsrf[0]
    return _xsrf

#---------------获取验证码文件--------------------
def get_captcha():
    randomtime = str(int(time.time() * 1000))
    print(randomtime)
    captchaurl = 'https://www.zhihu.com/captcha.gif?r='+\
                 randomtime+"&type=login"
    captcharesponse = session.get(url=captchaurl, headers=headers)
    with open('checkcode.gif', 'wb') as f:
        f.write(captcharesponse.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        # os.startfile('checkcode.gif')
    captcha = input('请输入验证码：')
    # print(captcha)
    return captcha


#--------------模拟登录-----------------
def login(account,password):
    _xsrf = get_xsrf()
    headers["X-Xsrftoken"] = _xsrf
    headers["X-Requested-With"] = "XMLHttpRequest"
    #通过account判断是手机号还是邮箱
    if re.match(r'^1\d{10}$',account):
        loginurl = 'https://www.zhihu.com/login/phone_num'
        formdata = {
            'phone_num': account,
            'password': password,
            '_xsrf': _xsrf,
        }
    else:
        loginurl= 'https://www.zhihu.com/login/email'
        formdata = {
            'email': account,
            'password': password,
            '_xsrf': _xsrf,
        }
    response = session.post(loginurl, formdata, headers=headers)#不加headers=会报错
    print(response.json())
    print(response.json()['msg'])
    #没有验证码登录失败，则
    if response.json()['r'] == 1:
        #获取验证码
        formdata['captcha'] = get_captcha()
        response = session.post(loginurl,formdata,headers = headers)
        print(response.json()['msg'])
        #打印response.headers里所有的键，会发现有一项是Set-Cookie
        print(response.headers.keys())
    #保存cookie，之后就可以使用cookie直接登录
    session.cookies.save()

account = input("请输入账号：")
password = input("请输入密码：")
login(account,password)

#验证是否登录成功
mylog = 'https://www.zhihu.com/people/da-da-juan-76-52/activities'
response = session.get(mylog,headers = headers)
print(response.status_code)
print(response.url)
# data = parse.urlencode(formdata).encode('UTF8')
# res = request.Request(loginurl,data)
# response2 = request.urlopen(res)


