import telebot
from telebot import types

import configparser
import datetime
import logging
import db_interface
import re

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

API_TOKEN = config.get("bot", "API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
bot.skip_pending = True

db_interface = db_interface
db_cursor = db_interface.cursor

auth_code = "www"
agent_id = 0
agent_name = ""
agent_pack_id = 0
pack_id = -1
name = ""
operator_info = ""
operator_id = 0
operator_name = ""
unit_profile_id = 0
up_info = ""
up_rank = 4
person_id = 0
person_name = ""
person_bio = ""
date_from = ""
date_to = ""
info = ""
mission_id = 0

switch = None  # Operator or Agent in unit_profile(up) chain
up_switch = False  # in unit_profile chain -> (true)
up_edit = False


@bot.message_handler(commands=['start'])
@bot.message_handler(regexp="^Меню$")
@bot.message_handler(regexp="^Отмена$")
def send_welcome(message):
    if message.text == '/start' or message.text == 'Отмена' or message.text == 'Меню':
        global switch
        switch = 0
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button1 = types.KeyboardButton("Добавить")
        button2 = types.KeyboardButton("Удалить")
        button3 = types.KeyboardButton("Последние результаты миссий")
        button4 = types.KeyboardButton("Миссии")
        button5 = types.KeyboardButton("Вооружение и предметы")
        button6 = types.KeyboardButton("Агенты")
        button7 = types.KeyboardButton("Личные дела сотрудников")
        button8 = types.KeyboardButton("Назначить агента/оператора")

        markup.add(button1, button2, button3, button4, button5, button6, button7, button8)

        bot.send_message(message.chat.id,
                         "Выберите действие.\n"
                         "Доступна команда: /help".format(message.from_user, bot.get_me()),
                         reply_markup=markup)


@bot.message_handler(regexp="^Добавить$")
def button(message):
    if message.text == 'Добавить':
        global switch
        switch = 0
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        key_agent = types.KeyboardButton("Добавить агента")
        key_operator = types.KeyboardButton("Добавить оператора")
        key_mission = types.KeyboardButton("Добавить миссию")
        key_item = types.KeyboardButton("Добавить предмет")
        key_pack = types.KeyboardButton("Добавить набор")
        key_up = types.KeyboardButton("Добавить личное дело")
        key_record = types.KeyboardButton("Добавить мед. данные")
        key_person = types.KeyboardButton("Добавить нового сотрудника")
        key_exit = types.KeyboardButton("Меню")

        markup.add(key_agent, key_operator, key_mission, key_item, key_pack, key_up, key_record,
                   key_person, key_exit)
        bot.send_message(message.chat.id,
                         "Кого или что нужно добавить?".format(message.from_user, bot.get_me()),
                         reply_markup=markup)


# @bot.message_handler(regexp="^Отмена$")
# def send_welcome(message):
#     if message.text == 'Отмена':
#         global switch
#         switch = 0
#         markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#         button1 = types.KeyboardButton("Добавить")
#         button2 = types.KeyboardButton("Изменить/Удалить")
#         button3 = types.KeyboardButton("Последние результаты миссий")
#         button4 = types.KeyboardButton("Миссии")
#         button5 = types.KeyboardButton("Вооружение и предметы")
#         button6 = types.KeyboardButton("Агенты")
#         button7 = types.KeyboardButton("Личные дела сотрудников")
#         button8 = types.KeyboardButton("Назначить агента/оператора")
#
#         markup.add(button1, button2, button3, button4, button5, button6, button7, button8)
#
#         bot.send_message(message.chat.id,
#                          "Выберите действие.\n"
#                          "Доступна команда: /help".format(message.from_user, bot.get_me()),
#                          reply_markup=markup)


@bot.message_handler(regexp="Добавить агента")
def add_agent(message):
    global switch
    if message.text == 'Добавить агента':
        switch = 1
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key_exit)

        msg = bot.send_message(message.chat.id, "Введите имя агента", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_agent_name)


def ask_agent_name(message):
    global agent_name
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    agent_name = message.text
    if not agent_name:
        msg = bot.send_message(message.chat.id, "Некорректное имя, введите еще раз", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_agent_name)
        return
    employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_true = types.InlineKeyboardButton(text="Да", callback_data='employ_a')
    key_false = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    employee_register_keyboard.add(key_true, key_false)
    bot.send_message(message.chat.id, "Регистрировать сотрудника " + agent_name + " ?",
                     reply_markup=employee_register_keyboard)


def check_auth_code(message):
    global auth_code
    continue_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_continue = types.InlineKeyboardButton(text="Да", callback_data='employee_retry')
    key_exit = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    continue_keyboard.add(key_continue, key_exit)

    bot.delete_message(message.chat.id, message.message_id)
    if not message.text == auth_code:
        msg = bot.send_message(message.chat.id, "Некорректный код доступа \n Желаете попробовать еще раз?",
                               reply_markup=continue_keyboard)
        bot.clear_reply_handlers_by_message_id(msg)
        bot.register_next_step_handler(msg, check_auth_code)
        return
    # else:
    #     msg = bot.send_message(message.chat.id, "Код доступа верный!")
    #     return 1


