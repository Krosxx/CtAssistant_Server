# 课表助手 服务器端

> 将课表导入至手机日历

## 支持学校

* 河南科技大学

## 如何支持你的学校

### 0x00. 继承 `BaseAdapter` 并且重写实现下列函数功能，返回数据参考`HaustAdapter`

```python
class YourAdapter(BaseAdapter):
    # 此学校显示提示消息
    '''
    json示例：
    无
    '''
    def homeMessage(self):
        pass

    # 登陆 
    # 返回账户信息是否正确
    def login(self) -> bool:
        pass

    # 个人课表
    # 返回list<ClassInfo>
    def getClassTable(self, academicYear, stuNo=None) -> list:
        pass

    # 第一周星期一日期 
    # 此接口可返回空，App端手动选择
    '''
    返回示例：
    2018-03-05
    '''
    def getBaseWeek(self, semester) -> str:
        pass

    # 学年信息(非必须)
    def getAyInfo(o):
        pass
        
    # 时间表
    '''
    返回 数组 [TimeTable,TimeTable, .. ]
    '''
    def getTimeTable(self):
        pass

    # 获取当前学期和周次
    '''
    @:return Optional[AcademicYear]
    '''
    def getCurrentAcademicYear(self) -> Optional[AcademicYear]:
        pass

    # 获取所有学年学期
    '''
    @:return Optional[List[AcademicYear]]
    '''
    def getAllAcademicYear(self) -> Optional[List[AcademicYear]]:
        pass


```

### 0x01. 在`app.py`中`supportSchools`中添加学校名以及学校代码

like this

```python
{
    '河南科技大学': 'haust',
}
```

### 0x02. 在`getSchoolAdapter()`添加你的适配器

```python
'学校代码': YourSchAdapter(...),
```

## 未完善功能

* 验证码问题
* 青果系统  参见:
    > https://blog.csdn.net/mrwangweijin/article/details/77194994
    > https://www.52pojie.cn/thread-743886-1-1.html

## App 端展示
Google Calendar
![](https://github.com/Vove7/CtAssistant_Server/blob/master/screenshot/Screenshot_1.jpg?raw=true)
![](https://github.com/Vove7/CtAssistant_Server/blob/master/screenshot/Screenshot_2.jpg?raw=true)

## 联系我

* 1132412166@qq.com