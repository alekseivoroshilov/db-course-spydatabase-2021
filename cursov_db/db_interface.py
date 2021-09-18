import psycopg2
# import random
# import argparse
import configparser
import datetime

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

connection = psycopg2.connect(
    dbname=config.get("postgres", "dbname"),
    user=config.get("postgres", "user"),
    password=config.get("postgres", "password"))

cursor = connection.cursor()
connection.autocommit = True


def truncate_db():
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


def get_agents():
    query = "SELECT name FROM agent"
    cursor.execute(query)
    agents_t = cursor.fetchall()
    agents = list(sum(agents_t, ()))
    agents_str = ""
    for agent in agents:
        agents_str += agent
        agents_str += '\n'
    return agents_str


def get_operators():
    query = "SELECT operator_id, info, available FROM operator"
    cursor.execute(query)
    some_list = cursor.fetchall()
    elements = list(sum(some_list, ()))
    string = format_operators(elements)
    return string


def show_agents():
    query = "SELECT agent_id, name, available, pack_id FROM agent"
    cursor.execute(query)
    some_list = cursor.fetchall()
    something = list(sum(some_list, ()))
    string = format_agents(something)
    return string


def show_packs():
    query = "SELECT pack_id, name, info FROM pack ORDER BY pack_id DESC"
    cursor.execute(query)
    some_list = cursor.fetchall()
    something = list(sum(some_list, ()))
    string = format_pack(something)
    return string


def show_agents_sorted_by_names():
    query = "SELECT agent_id, name, available, pack_id FROM agent ORDER BY name"
    cursor.execute(query)
    some_list = cursor.fetchall()
    something = list(sum(some_list, ()))
    string = format_agents(something)
    return string


def show_agents_without_pack():
    query = "SELECT agent_id, name, available, pack_id FROM agent WHERE pack_id is NULL"
    cursor.execute(query)
    some_list = cursor.fetchall()
    if not some_list:
        return -1
    something = list(sum(some_list, ()))
    string = format_agents(something)
    return string


def show_mr_last10():
    query = "SELECT mission_result_id, mission_id, info, time FROM mission_result ORDER BY time DESC LIMIT 10"
    cursor.execute(query)
    some_list = cursor.fetchall()
    if not some_list:
        return -1
    something = list(sum(some_list, ()))
    string = format_mr(something)
    return string


def show_mr_from_beginning():
    query = "SELECT mission_result_id, mission_id, info, time FROM mission_result ORDER BY time ASC"
    cursor.execute(query)
    some_list = cursor.fetchall()
    if not some_list:
        return -1
    something = list(sum(some_list, ()))
    string = format_mr(something)
    return string


def show_missions_without_operator():
    query = '''SELECT mission_id, name, rank, info, operator_id, mission_status 
            FROM mission WHERE operator_id IS NULL'''
    cursor.execute(query)
    missions_t = cursor.fetchall()
    if not missions_t:
        return -1
    missions = list(sum(missions_t, ()))
    missions_str = format_missions(missions)
    return missions_str


def show_missions_sorted_by_rank():
    query = '''SELECT mission_id, name, rank, info, operator_id, mission_status 
            FROM mission ORDER BY rank'''
    cursor.execute(query)
    missions_t = cursor.fetchall()
    if not missions_t:
        return -1
    missions = list(sum(missions_t, ()))
    missions_str = format_missions(missions)
    return missions_str


def show_missions_sorted_by_names():
    query = '''SELECT mission_id, name, rank, info, operator_id, mission_status 
            FROM mission ORDER BY name'''
    cursor.execute(query)
    missions_t = cursor.fetchall()
    if not missions_t:
        return -1
    missions = list(sum(missions_t, ()))
    missions_str = format_missions(missions)
    return missions_str


def show_items_without_pack():
    query = '''SELECT item_id, name, info, pack_id
                FROM item WHERE pack_id is NULL'''
    cursor.execute(query)
    elements = cursor.fetchall()
    if not elements:
        return -1
    some_list = list(sum(elements, ()))
    string = format_items(some_list)
    return string


def show_items_sorted_by_names():
    query = '''SELECT item_id, name, info, pack_id
                    FROM item ORDER BY name'''
    cursor.execute(query)
    elements = cursor.fetchall()
    if not elements:
        return -1
    some_list = list(sum(elements, ()))
    string = format_items(some_list)
    return string


