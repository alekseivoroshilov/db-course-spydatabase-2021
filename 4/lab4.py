import configparser

import psycopg2
import random
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import datetime

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

work_flag = 0  # operating mode, 1 for database answer time / queries per second relation
# 0 for database answer time / threads number relation
threads_min = 1     # threads number at which modeling with threads will start
threads_max = 20    # threads number at which modeling with threads will end
const_threads = 5   # threads number at which modeling with queries per second will run
queries_min = 10    # queries number at which modeling with queries per second will start
queries_max = 1000   # queries number at which modeling with queries per second will end
const_queries = 800     # queries number at which modeling with threads will run
seconds = 20        # seconds for modeling with queries per second

mission_status_list = ('PLANNING', 'STARTING', 'PERFORMING', 'CANCELLING', 'FINISHED')  # db enums
dates_for_second = pd.date_range('1925-01-01', '1930-01-01', freq='M')
dates_for_fifth = pd.date_range('2002-01-02', '2007-01-01', freq='M')

connection = psycopg2.connect(
    dbname=config.get("postgres", "dbname"),
    user=config.get("postgres", "user"),
    password=config.get("postgres", "password"))
cursor_begin = connection.cursor()
cursor_begin.execute('SELECT name FROM person;')
names = cursor_begin.fetchall()
cursor_begin.execute('SELECT name FROM agent;')
agent_names = cursor_begin.fetchall()
connection.close()

threads = []
results = []

prepare = False  # Another global var. If true -> use for "optimized with indices + prepared queries"

queries = {
    1: '''SELECT agent.agent_id, agent.name, person.name, pack.name, unit_profile.rank 
          FROM agent 
          JOIN pack ON pack.pack_id = agent.pack_id 
          JOIN unit_profile ON unit_profile.agent_id = agent.agent_id 
          JOIN person ON person.person_id = unit_profile.person_id 
          WHERE person.name = (%s);''',

    2: '''SELECT "operator".operator_id, person.name, med_record.title, med_record.date_from, med_record.date_to 
          FROM "operator" 
          JOIN unit_profile ON "operator".operator_id = unit_profile.operator_id 
          JOIN person ON person.person_id = unit_profile.person_id 
          JOIN med_record ON person.person_id = med_record.person_id 
          WHERE med_record.date_to < (%s);''',

    3: '''SELECT agent.name, pack.name as pack, item.name as item 
          FROM agent 
          JOIN pack ON agent.pack_id = pack.pack_id 
          JOIN item ON pack.pack_id = item.pack_id 
          WHERE agent.name = (%s);''',

    4: '''SELECT mission.mission_id, mission.name, mission.info, "operator".info as operator_info, mission_result.info 
            as mission_res 
          FROM mission 
          JOIN "operator" ON mission.operator_id = "operator".operator_id 
          JOIN mission_result ON mission.mission_id = mission_result.mission_id 
          WHERE mission_result."time" between %(time_from)s and %(time_to)s;''',

    5: '''SELECT agent_mission.agent_mission_id, agent.name, mission.name, agent_mission.date_from,
          agent_mission.date_to
          FROM agent_mission
          JOIN agent ON agent.agent_id = agent_mission.agent_id
          JOIN mission ON mission.mission_id = agent_mission.mission_id
          JOIN "operator" ON "operator".operator_id = mission.operator_id
          WHERE agent_mission.date_to > (%s);'''
}

queries_prepared = {
    1: "EXECUTE query1 (%s);",
    2: "EXECUTE query2 (%s);",
    3: "EXECUTE query3 (%s);",
    4: "EXECUTE query4 (%(time_from)s,%(time_to)s);",
    5: "EXECUTE query5 (%s);",
}