def check_auth_code_a(message):
    global agent_id
    code = message.text
    if not code == auth_code:
        continue_keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_continue = types.InlineKeyboardButton(text="Да", callback_data='employ_a')
        key_exit = types.InlineKeyboardButton(text="Нет", callback_data='exit')
        continue_keyboard.add(key_continue, key_exit)
        bot.delete_message(message.chat.id, message.message_id)
        bot.clear_reply_handlers_by_message_id(message)
        msg = bot.send_message(message.chat.id, "Некорректный код доступа \n Желаете попробовать еще раз?",
                               reply_markup=continue_keyboard)
        return

    msg = bot.send_message(message.chat.id, "Код принят!")
    db_interface.add_agent(agent_name)
    bot.send_message(msg.chat.id, "Новый агент " + agent_name + " добавлен в базу!")

    agent_id = db_interface.get_agent_id_by_name(agent_name)
    employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_true = types.InlineKeyboardButton(text="Да", callback_data='up_agent')
    key_false = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    employee_register_keyboard.add(key_true, key_false)
    bot.send_message(message.chat.id, "Назначить личное дело агенту " + agent_name + " ?",
                     reply_markup=employee_register_keyboard)
    # else:
    # msg = bot.send_message(message.chat.id, "Код доступа неверный!")
    # check_auth_code(msg)
    # return


def check_auth_code_o(message):
    global operator_id
    global operator_info
    code = message.text
    if not code == auth_code:
        continue_keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_continue = types.InlineKeyboardButton(text="Да", callback_data='employ_o')
        key_exit = types.InlineKeyboardButton(text="Нет", callback_data='exit')
        continue_keyboard.add(key_continue, key_exit)
        bot.delete_message(message.chat.id, message.message_id)
        bot.clear_reply_handlers_by_message_id(message)
        msg = bot.send_message(message.chat.id, "Некорректный код доступа \n Желаете попробовать еще раз?",
                               reply_markup=continue_keyboard)
        return

    msg = bot.send_message(message.chat.id, "Код принят!")

    db_interface.add_operator(operator_info)
    operator_id = db_interface.get_operator_id_by_info(operator_info)
    bot.send_message(msg.chat.id, "Новый оператор добавлен в базу!")

    employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_true = types.InlineKeyboardButton(text="Да", callback_data='up_operator')
    key_false = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    employee_register_keyboard.add(key_true, key_false)
    bot.send_message(message.chat.id, "Назначить личное дело оператору ?",
                     reply_markup=employee_register_keyboard)


def check_auth_code_p(message):
    global person_id
    global person_name

    code = message.text
    if not code == auth_code:
        continue_keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_continue = types.InlineKeyboardButton(text="Да", callback_data='employ_p')
        key_exit = types.InlineKeyboardButton(text="Нет", callback_data='exit')
        continue_keyboard.add(key_continue, key_exit)
        bot.delete_message(message.chat.id, message.message_id)
        bot.clear_reply_handlers_by_message_id(message)
        msg = bot.send_message(message.chat.id, "Некорректный код доступа \n Желаете попробовать еще раз?",
                               reply_markup=continue_keyboard)
        return

    msg = bot.send_message(message.chat.id, "Код принят!")
    db_interface.add_person(person_name, person_bio)
    person_id = db_interface.get_person_id_by_name(person_name)
    bot.send_message(msg.chat.id, "Мистер/Мисс " + person_name + " добавлен/а в базу!")

    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    if up_switch:
        msg = bot.send_message(message.chat.id, "Введите дату начала дела", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)


@bot.message_handler(regexp="Добавить оператора")
def add_operator(message):
    global switch
    switch = 2
    if message.text == 'Добавить оператора':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key_exit)
        msg = bot.send_message(message.chat.id, "Введите информацию об операторе", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_operator_info)


def ask_operator_info(message):
    global operator_info
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    operator_info = message.text

    if not operator_info:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Введите правильный текст",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_info_up)
        return

    employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_true = types.InlineKeyboardButton(text="Да", callback_data='employ_o')
    key_false = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    employee_register_keyboard.add(key_true, key_false)
    bot.send_message(message.chat.id, "Регистрировать оператора?",
                     reply_markup=employee_register_keyboard)


@bot.message_handler(regexp="Добавить предмет")
def add_item(message):
    if message.text == 'Добавить предмет':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key_exit)
        msg = bot.send_message(message.chat.id, "Введите имя предмета:", reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_item_name)


def ask_item_name(message):
    global name
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    name = message.text

    if not name:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Введите правильный текст",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_item_name)
        return

    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    msg = bot.send_message(message.chat.id, "Введите информацию предмета:", reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_item_info)


def ask_item_info(message):
    global info
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    info = message.text

    if not info:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Введите правильный текст",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_item_info)
        return

    employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_true = types.InlineKeyboardButton(text="Да", callback_data='add_pack_to_item')
    key_false = types.InlineKeyboardButton(text="Пока нет, назначить к снаряжению", callback_data='add_item')
    employee_register_keyboard.add(key_true, key_false)
    bot.send_message(message.chat.id, "Зарегистрировать предмет?",
                     reply_markup=employee_register_keyboard)


