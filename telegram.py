# from telegram import Updater, CommandHandler
import telebot
import json

from telebot import types
from telebot import apihelper

from airtable import Airtable

# apihelper.proxy = {'https': 'socks5://150399599:R6y5CH1S@ss-01.s5.ynvv.cc:999'}

# bot = telebot.TeleBot("927990044:AAGTf7reZwctIVnysUviPieXm84CPAUC_zU")
# keyboard = types.InlineKeyboardMarkup()

# callback_button = types.InlineKeyboardButton(
#     text="Поехали", callback_data="test")
# keyboard.add(callback_button)
# bot.send_message('150399599', 'Dimk_smith', reply_markup=keyboard)


def send_telegram_message():
    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        if call.message:
            if call.data == "test":
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id, text="Спасибо")
                result_data_set = {
                    'chat_id': call.message.chat.id,
                    'username': call.from_user.username,
                    'triggered_at': call.message.date,
                    'reporter_name': 'dimk_smith',
                    'event_type': 'event_type'
                }
                with open('/tmp/temp.json', 'w') as outfile:
                    json.dump(result_data_set, outfile)
                print(result_data_set)
                bot.stop_polling()
                print('Бот отработал')
    apihelper.proxy = {
        'https': 'socks5://150399599:R6y5CH1S@ss-01.s5.ynvv.cc:999'}

    bot = telebot.TeleBot("927990044:AAGTf7reZwctIVnysUviPieXm84CPAUC_zU")
    keyboard = types.InlineKeyboardMarkup()

    callback_button = types.InlineKeyboardButton(
        text="Поехали", callback_data="test")
    keyboard.add(callback_button)
    bot.send_message('150399599', 'Dimk_smith', reply_markup=keyboard)
    bot.polling()


def write_to_airtable():
    base_key = 'appNPoAJOyctb4MId'
    table_name = 'Test'
    airtable = Airtable(base_key, table_name, api_key='keyWMHvL8W3PuvyfJ')
    # api_key=os.environ['AIRTABLE_KEY'])
    records = airtable.get_all()

    print(records)


if __name__ == '__main__':
    # bot.polling()
    write_to_airtable()
