import json
import re
import datetime

import requests
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup
import io
import sys

from model.model import ClassInfo, TimeTableNode, AcademicYear, Time, TimeTable
from schooladapters.BaseAdapter import BaseAdapter

'''
@author: Vove
'''
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 作息表
timeTable = [
    TimeTable('5.1', [
        TimeTableNode(1, Time(8, 0), Time(8, 45)),
        TimeTableNode(2, Time(8, 0), Time(8, 45)),
        TimeTableNode(3, Time(8, 55), Time(9, 40)),
        TimeTableNode(4, Time(10, 0), Time(10, 45)),
        TimeTableNode(5, Time(10, 55), Time(11, 40)),
        TimeTableNode(6, Time(14, 30), Time(15, 15)),
        TimeTableNode(7, Time(15, 20), Time(16, 5)),
        TimeTableNode(8, Time(16, 25), Time(17, 10)),
        TimeTableNode(9, Time(17, 20), Time(18, 5)),
        TimeTableNode(10, Time(18, 10), Time(18, 55)),
        TimeTableNode(11, Time(19, 30), Time(20, 15)),
        TimeTableNode(12, Time(20, 20), Time(21, 5)),
        TimeTableNode(13, Time(21, 10), Time(21, 55)),
    ]),

    TimeTable('10.1', [
        TimeTableNode(1, Time(8, 0), Time(8, 45)),
        TimeTableNode(2, Time(8, 0), Time(8, 45)),
        TimeTableNode(3, Time(8, 55), Time(9, 40)),
        TimeTableNode(4, Time(10, 00), Time(10, 45)),
        TimeTableNode(5, Time(10, 55), Time(11, 40)),
        TimeTableNode(6, Time(14, 0), Time(14, 45)),
        TimeTableNode(7, Time(14, 50), Time(15, 35)),
        TimeTableNode(8, Time(15, 55), Time(16, 40)),
        TimeTableNode(9, Time(16, 50), Time(17, 35)),
        TimeTableNode(10, Time(17, 40), Time(18, 25)),
        TimeTableNode(11, Time(19, 00), Time(19, 45)),
        TimeTableNode(12, Time(19, 50), Time(20, 35)),
        TimeTableNode(13, Time(20, 40), Time(21, 25)),
    ]),
]


