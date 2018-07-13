# app.py
import json

from flask import Flask, Response
from flask import request

from schooladapters.BaseAdapter import BaseAdapter
from schooladapters.HaustAdapter import HaustAdapter


class MyResponse(Response):
    default_mimetype = 'application/json'


class MyFlask(Flask):
    response_class = MyResponse


app = MyFlask(__name__)


def obj2Json(o):
    return json.dumps(o, default=lambda o: o.__dict__, indent=3)


def getSchoolAdapter(schCode, sNo, pa, autoLogin=True):
    """
    获取学校适配器
    :param schCode: 学校代码
    :param sNo: 学号，登陆账号
    :param pa: 密码
    :param autoLogin: 某些功能不需要登陆
    :return: 学校适配器
    """
    # 此处添加你的适配器
    o = {
        'haust': HaustAdapter(sNo, pa),

    }.get(schCode)
    if (autoLogin and o is not None):
        o.login()
    return o

# 此处添加你的学校名and代码
supportSchools = {
    '河南科技大学': 'haust',
}


# 支持学校
@app.route('/getSupportSchools', methods=['GET', 'POST'])
def getSupportSchools():
    body = {
        'status': 'success',
        'supportSchools': supportSchools
    }
    return obj2Json(body)


@app.route('/homeMessage', methods=['GET', 'POST'])
def homeMessage():
    schCode = request.form.get('sCode', None)
    o = getSchoolAdapter(schCode, None, None, autoLogin=False)
    if (o is None):
        body = {
            'status': 'wrong sCode',
            'msg': '学校代码错误'
        }
    else:
        body = {
            'status': 'success',
            'message': o.homeMessage()
        }
    return obj2Json(body)


# 登陆
@app.route('/login', methods=['GET', 'POST'])
def login():
    body = {}
    body['status'], o = checkParams(request)
    return obj2Json(body)


# 课表
@app.route('/getClassTable', methods=['GET', 'POST'])
def getClassTable():
    body = {}
    body['status'], o = checkParams(request)
    if body['status'] != 'success':
        return obj2Json(body)

    semester = request.form.get('semester', None)  # 学年
    if semester is None:  # 默认当前
        semester = o.getCurrentAcademicYear().getCode()
    classTable = o.getClassTable(semester)

    body['classTable'] = classTable
    return obj2Json(body)


# 第一周星期一日期
@app.route('/getDateOfBaseWeek', methods=['GET', 'POST'])
def getDateOfBaseWeek():
    body = {}
    body['status'], o = checkParams(request)
    if body['status'] != 'success':
        return obj2Json(body)

    semester = request.form.get('semester', None)  # 学年
    if semester is None:  # 默认当前
        semester = o.getCurrentAcademicYear().getCode()

    body['dateOfBaseWeek'] = o.getBaseWeek(semester)
    return obj2Json(body)


# 作息表
@app.route('/getTimeTable', methods=['GET', 'POST'])
def getTimeTable():
    body = {}

    schCode = request.form.get('sCode', None)
    o = getSchoolAdapter(schCode, None, None, autoLogin=False)

    if (o):
        body['status'] = 'success'
        body['timetables'] = o.getTimeTable()
        return obj2Json(body)
    else:
        body['status'] = 'none'
        return obj2Json(body)


# 学年信息
@app.route('/getAyInfo', methods=['GET', 'POST'])
def getAyInfo():
    body = {}
    body['status'], o = checkParams(request)
    if body['status'] != 'success':
        return obj2Json(body)
    body = BaseAdapter.getAyInfo(o)
    return body


def checkParams(request):
    print(request.remote_addr)

    schCode = request.form.get('sCode', None)
    sNo = request.form.get('sNo', None)
    pa = request.form.get('pa', None)
    if schCode is None or sNo is None or pa is None:
        return 'params_none', None

    o = getSchoolAdapter(schCode, sNo, pa)
    if not o.isLogin:
        return 'login_failed', None
    return 'success', o


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    run_simple('localhost', 5000, app)