def get_missions():
    query = '''SELECT mission.name, mission.rank, mission.operator_id, person.name, mission_status, mission.info 
        FROM mission
        JOIN operator ON operator.operator_id = mission.operator_id
        JOIN unit_profile ON operator.operator_id = unit_profile.operator_id
        JOIN person ON person.person_id = unit_profile.person_id
        GROUP BY mission.name, mission.rank, mission.operator_id, person.name, mission_status, mission.info'''
    cursor.execute(query)
    missions_t = cursor.fetchall()
    missions = list(sum(missions_t, ()))
    missions_str = format_missions_with_person_operator(missions)
    return missions_str


def get_mission_by_operator_id(operator_id):
    name_row = tuple((operator_id,))
    query = "SELECT mission_id, name, rank, info, operator_id, mission_status  " \
            "FROM mission WHERE operator_id = (%s)"
    cursor.execute(query, name_row)

    temp = cursor.fetchall()
    if not temp:
        return -1
    elements = list(sum(temp, ()))
    string = format_missions(elements)
    return string


def get_mission_by_id(mission_id):
    name_row = tuple((mission_id,))
    query = "SELECT mission_id, name, rank, info, operator_id, mission_status  " \
            "FROM mission WHERE mission_id = (%s)"
    cursor.execute(query, name_row)

    temp = cursor.fetchall()
    if not temp:
        return -1
    elements = list(sum(temp, ()))
    string = format_missions(elements)
    return string


def get_pack_by_id(pack_id):
    name_row = tuple((pack_id,))
    query = "SELECT pack_id, name, info  " \
            "FROM pack WHERE pack_id = (%s)"
    cursor.execute(query, name_row)

    temp = cursor.fetchall()
    if not temp:
        return -1
    elements = list(sum(temp, ()))
    string = format_pack(elements)
    return string


def get_persons():
    query = "SELECT person_id, name FROM person"
    cursor.execute(query)
    data = cursor.fetchall()
    persons = list(sum(data, ()))
    persons_str = format_persons(persons)
    return persons_str


def get_person_by_id(person_id):
    name_row = tuple((person_id,))
    query = "SELECT person_id, name, bio FROM person WHERE person_id = (%s)"
    cursor.execute(query, name_row)

    temp = cursor.fetchall()
    if not temp:
        return -1
    person = list(sum(temp, ()))
    person_str = format_person(person)
    return person_str


def get_agent_by_id(agent_id):
    name_row = tuple((agent_id,))
    query = "SELECT agent_id, name, available, pack_id FROM agent WHERE agent_id = (%s)"
    cursor.execute(query, name_row)
    some_list = cursor.fetchall()
    if not some_list:
        return -1
    something = list(sum(some_list, ()))
    string = format_agents(something)
    return string


def get_person_id_by_name(name):
    name_row = tuple((name,))
    query = "SELECT person_id FROM person WHERE name = (%s)"
    cursor.execute(query, name_row)

    temp = cursor.fetchall()
    if not temp:
        return -1

    person_id = temp[0]
    return person_id


def get_up_by_id(unit_profile_id):
    row = tuple((unit_profile_id,))
    query = "SELECT unit_profile_id, info, rank, person_id, date_from, date_to, agent_id, operator_id " \
            "FROM unit_profile WHERE unit_profile_id = (%s)"
    cursor.execute(query, row)

    temp = cursor.fetchall()
    if not temp:
        return -1
    up = list(sum(temp, ()))
    up_str = format_up(up)
    return up_str


def get_agent_id_by_name(name):
    name_row = tuple((name,))
    query = "SELECT agent_id FROM agent WHERE name = (%s)"
    cursor.execute(query, name_row)

    temp = cursor.fetchall()
    if not temp:
        return -1

    agent_id = temp[0]
    return agent_id


def get_item_by_name(name):
    name_row = tuple((name,))
    query = "SELECT item_id, name, info, pack_id FROM item WHERE name = (%s)"
    cursor.execute(query, name_row)

    some_list = cursor.fetchall()
    if not some_list:
        return -1
    something = list(sum(some_list, ()))
    string = format_items(something)
    return string


def get_operator_by_id(operator_id):
    name_row = tuple((operator_id,))
    query = "SELECT operator_id, info, available FROM operator WHERE operator_id = (%s)"
    cursor.execute(query, name_row)

    temp = cursor.fetchall()
    if not temp:
        return -1
    elements = list(sum(temp, ()))
    string = format_operators(elements)
    return string


def get_operator_id_by_info(info):
    name_row = tuple((info,))
    query = "SELECT operator_id FROM operator WHERE info = (%s)"
    cursor.execute(query, name_row)

    temp = cursor.fetchall()
    if not temp:
        return 1

    operator_id = temp[0]
    return operator_id


def get_up_by_info(up_info):
    row = tuple((up_info,))
    query = "SELECT unit_profile_id, info, rank, person_id, date_from, date_to, agent_id, operator_id " \
            "FROM unit_profile WHERE info = (%s)"
    cursor.execute(query, row)

    temp = cursor.fetchall()
    if not temp:
        return 1

    up = list(sum(temp, ()))
    up_str = format_up(up)
    return up_str


