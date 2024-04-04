import telebot
from telebot import types
from database import *

bot = telebot.TeleBot('6335667283:AAFMNlVs-bzGKHJ2ts-fdu8G5VWIz8hXeSM')

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.send_message(message.chat.id, "Извините, я не могу обработать ваше сообщение.")

# Обработчик коллбэков кнопок "Да" и "Нет" при подтверждении пополнения счета
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_deposit') or call.data.startswith('cancel_deposit'))
def handle_deposit_confirmation(call):
    if call.data.startswith('confirm_deposit'):
        increase_balance(call.message)
    elif call.data.startswith('cancel_deposit'):
        bot.send_message(call.message.chat.id, 'Операция пополнения отменена.')

# Обработчик коллбэков кнопок "Да" и "Нет" при подтверждении снятия со счета
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_withdraw') or call.data.startswith('cancel_withdraw'))
def handle_withdraw_confirmation(call):
    if call.data.startswith('confirm_withdraw'):
        decrease_balance(call.message)
    elif call.data.startswith('cancel_withdraw'):
        bot.send_message(call.message.chat.id, 'Операция снятия отменена.')

# Обработчик коллбэков кнопок "Да" и "Нет" при подтверждении пополнения счета
@bot.callback_query_handler(func=lambda call: call.data.startswith('yes_deposit') or call.data.startswith('no_deposit'))
def handle_yes_no_deposit(call):
    if call.data.startswith('yes_deposit'):
        increase_balance(call.message)
    elif call.data.startswith('no_deposit'):
        bot.send_message(call.message.chat.id, 'Операция пополнения отменена.')

# Обработчик коллбэков кнопок "Мой баланс"
@bot.callback_query_handler(func=lambda call: call.data == 'balance')
def handle_balance(call):
    show_balance(call.message)

# Обработчик коллбэков кнопок "История операций"
@bot.callback_query_handler(func=lambda call: call.data == 'history')
def handle_history(call):
    show_history(call.message)

# Обработчик коллбэков кнопок "Пополнить счет"
@bot.callback_query_handler(func=lambda call: call.data == 'deposit')
def handle_deposit(call):
    bot.send_message(call.message.chat.id, 'Введите сумму для пополнения:')
    bot.register_next_step_handler(call.message, process_deposit)

# Обработчик коллбэков кнопок "Снять со счета"
@bot.callback_query_handler(func=lambda call: call.data == 'withdraw')
def handle_withdraw(call):
    bot.send_message(call.message.chat.id, 'Введите сумму для снятия:')
    bot.register_next_step_handler(call.message, process_withdraw)

# Обработчик некорректных действий
@bot.callback_query_handler(func=lambda call: True)
def handle_invalid_actions(call):
    bot.send_message(call.message.chat.id, 'Извините, но ваше действие не может быть выполнено.')

# Запуск бота
bot.polling(non_stop=True)
