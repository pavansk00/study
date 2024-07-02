# class Student:
#     '''This is student class with data'''          # doc string this is optional but to keep this good programming practice
#     def __init__(self, name, rollno, mark):        #constructor
#         self.name = name                           #this are instance veriable init. of obj to provide value to instance veriable
#         self.rollno = rollno
#         self.mark = mark

#     def read(self):
#         print("reanding python")

#     def display(self):
#         print("Student name:{}, rollno:{}, marks:{}".format(self.name, self.rollno, self.mark))

# s =Student("pav", 7, 70)
# # s.read()
# #print(s.name, s.rollno, s.mark)
# #s is ref veriable pointing to student obj

# s.display()
# print(s.__doc__)                                 #print doc string

"""//////////////////////////////////////////////////////////////////////////////////////////////////////"""

# static veriable, instance veriable, local veriable


class Student:
    # this is static veriable or class level veriable only one copy use by all
    collage_name = "mvp"

    # constructor can take optional arg. also
    def __init__(self, name='', rollno=None, mark=0):
        # constructor this will execute every time when you create obj but class methods will execut when they called only
        # this are instance veriable init. of obj to provide value to instance
        # veriable
        self.name = name
        # inside class we can call this with self and out side of class
        # instance vriable call
        self.rollno = rollno
        self.mark = mark  # call using ref. like s.rollno
        Student.div = "a"  # we can call static veriable inside constructor also using class name

    def student(self):  # function declear inside a class that function call methods
        a = 10  # this is local veriable
        print(a)
        # inside instance method by using class name we can create static
        # veriable
        Student.count = 100

    @classmethod
    def data(cls):
        cls.f = 60
        # inside class method by using class name or class veriable we can
        # declear static veriable
        Student.town = "nsk"

    @staticmethod
    def meta():
        # inside static method using class name we can declear static veriable
        Student.area = "nsk_road"


# physical existance of class called obj  here s is ref. veriable
# Studeent() obj
s = Student("pav", 7, 80)
s.city = 'nsk'  # we can add new instance veriable outside of class using ref. veriable
print(s.collage_name)
del s.mark  # we can delete intance veriable using del and ref. veriable
# if we change the static veriable it will change for all
Student.collage_name = "pvg"
# static veriable recommented to call with class name
print(Student.collage_name)
# help(Student)
# allows you to see all the instance variables and their current values.
print(s.__dict__)
# print(Student.__dict__)
Student.data()
Student.meta()
# outsid of class using class name we can declear static veriable
Student.park = "gandhi"
print(Student.__dict__)
