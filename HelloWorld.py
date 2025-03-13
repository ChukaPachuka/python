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
    print("Данные успешно получены", data[:2])  # выводим первые две записи
else:
    print("Ошибка:", response.status_code, response.text)

import ast

def parse_passback_params(record):
    try:
        params = ast.literal_eval(record["passback_params"])  # преобразуем строку в словарь
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
        return None  # пропускаем запись, если ошибка

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
    data = response.json()  # парсим JSON в Python-объект
    print(data[:2])  # выводим первые две записи для проверки
else:
    print(f"Ошибка при получении данных: {response.status_code}")

import ast

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

# применяем к данным из API
for entry in data:
    parsed_params = parse_passback_params(entry)
    entry.update(parsed_params)  # добавляем распарсенные данные в запись

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
    # преобразуем значение is_correct из 1 или 0 в True или False
    is_correct = True if entry["is_correct"] == 1 else False
    
    values = (
        entry["lti_user_id"],
        entry["oauth_consumer_key"],
        entry["lis_result_sourcedid"],
        entry["lis_outcome_service_url"],
        is_correct,  # используем преобразованное значение
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

# настройки логирования
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

import os
import logging
import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# настройки логирования
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_filename = os.path.join(log_folder, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")
logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# подключение к базе данных
DB_PARAMS = {
    "dbname": "grader_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5433",
}

def get_daily_stats():
    """Получает агрегированные данные за день"""
    today = datetime.today().strftime('%Y-%m-%d')

    query = f"""
        SELECT 
            COUNT(CASE WHEN attempt_type = 'submit' THEN 1 END) AS total_attempts,
            COUNT(CASE WHEN is_correct = TRUE THEN 1 END) AS successful_attempts,
            COUNT(DISTINCT user_id) AS unique_users
        FROM grader_attempts
        WHERE created_at::date = '{today}'
    """

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        # проверяем, есть ли данные за этот день
        if result is None or all(v is None for v in result):
            result = (0, 0, 0)  # если данных нет, ставим нули

        logging.info(f"Агрегированные данные за {today}: {result}")
        return [today] + list(result)

    except Exception as e:
        logging.error(f"Ошибка при работе с базой данных: {e}")
        return None

def upload_aggregated_data_to_google_sheets(data):
    """Загружает агрегированные данные в Google Sheets"""
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file"
    ]
    
    creds_path = r'C:\Users\user\Desktop\credentials.json'

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)

        logging.info("Начинаем авторизацию в Google Sheets")
        client = gspread.authorize(creds)
        logging.info("Авторизация прошла успешно")

        # spreadsheet = client.open("grader_attempts")
        spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1-tjqgz82i4sopKUNus1TgqZFsvqm3vU829u29CvTBCg/edit")
        sheet = spreadsheet.sheet1  # первый лист
        
        # добавляем строку с агрегированными данными
        sheet.append_row(list(data), value_input_option="RAW")

        logging.info("Агрегированные данные успешно загружены в Google Sheets")

    except Exception as e:
        logging.error(f"Ошибка при загрузке данных в Google Sheets: {e}")

import smtplib
import ssl
from email.message import EmailMessage

# настройки почты
SMTP_SERVER = "smtp.mail.ru"  # SMTP-сервер mail.ru
SMTP_PORT = 465  # порт для SSL
SENDER_EMAIL = "natalie.begunova@mail.ru"  # email-адрес
SENDER_PASSWORD = "WWJvZNF8VxUyEVysWUPP"  # пароль приложения ("пароль для внешнего приложения")
RECIPIENT_EMAIL = "natalie.begunova@mail.ru"  # кому отправляем письмо

def send_email(subject, message):
    msg = EmailMessage()
    msg.set_content(message)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    context = ssl.create_default_context()
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            logging.info("Email-уведомление успешно отправлено")
    except Exception as e:
        logging.error(f"Ошибка при отправке email: {e}")

if __name__ == "__main__":
    logging.info("Скрипт запущен")

    daily_stats = get_daily_stats()  # получаем данные из БД
    if daily_stats:
        upload_aggregated_data_to_google_sheets(daily_stats)  # загружаем в Google Sheets
        send_email("Обновление статистики", f"Агрегированные данные за день: {daily_stats}")  # отправляем email
    else:
        logging.error("Ошибка: данные для загрузки отсутствуют")