def ask_pack_id(message):
    global pack_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='add_item')
    exit_keyboard.add(key_exit)
    bot.send_message(message.chat.id, "Введите существующий ID pack")
    pack_id = int(message.text)
    if db_interface.get_pack_by_id(pack_id) == -1:
        msg = bot.send_message(message.chat.id, "Такого набора не существует, попробуйте ещё раз",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_pack_id)
        return

    bot.send_message(message.chat.id, db_interface.get_pack_by_id(pack_id))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Добавить!", callback_data='add_item')
    key2 = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить добавление предмета?", reply_markup=keyboard)


@bot.message_handler(regexp="Добавить личное дело")
def add_up(message):
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    msg = bot.send_message(message.chat.id, "Введите основную информацию личного дела",
                           reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_info_up)


def ask_info_up(message):
    global up_info
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    up_info = message.text
    if not up_info:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Введите правильный текст",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_info_up)
        return
    msg = bot.send_message(message.chat.id, "Введите ранг, число от 1 до 4", reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_rank_up)


def ask_rank_up(message):
    global up_rank
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    up_rank = int(message.text)
    if not up_info or up_rank > 4 or up_rank < 1:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Нужно число от 1 до 4",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_info_up)
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Выбрать существующего", callback_data='choose_person')
    key2 = types.InlineKeyboardButton(text="Создать нового", callback_data='add_person')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Нужно выбрать человека", reply_markup=keyboard)


def choose_person(message):
    global person_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    person_id = int(message.text)

    if db_interface.get_person_by_id(person_id) == -1:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Выберите правильный ID",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, choose_person)
        return
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='person_chosen_up')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='choose_person')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить выбор?", reply_markup=keyboard)


def ask_person_name(message):
    global person_name
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    person_name = message.text
    if not up_info:
        msg = bot.send_message(message.chat.id, "Некорректный текст",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_person_name)
        return

    msg = bot.send_message(message.chat.id, "Напишите биографию для данной персоны", reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_person_bio)


def ask_person_bio(message):
    global person_bio
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    person_bio = message.text
    if not up_info:
        msg = bot.send_message(message.chat.id, "Некорректный текст",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_person_bio)
        return

    employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
    key_true = types.InlineKeyboardButton(text="Да", callback_data='employ_p')
    key_false = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    employee_register_keyboard.add(key_true, key_false)
    bot.send_message(message.chat.id, "Зарегистрировать человека " + agent_name + " ?",
                     reply_markup=employee_register_keyboard)


