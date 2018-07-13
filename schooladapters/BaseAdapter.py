import json
from http.cookiejar import CookieJar

import requests


class BaseAdapter:

    def __init__(self, name='', password=''):
        # 账户名
        self.name = name
        self.password = password
        self.isLogin = False
        # 账户名
        self.s = requests.Session()
        # 模拟一个浏览器头
        #  保持Cookie不变，然后再次访问这个页面
        # CookieJar可以帮我们自动处理Cookie
        self.s.cookies = CookieJar()
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}

    # 主页显示提示消息
    def homeMessage(self):
        pass

    # 登陆
    def login(self) -> bool:
        pass

    # 个人课表
    def getClassTable(self, academicYear, stuNo=None) -> list:
        pass

    # 第一周星期一日期
    def getBaseWeek(self, semester) -> str:
        pass

    # 学年信息
    @staticmethod
    def getAyInfo(o):
        """学年信息"""
        body = {
            'status': 'success',
            'currentAy': o.getCurrentAcademicYear(),
            'allAy': o.getAllAcademicYear()
        }
        return json.dumps(body, default=lambda o: o.__dict__, indent=3)

    # 时间表
    def getTimeTable(self):
        pass

    # 获取当前学期和周次
    def getCurrentAcademicYear(self):
        pass

    # 获取所有学年学期
    def getAllAcademicYear(self):
        pass
