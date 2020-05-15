from threading import Thread, local
import asyncio
from functools import partial
import time
import datetime
import random

random.seed(0)

def start_loop(loop):
    loop.run_forever()

loop0 = asyncio.new_event_loop()
loop1 = asyncio.new_event_loop()
loop2 = asyncio.new_event_loop()

t0 = Thread(name="t0", daemon=True, target=start_loop, args=(loop0,))
t0.start()

t1 = Thread(name="t1", daemon=True, target=start_loop, args=(loop1,))
t1.start()

t2 = Thread(name="t2", daemon=True, target=start_loop, args=(loop2,))
t2.start()

threads_local = local()

def get_current_time():
    return str(datetime.datetime.now())[:-4]

def loop0_send(m, n):
    k = random.randint(1, m)
    data = random.choices(list(range(m)), k=k)
    print(f'{get_current_time()} 0 -> 1: {data}')
    loop1.call_soon_threadsafe(partial(loop1_receive, data))
    time.sleep(m / 4)
    if n != 0:
        loop0.call_soon_threadsafe(partial(loop0_send, m, n-1))
    else:
        print(f'{get_current_time()} 0: no data anymore')

def loop1_receive(data):
    # state 
    # 0: waiting for more data from loop0 to send to loop2
    # 1: saving more data from loop0 and waiting for loop2 to finish
    if 'state' not in threads_local.__dict__.keys():
        # init
        threads_local.state = 1
        threads_local.data = []
        print(f'{get_current_time()} 1 -> 2: {data}')
        loop2.call_soon_threadsafe(partial(loop2_receive, data))
        print(f'{get_current_time()} 1: data: {threads_local.data}')
    elif threads_local.state == 0:
        threads_local.state = 1
        print(f'{get_current_time()} 1 -> 2: {data}')
        loop2.call_soon_threadsafe(partial(loop2_receive, data))
        print(f'{get_current_time()} 1: data: {threads_local.data}')
    else:
        threads_local.data += data
        print(f'{get_current_time()} 1: data: {threads_local.data}')
    
def loop1_asked():
    if threads_local.state == 1:
        if threads_local.data == []:
            print(f'{get_current_time()} 1: currently no data')
            threads_local.state = 0
        else:
            data = threads_local.data
            threads_local.data = []
            print(f'{get_current_time()} 1 -> 2: {data}')
            loop2.call_soon_threadsafe(partial(loop2_receive, data))
            print(f'{get_current_time()} 1: data: {threads_local.data}')

def loop2_receive(data):
    time_spent = random.random() * len(data)
    time.sleep(time_spent)
    print(f'{get_current_time()} sum: {sum(data)} time_spent: {time_spent}')
    print(f'{get_current_time()} 2 -> 1: asking for data')
    loop1.call_soon_threadsafe(loop1_asked)

def start():
    time.sleep(0.5)
    print('')
    loop0.call_soon_threadsafe(partial(loop0_send, 10, 10))

t = Thread(target=start)
t.start()

breakpoint()
