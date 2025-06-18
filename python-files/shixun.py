# name :师冉亨
# 作用：
# $(DATE)
# $(DAY)
# $(HOUR)
# $(MINUTE)
# $(SECOND)
from importlib.metadata import pass_none
from random import choice
import csv

#老师和学生的功能
class Function:
    def Teacher_Function(self):#老师的功能
        print('''老师功能：
              1.用户管理(1.增加2.删除3.查找)
              2.课程管理(1.增加2.修改3.查找)
              3.成绩管理(1.增加2.查找)
              4.退出''')
    def  Student_Function(self):#学生的功能
        print('''学生功能：
              1.成绩查询
              2.教室课程表查询
              3.退出''')
teacher9=Function()#创建老师对象
student9=Function()#创建学生对象


#用户类
class Person:
    def __init__(self,name,id,gender):#初始化方法
        self.name=name
        self.id=id
        self.gender=gender
    def introduce(self):#介绍自己
        return f"姓名为{self.name},学号为{self.id},性别为{self.gender}"


#用户管理类
class Manager:
    def __init__(self,manage_file="user_management.csv"):#初始化Manager()类打开文件为"user_management.csv"
        self.manage_file=manage_file


    #判断用户是否存在
    def if_exit(self,name):
        with open(self.manage_file,'r',encoding='utf-8',newline='') as f:#打开文件
            reader=csv.DictReader(f)#读取文件
            for i in reader:
                if i['name']==name:#判断是否相同
                    return True
        return False


    #添加学生数据
    def add(self,name,age,id,gender):
        with open(self.manage_file,'a',encoding='utf-8',newline='') as f:#newline=''防止空一行
            writer=csv.writer(f)#创建一个csv写入对象（writer），写入csv文件f
            writer.writerow([name,age,id,gender])#写入单行
        print("添加成功")


    # 删除学生数据
    #不能直接删除，要重新写入一个新文件但是其中不包括要删除的数据    ————   读取，过滤，重写
    def delete(self,name):
        rows=[]#储存要保留的学生
        with open(self.manage_file, 'r', encoding='utf-8',newline='') as f:
            reader=csv.DictReader(f)
            header = reader.fieldnames#读取csv文件表头
            for row in reader:
                if row['name']!=name:
                    rows.append(row)#删除名字相同的，保留不删除的追加到列表rows里面

        with open(self.manage_file, 'w', encoding='utf-8', newline='') as fi:
            writer=csv.DictWriter(fi,fieldnames=header)#第一个参数为文件，第二个参数fielinames为文件的第一行
            writer.writeheader()#先写入表头，将指定的fieldnames作为第一行写入
            writer.writerows(rows)#写入保留下的数据
        print("删除成功")



##课程管理类
class  Course:
    def  __init__(self,course_file="course.csv"):#初始化Course()类的打开文件为"course.csv"
        self.course_file=course_file

    #判断课程是否存在
    def if_exit(self,name):
        with open(self.course_file,'r',encoding='utf-8',newline='') as f:
            reader=csv.DictReader(f)
            for i in reader:
                if i['name']==name:
                    return True
        return False


    #添加课程数据
    def add(self, name, teacher, credit, place):
        try:#捕获程序运行的异常
            if self.if_exit(name):#调用if_exit()方法
                print("该课程已存在")
                return False
            with open(self.course_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)#创建writer对象
                writer.writerow([name, teacher, credit, place])
            print("添加成功")
            return True
        except Exception as e:#所有异常的父类Exception
            print(f"添加课程失败: {e}")
            return False

# 修改课程数据
    def modify(self, name):
        if not self.if_exit(name):#调用自身方法检查课程是否存在
            print("课程不存在")
            return False

        with open("course.csv", 'r', encoding='utf-8',newline='') as f:
            reader = csv.DictReader(f)#读取文件
            header = reader.fieldnames#保留表头
            list1 = list(reader)#所有数据存入列表
            new_list = [i for i in list1 if i['name'] != name]#将要修改的课程过滤到，只保留需要的课程到new_list中
        #输入新课程
        new_name=input("请输入新课程名称:")
        new_teacher=input("请输入新课程老师:")
        new_credit=input("请输入新课程学分:")
        new_place=input("请输入新课程地点:")
        #追加到new_list中
        new_list.append({'name':new_name,'teacher':new_teacher,'credit':new_credit,'place':new_place})

        #重写csv文件
        with open("course.csv", 'w', encoding='utf-8',newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header)#设置表头参数为header
            writer.writeheader()#写入表头
            writer.writerows(new_list)#写入保留的内容
            print("修改成功")


    def    search(self, name):
        if not self.if_exit(name):#调用自身方法判断是否存在
            print("课程不存在")
            return False
        with open("course.csv", 'r', encoding='utf-8',newline='') as f:
            reader = csv.DictReader(f)#读取文件
            for i in reader:
                if i['name']==name:#如果要查找的课程名字相同
                    return i#返回课程的信息



