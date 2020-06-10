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


class TelegramOperator(BaseOperator):
    @apply_defaults
    def __init__(self, filename: str,
                 chat_id_for_send: str,
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
                    new_message = "Спасибо! Ваш голос 2020 принят!"
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=new_message)
                    result_data_set = {
                        'chat_id': str(call.message.chat.id),
                        'username': call.from_user.username,
                        'triggered_at': datetime.fromtimestamp(
                            int(call.message.date)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        'reporter_name': 'dimk_smith',
                        'event_type': new_message
                    }
                    with open(self.filename, 'w', encoding='utf-8') as outfile:
                        json.dump(result_data_set, outfile)
                    bot.stop_polling()

        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(
            text="Поехали", callback_data="test")
        keyboard.add(callback_button)
        bot.send_message(self.chat_id_for_send,
                         'Карантин закончился, может в бар?',
                         reply_markup=keyboard)
        bot.polling()


class FileCheckSensor(BaseSensorOperator):
    @apply_defaults
    def __init__(self, filename: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    def poke(self, *args, **kwargs):
        return os.path.isfile(self.filename)


class AirtableOperator(BaseOperator):
    @apply_defaults
    def __init__(self, air_table: str, filename: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        env_path = Path('.') / '.env'
        load_dotenv(dotenv_path=env_path)
        self.api_key = os.getenv("AIR_TABLE_API_KEY")
        self.base_key = os.getenv("AIR_TABLE_BASE_KEY")
        self.air_table = air_table
        self.filename = filename

    def execute(self, *args, **kwargs):
        with open(self.filename, encoding='utf-8') as f:
            data_set = json.load(f)
        airtable = Airtable(self.base_key, self.air_table,
                            api_key=self.api_key)
        records = airtable.get_all()
        airtable.insert({key: str(data_set[key]) for key in data_set})


default_args = {
    'owner': 'Dimk_smith',
    'start_date': days_ago(2),
    # test
    # 'chat_id_for_send': '150399599',
    # 'air_table': 'air_table',

    # prod
    'chat_id_for_send': '-496351002',
    'air_table': 'tg_actions',

    'filename': '/tmp/temp.json'}

dag = DAG(dag_id='telegram_listener',
          schedule_interval='@once', default_args=default_args)

send_telegram_message = TelegramOperator(
    task_id='send_telegram_message', dag=dag)

wait_for_file = FileCheckSensor(
    task_id='wait_for_file', poke_interval=10, dag=dag)

write_to_airtable = AirtableOperator(
    task_id='write_to_airtable', dag=dag)

all_success = DummyOperator(task_id='all_success', dag=dag)
send_telegram_message >> wait_for_file >> write_to_airtable >> all_success
