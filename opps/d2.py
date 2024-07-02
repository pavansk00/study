class Emp:
    def __init__(self, enum, ename, esal):
        self.enum = enum
        self.ename = ename
        self.esal = esal
        
    def display(self):
        print(f"emp name is: {self.ename}")
        print(f"emp No is: {self.enum}")
        print(f"emp sal is: {self.esal}")
        
class test:
    def modify(emp):
        """we can modify data of other class and use"""
        emp.esal = emp.esal+1000
        emp.display()
        
emp = Emp(7, 'pav', 100)
test.modify(emp)