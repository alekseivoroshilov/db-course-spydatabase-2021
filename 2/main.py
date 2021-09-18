import datetime
import psycopg2
import psycopg2.extras
import random
import argparse
import configparser
import time

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

db = getattr(config, 'db', 'default value if not found')
user = getattr(config, 'user', 'default value if not found')
password = getattr(config, 'password', 'default value if not found')

connection = psycopg2.connect(
    dbname=config.get("postgres", "dbname"),
    user=config.get("postgres", "user"),
    password=config.get("postgres", "password"))

# открытие соединения
# connection = psycopg2.connect(dbname=db, user=user, password=password)

# получение курсора
cursor = connection.cursor()

digits = '0123456789'
letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
en_letters = 'abcdefghijklmnopqrstuvwxyz'

today = datetime.datetime.today()

# Выборки из таблиц по PK, где используется как FK


persons = ()
unit_profiles = ()
operators = ()
packs = ()
missions = ()
agents = ()
mission_results = ()

names_list = open("names.txt", encoding="utf8").readlines()
agent_names_list = open("agent_names.txt", encoding="utf8").readlines()
mission_statuses = ('PLANNING', 'STARTING', 'PERFORMING', 'CANCELLING', 'FINISHED')


def truncate_data():
    cursor.execute("truncate table med_record restart identity cascade;"
                   "truncate table agent_mission restart identity cascade;"
                   "truncate table agent restart identity cascade;"
                   "truncate table loot restart identity cascade;"
                   "truncate table mission_result restart identity cascade;"
                   "truncate table mission restart identity cascade;"
                   "truncate table operator restart identity cascade;"
                   "truncate table unit_profile restart identity cascade;"
                   "truncate table person restart identity cascade;"
                   "truncate table item restart identity cascade;"
                   "truncate table pack restart identity cascade;")


def generate_data(arguments):
    if arguments.truncate is not None and int(arguments.truncate) > 0:
        truncate_data()

    if arguments.person is not None:
        generate_persons(arguments.person)

    generate_med_records()

    if arguments.person is not None:
        generate_operators(arguments.operator)

    if arguments.pack is not None:
        generate_packs(arguments.pack)

    if arguments.mission is not None:
        generate_missions(arguments.mission)

    if arguments.mission_result is not None:
        generate_mission_results(arguments.mission_result)

    if arguments.agent is not None:
        generate_agents(arguments.agent)

    if arguments.agent_mission is not None:
        generate_agent_missions(arguments.agent_mission)

    if arguments.unit_profile is not None:
        generate_unit_profiles(arguments.unit_profile)

    if arguments.item is not None:
        generate_items(arguments.item)

    generate_loots()


def generate_persons(number):
    global persons
    buf = []
    for i in range(int(number)):
        name = random.choice(names_list)
        name = name.replace("\n", "")
        bio = random_string(random.randint(1, 120))
        buf.append(tuple((bio, name), ))
    persons_tuple = tuple(buf)
    query = "INSERT INTO person(bio, name) VALUES(%s, %s)"
    # cursor.executemany(query, persons_tuple)
    psycopg2.extras.execute_batch(cursor, query, persons_tuple)
    cursor.execute('SELECT person_id FROM person')
    persons = cursor.fetchall()


def generate_unit_profiles(number):
    global unit_profiles
    buf = []
    for i in range(int(number)):
        a_exist = bool(random.getrandbits(1))
        o_exist = bool(random.getrandbits(1))
        rnd_agent = random.choice(agents)[0] if a_exist else None
        rnd_operator = random.choice(operators)[0] if (o_exist or not a_exist) else None
        buf.append(tuple((random_string(random.randint(1, 120)), random.randint(1, 5), random.choice(persons)[0],
                          random_date(today - datetime.timedelta(days=99 * 365), today - datetime.timedelta(days=14 * 365)),
                          random_date(today - datetime.timedelta(days=99 * 365), today - datetime.timedelta(days=14 * 365)),
                          rnd_agent, rnd_operator),))
    profiles_tuple = tuple(buf)
    query = "INSERT INTO unit_profile(info, rank, person_id, date_from, date_to, agent_id, operator_id)VALUES" \
            "(%s, %s, %s, %s, %s, %s, %s)"
    # cursor.executemany(query, profiles_tuple)
    psycopg2.extras.execute_batch(cursor, query, profiles_tuple)
    cursor.execute('SELECT unit_profile_id FROM unit_profile')
    unit_profiles = cursor.fetchall()