# Function, that creates indices
def optimize_create_indexes():
    connect = psycopg2.connect(
        dbname=config.get("postgres", "dbname"),
        user=config.get("postgres", "user"),
        password=config.get("postgres", "password"))
    cursor = connect.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS i1 ON person(name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS i2 ON med_record(date_to);")
    cursor.execute("CREATE INDEX IF NOT EXISTS i3 ON agent(name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS i4 ON mission_result(time);")
    cursor.execute("CREATE INDEX IF NOT EXISTS i5 ON agent_mission(date_to);")
    # cursor.execute("CREATE INDEX IF NOT EXISTS i6 ON agent_mission(date_from);")
    # cursor.execute("CREATE INDEX IF NOT EXISTS i7 ON agent_mission(date_to);")
    connect.commit()
    connect.close()


def prepare_queries(thread_cursor):
    thread_cursor.execute(
        "PREPARE query1 (varchar(50)) AS SELECT agent.agent_id, agent.name, person.name, pack.name, unit_profile.rank "
        "FROM agent "
        "JOIN pack ON pack.pack_id = agent.pack_id "
        "JOIN unit_profile ON unit_profile.agent_id = agent.agent_id "
        "JOIN person ON person.person_id = unit_profile.person_id "
        "WHERE person.name = $1;"
    )
    thread_cursor.execute(
        "PREPARE query2 (date) AS SELECT \"operator\".operator_id, person.name, "
        "med_record.title, med_record.date_from, med_record.date_to "
        "FROM \"operator\" "
        "JOIN unit_profile ON \"operator\".operator_id = unit_profile.operator_id "
        "JOIN person ON person.person_id = unit_profile.person_id "
        "JOIN med_record ON person.person_id = med_record.person_id "
        "WHERE med_record.date_to < $1;"
    )
    thread_cursor.execute(
        "PREPARE query3 (varchar(50)) AS SELECT agent.name, pack.name as pack, item.name as item "
        "FROM agent "
        "JOIN pack ON agent.pack_id = pack.pack_id "
        "JOIN item ON pack.pack_id = item.pack_id "
        "WHERE agent.name = $1;"
    )
    thread_cursor.execute(
        "PREPARE query4 (timestamp, timestamp) AS SELECT mission.mission_id, mission.name, "
        "mission.info, \"operator\".info as operator_info, mission_result.info as mission_res "
        "FROM mission "
        "JOIN \"operator\" ON mission.operator_id = \"operator\".operator_id "
        "JOIN mission_result ON mission.mission_id = mission_result.mission_id "
        "WHERE mission_result.\"time\" between $1 and $2;"
    )
    thread_cursor.execute(
        "PREPARE query5 (date) AS SELECT agent_mission.agent_mission_id, agent.name, "
        "mission.name, agent_mission.date_from, "
        "agent_mission.date_to "
        "FROM agent_mission "
        "JOIN agent ON agent.agent_id = agent_mission.agent_id "
        "JOIN mission ON mission.mission_id = agent_mission.mission_id "
        "JOIN \"operator\" ON \"operator\".operator_id = mission.operator_id "
        "WHERE agent_mission.date_to > $1;"
    )


def execute_random_query(thread_cursor):
    # random request with query
    global prepare

    query_number = random.randint(1, len(queries))
    if query_number == 1:
        args = [random.choice(names)]
    elif query_number == 2:
        args = [random.choice(dates_for_second)]
    elif query_number == 3:
        args = [random.choice(agent_names)]
    elif query_number == 4:
        args = {"time_from": datetime.datetime(random.randint(2013, 2016), random.randint(1, 6), 4, 0, 5, 23),
                "time_to": datetime.datetime(random.randint(2016, 2019), random.randint(6, 12), 4, 0, 5, 23)}
    elif query_number == 5:
        args = [random.choice(dates_for_fifth)]
    else:
        print('wrong query number')
        return

    if prepare:
        thread_cursor.execute("EXPLAIN ANALYSE " + queries_prepared[query_number], args)
    else:
        thread_cursor.execute("EXPLAIN ANALYSE " + queries[query_number], args)

    query_result = thread_cursor.fetchall()
    exec_time = float(query_result[-1][0].split()[2]) + float(query_result[-2][0].split()[2])

    return exec_time


def rnd_date(start_year, end_year):
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date = datetime.date(year, month, day)
    return date


def run_modeling_with_queries(x, y):
    for thread in range(const_threads):
        new_thread = ConstantQueryThread(queries_min, queries_max, seconds)
        new_thread.start()
        threads.append(new_thread)

    for t in threads:
        t.join()

    threads.clear()

    print('RESULTS', results)

    for second in range(seconds):
        queries_sum = 0
        threads_sum = 0
        avg_time_sum = 0
        for element in results:
            if element[0] == second:
                queries_sum += element[1]
                threads_sum += 1
                avg_time_sum += element[2]
        if len(x) == 0 or queries_sum > x[-1]:  # graph check
            x.append(queries_sum)
            y.append(avg_time_sum / threads_sum)

    results.clear()

    print('x:', x)
    print('y:', y)


def run_modeling_with_threads(x, y):
    for step in range(threads_min, threads_max + 1):
        for thread in range(step):
            new_thread = DynamicQueryThread(const_queries)
            new_thread.start()
            threads.append(new_thread)

        for t in threads:
            t.join()

        threads.clear()

        print('RESULTS', results)

        x.append(len(results))
        y.append(sum(results) / len(results))

        results.clear()

    print('x:', x)
    print('y:', y)


def build_answer_queries_relation():
    # Dependence of the database response time on the number of requests.

    global prepare

    # non-optimized
    x1 = []
    y1 = []
    run_modeling_with_queries(x1, y1)

    # optimized with indices
    optimize_create_indexes()
    x2 = []
    y2 = []
    run_modeling_with_queries(x2, y2)

    # optimized with indices + prepared queries
    prepare = True
    x3 = []
    y3 = []
    run_modeling_with_queries(x3, y3)

    fig, ax = plt.subplots()
    ax.plot(x1, y1, label='non-optimized')
    ax.plot(x2, y2, label='optimized with indices')
    ax.plot(x3, y3, label='optimized with indices + prepared queries')
    ax.grid(which='major', linewidth=0.5, color='k')
    ax.legend()
    plt.xlabel('Number of requests per second from all threads')
    plt.ylabel('Average response time for a single request, мс')
    plt.title(f'''Dependence of the database response time on the number of requests
    Number of threads: {const_threads}''')
    plt.show()


def build_answer_threads_relation():
    # Dependence of the database response time on the number of threads.

    global prepare

    # non-optimized
    x1 = []
    y1 = []
    run_modeling_with_threads(x1, y1)

    # optimized with indices
    optimize_create_indexes()
    x2 = []
    y2 = []
    run_modeling_with_threads(x2, y2)

    # optimized with indices + prepared queries
    prepare = True
    x3 = []
    y3 = []
    run_modeling_with_threads(x3, y3)

    fig, ax = plt.subplots()
    ax.plot(x1, y1, label='non-optimized')
    ax.plot(x2, y2, label='optimized with indices')
    ax.plot(x3, y3, label='optimized with indices + prepared queries')
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.minorticks_on()
    ax.grid(which='major', linewidth=0.5, color='k')
    ax.legend()
    plt.xlabel('Number of threads')
    plt.ylabel('Average response time per request, ms')
    plt.title('Dependence of the database response time on the number of threads ')
    plt.style.use('seaborn-whitegrid')
    plt.show()


class ConstantQueryThread(threading.Thread):
    """Поток, выполняющийся заданное время и старающийся выполнить переданное ему количество запросов в секунду"""

    def __init__(self, q_min, q_max, work_seconds):
        super().__init__()
        self.work_seconds = work_seconds
        self.queries_min = q_min
        self.queries_max = q_max
        self.query_con = psycopg2.connect(
            dbname=config.get("postgres", "dbname"),
            user=config.get("postgres", "user"),
            password=config.get("postgres", "password"))
        self.query_cur = self.query_con.cursor()

    def run(self):
        global prepare
        print(f'\nOpened DB connection in thread {threading.current_thread().ident}')
        if prepare:
            prepare_queries(self.query_cur)
            self.query_con.commit()
        step_length = (self.queries_max - self.queries_min) // (seconds - 1)
        for second, curr_q_num in enumerate(range(self.queries_min, self.queries_max + 1, step_length)):
            thread_results = []
            start_time = time.time()
            for query in range(curr_q_num):
                thread_results.append(execute_random_query(self.query_cur))
                if time.time() - start_time >= 1:  # если секунда вышла - перестаём делать запросы
                    break

            if time.time() - start_time <= 1:  # ждём остаток секунды, если она ещё не вышла, а цикл закончился
                time.sleep(1 - (time.time() - start_time))

            queries_amount = len(thread_results)
            avg_time = sum(thread_results) / queries_amount  # среднее время выполнения запроса
            results.append((second, queries_amount, avg_time))

        self.query_con.close()
        print(f'Closed DB connection in thread {threading.current_thread().ident}')


class DynamicQueryThread(threading.Thread):
    # The thread, which executes planned number of requests
    def __init__(self, q_amount):
        super().__init__()
        self.queries_amount = q_amount
        self.query_con = psycopg2.connect(
            dbname=config.get("postgres", "dbname"),
            user=config.get("postgres", "user"),
            password=config.get("postgres", "password"))
        self.query_cur = self.query_con.cursor()

    def run(self):
        global prepare
        print(f'\nOpened DB connection in thread {threading.current_thread().ident}')
        if prepare:
            prepare_queries(self.query_cur)
            self.query_con.commit()
        thread_results = []
        for query in range(self.queries_amount):
            thread_results.append(execute_random_query(self.query_cur))

        queries_amount = len(thread_results)
        avg_time = sum(thread_results) / queries_amount  # среднее время выполнения запроса
        results.append(avg_time)

        self.query_con.close()
        print(f'Closed DB connection in thread {threading.current_thread().ident}')


def drop_indexes():
    connect = psycopg2.connect(
        dbname=config.get("postgres", "dbname"),
        user=config.get("postgres", "user"),
        password=config.get("postgres", "password"))
    cursor = connect.cursor()
    cursor.execute("DROP INDEX IF EXISTS i1;")
    cursor.execute("DROP INDEX IF EXISTS i2;")
    cursor.execute("DROP INDEX IF EXISTS i3;")
    cursor.execute("DROP INDEX IF EXISTS i4;")
    cursor.execute("DROP INDEX IF EXISTS i5;")
    connect.commit()
    connect.close()


if work_flag:
    drop_indexes()
    build_answer_queries_relation()
else:
    drop_indexes()
    build_answer_threads_relation()
