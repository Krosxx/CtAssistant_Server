# app.py
import json
import time
import os

import os
from flask import Flask, Response
from flask import request
from flask import render_template, send_from_directory, url_for

from model.model import SchoolInfo
from schooladapters.BaseAdapter import BaseAdapter
from schooladapters.HaustAdapter import HaustAdapter

app = Flask(__name__, template_folder='templates')

app.config['APPLYS_FOLDER'] = os.getcwd() + '\\static\\applys'


class JsonResponse(Response):
    default_mimetype = 'application/json'


class HtmlResponse(Response):
    default_mimetype = 'text/html'


#
# class MyFlask(Flask):
#     response_class = MyResponse
#
#
# app = MyFlask(__name__)


@app.route('/', methods=['GET'])
def index():
    app.response_class = HtmlResponse
    return render_template('index.html')


@app.route('/applyAdapter', methods=["GET", "POST"])
def applyAdapter():
    app.response_class = HtmlResponse
    if request.method == "POST":
        date = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        schName = request.form.get('schName', '')
        data = {"schName": schName, "date": date, "shcUrl": request.form.get('shcUrl', ''),
                "sNo": request.form.get('sNo', ''), "pa": request.form.get('pa', ''),
                "other": request.form.get('other', '')}
        jsonData = json.dumps(data, indent=2, ensure_ascii=False)
        fileName = schName + '_' + date + '.json'
        requestFolder = app.config['APPLYS_FOLDER']
        filepath = os.path.join(requestFolder, fileName)
        if not os.path.exists(requestFolder):
            os.makedirs(requestFolder)
        with open(filepath, 'w', encoding='utf8') as f:
            f.write(jsonData)
        return render_template('success.html')
    else:
        return render_template('index.html')


@app.route('/applyDeal', methods=["GET", "POST"])
def applyDeal():
    app.response_class = HtmlResponse
    if request.method == "GET":
        applys = []
        if os.path.exists(app.config['APPLYS_FOLDER']):
            for file in os.listdir(app.config['APPLYS_FOLDER']):
                if os.path.splitext(file)[1] == '.json':
                    applys.append(file)
        return render_template('applyDeal.html', applys=applys)


def obj2Json(o):
    app.response_class = JsonResponse
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
    '河南科技大学': SchoolInfo('haust', '请使用我i科大账号密码登陆'),
}


# 支持学校列表
@app.route('/getSupportSchools', methods=['GET', 'POST'])
def getSupportSchools():
    body = {
        'status': 'success',
        'supportSchools': supportSchools
    }
    return obj2Json(body)


# 此学校显示提示消息
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


# 申请适配
@app.route('/postApplyAdapter', methods=['GET', 'POST'])
def postApplyAdapter():
    body = {}
    print(request.remote_addr)
    schoolName = request.form.get('schoolName', None)
    schoolWebsite = request.form.get('schoolWebsite', None)
    testAccount = request.form.get('testAccount', None)
    testPassword = request.form.get('testPassword', None)
    status = False
    date = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
    try:
        name = "applyAdapter/" + schoolName + ".json"
        result = os.path.exists(name)
        try:
            if result is False:  # 学校已经有人申请适配过则追击账号密码否则创建新文件
                data = {"学校名称": schoolName, "申请时间": date, "学校网站": schoolWebsite,
                        "account": [{"时间": date, "测试账号": testAccount, "测试密码": testPassword}]
                        }
                jsonData = json.dumps(data, indent=2, ensure_ascii=False)
                with open("applyAdapter/" + schoolName + ".json", 'w', encoding='utf8') as fp:  # 直接打开一个文件，如果文件不存在则创建文件
                    fp.write(jsonData)
            else:
                dataAdd = {"时间": date, "测试账号": testAccount, "测试密码": testPassword}
                with open("applyAdapter/" + schoolName + ".json", mode='r+', encoding='utf8') as fp:  # 直接打开一个文件，如果文件不存在则创建文件
                    last = json.loads(fp.read())
                    last["account"].append(dataAdd)
                with open("applyAdapter/" + schoolName + ".json", mode='w', encoding='utf8') as fp:
                    fp.write(json.dumps(last, indent=2, ensure_ascii=False))
            status = True
        except Exception as e:
            print(e)
            pass
    finally:
        body['status'] = status
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

    run_simple('0.0.0.0', 5000, app)
