# Airflow 101

## Challenge 3

Написан код [telegram_listerner.py](https://github.com/dimk00z/airflow_3/blob/master/dags/telegram_listener.py) содержащий ДАГ и три самописных оператора.
Для корректной работы необходимо наличие `.env` файла, содержащего себе следующие значения:

```
TELEGRAM_PROXY=socks5://login:pass@host (использование необязательно)
AIR_TABLE_NAME='имя таблицы airtable'
AIR_TABLE_API_KEY='ключ airtable'
AIR_TABLE_BASE_KEY='код приложения'
TELEGRAM_BOT_TOKEN='токен телеграма'
TELEGRAM_CHAT_ID='чат телеграма'
```

По умолчанию `.env` ищет в папке запуска, но можно задать нахождение, как параметр ДАГа.

### Операторы:

1. `send_telegram_message` - отправляет сообщение с кнопной и ждет нажатия. После нажатия записывает временный файл по умолчанию в `/tmp/temp.json`
2. `wait_for_file` - проверяет наличие временного файла
3. `write_to_airtable` - записывает данные в airtable и удаляет временный файл

### Как установить

Для корректной работы скрипта должны быть установлены зависимости:

```
pip install -r requirements.txt
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе [Airflow 101](https://airflow101.python-jitsu.club/).