def get_agent_mission_by_agent_id(agent_id):
    row = tuple((agent_id,))
    query = "SELECT agent_id, mission_id, info, date_from, date_to " \
            "FROM agent_mission WHERE agent_id = (%s)"
    cursor.execute(query, row)

    temp = cursor.fetchall()
    if not temp:
        return -1
    elements = list(sum(temp, ()))
    string = format_agent_mission(elements)
    return string


def get_ups():
    query = "SELECT unit_profile_id, info, rank, person_id, date_from, date_to, agent_id, operator_id " \
            "FROM unit_profile"
    cursor.execute(query)
    temp = cursor.fetchall()
    if not temp:
        return 1

    up = list(sum(temp, ()))
    up_str = format_up(up)
    return up_str


def format_missions_with_person_operator(missions):
    missions_str = ""
    i = 0
    for mission in missions:
        if i == 0:
            missions_str += "mission_name: "
            missions_str += str(mission)
            missions_str += ' '
            i += 1
            continue
        elif i == 1:
            missions_str += "level: "
            missions_str += str(mission)
            missions_str += ' '
            i += 1
            continue
        elif i == 2:
            missions_str += "operator ID: "
            missions_str += str(mission)
            missions_str += '\n'
            i += 1
            continue
        elif i == 3:
            missions_str += "operator name: "
            missions_str += str(mission)
            missions_str += '\n'
            i += 1
            continue
        elif i == 4:
            missions_str += "Mission status: "
            missions_str += str(mission)
            missions_str += '\n'
            i += 1
            continue
        elif i == 5:
            missions_str += "Mission info: "
            missions_str += str(mission)
            missions_str += '\n\n'
            i = 0
            continue
    return missions_str


def format_missions(missions):
    missions_str = ""
    i = 0
    for mission in missions:
        if i == 0:
            missions_str += "id: "
            missions_str += str(mission)
            missions_str += ' '
            i += 1
            continue
        elif i == 1:
            missions_str += "name: "
            missions_str += str(mission)
            missions_str += ' '
            i += 1
            continue
        elif i == 2:
            missions_str += "level: "
            missions_str += str(mission)
            missions_str += '\n'
            i += 1
            continue
        elif i == 3:
            missions_str += "Info: "
            missions_str += str(mission)
            missions_str += '\n'
            i += 1
            continue
        elif i == 4:
            missions_str += "operator ID: "
            missions_str += str(mission)
            missions_str += '\n'
            i += 1
            continue
        elif i == 5:
            missions_str += "Mission status: "
            missions_str += str(mission)
            missions_str += '\n\n'
            i = 0
            continue
    return missions_str


def format_persons(persons):
    string = ""
    i = 0
    for person in persons:
        if i == 0:
            string += "id: "
            string += str(person)
            string += ' '
            i += 1
            continue
        elif i == 1:
            string += "name: "
            string += str(person)
            string += '\n\n'
            i = 0
            continue
    return string


def format_person(person):
    string = ""
    i = 0
    for elem in person:
        if i == 0:
            string += "id: "
            string += str(elem)
            string += ' '
            i += 1
            continue
        elif i == 1:
            string += "name: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 2:
            string += "bio: "
            string += str(elem)
            string += '\n\n'
            i = 0
            continue
    return string


def format_up(up):
    string = ""
    i = 0
    for elem in up:
        if i == 0:
            string += "id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 1:
            string += "info: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 2:
            string += "rank: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 3:
            string += "person_id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 4:
            string += "date_from: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 5:
            string += "date_to: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 6:
            string += "agent_id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 7:
            string += "operator_id: "
            string += str(elem)
            string += '\n\n\n'
            i = 0
            continue
    return string


def format_mr(elements):
    string = ""
    i = 0
    for elem in elements:
        if i == 0:
            string += "id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 1:
            string += "name: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 2:
            string += "info: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 3:
            string += "time: "
            string += str(elem)
            string += '\n\n'
            i = 0
            continue
    return string


def format_agents(elements):
    string = ""
    i = 0
    for elem in elements:
        if i == 0:
            string += "id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 1:
            string += "name: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 2:
            string += "available: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 3:
            string += "pack_id: "
            string += str(elem)
            string += '\n\n'
            i = 0
            continue
    return string


def format_operators(elements):
    string = ""
    i = 0
    for elem in elements:
        if i == 0:
            string += "id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 1:
            string += "info: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 2:
            string += "available: "
            string += str(elem)
            string += '\n\n'
            i = 0
            continue
    return string


