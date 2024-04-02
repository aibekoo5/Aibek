import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot('6335667283:AAFMNlVs-bzGKHJ2ts-fdu8G5VWIz8hXeSM')
name = None

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS accounts (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id,f'Сәлем, {message.from_user.first_name}{message.from_user.last_name} шоттың атын жазыңыз: ')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id,'Пароль жаз')
    bot.register_next_step_handler(message, user_pass)

def user_pass(message):
    password = message.text.strip()

    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute(f'INSERT INTO accounts(name, pass) VALUES ({name}, {password})')
    conn.commit()
    cur.close()
    conn.close()
    markup = telebot.types.InlineKeyboardMarkup
    markup.add(telebot.types.InlineKeyboardButton('Қолданушылар тізімі', callback_data='accounts'))
    bot.send_message(message.chat.id,'Сіз тіркелдіңіз!', reply_markup=markup)


bot.polling(non_stop=True)
