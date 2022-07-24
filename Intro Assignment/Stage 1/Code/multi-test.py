import multiprocessing
from multiprocessing import Process, Queue
import random


def rand_num():
    num = random.random()
    queue.put(num)
    print(num)


queue = multiprocessing.SimpleQueue()

if __name__ == "__main__":
    queue = Queue()

    processes = [Process(target=rand_num, args=()) for x in range(4)]

    """ for p in processes:
        p.start()

    for p in processes:
        p.join()
 """
for _ in range(4):
    print(queue.get())
