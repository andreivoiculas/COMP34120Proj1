from multiprocessing import Process, Queue
import os
import time

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def f(name, queue):
    info('function f')
    time.sleep(10)
    queue.put(name)
    #print('hello', name)

if __name__ == '__main__':
    info('main line')
    queue = Queue()
    for i in range(10):
      p = Process(target=f, args=(i,queue))
      p.start()

    p.join()

    #time.sleep(10)
    while not queue.empty():
      print(queue.get())
    # w = Process(target=f, args=('matei',))
    # p.start()
    # #p.join()
    # w.start()
