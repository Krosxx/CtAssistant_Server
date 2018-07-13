

"""
标准类
"""

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


class TimeTable:

    def __init__(self, beginDate, nodeList) -> None:
        self.nodeList = nodeList
        self.beginDate = beginDate


class TimeTableNode:
    """作息表节数信息"""

    def __init__(self, nodeNum, timeOfBeginClass, timeOfEndClass) -> None:
        self.nodeNum = nodeNum
        # self.nodeName = nodeName
        self.timeOfBeginClass = timeOfBeginClass
        self.timeOfEndClass = timeOfEndClass


class Time:
    """时分"""
    def __init__(self, hour, minute) -> None:
        self.hour = int(hour)
        self.minute = int(minute)
        # self.second = int(second)


class AcademicYear:
    """学年"""

    def __init__(self, year, termCode, name) -> None:
        self.year = int(year)
        self.termCode = int(termCode)
        self.name = name

    def getCode(self):
        return str(self.year) + str(self.termCode)