def ask_dates(message):
    global date_from
    global date_to
    global switch

    dates = message.text
    pattern = r'\d\d\.\d\d\.\d\d\d\d\-\d\d\.\d\d\.\d\d\d\d'
    bot.clear_reply_handlers_by_message_id(message)
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)

    if not re.match(pattern, dates):
        msg = bot.send_message(message.chat.id,
                               "Некорректные даты. Корректный формат: dd.mm.yyyy-dd.mm.yyyy, нули учитываются"
                               " \n Попробуйте еще раз",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    dates_list = re.split(r'-', dates)

    start = re.split(r'\.', dates_list[0])
    end = re.split(r'\.', dates_list[1])
    start_year = int(start[2])
    start_month = int(start[1])
    start_day = int(start[0])
    end_year = int(end[2])
    end_month = int(end[1])
    end_day = int(end[0])

    if start_year > 2050 or end_year > 2050:
        msg = bot.send_message(message.chat.id,
                               "Введите год меньше 2050",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_year < 1990 or end_year < 1990:

        msg = bot.send_message(message.chat.id,
                               "Введите год больше 1990",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_month > 12 or end_month > 12 or start_month < 1 or end_month < 1:
        msg = bot.send_message(message.chat.id,
                               "Введите месяц от 1 до 12",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_day > 31 or end_day > 31 or start_day < 1 or end_day < 1:
        msg = bot.send_message(message.chat.id,
                               "Введите день от 1 до 31",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_month == 2 and not (start_day == 29 and start_year % 4 == 0) and start_day > 29 \
            or end_month == 2 and not (end_day == 29 and end_year % 4 == 0) and end_day > 29:
        msg = bot.send_message(message.chat.id,
                               "Вероятно, выбрано неправильное число в феврале. "
                               "\nСледует убедиться в том, что год високосный ",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    date_from = datetime.date(start_year, start_month, start_day)
    date_to = datetime.date(end_year, end_month, end_day)
    if switch == 1:
        employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_true = types.InlineKeyboardButton(text="Да", callback_data='up_finish_a')
        key_false = types.InlineKeyboardButton(text="отмена", callback_data='exit')
        employee_register_keyboard.add(key_true, key_false)
        bot.send_message(message.chat.id, "Зарегистрировать личное дело на агента?",
                         reply_markup=employee_register_keyboard)
    elif switch == 2:
        employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_true = types.InlineKeyboardButton(text="Да", callback_data='up_finish_o')
        key_false = types.InlineKeyboardButton(text="отмена", callback_data='exit')
        employee_register_keyboard.add(key_true, key_false)
        bot.send_message(message.chat.id, "Зарегистрировать личное дело на оператора?",
                         reply_markup=employee_register_keyboard)
    elif switch == 3:
        employee_register_keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_true = types.InlineKeyboardButton(text="Да", callback_data='add_agent_mission_finish')
        key_false = types.InlineKeyboardButton(text="отмена", callback_data='exit')
        employee_register_keyboard.add(key_true, key_false)
        bot.send_message(message.chat.id, "Создаём новое назначение на миссию для этого агента?",
                         reply_markup=employee_register_keyboard)


@bot.message_handler(regexp="Последние результаты миссий")
def show_last_m_results(message):
    if message.text == 'Последние результаты миссий':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key1 = types.InlineKeyboardButton(text="Последние 10", callback_data='show_mr_last10')
        key2 = types.InlineKeyboardButton(text="Все с начала", callback_data='show_mr_from_beginning')
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key1, key2, key_exit)
        msg = bot.send_message(message.chat.id, "Каким образом вывести результаты?", reply_markup=exit_keyboard)


@bot.message_handler(regexp="Агенты")
def show_last_m_results(message):
    if message.text == 'Агенты':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key1 = types.InlineKeyboardButton(text="Все агенты", callback_data='show_agents')
        key2 = types.InlineKeyboardButton(text="С сортировкой по имени", callback_data='show_agents_sorted_by_names')
        key3 = types.InlineKeyboardButton(text="У кого нет снаряжения", callback_data='show_agents_without_pack')
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key1, key2, key3, key_exit)
        msg = bot.send_message(message.chat.id, "Каким образом вывести результаты?", reply_markup=exit_keyboard)


@bot.message_handler(regexp="Вооружение и предметы")
def show_last_m_results(message):
    if message.text == 'Вооружение и предметы':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key1 = types.InlineKeyboardButton(text="С сортировкой по имени", callback_data='show_items_sorted_by_names')
        key2 = types.InlineKeyboardButton(text="Без назначения", callback_data='show_items_without_pack')
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key1, key2, key_exit)
        msg = bot.send_message(message.chat.id, "Каким образом вывести результаты?", reply_markup=exit_keyboard)


@bot.message_handler(regexp="Миссии")
def show_last_m_results(message):
    if message.text == 'Миссии':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key1 = types.InlineKeyboardButton(text="С сортировкой по имени", callback_data='show_missions_sorted_by_names')
        key2 = types.InlineKeyboardButton(text="С сортировкой по рангу", callback_data='show_missions_sorted_by_rank')
        key3 = types.InlineKeyboardButton(text="Без оператора", callback_data='show_missions_without_operator')
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key1, key2, key3, key_exit)
        msg = bot.send_message(message.chat.id, "Каким образом вывести результаты?", reply_markup=exit_keyboard)


@bot.message_handler(regexp="Назначить агента/оператора")
def show_last_m_results(message):
    if message.text == 'Назначить агента/оператора':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key1 = types.InlineKeyboardButton(text="Агента", callback_data='assign_agent')
        key2 = types.InlineKeyboardButton(text="Оператора", callback_data='assign_operator')
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key1, key2, key_exit)
        msg = bot.send_message(message.chat.id, "Кого назначить?", reply_markup=exit_keyboard)


@bot.message_handler(regexp="Удалить")
def show_last_m_results(message):
    if message.text == 'Удалить':
        exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
        key1 = types.InlineKeyboardButton(text="Агента", callback_data='delete_agent')
        key2 = types.InlineKeyboardButton(text="Оператора", callback_data='delete_operator')
        key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
        exit_keyboard.add(key1, key2, key_exit)
        bot.send_message(message.chat.id, "Кого удалить?", reply_markup=exit_keyboard)


def choose_agent_delete(message):
    global agent_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    agent_id = int(message.text)

    if db_interface.get_agent_by_id(agent_id) == -1:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Выберите правильный ID",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, agent_choose_mission)
        return
    bot.send_message(message.chat.id, db_interface.get_agent_by_id(agent_id))

    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key1 = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    key2 = types.InlineKeyboardButton(text="Удалить", callback_data='delete_agent_confirmed')
    exit_keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Уверены, что хотите удалить?", reply_markup=exit_keyboard)


def choose_operator_delete(message):
    global operator_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    operator_id = int(message.text)

    if db_interface.get_operator_by_id(operator_id) == -1:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Выберите правильный ID",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, choose_operator_delete)
        return
    bot.send_message(message.chat.id, db_interface.get_operator_by_id(operator_id))

    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key1 = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    key2 = types.InlineKeyboardButton(text="Удалить", callback_data='delete_operator_confirmed')
    exit_keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Уверены, что хотите удалить?", reply_markup=exit_keyboard)


def agent_choose_mission(message):
    global mission_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    mission_id = int(message.text)

    if db_interface.get_mission_by_id(mission_id) == -1:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Выберите правильный ID",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, agent_choose_mission)
        return
    bot.send_message(message.chat.id, db_interface.get_mission_by_id(mission_id))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='assign_agent_mission_confirmed')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить выбор?", reply_markup=keyboard)


