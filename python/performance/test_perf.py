import time
#@profile
def do_stuff():
    for i in range(100000000):
        i=+1

start_time = time.time()

print("aaaaaaaaaaaaa")
do_stuff()
end_time= start_time - time.time()
print("total elaps time %s ",end_time)
'''
1
python -m profile .\test_perf.py
profiler may take some time to execute but method wise we will get which fun req how much time
2
python -m cProfile .\test_perf.py
this is cprofiler is fast than normal profiler

-----but profiler is slow and not supporting to multithreading and memory consuption also not able to 
see 
----there are 3rd party profiler like py-spy , line-profiler, momory profiler

line-profiler ======>1.install line-profiler 
                    2.kernprof -lv test_perf.py then you get complete data
memory profiler ========> 1. install matplotlib, memory_profiler
                      2.mprof run test_perf.py
                      3.mprof plot --output mprofile_20240913151004.dat
snakeviz ============> 1. pip install snakeviz
'''