def generate_med_records():
    buf = []
    for person in persons:
        buf.append(tuple((random_string(random.randint(1, 30)), random_string(random.randint(1, 120)), person[0],
                          random_date(today - datetime.timedelta(days=99 * 365), today - datetime.timedelta(days=14 * 365)),
                          random_date(today - datetime.timedelta(days=99 * 365), today - datetime.timedelta(days=14 * 365))),))
    records_tuple = tuple(buf)
    query = "INSERT INTO med_record(title, info, person_id, date_from, date_to)VALUES" \
            "(%s, %s, %s, %s, %s)"
    # cursor.executemany(query, records_tuple)
    psycopg2.extras.execute_batch(cursor, query, records_tuple)
    cursor.execute('SELECT med_record_id FROM med_record')


def generate_operators(number):
    global operators
    buf = []
    for i in range(int(number)):
        buf.append(tuple((random_string(random.randint(1, 120)), bool(random.getrandbits(1))),))
    operators_tuple = tuple(buf)
    query = "INSERT INTO operator(info, available) VALUES" \
            "(%s, %s)"
    # cursor.executemany(query, operators_tuple)
    psycopg2.extras.execute_batch(cursor, query, operators_tuple)
    cursor.execute('SELECT operator_id FROM operator')
    operators = cursor.fetchall()


def generate_packs(number):
    global packs
    buf = []
    for i in range(int(number)):
        buf.append(tuple((random_string(50), random_string(random.randint(1, 120))),))
    packs_tuple = tuple(buf)
    query = "INSERT INTO pack(name, info) VALUES(%s, %s)"
    # cursor.executemany(query, packs_tuple)
    psycopg2.extras.execute_batch(cursor, query, packs_tuple)
    cursor.execute('SELECT pack_id FROM pack')
    packs = cursor.fetchall()


def generate_missions(number):
    global missions
    buf = []
    for i in range(int(number)):
        buf.append(tuple((random_string(50), random.randint(1, 5),
                          random_string(random.randint(1, 120)), random.choice(operators)[0],
                          random.choice(mission_statuses)),))
    missions_tuple = tuple(buf)
    query = "INSERT INTO mission(name, rank, info, operator_id, mission_status) " \
            "VALUES(%s, %s, %s, %s, %s)"
    # cursor.executemany(query, missions_tuple)
    psycopg2.extras.execute_batch(cursor, query, missions_tuple)
    cursor.execute('SELECT mission_id FROM mission')
    missions = cursor.fetchall()


def generate_agents(number):
    global agents
    buf = []
    for i in range(int(number)):
        buf.append(tuple((random.choice(agent_names_list), random.choice(packs)[0], bool(random.getrandbits(1))),))
    agents_tuple = tuple(buf)
    query = "INSERT INTO agent(name, pack_id, available) VALUES(%s, %s, %s)"
    # cursor.executemany(query, agents_tuple)
    psycopg2.extras.execute_batch(cursor, query, agents_tuple)
    cursor.execute('SELECT agent_id FROM agent')
    agents = cursor.fetchall()


def generate_items(number):
    buf = []
    for i in range(int(number)):
        buf.append(tuple((random_string(50), random_string(random.randint(1, 120)), random.choice(packs)[0]), ))
    items_tuple = tuple(buf)
    query = "INSERT INTO item(name, info, pack_id) VALUES(%s, %s, %s)"
    # cursor.executemany(query, items_tuple)
    psycopg2.extras.execute_batch(cursor, query, items_tuple)
    cursor.execute('SELECT item_id FROM item')


