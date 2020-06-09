# from telegram import Updater, CommandHandler
import telebot
import json
import os
from datetime import datetime

from pathlib import Path
from dotenv import load_dotenv

from telebot import types, apihelper

from airtable import Airtable

from airflow.models import DAG
from airflow.models.baseoperator import BaseOperator
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.dates import days_ago
from airflow.operators.dummy_operator import DummyOperator


AIR_TABLE_API_KEY = os.getenv("AIR_TABLE_API_KEY")
AIR_TABLE_BASE_KEY = os.getenv("AIR_TABLE_BASE_KEY")


class TelegramOperator(BaseOperator):
    @apply_defaults
    def __init__(self, filename: str,
                 chat_id_for_send='150399599',
                 use_proxy=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.filename = filename
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
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="Двинули!")
                    result_data_set = {
                        'chat_id': str(call.message.chat.id),
                        'username': call.from_user.username,
                        'triggered_at': datetime.utcfromtimestamp(
                            int(call.message.date)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'reporter_name': 'dimk_smith',
                        'event_type': 'event_type'
                    }
                    with open(self.filename, 'w') as outfile:
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


class FileCheckSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(self, filename: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    def poke(self, *args, **kwargs):
        return os.path.isfile(self.filename)


default_args = {
    'owner': 'Dimk_smith',
    'start_date': days_ago(2),
    'chat_id_for_send': '-496351002',

    'filename': '/tmp/temp.json'}

dag = DAG(dag_id='telegram_listener',
          schedule_interval='@once', default_args=default_args)

send_telegram_message = TelegramOperator(
    task_id='send_telegram_message', dag=dag)

wait_for_file = FileCheckSensor(
    task_id='wait_for_file', poke_interval=10, dag=dag)


all_success = DummyOperator(task_id='all_success', dag=dag)
send_telegram_message >> wait_for_file >> all_success
