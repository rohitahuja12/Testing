from dataclasses import dataclass
from typing import Callable
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from itertools import takewhile
from time import sleep

@dataclass
class Action:
    delay: int
    run: Callable

@dataclass
class ScheduledAction(Action):
    runAt: datetime


def scheduleMany(actions, startTime):

    def schedule(a, t):
        return ScheduledAction(
            delay = a.delay,
            run = a.run,
            runAt = t + timedelta(seconds=a.delay)
        )

    scheduledActions = [schedule(a,startTime) for a in actions]

    return scheduledActions

    
def play(actions, max_workers=8):
    sortedActions = sorted(actions, key=lambda a: a.runAt)

    # really janky cross-thread exception handling
    exception = None
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        while sortedActions:
            now = datetime.now()
            dueActions = list(takewhile(lambda a: a.runAt < now, sortedActions))
            sortedActions = sortedActions[len(dueActions):]
            for a in dueActions:
                def do(f):
                    def _inner():
                        nonlocal exception
                        try:
                            f()
                        except Exception as e:
                            print(f'Exception in player thread! {e}')
                            exception = e
                    return _inner
                pool.submit(do(a.run))
            sleep(0)
    if exception != None:
        raise exception

def playNow(actions, max_workers=8):
    startAt = datetime.now() + timedelta(seconds=0.5) 
    scheduledActions = scheduleMany(actions, startAt)
    play(scheduledActions, max_workers)
