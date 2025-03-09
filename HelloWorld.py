print("Hello, World!")
import requests

api_url = "https://b2b.itresume.ru/api/statistics"
params = {
    "client": "Skillfactory",
    "client_key": "M2MGWS",
    "start": "2023-04-01 12:46:47.860798",
    "end": "2023-04-02 12:46:47.860798"
}

response = requests.get(api_url, params=params)

if response.status_code == 200:
    data = response.json()
    print("Данные успешно получены!", data[:2])  # Выведем первые 2 записи
else:
    print("Ошибка:", response.status_code, response.text)

import ast

def parse_passback_params(record):
    try:
        params = ast.literal_eval(record["passback_params"])  # Преобразуем строку в словарь
        return {
            "user_id": record["lti_user_id"],
            "oauth_consumer_key": params.get("oauth_consumer_key", None),
            "lis_result_sourcedid": params.get("lis_result_sourcedid", None),
            "lis_outcome_service_url": params.get("lis_outcome_service_url", None),
            "is_correct": record["is_correct"],
            "attempt_type": record["attempt_type"],
            "created_at": record["created_at"]
        }
    except (ValueError, SyntaxError) as e:
        print(f"Ошибка обработки passback_params: {e}")
        return None  # Пропускаем запись, если ошибка

parsed_data = [parse_passback_params(record) for record in data if parse_passback_params(record)]
print("Обработанные данные:", parsed_data[:2])

import requests

api_url = "https://b2b.itresume.ru/api/statistics"
params = {
    "client": "Skillfactory",
    "client_key": "M2MGWS",
    "start": "2023-04-01 12:46:47.860798",
    "end": "2023-04-02 12:46:47.860798"
}

response = requests.get(api_url, params=params)

if response.status_code == 200:
    data = response.json()  # Парсим JSON в Python-объект
    print(data[:2])  # Выводим первые две записи для проверки
else:
    print(f"Ошибка при получении данных: {response.status_code}")

import ast  # Безопасно преобразует строку в словарь

def parse_passback_params(entry):
    try:
        params_str = entry.get("passback_params", "{}")
        params_dict = ast.literal_eval(params_str.replace("null", "None"))
        
        return {
            "oauth_consumer_key": params_dict.get("oauth_consumer_key", ""),
            "lis_result_sourcedid": params_dict.get("lis_result_sourcedid", ""),
            "lis_outcome_service_url": params_dict.get("lis_outcome_service_url", "")
        }
    except (SyntaxError, ValueError):
        return {"oauth_consumer_key": "", "lis_result_sourcedid": "", "lis_outcome_service_url": ""}

# Применяем к данным из API
for entry in data:
    parsed_params = parse_passback_params(entry)
    entry.update(parsed_params)  # Добавляем распарсенные данные в запись

import psycopg2

conn = psycopg2.connect(
    dbname="grader_db",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5433"
)
cursor = conn.cursor()

insert_query = """
INSERT INTO grader_attempts (
    user_id, oauth_consumer_key, lis_result_sourcedid, lis_outcome_service_url, 
    is_correct, attempt_type, created_at
) VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

for entry in data:
    values = (
        entry["lti_user_id"],
        entry["oauth_consumer_key"],
        entry["lis_result_sourcedid"],
        entry["lis_outcome_service_url"],
        entry["is_correct"],
        entry["attempt_type"],
        entry["created_at"]
    )
    cursor.execute(insert_query, values)

conn.commit()
cursor.close()
conn.close()

import logging
from datetime import datetime, timedelta
import os

# Настройки логирования
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

log_filename = os.path.join(log_folder, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def cleanup_old_logs():
    """Удаляет логи старше 3 дней"""
    for filename in os.listdir(log_folder):
        file_path = os.path.join(log_folder, filename)
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if datetime.now() - file_time > timedelta(days=3):
                os.remove(file_path)
                logging.info(f"Удален старый лог: {filename}")

logging.info("Скрипт запущен")
cleanup_old_logs()

try:
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        logging.info("Данные успешно получены")
    else:
        logging.error(f"Ошибка при получении данных: {response.status_code}")
except Exception as e:
    logging.error(f"Ошибка при обращении к API: {e}")