def add_agent_mission(message):
    global agent_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    agent_id = int(message.text)

    if db_interface.get_agent_by_id(agent_id) == -1:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Выберите правильный ID",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, agent_choose_mission)
        return
    bot.send_message(message.chat.id, db_interface.get_agent_by_id(agent_id))

    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    msg = bot.send_message(message.chat.id, "Введите информацию о назначении", reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_agent_mission_info)


def ask_agent_mission_info(message):
    global info
    global switch
    switch = 3
    info = message.text

    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    msg = bot.send_message(message.chat.id, "Введите даты", reply_markup=exit_keyboard)
    bot.register_next_step_handler(msg, ask_dates)


def operator_choose_mission(message):
    global mission_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    mission_id = int(message.text)

    if db_interface.get_mission_by_id(mission_id) == -1:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Выберите правильный ID",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, operator_choose_mission)
        return
    bot.send_message(message.chat.id, db_interface.get_mission_by_id(mission_id))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='assign_operator_mission_confirmed')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить выбор?", reply_markup=keyboard)


def operator_choose_for_mission(message):
    global operator_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    operator_id = int(message.text)

    if db_interface.get_operator_by_id(operator_id) == -1:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Выберите правильный ID",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, operator_choose_for_mission)
        return
    bot.send_message(message.chat.id, db_interface.get_operator_by_id(operator_id))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='assign_operator_mission_finished')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='exit')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить выбор?", reply_markup=keyboard)


def edit_up(message):
    global switch
    global unit_profile_id
    global up_edit
    # bot.send_message(message.chat.id, db_interface.get_ups())
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='exit')
    exit_keyboard.add(key_exit)
    unit_profile_id = int(message.text)
    print("unit_profile = " + str(unit_profile_id))

    if db_interface.get_up_by_id(unit_profile_id) == -1:
        msg = bot.send_message(message.chat.id, "Некорректная информация. Выберите правильный ID",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, edit_up)
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='chosen_up_agent_or_operator')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='up_choose_a') if switch == 1 \
        else types.InlineKeyboardButton(text="Нет", callback_data='up_choose_o')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить выбор?", reply_markup=keyboard)


def want_to_edit_up(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='chosen_up')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='start')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Желаете редактировать выбранное личное дело?",
                     reply_markup=keyboard)


def chosen_up(message):
    global switch
    global up_edit
    up_edit = False
    switch = 0
    bot.send_message(message.chat.id, db_interface.get_up_by_id(unit_profile_id))
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Информацию", callback_data='edit_op_info')
    key2 = types.InlineKeyboardButton(text="Ранг", callback_data='edit_op_rank')
    key3 = types.InlineKeyboardButton(text="ID Персоны", callback_data='edit_op_person_id')
    key4 = types.InlineKeyboardButton(text="Даты", callback_data='edit_op_dates')
    key5 = types.InlineKeyboardButton(text="Закончить", callback_data='exit')
    keyboard.add(key1, key2, key3, key4, key5)
    bot.send_message(message.chat.id, "Что именно отредактировать?", reply_markup=keyboard)


def edit_op_info(message):
    global up_info
    up_info = message.text
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='edit_op_info_confirmed')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='chosen_up')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить редактирование столбца info?", reply_markup=keyboard)


def edit_op_rank(message):
    global up_rank
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='chosen_up')
    exit_keyboard.add(key_exit)
    bot.send_message(message.chat.id, "Введите число от 1 до 4")
    up_rank = int(message.text)
    if up_rank > 4 or up_rank < 1:
        msg = bot.send_message(message.chat.id, "Неверное число. Введите цифру от 1 до 4",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, edit_op_rank)
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='edit_op_rank_confirmed')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='chosen_up')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить редактирование столбца rank?", reply_markup=keyboard)


def edit_op_person_id(message):
    global person_id
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='chosen_up')
    exit_keyboard.add(key_exit)
    bot.send_message(message.chat.id, "Введите существующий ID персоны")
    person_id = int(message.text)
    if db_interface.get_person_by_id(person_id) == -1:
        msg = bot.send_message(message.chat.id, "Такой персоны не существует, попробуйте ещё раз",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, edit_op_rank)
        return
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='edit_op_person_id_confirmed')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='chosen_up')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить редактирование столбца person_id?", reply_markup=keyboard)


