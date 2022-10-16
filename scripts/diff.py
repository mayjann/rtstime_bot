from datetime import datetime as dt
from math import ceil
import time


raw_minutes = None

async def minutes_make(time_begin_raw, time_end_raw):
    global raw_minutes
    fmt = "%H:%M"
    time_begin = dt.strptime(time_begin_raw, fmt)
    time_end = dt.strptime(time_end_raw, fmt)
    time_begin_tuple = time.mktime(time_begin.timetuple())
    time_end_tuple = time.mktime(time_end.timetuple())
    raw_minutes = int((time_end_tuple - time_begin_tuple) / 60)
    return raw_minutes

async def minutes_round_make():
    raw = raw_minutes
    num_hour = int(raw/60)
    if num_hour < 1:
        minutes_round = ceil(raw / 60) * 60
        return minutes_round
    else:
        minutes_round = ceil(raw / 30) * 30
        return minutes_round
