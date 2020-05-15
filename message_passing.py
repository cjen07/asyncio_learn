from threading import Thread
import asyncio
from functools import partial
import time

def start_loop(loop):
    loop.run_forever()

loop0 = asyncio.new_event_loop()
loop1 = asyncio.new_event_loop()
loop_main = asyncio.new_event_loop()

t0 = Thread(name="t0", daemon=True, target=start_loop, args=(loop0,))
t0.start()

t1 = Thread(name="t1", daemon=True, target=start_loop, args=(loop1,))
t1.start()

def collatz(n):
    d, m = divmod(n, 2)
    if m == 0:
        return d
    else:
        return 3 * n + 1

def main_message():
    print('done')
    exit(0)

def loop0_message(n):
    m = collatz(n)
    print(f'loop0: {n} -> {m}')
    if m != 1:
        time.sleep(0.5)
        loop1.call_soon_threadsafe(partial(loop1_message, m))
    else:
        loop_main.call_soon_threadsafe(main_message)

def loop1_message(n):
    m = collatz(n)
    print(f'loop1: {n} -> {m}')
    if m != 1:
        time.sleep(0.5)
        loop0.call_soon_threadsafe(partial(loop0_message, m))
    else:
        loop_main.call_soon_threadsafe(main_message)

loop_and_messaging = {
    0: (loop0, loop0_message),
    1: (loop1, loop1_message)
}

def start_messaging(i, n):
    loop, messaging = loop_and_messaging[i]
    loop.call_soon_threadsafe(partial(messaging, n))

def start():
    print(t0.is_alive(), t1.is_alive())
    start_messaging(1, 20)

start()
loop_main.run_forever()