def format_agent_mission(elements):
    string = ""
    i = 0
    for elem in elements:
        if i == 0:
            string += "agent_id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 1:
            string += "mission_id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 2:
            string += "info: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 3:
            string += "date_from: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 4:
            string += "date_to: "
            string += str(elem)
            string += '\n\n'
            i = 0
            continue
    return string


def format_pack(elements):
    string = ""
    i = 0
    for elem in elements:
        if i == 0:
            string += "item_id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 1:
            string += "name: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 2:
            string += "info: "
            string += str(elem)
            string += '\n\n'
            i = 0
            continue
    return string


def format_items(elements):
    string = ""
    i = 0
    for elem in elements:
        if i == 0:
            string += "item_id: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 1:
            string += "name: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 2:
            string += "info: "
            string += str(elem)
            string += '\n'
            i += 1
            continue
        elif i == 3:
            string += "pack_id: "
            string += str(elem)
            string += '\n\n'
            i = 0
            continue
    return string


def add_agent(name):
    agent_row = tuple((name, True), )
    query = "INSERT INTO agent (name, available) VALUES (%s, %s)"
    cursor.execute(query, agent_row)
    return


def add_operator(info):
    operator_row = tuple((info, True), )
    query = "INSERT INTO operator (info, available) VALUES (%s, %s)"
    cursor.execute(query, operator_row)
    return


def add_person(person_name, person_bio):
    row = tuple((person_name, person_bio), )
    query = "INSERT INTO person (name, bio) VALUES (%s, %s)"
    cursor.execute(query, row)
    return


def add_item(name, info, pack_id):
    row = tuple((name, info, pack_id), )
    query = "INSERT INTO item (name, info, pack_id) VALUES (%s, %s, %s)"
    cursor.execute(query, row)
    return


def add_up(up_info, up_rank, person_id, date_from, date_to, agent_id, operator_id):
    row = tuple((up_info, up_rank, person_id, date_from, date_to, agent_id, operator_id), )
    query = "INSERT INTO unit_profile (info, rank, person_id, date_from," \
            " date_to, agent_it, operator_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, row)
    return


def add_agent_mission(agent_id, mission_id, info, date_from, date_to):
    row = tuple((agent_id, mission_id, info, date_from, date_to), )
    query = "INSERT INTO agent_mission (agent_id, mission_id, info, date_from, date_to) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, row)
    return


def up_change_agent_id(unit_profile_id, agent_id):
    query = "UPDATE unit_profile SET agent_id = (%s) " \
            "WHERE unit_profile_id = (%s)"
    row = tuple((agent_id, unit_profile_id), )
    cursor.execute(query, row)
    return


def up_change_operator_id(unit_profile_id, operator_id):
    query = "UPDATE unit_profile SET operator_id = (%s) " \
            "WHERE unit_profile_id = (%s)"
    row = tuple((operator_id, unit_profile_id), )
    cursor.execute(query, row)
    return


def edit_op_info(unit_profile_id, up_info):
    query = "UPDATE unit_profile SET info = (%s) " \
            "WHERE unit_profile_id = (%s)"
    row = tuple((up_info, unit_profile_id), )
    cursor.execute(query, row)
    return


def edit_op_rank(unit_profile_id, up_rank):
    query = "UPDATE unit_profile SET rank = (%s) " \
            "WHERE unit_profile_id = (%s)"
    row = tuple((up_rank, unit_profile_id), )
    cursor.execute(query, row)
    return


def edit_op_person_id(unit_profile_id, person_id):
    query = "UPDATE unit_profile SET person_id = (%s) " \
            "WHERE unit_profile_id = (%s)"
    row = tuple((person_id, unit_profile_id), )
    cursor.execute(query, row)
    return


def edit_op_dates(unit_profile_id, date_from, date_to):
    query = "UPDATE unit_profile SET date_from = (%s), date_to = (%s)" \
            "WHERE unit_profile_id = (%s)"
    row = tuple((date_from, date_to, unit_profile_id), )
    cursor.execute(query, row)
    return


def add_operator_to_mission(mission_id, operator_id):
    query = "UPDATE mission SET operator_id = (%s)" \
            "WHERE mission_id = (%s)"
    row = tuple((operator_id, mission_id), )
    cursor.execute(query, row)
    return


def delete_agent_by_id(agent_id):
    rid_row = tuple((agent_id,))
    query = "DELETE FROM agent WHERE agent_id = (%s)"
    cursor.execute(query, rid_row)


def delete_operator_by_id(operator_id):
    rid_row = tuple((operator_id,))
    query = "DELETE FROM operator WHERE operator_id = (%s)"
    cursor.execute(query, rid_row)