#成绩管理
class Grade:
    def __init__(self,grade_file="grade.csv"):#设置Grade()类的文件为"grade.csv"
        self.grade_file=grade_file
    def if_exist(self,name):#判断是否存在
        with open(self.grade_file,'r',encoding='utf-8') as f:
            reader=csv.DictReader(f)
            for i in reader:
                if i['姓名']==name:
                    return True
        return False

    def add(self,name,grade1,grade2,grade3):
        with open(self.grade_file,'a',encoding='utf-8',newline="") as f:
            writer=csv.writer(f)#读取文件
            writer.writerow([name,grade1,grade2,grade3])#写入文件
        print("添加成功")


    def seek(self):
        with open(self.grade_file,'r',encoding='utf-8') as f:
            reader=csv.reader(f)#返回列表
            for row in reader:
                print(row)#输出全部内容



while True:
    user=int(input("请选择登录人物(1.老师/2.学生):"))#选择身份
    if user==1:#老师身份
        name=input("请输入用户名:")
        id=input("请输入学号:")
        gender=input("请输入性别:")
        laoshi=Person(name,id,gender)#创建Person类的对象
        print(laoshi.introduce())#调用介绍方法
        print("老师登录成功")
        teacher9.Teacher_Function()#调用老师的功能

        choice=int(input("请选择功能:"))#选择老师的总功能
        if choice==1:#用户管理系统
            print('''用户管理系统
                    1.增加
                    2.删除
                    3.查找''')
            choose=int(input("请选择功能:"))
            if choose==1:#增加学生
                manager=Manager()#创建Manager()类的对象manager
                student_name=input("请输入学生用户名:")
                if manager.if_exit(student_name):#判断是否存在
                    print("改学生已存在")

                else:#不存在改学生就输入信息然后增加
                    age=input("请输入学生年龄:")
                    id=input("请输入学生学号:")
                    gender=input("请输入学生性别:")
                    manager.add(student_name,age,id,gender)

            elif choose==2:
                manager1=Manager()#创建Manager()类的对象manager1
                student_name=input("请输入要删除的学生用户名:")
                if not manager1.if_exit(student_name):
                    print("该学生不存在")
                else:#改学生存在就删除
                    manager1.delete(student_name)

            elif  choose==3:
                manager3=Manager()#创建Manager()类的对象manager3
                with  open(manager3.manage_file, 'r', encoding='utf-8') as f:
                    reader=csv.DictReader(f)
                    for i in reader:
                        print(i)#输出全部信息


        elif  choice==2:#课程管理系统
            print('''课程管理系统
                    1.添加课程
                    2.修改课程
                    3.查找课程''')
            choose1=int(input("请选择功能:"))
            if choose1==1:#添加课程
                course1=Course()#创建Course()类的对象course1
                name1=input("请输入课程名称:")
                course1.if_exit(name1)#用对象course1调用方法判断是否存在
                teacher=input("输入老师名字")
                credit=input("输入学分")
                place=input("输入教室地点")
                course1.add(name1,teacher,credit,place)#增加
            elif choose1==2:#修改课程
                name2=input("输入要修改的课程名称")
                course2=Course()#创建Course()类的对象course2
                course2.if_exit(name2)#判断是否存在
                course2.modify(name2)#存在就修改
            elif choose1==3:#查找课程
                course3=Course()#创建Course()类的对象course3
                name3 = input("输入要查找的名称")
                course3.if_exit(name3)
                print(course3.search(name3))#查找课程的具体信息


        elif  choice==3:#成绩管理系统
            print('''成绩管理系统：
                    1.添加学生成绩
                    2.查找全部成绩''')
            choose2=int(input("请选择功能:"))
            grade=Grade()#创建Grade()类的对象grade
            if choose2==1:
                name = input("请输入学生用户名:")
                if grade.if_exist(name):
                    print("该学生存在")
                else:#不存在就添加
                    grade1=input("输入语文成绩")
                    grade2=input("输入数学成绩")
                    grade3=input("输入英语成绩")
                    grade.add(name,grade1,grade2,grade3)
            elif choose2==2:#查找
                grade.seek()
        elif choice==4:#退出
                break

    elif user==2:#学生
        name = input("请输入用户名:")
        id = input("请输入学号:")
        gender = input("请输入性别:")
        student1= Person(name,id,gender)#创建对象介绍自己
        print(student1.introduce())#调用introduce方法
        print("学生登录成功")
        student9.Student_Function()#学生功能
        student_choose=int(input("请选择功能:"))

        if student_choose==1:#查找某人的成绩
            with  open("grade.csv", 'r', encoding='utf-8') as f:
                reader=csv.DictReader(f)
                name = input("输入要查找的学生名字")
                for i in reader:#循环遍历查找是否存在
                    if i['姓名']==name:#存在就输出
                        print(i)
                        break#找到就退出循环
                else:#循环正常结束都没有找到才执行else
                    print("成绩不存在")

        if student_choose==2:#查找课程表
            with open("room.csv",'r',encoding='utf-8') as f:#打开文件
                reader=csv.reader(f)#读取文件
                for row in reader:#循环遍历reader
                    print(row)

        if student_choose == 3:#退出
            break


    choice=int(input("是否继续进行(0/1)"))#判断是否继续进行
    if choice==0:
        break#退出教务系统



        