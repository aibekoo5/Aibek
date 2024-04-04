import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot('6335667283:AAFMNlVs-bzGKHJ2ts-fdu8G5VWIz8hXeSM')
name = None
deposit_amount = None


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(50), pass VARCHAR(50), balance INTEGER DEFAULT 0, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, operation_type VARCHAR(10))')
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id,
                     f'Сәлем, {message.from_user.first_name}{message.from_user.last_name}! Қазір сізді тіркейміз шотыңызға ат беріңіз немесе бұрын тіркелген шоттың атын жазыңыз: ')
    bot.register_next_step_handler(message, user_name)


def user_name(message):
    global name
    name = message.text.strip()

    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE name=?", (name,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:  # If the name exists in the database
        bot.send_message(message.chat.id, 'Такой счет есть в базе, введите пароль для входа:')
        bot.register_next_step_handler(message, user_password)
    else:
        bot.send_message(message.chat.id, 'Открыт новый счет, введите пароль:')
        bot.register_next_step_handler(message, create_password)


def create_password(message):
    global name
    password = message.text.strip()

    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO accounts(name, pass) VALUES (?, ?)", (name, password))
    conn.commit()
    cur.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Менің балансым', callback_data='balance'))
    markup.add(telebot.types.InlineKeyboardButton('Тарих', callback_data='history'))
    markup.add(telebot.types.InlineKeyboardButton('Ақша салу', callback_data='deposit'))
    markup.add(telebot.types.InlineKeyboardButton('Ақша алу', callback_data='withdraw'))
    bot.send_message(message.chat.id, 'Сіз тіркелдіңіз!', reply_markup=markup)

    # Сохраняем имя пользователя
    name = message.text.strip()



def user_password(message):
    password = message.text.strip()

    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE name=? AND pass=?", (name, password))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:  # If the name and password match
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton('Менің балансым', callback_data='balance'))
        markup.add(telebot.types.InlineKeyboardButton('Тарих', callback_data='history'))
        markup.add(telebot.types.InlineKeyboardButton('Ақша алу', callback_data='withdraw'))
        markup.add(telebot.types.InlineKeyboardButton('Ақша салу', callback_data='deposit'))
        bot.send_message(message.chat.id, 'Вход выполнен успешно!', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Неверный пароль. Попробуйте еще раз:')
        bot.register_next_step_handler(message, user_password)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'balance':
        show_balance(call.message)
    elif call.data == 'history':
        show_history(call.message)
    elif call.data == 'deposit':
        bot.send_message(call.message.chat.id, 'Введите сумму для пополнения:')
        bot.register_next_step_handler(call.message, process_deposit)
    elif call.data == 'confirm_deposit':
        increase_balance(call.message)
    elif call.data == 'cancel_deposit':
        bot.send_message(call.message.chat.id, 'Операция пополнения отменена.')
    elif call.data == 'withdraw':
        bot.send_message(call.message.chat.id, 'Введите сумму для снятия:')
        bot.register_next_step_handler(call.message, process_withdraw)
    elif call.data == 'confirm_withdraw':
        decrease_balance(call.message)
    elif call.data == 'cancel_withdraw':
        bot.send_message(call.message.chat.id, 'Операция снятия отменена.')
    # Добавляем обработчики для кнопок "Да" и "Нет"
    elif call.data == 'yes_deposit':
        increase_balance(call.message)
    elif call.data == 'no_deposit':
        bot.send_message(call.message.chat.id, 'Операция пополнения отменена.')

def process_withdraw(message):
    global withdraw_amount
    try:
        withdraw_amount = float(message.text)
        if withdraw_amount <= 0:
            bot.send_message(message.chat.id, 'Сумма должна быть больше нуля. Попробуйте еще раз:')
            bot.register_next_step_handler(message, process_withdraw)
        else:
            confirm_withdraw(message)
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат суммы. Введите числовое значение. Попробуйте еще раз:')
        bot.register_next_step_handler(message, process_withdraw)

def confirm_withdraw(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Да', callback_data='confirm_withdraw'),
               telebot.types.InlineKeyboardButton('Нет', callback_data='cancel_withdraw'))
    bot.send_message(message.chat.id, f'Снять счета на {withdraw_amount}?', reply_markup=markup)

def decrease_balance(message):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute(
        "UPDATE accounts SET balance = balance - ?, timestamp = CURRENT_TIMESTAMP, operation_type = 'withdraw' WHERE name=?",(withdraw_amount, name))
    result = cur.fetchone()
    if result is not None:
        balance = result[0]
        if balance >= withdraw_amount:
            cur.execute("UPDATE accounts SET balance = balance - ? WHERE name=?", (withdraw_amount, name))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, f'Счет успешно уменьшен на {withdraw_amount}.')
            show_balance(message)
        else:
            bot.send_message(message.chat.id, 'Недостаточно средств на счете.')
    else:
        bot.send_message(message.chat.id, 'Счет не найден.')


def process_deposit(message):
    global deposit_amount
    try:
        deposit_amount = float(message.text)
        if deposit_amount <= 0:
            bot.send_message(message.chat.id, 'Сумма должна быть больше нуля. Попробуйте еще раз:')
            bot.register_next_step_handler(message, process_deposit)
        else:
            confirm_deposit(message)
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат суммы. Введите числовое значение. Попробуйте еще раз:')
        bot.register_next_step_handler(message, process_deposit)


def confirm_deposit(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Да', callback_data='yes_deposit'),
               telebot.types.InlineKeyboardButton('Нет', callback_data='no_deposit'))
    bot.send_message(message.chat.id, f'Пополнить счет на {deposit_amount}?', reply_markup=markup)


def increase_balance(message):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance + ?, timestamp = CURRENT_TIMESTAMP, operation_type = 'deposit' WHERE name=?", (deposit_amount, name))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Счет успешно пополнен на {deposit_amount}.')
    show_balance(message)

def show_balance(message):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute("SELECT balance FROM accounts WHERE name=?", (name,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result is not None:
        balance = result[0]
        bot.send_message(message.chat.id, f'Ваш текущий баланс: {balance}')
    else:
        bot.send_message(message.chat.id, 'Сіз жаңадан шот аштыңыз, сізде баланс жоқ.Өтінемін шотыңызды толықтырыңыз')

def show_history(message):
    conn = sqlite3.connect('money.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE name=?", (name,))
    results = cur.fetchall()
    cur.close()
    conn.close()

    if results:
        history_text = "История операций:\n"
        for result in results:
            operation_type = "Пополнение" if result[5] == "deposit" else "Снятие"
            history_text += f"Сумма: {result[4]} Тип: {operation_type} Время: {result[3]}\n"
        bot.send_message(message.chat.id, history_text)
    else:
        bot.send_message(message.chat.id, 'История операций пуста.')

bot.polling(non_stop=True)