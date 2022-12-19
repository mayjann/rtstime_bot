import pymysql
import configparser


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

сon = pymysql.connect(host='127.0.0.1',
                    user = config.get('mysql', 'user'),
                    password = config.get('mysql', 'password'),
                    db = 'RTSTH_DB',
                    charset = 'utf8mb4',
                    cursorclass = pymysql.cursors.DictCursor)
cur = сon.cursor()



# Функция записи в базу данных информации при начале работы.
async def input(full_name, userid, user_dst, time_begin_raw, datejob):
    сon.ping(reconnect=True)
    query = """
    INSERT INTO default_table(
    user_full_name,
    user_id,
    destination,
    time_of_begin,
    time_of_end,
    date_job) values(%s, %s, %s, %s, %s, %s)
    """

    cur.execute(query, (full_name, userid, user_dst, time_begin_raw, None, datejob))
    сon.commit()

# Функция внесения записи в существующую строку базы данных при завершении работы.
async def update(time_end_raw, minutes_raw, minutes_round, userid):
    сon.ping(reconnect=True)
    query = """ UPDATE default_table SET time_of_end = %s, raw_minutes = %s, round_minutes = %s 
    WHERE user_id LIKE %s AND time_of_end IS NULL"""

    cur.execute(query, (time_end_raw, minutes_raw, minutes_round, userid))
    сon.commit()

# Функция внесения записи в существующую строку базы данных при завершении работы.
def update_minutes(minutes_raw, minutes_round, out_time_end, userid):
    сon.ping(reconnect=True)
    query = """UPDATE default_table set raw_minutes = %s AND round_minutes = %s WHERE user_id LIKE %s AND time_of_end = %s"""

    cur.execute(query, (minutes_raw, minutes_round, userid, out_time_end))
    сon.commit()

# Функция записи идентификатора сообщения в базу данных.
async def update_alt_msg(userid, message_to_delete):
    сon.ping(reconnect=True)
    query = """UPDATE default_table set alt_message_id = %s WHERE user_id LIKE %s AND alt_message_id IS NULL"""

    cur.execute(query, (message_to_delete, userid))
    сon.commit()

# Функция получения идентификатора сообщения из базы данных.
def get_alt_msg(userid, date_today):
    сon.ping(reconnect=True)
    query = """SELECT alt_message_id FROM default_table WHERE user_id LIKE %s AND date_job LIKE %s"""


    cur.execute(query, (userid, date_today))
    for row in cur:
        message_to_delete = row['alt_message_id']
        return message_to_delete

    сon.commit()

# Функция записи идентификатора сообщения в базу данных.
async def update_msg(userid, message_to_delete):
    сon.ping(reconnect=True)
    query = """UPDATE default_table set message_id = %s WHERE user_id LIKE %s AND message_id IS NULL"""

    cur.execute(query, (message_to_delete, userid))
    сon.commit()

# Функция получения идентификатора сообщения из базы данных.
def get_msg(userid):
    сon.ping(reconnect=True)
    query = """SELECT message_id FROM default_table WHERE user_id LIKE %s AND time_of_end IS NULL"""

    cur.execute(query, (userid))
    for row in cur:
        message_to_delete = row['message_id']
        return message_to_delete

    сon.commit()

# Функция получения информации из базы данных.
async def output(userid):
    сon.ping(reconnect=True)
    query = """SELECT * FROM default_table WHERE user_id LIKE %s AND time_of_end IS NULL"""

    cur.execute(query, (userid))
    for row in cur:

        out_name = row['user_full_name']
        out_id = row['user_id']
        out_destination = row['destination']
        out_time_begin = row['time_of_begin']
        out_date = row['date_job']
        return out_name, out_id, out_destination, out_time_begin, out_date
    сon.commit()

# Функция получения информации из базы данных для проверки опоздания.
async def output_begin(userid, datejob):
    сon.ping(reconnect=True)
    query = """SELECT * FROM default_table WHERE user_id LIKE %s AND date_job LIKE %s"""
    data = cur.execute(query, (userid, datejob))
    сon.commit()

    return data
