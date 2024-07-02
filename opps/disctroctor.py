import time
class test():
    def __init__(self):
        print("init constructor")
        
    def __del__(self):
        print("init disctructor")
        
t = test()
t1 = t
t2 = t1
t3= t2
del t1
time.sleep(0.1)
print("obj not yet distroyed after del t1")
#del t2
time.sleep(0.1)
print("obj not yet distroyed after del t2")
#del t3
time.sleep(0.1)
