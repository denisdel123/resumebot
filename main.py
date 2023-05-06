import telebot
from telebot import types
import os
import psycopg2
from dotenv import load_dotenv
import json

load_dotenv()
token_bot = os.environ.get("BOT")
bot = telebot.TeleBot(token_bot)

name = None
last_name = None
about_myself = None
skills = None
work = None
user_id = None

conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="rootroot",
    port="5432")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS workers1 (worker_id SERIAL NOT NULL PRIMARY KEY, name varchar(50), \
                        last_name varchar(50), about_myself varchar(1000), skils varchar(1000), work varchar(50))")
conn.commit()
cur.close()
conn.close()

WORKER_INFO_COLS = ("ID", "Имя", "Фамилия", "О себе", "Проф скилы", "Специальность")


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    but_new_user = types.InlineKeyboardButton('Зарегестрироваться', callback_data='register')
    but_old_user = types.InlineKeyboardButton('Найти пользователя', callback_data='found')
    markup.row(but_new_user, but_old_user)
    bot.send_message(message.chat.id, "Выбери действие", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_f(call):
    if call.data == 'register':
        bot.send_message(call.message.chat.id, 'Введите ваше имя')
        bot.register_next_step_handler(call.message, user_name)
    elif call.data == 'found':
        bot.send_message(call.message.chat.id, 'Введите ID')
        bot.register_next_step_handler(call.message, info)
    else:
        bot.send_message(call.message.chat.id, 'Ошибка попробуйте снова')
        bot.register_next_step_handler(call.message, start)


def user_name(message):
    global name
    name = message.text.capitalize().strip()
    bot.send_message(message.chat.id, 'Введите вашу Фамилию')
    bot.register_next_step_handler(message, user_last_name)


def user_last_name(message):
    global last_name
    last_name = message.text.capitalize().strip()
    bot.send_message(message.chat.id, 'Расскажите о себе')
    bot.register_next_step_handler(message, user_about)


def user_about(message):
    global about_myself
    about_myself = message.text
    bot.send_message(message.chat.id, 'Проф скилы')
    bot.register_next_step_handler(message, skils_user)


def skils_user(message):
    global skills
    skills = message.text
    print(about_myself)
    bot.send_message(message.chat.id, 'Напишите вашу специальность')
    bot.register_next_step_handler(message, save_data_user)


def save_data_user(message):
    global work
    work = message.text
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="rootroot",
        port="5432")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO workers1 (name, last_name, about_myself, skils, work) \
        VALUES ('%s', '%s', '%s', '%s', '%s')" % (name, last_name, about_myself, skills, work))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "вы зарегестрированы")
    bot.register_next_step_handler(message, start)


def info(message):
    global WORKER_INFO_COLS
    global name, worker_dict, user_id
    global user_id
    user_id = str(message.text.strip())
    print(f"User_id: {user_id}")

    name = message.text.capitalize().strip()
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="rootroot",
        port="5432")
    cur = conn.cursor()

    cur.execute(f"SELECT * FROM workers1 WHERE worker_id={user_id} LIMIT 1")
    worker = cur.fetchall().pop()

    worker_dict = {
        name: value for name, value in zip(WORKER_INFO_COLS, worker)
    }

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, str(worker_dict))


bot.polling(none_stop=True)
