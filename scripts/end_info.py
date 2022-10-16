from datetime import datetime as dt


async def end_info_get(member):
    now = dt.now()
    current_date = now.strftime("%d.%m.%Y")
    time_begin_raw = now.strftime("%H:%M")
    time_end_raw = now.strftime("%H:%M")

    temp = open(f"temp/{member}", "rt")
    time_begin_raw = temp.read()
    temp.close()

    dst_temp_get = open(f"temp/dst_{member}", "rt")
    dst_get = dst_temp_get.read()
    dst_temp_get.close()

    return current_date, time_begin_raw, time_end_raw, dst_get