def generate_mission_results(number):
    global mission_results
    buf = []
    temporary = random.randint(0, int(number))
    for mission in missions:
        last_time = randomDate("01-01-1990 00:00:00", "01-01-2021 00:00:00")
        for i in range(temporary):
            buf.append(tuple((mission[0], random_string(random.randint(1, 120)), last_time), ))
            last_time = randomDate(last_time, "01-01-2021 00:00:00")
    results_tuple = tuple(buf)
    query = "INSERT INTO mission_result(mission_id, info, time) VALUES(%s, %s, %s)"
    # cursor.executemany(query, results_tuple)
    psycopg2.extras.execute_batch(cursor, query, results_tuple)
    cursor.execute('SELECT mission_result_id FROM mission_result')
    mission_results = cursor.fetchall()


def generate_agent_missions(number):
    buf = []
    for i in range(int(number)):
        agent = random.choice(agents)
        empty = bool(random.getrandbits(1))
        if empty:
            continue
        agent_id = agent[0]
        mission_id = random.choice(missions)[0]
        info = random_string(random.randint(1, 120))
        date_from = random_date(today - datetime.timedelta(days=99 * 365), today - datetime.timedelta(days=14 * 365))
        date_to = random_date(today - datetime.timedelta(days=99 * 365), today - datetime.timedelta(days=14 * 365))
        buf.append(tuple((agent_id, mission_id, info, date_from, date_to),))
    mission_tuple = tuple(buf)
    query = "INSERT INTO agent_mission(agent_id, mission_id, info, date_from, date_to) " \
            "VALUES(%s, %s, %s, %s, %s)"
    # cursor.executemany(query, mission_tuple)
    psycopg2.extras.execute_batch(cursor, query, mission_tuple)


def generate_loots():
    buf = []
    for mission_result in mission_results:
        l_exist = random.random() < 0.15
        if l_exist:
            mission_result_id = mission_result[0]
            rank = random.randint(1, 5)
            info = random_string(random.randint(1, 120))
            name = random_string(50)
            buf.append(tuple((mission_result_id, rank, info, name), ))
    loot_tuple = tuple(buf)
    query = "INSERT INTO loot(mission_result_id, rank, info, name) VALUES(%s, %s, %s, %s)"
    # cursor.executemany(query, loot_tuple)
    psycopg2.extras.execute_batch(cursor, query, loot_tuple)


def random_date(start_date, end_date):
    date_delta = end_date - start_date
    days_delta = date_delta.days
    days_random = random.randrange(days_delta)
    r_date = start_date + datetime.timedelta(days=days_random)
    return r_date


def random_string(length):
    str = ''
    for i in range(int(length)):
        str += random.choice(letters)
    return str


def random_number(length):
    num = ''
    for i in range(int(length)):
        num += random.choice(digits)
    return num


def randomDate(start, end):
    frmt = "%d-%m-%Y %H:%M:%S"

    stime = time.mktime(time.strptime(start, frmt))
    etime = time.mktime(time.strptime(end, frmt))

    ptime = stime + random.random() * (etime - stime)
    dt = datetime.datetime.fromtimestamp(time.mktime(time.localtime(ptime))).strftime(frmt)
    return dt


if __name__ == '__main__':
    args = argparse.ArgumentParser(description="Details of data generation")

    args.add_argument('--person', action="store", dest="person")
    args.add_argument('--operator', action="store", dest="operator")
    args.add_argument('--pack', action="store", dest="pack")
    args.add_argument('--mission', action="store", dest="mission")
    args.add_argument('--mission_result', action="store", dest="mission_result")
    args.add_argument('--agent_mission', action="store", dest="agent_mission")
    args.add_argument('--agent', action="store", dest="agent")
    args.add_argument('--unit_profile', action="store", dest="unit_profile")
    args.add_argument('--item', action="store", dest="item")
    args.add_argument('--truncate', action="store", dest="truncate")

    arguments = args.parse_args()

    generate_data(arguments)

    # закрытие соединения
    connection.commit()
    connection.close()