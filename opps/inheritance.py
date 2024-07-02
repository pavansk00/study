class A:
    pav = 10
    def __init__(self):None
    
    def display(self):
        print("main class a")
        print(A.pav)

class B(A):
    def __init__(self):None
    def display1(self):
        print("this is class b")
        
b = B()
b.display()