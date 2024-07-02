"""The super keyword in Python is used to call methods from a parent class. It is commonly used in the context of inheritance to ensure that the derived class can access and extend the functionality of its base class.

Here are some key points about super:

Basic Usage: super() returns a temporary object of the superclass that allows you to call its methods.
Syntax: It is typically used in the __init__ method of a class to call the __init__ method of its superclass.
Multiple Inheritance: super is especially useful in multiple inheritance scenarios, where it helps in maintaining the Method Resolution Order (MRO) and ensures that each parent class is only initialized once.
"""
 
# class A:

#     def __init__(self):None
#     p = 10
#     def amain(self):
#         print("main class")
#         print(A.p)
        
        
# class B(A):
#     p = 11
#     def __init__(self):None
    
#     def bdisplay(self):
#         print("child")
#         super().amain()
    
# x = B()
# x.bdisplay()


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        
    def display(self):
        print(f"name is {self.name} and age is {self.age} this is main class")
        
class su(Person):
    def __init__(self, name, age, eno, esal):
        super().__init__(name, age)
        self.eno = eno
        self.esal = esal
    
    def work(self):
        print(f"this is child class")
        print(self.name, self.age,self.eno,self.esal)
        
p = su("pav", 28, 7, 73000)

p.display()
p.work()
        
#only in super instance veriable not use instance methods class varialbes are used
        