import datetime

async def format_time(manual_first_time_raw):
    time_obj_raw = datetime.datetime.strptime(manual_first_time_raw, '%H:%M')
    time_obj = time_obj_raw.strftime('%H:%M')
    return time_obj
