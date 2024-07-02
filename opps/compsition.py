class A:
    a = 10
    def __init__(self, name, rollno, city):
        self.name=name
        self.rollno=rollno
        self.city=city
    
    def display(self):
        print("main class a")

class B:
    def __init__(self, car, price, name):
        self.car = car
        self.price = price
        self.name = name
    def display(self):
        print("this is class b")
        print(f"city name is :{self.name.city}")
a = A("pav", 7, 'nsk')

b= B("thar", 150000, a)

b.display()
