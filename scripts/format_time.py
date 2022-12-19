import datetime

async def format_time(manual_first_time_raw):
    time_obj_raw = datetime.datetime.strptime(manual_first_time_raw, '%H:%M')
    manual_first_time = time_obj_raw.strftime('%H:%M')
    return manual_first_time

async def format_time(manual_second_time_raw):
    time_obj_raw = datetime.datetime.strptime(manual_second_time_raw, '%H:%M')
    manual_second_time = time_obj_raw.strftime('%H:%M')
    return manual_second_time
