# from telegram import Updater, CommandHandler
import telebot
import json
import os
from datetime import datetime

from pathlib import Path
from dotenv import load_dotenv

from telebot import types
from telebot import apihelper

from airtable import Airtable

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

AIR_TABLE_API_KEY = os.getenv("AIR_TABLE_API_KEY")
AIR_TABLE_BASE_KEY = os.getenv("AIR_TABLE_BASE_KEY")


def get_data_from_env(data_name):
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    return getenv(data_name)


class TelegramOperator(BaseOperator):
    @apply_defaults
    def __init__(self, data_set_file_name='/tmp/temp.json',
                 chat_id_for_send='150399599', use_proxy=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.use_proxy = use_proxy
        self.chat_id_for_send = chat_id_for_send
        if use_proxy:
            self.proxy = os.getenv("TELEGRAM_PROXY")

    def execute(self, *args, **kwargs):
        if self.use_proxy:
            apihelper.proxy = {
                'https': self.proxy}
        bot = telebot.TeleBot(self.token)

        @bot.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            if call.message:
                if call.data == "test":
                    bot.edit_message_text(
                        chat_id=call.message.chat.id, message_id=call.message.message_id, text="Двинули!")
                    print(call)
                    result_data_set = {
                        'chat_id': str(call.message.chat.id),
                        'username': call.from_user.username,
                        'triggered_at': datetime.utcfromtimestamp(
                            int(call.message.date)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'reporter_name': 'dimk_smith',
                        'event_type': 'event_type'
                    }
                    with open('/tmp/temp.json', 'w') as outfile:
                        json.dump(result_data_set, outfile)
                    bot.stop_polling()
                    print('Бот отработал')

        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(
            text="Поехали", callback_data="test")
        keyboard.add(callback_button)
        bot.send_message(self.chat_id_for_send,
                         'Dimk_smith', reply_markup=keyboard)
        bot.polling()


def send_telegram_message():
    apihelper.proxy = {
        'https': TELEGRAM_PROXY}

    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):
        if call.message:
            if call.data == "test":
                bot.edit_message_text(
                    chat_id=call.message.chat.id, message_id=call.message.message_id, text="Спасибо")
                print(call)
                result_data_set = {
                    'chat_id': str(call.message.chat.id),
                    'username': call.from_user.username,
                    'triggered_at': datetime.utcfromtimestamp(
                        int(call.message.date)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'reporter_name': 'dimk_smith',
                    'event_type': 'event_type'
                }
                with open('/tmp/temp.json', 'w') as outfile:
                    json.dump(result_data_set, outfile)
                bot.stop_polling()
                print('Бот отработал')

    keyboard = types.InlineKeyboardMarkup()

    callback_button = types.InlineKeyboardButton(
        text="Поехали", callback_data="test")
    keyboard.add(callback_button)
    bot.send_message('150399599', 'Dimk_smith', reply_markup=keyboard)
    bot.polling()


def write_to_airtable():
    table_name = 'air_table'
    with open('/tmp/temp.json') as f:
        data_set = json.load(f)
    airtable = Airtable(AIR_TABLE_BASE_KEY, table_name,
                        api_key=AIR_TABLE_API_KEY)
    records = airtable.get_all()
    airtable.insert({key: str(data_set[key]) for key in data_set})


if __name__ == '__main__':
    telegramOperator = TelegramOperator()
    print(telegramOperator)
    # send_telegram_message()
    # write_to_airtable()