class HaustAdapter(BaseAdapter):
    '河南科技大学'
    __loginUri = 'http://my.haust.edu.cn/cas/login'
    __URL_CT_API = 'http://jskb.haust.edu.cn:9900/xqcx/xqcx/datacollection/getData.do?dcUuid='
    __apiHeader = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Referer': 'http://jskb.haust.edu.cn:9900/jwkz/xgrkb.jsp'
    }

    # 初始化构造函数，账户和密码
    def __init__(self, name='', password=''):
        super().__init__(name, password)

        if not self.login():
            # print('账号密码无效')
            return

    # 主页显示提示消息
    def homeMessage(self):
        return '密码为我i科大密码'

    # 登陆
    def login(self) -> bool:
        if self.isLogin:
            return True
        # 得到一个Response对象，但是此时还没有登录
        r = self.s.get(self.__loginUri, headers=self.header)
        # 得到post data应该有的lt
        # 这里使用BeautifulSoup对象来解析HTML
        dic = {}
        lt = BeautifulSoup(r.text, 'html.parser')
        for line in lt.form.findAll('input'):
            if (not line.attrs['name'] is None):
                if line['name'] == "username" or line.attrs['name'] == "password":
                    continue
                dic[line.attrs['name']] = line.attrs['value']
        # 取form值
        params = {
            'username': self.name,
            'password': self.password,
            'lt': dic['lt'],
            'execution': dic['execution'],
            '_eventId': dic['_eventId']}
        # 使用构建好的PostData重新登录,以更新Cookie
        r = self.s.post(self.__loginUri, data=params, headers=self.header)  # 登陆
        # print(r.text)
        if r.text.__contains__("登录成功"):
            self.isLogin = True

        # 登陆 获取api postData
        js = self.s.get('http://jskb.haust.edu.cn:9900/jwkz/js/xgrkb.js')  # js文件包含参数
        text = js.text
        reg = 'dcUuid=[0-9a-z]+'
        pattern1 = re.compile(reg)
        self.ctUuid = re.findall(re.compile('var uuid = \'[0-9a-z]+'), text)[0].split('\'')[1]  # 课程表uuid

        self.uuid = [i.split('=')[1] for i in re.findall(pattern1, text)]
        # print(self.uuid)
        # print(self.ctUuid)

        return self.isLogin

    # 个人信息
    def getPersonalInfo(self, stuNo=None):
        if not self.isLogin:
            # print("未登录")
            return
        if stuNo is None:
            stuNo = self.name
        q_uuid = self.uuid[6].__str__()
        data = "queryCondition=[{qcLogicSign:'like', qcUuid:'1', qcRelationSign:'and', fName:'xh', qcValue:'" + stuNo + "'}]"

        json = self.s.post(self.__URL_CT_API + q_uuid, data=data, headers=self.__apiHeader)
        print(json.text)
        return json.text

    # 第一周星期一日期
    def getBaseWeek(self, semester):
        try:
            j = self.getDataByWeek(semester, '01')
            date = json.loads(j)[0]['ZCRQ'][4:14]
            return date
        except Exception as err:
            print(err)
            return None

    # 个人课表
    def getClassTable(self, academicYear, stuNo=None) -> list:
        if not self.isLogin:
            # print("未登录")
            return []
        if stuNo is None:
            stuNo = self.name
        uuid = self.ctUuid.__str__()
        kcmc = stuNo
        dqzc = '1'
        xnxq = academicYear
        linkParam = "queryCondition=[{qcLogicSign:'=', qcUuid:'" + uuid + "', qcRelationSign:'and', fName:'xh', qcValue:'" + kcmc + "'}," + "{qcLogicSign:'=', qcUuid:'" + uuid + "', qcRelationSign:'and', fName:'jgh', qcValue:'" + kcmc + "'}," + "{qcLogicSign:'=', qcUuid:'" + uuid + "', qcRelationSign:'and', fName:'xnxq', qcValue:'" + xnxq + "'}," + "{qcLogicSign:'=', qcUuid:'" + uuid + "', qcRelationSign:'and', fName:'zc', qcValue:'" + dqzc + "'}]"

        j = self.s.post(self.__URL_CT_API + uuid, data=linkParam, headers=self.__apiHeader)
        cts = []
        js = json.loads(j.text)
        for c in js:
            # print(c)
            info = ClassInfo(c['SKJS'].replace(' ', ''), c['ZC'].split(','), c['KCMC'], c['ROOM'], c['JC'].split(','),
                             c['XINQ'])
            cts.append(info)
            # print(json.dumps(info, cls=ClassInfoEncoder))
        # print(json.dumps(cts,cls=ClassInfoEncoder))
        return cts

    # 某学期某周次日期
    def getDataByWeek(self, academicYear, week):
        if not self.isLogin:
            # print("未登录")
            return
        zc = week
        xnxq = academicYear
        uuid = self.uuid[3].__str__()
        linkParam = "queryCondition=[{qcLogicSign:'like', qcUuid:'" + uuid + "', qcRelationSign:'and', fName:'xnxq', qcValue:'" + xnxq + "'},{qcLogicSign:'like', qcUuid:'" + uuid + "', qcRelationSign:'and', fName:'zc', qcValue:'" + zc + "'}]"

        j = self.s.post(self.__URL_CT_API + uuid, data=linkParam, headers=self.__apiHeader)
        j = j.text

        # print(json.text)
        return j

    # 时间表
    def getTimeTable(self):
        return timeTable

    # def getTimeTable(self):
    #     if not self.isLogin:
    #         # print("未登录")
    #         return
    #     linkParam = "queryCondition="
    #     uuid = self.uuid[4].__str__()
    #     j = self.s.post(self.__URL_CT_API + uuid, data=linkParam, headers=self.apiHeader)
    #     l = []
    #     js = json.loads(j.text)
    #     for n in js:
    #         hour, minute = n['KSSJ'].split(':')
    #         node = TimeTableNode(int(n['DM']), n['MC'], Time(hour, minute, 0), '')
    #         l.append(node)
    #     return l

    # 获取某学年对应周日期区间
    def getWeekDate(self, academicYear):
        if not self.isLogin:
            # print("未登录")
            return
        uuid = self.uuid[8].__str__()
        xnxq = academicYear
        linkParam = "queryCondition=[{qcLogicSign:'like', qcUuid:'" + uuid + "', qcRelationSign:'and', fName:'xnxq', qcValue:'" + xnxq + "'}]"

        json = self.s.post(self.__URL_CT_API + uuid, data=linkParam, headers=self.__apiHeader)
        # print(json.text)
        return json.text

    # 获取当前学期和周次
    def getCurrentAcademicYear(self):
        if not self.isLogin:
            # print("未登录")
            return None

        try:
            uuid = self.uuid[2].__str__()
            now = datetime.date.today().__str__()
            linkParam = "queryCondition=[{qcLogicSign:'like', qcUuid:'" + uuid + "', qcRelationSign:'and', fName:'dqrq', qcValue:'" + now + "'}]"

            j = self.s.post(self.__URL_CT_API + uuid, data=linkParam, headers=self.__apiHeader)

            cy = json.loads(j.text)[0]['XNXQ']
            year = cy[:4]
            code = cy[4:]

            return AcademicYear(year, code, year + '-' + str(int(year) + 1) + '第' + str(int(code) + 1) + '学期')
        except Exception as msg:
            print(msg)
            return None

    # 获取所有学年学期
    def getAllAcademicYear(self):
        if not self.isLogin:
            # print("未登录")
            return None
        uuid = self.uuid[1].__str__()

        j = self.s.post(self.__URL_CT_API + uuid, data='', headers=self.__apiHeader)
        l = []
        for ay in json.loads(j.text):
            academicYear = AcademicYear(ay['XN'], ay['XQ_ID'], ay['XN_MC'] + ay['XQ_MC'])
            l.append(academicYear)
        return l

    def close(self):
        self.isLogin = False
        self.s.close()


if (__name__ == "__main__"):
    f = open('t', 'r')
    n = f.readline().replace('\n', '')
    p = f.readline()
    h = HaustAdapter(n, p)
    # h.getPersonalInfo('151404060132')
    # cts = h.getClassTable('20171')
    # print(json.dumps(cts, default=lambda o: o.__dict__, indent=4))

    # print(h.getBaseWeek('20171'))
    # print(h.getDataByWeek('20171', '01'))
    # tb = h.getTimeTable()
    # print(json.dumps(tb, default=lambda o: o.__dict__, indent=3))
    # h.getWeekDate('20171')
    j = h.getCurrentAcademicYear()
    print(json.dumps(j, default=lambda o: o.__dict__, indent=3))
    j = h.getAllAcademicYear()
    print(json.dumps(j, default=lambda o: o.__dict__, indent=3))
    h.close()
