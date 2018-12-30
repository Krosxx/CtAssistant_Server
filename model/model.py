"""
标准类
"""


class SchoolInfo:
    def __init__(self, code, hintMessage):
        self.schoolCode = code
        self.hintMessage = hintMessage

'''
@:param teacher 教师
@:param weeks 周数组 int() #第1-6周 [1,2,3,4,5,6] 
@:param className 课程名 str
@:param classRoom 教室 str
@:param node 节数 int()
@:param week 第几节 
'''
class ClassInfo:
    """课程信息"""
    def __init__(self, teacher, weeks, className, classRoom, node, week) -> None:
        self.teacher = teacher
        self.weeks = [int(w) for w in weeks]
        self.className = className
        self.classRoom = classRoom
        self.node = [int(n) for n in node]
        self.week = int(week)

    def __repr__(self) -> str:
        return repr((self.teacher, self.weeks, self.className, self.classRoom, self.node, self.week))

'''
作息表 （可能多套作息表）
@:param beginDate str 开始日期 : '5.1'
@:param nodeList 作息时间节点
'''
class TimeTable:

    def __init__(self, beginDate, nodeList) -> None:
        self.nodeList = nodeList
        self.beginDate = beginDate

'''
作息时间节点
TimeTableNode(1, Time(8, 0), Time(8, 45))
@:param nodeNum 节数
@:param timeOfBeginClass 开始时间
@:param timeOfEndClass 结束时间
'''
class TimeTableNode:
    """作息表节数信息"""

    def __init__(self, nodeNum, timeOfBeginClass, timeOfEndClass) -> None:
        self.nodeNum = nodeNum
        # self.nodeName = nodeName
        self.timeOfBeginClass = timeOfBeginClass
        self.timeOfEndClass = timeOfEndClass

'''
时间类
'''
class Time:
    """时分"""

    def __init__(self, hour, minute) -> None:
        self.hour = int(hour)
        self.minute = int(minute)
        # self.second = int(second)

'''
@:param year 年 int
@:param termCode int 0/1 第一/二学期
@:param name str 学年学期名： 2017-2018第2学期
'''
class AcademicYear:
    """学年"""

    def __init__(self, year, termCode, name) -> None:
        self.year = int(year)
        self.termCode = int(termCode)
        self.name = name

    def getCode(self):
        return str(self.year) + str(self.termCode)
