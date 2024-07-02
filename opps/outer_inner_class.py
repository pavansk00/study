class outer():
    def m1(self):
        print("outer class")
    class inner():
        def m2(self):
            print("inner class")

o = outer()
o.m1()

i = o.inner()
i.m2()
b = outer().inner()
b.m2()
outer().inner().m2()