def edit_op_dates(message):
    global date_from
    global date_to
    dates = message.text
    pattern = r'\d\d\.\d\d\.\d\d\d\d\-\d\d\.\d\d\.\d\d\d\d'
    bot.clear_reply_handlers_by_message_id(message)
    exit_keyboard = types.InlineKeyboardMarkup(row_width=1)
    key_exit = types.InlineKeyboardButton(text="Отмена", callback_data='chosen_up')
    exit_keyboard.add(key_exit)

    if not re.match(pattern, dates):
        msg = bot.send_message(message.chat.id,
                               "Некорректные даты. Корректный формат: dd.mm.yyyy-dd.mm.yyyy, нули учитываются"
                               " \n Попробуйте еще раз",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, edit_op_dates)
        return

    dates_list = re.split(r'-', dates)

    start = re.split(r'\.', dates_list[0])
    end = re.split(r'\.', dates_list[1])
    start_year = int(start[2])
    start_month = int(start[1])
    start_day = int(start[0])
    end_year = int(end[2])
    end_month = int(end[1])
    end_day = int(end[0])

    if start_year > 2050 or end_year > 2050:
        msg = bot.send_message(message.chat.id,
                               "Введите год меньше 2050",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_year < 1990 or end_year < 1990:

        msg = bot.send_message(message.chat.id,
                               "Введите год больше 1990",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_month > 12 or end_month > 12 or start_month < 1 or end_month < 1:
        msg = bot.send_message(message.chat.id,
                               "Введите месяц от 1 до 12",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_day > 31 or end_day > 31 or start_day < 1 or end_day < 1:
        msg = bot.send_message(message.chat.id,
                               "Введите день от 1 до 31",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    elif start_month == 2 and not (start_day == 29 and start_year % 4 == 0) and start_day > 29 \
            or end_month == 2 and not (end_day == 29 and end_year % 4 == 0) and end_day > 29:
        msg = bot.send_message(message.chat.id,
                               "Вероятно, выбрано неправильное число в феврале. "
                               "\nСледует убедиться в том, что год високосный ",
                               reply_markup=exit_keyboard)
        bot.register_next_step_handler(msg, ask_dates)
        return

    date_from = datetime.date(start_year, start_month, start_day)
    date_to = datetime.date(end_year, end_month, end_day)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    key1 = types.InlineKeyboardButton(text="Да", callback_data='edit_op_dates_confirmed')
    key2 = types.InlineKeyboardButton(text="Нет", callback_data='chosen_up')
    keyboard.add(key1, key2)
    bot.send_message(message.chat.id, "Подтвердить редактирование столбцов date_from, date_to?",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global switch
    bot.answer_callback_query(callback_query_id=call.id, text='Вот доступные команды')
    answer = ''

    if call.data == 'exit':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Действия отменены")
        bot.clear_step_handler_by_chat_id(msg.chat.id)
        return
    if call.data == 'start':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.message.chat.id, "Возврат в главное меню")
        bot.clear_step_handler_by_chat_id(msg.chat.id)
        switch = 0
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button1 = types.KeyboardButton("Добавить")
        button2 = types.KeyboardButton("Изменить/Удалить")
        button3 = types.KeyboardButton("Последние результаты миссий")
        button4 = types.KeyboardButton("Миссии")
        button5 = types.KeyboardButton("Вооружение и предметы")
        button6 = types.KeyboardButton("Агенты")
        button7 = types.KeyboardButton("Личные дела сотрудников")
        button8 = types.KeyboardButton("Назначить агента/оператора")

        markup.add(button1, button2, button3, button4, button5, button6, button7, button8)

        bot.send_message(call.message.chat.id,
                         "Выберите действие.\n"
                         "Доступна команда: /help".format(call.message.from_user, bot.get_me()),
                         reply_markup=markup)
        return
    if call.data == '1':
        send_time(call.message)
        answer = 'Текущее время'
    elif call.data == '2':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        help_message(call.message)
    if call.data == '3':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        send_welcome(call.message)

    # unit_profile_add/edit
    global operator_id
    global agent_id
    global unit_profile_id
    global pack_id
    global person_id
    global up_info
    global up_rank
    global date_from
    global date_to
    global mission_id
    global info
    global name

    if call.data == 'up_create_a':
        switch = 1
        msg = bot.send_message(call.message.chat.id, "Создание личного дела для агента:")
        bot.register_next_step_handler(msg, add_up)
    elif call.data == 'up_create_o':
        switch = 2
        msg = bot.send_message(call.message.chat.id, "Создание личного дела для оператора:")
        bot.register_next_step_handler(msg, add_up)

    if call.data == 'up_choose_a':
        switch = 1
        msg = bot.send_message(call.message.chat.id, "Изменение личного дела для агента:")
        ups = db_interface.get_ups()
        if len(ups) > 4096:
            for x in range(0, len(ups), 4096):
                bot.send_message(call.message.chat.id, ups[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, ups)

        bot.register_next_step_handler(msg, edit_up)
    elif call.data == 'up_choose_o':
        switch = 2
        msg = bot.send_message(call.message.chat.id, "Изменение личного дела для оператора:")
        bot.register_next_step_handler(msg, edit_up)

    if call.data == 'up_finish_a':
        operator_id = None
        db_interface.add_up(up_info, up_rank, person_id, date_from, date_to, agent_id, operator_id)
        bot.send_message(call.message.chat.id, "Личное дело для агента " + agent_name + " добавлено!")
        bot.send_message(call.message.chat.id, db_interface.get_up_by_info(up_info))
    elif call.data == 'up_finish_o':
        agent_id = None
        db_interface.add_up(up_info, up_rank, person_id, date_from, date_to, agent_id, operator_id)
        bot.send_message(call.message.chat.id, "Личное дело для оператора " + operator_id + " добавлено!")
        bot.send_message(call.message.chat.id, db_interface.get_up_by_info(up_info))

    if call.data == 'chosen_up_agent_or_operator':
        if switch == 1:
            db_interface.up_change_agent_id(unit_profile_id, agent_id)
            bot.send_message(call.message.chat.id, db_interface.get_up_by_id(unit_profile_id))
        elif switch == 2:
            db_interface.up_change_operator_id(unit_profile_id, operator_id)
            bot.send_message(call.message.chat.id, db_interface.get_up_by_id(unit_profile_id))
        msg = bot.send_message(call.message.chat.id, "Ваш выбор внесён в выбранное личное дело")
        bot.register_next_step_handler_by_chat_id(msg, want_to_edit_up(msg))

    if call.data == 'chosen_up':
        msg = bot.send_message(call.message.chat.id, "Продолжаем редактирование личного дела:")
        bot.register_next_step_handler_by_chat_id(msg, chosen_up(msg))
        # switch = 0
        # bot.send_message(call.message.chat.id, db_interface.get_up_by_id(unit_profile_id))
        # keyboard = types.InlineKeyboardMarkup(row_width=2)
        # key1 = types.InlineKeyboardButton(text="Информацию", callback_data='edit_op_info')
        # key2 = types.InlineKeyboardButton(text="Ранг", callback_data='edit_op_rank')
        # key3 = types.InlineKeyboardButton(text="ID Персоны", callback_data='edit_op_person_id')
        # key4 = types.InlineKeyboardButton(text="Даты", callback_data='edit_op_dates')
        # key5 = types.InlineKeyboardButton(text="Закончить", callback_data='exit')
        # keyboard.add(key1, key2, key3, key4, key5)
        # bot.send_message(call.message.chat.id, "Что именно отредактировать?", reply_markup=keyboard)

    if call.data == 'choose_person':
        db_interface.get_persons()
        msg = bot.send_message(call.message.chat.id, "Выберите человека:")
        bot.register_next_step_handler(msg, choose_person)
    elif call.data == 'person_chosen_up':
        msg = bot.send_message(call.message.chat.id, "Теперь необходимо выбрать дату начала действия"
                                                     "личного дела:")
        bot.register_next_step_handler(msg, ask_dates)
    elif call.data == 'add_person':
        msg = bot.send_message(call.message.chat.id, "Добавление человека в бюро:")
        bot.register_next_step_handler(msg, ask_person_name)
    # add commands

    if call.data == 'add_item':
        if pack_id == -1:
            db_interface.add_item(name, info, None)
            bot.send_message(call.message.chat.id, "Предмет добавлен!")
            db_interface.get_item_by_name(name)
        else:
            db_interface.add_item(name, info, pack_id)
            bot.send_message(call.message.chat.id, "Предмет добавлен!")
            db_interface.get_item_by_name(name)
        pack_id = -1

    elif call.data == 'add_pack_to_item':
        ups = db_interface.show_packs()
        if len(ups) > 4096:
            for x in range(0, len(ups), 4096):
                bot.send_message(call.message.chat.id, ups[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, ups)
        msg = bot.send_message(call.message.chat.id, "Хорошо! Тогда к какому pack добавим?")
        bot.register_next_step_handler(msg, ask_pack_id)

    if call.data == 'employ_a':
        msg = bot.send_message(call.message.chat.id, "Введите правильный код доступа")
        bot.register_next_step_handler(msg, check_auth_code_a)

    elif call.data == 'employ_o':
        msg = bot.send_message(call.message.chat.id, "Введите код доступа")
        bot.register_next_step_handler(msg, check_auth_code_o)

    elif call.data == 'employ_p':
        msg = bot.send_message(call.message.chat.id, "Введите код доступа")
        bot.register_next_step_handler(msg, check_auth_code_p)

    if call.data == 'employee_retry':
        msg = bot.send_message(call.message.chat.id, "Попробуйте ввести код еще раз")
        bot.register_next_step_handler(msg, check_auth_code)

    if call.data == 'up_agent':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton(text="Создать новое", callback_data='up_create_a')
        key2 = types.InlineKeyboardButton(text="Выбрать существующее", callback_data='up_choose_a')
        keyboard.add(key1, key2)
        bot.send_message(call.message.chat.id, "Создать или редактировать личное дело?", reply_markup=keyboard)

    if call.data == 'up_operator':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton(text="Создать новое", callback_data='up_create_o')
        key2 = types.InlineKeyboardButton(text="Выбрать существующее", callback_data='up_choose_o')
        keyboard.add(key1, key2)
        bot.send_message(call.message.chat.id, "Создать или редактировать личное дело?", reply_markup=keyboard)

    # edit unit_profile

    if call.data == 'edit_op_info':
        bot.send_message(call.message.chat.id, "Введите новую информацию")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, edit_op_info)
    elif call.data == 'edit_op_info_confirmed':
        msg = bot.send_message(call.message.chat.id, "Изменения внесены")
        db_interface.edit_op_info(unit_profile_id, up_info)
        bot.register_next_step_handler_by_chat_id(msg, chosen_up(msg))
    elif call.data == 'edit_op_rank':
        bot.send_message(call.message.chat.id, "Введите новый ранг")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, edit_op_rank)
    elif call.data == 'edit_op_rank_confirmed':
        msg = bot.send_message(call.message.chat.id, "Изменения внесены")
        db_interface.edit_op_rank(unit_profile_id, up_rank)
        bot.register_next_step_handler_by_chat_id(msg, chosen_up(msg))
    elif call.data == 'edit_op_person_id':
        bot.send_message(call.message.chat.id, "Введите новый ID персоны")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, edit_op_person_id)
    elif call.data == 'edit_op_person_id_confirmed':
        msg = bot.send_message(call.message.chat.id, "Изменения внесены")
        db_interface.edit_op_person_id(unit_profile_id, person_id)
        bot.register_next_step_handler_by_chat_id(msg, chosen_up(msg))
    elif call.data == 'edit_op_dates':
        bot.send_message(call.message.chat.id, "Введите новые даты")
        bot.register_next_step_handler(call.message, edit_op_dates)
    elif call.data == 'edit_op_dates_confirmed':
        msg = bot.send_message(call.message.chat.id, "Изменения внесены")
        db_interface.edit_op_dates(unit_profile_id, date_from, date_to)
        bot.register_next_step_handler_by_chat_id(msg, chosen_up(msg))
    if call.data == 'show_mr_last10':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_mr_last10()
        for x in range(0, len(lines), 4096):
            bot.send_message(call.message.chat.id, lines[x:x + 4096])
    elif call.data == 'show_mr_from_beginning':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_mr_from_beginning()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
    if call.data == 'show_agents':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_agents()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
    elif call.data == 'show_agents_sorted_by_names':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_agents_sorted_by_names()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
    elif call.data == 'show_agents_without_pack':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_agents_without_pack()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
    if call.data == 'show_items_sorted_by_names':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_items_sorted_by_names()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
    elif call.data == 'show_items_without_pack':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_items_without_pack()
        if lines == -1:
            bot.send_message(call.message.chat.id, "Нет вещей, не входящих в снаряжение")
        else:
            if len(lines) > 4096:
                for x in range(0, len(lines), 4096):
                    bot.send_message(call.message.chat.id, lines[x:x + 4096])
            else:
                bot.send_message(call.message.chat.id, lines)
    if call.data == 'show_missions_sorted_by_names':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_missions_sorted_by_names()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
    elif call.data == 'show_missions_sorted_by_rank':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_missions_sorted_by_rank()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
    elif call.data == 'show_missions_without_operator':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        lines = db_interface.show_missions_without_operator()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)

    if call.data == 'assign_agent':
        msg = bot.send_message(call.message.chat.id, "На какую миссию назначить?")
        lines = db_interface.get_missions()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
        bot.register_next_step_handler(msg, agent_choose_mission)
    elif call.data == 'assign_agent_mission_confirmed':
        msg = bot.send_message(call.message.chat.id, "Выберите агента")
        lines = db_interface.get_agents()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
        bot.register_next_step_handler(msg, add_agent_mission)
    elif call.data == 'add_agent_mission_finish':
        db_interface.add_agent_mission(agent_id, mission_id, info, date_from, date_to)
        bot.send_message(call.message.chat.id, "Агент назначен на миссию")
        lines = db_interface.get_agent_mission_by_agent_id(agent_id)
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
    if call.data == 'assign_operator':
        msg = bot.send_message(call.message.chat.id, "На какую миссию назначить?")
        lines = db_interface.get_missions()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
        bot.register_next_step_handler(msg, operator_choose_mission)
    elif call.data == 'assign_operator_mission_confirmed':
        msg = bot.send_message(call.message.chat.id, "Выберите назначаемого оператора:")
        lines = db_interface.get_operators()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
        bot.register_next_step_handler(msg, operator_choose_for_mission)
    elif call.data == 'assign_operator_mission_finished':
        db_interface.add_operator_to_mission(mission_id, operator_id)
        bot.send_message(call.message.chat.id, "Оператор назначен на миссию")
        lines = db_interface.get_mission_by_operator_id(operator_id)
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
    if call.data == 'delete_agent':
        msg = bot.send_message(call.message.chat.id, "Выберите агента")
        lines = db_interface.show_agents()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
        bot.register_next_step_handler(msg, choose_agent_delete)
    elif call.data == 'delete_agent_confirmed':
        db_interface.delete_agent_by_id(agent_id)
        bot.send_message(call.message.chat.id, "Агент удалён")
    if call.data == 'delete_operator':
        msg = bot.send_message(call.message.chat.id, "Выберите агента")
        lines = db_interface.get_operators()
        if len(lines) > 4096:
            for x in range(0, len(lines), 4096):
                bot.send_message(call.message.chat.id, lines[x:x + 4096])
        else:
            bot.send_message(call.message.chat.id, lines)
        bot.register_next_step_handler(msg, choose_operator_delete)
    elif call.data == 'delete_operator_confirmed':
        db_interface.delete_operator_by_id(operator_id)
        bot.send_message(call.message.chat.id, "Оператор удалён")


@bot.message_handler(commands=['time'])
def send_time(message):
    bot.send_message(message.chat.id, datetime.datetime.today())
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.message_handler(commands=['help'])
def help_message(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='time', callback_data=1))
    markup.add(telebot.types.InlineKeyboardButton(text='help', callback_data=2))
    markup.add(telebot.types.InlineKeyboardButton(text='menu', callback_data=3))


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
