from datetime import datetime as dt


async def begin_info_get(member, dst):
    now = dt.now()
    time_begin_raw = now.strftime("%H:%M")

    temp = open(f"temp/{member}", "wt")
    temp.write(time_begin_raw)
    temp.close()

    dst_temp = open(f"temp/dst_{member}", "wt")
    dst_temp.write(dst)
    dst_temp.close()
